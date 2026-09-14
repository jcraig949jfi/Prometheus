"""ABK 1996 Table 1 reproduction under the paper's own convention (R1-R3).

N = 149, iid Bernoulli(0.5), n = 10000, horizon 600, at_T; z = 2.498
(Bonferroni over 4 cells). Sensitivity arm at horizon 298. See PROTOCOL.md.

    python herakles/specimens/spec-andre-bennett-koza-1996/derived/run_reproduction.py
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
from herakles.workspace import assert_not_canonical      # noqa: E402
from herakles import evca                                # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = os.path.join(HERE, "abk_1996_rule_tables.json")
OUT = os.path.join(HERE, "reproduction_results.json")

N_CELLS, N_ICS, HORIZON, SENS_HORIZON = 149, 10000, 600, 298
BASE_SEED = 20260911 + 2000
RULES = ("gkl", "davis1995", "das1995", "abk_gp")
Z = 2.498


def main():
    ws = assert_not_canonical("run the ABK 1996 reproduction")
    t0 = time.time()
    tab = json.load(open(TABLES, encoding="utf-8"))
    assert tab["gkl_calibration"] is True
    out = {"protocol": "herakles/specimens/spec-andre-bennett-koza-1996/PROTOCOL.md",
           "workspace": ws, "z": Z, "primary": [], "sensitivity": []}
    for ri, name in enumerate(RULES):
        t = tab["tables"][name]
        table = evca.decode_table(t["hex"])
        ics = evca.make_ics(N_ICS, N_CELLS, BASE_SEED + ri)
        pub = float(t["published"]["acc"])
        rows = {}
        for label, steps in (("primary", HORIZON), ("sensitivity", SENS_HORIZON)):
            r = evca.classify(table, ics, steps, witness_limit=evca.WITNESS_LIMIT)
            p = r["accuracy"]
            se = math.sqrt(p * (1 - p) / N_ICS)
            row = {"rule": name, "n_cells": N_CELLS, "n_ics": N_ICS,
                   "steps": steps, "seed": BASE_SEED + ri, "published": pub,
                   "published_cases": t["published"]["cases"],
                   "measured": p, "n_correct": r["n_correct"], "se": se,
                   "diff": p - pub, "band_half_width": Z * se,
                   "abs_diff_in_se": abs(p - pub) / se if se > 0 else None,
                   "correct_mask_digest": r["correct_mask_digest"]}
            if label == "primary":
                row["decision"] = "REPRODUCED" if abs(p - pub) <= Z * se \
                    else "DISCREPANT"
            rows[label] = row
            out[label].append(row)
        rows["sensitivity"]["delta_vs_600"] = \
            rows["sensitivity"]["measured"] - rows["primary"]["measured"]
        rows["sensitivity"]["within_0_01"] = \
            abs(rows["sensitivity"]["delta_vs_600"]) <= 0.01
        print("%-10s 600: %.4f (pub %.5f, %.2f SE) %s | 298: %.4f delta %+.4f"
              % (name, rows["primary"]["measured"], pub,
                 rows["primary"]["abs_diff_in_se"], rows["primary"]["decision"],
                 rows["sensitivity"]["measured"],
                 rows["sensitivity"]["delta_vs_600"]), flush=True)
        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=1)
    n_rep = sum(1 for r in out["primary"] if r["decision"] == "REPRODUCED")
    out["R1"] = {"reproduced": n_rep, "of": 4, "holds": n_rep >= 3}
    out["R2"] = {"note": "ranking not tested by preregistration; gaps below 1 SE",
                 "observed_order_600": [r["rule"] for r in sorted(
                     out["primary"], key=lambda r: -r["measured"])]}
    out["R3"] = {"holds": all(r["within_0_01"] for r in out["sensitivity"]),
                 "deltas": {r["rule"]: r["delta_vs_600"] for r in out["sensitivity"]}}
    out["elapsed_s"] = round(time.time() - t0, 1)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print("R1", out["R1"], "R3", out["R3"], "%.0fs" % out["elapsed_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
