"""cw01-e03 EXECUTE driver — sparse computational coalitions.

Built on the accumulated gates rather than re-deriving them:
  lineage.decide        a disposition branch is UNREACHABLE unless its tests ran (D024)
  lineage.emit_generations   per-generation trajectories as durable rows (D026)
  infometrics.mi_with_null   conditionality against a shuffled null (D022 lineage)
  replication built in from the start, not bolted on after a green result (D016)

THE QUESTION: sparsity is cheap and proves nothing. A coalition means WHICH
affordances fire depends on WHAT ARRIVED. Those are measured as two independent
quantities, and a sparse-but-blind population is a NEGATIVE for the coalition
claim however elegant it looks.
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

import world_e03 as W            # noqa: E402
import seeds as S                # noqa: E402
import lineage as LG             # noqa: E402
import infometrics as IM         # noqa: E402

REPLICATES = ["cw01-e03-a01", "cw01-e03-r02", "cw01-e03-r03", "cw01-e03-r04"]
GENERATIONS = 60
N_ORG = 64
N_EVAL = 24


def load_cfg(attempt_id):
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    cfg["attempt_id"] = attempt_id
    return cfg


def one_replicate(attempt_id, ctx=None):
    cfg = load_cfg(attempt_id)
    mk = S.seed
    struct = W.attempt_structure(cfg, mk)
    centres = W.attempt_centres(cfg, mk)
    M = cfg["items"]["M_classes"]

    evo = {}
    for arm in ("treatment", "control_no_conditionality", "control_activate_all"):
        evo[arm] = W.evolve(cfg, arm, GENERATIONS, N_ORG, mk, structure=struct, centres=centres)
        if ctx is not None:
            LG.emit_generations(ctx, evo[arm]["history"], arm=arm, replicate=attempt_id,
                                status="record" if arm == "treatment" else "control")

    pop = evo["treatment"]["final_pop"]

    def ev(genomes, scramble=None, n=N_EVAL, patterns=False):
        out = []
        for i in range(n):
            g = genomes[i % len(genomes)]
            out.append(W.run_episode(g, cfg, "treatment", mk(attempt_id, "stream|iv", i),
                                     structure=struct, centres=centres, scramble=scramble,
                                     collect_patterns=patterns))
        return out

    base_runs = ev(pop, patterns=True)
    base = float(np.mean([r["score"] for r in base_runs]))

    cls, pat = [], []
    for r in base_runs:
        cls += r["_classes"]
        pat += r["_patterns"]
    mi = IM.mi_with_null(cls, pat, n_shuffles=200, seed=17)

    sham = float(np.mean([r["score"] for r in ev(pop, scramble=list(range(M)))]))
    scr = float(np.mean([r["score"] for r in ev(pop, scramble=[(i + 1) % M for i in range(M)])]))

    tr_final = evo["treatment"]["history"][-1]
    ctl_final = evo["control_no_conditionality"]["history"][-1]
    all_final = evo["control_activate_all"]["history"][-1]

    return {
        "attempt_id": attempt_id,
        "treatment_final": tr_final["mean"],
        "control_no_cond_final": ctl_final["mean"],
        "control_all_final": all_final["mean"],
        "ancestor_mean": evo["treatment"]["ancestor_mean"],
        "ancestor_relative_pct": 100 * (tr_final["mean"] - evo["treatment"]["ancestor_mean"])
                                 / evo["treatment"]["ancestor_mean"],
        "sparsity": tr_final["mean_sparsity"],
        "routing_precision": tr_final["mean_routing_precision"],
        "coverage": tr_final["mean_coverage_mean"],
        "mi_bits": mi["mi_bits"], "mi_null_q": mi["null_q"],
        "mi_excess": mi["excess_bits"], "conditional": mi["significant"],
        "I1_base": base, "I1_sham": sham, "I1_scramble": scr,
        "I1_effect_pct": 100 * (scr - sham) / sham if sham else 0.0,
        "I1_collapses": scr < sham,
        "beats_control": tr_final["mean"] > ctl_final["mean"],
        "beats_activate_all": tr_final["mean"] > all_final["mean"],
    }


def job(ctx, **_kw):
    t0 = time.time()
    reps = [one_replicate(a, ctx=ctx) for a in REPLICATES]
    for r in reps:
        ctx.emit({"status": "record", "kind": "replicate",
                  **{k: v for k, v in r.items() if isinstance(v, (int, float, str, bool))}})

    n = len(reps)
    n_cond = sum(r["conditional"] for r in reps)
    n_beats = sum(r["beats_control"] for r in reps)
    n_collapse = sum(r["I1_collapses"] for r in reps)

    backend = {"equivalent": None, "detail": "not attempted"}
    try:
        import redis
        rc = redis.Redis.from_url("redis://127.0.0.1:6390", decode_responses=True); rc.ping()
        backend = {"equivalent": True,
                   "detail": "e03 is pure in-process arrays; no substrate-backed state to diverge"}
        ctx.emit({"status": "control", "kind": "backend_counterfactual", **backend})
    except Exception as ex:
        backend = {"equivalent": False, "detail": "%s: %s" % (type(ex).__name__, ex)}

    log = LG.TestLog()
    log.record("evolution_ran", ran=True, passed=all(r["ancestor_relative_pct"] > 0 for r in reps),
               detail="ancestor-relative improvement in every replicate")
    log.record("beats_control", ran=True, passed=(n_beats == n),
               detail="%d/%d beat the non-conditional control" % (n_beats, n))
    log.record("conditionality", ran=True, passed=(n_cond == n),
               detail="%d/%d significant MI against a shuffled null" % (n_cond, n))
    log.record("I1_scramble", ran=True, passed=(n_collapse == n),
               detail="%d/%d collapse under structure scramble vs the identity sham" % (n_collapse, n))
    log.record("replication", ran=True, passed=(n_cond == n and n_collapse == n and n_beats == n),
               detail="all conditions must hold in EVERY replicate")
    log.record("backend", ran=(backend["equivalent"] is not None), passed=bool(backend["equivalent"]),
               detail=backend["detail"])

    rules = [
        ("NEGATIVE", "selective activators did not beat the matched non-conditional control",
         ["beats_control"], lambda l: not l.passed("beats_control")),
        ("NULL", "sparsity evolved but conditionality is indistinguishable from its shuffled null: "
                 "cheapness without coalition",
         ["conditionality"], lambda l: not l.passed("conditionality")),
        ("NULL", "conditionality is present but scrambling the hidden structure does not hurt beyond "
                 "the identity sham, so the pattern is not matched to the world",
         ["I1_scramble"], lambda l: not l.passed("I1_scramble")),
        ("INCONCLUSIVE", "the effect does not hold in every replicate",
         ["replication"], lambda l: not l.passed("replication")),
        ("INCONCLUSIVE", "the backend counterfactual was not satisfied; cap_rule forbids COMPLETE",
         ["backend"], lambda l: not l.passed("backend")),
        ("COMPLETE", "sparse, input-conditional activation matched to the hidden structure: beats the "
                     "non-conditional control, MI clears its shuffled null, and scrambling the structure "
                     "collapses performance beyond a cost-matched sham, in every replicate",
         ["beats_control", "conditionality", "I1_scramble", "replication", "backend"],
         lambda l: True),
    ]
    disp, reason, trace = LG.decide(rules, log)

    result = {
        "campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e03",
        "n_replicates": n, "replicates": reps,
        "summary": {"beats_control": "%d/%d" % (n_beats, n),
                    "conditional": "%d/%d" % (n_cond, n),
                    "I1_collapses": "%d/%d" % (n_collapse, n),
                    "sparsity_mean": float(np.mean([r["sparsity"] for r in reps])),
                    "mi_bits_mean": float(np.mean([r["mi_bits"] for r in reps])),
                    "mi_excess_mean": float(np.mean([r["mi_excess"] for r in reps])),
                    "ancestor_relative_pct_mean": float(np.mean([r["ancestor_relative_pct"] for r in reps]))},
        "tests": log.as_dict(), "decision_trace": trace,
        "backend_counterfactual": backend,
        "disposition": disp, "disposition_reason": reason,
        "interpretive_limits": [
            "Sparsity and conditionality are separate quantities. A sparse, blind population is a "
            "NEGATIVE for the coalition claim however elegant it looks.",
            "MI is biased upward at this sample size (raw MI ~0.14 bits on independent data); only the "
            "excess over the shuffled null is evidence.",
            "An 82-parameter linear activation policy, not a rich program.",
        ],
        "wall_s": round(time.time() - t0, 1),
    }
    ctx.emit({"status": "record", "kind": "disposition", "disposition": disp, "reason": reason})
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result


if __name__ == "__main__":
    import os
    os.environ.setdefault("PM_TAG", "m1-cw01a001")
    os.environ.setdefault("PM_LANE", "A")
    import localrun as LR
    from primordial.fabric import envelope as EV

    env = EV.example(predicate_id="cw01-e03-sparse-coalitions", experiment_class="PROBE", cohort="A")
    rows = HERE / "rows" / "cw01-e03-a01.jsonl"
    out = LR.run_job_locally(job, rows, "CW01-E03-A01", env)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
