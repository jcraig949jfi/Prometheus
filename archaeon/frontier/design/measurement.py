"""MEASUREMENT MUTATION (CALIBRATION_EPOCH-002): two population-level rulers added beside the eleven, unvalidated, run on
every archived generation from the segment observations and the T0 rows, and written into the receipts by the digest.
Nothing existing moves.

  population_shift   distance between the population fingerprint centroid at generation g and at g - k (k = 8 archived
                     generations), in units of the frozen spread -- a population moving as a whole with no exceptional
                     individual (the directive's fixture class the single-organism rulers cannot see)
  max_spike          reward_max rises by >= 2 bands between adjacent archived generations and falls back by >= 1 band
                     within 4 generations -- the boom-bust shape

Both are computed by the digest and by `measure(out)` here from a segment output; when a run's spec lists
"measurements": ["population_shift", "max_spike"] the scheduler writes their series into the receipt.
"""
from __future__ import annotations

import math
from typing import Dict, List

from archaeon.campaign6.observatory.fingerprint import numeric_vector

BAND = 1 / 16


def population_shift(out: dict, spread: Dict[str, float], k: int = 8) -> List[dict]:
    """Centroid of numeric fingerprint fields per generation (from rows), distance to the centroid k generations back."""
    by_gen: Dict[int, List[Dict[str, float]]] = {}
    for r in out["rows"]:
        by_gen.setdefault(r["t0"]["lt"], []).append(numeric_vector((r["t0"], r["ext"])))
    gens = sorted(by_gen); cents = {}
    for g in gens:
        vs = by_gen[g]; keys = vs[0].keys()
        cents[g] = {kk: sum(v[kk] for v in vs) / len(vs) for kk in keys}
    series = []
    for i, g in enumerate(gens):
        if i >= k:
            g0 = gens[i - k]; a, b = cents[g0], cents[g]
            d = sum(abs(a[kk] - b[kk]) / max(spread.get(kk, 1.0), 1e-6) for kk in a)
            series.append({"generation": g, "from": g0, "shift": round(d, 4)})
    return series


def max_spike(out: dict) -> List[dict]:
    obs = sorted(out["observations"], key=lambda o: o["generation"])
    spikes = []
    for i in range(1, len(obs)):
        rise = obs[i]["reward_max"] - obs[i - 1]["reward_max"]
        if rise >= 2 * BAND:
            fell = any(obs[j]["reward_max"] <= obs[i]["reward_max"] - BAND for j in range(i + 1, min(len(obs), i + 5)))
            spikes.append({"generation": obs[i]["generation"], "rise": round(rise, 4), "reverted_within_4": fell})
    return spikes


def measure(out: dict, spread: Dict[str, float]) -> dict:
    return {"population_shift": population_shift(out, spread), "max_spike": max_spike(out)}


def emit(reg, q, priority=None):
    """Registers the calibration epoch in the registry (no specs queued): the rulers are computed for every run from now on."""
    lid0 = reg.all()[0]["lineage_id"]
    reg.event(lid0, "CALIBRATION_EPOCH", {"epoch": "CALIBRATION_EPOCH-002", "added": ["population_shift", "max_spike"], "thresholds_moved": False, "status": "UNVALIDATED",
                                         "definition": "archaeon/frontier/design/measurement.py", "reason": "population-level rulers for effects with no exceptional individual (boom-bust maximum seen on coupled worlds)"})
    return {"epoch": "CALIBRATION_EPOCH-002", "rulers": ["population_shift", "max_spike"]}
