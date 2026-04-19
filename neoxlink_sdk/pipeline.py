from __future__ import annotations

from typing import Any, Callable

from .client import NeoXlinkClient
from .models import (
    ConfirmedEntry,
    ParseDraft,
    ParsedPreview,
    PipelineOutcome,
    ResolveResult,
)

ConfirmDecision = bool | dict[str, Any]
ConfirmHandler = Callable[[ParseDraft], ConfirmDecision]


class StructuredSubmissionPipeline:
    """Orchestrates parse -> confirm -> resolve for SDK consumers."""

    def __init__(self, client: NeoXlinkClient) -> None:
        self.client = client

    def parse(
        self,
        text: str,
        entry_kind: str = "demand",
        metadata: dict[str, Any] | None = None,
        use_own_model: bool = False,
    ) -> ParseDraft:
        parse_metadata = dict(metadata or {})
        parse_metadata.setdefault("billing", {})
        if isinstance(parse_metadata["billing"], dict):
            parse_metadata["billing"].setdefault("use_own_model", use_own_model)
        payload = self.client.parse_entry(
            raw_text=text,
            entry_kind=entry_kind,
            metadata=parse_metadata,
            use_own_model=use_own_model,
        )
        preview = ParsedPreview.model_validate(payload["preview"])
        return ParseDraft(
            confirmation_token=str(payload["confirmation_token"]),
            preview=preview,
            parser_version=payload.get("parser_version"),
        )

    def confirm(self, draft: ParseDraft, overrides: dict[str, Any] | None = None) -> ConfirmedEntry:
        confirm_overrides = dict(overrides or {})
        # Standardize category metadata with UNSPSC code/name for both demand and supply.
        if draft.preview.unspsc:
            confirm_overrides.setdefault("unspsc_code", draft.preview.unspsc.code)
            confirm_overrides.setdefault("unspsc_name", draft.preview.unspsc.name)
        payload = self.client.confirm_entry(confirmation_token=draft.confirmation_token, overrides=confirm_overrides)
        structured_data = payload.get("structured_data")
        if isinstance(structured_data, dict):
            try:
                structured_data = ParsedPreview.model_validate(structured_data)
            except Exception:
                pass
        return ConfirmedEntry(
            raw_entry_id=str(payload["raw_entry_id"]),
            entry_kind=payload.get("entry_kind", draft.preview.entry_kind),
            status=payload.get("status"),
            structured_data=structured_data,
        )

    def resolve(self, raw_entry_id: str) -> ResolveResult:
        payload = self.client.resolve_entry(raw_entry_id=raw_entry_id)
        return ResolveResult.model_validate(payload)

    def run(
        self,
        text: str,
        entry_kind: str = "demand",
        metadata: dict[str, Any] | None = None,
        confirm_handler: ConfirmHandler | None = None,
        resolve_after_confirm: bool = True,
        use_own_model: bool = False,
    ) -> PipelineOutcome:
        draft = self.parse(text=text, entry_kind=entry_kind, metadata=metadata, use_own_model=use_own_model)
        decision: ConfirmDecision = True
        if confirm_handler is not None:
            decision = confirm_handler(draft)

        if decision is False:
            return PipelineOutcome(parse=draft, skipped_by_user=True)

        overrides = decision if isinstance(decision, dict) else {}
        confirmed = self.confirm(draft=draft, overrides=overrides)
        resolved = self.resolve(confirmed.raw_entry_id) if resolve_after_confirm else None
        return PipelineOutcome(parse=draft, confirmed=confirmed, resolve=resolved, skipped_by_user=False)
