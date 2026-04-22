# Taxonomy assets

The canonical UNSPSC subset for this repository lives in the Python package as
[`neoxlink_sdk/data/unspsc_catalog.json`](../neoxlink_sdk/data/unspsc_catalog.json)
(single source of truth for both `neoxlink_sdk.unspsc` and the open-source
`TaxonomyLoader` / `load_default_taxonomy_nodes` helpers).

The former `unspsc_open_source.json` in this directory was removed to avoid
drift. Examples should import `load_default_taxonomy_nodes()` or read the
packaged JSON path via `neoxlink_sdk.catalog.default_unspsc_catalog_path()`.
