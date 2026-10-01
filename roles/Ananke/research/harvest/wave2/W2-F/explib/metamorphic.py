"""(5) Metamorphic experiment-testing harness: the engine-agnostic protocol.

An EXPERIMENT is any callable experiment(x) -> y, where x is an experiment input (a specimen plus a design:
seeds, schedule, intervention, scoring) and y is what the experiment reports (a statistic, a verdict, a
table). A METAMORPHIC RELATION says how y must change when x is transformed in a known way, without
knowing the right y for any single x:

    Relation(name, transform(x, rng) -> x', check(y, y', x, x') -> True | False | None, kind)
      kind = "invariant"   (y' must equal y: relabel units, permute pair order, rename seeds of a CRN arm)
           | "equivariant" (y' is a known function of y: negate cues and targets -> same accuracy)
           | "must_change" (y' must differ: a construct-removing transform must move a construct verdict)
           | "causal"      (a transform that cannot act before the readout must leave y unchanged)
      check returning None means NOT_VERIFIED for that input (the relation does not apply there).

Mutation adequacy (the "guard that cannot fire" rule): a relation earns its place only if it KILLS at least
one deliberately broken experiment (a mutant), and the correct experiment must satisfy every relation.
run_suite() returns the relation x input table for the experiment and the kill matrix over mutants; its
`adequate` flag is True only if (a) the experiment passes every applicable relation on every input,
(b) every relation kills >= 1 mutant, (c) every mutant is killed by >= 1 relation.

Division of labour: W2-C builds the PTE mutation OPERATORS (harvest/wave2/W2-C); they plug in here as
`mutants` (broken experiments) and as `transform`s. This module defines only the protocol and a few
engine-neutral relations over a plain "pair table" input (dict with units/pairs/targets/outputs).
"""
from __future__ import annotations

import contextlib
import dataclasses
from typing import Any, Callable, ContextManager, Optional, Protocol

import numpy as np

from .outcomes import FAIL, NOT_VERIFIED, PASS

Experiment = Callable[[Any], Any]


@dataclasses.dataclass(frozen=True)
class Relation:
    name: str
    transform: Callable[[Any, np.random.Generator], Any]
    check: Callable[[Any, Any, Any, Any], Optional[bool]]
    kind: str = "invariant"


def apply_relation(experiment: Experiment, rel: Relation, x: Any, rng: np.random.Generator) -> str:
    try:
        y = experiment(x)
        x2 = rel.transform(x, rng)
        y2 = experiment(x2)
        ok = rel.check(y, y2, x, x2)
    except Exception as e:                       # a crash on a transformed input is a FAIL, never data
        return f"{FAIL}:{type(e).__name__}"
    if ok is None:
        return NOT_VERIFIED
    return PASS if ok else FAIL


def run_relations(experiment: Experiment, inputs: list, relations: list, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    return {r.name: [apply_relation(experiment, r, x, rng) for x in inputs] for r in relations}


def run_suite(experiment: Experiment, inputs: list, relations: list, mutants: dict, seed: int = 0) -> dict:
    base = run_relations(experiment, inputs, relations, seed)
    base_ok = all(not v.startswith(FAIL) for vs in base.values() for v in vs)
    kills = {}
    for mname, m in mutants.items():
        res = run_relations(m, inputs, relations, seed)
        kills[mname] = {r: any(v.startswith(FAIL) for v in vs) for r, vs in res.items()}
    rel_kills = {r.name: [m for m in mutants if kills[m][r.name]] for r in relations}
    idle = [r for r, ms in rel_kills.items() if not ms]
    survivors = [m for m in mutants if not any(kills[m].values())]
    return {"experiment": base, "experiment_passes": base_ok, "kill_matrix": kills,
            "relation_kills": rel_kills, "idle_relations": idle, "surviving_mutants": survivors,
            "adequate": base_ok and not idle and not survivors and bool(mutants)}


# ----------------------------------------------------------------------------- engine-neutral relations
# Input convention for these: a dict with
#   outputs [U, K]  readout values (sign is the answer; 0 = tie)
#   targets [U, K]  +-1 targets
#   pair    [U]     mirror-pair id of each unit (two units per id)
# Experiments may carry any other keys; transforms copy them through.

def _copy(x: dict) -> dict:
    return {k: (np.array(v, copy=True) if isinstance(v, np.ndarray) else v) for k, v in x.items()}


def permute_units() -> Relation:
    """Reorder units (keeping their pair ids): a unit-aggregated statistic must not change."""
    def tf(x, rng):
        y = _copy(x)
        idx = rng.permutation(len(x["pair"]))
        for k in ("outputs", "targets", "pair"):
            y[k] = np.asarray(x[k])[idx]
        return y
    return Relation("permute_units", tf, lambda a, b, *_: _close(a, b), "invariant")


def relabel_pairs() -> Relation:
    """Rename pair ids by a bijection: nothing may change."""
    def tf(x, rng):
        y = _copy(x)
        ids = np.unique(x["pair"])
        new = dict(zip(ids, rng.permutation(ids) + 10_000))
        y["pair"] = np.array([new[p] for p in x["pair"]])
        return y
    return Relation("relabel_pairs", tf, lambda a, b, *_: _close(a, b), "invariant")


def negate_world() -> Relation:
    """Negate outputs and targets of every unit: accuracy is equivariant (unchanged)."""
    def tf(x, rng):
        y = _copy(x)
        y["outputs"] = -np.asarray(x["outputs"])
        y["targets"] = -np.asarray(x["targets"])
        return y
    return Relation("negate_world", tf, lambda a, b, *_: _close(a, b), "equivariant")


def cue_blind_must_be_half(key: Optional[str] = None) -> Relation:
    """Replace each unit's outputs by its partner's (a cue-blind specimen under mirror pairs): the accuracy
    statistic (y[key] when the experiment returns a dict) must become exactly 1/2. An experiment that does
    not is mis-pairing units, mis-scoring ties, or reading only one side of each pair."""
    def tf(x, rng):
        y = _copy(x)
        pair = np.asarray(x["pair"])
        out = np.asarray(x["outputs"]).copy()
        for p in np.unique(pair):
            i = np.nonzero(pair == p)[0]
            out[i[1]] = out[i[0]]
        y["outputs"] = out
        return y

    def chk(a, b, x, x2):
        t = np.asarray(x["targets"])
        pair = np.asarray(x["pair"])
        for p in np.unique(pair):                 # only applies when partners' targets are negated
            i = np.nonzero(pair == p)[0]
            if len(i) != 2 or not np.array_equal(t[i[0]], -t[i[1]]):
                return None
        return _close(b[key] if key is not None else b, 0.5)
    return Relation("cue_blind_must_be_half", tf, chk, "must_change")


def _close(a, b, tol=1e-12) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_close(a[k], b[k], tol) for k in a)
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    return bool(np.allclose(np.asarray(a, float), np.asarray(b, float), atol=tol, equal_nan=True))


