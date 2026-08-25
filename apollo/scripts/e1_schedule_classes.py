"""e1_schedule_classes.py — E1: did O1 cover the behaviourally distinct schedules?

O1's ceiling claim rests on sampling 48 topological orderings per operator subset, from
subsets with up to 166,320 valid orderings. If most orderings are behaviourally identical,
48 may be effectively exhaustive. If not, "nothing in 1.74M pipelines beats 0.833" is a
statement about a sample, not about the space.

Reviewer's correction, adopted: STATIC noncommutativity OVERCOUNTS. Two orderings can differ
statically and be semantically identical. The unit is a SEMANTIC SCHEDULE CLASS — orderings
producing the same answer vector across the whole battery.

Method:
  1. Static conflict graph from @blackboard_op declarations (write-write, read-after-write).
     Upper bound on distinct classes.
  2. EXECUTE orderings for sampled subsets, cluster by battery-answer-vector -> the true
     semantic class count. Measures how far the static bound overshoots.
  3. Self-test: the checker must rediscover the write-write hazard that invalidated two O1
     runs (relations_from_facts vs parse_names_and_relations, both write `relations`).
     If it cannot rediscover a hazard known to exist, the checker is broken.

Pre-committed outcome (PREREGISTRATION §4), one of two sentences chosen in advance:
  - "O1 covered essentially all behaviourally distinct schedules"  if semantic classes
    at k>=8 are <= the 48 orderings O1 sampled per subset;
  - "O1 sampled an unknown fraction of behaviourally distinct schedules" otherwise, in
    which case O1's ceiling is DOWNGRADED from measured to conjectured.

CAVEAT, standing after E9: the battery this is measured on does not survive independent
authorship. E1 is instrument validity on O1, not a capability claim.

Usage: python e1_schedule_classes.py --subsets 40 --max-orders 400
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
OUT = HERE.parent / "cycles" / "campaign_20260825"
sys.path.insert(0, str(SRC)); sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be  # noqa: E402
from blackboard import BlackboardState, run_pipeline  # noqa: E402

GIVEN = frozenset({"problem_text", "candidates"})
O1_ORDERS_SAMPLED = 48


def battery():
    canary = json.loads((SRC.parent / "data" / "clean_canary_v01.json")
                        .read_text(encoding="utf-8"))["tasks"]
    from composition_gauntlet import build_synthetic_canary
    from inference_canary import build_inference_canary
    from cross_tier_canary import build_cross_tier_canary
    return canary + build_synthetic_canary(n_each=15) + \
        build_inference_canary(n=20) + build_cross_tier_canary(n=20)


def conflict_graph(reads, writes, ops):
    """Pairs whose relative order can matter, from declarations alone."""
    ww, raw_, pairs = [], [], []
    for a, b in combinations(sorted(ops), 2):
        w_w = writes[a] & writes[b]
        r_a_w = (reads[a] & writes[b]) | (reads[b] & writes[a])
        if w_w:
            ww.append((a, b, sorted(w_w)))
        if r_a_w:
            raw_.append((a, b, sorted(r_a_w)))
        if w_w or r_a_w:
            pairs.append((a, b))
    return ww, raw_, set(pairs)


def valid_orders(subset, reads, writes, cap):
    out = []

    def rec(avail, remaining, acc):
        if len(out) >= cap:
            return
        if not remaining:
            out.append(tuple(acc)); return
        for op in sorted(remaining):
            if reads[op] <= avail:
                rec(avail | writes[op], remaining - {op}, acc + [op])
                if len(out) >= cap:
                    return
    rec(GIVEN, set(subset), [])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subsets", type=int, default=40)
    ap.add_argument("--max-orders", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20260825)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    random.seed(args.seed)

    tasks = battery()
    transformers = sorted(be.TRANSFORMERS)
    reads = {n: frozenset(be.REGISTRY[n][0].reads) for n in be.REGISTRY}
    writes = {n: frozenset(be.REGISTRY[n][0].writes) for n in be.REGISTRY}
    tail = ["score_by_extreme_number__g", "score_by_aggregate__g",
            "score_by_derivability__g", "score_by_comparison__g", "select_nth__g"]

    ww, raw_, conflicting = conflict_graph(reads, writes, transformers)
    n_pairs = len(list(combinations(transformers, 2)))
    print(f"static conflict graph over {len(transformers)} transformers, {n_pairs} pairs")
    print(f"  write-write pairs      : {len(ww)}")
    print(f"  read-after-write pairs : {len(raw_)}")
    print(f"  order-relevant pairs   : {len(conflicting)} ({len(conflicting)/n_pairs:.1%})")
    print(f"  commuting pairs        : {n_pairs-len(conflicting)} "
          f"({(n_pairs-len(conflicting))/n_pairs:.1%})")

    # self-test: must rediscover the known hazard
    known = ("parse_names_and_relations", "relations_from_facts")
    found = any(set(p[:2]) == set(known) for p in ww)
    print(f"\nSELF-TEST rediscover known write-write hazard {known}: "
          f"{'PASS' if found else 'FAIL — checker is broken'}")
    if not found:
        json.dump({"verdict": "CHECKER_BROKEN"},
                  open(OUT / "E1_RESULT.json", "w", encoding="utf-8"), indent=2)
        return

    def answer_vector(pipeline):
        ops = [be.REGISTRY[n][0] for n in pipeline]
        v = []
        for t in tasks:
            st = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
            try:
                v.append(run_pipeline(ops, st).selected_answer)
            except Exception:
                v.append("__ERR__")
        return tuple(v)

    rows = []
    for k in (4, 6, 8, 10):
        cand = [s for s in combinations(transformers, k)]
        random.shuffle(cand)
        picked, done = [], 0
        for subset in cand:
            if done >= args.subsets:
                break
            orders = valid_orders(subset, reads, writes, args.max_orders)
            if len(orders) < 2:
                continue
            classes = {}
            for o in orders:
                classes.setdefault(answer_vector(list(o) + tail), []).append(o)
            picked.append({"subset": list(subset), "n_orders_enumerated": len(orders),
                           "n_semantic_classes": len(classes),
                           "collapse_ratio": round(len(orders) / len(classes), 2)})
            done += 1
        if not picked:
            continue
        mx = max(p["n_semantic_classes"] for p in picked)
        med = sorted(p["n_semantic_classes"] for p in picked)[len(picked) // 2]
        rows.append({"k": k, "subsets_measured": len(picked),
                     "max_semantic_classes": mx, "median_semantic_classes": med,
                     "max_orders_enumerated": max(p["n_orders_enumerated"] for p in picked),
                     "mean_collapse_ratio": round(
                         sum(p["collapse_ratio"] for p in picked) / len(picked), 2),
                     "detail": picked[:8]})
        print(f"  k={k:2d}: {len(picked)} subsets | orders<= {rows[-1]['max_orders_enumerated']:4d}"
              f" | semantic classes median {med} max {mx}"
              f" | collapse x{rows[-1]['mean_collapse_ratio']}")

    deep = [r for r in rows if r["k"] >= 8]
    covered = all(r["max_semantic_classes"] <= O1_ORDERS_SAMPLED for r in deep) if deep else False
    verdict = ("O1 covered essentially all behaviourally distinct schedules" if covered
               else "O1 sampled an unknown fraction of behaviourally distinct schedules — "
                    "the ceiling is DOWNGRADED from measured to conjectured")
    print(f"\nVERDICT: {verdict}")

    res = {"experiment": "E1_semantic_schedule_classes", "date": "2026-08-25",
           "prereg": "apollo/cycles/campaign_20260825/PREREGISTRATION.md §4",
           "static": {"n_transformers": len(transformers), "n_pairs": n_pairs,
                      "write_write": ww, "read_after_write_count": len(raw_),
                      "order_relevant_pairs": len(conflicting),
                      "commuting_fraction": round((n_pairs-len(conflicting))/n_pairs, 4)},
           "self_test_rediscovers_known_hazard": found,
           "by_k": rows, "o1_orders_sampled_per_subset": O1_ORDERS_SAMPLED,
           "verdict": verdict,
           "standing_caveat": ("E9 (2026-08-25) showed the battery does not survive "
                               "independent authorship. E1 is instrument validity on O1, "
                               "not a capability claim.")}
    with open(OUT / "E1_RESULT.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2); f.flush(); os.fsync(f.fileno())


if __name__ == "__main__":
    main()
