# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Typed output module at `neoxlink_sdk.typed_outputs` with strict Pydantic v2 validation.
- MkDocs configuration and starter docs for quickstart and API reference.
- Benchmark workflow and script for PR-level performance visibility.
- Publishing workflow alias (`publish.yml`) for tag-triggered PyPI release.

### Changed
- Optional dependencies now expose `core`, `mcp`, `matching`, `dev`, and `all` tiers.
- Pipeline sync/async internals now share helper logic via `pipeline_core`.
