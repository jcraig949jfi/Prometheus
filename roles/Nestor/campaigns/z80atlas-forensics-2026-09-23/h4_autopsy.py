"""S1-B: H4 extinction autopsy for 64dea50f417efb02-s1203-tL-a0.

Runs, each with per-epoch telemetry (population, births by kind, deaths by cause,
validation epochs, held trajectory, first cross, ops consumed, wall time):

  T      the historical endogenous run                          frozen replay, checked
  USED   d0f78df5558316cb-s1816-tM-a0, the control the flag     frozen replay, checked
         was actually adjudicated against
  SIB    64dea50f417efb02-s1816-tM-a0, the M-tier run T was     frozen replay, checked
         promoted from (the neighbouring family member)
  EXACT  the partner cell (reproduction -> EXTERNAL) at T's own  NEW forensic run: the
         seed 1203 and tier L                                   frozen record has none

Then the Cycle-9 smoke pair that produced the 0.62 s / 2.46 s figures, re-run on the
Cycle-9 substrate at the smoke's own 120 epochs, with ops, births, deaths and halting.

    python h4_autopsy.py   -> H4_AUTOPSY.json
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
T = "64dea50f417efb02-s1203-tL-a0"
USED = "d0f78df5558316cb-s1816-tM-a0"
SIB = "64dea50f417efb02-s1816-tM-a0"


def _job(which):
    import forensic
    if which == "EXACT":
        cfg, _ = forensic.frozen_record(T)
        cell = dict(cfg["job"]["cell"], reproduction="EXTERNAL")
        assert forensic.G.cell_id(cell).startswith("d0f78df5558316cb")
        return which, forensic.replay("EXACT_CONTROL_d0f78df5558316cb-s1203-tL", "h4",
                                      cell=cell, seed=1203, tier="L", check=False)
    rid = {"T": T, "USED": USED, "SIB": SIB}[which]
    return which, forensic.replay(rid, "h4")


def _smoke_pair():
    """The Cycle-9 smoke H4 bundle (first bundle, block A_historical), both arms."""
    verify = HERE.parent / "z80atlas-verify-2026-09-22"
    code = r'''
import json, sys, time
sys.path.insert(0, %r)
import manifest as M, world
b = M.h4_bundles(M.SIZE["H4_seeds"])[0]   # the first H4 bundle, as smoke.timings() takes it
out = {}
for arm in b["arms"]:
    t0 = time.time()
    r = world.run_cell(arm["cell"], arm["seed"], tier=arm["tier"], max_epochs=120)
    s = r["summary"]
    out[arm["arm"]] = {"wall_s": round(time.time() - t0, 3), "seed": arm["seed"],
        "block": b["block"], **{k: s.get(k) for k in ("ops", "slices", "births_endogenous",
        "births_external", "deaths", "alloc_calls", "pop_final", "extinct", "epochs_run",
        "budget_exhausted_share", "held_max_ever", "uniq_final", "halted_share_of_best")}}
    out[arm["arm"]]["ops_per_slice"] = round(s["ops"] / max(1, s["slices"]), 2)
print(json.dumps(out))
''' % str(verify)
    import subprocess
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=verify)
    if p.returncode:
        return {"error": p.stderr[-2000:]}
    return json.loads(p.stdout.strip().splitlines()[-1])


def main():
    t0 = time.time()
    with mp.Pool(4) as pool:
        res = dict(pool.map(_job, ["T", "USED", "SIB", "EXACT"]))
    smoke = _smoke_pair()
    out = {"source_run": T, "runs": res, "cycle9_smoke_pair": smoke,
           "wall_s": round(time.time() - t0, 1)}
    (HERE / "H4_AUTOPSY.json").write_text(json.dumps(out, indent=1, default=str))
    for k, r in res.items():
        print(k, r["run_id"], r["status"], r["wall_s"], r["summary_key"], r["deaths_by_cause"])
    print("smoke", json.dumps(smoke))


if __name__ == "__main__":
    main()
