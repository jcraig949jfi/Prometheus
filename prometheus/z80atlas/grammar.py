"""The FROZEN factor grammar. Every experiment the campaign ever runs is a factor VECTOR over these axes; the
producer may only instantiate, mutate (one factor), combine (cross a vector with a collision template), replicate
(fresh seed), promote (allocate more) and retire. No level, axis, constraint or threshold changes during a campaign:
grammar_hash() is recorded at start and re-checked on every resume.

Levels that exist in the directive but are UNAVAILABLE on this seat are declared as such with the reason, never
silently substituted (the same rule as D-BELL-2)."""
from __future__ import annotations

import hashlib
import inspect
import itertools
import json
import random
from typing import Dict, List, Optional, Tuple

from prometheus.z80atlas.world import Config, ENDOGENOUS

FACTORS: Dict[str, Tuple[str, ...]] = {
    "world":          ("SOUP", "GRID", "NICHES", "GRAPH"),
    "representation": ("Z80_64", "BYTECODE32", "VM_COPY"),
    "layout":         ("SHARED", "SEPARATED"),
    "reproduction":   ("EXTERNAL", "ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION"),
    "pressure":       ("IMPLICIT", "EXPLICIT", "GATED_INTERACTION", "RESOURCE_GATED", "METABOLIC", "NOVELTY", "QD", "MINIMAL_CRITERION", "EXPLOIT"),
    "spatial":        ("WELL_MIXED", "LOCAL", "NICHES_ISOLATED", "NICHES_LOW_MIG", "NICHES_HIGH_MIG", "NICHES_PERIODIC",
                       "NICHES_COMPETENCE_MIG", "NICHES_POLLINATION", "NICHES_ENV_MIG", "RESERVOIR"),
    "task":           ("CONST", "ECHO", "INC", "COND_ONE", "COND_MULTI", "SUM2"),
    "scoring":        ("ATOMIC", "INCREMENTAL", "NEUTRAL"),
    "read_gate":      ("ABR", "FORCED"),
    "env_dynamics":   ("FIXED", "SHIFT", "DRIFT", "COEVOLVE", "PER_NICHE", "ENV_REPRO"),
    "mutation":       ("OPERAND", "OPCODE", "BYTE", "STRUCTURAL"),
    "mutation_rate":  ("LOW", "MED", "HIGH"),
    "recombination":  ("NONE", "CROSSOVER"),
    "init":           ("RANDOM", "SEEDED_REPLICATOR", "SEEDED_WITNESS", "SEEDED_HYBRID"),
}
AXES = tuple(FACTORS)

UNAVAILABLE = {
    "representation:NESTOR_TAPE": "Nestor's tape/tree organisms live on M1-local branches not readable from this seat (UNAVAILABLE_INTERFACE); not emulated",
    "pressure:PREDATOR_PREY_EXPLICIT": "only the EXPLOIT coupling (read-and-overwrite feeds the exploiter) is implemented; no separate prey species",
}

# the directive's high-value collisions, as partial vectors the producer CROSSES onto sampled vectors
COLLISIONS: List[Tuple[str, Dict[str, str]]] = [
    ("endogenous x atomic/incremental constants", {"reproduction": "ENDOGENOUS_COPY", "task": "CONST"}),
    ("endogenous x answer-before-read moat", {"reproduction": "ENDOGENOUS_COPY", "read_gate": "FORCED", "task": "ECHO"}),
    ("spatial reservoirs x hard conditional", {"spatial": "RESERVOIR", "task": "COND_MULTI"}),
    ("competence-gated interaction x neutral precursor", {"pressure": "GATED_INTERACTION", "scoring": "INCREMENTAL"}),
    ("metabolic cost x reproductive compression x task complexity", {"pressure": "METABOLIC", "task": "COND_MULTI"}),
    ("world co-evolution x endogenous replication", {"env_dynamics": "COEVOLVE", "task": "CONST", "reproduction": "ENDOGENOUS_PARTIAL"}),
    ("damage rulers x repro-code vs task-code regions", {"layout": "SEPARATED", "mutation_rate": "HIGH"}),
    ("recombination x self-copying architecture", {"reproduction": "PAIR_EXECUTION", "init": "SEEDED_REPLICATOR"}),
    ("cross-niche migration x standing variation", {"spatial": "NICHES_LOW_MIG", "env_dynamics": "SHIFT"}),
    ("mutation-selection load x shared replication/task tape", {"layout": "SHARED", "mutation_rate": "HIGH", "reproduction": "ENDOGENOUS_COPY"}),
    ("environment shifts x persistence of reproductive machinery", {"env_dynamics": "SHIFT", "reproduction": "OVERWRITE"}),
    ("minimal criterion x spontaneous replication", {"pressure": "MINIMAL_CRITERION", "init": "RANDOM", "reproduction": "ENDOGENOUS_PARTIAL"}),
]

