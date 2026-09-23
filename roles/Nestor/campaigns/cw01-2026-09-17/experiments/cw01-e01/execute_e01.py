"""cw01-e01 EXECUTE driver — the pre-registered minimal form.

Runs, in order:
  1. evolution in three matched arms (treatment, control_no_retention, control_no_recurrence)
  2. ancestor contrast: evolved population vs its own ancestors under identical streams
  3. post-hoc I1_erase vs its cost-matched sham on the EVOLVED treatment population
  4. backend counterfactual: mem vs redis, identical seeds, identical metric vectors (IX)

Emits durable rows through localrun (RowWriter, git-committed, no Redis needed for
the science path) and writes RESULT.json with a disposition chosen by the rules
fixed in PREREGISTRATION.md — not by whatever the numbers turn out to be.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

BASE = pathlib.Path(__file__).resolve().parents[2]          # campaigns/cw01-2026-09-17
REPO = BASE.parents[3]                                      # worktree root
for p in (str(REPO), str(BASE / "lib"), str(pathlib.Path(__file__).parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

import world_e01 as W                                        # noqa: E402
from seeds import seed as mkseed                             # noqa: E402

ATTEMPT = "cw01-e01-a01"
N_INTERVENTION_STREAMS = 32


def load_cfg():
    cfg = json.loads((pathlib.Path(__file__).parent / "WORLD.json").read_text(encoding="utf-8"))
    cfg["attempt_id"] = ATTEMPT
    return cfg


def episode(g, cfg, arm, tag, i, **kw):
    return W.run_episode(g, cfg, arm, mkseed(ATTEMPT, f"stream|{tag}", i),
                         policy_seed=mkseed(ATTEMPT, f"policy|{tag}", i), **kw)


def mean_of(rs, k):
    return float(np.mean([r[k] for r in rs]))


def job(ctx, generations=40, n_org=64):
    cfg = load_cfg()
    t0 = time.time()
    result = {"attempt_id": ATTEMPT, "generations": generations, "n_org": n_org, "arms": {}}

    # ---- 1. evolution in three matched arms ---------------------------------
    evo = {}
    for arm in ("treatment", "control_no_retention", "control_no_recurrence"):
        evo[arm] = W.evolve(cfg, arm, generations, n_org, mkseed=mkseed)
        h = evo[arm]["history"]
        for row in h:
            ctx.emit({"status": "record" if arm == "treatment" else "control",
                      "kind": "generation", "arm": arm, **row})
        result["arms"][arm] = {
            "ancestor_mean": evo[arm]["ancestor_mean"],
            "final_mean": h[-1]["mean"], "final_best": h[-1]["best"],
            "ancestor_relative": h[-1]["ancestor_relative"],
            "final_reentries": h[-1]["mean_reentries"],
            "final_p_write": h[-1]["mean_p_write"],
            "final_p_reenter": h[-1]["mean_p_reenter"],
            "final_persist": h[-1]["mean_persist"],
        }

    # ---- 2. ancestor contrast under identical streams -----------------------
    contrast = {}
    for arm in evo:
        anc = [episode(g, cfg, arm, "contrast", i) for i, g in enumerate(evo[arm]["ancestor_pop"])]
        fin = [episode(g, cfg, arm, "contrast", i) for i, g in enumerate(evo[arm]["final_pop"])]
        a, f = mean_of(anc, "score"), mean_of(fin, "score")
        contrast[arm] = {"ancestor": a, "evolved": f,
                         "delta_pct": 100 * (f - a) / a if a else 0.0,
                         "anc_reentries": mean_of(anc, "re_entries"),
                         "evo_reentries": mean_of(fin, "re_entries")}
        ctx.emit({"status": "record", "kind": "ancestor_contrast", "arm": arm, **contrast[arm]})
    result["ancestor_contrast"] = contrast

    # ---- 3. post-hoc interventions on the EVOLVED treatment population ------
    pop = evo["treatment"]["final_pop"]
    iv = {}
    for name, arg in (("baseline", None), ("I1_sham", "I1_sham"), ("I1_erase", "I1_erase")):
        rs = [episode(pop[i % len(pop)], cfg, "treatment", "iv", i, intervention=arg)
              for i in range(N_INTERVENTION_STREAMS)]
        iv[name] = {"score": mean_of(rs, "score"), "re_entries": mean_of(rs, "re_entries"),
                    "info": mean_of(rs, "info"), "cost": mean_of(rs, "cost"),
                    "scores": [r["score"] for r in rs]}
        ctx.emit({"status": "control" if name != "baseline" else "record",
                  "kind": "intervention", "arm": "treatment", "intervention": name,
                  **{k: v for k, v in iv[name].items() if k != "scores"}})

    e = np.array(iv["I1_erase"]["scores"]); s = np.array(iv["I1_sham"]["scores"])
    paired = e - s
    result["dependence"] = {
        "erase_minus_sham_pct": float(100 * (e.mean() - s.mean()) / s.mean()),
        "paired_mean": float(paired.mean()), "paired_sd": float(paired.std(ddof=1)),
        "negative_in": f"{int((paired < 0).sum())}/{len(paired)}",
        "n_streams": N_INTERVENTION_STREAMS,
    }
    result["interventions"] = {k: {kk: vv for kk, vv in v.items() if kk != "scores"}
                               for k, v in iv.items()}

    # ---- 4. backend counterfactual (IX) — lifts the INCONCLUSIVE cap --------
    backend = {"attempted": True, "equivalent": None, "detail": ""}
    try:
        import redis
        r = redis.Redis.from_url("redis://127.0.0.1:6390", decode_responses=True)
        r.ping()
        ns = f"pm:cw01:e01:{ATTEMPT}"
        g0 = pop[0]
        keys = ("score", "info", "cost", "re_entries", "writes", "work_saved", "evicted", "jammed")
        diffs = []
        for i in range(6):
            m = episode(g0, cfg, "treatment", "bx", i)
            r.delete(ns + ":region")
            d = episode(g0, cfg, "treatment", "bx", i, backend="redis", rconn=r, ns=ns)
            r.delete(ns + ":region")
            diffs.append({k: (m[k], d[k]) for k in keys if m[k] != d[k]})
        bad = [d for d in diffs if d]
        backend["equivalent"] = not bad
        backend["detail"] = "identical metric vectors on 6/6 episodes" if not bad else f"DIVERGED: {bad[:2]}"
        ctx.emit({"status": "control", "kind": "backend_counterfactual",
                  "equivalent": backend["equivalent"], "detail": backend["detail"]})
        for k in r.scan_iter(match=ns + "*"):
            r.delete(k)
    except Exception as ex:
        backend["equivalent"] = False
        backend["detail"] = f"not exercised: {type(ex).__name__}: {ex}"
    result["backend_counterfactual"] = backend

    # ---- disposition, by the rules fixed in PREREGISTRATION.md --------------
    tr = contrast["treatment"]["delta_pct"]
    ctl = contrast["control_no_retention"]["delta_pct"]
    beats_control = result["arms"]["treatment"]["final_mean"] > \
        result["arms"]["control_no_retention"]["final_mean"]
    dep = result["dependence"]["paired_mean"] < 0 and \
        int(result["dependence"]["negative_in"].split("/")[0]) >= 0.75 * N_INTERVENTION_STREAMS
    evolved_uses_it = result["arms"]["treatment"]["final_reentries"] > 1.0

    if not beats_control:
        disp = "NEGATIVE"
        why = ("retention-capable lineages did not beat the matched non-retaining control "
               f"(treatment {result['arms']['treatment']['final_mean']:.5f} vs control "
               f"{result['arms']['control_no_retention']['final_mean']:.5f})")
    elif not dep:
        disp = "NULL"
        why = ("an advantage exists but is intervention-insensitive: destroying the retained state did "
               "not cost more than the cost-matched sham, so the advantage was not the machinery")
    elif not evolved_uses_it:
        disp = "NULL"
        why = ("advantage without the mechanism: evolved populations average "
               f"{result['arms']['treatment']['final_reentries']:.2f} re-entries, so retention is not "
               "what they are doing")
    elif not backend["equivalent"]:
        disp = "INCONCLUSIVE"
        why = ("retention-dependent advantage observed, but the backend counterfactual was not "
               f"satisfied ({backend['detail']}); WORLD.json cap_rule forbids COMPLETE")
    else:
        disp = "COMPLETE"
        why = ("retention-dependent advantage: evolved treatment beats the matched non-retaining "
               "control, the evolved population actually uses the mechanism, destroying the retained "
               "state costs more than the cost-matched sham, and the physics survives a backend swap")

    result["disposition"] = disp
    result["disposition_reason"] = why
    result["wall_s"] = round(time.time() - t0, 1)
    result["_honest_limitation"] = (
        "The minimal form evolves a 5-gene policy vector, not a rich program. This can show whether the "
        "ECONOMICS select for retention; it cannot say what machinery a richer organism would invent.")

    ctx.emit({"status": "record", "kind": "disposition", "disposition": disp, "reason": why,
              "wall_s": result["wall_s"]})
    (pathlib.Path(__file__).parent / "RESULT.json").write_text(
        json.dumps(result, indent=1), encoding="utf-8")
    return result


if __name__ == "__main__":
    import os
    os.environ.setdefault("PM_TAG", "m1-cw01a001")
    os.environ.setdefault("PM_LANE", "A")
    import localrun as LR
    from primordial.fabric import envelope as EV

    env = EV.example(predicate_id="cw01-e01-workspace-necessity",
                     experiment_class="PROBE", cohort="A")
    rows = pathlib.Path(__file__).parent / "rows" / "cw01-e01-a01.jsonl"
    out = LR.run_job_locally(job, rows, "CW01-E01-A01", env,
                             kwargs={"generations": 40, "n_org": 64})
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
