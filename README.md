# NEOXLINK-SDK

Open-source core contracts, deduplication, matching primitives, and Python SDK client for the NEOXLINK platform.

## Install

```bash
pip install -e .
```

## Package Contents

### `core/` - Shared Contracts

- `schema.py` - Canonical StructuredRecordV1 Pydantic model (extraction output contract)
- `dedup.py` - Text normalization, SHA-256 hashing, SimHash fingerprinting, Hamming distance
- `matching.py` - Weighted multi-feature scoring for demand/supply matching

### `neoxlink_sdk/` - Python SDK Client

Thin HTTP client for agent integration:

```python
from neoxlink_sdk import NeoXlinkClient

client = NeoXlinkClient(base_url="https://your-server.com", api_key="ak_live_xxx")

# Submit entry
result = client.submit_entry("Need 5000 kraft boxes in Shenzhen", entry_kind="demand")

# Get structured entry
entry = client.get_entry(result["raw_entry_id"])

# Search
hits = client.search("packaging supplier Shenzhen", entry_kind="supply", top_k=10)
```

## License

MIT
