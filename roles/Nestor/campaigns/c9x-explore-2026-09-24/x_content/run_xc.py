"""X-CONTENT (EXPLORE, MEASUREMENT / ruler check; child of X-ACQUIRE). Declared before running.

X-ACQUIRE: the most frequent genomes of two founder-descended (anc == 0) runaway populations differ
from the founder at 58-62 of 64 bytes, far beyond nominal copy mutation. anc passes through overwrite
events, so "founder-descended" (X-ATOMIC-RANDOM, X-SWAP-ANCESTRY, C-SWAP-ACQUIRE) may mark slot
lineage rather than inherited content. Question: do anc-descended runaway populations carry the
founder's actual bytes?

Ruler: z8taint material tags (C9-D14 / H3 ruler R3, bit-identical to the untagged VM by its tests):
every byte value carries the tag of where it was made; copies keep the source tag, computed values
take the executor's niche. Here tracking is switched on in non-RESERVOIR cells and the implanted
founder's bytes get a unique tag FOUNDER = 254 at the first epoch; niche tags are small integers and
UNKNOWN = 255, so no collision. The ATOMIC runner restores tags with the genome (C-ATOMIC A1).
Sample (replays; world depth must equal the record):
  group OWN     - 7ae3's cell: the first 10 C-ATOMIC C1 ATOMIC runs (by seed) with depth >= 20;
  group FOREIGN - all 9 C-SWAP-ACQUIRE GENOME runs with the founder-descended runaway endpoint.
Readouts at the end: founder_byte_share = live bytes tagged FOUNDER / all live bytes; share of live
organisms whose bytes are >= 50% FOUNDER; anc0 share (for comparison).
INVALID if any replay's world depth differs from its record.
Classification (per group median founder_byte_share): SIGNAL (anc marks inherited content) if both
medians >= 0.5; CLEAN_NULL (anc marks slot lineage, not content) if both < 0.1; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
CAT = HERE.parent / "c_atomic" / "results"
CSA = HERE.parent / "c_swap_acquire" / "results"
OWN = "7ae3f9c1437c8000-s54765-tL-a0"
FOUNDER = 254
N_OWN = 10


def plan():
    own = []
    for s in range(80):
        r = json.loads((CAT / ("%s_%d_ATOMIC.json" % (OWN[:16], 12_000_000 + s))).read_text())
        if r["depth"] >= 20 and len(own) < N_OWN:
            own.append(("OWN", OWN, r["seed"], r["depth"]))
    foreign = []
    for p in sorted(CSA.glob("*_GENOME.json")):
        r = json.loads(p.read_text())
        if r["depth"] >= 20 and r["anc0_share"] >= 0.9:
            foreign.append(("FOREIGN", r["specimen"], r["seed"], r["depth"]))
    return own + foreign


def job(args):
    group, sp, seed, recorded = args
    import world
    import run_ds
    arm = run_ds.cells()[sp]

    class Tg(run_ds.runner_cls(world)):
        tagged = False

        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.track_material = True
            for o in self.orgs:
                if o.orig is None:
                    o.orig = bytearray([o.niche]) * o.length

        def _place(self, genome, anc, pid=None, niche=0):
            o = super()._place(genome, anc, pid, niche)
            if o.orig is None:
                o.orig = bytearray([niche]) * o.length
            return o

        def material_certificate(self):
            return None

        def step(self):
            if not self.tagged:
                f = next(o for o in self.orgs if o.anc == 0)
                f.orig = bytearray([FOUNDER]) * f.length
                self.tagged = True
            super().step()

    r = Tg(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    out = r.run()
    alive = [o for o in r.orgs if o.alive]
    tot = sum(len(o.orig or b"") for o in alive)
    fb = sum(sum(1 for t in (o.orig or b"") if t == FOUNDER) for o in alive)
    half = sum(1 for o in alive if o.orig and sum(1 for t in o.orig if t == FOUNDER) >= 0.5 * len(o.orig))
    rec = {"group": group, "specimen": sp, "seed": seed, "depth": out["max_causal_replication_depth"],
           "recorded_depth": recorded, "alive": len(alive),
           "founder_byte_share": round(fb / tot, 4) if tot else 0.0,
           "orgs_half_founder": round(half / len(alive), 4) if alive else 0.0,
           "anc0_share": round(sum(o.anc == 0 for o in alive) / len(alive), 4) if alive else 0.0}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%s_%d.json" % (group, sp[:4], seed))).write_text(json.dumps(rec))
    return rec


def main():
    todo = plan()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%s_%d" % (t[0], t[1][:4], t[2]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mism = [(r["group"], r["specimen"][:4], r["seed"]) for r in res if r["depth"] != r["recorded_depth"]]
    med = {g: statistics.median([r["founder_byte_share"] for r in res if r["group"] == g]) for g in ("OWN", "FOREIGN")}
    cls = ("INVALID" if mism or len(res) != len(todo) else "SIGNAL" if min(med.values()) >= 0.5 else
           "CLEAN_NULL" if max(med.values()) < 0.1 else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches": mism, "median_founder_byte_share": med,
            "n": {g: sum(r["group"] == g for r in res) for g in ("OWN", "FOREIGN")}, "runs": res}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
