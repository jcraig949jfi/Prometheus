"""cw01-e02 EXECUTE driver — ancestral efficiency ratchet.

Q12: the disposition is computed IN CODE from PREREGISTRATION.md, including the
replication clause. e01's driver hand-wrote four conditions, omitted replication,
and awarded COMPLETE from a single seed (CW01-D016). Replication is built in here
from the start rather than bolted on after a green result.

The ratchet definition, all three conditions required:
  1. TEMPORAL ORDERING  - gain A fixes before gain B appears
  2. SUPERADDITIVE KNOCKOUT - loss(revert A from A+B) > gain(A alone, when it arrived)
  3. ORDER-DEPENDENCE   - B is worth more on the post-A background (K2, expansion)

Minimal form runs conditions 1 and 2 with K1 and its cost-matched sham.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE.parents[3]
for p in (str(REPO), str(BASE / "lib"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import world_e02 as W                       # noqa: E402
import seeds as S                           # noqa: E402

REPLICATES = ["cw01-e02-a01", "cw01-e02-r02", "cw01-e02-r03", "cw01-e02-r04"]
GENERATIONS = 80
N_ORG = 64
N_EVAL = 24


def load_cfg(attempt_id):
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    cfg["attempt_id"] = attempt_id
    return cfg


def attribute_genes(history, gen, baseline_window, persistence, top_k=2):
    """Which genes moved across this gain? Normalised by each gene's own range."""
    before = history[max(0, gen - baseline_window):gen]
    after = history[gen:gen + persistence]
    deltas = {}
    for g, (lo, hi) in W.GENE_BOUNDS.items():
        b = float(np.mean([h["gene_" + g] for h in before]))
        a = float(np.mean([h["gene_" + g] for h in after]))
        deltas[g] = {"pre": b, "post": a, "norm_delta": (a - b) / (hi - lo)}
    ranked = sorted(deltas.items(), key=lambda kv: -abs(kv[1]["norm_delta"]))
    movers = [k for k, _ in ranked if k not in W.NEUTRAL_GENES][:top_k]
    return movers, deltas


def one_replicate(attempt_id):
    cfg = load_cfg(attempt_id)
    gd = cfg["gain_detection"]
    ES, SEP = gd["effect_size_min_pct"], gd["min_sd_separation"]
    PG, BW, OB = gd["persistence_generations"], gd["baseline_window"], gd["ordering_bar_pct"]
    mk = S.seed

    evo = W.evolve(cfg, "treatment", GENERATIONS, N_ORG, mkseed=mk)
    hist = evo["history"]
    gains = W.detect_gains(hist, ES, PG, baseline_window=BW, min_sd_separation=SEP)

    def ev(pop, tag):
        return float(np.mean([
            W.run_episode(pop[i % len(pop)], cfg, "treatment",
                          mk(attempt_id, f"stream|{tag}", i),
                          policy_seed=mk(attempt_id, f"policy|{tag}", i))["score"]
            for i in range(N_EVAL)]))

    out = {"attempt_id": attempt_id, "n_gains": len(gains),
           "gains": [{"gen": g["gen"], "lift_pct": g["lift_pct"],
                      "sd_separation": g["sd_separation"]} for g in gains],
           "ancestor_mean": evo["ancestor_mean"],
           "final_mean": hist[-1]["mean"],
           "ancestor_relative_pct": 100 * (hist[-1]["mean"] - evo["ancestor_mean"]) / evo["ancestor_mean"],
           "final_ordered": hist[-1]["mean_ordered"],
           "final_genes": {g: hist[-1]["gene_" + g] for g in W.GENE_NAMES}}

    # --- conditions 1 and 2 need at least two ordered gains -------------------
    ordering_gains = [g for g in gains if g["lift_pct"] >= OB]
    out["gains_above_ordering_bar"] = len(ordering_gains)
    out["temporal_ordering"] = len(ordering_gains) >= 2

    if not out["temporal_ordering"]:
        out["ratchet"] = False
        out["why"] = (f"only {len(ordering_gains)} gain(s) cleared the ordering bar ({OB}%); "
                      f"condition 1 (temporal ordering) not met")
        return out

    A, B = ordering_gains[0], ordering_gains[1]
    movers_A, deltas_A = attribute_genes(hist, A["gen"], BW, PG)
    out["gain_A"] = {"gen": A["gen"], "lift_pct": A["lift_pct"], "genes": movers_A}
    out["gain_B"] = {"gen": B["gen"], "lift_pct": B["lift_pct"]}

    final = evo["final_pop"]
    base_score = ev(final, "k1base")

    reverted = [dict(p) for p in final]
    for p in reverted:
        for g in movers_A:
            p[g] = deltas_A[g]["pre"]
    k1_score = ev(reverted, "k1base")

    sham = [dict(p) for p in final]
    for p in sham:
        for g in W.NEUTRAL_GENES[:len(movers_A)]:
            p[g] = deltas_A[g]["pre"]
    sham_score = ev(sham, "k1base")

    loss_pct = 100 * (base_score - k1_score) / base_score
    sham_loss_pct = 100 * (base_score - sham_score) / base_score
    out["K1"] = {"base": base_score, "reverted": k1_score, "sham": sham_score,
                 "loss_pct": loss_pct, "sham_loss_pct": sham_loss_pct,
                 "loss_net_of_sham_pct": loss_pct - sham_loss_pct}
    out["gain_A_magnitude_pct"] = A["lift_pct"]
    out["superadditive"] = (loss_pct - sham_loss_pct) > A["lift_pct"]
    out["ratchet"] = bool(out["temporal_ordering"] and out["superadditive"])
    out["why"] = ("reverting gain A costs %.2f%% (net of sham %.2f%%) against gain A's own arrival value "
                  "of %.2f%%" % (loss_pct, sham_loss_pct, A["lift_pct"]))
    return out


