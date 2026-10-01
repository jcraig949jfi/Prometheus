"""(6) Attainable-range certification of a gate, BEFORE a preregistration is frozen (generic protocol).

A gate is a decision rule over a statistic (e.g. C1 SIGNAL: held lo99 > .55). Before it is frozen, four
questions must have numbers (fleet memory `preregistered_rules_need_an_eligibility_count`):

  G1 NULL          how often does the gate pass when the construct is absent? (false-pass rate with an exact
                   one-sided Clopper-Pearson upper bound; must be <= alpha)
  G2 ADVERSARY     does any committed NON-CONSTRUCT policy pass it? (Harmonia R-C baseline_gaming; PTE: a
                   one-flag readout passes C1's XOR SIGNAL rule at .763)
  G3 POSITIVE      a PLANT (a policy that has the construct) passes the gate: the gate is shown passable, not
                   merely not-impossible (W2-B's 'plant' role; Harmonia R-B's calibration item)
  G4 ELIGIBILITY   per-cell CEILINGS (an upper bound on the statistic no program can beat; PTE: the H-PLANT
                   light-cone bound) give the number of eligible cells; below the prereg's minimum the gate's
                   NULL is uninformative by design (PTE: P3 "zero XOR SIGNAL" on ring rows, 2/19 eligible)
  plus ATTAINABLE  the set of verdict labels that any admissible input can produce (Harmonia R-A
                   reachability; returned keys are compatible with roles/Harmonia/qualification/primitives)

W2-B's PTE certifier (wave2/W2-B/attain.py) runs programs by ROLE (null / adversary / plant / probe) over cells
and issues UNREACHABLE / DEGENERATE / CHEATABLE / SOUND / NO_PLANT. Its outputs map onto these inputs:
null-role statistics -> G1, adversary-role -> G2, plant-role -> G3, per-cell plant crossing or analytic bounds
-> G4; DEGENERATE (a constant ruler) is explib.controls A2/A3. map_w2b() names the corresponding check.
"""
from __future__ import annotations

import math
from typing import Callable, Iterable, Optional

import numpy as np

from .outcomes import FAIL, NOT_VERIFIED, PASS, Check, worst


def _betainc_upper(k: int, n: int, level: float) -> float:
    """Exact one-sided Clopper-Pearson upper bound for k successes in n (bisection on the binomial tail)."""
    if k >= n:
        return 1.0
    a = 1 - level

    def tail_le_k(p):          # P(X <= k | n, p), in log space (n can be large)
        if p <= 0:
            return 1.0
        if p >= 1:
            return 0.0
        lp, lq = math.log(p), math.log1p(-p)
        return sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq)
                   for i in range(k + 1))
    lo, hi = k / n, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if tail_le_k(mid) > a:
            lo = mid
        else:
            hi = mid
    return hi


def null_pass_rate(gate: Callable[[dict], bool], sampler: Callable[[np.random.Generator], dict], n: int = 2000,
                   seed: int = 0, alpha: float = 0.01, level: float = 0.95) -> Check:
    rng = np.random.default_rng(seed)
    k = sum(bool(gate(sampler(rng))) for _ in range(n))
    ub = _betainc_upper(k, n, level)
    # FAIL only when the observed rate itself exceeds alpha; a small rate whose upper bound still exceeds
    # alpha is NOT_VERIFIED (too few null draws), never a pass
    out = PASS if ub <= alpha else (FAIL if k / n > alpha else NOT_VERIFIED)
    return Check("G1_null", out,
                 {"passes": k, "n": n, "rate": k / n, "upper": round(ub, 6), "alpha": alpha})


def adversary_check(gate: Callable[[dict], bool], adversaries: dict) -> Check:
    """adversaries: {name: stat dict computed from a policy that lacks the construct}."""
    if not adversaries:
        return Check("G2_adversary", NOT_VERIFIED, "no adversary policies supplied")
    passers = sorted(k for k, v in adversaries.items() if gate(v))
    return Check("G2_adversary", FAIL if passers else PASS, {"passers": passers, "n": len(adversaries)})


