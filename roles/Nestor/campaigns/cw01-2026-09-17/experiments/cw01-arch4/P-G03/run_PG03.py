"""P-G03 [T-X15; requires P-G01]: GRADED PERSISTENCE without function destruction.

At every tick boundary the persist policy is applied with probability q, else the state is cleared
(as persist=none would); the clearing pattern comes from a seed shared by the baseline and every
damaged evaluation of the same program and dose (CRN). A dose is ELIGIBLE for a program only if its
reward stays within the band of q=1 and above the floor. Scattered deletion (f .10, 4 draws) at every
eligible dose; loss against that dose's own baseline. Computational scope: integer programs on a
bounded VM.
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
import gate                    # noqa: E402
A, L = CM.A, CM.L
from proteus.foundry.vm import Player, Meter   # noqa: E402
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops   # noqa: E402

PID, TID = "P-G03", "T-X15"
QS, F, DRAWS = (1.0, 0.75, 0.5, 0.25, 0.0), 0.10, 4
FLOOR, BAND = A.C1.FLOOR, A.C1.BAND


def eval_q(m, eps, q, seed):
    """evaluate()'s loop with a probabilistic boundary clear; returns reward_per_ask, answered_share, answers."""
    player = Player(m)
    qrng = A.SplitMix64(A.seed_from("nestor.pg03.clear", A.LOOP_SEED, seed))
    correct = asks = answered = 0
    ans = []
    for ei, ep in enumerate(eps):
        st = player.fresh_state()
        rng = A.SplitMix64(A.seed_from("wse.vmrng", 0, ei))
        for ti, words in enumerate(ep.ticks):
            u = qrng.unit()                                   # drawn at EVERY boundary in every dose (CRN)
            if st["ticks"] > 0 and u >= q:
                st["tape"] = list(player.genome) + [0] * (player.tape_words - player.genome_len)
                st["regs"] = [0] * player.n_regs
            player.begin_tick(st)
            outs, _ = player.run_tick(st, [words], 1, rng, meter=Meter())
            if ti in ep.expected:
                asks += 1
                a = outs[0][0] if outs[0] else None
                ans.append(a)
                if a is not None:
                    answered += 1
                    if a == ep.expected[ti]:
                        correct += 1
    return {"reward": correct / max(1, asks), "answered": answered / max(1, asks), "answers": ans}


def loss_of(base, dmg):
    vals = [x for x in dmg["answers"] if x is not None]
    if dmg["answered"] == 0.0 or (vals and len(set(vals)) == 1 and len(vals) == len(dmg["answers"])):
        return 1
    return int(dmg["reward"] < FLOOR)


