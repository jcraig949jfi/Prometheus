"""W5 probe evaluator (HT-e106e1603b). Reproducibility check against
ATTAINABILITY.json FIRST, then the frozen clauses. Writes OUTCOME.json."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import math
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
sys.path.insert(0, WORLD)
import controls as C  # noqa: E402

CMP = {">=": lambda a, b: a >= b, "<": lambda a, b: a < b,
       ">": lambda a, b: a > b, "<=": lambda a, b: a <= b}


def load_rows():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8") if l.strip()]
    by = {}
    for r in rows:
        by.setdefault(r["arm"], {})[r["seed"]] = r
    return by


def gvec(by, arm, seeds):
    return [by[arm][s]["G"] for s in seeds]


def clause_value(cid, g):
    return float(np.mean(g)) if cid in ("S1", "F1") else float(np.min(g))


def main():
    c0 = time.process_time()
    spec = json.load(open(os.path.join(WORLD, "spec.json"), encoding="utf-8"))
    att = json.load(open(os.path.join(WORLD, "ATTAINABILITY.json"), encoding="utf-8"))
    seeds = spec["seeds"]
    by = load_rows()
    anomalies, notes = [], []
    out = {"triplicateId": spec["triplicateId"], "world": spec["id"]}

    # ---- 1. reproducibility -------------------------------------------------
    missing = [(a, s) for a in ("TREATMENT", "POSITIVE_CONTROL", "NULL_TWIN", "CHEAT")
               for s in seeds if s not in by.get(a, {})]
    if missing:
        out.update(outcome="NOT_BUILT", notes=[f"missing rows {missing}"])
        json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
        return
    repro = []
    for arm in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"):
        dev = max(abs(a - b) for a, b in zip(gvec(by, arm, seeds), att["per_seed"][arm]))
        if dev > 1e-9:
            anomalies.append(f"{arm} per-seed G deviates from ATTAINABILITY.json by up to {dev:.3g}")
        repro.append({"arm": arm, "max_abs_dev_G": dev})
    repro_ok = True
    for cl in spec["success_clauses"]:
        pv = clause_value(cl["id"], gvec(by, "POSITIVE_CONTROL", seeds))
        tv = clause_value(cl["id"], gvec(by, "NULL_TWIN", seeds))
        f = CMP[cl["comparison"]]
        attn, disc = bool(f(pv, cl["threshold"])), bool(not f(tv, cl["threshold"]))
        frozen = next(c for c in att["clauses"] if c["id"] == cl["id"])
        same = attn == frozen["attainable"] and disc == frozen["discriminating"]
        repro_ok &= same
        repro.append({"clause": cl["id"], "positive_value": pv, "twin_value": tv,
                      "attainable": attn, "discriminating": disc,
                      "frozen_attainable": frozen["attainable"],
                      "frozen_discriminating": frozen["discriminating"], "match": same})
    out["reproducibility"] = repro

    def meets_success(arm):
        g = gvec(by, arm, seeds)
        return all(CMP[c["comparison"]](clause_value(c["id"], g), c["threshold"])
                   for c in spec["success_clauses"])

    f1 = next(c for c in spec["failure_clauses"] if c["id"] == "F1")
    f2 = next(c for c in spec["failure_clauses"] if c["id"] == "F2")
    pc_detected = meets_success("POSITIVE_CONTROL") and not CMP[f1["comparison"]](
        clause_value("F1", gvec(by, "POSITIVE_CONTROL", seeds)), f1["threshold"])
    cheat_detected = meets_success("CHEAT")
    twin_success = meets_success("NULL_TWIN")

    # ---- 2. treatment clauses -------------------------------------------------
    gt = gvec(by, "TREATMENT", seeds)
    blk = [np.load(os.path.join(HERE, f"treatment_blocks_seed{s}.npz")) for s in seeds]
    p = np.concatenate([b["p"] for b in blk]); t = np.concatenate([b["t"] for b in blk])
    hi = (p >= 0.06) & (p <= 0.09); lo = (p >= 0.02) & (p <= 0.04)
    med_hi, med_lo = float(np.median(t[hi])), float(np.median(t[lo]))
    if med_lo > 0:
        ratio = med_hi / med_lo
    elif med_hi > 0:
        ratio = math.inf
    else:
        ratio = None
        notes.append("F2 ratio undefined (both medians 0): F2 treated as holding")
    stats = {"TREATMENT_G_per_seed": gt,
             "S1_mean_G": clause_value("S1", gt), "S2_min_G": clause_value("S2", gt),
             "F1_mean_G": clause_value("F1", gt),
             "F2_ratio": ratio, "median_t_p_0.06_0.09": med_hi, "median_t_p_0.02_0.04": med_lo,
             "n_hi": int(hi.sum()), "n_lo": int(lo.sum()),
             "frac_cap_all": float((t == C.TMAX).mean()),
             "frac_cap_hi": float((t[hi] == C.TMAX).mean()), "frac_cap_lo": float((t[lo] == C.TMAX).mean()),
             "frac_t0": float((t == 0).mean()),
             "n_wrong_codeword": int(sum(int(b["wrong"].sum()) for b in blk))}
    for arm in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"):
        g = gvec(by, arm, seeds)
        stats[arm] = {"G_per_seed": g, "mean_G": float(np.mean(g)), "min_G": float(np.min(g))}
    # secondary (spec alternative_explanation, not a clause): G from 1[t = cap]
    gcap = []
    for s, b in zip(seeds, blk):
        ind = (b["t"] == C.TMAX).astype(float)
        gcap.append(C.g_statistic(b["w"], b["s"], ind, s)[0])
    stats["secondary_G_cap_indicator_per_seed"] = gcap
    stats["secondary_G_cap_indicator_mean"] = float(np.mean(gcap))
    # descriptive: G using only unconverged-vs-converged-with-graded-t among t < cap
    s1 = CMP[">="](stats["S1_mean_G"], 0.20)
    s2 = CMP[">="](stats["S2_min_G"], 0.10)
    f1h = CMP[f1["comparison"]](stats["F1_mean_G"], f1["threshold"])
    f2h = True if ratio is None else CMP[f2["comparison"]](ratio, f2["threshold"])
    applied = {"S1": {"value": stats["S1_mean_G"], "cmp": ">=", "threshold": 0.20, "holds": bool(s1)},
               "S2": {"value": stats["S2_min_G"], "cmp": ">=", "threshold": 0.10, "holds": bool(s2)},
               "F1": {"value": stats["F1_mean_G"], "cmp": "<", "threshold": 0.05, "holds": bool(f1h)},
               "F2": {"value": ratio, "cmp": "<", "threshold": 1.5, "holds": bool(f2h)},
               "rule": spec["outcome_rule"]}

    # ---- 3. outcome ---------------------------------------------------------
    if not repro_ok:
        outcome = "INSTRUMENT_FAIL"
        notes.append("reproducibility: control clause status differs from ATTAINABILITY.json")
    elif not (pc_detected and cheat_detected):
        outcome = "INSTRUMENT_FAIL"
    elif twin_success:
        outcome = "CONFOUNDED"
    elif s1 and s2 and not f1h and not f2h:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"
        if 0.05 <= stats["S1_mean_G"] < 0.20:
            notes.append("NULL (weak): mean G in [0.05, 0.20)")

    # stupid explanations
    se_text = spec["stupid_explanations"]
    cap_share = (stats["secondary_G_cap_indicator_mean"] / stats["S1_mean_G"]
                 if stats["S1_mean_G"] > 0 else None)
    se = [
        {"text": se_text[0], "addressed_by_this_run": True,
         "how": f"secondary G with t -> 1[t=60]: mean {stats['secondary_G_cap_indicator_mean']:.4f} vs "
                f"full-t mean {stats['S1_mean_G']:.4f} (ratio {cap_share if cap_share is None else round(cap_share, 3)}); "
                f"cap fraction {stats['frac_cap_all']:.3f}"},
        {"text": se_text[1], "addressed_by_this_run": True,
         "how": f"null twin (t from s alone, same shape) re-run in the same code path: mean G "
                f"{stats['NULL_TWIN']['mean_G']:.4f}; underfit absorption by an s-correlated feature is at most this"},
        {"text": se_text[2], "addressed_by_this_run": True,
         "how": "decoder uses fixed LLR +-1 for every block (world.py min_sum_iterations); p and w are never passed to it"},
        {"text": se_text[3], "addressed_by_this_run": False,
         "how": "reported only: cap fractions (all/hi/lo) and the cap-indicator G; no run with a different cap "
                "(the cap is frozen), so a plateau set by the cap is not excluded"},
    ]

    cpu_world = json.load(open(os.path.join(HERE, "world_cpu.json")))["cpu_seconds"]
    out.update({
        "outcome": outcome, "statistics": stats, "criterion_as_applied": applied,
        "positive_control_detected": bool(pc_detected), "cheat_detected": bool(cheat_detected),
        "null_twin_meets_success": bool(twin_success),
        "stupid_explanations_status": se, "anomalies": anomalies,
        "core_minutes": round((cpu_world + time.process_time() - c0) / 60.0, 3),
        "attempts": 1, "notes": notes})
    with open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(outcome, json.dumps(applied))


if __name__ == "__main__":
    sys.exit(main())
