"""recombination_falsification.py — does a CROSSOVER operator reach a load-bearing
multi-tier solver that single-step mutation provably cannot?

Context. Branch C Run 1 (gen 481) and Run 2 (gen 2668) both plateaued: the
substrate HOSTS the cross-tier organism (falsification 2026-06-10) and the eval
REWARDS it (cross-tier canary), yet evolution never assembled a novel multi-tier
organism de novo — it only kept the *seeded* one alive. Diagnosis
(RESUME_apollo_2026-06-15.md): the mutation operator is single-step. Building the
6-op multi-tier pipeline from ancestors needs several coordinated inserts that are
each individually neutral or harmful — a fitness valley single-step hill-climbing
won't cross. This experiment tests the proposed fix (recombination) BEFORE any
long run, falsification-first.

Question: *Is splice(P1, P2) the unique multi-tier solver — solving the cross-tier
canary with every link load-bearing, while (a) neither parent solves it, and
(b) single-step mutation from either parent cannot bridge the gap within budget,
yet (c) one crossover operation does?*

  YES -> the search-operator bottleneck is the real cause and crossover attacks
         it directly; wire crossover into evolve and launch.
  NO  -> either the construction isn't valid (a parent already solves it / the
         splice isn't load-bearing) or single-step reaches it just as well
         (no valley) — in which case crossover is not the lever. Fix before run.

The two parents are deliberately PLAUSIBLE archive shapes, each a known control
from the cross-tier falsification:
  P1 = R2-inference + bridge but WRONG terminal  (derivability, not rank)
  P2 = R01_ONLY control                          (parses names, finds no relations)
Their one-point splice == the validated cross-tier organism:
  parse_rules -> parse_ordinal -> forward_chain -> relations_from_facts
              -> op_build_ordering -> select_nth

Writes a JSON artifact for re-audit.

Usage:
    python recombination_falsification.py
"""
import sys
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blackboard import BlackboardState, run_pipeline
from dataflow_fitness import compute_dataflow_fitness
from cross_tier_canary import build_cross_tier_canary
# Reuse the EXACT registry + mutation operator the evolve loop uses, so the
# "single-step can't" claim is about the real operator, not a toy.
from blackboard_evolve import (REGISTRY, TRANSFORMERS, SCORERS, role_of,
                               ROLE_SCORER, BlackboardOrganism,
                               mutate_deterministic, _single_primitive_baseline)

SEED = 20260616


# ── the construction ──────────────────────────────────────────────────

# P1: has the R2 inference AND the type bridge, but terminates in the
# derivability scorer -> answers "is it derivable", never "what rank". Plausible
# evolved shape (COMP_R2 grown with parse_ordinal + bridge), fails the canary.
P1 = ["parse_rules", "parse_ordinal", "forward_chain", "relations_from_facts",
      "score_by_derivability"]

# P2: the R0-R1 ordering shape (== the R01_ONLY control). Parses relations from
# NAMES, but the canary's comparisons are hidden behind inference, so it finds no
# explicit relations -> empty ordering -> wrong nth. A real, useful ordering organism.
P2 = ["parse_names_and_relations", "parse_ordinal", "op_build_ordering", "select_nth"]

# The validated cross-tier solver == one-point splice P1[:4] + P2[2:].
SOLVER = ["parse_rules", "parse_ordinal", "forward_chain", "relations_from_facts",
          "op_build_ordering", "select_nth"]


def ops_of(names):
    return [REGISTRY[n][0] for n in names]


# ── evaluation helpers ──────────────────────────────────────────────────

def evaluate_acc(names, tasks):
    ops = ops_of(names)
    n = 0
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            out = run_pipeline(ops, s)
            if out.selected_answer == t["correct"]:
                n += 1
        except Exception:
            pass
    return n / max(len(tasks), 1)


def chance(tasks):
    return sum(1.0 / max(len(t["candidates"]), 1) for t in tasks) / max(len(tasks), 1)


def load_bearing_slots(names, tasks):
    df = compute_dataflow_fitness(ops_of(names), tasks)
    return {s["slot"] for s in df["per_slot_signatures"]
            if s["signature"] == "load-bearing"}


# ── single-step neighborhood (the valley's first step) ─────────────────

