"""X-H2-TERMINATION (EXPLORE, MEASUREMENT; child of X-H2-7AE3). Declared before running.

Observation: 7ae3's implanted genome makes P-11-causal copies, but lineages stall at depth 1-4
whatever the founder dose. For every P-11-causal CHILD, what ends its line?
  OVERWRITTEN   its bytes decay below 0.5 identity to its birth genome before it donates
  DIED          it dies/is replaced as an id before donating
  INTACT_NO_COPY  it stays >= 0.5 identical to birth but never becomes a P-11 donor
  PROPAGATED    it becomes the parent of a later P-11-causal edge
Method: C9 arm-B physics for specimen 7ae3 (its cell, tier M, frozen donor genome, k=1),
fresh seeds 9_975_000 + s, s < 16. After every epoch the harness reads new P-11-causal
lineage edges, records each child's genome at birth, then tracks per epoch its identity to
that genome and whether it is later a parent in any P-11-causal edge.
Readout: the fate distribution over all causal children. Descriptive; it names the dominant
terminating transition, which decides the next targeted child.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"


def job(s):
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])
    kids = {}

    class T(world.Runner):
        _seen = 0

        def step(self):
            out = super().step()
            by_oid = {o.oid: o for o in self.orgs if o.alive}
            for e in self.lineage[self._seen:]:
                if e["kind"] == "birth" and e["causal"]:
                    if e["parent"] in kids:
                        kids[e["parent"]]["donated"] = True
                    o = by_oid.get(e["child"])
                    if o is not None:
                        kids[e["child"]] = {"born": e["epoch"], "g0": self._genome(o), "donated": False,
                                            "min_id": 1.0, "decayed_epoch": None, "gone_epoch": None}
            self._seen = len(self.lineage)
            for oid, k in kids.items():
                if k["gone_epoch"] is not None:
                    continue
                o = by_oid.get(oid)
                if o is None:
                    k["gone_epoch"] = self.epoch
                    continue
                fid = world._fidelity(k["g0"], self._genome(o))
                k["min_id"] = min(k["min_id"], fid)
                if fid < 0.5 and k["decayed_epoch"] is None:
                    k["decayed_epoch"] = self.epoch
            return out

    T(arm["cell"], 9_975_000 + s, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=genome).run()
    fates = []
    for k in kids.values():
        if k["donated"]:
            fates.append("PROPAGATED")
        elif k["decayed_epoch"] is not None:
            fates.append("OVERWRITTEN")
        elif k["gone_epoch"] is not None:
            fates.append("DIED")
        else:
            fates.append("INTACT_NO_COPY")
    decay = [k["decayed_epoch"] - k["born"] for k in kids.values() if k["decayed_epoch"] is not None and not k["donated"]]
    return {"s": s, "children": len(kids), "fates": dict(Counter(fates)), "decay_epochs": decay}


def main():
    with mp.Pool(6, maxtasksperchild=2) as pool:
        res = pool.map(job, range(16))
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    tot = Counter()
    for r in res:
        tot.update(r["fates"])
    dec = sorted(d for r in res for d in r["decay_epochs"])
    out = {"children": sum(r["children"] for r in res), "fates": dict(tot),
           "median_epochs_to_decay": dec[len(dec) // 2] if dec else None,
           "dominant": tot.most_common(1)[0][0] if tot else None}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
