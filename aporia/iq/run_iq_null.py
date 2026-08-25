"""run_iq_null.py — IQ-NULL. Assay validity, and the gate on every DeltaE so far.

Preregistration: aporia/iq/PREREG_IQ_NULL_2026-08-25.md, committed de27e115 before any
measurement here was taken. null_noop was frozen one commit earlier still (28761a6f).

    python aporia/iq/run_iq_null.py
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "apollo" / "src", ROOT / "apollo" / "scripts",
          ROOT / "agents" / "hephaestus" / "src", Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import blackboard_evolve as be                                     # noqa: E402
from blackboard import BlackboardState, blackboard_op, run_pipeline  # noqa: E402
import forge_primitives as fp                                       # noqa: E402
import port_ops                                                     # noqa: E402
from run_iq_port_1 import (TASKS, BOUNDS, acc, subset_acc, cat_acc, make_pool,  # noqa: E402
                           evaluator_hash, PREREG_HASH, CEILING_BODY, CEILING_TAIL)

OUT = Path(__file__).resolve().parent
GIVEN = frozenset({"problem_text", "candidates"})


# ── the second null: a port into an ALREADY-SOLVED category ──────────────────

@blackboard_op(
    reads=["relations"],
    writes=["transitive_closure"],
    precondition=lambda s: bool(s.relations),
)
def op_check_transitivity(state: BlackboardState) -> BlackboardState:
    """PORT of fp.check_transitivity. Warshall closure of `relations` into the declared
    slot `transitive_closure` (type dict_str_set_str -- an exact type match). Targets
    `transitivity`, which the ceiling organism already solves 10/10."""
    state.transitive_closure = fp.check_transitivity(list(state.relations))
    return state


def reachable_ops(pool):
    """Fixpoint over DECLARED writes: which operators can ever appear in a valid ordering?
    An op is enumerable iff every slot it reads is written by some op reachable before it.
    This is the enumerator's own rule (o1_enumerate.valid_orders), lifted to a closure."""
    avail = set(GIVEN)
    reached = set()
    changed = True
    while changed:
        changed = False
        for name, op in pool.items():
            if name in reached:
                continue
            if set(op.reads) <= avail:
                reached.add(name)
                avail |= set(op.writes)
                changed = True
    return reached, avail


def valid_orders(subset, pool, cap):
    out = []

    def rec(avail, remaining, accum):
        if len(out) >= cap:
            return
        if not remaining:
            out.append(tuple(accum))
            return
        for op in sorted(remaining):
            if set(pool[op].reads) <= avail:
                rec(avail | set(pool[op].writes), remaining - {op}, accum + [op])
                if len(out) >= cap:
                    return

    rec(set(GIVEN), set(subset), [])
    return out


def footprint(ops):
    """Tasks (of 120) on which running these ops from a fresh state changes ANY slot."""
    hit = []
    for i, t in enumerate(TASKS):
        st = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        before = deepcopy(st)
        out = run_pipeline(ops, st)
        same = all(getattr(out, f) == getattr(before, f) for f in
                   ("quantities", "counts", "transitive_closure", "names", "relations",
                    "ordered", "evidence", "max_value", "selected_answer", "facts",
                    "derived_facts", "numbers", "hypotheses", "probabilities",
                    "question_target", "comparison", "extreme_number", "max_entity"))
        if not same:
            hit.append(i)
    return hit


def differential_footprint(prefix_ops, op):
    """Tasks on which inserting `op` after `prefix_ops` changes the resulting state.

    NOT the set-difference of two touched-task lists: the prefix already touches those
    tasks, so that difference is empty by construction and any predicate reading it passes
    vacuously (LOOP_APORIA P138). This runs both pipelines and diffs the states."""
    fields = ("quantities", "counts", "transitive_closure", "names", "relations", "ordered",
              "evidence", "max_value", "selected_answer", "facts", "derived_facts",
              "numbers", "hypotheses", "probabilities", "question_target", "comparison",
              "extreme_number", "max_entity")
    hit = []
    for i, t in enumerate(TASKS):
        a = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        b = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        A = run_pipeline(list(prefix_ops), a)
        B = run_pipeline(list(prefix_ops) + [op], b)
        if any(getattr(A, f) != getattr(B, f) for f in fields):
            hit.append(i)
    return hit


