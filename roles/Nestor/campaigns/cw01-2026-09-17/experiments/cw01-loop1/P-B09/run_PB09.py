"""P-B09 (anti-gravity): e04 evolved under a TTL DISTRIBUTION vs fixed TTL.

Parent T-X08 (<- T-E04). Delta: in the DIST arm each training episode draws ttl from
{7, 15, 30} (weather rng seeded from the stream seed, not the policy stream); FIXED arm uses
15 as e04 did. 4 replicates per arm, 60 generations. After evolution the top-8 of each
population (by train score on selection streams) are scored on 16 matched test streams at
ttl 7, 15 and 30, and under a sham shock (ttl re-set to 15: the identity, cost-matched by
construction). Ruler: relative score s(ttl)/s(15) per replicate; arm contrast by exact
relabelling (C(8,4)=70). Unchanged: everything else in e04.
"""
from __future__ import annotations

import copy
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W4 = L.import_world("cw01-e04", "world_e04")
PID, TID, AID = "P-B09", "T-X08", "cw01-loop1-PB09"
TTLS, N_REP, G, N_SEL, N_TEST, TOP_K = (7, 15, 30), 4, 60, 8, 16, 8
MODE = {"dist": False}
_orig = W4.run_episode


def run_episode_w(genome, cfg, arm, stream_seed, wmap=None, scramble=None, collect_patterns=False):
    if MODE["dist"]:
        r = np.random.Generator(np.random.PCG64(S.seed(str(stream_seed), "weather")))
        cfg = copy.deepcopy(cfg)
        cfg["channel"]["ttl_steps"] = int(r.choice(TTLS))
    return _orig(genome, cfg, arm, stream_seed, wmap, scramble, collect_patterns)


W4.run_episode = run_episode_w


def score_at(pop, cfg, wmap, streams, ttl):
    c = copy.deepcopy(cfg)
    c["channel"]["ttl_steps"] = ttl
    MODE["dist"] = False
    return np.array([[W4.run_episode(g, c, "treatment", s, wmap=wmap)["score"] for s in streams] for g in pop])


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "exploratory-with-relabelling",
                         "delta": "DIST arm evolves with ttl drawn per episode from %s; FIXED arm at 15" % (TTLS,),
                         "unchanged": "e04 world, organism, selection, 60 generations, worth map per attempt",
                         "attacks": "the inverted generality (better under ttl_double, worse under ttl_half): schedule specialisation?",
                         "replicates_per_arm": N_REP, "test_ttls": TTLS, "sham": "ttl re-set to 15 (identity)",
                         "statistic": "rel(ttl) = mean score at ttl / mean score at 15 per replicate; DIST minus FIXED by exact relabelling; also absolute score at each ttl",
                         "decision": "descriptive; DIST rel(7) above p95 of the relabelling null is recorded as material (specialisation removed)"})
    runs = {"FIXED": [], "DIST": []}
    for arm in ("FIXED", "DIST"):
        for rep in range(N_REP):
            cfg = L.load_cfg("cw01-e04", AID + "|r%d" % rep)
            wmap = W4.attempt_worth_map(cfg, S.seed)
            MODE["dist"] = (arm == "DIST")
            ev = W4.evolve(cfg, "treatment", G, cfg["population"]["organisms"], S.seed, wmap=wmap)
            pop = ev["final_pop"]
            sel = [S.seed(AID, "sel", j) for j in range(N_SEL)]
            s_sel = score_at(pop, cfg, wmap, sel, 15).mean(1)
            reps = [pop[i] for i in np.argsort(-s_sel)[:TOP_K]]
            test = [S.seed(AID, "test", j) for j in range(N_TEST)]
            abs_s = {t: float(score_at(reps, cfg, wmap, test, t).mean()) for t in TTLS}
            rel = {t: abs_s[t] / abs_s[15] for t in TTLS}
            rec = {"rep": rep, "abs": abs_s, "rel": rel, "selectivity": ev["history"][-1]["mean_selectivity"],
                   "final_mean": ev["history"][-1]["mean"]}
            runs[arm].append(rec)
            print("   %-5s r%d  abs %s  rel7 %.3f rel30 %.3f  sel %.2f" % (arm, rep, {k: round(v, 3) for k, v in abs_s.items()},
                                                                       rel[7], rel[30], rec["selectivity"]), flush=True)
    contrasts = {}
    for t in (7, 30):
        contrasts["rel_%d" % t] = L.relabel_diff([r["rel"][t] for r in runs["FIXED"]], [r["rel"][t] for r in runs["DIST"]])
        contrasts["abs_%d" % t] = L.relabel_diff([r["abs"][t] for r in runs["FIXED"]], [r["abs"][t] for r in runs["DIST"]])
    contrasts["abs_15"] = L.relabel_diff([r["abs"][15] for r in runs["FIXED"]], [r["abs"][15] for r in runs["DIST"]])
    material = bool(contrasts["rel_7"]["above_p95"])
    res = {"perturbation_id": PID, "parent": TID, "contrasts": contrasts, "runs": runs,
           "arm_means": {a: {"rel7": float(np.mean([r["rel"][7] for r in runs[a]])), "rel30": float(np.mean([r["rel"][30] for r in runs[a]])),
                             "abs15": float(np.mean([r["abs"][15] for r in runs[a]]))} for a in runs},
           "reading": ("evolving under a TTL distribution removes the fast-forgetting penalty" if material else
                       "no relabelling-clearing change in rel(7); inversion persists or is noise"),
           "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "TTL-distribution evolution: FIXED rel7 %.3f vs DIST rel7 %.3f (effect %.3f, band [%.3f, %.3f])"
                      % (res["arm_means"]["FIXED"]["rel7"], res["arm_means"]["DIST"]["rel7"], contrasts["rel_7"]["effect"],
                         contrasts["rel_7"]["p05"], contrasts["rel_7"]["p95"]), material, detail=contrasts)
    L.append_evidence("T-E04", PID, "schedule-distribution perturbation run; see T-X08", material)
    print("DONE %s (%.0f s)" % (res["reading"], time.time() - t0))


if __name__ == "__main__":
    main()
