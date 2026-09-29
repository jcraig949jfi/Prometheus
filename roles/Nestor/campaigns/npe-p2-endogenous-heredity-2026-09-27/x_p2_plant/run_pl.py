"""X-P2-PLANT (EXPLORE, INITIAL_CONDITION / adversarial test of C-DENSE-COPY; program P2 Block A). Declared
before running. Theory-aware by date.

C-DENSE-COPY (confirmed): a one-byte alias for LDIR/LDDR raises spontaneous donor acquisition from 1/64 to 39/64
runs. W1 read this as "acquisition is limited by the encoding ACCESSIBILITY of the block-copy primitive".
Rival readings: the alias raises the mere PRESENCE (frequency) of block-copy in random material; or it changes
something only a one-byte form has (placement freedom, reachability by point mutation, instruction density
effects on unrelated dynamics).
Question: if every initial genome CONTAINS a two-byte block-copy (presence at 100% at epoch 0) on the stock VM,
does donor acquisition approach the dense-alias level?

Arm PLANT: stock z8 (no aliases); the cell's random initial population, except that each initial genome gets
ED B0 (LDIR) or ED B8 (LDDR), chosen 50/50, written over 2 bytes at a uniformly random offset p in [0, L-2].
Planting uses its own RNG (seeded from the run seed), so the world's RNG stream -- and hence the random
background -- is the same as in W1's arms on the same seed. Only the initial population is planted.
Cells 7ae3 and ffa6 (ATOMIC runner), seeds 16_000_000 + s, s < 48 -- the SAME cells and seeds as
X-DD-DENSE-COPY, whose PLAIN (0/96 runs with L2) and DENSE_COPY (49/96) arms are the paired references
(read from their results, not re-run).
Ruler: the W1 screen (L2 COMPETENT, every 100 epochs, stock VM), L4 = world causal depth >= 20; plus L1c =
genomes containing ED B0 / ED B8, per checkpoint.
Classification (question: does presence alone suffice?):
  SIGNAL (presence suffices)       if PLANT L2 runs >= 25 of 96 (half the dense-alias level);
  CLEAN_NULL (presence does not)   if PLANT L2 runs <= 3 of 96 (PLAIN + 3);
  WEAK_SIGNAL otherwise.
Reported: L2 per cell, first-L2 epochs, L1c persistence over time (does the planted instruction survive
selection / mutation?), L4.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
for p in (W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
N = 48
SEED0 = 16_000_000
PATS = (bytes((0xED, 0xB0)), bytes((0xED, 0xB8)))


def job(args):
    cell, seed = args
    import world
    import z8 as z8_plain
    import run_dd
    import run_ds
    world.z8 = z8_plain
    a = run_ds.cells()[run_dd.CELLS[cell]]
    prng = random.Random(("X-P2-PLANT", seed).__repr__())
    cps = []
    st = {"planting": True, "planted": 0}

    class Pl(run_ds.runner_cls(world)):
        def _place(self, genome, anc, pid=None, niche=0):
            if st["planting"]:
                g = bytearray(genome)
                if len(g) >= 2:
                    p = prng.randrange(0, len(g) - 1)
                    g[p:p + 2] = PATS[prng.randrange(2)]
                    genome = bytes(g)
                    st["planted"] += 1
            return super()._place(genome, anc, pid, niche)

        def step(self):
            st["planting"] = False
            super().step()
            if self.epoch % run_dd.EVERY == 0:
                gs = sorted({bytes(self._genome(o)) for o in self.orgs if o.alive})
                c = run_dd.screen(world, self, gs, ("X-P2-PLANT", cell, seed, self.epoch))
                c["L1c"] = sum(any(q in g for q in PATS) for g in gs)
                c["epoch"] = self.epoch
                cps.append({k: c[k] for k in ("epoch", "distinct", "L1c", "stage1", "L2", "best_fid_final")})

    r = Pl(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"arm": "PLANT", "cell": cell, "seed": seed, "planted": st["planted"],
           "depth": out["max_causal_replication_depth"], "p11_events": out["p11_events"], "checkpoints": cps}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def jobs():
    return [(c, SEED0 + s) for s in range(N) for c in ("7ae3", "ffa6")]


def main():
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in jobs() if "%s_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    ref = {}
    for arm in ("PLAIN", "DENSE_COPY"):
        rows = [json.loads(p.read_text()) for p in (W1 / "x_dd_dense_copy" / "results").glob(arm + "_*.json")]
        ref[arm] = {"n": len(rows), "L2": sum(any(c["L2"] > 0 for c in r["checkpoints"]) for r in rows)}

    def ever(r):
        return any(c["L2"] > 0 for c in r["checkpoints"])
    l2 = sum(ever(r) for r in res)
    cls = ("INVALID" if len(res) != len(jobs()) or any(r["planted"] == 0 for r in res) else
           "SIGNAL" if l2 >= 25 else "CLEAN_NULL" if l2 <= 3 else "WEAK_SIGNAL")
    l1c = {}
    for e in (100, 500, 1000, 2000):
        v = [c["L1c"] / c["distinct"] for r in res for c in r["checkpoints"] if c["epoch"] == e and c["distinct"]]
        l1c[e] = round(sum(v) / len(v), 4) if v else None
    summ = {"classification": cls, "PLANT_L2_runs": l2, "n": len(res), "reference": ref,
            "per_cell_L2": {c: sum(ever(r) for r in res if r["cell"] == c) for c in ("7ae3", "ffa6")},
            "L4": sum(r["depth"] >= 20 for r in res),
            "first_L2_epochs": sorted(next(c["epoch"] for c in r["checkpoints"] if c["L2"]) for r in res if ever(r)),
            "mean_share_genomes_with_blockcopy_by_epoch": l1c}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
