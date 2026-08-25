"""IQ-PORT-1 step 0: enumerate the battery inventory. No modelling, no claims.

Reports: subset sizes, per-category counts, and for the KNOWN 0.833 organism
which tasks pass/fail and whether the failures abstain (selected_answer empty).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "apollo" / "src"
SCRIPTS = ROOT / "apollo" / "scripts"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be
from blackboard import BlackboardState

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
    return subs


def main():
    subs = build_battery()
    total = sum(len(ts) for _, ts in subs)
    print(f"SUBSETS (total {total} tasks)")
    for name, ts in subs:
        print(f"  {name:12s} n={len(ts):3d}  keys={sorted(ts[0].keys())}")

    print("\nCATEGORY COUNTS per subset")
    for name, ts in subs:
        c = Counter(t.get("category", "<none>") for t in ts)
        for k, v in sorted(c.items()):
            print(f"  {name:12s} {k:28s} {v}")

    ops = [be.REGISTRY[n][0] for n in KNOWN_0833]
    print("\nKNOWN 0.833 ORGANISM — per-task outcome")
    per_cat = defaultdict(lambda: [0, 0, 0])  # correct, total, abstain
    fails = []
    for name, ts in subs:
        for t in ts:
            cat = f"{name}:{t.get('category','<none>')}"
            st = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
            try:
                out = be.run_pipeline(ops, st)
                ans = out.selected_answer
            except Exception as e:
                ans = f"<EXC {type(e).__name__}>"
            ok = (ans == t["correct"])
            per_cat[cat][1] += 1
            if ok:
                per_cat[cat][0] += 1
            if not ans:
                per_cat[cat][2] += 1
            if not ok:
                fails.append((cat, t["prompt"], t["candidates"], t["correct"], repr(ans)))
    ncorr = sum(v[0] for v in per_cat.values())
    print(f"  overall {ncorr}/{total} = {ncorr/total:.4f}")
    for cat in sorted(per_cat):
        c, n, ab = per_cat[cat]
        print(f"  {cat:34s} {c:3d}/{n:3d}  abstain={ab}")

    print(f"\nFAILING TASKS ({len(fails)})")
    for cat, p, cands, corr, ans in fails:
        print(f"\n  [{cat}] answer={ans} correct={corr!r}")
        print(f"    prompt: {p}")
        print(f"    candidates: {cands}")


if __name__ == "__main__":
    main()
