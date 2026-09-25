"""C-ATOMIC (CONFIRM lane, fresh and frozen). Parent: X-ATOMIC (EXPLORE, SIGNAL: with ATOMIC
write-back, runaway causal heredity in 36/64 vs 3/64, p = 4e-11; copy duration 38 vs 4 epochs).

NOTHING HERE MAY CHANGE AFTER COMMIT: specimens, cells, seeds, arms, endpoints, rules, allocation.

Mechanism under test: in the pair tape, the write-back of BOTH halves after every interaction is
a non-replicative erosion (~5%/byte/epoch, X-STALL-F0) that sterilizes causal lineages. ATOMIC
write-back: a half keeps its new tape contents only when an accepted replication event
re-identified it as a child; otherwise it is restored to its pre-interaction genome and then
receives the ordinary per-epoch in-place mutation. Copying, P-11 and its instrument unchanged.
Both arms: implanted donor genome (C9 arm B), one founder, tier from the manifest, the specimen's
frozen cell with atlas_axis NONE. One job per process.

C1 (primary; replication): specimen 7ae3; 80 fresh seeds 12_000_000 + s per arm.
    Endpoint: runaway = P-11 max causal replication depth >= 20.
    CONFIRMED iff share(ATOMIC) - share(BASE) >= 0.25 AND one-sided Fisher p < 0.001.
C2 (generality; separate claim): the 15 OTHER H2 panel specimens; 8 fresh seeds 12_100_000 + s per
    specimen per arm (120 runs per arm). Same endpoint, pooled.
    CONFIRMED iff pooled share(ATOMIC) - share(BASE) >= 0.10 AND one-sided Fisher p < 0.001 AND at
    least 4 specimens have more ATOMIC than BASE runaways.
Secondary, never decisive: depth >= 5, max depth, per-specimen counts.

    python run_cat.py -> RESULTS.json, VERDICT.json

AMENDMENT A1 (infrastructure, 2026-09-25 06:25, after the first launch aborted and BEFORE any C2
outcome was inspected): the frozen runner asserted `not track_material`; the two panel
specimens with RESERVOIR cells (4931614d912c52b2, a62116831aa6d956) track per-byte material
tags, so the assertion fired and the pool aborted with 231/400 runs done (C1 complete, 160/160).
Repair: the ATOMIC restore also restores the member's material tags, re-tagged by the world's own
_mutated_orig rule. Rules, seeds, arms, endpoints and allocation are unchanged; completed runs
(no tracked cell among them) took the identical code path and are kept.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
PRIMARY = "7ae3f9c1437c8000-s54765-tL-a0"
ARMS = ("BASE", "ATOMIC")
N1, N2 = 80, 8


def panel():
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    return sorted({b["specimen"] for b in man["bundles"] if b["hypothesis_id"] == "H2"})


def jobs():
    out = [(PRIMARY, 12_000_000 + s, a) for s in range(N1) for a in ARMS]
    out += [(sp, 12_100_000 + s, a) for sp in panel() if sp != PRIMARY for s in range(N2) for a in ARMS]
    return out


def key(sp, seed, armname):
    return "%s_%d_%s" % (sp[:16], seed, armname)


def job(args):
    sp, seed, armname = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == sp)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])

    class At(world.Runner):
        def _pair_interact(self, i, a, b):
            if armname == "BASE":
                return super()._pair_interact(i, a, b)
            pre = [(o, o.oid, self._genome(o), bytearray(o.orig) if self.track_material else None)
                   for o in (a, b)]
            super()._pair_interact(i, a, b)
            for o, oid, g, orig in pre:
                if o.oid != oid:
                    continue                      # accepted replication event: keep the copy
                new = self._mutate(g)             # ordinary per-epoch in-place mutation only
                self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                self.mem[o.slot:o.slot + len(new)] = new
                o.length = len(new)
                if orig is not None:
                    # AMENDMENT A1 (infrastructure): RESERVOIR cells carry per-byte material
                    # tags; restore them with the genome, re-tagged by the world's own rule
                    o.orig = world._mutated_orig(g, new, orig, o.niche)

    r = At(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=genome)
    out = r.run()
    rec = {"specimen": sp, "seed": seed, "arm": armname, "depth": out["max_causal_replication_depth"],
           "p11_events": out["p11_events"]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / (key(sp, seed, armname) + ".json")).write_text(json.dumps(rec))
    return rec


def fisher(a, b, n1, n2=None):
    n2 = n1 if n2 is None else n2
    k0 = a + b
    return (sum(math.comb(n1, x) * math.comb(n2, k0 - x) for x in range(a, min(n1, k0) + 1))
            / math.comb(n1 + n2, k0)) if k0 else 1.0


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [j for j in jobs() if key(*j) not in done]
    # longest-first is not result-dependent: primary jobs first, then the panel, fixed order
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    assert len(res) == len(jobs()), "incomplete: %d of %d" % (len(res), len(jobs()))

    def cnt(rows, arm, thr=20):
        return sum(r["depth"] >= thr for r in rows if r["arm"] == arm)

    p1 = [r for r in res if r["specimen"] == PRIMARY]
    a1, b1 = cnt(p1, "ATOMIC"), cnt(p1, "BASE")
    fp1 = fisher(a1, b1, N1)
    c1 = (a1 - b1) / N1 >= 0.25 and fp1 < 0.001
    p2 = [r for r in res if r["specimen"] != PRIMARY]
    n2 = len(p2) // 2
    a2, b2 = cnt(p2, "ATOMIC"), cnt(p2, "BASE")
    fp2 = fisher(a2, b2, n2)
    per = {sp: {"ATOMIC": cnt([r for r in p2 if r["specimen"] == sp], "ATOMIC"),
                "BASE": cnt([r for r in p2 if r["specimen"] == sp], "BASE"),
                "ATOMIC_d5": cnt([r for r in p2 if r["specimen"] == sp], "ATOMIC", 5),
                "BASE_d5": cnt([r for r in p2 if r["specimen"] == sp], "BASE", 5)}
           for sp in sorted({r["specimen"] for r in p2})}
    more = sum(v["ATOMIC"] > v["BASE"] for v in per.values())
    c2 = (a2 - b2) / n2 >= 0.10 and fp2 < 0.001 and more >= 4
    v = {"C1": {"verdict": "CONFIRMED" if c1 else "NOT_CONFIRMED", "runaways": {"ATOMIC": a1, "BASE": b1},
                "n_per_arm": N1, "share_diff": round((a1 - b1) / N1, 4), "fisher_p": fp1,
                "secondary_depth_ge5": {"ATOMIC": cnt(p1, "ATOMIC", 5), "BASE": cnt(p1, "BASE", 5)},
                "max_depth": {a: max(r["depth"] for r in p1 if r["arm"] == a) for a in ARMS}},
         "C2": {"verdict": "CONFIRMED" if c2 else "NOT_CONFIRMED", "runaways": {"ATOMIC": a2, "BASE": b2},
                "n_per_arm": n2, "share_diff": round((a2 - b2) / n2, 4), "fisher_p": fp2,
                "specimens_more_atomic": more, "per_specimen": per},
         "n_results": len(res)}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
