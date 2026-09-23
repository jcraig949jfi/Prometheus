"""C1b budget calibration from controls only (operator GO 2026-09-19, items 1-2, 5).

Rule (recorded here before any search):
  For each chain depth d in {2, 3, 4}, on a grid of budgets b = 50, 100, ..., B_old(d):
    R(d, b) = fraction of depth-d chain tasks RANDOM_C1 solves within b interactions
              (from one run per stream under the C1 budgets: a walk that hit the
              target at step t is "solved within b" iff t <= b)
    H(d)    = 2 x the 95th percentile of PROCEDURE_REUSE_C1's interactions_used on
              depth-d chain tasks it solved (ACCUMULATED), the "comfortable headroom"
    budget(d) = the smallest grid b with R(d, b) < 0.05 and b >= H(d);
                if no such b exists the smallest b >= H(d) is taken and the conflict is
                reported (the search is then not launched).
  Depth 1 keeps its preregistered budget (2000): single-template tasks are the
  acquisition route and must stay brute-forceable.
Streams: gate namespace seeds 301-310 (depths 2-3) and qual namespace seeds
201-210 for depth 4 only (chain4 exists only there; 40 tasks); controls only,
no candidate touches them. Pass 1 (CALIBRATION_pass1.md) used qual 201-203
(12 depth-4 tasks): one lucky walk gave 8.3 percent and a spurious conflict.
Depth-4 chains never occur in SEARCH streams (only in qualification), so a
depth-4 conflict is reported but does not block the search launch; a depth-2
or depth-3 conflict does.
CONSEQUENCE, stated before search: budgets of ~50 admit the demonstrated route
(mental planning, then ~6-20 interactions of invocation) and exclude PHYSICAL
trial of stored procedures on chains (144 (block, arg) pairs x ~6 actions).
An evolved Player must therefore plan in the head, or find a partial-progress
signal, to solve chains. This is a property of the isolation design, recorded
here, not a finding.

CLI: python -m crius.calibrate_c1b --config crius/configs/c1.json --out crius/configs/c1b.json
"""

from __future__ import annotations

import argparse
import json
import os

from . import baselines_c1 as bl, evaluate, receipts, streams

GRID_STEP = 50
TARGET_RATE = 0.05
HEADROOM = 2.0
PCTL = 0.95


def _pctl(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = max(0, min(len(xs) - 1, int(round(q * (len(xs) - 1)))))
    return xs[k]


def collect(cfg, namespace, seeds):
    rows = []
    for seed in seeds:
        tasks = streams.lifetime(cfg, seed, namespace)
        rnd = evaluate.run_lifetime(bl.make_baseline("RANDOM_C1"), tasks, cfg, "ACCUMULATED", seed=seed)
        prc = evaluate.run_lifetime(bl.make_baseline("PROCEDURE_REUSE_C1"), tasks, cfg, "ACCUMULATED", seed=seed)
        for t, r, p in zip(tasks, rnd["task_results"], prc["task_results"]):
            if t.depth >= 2:
                rows.append({"namespace": namespace, "seed": seed, "depth": t.depth, "family": t.family,
                             "random_success": r["success"], "random_interactions": r["interactions_used"],
                             "proc_success": p["success"], "proc_interactions": p["interactions_used"],
                             "proc_in_block": p["success_in_block"], "budget_old": t.interaction_budget})
    return rows


def calibrate(cfg, rows):
    out = {}
    for d in (2, 3, 4):
        rs = [r for r in rows if r["depth"] == d]
        b_old = cfg["budgets"]["interactions_by_depth"][str(d)]
        n = len(rs)
        curve = {}
        for b in range(GRID_STEP, b_old + 1, GRID_STEP):
            k = sum(1 for r in rs if r["random_success"] and r["random_interactions"] <= b)
            curve[b] = round(k / n, 4) if n else None
        solved_costs = [r["proc_interactions"] for r in rs if r["proc_success"]]
        p95 = _pctl(solved_costs, PCTL)
        mx = max(solved_costs) if solved_costs else None
        h = HEADROOM * p95 if p95 is not None else None
        chosen = None
        conflict = False
        for b in sorted(curve):
            if h is not None and b >= h and curve[b] < TARGET_RATE:
                chosen = b
                break
        if chosen is None and h is not None:
            chosen = min((b for b in curve if b >= h), default=b_old)
            conflict = True
        out[str(d)] = {"n_tasks": n, "budget_old": b_old, "random_curve": curve,
                       "proc_solved": len(solved_costs), "proc_p95": p95, "proc_max": mx, "headroom": h,
                       "budget_new": chosen, "random_rate_at_new": curve.get(chosen), "conflict": conflict}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("crius", "configs", "c1.json"))
    ap.add_argument("--out", default=os.path.join("crius", "configs", "c1b.json"))
    ap.add_argument("--report-dir", default=os.path.join("crius", "runs", "calibration_c1b"))
    args = ap.parse_args(argv)
    cfg = receipts.load_config(args.config)
    rows = collect(cfg, "gate", list(range(301, 311))) + [r for r in collect(cfg, "qual", list(range(201, 211))) if r["depth"] == 4]
    cal = calibrate(cfg, rows)
    os.makedirs(args.report_dir, exist_ok=True)
    meta = receipts.run_meta(cfg, args.config)
    receipts.write_json(os.path.join(args.report_dir, "CALIBRATION.json"), {"meta": meta, "rule": __doc__, "rows": rows, "result": cal})
    new = json.loads(json.dumps(cfg))
    new["campaign"] = "c1b"
    for d in ("2", "3", "4"):
        new["budgets"]["interactions_by_depth"][d] = cal[d]["budget_new"]
    new["_note"] = ("C1b = C1 with chain budgets recalibrated from controls only (crius/calibrate_c1b.py; "
                    "crius/runs/calibration_c1b/CALIBRATION.md). Everything else identical to c1.json.")
    with open(args.out, "w", encoding="ascii", newline="\n") as f:
        f.write(json.dumps(new, indent=2) + "\n")
    lines = ["C1b BUDGET CALIBRATION (controls only; rule in crius/calibrate_c1b.py)",
             "streams: gate 301-310 (depths 2-3), qual 201-210 (depth 4 only, controls only); code %s" % meta["code_commit"][:9],
             "depth  n   old   RANDOM<5pct at  proc_p95  proc_max  headroom(2xp95)  NEW  random_rate_at_new  conflict"]
    for d in ("2", "3", "4"):
        c = cal[d]
        first_ok = min((b for b, r in c["random_curve"].items() if r is not None and r < TARGET_RATE), default=None)
        lines.append("  %s   %3d  %4d   %5s          %5s     %5s     %7s        %4s   %5s   %s" % (
            d, c["n_tasks"], c["budget_old"], first_ok, c["proc_p95"], c["proc_max"],
            None if c["headroom"] is None else round(c["headroom"], 1), c["budget_new"], c["random_rate_at_new"], c["conflict"]))
        lines.append("      random solve-within-b curve: " + " ".join("%d:%.3f" % (b, r) for b, r in c["random_curve"].items() if b % 100 == 0 or b == c["budget_new"]))
    lines.append("budget vector (interactions_by_depth): " + json.dumps(new["budgets"]["interactions_by_depth"]))
    lines.append("new config hash: %s" % receipts.config_hash(new))
    text = "\n".join(lines)
    with open(os.path.join(args.report_dir, "CALIBRATION.md"), "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    return 0 if not any(cal[d]["conflict"] for d in ("2", "3")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
