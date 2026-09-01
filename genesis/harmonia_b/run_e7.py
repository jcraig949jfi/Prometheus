#!/usr/bin/env python
"""E7 -- prospective cheapness. Frozen by FREEZE_E7.txt. Nothing gated."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import substrates as S      # noqa: E402
import mutators as M        # noqa: E402
import assay as A           # noqa: E402
import run_e6 as E6         # noqa: E402

SEEDS = list(range(5000, 5060))
KS = [10, 25, 50, 100, 200, 400]
SEARCH_COST = 800 * 10 * 15

CELLS = {
    "CIRCUIT|M-UNIFORM": (S.Circuit(), M.UniformSite()),
    "CIRCUIT|M-OPONLY": (S.Circuit(), M.OpOnly()),
    "CIRCUIT|M-WIREONLY": (S.Circuit(), M.WireOnly()),
    "BYTEVM|M-RAWBYTE": (S.ByteVM(), M.RawByte()),
    "BYTEVM|M-INSTR": (S.ByteVM(), M.InstructionAware()),
    "DNF|M-UNIFORM": (S.DNF(), M.UniformSite()),
    "RELAX[tau=0.1]|M-GAUSS[1.0]": (S.RelaxedCircuit(tau=0.1), M.GaussianStep(1.0)),
    "RELAX[tau=0.5]|M-GAUSS[1.0]": (S.RelaxedCircuit(tau=0.5), M.GaussianStep(1.0)),
    "RELAX[tau=2.0]|M-GAUSS[4.0]": (S.RelaxedCircuit(tau=2.0), M.GaussianStep(4.0)),
}
E5 = json.loads((HERE / "results" / "e5_search.json").read_text(encoding="utf-8"))


def outcome(mode):
    return {c: E5["cell_scores"][f"{c}||{mode}"]["mean_norm_improve"] for c in CELLS}


def main():
    out = {"experiment": "E7", "freeze": "FREEZE_E7.txt",
           "search_cost_evals_per_cell": SEARCH_COST, "by_k": {}, "summary": {}}
    est = {k: {} for k in KS}
    for cname, (sub, mut) in CELLS.items():
        for k in KS:
            t0 = time.time()
            Q, _pt, raw = A.measure_cell(sub, operator=mut, seeds=SEEDS,
                                         n_draws=k, seed_key=8000 + k)
            est[k][cname] = {"q10": Q["q10_reach_improve_at1"],
                             "q4": Q["q4_middle_mass"],
                             "q3": Q["q3_band_rate"],
                             "n_edits": raw["n_edits"],
                             "seconds": round(time.time() - t0, 2)}
        print(f"  {cname:30s} done")

    for mode in ("STRICT", "NEUTRAL-OK"):
        oc = outcome(mode)
        cells = list(CELLS)
        full = [est[400][c]["q10"] for c in cells]
        rows = {}
        for k in KS:
            v = [est[k][c]["q10"] for c in cells]
            cost = 60 * k
            rows[k] = {
                "assay_cost_evals_per_cell": cost,
                "cost_ratio_vs_search": round(cost / SEARCH_COST, 5),
                "stability_rho_vs_k400": round(E6.spear(v, full), 4),
                "predictive_rho_q10_vs_outcome": round(
                    E6.spear(v, [oc[c] for c in cells]), 4),
                "predictive_rho_q4_vs_outcome": round(
                    E6.spear([est[k][c]["q4"] for c in cells],
                             [oc[c] for c in cells]), 4)}
        out["by_k"][mode] = rows
        stable = [k for k in KS if rows[k]["stability_rho_vs_k400"] >= 0.95]
        km = min(stable) if stable else None
        out["summary"][mode] = {
            "E7-M1_smallest_k_stable": km,
            "E7-M2_predictive_at_that_k": rows[km]["predictive_rho_q10_vs_outcome"] if km else None,
            "predictive_at_k400": rows[400]["predictive_rho_q10_vs_outcome"],
            "E7-M3_cost_ratio_at_that_k": rows[km]["cost_ratio_vs_search"] if km else None}
        print(f"\n=== {mode} ===")
        print(f"{'k':>5s} {'assay_evals':>12s} {'cost_ratio':>11s} {'stability':>10s} "
              f"{'pred_q10':>9s} {'pred_q4':>8s}")
        for k in KS:
            r = rows[k]
            print(f"{k:5d} {r['assay_cost_evals_per_cell']:12d} "
                  f"{r['cost_ratio_vs_search']:11.5f} {r['stability_rho_vs_k400']:10.3f} "
                  f"{r['predictive_rho_q10_vs_outcome']:9.3f} "
                  f"{r['predictive_rho_q4_vs_outcome']:8.3f}")
        print(f"  M1 smallest stable k = {km}  "
              f"M3 cost ratio = {out['summary'][mode]['E7-M3_cost_ratio_at_that_k']}")

    out["estimates"] = {str(k): est[k] for k in KS}
    (HERE / "results" / "e7_cheapness.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print("\nwrote results/e7_cheapness.json")


if __name__ == "__main__":
    main()
