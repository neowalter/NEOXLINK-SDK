---
title: Home
description: NEOXLINK SDK — natural language to structured intent for agents and systems.
---

<div class="nx-hero" markdown="1">

# NEOXLINK SDK

<p class="nx-lead">Turn natural-language requirements into <strong>structured, machine-readable intent</strong> — UNSPSC normalization, typed outputs, and MCP — so agents and backends can route, confirm, and execute without guessing.</p>

<div class="nx-hero-actions" markdown="1">

[Quickstart](quickstart.md){ .md-button .md-button--primary }
[Python API](api/neoxlink_sdk.md){ .md-button }

</div>

</div>

## 5-minute path

1. **Install:** `pip install neoxlink`
2. **Import:** `from neoxlink import SDK`
3. **First call:**

```python
from neoxlink import SDK

sdk = SDK(base_url="http://localhost:8000", api_key="demo")
preview = sdk.parse_preview("Need AI-ready procurement intake workflow")
print(preview)
```

<div class="nx-features">

  <div class="nx-feature">
    <h3>Structured preview</h3>
    <p>LLM-refined structure before anything is committed downstream.</p>
  </div>

  <div class="nx-feature">
    <h3>UNSPSC-ready</h3>
    <p>Code + name alignment when classifying goods and services.</p>
  </div>

  <div class="nx-feature">
    <h3>Agent-native</h3>
    <p>MCP tools and skill adapters for interoperable orchestration.</p>
  </div>

</div>

---

<div class="nx-hero-actions" markdown="1">

[Repository on GitHub](https://github.com/neowalter/NEOXLINK-SDK){ .md-button }
[PyPI package](https://pypi.org/project/neoxlink/){ .md-button }

</div>
