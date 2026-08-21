"""CANON R12 — generative conjecture / research. **An AUDIT of the existing grader.**

Canon v2.0 §3: *"Kill: a small closed universe (graphs ≤ 8, short sequences)."* Canon §7 records
R12's grader as *"built, unit-tested, endorsed by all four frontier reviewers, never run."*

**It was there, and this cycle ran it.** `harmonia/experiments/r12_grader.py` (615 lines) plus
`r12_universe.py`, `run_r12.py` and 17 unit tests, all green. The offline runner discriminates
exactly as designed:

    good      conjecture-quality 0.238–0.526, holdout 1.000, exact_partition, test efficiency 1.000
    overfit   conjecture-quality 0.000                      , test efficiency 0.566–0.647
    naive     conjecture-quality 0.000                      , test efficiency 0.000

So this module does NOT build a second grader. It builds the three probes the standing
instruments say to point at one, and reports what they find.

The findings are in the tests. In summary:

1. **The two channels are asymmetrically defended.** Conjecture-quality subtracts a baseline
   (the score is zeroed when a naive baseline is at least as similar to the target). Test-quality
   does not subtract anything — it reports `info_gain / optimal_gain`. A probe chosen with no
   reasoning at all collects a substantial fraction of the available bits, which is why the
   overfit arm banks ~0.6 bits while scoring zero on conjectures.

2. **The canon's own kill test is an aliasing statement**, and it is UNBREAKABLE from inside —
   the same shape as R11, not the R6/R9/R10 shape. Two conjectures with identical extensions on
   the closed universe are indistinguishable to any grader that observes only the universe; they
   differ the moment the universe is widened. "Do not grade in a small closed universe" is
   exactly "the projection is not sufficient for the target you want".

3. **Claim v13 is at its sharpest here**, because R12 generates its own candidates. A generator
   that internally draws N and reports its best publishes an unfalsified record whose score is a
   maximum masquerading as a sample. Nothing in the emission reveals N.
"""
from __future__ import annotations

import os
import statistics
import sys
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_HARMONIA = os.path.join(_REPO, "harmonia", "experiments")
for _p in (_REPO, _HARMONIA):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from r12_grader import (  # noqa: E402
    compile_safe_conjecture, consistent_version_space, grade_conjecture, grade_test_object,
)
from r12_universe import (  # noqa: E402
    Trial, Universe, build_tuples_universe, enumerate_hypothesis_class, make_trial,
    pred_to_python,
)

__all__ = [
    "small_universe", "wide_universe", "extension_of", "closed_universe_alias_pair",
    "constant_probe_gain", "informed_probe_gain", "best_of_n_inflation", "InflationReport",
    "trials", "CLOSED_UNIVERSE_TWINS",
]


def small_universe() -> Universe:
    """The graded universe: 8x8 tuples, 64 objects. The canon's "small closed universe"."""
    return build_tuples_universe(lo=0, hi=7)


def wide_universe() -> Universe:
    """The same construction, widened. Nothing about the grammar or the features changes —
    only how much of the world is in scope."""
    return build_tuples_universe(lo=0, hi=15)


def extension_of(src: str, universe: Universe) -> FrozenSet[int]:
    """Extension of a Python conjecture body over a universe, via the grader's own safe
    compiler — so this audit and the thing it audits agree on what a conjecture MEANS."""
    return compile_safe_conjecture(src).extension(universe)


#: Conjectures that are indistinguishable on the small universe and differ on the wide one.
#: On 0..7 every object has x <= 7 and s = x + y <= 14, so all three accept everything.
CLOSED_UNIVERSE_TWINS: Tuple[str, ...] = (
    "True",
    "obj['x'] <= 7",
    "obj['s'] <= 14",
)


def closed_universe_alias_pair() -> Tuple[str, str]:
    """The canon's kill, as a concrete pair: same extension on 0..7, different on 0..15."""
    return CLOSED_UNIVERSE_TWINS[0], CLOSED_UNIVERSE_TWINS[1]


# --------------------------------------------------------------------------------------------
# Probe 1: is the test-quality channel baseline-corrected?

def constant_probe_gain(trial: Trial, obj_index: int = 0) -> float:
    """Efficiency earned by proposing a FIXED universe object, chosen without looking at
    anything. The floor a grader credits to no reasoning whatsoever."""
    probe = trial.universe.objects[obj_index]
    return grade_test_object(trial, probe).efficiency


def informed_probe_gain(trial: Trial) -> float:
    """Efficiency of the best available probe — by construction 1.0, and included so the two
    numbers are produced by the same code path rather than compared across sources."""
    V = consistent_version_space(trial)
    best = 0.0
    for obj in trial.universe.objects:
        best = max(best, grade_test_object(trial, obj, V=V).efficiency)
    return best


# --------------------------------------------------------------------------------------------
# Probe 2: claim v13 at R12 — best-of-N reported as a single draw

@dataclass(frozen=True)
class InflationReport:
    """What a best-of-N generator gains by not declaring N."""

    n: int
    honest_mean: float          # expected score of ONE consistent draw
    best_of_n: float            # score of the best of n draws
    inflation: float            # best_of_n - honest_mean
    declared_n: Optional[int]   # None when the emission does not say


def _consistent_sources(trial: Trial, limit: int = 64) -> List[str]:
    """Python sources for hypotheses consistent with the revealed data — what an honest
    generator draws from."""
    V = consistent_version_space(trial)
    out = []
    for hi, _sig in V[:limit]:
        out.append(pred_to_python(trial.H[hi][0]))
    return out


def best_of_n_inflation(trial: Trial, n: int = 8,
                        declared_n: Optional[int] = None) -> InflationReport:
    """Draw n consistent conjectures, grade each, and report the best as if it were one draw.

    This is claim v13 in its sharpest setting. Nothing is falsified: every candidate really is
    consistent with the revealed data, and the reported score really is the reported
    conjecture's score. The omission is *the other n − 1 attempts*, and no function of the
    emission can recover them — the emission does not contain what was discarded.
    """
    sources = _consistent_sources(trial)[:n]
    if not sources:
        return InflationReport(n, 0.0, 0.0, 0.0, declared_n)
    scores = [grade_conjecture(trial, extension_of(s, trial.universe)).quality for s in sources]
    return InflationReport(
        n=len(scores),
        honest_mean=statistics.fmean(scores),
        best_of_n=max(scores),
        inflation=max(scores) - statistics.fmean(scores),
        declared_n=declared_n,
    )


def trials(seeds: Sequence[int], universe: Optional[Universe] = None) -> List[Trial]:
    uni = universe or small_universe()
    H = enumerate_hypothesis_class(uni, max_terms=2)
    return [make_trial(seed=s, universe=uni, H=H) for s in seeds]
