from __future__ import annotations

from dataclasses import dataclass

from .extraction_engine import ExtractionEngine


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    text: str
    expected_service: str
    expected_taxonomy_code: str | None = None


@dataclass(frozen=True)
class EvaluationReport:
    total_cases: int
    service_accuracy: float
    taxonomy_hit_rate: float


def evaluate_intent_parsing(engine: ExtractionEngine, cases: list[BenchmarkCase]) -> EvaluationReport:
    if not cases:
        return EvaluationReport(total_cases=0, service_accuracy=0.0, taxonomy_hit_rate=0.0)

    service_hits = 0
    taxonomy_hits = 0
    for case in cases:
        extracted = engine.extract(request_id=case.case_id, text=case.text)
        service = extracted.intent.product_or_service.lower()
        if case.expected_service.lower() in service:
            service_hits += 1
        if case.expected_taxonomy_code:
            predicted_codes = [str(item.get("code", "")) for item in extracted.taxonomy_candidates]
            if case.expected_taxonomy_code in predicted_codes:
                taxonomy_hits += 1
    total = len(cases)
    return EvaluationReport(
        total_cases=total,
        service_accuracy=service_hits / total,
        taxonomy_hit_rate=taxonomy_hits / total,
    )