def single_edit_neighbors(names):
    """Every pipeline one deterministic edit away — the FULL 1-step neighborhood
    of the operator the evolve loop uses (insert any transformer at any body pos,
    remove any body op, swap any body op, swap the terminal scorer). The terminal
    scorer is never displaced (mirrors mutate_* role guard)."""
    out = set()
    body_len = len(names) - 1
    # insert each transformer at each body position (0..body_len)
    if body_len < 5:
        for pos in range(0, body_len + 1):
            for tr in TRANSFORMERS:
                out.add(tuple(names[:pos] + [tr] + names[pos:]))
    # remove each body op (keep >=1 body op)
    if body_len > 1:
        for pos in range(0, body_len):
            out.add(tuple(names[:pos] + names[pos + 1:]))
    # swap each body op for another transformer
    for pos in range(0, body_len):
        for tr in TRANSFORMERS:
            if tr != names[pos]:
                out.add(tuple(names[:pos] + [tr] + names[pos + 1:]))
    # swap terminal scorer
    for sc in SCORERS:
        if sc != names[-1]:
            out.add(tuple(names[:-1] + [sc]))
    return [list(t) for t in out]


# ── budgeted random walk under the real operator ───────────────────────

def random_walk_reach(parent_names, tasks, solve_thresh, n_walks, max_depth, rng):
    """From the parent, take random single-step mutations (the EXACT
    mutate_deterministic the loop uses) up to max_depth; does any walk reach a
    pipeline that solves the canary >= solve_thresh? Reports reach-rate, best acc,
    and whether the exact SOLVER shape was ever produced."""
    reached = 0
    best_acc = 0.0
    solver_hits = 0
    solver_tup = tuple(SOLVER)
    for _ in range(n_walks):
        org = BlackboardOrganism(pipeline=list(parent_names), genome_id="w")
        for _ in range(max_depth):
            org = mutate_deterministic(org)
            if tuple(org.pipeline) == solver_tup:
                solver_hits += 1
            if role_of(org.pipeline[-1]) != ROLE_SCORER:
                continue
            acc = evaluate_acc(org.pipeline, tasks)
            if acc > best_acc:
                best_acc = acc
            if acc >= solve_thresh:
                reached += 1
                break
    return {"reach_rate": reached / max(n_walks, 1), "best_acc": round(best_acc, 3),
            "solver_shape_hits": solver_hits, "n_walks": n_walks, "max_depth": max_depth}


# ── crossover operator (general one-point splice) ──────────────────────

def crossover(pa, pb, rng):
    """One-point splice: prefix(pa body) + suffix(pb from a cut). Result always
    ends in pb's terminal scorer. pa contributes only body ops (its terminal is
    dropped), so no scorer lands mid-pipeline."""
    i = rng.randint(1, len(pa) - 1)     # take pa[:i] from the body (>=1 op, excl pa terminal)
    j = rng.randint(0, len(pb) - 1)     # take pb[j:] (>=1 op, includes pb terminal scorer)
    return pa[:i] + pb[j:]


def crossover_reach(pa, pb, tasks, solve_thresh, n_trials, rng):
    """Run the crossover operator on the parent pair (both orderings) and report
    how often it yields a solver, plus whether the exact SOLVER shape appears."""
    solved = 0
    best_acc = 0.0
    solver_tup = tuple(SOLVER)
    solver_hits = 0
    distinct_solvers = set()
    for _ in range(n_trials):
        a, b = (pa, pb) if rng.random() < 0.5 else (pb, pa)
        child = crossover(a, b, rng)
        if role_of(child[-1]) != ROLE_SCORER:
            continue
        if tuple(child) == solver_tup:
            solver_hits += 1
        acc = evaluate_acc(child, tasks)
        if acc > best_acc:
            best_acc = acc
        if acc >= solve_thresh:
            solved += 1
            distinct_solvers.add(tuple(child))
    return {"solve_rate": solved / max(n_trials, 1), "best_acc": round(best_acc, 3),
            "solver_shape_hits": solver_hits, "n_trials": n_trials,
            "distinct_solving_shapes": [list(s) for s in distinct_solvers]}


# ── main ────────────────────────────────────────────────────────────────

