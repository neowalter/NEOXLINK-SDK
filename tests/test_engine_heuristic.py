from __future__ import annotations

from neoxlink_sdk.engine import HeuristicModelAdapter, InMemoryDataSource, ProcurementIntentEngine
from neoxlink_sdk.models import MatchCandidate, NormalizedIntent


def test_heuristic_unspsc_boost_for_software() -> None:
    h = HeuristicModelAdapter()
    cands = h.infer_unspsc_candidates("Need enterprise software and API development.", top_k=3)
    assert cands[0].code == "81111500"
    assert cands[0].confidence > 0.0


def test_parse_intent_sets_ambiguity_for_short_text() -> None:
    h = HeuristicModelAdapter()
    p = h.parse_intent("need software")
    assert "query_too_short" in p.ambiguity_signals or p.confidence < 0.9


def test_procurement_engine_runs() -> None:
    ds = InMemoryDataSource(
        [
            MatchCandidate(
                partner_id="a1",
                partner_type="supplier",
                title="Web agency",
                description="SaaS and app development in Shanghai",
                location="Shanghai",
                unspsc_codes=["81111500"],
                attributes={},
                performance_score=0.7,
                recency_days=10,
            )
        ]
    )
    eng = ProcurementIntentEngine(data_source=ds, model_adapter=HeuristicModelAdapter(), clarification_threshold=0.0)
    out = eng.run("Need a mobile app development vendor in Shanghai.", top_k=3)
    assert out.normalized_intent.unspsc_code == "81111500" or out.unspsc_candidates
    assert out.matches  # or empty if ranking filtered


def test_score_match_produces_keys() -> None:
    h = HeuristicModelAdapter()
    norm = NormalizedIntent(
        entry_kind="demand",
        unspsc_code="44121500",
        unspsc_name="Packaging",
        attributes={"product_or_service": "boxes", "keywords": "packaging", "quantity_signal": None},
        constraints={},
    )
    cand = MatchCandidate(
        partner_id="p",
        partner_type="supplier",
        title="Carton supply",
        description="Kraft and labels",
        location="NYC",
        unspsc_codes=["44121500"],
        attributes={},
        performance_score=0.5,
        recency_days=5,
    )
    s = h.score_match(norm, cand)
    assert "semantic_relevance" in s and "intent_fit" in s
