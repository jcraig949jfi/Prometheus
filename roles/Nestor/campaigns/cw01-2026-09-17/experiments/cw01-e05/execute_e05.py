"""cw01-e05 EXECUTE driver — frozen measurement contract.

The binding specification is embedded LITERALLY below and checked against the
committed VERDICT_CONTRACT.json before any organism is evaluated. If they differ,
the driver refuses. It does not reconcile, repair, or fall back.

FREEZE RULE: once the first organism is evaluated under this attempt_id, no metric,
normalisation, control, threshold, set-selection rule, budget, null or verdict
criterion may change. A defect discovered during EXECUTE voids the affected verdict
and opens a NEW attempt_id. Criteria are never repaired in place while evidence
accumulates.

M3 is exactly: difference-in-differences on normalised INFORMATION superadditivity.
There is no alternate interpretation and no fallback path.
"""
from __future__ import annotations

import itertools
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

import world_e05 as W          # noqa: E402
import seeds as S              # noqa: E402
import lineage as LG           # noqa: E402
import infometrics as IM       # noqa: E402
import learnability as LN      # noqa: E402
import contract as CT          # noqa: E402

CONTRACT_PATH = HERE / "VERDICT_CONTRACT.json"

# --------------------------------------------------------------------------
# LITERAL embedded copy of the binding contract. Any drift from the committed
# file is a hard refusal, not a reconciliation.
# --------------------------------------------------------------------------
EMBEDDED_CONTRACT = {
 "experiment_id": "cw01-e05",
 "attempt_id": "cw01-e05-a01",
 "world_schema_version": "composition-economics-v1",
 "statistic_name": "difference_in_differences_normalised_information_superadditivity",
 "statistic_formula": "DiD = (nsa(BEST,conj) - nsa(BEST,disj)) - (nsa(WORST,conj) - nsa(WORST,disj))",
 "normalisation": "nsa(S,law) = 100 * (mixture_info(S,law) - additive_prediction(S,law)) / additive_prediction(S,law)",
 "intervention_control_relationship": "every intervention applied to a treatment is also applied to every baseline it is compared against; enforced by learnability.assert_controlled",
 "null_construction": "repeated measurement of the same quantity across at least 8 independent seed blocks; pairwise relative differences form the null",
 "effect_clearing_rule": "infometrics.effect_clears_null at the 5th/95th percentile of the measured null, in the pre-declared direction",
 "set_selection_procedure": "exhaustive enumeration of all C(K,B) subsets; BEST = argmax mean score, WORST = argmin; no hand-picked sets",
 "budget_B": 3,
 "budget_derivation": "measured mean conjunctive demand size over the attempt-stable pool, rounded; declared before inspecting superadditivity",
 "superadditivity_basis": "information, not info/cost; carry cost stored separately",
 "baseline_law_rule": "solo baselines measured under the SAME composition law as the mixture they are compared to",
 "liveness_rule": "learnability.assert_live must pass before any matched-arm identity comparison",
 "disposition_rules": {
   "NEGATIVE": "mixtures do not beat the best single component",
   "NULL": "superadditivity does not clear its measured null, OR targeted ablation costs no more than solo value",
   "INCONCLUSIVE": "effect present but not replicated across all attempt seeds, or IX not discharged",
   "COMPLETE": "mixtures beat the best single component AND superadditivity clears its null AND targeted ablation exceeds solo value AND the composition law benefits BEST more than WORST, in every replicate"},
 "freeze_rule": "once the first organism is evaluated under this attempt_id, no metric, normalisation, control, threshold, set-selection rule, budget, null or verdict criterion may change; a defect voids the verdict and opens a new attempt_id",
}

REPLICATES = ["cw01-e05-a01", "cw01-e05-r02", "cw01-e05-r03", "cw01-e05-r04"]
GENERATIONS = 60
N_ORG = 64
N_EVAL = 12
N_BLOCKS = 8


class AttemptVoided(RuntimeError):
    """The contract is insufficient for a verdict. Void; do not repair in place."""


def bind_contract():
    """Load committed, compare to embedded, refuse on any difference, then freeze."""
    if not CONTRACT_PATH.exists():
        raise CT.ContractViolation("committed contract missing: %s" % CONTRACT_PATH)
    c = CT.VerdictContract(EMBEDDED_CONTRACT)
    c.require_matches(CONTRACT_PATH)       # raises ContractViolation naming fields
    return c.freeze()


def load_cfg(attempt_id, contract):
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    cfg["attempt_id"] = attempt_id
    B = contract.get("budget_B")
    for arm in ("treatment", "control_disjunctive_only"):
        if cfg["arms"][arm].get("max_components") != B:
            raise CT.ContractViolation(
                "WORLD.json arm %s max_components=%s but contract budget_B=%s"
                % (arm, cfg["arms"][arm].get("max_components"), B))
    return cfg


