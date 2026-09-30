"""Pilot evaluator -> PILOT.json. Readings: NOTES.md ambiguities 1-4.
Thresholds are the spec's and are never changed."""
import json, os, sys
import numpy as np
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
RATIO_MAX, P_MAX, PC_RED_MIN = 0.85, 0.05, 0.15


def load(path):
    rows = [json.loads(l) for l in open(path)]
    by = {}
    for r in rows:
        by.setdefault(r["arm"], {})[r["seed"]] = r
    return by


def compare(x, ref):
    """x meets 'ratio <= 0.85 and one-sided MWU (x < ref) p < 0.05'."""
    ratio = float(np.mean(x) / np.mean(ref))
    p = float(mannwhitneyu(x, ref, alternative="less").pvalue)
    return dict(mean=float(np.mean(x)), ref_mean=float(np.mean(ref)), ratio=ratio,
                p_one_sided=p, meets=bool(ratio <= RATIO_MAX and p < P_MAX))


def reduction(post, pre):
    return float(1 - np.mean(post) / np.mean(pre))


def evaluate(by):
    seeds = sorted(by["NULL_TWIN"])
    v = lambda arm, key="nrmse_A": np.array([by[arm][s][key] for s in seeds])
    nt = v("NULL_TWIN")
    pc = compare(v("POSITIVE_CONTROL"), nt)
    pc["reduction"] = reduction(v("POSITIVE_CONTROL"), v("POSITIVE_CONTROL", "pre_deposit_nrmse_A"))
    pc["meets"] = bool(pc["meets"] and pc["reduction"] >= PC_RED_MIN)
    pcn = compare(v("PC_NULL_TWIN"), nt)
    pcn["reduction"] = reduction(v("PC_NULL_TWIN"), v("PC_NULL_TWIN", "pre_deposit_nrmse_A"))
    pcn["meets"] = bool(pcn["meets"] and pcn["reduction"] >= PC_RED_MIN)
    ch = compare(v("CHEAT"), nt)
    info_nt_vs_gen0 = compare(nt, v("NULL_TWIN", "gen0_elites_nrmse_A"))
    return dict(
        positive_meets_success=pc["meets"],
        cheat_detected=ch["meets"],
        null_twin_meets_success=pcn["meets"],
        pilot_pass=bool(pc["meets"] and ch["meets"] and not pcn["meets"]),
        stats=dict(n_seeds=len(seeds), positive_control=pc, cheat=ch,
                   null_twin_gen80_deposit=pcn,
                   info_null_twin_gen80_vs_gen0=info_nt_vs_gen0,
                   null_twin_arm_values=nt.tolist(),
                   pc_values=v("POSITIVE_CONTROL").tolist(),
                   pc_null_values=v("PC_NULL_TWIN").tolist()))


def main():
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    path = os.path.join(HERE, "pilot_rows.jsonl" if attempt == 1 else f"pilot_rows_attempt{attempt}.jsonl")
    res = evaluate(load(path))
    res["attempt"] = attempt
    res["rows_file"] = os.path.basename(path)
    out = os.path.join(HERE, "PILOT.json")
    if attempt > 1 and os.path.exists(out):
        prev = json.load(open(out))
        res["previous_attempts"] = prev.get("previous_attempts", []) + [
            {k: prev[k] for k in prev if k != "previous_attempts"}]
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in res if k not in ("stats", "previous_attempts")}))
    s = res["stats"]
    for k in ("positive_control", "cheat", "null_twin_gen80_deposit", "info_null_twin_gen80_vs_gen0"):
        print(k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in s[k].items()})


if __name__ == "__main__":
    main()
