"""PTE-C3S reducer (frozen rules; PREREG_PTE_C3S.md s4). usage: python reduce_c3s.py PLAN.json RUN_DIR OUT.json

Per search, on the C2C held worlds with the frozen FLIP ruler (B = mean(changed-cue acc, same-cue acc)):
  stone B  = injected stone's held B;  BL B = best surviving lineage member's held B (chosen on monitor worlds).
  D  CLIMB_TO_COMPETENCE : BL is competent (status TRUE), or the champion is competent with lineage share >= .5
  A  LINEAGE_AND_FUNCTION_SURVIVE : lineage alive, not D, BL B >= stone B - .05
  B  LINEAGE_SURVIVES_FUNCTION_ERODES : lineage alive, not D, BL B < stone B - .05
  C  LINEAGE_DIES : no final-population member with lineage share >= .5
  climb (secondary) : lineage alive and BL B >= stone B + .05
  retained = A or D.
Exclusions (flagged; never counted): PLANT/STONE inconsistency is not applicable here; OVERLAP (held/train or
held/monitor), REPLAY_FAIL (S8 arm whose champion or status differs from the C2C OP0_STEP row: a reproducibility
failure -> the S8 row is excluded and the run is flagged).
Effects (paired by stone; each stone contributes one paired difference per level of the other factor):
  M effect      = retained(M32) - retained(M8), pooled over shaping on/off (56 pairs).
  shaping effect= retained(shaping off) - retained(shaping on), pooled over M 8/32 (56 pairs).
  Exact one-sided (M) / two-sided (shaping) sign test on discordant pairs; per-cell mean differences; a stone-level
  bootstrap 95% interval (seed 0, 4000 draws) of the pooled mean difference.
Labels (both may be issued):
  SELECTOR_RESOLUTION_EFFECT : M effect >= +.20, sign-test p < .05, positive in >= 3 of 4 cells;
                               OR D under M32 arms >= 4 in >= 2 cells and exceeding D under M8 arms by >= 4.
  NO_SELECTOR_RESOLUTION_EFFECT : not the above, M-effect bootstrap upper bound < .20, and P(retained | M32) <= .50.
  SHAPING_INTERFERENCE : |shaping effect| >= .20, two-sided sign-test p < .05, same sign in >= 3 of 4 cells
                         (direction reported: shaping HURTS retention if the effect is positive).
  MIXED_OR_INCONCLUSIVE : no label above.
Decision rule for C3R: if SELECTOR_RESOLUTION_EFFECT, C3R uses M32 in every arm; otherwise C3R uses the C2 selector.
"""
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np
from scipy.stats import binomtest


def classify(r):
    if r["final_n_lineage"] == 0:
        return "C"
    sb = r["stone_held"]["B"]["mean"]
    blB = r["bl_held"]["B"]["mean"] if r["bl_held"] else None
    d = (r["bl_held"] and r["bl_held"]["status"] == "TRUE") or (r["champ_held"]["status"] == "TRUE" and r["champ_share"] >= .5)
    if d:
        return "D"
    return "A" if blB is not None and blB >= sb - .05 else "B"


