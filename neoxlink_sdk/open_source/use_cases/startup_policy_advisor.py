from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from ...model_adapters import OpenAIChatCompletionsModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AdvisorConfig:
    max_rounds: int = 4
    max_sources: int = 6
    fetch_timeout_seconds: float = 20.0


class StartupPolicyAdvisor:
    """Real-world interactive advisor for startup policy and incentive discovery.

    Flow:
    1) Clarify user intent via iterative LLM dialogue.
    2) Check whether existing evidence is sufficient.
    3) If insufficient, discover and fetch public sources.
    4) Synthesize actionable answer and ask user for satisfaction.
    5) Continue search until user confirms needs are met or round limit reached.
    """

    def __init__(self, model: OpenAIChatCompletionsModel, config: AdvisorConfig | None = None) -> None:
        self.model = model
        self.config = config or AdvisorConfig()

    def run_interactive(self, initial_user_input: str) -> None:
        logger.info("StartupPolicyAdvisor run started. goal=%r", initial_user_input)
        state: dict[str, Any] = {
            "goal": initial_user_input,
            "intent_summary": "",
            "must_cover": [],
            "constraints": {},
            "clarification_history": [],
            "sources": [],
            "evidence": [],
        }

        print("\n[Advisor] Step 1/5: Starting clarification...", flush=True)
        self._clarification_loop(state)
        print("[Advisor] Step 1/5 complete.", flush=True)

        for round_id in range(1, self.config.max_rounds + 1):
            print(f"\n[Advisor] Step 2/5 (round {round_id}): Assessing evidence sufficiency...", flush=True)
            sufficiency = self._assess_sufficiency(state)
            if sufficiency.get("sufficient") is True:
                logger.info("Sufficiency check passed on round=%s.", round_id)
                print(f"[Advisor] Step 2/5 result: evidence is sufficient in round {round_id}.", flush=True)
                print(f"[Advisor] Step 4/5 (round {round_id}): Building recommendation...", flush=True)
                answer = self._build_answer(state)
                print("\n[Advisor] Proposed solution:\n")
                print(answer)
            else:
                logger.info("Sufficiency check failed on round=%s; collecting sources.", round_id)
                queries = sufficiency.get("search_queries") or [state["goal"]]
                print(f"[Advisor] Step 2/5 result: evidence insufficient in round {round_id}.", flush=True)
                print(f"[Advisor] Step 3/5 (round {round_id}): Collecting sources...", flush=True)
                self._collect_sources_and_evidence(state, queries)
                print(
                    f"[Advisor] Step 3/5 complete. Sources: {len(state['sources'])}, "
                    f"evidence items: {len(state['evidence'])}.",
                    flush=True,
                )
                print(f"[Advisor] Step 4/5 (round {round_id}): Building updated recommendation...", flush=True)
                answer = self._build_answer(state)
                print("\n[Advisor] Updated solution:\n")
                print(answer)

            print("[Advisor] Step 5/5: Waiting for user feedback...", flush=True)
            user_feedback = input("\n[You] Does this fully meet your needs? (yes/no + optional details): ").strip()
            if user_feedback.lower().startswith("y"):
                logger.info("User accepted recommendation at round=%s.", round_id)
                print("[Advisor] Great. Ending with finalized recommendations.")
                return

            state["clarification_history"].append(
                {"role": "user", "feedback": user_feedback, "round": round_id}
            )
            refine = self.model.analyze_json(
                "You are refining startup policy research requirements.\n"
                "Return JSON with keys: additional_queries (list of strings), updated_must_cover (list of strings).\n"
                f"Current intent: {state['intent_summary']}\n"
                f"Feedback: {user_feedback}"
            )
            additional_queries = refine.get("additional_queries")
            if isinstance(additional_queries, list):
                self._collect_sources_and_evidence(state, [str(item) for item in additional_queries if item])
            updated_must_cover = refine.get("updated_must_cover")
            if isinstance(updated_must_cover, list):
                state["must_cover"] = [str(item) for item in updated_must_cover if item]

        print("[Advisor] Reached max rounds. Please refine constraints and rerun for higher precision.")

    def _clarification_loop(self, state: dict[str, Any]) -> None:
        while True:
            started = time.perf_counter()
            print("[Advisor] Clarification: requesting model analysis...", flush=True)
            payload = self.model.analyze_json(
                "You are a startup consulting assistant.\n"
                "Goal: clarify user needs for startup consulting policy guidance.\n"
                "Return JSON with keys:\n"
                "- status: 'needs_clarification' or 'ready'\n"
                "- assistant_message: concise question or confirmation\n"
                "- intent_summary: short summary\n"
                "- must_cover: list\n"
                "- constraints: object\n"
                f"Current goal: {state['goal']}\n"
                f"History: {state['clarification_history']}"
            )
            status = str(payload.get("status", "")).lower()
            assistant_message = str(payload.get("assistant_message", "Please provide more details."))
            elapsed = time.perf_counter() - started
            print(f"[Advisor] Clarification model response received in {elapsed:.2f}s.", flush=True)

            if not payload:
                print(
                    "[Advisor] Model response unavailable. Continuing with current goal and collected context.",
                    flush=True,
                )
                logger.error("Clarification payload empty; fallback to current goal.")
                state["intent_summary"] = state["intent_summary"] or state["goal"]
                return

            print(f"[Advisor] {assistant_message}")

            state["intent_summary"] = str(payload.get("intent_summary", state["intent_summary"]))
            must_cover = payload.get("must_cover")
            if isinstance(must_cover, list):
                state["must_cover"] = [str(item) for item in must_cover if item]
            constraints = payload.get("constraints")
            if isinstance(constraints, dict):
                state["constraints"] = constraints

            if status == "ready":
                print("[Advisor] Clarification complete.")
                return

            user_reply = input("[You] ").strip()
            state["clarification_history"].append({"role": "user", "content": user_reply})

    def _assess_sufficiency(self, state: dict[str, Any]) -> dict[str, Any]:
        return self.model.analyze_json(
            "Assess whether available evidence is sufficient to answer startup policy consulting needs.\n"
            "Return JSON with keys: sufficient (boolean), gaps (list), search_queries (list).\n"
            f"Intent summary: {state['intent_summary']}\n"
            f"Must cover: {state['must_cover']}\n"
            f"Constraints: {state['constraints']}\n"
            f"Evidence snippets: {state['evidence'][:8]}"
        )

    def _collect_sources_and_evidence(self, state: dict[str, Any], queries: list[str]) -> None:
        print(f"[Advisor] Discovering URLs for {len(queries)} query(s)...", flush=True)
        logger.info("Collecting sources for %s query(s).", len(queries))
        urls = self._discover_urls(queries)
        print(f"[Advisor] URL discovery returned {len(urls)} candidate(s).", flush=True)
        logger.info("URL discovery returned %s candidates.", len(urls))
        for url in urls[: self.config.max_sources]:
            if url in state["sources"]:
                continue
            print(f"[Advisor] Fetching source: {url}", flush=True)
            snippet = self._fetch_text_snippet(url)
            if not snippet:
                print(f"[Advisor] Skipped source (no readable content): {url}", flush=True)
                logger.warning("Skipped source due to empty content: %s", url)
                continue
            state["sources"].append(url)
            state["evidence"].append({"url": url, "snippet": snippet})
            print(f"[Advisor] Collected evidence from: {url}", flush=True)
            logger.info("Collected evidence from source: %s", url)

    def _discover_urls(self, queries: list[str]) -> list[str]:
        urls: list[str] = []
        try:
            from duckduckgo_search import DDGS
        except Exception:
            return urls
        with DDGS() as ddgs:
            for query in queries:
                for result in ddgs.text(query, max_results=5):
                    href = result.get("href")
                    if href and isinstance(href, str) and href.startswith("http"):
                        urls.append(href)
        # Deduplicate while preserving order
        deduped: list[str] = []
        seen: set[str] = set()
        for item in urls:
            if item in seen:
                continue
            seen.add(item)
            deduped.append(item)
        return deduped

    def _fetch_text_snippet(self, url: str) -> str:
        try:
            with httpx.Client(timeout=self.config.fetch_timeout_seconds) as client:
                response = client.get(url)
                response.raise_for_status()
                text = response.text
        except Exception:
            return ""

        # Minimal cleanup for LLM consumption; not for deterministic extraction.
        compact = " ".join(text.replace("\n", " ").split())
        return compact[:2000]

    def _build_answer(self, state: dict[str, Any]) -> str:
        payload = self.model.analyze_json(
            "Generate an actionable startup consulting recommendation report.\n"
            "Return JSON with keys: summary, recommended_actions (list), source_citations (list), "
            "known_gaps (list), next_questions (list).\n"
            f"Intent summary: {state['intent_summary']}\n"
            f"Must cover: {state['must_cover']}\n"
            f"Constraints: {state['constraints']}\n"
            f"Evidence: {state['evidence'][:12]}"
        )
        summary = str(payload.get("summary", "No summary generated."))
        actions = payload.get("recommended_actions") or []
        citations = payload.get("source_citations") or []
        gaps = payload.get("known_gaps") or []
        output_lines = [f"Summary: {summary}", ""]
        if actions:
            output_lines.append("Recommended actions:")
            output_lines.extend([f"- {item}" for item in actions])
            output_lines.append("")
        if citations:
            output_lines.append("Sources:")
            output_lines.extend([f"- {item}" for item in citations])
            output_lines.append("")
        if gaps:
            output_lines.append("Known gaps:")
            output_lines.extend([f"- {item}" for item in gaps])
        return "\n".join(output_lines).strip()
