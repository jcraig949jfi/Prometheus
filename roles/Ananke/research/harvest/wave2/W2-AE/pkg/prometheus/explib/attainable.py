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

The role-based FAMILY certifier (certify_family, promoted from W2-B attain.py) runs programs by ROLE (null /
adversary / plant / probe) over cells through an engine-supplied Ruler.measure and issues UNREACHABLE /
DEGENERATE / CHEATABLE / SOUND / NO_PLANT. Its outputs map onto the G-checks:
null-role statistics -> G1, adversary-role -> G2, plant-role -> G3, per-cell plant crossing or analytic bounds
-> G4; DEGENERATE (a constant ruler) is explib.controls A2/A3. map_w2b() names the corresponding check.
"""
from __future__ import annotations

import math
import dataclasses
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


# ====================================================================== role-based family certifier
# Promoted from W2-B attain.py (verbatim semantics; the engine enters only through Ruler.measure and
# Program.make, so this half is engine-free as well).
#
# Question: over a declared family of worlds and programs, what values can a ruler take, which programs cross
# its gate, and is the gate's outcome FORCED, CHEATABLE or UNREACHABLE?
#   worlds   = Cell(ph, env, label, sched_fn): an engine's world spec, optionally a world-level edit;
#   programs = Program(name, role, make): role in
#                null       must not cross (no competence of any kind),
#                adversary  must not cross (lacks the property the ruler claims; `lacks` names it),
#                plant      should cross (has the property; a positive control),
#                probe      no expectation;
#   ruler    = Ruler(name, claim, measure): measure(ph, env, genome, seeds, sched_fn) ->
#                {"value": float, "passed": bool, optional "pairs": per-pair vector}.
# Verdict precedence:
#   UNREACHABLE  value FORCED (identical for every program; pair-exact when pairs are given) and never passes
#   DEGENERATE   value FORCED, or the gate passes for every program including nulls (a gate that cannot fail)
#   CHEATABLE    some null or adversary crosses (`cheapest` names it: a null before an adversary, then the
#                highest score)
#   UNREACHABLE  nothing crosses, plants included
#   SOUND        >= 1 plant crosses and no null / adversary does
#   NO_PLANT     nothing decides (no plant offered, or only probes cross)
# SOUND is relative to the declared family, never a proof; CHEATABLE / DEGENERATE rows are constructive
# counterexamples. FORCED needs >= 2 programs to be testable.

ROLES = ("null", "adversary", "plant", "probe")


@dataclasses.dataclass
class Cell:
    ph: object
    env: object
    label: str
    sched_fn: Optional[Callable] = None


@dataclasses.dataclass
class Program:
    name: str
    role: str
    make: Callable            # (ph, env) -> genome, or None (not applicable in this cell)
    lacks: str = ""
    only: tuple = ()          # restrict to these cell labels (a role can depend on the world)

    def __post_init__(self):
        if self.role not in ROLES:
            raise ValueError(f"role {self.role!r} not in {ROLES}")


@dataclasses.dataclass
class Ruler:
    name: str
    claim: str
    measure: Callable         # (ph, env, genome, seeds, sched_fn) -> {"value", "passed", ["pairs"]}


@dataclasses.dataclass
class Certificate:
    ruler: str
    claim: str
    rows: list
    verdict: str
    attainable: tuple
    eligibility: dict
    null_scores: dict
    adversary_scores: dict
    cheapest: Optional[dict]
    forced: bool
    always_pass: bool
    notes: list

    def summary(self) -> dict:
        d = dataclasses.asdict(self)
        d.pop("rows")
        return d


def certify_family(ruler: Ruler, cells, programs, seeds, tol: float = 1e-12) -> Certificate:
    rows = []
    for cell in cells:
        for p in programs:
            if p.only and cell.label not in p.only:
                continue
            g = p.make(cell.ph, cell.env)
            if g is None:
                continue
            m = ruler.measure(cell.ph, cell.env, g, seeds, cell.sched_fn)
            rows.append({"cell": cell.label, "program": p.name, "role": p.role, "lacks": p.lacks,
                         "value": float(m["value"]), "passed": bool(m["passed"]),
                         "pairs": None if m.get("pairs") is None else np.asarray(m["pairs"], float)})
    if not rows:
        raise ValueError("empty family: no (cell, program) row was applicable")
    vals = np.array([r["value"] for r in rows])
    passed = np.array([r["passed"] for r in rows])
    notes = []
    n_prog = len({r["program"] for r in rows})
    forced = bool(np.ptp(vals) <= tol) and n_prog >= 2
    if n_prog < 2:
        notes.append("single program: forcing not testable")
    pair_rows = [r["pairs"] for r in rows if r["pairs"] is not None]
    if pair_rows and len(pair_rows) == len(rows) and len({p.shape for p in pair_rows}) == 1:
        pair_forced = bool(np.all(np.ptp(np.stack(pair_rows), 0) <= tol))
        if pair_forced:
            notes.append("pair-exact: every program gives the identical per-pair vector")
        forced = pair_forced and n_prog >= 2      # pairs given: FORCED means pair-exact, not equal means
    always_pass = bool(passed.all())
    by_role = {k: [r for r in rows if r["role"] == k] for k in ROLES}
    bad = [r for r in by_role["null"] + by_role["adversary"] if r["passed"]]
    plants_pass = [r for r in by_role["plant"] if r["passed"]]
    elig = {k: f"{sum(r['passed'] for r in v)}/{len(v)}" for k, v in by_role.items() if v}
    cheapest = None
    if bad:
        bad.sort(key=lambda r: (r["role"] != "null", -r["value"]))
        cheapest = {k: bad[0][k] for k in ("cell", "program", "role", "lacks", "value")}
    if forced:
        notes.append(f"value forced to {vals[0]:.6g} for every program and cell")
    if forced and not passed.any():
        verdict = "UNREACHABLE"
    elif forced or (always_pass and by_role["null"]):
        verdict = "DEGENERATE"
        if not forced:
            notes.append("gate passes for every program, nulls included")
    elif bad:
        verdict = "CHEATABLE"
    elif not passed.any():
        verdict = "UNREACHABLE" if by_role["plant"] else "NO_PLANT"
    elif plants_pass:
        verdict = "SOUND"
    else:
        verdict = "NO_PLANT"
        notes.append("only probes cross; no plant or adversary decides")
    return Certificate(
        ruler=ruler.name, claim=ruler.claim, rows=rows, verdict=verdict,
        attainable=(float(vals.min()), float(vals.max())), eligibility=elig,
        null_scores={r["program"] + "@" + r["cell"]: r["value"] for r in by_role["null"]},
        adversary_scores={r["program"] + "@" + r["cell"]: r["value"] for r in by_role["adversary"]},
        cheapest=cheapest, forced=forced, always_pass=always_pass, notes=notes)


def alias(a: Certificate, b: Certificate) -> dict:
    """Identical pass vectors on every common (cell, program) row: the two rulers are one ruler here."""
    ka = {(r["cell"], r["program"]): r["passed"] for r in a.rows}
    kb = {(r["cell"], r["program"]): r["passed"] for r in b.rows}
    common = sorted(set(ka) & set(kb))
    same = [ka[k] == kb[k] for k in common]
    return {"rows": len(common), "identical": bool(common) and all(same),
            "disagree": [k for k, s in zip(common, same) if not s]}


def family_checks(cert: Certificate) -> list:
    """The family verdict re-expressed as explib checks (map_w2b made executable). Missing roles are
    NOT_VERIFIED, never PASS."""
    roles = {r["role"] for r in cert.rows}
    bad_null = any(r["passed"] for r in cert.rows if r["role"] == "null")
    bad_adv = any(r["passed"] for r in cert.rows if r["role"] == "adversary")
    plant = [r for r in cert.rows if r["role"] == "plant"]
    return [
        Check("G1_null", (FAIL if bad_null else PASS) if "null" in roles else NOT_VERIFIED, cert.null_scores),
        Check("G2_adversary", (FAIL if bad_adv else PASS) if "adversary" in roles else NOT_VERIFIED,
              cert.adversary_scores),
        Check("G3_positive", (PASS if any(r["passed"] for r in plant) else FAIL) if plant else NOT_VERIFIED,
              {"plants": [r["program"] + "@" + r["cell"] for r in plant]}),
        Check("A2_not_forced", FAIL if cert.forced else PASS, {"attainable": cert.attainable}),
    ]


# ---------------------------------------------------------------- analytic CI-gate power (eligibility)
_Z99 = 2.5758293035489004


def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def pair_sd(p: float, K: int, twin_corr: float = 1.0) -> float:
    """SD of one mirror-pair mean of K scored trials per world, each Bernoulli(p). twin_corr = 1: twins' trial
    outcomes identical (K effective trials); 0: independent twins (2K effective trials)."""
    v = p * (1 - p) / K
    return math.sqrt(v * (1 + twin_corr) / 2)


def ci_gate_power(p_true: float, threshold: float, P: int, K: int, side: str = "lo_gt",
                  twin_corr: float = 1.0, z: float = _Z99) -> float:
    """P(gate crossed) under a normal approximation to the pair interval over P pairs.
    side 'lo_gt': lo99 > threshold;  'hi_lt': hi99 < threshold."""
    if side not in ("lo_gt", "hi_lt"):
        raise ValueError(side)
    se = pair_sd(p_true, K, twin_corr) / math.sqrt(P)
    if se == 0:
        return float((p_true > threshold) if side == "lo_gt" else (p_true < threshold))
    if side == "lo_gt":
        return 1 - _phi((threshold + z * se - p_true) / se)
    return _phi((threshold - z * se - p_true) / se)


def min_true_to_cross(threshold: float, P: int, K: int, side: str = "lo_gt", power: float = 0.5,
                      twin_corr: float = 1.0) -> float:
    """Smallest (lo_gt) or largest (hi_lt) true accuracy with P(cross) >= power (bisection on [0, 1])."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        ok = ci_gate_power(mid, threshold, P, K, side, twin_corr) >= power
        if side == "lo_gt":
            lo, hi = (lo, mid) if ok else (mid, hi)
        else:
            lo, hi = (mid, hi) if ok else (lo, mid)
    return hi if side == "lo_gt" else lo