# critical controls: (name, axis, level for the treatment side, level for the control side)
CRITICAL_CONTROLS = [
    ("endogenous_vs_exogenous", "reproduction", None, "EXTERNAL"),
    ("gated_vs_ungated", "pressure", "GATED_INTERACTION", "IMPLICIT"),
    ("local_vs_wellmixed", "spatial", "LOCAL", "WELL_MIXED"),
    ("migration_vs_isolation", "spatial", "NICHES_LOW_MIG", "NICHES_ISOLATED"),
    ("atomic_vs_incremental", "scoring", "ATOMIC", "INCREMENTAL"),
    ("fixed_vs_evolving_env", "env_dynamics", None, "FIXED"),
    ("task_pressure_vs_neutral", "scoring", None, "NEUTRAL"),
    ("metabolic_vs_none", "pressure", "METABOLIC", "IMPLICIT"),
]


def violations(vec: Dict[str, str]) -> List[str]:
    v = []
    for a in AXES:
        if vec.get(a) not in FACTORS[a]:
            v.append("axis %s has no level %r" % (a, vec.get(a)))
    if v:
        return v
    niche_spatial = vec["spatial"].startswith("NICHES") or vec["spatial"] == "RESERVOIR"
    if niche_spatial and vec["world"] != "NICHES":
        v.append("niche spatial policies require world=NICHES")
    if vec["world"] == "NICHES" and not niche_spatial:
        v.append("world=NICHES requires a niche spatial policy")
    if vec["world"] == "SOUP" and vec["spatial"] != "WELL_MIXED":
        v.append("SOUP is well mixed by definition")
    if vec["world"] == "GRAPH" and vec["spatial"] != "LOCAL":
        v.append("GRAPH interactions are along edges (LOCAL)")
    if vec["env_dynamics"] in ("PER_NICHE", "ENV_REPRO") and not niche_spatial:
        v.append("%s needs niches" % vec["env_dynamics"])
    if vec["env_dynamics"] == "COEVOLVE" and vec["task"] != "CONST":
        v.append("COEVOLVE moves a constant target: task must be CONST")
    if vec["recombination"] == "CROSSOVER" and vec["reproduction"] != "EXTERNAL":
        v.append("CROSSOVER is a population-manager operator: EXTERNAL only (endogenous recombination is PAIR_EXECUTION)")
    if vec["reproduction"] == "PAIR_EXECUTION" and vec["layout"] != "SHARED":
        v.append("PAIR_EXECUTION concatenates whole tapes: layout must be SHARED")
    if vec["scoring"] == "NEUTRAL" and vec["pressure"] in ("EXPLICIT", "GATED_INTERACTION", "RESOURCE_GATED", "QD"):
        v.append("a task-coupled pressure with a NEUTRAL task is undefined")
    if vec["pressure"] == "MINIMAL_CRITERION" and vec["reproduction"] == "EXTERNAL":
        v.append("MINIMAL_CRITERION (must replicate to persist) needs endogenous reproduction")
    if vec["spatial"] == "RESERVOIR" and vec["task"] in ("ECHO", "CONST"):
        v.append("RESERVOIR's easy niche is ECHO; the hard niches need a harder task")
    return v


def is_valid(vec: Dict[str, str]) -> bool:
    return not violations(vec)


