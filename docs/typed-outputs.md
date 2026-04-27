# Typed Outputs

!!! info "Module"

    `neoxlink_sdk.typed_outputs` provides **strict Pydantic v2** validation for LLM structured responses, so you can treat model output as data, not free text.

```python
from neoxlink_sdk.typed_outputs import parse_typed_output

payload = {
    "intent": "match supplier",
    "confidence": 0.92,
    "tags": ["MCP", "agent"],
    "attributes": {"region": "APAC"},
}
typed = parse_typed_output(payload)
print(typed.model_dump())
```
