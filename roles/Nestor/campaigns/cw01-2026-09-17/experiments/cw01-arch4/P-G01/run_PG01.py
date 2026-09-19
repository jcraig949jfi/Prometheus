"""P-G01 [T-R01]: QUALIFICATION of the scattered damage ruler (scatter.py) before any scientific use.

Controls: (1) hit counts vs Binomial(n, f): pooled z-scores over 200 draws x 60 programs (|mean z| <= .10,
var z in [.85, 1.15]) and a Monte Carlo chi-square on the pooled counts; (2) positions not clustered: the
variance of gaps between consecutive hits inside the 5-95 band of simulated Bernoulli masks; (3)
fraction hit independent of length: slope of fraction_hit on n inside its permutation band; (4) equal
seeds reproduce exact masks (all programs, 3 keys); (5) SHAM path: mask drawn, nothing applied, same
route: displacement 0 and reward equal on every program. Any failure -> INSTRUMENT_FAILURE.
Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import scatter as SC           # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops   # noqa: E402

PID, TID, F = "P-G01", "T-R01", 0.10


def programs():
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    out = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        out.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    return out + c408_tops()


def job(j):
    p = j["program"]
    pm = A.canonical(p["manifest"])
    n = len(pm["genome"]) // A.IW
    hits, gapvars = [], []
    for d in range(1, 201):
        msk = SC.mask(n, F, (p["organism_id"], "qual", F, d))
        k = sum(msk)
        hits.append(k)
        pos = [i for i in range(n) if msk[i]]
        if len(pos) >= 3:
            gapvars.append(float(np.var(np.diff(pos))))
    rng = np.random.Generator(np.random.PCG64(abs(hash(p["organism_id"])) % (2 ** 32)))
    sim_gap = []
    for _ in range(200):
        m2 = rng.random(n) < F
        pos = np.flatnonzero(m2)
        if len(pos) >= 3:
            sim_gap.append(float(np.var(np.diff(pos))))
    repro = all(SC.mask(n, F, (p["organism_id"], "qual", F, d)) == SC.mask(n, F, (p["organism_id"], "qual", F, d)) for d in (1, 2, 3))
    eps = A.episodes(p["env"])
    sh = SC.sham(pm, p["env"], eps, F, p["organism_id"])
    return {"pid": p["organism_id"], "set": p["stratum"], "n": n, "hits": hits, "z": [(k - n * F) / np.sqrt(n * F * (1 - F)) for k in hits],
            "gap_var": float(np.mean(gapvars)) if gapvars else None, "sim_gap_var": (float(np.percentile(sim_gap, 5)), float(np.percentile(sim_gap, 95))) if len(sim_gap) >= 20 else None,
            "repro": repro, "sham": sh}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "R", "scope": CM.SCOPE, "claim_type": "instrument-qualification", "f": F, "draws_per_program": 200,
                         "controls": {"hit_counts": "|mean z| <= .10 and var z in [.85, 1.15] pooled; Monte Carlo chi-square p >= .05 on pooled counts", "clustering": "per-program gap variance inside its simulated 5-95 band for >= 90 percent of programs",
                                      "length_independence": "slope of mean fraction_hit on n inside its 2000-permutation band", "reproducibility": "equal keys give equal masks for every program (3 keys)", "sham": "displacement 0 and reward equal for every program"},
                         "disposition_rule": "INSTRUMENT_QUALIFIED iff every control passes; else INSTRUMENT_FAILURE (rereads stop)", "provenance": SC.PROVENANCE, "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    progs = programs()
    with A.pool(8) as ex:
        rows = list(ex.map(job, [{"program": p} for p in progs]))
    z = np.array([x for r in rows for x in r["z"]])
    hit_ok = bool(abs(z.mean()) <= 0.10 and 0.85 <= z.var() <= 1.15)
    # Monte Carlo chi-square: pooled counts vs simulated Binomial counts with the same n's
    rng = np.random.Generator(np.random.PCG64(1))
    obs = np.array([k for r in rows for k in r["hits"]])
    ns = np.array([r["n"] for r in rows for _ in r["hits"]])
    sims = [rng.binomial(ns, F) for _ in range(200)]
    edges = np.arange(0, obs.max() + 2)
    ho = np.histogram(obs, edges)[0]
    hs = np.array([np.histogram(s, edges)[0] for s in sims])
    exp = hs.mean(axis=0) + 1e-9
    chi_obs = float(((ho - exp) ** 2 / exp).sum())
    chi_null = [float(((h - exp) ** 2 / exp).sum()) for h in hs]
    chi_p = float(np.mean([c >= chi_obs for c in chi_null]))
    clust_ok_share = float(np.mean([r["gap_var"] is None or r["sim_gap_var"] is None or (r["sim_gap_var"][0] <= r["gap_var"] <= r["sim_gap_var"][1]) for r in rows]))
    clust_ok = clust_ok_share >= 0.90
    fr = np.array([np.mean(r["hits"]) / r["n"] for r in rows])
    nn = np.array([r["n"] for r in rows], float)
    slope = float(np.polyfit(nn, fr, 1)[0])
    null = np.array([np.polyfit(rng.permutation(nn), fr, 1)[0] for _ in range(2000)])
    len_ok = bool(np.percentile(null, 5) <= slope <= np.percentile(null, 95))
    repro_ok = all(r["repro"] for r in rows)
    sham_ok = all(r["sham"]["disp"] == 0.0 and r["sham"]["reward_equal"] for r in rows)
    controls = {"hit_counts": {"pass": hit_ok and chi_p >= 0.05, "mean_z": float(z.mean()), "var_z": float(z.var()), "chi_p": chi_p, "n_draws": int(len(z))},
                "clustering": {"pass": clust_ok, "share_inside_band": clust_ok_share}, "length_independence": {"pass": len_ok, "slope": slope, "band": [float(np.percentile(null, 5)), float(np.percentile(null, 95))]},
                "reproducibility": {"pass": repro_ok}, "sham": {"pass": sham_ok, "n": len(rows)}}
    qualified = all(c["pass"] for c in controls.values())
    out = {"perturbation_id": PID, "parent": TID, "disposition": "INSTRUMENT_QUALIFIED" if qualified else "INSTRUMENT_FAILURE", "controls": controls, "provenance": SC.PROVENANCE,
           "n_programs": len(rows), "material": bool(qualified), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "scattered ruler qualification: %s; hit counts mean z %+.3f var z %.3f chi p %.2f; clustering inside band %.2f; length slope %+.2e band %s; reproducible %s; sham %s"
                      % (out["disposition"], z.mean(), z.var(), chi_p, clust_ok_share, slope, controls["length_independence"]["band"], repro_ok, sham_ok), bool(qualified), detail=controls,
                      state="ACTIVE", state_reason="ruler %s" % out["disposition"])
    print("DONE %s %s (%.0f s)" % (out["disposition"], {k: v["pass"] for k, v in controls.items()}, time.time() - t0))


if __name__ == "__main__":
    main()
