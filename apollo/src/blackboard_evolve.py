"""blackboard_evolve.py — Branch C Phase 1 evolutionary loop.

Evolves BlackboardOrganisms (pipelines of typed operator-steps) over the
clean canary, using:
  - role-tiered registry (transformer / scorer; v1 answer-producers quarantined)
  - causal_composition_score = composition_lift x clip+(dataflow_score)
    (gated derived axis per 2026-05-29 review Q5 — NOT independent axes)
  - 4 during-run abort conditions (mutation viability, causal-slot
    starvation, terminal-router dominance, role collapse)
  - JSON-DSL LLM mutation (Granite) OR deterministic registry mutation

Per Doctrine #2, the loop logs failure signatures, not just fitness scores.

Usage:
    python -m blackboard_evolve --gens 200 --mode deterministic
    python -m blackboard_evolve --gens 1000 --mode llm
"""
from __future__ import annotations
import sys
import json
import random
import argparse
import copy
import time
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src"))

from blackboard import BlackboardState, BlackboardOp, run_pipeline, audit_pipeline
from dataflow_fitness import compute_dataflow_fitness
import blackboard_ops as v1
import blackboard_ops_v2 as v2
import blackboard_ops_r2 as r2  # R2 inference transformers (2026-06-09 falsification PASSED)
import blackboard_ops_compare as cmp  # boolean/comparison primitives (lever 2, 2026-06-26)


# ── Role-tiered registry ──────────────────────────────────────────────

ROLE_TRANSFORMER = "transformer"
ROLE_SCORER = "scorer"          # terminal-only
ROLE_QUARANTINE = "quarantine"  # v1 answer-producers; baseline/terminal only

REGISTRY = {
    # transformers (eligible mid-pipeline, preferred)
    "parse_numbers": (v1.parse_numbers, ROLE_TRANSFORMER),
    "parse_names_and_relations": (v1.parse_names_and_relations, ROLE_TRANSFORMER),
    "parse_question_target": (v1.parse_question_target, ROLE_TRANSFORMER),
    "parse_ordinal": (v2.parse_ordinal, ROLE_TRANSFORMER),
    "parse_box_items": (v2.parse_box_items, ROLE_TRANSFORMER),
    "op_build_ordering": (v2.op_build_ordering, ROLE_TRANSFORMER),
    "op_aggregate_quantities": (v2.op_aggregate_quantities, ROLE_TRANSFORMER),
    "entity_counter": (v2.entity_counter, ROLE_TRANSFORMER),
    "evidence_updater": (v2.evidence_updater, ROLE_TRANSFORMER),
    "distribution_reducer": (v2.distribution_reducer, ROLE_TRANSFORMER),
    "op_transitive_closure": (v1.op_transitive_closure, ROLE_QUARANTINE),  # side-output v1
    # R2 inference transformers (decomposed from hephaestus r2_chain_tracker;
    # falsification PASSED 2026-06-09 — forward_chain is a load-bearing R2 op
    # the R0-R1 set provably can't reach; see pivot/r2_falsification_result_*.json)
    "parse_rules": (r2.parse_rules, ROLE_TRANSFORMER),
    "forward_chain": (r2.forward_chain, ROLE_TRANSFORMER),
    # R2->R1 type bridge (2026-06-10): lets forward_chain feed op_build_ordering;
    # cross-tier falsification PASSED — see pivot/cross_tier_falsification_result_*.json
    "relations_from_facts": (r2.relations_from_facts, ROLE_TRANSFORMER),
    # comparison/boolean transformers (lever 2, 2026-06-26): parse "Is X larger than
    # Y?" / "which is larger?" into typed slots so a guarded scorer can route them.
    "parse_comparison": (cmp.parse_comparison, ROLE_TRANSFORMER),
    "parse_which_extreme": (cmp.parse_which_extreme, ROLE_TRANSFORMER),
    # scorers (terminal-only)
    "select_nth": (v2.select_nth, ROLE_SCORER),
    "score_by_aggregate": (v2.score_by_aggregate, ROLE_SCORER),
    "score_by_derivability": (r2.score_by_derivability, ROLE_SCORER),
    "score_by_max_entity": (v1.score_by_max_entity, ROLE_SCORER),
    "score_by_max_value": (v1.score_by_max_value, ROLE_SCORER),
    # quarantined v1 answer-producers
    "op_numeric_argmax": (v1.op_numeric_argmax, ROLE_QUARANTINE),
}


# ── Guarded scorer atoms (DISPATCH / routing — falsification PASSED 2026-06-24) ──
# A scorer whose precondition fails is skipped (on_fail="skip") and leaves
# selected_answer untouched. With MUTUALLY-EXCLUSIVE preconditions keyed on
# SEMANTIC SLOTS (never problem_text surface — that would be memorization), several
# guarded scorers coexist in one organism and exactly one fires per task: a pipeline
# of guarded scorers IS a dispatcher. This is the R3 step that breaks the
# single-terminal best_acc ceiling (0.558 diagnosis). Validated G1-G4 in
# scripts/dispatch_falsification.py; see pivot/dispatch_falsification_findings_2026-06-24.md.
# The exclusion clauses encode routing priority structurally, so correctness does
# NOT depend on tail-ordering (the Goodhart trap the PoC surfaced).
def _guarded(base_name, precond):
    base = REGISTRY[base_name][0]
    return BlackboardOp(base.fn, reads=base.reads, writes=base.writes,
                        precondition=precond, on_fail="skip", name=base_name + "__g")

