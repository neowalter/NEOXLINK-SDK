from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from .client import NeoXlinkClient


class CreditLimitExceeded(RuntimeError):
    """Raised when a user does not have enough credits."""


class CreditPolicy(BaseModel):
    """Configurable credit policy for SDK-side metering."""

    free_daily_llm_extractions: int = Field(default=5, ge=0)
    search_credit_cost: int = Field(default=1, ge=0)
    match_credit_cost: int = Field(default=1, ge=0)
    llm_extraction_credit_cost: int = Field(default=2, ge=0)


class CreditAccount(BaseModel):
    user_id: str
    tier: Literal["free", "pro", "enterprise"] = "free"
    credits_balance: int = Field(default=0, ge=0)
    daily_free_llm_extractions_used: int = Field(default=0, ge=0)
    daily_window: date = Field(default_factory=lambda: datetime.now(UTC).date())
    total_search_count: int = Field(default=0, ge=0)
    total_match_count: int = Field(default=0, ge=0)
    total_llm_extraction_count: int = Field(default=0, ge=0)


class CreditLedger:
    """In-memory credit ledger for SDK clients.

    Applications may persist account snapshots externally if needed.
    """

    def __init__(self, policy: CreditPolicy | None = None) -> None:
        self.policy = policy or CreditPolicy()
        self._accounts: dict[str, CreditAccount] = {}

    def ensure_account(
        self,
        user_id: str,
        *,
        tier: Literal["free", "pro", "enterprise"] = "free",
        starting_credits: int = 0,
    ) -> CreditAccount:
        account = self._accounts.get(user_id)
        if account is None:
            account = CreditAccount(user_id=user_id, tier=tier, credits_balance=max(0, starting_credits))
            self._accounts[user_id] = account
        else:
            self._rotate_daily_window(account)
        return account

    def get_account(self, user_id: str) -> CreditAccount:
        return self.ensure_account(user_id)

    def grant_credits(self, user_id: str, amount: int) -> CreditAccount:
        if amount < 0:
            raise ValueError("amount must be >= 0")
        account = self.ensure_account(user_id)
        account.credits_balance += amount
        return account

    def charge_search(self, user_id: str) -> CreditAccount:
        account = self.ensure_account(user_id)
        self._debit(account, self.policy.search_credit_cost, "search")
        account.total_search_count += 1
        return account

    def charge_match(self, user_id: str) -> CreditAccount:
        account = self.ensure_account(user_id)
        self._debit(account, self.policy.match_credit_cost, "matching")
        account.total_match_count += 1
        return account

    def charge_llm_extraction(self, user_id: str, *, use_own_model: bool = False) -> CreditAccount:
        account = self.ensure_account(user_id)
        account.total_llm_extraction_count += 1
        if use_own_model:
            return account

        if account.tier == "free":
            if account.daily_free_llm_extractions_used < self.policy.free_daily_llm_extractions:
                account.daily_free_llm_extractions_used += 1
                return account

        self._debit(account, self.policy.llm_extraction_credit_cost, "llm_extraction")
        return account

    def _debit(self, account: CreditAccount, amount: int, reason: str) -> None:
        if amount <= 0:
            return
        if account.credits_balance < amount:
            raise CreditLimitExceeded(
                f"Insufficient credits for {reason}. "
                f"Required={amount}, available={account.credits_balance}"
            )
        account.credits_balance -= amount

    def _rotate_daily_window(self, account: CreditAccount) -> None:
        today = datetime.now(UTC).date()
        if account.daily_window != today:
            account.daily_window = today
            account.daily_free_llm_extractions_used = 0


class MeteredNeoXlinkClient(NeoXlinkClient):
    """NeoXlink client wrapper with built-in credit accounting."""

    def __init__(
        self,
        *,
        user_id: str,
        ledger: CreditLedger,
        default_use_own_model: bool = False,
        **client_kwargs: Any,
    ) -> None:
        super().__init__(**client_kwargs)
        self.user_id = user_id
        self.ledger = ledger
        self.default_use_own_model = default_use_own_model

    def parse_entry(
        self,
        raw_text: str,
        entry_kind: str = "demand",
        metadata: dict[str, Any] | None = None,
        use_own_model: bool = False,
    ) -> dict[str, Any]:
        byom = use_own_model or self.default_use_own_model
        self.ledger.charge_llm_extraction(self.user_id, use_own_model=byom)
        return super().parse_entry(raw_text=raw_text, entry_kind=entry_kind, metadata=metadata, use_own_model=byom)

    def search(
        self,
        query: str,
        filters: dict[str, list[str]] | None = None,
        entry_kind: str | None = None,
        top_k: int = 20,
    ) -> dict[str, Any]:
        self.ledger.charge_search(self.user_id)
        self.ledger.charge_match(self.user_id)
        return super().search(query=query, filters=filters, entry_kind=entry_kind, top_k=top_k)