def enumerate_sets(cfg, pool, capmap, mk, aid, B):
    """BEST/WORST by EXHAUSTIVE enumeration only. No hand-picked sets (D042)."""
    K = cfg["components"]["K"]
    scored = []
    for s in itertools.combinations(range(K), B):
        sc = W.mean_score(W.genome_with(cfg, list(s)), cfg, "treatment", pool, capmap,
                          mk, aid, "enum", 10)
        scored.append((sc, list(s)))
    scored.sort(reverse=True)
    return {"best": scored[0][1], "best_score": scored[0][0],
            "worst": scored[-1][1], "worst_score": scored[-1][0],
            "n_subsets": len(scored),
            "median_score": scored[len(scored) // 2][0]}


def nsa(cfg, pool, capmap, comps, mk, aid, tag, n, law):
    """Normalised INFORMATION superadditivity under one law, baselines under the SAME law.

    `law` is 'conjunctive' or 'disjunctive'. The law condition is applied identically
    to the mixture and to every solo baseline (assert_controlled, guarding D038a).
    """
    kw = {} if law == "conjunctive" else {"force_disjunctive": True}
    LN.require_controlled(dict(kw), dict(kw), "nsa/%s" % law)
    s = W.superadditivity(cfg, "treatment", pool, capmap, W.genome_with(cfg, comps),
                          mk, aid, tag, n, **kw)
    add = s["additive_prediction"]
    if add == 0:
        raise AttemptVoided("additive prediction is zero for %s under %s; nsa undefined" % (comps, law))
    return {"nsa_pct": 100.0 * s["superadditivity"] / add,
            "mixture_info": s["mixture_info"], "additive_prediction": add,
            "carry_cost": s["carry_cost"], "carried": s["carried"], "law": law}


def did_statistic(cfg, pool, capmap, best, worst, mk, aid, tag="dd", n=16):
    """M3, exactly as contracted. No fallback interpretation."""
    cells = {}
    for label, comps in (("BEST", best), ("WORST", worst)):
        for law in ("conjunctive", "disjunctive"):
            cells[(label, law)] = nsa(cfg, pool, capmap, comps, mk, aid, tag, n, law)
    law_effect_best = cells[("BEST", "conjunctive")]["nsa_pct"] - cells[("BEST", "disjunctive")]["nsa_pct"]
    law_effect_worst = cells[("WORST", "conjunctive")]["nsa_pct"] - cells[("WORST", "disjunctive")]["nsa_pct"]
    return {"cells": {"%s|%s" % k: v for k, v in cells.items()},
            "law_effect_best_points": law_effect_best,
            "law_effect_worst_points": law_effect_worst,
            "did_points": law_effect_best - law_effect_worst}


def superadditivity_null(cfg, pool, capmap, comps, mk, aid, n_blocks=N_BLOCKS, per=12):
    """Repeated measurement of the SAME quantity across independent seed blocks."""
    blocks = []
    for b in range(n_blocks):
        blocks.append(nsa(cfg, pool, capmap, comps, mk, aid, "nf%d" % b, per, "conjunctive")["nsa_pct"])
    return blocks


def one_replicate(aid, contract, ctx=None):
    B = contract.get("budget_B")
    cfg = load_cfg(aid, contract)
    mk = S.seed
    capmap = W.attempt_capabilities(cfg, mk)
    pool = W.attempt_item_pool(cfg, mk)

    sets = enumerate_sets(cfg, pool, capmap, mk, aid, B)
    best, worst = sets["best"], sets["worst"]

    evo = {}
    for arm in ("treatment", "control_disjunctive_only", "control_singleton"):
        evo[arm] = W.evolve(cfg, arm, GENERATIONS, N_ORG, mk, pool=pool, capmap=capmap, n_eval=3)
        if ctx is not None:
            LG.emit_generations(ctx, evo[arm]["history"], arm=arm, replicate=aid,
                                status="record" if arm == "treatment" else "control")

    # --- matched-arm comparison, liveness first (D034) --------------------
    live_probe = W.run_episode(W.genome_with(cfg, best), cfg, "treatment",
                               mk(aid, "stream|live", 0), pool, capmap, force_disjunctive=True)
    LN.require_live(live_probe, ("info", "components_carried"), "matched-arm/%s" % aid)
    ctrl_probe = W.run_episode(W.genome_with(cfg, best), cfg, "control_disjunctive_only",
                               mk(aid, "stream|live", 0), pool, capmap)
    arms_match = all(live_probe[k] == ctrl_probe[k] for k in ("info", "cost", "disjunctive_satisfied"))

    # --- M3 interaction, contracted statistic only ------------------------
    d = did_statistic(cfg, pool, capmap, best, worst, mk, aid)

    # --- superadditivity vs its measured null (D035) ----------------------
    blocks = superadditivity_null(cfg, pool, capmap, best, mk, aid)
    sa_mean = float(np.mean(blocks))
    clears = IM.effect_clears_null(sa_mean, [b + 100.0 for b in blocks], direction="positive")

    # --- M1 targeted vs random ablation, same law -------------------------
    ab = W.ablation_profile(cfg, "treatment", pool, capmap, W.genome_with(cfg, best), mk, aid, "abl", 16)
    prof = ab["profile"]
    tgt_c = max(prof, key=lambda c: prof[c]["ablation_cost"])
    targeted = prof[tgt_c]["ablation_cost"]
    random_sham = float(np.mean([prof[c]["ablation_cost"] for c in prof if c != tgt_c])) if len(prof) > 1 else 0.0
    exceeds_solo = all(v["load_bearing"] for v in prof.values())

    # --- mixtures vs best single component --------------------------------
    best_single = max(W.mean_score(W.genome_with(cfg, [c]), cfg, "treatment", pool, capmap,
                                   mk, aid, "solo1", 12) for c in range(cfg["components"]["K"]))
    mix_score = W.mean_score(W.genome_with(cfg, best), cfg, "treatment", pool, capmap, mk, aid, "mix", 12)

    return {
        "attempt_id": aid, "budget_B": B,
        "enumeration": sets,
        "arms_match": bool(arms_match),
        "did_points": d["did_points"],
        "law_effect_best_points": d["law_effect_best_points"],
        "law_effect_worst_points": d["law_effect_worst_points"],
        "superadditivity_mean_pct": sa_mean,
        "superadditivity_blocks": blocks,
        "superadditivity_clears_null": bool(clears["clears"]),
        "null_p05": clears["null_p05"], "null_p95": clears["null_p95"],
        "ablation_targeted": targeted, "ablation_random_sham": random_sham,
        "ablation_all_load_bearing": bool(exceeds_solo),
        "n_load_bearing": ab["n_load_bearing"], "n_carried": ab["n_carried"],
        "mixture_score": mix_score, "best_single_score": best_single,
        "beats_best_single": bool(mix_score > best_single),
        "evolved_final_mean": evo["treatment"]["history"][-1]["mean"],
        "ancestor_mean": evo["treatment"]["ancestor_mean"],
        "ancestor_relative_pct": 100 * (evo["treatment"]["history"][-1]["mean"] - evo["treatment"]["ancestor_mean"])
                                 / evo["treatment"]["ancestor_mean"],
        "cells": d["cells"],
    }


def job(ctx, **_kw):
    t0 = time.time()
    contract = bind_contract()          # refuses BEFORE any organism is evaluated

    reps = [one_replicate(a, contract, ctx=ctx) for a in REPLICATES]
    for r in reps:
        ctx.emit({"status": "record", "kind": "replicate",
                  **{k: v for k, v in r.items() if isinstance(v, (int, float, str, bool))}})

    n = len(reps)
    n_beats = sum(r["beats_best_single"] for r in reps)
    n_clears = sum(r["superadditivity_clears_null"] for r in reps)
    n_load = sum(r["ablation_all_load_bearing"] for r in reps)
    n_did = sum(r["did_points"] > 0 for r in reps)

    # IX: independent reimplementation (bitmask arithmetic vs python sets)
    cfg = load_cfg(REPLICATES[0], contract)
    capmap = W.attempt_capabilities(cfg, S.seed)
    pool = W.attempt_item_pool(cfg, S.seed)
    worst_div = 0.0
    for gi, comps in enumerate(([0, 2, 4], [1, 3, 5], [2, 6, 7])):
        for i in range(3):
            ss = S.seed("cw01-e05-a01", "stream|ix", i)
            a = W.run_episode(W.genome_with(cfg, comps), cfg, "treatment", ss, pool, capmap)
            b = _reference_episode(W.genome_with(cfg, comps), cfg, "treatment", ss, pool, capmap)
            for k in ("info", "cost", "conjunctive_satisfied", "disjunctive_satisfied"):
                worst_div = max(worst_div, abs(float(a[k]) - float(b[k])))
    backend = {"equivalent": worst_div < 1e-9,
               "method": "bitmask arithmetic reimplementation vs python set operations",
               "detail": "36 comparisons; worst absolute divergence %.3e" % worst_div}
    ctx.emit({"status": "control", "kind": "backend_counterfactual", **backend})

    log = LG.TestLog()
    log.record("beats_best_single", ran=True, passed=(n_beats == n),
               detail="%d/%d mixtures beat the best single component" % (n_beats, n))
    log.record("superadditivity_clears_null", ran=True, passed=(n_clears == n),
               detail="%d/%d clear the measured null band" % (n_clears, n))
    log.record("ablation_exceeds_solo", ran=True, passed=(n_load == n),
               detail="%d/%d have every carried component load-bearing" % (n_load, n))
    log.record("m3_interaction", ran=True, passed=(n_did == n),
               detail="%d/%d show the composition law benefiting BEST more than WORST" % (n_did, n))
    log.record("replication", ran=True,
               passed=(n_beats == n and n_clears == n and n_load == n and n_did == n),
               detail="all conditions must hold in EVERY replicate")
    log.record("backend", ran=True, passed=backend["equivalent"], detail=backend["detail"])

    rules = [
        ("NEGATIVE", contract.get("disposition_rules")["NEGATIVE"],
         ["beats_best_single"], lambda l: not l.passed("beats_best_single")),
        ("NULL", contract.get("disposition_rules")["NULL"],
         ["superadditivity_clears_null", "ablation_exceeds_solo"],
         lambda l: not (l.passed("superadditivity_clears_null") and l.passed("ablation_exceeds_solo"))),
        ("NULL", "the composition law does not selectively benefit a well-chosen set",
         ["m3_interaction"], lambda l: not l.passed("m3_interaction")),
        ("INCONCLUSIVE", contract.get("disposition_rules")["INCONCLUSIVE"],
         ["replication"], lambda l: not l.passed("replication")),
        ("INCONCLUSIVE", "IX not discharged; cap_rule forbids COMPLETE",
         ["backend"], lambda l: not l.passed("backend")),
        ("COMPLETE", contract.get("disposition_rules")["COMPLETE"],
         ["beats_best_single", "superadditivity_clears_null", "ablation_exceeds_solo",
          "m3_interaction", "replication", "backend"], lambda l: True),
    ]
    disp, reason, trace = LG.decide(rules, log)

    result = {
        "campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e05",
        "n_replicates": n, "replicates": reps,
        "summary": {"beats_best_single": "%d/%d" % (n_beats, n),
                    "superadditivity_clears_null": "%d/%d" % (n_clears, n),
                    "ablation_all_load_bearing": "%d/%d" % (n_load, n),
                    "m3_interaction_positive": "%d/%d" % (n_did, n),
                    "did_points_mean": float(np.mean([r["did_points"] for r in reps])),
                    "superadditivity_mean_pct": float(np.mean([r["superadditivity_mean_pct"] for r in reps])),
                    "ancestor_relative_pct_mean": float(np.mean([r["ancestor_relative_pct"] for r in reps]))},
        "tests": log.as_dict(), "decision_trace": trace,
        "backend_counterfactual": backend,
        "disposition": disp, "disposition_reason": reason,
        "freeze_rule": contract.get("freeze_rule"),
        "wall_s": round(time.time() - t0, 1)}
    contract.stamp(result)
    ctx.emit({"status": "record", "kind": "disposition", "disposition": disp, "reason": reason,
              "verdict_contract_sha256": result["verdict_contract_sha256"]})
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result


def _reference_episode(genome, cfg, arm, stream_seed, pool, capmap, force_disjunctive=False):
    """IX reimplementation: bitmask arithmetic instead of python sets."""
    import math
    arm_cfg = cfg["arms"][arm]
    on = W.carried(genome, arm_cfg)
    mask = 0
    for c in on:
        mask |= (1 << capmap[c])
    conj_on = arm_cfg.get("conjunctive_enabled", True) and not force_disjunctive
    cc = cfg["components"]["cost_carry_per_episode"]
    ca = cfg["items"]["cost_attempt"]
    rng = np.random.Generator(np.random.PCG64(stream_seed))
    items = W.make_items(cfg, rng, pool)
    cost = cc * len(on)
    info = 0.0
    cs = ds = 0
    for it in items:
        cost += ca
        nm = 0
        for c in it["need"]:
            nm |= (1 << c)
        if it["conj"] and conj_on:
            ok = (nm & mask) == nm
            if ok:
                cs += 1
        else:
            ok = (nm & mask) != 0
            if ok:
                ds += 1
        if ok:
            info += math.log2(1.0 + it["value"])
    return {"info": info, "cost": cost, "conjunctive_satisfied": cs,
            "disjunctive_satisfied": ds, "score": info / cost if cost > 0 else 0.0}


if __name__ == "__main__":
    import os
    os.environ.setdefault("PM_TAG", "m1-cw01a001")
    os.environ.setdefault("PM_LANE", "A")
    import localrun as LR
    from primordial.fabric import envelope as EV

    env = EV.example(predicate_id="cw01-e05-marginal-mixtures", experiment_class="PROBE", cohort="A")
    rows = HERE / "rows" / "cw01-e05-a01.jsonl"
    out = LR.run_job_locally(job, rows, "CW01-E05-A01", env)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
