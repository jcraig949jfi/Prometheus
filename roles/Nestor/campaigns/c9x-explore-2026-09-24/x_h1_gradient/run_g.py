"""X-H1-GRADIENT (EXPLORE, MEASUREMENT; child of X-H1-TRANSPLANT). Declared before running.

Hypothesis from X-H1-TRANSPLANT: when reading the cue costs instructions, the gate abolishes
competence because it suppresses answer-before-read guessers, which in the ungated arm earn
the partial credit that populations climb (gradient removal). A correct reader scores
identically under the gate, so the task is solvable.

Measure, per arm (the four H1 arms, C9-H1R's repaired runner, the H1 cell, tier S, 20 fresh
seeds 9_140_000 + s), every 50 epochs: the share of living organisms that have answered
(answered > 0 at their last validation) and among them the share answering BEFORE reading the
cue (reads_at_answer < cue_index + 1), plus mean competence of answer-before-read organisms
and of readers.
Prediction (declared): ungated+VM - most competence carried by answer-before-read organisms;
gated+VM - no organism earns any competence at any time (flat landscape), with or without
readers present. If readers with competence exist in gated+VM, the mechanism is wrong.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
C9 = ROOT.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
sys.path.insert(0, str(ROOT / "c9_h1r"))


def job(a):
    import run_h1r
    R = run_h1r.repaired_runner()
    series = []

    class Obs(R):
        def step(self):
            out = super().step()
            if self.epoch % 50 == 0:
                ci = self.spec.cue_index()
                alive = [o for o in self.orgs if o.alive]
                early = [o for o in alive if 0 <= o.probe < ci + 1]
                readers = [o for o in alive if o.probe >= ci + 1]
                series.append({"e": self.epoch,
                               "early_share": round(len(early) / max(1, len(alive)), 3),
                               "reader_share": round(len(readers) / max(1, len(alive)), 3),
                               "early_comp": round(statistics.mean(o.comp for o in early), 3) if early else None,
                               "reader_comp": round(statistics.mean(o.comp for o in readers), 3) if readers else None,
                               "max_comp": round(max((o.comp for o in alive), default=0), 3)})
            return out

    s = Obs(a["cell"], a["seed"], tier=a["tier"], **a["kwargs"]).run()
    return {"arm": a["arm"], "seed": a["seed"], "series": series, "held_max_final": s["held_max_final"]}


def main():
    import manifest as M
    base = M.h1_bundles(1)[0]
    arms = [dict(a, seed=9_140_000 + s) for s in range(20) for a in base["arms"]]
    with mp.Pool(6, maxtasksperchild=8) as pool:
        res = pool.map(job, arms)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    out = {}
    for arm in {r["arm"] for r in res}:
        rows = [row for r in res if r["arm"] == arm for row in r["series"]]
        ec = [x["early_comp"] for x in rows if x["early_comp"] is not None]
        rc = [x["reader_comp"] for x in rows if x["reader_comp"] is not None]
        out[arm] = {"mean_early_share": round(statistics.mean(x["early_share"] for x in rows), 3),
                    "mean_reader_share": round(statistics.mean(x["reader_share"] for x in rows), 3),
                    "mean_comp_of_early": round(statistics.mean(ec), 3) if ec else None,
                    "mean_comp_of_readers": round(statistics.mean(rc), 3) if rc else None,
                    "max_comp_ever": max(x["max_comp"] for x in rows)}
    g = out.get("gate_on_cost_vm", {})
    out["prediction_holds"] = (g.get("max_comp_ever", 1) == 0)
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
