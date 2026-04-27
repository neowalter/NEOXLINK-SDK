# Quickstart

## Install

```bash
pip install neoxlink
```

## First API call

```python
from neoxlink import SDK

sdk = SDK(base_url="http://localhost:8000", api_key="demo")
result = sdk.parse_preview("Need a supplier for industrial sensors")
print(result)
```

## Optional extras

- MCP support: `pip install "neoxlink[mcp]"`
- Matching helpers: `pip install "neoxlink[matching]"`
- Full bundle: `pip install "neoxlink[all]"`
