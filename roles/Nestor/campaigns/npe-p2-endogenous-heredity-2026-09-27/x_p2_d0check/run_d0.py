"""X-P2-D0CHECK (EXPLORE, MEASUREMENT / check on X-P2-LINEAGE; P2 Block N). Declared before running. Theory-aware.

X-P2-LINEAGE (WEAK_SIGNAL): in 4 of 13 persistent-register runaway runs every late state-robust competent genome is in
the lineage L of the first competent organisms D0 (7ae3 16000006, 16000021, 16000046; ffa6 16000030). That is a
candidate endogenous transition ONLY if D0 itself was not already robust: D0 is every organism competent at the first
20-epoch check, so a robust genome among D0 would make "in L" uninformative.
Question: in those 4 runs, were the D0 genomes self-poisoning (non-robust) at D0?

Method: replay each run exactly (DENSE_COPY arm: dense VM, ATOMIC runner, same cell and seed) up to its D0 epoch; take
the distinct D0 genomes (COMPETENT by X-DD-ESTABLISH's cached screen at that check, as in X-P2-LINEAGE); measure each
with X-DD-SELFSTATE's method (rate_0, rate_1; STATE_ROBUST iff rate_1 >= 0.25 rate_0). The replay must reproduce the
recorded D0 epoch.
Per run: ALL_POISONED if every D0 genome is non-robust; SOME_ROBUST otherwise.
Classification: SIGNAL (candidate endogenous transitions stand) if >= 3 of 4 runs are ALL_POISONED; CLEAN_NULL (the
lineage already carried robust genomes at D0) if <= 1; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LN = HERE.parent / "x_p2_lineage"
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
for p in (LN, W1 / "x_dd_selfstate", W1 / "x_dd_establish", W1 / "x_dd_nocopy_context", W1 / "x_dd_dense_copy",
          W1 / "x_donor_discovery", HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
RUNS = [("7ae3", 16000006, 340), ("7ae3", 16000021, 1360), ("7ae3", 16000046, 140), ("ffa6", 16000030, 280)]


class Stop(Exception):
    pass


def one(cell, seed, d0_rec):
    import world
    import run_dc
    import run_dd
    import run_de
    import run_ds
    import run_ss
    world.z8 = run_dc.dense_z8()
    run_ss.HERE = HERE / "scratch"
    a = run_ds.cells()[run_dd.CELLS[cell]]
    cache = {}
    got = {}

    class R(run_ds.runner_cls(world)):
        def step(self):
            super().step()
            if self.epoch % 20 == 0:
                comp = [o for o in self.orgs if o.alive and run_de.competent(world, self, bytes(self._genome(o)), cache)]
                if comp:
                    got["epoch"] = self.epoch
                    got["genomes"] = sorted({bytes(self._genome(o)) for o in comp})
                    raise Stop()

    r = R(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    try:
        r.run()
    except Stop:
        pass
    rows = []
    for g in got.get("genomes", []):
        k = run_ss.job(("ANY", cell, seed, g.hex()))["rates_by_k"]
        rows.append({"hex": g.hex(), "rate0": k[0], "rate1": k[1], "robust": k[0] > 0 and k[1] >= 0.25 * k[0]})
    return {"cell": cell, "seed": seed, "d0_epoch": got.get("epoch"), "d0_recorded": d0_rec,
            "replay_ok": got.get("epoch") == d0_rec, "d0_genomes": rows,
            "label": "ALL_POISONED" if rows and not any(x["robust"] for x in rows) else "SOME_ROBUST"}


def main():
    (HERE / "scratch" / "results").mkdir(parents=True, exist_ok=True)
    res = [one(*t) for t in RUNS]
    ok = all(r["replay_ok"] for r in res)
    n = sum(r["label"] == "ALL_POISONED" for r in res)
    cls = "INVALID" if not ok else "SIGNAL" if n >= 3 else "CLEAN_NULL" if n <= 1 else "WEAK_SIGNAL"
    summ = {"classification": cls, "all_poisoned_runs": n,
            "runs": [{k: r[k] for k in ("cell", "seed", "d0_epoch", "replay_ok", "label")} |
                     {"d0_robust": sum(x["robust"] for x in r["d0_genomes"]), "d0_n": len(r["d0_genomes"])} for r in res]}
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
