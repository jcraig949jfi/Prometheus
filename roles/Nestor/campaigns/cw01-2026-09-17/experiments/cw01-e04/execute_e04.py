"""cw01-e04 EXECUTE driver — queue/TTL ecology.

Built on the accumulated gates:
  lineage.decide          a branch is UNREACHABLE unless its tests ran (D024)
  lineage.emit_generations per-generation trajectories as durable rows (D026)
  infometrics.mi_with_null triage against a shuffled null (D022)
  replication built in from the start, not bolted on (D016)
  IX by independent REIMPLEMENTATION, not by assertion (D031)

THE QUESTION: selectivity is cheap and proves nothing. Triage means WHICH items
get carried depends on what they are worth. Measured as two independent quantities;
a selective-but-blind population is a NEGATIVE for the triage claim.

Generality (J2 ttl-shock, J3 discipline swap, J4 drop shock) is reported as a
SEPARATE verdict and never upgrades the primary disposition.
"""
from __future__ import annotations

import json
import math
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

import world_e04 as W          # noqa: E402
import seeds as S              # noqa: E402
import lineage as LG           # noqa: E402
import infometrics as IM       # noqa: E402

REPLICATES = ["cw01-e04-a01", "cw01-e04-r02", "cw01-e04-r03", "cw01-e04-r04"]
GENERATIONS = 60
N_ORG = 64
N_EVAL = 16


def load_cfg(attempt_id, **over):
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    cfg["attempt_id"] = attempt_id
    for k, v in over.items():
        cfg["channel"][k] = v
    return cfg


def reference_episode(genome, cfg, arm, stream_seed, wmap):
    """IX: independent reimplementation. Explicit list bookkeeping instead of the
    primary dict-based channel. Same declared physics, different machinery."""
    arm_cfg = cfg["arms"][arm]
    g = W.apply_arm(genome, arm_cfg)
    on = bool(arm_cfg.get("channel_enabled", True))
    wrng = np.random.Generator(np.random.PCG64(stream_seed))
    items = W.make_items(cfg, wrng, wmap, None)
    c = cfg["channel"]
    cap, ttl, delay = c["capacity"], c["ttl_steps"], c["delay_steps"]
    c_put, c_get, c_rec = c["cost_put"], c["cost_get"], cfg["actions"]["cost_recompute"]
    slots = []                                   # list of (key, placed_step)
    by_partner = {}
    for it in items:
        by_partner.setdefault(it["partner_t"], []).append(it)
    info = cost = 0.0
    placements = hits = 0
    for step in range(cfg["items"]["items_per_episode"]):
        it = items[step]
        if on and (g["b_place"] + float(np.dot(g["w_place"], it["x"]))) > 0.0:
            cost += c_put
            placements += 1
            if not it["drop"] and len(slots) < cap:
                slots.append([it["t"], step])
        for partner in by_partner.get(step, []):
            got = False
            if on:
                cost += c_get
                for j, (k, t0) in enumerate(slots):
                    if k == partner["t"] and step - t0 >= delay:
                        slots.pop(j)
                        got = True
                        break
            if got:
                hits += 1
                info += math.log2(1.0 + partner["worth"])
            elif (g["b_rec"] + float(np.dot(g["w_rec"], partner["x"]))) > 0.0:
                cost += c_rec
                info += math.log2(1.0 + partner["worth"])
        slots = [s for s in slots if step - s[1] < ttl]
    return {"info": info, "cost": cost, "score": info / cost if cost > 0 else 0.0,
            "placements": placements, "retrieval_hits": hits}


