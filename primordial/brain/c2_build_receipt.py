"""Score the C2 record run against the pre-run hypothesis (bus 1789388174038-0).

Copies the record rows to primordial/ledger/rows/C/ and writes a summary with one
verdict per prediction. Thresholds below are the posted ones, verbatim.

usage: python -m primordial.brain.c2_build_receipt <record.jsonl>
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

from primordial.brain.c2_plastic_rank import EXP_ID

ROWS = pathlib.Path(__file__).resolve().parents[1] / "ledger" / "rows" / "C"


def main(argv):
    src = pathlib.Path(argv[0])
    rows = [json.loads(line) for line in open(src, encoding="utf-8")]
    runs = {(r["seed"], r["world"], r["brain"]): r for r in rows if r["kind"] == "run"}
    seeds = sorted({k[0] for k in runs})
    sc = lambda s, w, b: runs[(s, w, b)]["score_flag_shifted"]

    # (1) REAL world, plastic
    cells = [abs(m - o) <= 1 for s in seeds
             for m, o in zip(sc(s, "real", "plastic")["steady_max_rank"], runs[(s, "real", "plastic")]["oracle"])]
    p1 = {"within1_frac": sum(cells) / len(cells),
          "rho_oracle_per_seed": [sc(s, "real", "plastic")["rho_oracle"] for s in seeds],
          "switch_response_per_seed": [sc(s, "real", "plastic")["switch_response"] for s in seeds],
          "false_surprises_per_seed": [sc(s, "real", "plastic")["false_surprises"] for s in seeds]}
    p1["held"] = (p1["within1_frac"] >= 0.9 and all((x or 0) >= 0.9 for x in p1["rho_oracle_per_seed"])
                  and all(x >= 0.9 for x in p1["switch_response_per_seed"])
                  and all(x <= 2 for x in p1["false_surprises_per_seed"]))

    # (2) SOFT world, plastic
    cells2 = [abs(m - o) <= 1 for s in seeds
              for m, o in zip(sc(s, "soft", "plastic")["steady_max_rank"], runs[(s, "soft", "plastic")]["oracle"])]
    below = [m < o for s in seeds
             for m, o in zip(sc(s, "soft", "plastic")["steady_max_rank"], runs[(s, "soft", "plastic")]["oracle"])]
    p2 = {"rho_oracle_per_seed": [sc(s, "soft", "plastic")["rho_oracle"] for s in seeds],
          "within1_frac": sum(cells2) / len(cells2), "below_oracle_frac": sum(below) / len(below)}
    p2["held"] = all((x or 0) >= 0.8 for x in p2["rho_oracle_per_seed"]) and p2["within1_frac"] <= 0.5

    # (3) memory at parity (REAL)
    par = []
    for s in seeds:
        pp, p8, p2b = (runs[(s, "real", b)] for b in ("plastic", "fixed8", "fixed2"))
        par.append({"seed": s,
                    "params_ratio_plastic_over_fixed8": pp["steady_params_mean"] / p8["steady_params_mean"],
                    "excess_plastic": pp["score_flag_shifted"]["steady_excess_mse_mean"],
                    "excess_fixed8": p8["score_flag_shifted"]["steady_excess_mse_mean"],
                    "excess_fixed2": p2b["score_flag_shifted"]["steady_excess_mse_mean"]})
    p3 = {"per_seed": par, "held": all(
        x["params_ratio_plastic_over_fixed8"] <= 0.5 and x["excess_plastic"] <= x["excess_fixed8"] + 0.01
        and x["excess_fixed2"] >= 5 * max(x["excess_plastic"], 1e-12) for x in par)}

    # (4) NULL
    p4 = {"spread_per_seed": [sc(s, "null", "plastic")["steady_rank_spread"] for s in seeds],
          "rho_label_per_seed": [sc(s, "null", "plastic")["rho_label"] for s in seeds]}
    p4["held"] = all(x <= 1.0 for x in p4["spread_per_seed"])

    # (5) LEAK probe
    leak = [runs[k]["probe"] for k in runs if k[2] == "leak_flag"]
    honest = [(k, runs[k]["probe"], runs[k]["deterministic"]) for k in runs if k[2] != "leak_flag"]
    rho_gap = [abs((sc(s, "real", "leak_flag")["rho_oracle"] or 0) - (sc(s, "real", "plastic")["rho_oracle"] or 0))
               for s in seeds]
    p5 = {"leak_flagged": f"{leak.count('LEAK')}/{len(leak)}",
          "honest_clean": f"{sum(p == 'CLEAN' for _, p, _ in honest)}/{len(honest)}",
          "honest_deterministic": f"{sum(d for _, _, d in honest)}/{len(honest)}",
          "tracking_rho_gap_leak_vs_plastic_real": rho_gap}
    p5["held"] = (leak.count("LEAK") == len(leak) and all(p == "CLEAN" and d for _, p, d in honest)
                  and all(g <= 0.1 for g in rho_gap))
    probe_worked = leak.count("LEAK") == len(leak) and all(p == "CLEAN" and d for _, p, d in honest)

    status = "KILL" if not p1["held"] else ("PASS" if (p4["held"] and probe_worked) else "FAIL")
    summary = {"exp_id": EXP_ID, "source": src.name, "git": rows[0]["git"], "seeds": seeds,
               "p1_real_tracking": p1, "p2_soft_below_oracle": p2, "p3_memory_parity": p3,
               "p4_null": p4, "p5_leak_probe": p5, "probe_worked": probe_worked,
               "status_by_posted_rule": status}
    ROWS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, ROWS / f"{EXP_ID}.jsonl")
    with open(ROWS / f"{EXP_ID}.summary.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
