# Quickstart

!!! abstract "What you will do"

    Install the package, point the client at your **NEOXLINK** base URL, then call **`parse_preview`** with a natural-language requirement string.

## Install

=== "pip"

    ```bash
    pip install neoxlink
    ```

=== "pip (extras later)"

    ```bash
    pip install neoxlink
    # optional: mcp, matching, or all — see below
    ```

## First API call

```python
from neoxlink import SDK

sdk = SDK(base_url="http://localhost:8000", api_key="demo")
result = sdk.parse_preview("Need a supplier for industrial sensors")
print(result)
```

## Optional extras

| Bundle | Command |
| --- | --- |
| MCP | `pip install "neoxlink[mcp]"` |
| Matching | `pip install "neoxlink[matching]"` |
| Full | `pip install "neoxlink[all]"` |

!!! tip "Next"

    Read **[Typed outputs](typed-outputs.md)** for strict Pydantic validation and **[API](api/neoxlink_sdk.md)** for the full module surface.
