# NEOXLINK SDK

NEOXLINK SDK turns natural-language requirements into structured intent so you can route demand/supply workflows with typed outputs.

## 5-minute path

1. Install: `pip install neoxlink`
2. Import: `from neoxlink import SDK`
3. Run first call:

```python
from neoxlink import SDK

sdk = SDK(base_url="http://localhost:8000", api_key="demo")
preview = sdk.parse_preview("Need AI-ready procurement intake workflow")
print(preview)
```
