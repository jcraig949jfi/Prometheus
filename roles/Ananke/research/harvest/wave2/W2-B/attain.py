"""ATTAINABILITY CERTIFIER (W2-B draft; generalises lens.verify_reach).

Question it answers for ANY ruler (a gate, label, control or intervention reading): over a declared family
of worlds and programs, what values can the ruler take, which programs cross its gate, and is the gate's
outcome FORCED, ALIASED, CHEATABLE or UNREACHABLE?

verify_reach asks it for one intervention with one specimen and one plant (applied? plant fired?). Here:
  * worlds   = Cell(ph, env, label, sched_fn): physics x environment, optionally a world-level edit
               (e.g. "only one MAJ sensor carries a cue", "teachers after trial 0 removed");
  * programs = Program(name, role, make): role in
                 null       must not cross (no competence of any kind),
                 adversary  must not cross (lacks the property the ruler claims; `lacks` names it),
                 plant      should cross (has the property; a positive control),
                 probe      no expectation (random genomes, specimens);
  * ruler    = Ruler(name, claim, measure): measure(ph, env, genome, seeds, sched_fn) ->
               {"value": float, "passed": bool, optional "pairs": per-pair vector}.

certify() returns per-row values and a verdict, by precedence:
  UNREACHABLE*  (checked first) the value is FORCED (as below) to a level that never crosses the gate;
  DEGENERATE   the measured value is identical for every program in every cell (pair-exact when the
                ruler returns "pairs": a FORCED control), or the gate outcome is True for every program
                including nulls (a gate that cannot fail);
  CHEATABLE     some null or adversary crosses the gate (names the cheapest one and its score);
  UNREACHABLE   no program crosses the gate, plants included (eligibility count 0 in this family);
  SOUND         >= 1 plant crosses and no null/adversary does;
  NO_PLANT      nothing crosses and no plant was offered (the family cannot say).
The verdict is relative to the declared family. SOUND is never a proof; a CHEATABLE/DEGENERATE verdict
is a constructive counterexample (the row is the certificate).

alias(cert_a, cert_b): identical pass vectors on every row -> the two rulers are one ruler here (e.g.
COMM_DEPENDENT == SIGNAL whenever zero_comm is forced).

Analytic half (no engine): ci_gate_power() / min_true_to_cross() give the true accuracy a specimen needs
before a CI-bound gate (lo99 > c or hi99 < c over P mirror pairs, K scored trials per world) can be
crossed with a given probability. This is the eligibility count for gates such as the absolute swap rule
(hi99 < .40), C1b's T clause (lo99 >= .62) or SIGNAL itself.
"""
from __future__ import annotations

import dataclasses
import math
from typing import Callable

import numpy as np

ROLES = ("null", "adversary", "plant", "probe")


@dataclasses.dataclass
class Cell:
    ph: object
    env: object
    label: str
    sched_fn: Callable | None = None


@dataclasses.dataclass
class Program:
    name: str
    role: str
    make: Callable            # (ph, env) -> genome [G, L, 5] or None (not applicable here)
    lacks: str = ""
    only: tuple = ()          # restrict to these cell labels (roles can depend on the world)

    def __post_init__(self):
        assert self.role in ROLES, self.role


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
    cheapest: dict | None
    forced: bool
    always_pass: bool
    notes: list

    def summary(self) -> dict:
        d = dataclasses.asdict(self)
        d.pop("rows")
        return d


def certify(ruler: Ruler, cells, programs, seeds, tol: float = 1e-12) -> Certificate:
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
    assert rows, "empty family"
    vals = np.array([r["value"] for r in rows])
    passed = np.array([r["passed"] for r in rows])
    notes = []
    n_prog = len({r["program"] for r in rows})
    forced = bool(np.ptp(vals) <= tol) and n_prog >= 2      # forcing needs >= 2 programs to be testable
    if n_prog < 2:
        notes.append("single program: forcing not testable")
    pair_rows = [r["pairs"] for r in rows if r["pairs"] is not None]
    if pair_rows and len(pair_rows) == len(rows):
        same_shape = len({p.shape for p in pair_rows}) == 1
        if same_shape:
            pair_forced = bool(np.all(np.ptp(np.stack(pair_rows), 0) <= tol))
            if pair_forced:
                notes.append("pair-exact: every program gives the identical per-pair vector")
            forced = pair_forced and n_prog >= 2   # pairs given: FORCED means pair-exact, not equal means
    always_pass = bool(passed.all())
    by_role = {k: [r for r in rows if r["role"] == k] for k in ROLES}
    bad = [r for r in by_role["null"] + by_role["adversary"] if r["passed"]]
    plants_pass = [r for r in by_role["plant"] if r["passed"]]
    eligibility = {k: f"{sum(r['passed'] for r in v)}/{len(v)}" for k, v in by_role.items() if v}
    cheapest = None
    if bad:
        # cheapest = a null before an adversary; then the highest-scoring one
        bad.sort(key=lambda r: (r["role"] != "null", -r["value"]))
        b = bad[0]
        cheapest = {k: b[k] for k in ("cell", "program", "role", "lacks", "value")}
    if forced:
        notes.append(f"value forced to {vals[0]:.6g} for every program and cell")
    if forced and not passed.any():
        verdict = "UNREACHABLE"            # forced to a level that never crosses the gate
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
        attainable=(float(vals.min()), float(vals.max())), eligibility=eligibility,
        null_scores={r["program"] + "@" + r["cell"]: r["value"] for r in by_role["null"]},
        adversary_scores={r["program"] + "@" + r["cell"]: r["value"] for r in by_role["adversary"]},
        cheapest=cheapest, forced=forced, always_pass=always_pass, notes=notes)


def alias(a: Certificate, b: Certificate) -> dict:
    ka = {(r["cell"], r["program"]): r["passed"] for r in a.rows}
    kb = {(r["cell"], r["program"]): r["passed"] for r in b.rows}
    common = sorted(set(ka) & set(kb))
    same = [ka[k] == kb[k] for k in common]
    return {"rows": len(common), "identical": bool(common) and all(same),
            "disagree": [k for k, s in zip(common, same) if not s]}


# ------------------------------------------------------------------ analytic half
_Z99 = 2.5758293035489004


def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def pair_sd(p: float, K: int, twin_corr: float = 1.0) -> float:
    """SD of one mirror-pair mean of K scored trials per world when each trial is Bernoulli(p).
    twin_corr = 1: twins' trial outcomes identical (mirror-equivariant program; K effective trials);
    twin_corr = 0: independent twins (2K effective trials)."""
    v = p * (1 - p) / K
    return math.sqrt(v * (1 + twin_corr) / 2)


def ci_gate_power(p_true: float, threshold: float, P: int, K: int, side: str = "lo_gt",
                  twin_corr: float = 1.0, z: float = _Z99) -> float:
    """P(the gate is crossed) under a normal approximation to the pair-bootstrap interval.
    side 'lo_gt': lo99 > threshold;  'hi_lt': hi99 < threshold."""
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
    f = (lambda p: ci_gate_power(p, threshold, P, K, side, twin_corr)) if side == "lo_gt" else \
        (lambda p: ci_gate_power(p, threshold, P, K, side, twin_corr))
    for _ in range(60):
        mid = (lo + hi) / 2
        ok = f(mid) >= power
        if side == "lo_gt":
            lo, hi = (lo, mid) if ok else (mid, hi)
        else:
            lo, hi = (mid, hi) if ok else (lo, mid)
    return hi if side == "lo_gt" else lo