def job(ctx, **_kw):
    t0 = time.time()
    reps = [one_replicate(a) for a in REPLICATES]
    for r in reps:
        ctx.emit({"status": "record", "kind": "replicate", **{k: v for k, v in r.items()
                                                              if not isinstance(v, (dict, list))}})

    n = len(reps)
    n_ratchet = sum(r["ratchet"] for r in reps)
    n_beats = sum(r["ancestor_relative_pct"] > 0 for r in reps)
    n_mech = sum(r["final_ordered"] > 1.0 for r in reps)

    backend = {"equivalent": None, "detail": ""}
    try:
        import redis
        r = redis.Redis.from_url("redis://127.0.0.1:6390", decode_responses=True); r.ping()
        ns = "pm:cw01:e02:a01"
        cfg = load_cfg("cw01-e02-a01")
        g0 = W.seed_genome(np.random.Generator(np.random.PCG64(5)))
        keys = ("score", "info", "cost", "t1_applied", "t2_applied", "ordered", "binds")
        bad = []
        for i in range(6):
            m = W.run_episode(g0, cfg, "treatment", S.seed("cw01-e02-a01", "stream|bx", i),
                              policy_seed=S.seed("cw01-e02-a01", "policy|bx", i))
            r.delete(ns + ":region")
            d = W.run_episode(g0, cfg, "treatment", S.seed("cw01-e02-a01", "stream|bx", i),
                              policy_seed=S.seed("cw01-e02-a01", "policy|bx", i),
                              backend="redis", rconn=r, ns=ns)
            r.delete(ns + ":region")
            diff = {k: (m[k], d[k]) for k in keys if m[k] != d[k]}
            if diff:
                bad.append(diff)
        backend["equivalent"] = not bad
        backend["detail"] = "identical metric vectors 6/6" if not bad else f"DIVERGED: {bad[:2]}"
        for k in r.scan_iter(match=ns + "*"):
            r.delete(k)
    except Exception as ex:
        backend["equivalent"] = False
        backend["detail"] = f"not exercised: {type(ex).__name__}: {ex}"
    ctx.emit({"status": "control", "kind": "backend_counterfactual", **backend})

    # ---- disposition, executable, from the pre-registration -----------------
    replicated = (n_ratchet == n)
    if n_beats == 0:
        disp, why = "NEGATIVE", "descendants did not beat their ancestors under matched budgets"
    elif n_mech < n:
        disp, why = "NULL", (f"the mechanism is not in use in {n - n_mech}/{n} replicates "
                             "(ordered transformations ~0)")
    elif n_ratchet == 0:
        disp, why = "NULL", ("gains occur but are ADDITIVE: reverting the earlier gain costs no more "
                             "than that gain was worth, so no later machinery rests on it")
    elif not replicated:
        disp, why = "INCONCLUSIVE", (f"a ratchet signature appears in {n_ratchet}/{n} replicates but "
                                     "does not replicate; PREREGISTRATION requires all")
    elif not backend["equivalent"]:
        disp, why = "INCONCLUSIVE", (f"ratchet replicated but the backend counterfactual failed "
                                     f"({backend['detail']}); WORLD.json cap_rule forbids COMPLETE")
    else:
        disp, why = "COMPLETE", ("ordered gains, superadditive knockout against a cost-matched sham, "
                                 "replicated across all seeds, physics survives a backend swap")

    result = {"campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e02",
              "n_replicates": n, "replicates": reps,
              "summary": {"ratchet": f"{n_ratchet}/{n}", "beats_ancestor": f"{n_beats}/{n}",
                          "mechanism_in_use": f"{n_mech}/{n}",
                          "ancestor_relative_pct_mean": float(np.mean([r["ancestor_relative_pct"] for r in reps])),
                          "gains_mean": float(np.mean([r["n_gains"] for r in reps]))},
              "backend_counterfactual": backend,
              "disposition": disp, "disposition_reason": why,
              "interpretive_limits": [
                  "The ordering is an ENHANCEMENT (+22.66% at QUALIFY), not a PRECONDITION: T2 alone "
                  "already scores +38.11% over nothing. Any ratchet here means the later gain is worth "
                  "MORE on the foundation, not that it is impossible without it.",
                  "Detection floor 12.3% lift. A NULL means 'no ratchet above the floor', never "
                  "'no ratchet'.",
                  "9-gene policy vector, not a rich program.",
              ],
              "wall_s": round(time.time() - t0, 1)}
    ctx.emit({"status": "record", "kind": "disposition", "disposition": disp, "reason": why})
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result


if __name__ == "__main__":
    import os
    os.environ.setdefault("PM_TAG", "m1-cw01a001")
    os.environ.setdefault("PM_LANE", "A")
    import localrun as LR
    from primordial.fabric import envelope as EV

    env = EV.example(predicate_id="cw01-e02-ancestral-ratchet", experiment_class="PROBE", cohort="A")
    rows = HERE / "rows" / "cw01-e02-a01.jsonl"
    out = LR.run_job_locally(job, rows, "CW01-E02-A01", env)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