REGISTRY.update({
    "select_nth__g": (_guarded("select_nth",
        lambda s: len(s.ordered) > 0), ROLE_SCORER),
    "score_by_derivability__g": (_guarded("score_by_derivability",
        lambda s: (len(s.derived_facts) > 0 or len(s.facts) > 0) and len(s.ordered) == 0), ROLE_SCORER),
    # NOTE (2026-06-27): guard keys on `counts` (what parse_box_items writes), NOT
    # `quantities` (which nothing writes — a latent bug that made this branch ALWAYS
    # decorative and produced a spurious "aggregate solves 0 synth" falsification).
    # With the fix, parse_box_items→op_aggregate_quantities→this scorer routes the
    # two_stage_count synth tasks (synth 15→30). counts is empty on non-box tasks.
    "score_by_aggregate__g": (_guarded("score_by_aggregate",
        lambda s: len(s.counts) > 0 and len(s.ordered) == 0
                  and len(s.derived_facts) == 0 and len(s.facts) == 0), ROLE_SCORER),
    # comparison/boolean guarded scorers (lever 2, 2026-06-26): preconditions are
    # built into the ops (comparison is not None / extreme_number != ""); they key on
    # the typed slots their parser transformers write, mutually exclusive with the
    # ordering/inference/aggregate guards (compare tasks populate neither).
    "score_by_comparison__g": (cmp.score_by_comparison, ROLE_SCORER),
    "score_by_extreme_number__g": (cmp.score_by_extreme_number, ROLE_SCORER),
})

GUARDED_SCORERS = ["select_nth__g", "score_by_derivability__g", "score_by_aggregate__g",
                   "score_by_comparison__g", "score_by_extreme_number__g"]

TRANSFORMERS = [n for n, (_, r) in REGISTRY.items() if r == ROLE_TRANSFORMER]
SCORERS = [n for n, (_, r) in REGISTRY.items() if r == ROLE_SCORER]
PLAIN_SCORERS = [n for n in SCORERS if n not in GUARDED_SCORERS]

# Scorer pool mutation draws from. In dispatch mode evolve() narrows this to
# GUARDED_SCORERS only, so plain (unconditional) scorers never enter — that removes
# the SOURCE of plain+guarded "override hybrids" whose unconditional scorer fires on
# every task and racks up incidental hits (the clean-routing pressure, 2026-06-24).
_MUT_SCORER_POOL = SCORERS


def role_of(op_name: str) -> str:
    return REGISTRY.get(op_name, (None, ROLE_QUARANTINE))[1]


# ── Genome ────────────────────────────────────────────────────────────

@dataclass
class BlackboardOrganism:
    pipeline: list[str]            # ordered op names; last must be a scorer
    genome_id: str = ""
    parent_id: str = ""
    lineage: list[str] = field(default_factory=list)   # mutations applied

    def ops(self):
        return [REGISTRY[n][0] for n in self.pipeline if n in REGISTRY]

    def clone(self):
        c = BlackboardOrganism(pipeline=list(self.pipeline),
                               parent_id=self.genome_id,
                               lineage=list(self.lineage))
        c.genome_id = f"{random.randint(0, 1<<30):08x}"
        return c

    def role_signature(self):
        return tuple(role_of(n) for n in self.pipeline)


def _new_id():
    return f"{random.randint(0, 1<<30):08x}"


# ── Seeds ─────────────────────────────────────────────────────────────

