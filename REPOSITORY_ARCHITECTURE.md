# Repository Architecture

## Module One: Intent Parsing
- code: `neoxlink_sdk/open_source/intent_parsing.py`
- prompts: `prompts/intent/`
- benchmark data: `benchmarks/intent_parsing/`

## Module Two: Taxonomy Mapping
- code: `neoxlink_sdk/open_source/taxonomy_mapping.py`
- taxonomy assets (source of truth): `neoxlink_sdk/data/unspsc_catalog.json` (see [taxonomy/README.md](taxonomy/README.md) for the removed duplicate path)

## Module Three: Data Connectors
- code: `neoxlink_sdk/open_source/connectors.py`
- unified interface: `PublicDataConnector`

## Module Four: Extraction Engine
- code: `neoxlink_sdk/open_source/extraction_engine.py`
- prompts: `prompts/extraction/`

## Module Five: Matching Engine
- code: `neoxlink_sdk/open_source/matching_engine.py`
- scoring framework: `ScoringPolicy` (no fixed proprietary weights)

## Module Six: Data Schema
- code: `neoxlink_sdk/open_source/schemas.py`
- version marker: `SCHEMA_VERSION`

## Module Seven: Evaluation and Benchmarking
- code: `neoxlink_sdk/open_source/evaluation.py`
- datasets: `benchmarks/`

## Module Eight: Contribution System
- code: `neoxlink_sdk/open_source/contribution.py`
- tooling: `scripts/validate_contribution.py`
- templates: `.github/PULL_REQUEST_TEMPLATE.md`
