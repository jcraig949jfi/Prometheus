"""Residue revocation mechanism — Phase 1B ITER-39 seam primitive.

When a Phase 1A retrofit produces a new verdict that supersedes a
prior emission (e.g., G10 v2 BOCPD posterior replaces G10 v1
max/mean ratio on the same Lehmer cliff), the predecessor's ledger
row must be marked SUPERSEDED so Layer 2's accumulator does not
double-count the same signal.

Per Doctrine v1.0 §"the seam" + _residue_eligibility.py CRITERION_
FALSIFIES_PRIOR: revocation is the action taken when the eligibility
gate flags a verdict as prior-falsifying. Without revocation, the
accumulator carries stale residue that distorts cross-emission
navigation.

## Contract

Revocations are APPEND-ONLY. We do not delete or mutate ledger rows;
we record a separate `RevocationRecord(row_id, superseded_by, reason,
ts)` per revocation. Layer 2 queries filter via `is_revoked(row_id)`
or `filter_active(rows)`.

A single row can be revoked at most ONCE -- a second revoke call
for the same row_id is a no-op (idempotent) unless `reason` or
`superseded_by` differ, in which case we warn and append a second
record (multi-revocation is a substrate-anomaly worth surfacing,
not silently overwriting).

## What this primitive is NOT

- NOT a deletion mechanism. The original row stays in the ledger
  for audit. Only the query layer filters.
- NOT a quality judgment. Revoking row R does not say R's verdict
  was wrong; it says R has been SUPERSEDED by a sharper successor.
  Sometimes the successor will be revoked in turn.
- NOT load-bearing for Layer 1. Layer 1 still computes verdicts
  independently of revocation state. Revocation is a Layer 2 hygiene
  primitive.

## Integration contract

The daemon (in a future iteration -- this primitive is storage-
backend independent) will:
  1. After a new claim's eligibility verdict shows CRITERION_
     FALSIFIES_PRIOR fired, look up the prior ledger rows that
     match the input_signature.
  2. Call revoke(prior_row_id, superseded_by=new_row_id,
     reason=<eligibility detail>) for each.
  3. Layer 2 queries use filter_active() to skip revoked rows.

This module is daemon-call-site agnostic so it can be exercised in
isolation and so the storage backend (in-memory for tests, file-
based for production, eventually database-backed) is pluggable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Optional


@dataclass(frozen=True)
class RevocationRecord:
    """One revocation event.

    Attributes:
        row_id: the ledger row being revoked.
        superseded_by: the ledger row that supersedes it (the new
            successor emission). May be None if revocation is for
            non-supersession reasons (e.g., manual override, audit
            disqualification) -- caller specifies.
        reason: human-readable rationale for the revocation. Used
            in audit logs and exhaust-pool reports.
        ts: ISO-8601 UTC timestamp of the revocation.
    """
    row_id: str
    superseded_by: Optional[str]
    reason: str
    ts: str


@dataclass
class RevocationRegistry:
    """In-memory append-only revocation log.

    The production daemon will wire this to a persistent backend
    (likely the same JSONL the kill_ledger uses, with a separate
    revocations file). For tests + Phase 1B MVP, in-memory is
    sufficient.

    All mutations go through methods; the records list is treated
    as append-only.
    """
    records: list[RevocationRecord] = field(default_factory=list)

    def revoke(
        self,
        row_id: str,
        *,
        superseded_by: Optional[str] = None,
        reason: str = "",
    ) -> RevocationRecord:
        """Append a revocation record for row_id.

        If row_id was already revoked with IDENTICAL superseded_by
        and reason, the call is a no-op (returns the existing record)
        to keep daemon retries idempotent. If row_id was revoked
        with DIFFERENT superseded_by or reason, append a second
        record (multi-revocation is a substrate-anomaly signal).
        """
        if not row_id:
            raise ValueError("revoke: row_id must be a non-empty string")
        existing = [r for r in self.records if r.row_id == row_id]
        for r in existing:
            if r.superseded_by == superseded_by and r.reason == reason:
                return r  # idempotent
        ts = datetime.now(timezone.utc).isoformat()
        rec = RevocationRecord(
            row_id=row_id,
            superseded_by=superseded_by,
            reason=reason,
            ts=ts,
        )
        self.records.append(rec)
        return rec

    def is_revoked(self, row_id: str) -> bool:
        """True iff row_id has at least one revocation record."""
        return any(r.row_id == row_id for r in self.records)

    def revocations_for(self, row_id: str) -> list[RevocationRecord]:
        """Return all revocation records for row_id (append-only;
        ordered by insertion = chronological)."""
        return [r for r in self.records if r.row_id == row_id]

    def filter_active(self, rows: Iterable[dict]) -> list[dict]:
        """Return rows whose 'row_id' (or 'id') is NOT revoked.

        Layer 2 query helper. Accepts any iterable of dicts; uses
        the 'row_id' key if present, else 'id'. Rows without an
        identifiable id are passed through (presumed un-revokable).
        """
        revoked_ids = {r.row_id for r in self.records}
        out = []
        for row in rows:
            rid = row.get("row_id") or row.get("id")
            if rid is None or rid not in revoked_ids:
                out.append(row)
        return out

    def superseded_by(self, row_id: str) -> Optional[str]:
        """Return the most recent superseded_by for row_id, or None
        if not revoked or revoked without supersession."""
        recs = self.revocations_for(row_id)
        if not recs:
            return None
        # Most recent record wins
        return recs[-1].superseded_by

    def __len__(self) -> int:
        return len(self.records)


# Module-level default registry. The daemon may import this directly
# for the simple single-process case; tests construct their own
# RevocationRegistry instances for isolation.
DEFAULT_REGISTRY = RevocationRegistry()


def revoke(
    row_id: str,
    *,
    superseded_by: Optional[str] = None,
    reason: str = "",
) -> RevocationRecord:
    """Module-level convenience: revoke against DEFAULT_REGISTRY."""
    return DEFAULT_REGISTRY.revoke(
        row_id, superseded_by=superseded_by, reason=reason
    )


def is_revoked(row_id: str) -> bool:
    """Module-level convenience: query DEFAULT_REGISTRY."""
    return DEFAULT_REGISTRY.is_revoked(row_id)


def filter_active(rows: Iterable[dict]) -> list[dict]:
    """Module-level convenience: filter via DEFAULT_REGISTRY."""
    return DEFAULT_REGISTRY.filter_active(rows)
