"""Diagnostic probes AFTER the first gate refusal, BEFORE choosing the one correction.

The gate refused on P1 (ACCUMULATOR deficit 4.4% against a preregistered 10%) and P4 (the
pilot population is near-stateless, so state deletion is inert on it). Carry-forward
lesson 5: measure before theorising. These probes are MEASUREMENTS that inform the single
permitted correction; they are not a world-design iteration and no gate is re-run here.

  A  P1 attainability: ACCUMULATOR AURC as a function of k (the eligibility count that
     should have preceded freezing the 0.90 threshold - CW01-D058).
  B  How much of the pilot's useful computation lives in state: I_intact minus I with the
     state zeroed before every episode (the stateless twin of the same organism).
  C  Evolvability at the REAL budget: one STATIC lineage for 120 generations; state
     dependence of its top 8.
  D  Candidate causal feature: persistence prior (A initialised at 0.9 I + noise);
     40-generation pilot lineage; state dependence and damage bite.
  E  P4 on the current pilot at k in {3, 5, 7}: does separability appear at higher
     severity without any change to evolvability?
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
import seeds as S              # noqa: E402
import world_e07 as W          # noqa: E402


def state_dependence(cfg, aid, r, pop, Q):
    """I_intact - I_stateless_twin on the selection stream, per organism."""
    stream = W.task_stream(cfg, aid, r, "select", 0, cfg["test"]["n_select"], Q)
    s_int = W.run_lifetimes(pop, cfg, stream).mean(axis=(1, 2))
    every = {t: [(l, np.arange(cfg["world"]["K"])) for l in range(stream["n"])]
             for t in range(cfg["world"]["L"])}
    s_sl = W.run_lifetimes(pop, cfg, stream, every, W.damage_op).mean(axis=(1, 2))
    return s_int, s_sl, s_int - s_sl


def aurc_at_k(cfg, aid, pop, Q, ks, n=64, tag="p1"):
    d = cfg["damage"]
    stream = W.task_stream(cfg, aid, "gate", tag, 0, n, Q)
    F = W.floor_scores(stream)
    s_int = W.run_lifetimes(pop, cfg, stream)
    out = {}
    for k in ks:
        rng = S.rng(aid, "probe|%s|k%d" % (tag, k))
        sched = {}
        for l in range(n):
            sched.setdefault(d["T_d"], []).append((l, W.select_cells(cfg["world"]["K"], k, rng)))
        s_d = W.run_lifetimes(pop, cfg, stream, sched, W.damage_op)
        rb = W.robustness(s_int, s_d, F, cfg)
        even = W.robustness(s_int, s_d, F, cfg, lifetimes=np.arange(0, n, 2))
        odd = W.robustness(s_int, s_d, F, cfg, lifetimes=np.arange(1, n, 2))
        out[k] = {"rb": rb, "even": even, "odd": odd}
    return out


def main():
    t0 = time.time()
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    aid = cfg["attempt_id"]
    Q = W.attempt_Q(cfg, aid, "gate")
    K = cfg["world"]["K"]
    rep = {}

    print("-- A: P1 attainability, ACCUMULATOR AURC vs k (64 lifetimes) --")
    probes = W.probe_genomes(cfg, Q)
    P = np.array([probes["ACCUMULATOR"], probes["STATELESS"]])
    A = aurc_at_k(cfg, aid, P, Q, range(1, 9))
    rep["A_accumulator_aurc_vs_k"] = {}
    for k, v in A.items():
        a, r0 = float(v["rb"]["AURC"][0]), float(v["rb"]["rho0"][0])
        rep["A_accumulator_aurc_vs_k"][k] = {"f": k / K, "AURC": a, "rho0": r0,
                                             "rhoH": float(v["rb"]["rhoH"][0])}
        print("   k=%d f=%.3f  AURC %.4f  rho0 %.4f  rhoH %.4f  %s"
              % (k, k / K, a, r0, v["rb"]["rhoH"][0], "<=0.90 OK" if a <= 0.90 else ""))

    print("\n-- B: pilot state dependence (I_intact - I_stateless_twin) --")
    from gate_e07 import build_pilot
    pilot, _ = build_pilot(cfg, aid, Q)
    s_int, s_sl, dep = state_dependence(cfg, aid, "gate", pilot, Q)
    rep["B_pilot_state_dependence"] = {
        "I_mean": float(s_int.mean()), "I_max": float(s_int.max()),
        "stateless_twin_mean": float(s_sl.mean()),
        "dependence_mean": float(dep.mean()), "dependence_max": float(dep.max()),
        "dependence_quartiles": [float(x) for x in np.percentile(dep, [25, 50, 75])],
        "frac_dependence_above_0.05": float(np.mean(dep > 0.05))}
    print("   %s" % rep["B_pilot_state_dependence"])

    print("\n-- C: evolvability at the real budget: one STATIC lineage, 120 generations --")
    ev = W.evolve(cfg, aid, "gate", "STATIC", 0, Q, seed_component="probeC", stream_kind="pilottrain")
    hist = ev["history"]
    marks = {g: (round(hist[g]["mean"], 4), round(hist[g]["max"], 4)) for g in (0, 19, 39, 59, 79, 99, 119)}
    reps, _ = W.select_representatives(cfg, aid, "gate", ev["pop"], Q)
    s_int, s_sl, dep = state_dependence(cfg, aid, "gate", reps, Q)
    Ck = aurc_at_k(cfg, aid, reps, Q, [3, 5, 7], n=32, tag="test")
    rep["C_static_120gen"] = {
        "trajectory_mean_max": {str(k): v for k, v in marks.items()},
        "top8_I": [float(x) for x in s_int], "top8_state_dependence": [float(x) for x in dep],
        "top8_AURC_by_k": {k: [float(x) for x in Ck[k]["rb"]["AURC"]] for k in Ck}}
    print("   trajectory (mean,max): %s" % marks)
    print("   top8 I %s" % np.round(s_int, 3).tolist())
    print("   top8 state dependence %s" % np.round(dep, 3).tolist())
    for k in Ck:
        print("   top8 AURC at k=%d: %s" % (k, np.round(Ck[k]["rb"]["AURC"], 3).tolist()))

    print("\n-- D: candidate causal feature: persistence prior A0 = 0.9 I, 40-gen pilot lineage --")
    ev0 = cfg["evolution"]
    G = cfg["gate"]["pilot_generations"]
    rng = S.rng(aid, "probeD|gate|STATIC|0")
    pop = rng.normal(0.0, ev0["init_sigma"], size=(ev0["n_org"], W.genome_size(cfg)))
    v = W.unpack(pop, cfg)
    for i in range(pop.shape[0]):
        v["A"][i] += 0.9 * np.eye(K)
    histD = []
    for g in range(G):
        stream = W.task_stream(cfg, aid, "gate", "pilottrain", g, ev0["lifetimes_per_eval"], Q)
        fit = W.run_lifetimes(pop, cfg, stream).mean(axis=(1, 2))
        histD.append((round(float(fit.mean()), 4), round(float(fit.max()), 4)))
        if g < G - 1:
            pop = W.next_generation(pop, fit, rng, ev0)
    repsD, _ = W.select_representatives(cfg, aid, "gate", pop, Q, top_k=16)
    s_int, s_sl, dep = state_dependence(cfg, aid, "gate", repsD, Q)
    Dk = aurc_at_k(cfg, aid, repsD, Q, [3, 5, 7], n=32, tag="test")
    sepD = {k: W.separability(Dk[k]["rb"]["I"], Dk[k]["rb"]["AURC"], Dk[k]["even"]["AURC"],
                              Dk[k]["odd"]["AURC"], cfg) for k in Dk}
    rep["D_persistence_prior_40gen"] = {
        "trajectory_mean_max": {str(g): histD[g] for g in (0, 9, 19, 29, 39)},
        "top16_I": [float(x) for x in s_int], "top16_state_dependence": [float(x) for x in dep],
        "top16_AURC_by_k": {k: [float(x) for x in Dk[k]["rb"]["AURC"]] for k in Dk},
        "separability_by_k": sepD}
    print("   trajectory: %s" % {g: histD[g] for g in (0, 9, 19, 29, 39)})
    print("   top16 I %s" % np.round(s_int, 3).tolist())
    print("   top16 state dependence %s" % np.round(dep, 3).tolist())
    for k in Dk:
        print("   top16 AURC at k=%d: %s | P4 %s ratio %.2f pairs %d"
              % (k, np.round(Dk[k]["rb"]["AURC"], 3).tolist(), sepD[k]["outcome"],
                 sepD[k]["ratio"] if np.isfinite(sepD[k]["ratio"]) else float("nan"), sepD[k]["n_pairs"]))

    print("\n-- E: P4 on the CURRENT pilot at k in {3,5,7} --")
    Ek = aurc_at_k(cfg, aid, pilot, Q, [3, 5, 7], n=32, tag="test")
    rep["E_pilot_separability_by_k"] = {}
    for k in Ek:
        rb = Ek[k]["rb"]
        u = rb["useful"]
        sep = W.separability(rb["I"][u], rb["AURC"][u], Ek[k]["even"]["AURC"][u], Ek[k]["odd"]["AURC"][u], cfg)
        rep["E_pilot_separability_by_k"][k] = {"AURC_median": float(np.nanmedian(rb["AURC"][u])),
                                               "AURC_min": float(np.nanmin(rb["AURC"][u])), **sep}
        print("   k=%d median AURC %.4f min %.4f | P4 %s ratio %.2f pairs %d"
              % (k, np.nanmedian(rb["AURC"][u]), np.nanmin(rb["AURC"][u]), sep["outcome"],
                 sep["ratio"] if np.isfinite(sep["ratio"]) else float("nan"), sep["n_pairs"]))

    rep["_elapsed_s"] = round(time.time() - t0, 1)
    (HERE / "PROBE_E07.json").write_text(json.dumps(rep, indent=1, ensure_ascii=True, default=str),
                                         encoding="utf-8")
    print("\nPROBE_E07.json written (%.1f s)" % (time.time() - t0))


if __name__ == "__main__":
    main()
