from __future__ import annotations

import json
import sys
from pathlib import Path

from neoxlink_sdk.open_source import ContributionSubmission, validate_submission


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_contribution.py <submission.json>")
        return 1
    path = Path(sys.argv[1])
    payload = json.loads(path.read_text())
    submission = ContributionSubmission.model_validate(payload)
    ok, failures = validate_submission(submission)
    if ok:
        print("Contribution validation: PASSED")
        return 0
    print("Contribution validation: FAILED")
    for item in failures:
        print(f"- {item}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
