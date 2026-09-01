#!/usr/bin/env python
"""E8 -- does the substrate/operator decomposition survive on SEARCH?
Frozen by FREEZE_E8.txt. The eighth and final experiment."""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import substrates as S      # noqa: E402
import mutators as M        # noqa: E402
import assay as A           # noqa: E402
from run_e3 import two_way_eta2   # noqa: E402  (identical routine E3 used)
from run_e5 import hill_climb     # noqa: E402  (identical harness E5 used)

BUDGET = 800
SEEDS = list(range(9000, 9015))
MODES = ("STRICT", "NEUTRAL-OK")
SUBS = {"CIRCUIT": S.Circuit(), "BYTEVM": S.ByteVM(), "DNF": S.DNF()}
OPS = {"M-UNIFORM": M.UniformSite, "M-UNIFORM2": M.UniformDouble,
       "M-TAILSITE": M.TailSite}


def main():
    e3 = json.loads((HERE / "results" / "e3_decomposition.json")
                    .read_text(encoding="utf-8"))
    out = {"experiment": "E8", "freeze": "FREEZE_E8.txt", "budget_evals": BUDGET,
           "cell_scores": {}, "eta2_search": {}, "comparison": {}}

    for mode in MODES:
        table = {}
        for sname, sub in SUBS.items():
            for oname, ocls in OPS.items():
                t0 = time.time()
                mut = ocls()
                per_seed = []
                for sd in SEEDS:
                    vals = []
                    for tname in A.TARGET_NAMES:
                        r = hill_climb(sub, mut, sd, A.TARGETS[tname],
                                       BUDGET, mode)
                        vals.append(r["norm_improve"])
                    per_seed.append({"norm_improve": float(np.mean(vals)),
                                     "seed": sd})
                table[(sname, oname)] = per_seed
                m = float(np.mean([r["norm_improve"] for r in per_seed]))
                out["cell_scores"][f"{sname}|{oname}||{mode}"] = {
                    "mean_norm_improve": m, "n_seeds": len(per_seed),
                    "seconds": round(time.time() - t0, 1)}
                print(f"{mode:11s} {sname:8s} {oname:12s} improve={m:.4f} "
                      f"({round(time.time()-t0,1)}s)")
        out["eta2_search"][mode] = two_way_eta2(table, "norm_improve")

    # ---- comparison with E3's geometry decomposition on the same cells
    geo_band = e3["eta2"]["q3_band_rate"]
    geo_mm = e3["eta2"]["q4_middle_mass"]
    ranges_search = {}
    for mode in MODES:
        for sname in SUBS:
            vals = [out["cell_scores"][f"{sname}|{o}||{mode}"]["mean_norm_improve"]
                    for o in OPS]
            ranges_search.setdefault(mode, {})[sname] = {
                "min": round(min(vals), 4), "max": round(max(vals), 4),
                "range": round(max(vals) - min(vals), 4),
                "fold": round(max(vals) / min(vals), 2) if min(vals) > 0 else None}

    gates = {}
    for mode in MODES:
        es = out["eta2_search"][mode]
        ratio = (es["eta2_operator"] / geo_band["eta2_operator"]
                 if geo_band["eta2_operator"] > 0 else float("inf"))
        max_range = max(v["range"] for v in ranges_search[mode].values())
        gates[mode] = {
            "eta2_operator_search": round(es["eta2_operator"], 4),
            "eta2_operator_geometry_band": round(geo_band["eta2_operator"], 6),
            "ratio": (round(ratio, 1) if np.isfinite(ratio) else "inf"),
            "E8-G1_dissociation_x10": bool(ratio >= 10),
            "max_within_substrate_operator_range": round(max_range, 4),
            "E8-G2_range_material": bool(max_range > 0.05),
            "KILL_operator_negligible_on_search_too":
                bool(es["eta2_operator"] < 0.01)}
    out["comparison"] = {
        "geometry_eta2_band": geo_band,
        "geometry_eta2_middle_mass": geo_mm,
        "geometry_within_substrate_operator_range_band":
            e3["post_hoc_diagnostic_within_substrate_operator_range"]["ranges"]["q3_band_rate"],
        "search_within_substrate_operator_range": ranges_search,
        "gates": gates}
    any_g1 = any(g["E8-G1_dissociation_x10"] for g in gates.values())
    any_g2 = any(g["E8-G2_range_material"] for g in gates.values())
    all_kill = all(g["KILL_operator_negligible_on_search_too"] for g in gates.values())
    out["verdict"] = ("SUBSTRATE_FRAMING_SURVIVES_BOTH_MEASUREMENTS" if all_kill
                      else "DECOMPOSITION_IS_NOT_MEASUREMENT_INVARIANT"
                      if (any_g1 and any_g2) else "DISSOCIATION_INCONCLUSIVE")

    (HERE / "results" / "e8_search_decomposition.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")

    print("\n--- eta^2 comparison, IDENTICAL crossed 3x3 cells ---")
    print(f"{'measured on':32s} {'substrate':>10s} {'operator':>10s} {'interact':>10s}")
    print(f"{'GEOMETRY band rate (E3)':32s} {geo_band['eta2_substrate']:10.4f} "
          f"{geo_band['eta2_operator']:10.4f} {geo_band['eta2_interaction']:10.4f}")
    print(f"{'GEOMETRY middle mass (E3)':32s} {geo_mm['eta2_substrate']:10.4f} "
          f"{geo_mm['eta2_operator']:10.4f} {geo_mm['eta2_interaction']:10.4f}")
    for mode in MODES:
        es = out["eta2_search"][mode]
        print(f"{'SEARCH ' + mode + ' (E8)':32s} {es['eta2_substrate']:10.4f} "
              f"{es['eta2_operator']:10.4f} {es['eta2_interaction']:10.4f}")
    print("\n--- within-substrate operator RANGE ---")
    for mode in MODES:
        print(f"  search[{mode}]: " + ", ".join(
            f"{k} {v['range']:.4f}" for k, v in ranges_search[mode].items()))
    print("  geometry band: " + ", ".join(
        f"{k} {v['range']:.4f}" for k, v in
        out["comparison"]["geometry_within_substrate_operator_range_band"].items()))
    print("\n--- GATES ---")
    for mode, g in gates.items():
        print(f"  [{mode}] {g}")
    print(f"\nVERDICT: {out['verdict']}")


if __name__ == "__main__":
    main()
