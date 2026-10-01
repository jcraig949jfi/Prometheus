"""W2-38: deterministic replay of a frozen C-A3-INTERNALIZE run with read-only genome+register dumps.

Reproduces run_ci._run line for line (the frozen file is imported for its path setup, never edited) and adds
observation only: at chosen checkpoints every live organism's genome bytes, (regs, fz, fc), L membership; and the
world's own counters (P-11 events, accepted replications) at every 100-epoch checkpoint. Nothing here touches
self.rng or any world state. Bit-exactness: the rebuilt record must equal results/<cell>_<seed>.json.

    python -B replay_dump.py ffa6 27000052 1200,1600,1700,1800,2000
"""
from __future__ import annotations

import gzip
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CI = HERE.parents[1] / "campaigns" / "npe-arc3-2026-09-28" / "c_a3_internalize"
sys.path.insert(0, str(CI))
import run_ci  # noqa: E402  (its module body inserts the frozen sys.path entries)


def replay(cell, seed, dump_epochs):
    import world
    import run_dc
    import run_dd
    import run_de
    import run_ds
    import run_fair
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    cc, sfc = {}, {}
    S = {"d0": None, "d0_free": None, "L": set(), "cps": []}
    dumps, counters = [], []

    def sf(self, g):
        if g not in sfc:
            sfc[g] = all(run_fair.fair_assay(world, self, g, e, "SFL" + g.hex(), 20) >= 0.5 for e in ("R1", "R2"))
        return sfc[g]

    class Ln(run_ds.runner_cls(world)):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if S["d0"] is not None:
                if parent in S["L"]:
                    S["L"].add(child)
                else:
                    S["L"].discard(child)
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            super().step()
            alive = [o for o in self.orgs if o.alive]
            if S["d0"] is None and self.epoch % 20 == 0:
                comp = [o for o in alive if run_de.competent(world, self, bytes(self._genome(o)), cc)]
                if comp:
                    S["d0"] = self.epoch
                    S["L"] = {o.oid for o in comp}
                    S["d0_free"] = [sf(self, g) for g in sorted({bytes(self._genome(o)) for o in comp})]
            if S["d0"] is not None and self.epoch % 100 == 0:
                inL = {}
                for o in alive:
                    g = bytes(self._genome(o))
                    inL[g] = inL.get(g, False) or (o.oid in S["L"])
                rows = [(sf(self, g), l) for g, l in inL.items() if run_de.competent(world, self, g, cc)]
                S["cps"].append({"epoch": self.epoch, "L_share": round(sum(o.oid in S["L"] for o in alive) / len(alive), 4),
                                 "competent": len(rows), "free": sum(f for f, _ in rows), "free_in_L": sum(f and l for f, l in rows)})
            # ---- observation only (W2-38) ----
            if self.epoch % 100 == 0:
                counters.append({"epoch": self.epoch, "p11_events": self.ct["p11_events"],
                                 "replication_events": self.ct["replication_events"], "alive": len(alive)})
            if self.epoch in dump_epochs:
                dumps.append({"epoch": self.epoch, "orgs": [
                    {"oid": o.oid, "slot": o.slot, "genome": bytes(self._genome(o)).hex(),
                     "regs": None if o.regs is None else list(o.regs), "fz": o.fz, "fc": o.fc,
                     "inL": o.oid in S["L"], "born": o.born, "pid": o.pid, "age": o.age,
                     "zero_competent": cc.get(bytes(self._genome(o)))} for o in alive]})

    t0 = time.time()
    r = Ln(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"], "d0_epoch": S["d0"],
           "d0_free": S["d0_free"], "checkpoints": S["cps"]}
    ref = json.loads((CI / "results" / ("%s_%d.json" % (cell, seed))).read_text())
    diffs = []
    for k in ("depth", "d0_epoch", "d0_free"):
        if rec[k] != ref[k]:
            diffs.append((k, rec[k], ref[k]))
    for x, y in zip(rec["checkpoints"], ref["checkpoints"]):
        if x != y:
            diffs.append(("cp", x, y))
    if len(rec["checkpoints"]) != len(ref["checkpoints"]):
        diffs.append(("n_cps", len(rec["checkpoints"]), len(ref["checkpoints"])))
    res = {"cell": cell, "seed": seed, "replay_identical": rec == ref, "diffs": diffs,
           "wall_s": round(time.time() - t0, 1), "record": rec, "counters": counters,
           "runner": {"L": r.L, "slice": r.t["slice"], "ops_mask": r._ops_mask(), "copy_mut": r.copy_mut,
                      "slot_size": r.slot_size},
           "sfc": {g.hex(): v for g, v in sfc.items()}, "dumps": dumps}
    p = HERE / ("replay_%s_%d.json.gz" % (cell, seed))
    with gzip.open(p, "wt") as f:
        json.dump(res, f)
    print(json.dumps({"cell": cell, "seed": seed, "replay_identical": res["replay_identical"], "diffs": diffs[:5],
                      "wall_s": res["wall_s"], "bytes": p.stat().st_size}))


if __name__ == "__main__":
    replay(sys.argv[1], int(sys.argv[2]), {int(x) for x in sys.argv[3].split(",")})
