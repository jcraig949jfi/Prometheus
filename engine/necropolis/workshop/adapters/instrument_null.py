"""Instrument null for a two-sample statistic (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: none of its own.  It takes ANY statistic
``f(a, b) -> float | None`` and asks whether the statistic can tell samples
apart at all, before anyone reads its value on a grave.  The pattern is the
one that killed the Pollux verdict column: a statistic that returns the same
number on the real pair, on a shuffled pair and on an independent pair is
measuring its own construction, not the data.

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_instrument_null.*

Reads: the two samples handed to it.  Writes: nothing (returns a dict).
Never touches a grave; the caller decides what samples to pass.
"""
from __future__ import annotations

import math
import random
from typing import Callable, Optional, Sequence

Stat = Callable[[Sequence[float], Sequence[float]], Optional[float]]


def _finite(x) -> bool:
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


def instrument_null(stat: Stat, a: Sequence[float], b: Sequence[float], *,
                    n_draws: int = 200, seed: int = 0, tol: float = 1e-9) -> dict:
    """Return the statistic under five conditions and a verdict about the instrument.

    conditions
      observed      f(a, b)
      shuffle_b     f(a, permuted b)               -- pairing destroyed
      independent   f(a, resample from a's marginal) -- b replaced by noise shaped like a
      sorted_both   f(sorted a, sorted b)           -- the Pollux construction
      repeat        f(a, b) again                   -- determinism

    verdict
      TAUTOLOGICAL   observed == shuffle == independent (within tol) on every draw:
                     the statistic does not respond to the relation between a and b
      NONDETERMINISTIC  repeat != observed
      SORT_INVARIANT observed equals sorted_both: the statistic ignores pairing order
      RESPONSIVE     otherwise (the instrument CAN see something; says nothing about a, b)
    """
    rng = random.Random(seed)
    a = list(a)
    b = list(b)
    obs = stat(a, b)
    rep = stat(a, b)
    shuffles, indeps = [], []
    for _ in range(n_draws):
        bb = b[:]
        rng.shuffle(bb)
        shuffles.append(stat(a, bb))
        indeps.append(stat(a, [rng.choice(a) for _ in range(len(b))]))
    sorted_both = stat(sorted(a), sorted(b))

    def _all_equal(vals):
        return all(_finite(v) and _finite(obs) and abs(v - obs) <= tol for v in vals)

    if not (_finite(obs) and _finite(rep) and abs(obs - rep) <= tol):
        verdict = "NONDETERMINISTIC" if _finite(obs) else "UNMEASURABLE"
    elif _all_equal(shuffles) and _all_equal(indeps):
        verdict = "TAUTOLOGICAL"
    elif _finite(sorted_both) and abs(sorted_both - obs) <= tol:
        verdict = "SORT_INVARIANT"
    else:
        verdict = "RESPONSIVE"

    fin_sh = [v for v in shuffles if _finite(v)]
    fin_in = [v for v in indeps if _finite(v)]
    return {
        "verdict": verdict,
        "observed": obs,
        "repeat": rep,
        "sorted_both": sorted_both,
        "shuffle_b": {"n": len(fin_sh), "min": min(fin_sh) if fin_sh else None,
                      "max": max(fin_sh) if fin_sh else None,
                      "frac_ge_observed": (sum(1 for v in fin_sh if v >= obs) / len(fin_sh)) if fin_sh and _finite(obs) else None},
        "independent": {"n": len(fin_in), "min": min(fin_in) if fin_in else None,
                        "max": max(fin_in) if fin_in else None,
                        "frac_ge_observed": (sum(1 for v in fin_in if v >= obs) / len(fin_in)) if fin_in and _finite(obs) else None},
        "n_a": len(a), "n_b": len(b), "n_draws": n_draws, "seed": seed,
        "forbidden_inference": "RESPONSIVE means the instrument can distinguish conditions; it is not "
                               "evidence that a and b are related. TAUTOLOGICAL means no reading of this "
                               "statistic on these inputs is evidence of anything.",
    }
