"""o1_enumerate.py — O1: type-directed enumeration vs evolution.

The decisive experiment. Apollo's operators declare typed reads/writes; nobody has ever
enumerated the type-correct pipelines. If brute force finds what four months of evolution
found, and finds it cheaper, the evolutionary framing was decorative.

Prereg + ratified stop rule: apollo/cycles/o1_enumeration/PREREGISTRATION.md
Comparator: evolution reached max_acc 0.833 in 24 x 131 = 3,144 organism-evaluations.

METHOD. Enumerate operator SUBSETS by increasing size (simplest-first, the fair order),
and for each subset every valid topological ordering up to a cap. An ordering is valid iff
each operator's declared reads are already written when it runs (problem_text/candidates
given). Each ordering is closed with every scorer tail: each single scorer, and each set of
2-3 guarded scorers (a dispatch shape). Guards are NOT applicability-filtered — a guard
whose slot is unwritten simply never fires, which is exactly how the substrate behaves.

Every candidate is scored by the SUBSTRATE'S OWN _evaluate_acc on the real 120-task
battery. Nothing is simulated.

NOTE ON A PRIOR VERSION (2026-08-23, caught before it produced evidence): an earlier
enumerator required each operator to write a slot not already written. That rule makes the
known 0.833 organism UNREACHABLE — `relations_from_facts` deliberately overwrites
`relations` after `parse_names_and_relations` has written it. The prune was stricter than
the substrate's real semantics and would have handed evolution an unearned win. It is gone;
the positive control now exists to catch exactly that class of error.

Usage:
    python o1_enumerate.py --max-k 10 --orders 4
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
OUT = HERE.parent / "cycles" / "o1_enumeration"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be  # noqa: E402
from blackboard import BlackboardState  # noqa: E402

GIVEN = frozenset({"problem_text", "candidates"})
EVOLUTION_EVALS_TO_CEILING = 24 * 131
EVOLUTION_CEILING = 0.833

# The known production organism — the mandatory positive control.
KNOWN_0833 = ["parse_comparison", "parse_which_extreme", "parse_box_items",
              "op_aggregate_quantities", "parse_rules", "parse_ordinal", "forward_chain",
              "parse_names_and_relations", "relations_from_facts", "op_build_ordering",
              "score_by_extreme_number__g", "score_by_aggregate__g",
              "score_by_derivability__g", "score_by_comparison__g", "select_nth__g"]


def build_battery():
    canary = json.loads((SRC.parent / "data" / "clean_canary_v01.json")
                        .read_text(encoding="utf-8"))["tasks"]
    from composition_gauntlet import build_synthetic_canary
    from inference_canary import build_inference_canary
    from cross_tier_canary import build_cross_tier_canary
    subs = [("canary", canary), ("synth", build_synthetic_canary(n_each=15)),
            ("inference", build_inference_canary(n=20)),
            ("cross_tier", build_cross_tier_canary(n=20))]
    tasks = [t for _, ts in subs for t in ts]
    bounds, off = [], 0
    for name, ts in subs:
        bounds.append((name, off, off + len(ts)))
        off += len(ts)
    return tasks, bounds


def valid_orders(subset, reads, writes, cap):
    """Up to `cap` valid topological orderings of `subset`: each op runs only once every
    slot it reads has been written. Deterministic DFS, so runs are reproducible."""
    out = []

    def rec(avail, remaining, acc):
        if len(out) >= cap:
            return
        if not remaining:
            out.append(tuple(acc))
            return
        for op in sorted(remaining):
            if reads[op] <= avail:
                rec(avail | writes[op], remaining - {op}, acc + [op])
                if len(out) >= cap:
                    return

    rec(GIVEN, set(subset), [])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-k", type=int, default=10, help="max transformers in the body")
    ap.add_argument("--orders", type=int, default=4, help="valid orderings per subset")
    ap.add_argument("--time-budget-s", type=int, default=64800, help="hard stop (18h)")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    tasks, bounds = build_battery()
    single_baseline = be._single_primitive_baseline(tasks)

    transformers = sorted(be.TRANSFORMERS)
    scorers = sorted(be.SCORERS)
    guarded = sorted(be.GUARDED_SCORERS)
    reads = {n: frozenset(be.REGISTRY[n][0].reads) for n in be.REGISTRY}
    writes = {n: frozenset(be.REGISTRY[n][0].writes) for n in be.REGISTRY}

    # Guard-set tails must reach the size the KNOWN organism uses (5). An earlier version
    # capped at 3 and therefore could not represent the 0.833 shape at all — it would have
    # reported "enumeration cannot reach the ceiling" as a win for evolution. This is the
    # under-exploration failure mode named in PREREGISTRATION.md; the control below now
    # tests the FULL pipeline, not just the body.
    tails = [(s,) for s in scorers]
    for g in range(2, len(guarded) + 1):
        tails += [tuple(c) for c in combinations(guarded, g)]

    def acc_of(pipeline):
        return be._evaluate_acc([be.REGISTRY[n][0] for n in pipeline], tasks)

    def sub_acc(pipeline):
        ops = [be.REGISTRY[n][0] for n in pipeline]
        out = {}
        for name, a, b in bounds:
            k = 0
            for t in tasks[a:b]:
                st = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
                try:
                    if be.run_pipeline(ops, st).selected_answer == t["correct"]:
                        k += 1
                except Exception:
                    pass
            out[name] = round(k / max(b - a, 1), 3)
        return out

    # ── positive control FIRST: is the known organism even representable+scorable? ──
    known_acc = acc_of(KNOWN_0833)
    known_body = [n for n in KNOWN_0833 if be.role_of(n) != be.ROLE_SCORER]
    known_orders = valid_orders(known_body, reads, writes, cap=1)
    known_tail = tuple(n for n in KNOWN_0833 if be.role_of(n) == be.ROLE_SCORER)
    tail_reachable = tuple(sorted(known_tail)) in {tuple(sorted(t)) for t in tails}
    body_reachable = len(known_body) <= args.max_k and len(known_orders) > 0
    control_ok = known_acc >= 0.8 and body_reachable and tail_reachable
    print(f"positive control: known organism scores {known_acc:.3f} | body orderable "
          f"{bool(known_orders)} (k={len(known_body)}<=max_k {args.max_k}: {body_reachable}) "
          f"| tail of {len(known_tail)} guards reachable: {tail_reachable}", flush=True)
    if not control_ok:
        json.dump({"verdict": "ENUMERATOR_BROKEN",
                   "known_acc": known_acc, "body_reachable": body_reachable,
                   "tail_reachable": tail_reachable,
                   "note": "the known 0.833 organism is not representable in the enumerated "
                           "space; this run says NOTHING about evolution"},
                  open(OUT / "RESULT.json", "w", encoding="utf-8"), indent=2)
        print("ENUMERATOR_BROKEN — reports nothing about evolution.")
        return

    evals = 0
    best = {"acc": -1.0}
    best_raw = -1.0
    rows = []
    evals_to_ceiling = None
    ceiling_pipeline = None
    t0 = time.time()
    stopped_early = None

    print(f"battery {len(tasks)} | {len(transformers)} transformers, {len(tails)} tails | "
          f"comparator: {EVOLUTION_EVALS_TO_CEILING} evals to {EVOLUTION_CEILING}", flush=True)

    for k in range(1, args.max_k + 1):
        k_evals, k_best, k_subsets, k_orderable = 0, -1.0, 0, 0
        for subset in combinations(transformers, k):
            k_subsets += 1
            orders = valid_orders(subset, reads, writes, args.orders)
            if not orders:
                continue
            k_orderable += 1
            for body in orders:
                for tail in tails:
                    pipeline = list(body) + list(tail)
                    a = acc_of(pipeline)
                    evals += 1
                    k_evals += 1
                    if a > k_best:
                        k_best = a
                    if a > best_raw + 1e-12:
                        best_raw = a
                        best = {"acc": round(a, 4), "pipeline": pipeline, "k": k,
                                "evals_when_found": evals,
                                "comp_lift": round(a - single_baseline, 4)}
                        print(f"    new best {a:.4f} @eval {evals} (k={k}): "
                              f"{' -> '.join(pipeline)}", flush=True)
                    if evals_to_ceiling is None and a >= EVOLUTION_CEILING:
                        evals_to_ceiling = evals
                        ceiling_pipeline = pipeline
                        print(f"  *** CEILING {EVOLUTION_CEILING} reached at eval {evals} "
                              f"(k={k}): {' -> '.join(pipeline)}", flush=True)
            if time.time() - t0 > args.time_budget_s:
                stopped_early = f"time budget at k={k}"
                break
        rows.append({"k": k, "subsets": k_subsets, "orderable_subsets": k_orderable,
                     "evals_at_k": k_evals, "cumulative_evals": evals,
                     "best_at_k": round(k_best, 4), "best_overall": best["acc"],
                     "elapsed_s": round(time.time() - t0, 1)})
        print(f"  k={k:2d}: subsets={k_subsets:6d} orderable={k_orderable:6d} "
              f"evals={k_evals:8d} cum={evals:9d} best_k={k_best:.3f} "
              f"best={best['acc']:.3f} ({time.time()-t0:.0f}s)", flush=True)
        # checkpoint every k so a long run is never lost
        json.dump({"partial": True, "by_k": rows, "best_found": best,
                   "enumeration_evals_to_ceiling": evals_to_ceiling,
                   "total_evals": evals},
                  open(OUT / "RESULT_partial.json", "w", encoding="utf-8"), indent=2)
        if stopped_early:
            break

    if evals_to_ceiling is not None:
        verdict = ("ENUMERATION_WINS — evolution is decorative"
                   if evals_to_ceiling < EVOLUTION_EVALS_TO_CEILING
                   else "EVOLUTION_MORE_EFFICIENT")
    else:
        verdict = "ENUMERATION_CANNOT_REACH_CEILING — evolution has a reachability advantage"

    result = {
        "experiment": "O1_type_directed_enumeration",
        "prereg": "apollo/cycles/o1_enumeration/PREREGISTRATION.md",
        "date": "2026-08-23", "generator": "Apollo (M2)",
        "config": {"max_k": args.max_k, "orders_per_subset": args.orders,
                   "n_transformers": len(transformers), "n_tails": len(tails),
                   "stopped_early": stopped_early},
        "comparator": {"evolution_evals_to_ceiling": EVOLUTION_EVALS_TO_CEILING,
                       "evolution_ceiling": EVOLUTION_CEILING,
                       "note": "pop 24 x gen 131, the generation max_acc first hit 0.833"},
        "enumeration_evals_to_ceiling": evals_to_ceiling,
        "ceiling_pipeline": ceiling_pipeline,
        "total_evals": evals,
        "best_found": best,
        "best_per_subset": sub_acc(best["pipeline"]) if best.get("pipeline") else None,
        "by_k": rows,
        "positive_control": {"known_0833_organism_acc": round(known_acc, 4), "ok": True},
        "single_primitive_baseline": single_baseline,
        "wall_clock_s": round(time.time() - t0, 1),
        "verdict": verdict,
    }
    with open(OUT / "RESULT.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

    print(f"\ntotal evals {evals} | best {best['acc']} at k={best.get('k')} "
          f"after {best.get('evals_when_found')} evals")
    print(f"best: {' -> '.join(best.get('pipeline', []))}")
    print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
