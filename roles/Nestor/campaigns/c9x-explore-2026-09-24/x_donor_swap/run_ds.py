"""X-DONOR-SWAP (EXPLORE, TRANSPLANT / orthogonal; child of X-DONOR-RATE). Declared before running.

X-DONOR-RATE (SIGNAL): 7ae3's donor copies from a fresh state in 96% of assays; 12 of the other 15
panel donors never do. C-ATOMIC C2's null could therefore be the DONORS, not the CELLS. Question:
given a competent donor (7ae3's genome) and no erosion (ATOMIC write-back), do the other panel
specimens' worlds permit runaway heredity?

Design: 7ae3's 64-byte donor genome implanted as the single founder into each other panel
specimen's frozen cell (atlas_axis NONE, the specimen's own tier) with ATOMIC write-back (as
C-ATOMIC, amendment A1 included). Eligible cells: representation length L >= 64 (11 of 15; the
four Z8_32 cells, L = 32, cannot hold the genome and are excluded before running). Positive
control: 7ae3's own cell, same seeds. 8 fresh seeds 11_000_000 + s per cell. One job per process.
Also per cell: the genome's fresh-state P-11 assay pass rate in that cell (200 seeds, either side).
Readouts: runaway (depth >= 20), depth >= 5, any P-11 event.
Classification: INVALID if the positive control has 0 runaways; SIGNAL if runaways occur in >= 4 of
the 11 foreign cells; CLEAN_NULL if no foreign cell has a runaway; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
DONOR = "7ae3f9c1437c8000-s54765-tL-a0"
N = 8
K = 200


def cells():
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    out = {}
    for b in man["bundles"]:
        if b["hypothesis_id"] == "H2":
            a = next(x for x in b["arms"] if x["arm"] == "B_reimplant_actual")
            out[b["specimen"]] = a
    return out


def donor_genome():
    return bytes.fromhex(cells()[DONOR]["kwargs"]["implant_hex"])


def runner_cls(world):
    class At(world.Runner):
        def _pair_interact(self, i, a, b):
            pre = [(o, o.oid, self._genome(o), bytearray(o.orig) if self.track_material else None)
                   for o in (a, b)]
            super()._pair_interact(i, a, b)
            for o, oid, g, orig in pre:
                if o.oid != oid:
                    continue
                new = self._mutate(g)
                self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                self.mem[o.slot:o.slot + len(new)] = new
                o.length = len(new)
                if orig is not None:
                    o.orig = world._mutated_orig(g, new, orig, o.niche)
    return At


def assay_rate(sp):
    import world
    arm = cells()[sp]
    g0 = donor_genome()
    r = world.Runner(dict(arm["cell"], atlas_axis="NONE"), 1, tier=arm["tier"],
                     implant="ACTUAL_GENOME", implant_bytes=g0)
    g = r._pad(g0)
    n, tl = r.L, world._pow2(2 * r.L)
    fresh, hits = (None, 0, 0), 0
    for k in range(K):
        ok = False
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            ok = ok or world.p11.assay(world.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=fresh, st_b=fresh,
                                       budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=r.copy_mut,
                                       victim_side=1 - side, seed=("X-DONOR-SWAP", sp, k, side))["pass"]
        hits += ok
    return {"specimen": sp, "L": r.L, "assay_rate": hits / K}


def job(args):
    sp, s = args
    import world
    arm = cells()[sp]
    r = runner_cls(world)(dict(arm["cell"], atlas_axis="NONE"), 11_000_000 + s, tier=arm["tier"],
                          implant="ACTUAL_GENOME", implant_bytes=donor_genome())
    out = r.run()
    rec = {"specimen": sp, "s": s, "depth": out["max_causal_replication_depth"], "p11_events": out["p11_events"]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (sp[:16], s))).write_text(json.dumps(rec))
    return rec


def eligible():
    import world
    out = []
    for sp, arm in sorted(cells().items()):
        r = world.Runner(dict(arm["cell"], atlas_axis="NONE"), 1, tier=arm["tier"])
        if r.L >= len(donor_genome()):
            out.append(sp)
    return out


def main():
    sps = eligible()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [(sp, s) for sp in sps for s in range(N) if "%s_%d" % (sp[:16], s) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        rates = pool.map(assay_rate, sps)
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    per = {}
    for r in rates:
        rows = [x for x in res if x["specimen"] == r["specimen"]]
        per[r["specimen"][:4]] = {**{k: r[k] for k in ("L", "assay_rate")},
                                  "runaways": sum(x["depth"] >= 20 for x in rows),
                                  "depth_ge5": sum(x["depth"] >= 5 for x in rows),
                                  "any_copy": sum(x["p11_events"] > 0 for x in rows),
                                  "max_depth": max(x["depth"] for x in rows), "n": len(rows)}
    ctrl = per[DONOR[:4]]
    foreign = {k: v for k, v in per.items() if k != DONOR[:4]}
    with_run = sum(v["runaways"] > 0 for v in foreign.values())
    cls = ("INVALID" if ctrl["runaways"] == 0 else "SIGNAL" if with_run >= 4 else
           "CLEAN_NULL" if with_run == 0 else "WEAK_SIGNAL")
    summ = {"classification": cls, "foreign_cells": len(foreign), "foreign_cells_with_runaway": with_run,
            "control_7ae3": ctrl, "per_cell": per}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
