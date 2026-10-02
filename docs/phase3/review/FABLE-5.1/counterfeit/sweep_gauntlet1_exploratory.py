"""Exploratory, after the fact, NOT preregistered: how the first gauntlet's verdicts depend on the budget.

A read-only reviewer re-ran gauntlet.py at other construction budgets and reported that the PASS
verdicts hold only in a window. This script repeats that check on the registered seeds so the claim
does not rest on the reviewer's word, and writes what it finds.

For each organism and target it sweeps the construction budget from 1 to 13 and records the v0.1
verdict of gauntlet.py's own protocol, and the label of the naive arm and of the intact arm. The
smallest budget at which an arm turns GOOD is its acquisition cost in tasks.

    python sweep_gauntlet1_exploratory.py      writes RECEIPT_gauntlet_sweep_exploratory.json
"""
import hashlib
import json
import pathlib
import platform
import sys
from datetime import datetime, timezone

import gauntlet as g

HERE = pathlib.Path(__file__).resolve().parent
BUDGETS = list(range(1, 14))
BASE = g.REGISTERED_BASE
CASES = [
    # name, class whose tight_budget is swept, factory, history, irrelevant history, target, seed offset, development budget
    ("GEARBOX SHIFT", g.Gearbox, lambda: g.Gearbox(), ["SHIFT"] * 3, ["SCALE"] * 3, "SHIFT", 3, 3),
    ("GEARBOX SCALE", g.Gearbox, lambda: g.Gearbox(), ["SCALE"] * 3, ["SHIFT"] * 3, "SCALE", 4, 3),
    ("BUILDER AFFINE", g.Builder, lambda: g.Builder(), ["SHIFT", "SCALE"], ["SQR", "CUB"], "AFFINE", 5, 42),
]


def first_good(labels):
    for b in BUDGETS:
        if labels[b] == "GOOD":
            return b
    return None


def main():
    out = {}
    for name, klass, make, hist, irr, target, offset, dev_budget in CASES:
        registered = klass.tight_budget
        verdicts, naive, intact = {}, {}, {}
        try:
            for b in BUDGETS:
                klass.tight_budget = b
                res = g.protocol(make, hist, irr, target, BASE + offset, dev_budget)
                verdicts[b] = g.v01_verdict(res)[0]
                naive[b] = res["naive"]["label"]
                intact[b] = res["intact"]["label"]
        finally:
            klass.tight_budget = registered
        passes = [b for b in BUDGETS if verdicts[b] == "PASS"]
        cost_naive, cost_dev = first_good(naive), first_good(intact)
        # development cost in tasks: one construction per history family, each at most dev_budget tasks
        out[name] = {"registered_budget": registered, "verdict_by_budget": verdicts, "budgets_that_pass": passes,
                     "naive_arm_by_budget": naive, "intact_arm_by_budget": intact,
                     "tasks_to_an_acceptable_U_naive": cost_naive, "tasks_to_an_acceptable_U_developed": cost_dev}
        print("%-15s registered budget %d; PASS at budgets %s; tasks to an acceptable U: naive %s, developed %s"
              % (name, registered, passes, cost_naive, cost_dev))
    receipt = {
        "what": "EXPLORATORY, not preregistered: budget sweep of the first gauntlet on its registered seeds",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0], "seed_base": BASE, "budgets": BUDGETS,
        "gauntlet_sha256_lf": hashlib.sha256((HERE / "gauntlet.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "cases": {k: {kk: ({str(b): v for b, v in vv.items()} if isinstance(vv, dict) else vv)
                      for kk, vv in c.items()} for k, c in out.items()},
    }
    (HERE / "RECEIPT_gauntlet_sweep_exploratory.json").write_text(
        json.dumps(receipt, indent=1, sort_keys=True) + "\n", encoding="ascii", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