def seed_population(size=20, variant="default", dispatch=False):
    # In dispatch mode the specialist seeds use GUARDED scorers so the search can
    # compose them into an order-independent router (add_guard mutation / merge).
    sc = (lambda n: n + "__g") if dispatch else (lambda n: n)
    scorer_pool = GUARDED_SCORERS if dispatch else SCORERS
    pop = []
    # 2 hand-written passing compositions
    a = BlackboardOrganism(["parse_names_and_relations", "parse_ordinal",
                            "op_build_ordering", sc("select_nth")], genome_id=_new_id())
    a.lineage = ["seed:COMP_A"]
    c = BlackboardOrganism(["parse_box_items", "op_aggregate_quantities",
                            sc("score_by_aggregate")], genome_id=_new_id())
    c.lineage = ["seed:COMP_C"]
    # R2 inference shape (validated 2026-06-09): the foothold for climbing
    # past the R0-R1 tier ceiling. forward_chain is the load-bearing keystone.
    r = BlackboardOrganism(["parse_rules", "forward_chain",
                            sc("score_by_derivability")], genome_id=_new_id())
    r.lineage = ["seed:COMP_R2"]
    if variant == "ingredients":
        # Recombination experiment (2026-06-16): seed the two INGREDIENT shapes
        # whose one-point splice IS the cross-tier solver, but NOT the
        # pre-assembled solver itself. P2 == COMP_A (already seeded as `a`); P1 is
        # the R2-inference+bridge shape with the WRONG (derivability) terminal.
        # Crossover must DISCOVER splice(P1, COMP_A); single-step provably can't
        # (recombination_falsification_result_2026-06-16.json). No COMP_CROSS_TIER.
        p1 = BlackboardOrganism(["parse_rules", "parse_ordinal", "forward_chain",
                                 "relations_from_facts", "score_by_derivability"],
                                genome_id=_new_id())
        p1.lineage = ["seed:INGREDIENT_P1"]
        pop.extend([a, c, r, p1])
    else:
        # Cross-tier shape (validated 2026-06-10): the unique solver of the
        # derive-then-order canary. Spans R1 parse + R2 inference + bridge + R1 order.
        xt = BlackboardOrganism(["parse_rules", "parse_ordinal", "forward_chain",
                                 "relations_from_facts", "op_build_ordering",
                                 sc("select_nth")], genome_id=_new_id())
        xt.lineage = ["seed:COMP_CROSS_TIER"]
        pop.extend([a, c, r, xt])
    # random typed pipelines: 1-3 transformers + a scorer
    while len(pop) < size:
        k = random.randint(1, 3)
        body = [random.choice(TRANSFORMERS) for _ in range(k)]
        scorer = random.choice(scorer_pool)
        org = BlackboardOrganism(body + [scorer], genome_id=_new_id())
        org.lineage = ["seed:random"]
        pop.append(org)
    return pop


# ── Mutation (deterministic; LLM mode hooks the same validators) ──────

def mutate_deterministic(org: BlackboardOrganism) -> BlackboardOrganism:
    """Multi-scorer-robust mutation. Body = non-scorer ops; tail may hold several
    guarded scorers (a dispatcher). The `add_guard` move grows a router by
    appending a guarded scorer not already present — the falsification (2026-06-24)
    showed this move ALONE assembles a genuine dispatcher (no bespoke merge needed).
    Removal only targets body ops, so an organism always retains >=1 scorer."""
    child = org.clone()
    p = child.pipeline
    body_idx = [i for i, n in enumerate(p) if role_of(n) != ROLE_SCORER]
    scorer_idx = [i for i, n in enumerate(p) if role_of(n) == ROLE_SCORER]
    move = random.choice(["insert", "remove", "swap_t", "swap_scorer", "add_guard"])
    if move == "insert" and len(body_idx) < 6:
        pos = random.randint(0, len(p))
        p.insert(pos, random.choice(TRANSFORMERS))
        child.lineage.append(f"insert_step@{pos}")
    elif move == "remove" and body_idx:
        pos = random.choice(body_idx)
        removed = p.pop(pos)
        child.lineage.append(f"remove_step:{removed}")
    elif move == "swap_t" and body_idx:
        pos = random.choice(body_idx)
        p[pos] = random.choice(TRANSFORMERS)
        child.lineage.append(f"swap_step@{pos}")
    elif move == "swap_scorer" and scorer_idx:
        pos = random.choice(scorer_idx)
        p[pos] = random.choice(_MUT_SCORER_POOL)
        child.lineage.append("swap_scorer")
    elif move == "add_guard":
        have = {n for n in p if n in GUARDED_SCORERS}
        opts = [g for g in GUARDED_SCORERS if g not in have]
        if opts:
            g = random.choice(opts)
            p.append(g)
            child.lineage.append(f"add_guard:{g}")
    return child


# ── LLM mutation (JSON-DSL interface, dry-run-validated) ──────────────

_LLM_HELPERS = {}

def _load_llm_helpers():
    if _LLM_HELPERS:
        return _LLM_HELPERS
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import mutation_dryrun as md
    _LLM_HELPERS.update(build_prompt=md.build_prompt, extract_json=md.extract_json,
                        validate=md.validate, call_granite=md.call_granite, catalog=md.CATALOG)
    return _LLM_HELPERS


def mutate_llm(org: BlackboardOrganism, llm_fraction=0.5):
    """Propose an insert_step via Granite (JSON-DSL). Falls back to
    deterministic remove/swap so pipelines can also shrink. Returns
    (child, used_llm: bool)."""
    if random.random() > llm_fraction:
        return mutate_deterministic(org), False
    h = _load_llm_helpers()
    text = h["call_granite"](h["build_prompt"](org.pipeline))
    if text.startswith("__ERROR__"):
        return mutate_deterministic(org), False
    obj = h["extract_json"](text)
    p_ok, t_ok, sig = h["validate"](obj, org.pipeline)
    if not t_ok:
        return mutate_deterministic(org), False
    # role guard: only transformers may be inserted mid-pipeline
    op_name = obj["step"]["op"]
    if role_of(op_name) != ROLE_TRANSFORMER:
        return mutate_deterministic(org), False
    child = org.clone()
    pos = obj["position"]
    pos = min(pos, len(child.pipeline) - 1)  # never displace the terminal scorer
    child.pipeline.insert(pos, op_name)
    child.lineage.append(f"llm_insert:{op_name}@{pos}")
    return child, True


