"""P-D02 [deformation B]: the DELAY SWITCH probed around its boundary.

Parent T-ARCH4/W1. Programs: w0_solver parents (walkers 1-4), delay_general parents (walkers
1-4), C4-08 ordinary top-16 (walkers 1-2), each walker regenerated on its program's own
environment (C4-05 rules). Environment grid: deterministic delay 0/1/2/4; stochastic per-tag
delay sets (0,1), rare (0,0,0,1), heterogeneous (1,2,3,4); ask_timing 'interleaved' at delay 0
and 1 (the delay attached to a different computational event); interleave 'random'; noise .10 at
delay 0 and 1. Per (walker, environment): displacement of the walker from its program and both
rewards. Per-step trace: for every accepted step of the w0_solver walkers, the W1_d1 displacement
of the child vs the program, to locate the step at which drift becomes loud and its operator /
region / reference facts. Computational scope: integer programs on a bounded VM.
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
import common as CM            # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops   # noqa: E402

PID, TID = "P-D02", "T-ARCH4/W1"
W0 = A.WorldSpec("W0", value_bits=4)
GRID = {"det0": W0, "det1": A.WorldSpec("W1_d1", delay=1, value_bits=4), "det2": A.WorldSpec("W1_d2", delay=2, value_bits=4),
        "det4": A.WorldSpec("W1_d4", delay=4, value_bits=4),
        "stoch01": A.with_knobs(W0, name="Ws01", delays=(0, 1)), "rare0001": A.with_knobs(W0, name="Wrare", delays=(0, 0, 0, 1)),
        "hetero1234": A.with_knobs(W0, name="Whet", delays=(1, 2, 3, 4)),
        "interleaved_d0": A.with_knobs(W0, name="Wi0", ask_timing="interleaved"), "interleaved_d1": A.with_knobs(W0, name="Wi1", ask_timing="interleaved", delay=1),
        "random_order": A.with_knobs(W0, name="Wr", interleave="random"),
        "noise_d0": A.with_knobs(W0, name="Wn0", noise_rate=0.10), "noise_d1": A.with_knobs(W0, name="Wn1", noise_rate=0.10, delay=1)}
LOUD = 0.10


def job(j):
    p = j["program"]
    env = p["env"]
    env_eps = A.episodes(env)
    fam = {k: A.episodes_for(spec, A.CAMPAIGN_SEED, "train", 1, A.C1.E) for k, spec in GRID.items()}
    p_ans = {k: A.C1.answers(p["manifest"], e) for k, e in fam.items()}
    p_rew = {k: A.evaluate(p["manifest"], e, rng_seed=0, reward_mode="per_ask")["reward_per_ask"] for k, e in fam.items()}
    d1_eps = fam["det1"]
    out = []
    for w in range(1, j["walkers"] + 1):
        trace = {}
        cur_holder = {"cur": p["manifest"]}

        def proposal(cur, rng):
            child, rec = A.GR.mutate(cur, rng, mate=None, name=None)
            if "noop" not in (rec.get("args") or {}):
                dg = A.digest(child)
                trace[dg] = {"disp_d1": A.C1.displacement(A.C1.answers(child, d1_eps), p_ans["det1"]),
                             "region": A.C1.region_of(cur, rec["operator"], rec.get("args") or {})}
            return child, rec

        wk = A.C5.walk(p["manifest"], p["organism_id"], w, env_eps, 16, 32, proposal=proposal)
        final = wk["archived"].get(wk["depth"])
        per_env = {}
        for k, e in fam.items():
            an = A.C1.answers(final, e)
            per_env[k] = {"disp": A.C1.displacement(an, p_ans[k]), "reward": A.evaluate(final, e, rng_seed=0, reward_mode="per_ask")["reward_per_ask"], "parent_reward": p_rew[k]}
        loud_step = None
        for s in wk["steps"]:
            t = trace.get(s["digest"])
            if t and t["disp_d1"] > LOUD:
                loud_step = {"depth": s["depth"], "operator": s["operator"], "region": t["region"], "ref_broken": s["ref_broken"], "disp_d1": t["disp_d1"]}
                break
        out.append({"walker": w, "depth": wk["depth"], "per_env": per_env, "loud_step": loud_step,
                    "step_disp_d1": [trace.get(s["digest"], {}).get("disp_d1") for s in wk["steps"]]})
    return {"pid": p["organism_id"], "set": p["stratum"], "walkers": out}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "B", "scope": CM.SCOPE, "claim_type": "parameterized-switch-probe",
                         "grid": list(GRID), "programs": "w0_solver parents (4 walkers), delay_general parents (4 walkers), C4-08 ordinary top-16 seed 1 (2 walkers)",
                         "held_fixed": "walk seeds and rules, displacement ruler, episodes (CRN)", "attacks": "zero-vs-nonzero delay discontinuity (P-C14): causal delay or a hidden state transition exposed by any timing change?",
                         "trace": "W1_d1 displacement of every accepted step; loud = first step with displacement > %.2f" % LOUD,
                         "continuation": ["revert-and-replay ablation of the loud step", "delay on PUT vs ASK", "combined noise x delay dose", "C5 representation B walkers"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    vp = [p for p in CM.viable_parents() if not p["degenerate"]]
    jobs = [{"program": dict(p, stratum="w0_solver"), "walkers": 4} for p in vp if p["stratum"] == "w0_solver"]
    jobs += [{"program": dict(p, stratum="delay_general"), "walkers": 4} for p in vp if p["stratum"] == "delay_general"]
    jobs += [{"program": p, "walkers": 2} for p in c408_tops(n=16)]
    with A.pool(8) as ex:
        res = list(ex.map(job, jobs))
    curve = {}
    for st in ("w0_solver", "delay_general", "c408_ordinary"):
        curve[st] = {}
        for k in GRID:
            d = [w["per_env"][k]["disp"] for r in res if r["set"] == st for w in r["walkers"]]
            rw = [w["per_env"][k]["reward"] for r in res if r["set"] == st for w in r["walkers"]]
            pr = [w["per_env"][k]["parent_reward"] for r in res if r["set"] == st for w in r["walkers"]]
            if d:
                curve[st][k] = {"disp_mean": float(np.mean(d)), "disp_p90": float(np.percentile(d, 90)), "walker_reward": float(np.mean(rw)), "parent_reward": float(np.mean(pr)), "n": len(d)}
    loud = [w["loud_step"] for r in res if r["set"] == "w0_solver" for w in r["walkers"]]
    loud_depth = [x["depth"] for x in loud if x]
    loud_ops = Counter(x["operator"] for x in loud if x)
    loud_regions = Counter(x["region"] for x in loud if x)
    loud_ref = float(np.mean([x["ref_broken"] for x in loud if x])) if any(loud) else None
    w0 = curve["w0_solver"]
    material = bool(w0["det1"]["disp_mean"] > 5 * max(w0["det0"]["disp_mean"], 1e-3) and (w0["stoch01"]["disp_mean"] > 0.05 or w0["rare0001"]["disp_mean"] > 0.05 or w0["interleaved_d0"]["disp_mean"] > 0.05))
    out = {"perturbation_id": PID, "parent": TID, "curve": curve,
           "loud_step": {"n_walkers": len(loud), "n_loud": sum(1 for x in loud if x), "depth_median": (float(np.median(loud_depth)) if loud_depth else None),
                         "depth_hist": dict(Counter(loud_depth)), "operators": dict(loud_ops), "regions": dict(loud_regions), "ref_broken_share": loud_ref},
           "material": material, "elapsed_s": round(time.time() - t0, 1),
           "per_walker": [{"pid": r["pid"], "set": r["set"], "walkers": [{k: v for k, v in w.items() if k != "per_env"} for w in r["walkers"]]} for r in res]}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "delay switch grid (w0 walkers, displacement): %s; loud step depth median %s, ops %s, regions %s, ref_broken %s"
                      % ({k: round(v["disp_mean"], 3) for k, v in w0.items()}, out["loud_step"]["depth_median"], dict(loud_ops), dict(loud_regions), loud_ref),
                      material, detail=out["loud_step"] | {"curve_w0": w0})
    print("DONE material=%s (%.0f s) w0 %s | loud %s" % (material, time.time() - t0, {k: round(v["disp_mean"], 3) for k, v in w0.items()}, out["loud_step"]))


if __name__ == "__main__":
    main()
