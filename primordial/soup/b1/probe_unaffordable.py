"""Probe: does an UNAFFORDABLE action still move registers in wforge Encounter?

Found while copying semantics for B1 (world.py phase 1: `mag, cost = 0, 0` on a
forced abstain, but the pending-write loop below it still appends every a[i] % 8).
Read-only against wforge. Per world: charge 1, act_cost 3, delay 0, lin_ops and stoch
removed so only intake can move a register; one step with max actions vs one idle step.

Cheat control: with start_charge high enough to AFFORD the action, the registers must
move AND charge must drop (the probe must not call a legitimate, paid action a leak).

usage: python -m primordial.soup.b1.probe_unaffordable --worlds 200 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import copy
import json

from .common import Encounter, make_world


def one(g: int, start_charge: int) -> dict:
    mech, wid = make_world(g)
    m = copy.deepcopy(mech)
    m.start_charge, m.act_cost, m.delay, m.lin_ops, m.stoch_rate = start_charge, 3, 0, [], 0
    act, idle = Encounter(m, wid, 1), Encounter(m, wid, 1)
    act.step([[7] * m.act_width for _ in range(m.n_slots)])
    idle.step([[0] * m.act_width for _ in range(m.n_slots)])
    cost = 7 * m.act_width * m.act_cost
    return {"world_seed": g, "world_id": wid, "start_charge": start_charge, "cost_per_slot": cost,
            "affordable": cost <= start_charge, "regs_moved": act.regs != idle.regs,
            "charge_paid": act.charge != idle.charge, "actions_used": act.actions_used}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=200)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = [one(g, 1) for g in range(a.worlds)] + [one(g, 10_000) for g in range(a.worlds)]
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    unaff = [r for r in rows if not r["affordable"]]
    aff = [r for r in rows if r["affordable"]]
    summary = {
        "unaffordable_worlds": len(unaff),
        "unaffordable_moved_registers": sum(r["regs_moved"] for r in unaff),
        "unaffordable_paid": sum(r["charge_paid"] for r in unaff),
        "control_affordable_worlds": len(aff),
        "control_moved_and_paid": sum(r["regs_moved"] and r["charge_paid"] for r in aff),
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
