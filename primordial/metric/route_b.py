"""R8 item 1 (SWARM_R8 s4.3, Route B): a code-derived SURVIVAL_IMPOSSIBLE bound for the PENDING R16 train128 cells.

A PENDING cell has its baseline_r16 row (runs_total 32 / rng_family_count 4 / runs_per_family 8) and its
floor_suite_r16 row committed, but not the train128 input-invariant learner. The learner enters the cell only as one
more floor part, so for ANY learner result x the production verdict code (worlds.cell -> screen.variant_verdict) sees

    F(x) = max(b, x)            b = max of the committed floor parts (the bound)
    f(x) = F(x)                 four_policy
    f(x) = max(F(x), gate)      gate_in
    SURVIVED(x)  iff  ci_lo > f(x)

f is nondecreasing in x, so min_x f(x) = b (four_policy) or max(b, gate) (gate_in), and

    SURVIVAL_IMPOSSIBLE (variant)  iff  ci_lo <= min_x f(x).

The inequality above is the claim; it is not trusted on its own. `exhaustive` re-derives it with the production
code: the verdict is piecewise constant in x with breakpoints only at {b, gate, ci_lo}, so evaluating worlds.cell at
every breakpoint, every midpoint and one point beyond each end covers every learner result there is.
Nothing here reads or writes a learner row; the inputs are committed rows only.
"""
from __future__ import annotations

import json
import subprocess
import sys

from primordial.metric import r16 as R
from primordial.metric import r16_cells as RC
from primordial.metric import sample as SM
from primordial.metric import screen as SC
from primordial.metric import worlds as WR

PENDING_R7 = ((1, "train128_held64"), (10, "train128_held64"), (7, "train128_held64"), (34, "train128_held64"))
OUT = R.ROOT / "primordial" / "ledger" / "qd" / "r8_route_b.json"
SCHEMA = "g-r8-route-b/v1"


def committed_rows(cells=PENDING_R7, cell_rows=RC.ROWS, floors=R.ROWS["floors"], baseline=R.ROWS["baseline"],
                   learner128=R.ROWS["learner128"]) -> dict:
    """{(gs, p): (floor_suite_r16, baseline_r16, learner or None)} from the same files partial_v2 reads."""
    frows = R._rows(floors) + R._rows(cell_rows)
    brows = R._rows(baseline) + R._rows(cell_rows)
    lrows = R._rows(learner128) + R._rows(cell_rows)
    fl = {(int(x["gen_seed"]), x["pressure"]): x for x in frows if x.get("kind") == "floor_suite_r16"}
    base = {(int(x["gen_seed"]), x["pressure"]): x for x in brows if x.get("kind") == "baseline_r16"}
    lrn = {(int(x["gen_seed"]), x["pressure"]): x for x in lrows
           if x.get("kind") == "floor_invariant_r16" and x["pressure"] == "train128_held64"}
    return {(int(g), p): (fl.get((int(g), p)), base.get((int(g), p)), lrn.get((int(g), p))) for g, p in cells}


def _synthetic_learner(gs: int, p: str, x: float) -> dict:
    return {"gen_seed": gs, "pressure": p, "invariant_held64_median": float(x), "invariant_held64_iqr": 0.0,
            "run_seeds": [], "budget_ok": True}


def exhaustive(fl: dict, base: dict) -> dict:
    """Every verdict any learner result can produce, per variant, from the production verdict code."""
    rec0 = WR.cell(fl, base, None, est_runs=32)
    b, gate, lo = float(rec0["floor"]), float(rec0["gate_held64"]), float(base["ci95"][0])
    pts = sorted({b, gate, lo})
    xs = [pts[0] - 1e6] + pts + [(u + v) / 2 for u, v in zip(pts, pts[1:])] + [pts[-1] + 1e6]
    seen = {SC.vkey(*v): set() for v in SC.VARIANTS}
    for x in xs:
        rec = WR.cell(fl, base, _synthetic_learner(int(fl["gen_seed"]), fl["pressure"], x), est_runs=32)
        for k, v in rec["verdicts"].items():
            seen[k].add(v["verdict"])
    return {"points_evaluated": len(xs), "x": xs, "verdicts_reachable": {k: sorted(v) for k, v in seen.items()}}


