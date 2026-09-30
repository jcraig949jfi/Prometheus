"""Pilot evaluator -> PILOT.json. Criterion code is shared with evaluate.py."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RATIO_OK, RATIO_FAIL, OV_OK, OV_FAIL = 0.7, 0.9, 0.05, 0.2
NEED_OK, NEED_FAIL = 8, 5


def load(name):
    with open(os.path.join(HERE, name)) as f:
        return [json.loads(l) for l in f if l.strip()]


def by_arm(rows, arm):
    return {r["seed"]: r for r in rows if r["arm"] == arm}


def criterion(sanc, null):
    """sanc, null: {seed: row}. Applies the spec's success/failure criteria."""
    seeds = sorted(set(sanc) & set(null))
    ratios = {s: (sanc[s]["s_psi"] / null[s]["s_psi"]) if null[s]["s_psi"] else float("inf")
              for s in seeds}
    m13_ok = sum(sanc[s]["s_psi"] <= RATIO_OK * null[s]["s_psi"] for s in seeds)
    m3_ok_s = sum(sanc[s]["overlap"] <= OV_OK for s in seeds)
    m3_ok_n = sum(null[s]["overlap"] <= OV_OK for s in seeds)
    m13_bad = sum(ratios[s] > RATIO_FAIL for s in seeds)
    m3_bad_s = sum(sanc[s]["overlap"] > OV_FAIL for s in seeds)
    m3_bad_n = sum(null[s]["overlap"] > OV_FAIL for s in seeds)
    m13_success = m13_ok >= NEED_OK
    m3_success = m3_ok_s >= NEED_OK and m3_ok_n >= NEED_OK
    return dict(n_seeds=len(seeds), ratios=ratios,
                m13_seeds_ratio_le_0p7=m13_ok, m13_success=m13_success,
                m3_seeds_overlap_le_0p05_sanction_slot=m3_ok_s,
                m3_seeds_overlap_le_0p05_null_slot=m3_ok_n, m3_success=m3_success,
                success=bool(m13_success and m3_success),
                m13_seeds_ratio_gt_0p9=m13_bad, m13_failed=m13_bad >= NEED_FAIL,
                m3_seeds_overlap_gt_0p2_sanction_slot=m3_bad_s,
                m3_seeds_overlap_gt_0p2_null_slot=m3_bad_n,
                m3_failed=(m3_bad_s >= NEED_FAIL or m3_bad_n >= NEED_FAIL))


def summarize(d):
    vals = {k: [r[k] for r in d.values()] for k in ("s_psi", "overlap", "w_norm2",
                                                  "mean_sanction_rate", "gen0_sanction_rate")}
    return {k: v for k, v in vals.items()}


def main(attempt=1):
    rows = load("pilot_rows.jsonl")
    pc, nt, ntb, ch = (by_arm(rows, a) for a in
                       ("POSITIVE_CONTROL", "NULL_TWIN", "NULL_TWIN_B", "CHEAT"))
    pc_gen0_ok = sum(r["gen0_sanction_rate"] < 0.05 for r in pc.values())
    pc_crit = criterion(pc, nt)
    positive = bool(pc_gen0_ok >= NEED_OK and pc_crit["success"])
    cheat_crit = criterion(ch, nt)
    null_crit = criterion(nt, ntb)
    out = dict(positive_meets_success=positive,
               cheat_detected=bool(cheat_crit["success"]),
               null_twin_meets_success=bool(null_crit["success"]),
               attempt=int(attempt))
    out["pilot_pass"] = bool(out["positive_meets_success"] and out["cheat_detected"]
                             and not out["null_twin_meets_success"])
    out["stats"] = dict(pc_gen0_sanction_rate_lt_0p05_seeds=pc_gen0_ok,
                        positive_vs_null_twin=pc_crit, cheat_vs_null_twin=cheat_crit,
                        null_twin_vs_null_twin_b=null_crit,
                        per_arm={a: summarize(d) for a, d in
                                 (("POSITIVE_CONTROL", pc), ("NULL_TWIN", nt),
                                  ("NULL_TWIN_B", ntb))},
                        cpu_s_total=sum(r["cpu_s"] for r in rows))
    with open(os.path.join(HERE, "PILOT.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "stats"}))


if __name__ == "__main__":
    main(*sys.argv[1:])