# ── Recombination / crossover (validated 2026-06-16) ──────────────────

def recombine(pa: BlackboardOrganism, pb: BlackboardOrganism) -> BlackboardOrganism:
    """One-point splice: prefix(pa body) + suffix(pb from a cut). The child ends
    in pb's terminal scorer; pa contributes BODY ops only (its terminal is
    dropped), so no scorer ever lands mid-pipeline.

    This is the operator Run 1+2 lacked. Single-step mutation can't assemble a
    multi-op multi-tier organism de novo: the coordinated inserts are each
    individually neutral/harmful (a fitness valley >=1 edit wide, first step
    non-improving). One splice crosses that valley. Falsification-validated
    (recombination_falsification_result_2026-06-16.json): crossover reaches a
    load-bearing multi-tier solver at 6.1%/pair while 8000 single-step random
    walks reach it 0%."""
    a, b = pa.pipeline, pb.pipeline
    if len(a) < 2 or len(b) < 1:
        return pa.clone()
    i = random.randint(1, len(a) - 1)   # pa body prefix (>=1 op, excludes pa terminal)
    j = random.randint(0, len(b) - 1)   # pb suffix (>=1 op, includes pb terminal scorer)
    child = pa.clone()
    child.pipeline = a[:i] + b[j:]
    child.lineage = list(pa.lineage) + [f"xover:{pb.genome_id}@({i},{j})"]
    return child


def dispatch_merge(pa: BlackboardOrganism, pb: BlackboardOrganism) -> BlackboardOrganism:
    """Dispatch-aware crossover: UNION of transformer bodies + UNION of guarded
    scorers. Unlike recombine() (single-suffix splice), this brings BOTH parents'
    branches together — crucially each branch's PARSER transformer AND its guarded
    scorer in one move. That co-location is the valley single-step add_guard+insert
    can't cross: a guarded scorer without its parser is decorative (the slot it keys
    on is never written). Validated in dispatch_falsification.py (treatment_merge 5/5).

    Body order: pa's body, then pb's transformers not already present. Guards: the
    unique guarded scorers across both (plain scorers dropped — clean routing)."""
    body_a = [n for n in pa.pipeline if role_of(n) != ROLE_SCORER]
    body_b = [n for n in pb.pipeline if role_of(n) != ROLE_SCORER]
    body = body_a + [n for n in body_b if n not in body_a]
    guards = []
    for n in pa.pipeline + pb.pipeline:
        if n in GUARDED_SCORERS and n not in guards:
            guards.append(n)
    if not guards:
        guards = [random.choice(GUARDED_SCORERS)]
    child = pa.clone()
    child.pipeline = body + guards
    child.lineage = list(pa.lineage) + [f"dmerge:{pb.genome_id}"]
    return child


# ── Fitness ───────────────────────────────────────────────────────────

def _evaluate_acc(pipeline_ops, tasks):
    n = 0
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            out = run_pipeline(pipeline_ops, s)
            if out.selected_answer == t["correct"]:
                n += 1
        except Exception:
            pass
    return n / max(len(tasks), 1)


def _single_primitive_baseline(tasks):
    n = 0
    for t in tasks:
        if t.get("single_primitive_answer") == t["correct"]:
            n += 1
    return n / max(len(tasks), 1)


def _clip_pos(x):
    return max(0.0, x)


def fitness(org: BlackboardOrganism, tasks, single_baseline):
    ops = org.ops()
    # Valid if the organism contains >=1 scorer anywhere (dispatch organisms carry
    # several guarded scorers; the fired guard writes selected_answer). Relaxed from
    # the v1 "exactly one scorer, must be last" rule (dispatch wiring 2026-06-24).
    if not ops or not any(role_of(n) == ROLE_SCORER for n in org.pipeline):
        return {"acc": 0.0, "comp_lift": 0.0, "dataflow_score": 0.0,
                "causal_composition_score": 0.0, "n_load_bearing": 0,
                "lb_ops": frozenset(), "valid": False}
    acc = _evaluate_acc(ops, tasks)
    comp_lift = acc - single_baseline
    df = compute_dataflow_fitness(ops, tasks)
    # Routing purity (clean-routing pressure, 2026-06-24): a genuine dispatcher uses
    # ONLY mutually-exclusive guarded scorers. A plain (unconditional) scorer mixed in
    # fires on every task and override-routes by tail-order — racking up incidental
    # hits that mimic capability. Zero out ccs for such hybrids so the archive cell is
    # won by the clean all-guarded router (or single plain specialist). Non-dispatch
    # organisms carry no guarded scorers, so purity is always 1.0 for them.
    scorer_names = [n for n in org.pipeline if role_of(n) == ROLE_SCORER]
    n_guard = sum(1 for n in scorer_names if n in GUARDED_SCORERS)
    n_plain = len(scorer_names) - n_guard
    routing_purity = 0.0 if (n_guard >= 1 and n_plain >= 1) else 1.0
    ccs = _clip_pos(comp_lift) * _clip_pos(df["load_bearing_ratio"]) * routing_purity
    # Load-bearing CORE: body (non-scorer) ops whose state-writes are causally read
    # downstream. Decorative ops are excluded — this is what makes the archive key
    # invariant to no-op padding (Goodhart guard).
    lb_slots = {s["slot"] for s in df["per_slot_signatures"]
                if s["signature"] == "load-bearing"}
    lb_ops = frozenset(org.pipeline[i] for i, op in enumerate(ops)
                       if role_of(org.pipeline[i]) != ROLE_SCORER and set(op.writes) & lb_slots)
    return {
        "acc": acc,
        "comp_lift": comp_lift,
        "dataflow_score": df["load_bearing_ratio"],
        "causal_composition_score": ccs,
        "n_load_bearing": df["n_load_bearing"],
        "lb_ops": lb_ops,
        "valid": True,
    }