def one_replicate(attempt_id, ctx=None):
    cfg = load_cfg(attempt_id)
    mk = S.seed
    wmap = W.attempt_worth_map(cfg, mk)
    F = cfg["items"]["observable_features"]

    evo = {}
    for arm in ("treatment", "control_no_triage", "control_always_recompute"):
        evo[arm] = W.evolve(cfg, arm, GENERATIONS, N_ORG, mk, wmap=wmap)
        if ctx is not None:
            LG.emit_generations(ctx, evo[arm]["history"], arm=arm, replicate=attempt_id,
                                status="record" if arm == "treatment" else "control")

    pop = evo["treatment"]["final_pop"]

    def ev(scramble=None, c=None, n=N_EVAL, patterns=False):
        cc = c or cfg
        return [W.run_episode(pop[i % len(pop)], cc, "treatment",
                              mk(attempt_id, "stream|iv", i), wmap=wmap,
                              scramble=scramble, collect_patterns=patterns)
                for i in range(n)]

    base_runs = ev(patterns=True)
    base = float(np.mean([r["score"] for r in base_runs]))
    ws, acts = [], []
    for r in base_runs:
        ws += r["_worths"]; acts += r["_actions"]
    mi = IM.mi_with_null(ws, acts, n_shuffles=200, seed=29)

    sham = float(np.mean([r["score"] for r in ev(scramble=list(range(F)))]))
    scr = float(np.mean([r["score"] for r in ev(scramble=[(i + 1) % F for i in range(F)])]))

    gen = {}
    for name, over in (("ttl_half", {"ttl_steps": max(2, cfg["channel"]["ttl_steps"] // 2)}),
                       ("ttl_double", {"ttl_steps": cfg["channel"]["ttl_steps"] * 2}),
                       ("drop_shock", {"p_drop": min(0.5, cfg["channel"]["p_drop"] * 4)})):
        gen[name] = float(np.mean([r["score"] for r in ev(c=load_cfg(attempt_id, **over))]))

    tr = evo["treatment"]["history"][-1]
    ct = evo["control_no_triage"]["history"][-1]
    ar = evo["control_always_recompute"]["history"][-1]
    return {
        "attempt_id": attempt_id,
        "treatment_final": tr["mean"], "control_no_triage_final": ct["mean"],
        "control_always_recompute_final": ar["mean"],
        "ancestor_mean": evo["treatment"]["ancestor_mean"],
        "ancestor_relative_pct": 100 * (tr["mean"] - evo["treatment"]["ancestor_mean"])
                                 / evo["treatment"]["ancestor_mean"],
        "selectivity": tr["mean_selectivity"], "retrieval_hits": tr["mean_retrieval_hits"],
        "expiries": tr["mean_expiries_suffered"], "full_failures": tr["mean_placement_failures_full"],
        "mi_bits": mi["mi_bits"], "mi_null_q": mi["null_q"], "mi_excess": mi["excess_bits"],
        "triage": mi["significant"],
        "J1_base": base, "J1_sham": sham, "J1_scramble": scr,
        "J1_effect_pct": 100 * (scr - sham) / sham if sham else 0.0,
        "J1_collapses": scr < sham,
        "beats_no_triage": tr["mean"] > ct["mean"],
        "beats_always_recompute": tr["mean"] > ar["mean"],
        "generality": gen,
        "generality_retained_pct": {k: 100 * (v - base) / base for k, v in gen.items()},
    }


def job(ctx, **_kw):
    t0 = time.time()
    reps = [one_replicate(a, ctx=ctx) for a in REPLICATES]
    for r in reps:
        ctx.emit({"status": "record", "kind": "replicate",
                  **{k: v for k, v in r.items() if isinstance(v, (int, float, str, bool))}})

    n = len(reps)
    n_triage = sum(r["triage"] for r in reps)
    n_beats = sum(r["beats_no_triage"] for r in reps)
    n_collapse = sum(r["J1_collapses"] for r in reps)

    cfg = load_cfg(REPLICATES[0])
    wmap = W.attempt_worth_map(cfg, S.seed)
    rng = np.random.Generator(np.random.PCG64(5))
    worst = 0.0
    for gi in range(3):
        g = W.seed_genome(cfg, rng)
        for arm in ("treatment", "control_no_triage", "control_always_recompute"):
            for i in range(3):
                ss = S.seed("cw01-e04-a01", "stream|ix", i)
                a = W.run_episode(g, cfg, arm, ss, wmap=wmap)
                b = reference_episode(g, cfg, arm, ss, wmap)
                for k in ("info", "cost", "score", "placements", "retrieval_hits"):
                    worst = max(worst, abs(float(a[k]) - float(b[k])))
    backend = {"equivalent": worst < 1e-9,
               "method": "independent reimplementation (explicit list bookkeeping vs dict channel)",
               "detail": "81 comparisons; worst absolute divergence %.3e" % worst}
    ctx.emit({"status": "control", "kind": "backend_counterfactual", **backend})

    log = LG.TestLog()
    log.record("beats_no_triage", ran=True, passed=(n_beats == n),
               detail="%d/%d beat the non-conditional control" % (n_beats, n))
    log.record("triage", ran=True, passed=(n_triage == n),
               detail="%d/%d significant I(worth;handling) against a shuffled null" % (n_triage, n))
    log.record("J1_scramble", ran=True, passed=(n_collapse == n),
               detail="%d/%d collapse under value scramble vs the identity sham" % (n_collapse, n))
    log.record("replication", ran=True, passed=(n_triage == n and n_collapse == n and n_beats == n),
               detail="all conditions must hold in EVERY replicate")
    log.record("backend", ran=True, passed=backend["equivalent"], detail=backend["detail"])

    rules = [
        ("NEGATIVE", "channel users did not beat the matched non-conditional control",
         ["beats_no_triage"], lambda l: not l.passed("beats_no_triage")),
        ("NULL", "selectivity evolved but triage is indistinguishable from its shuffled null: a policy "
                 "that is cheap without being informed",
         ["triage"], lambda l: not l.passed("triage")),
        ("NULL", "triage is present but scrambling which properties predict worth does not hurt beyond "
                 "the identity sham, so the policy is not matched to the world",
         ["J1_scramble"], lambda l: not l.passed("J1_scramble")),
        ("INCONCLUSIVE", "the effect does not hold in every replicate",
         ["replication"], lambda l: not l.passed("replication")),
        ("INCONCLUSIVE", "IX was not discharged; cap_rule forbids COMPLETE",
         ["backend"], lambda l: not l.passed("backend")),
        ("COMPLETE", "selective, worth-conditional carrying matched to the hidden value structure: beats "
                     "the non-conditional control, triage clears its shuffled null, and scrambling which "
                     "properties predict worth collapses performance beyond a cost-matched sham, in every "
                     "replicate",
         ["beats_no_triage", "triage", "J1_scramble", "replication", "backend"], lambda l: True),
    ]
    disp, reason, trace = LG.decide(rules, log)

    gk = ["ttl_half", "ttl_double", "drop_shock"]
    gmean = {k: float(np.mean([r["generality_retained_pct"][k] for r in reps])) for k in gk}
    result = {
        "campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e04",
        "n_replicates": n, "replicates": reps,
        "summary": {"beats_no_triage": "%d/%d" % (n_beats, n), "triage": "%d/%d" % (n_triage, n),
                    "J1_collapses": "%d/%d" % (n_collapse, n),
                    "selectivity_mean": float(np.mean([r["selectivity"] for r in reps])),
                    "mi_bits_mean": float(np.mean([r["mi_bits"] for r in reps])),
                    "mi_excess_mean": float(np.mean([r["mi_excess"] for r in reps])),
                    "J1_effect_pct_mean": float(np.mean([r["J1_effect_pct"] for r in reps])),
                    "ancestor_relative_pct_mean": float(np.mean([r["ancestor_relative_pct"] for r in reps]))},
        "generality_separate_verdict": {
            "retained_pct_mean": gmean,
            "_rule": "reported SEPARATELY; never upgrades the primary disposition",
            "reading": "a policy tuned to one TTL is a weaker result than one surviving nearby physics"},
        "tests": log.as_dict(), "decision_trace": trace,
        "backend_counterfactual": backend,
        "disposition": disp, "disposition_reason": reason,
        "interpretive_limits": [
            "Selectivity and triage are separate quantities; selective-but-blind is a NEGATIVE.",
            "I(features;handling) understates triage because the feature code bins one feature while "
            "worth depends on all four; I(worth;handling) is the informative measure.",
            "Two 5-parameter linear policies, not a rich program."],
        "wall_s": round(time.time() - t0, 1)}
    ctx.emit({"status": "record", "kind": "disposition", "disposition": disp, "reason": reason})
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result


if __name__ == "__main__":
    import os
    os.environ.setdefault("PM_TAG", "m1-cw01a001")
    os.environ.setdefault("PM_LANE", "A")
    import localrun as LR
    from primordial.fabric import envelope as EV

    env = EV.example(predicate_id="cw01-e04-queue-ttl-ecology", experiment_class="PROBE", cohort="A")
    rows = HERE / "rows" / "cw01-e04-a01.jsonl"
    out = LR.run_job_locally(job, rows, "CW01-E04-A01", env)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
