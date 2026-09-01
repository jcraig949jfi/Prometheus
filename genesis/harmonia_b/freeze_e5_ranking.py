#!/usr/bin/env python
"""Writes the FROZEN PRE-SEARCH RANKING from E2's table. Run BEFORE any search."""
import json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
e2 = json.loads((HERE/"results"/"e2_arena.json").read_text(encoding="utf-8"))
cells = {f"{c['substrate']}|{c['operator']}": c for c in e2["cells"]}
SEARCH_CELLS = [
    "CIRCUIT|M-UNIFORM", "CIRCUIT|M-OPONLY", "CIRCUIT|M-WIREONLY",
    "BYTEVM|M-RAWBYTE", "BYTEVM|M-INSTR", "DNF|M-UNIFORM",
    "RELAX[tau=0.1]|M-GAUSS[1.0]", "RELAX[tau=0.5]|M-GAUSS[1.0]",
    "RELAX[tau=2.0]|M-GAUSS[4.0]",
    "P1-BLOCKS|SWEEP-ALL", "N1-SMOOTH-UNREACHABLE|SWEEP-ALL", "N2-HASH|SWEEP-ALL",
]
REAL = SEARCH_CELLS[:9]
rank = []
for k in SEARCH_CELLS:
    Q = cells[k]["Q"]
    rank.append({"cell": k, "is_control": k not in REAL,
                 "q10_reach_improve_at1": Q["q10_reach_improve_at1"],
                 "q4_middle_mass": Q["q4_middle_mass"],
                 "q3_band_rate": Q["q3_band_rate"],
                 "q1_neutral_rate": Q["q1_neutral_rate"],
                 "q2_destruction_rate": Q["q2_destruction_rate"],
                 "q11_drift": Q["q11_drift"],
                 "q13_baseline_d": Q["q13_baseline_d"]})
rank.sort(key=lambda r: -r["q10_reach_improve_at1"])
for i, r in enumerate(rank): r["predicted_rank_by_q10"] = i + 1
out = {"note": "FROZEN PRE-SEARCH PREDICTION. Written and journaled before any search ran.",
       "prediction": "PC-4: this q10 ordering correlates with compute-matched search improvement at Spearman rho >= 0.70.",
       "search_cells": SEARCH_CELLS, "real_substrate_cells": REAL, "ranking": rank}
p = HERE/"results"/"e5_frozen_ranking.json"
p.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"{'rank':>4s}  {'cell':32s} {'q10':>6s} {'q4':>6s} {'q3':>6s}")
for r in rank:
    print(f"{r['predicted_rank_by_q10']:4d}  {r['cell']:32s} "
          f"{r['q10_reach_improve_at1']:.3f} {r['q4_middle_mass']:6.3f} {r['q3_band_rate']:6.3f}"
          + ("   [control]" if r["is_control"] else ""))
print(f"\nwrote {p}")