# ----------------------------------------------------------------------------- mutation OPERATORS on a pipeline
# W2-C (harvest/wave2/W2-C/pte_mut) corrupts a running PTE pipeline with operators applied as context managers
# and classifies each operator x stage x fixture. The engine-agnostic protocol below adopts W2-C's expectation
# and classification vocabulary VERBATIM (pte_mut/score.py, read-only coordination), so an engine only supplies
# operators, a stage function and an expectation table declared before any mutant runs.

class MutationOperator(Protocol):
    name: str

    def active(self) -> ContextManager: ...


@dataclasses.dataclass
class StageResult:
    verdict: Any                                   # what the stage reports
    alarms: tuple = ()                             # self-detected anomaly states (guards that fired)
    fingerprints: tuple = ()                       # world/trace digests (equal -> the mutant was inert)
    numeric: dict = dataclasses.field(default_factory=dict)


EXPECTATIONS = ("change", "alarm_only", "invariant", "unknown")
CATEGORIES = ("KILLED(A)", "KILLED(D)", "EQUIVALENT", "SURVIVED", "UNRESOLVED", "FRAGILE")


def classify_mutant(base: StageResult, mut: StageResult, expectation: str) -> dict:
    """W2-C semantics: FRAGILE (an 'invariant' mutant changed the verdict or alarmed) > KILLED(A) (new alarm:
    self-detection) > KILLED(D) (verdict differs: only a differential comparison sees it) > EQUIVALENT (inert
    worlds, or expectation 'invariant') > UNRESOLVED (expectation 'unknown') > SURVIVED."""
    if expectation not in EXPECTATIONS:
        raise ValueError(expectation)
    new_alarms = sorted(set(mut.alarms) - set(base.alarms))
    changed = mut.verdict != base.verdict
    inert = bool(base.fingerprints) and tuple(base.fingerprints) == tuple(mut.fingerprints)
    if expectation == "invariant" and (changed or new_alarms):
        cat = "FRAGILE"
    elif new_alarms:
        cat = "KILLED(A)"
    elif changed:
        cat = "KILLED(D)"
    elif inert or expectation == "invariant":
        cat = "EQUIVALENT"
    elif expectation == "unknown":
        cat = "UNRESOLVED"
    else:
        cat = "SURVIVED"
    return {"category": cat, "expectation": expectation, "verdict_changed": changed, "new_alarms": new_alarms,
            "inert": inert, "base_verdict": base.verdict, "mut_verdict": mut.verdict}


def run_operator_suite(stage: Callable[[Any], StageResult], fixtures: dict, operators: list,
                       expect: Callable[[str, str], str]) -> dict:
    """stage(fixture) -> StageResult; operators: MutationOperator list; expect(op_name, fixture_name) ->
    expectation. The spec table is computed BEFORE any mutant runs and returned with the results, so it can
    be hashed and committed first."""
    spec = {(op.name, fx): expect(op.name, fx) for op in operators for fx in fixtures}
    base = {fx: stage(f) for fx, f in fixtures.items()}
    rows = {}
    for op in operators:
        for fx, f in fixtures.items():
            with op.active():
                m = stage(f)
            rows[(op.name, fx)] = classify_mutant(base[fx], m, spec[(op.name, fx)])
    counts = {c: sum(r["category"] == c for r in rows.values()) for c in CATEGORIES}
    return {"spec": {f"{k[0]}|{k[1]}": v for k, v in spec.items()}, "rows": rows, "counts": counts,
            "survivors": [k for k, r in rows.items() if r["category"] == "SURVIVED"],
            "fragile": [k for k, r in rows.items() if r["category"] == "FRAGILE"]}


@contextlib.contextmanager
def patched_attr(obj, name: str, value):
    """Minimal operator helper: set obj.name = value inside the block and always restore it."""
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)
