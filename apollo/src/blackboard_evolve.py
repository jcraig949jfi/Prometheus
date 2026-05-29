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

from blackboard import BlackboardState, run_pipeline, audit_pipeline
from dataflow_fitness import compute_dataflow_fitness
import blackboard_ops as v1
import blackboard_ops_v2 as v2


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
    # scorers (terminal-only)
    "select_nth": (v2.select_nth, ROLE_SCORER),
    "score_by_aggregate": (v2.score_by_aggregate, ROLE_SCORER),
    "score_by_max_entity": (v1.score_by_max_entity, ROLE_SCORER),
    "score_by_max_value": (v1.score_by_max_value, ROLE_SCORER),
    # quarantined v1 answer-producers
    "op_numeric_argmax": (v1.op_numeric_argmax, ROLE_QUARANTINE),
}

TRANSFORMERS = [n for n, (_, r) in REGISTRY.items() if r == ROLE_TRANSFORMER]
SCORERS = [n for n, (_, r) in REGISTRY.items() if r == ROLE_SCORER]


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

def seed_population(size=20):
    pop = []
    # 2 hand-written passing compositions
    a = BlackboardOrganism(["parse_names_and_relations", "parse_ordinal",
                            "op_build_ordering", "select_nth"], genome_id=_new_id())
    a.lineage = ["seed:COMP_A"]
    c = BlackboardOrganism(["parse_box_items", "op_aggregate_quantities",
                            "score_by_aggregate"], genome_id=_new_id())
    c.lineage = ["seed:COMP_C"]
    pop.extend([a, c])
    # random typed pipelines: 1-3 transformers + a scorer
    while len(pop) < size:
        k = random.randint(1, 3)
        body = [random.choice(TRANSFORMERS) for _ in range(k)]
        scorer = random.choice(SCORERS)
        org = BlackboardOrganism(body + [scorer], genome_id=_new_id())
        org.lineage = ["seed:random"]
        pop.append(org)
    return pop


# ── Mutation (deterministic; LLM mode hooks the same validators) ──────

