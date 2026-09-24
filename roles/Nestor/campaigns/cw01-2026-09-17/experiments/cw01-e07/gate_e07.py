"""cw01-e07 PRE-QUALIFY ADMISSIBILITY GATE: the world must EARN admission before budget.

P1  DAMAGE FIRES        ACCUMULATOR's block-mean AURC at the primary severity is below
                        p1_block_max in every block and its grand mean at most p1_mean_max;
                        STATELESS is unaffected (damage acts only through state).
P2  SHAM IS INERT       sham lifetimes equal intact lifetimes to within p2_tol, everywhere.
P3  NON-LETHAL          useful pilot organisms: median AURC at the top of the sweep at least
                        p3_median_aurc_min; at the primary severity at least p3_rhoH_frac
                        recover to rhoH >= p3_rhoH_min inside the horizon.
P4  SEPARABLE           conditional variance of AURC given intact ability exceeds retest
                        noise by p4_ratio_min (organisms of like ability differ in response).
P5  BLIND               the production operator deletes the same index set for different
                        states under the same RNG, on every trial.

THE GATE MUST BE SHOWN REFUSING. Five known-broken fixtures run through the SAME gate:
F1 no-op selector (P1), F2 sham that zeros (P2), F3 persistent lesion (P3), F4 readout-gain
family (P4), F5 magnitude-targeting selector (P5). Each refusal is demonstrated once. The
gate is never relaxed to admit the candidate.

Also: learnability (ACCUMULATOR beats STATELESS beats ZERO), and determinism (a pilot
lineage evolved twice is bit-identical).
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
import repopath as RP          # noqa: E402,F401
import seeds as S              # noqa: E402
import learnability as LN      # noqa: E402
import world_e07 as W          # noqa: E402


# ----------------------------------------------------------------- fixtures

def noop_select(K, k, rng, M=None):
    """F1: consumes the same draws, selects nothing."""
    if k > 0:
        rng.choice(K, size=int(k), replace=False)
    return np.zeros(0, dtype=int)


def magnitude_select(K, k, rng, M=None):
    """F5: deletes the k largest-magnitude cells (semantic targeting)."""
    if k > 0:
        rng.choice(K, size=int(k), replace=False)
    if M is None or k <= 0:
        return np.zeros(0, dtype=int)
    mag = np.abs(M).reshape(-1, K).mean(axis=0)
    return np.sort(np.argsort(-mag)[:int(k)])


def fixtures(cfg, Q, pilot):
    fam = W.gain_family(cfg, Q)
    return [
        ("F1_noop_selector", {"select": noop_select, "damage": W.damage_op, "sham": W.sham_op,
                              "lethal": False}, pilot, "P1"),
        ("F2_sham_that_zeros", {"select": W.select_cells, "damage": W.damage_op,
                                "sham": W.damage_op, "lethal": False}, pilot, "P2"),
        ("F3_persistent_lesion", {"select": W.select_cells, "damage": W.damage_op,
                                  "sham": W.sham_op, "lethal": True}, pilot, "P3"),
        ("F4_readout_gain_family", dict(W.PRODUCTION_OPS), fam, "P4"),
        ("F5_magnitude_selector", {"select": magnitude_select, "damage": W.damage_op,
                                   "sham": W.sham_op, "lethal": False}, pilot, "P5"),
    ]


# ----------------------------------------------------------------- the gate

def p5_blind(cfg, aid, select):
    K, k = cfg["world"]["K"], W.severity_k(cfg["damage"]["primary"], cfg["world"]["K"])
    n_trials = cfg["gate"]["p5_trials"]
    base = S.rng(aid, "p5")
    same = 0
    for i in range(n_trials):
        seed = int(base.integers(0, 2 ** 31))
        M1 = np.random.Generator(np.random.PCG64(seed + 1)).uniform(0.5, 3.0, size=(4, 2, K))
        M2 = np.random.Generator(np.random.PCG64(seed + 2)).uniform(-3.0, -0.5, size=(4, 2, K))
        i1 = select(K, k, np.random.Generator(np.random.PCG64(seed)), M1)
        i2 = select(K, k, np.random.Generator(np.random.PCG64(seed)), M2)
        same += int(np.array_equal(i1, i2))
    return {"outcome": "PASS" if same == n_trials else "FAIL", "same": same, "trials": n_trials}


def run_gate(cfg, aid, Q, ops, pilot, label):
    gc, d = cfg["gate"], cfg["damage"]
    K = cfg["world"]["K"]
    probes = W.probe_genomes(cfg, Q)
    P = np.array([probes["ACCUMULATOR"], probes["STATELESS"], probes["ZERO"]])
    reasons = []

    # ---- P1 on the hand-built probes, 8 blocks of 8 lifetimes
    n1 = gc["p1_lifetimes"]
    stream = W.task_stream(cfg, aid, "gate", "p1", 0, n1, Q)
    F = W.floor_scores(stream)
    s_int = W.run_lifetimes(P, cfg, stream)
    sched = W.event_schedule(cfg, S.rng(aid, "p1weather"), n1, d["primary"], [d["T_d"]], ops["select"])
    if ops.get("lethal"):
        sched = W.lethal_schedule(cfg, n1)
    s_dmg = W.run_lifetimes(P, cfg, stream, sched, ops["damage"], lesion=bool(ops.get("lethal")))
    bs = n1 // gc["p1_blocks"]
    blocks = [W.robustness(s_int, s_dmg, F, cfg, lifetimes=np.arange(b * bs, (b + 1) * bs))["AURC"]
              for b in range(gc["p1_blocks"])]
    acc_blocks = [float(b[0]) for b in blocks]
    grand = W.robustness(s_int, s_dmg, F, cfg)["AURC"]
    p1_fires = all(x < gc["p1_block_max"] for x in acc_blocks) and grand[0] <= gc["p1_mean_max"]
    p1_stateless = abs(grand[1] - 1.0) <= gc["p1_stateless_tol"]
    p1 = bool(p1_fires and p1_stateless)
    if not p1_fires:
        reasons.append("P1 damage does not fire on ACCUMULATOR: blocks %s grand %.4f"
                       % (["%.3f" % x for x in acc_blocks], grand[0]))
    if not p1_stateless:
        reasons.append("P1 damage touched a STATELESS organism: AURC %.6f" % grand[1])

    # ---- P2 sham inert, on probes and pilot
    tp_probe = W.test_protocol(cfg, aid, "gate", P, Q, ops=ops)
    tp_pilot = W.test_protocol(cfg, aid, "gate", pilot, Q, ops=ops)
    sham_dev = float(max(tp_probe["sham_max_abs_diff"].max(), tp_pilot["sham_max_abs_diff"].max()))
    p2 = bool(sham_dev <= gc["p2_tol"])
    if not p2:
        reasons.append("P2 sham deviates from intact by %.3e" % sham_dev)

    # ---- P3 / P4 on useful pilot organisms
    prim = tp_pilot["conditions"]["primary"]
    top = tp_pilot["conditions"]["sev030"]
    useful = prim["useful"]
    n_useful = int(useful.sum())
    if n_useful < gc["min_useful_pilot"]:
        p3, p4 = False, False
        p3_detail = {"outcome": "NOT_VERIFIED", "n_useful": n_useful}
        p4_detail = {"outcome": "NOT_VERIFIED", "n_useful": n_useful}
        reasons.append("P3/P4 NOT_VERIFIED: only %d useful pilot organisms (need %d)"
                       % (n_useful, gc["min_useful_pilot"]))
    else:
        med = float(np.nanmedian(top["AURC"][useful]))
        frac = float(np.mean(prim["rhoH"][useful] >= gc["p3_rhoH_min"]))
        p3 = bool(med >= gc["p3_median_aurc_min"] and frac >= gc["p3_rhoH_frac"])
        p3_detail = {"outcome": "PASS" if p3 else "FAIL", "n_useful": n_useful,
                     "median_AURC_at_top_severity": med, "frac_recovered_rhoH": frac,
                     "median_AURC_primary": float(np.nanmedian(prim["AURC"][useful])),
                     "mean_rho0_primary": float(np.nanmean(prim["rho0"][useful]))}
        if not p3:
            reasons.append("P3 regime lethal/unrecoverable: median AURC(f=0.30) %.3f, recovered %.2f"
                           % (med, frac))
        p4_detail = W.separability(prim["I"][useful], prim["AURC"][useful],
                                   prim["AURC_even"][useful], prim["AURC_odd"][useful], cfg)
        p4_detail["n_useful"] = n_useful
        p4 = p4_detail["outcome"] == "PASS"
        if not p4:
            reasons.append("P4 %s: v_cond/v_noise = %s over %d pairs"
                           % (p4_detail["outcome"], "%.2f" % p4_detail["ratio"]
                              if np.isfinite(p4_detail["ratio"]) else "nan", p4_detail["n_pairs"]))

    # ---- P5 blindness
    p5_detail = p5_blind(cfg, aid, ops["select"])
    p5 = p5_detail["outcome"] == "PASS"
    if not p5:
        reasons.append("P5 selector is not blind: same index set on %d/%d trials"
                       % (p5_detail["same"], p5_detail["trials"]))

    admitted = bool(p1 and p2 and p3 and p4 and p5)
    return {"world": label, "P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5,
            "admitted": admitted, "reasons": reasons or ["all five preconditions met"],
            "detail": {"P1": {"accumulator_blocks": acc_blocks, "accumulator_grand": float(grand[0]),
                              "stateless": float(grand[1]), "zero": float(grand[2])},
                       "P2": {"sham_max_abs_diff": sham_dev},
                       "P3": p3_detail, "P4": p4_detail, "P5": p5_detail,
                       "pilot": {"n": int(pilot.shape[0]), "n_useful": n_useful,
                                 "I_mean": float(np.mean(prim["I"])),
                                 "I_range": [float(np.min(prim["I"])), float(np.max(prim["I"]))]}}}


# ----------------------------------------------------------------- pilot + learnability

def build_pilot(cfg, aid, Q):
    gc = cfg["gate"]
    parts, hist = [], []
    for j in range(gc["pilot_lineages"]):
        ev = W.evolve(cfg, aid, "gate", "STATIC", j, Q, generations=gc["pilot_generations"],
                      seed_component="pilot", stream_kind="pilottrain")
        reps, _ = W.select_representatives(cfg, aid, "gate", ev["pop"], Q, top_k=gc["pilot_top_k"])
        parts.append(reps)
        hist.append(ev["history"][-1])
    return np.concatenate(parts, axis=0), hist


def main():
    t0 = time.time()
    print("########## cw01-e07 PRE-QUALIFY ADMISSIBILITY GATE ##########")
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    aid = cfg["attempt_id"]
    Q = W.attempt_Q(cfg, aid, "gate")

    print("\n-- learnability --")
    probes = W.probe_genomes(cfg, Q)

    def evaluate(g):
        return {"score": float(W.intact_score(cfg, aid, "gate", g[None], Q)[0])}

    learn = LN.probe(probes, evaluate, "ACCUMULATOR", "STATELESS",
                     min_advantage_pct=cfg["gate"]["learnability_min_advantage_pct"])
    learn2 = LN.probe(probes, evaluate, "STATELESS", "ZERO",
                      min_advantage_pct=cfg["gate"]["learnability_min_advantage_pct"])
    for k, v in learn["results"].items():
        print("   %-12s intact score %.4f" % (k, v["score"]))
    print("   ACCUMULATOR over STATELESS %+.1f%%  -> %s" % (learn["advantage_pct"], learn["verdict"]))
    print("   STATELESS over ZERO %+.1f%%  -> %s" % (learn2["advantage_pct"], learn2["verdict"]))

    print("\n-- pilot (4 x 40-generation STATIC lineages, top 16 each) --")
    pilot, phist = build_pilot(cfg, aid, Q)
    for j, h in enumerate(phist):
        print("   pilot %d gen %d  mean %.4f  max %.4f" % (j, h["gen"], h["mean"], h["max"]))

    print("\n-- determinism --")
    a = W.evolve(cfg, aid, "gate", "STATIC", 0, Q, generations=cfg["gate"]["pilot_generations"],
                 seed_component="pilot", stream_kind="pilottrain")
    b = W.evolve(cfg, aid, "gate", "STATIC", 0, Q, generations=cfg["gate"]["pilot_generations"],
                 seed_component="pilot", stream_kind="pilottrain")
    deterministic = bool(np.array_equal(a["pop"], b["pop"]) and np.array_equal(a["fit"], b["fit"]))
    print("   pilot lineage 0 evolved twice: identical=%s" % deterministic)

    results = {}
    print("\n-- gate on CANDIDATE world --")
    cand = run_gate(cfg, aid, Q, W.PRODUCTION_OPS, pilot, "CANDIDATE")
    results["CANDIDATE"] = cand
    _print(cand)

    print("\n-- gate credibility: five known-broken fixtures --")
    fx = []
    for name, ops, pop, expect in fixtures(cfg, Q, pilot):
        res = run_gate(cfg, aid, Q, ops, pop, name)
        res["expected_failure"] = expect
        res["expected_fired"] = not res[expect]
        results[name] = res
        fx.append(res)
        print("   %-24s admitted=%-5s  expected %s fired=%s  | %s"
              % (name, res["admitted"], expect, res["expected_fired"], "; ".join(res["reasons"])[:110]))

    gate_proven = all((not r["admitted"]) and r["expected_fired"] for r in fx)
    verdict = ("GATE PROVEN AND WORLD ADMITTED" if (gate_proven and cand["admitted"]) else
               "GATE PROVEN, WORLD REFUSED" if gate_proven else
               "GATE NOT CREDIBLE - a known-broken fixture was admitted or refused for the wrong reason")
    print("\n== %s  (%.1f s) ==" % (verdict, time.time() - t0))

    out = {"campaign_id": cfg["campaign_id"], "experiment_id": cfg["experiment_id"],
           "attempt_id": aid, "phase": "QUALIFY", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "learnability": {"acc_vs_stateless": learn, "stateless_vs_zero": learn2},
           "determinism": deterministic,
           "pilot_final_generation": phist,
           "results": results, "gate_can_refuse": gate_proven,
           "world_admitted": cand["admitted"], "verdict": verdict,
           "_rule": "the gate is never tuned until it admits; a refusal is a finding"}
    (HERE / "GATE_E07.json").write_text(json.dumps(out, indent=1, ensure_ascii=True, default=_js),
                                        encoding="utf-8")
    ok = gate_proven and cand["admitted"] and learn["learnable"] and learn2["learnable"] and deterministic
    return 0 if ok else 1


def _js(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


def _print(res):
    d = res["detail"]
    print("   P1 %s | ACC blocks %s grand %.3f | STATELESS %.6f"
          % (res["P1"], ["%.2f" % x for x in d["P1"]["accumulator_blocks"]],
             d["P1"]["accumulator_grand"], d["P1"]["stateless"]))
    print("   P2 %s | sham max dev %.2e" % (res["P2"], d["P2"]["sham_max_abs_diff"]))
    print("   P3 %s | %s" % (res["P3"], {k: (round(v, 4) if isinstance(v, float) else v)
                                         for k, v in d["P3"].items()}))
    print("   P4 %s | %s" % (res["P4"], {k: (round(v, 5) if isinstance(v, float) else v)
                                         for k, v in d["P4"].items()}))
    print("   P5 %s | %s" % (res["P5"], d["P5"]))
    print("   pilot %s" % d["pilot"])
    print("   => %s" % ("ADMIT" if res["admitted"] else "REFUSE"))
    for why in res["reasons"]:
        print("      - %s" % why)


if __name__ == "__main__":
    raise SystemExit(main())
