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
Schema v2 (Fire #83):
    {
      "version": 2,
      "yield_scores": {gid: [scores...]},
      "fire_counter": int,           # total fires bandit has run
      "last_picked_at": {gid: int}   # fire_counter at last pick
    }

Why v2 — the "finite refillable reservoir" pattern (Fire #80-82):
- Fire #66: f4 picked, contributed 175 templates
- Fire #80: f4 re-picked, contributed 0 (locally exhausted)
- Same trajectory observed for e2 (#79→#81) and g4 (#65→#82)

Each explorer gen has a deep-but-finite claim space at any moment.
Re-picking soon after a burst wastes the slot. v2 tracks per-gen
recency so the bandit can downweight recently-bursted gens.

Backwards compatible: v1 history files load fine; fire_counter
starts at 0, last_picked_at defaults to empty.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from theseus.config import THESEUS_ROOT


BANDIT_HISTORY_PATH = THESEUS_ROOT / "orchestration" / "bandit_history.json"
SCHEMA_VERSION = 2


def load_history(path: Path = BANDIT_HISTORY_PATH) -> Dict[str, List[float]]:
    """Load persisted bandit history (yield_scores per generator).

    Returns empty dict if file missing or unparseable (fail-soft).
    Accepts v1 and v2 schemas.
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
    # Accept both v1 and v2 (v2 just adds fire_counter + last_picked_at)
    if payload.get("version") not in (1, 2):
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


def load_pick_recency(
    path: Path = BANDIT_HISTORY_PATH,
) -> tuple[int, Dict[str, int]]:
    """Load fire counter + last-picked-at map. Returns (counter, {gid: fire}).

    For v1 files (no recency data) returns (0, {}).
    """
    if not path.exists():
        return 0, {}
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return 0, {}
    if not isinstance(payload, dict):
        return 0, {}
    counter = payload.get("fire_counter", 0)
    if not isinstance(counter, int):
        counter = 0
    last_picked = payload.get("last_picked_at", {})
    if not isinstance(last_picked, dict):
        last_picked = {}
    # Sanitize
    out: Dict[str, int] = {}
    for gid, fire_n in last_picked.items():
        if isinstance(gid, str) and isinstance(fire_n, int):
            out[gid] = fire_n
    return counter, out


def fires_since_last_pick(
    gen_id: str,
    counter: int,
    last_picked: Dict[str, int],
) -> int:
    """Return number of fires since this gen was last picked.
    Returns a large number (1000) if never picked — treat as fresh.
    """
    if gen_id not in last_picked:
        return 1000  # never picked → maximally fresh
    return max(0, counter - last_picked[gen_id])


def save_history(
    history: Dict[str, List[float]],
    path: Path = BANDIT_HISTORY_PATH,
    fire_counter: int = 0,
    last_picked_at: Dict[str, int] | None = None,
) -> None:
    """Persist bandit yield-score history + recency. Best-effort.

    fire_counter + last_picked_at are optional for backwards compat;
    callers that don't track them get v1-equivalent semantics.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "version": SCHEMA_VERSION,
        "yield_scores": {gid: list(vals) for gid, vals in history.items()},
        "fire_counter": fire_counter,
        "last_picked_at": dict(last_picked_at) if last_picked_at else {},
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


def persist_bandit(
    bandit,
    path: Path = BANDIT_HISTORY_PATH,
    picked_this_fire: List[str] | None = None,
) -> None:
    """Persist the bandit's _history dict to disk, plus update recency.

    `picked_this_fire` is the list of gen_ids selected by the bandit
    this fire. Each gets its `last_picked_at` updated to the new
    `fire_counter` (incremented by 1 from the persisted value).
    """
    # Load current recency state, increment counter, mark picks
    counter, last_picked = load_pick_recency(path)
    counter += 1
    if picked_this_fire:
        for gid in picked_this_fire:
            last_picked[gid] = counter
    save_history(
        bandit._history,
        path,
        fire_counter=counter,
        last_picked_at=last_picked,
    )
