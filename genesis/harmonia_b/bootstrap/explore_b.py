#!/usr/bin/env python
"""BOOTSTRAP -- NON-ADJUDICATING. Harmonia B Gen-3B arena smoke test.

THIS FILE DECIDES NOTHING. It exists to answer engineering questions before
the charter is frozen: does each substrate run, is it non-degenerate, is it
fast enough, and does the CIRCUIT arm reproduce Harmonia A's published
marginals (which would validate the ruler port). No number produced here may
appear in any verdict; the charter is written after it, and every experiment
re-measures from scratch under a frozen script.

Run: PYTHONPATH=. python genesis/harmonia_b/bootstrap/explore_b.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import substrates as S           # noqa: E402
import mutators as M             # noqa: E402


def arena():
    return [
        S.Circuit(),
        S.ByteVM(),
        S.DNF(),
        S.RelaxedCircuit(tau=0.5),
        S.BlocksPositive(),
        S.SmoothUnreachable(),
        S.HashSubstrate(),
    ]


def sweep_profile(sub, n_obj=6, cap=8, seed0=1000):
    """Exhaustive-ish single-edit neighbourhood profile under R_VEC2."""
    rng = S.rng_for(seed0, 0xEE)
    cls = Counter()
    ds = []
    n_geno = 0
    for k in range(n_obj):
        g = sub.sample(seed0 + k)
        f = sub.phenotype(g)
        n_geno += 1
        for site, val, g2 in M.ExhaustiveSiteSweep.neighbourhood(
                sub, g, rng, cap_per_site=cap):
            f2 = sub.phenotype(g2)
            cls[S.r_vec2(f, f2)] += 1
            ds.append(S.d_of(f, f2))
    tot = sum(cls.values())
    ds = np.array(ds)
    nz = ds[ds > 0]
    return {
        "substrate": sub.name,
        "n_objects": n_geno,
        "n_edits": tot,
        "neutral": round(cls["NEUTRAL"] / tot, 4) if tot else None,
        "small": round(cls["SMALL"] / tot, 4) if tot else None,
        "large": round(cls["LARGE"] / tot, 4) if tot else None,
        "destruction": round(cls["DESTRUCTION"] / tot, 4) if tot else None,
        # A's D-14 statistic, computed per EDIT here (not per site) -- bootstrap only
        "middle_mass_edits": round(float(np.mean((ds > 0) & (ds <= 0.25))), 4)
        if len(ds) else None,
        "median_nonzero_d": round(float(np.median(nz)), 4) if len(nz) else None,
        "mean_d": round(float(ds.mean()), 4) if len(ds) else None,
    }


def continuous_profile(sub, sigma, n_obj=6, n_draw=200, seed0=2000):
    rng = S.rng_for(seed0, int(sigma * 1000))
    mut = M.GaussianStep(sigma)
    cls = Counter()
    ds = []
    for k in range(n_obj):
        g = sub.sample(seed0 + k)
        f = sub.phenotype(g)
        for _ in range(n_draw):
            r = mut(sub, g, rng)
            if r is None:
                continue
            g2, _site, _meta = r
            f2 = sub.phenotype(g2)
            cls[S.r_vec2(f, f2)] += 1
            ds.append(S.d_of(f, f2))
    tot = sum(cls.values())
    ds = np.array(ds)
    nz = ds[ds > 0]
    return {
        "substrate": f"{sub.name}[tau={sub.tau}]",
        "operator": mut.name,
        "n_edits": tot,
        "neutral": round(cls["NEUTRAL"] / tot, 4) if tot else None,
        "small": round(cls["SMALL"] / tot, 4) if tot else None,
        "large": round(cls["LARGE"] / tot, 4) if tot else None,
        "destruction": round(cls["DESTRUCTION"] / tot, 4) if tot else None,
        "middle_mass_edits": round(float(np.mean((ds > 0) & (ds <= 0.25))), 4)
        if len(ds) else None,
        "median_nonzero_d": round(float(np.median(nz)), 4) if len(nz) else None,
    }


def main():
    out = {"note": "BOOTSTRAP -- NON-ADJUDICATING. Decides nothing.",
           "profiles": [], "timing": {}, "operator_probe": []}

    for sub in arena():
        t0 = time.time()
        try:
            prof = sweep_profile(sub)
        except Exception as e:                       # counted, not swallowed
            prof = {"substrate": sub.name, "ERROR": f"{type(e).__name__}: {e}"}
        prof["seconds"] = round(time.time() - t0, 2)
        out["profiles"].append(prof)
        print(json.dumps(prof))

    # continuous arm at three temperatures x three step sizes
    for tau in (0.1, 0.5, 2.0):
        sub = S.RelaxedCircuit(tau=tau)
        for sigma in (0.25, 1.0, 4.0):
            t0 = time.time()
            try:
                prof = continuous_profile(sub, sigma)
            except Exception as e:
                prof = {"substrate": f"RELAX[tau={tau}]",
                        "ERROR": f"{type(e).__name__}: {e}"}
            prof["seconds"] = round(time.time() - t0, 2)
            out["profiles"].append(prof)
            print(json.dumps(prof))

    # operator probe: does M-INSTR actually differ from M-RAWBYTE on BYTEVM?
    vm = S.ByteVM()
    for mut in (M.RawByte(), M.InstructionAware()):
        rng = S.rng_for(3000, len(mut.name))
        cls = Counter()
        declines = 0
        for k in range(6):
            g = vm.sample(3000 + k)
            f = vm.phenotype(g)
            for _ in range(400):
                r = mut(vm, g, rng)
                if r is None:
                    declines += 1
                    continue
                cls[S.r_vec2(f, vm.phenotype(r[0]))] += 1
        tot = sum(cls.values())
        row = {"substrate": "BYTEVM", "operator": mut.name, "n": tot,
               "declines": declines,
               **{k.lower(): round(cls[k] / tot, 4) for k in
                  ("NEUTRAL", "SMALL", "LARGE", "DESTRUCTION")}}
        out["operator_probe"].append(row)
        print(json.dumps(row))

    p = HERE / "bootstrap_results.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
