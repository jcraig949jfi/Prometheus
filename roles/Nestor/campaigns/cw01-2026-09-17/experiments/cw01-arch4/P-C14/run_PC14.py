"""P-C14 (anti-gravity): SILENT DRIFT made audible.

Parent T-ARCH4/W1. The depth-16 walkers of the w0_solver parents (regenerated with C4-05's seeds
and rules on the ORIGINAL parents, digest-verified against the committed steps where available)
are exposed to a graded family: W0, W0 with noise_rate 0.10, W1_d1, W1_d2, W1_d3, W1_d4; per
environment the walker's displacement from its original parent and both rewards. The anomaly:
W0 solvers drift silently on W0 (.002) and loudly elsewhere (.17 on W1_d1). Descriptive.
Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-C14", "T-ARCH4/W1"
FAMILY = {"W0": A.WorldSpec("W0", value_bits=4), "W0_noise": A.with_knobs(A.WorldSpec("W0", value_bits=4), name="W0_noise", noise_rate=0.10),
          "W1_d1": A.WorldSpec("W1_d1", delay=1, value_bits=4), "W1_d2": A.WorldSpec("W1_d2", delay=2, value_bits=4),
          "W1_d3": A.WorldSpec("W1_d3", delay=3, value_bits=4), "W1_d4": A.WorldSpec("W1_d4", delay=4, value_bits=4)}


def job(p):
    env_eps = A.episodes("W0")
    fam_eps = {k: A.episodes_for(spec, A.CAMPAIGN_SEED, "train", 1, A.C1.E) for k, spec in FAMILY.items()}
    p_ans = {k: A.C1.answers(p["manifest"], e) for k, e in fam_eps.items()}
    p_rew = {k: A.evaluate(p["manifest"], e, rng_seed=0, reward_mode="per_ask")["reward_per_ask"] for k, e in fam_eps.items()}
    out = []
    for w in range(1, 5):
        wk = A.C5.walk(p["manifest"], p["organism_id"], w, env_eps, 16, 32)
        final = wk["archived"].get(wk["depth"])
        rec = {"walker": w, "depth": wk["depth"], "digest": A.digest(final), "per_env": {}}
        for k, e in fam_eps.items():
            an = A.C1.answers(final, e)
            rew = A.evaluate(final, e, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            rec["per_env"][k] = {"displacement": A.C1.displacement(an, p_ans[k]), "reward": rew, "parent_reward": p_rew[k]}
        out.append(rec)
    return {"parent_id": p["organism_id"], "walkers": out}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "exploratory-descriptive",
                         "delta": "expose regenerated depth-16 W0-solver walkers to a graded family (W0, W0+noise .10, W1_d1..d4); displacement vs the original parent per environment",
                         "held_fixed": "walkers (C4-05 seeds and rules), displacement ruler", "attacks": "the silent-vs-loud drift anomaly (C4-05 R2)",
                         "nonredundant": "an unnamed phenotype never mapped along a graded axis", "family": list(FAMILY),
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if p["stratum"] == "w0_solver" and not p["degenerate"]]
    last = CM.committed_last_steps()
    with A.pool(8) as ex:
        res = list(ex.map(job, parents))
    verified, n = 0, 0
    for r in res:
        for w in r["walkers"]:
            ref = last.get((r["parent_id"], w["walker"]))
            n += 1
            if ref and ref["digest"] == w["digest"] and ref["depth"] == w["depth"]:
                verified += 1
    curve = {}
    for k in FAMILY:
        d = [w["per_env"][k]["displacement"] for r in res for w in r["walkers"]]
        rw = [w["per_env"][k]["reward"] for r in res for w in r["walkers"]]
        pr = [w["per_env"][k]["parent_reward"] for r in res for w in r["walkers"]]
        curve[k] = {"displacement_mean": float(np.mean(d)), "displacement_p90": float(np.percentile(d, 90)),
                    "walker_reward_mean": float(np.mean(rw)), "parent_reward_mean": float(np.mean(pr)),
                    "share_displaced_gt_0.25": float(np.mean(np.array(d) > 0.25))}
    material = bool(curve["W1_d1"]["displacement_mean"] > 5 * max(curve["W0"]["displacement_mean"], 1e-3))
    out = {"perturbation_id": PID, "parent": TID, "n_parents": len(parents), "walkers_regenerated": n, "digest_verified": verified,
           "curve": curve, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "silent drift curve (displacement mean): %s; digests verified %d/%d" % ({k: round(v["displacement_mean"], 3) for k, v in curve.items()}, verified, n),
                      material, detail=curve)
    print("DONE verified %d/%d %s (%.0f s)" % (verified, n, {k: round(v["displacement_mean"], 3) for k, v in curve.items()}, time.time() - t0))


if __name__ == "__main__":
    main()
