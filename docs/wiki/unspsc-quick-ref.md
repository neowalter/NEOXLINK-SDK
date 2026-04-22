# UNSPSC quick reference (for NEOXLINK-SDK)

**UNSPSC** (United Nations Standard Products and Services Code) is the **commercial taxonomy** this SDK uses to map natural language to **Code + Name** pairs — not a chat label, but a **B2B execution coordinate** shared by procurement, marketplaces, and compliance tooling.

## Why it matters here

- **Chat → transaction:** A buyer might say *“compliance help for our EU store launch”*; the SDK’s pipeline (preview, confirm, structured record) aims to carry **structured intent** and **UNSPSC** when applicable so downstream systems can act.  
- **Code + Name:** A valid segment code is **8 digits**; `UNSPSCClassification` in the public models enforces the pattern.  
- **Heuristic path:** The open-source `HeuristicModelAdapter` maps text to **candidate** UNSPSC codes for demos and tests; production flows typically use the hosted API and/or your own model adapter.

## Mapping flow (simplified)

1. **Input** — free text (demand/supply).  
2. **Parse / preview** — `ParsedIntent` + optional taxonomy candidates.  
3. **Normalize** — `NormalizedIntent` with `unspsc_code` and `unspsc_name`.  
4. **Match / resolve** — ranking and fulfillment on the same code axis.

## Pointers in this repo

| Topic | Where |
| --- | --- |
| UNSPSC data helpers | `neoxlink_sdk/unspsc.py` |
| Engine stages | `neoxlink_sdk/engine.py` — `ProcurementIntentEngine` |
| HTTP preview objects | `neoxlink_sdk/models.py` — `UNSPSCClassification`, `ParsedPreview` |
| Example | `examples/04_procurement_intent_engine.py` |

## Further reading

- [UNSPSC official site](https://www.unspsc.org/) (taxonomy ownership and updates).
