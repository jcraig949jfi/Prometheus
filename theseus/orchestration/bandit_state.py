"""Bandit history persistence across daemon invocations.

Without this, each `python -m theseus.daemon` invocation reseeds the
bandit with empty history. Cross-fire learning is impossible — the
bandit's yield-driven selection only matters within a single
multi-batch run, not across fires. With persistence:

  Fire #N picks → batch metrics → bandit.update(per_generator)
                              → save_history(bandit) at end
  Fire #N+1   load_history(bandit) on start → bandit.select knows
                              N fires' worth of yield data → picks
                              high-yield generators preferentially

Storage: theseus/orchestration/bandit_history.json
Schema:  {"version": 1, "yield_scores": {gid: [scores...]}}

The history is a flat list of yield_scores per generator. Fire-N
identity is not tracked (we don't need it for the bandit's mean +
UCB formula).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from theseus.config import THESEUS_ROOT


BANDIT_HISTORY_PATH = THESEUS_ROOT / "orchestration" / "bandit_history.json"
SCHEMA_VERSION = 1


def load_history(path: Path = BANDIT_HISTORY_PATH) -> Dict[str, List[float]]:
    """Load persisted bandit history (yield_scores per generator).

    Returns empty dict if file missing or unparseable (fail-soft).
    """
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    if payload.get("version") != SCHEMA_VERSION:
        return {}
    scores = payload.get("yield_scores")
    if not isinstance(scores, dict):
        return {}
    # Sanitize: ensure values are list[float]
    out: Dict[str, List[float]] = {}
    for gid, vals in scores.items():
        if not isinstance(gid, str):
            continue
        if not isinstance(vals, list):
            continue
        out[gid] = [float(v) for v in vals if isinstance(v, (int, float))]
    return out


def save_history(
    history: Dict[str, List[float]],
    path: Path = BANDIT_HISTORY_PATH,
) -> None:
    """Persist bandit yield-score history. Best-effort; logs on error."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "version": SCHEMA_VERSION,
        "yield_scores": {gid: list(vals) for gid, vals in history.items()},
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, sort_keys=True, indent=2)
        # Atomic replace (cross-platform-ish).
        tmp.replace(path)
    except OSError as e:
        print(
            f"[bandit_state] save_history failed (non-fatal): {e}",
        )
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def hydrate_bandit(bandit, path: Path = BANDIT_HISTORY_PATH) -> int:
    """Load persisted history into the bandit's _history dict.

    Returns the number of yield-score entries loaded (across all gens).
    Works with both YieldProportionalBandit and EpsilonGreedyBandit —
    both store history as Dict[str, List[float]] under the same name.
    """
    persisted = load_history(path)
    if not persisted:
        return 0
    n = 0
    for gid, scores in persisted.items():
        bandit._history.setdefault(gid, []).extend(scores)
        n += len(scores)
    return n


def persist_bandit(bandit, path: Path = BANDIT_HISTORY_PATH) -> None:
    """Persist the bandit's _history dict to disk."""
    save_history(bandit._history, path)
