#!/usr/bin/env python
"""E1 -- assay qualification and calibration. Frozen by FREEZE_E1.txt.

Run: PYTHONPATH=genesis/harmonia_b python genesis/harmonia_b/run_e1.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import substrates as S      # noqa: E402
import assay as A           # noqa: E402

SEEDS = range(1000, 1060)          # disjoint from the bootstrap's 1000-block? no --
# bootstrap used seed0=1000 for sweep_profile with 6 objects (1000..1005) and
# 2000/3000 blocks elsewhere. E1 therefore uses a DISJOINT block, 5000..5059,
# so that no E1 object was ever seen in the bootstrap.
SEEDS = range(5000, 5060)

A_PUBLISHED_CIRCUIT_LOCAL = 0.119   # Harmonia A Gen-0, published


def main():
    cells = [
        ("CIRCUIT", S.Circuit(), None, None),
        ("P1-BLOCKS", S.BlocksPositive(), None, None),
        ("N1-SMOOTH-UNREACHABLE", S.SmoothUnreachable(), None, None),
        ("N2-HASH", S.HashSubstrate(), None, 8),
    ]
    out = {"experiment": "E1", "freeze": "FREEZE_E1.txt",
           "seeds": [SEEDS.start, SEEDS.stop], "cells": {}}
    for name, sub, op, cap in cells:
        t0 = time.time()
        Q, per_t, raw = A.measure_cell(sub, operator=op, seeds=SEEDS,
                                       cap_per_site=cap, seed_key=5001)
        raw["seconds"] = round(time.time() - t0, 1)
        out["cells"][name] = {"Q": Q, "per_target": per_t, "raw": raw}
        print(f"{name:24s} n_edits={raw['n_edits']:7d} "
              f"q1={Q['q1_neutral_rate']:.4f} q3={Q['q3_band_rate']:.4f} "
              f"q4={Q['q4_middle_mass']:.4f} q5={Q['q5_median_nonzero_d']} "
              f"({raw['seconds']}s)")

    q = {k: out["cells"][k]["Q"] for k in out["cells"]}
    pt = {k: out["cells"][k]["per_target"] for k in out["cells"]}

    c1_val = abs(q["CIRCUIT"]["q4_middle_mass"] - A_PUBLISHED_CIRCUIT_LOCAL)
    c2_val = abs(q["P1-BLOCKS"]["q3_band_rate"] - q["N2-HASH"]["q3_band_rate"])
    c3_val = (pt["P1-BLOCKS"]["T9_P1_TARGET"]["q10_reach_improve_at1"]
              - pt["N1-SMOOTH-UNREACHABLE"]["T10_N1_TARGET"]["q10_reach_improve_at1"])
    c4a = abs(q["P1-BLOCKS"]["q3_band_rate"] - q["N1-SMOOTH-UNREACHABLE"]["q3_band_rate"])
    c4b = abs(q["P1-BLOCKS"]["q4_middle_mass"] - q["N1-SMOOTH-UNREACHABLE"]["q4_middle_mass"])
    c4c = abs(q["P1-BLOCKS"]["q5_median_nonzero_d"]
              - q["N1-SMOOTH-UNREACHABLE"]["q5_median_nonzero_d"])
    m5_val = abs(pt["P1-BLOCKS"]["T9_P1_TARGET"]["q10_reach_improve_at1"]
                 - pt["N2-HASH"]["T9_P1_TARGET"]["q10_reach_improve_at1"])

    gates = {
        "E1-C1_calibration": {"value": round(c1_val, 4), "bar": "<= 0.03",
                              "pass": bool(c1_val <= 0.03),
                              "measured_q4": q["CIRCUIT"]["q4_middle_mass"],
                              "A_published": A_PUBLISHED_CIRCUIT_LOCAL},
        "E1-C2_geometry_separates_P1_N2": {"value": round(c2_val, 4),
                                           "bar": ">= 0.50",
                                           "pass": bool(c2_val >= 0.50)},
        "E1-C3_target_separates_P1_N1": {"value": round(c3_val, 4),
                                         "bar": ">= 0.50",
                                         "pass": bool(c3_val >= 0.50)},
        "E1-C4_geometry_blind_to_P1_N1": {
            "q3_diff": round(c4a, 4), "q4_diff": round(c4b, 4),
            "q5_diff": round(c4c, 4), "bar": "each <= 0.02",
            "pass": bool(c4a <= 0.02 and c4b <= 0.02 and c4c <= 0.02)},
    }
    measured = {
        "E1-M5_single_step_cannot_separate_P1_N2": {
            "value": round(m5_val, 4), "expectation": "<= 0.20 (NOT GATED)",
            "as_expected": bool(m5_val <= 0.20),
            "q10_P1_on_T9": pt["P1-BLOCKS"]["T9_P1_TARGET"]["q10_reach_improve_at1"],
            "q10_N2_on_T9": pt["N2-HASH"]["T9_P1_TARGET"]["q10_reach_improve_at1"]},
    }
    all_pass = all(g["pass"] for g in gates.values())
    out["gates"] = gates
    out["measured_not_gated"] = measured
    out["verdict"] = "ASSAY_QUALIFIED" if all_pass else "ASSAY_UNQUALIFIED"

    (HERE / "results").mkdir(exist_ok=True)
    p = HERE / "results" / "e1_results.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("\n--- GATES ---")
    for k, v in gates.items():
        print(f"  {k:38s} {'PASS' if v['pass'] else 'FAIL'}  {v}")
    print("--- MEASURED, NOT GATED ---")
    for k, v in measured.items():
        print(f"  {k:38s} {v}")
    print(f"\nVERDICT: {out['verdict']}")
    print(f"wrote {p}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