def main(plan_p, run_dir, out_p):
    plan = json.load(open(plan_p))
    rows = []
    for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")):
        rows += [json.loads(l) for l in open(p) if l.strip()]
    flags, kept = [], []
    for r in rows:
        bad = None
        if r["held_train_overlap"] or r["held_monitor_overlap"]:
            bad = "OVERLAP"
        elif r["arm"] == "S8" and r.get("replay_gate") and not (r["replay_gate"]["champion_equal"] and r["replay_gate"]["status_equal"]):
            bad = "REPLAY_FAIL"
        (flags.append([bad, r["job_id"]]) if bad else kept.append(r))
    for r in kept:
        r["cls"] = classify(r)
        r["retained"] = r["cls"] in ("A", "D")
        r["climb"] = r["cls"] != "C" and r["bl_held"] is not None and r["bl_held"]["B"]["mean"] >= r["stone_held"]["B"]["mean"] + .05
    by = {(r["cell_id"], r["idx"], r["arm"]): r for r in kept}
    arms = sorted({r["arm"] for r in kept})
    res = {"n_rows": len(rows), "n_counted": len(kept), "flags": flags, "arms": {}}
    for a in arms:
        rr = [r for r in kept if r["arm"] == a]
        cnt = {k: sum(r["cls"] == k for r in rr) for k in "ABCD"}
        res["arms"][a] = {"n": len(rr), **cnt, "retained": sum(r["retained"] for r in rr), "climb": sum(r["climb"] for r in rr),
                          "champ_competent": sum(r["champ_held"]["status"] == "TRUE" for r in rr),
                          "median_bl_B": float(np.median([r["bl_held"]["B"]["mean"] for r in rr if r["bl_held"]] or [np.nan])),
                          "median_stone_B": float(np.median([r["stone_held"]["B"]["mean"] for r in rr])),
                          "per_cell": {c: {k: sum(1 for r in rr if r["cell_id"] == c and r["cls"] == k) for k in "ABCD"}
                                       for c in sorted({r["cell_id"] for r in rr})}}

    def effect(a_hi, a_lo, pairs_of_levels, two_sided=False):
        diffs, cells_d = [], defaultdict(list)
        for hi, lo in pairs_of_levels:
            for (c, i, a), r in by.items():
                if a != hi:
                    continue
                q = by.get((c, i, lo))
                if q is None:
                    continue
                d = int(r["retained"]) - int(q["retained"])
                diffs.append((c, i, d)); cells_d[c].append(d)
        if not diffs:
            return None
        dv = np.array([d for _, _, d in diffs])
        pos, neg = int((dv > 0).sum()), int((dv < 0).sum())
        n = pos + neg
        p = (binomtest(pos, n, .5, alternative="two-sided" if two_sided else "greater").pvalue if n else 1.0)
        stones = sorted({(c, i) for c, i, _ in diffs})
        rng = np.random.default_rng(0)
        bs = []
        for _ in range(4000):
            pick = [stones[j] for j in rng.integers(len(stones), size=len(stones))]
            vals = [d for s in pick for (c, i, d) in diffs if (c, i) == s]
            bs.append(np.mean(vals))
        return {"n_pairs": len(dv), "mean": float(dv.mean()), "pos": pos, "neg": neg, "sign_p": float(p),
                "boot95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                "per_cell_mean": {c: float(np.mean(v)) for c, v in cells_d.items()}}
    Meff = effect(None, None, [("S32", "S8"), ("W32", "W8")])
    Seff = effect(None, None, [("W8", "S8"), ("W32", "S32")], two_sided=True)
    res["M_effect"] = Meff; res["shaping_effect"] = Seff
    labels = []
    D32 = sum(r["cls"] == "D" for r in kept if r["arm"] in ("S32", "W32"))
    D8 = sum(r["cls"] == "D" for r in kept if r["arm"] in ("S8", "W8"))
    D32cells = len({r["cell_id"] for r in kept if r["arm"] in ("S32", "W32") and r["cls"] == "D"})
    ret32 = [r["retained"] for r in kept if r["arm"] in ("S32", "W32")]
    if Meff and ((Meff["mean"] >= .20 and Meff["sign_p"] < .05 and sum(v > 0 for v in Meff["per_cell_mean"].values()) >= 3)
                 or (D32 >= 4 and D32cells >= 2 and D32 - D8 >= 4)):
        labels.append("SELECTOR_RESOLUTION_EFFECT")
    elif Meff and Meff["boot95"][1] < .20 and (np.mean(ret32) if ret32 else 0) <= .50:
        labels.append("NO_SELECTOR_RESOLUTION_EFFECT")
    if Seff and abs(Seff["mean"]) >= .20 and Seff["sign_p"] < .05:
        sgn = np.sign(Seff["mean"])
        if sum(np.sign(v) == sgn for v in Seff["per_cell_mean"].values()) >= 3:
            labels.append("SHAPING_INTERFERENCE" + ("(shaping_hurts_retention)" if sgn > 0 else "(shaping_helps_retention)"))
    res["labels"] = labels or ["MIXED_OR_INCONCLUSIVE"]
    res["D_M32"], res["D_M8"] = D32, D8
    res["c3r_selector"] = "M32" if "SELECTOR_RESOLUTION_EFFECT" in labels else "M8 (C2 selector)"
    json.dump(res, open(out_p, "w"), indent=1, default=str)
    print(json.dumps({"labels": res["labels"], "c3r_selector": res["c3r_selector"],
                      "arms": {a: {k: v[k] for k in ("n", "A", "B", "C", "D", "retained", "climb", "median_bl_B", "median_stone_B")} for a, v in res["arms"].items()},
                      "M_effect": Meff and {k: Meff[k] for k in ("mean", "sign_p", "boot95")},
                      "shaping_effect": Seff and {k: Seff[k] for k in ("mean", "sign_p", "boot95")}}, indent=1, default=str))
    print("flags", flags)


if __name__ == "__main__":
    main(*sys.argv[1:4])
