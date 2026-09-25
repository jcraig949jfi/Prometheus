"""X-H3-FLOW (EXPLORE, MEASUREMENT; localization of C9 H3 CLEAN_NULL). Declared before running.

C9 H3: in cell a62116831aa6d956 crossings are frequent (A 24, B 29, C 25 of 32) but only 1
crossing per arm was by a majority-easy-MATERIAL genome; the easy niche does not raise
crossings. Where does the reservoir chain stop?
  (1) is easy-niche material ever MADE differently (does niche 0 hold competent genomes)?
  (2) does easy-niche material REACH hard niches (share of bytes tagged 0 in hard-niche
      organisms over time)?
  (3) are crossings in hard niches made of LOCAL (hard-origin) material?

Deterministic replays of C9's H3 arms A and B for cell a621 (the frozen seeds 9_300_000 + s,
s < 8 - identical runs, so readouts attach to the frozen record), sampling every 25 epochs:
per niche - population, mean held of its organisms, mean easy-material share; and at every
crossing - niche and easy share. Readout is descriptive; the classification names the stage
where easy material is lost: NOT_COMPETENT (niche 0 no more competent than hard niches),
NOT_TRANSPORTED (hard-niche easy share stays < 0.25 in A), or NOT_USED (transported but
crossings use hard material).
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


def job(args):
    s, arm = args
    import manifest as M
    import world
    cell = dict(dict(M.H3_CELLS)[CELL_RUN])
    kw = {"easy_niche_disabled": True} if arm == "B" else {}
    series = []

    class Obs(world.Runner):
        def step(self):
            out = super().step()
            if self.epoch % 25 == 0:
                row = {"e": self.epoch}
                for n in range(self.n_niches):
                    os_ = [o for o in self.orgs if o.alive and o.niche == n]
                    row["n%d" % n] = {"pop": len(os_),
                                      "held": round(statistics.mean(o.held for o in os_), 3) if os_ else None,
                                      "easy": round(statistics.mean(sum(1 for t in o.orig if t == 0) / len(o.orig)
                                                                    for o in os_ if o.orig), 3) if os_ else None}
                series.append(row)
            return out

    r = Obs(cell, 9_300_000 + s, tier="M", **kw)
    summ = r.run()
    cross = [{"e": c["epoch"], "niche": c["niche"], "easy": c.get("easy_material_share"), "held": c["held"]}
             for c in r.cross_events]
    return {"s": s, "arm": arm, "series": series, "crossings": cross,
            "has_cert": summ["has_reservoir_certificate"]}


def main():
    todo = [(s, a) for s in range(8) for a in ("A", "B")]
    with mp.Pool(6, maxtasksperchild=2) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    A = [r for r in res if r["arm"] == "A"]
    held0 = [row["n0"]["held"] for r in A for row in r["series"] if row["n0"]["held"] is not None]
    heldh = [row["n%d" % n]["held"] for r in A for row in r["series"] for n in (1, 2, 3)
             if row["n%d" % n]["held"] is not None]
    easyh = [row["n%d" % n]["easy"] for r in A for row in r["series"] for n in (1, 2, 3)
             if row["n%d" % n]["easy"] is not None]
    hard_cross = [c for r in A for c in r["crossings"] if c["niche"] != 0]
    easy_cross = [c for r in A for c in r["crossings"] if c["niche"] == 0]
    out = {"A_mean_held_niche0": round(statistics.mean(held0), 3) if held0 else None,
           "A_mean_held_hard": round(statistics.mean(heldh), 3) if heldh else None,
           "A_mean_easy_share_in_hard_niches": round(statistics.mean(easyh), 3) if easyh else None,
           "A_crossings_hard": len(hard_cross), "A_crossings_easy_niche": len(easy_cross),
           "A_hard_crossings_easy_share_median": (statistics.median(c["easy"] for c in hard_cross)
                                                  if hard_cross else None)}
    if out["A_mean_held_niche0"] is not None and out["A_mean_held_niche0"] <= (out["A_mean_held_hard"] or 0) + 0.05:
        cls = "NOT_COMPETENT"
    elif (out["A_mean_easy_share_in_hard_niches"] or 0) < 0.25:
        cls = "NOT_TRANSPORTED"
    else:
        cls = "NOT_USED"
    out["classification"] = cls
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
