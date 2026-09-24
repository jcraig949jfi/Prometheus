"""G-R6-1 (round 6 R6-BUILD, builder G): search-budget accounting for Clause A (SWARM_R6 O2, operator 21).

Fields (G 1789479722885-0, accepted A 1789479784674-0), top-level on every new Clause A run row, summary and receipt:
  search_generations, search_batch, search_evals (= generations x batch), search_train_episodes (evals x train seeds),
  search_cpu_s (child CPU of the search; None when not measured), search_wall_s.

The reader computes, from COMMITTED rows only, the candidate's and the baseline's search effort, and decides the O2
rule fixed before the round: the equal-search-budget float comparator on w13 runs this round iff
candidate evals per run > baseline evals per run. Both interpretations are reported either way.

    python -m primordial.metric.search_budget          # B-R5-1 vs the w13 train128 R16 baseline
"""
from __future__ import annotations

import json

import numpy as np

from primordial.metric import r16 as R

B_R5_1_ROWS = "primordial/ledger/rows/B/B-R5-1-cand-int4a4-w13-train128.jsonl"
W13 = (13, "train128_held64")
TRAIN_SEEDS = {"train8_held64": 8, "train128_held64": 128}


def fields(gens: int, batch: int, pressure: str, cpu_s=None, wall_s=None) -> dict:
    evals = int(gens) * int(batch)
    return {"search_generations": int(gens), "search_batch": int(batch), "search_evals": evals,
            "search_train_episodes": evals * TRAIN_SEEDS[pressure],
            "search_cpu_s": None if cpu_s is None else float(cpu_s), "search_wall_s": None if wall_s is None else float(wall_s)}


def _account(runs: list[dict], pressure: str, label: str, rows: str, cpu_total=None, cpu_basis=None) -> dict:
    if not runs:
        raise ValueError(f"no run rows for {label} in {rows}")
    per = [fields(x["gens"], x["batch"], pressure, wall_s=x.get("qd_wall_s")) for x in runs]
    evals = sorted({p["search_evals"] for p in per})
    fams = sorted({int(x["rng_family"]) for x in runs})
    walls = [p["search_wall_s"] for p in per if p["search_wall_s"] is not None]
    return {"label": label, "rows": rows, "runs_total": len(runs), "rng_family_count": len(fams),
            "runs_per_family": (len(runs) // len(fams)) if len(runs) % len(fams) == 0 else None,
            "families": fams, "search_generations_per_run": sorted({p["search_generations"] for p in per}),
            "search_batch_per_run": sorted({p["search_batch"] for p in per}),
            "search_evals_per_run": evals[0] if len(evals) == 1 else evals,
            "search_evals_total": int(sum(p["search_evals"] for p in per)),
            "search_train_episodes_total": int(sum(p["search_train_episodes"] for p in per)),
            "search_wall_s_total": round(float(np.sum(walls)), 2) if walls else None,
            "search_cpu_s_total": cpu_total, "search_cpu_s_basis": cpu_basis}


def candidate_b_r5_1(rows=B_R5_1_ROWS) -> dict:
    rr = R._rows(rows)
    runs = [x for x in rr if x.get("kind") == "run"]
    cand = [x for x in rr if x.get("kind") == "candidate"]
    return _account(runs, W13[1], "candidate B-R5-1 int4a4 16 B", rows,
                    cpu_total=None, cpu_basis="not in rows (B's receipt reports cpu_s 1637.3 for the job)")


def baseline_w13(rows=R.ROWS["baseline"]) -> dict:
    runs = [x for x in R._rows(rows) if x.get("kind") == "run" and x.get("family") == "linear" and "rng_family" in x
            and (int(x["gen_seed"]), x["pressure"]) == W13]
    from primordial.metric.r16_cells import CPU_PER_WALL
    acc = _account(runs, W13[1], "baseline R16 float linear 200 B", rows)
    if acc["search_wall_s_total"] is not None:
        acc["search_cpu_s_total"] = round(acc["search_wall_s_total"] * CPU_PER_WALL, 1)
        acc["search_cpu_s_basis"] = "ESTIMATED: qd wall x measured J2 CPU/wall ratio (no per-run CPU in rows)"
    return acc


def accounting(cand=None, base=None) -> dict:
    cand = cand or candidate_b_r5_1()
    base = base or baseline_w13()
    ce, be = cand["search_evals_per_run"], base["search_evals_per_run"]
    if isinstance(ce, list) or isinstance(be, list):
        raise ValueError(f"search_evals_per_run is not constant: candidate {ce}, baseline {be}")
    fires = ce > be
    return {"kind": "search_budget_accounting", "cell": {"world": "w13", "pressure": W13[1]},
            "candidate": cand, "baseline": base,
            "ratio_evals_per_run": ce / be, "ratio_evals_total": cand["search_evals_total"] / base["search_evals_total"],
            "ratio_train_episodes_total": cand["search_train_episodes_total"] / base["search_train_episodes_total"],
            "comparator_fires": bool(fires),
            "rule": "SWARM_R6 O2: the equal-budget float comparator on w13 runs this round iff candidate evals per run > baseline evals per run",
            "interpretations": {
                "clause_a_as_worded": "a smaller representation reached parity; search effort is not part of Clause A",
                "equal_budget": ("candidate searched MORE than the baseline per run: the comparator decides whether the "
                                 "float baseline matches at equal search") if fires else
                                ("candidate searched no more than the baseline per run (equal generations x batch): "
                                 "the win is not explained by extra search evaluations")}}


def main(argv=None) -> int:
    print(json.dumps(accounting(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
