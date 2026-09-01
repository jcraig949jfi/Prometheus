#!/usr/bin/env python
"""E3 -- substrate vs operator decomposition. Frozen by FREEZE_E3.txt.

Per-OBJECT Q values are computed so that variance is estimable and the
bootstrap can resample the independent unit (objects), not edits.
"""
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

SEEDS = list(range(5000, 5060))
N_DRAWS = 400
COORDS = ["q1_neutral_rate", "q2_destruction_rate", "q3_band_rate",
          "q4_middle_mass", "q10_reach_improve_at1", "q11_drift"]


def per_object_Q(sub, operator, seeds, n_draws, seed_key):
    """Q for each object separately -- the resampling unit is the object."""
    rows = []
    for s in seeds:
        Q, _pt, raw = A.measure_cell(sub, operator=operator, seeds=[s],
                                     n_draws=n_draws, seed_key=seed_key + s)
        if raw["n_edits"] == 0:
            continue
        rows.append({c: Q[c] for c in COORDS} | {"seed": s,
                                                 "n_edits": raw["n_edits"],
                                                 "n_declines": raw["n_declines"]})
    return rows


def two_way_eta2(table, coord):
    """table[(sub, op)] = list of per-object values. Standard two-way eta^2."""
    subs = sorted({k[0] for k in table})
    ops = sorted({k[1] for k in table})
    allv = np.concatenate([np.array([r[coord] for r in table[k]])
                           for k in table])
    gm = allv.mean()
    sst = ((allv - gm) ** 2).sum()
    if sst == 0:
        return {"eta2_substrate": 0.0, "eta2_operator": 0.0,
                "eta2_interaction": 0.0, "sst": 0.0, "degenerate": True}

    def marg(idx, level):
        vs = [r[coord] for k in table if k[idx] == level for r in table[k]]
        return np.array(vs)

    ssa = sum(len(marg(0, s)) * (marg(0, s).mean() - gm) ** 2 for s in subs)
    ssb = sum(len(marg(1, o)) * (marg(1, o).mean() - gm) ** 2 for o in ops)
    sscell = 0.0
    for k, rows in table.items():
        v = np.array([r[coord] for r in rows])
        sscell += len(v) * (v.mean() - gm) ** 2
    ssab = max(0.0, sscell - ssa - ssb)
    return {"eta2_substrate": ssa / sst, "eta2_operator": ssb / sst,
            "eta2_interaction": ssab / sst, "sst": float(sst),
            "degenerate": False}


def boot_diff(a, b, n=2000, seed=17):
    """95% CI on mean(a)-mean(b), resampling OBJECTS."""
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = []
    for _ in range(n):
        d.append(rng.choice(a, len(a), replace=True).mean()
                 - rng.choice(b, len(b), replace=True).mean())
    d = np.sort(d)
    return (float(a.mean() - b.mean()),
            float(d[int(0.025 * n)]), float(d[int(0.975 * n)]))


def main():
    out = {"experiment": "E3", "freeze": "FREEZE_E3.txt", "arm1": {},
           "arm2": {}, "eta2": {}, "gates": {}}

    # -------- ARM 1: crossed 3x3
    subs = {"CIRCUIT": S.Circuit(), "BYTEVM": S.ByteVM(), "DNF": S.DNF()}
    ops = {"M-UNIFORM": M.UniformSite, "M-UNIFORM2": M.UniformDouble,
           "M-TAILSITE": M.TailSite}
    table = {}
    for sname, sub in subs.items():
        for oname, ocls in ops.items():
            t0 = time.time()
            rows = per_object_Q(sub, ocls(), SEEDS, N_DRAWS, 7000)
            table[(sname, oname)] = rows
            m = {c: float(np.mean([r[c] for r in rows])) for c in COORDS}
            out["arm1"][f"{sname}|{oname}"] = {
                "n_objects": len(rows), "mean": m,
                "n_declines": int(sum(r["n_declines"] for r in rows)),
                "seconds": round(time.time() - t0, 1)}
            print(f"{sname:8s} {oname:12s} n_obj={len(rows):3d} "
                  f"q2={m['q2_destruction_rate']:.4f} q3={m['q3_band_rate']:.4f} "
                  f"q4={m['q4_middle_mass']:.4f} q10={m['q10_reach_improve_at1']:.3f} "
                  f"({round(time.time()-t0,1)}s)")

    for c in COORDS:
        out["eta2"][c] = two_way_eta2(table, c)

    # -------- ARM 2: the typed contrast, paired on identical parents
    vm = S.ByteVM()
    raw_rows = per_object_Q(vm, M.RawByte(), SEEDS, N_DRAWS, 7100)
    ins_rows = per_object_Q(vm, M.InstructionAware(), SEEDS, N_DRAWS, 7100)
    for coord in ("q2_destruction_rate", "q3_band_rate", "q1_neutral_rate",
                  "q4_middle_mass"):
        a = [r[coord] for r in raw_rows]
        b = [r[coord] for r in ins_rows]
        diff, lo, hi = boot_diff(a, b)
        out["arm2"][coord] = {"M-RAWBYTE": float(np.mean(a)),
                              "M-INSTR": float(np.mean(b)),
                              "diff": diff, "ci95": [lo, hi]}
        print(f"ARM2 {coord:24s} raw={np.mean(a):.4f} instr={np.mean(b):.4f} "
              f"diff={diff:+.4f} CI[{lo:+.4f},{hi:+.4f}]")

    q2d = abs(out["arm2"]["q2_destruction_rate"]["diff"])
    q3r = out["arm2"]["q3_band_rate"]["M-RAWBYTE"]
    q3i = out["arm2"]["q3_band_rate"]["M-INSTR"]
    pc2 = bool(q2d >= 0.02 and q3r < 0.05 and q3i < 0.05)

    e3 = out["eta2"]["q3_band_rate"]
    out["gates"] = {
        "PC2_operator_moves_destruction_substrate_owns_band": {
            "pass": pc2, "q2_abs_diff": round(q2d, 4),
            "q3_rawbyte": round(q3r, 4), "q3_instr": round(q3i, 4),
            "bar": "|dq2|>=0.02 and both q3<0.05"},
        "KILL_mutator_dominates_on_band": {
            "fired": bool(e3["eta2_operator"] > e3["eta2_substrate"]),
            "eta2_substrate": round(e3["eta2_substrate"], 4),
            "eta2_operator": round(e3["eta2_operator"], 4),
            "eta2_interaction": round(e3["eta2_interaction"], 4)},
        "KILL_interaction_dominates_on_band": {
            "fired": bool(e3["eta2_interaction"] > e3["eta2_substrate"]
                          and e3["eta2_interaction"] > e3["eta2_operator"])},
    }
    (HERE / "results").mkdir(exist_ok=True)
    p = HERE / "results" / "e3_decomposition.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("\n--- eta^2 (ARM 1, crossed 3x3) ---")
    print(f"{'coordinate':26s} {'substrate':>10s} {'operator':>10s} {'interact':>10s}")
    for c in COORDS:
        e = out["eta2"][c]
        print(f"{c:26s} {e['eta2_substrate']:10.4f} {e['eta2_operator']:10.4f} "
              f"{e['eta2_interaction']:10.4f}")
    print("\n--- GATES ---")
    for k, v in out["gates"].items():
        print(f"  {k}: {v}")
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
