from __future__ import annotations

import re
from time import perf_counter
from typing import Any, Protocol

from .models import (
    ClarificationQuestion,
    ClarificationState,
    MatchCandidate,
    ModelCallTrace,
    NormalizedIntent,
    ParsedIntent,
    PipelineStageTrace,
    ProcurementEngineResult,
    RankedMatch,
    UNSPSCCandidate,
)
from .unspsc import unspsc_candidates


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9]+", text.lower()) if token}


class ModelAdapter(Protocol):
    def parse_intent(self, text: str) -> ParsedIntent:
        """Parse free text into structured intent."""

    def disambiguate_unspsc(self, text: str, candidates: list[UNSPSCCandidate]) -> list[UNSPSCCandidate]:
        """Rerank or adjust UNSPSC candidates."""

    def score_match(self, normalized_intent: NormalizedIntent, candidate: MatchCandidate) -> dict[str, float]:
        """Return score signals for ranking."""

    @property
    def provider_name(self) -> str:
        """Provider identifier for tracing."""

    @property
    def model_name(self) -> str:
        """Model identifier for tracing."""


class HeuristicModelAdapter:
    """Deterministic model adapter for local SDK usage and tests."""

    provider_name = "local"
    model_name = "heuristic-v1"

    def parse_intent(self, text: str) -> ParsedIntent:
        tokens = _tokenize(text)
        quantity_match = re.search(r"\b(\d+)\b", text)
        budget_match = re.search(r"\$?\b(\d{2,}(?:[.,]\d{3})*)\b", text)
        location_match = re.search(r"\b(in|at|near|from)\s+([A-Za-z][A-Za-z\s-]{1,40})", text)

        constraints: dict[str, Any] = {}
        if "urgent" in tokens or "asap" in tokens:
            constraints["urgency"] = "high"
        if location_match:
            constraints["location"] = location_match.group(2).strip()
        if budget_match:
            constraints["budget_hint"] = budget_match.group(1)

        ambiguity_signals: list[str] = []
        if len(tokens) < 5:
            ambiguity_signals.append("query_too_short")
        if "or" in tokens:
            ambiguity_signals.append("contains_alternative_paths")
        if not any(term in tokens for term in ("need", "looking", "offer", "supply", "buy", "procure")):
            ambiguity_signals.append("intent_verb_missing")

        confidence = 0.85 - (0.12 * len(ambiguity_signals))
        if confidence < 0.35:
            confidence = 0.35

        return ParsedIntent(
            product_or_service=text.strip(),
            constraints=constraints,
            quantity_signal=quantity_match.group(1) if quantity_match else None,
            location=constraints.get("location"),
            budget_hint=constraints.get("budget_hint"),
            temporal_context="short_term" if "urgent" in tokens else None,
            ambiguity_signals=ambiguity_signals,
            confidence=confidence,
            raw_text=text,
        )

    def disambiguate_unspsc(self, text: str, candidates: list[UNSPSCCandidate]) -> list[UNSPSCCandidate]:
        tokens = _tokenize(text)
        adjusted: list[UNSPSCCandidate] = []
        for candidate in candidates:
            boost = 0.0
            if "software" in tokens and candidate.code.startswith("8111"):
                boost += 0.06
            if "marketing" in tokens and candidate.code.startswith("8014"):
                boost += 0.06
            if "consult" in "".join(tokens) and candidate.code.startswith("8010"):
                boost += 0.04
            adjusted.append(candidate.model_copy(update={"confidence": min(1.0, candidate.confidence + boost)}))
        adjusted.sort(key=lambda item: item.confidence, reverse=True)
        return adjusted

    def score_match(self, normalized_intent: NormalizedIntent, candidate: MatchCandidate) -> dict[str, float]:
        intent_tokens = _tokenize(
            " ".join(
                [
                    str(normalized_intent.attributes.get("product_or_service", "")),
                    str(normalized_intent.attributes.get("keywords", "")),
                    str(normalized_intent.constraints),
                ]
            )
        )
        cand_tokens = _tokenize(f"{candidate.title} {candidate.description} {candidate.attributes}")
        overlap = len(intent_tokens.intersection(cand_tokens))
        union = max(1, len(intent_tokens.union(cand_tokens)))
        semantic_relevance = overlap / union

        unspsc_fit = 1.0 if normalized_intent.unspsc_code in candidate.unspsc_codes else 0.35
        location_fit = 0.5
        requested_location = normalized_intent.constraints.get("location")
        if requested_location and candidate.location:
            location_fit = 1.0 if candidate.location.lower() == str(requested_location).lower() else 0.2

        recency = max(0.05, 1.0 - (candidate.recency_days / 365))
        intent_fit = min(1.0, (semantic_relevance * 0.7) + (unspsc_fit * 0.3))
        return {
            "semantic_relevance": semantic_relevance,
            "unspsc_fit": unspsc_fit,
            "historical_performance": candidate.performance_score,
            "recency": recency,
            "intent_fit": intent_fit,
            "location_fit": location_fit,
        }