def bound(fl: dict, base: dict, learner: dict | None = None) -> dict:
    gs, p = int(fl["gen_seed"]), fl["pressure"]
    problems = []
    if learner is not None:
        problems.append("learner row committed: the cell is not PENDING, Route B does not apply")
    if base is None:
        problems.append("no baseline_r16 row")
        return {"world": f"w{gs}", "gen_seed": gs, "pressure": p, "status": "NOT_APPLICABLE", "problems": problems}
    sample = SM.from_counts(base["n_per_family"])
    want = {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8}
    if any(sample.get(k) != v for k, v in want.items()):
        problems.append(f"baseline sample {sample} is not {want}")
    if not fl.get("floor_is_bound", fl["floor_parts"].get("input_invariant_learner") is None):
        problems.append("floor is not a bound")
    rec0 = WR.cell(fl, base, None, est_runs=32)
    b, gate, lo = float(rec0["floor"]), float(rec0["gate_held64"]), float(base["ci95"][0])
    per = {}
    for q1, q2 in SC.VARIANTS:
        k = SC.vkey(q1, q2)
        min_f = b if q1 == "four_policy" else max(b, gate)
        per[k] = {"min_over_learner_floor": min_f, "ci_lo": lo, "impossible": lo <= min_f,
                  "inequality": f"ci_lo {lo!r} <= min_x f(x) = {'b' if q1 == 'four_policy' else 'max(b, gate)'} "
                                f"= {min_f!r}" if lo <= min_f else
                                f"ci_lo {lo!r} > min_x f(x) = {min_f!r}: a learner result x < {lo!r} yields SURVIVED",
                  "margin": min_f - lo}
    ex = exhaustive(fl, base)
    for k, v in per.items():
        v["verdicts_reachable"] = ex["verdicts_reachable"][k]
        if v["impossible"] == ("SURVIVED" in v["verdicts_reachable"]):
            problems.append(f"{k}: analytic bound disagrees with the production verdict code")
    active = SC.vkey(*SC.ACTIVE)
    impossible_all = all(v["impossible"] for v in per.values())
    status = "SURVIVAL_IMPOSSIBLE" if impossible_all and not problems else ("UNRESOLVED" if not problems else "ERROR")
    return {"world": f"w{gs}", "gen_seed": gs, "pressure": p, "status": status,
            "active_variant": active, "active_verdicts_reachable": per[active]["verdicts_reachable"],
            "b_floor_bound": b, "b_parts": {k: v for k, v in fl["floor_parts"].items() if v is not None},
            "gate_held64": gate, "baseline_ci95": list(base["ci95"]), "baseline_median": base.get("median"),
            "baseline_sample": {k: sample.get(k) for k in want}, "det_matches_stage1": fl.get("det_matches_stage1"),
            "variants": per, "exhaustive_points": ex["points_evaluated"], "problems": problems}


def build(cells=PENDING_R7) -> dict:
    rows = committed_rows(cells)
    out = [bound(fl, base, lrn) for (fl, base, lrn) in rows.values()]
    head = subprocess.run(["git", "-C", str(R.ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    srcs = [RC.ROWS, R.ROWS["floors"], R.ROWS["baseline"], R.ROWS["learner128"]]
    rc = {str(s): subprocess.run(["git", "-C", str(R.ROOT), "log", "-1", "--format=%H", "--", str(s)],
                                 capture_output=True, text=True).stdout.strip() or None for s in srcs}
    return {"schema": SCHEMA, "item": "SWARM_R8 s4.3 Route B", "code_head": head, "rows_commits": rc,
            "rule": __doc__.split("\n\n")[1], "cells": out,
            "resolved": [c["world"] + "|" + c["pressure"] for c in out if c["status"] == "SURVIVAL_IMPOSSIBLE"],
            "unresolved": [c["world"] + "|" + c["pressure"] for c in out if c["status"] != "SURVIVAL_IMPOSSIBLE"]}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    doc = build()
    text = json.dumps(doc, indent=1, sort_keys=True) + "\n"
    if argv[:1] == ["write"]:
        OUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {OUT}")
    else:
        print(text)
    for c in doc["cells"]:
        print(c["world"], c["pressure"], c["status"], c["variants"][c["active_variant"]]["inequality"], c["problems"])
    return 0 if not doc["unresolved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
