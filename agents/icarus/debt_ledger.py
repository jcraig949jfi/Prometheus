"""
Icarus Skeptic/Contract debt ledger.

Per the 2026-05-28 review point #2: a minority report or contract violation
that does not block promotion must become "debt with teeth." When a cycle
promotes despite a Skeptic minority position or a deterministic Contract Lens
violation, the concern is recorded as an OPEN DEBT. The next cycle's Generator
is then FORCED to either write a regression test for it or explicitly retire
it with evidence. This turns the Skeptic from a commentator into a gradient
emitter.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path(r"D:\Prometheus\agents\icarus\state\debt_ledger.json")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> list[dict]:
    if not LEDGER.exists():
        return []
    try:
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(debts: list[dict]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(debts, indent=2, default=str), encoding="utf-8")


def _debt_id(concern: str, cycle: int) -> str:
    h = hashlib.sha1(f"{concern}".encode("utf-8")).hexdigest()[:10]
    return f"debt_{h}"


def open_debts() -> list[dict]:
    """Return all currently-open debts (for surfacing to the next Generator)."""
    return [d for d in _load() if d.get("status") == "open"]


def record_debt(
    cycle: int,
    concern: str,
    regression_test_to_write: str | None,
    source: str,          # "skeptic" | "contract"
    future_tier_risk: list[str] | None = None,
) -> dict | None:
    """Record a new open debt when a cycle promotes despite a concern.
    Deduplicates by concern hash -- the same recurring concern does not
    spawn N debts."""
    if not concern:
        return None
    debts = _load()
    did = _debt_id(concern, cycle)
    for d in debts:
        if d.get("debt_id") == did and d.get("status") == "open":
            # already tracked; bump the recurrence counter
            d["recurrences"] = d.get("recurrences", 1) + 1
            d["last_seen_cycle"] = cycle
            _save(debts)
            return d
    debt = {
        "debt_id": did,
        "cycle_created": cycle,
        "last_seen_cycle": cycle,
        "concern": concern[:500],
        "regression_test_to_write": regression_test_to_write,
        "source": source,
        "future_tier_risk": future_tier_risk or [],
        "status": "open",
        "recurrences": 1,
        "created_at": _now_iso(),
    }
    debts.append(debt)
    _save(debts)
    return debt


def close_debt(debt_id: str, cycle: int, how: str) -> None:
    """Mark a debt closed. how is 'regression_test_written' or
    'retired_with_evidence'."""
    debts = _load()
    for d in debts:
        if d.get("debt_id") == debt_id and d.get("status") == "open":
            d["status"] = "closed"
            d["closed_cycle"] = cycle
            d["closed_how"] = how
            d["closed_at"] = _now_iso()
    _save(debts)


def attempt_auto_close(
    cycle: int,
    tests_run_before: int,
    tests_run_after: int,
    integrator_retired: list[str] | None = None,
) -> list[str]:
    """Best-effort debt closure after a cycle.

    Two paths:
      1. Explicit retirement: the Integrator named debt_ids it retired with
         evidence (integrator_retired list).
      2. Test-addition heuristic: if the cycle added tests (tests_run grew)
         and there are open debts, close the OLDEST open debt as
         'regression_test_written'. Conservative: one debt per cycle.

    Returns the list of debt_ids closed this cycle.
    """
    closed = []
    # Path 1: explicit retirement
    for did in (integrator_retired or []):
        close_debt(did, cycle, how="retired_with_evidence")
        closed.append(did)

    # Path 2: test-addition heuristic
    if tests_run_after > tests_run_before:
        remaining = [d for d in open_debts() if d["debt_id"] not in closed]
        if remaining:
            oldest = min(remaining, key=lambda d: d.get("cycle_created", 0))
            close_debt(oldest["debt_id"], cycle, how="regression_test_written")
            closed.append(oldest["debt_id"])

    return closed


def ledger_summary() -> dict:
    debts = _load()
    return {
        "total": len(debts),
        "open": sum(1 for d in debts if d.get("status") == "open"),
        "closed": sum(1 for d in debts if d.get("status") == "closed"),
        "open_debts": open_debts(),
    }
