from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ContributionType(str, Enum):
    PROMPT_IMPROVEMENT = "prompt_improvement"
    NEW_CONNECTOR = "new_data_connector"
    EXTRACTION_ENHANCEMENT = "extraction_logic_enhancement"
    TAXONOMY_IMPROVEMENT = "taxonomy_improvement"
    DATASET_CONTRIBUTION = "dataset_contribution"


class ContributionChecklist(BaseModel):
    schema_validation_passed: bool
    unit_tests_passed: bool
    benchmarks_passed: bool
    legal_compliance_confirmed: bool


class ContributionSubmission(BaseModel):
    title: str
    contribution_type: ContributionType
    description: str
    expected_impact: str
    test_results: str
    checklist: ContributionChecklist
    files_changed: list[str] = Field(default_factory=list)


def validate_submission(submission: ContributionSubmission) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not submission.checklist.schema_validation_passed:
        failures.append("schema validation not passed")
    if not submission.checklist.unit_tests_passed:
        failures.append("unit tests not passed")
    if not submission.checklist.benchmarks_passed:
        failures.append("benchmarks not passed")
    if not submission.checklist.legal_compliance_confirmed:
        failures.append("legal compliance not confirmed")
    return (len(failures) == 0, failures)