def eligibility(ceilings: dict, threshold: float, min_eligible: int, margin: float = 0.0) -> Check:
    """ceilings: {cell: upper bound on the statistic}. A cell is eligible iff bound > threshold + margin."""
    if not ceilings:
        return Check("G4_eligibility", NOT_VERIFIED, "no ceilings supplied")
    elig = sorted(k for k, b in ceilings.items() if b > threshold + margin)
    return Check("G4_eligibility", PASS if len(elig) >= min_eligible else FAIL,
                 {"eligible": len(elig), "cells": len(ceilings), "min_eligible": min_eligible,
                  "ineligible": len(ceilings) - len(elig), "threshold": threshold})


def attainable_labels(verdict_fn: Callable[[dict], str], design_space: Iterable[dict], gated: Iterable[str]) -> dict:
    """Harmonia R-A semantics: the labels any admissible input reaches; gated labels nobody reaches."""
    seen: dict = {}
    for x in design_space:
        v = verdict_fn(x)
        seen[v] = seen.get(v, 0) + 1
    un = sorted(set(gated) - set(seen))
    return {"attainable": sorted(seen), "counts": seen, "unreachable_gated": un, "flag": bool(un)}


def positive_check(gate: Callable[[dict], bool], plants: dict) -> Check:
    if not plants:
        return Check("G3_positive", NOT_VERIFIED, "no plant supplied: the gate was never shown passable")
    passers = sorted(k for k, v in plants.items() if gate(v))
    return Check("G3_positive", PASS if passers else FAIL, {"passing_plants": passers, "n": len(plants)})


def certify_gate(gate: Callable[[dict], bool], *, null_sampler=None, adversaries: Optional[dict] = None,
                 plants: Optional[dict] = None, ceilings: Optional[dict] = None, threshold: Optional[float] = None,
                 min_eligible: int = 1, verdict_fn=None, design_space=None, gated=(), n_null: int = 2000,
                 alpha: float = 0.01, seed: int = 0) -> dict:
    """CERTIFIED only if every question PASSes and none is missing (fail-closed: a missing null, adversary
    set, plant or ceiling table is NOT_VERIFIED, and NOT_VERIFIED blocks certification)."""
    checks = []
    checks.append(null_pass_rate(gate, null_sampler, n_null, seed, alpha) if null_sampler else
                  Check("G1_null", NOT_VERIFIED, "no null sampler"))
    checks.append(adversary_check(gate, adversaries or {}))
    checks.append(positive_check(gate, plants or {}))
    if ceilings is not None and threshold is not None:
        checks.append(eligibility(ceilings, threshold, min_eligible))
    else:
        checks.append(Check("G4_eligibility", NOT_VERIFIED, "no ceilings/threshold"))
    att = None
    if verdict_fn is not None and design_space is not None:
        att = attainable_labels(verdict_fn, design_space, gated)
        checks.append(Check("A_attainable", FAIL if att["flag"] else PASS, att))
    o = worst(checks)
    return {"verdict": "CERTIFIED" if o == PASS else ("FLAGGED" if o == FAIL else "NOT_VERIFIED"),
            "checks": [c.as_dict() for c in checks], "attainable": att}


def map_w2b(verdict: str) -> str:
    """W2-B certifier verdict -> the explib check that fails (or passes) for the same evidence."""
    return {"CHEATABLE": "G1_null or G2_adversary FAIL", "DEGENERATE": "controls A2/A3 FAIL (or G1_null FAIL)",
            "UNREACHABLE": "G3_positive FAIL and/or G4_eligibility FAIL", "NO_PLANT": "G3_positive NOT_VERIFIED",
            "SOUND": "G1, G2, G3 PASS (relative to the declared family)"}.get(verdict.rstrip("*"), "unknown")
