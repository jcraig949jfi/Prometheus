"""FROZEN FACTOR GRAMMAR (Z80 x Atlas). Every experiment is assembled from these axes; Python may instantiate, mutate,
combine, schedule, promote and retire specs only from here. Frozen at launch: GRAMMAR_FROZEN.json carries the digest.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional

from proteus.foundry.prng import SplitMix64, seed_from

AXES: Dict[str, List] = {
    "world.topology": ["well_mixed", "grid_vn", "graph", "ring_soup", "niches"],
    "world.migration": ["none", "low", "high", "periodic", "competence", "env_dependent"],
    "world.resources": ["unlimited", "limited"],
    "world.env_dynamics": ["fixed", "nonstationary", "local_shift", "env_mutate", "env_coevolve"],
    "world.reservoir": [False, True],
    "representation.substrate": ["z80", "vmcopy"],
    "representation.genome": [32, 64],
    "representation.layout": ["shared", "separated"],
    "reproduction": ["EXTERNAL", "ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION"],
    "pressure": ["implicit_survival", "explicit_fitness", "competence_gated", "resource_gated", "metabolic", "exec_time", "tape_cost", "novelty", "qd", "minimal_criterion", "resource_competition", "recombination"],
    "task": ["none", "CONST_atomic", "CONST_incremental", "ECHO_forced", "ECHO_abr", "INC1", "NEG", "COND_1edit", "COND_multi", "ADD2"],
    "mutation": ["local_byte", "operand_bias", "opcode_bias", "structural"],
    "init": ["random", "seeded_replicator"],
}
BLOCKED = {"representation.substrate": {"nestor_tape": "BLOCKED_MISSING_CAPABILITY: Nestor tape organisms not importable in this worktree",
                                        "nestor_tree": "BLOCKED_MISSING_CAPABILITY: Nestor tree organisms not importable in this worktree"}}
ATLAS_AXES = ["damage_ruler", "length_robustness(genome 32 vs 64)", "selection_vs_drift(implicit_survival vs explicit_fitness)", "deleterious_load(fidelity, ruler)",
              "transport(late-stage transplant)", "equal_compute(EXTERNAL control same step_cap/budget)", "implicit_vs_explicit", "stasis_escape(telemetry)",
              "recombination(pressure; PAIR_EXECUTION)", "transition_detectors(first_crossing, new_arch)", "coevolution_vs_curriculum_vs_randomization(env_dynamics)", "damage_under_alt_substrate(z80 vs vmcopy)"]

FROZEN = {
    "cases_per_opportunity": 3, "init_fill_pct": 60, "seed_fraction_pct": 10, "energy_init": 40.0, "intake_base": 2.0, "intake_gain": 12.0, "gate_floor": 0.15,
    "minimal_criterion": 0.5, "mc_penalty": 0.25, "exec_cost": 0.004, "tape_cost": 0.02, "novelty_bonus": 6.0, "qd_bonus": 4.0, "resource_cap": 30.0, "resource_regen": 3.0,
    "copy_min_frac": 0.9, "copy_noise": 0.004, "background_mutation": 0.02, "mutation_rate": 0.03, "external_replace_frac": 0.15, "max_age": 60, "death_rate": 0.01, "fitness_death": 0.15,
    "migration": {"none": 0.0, "low": 0.002, "high": 0.02, "periodic": 0.05, "competence": 0.0, "env_dependent": 0.0}, "stress_score": 0.2, "env_period": 100, "env_reproduce_score": 0.8,
    "cross_score": 0.999, "coexist_frac": 0.1, "compression_ratio": 0.75, "spont_births": 50, "spont_pop_frac": 0.25, "spont_fid": 0.9, "ruler_samples": 64,
    "snapshot_cap": 24, "snapshot_min_gap": 10, "event_cap": 20000,
    "budgets": {"early": {"vm_steps": 60_000_000, "step_cap": 256, "max_epochs": 1500}, "middle": {"vm_steps": 150_000_000, "step_cap": 256, "max_epochs": 4000}, "late": {"vm_steps": 150_000_000, "step_cap": 256, "max_epochs": 4000}},
    "N": 128, "niches": 4,
    # scheduler (wall-clock hours from campaign start)
    "campaign_hours": 72.0, "early_until_h": 16.0, "late_from_h": 60.0, "stop_launch_h": 71.6, "exploration_floor": 0.30, "workers": 24,
    "promotion_weights": {"spontaneous_replication": 5, "moat_crossed": 2, "moat_advantage": 6, "compression": 2, "new_arch_events": 1, "coexistence": 1, "persistence_over_control": 1,
                          "ruler_gain": 2, "transport": 1, "env_lineage": 1, "longevity": 1, "exploit": 0},
    "promote_min": 3, "promote_children": 3, "retire_after_runs": 3, "verify_top": 12, "verify_seeds": 3,
    "signal_thresholds": {"coexist_epochs": 200, "new_arch_events": 20, "ruler_gain": 0.15, "longevity": 300, "persistence_delta": 0.15, "env_births": 3, "migrations": 20},
}
CONSTRAINTS = [
    ("explicit_fitness only with EXTERNAL", lambda s: "explicit_fitness" not in s["pressure"] or s["reproduction"] == "EXTERNAL"),
    ("recombination only with EXTERNAL (PAIR_EXECUTION is the endogenous form)", lambda s: "recombination" not in s["pressure"] or s["reproduction"] == "EXTERNAL"),
    ("separated layout needs a task", lambda s: s["representation"]["layout"] == "shared" or s["task"]["name"] != "none"),
    ("migration / reservoir need niches", lambda s: s["world"]["topology"] == "niches" or (s["world"]["migration"] == "none" and not s["world"]["reservoir"])),
    ("env dynamics that move between niches need niches", lambda s: s["world"]["env_dynamics"] not in ("local_shift", "env_coevolve") or s["world"]["topology"] == "niches"),
    ("at most two pressures", lambda s: 1 <= len(s["pressure"]) <= 2),
    ("CONSTRUCTIVE needs deaths (always true: death_rate > 0)", lambda s: True),
]


def digest() -> str:
    return hashlib.sha256(json.dumps({"AXES": AXES, "FROZEN": FROZEN, "constraints": [c[0] for c in CONSTRAINTS]}, sort_keys=True, default=str).encode()).hexdigest()[:16]


def spec_id(s: dict) -> str:
    return hashlib.sha256(json.dumps({k: v for k, v in s.items() if k not in ("spec_id", "parents", "family", "scheduler_reason", "stage", "budget")}, sort_keys=True).encode()).hexdigest()[:12]


def make(world: dict, rep: dict, reproduction: str, pressure: List[str], task: str, mutation: str, init: str, *, stage: str, parents=None, family=None, reason="", init_hybrid=True) -> dict:
    s = {"schema": "archaeon.z80atlas.spec.v1", "grammar": digest(), "world": world, "representation": rep, "reproduction": reproduction, "pressure": sorted(pressure), "task": {"name": task},
         "mutation": mutation, "init": init, "init_hybrid": init_hybrid, "population": {"N": FROZEN["N"]}, "budget": dict(FROZEN["budgets"][stage]), "stage": stage,
         "parents": parents or [], "scheduler_reason": reason}
    s["spec_id"] = spec_id(s); s["family"] = family or s["spec_id"]
    for name, ok in CONSTRAINTS:
        if not ok(s):
            return None
    return s


def factor_vector(s: dict) -> dict:
    return {"world.topology": s["world"]["topology"], "world.migration": s["world"]["migration"], "world.resources": s["world"]["resources"], "world.env_dynamics": s["world"]["env_dynamics"],
            "world.reservoir": s["world"]["reservoir"], "representation.substrate": s["representation"]["substrate"], "representation.genome": s["representation"]["genome"],
            "representation.layout": s["representation"]["layout"], "reproduction": s["reproduction"], "pressure": "+".join(s["pressure"]), "task": s["task"]["name"], "mutation": s["mutation"], "init": s["init"]}


def random_spec(rng: SplitMix64, stage: str, coverage: Dict[str, int], reason: str) -> Optional[dict]:
    """Sparse coverage: draw each axis level with weight 1/(1+count of that level in coverage), so underexplored levels and
    pairs are favoured; pairwise coverage counted by the scheduler. Structural axes vary before numeric ones (no numeric axis here)."""
    def pick(axis):
        lv = AXES[axis]; w = [1.0 / (1 + coverage.get("%s=%s" % (axis, l), 0)) for l in lv]; t = sum(w); x = rng.randbelow(1000000) / 1000000 * t
        for l, ww in zip(lv, w):
            x -= ww
            if x <= 0: return l
        return lv[-1]
    for _ in range(50):
        topo = pick("world.topology")
        world = {"topology": topo, "migration": pick("world.migration") if topo == "niches" else "none", "resources": pick("world.resources"), "env_dynamics": pick("world.env_dynamics"),
                 "reservoir": pick("world.reservoir") if topo == "niches" else False, "niches": FROZEN["niches"]}
        rep = {"substrate": pick("representation.substrate"), "genome": pick("representation.genome"), "layout": pick("representation.layout")}
        repro = pick("reproduction"); n_p = 1 + rng.randbelow(2); press = []
        while len(press) < n_p:
            p = pick("pressure")
            if p not in press: press.append(p)
        s = make(world, rep, repro, press, pick("task"), pick("mutation"), pick("init"), stage=stage, reason=reason)
        if s: return s
    return None


def matched_controls(s: dict, stage: str) -> List[dict]:
    """The controls every treatment carries (equal compute): reproduction flipped (endogenous <-> EXTERNAL), and for
    accessibility tasks the representation flip (atomic <-> incremental, forced <-> abr, 1edit <-> multi)."""
    out = []
    flip_r = "EXTERNAL" if s["reproduction"] != "EXTERNAL" else "ENDOGENOUS_COPY"
    press = [p for p in s["pressure"] if not (flip_r != "EXTERNAL" and p in ("explicit_fitness", "recombination"))] or ["implicit_survival"]
    c = make(s["world"], s["representation"], flip_r, press, s["task"]["name"], s["mutation"], s["init"], stage=stage, parents=[s["spec_id"]], family=s["family"], reason="matched_control:reproduction")
    if c: out.append(c)
    pairs = {"CONST_atomic": "CONST_incremental", "CONST_incremental": "CONST_atomic", "ECHO_forced": "ECHO_abr", "ECHO_abr": "ECHO_forced", "COND_1edit": "COND_multi", "COND_multi": "COND_1edit"}
    t = s["task"]["name"]
    if t in pairs:
        c = make(s["world"], s["representation"], s["reproduction"], s["pressure"], pairs[t], s["mutation"], s["init"], stage=stage, parents=[s["spec_id"]], family=s["family"], reason="matched_control:accessibility")
        if c: out.append(c)
    return out


def mutate_spec(s: dict, rng: SplitMix64, stage: str, reason: str) -> Optional[dict]:
    """One-factor neighbour of a promoted spec (the producer 'mutates' experiments only inside the grammar)."""
    for _ in range(30):
        axis = list(AXES.keys())[rng.randbelow(len(AXES))]; lv = AXES[axis]; v = lv[rng.randbelow(len(lv))]
        w = json.loads(json.dumps(s["world"])); r = dict(s["representation"]); repro = s["reproduction"]; press = list(s["pressure"]); task = s["task"]["name"]; mut = s["mutation"]; init = s["init"]
        if axis.startswith("world."): w[axis.split(".")[1]] = v
        elif axis.startswith("representation."): r[axis.split(".")[1]] = v
        elif axis == "reproduction": repro = v
        elif axis == "pressure":
            if v in press and len(press) > 1: press.remove(v)
            elif v not in press: press = (press + [v])[-2:]
        elif axis == "task": task = v
        elif axis == "mutation": mut = v
        elif axis == "init": init = v
        c = make(w, r, repro, press, task, mut, init, stage=stage, parents=[s["spec_id"]], family=s["family"], reason=reason + ":" + axis)
        if c and c["spec_id"] != s["spec_id"]: return c
    return None


def combine_specs(a: dict, b: dict, rng: SplitMix64, stage: str, reason: str) -> Optional[dict]:
    """Crossover of two promoted factor vectors (uniform per axis)."""
    for _ in range(20):
        pk = lambda x, y: x if rng.randbelow(2) else y
        w = {k: pk(a["world"][k], b["world"][k]) for k in a["world"]}; r = {k: pk(a["representation"][k], b["representation"][k]) for k in a["representation"]}
        c = make(w, r, pk(a["reproduction"], b["reproduction"]), pk(a["pressure"], b["pressure"]), pk(a["task"]["name"], b["task"]["name"]), pk(a["mutation"], b["mutation"]), pk(a["init"], b["init"]),
                 stage=stage, parents=[a["spec_id"], b["spec_id"]], family=a["family"], reason=reason)
        if c: return c
    return None


def positive_controls(stage: str = "early") -> List[dict]:
    """Calibration specs that must pass before promotion is trusted (recorded, never patched during the campaign)."""
    out = []
    wm = {"topology": "well_mixed", "migration": "none", "resources": "unlimited", "env_dynamics": "fixed", "reservoir": False, "niches": 1}
    for sub in ("z80", "vmcopy"):
        rep = {"substrate": sub, "genome": 32, "layout": "shared"}
        out.append(make(wm, rep, "ENDOGENOUS_COPY", ["implicit_survival"], "none", "local_byte", "seeded_replicator", stage=stage, reason="positive_control:replicator_replicates"))
        out.append(make(wm, rep, "EXTERNAL", ["explicit_fitness"], "CONST_incremental", "local_byte", "random", stage=stage, reason="positive_control:external_evolves"))
        out.append(make(wm, rep, "ENDOGENOUS_COPY", ["competence_gated"], "ECHO_forced", "local_byte", "seeded_replicator", stage=stage, reason="positive_control:endogenous_invades_when_seeded"))
    return [s for s in out if s]


def control_verdict(s: dict, sig: dict) -> str:
    r = s["scheduler_reason"]
    if r.endswith("replicator_replicates"): return "PASS" if sig["births_endo"] >= 50 and (sig["fidelity_late"] or 0) >= 0.95 else "FAIL"
    if r.endswith("external_evolves"): return "PASS" if sig["best_ever"] >= 0.9 else "FAIL"
    if r.endswith("endogenous_invades_when_seeded"): return "PASS" if sig["final_pop_frac"] >= 0.5 and sig["births_endo"] >= 50 else "FAIL"
    return "N/A"