def job(j):
    p = j["program"]
    env = p["env"]
    eps = A.episodes(env)
    pm = A.canonical(p["manifest"])
    n = len(pm["genome"]) // A.IW
    seed = p["organism_id"]
    out = {"pid": p["organism_id"], "set": p["stratum"], "n_instr": n, "persist": pm["persist"], "doses": {}}
    b1 = eval_q(pm, eps, 1.0, seed)
    ev = A.evaluate(pm, eps, rng_seed=0, reward_mode="per_ask")
    out["q1_equals_evaluate"] = abs(b1["reward"] - ev["reward_per_ask"]) < 1e-12
    out["persistent_words"] = ev["meter"].get("persistent_state_words", 0)
    for q in QS:
        b = eval_q(pm, eps, q, seed)
        eligible = bool(b["reward"] >= FLOOR and b["reward"] >= b1["reward"] - BAND and b["answered"] > 0)
        d = {"reward": b["reward"], "answered": b["answered"], "disp_from_q1": A.C1.displacement(b["answers"], b1["answers"]), "eligible": eligible}
        if eligible:
            losses, drs = [], []
            for dr in range(1, DRAWS + 1):
                key = (seed, "pg03", F, dr)
                child = SC.apply(pm, SC.mask(n, F, key), "delete", key)
                c = eval_q(child, eps, q, seed)
                losses.append(loss_of(b, c))
                drs.append(c["reward"] - b["reward"])
            d["loss"] = float(np.mean(losses))
            d["dreward"] = float(np.mean(drs))
        out["doses"][str(q)] = d
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-G01"], "scope": CM.SCOPE, "claim_type": "causal-separation",
                         "intervention": {"family": "graded persistence", "geometry": "per tick boundary", "sampling_law": "Bernoulli(1-q) clear of tape and registers", "normalisation": "loss vs the dose's own baseline",
                                          "denominator": "4 draws", "price_assumptions": "none", "viability_floor": FLOOR, "alters_baseline_function": "checked per dose: eligible only inside the band of q=1 and above the floor", "qualification": "q=1 must reproduce evaluate() exactly (harness check)"},
                         "damage_ruler": SC.PROVENANCE, "doses": QS, "f": F, "draws": DRAWS,
                         "readings": {"STATE_CAUSAL": "among programs with >= 2 eligible doses, paired loss(lowest eligible q) - loss(q=1) outside its sign-flip band",
                                      "STATE_ENTANGLED_WITH_FUNCTION": "fewer than 8 programs keep function at any q < 1", "STATE_CORRELATED": "persistent words correlate with loss at q=1 (Spearman clears band) but the dose contrast is inside its band",
                                      "NO_RESIDUAL_STATE_EFFECT": "dose contrast inside band and no correlation"},
                         "material_rule": "reading is STATE_CAUSAL, or the harness check fails (recorded), or STATE_ENTANGLED is itself the finding", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    gate.require_qualified(HERE, PID, TID, ph)
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    with A.pool(8) as ex:
        rows = list(ex.map(job, [{"program": p} for p in programs]))
    harness_ok = all(r["q1_equals_evaluate"] for r in rows)
    elig = {str(q): sum(1 for r in rows if r["doses"][str(q)]["eligible"]) for q in QS}
    reward_by_q = {str(q): float(np.mean([r["doses"][str(q)]["reward"] for r in rows])) for q in QS}
    multi = [r for r in rows if sum(1 for q in QS if q < 1 and r["doses"][str(q)]["eligible"]) >= 1 and r["doses"]["1.0"]["eligible"]]
    diffs, lows = [], []
    for r in multi:
        ql = min(q for q in QS if r["doses"][str(q)]["eligible"])
        lows.append(ql)
        diffs.append(r["doses"][str(ql)]["loss"] - r["doses"]["1.0"]["loss"])
    sf = CM.paired_signflip(diffs)
    loss_by_q = {str(q): float(np.mean([r["doses"][str(q)]["loss"] for r in rows if r["doses"][str(q)].get("loss") is not None])) if any(r["doses"][str(q)].get("loss") is not None for r in rows) else None for q in QS}
    # correlation at q=1: persistent words vs loss
    pw = [r["persistent_words"] for r in rows if r["doses"]["1.0"].get("loss") is not None]
    l1 = [r["doses"]["1.0"]["loss"] for r in rows if r["doses"]["1.0"].get("loss") is not None]

    def spearman_perm(x, y, n=2000):
        x, y = np.asarray(x, float), np.asarray(y, float)
        rk = lambda v: np.argsort(np.argsort(v)).astype(float)   # noqa: E731
        rho = lambda a, b: float(np.corrcoef(rk(a), rk(b))[0, 1])   # noqa: E731
        obs = rho(x, y)
        rng = np.random.Generator(np.random.PCG64(0))
        null = np.array([rho(x, rng.permutation(y)) for _ in range(n)])
        return {"rho": obs, "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)), "clears": bool(obs < np.percentile(null, 5) or obs > np.percentile(null, 95)), "n": int(len(x))}
    corr = spearman_perm(pw, l1) if len(pw) >= 8 else None
    if len(multi) < 8:
        reading = "STATE_ENTANGLED_WITH_FUNCTION"
    elif sf and (sf["above_p95"] or sf["below_p05"]):
        reading = "STATE_CAUSAL"
    elif corr and corr["clears"]:
        reading = "STATE_CORRELATED"
    else:
        reading = "NO_RESIDUAL_STATE_EFFECT"
    material = bool(harness_ok and reading in ("STATE_CAUSAL", "STATE_ENTANGLED_WITH_FUNCTION"))
    out = {"perturbation_id": PID, "parent": TID, "harness_q1_equals_evaluate": harness_ok, "reading": reading if harness_ok else "INVALID_HARNESS", "eligible_by_q": elig, "reward_by_q": reward_by_q, "loss_by_q": loss_by_q,
           "n_programs_with_lower_eligible_dose": len(multi), "lowest_eligible_q_hist": {str(q): lows.count(q) for q in QS}, "dose_contrast": sf, "pw_loss_correlation_q1": corr,
           "by_persist_policy": {pol: {"n": sum(1 for r in rows if r["persist"] == pol), "eligible_below_1": sum(1 for r in rows if r["persist"] == pol and any(r["doses"][str(q)]["eligible"] for q in QS if q < 1))} for pol in ("none", "regs", "tape", "all")},
           "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "graded persistence (q=1 reproduces evaluate: %s): reading %s; eligible by q %s; reward by q %s; loss by q %s; programs with a lower eligible dose %d (lowest q hist %s); dose contrast %s; pw-loss correlation at q=1 %s; by persist policy %s"
                      % (harness_ok, out["reading"], elig, {k: round(v, 3) for k, v in reward_by_q.items()}, {k: (round(v, 3) if v is not None else None) for k, v in loss_by_q.items()}, len(multi), out["lowest_eligible_q_hist"],
                         (round(sf["mean_diff"], 3), sf["n"], sf["above_p95"], sf["below_p05"]) if sf else None, (round(corr["rho"], 3), corr["clears"]) if corr else None, out["by_persist_policy"]), material, detail=out["dose_contrast"] or {})
    print("DONE material=%s reading=%s harness=%s (%.0f s) elig %s reward %s loss %s contrast %s" % (material, out["reading"], harness_ok, time.time() - t0, elig, reward_by_q, loss_by_q, sf))


if __name__ == "__main__":
    main()
