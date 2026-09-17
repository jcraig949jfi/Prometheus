"""B-R6-1: search-budget accounting for B-R5-1 vs the w13 train128 float linear baseline (SWARM_R6 O2, prompts_r6/B.md 1).

The numbers are G-R6-1's reader, never recomputed here: primordial.metric.search_budget.accounting() over COMMITTED rows
(candidate primordial/ledger/rows/B/B-R5-1-cand-int4a4-w13-train128.jsonl, baseline G-R16-baseline.jsonl).

Oracle (oracles_budget_crosscheck): the reader's candidate evals per run must equal two records it does not read --
the B-R5-1 receipt's engineering.qd_genomes_per_run (primordial/ledger/B.jsonl) and the frozen recipe's search_evals
(primordial.metric.replication.RECIPE) -- and each side's search_evals_total must equal runs_total x evals per run.

The job emits ONE row. comparator_fires decides item 2 (the equal-budget float comparator runs only if True). CPU per
run is in neither rows file, so no CPU comparison is claimed.

    python -m primordial.fabric.worker submit B primordial.cohorts.b.r6_1_budget:job ...   (envelope required)
"""
from __future__ import annotations

import json
import pathlib
import time

EXP = "B-R6-1-search-budget-w13-train128"
R5_EXP = "B-R5-1-cand-int4a4-w13-train128"


def r5_receipt_evals(ledger="primordial/ledger/B.jsonl", root=None) -> int | None:
    """engineering.qd_genomes_per_run of the latest committed B-R5-1 receipt, or None."""
    from primordial.metric.r16 import ROOT
    got = None
    for line in (pathlib.Path(root or ROOT) / ledger).read_text(encoding="utf-8").splitlines():
        try:
            x = json.loads(line)
        except ValueError:
            continue
        if isinstance(x, dict) and x.get("exp_id") == R5_EXP and "qd_genomes_per_run" in (x.get("engineering") or {}):
            got = int(x["engineering"]["qd_genomes_per_run"])
    return got


def crosscheck(acc: dict, receipt_evals, recipe_evals) -> dict:
    ce = acc["candidate"]["search_evals_per_run"]
    checks = {"receipt_qd_genomes_per_run": receipt_evals == ce, "recipe_search_evals": recipe_evals == ce}
    for side in ("candidate", "baseline"):
        s = acc[side]
        checks[f"{side}_total_eq_runs_x_per_run"] = s["search_evals_total"] == s["runs_total"] * s["search_evals_per_run"]
    return {"clean": all(checks.values()), "checks": checks,
            "values": {"reader_candidate_evals_per_run": ce, "receipt_qd_genomes_per_run": receipt_evals,
                       "recipe_search_evals": recipe_evals}}


def job(ctx, stage="PRODUCTION"):
    from primordial.metric import replication as RP
    from primordial.metric import search_budget as SB
    t0 = time.perf_counter()
    acc = SB.accounting()
    orc = crosscheck(acc, r5_receipt_evals(), RP.RECIPE["search_budget"]["search_evals"])
    ctx.emit({**acc, "exp_id": EXP, "campaign_stage": stage, "world": "w13", "gen_seed": 13,
              "pressure": "train128_held64", "candidate_receipt": "1789473262958-0",
              "oracles_budget_crosscheck": orc, "cpu_comparison": "NOT_CLAIMED: per-run CPU is in neither rows file",
              "wall_s": round(time.perf_counter() - t0, 3), "ts": round(time.time(), 3), "status": "record"})