# ── Abort conditions ──────────────────────────────────────────────────

def check_aborts(history, gen, terminal_only_acc, elite_acc, role_sigs):
    """Return list of (abort_code, reason) signatures. Per 2026-05-29 review."""
    aborts = []
    # B: causal-slot starvation — after 150 gens, elites should have >=1 load-bearing slot
    if gen >= 150:
        recent_lb = [h["best_n_load_bearing"] for h in history[-50:]]
        if recent_lb and (sum(recent_lb) / len(recent_lb)) < 1.0:
            aborts.append(("B_causal_slot_starvation",
                           f"median load-bearing intermediate slots < 1 over last 50 gens"))
    # C: terminal-router dominance
    if elite_acc - terminal_only_acc < 0.02:
        aborts.append(("C_terminal_router_dominance",
                       f"elite acc {elite_acc:.3f} barely beats terminal-only {terminal_only_acc:.3f}"))
    # D: role collapse — elites all-scorer (no transformers in body)
    transformer_present = any(ROLE_TRANSFORMER in sig[:-1] for sig in role_sigs)
    if not transformer_present and gen >= 50:
        aborts.append(("D_role_collapse", "no transformer roles in elite bodies"))
    return aborts


# ── MAP-Elites descriptor ─────────────────────────────────────────────

def descriptor(org: BlackboardOrganism, f: dict):
    """Behavioral descriptor = (frozenset of scorer names, frozenset of LOAD-BEARING
    body ops).

    Keyed on the SCORER SET (not just the terminal) so a dispatcher carrying several
    guarded scorers occupies a distinct cell from each single-scorer specialist —
    the routing organism is a genuinely different behavioral shape. Keyed on the
    load-bearing CORE (not the full op-set) so decorative-op padding collapses into
    the same cell instead of inflating the archive with fake 'shapes'.

    This operationalizes the project's central guard: a composition is only a
    distinct shape if its intermediate state is causally load-bearing."""
    scorers = frozenset(n for n in org.pipeline if role_of(n) == ROLE_SCORER)
    return (scorers, f["lb_ops"])


def n_distinct_real_shapes(archive, threshold=0.05):
    """Count archive cells whose occupant beats single-primitive by >threshold
    AND has >=1 load-bearing slot. The graduation-relevant count."""
    n = 0
    for f in archive.values():
        if f["fitness"]["comp_lift"] > threshold and f["fitness"]["n_load_bearing"] >= 1:
            n += 1
    return n


def dump_archive(archive, run_dir, gen):
    """Write the whole archive to a checkpoint. The portfolio is the artifact,
    not a single best organism. Called periodically so a multi-day run is
    crash-safe."""
    ckpt = Path(run_dir) / "checkpoints" / f"branch_c_gen_{gen:06d}.json"
    ckpt.parent.mkdir(parents=True, exist_ok=True)  # crash-safe: dir may not exist on first dump
    archive_dump = []
    for d, e in archive.items():
        archive_dump.append({
            "scorers": sorted(d[0]),
            "load_bearing_core": sorted(d[1]),
            "pipeline": e["org"].pipeline,
            "lineage": e["org"].lineage,
            "acc": round(e["fitness"]["acc"], 3),
            "comp_lift": round(e["fitness"]["comp_lift"], 3),
            "causal_composition_score": round(e["fitness"]["causal_composition_score"], 3),
            "n_load_bearing": e["fitness"]["n_load_bearing"],
        })
    archive_dump.sort(key=lambda x: x["causal_composition_score"], reverse=True)
    with open(ckpt, "w", encoding="utf-8") as f:
        json.dump({"gen": gen, "n_cells": len(archive),
                   "distinct_real_shapes": n_distinct_real_shapes(archive),
                   "archive": archive_dump}, f, indent=2)
    return archive_dump


# ── Main loop ─────────────────────────────────────────────────────────

