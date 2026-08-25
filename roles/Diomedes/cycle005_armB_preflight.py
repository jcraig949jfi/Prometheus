"""Diomedes cycle 005 Arm B — PRE-FLIGHT (structural properties only, no outcome measured).

Standing rule adopted 2026-08-25 (BOOTSTRAP S6): measure the properties a design depends
on BEFORE writing the design down. Arm A was wasted by skipping this.

Measures, and nothing else:
  (a) RELATION INVENTORY     - which thresholds / moduli actually occur -> T2/T3 liveness
  (b) CELL INVENTORY         - cells, ordered cell pairs, sizes at MIN_CELL=150
  (c) INVARIANT SCALE SPREAD - do companion invariants differ in scale across cells?
                               -> T4 liveness (its whole premise)
No AUC is computed here. No model is fit. Nothing about the OUTCOME is observed.

    python roles/Diomedes/cycle005_armB_preflight.py
"""
import collections
import json
import pathlib
import random

import numpy as np

import cycle001_run as R
import cycle002_run as C2
import cycle003_run as C3
from harvest_cache import load_verified

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "cycle005_armB_preflight.json"
MIN_CELL = 150          # frozen by cycle 004
SEEDS = C2.SEEDS


def main():
    values, parents, osee, obrk, ocel, orel = load_verified()
    inv_cat, by_cat, sortedvals = C2.build(values, R.RELATIONS)
    FEATS, CARRY = [], ["B1_break_rate", "B2_freq", "n_cells", "n_rels"]
    for i in range(C2.N_COMPANIONS):
        FEATS += [f"delta_{i}", f"absdelta_{i}", f"parity_match_{i}",
                  f"absdiff_target_{i}", f"absdiff_le3_{i}", f"rank_delta_{i}"]

    # ---------- (a) relation inventory ----------
    rels = sorted(R.RELATIONS)
    thresholds, moduli = {}, {}
    for r in rels:
        if r.startswith("abs_diff_le_"):
            thresholds[r] = int(r.rsplit("_", 1)[1])
        if r.startswith("equal_mod_"):
            moduli[r] = int(r.rsplit("_", 1)[1])
    rel_inv = {
        "relations": rels,
        "thresholds_present": thresholds,
        "moduli_present": moduli,
        "n_distinct_thresholds": len(set(thresholds.values())),
        "n_distinct_moduli": len(set(moduli.values())),
    }

    # ---------- (b) + (c) per seed ----------
    per_seed = []
    for seed in SEEDS:
        rng = random.Random(seed)
        states = C3.C2_states(values, parents, osee, obrk, ocel, orel,
                              inv_cat, by_cat, sortedvals, rng, FEATS, CARRY)
        cell = collections.defaultdict(list)
        for s in states:
            cell[(s["key"], s["rel"])].append(s)

        pairs = collections.defaultdict(set)
        for (k, rel), ss in cell.items():
            if len(ss) >= MIN_CELL:
                pairs[k].add(rel)
        mixed = sorted([k for k, rs in pairs.items() if len(rs) >= 2])
        usable = [(k, r) for k in mixed for r in rels if len(cell.get((k, r), [])) >= MIN_CELL]

        # (c) scale of the raw-unit features, per cell, per companion slot
        scale = {}
        for c in usable:
            rows = [f for s in cell[c] for f in s["F"]]
            d = {}
            for i in range(C2.N_COMPANIONS):
                v = np.array([f[f"absdiff_target_{i}"] for f in rows], dtype=float)
                w = np.array([f[f"absdelta_{i}"] for f in rows], dtype=float)
                d[f"comp{i}"] = {
                    "median_absdiff_target": round(float(np.median(v)), 3),
                    "p95_absdiff_target": round(float(np.percentile(v, 95)), 3),
                    "median_absdelta": round(float(np.median(w)), 3),
                    "frac_absdiff_le3": round(float(np.mean(v <= 3)), 4),
                }
            scale[f"{c[0][0]}|{c[0][1]}|{c[1]}"] = d

        ratios = {}
        for i in range(C2.N_COMPANIONS):
            meds = [v[f"comp{i}"]["median_absdiff_target"] for v in scale.values()]
            nz = [m for m in meds if m > 0]
            ratios[f"comp{i}"] = {
                "n_cells": len(meds),
                "n_cells_nonzero_median": len(nz),
                "min_median": round(min(meds), 3) if meds else None,
                "max_median": round(max(meds), 3) if meds else None,
                "max_over_min_nonzero": round(max(nz) / min(nz), 2) if len(nz) >= 2 else None,
            }

        per_seed.append({
            "seed": seed,
            "n_states": len(states),
            "n_mixed_pairs": len(mixed),
            "n_usable_cells": len(usable),
            "n_ordered_cell_pairs": len(usable) * (len(usable) - 1),
            "cell_sizes": {f"{c[0][0]}|{c[0][1]}|{c[1]}": len(cell[c]) for c in usable},
            "scale_ratio_across_cells": ratios,
            "per_cell_scale": scale if seed == SEEDS[0] else "omitted (seed 0 only)",
        })

    live = {
        "T0_identity": "LIVE (definitional anchor)",
        "T1_sign_flip": "LIVE but analytically bounded: AUC -> 1-AUC exactly",
        "T2_threshold_norm": (
            "DEGENERATE-WITHIN-RELATION / LIVE-ACROSS-RELATION: exactly one threshold "
            f"({thresholds}) occurs, so T2 is the identity between two abs_diff_le_3 cells "
            "and a constant relative rescale only between abs_diff_le_3 and equal_mod_2 cells"),
        "T3_modulus_align": (
            f"DEGENERATE: exactly one modulus ({moduli}) occurs and abs_diff_le_3 has none, "
            "so (u-t) mod m == (u-t) mod 2 everywhere; T3 is the identity map on this "
            "population and must equal T0 to the last digit"),
        "T4_quantile_std": "LIVE (see scale_ratio_across_cells)",
        "T5_T2_after_T4": "LIVE iff T2 is (across-relation pairs only)",
    }

    rep = {"purpose": "Arm B structural pre-flight; NO outcome measured",
           "prereg": "CYCLE_005_PREREG_terminal.md S3",
           "population_digest_required": "1b4abb1a36a9cfb53d6a4bfb8c08a0623e28a88ba996556532d80e71d889af52",
           "relation_inventory": rel_inv,
           "transport_liveness": live,
           "per_seed": per_seed}
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rel_inv, indent=1))
    for k, v in live.items():
        print(f"  {k:22s} {v}")
    for p in per_seed:
        print(f"seed {p['seed']}: states={p['n_states']} mixed_pairs={p['n_mixed_pairs']} "
              f"cells={p['n_usable_cells']} ordered_pairs={p['n_ordered_cell_pairs']}")
        print("   scale ratios:", json.dumps(p["scale_ratio_across_cells"]))
    print("->", OUT)


if __name__ == "__main__":
    main()
