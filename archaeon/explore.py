"""Exploration fallback.

When no detector fires, Archaeon still proposes an experiment. This is
DELIBERATE EXPLORATION, not an error condition and not a verdict about the
corpus. Nothing in this module may be read as "there was nothing to find".

Policy: coverage-biased, not uniform. Uniform RNG re-samples the dense regions
in proportion to how dense they already are, which is the opposite of what an
archaeology service wants. The bias is the simplest one that is still
inspectable by hand:

  1. Enumerate the LEGAL cells: the observed (world_family x player_family)
     grid, plus every world x player combination those families license.
  2. Count observations per cell from the fossil record.
  3. NEVER-SAMPLED legal cells are preferred outright (they carry the most
     coverage per run).
  4. Otherwise take cells at or below the ``undersampled_quantile`` of the
     occupied-cell count distribution.
  5. Choose among the survivors with a seeded PRNG.

Reproducibility is the point. The recorded ``seed`` and ``candidate_set_hash``
together let anyone re-derive exactly why this cell was chosen: the hash pins
the candidate set the seed indexed into, so a later corpus that would have
produced a different set is detectable rather than silently different.

The seed is derived from the corpus hash and the UTC day, so two Archaeon
instances reading the same corpus on the same day propose the same exploration
-- and the cadence layer then admits only one of them.

No human scientific literature and no model prior touches any of this. The only
inputs are counts.
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .clock import utc_day_str


def _quantile(sorted_vals: Sequence[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    if q <= 0:
        return sorted_vals[0]
    if q >= 1:
        return sorted_vals[-1]
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def coverage(corpus) -> Dict[str, Any]:
    """Observation counts over the (region, player) grid and its families.

    Returned as data so the exploration choice is auditable without re-running
    anything: the counts that drove the choice are written into provenance.
    """
    cell_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    region_family: Dict[str, str] = {}
    players: set = set()
    regions: set = set()
    for r in corpus.rows:
        p = r.player or "<noplayer>"
        cell_counts[(r.region, p)] += 1
        region_family[r.region] = r.family or "<nofamily>"
        players.add(p)
        regions.add(r.region)
    return {"cell_counts": cell_counts,
            "region_family": region_family,
            "regions": sorted(regions),
            "players": sorted(players)}


def legal_cells(cov: Dict[str, Any]) -> List[Tuple[str, str]]:
    """The cells Archaeon is allowed to propose.

    v0 takes the observed cross-product of regions and players. It does NOT
    invent worlds or players: proposing a combination the substrate has never
    instantiated would produce an experiment Vivarium cannot run, and Archaeon
    has no way to check legality from the fossil record alone.
    """
    return sorted((reg, pl) for reg in cov["regions"] for pl in cov["players"])


def derive_seed(corpus_hash: str, day: str, salt: str = "") -> int:
    """Deterministic 64-bit seed. Recorded verbatim in provenance."""
    blob = "|".join([corpus_hash, day, salt]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(blob).digest()[:8], "big")


def candidate_set_hash(cands: Sequence[Tuple[str, str]]) -> str:
    blob = json.dumps([list(c) for c in sorted(cands)],
                      separators=(",", ":"))
    return "cand:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def choose(corpus, ecfg, *, day: Optional[str] = None,
           salt: str = "") -> Dict[str, Any]:
    """Pick one under-sampled cell. Returns the full selection record."""
    day = day or utc_day_str()
    cov = coverage(corpus)
    counts: Dict[Tuple[str, str], int] = cov["cell_counts"]
    legal = legal_cells(cov)

    if not legal:
        return {"ok": False,
                "reason": ("fossil record supplies no region/player cells, so "
                           "no legal experiment can be constructed from it"),
                "policy": "coverage_biased.v0",
                "day": day}

    never = [c for c in legal if counts.get(c, 0) == 0]
    occupied_counts = sorted(float(v) for v in counts.values() if v > 0)
    cutoff = _quantile(occupied_counts, ecfg.undersampled_quantile)

    if never and ecfg.prefer_never_sampled:
        pool, pool_kind = never, "NEVER_SAMPLED"
    else:
        pool = [c for c in legal if counts.get(c, 0) <= cutoff]
        pool_kind = "AT_OR_BELOW_QUANTILE"
        if not pool:
            # Everything is above the cutoff (possible when all counts tie).
            # Fall back to the globally least-sampled cells; still not uniform.
            lo = min(counts.get(c, 0) for c in legal)
            pool = [c for c in legal if counts.get(c, 0) == lo]
            pool_kind = "MINIMUM_COUNT"

    # Cap deterministically (sorted, then truncate) so candidate_set_hash names
    # a set that can be rebuilt, not a random sample of one.
    pool = sorted(pool)
    truncated = len(pool) > ecfg.max_candidates
    if truncated:
        pool = pool[:ecfg.max_candidates]

    seed = derive_seed(corpus.corpus_hash(), day, salt)
    rng = random.Random(seed)
    pick = pool[rng.randrange(len(pool))]

    return {
        "ok": True,
        "policy": "coverage_biased.v0",
        "day": day,
        "chosen_cell": {"region": pick[0], "player": pick[1],
                        "observed_count": counts.get(pick, 0),
                        "region_family": cov["region_family"].get(pick[0])},
        "pool_kind": pool_kind,
        "candidate_count": len(pool),
        "candidate_set_hash": candidate_set_hash(pool),
        "candidate_set_truncated": truncated,
        "seed": seed,
        "seed_inputs": {"corpus_hash": corpus.corpus_hash(), "day": day,
                        "salt": salt},
        "undersampled_quantile": ecfg.undersampled_quantile,
        "quantile_cutoff_count": cutoff,
        "legal_cells": len(legal),
        "never_sampled_cells": len(never),
        "occupied_cells": len(occupied_counts),
        "prefer_never_sampled": ecfg.prefer_never_sampled,
    }


def build_spec(selection: Dict[str, Any], corpus) -> Dict[str, Any]:
    """An ordinary SFE-compatible spec for an exploration run."""
    cell = selection["chosen_cell"]
    spec: Dict[str, Any] = {
        "procedure": "archaeon.explore.v0",
        "probe_kind": "COVERAGE_FILL",
        "replicates": 8,
        "worlds": [cell["region"]],
        "players": ([] if cell["player"] == "<noplayer>" else [cell["player"]]),
        "target": {},
        "hold_fixed": "region+player",
        "archaeon": {
            "detector": None,
            "intent": "COVERAGE",
            "chart": corpus.chart.name,
            "policy": selection["policy"],
            "seed": selection["seed"],
            "candidate_set_hash": selection["candidate_set_hash"],
        },
    }
    from .propose import _hash
    spec["spec_hash"] = _hash(spec)
    return spec
