---
title: Home
description: NEOXLINK SDK — natural language to structured intent for agents and systems.
---

<section class="nx-hero" aria-label="NEOXLINK SDK overview">
  <div class="nx-hero__inner">
    <div class="nx-hero__badge">Developer preview</div>
    <h1>NEOXLINK SDK</h1>
    <p class="nx-lead">Turn natural-language requirements into <strong>structured, machine-readable intent</strong> — UNSPSC normalization, typed outputs, and MCP — so agents and backends can route, confirm, and execute without guessing.</p>
    <p class="nx-hero-actions">
      <a href="quickstart/" class="md-button md-button--primary">Get started</a>
      <a href="api/neoxlink_sdk/" class="md-button">API reference</a>
    </p>
    <div class="nx-flow" role="list" aria-label="Pipeline">
      <span class="nx-pill" role="listitem">Natural language</span>
      <span class="nx-arrow" aria-hidden="true">→</span>
      <span class="nx-pill" role="listitem">Structured preview</span>
      <span class="nx-arrow" aria-hidden="true">→</span>
      <span class="nx-pill" role="listitem">Confirm / store</span>
      <span class="nx-arrow" aria-hidden="true">→</span>
      <span class="nx-pill" role="listitem">Resolve &amp; integrate</span>
    </div>
  </div>
</section>

## First run

!!! tip "5-minute path"

    Follow these steps, then open **[Quickstart](quickstart.md)** for install variants and next calls.

<ol class="nx-steps">
  <li><strong>Install:</strong> <code>pip install neoxlink</code></li>
  <li><strong>Import:</strong> <code>from neoxlink import SDK</code></li>
  <li><strong>Run:</strong> <code>parse_preview(...)</code> with your first requirement string.</li>
</ol>

### Example

=== "Python"

    ```python
    from neoxlink import SDK

    sdk = SDK(base_url="http://localhost:8000", api_key="demo")
    preview = sdk.parse_preview("Need AI-ready procurement intake workflow")
    print(preview)
    ```

=== "What you get"

    A **Structured Preview** object your app or agent can inspect, edit, and confirm before persisting or handoff.

## Capabilities

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

<div class="nx-footer-cta" markdown="1">
<span class="nx-footer-cta__label">Ecosystem &amp; install</span>
[GitHub](https://github.com/neowalter/NEOXLINK-SDK){ .md-button }
[PyPI](https://pypi.org/project/neoxlink/){ .md-button }
[Quickstart](quickstart.md){ .md-button .md-button--primary }
</div>