def mutate_deterministic(org: BlackboardOrganism) -> BlackboardOrganism:
    child = org.clone()
    p = child.pipeline
    move = random.choice(["insert", "remove", "swap"])
    body_len = len(p) - 1  # exclude terminal scorer
    if move == "insert" and body_len < 5:
        pos = random.randint(0, body_len)
        p.insert(pos, random.choice(TRANSFORMERS))
        child.lineage.append(f"insert_step@{pos}")
    elif move == "remove" and body_len > 1:
        pos = random.randint(0, body_len - 1)
        removed = p.pop(pos)
        child.lineage.append(f"remove_step:{removed}")
    elif move == "swap":
        if random.random() < 0.85 and body_len > 0:  # swap a transformer
            pos = random.randint(0, body_len - 1)
            p[pos] = random.choice(TRANSFORMERS)
            child.lineage.append(f"swap_step@{pos}")
        else:  # swap the terminal scorer
            p[-1] = random.choice(SCORERS)
            child.lineage.append("swap_scorer")
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
    if not ops or role_of(org.pipeline[-1]) != ROLE_SCORER:
        return {"acc": 0.0, "comp_lift": 0.0, "dataflow_score": 0.0,
                "causal_composition_score": 0.0, "n_load_bearing": 0,
                "lb_ops": frozenset(), "valid": False}
    acc = _evaluate_acc(ops, tasks)
    comp_lift = acc - single_baseline
    df = compute_dataflow_fitness(ops, tasks)
    ccs = _clip_pos(comp_lift) * _clip_pos(df["load_bearing_ratio"])
    # Load-bearing CORE: body ops whose state-writes are causally read downstream.
    # Decorative ops are excluded — this is what makes the archive key invariant
    # to no-op padding (Goodhart guard).
    lb_slots = {s["slot"] for s in df["per_slot_signatures"]
                if s["signature"] == "load-bearing"}
    lb_ops = frozenset(org.pipeline[i] for i, op in enumerate(ops[:-1])
                       if set(op.writes) & lb_slots)
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
    """Behavioral descriptor = (terminal scorer, frozenset of LOAD-BEARING body ops).

    Keyed on the load-bearing CORE, not the full op-set — so decorative-op
    padding collapses into the same cell instead of inflating the archive
    with thousands of fake 'shapes'. We keep the best (and, on ties, the
    shortest) organism per core, so COMP_A and COMP_C coexist as distinct
    real shapes while no-op variants do not multiply.

    This operationalizes the project's central guard: a composition is only
    a distinct shape if its intermediate state is causally load-bearing."""
    return (org.pipeline[-1], f["lb_ops"])


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
    archive_dump = []
    for d, e in archive.items():
        archive_dump.append({
            "terminal_scorer": d[0],
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
           run_dir=None, log_every=10, checkpoint_every=50):
    random.seed(seed)
    canary_path = Path(__file__).parent.parent / "data" / "clean_canary_v01.json"
    with open(canary_path, "r", encoding="utf-8") as f:
        canary = json.load(f)["tasks"]
    # Synthetic dependency tasks too (the gauntlet's construct-valid set)
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from composition_gauntlet import build_synthetic_canary
    synth = build_synthetic_canary(n_each=15)
    tasks = canary + synth
    single_baseline = _single_primitive_baseline(tasks)

    if run_dir is None:
        run_dir = Path(__file__).parent.parent / "run_branch_c"
    run_dir = Path(run_dir)
    (run_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "evolve_log.jsonl"

    pop = seed_population(pop_size)
    history = []
    t0 = time.time()

    print(f"Branch C Phase 1 — {gens} gens, pop {pop_size}, mode={mode}")
    print(f"Eval set: {len(tasks)} tasks ({len(canary)} canary + {len(synth)} synthetic-dependency)")
    print(f"Single-primitive baseline: {single_baseline:.3f}")
    print()

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
        # Reproduce: mutate random archive occupants (uniform cell selection)
        n_offspring = pop_size
        invalid = 0
        llm_used = 0
        for _ in range(n_offspring):
            if not archive:
                break
            parent = random.choice(list(archive.values()))["org"]
            if mode == "llm":
                child, used = mutate_llm(parent)
                llm_used += int(used)
            else:
                child = mutate_deterministic(parent)
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
        rec = {
            "gen": gen,
            "archive_cells": len(archive),
            "distinct_real_shapes": n_real,
            "primitive_families": len(families),
            "mutation_viability": round(viability, 3),
            "llm_used": llm_used,
            "best_acc": round(best_f["acc"], 3),
            "best_comp_lift": round(best_f["comp_lift"], 3),
            "best_causal_composition_score": round(best_f["causal_composition_score"], 3),
            "best_n_load_bearing": best_f["n_load_bearing"],
            "best_pipeline": best_org.pipeline,
            "elapsed_s": round(time.time() - t0, 1),
        }
        history.append(rec)
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(json.dumps(rec) + "\n")

        aborts = check_aborts(history, gen, terminal_only_acc, best_f["acc"], role_sigs)
        if viability < 0.50 and gen >= 100:
            aborts.append(("A_mutation_viability", f"valid-rate {viability:.2f} < 0.50"))
        if aborts and gen >= 150:
            print(f"  [gen {gen}] ABORT signatures: {[a[0] for a in aborts]}")

        if gen % log_every == 0 or gen == 1:
            print(f"  gen {gen:4d} | cells={len(archive):2d} real_shapes={n_real} "
                  f"fams={len(families):2d} | best_acc={best_f['acc']:.3f} "
                  f"comp_lift={best_f['comp_lift']:+.3f} ccs={best_f['causal_composition_score']:.3f} "
                  f"lb={best_f['n_load_bearing']} viab={viability:.2f} | {time.time()-t0:.0f}s")

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
    args = ap.parse_args()
    evolve(gens=args.gens, pop_size=args.pop, mode=args.mode,
           checkpoint_every=args.checkpoint_every, run_dir=args.run_dir)


if __name__ == "__main__":
    main()