class DataSource(Protocol):
    source_name: str

    def search(self, normalized_intent: NormalizedIntent, target: str, limit: int) -> list[MatchCandidate]:
        """Return candidate buyers or suppliers."""


class InMemoryDataSource:
    def __init__(self, records: list[MatchCandidate], source_name: str = "in_memory") -> None:
        self._records = records
        self.source_name = source_name

    def search(self, normalized_intent: NormalizedIntent, target: str, limit: int) -> list[MatchCandidate]:
        expected_type = "supplier" if target == "suppliers" else "buyer"
        filtered = [record for record in self._records if record.partner_type == expected_type]
        if normalized_intent.unspsc_code:
            filtered = [
                record
                for record in filtered
                if normalized_intent.unspsc_code in record.unspsc_codes or not record.unspsc_codes
            ]
        return filtered[: max(1, limit)]


class ProcurementIntentEngine:
    """Six-stage pipeline for demand/supply matching with UNSPSC standardization."""

    def __init__(
        self,
        data_source: DataSource,
        model_adapter: ModelAdapter | None = None,
        clarification_threshold: float = 0.7,
    ) -> None:
        self.data_source = data_source
        self.model_adapter = model_adapter or HeuristicModelAdapter()
        self.clarification_threshold = clarification_threshold

    def parse_intent(self, text: str) -> tuple[ParsedIntent, PipelineStageTrace, ModelCallTrace]:
        start = perf_counter()
        parsed = self.model_adapter.parse_intent(text)
        elapsed = (perf_counter() - start) * 1000
        trace = PipelineStageTrace(
            stage="intent_parsing",
            elapsed_ms=elapsed,
            confidence=parsed.confidence,
            notes={"ambiguity_signals": parsed.ambiguity_signals},
        )
        model_call = ModelCallTrace(
            stage="intent_parsing",
            provider=self.model_adapter.provider_name,
            model=self.model_adapter.model_name,
            latency_ms=elapsed,
            estimated_cost_usd=0.0,
        )
        return parsed, trace, model_call

    def map_unspsc(self, parsed: ParsedIntent) -> tuple[list[UNSPSCCandidate], PipelineStageTrace, ModelCallTrace]:
        start = perf_counter()
        retrieval = unspsc_candidates(parsed.raw_text, top_k=5)
        candidates = [
            UNSPSCCandidate(code=entry.code, name=entry.name, confidence=confidence)
            for entry, confidence in retrieval
        ]
        candidates = self.model_adapter.disambiguate_unspsc(parsed.raw_text, candidates)
        elapsed = (perf_counter() - start) * 1000
        top_conf = candidates[0].confidence if candidates else 0.0
        trace = PipelineStageTrace(
            stage="unspsc_mapping",
            elapsed_ms=elapsed,
            confidence=top_conf,
            notes={"candidate_count": len(candidates)},
        )
        model_call = ModelCallTrace(
            stage="unspsc_mapping",
            provider=self.model_adapter.provider_name,
            model=self.model_adapter.model_name,
            latency_ms=elapsed,
            estimated_cost_usd=0.0,
        )
        return candidates, trace, model_call

    def clarification_loop(
        self,
        parsed: ParsedIntent,
        unspsc_matches: list[UNSPSCCandidate],
        clarification_answers: dict[str, str] | None = None,
    ) -> tuple[ClarificationState, PipelineStageTrace]:
        start = perf_counter()
        top_conf = unspsc_matches[0].confidence if unspsc_matches else 0.0
        needs_clarification = parsed.confidence < self.clarification_threshold or top_conf < self.clarification_threshold
        questions: list[ClarificationQuestion] = []
        if needs_clarification:
            if not parsed.location:
                questions.append(
                    ClarificationQuestion(
                        key="location",
                        question="Which target location should we prioritize for matching?",
                        reason="Location is missing and affects supplier/buyer ranking.",
                    )
                )
            if not parsed.quantity_signal:
                questions.append(
                    ClarificationQuestion(
                        key="quantity",
                        question="What quantity or scale are you targeting?",
                        reason="Quantity influences fit for candidate capacity.",
                    )
                )
            if len(unspsc_matches) >= 2:
                questions.append(
                    ClarificationQuestion(
                        key="unspsc_preference",
                        question=f"Should we prioritize {unspsc_matches[0].name} or {unspsc_matches[1].name}?",
                        reason="Top UNSPSC candidates are close in confidence.",
                    )
                )
        answers = dict(clarification_answers or {})
        resolved = not questions or all(question.key in answers for question in questions)
        clarification = ClarificationState(
            required=needs_clarification,
            confidence_threshold=self.clarification_threshold,
            questions=questions,
            answers=answers,
            resolved=resolved,
        )
        elapsed = (perf_counter() - start) * 1000
        trace = PipelineStageTrace(
            stage="clarification_loop",
            elapsed_ms=elapsed,
            confidence=1.0 if clarification.resolved else 0.5,
            notes={"question_count": len(questions)},
        )
        return clarification, trace

    def normalize_intent(
        self,
        entry_kind: str,
        parsed: ParsedIntent,
        unspsc_matches: list[UNSPSCCandidate],
        clarification: ClarificationState,
    ) -> tuple[NormalizedIntent, PipelineStageTrace]:
        start = perf_counter()
        primary = unspsc_matches[0] if unspsc_matches else UNSPSCCandidate(
            code="80101500",
            name="Business and corporate management consultation services",
            confidence=0.25,
        )

        constraints = dict(parsed.constraints)
        if clarification.answers.get("location"):
            constraints["location"] = clarification.answers["location"]
        attributes = {
            "product_or_service": parsed.product_or_service,
            "quantity_signal": clarification.answers.get("quantity", parsed.quantity_signal),
            "keywords": sorted(_tokenize(parsed.raw_text))[:20],
        }
        normalized = NormalizedIntent(
            entry_kind="supply" if entry_kind == "supply" else "demand",
            unspsc_code=primary.code,
            unspsc_name=primary.name,
            attributes=attributes,
            constraints=constraints,
            inferred_metadata={
                "budget_hint": parsed.budget_hint,
                "temporal_context": parsed.temporal_context,
                "clarification_used": bool(clarification.answers),
            },
        )
        elapsed = (perf_counter() - start) * 1000
        trace = PipelineStageTrace(
            stage="structured_normalization",
            elapsed_ms=elapsed,
            confidence=primary.confidence,
            notes={"normalized_unspsc": primary.code},
        )
        return normalized, trace

    def match(
        self,
        normalized_intent: NormalizedIntent,
        target: str = "suppliers",
        top_k: int = 10,
    ) -> tuple[list[MatchCandidate], PipelineStageTrace]:
        start = perf_counter()
        candidates = self.data_source.search(normalized_intent=normalized_intent, target=target, limit=max(10, top_k * 3))
        elapsed = (perf_counter() - start) * 1000
        trace = PipelineStageTrace(
            stage="matching_retrieval",
            elapsed_ms=elapsed,
            notes={"candidate_pool": len(candidates), "target": target},
        )
        return candidates, trace

    def rank(
        self,
        normalized_intent: NormalizedIntent,
        candidates: list[MatchCandidate],
        top_k: int = 5,
    ) -> tuple[list[RankedMatch], PipelineStageTrace, ModelCallTrace]:
        start = perf_counter()
        ranked: list[RankedMatch] = []
        for candidate in candidates:
            signals = self.model_adapter.score_match(normalized_intent, candidate)
            score = (
                signals["semantic_relevance"] * 0.25
                + signals["historical_performance"] * 0.20
                + signals["recency"] * 0.15
                + signals["intent_fit"] * 0.25
                + signals["location_fit"] * 0.15
            )
            ranked.append(
                RankedMatch(
                    partner_id=candidate.partner_id,
                    partner_type=candidate.partner_type,
                    score=min(1.0, max(0.0, score)),
                    confidence=min(1.0, max(0.0, (signals["intent_fit"] * 0.6) + (signals["semantic_relevance"] * 0.4))),
                    reason_signals=signals,
                    matched_attributes={"unspsc_codes": candidate.unspsc_codes, "location": candidate.location},
                    source=getattr(self.data_source, "source_name", "unknown"),
                )
            )
        ranked.sort(key=lambda match: match.score, reverse=True)
        elapsed = (perf_counter() - start) * 1000
        stage_trace = PipelineStageTrace(
            stage="ranking_output",
            elapsed_ms=elapsed,
            confidence=ranked[0].confidence if ranked else 0.0,
            notes={"returned": min(top_k, len(ranked))},
        )
        model_trace = ModelCallTrace(
            stage="ranking_output",
            provider=self.model_adapter.provider_name,
            model=self.model_adapter.model_name,
            latency_ms=elapsed,
            estimated_cost_usd=0.0,
        )
        return ranked[: max(1, top_k)], stage_trace, model_trace

    def run(
        self,
        text: str,
        *,
        entry_kind: str = "demand",
        target: str = "suppliers",
        top_k: int = 5,
        clarification_answers: dict[str, str] | None = None,
    ) -> ProcurementEngineResult:
        traces: list[PipelineStageTrace] = []
        model_calls: list[ModelCallTrace] = []

        parsed, stage_trace, model_trace = self.parse_intent(text)
        traces.append(stage_trace)
        model_calls.append(model_trace)

        unspsc_list, stage_trace, model_trace = self.map_unspsc(parsed)
        traces.append(stage_trace)
        model_calls.append(model_trace)

        clarification, stage_trace = self.clarification_loop(
            parsed=parsed,
            unspsc_matches=unspsc_list,
            clarification_answers=clarification_answers,
        )
        traces.append(stage_trace)

        normalized, stage_trace = self.normalize_intent(
            entry_kind=entry_kind,
            parsed=parsed,
            unspsc_matches=unspsc_list,
            clarification=clarification,
        )
        traces.append(stage_trace)

        candidates, stage_trace = self.match(normalized_intent=normalized, target=target, top_k=top_k)
        traces.append(stage_trace)

        ranked, stage_trace, model_trace = self.rank(normalized_intent=normalized, candidates=candidates, top_k=top_k)
        traces.append(stage_trace)
        model_calls.append(model_trace)

        return ProcurementEngineResult(
            parsed_intent=parsed,
            unspsc_candidates=unspsc_list,
            clarification=clarification,
            normalized_intent=normalized,
            matches=ranked,
            traces=traces,
            model_calls=model_calls,
        )
