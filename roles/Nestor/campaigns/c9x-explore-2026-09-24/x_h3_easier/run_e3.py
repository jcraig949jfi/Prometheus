"""X-H3-EASIER (EXPLORE, DOSE; targeted mutation after X-H3-FLOW = NOT_COMPETENT). Declared before running.

Localization: in C9 H3's crossing cell (a621), niche 0 - the "easy" variant (FORCED_READ +
NEUTRAL_BRIDGE on the cell's XOR5A) - never becomes competent (mean held 0.000), so the
reservoir chain fails at its FIRST link; material transport itself works (~21% easy-origin
bytes in hard niches). Targeted mutation (single coordinate, DOSE of easiness): niche 0's task
becomes XOR1 (a 1-bit transform) with FORCED_READ + NEUTRAL_BRIDGE; hard niches unchanged.

Arms (8 seeds 9_990_000 + s, tier M, cell a621, arm-A physics = RESERVOIR + migration):
  EASIER   niche 0 = XOR1 easy variant
Readouts: mean held in niche 0 vs hard niches over time; crossings by niche; R3 material
certificates. Retirement rule (declared): if niche-0 mean held stays < 0.10 over the run AND
there is no niche-0 crossing, the H3 branch RETIRES structurally - random pair-tape
populations do not evolve task competence in any niche at this scale, so no easy niche can
act as a reservoir. Otherwise H3 continues with a fresh CONFIRM design on the easier niche.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
CELL_RUN = "a62116831aa6d956-s7926-tM-a0"


def job(s):
    import manifest as M
    import tasks
    import world
    cell = dict(dict(M.H3_CELLS)[CELL_RUN])
    series = []

    class Easier(world.Runner):
        def _apply_niche_modifier(self, spec, niche):
            if niche == 0:
                return tasks.TaskSpec(transform="XOR1", read_order="FORCED_READ", bridge="NEUTRAL_BRIDGE",
                                      n_episodes=spec.n_episodes, budget=spec.budget, neutral=spec.neutral)
            return spec

        def step(self):
            out = super().step()
            if self.epoch % 50 == 0:
                h = {}
                for n in range(self.n_niches):
                    os_ = [o.held for o in self.orgs if o.alive and o.niche == n]
                    h[n] = round(statistics.mean(os_), 3) if os_ else None
                series.append({"e": self.epoch, "held": h})
            return out

    r = Easier(cell, 9_990_000 + s, tier="M")
    summ = r.run()
    return {"s": s, "series": series,
            "cross_by_niche": [sum(1 for c in r.cross_events if c["niche"] == n) for n in range(4)],
            "cert": summ["has_reservoir_certificate"], "held_max_ever": summ["held_max_ever"]}


def main():
    with mp.Pool(6, maxtasksperchild=2) as pool:
        res = pool.map(job, range(8))
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    h0 = [row["held"][0] for r in res for row in r["series"] if row["held"][0] is not None]
    hh = [row["held"][n] for r in res for row in r["series"] for n in (1, 2, 3) if row["held"][n] is not None]
    c0 = sum(r["cross_by_niche"][0] for r in res)
    out = {"niche0_mean_held": round(statistics.mean(h0), 3), "hard_mean_held": round(statistics.mean(hh), 3),
           "niche0_crossings": c0, "hard_crossings": sum(sum(r["cross_by_niche"][1:]) for r in res),
           "certificates": sum(r["cert"] for r in res)}
    out["decision"] = ("RETIRE_H3_STRUCTURAL" if out["niche0_mean_held"] < 0.10 and c0 == 0
                       else "CONTINUE_H3_CONFIRM")
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
