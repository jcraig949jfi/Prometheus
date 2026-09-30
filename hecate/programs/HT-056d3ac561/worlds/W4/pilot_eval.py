"""W4 pilot evaluator -> PILOT.json (applies the spec criterion; see NOTES.md readings 2-5)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KLE3 = ["1", "2", "3"]
LT, MT, HI, LO = 0.20, 0.50, 0.80, 0.20


def load(attempt):
    rows = [json.loads(l) for l in open(os.path.join(HERE, "pilot_rows.jsonl"), encoding="utf-8")]
    return [r for r in rows if r["attempt"] == attempt]


def idx(rows):
    return {(r["arm"], r["seed"]): r for r in rows}


def full_criterion(I, arm_lasso, arm_mn, seeds):
    """Every seed, every k<=3: lasso clause, min-norm clause, null-twin clause."""
    detail = {}
    ok = True
    for s in seeds:
        for k in KLE3:
            a = I[(arm_lasso, s)]["per_k"][k]["lasso_success_rate"]
            b = I[(arm_mn, s)]["per_k"][k]["mn_success_rate"]
            c = I[("NULL_TWIN", s)]["per_k"][k]["lasso_success_rate"]
            met = (a >= HI) and (b >= HI) and (c <= LO)
            detail[f"s{s}_k{k}"] = {"lasso_rate": a, "mn_rate": b, "nt_lasso_rate": c, "met": met}
            ok = ok and met
    return ok, detail


def arm_clauses(I, arm, seeds):
    ok = True
    detail = {}
    for s in seeds:
        for k in KLE3:
            a = I[(arm, s)]["per_k"][k]["lasso_success_rate"]
            b = I[(arm, s)]["per_k"][k]["mn_success_rate"]
            met = (a >= HI) and (b >= HI)
            detail[f"s{s}_k{k}"] = {"lasso_rate": a, "mn_rate": b, "met": met}
            ok = ok and met
    return ok, detail


def pooled(I, arm, seeds):
    out = {}
    for k in ["1", "2", "3", "6", "10"]:
        rs = [I[(arm, s)]["per_k"][k] for s in seeds]
        out[k] = {
            "lasso_rate": sum(r["lasso_success_rate"] for r in rs) / len(rs),
            "mn_rate": sum(r["mn_success_rate"] for r in rs) / len(rs),
            "lasso_err_median_mean": sum(r["lasso_err_median"] for r in rs) / len(rs),
            "mn_err_median_mean": sum(r["mn_err_median"] for r in rs) / len(rs),
            "lasso_rkf_mean": (sum(r["lasso_rkf_mean"] for r in rs) / len(rs))
            if all(r["lasso_rkf_mean"] is not None for r in rs) else None,
            "mn_rkf_mean": (sum(r["mn_rkf_mean"] for r in rs) / len(rs))
            if all(r["mn_rkf_mean"] is not None for r in rs) else None,
            "visibility_mean": sum(r["visibility_mean"] for r in rs) / len(rs),
        }
    return out


def main():
    attempt = int(sys.argv[1])
    rows = load(attempt)
    I = idx(rows)
    seeds = sorted({r["seed"] for r in rows})
    assert len(seeds) >= 5
    pos, pos_d = full_criterion(I, "POSITIVE_CONTROL", "POSITIVE_CONTROL", seeds)
    cheat, cheat_d = full_criterion(I, "CHEAT", "CHEAT", seeds)
    nt, nt_d = arm_clauses(I, "NULL_TWIN", seeds)
    res = {
        "positive_meets_success": pos,
        "cheat_detected": cheat,
        "null_twin_meets_success": nt,
        "pilot_pass": bool(pos and cheat and not nt),
        "stats": {
            "pc_mode": rows[0]["pc_mode"],
            "pooled": {a: pooled(I, a, seeds) for a in ("POSITIVE_CONTROL", "CHEAT", "NULL_TWIN")},
            "per_seed_k": {"POSITIVE_CONTROL": pos_d, "CHEAT": cheat_d, "NULL_TWIN": nt_d},
            "sim_check": {s: I[("NULL_TWIN", s)]["sim_check"] for s in seeds},
            "world_meta": {s: I[("NULL_TWIN", s)]["world_meta"] for s in seeds},
        },
        "attempt": attempt,
    }
    with open(os.path.join(HERE, "PILOT.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: res[k] for k in ("positive_meets_success", "cheat_detected",
                                         "null_twin_meets_success", "pilot_pass", "attempt")}))


if __name__ == "__main__":
    main()
