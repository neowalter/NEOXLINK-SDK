from __future__ import annotations

import json
import time
from pathlib import Path

from neoxlink_sdk.typed_outputs import parse_typed_output


def main() -> None:
    sample_path = Path(__file__).with_name("intent_parsing") / "sample_cases.jsonl"
    rows = [json.loads(line) for line in sample_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    start = time.perf_counter()
    parsed = 0
    for row in rows:
        payload = {
            "intent": row.get("query", "intent"),
            "confidence": 0.9,
            "tags": ["benchmark"],
            "attributes": {"source": "sample_cases"},
        }
        parse_typed_output(payload)
        parsed += 1
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(json.dumps({"cases": parsed, "elapsed_ms": round(elapsed_ms, 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