def evolve(gens=200, pop_size=20, mode="deterministic", seed=20260529,
           run_dir=None, log_every=10, checkpoint_every=50,
           crossover_frac=0.0, seed_variant="default", dispatch=False):
    random.seed(seed)
    # Clean-routing pressure: in dispatch mode, mutation draws scorers from the
    # guarded pool only, so plain+guarded override-hybrids can't form (2026-06-24).
    global _MUT_SCORER_POOL
    _MUT_SCORER_POOL = GUARDED_SCORERS if dispatch else SCORERS
    canary_path = Path(__file__).parent.parent / "data" / "clean_canary_v01.json"
    with open(canary_path, "r", encoding="utf-8") as f:
        canary = json.load(f)["tasks"]
    # Synthetic dependency tasks too (the gauntlet's construct-valid set)
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from composition_gauntlet import build_synthetic_canary
    from inference_canary import build_inference_canary
    from cross_tier_canary import build_cross_tier_canary
    synth = build_synthetic_canary(n_each=15)
    # Constraint-tracking tasks the R0-R1 set provably can't solve — present
    # so forward_chain (R2) can earn load-bearing status (falsification 2026-06-09).
    inference = build_inference_canary(n=20)
    # Derive-then-order tasks solvable ONLY by a multi-tier organism (R2 inference
    # -> bridge -> R1 ordering) — the cross-tier gradient Run 1 lacked (2026-06-10).
    cross_tier = build_cross_tier_canary(n=20)
    tasks = canary + synth + inference + cross_tier
    single_baseline = _single_primitive_baseline(tasks)
    # Subset index bounds for the portfolio-coverage metric (dispatch wiring
    # 2026-06-24): best_acc tracks ONE organism and is ceiling-bound on a
    # heterogeneous battery; portfolio coverage = fraction solved by ANY archive
    # occupant, the real capability the 0.558 diagnosis surfaced.
    _subset_bounds = []
    _off = 0
    for _name, _sub in (("canary", canary), ("synth", synth),
                        ("inference", inference), ("cross_tier", cross_tier)):
        _subset_bounds.append((_name, _off, _off + len(_sub)))
        _off += len(_sub)

    if run_dir is None:
        run_dir = Path(__file__).parent.parent / "run_branch_c"
    run_dir = Path(run_dir)
    (run_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "evolve_log.jsonl"

    pop = seed_population(pop_size, variant=seed_variant, dispatch=dispatch)
    # Pipelines present at seed time — used to flag organisms that are NOVEL
    # (not a seed) so we can detect de-novo multi-tier discovery, not seed survival.
    seed_pipes = {tuple(o.pipeline) for o in pop}
    history = []
    t0 = time.time()

    print(f"Branch C Phase 1 — {gens} gens, pop {pop_size}, mode={mode}")
    print(f"Eval set: {len(tasks)} tasks ({len(canary)} canary + {len(synth)} synthetic-dependency "
          f"+ {len(inference)} inference + {len(cross_tier)} cross-tier)")
    print(f"Single-primitive baseline: {single_baseline:.3f}")
    print(f"crossover_frac={crossover_frac}  seed_variant={seed_variant}")
    print()

    _cross_tier_acc_cache = {}
    _solve_cache = {}  # pipeline tuple -> frozenset(task indices solved); memoized

    def _solved_set(org):
        key = tuple(org.pipeline)
        s = _solve_cache.get(key)
        if s is None:
            ops = org.ops()
            solved = set()
            for i, t in enumerate(tasks):
                st = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
                try:
                    if run_pipeline(ops, st).selected_answer == t["correct"]:
                        solved.add(i)
                except Exception:
                    pass
            s = frozenset(solved)
            _solve_cache[key] = s
        return s

    # Routable task indices = every subset EXCEPT canary. canary's compare/bool tasks
    # are genuinely unsolvable in the current substrate (no boolean primitive) yet
    # reward unconditional guessing — so full-battery acc is a misleading headline that
    # penalizes the honest, abstaining clean router. routable_acc is the genuine-
    # capability metric the LLM run should be judged on (2026-06-24).
    _routable_idx = frozenset(i for name, a, b in _subset_bounds if name != "canary"
                              for i in range(a, b))

    def _portfolio(occupants):
        """Oracle/portfolio coverage: fraction of tasks solved by ANY occupant, plus
        per-subset. The real capability metric (0.558 diagnosis) — best_acc tracks one
        organism and is ceiling-bound on a heterogeneous battery; with dispatch the two
        should converge."""
        covered = set()
        for e in occupants:
            covered |= _solved_set(e["org"])
        cov = len(covered) / max(len(tasks), 1)
        per = {name: round(len(covered & set(range(a, b))) / max(b - a, 1), 3)
               for name, a, b in _subset_bounds}
        return round(cov, 3), per

    def _max_routable_acc(occupants):
        """Best SINGLE organism's accuracy on the routable (non-canary) battery —
        the honest capability headline, immune to canary guessing."""
        best = 0.0
        for e in occupants:
            solved = _solved_set(e["org"]) & _routable_idx
            best = max(best, len(solved) / max(len(_routable_idx), 1))
        return round(best, 3)

    def _sub_acc(pl_names):
        ops_ = [REGISTRY[n][0] for n in pl_names if n in REGISTRY]
        out = {}
        for name, a, b in _subset_bounds:
            nc = 0
            for t in tasks[a:b]:
                st = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
                try:
                    if run_pipeline(ops_, st).selected_answer == t["correct"]:
                        nc += 1
                except Exception:
                    pass
            out[name] = nc / max(b - a, 1)
        return out

    def _dispatch_audit(org):
        """In-loop Goodhart guard for routers: per-branch ablation must show each
        guarded scorer is load-bearing for EXACTLY one subset (genuine routing, not
        tail-ordering). Returns None for non-dispatchers (<2 guarded scorers)."""
        guards = [n for n in org.pipeline if n in GUARDED_SCORERS]
        if len(guards) < 2:
            return None
        base = _sub_acc(org.pipeline)
        branches = {}
        genuine = True
        for g in guards:
            ablated = [n for n in org.pipeline if n != g]
            ab = _sub_acc(ablated)
            drops = {k: round(base[k] - ab[k], 3) for k in base}
            collapsed = [k for k, d in drops.items() if d > 0.3]
            branches[g] = {"load_bearing_for": collapsed, "drops": drops}
            if len(collapsed) != 1:
                genuine = False
        return {"n_guards": len(guards), "genuine_routing": genuine, "branches": branches}

    def _novel_multitier_solvers(occupants):
        """Archive occupants that are NOVEL (not a seed) multi-tier solvers:
        contain both an R2 inference op and an R1 ordering op AND actually solve
        the cross-tier subset (>=0.9). This is the de-novo-discovery signal —
        the thing Run 1+2 never produced beyond the seed.

        Cross-tier acc is memoized by pipeline shape so a large archive scanned
        every gen stays cheap (each distinct shape is evaluated once)."""
        found = []
        for e in occupants:
            pl = e["org"].pipeline
            key = tuple(pl)
            if ("forward_chain" in pl and "op_build_ordering" in pl
                    and key not in seed_pipes):
                cta = _cross_tier_acc_cache.get(key)
                if cta is None:
                    cta = _evaluate_acc(e["org"].ops(), cross_tier)
                    _cross_tier_acc_cache[key] = cta
                if cta >= 0.9:
                    found.append((list(pl), round(cta, 3), e["org"].lineage))
        return found

    terminal_only_acc = _evaluate_acc([REGISTRY["score_by_max_value"][0]], tasks)

    # MAP-Elites archive: descriptor -> {"org": BlackboardOrganism, "fitness": dict}
    archive = {}

    def _try_insert(org):
        f = fitness(org, tasks, single_baseline)
        if not f["valid"]:
            return f, False
        d = descriptor(org, f)
        cur = archive.get(d)
        # tiebreak: higher ccs, then acc, then SHORTER pipeline (parsimony —
        # prefer the minimal pipeline achieving this load-bearing core)
        new_key = (f["causal_composition_score"], f["acc"], -len(org.pipeline))
        better = cur is None or new_key > (
            cur["fitness"]["causal_composition_score"], cur["fitness"]["acc"],
            -len(cur["org"].pipeline))
        if better:
            archive[d] = {"org": org, "fitness": f}
        return f, better

    # Seed the archive
    for org in pop:
        _try_insert(org)

    for gen in range(1, gens + 1):
        # Reproduce: mutate (or recombine) random archive occupants (uniform cell selection)
        n_offspring = pop_size
        invalid = 0
        llm_used = 0
        xover_used = 0
        occ_snapshot = list(archive.values())
        for _ in range(n_offspring):
            if not archive:
                break
            if (crossover_frac > 0.0 and len(occ_snapshot) >= 2
                    and random.random() < crossover_frac):
                pa, pb = random.sample(occ_snapshot, 2)
                # dispatch mode uses the body+guard UNION merge (co-locates each
                # branch's parser+scorer); else the single-suffix recombine.
                child = (dispatch_merge(pa["org"], pb["org"]) if dispatch
                         else recombine(pa["org"], pb["org"]))
                xover_used += 1
            elif mode == "llm":
                child, used = mutate_llm(random.choice(occ_snapshot)["org"])
                llm_used += int(used)
            else:
                child = mutate_deterministic(random.choice(occ_snapshot)["org"])
            f, _ = _try_insert(child)
            if not f["valid"]:
                invalid += 1

        # Read archive state
        occupants = list(archive.values())
        best = max(occupants, key=lambda e: (e["fitness"]["causal_composition_score"],
                                             e["fitness"]["acc"]))
        best_org, best_f = best["org"], best["fitness"]
        n_real = n_distinct_real_shapes(archive)
        # families present across all real-shape cells
        families = set()
        for e in occupants:
            if e["fitness"]["comp_lift"] > 0.05:
                families.update(e["org"].pipeline[:-1])
        viability = 1.0 - (invalid / max(n_offspring, 1))  # abort A signal

        role_sigs = [e["org"].role_signature() for e in occupants]
        novel_solvers = _novel_multitier_solvers(occupants)
        portfolio_cov, portfolio_per_subset = _portfolio(occupants)
        # max_acc = best SINGLE organism by accuracy (the honest ceiling-break number;
        # `best`/best_acc is ccs-selected and can trail the highest-acc organism).
        max_acc = max(e["fitness"]["acc"] for e in occupants)
        max_routable_acc = _max_routable_acc(occupants)
        n_dispatchers = sum(1 for e in occupants
                            if sum(1 for n in e["org"].pipeline if n in GUARDED_SCORERS) >= 2)
        rec = {
            "gen": gen,
            "archive_cells": len(archive),
            "distinct_real_shapes": n_real,
            "primitive_families": len(families),
            "mutation_viability": round(viability, 3),
            "llm_used": llm_used,
            "xover_used": xover_used,
            "novel_multitier": len(novel_solvers),
            "best_acc": round(best_f["acc"], 3),
            "best_comp_lift": round(best_f["comp_lift"], 3),
            "best_causal_composition_score": round(best_f["causal_composition_score"], 3),
            "best_n_load_bearing": best_f["n_load_bearing"],
            "best_pipeline": best_org.pipeline,
            "max_acc": round(max_acc, 3),
            "max_routable_acc": max_routable_acc,
            # dispatch wiring (2026-06-24): portfolio coverage is the real capability;
            # best_acc is ceiling-bound on a heterogeneous battery until one organism routes.
            "portfolio_coverage": portfolio_cov,
            "portfolio_per_subset": portfolio_per_subset,
            "n_dispatchers": n_dispatchers,
            "elapsed_s": round(time.time() - t0, 1),
        }
        # Periodic in-loop dispatch audit on the best organism (bounded cost).
        if (gen == 1 or gen % max(log_every, 1) == 0):
            da = _dispatch_audit(best_org)
            if da is not None:
                rec["dispatch_audit"] = da
        history.append(rec)
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(json.dumps(rec) + "\n")

        # First de-novo multi-tier solver is the headline event — announce + record it.
        if novel_solvers and (gen == 1 or history[-2].get("novel_multitier", 0) == 0):
            pl, cta, lin = novel_solvers[0]
            print(f"  [gen {gen}] *** NOVEL multi-tier solver discovered (cross_tier_acc={cta}): "
                  f"{' -> '.join(pl)}  lineage={lin}")
            with open(run_dir / "novel_discovery.jsonl", "a", encoding="utf-8") as nf:
                nf.write(json.dumps({"gen": gen, "pipeline": pl, "cross_tier_acc": cta,
                                     "lineage": lin}) + "\n")

        aborts = check_aborts(history, gen, terminal_only_acc, best_f["acc"], role_sigs)
        if viability < 0.50 and gen >= 100:
            aborts.append(("A_mutation_viability", f"valid-rate {viability:.2f} < 0.50"))
        if aborts and gen >= 150:
            print(f"  [gen {gen}] ABORT signatures: {[a[0] for a in aborts]}")

        if gen % log_every == 0 or gen == 1:
            print(f"  gen {gen:4d} | cells={len(archive):2d} real_shapes={n_real} "
                  f"fams={len(families):2d} novel_mt={len(novel_solvers)} | best_acc={best_f['acc']:.3f} "
                  f"comp_lift={best_f['comp_lift']:+.3f} ccs={best_f['causal_composition_score']:.3f} "
                  f"lb={best_f['n_load_bearing']} xover={xover_used} viab={viability:.2f} | {time.time()-t0:.0f}s")

        # Periodic crash-safe checkpoint of the whole archive
        if gen % checkpoint_every == 0:
            dump_archive(archive, run_dir, gen)

    # Final checkpoint — the whole archive (the portfolio is the artifact)
    archive_dump = dump_archive(archive, run_dir, gens)

    print()
    print(f"Archive: {len(archive)} cells, {n_distinct_real_shapes(archive)} distinct real shapes")
    print("Top elites (the discovered portfolio):")
    for e in archive_dump[:6]:
        if e["comp_lift"] > 0.05:
            print(f"  ccs={e['causal_composition_score']:.3f} acc={e['acc']:.3f} "
                  f"lift={e['comp_lift']:+.3f} lb={e['n_load_bearing']} | {' -> '.join(e['pipeline'])}")
    return history


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=200)
    ap.add_argument("--pop", type=int, default=20)
    ap.add_argument("--mode", default="deterministic", choices=["deterministic", "llm"])
    ap.add_argument("--checkpoint-every", type=int, default=50)
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--crossover-frac", type=float, default=0.0,
                    help="fraction of offspring produced by recombination (0 disables)")
    ap.add_argument("--seed-variant", default="default", choices=["default", "ingredients"],
                    help="'ingredients' seeds the two splice-parents but NOT the cross-tier solver")
    ap.add_argument("--dispatch", action="store_true",
                    help="enable DISPATCH: guarded scorers + multi-scorer routers "
                         "(validated 2026-06-24); seeds use guarded scorers")
    args = ap.parse_args()
    evolve(gens=args.gens, pop_size=args.pop, mode=args.mode,
           checkpoint_every=args.checkpoint_every, run_dir=args.run_dir,
           crossover_frac=args.crossover_frac, seed_variant=args.seed_variant,
           dispatch=args.dispatch)


if __name__ == "__main__":
    main()
