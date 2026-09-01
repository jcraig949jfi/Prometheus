#!/usr/bin/env python
"""E2 -- arena characterisation. Frozen by FREEZE_E2.txt. Descriptive only."""
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

SEEDS = range(5000, 5060)
N_DRAWS = 400


def cells():
    circ = S.Circuit()
    vm = S.ByteVM()
    dnf = S.DNF()
    out = [
        ("CIRCUIT", "SWEEP-ALL", circ, None, None),
        ("CIRCUIT", "M-UNIFORM", circ, M.UniformSite(), None),
        ("CIRCUIT", "M-OPONLY", circ, M.OpOnly(), None),
        ("CIRCUIT", "M-WIREONLY", circ, M.WireOnly(), None),
        ("BYTEVM", "SWEEP-ALL", vm, None, 16),
        ("BYTEVM", "M-UNIFORM", vm, M.UniformSite(), None),
        ("BYTEVM", "M-RAWBYTE", vm, M.RawByte(), None),
        ("BYTEVM", "M-INSTR", vm, M.InstructionAware(), None),
        ("DNF", "SWEEP-ALL", dnf, None, None),
        ("DNF", "M-UNIFORM", dnf, M.UniformSite(), None),
    ]
    for tau in (0.1, 0.5, 2.0):
        sub = S.RelaxedCircuit(tau=tau)
        for sigma in (0.25, 1.0, 4.0):
            out.append((f"RELAX[tau={tau}]", f"M-GAUSS[{sigma}]", sub,
                        M.GaussianStep(sigma), None))
    out += [
        ("P1-BLOCKS", "SWEEP-ALL", S.BlocksPositive(), None, None),
        ("N1-SMOOTH-UNREACHABLE", "SWEEP-ALL", S.SmoothUnreachable(), None, None),
        ("N2-HASH", "SWEEP-ALL", S.HashSubstrate(), None, 8),
    ]
    return out


def main():
    out = {"experiment": "E2", "freeze": "FREEZE_E2.txt",
           "seeds": [SEEDS.start, SEEDS.stop], "n_draws_operator": N_DRAWS,
           "cells": [], "gates": {}}
    unmeasurable = []
    for sname, oname, sub, op, cap in cells():
        t0 = time.time()
        try:
            Q, per_t, raw = A.measure_cell(
                sub, operator=op, seeds=SEEDS, cap_per_site=cap,
                n_draws=N_DRAWS, seed_key=5002)
        except Exception as e:
            unmeasurable.append({"substrate": sname, "operator": oname,
                                 "reason": f"{type(e).__name__}: {e}"})
            print(f"  UNMEASURABLE {sname} x {oname}: {e}")
            continue
        raw["seconds"] = round(time.time() - t0, 1)
        row = {"substrate": sname, "operator": oname,
               "Q": Q, "per_target": per_t, "raw": raw}
        out["cells"].append(row)
        print(f"{sname:22s} {oname:14s} n={raw['n_edits']:6d} dec={raw['n_declines']:5d} "
              f"q1={Q['q1_neutral_rate']:.3f} q2={Q['q2_destruction_rate']:.3f} "
              f"q3={Q['q3_band_rate']:.3f} q4={Q['q4_middle_mass']:.3f} "
              f"q5={str(Q['q5_median_nonzero_d'])[:6]:6s} "
              f"q10={Q['q10_reach_improve_at1']:.3f} q11={Q['q11_drift']:+.3f} "
              f"q12={'null' if Q['q12_neutral_option_gain'] is None else round(Q['q12_neutral_option_gain'],3)} "
              f"({raw['seconds']}s)")

    g1 = [c for c in out["cells"] if c["raw"]["n_edits"] < 1000]
    relax = [c for c in out["cells"] if c["substrate"].startswith("RELAX")]
    out["gates"] = {
        "E2-G1_all_cells_measurable": {
            "pass": len(unmeasurable) == 0,
            "unmeasurable": unmeasurable,
            "cells_under_1000_edits": [(c["substrate"], c["operator"],
                                        c["raw"]["n_edits"]) for c in g1]},
        "E2-G2_declines_counted": {
            "pass": True,
            "by_cell": {f"{c['substrate']}|{c['operator']}": c["raw"]["n_declines"]
                        for c in out["cells"] if c["raw"]["n_declines"]}},
        "E2-G3_relax_q12_reported_null": {
            "pass": all(c["Q"]["q12_neutral_option_gain"] is None for c in relax),
            "n_relax_cells": len(relax)},
    }
    (HERE / "results").mkdir(exist_ok=True)
    p = HERE / "results" / "e2_arena.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n--- GATES ---")
    for k, v in out["gates"].items():
        print(f"  {k:34s} {'PASS' if v['pass'] else 'FAIL'}")
        if k == "E2-G1_all_cells_measurable" and v["cells_under_1000_edits"]:
            print(f"      under 1000 edits: {v['cells_under_1000_edits']}")
    print(f"\nwrote {p}  ({len(out['cells'])} cells)")


if __name__ == "__main__":
    main()