def vec_id(vec: Dict[str, str]) -> str:
    return hashlib.sha256(json.dumps({a: vec[a] for a in AXES}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def to_config(vec: Dict[str, str], ticks: int, cells: int, budget: int = 256, init_tapes: Tuple[str, ...] = ()) -> Config:
    return Config(ticks=ticks, cells=cells, budget=budget, init_tapes=init_tapes, **{a: vec[a] for a in AXES})


def random_vec(rng: random.Random, fixed: Optional[Dict[str, str]] = None, tries: int = 400) -> Optional[Dict[str, str]]:
    for _ in range(tries):
        vec = {a: rng.choice(FACTORS[a]) for a in AXES}
        if fixed:
            vec.update(fixed)
            # repair the structural implications of a partial template
            if vec["spatial"].startswith("NICHES") or vec["spatial"] == "RESERVOIR":
                vec["world"] = "NICHES"
            elif vec["world"] == "NICHES":
                vec["spatial"] = rng.choice([s for s in FACTORS["spatial"] if s.startswith("NICHES")])
            if vec["world"] == "SOUP":
                vec["spatial"] = "WELL_MIXED"
            if vec["world"] == "GRAPH":
                vec["spatial"] = "LOCAL"
        if is_valid(vec):
            return vec
    return None


def pairs_of(vec: Dict[str, str]) -> set:
    return {(a, vec[a], b, vec[b]) for a, b in itertools.combinations(AXES, 2)}


def triples_of(vec: Dict[str, str]) -> set:
    return {(a, vec[a], b, vec[b], c, vec[c]) for a, b, c in itertools.combinations(AXES, 3)}


def sample_sparse(rng: random.Random, n: int, covered_pairs: set, fixed: Optional[Dict[str, str]] = None, candidates: int = 40) -> List[Dict[str, str]]:
    """Greedy pairwise-coverage sampling: each pick is the candidate that covers the most still-uncovered
    (axis=level, axis=level) pairs. Sparse initial coverage; interaction-driven, never uniform enumeration."""
    out = []
    cov = set(covered_pairs)
    for _ in range(n):
        best = None; best_gain = -1
        for _ in range(candidates):
            v = random_vec(rng, fixed)
            if v is None:
                continue
            gain = len(pairs_of(v) - cov)
            if gain > best_gain:
                best, best_gain = v, gain
        if best is None:
            break
        out.append(best); cov |= pairs_of(best)
    return out


def neighbours(vec: Dict[str, str], rng: random.Random, k: int = 4) -> List[Dict[str, str]]:
    """One-factor mutations of a vector (the producer's 'mutate' move), valid ones only, k at random."""
    outs = []
    axes = list(AXES); rng.shuffle(axes)
    for a in axes:
        for lvl in FACTORS[a]:
            if lvl == vec[a]:
                continue
            v = dict(vec, **{a: lvl})
            if is_valid(v):
                outs.append(v)
    rng.shuffle(outs)
    return outs[:k]


def repair(v: Dict[str, str], protect: Tuple[str, ...] = ()) -> Dict[str, str]:
    """Resolve the structural implications of a partial template deterministically (never touching `protect`)."""
    v = dict(v)
    def setif(a, lvl):
        if a not in protect:
            v[a] = lvl
    if v["spatial"].startswith("NICHES") or v["spatial"] == "RESERVOIR":
        setif("world", "NICHES")
    elif v["world"] == "NICHES":
        setif("spatial", "NICHES_LOW_MIG")
    if v["world"] == "SOUP":
        setif("spatial", "WELL_MIXED")
    if v["world"] == "GRAPH":
        setif("spatial", "LOCAL")
    if v["spatial"] == "RESERVOIR" and v["task"] in ("ECHO", "CONST"):
        setif("spatial", "NICHES_LOW_MIG")
    if v["env_dynamics"] in ("PER_NICHE", "ENV_REPRO") and v["world"] != "NICHES":
        setif("env_dynamics", "FIXED")
    if v["env_dynamics"] == "COEVOLVE" and v["task"] != "CONST":
        setif("env_dynamics", "FIXED")
    if v["reproduction"] == "PAIR_EXECUTION":
        setif("layout", "SHARED")
    if v["reproduction"] != "EXTERNAL":
        setif("recombination", "NONE")
    if v["pressure"] == "MINIMAL_CRITERION" and v["reproduction"] == "EXTERNAL":
        setif("pressure", "IMPLICIT")
    if v["scoring"] == "NEUTRAL" and v["pressure"] in ("EXPLICIT", "GATED_INTERACTION", "RESOURCE_GATED", "QD"):
        setif("pressure", "IMPLICIT")
    return v


def cross(vec: Dict[str, str], template: Dict[str, str]) -> Optional[Dict[str, str]]:
    v = repair(dict(vec, **template), protect=tuple(template))
    return v if is_valid(v) else None


def matched_controls(vec: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """The critical-controls set for a treatment vector: each control flips ONE axis (matched pair)."""
    out = {}
    for name, axis, treat_level, ctrl_level in CRITICAL_CONTROLS:
        if treat_level is not None and vec[axis] != treat_level:
            continue
        if vec[axis] == ctrl_level:
            continue
        v = dict(vec, **{axis: ctrl_level})
        if axis == "reproduction" and ctrl_level == "EXTERNAL" and v["pressure"] == "MINIMAL_CRITERION":
            v["pressure"] = "IMPLICIT"
        if axis == "scoring" and ctrl_level == "NEUTRAL" and v["pressure"] in ("EXPLICIT", "GATED_INTERACTION", "RESOURCE_GATED", "QD"):
            v["pressure"] = "IMPLICIT"
        if is_valid(v):
            out[name] = v
    # the reverse of endogenous_vs_exogenous: an EXTERNAL treatment gets its endogenous partner
    if vec["reproduction"] == "EXTERNAL":
        v = dict(vec, reproduction="ENDOGENOUS_COPY", recombination="NONE")
        if is_valid(v):
            out["exogenous_vs_endogenous"] = v
    return out


def grammar_hash() -> str:
    src = json.dumps({"factors": FACTORS, "unavailable": UNAVAILABLE, "collisions": COLLISIONS, "controls": CRITICAL_CONTROLS}, sort_keys=True)
    src += inspect.getsource(violations)
    return hashlib.sha256(src.encode()).hexdigest()
