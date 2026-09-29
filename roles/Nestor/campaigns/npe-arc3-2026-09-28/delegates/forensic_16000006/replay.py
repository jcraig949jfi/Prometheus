"""Forensic replay of X-DD-DENSE-COPY DENSE_COPY 7ae3 seed 16000006 with full genome-version logging.

Computational artificial life (integer programs on the z8 VM). Read-only w.r.t. the rest of the repo.

The world is replayed exactly (dense VM set explicitly, ATOMIC runner from x_donor_swap, same cell/seed). No
assays are run inside the replay (so nothing can perturb it). Every change of any organism's genome is logged:
  kind "birth": accepted replication (predecessor criterion) -- org's half overwritten by a copy of the donor.
                parent = donor oid (as the world's lineage records it), child = new oid, causal = P-11 pass,
                donor_pre = donor genome before the interaction, victim_old = overwritten genome, g = child genome.
  kind "mut":   ATOMIC write-back with mutation of an organism that was NOT overwritten (in-place point mutation;
                same oid). g_old -> g.
  kind "reap":  organism removed.
Snapshots of the live (oid, genome) population every SNAP epochs up to LOG_UNTIL. Logging stops at LOG_UNTIL;
the run continues to the end so max_causal_replication_depth can be checked against the record.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[2]
W1 = CAMP / "npe-w1-donor-discovery-2026-09-26"
for p in (W1 / "x_dd_dense_copy", W1 / "x_donor_discovery", CAMP / "c9x-explore-2026-09-24" / "x_donor_swap",
          CAMP / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
CELL, SEED = "7ae3", 16000006
LOG_UNTIL = int(sys.argv[1]) if len(sys.argv) > 1 else 700
SNAP = 10


def main():
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[CELL]]
    ev, snaps = [], {}
    S = {"seq": 0}

    class Fr(run_ds.runner_cls(world)):
        def _pair_interact(self, i, a_, b_):
            log = self.epoch < LOG_UNTIL
            if log:
                pre = {id(o): (o.oid, bytes(self._genome(o))) for o in (a_, b_)}
                self._births = []
            super()._pair_interact(i, a_, b_)
            if not log:
                return
            # births (recorded by _lin_birth hook in order) and in-place mutations
            for o in (a_, b_):
                oid0, g0 = pre[id(o)]
                other = b_ if o is a_ else a_
                g = bytes(self._genome(o))
                if o.oid != oid0:
                    b = next(x for x in self._births if x["child"] == o.oid)
                    S["seq"] += 1
                    ev.append({"seq": S["seq"], "e": self.epoch, "kind": "birth", "child": o.oid,
                               "parent": b["parent"], "victim_oid": oid0, "causal": b["causal"],
                               "fid": b["fid"], "donor_pre": pre[id(other)][1].hex(), "victim_old": g0.hex(),
                               "g": g.hex(), "slot": o.slot, "pair_i": i})
                elif g != g0:
                    S["seq"] += 1
                    ev.append({"seq": S["seq"], "e": self.epoch, "kind": "mut", "oid": o.oid, "g_old": g0.hex(),
                               "g": g.hex()})

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if self.epoch < LOG_UNTIL and hasattr(self, "_births"):
                self._births.append({"child": child, "parent": parent, "causal": bool(causal), "fid": fid})
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _kill(self, o, why="reaped"):
            if self.epoch < LOG_UNTIL and o.alive:
                S["seq"] += 1
                ev.append({"seq": S["seq"], "e": self.epoch, "kind": "reap", "oid": o.oid, "why": why})
            return super()._kill(o, why)

        def step(self):
            super().step()
            if self.epoch <= LOG_UNTIL and self.epoch % SNAP == 0:
                snaps[self.epoch] = {"seq": S["seq"],
                                     "live": [[o.oid, bytes(self._genome(o)).hex()] for o in self.orgs if o.alive]}

    t0 = time.time()
    r = Fr(dict(a["cell"], atlas_axis="NONE"), SEED, tier=a["tier"])
    # initial population snapshot (epoch 0 genomes are the random founders)
    out = r.run()
    rec = json.loads((W1 / "x_dd_dense_copy" / "results" / ("DENSE_COPY_%s_%d.json" % (CELL, SEED))).read_text())
    res = {"cell": CELL, "seed": SEED, "vm": world.z8.__name__, "depth": out["max_causal_replication_depth"],
           "recorded_depth": rec["depth"], "p11_events": out["p11_events"], "recorded_p11_events": rec["p11_events"],
           "replay_ok": out["max_causal_replication_depth"] == rec["depth"] and out["p11_events"] == rec["p11_events"],
           "log_until": LOG_UNTIL, "wall_s": round(time.time() - t0, 1), "n_events": len(ev)}
    (HERE / "replay_events.json").write_text(json.dumps({"meta": res, "events": ev, "snaps": snaps}))
    (HERE / "REPLAY_META.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res))


if __name__ == "__main__":
    main()
