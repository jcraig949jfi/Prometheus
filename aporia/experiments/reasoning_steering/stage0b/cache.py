"""Score-and-cache the in-band states' per-falsifier margin vectors (Stage 0b v0.3).

Scoring is ~55s/state (the falsifier battery), so the ~21 in-band states are scored
ONCE here and cached to disk; the flow builder + runner read the cache. The
orchestration (score_states) takes an injected scorer so it is unit-testable with a
mock; the real ~19-min batch runs via __main__ with the real Axis2DamageScorer.
"""
from __future__ import annotations

import json
from pathlib import Path

__all__ = ["score_states", "write_cache", "load_cache", "CACHE_PATH"]

CACHE_PATH = Path(__file__).with_name("stage0b_margin_cache.json")


def score_states(states, scorer) -> list:
    """Score each state's margin vector. `scorer` must have .margin_vector(coeffs, M).

    `states` is a list of objects with .coeffs, .mahler_measure, .name (InBandState).
    Returns a list of plain dicts (JSON-ready).
    """
    records = []
    for s in states:
        records.append({
            "coeffs": list(s.coeffs),
            "mahler_measure": float(s.mahler_measure),
            "name": s.name,
            "margins": dict(scorer.margin_vector(s.coeffs, s.mahler_measure)),
        })
    return records


def write_cache(records, path=CACHE_PATH) -> Path:
    path = Path(path)
    path.write_text(json.dumps(records, indent=2, sort_keys=True))
    return path


def load_cache(path=CACHE_PATH) -> list:
    return json.loads(Path(path).read_text())


if __name__ == "__main__":
    import time
    from aporia.experiments.reasoning_steering.stage0b.corpus import load_in_band_states
    from aporia.experiments.reasoning_steering.stage0b.damage import Axis2DamageScorer

    states = load_in_band_states()
    print(f"scoring {len(states)} in-band states ...")
    scorer = Axis2DamageScorer()
    t0 = time.time()
    recs = score_states(states, scorer)
    write_cache(recs)
    print(f"wrote {len(recs)} records to {CACHE_PATH} in {time.time()-t0:.0f}s")