def main():
    R = {"experiment": "IQ-NULL", "date": "2026-08-25", "agent": "Aporia (M1)",
         "prereg": "aporia/iq/PREREG_IQ_NULL_2026-08-25.md",
         "prereg_commit": "de27e115", "null_ops_frozen_at": "28761a6f (null_noop)"}

    h = evaluator_hash()
    R["evaluator_hash_matches_prereg"] = (h == PREREG_HASH)
    if h != PREREG_HASH:
        R["verdict"] = "INADMISSIBLE_EVALUATOR_DRIFT"
        json.dump(R, open(OUT / "RESULT_IQ_NULL.json", "w", encoding="utf-8"), indent=2)
        print("INADMISSIBLE"); return

    C = make_pool()
    base_acc, base_pt = acc(CEILING_BODY + CEILING_TAIL, C)
    R["E_C"] = round(base_acc, 6)
    unsolved_idx = [i for i, ok in enumerate(base_pt) if not ok]

    # ── N2/N3: reachability audit over DECLARED writes ───────────────────────
    reach_C, avail_C = reachable_ops(C)
    unreachable_C = sorted(set(C) - reach_C)
    C_null = make_pool({"null_noop": port_ops.null_noop})
    reach_N, _ = reachable_ops(C_null)
    unlocked = sorted(reach_N - reach_C - {"null_noop"})
    R["unreachable_ops_in_C"] = unreachable_C
    R["n_unreachable_in_C"] = len(unreachable_C)
    R["ops_unlocked_by_null_noop"] = unlocked
    R["N2_entity_counter_unreachable_in_C"] = "entity_counter" in unreachable_C
    R["N3_null_noop_changes_reachable_set"] = bool(unlocked)

    # ── N1: null_noop footprint ──────────────────────────────────────────────
    fp_null = footprint([port_ops.null_noop])
    R["null_noop_footprint_size"] = len(fp_null)
    R["N1_null_noop_footprint_zero"] = (len(fp_null) == 0)

    # ── N4: search the region null_noop unlocks ──────────────────────────────
    # Enumerate every valid ordering over subsets of (previously-unreachable transformers
    # + null_noop + the transformers that feed them), closed with every O1 scorer tail.
    scorers = sorted(be.SCORERS)
    guarded = sorted(be.GUARDED_SCORERS)
    tails = [(s,) for s in scorers]
    for g in range(2, len(guarded) + 1):
        tails += [tuple(c) for c in combinations(guarded, g)]

    body_pool = sorted(n for n in reach_N
                       if n == "null_noop" or be.role_of(n) != be.ROLE_SCORER)
    must = {"null_noop"} | set(unlocked)
    others = [n for n in body_pool if n not in must]
    R["null_region_body_pool"] = body_pool
    R["null_region_must_contain"] = sorted(must)

    best_null = {"acc": -1.0, "pipeline": None}
    evals = 0

    def sweep(subset, cap):
        nonlocal best_null, evals
        for b in valid_orders(subset, C_null, cap):
            for tail in tails:
                a, _ = acc(list(b) + list(tail), C_null)
                evals += 1
                if a > best_null["acc"]:
                    best_null = {"acc": round(a, 6), "pipeline": list(b) + list(tail)}

    # Region A: the CEILING BODY (which already scores 100/120) plus the null and every
    # op it unlocks. This is where a gain is most likely, so it is swept first and whole.
    sweep(sorted(set(CEILING_BODY) | must), cap=24)
    R["null_region_A_best"] = dict(best_null)

    # Region B: every subset containing the null and its unlocked ops, plus up to
    # max_extra further transformers. Exhaustive over that range -- not a prefix sample.
    max_extra = 4
    n_subsets = sum(len(list(combinations(others, k))) for k in range(0, max_extra + 1))
    R["null_region_subsets"] = n_subsets
    R["null_region_declared_scope"] = (
        f"Region A: ceiling body + {sorted(must)}, <=24 orderings x {len(tails)} tails. "
        f"Region B: all subsets containing {sorted(must)} plus up to {max_extra} of "
        f"{len(others)} other transformers = {n_subsets} subsets, <=8 orderings x "
        f"{len(tails)} tails. Every subset in that range is visited; nothing is sampled. "
        f"NOT covered: subsets with 5+ extras that are not a superset of the ceiling body.")
    for k in range(0, max_extra + 1):
        for extra in combinations(others, k):
            sweep(sorted(must | set(extra)), cap=8)

    R["null_region_evals"] = evals
    R["null_region_best"] = best_null
    delta_null = max(0.0, best_null["acc"] - base_acc)
    R["delta_E_null_noop"] = round(delta_null, 6)
    R["N4_delta_null_noop_zero"] = (delta_null == 0.0)

    # ── N5/N6: op_check_transitivity ─────────────────────────────────────────
    C_tr = make_pool({"op_check_transitivity": op_check_transitivity})
    fp_tr_only = differential_footprint([be.REGISTRY["parse_names_and_relations"][0]],
                                        op_check_transitivity)
    R["op_check_transitivity_footprint_size"] = len(fp_tr_only)
    by_cat = {}
    for i in fp_tr_only:
        k = TASKS[i]["_subset"] + ":" + str(TASKS[i].get("category"))
        by_cat[k] = by_cat.get(k, 0) + 1
    R["op_check_transitivity_footprint_by_category"] = by_cat
    # P138 guard, executed: a non-empty footprint is what makes N6 capable of failing.
    R["N6_reading_is_non_vacuous"] = len(fp_tr_only) > 0
    R["N6_footprint_excludes_unsolved"] = (len(fp_tr_only) > 0
                                           and not (set(fp_tr_only) & set(unsolved_idx)))
    # exhibited: insert it into the ceiling pipeline at every valid position
    best_tr = base_acc
    body = CEILING_BODY
    for pos in range(len(body) + 1):
        cand = body[:pos] + ["op_check_transitivity"] + body[pos:]
        a, _ = acc(cand + CEILING_TAIL, C_tr)
        best_tr = max(best_tr, a)
    # and over subsets: any ordering containing it, up to 5 further transformers
    reach_tr, _ = reachable_ops(C_tr)
    tr_others = sorted(n for n in reach_tr
                       if be.role_of(n) != be.ROLE_SCORER and n != "op_check_transitivity")
    tr_evals = 0
    for k in range(0, 4):
        for extra in combinations(tr_others, k):
            subset = sorted({"op_check_transitivity"} | set(extra))
            for b in valid_orders(subset, C_tr, cap=6):
                for tail in tails:
                    a, _ = acc(list(b) + list(tail), C_tr)
                    tr_evals += 1
                    best_tr = max(best_tr, a)
    R["check_transitivity_evals"] = tr_evals
    R["check_transitivity_best"] = round(best_tr, 6)
    delta_tr = max(0.0, best_tr - base_acc)
    R["delta_E_check_transitivity"] = round(delta_tr, 6)
    R["N5_delta_check_transitivity_zero"] = (delta_tr == 0.0)

    checks = {"N1": R["N1_null_noop_footprint_zero"],
              "N4": R["N4_delta_null_noop_zero"],
              "N5": R["N5_delta_check_transitivity_zero"],
              "N6": R["N6_footprint_excludes_unsolved"]}
    R["checks"] = checks
    R["verdict"] = "ADVANCE" if all(checks.values()) else "REDESIGN"
    R["failed_checks"] = sorted(k for k, v in checks.items() if not v)
    if R["verdict"] == "REDESIGN":
        R["consequence"] = ("E is contaminated by declared-type reachability. IQ-PORT-1's "
                            "+0.0416667 is SUSPENDED as a DeltaE-over-a-max; the exhibited "
                            "pipeline, knockouts, mutants and injections all stand.")

    json.dump(R, open(OUT / "RESULT_IQ_NULL.json", "w", encoding="utf-8"), indent=2)
    for k, v in R.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