def main():
    rng = random.Random(SEED)
    print("=" * 78)
    print("RECOMBINATION FALSIFICATION — does crossover cross the valley single-")
    print("step mutation can't?")
    print("=" * 78)

    tasks = build_cross_tier_canary(30)
    ch = chance(tasks)
    single_base = _single_primitive_baseline(tasks)
    solve_thresh = max(0.60, ch + 0.30)   # must clearly solve, well above chance
    print(f"Cross-tier canary: {len(tasks)} derive-then-order tasks. "
          f"chance={ch:.3f} single-primitive={single_base:.3f} "
          f"solve_thresh={solve_thresh:.3f}")
    print(f"P1 = {' -> '.join(P1)}")
    print(f"P2 = {' -> '.join(P2)}")
    print(f"S  = {' -> '.join(SOLVER)}   (== P1[:4] + P2[2:])")
    print()

    # sanity: splice identity
    assert P1[:4] + P2[2:] == SOLVER, "splice identity broken"

    # ── GATE 1: splice solves, parents fail, links load-bearing ──────────
    acc_p1 = evaluate_acc(P1, tasks)
    acc_p2 = evaluate_acc(P2, tasks)
    acc_s = evaluate_acc(SOLVER, tasks)
    comp_lift_s = acc_s - single_base
    lb = load_bearing_slots(SOLVER, tasks)
    derived_lb = "derived_facts" in lb
    relations_lb = "relations" in lb
    print("--- GATE 1: construct validity ---")
    print(f"  acc(P1)     = {acc_p1:.3f}   (parent 1 alone)")
    print(f"  acc(P2)     = {acc_p2:.3f}   (parent 2 alone)")
    print(f"  acc(SPLICE) = {acc_s:.3f}   comp_lift={comp_lift_s:+.3f}")
    print(f"  splice load-bearing slots = {sorted(lb)}")
    print(f"    derived_facts LB={derived_lb}  relations LB={relations_lb}")
    parents_fail = acc_p1 <= ch + 0.05 and acc_p2 <= ch + 0.05
    splice_solves = acc_s >= solve_thresh and comp_lift_s >= 0.10 and derived_lb and relations_lb
    gate1 = parents_fail and splice_solves
    print(f"  parents fail (<=chance+0.05): {parents_fail} | "
          f"splice solves + load-bearing: {splice_solves} -> GATE1={gate1}")
    print()

    # ── GATE 2: the valley — single-step can't bridge ────────────────────
    print("--- GATE 2: the fitness valley (single-step mutation) ---")
    nbrs_p1 = single_edit_neighbors(P1)
    nbrs_p2 = single_edit_neighbors(P2)
    best_nbr_p1 = max((evaluate_acc(n, tasks) for n in nbrs_p1), default=0.0)
    best_nbr_p2 = max((evaluate_acc(n, tasks) for n in nbrs_p2), default=0.0)
    solver_in_p1_nbrs = SOLVER in nbrs_p1
    solver_in_p2_nbrs = SOLVER in nbrs_p2
    print(f"  P1: {len(nbrs_p1)} single-edit neighbors | best neighbor acc = "
          f"{best_nbr_p1:.3f} | solver in 1-edit nbrhood = {solver_in_p1_nbrs}")
    print(f"  P2: {len(nbrs_p2)} single-edit neighbors | best neighbor acc = "
          f"{best_nbr_p2:.3f} | solver in 1-edit nbrhood = {solver_in_p2_nbrs}")
    # first step is non-improving toward a solution from either parent:
    first_step_flat = best_nbr_p1 < solve_thresh and best_nbr_p2 < solve_thresh
    not_one_edit = not solver_in_p1_nbrs and not solver_in_p2_nbrs
    print(f"  no single edit solves (first step has no gradient): {first_step_flat}")
    print(f"  solver is >1 edit from BOTH parents: {not_one_edit}")

    walk_p1 = random_walk_reach(P1, tasks, solve_thresh, n_walks=4000, max_depth=4, rng=rng)
    walk_p2 = random_walk_reach(P2, tasks, solve_thresh, n_walks=4000, max_depth=4, rng=rng)
    print(f"  random-walk P1 (4000 walks x depth4): reach_rate={walk_p1['reach_rate']:.4f} "
          f"best_acc={walk_p1['best_acc']:.3f} solver_shape_hits={walk_p1['solver_shape_hits']}")
    print(f"  random-walk P2 (4000 walks x depth4): reach_rate={walk_p2['reach_rate']:.4f} "
          f"best_acc={walk_p2['best_acc']:.3f} solver_shape_hits={walk_p2['solver_shape_hits']}")
    valley = first_step_flat and not_one_edit
    print(f"  -> GATE2 (valley present): {valley}")
    print()

    # ── GATE 3: crossover reaches the solver in one operation ────────────
    print("--- GATE 3: crossover crosses it ---")
    xo = crossover_reach(P1, P2, tasks, solve_thresh, n_trials=2000, rng=rng)
    print(f"  crossover (2000 trials): solve_rate={xo['solve_rate']:.4f} "
          f"best_acc={xo['best_acc']:.3f} solver_shape_hits={xo['solver_shape_hits']}")
    for s in xo["distinct_solving_shapes"]:
        print(f"      solver shape: {' -> '.join(s)}")
    gate3 = xo["solve_rate"] > 0.0 and xo["best_acc"] >= solve_thresh
    print(f"  -> GATE3 (crossover finds a solver): {gate3}")
    print()

    # ── verdict ──────────────────────────────────────────────────────────
    # crossover must reach the solver at a rate single-step never does
    crossover_dominates = xo["solve_rate"] > max(walk_p1["reach_rate"], walk_p2["reach_rate"])
    verdict = gate1 and valley and gate3 and crossover_dominates
    print("=" * 78)
    print(f"  GATE1 construct-valid        : {gate1}")
    print(f"  GATE2 valley (single-step X) : {valley}")
    print(f"  GATE3 crossover crosses it   : {gate3}")
    print(f"  crossover_rate > single-step : {crossover_dominates} "
          f"({xo['solve_rate']:.4f} vs {max(walk_p1['reach_rate'], walk_p2['reach_rate']):.4f})")
    print()
    if verdict:
        print("  RESULT = YES. The crossover operator reaches a load-bearing multi-tier")
        print("  solver that single-step mutation cannot bridge (fitness valley >=1 edit")
        print("  wide, first step non-improving). The search-operator bottleneck is the")
        print("  real cause; wiring crossover into evolve is justified. Launch the run.")
    else:
        print("  RESULT = NO. Inspect the failing gate before any run:")
        print(f"    construct-valid={gate1} valley={valley} crossover={gate3} "
              f"dominates={crossover_dominates}")

    out = {
        "experiment": "recombination_falsification",
        "date": "2026-06-16",
        "seed": SEED,
        "n_tasks": len(tasks),
        "chance": ch,
        "single_primitive_baseline": single_base,
        "solve_thresh": solve_thresh,
        "parents": {"P1": P1, "P2": P2},
        "solver": SOLVER,
        "gate1_construct_validity": {
            "acc_p1": acc_p1, "acc_p2": acc_p2, "acc_splice": acc_s,
            "comp_lift_splice": comp_lift_s,
            "splice_load_bearing_slots": sorted(lb),
            "derived_facts_load_bearing": derived_lb,
            "relations_load_bearing": relations_lb,
            "parents_fail": parents_fail, "splice_solves": splice_solves,
            "passed": gate1,
        },
        "gate2_valley": {
            "n_neighbors_p1": len(nbrs_p1), "n_neighbors_p2": len(nbrs_p2),
            "best_neighbor_acc_p1": best_nbr_p1, "best_neighbor_acc_p2": best_nbr_p2,
            "solver_in_p1_one_edit": solver_in_p1_nbrs,
            "solver_in_p2_one_edit": solver_in_p2_nbrs,
            "first_step_flat": first_step_flat, "solver_gt_one_edit": not_one_edit,
            "random_walk_p1": walk_p1, "random_walk_p2": walk_p2,
            "passed": valley,
        },
        "gate3_crossover": {**xo, "passed": gate3},
        "crossover_dominates_single_step": crossover_dominates,
        "verdict_recombination_justified": verdict,
    }
    art = ROOT / "pivot" / "recombination_falsification_result_2026-06-16.json"
    with open(art, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print()
    print(f"  artifact -> {art}")
    return verdict


if __name__ == "__main__":
    main()
