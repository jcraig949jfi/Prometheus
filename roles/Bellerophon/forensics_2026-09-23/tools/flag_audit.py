"""Adjudicate the FAMILY-level high-value flags (REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL, REACHED_INCREMENTAL_NOT_ATOMIC,
RESERVOIR_CROSSED_MOAT) against the null the harness never computed:

  1. reproduce the flag set exactly from runs.jsonl with the frozen predicate (else the audit is not of this data)
  2. the REVERSE flag over the SAME matched pairs (control solved, treatment did not) -- the base-rate null
  3. exposure: runs per side; P(flag | no real difference) when the treatment side simply had more runs
  4. a run-level comparison: per matched pair, solved-run fraction on each side; sign test over discordant pairs,
     and an exposure-matched version that uses only the FIRST run of each side (one experimental unit per side)
  5. criterion comparability: under INCREMENTAL a 'solver' is score_ema >= 0.85 of PARTIAL credit (an output within
     ~19 of the target on average), under ATOMIC it is an exact answer -- the two arms are not measured on one ruler.
Writes receipts/FLAG_AUDIT.json."""
from __future__ import annotations

import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

PAIRS = {
    "REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL": ("reproduction", lambda v: v["reproduction"] in Ld.ENDOGENOUS, "EXTERNAL"),
    "REACHED_INCREMENTAL_NOT_ATOMIC": ("scoring", lambda v: v["scoring"] == "INCREMENTAL", "ATOMIC"),
    "RESERVOIR_CROSSED_MOAT": ("spatial", lambda v: v["spatial"] == "RESERVOIR", "NICHES_ISOLATED"),
}


def solved_run(r) -> bool:
    return (r["summary"].get("solvers_tail") or 0) >= 1


def binom_two_sided(k: int, n: int) -> float:
    if n == 0:
        return 1.0
    pk = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    obs = pk[k]
    return min(1.0, sum(p for p in pk if p <= obs + 1e-15))


def main() -> None:
    R = Ld.runs(); F = Ld.families(); FL = Ld.flags()
    by_fam = collections.defaultdict(list)
    for r in R:
        by_fam[r["family"]].append(r)
    vkey = {json.dumps(F[f]["vec"], sort_keys=True): f for f in F}
    out = {}
    for name, (axis, is_treat, ctrl_level) in PAIRS.items():
        stored = {(f["family"], f["control_family"]) for f in FL if f["flag"] == name}
        fwd = set(); rev = set(); pairs = []
        for f, fam in F.items():
            v = fam["vec"]
            if not is_treat(v):
                continue
            g = vkey.get(json.dumps(dict(v, **{axis: ctrl_level}), sort_keys=True))
            if not g or not by_fam.get(g) or not by_fam.get(f):
                continue
            ts, cs = by_fam[f], by_fam[g]
            t_any, c_any = any(map(solved_run, ts)), any(map(solved_run, cs))
            pairs.append({"t": f, "c": g, "nt": len(ts), "nc": len(cs), "st": sum(map(solved_run, ts)), "sc": sum(map(solved_run, cs)),
                          "t_first": solved_run(min(ts, key=lambda r: r["_no"])), "c_first": solved_run(min(cs, key=lambda r: r["_no"])),
                          "init": v["init"], "task": v["task"], "scoring": v["scoring"], "repro": v["reproduction"]})
            if t_any and not c_any:
                fwd.add((f, g))
            if c_any and not t_any:
                rev.add((f, g))
        # exposure asymmetry among forward flags
        fl_pairs = [p for p in pairs if (p["t"], p["c"]) in fwd]
        more_t = sum(1 for p in fl_pairs if p["nt"] > p["nc"]); more_c = sum(1 for p in fl_pairs if p["nc"] > p["nt"])
        # exposure-matched: first run of each side only
        d_t = sum(1 for p in pairs if p["t_first"] and not p["c_first"]); d_c = sum(1 for p in pairs if p["c_first"] and not p["t_first"])
        # run-level pooled rates (runs are NOT independent within a family; reported for orientation only)
        rt = sum(p["st"] for p in pairs) / max(1, sum(p["nt"] for p in pairs)); rc = sum(p["sc"] for p in pairs) / max(1, sum(p["nc"] for p in pairs))
        strata = {}
        for key in ("init", "task", "scoring", "repro"):
            s = collections.defaultdict(lambda: [0, 0, 0])
            for p in pairs:
                s[p[key]][0] += 1
                s[p[key]][1] += int(p["t_first"] and not p["c_first"])
                s[p[key]][2] += int(p["c_first"] and not p["t_first"])
            strata[key] = {k: {"pairs": a, "treat_only_first_run": b, "control_only_first_run": c} for k, (a, b, c) in sorted(s.items())}
        out[name] = {
            "matched_pairs_with_runs_both_sides": len(pairs),
            "forward_recomputed": len(fwd), "forward_stored": len(stored), "recompute_equals_stored": fwd == stored,
            "reverse_same_pairs": len(rev),
            "forward_flags_where_treatment_had_more_runs": more_t, "forward_flags_where_control_had_more_runs": more_c,
            "forward_flags_equal_runs": len(fl_pairs) - more_t - more_c,
            "exposure_matched_first_run": {"treat_only": d_t, "control_only": d_c, "sign_test_p": binom_two_sided(d_t, d_t + d_c)},
            "pooled_run_solve_rate": {"treatment": round(rt, 4), "control": round(rc, 4)},
            "strata_first_run": strata,
        }
    # criterion comparability for INCREMENTAL: how many INCREMENTAL 'solver' runs had an EXACT best score of 1.0?
    inc = [r for r in R if r["vec"]["scoring"] == "INCREMENTAL" and solved_run(r)]
    out["incremental_solver_criterion"] = {"incremental_runs_with_solvers": len(inc),
                                           "of_which_best_score_tail_eq_1": sum(1 for r in inc if (r["summary"].get("best_score_tail") or 0) >= 0.999),
                                           "note": "INCREMENTAL score = 1 - d/128 per output; score_ema >= 0.85 does not require an exact answer"}
    p = Ld.write("FLAG_AUDIT.json", out)
    print(p)
    for k, v in out.items():
        print(k, json.dumps({kk: vv for kk, vv in v.items() if kk != "strata_first_run"}))


if __name__ == "__main__":
    main()
