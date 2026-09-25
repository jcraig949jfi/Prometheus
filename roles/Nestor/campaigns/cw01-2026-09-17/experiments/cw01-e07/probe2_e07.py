"""Probe F: does DIAGONAL recurrence (per-cell leaky integrators, |a_i| <= 1) make
state-dependent computation evolvable? Measured BEFORE the one correction is chosen.

Runs the candidate variant at the pilot budget (40 gens) and at the real budget (120 gens)
with the production evolution regime otherwise unchanged. Reports fitness trajectory,
state dependence of the representatives, damage bite at k=3, and the P4 ratio. Also
re-measures the ACCUMULATOR under the variant so the analytic P1 bound is on record for
the corrected world too.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
sys.path.insert(0, str(HERE))
import world_e07 as W          # noqa: E402
from probe_e07 import state_dependence, aurc_at_k   # noqa: E402


def variant_run(cfg, aid, Q, gens, lineage, label):
    ev = W.evolve(cfg, aid, "gate", "STATIC", lineage, Q, generations=gens,
                  seed_component="probeF", stream_kind="pilottrain")
    h = ev["history"]
    marks = {g: (round(h[g]["mean"], 4), round(h[g]["max"], 4)) for g in range(0, gens, max(1, gens // 6))}
    marks[gens - 1] = (round(h[-1]["mean"], 4), round(h[-1]["max"], 4))
    reps, _ = W.select_representatives(cfg, aid, "gate", ev["pop"], Q, top_k=16)
    s_int, s_sl, dep = state_dependence(cfg, aid, "gate", reps, Q)
    R = aurc_at_k(cfg, aid, reps, Q, [3, 7], n=32, tag="test")
    sep = {}
    for k in R:
        rb = R[k]["rb"]
        u = rb["useful"]
        sep[k] = W.separability(rb["I"][u], rb["AURC"][u], R[k]["even"]["AURC"][u], R[k]["odd"]["AURC"][u], cfg)
    out = {"label": label, "trajectory": {str(k): v for k, v in sorted(marks.items())},
           "top16_I": [round(float(x), 3) for x in s_int],
           "top16_dep": [round(float(x), 3) for x in dep],
           "AURC_k3": [round(float(x), 3) for x in R[3]["rb"]["AURC"]],
           "AURC_k7": [round(float(x), 3) for x in R[7]["rb"]["AURC"]],
           "P4_k3": sep[3], "P4_k7": sep[7]}
    print("   [%s] trajectory %s" % (label, out["trajectory"]))
    print("   [%s] top16 I   %s" % (label, out["top16_I"]))
    print("   [%s] top16 dep %s" % (label, out["top16_dep"]))
    print("   [%s] AURC k=3  %s" % (label, out["AURC_k3"]))
    print("   [%s] AURC k=7  %s" % (label, out["AURC_k7"]))
    for k in (3, 7):
        print("   [%s] P4 k=%d %s ratio %.2f pairs %d" % (label, k, sep[k]["outcome"],
              sep[k]["ratio"] if np.isfinite(sep[k]["ratio"]) else float("nan"), sep[k]["n_pairs"]))
    return out


def main():
    t0 = time.time()
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    cfg["organism"] = {"recurrence": "diagonal"}
    aid = cfg["attempt_id"]
    Q = W.attempt_Q(cfg, aid, "gate")
    rep = {}

    print("-- F0: ACCUMULATOR under diagonal recurrence, AURC vs k --")
    probes = W.probe_genomes(cfg, Q)
    P = np.array([probes["ACCUMULATOR"], probes["STATELESS"]])
    A = aurc_at_k(cfg, aid, P, Q, [3, 7])
    rep["F0"] = {k: {"AURC": float(A[k]["rb"]["AURC"][0]), "rho0": float(A[k]["rb"]["rho0"][0])} for k in A}
    print("   %s" % rep["F0"])

    print("\n-- F1: diagonal, 40 generations (pilot budget), two lineages --")
    rep["F1"] = [variant_run(cfg, aid, Q, 40, j, "diag40-%d" % j) for j in range(2)]

    print("\n-- F2: diagonal, 120 generations (real budget) --")
    rep["F2"] = variant_run(cfg, aid, Q, 120, 0, "diag120")

    rep["_elapsed_s"] = round(time.time() - t0, 1)
    (HERE / "PROBE2_E07.json").write_text(json.dumps(rep, indent=1, ensure_ascii=True, default=str),
                                          encoding="utf-8")
    print("\nPROBE2_E07.json written (%.1f s)" % (time.time() - t0))


if __name__ == "__main__":
    main()
