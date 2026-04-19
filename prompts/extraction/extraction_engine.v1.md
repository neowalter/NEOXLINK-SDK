# extraction_engine.v1

## Goal
Extract normalized request fields from noisy public text.

## Required fields
- product_or_service
- constraints
- confidence

## Quality rules
- Return valid JSON only.
- Keep unknown values null rather than fabricated.
- Preserve original user meaning.
