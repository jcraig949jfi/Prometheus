"""NEUTRAL process for the Q2 baseline pilot (and the Q1 landscape predictor).

Computational artificial life: integer programs on the z8 VM. Nothing biological.

The soup (ATOMIC runner, PAIR_TAPE, QUALITY_DIVERSITY, pop 256, 2000 epochs) gives every live
organism exactly ONE world._mutate call per epoch that persists (the ATOMIC write-back of the
pre-interaction genome, mutated), unless the organism is overwritten by a replication event.
There is no death, reaping or immigration in these two cells (pop stays at the cap).
The neutral process keeps everything but the interaction:
  * SAME initial population: world.Runner.run()'s own initialisation, same cell, same seed
    16_000_000 + s (and, for the PLANT material, run_pl's own planting RNG and rule);
  * SAME mutation opportunities: one real world._mutate call per organism per epoch (the cell's
    operator and rate, drawn from the runner's own RNG), 2000 epochs;
  * SAME evaluations: every 100 epochs every distinct live genome is screened with run_dd.screen
    (4-seed stage 1, 20-seed COMPETENT), with the same VM the soup arm used;
  * NO execution in the world, no pair tape, no copying, no overwrites, no carried register state.
One walk is screened under several VMs (the mutation operator does not depend on the VM: world
._boundaries uses z8.dis, which the dense/sham patches do not change), so PLAIN/DENSE/SHAM neutral
arms share their genomes exactly, as their soups share initial material.

Usage: python neutral.py <material RANDOM|PLANT> <cell> <s0> <s1> [epochs]  -> results_neutral/*.json
"""
from __future__ import annotations

import json
import pathlib
import random
import sys
import time

import acc_lib as A

OUT = A.HERE / "results_neutral"
EVERY = 100
PATS = (bytes((0xED, 0xB0)), bytes((0xED, 0xB8)))


def run_one(material, cell, seed, epochs=2000, vms=None):
    import world
    import run_dd
    import run_ds
    world.z8 = A.vm("STOCK")
    vms = vms or (("STOCK", "DENSE", "SHAM") if material == "RANDOM" else ("STOCK",))
    a = run_ds.cells()[A.CELLS[cell]]
    prng = random.Random(("X-P2-PLANT", seed).__repr__())       # run_pl's planting RNG, verbatim
    st = {"planting": material == "PLANT"}
    cps = {v: [] for v in vms}
    t0 = time.time()
    nmut = {"calls": 0, "changed": 0}

    class Neutral(world.Runner):
        def _place(self, genome, anc, pid=None, niche=0):
            if st["planting"]:
                g = bytearray(genome)
                if len(g) >= 2:
                    p = prng.randrange(0, len(g) - 1)
                    g[p:p + 2] = PATS[prng.randrange(2)]
                    genome = bytes(g)
            return super()._place(genome, anc, pid, niche)

        def step(self):
            st["planting"] = False
            for o in self.orgs:
                if not o.alive:
                    continue
                g = self._genome(o)
                new = self._mutate(g)
                nmut["calls"] += 1
                nmut["changed"] += new != g
                self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                self.mem[o.slot:o.slot + len(new)] = new
                o.length = len(new)
            self.epoch += 1
            if self.epoch % EVERY == 0:
                gs = sorted({bytes(self._genome(o)) for o in self.orgs if o.alive})
                for v in vms:
                    world.z8 = A.vm(v)
                    c = run_dd.screen(world, self, gs, ("NEUTRAL", material, v, cell, seed, self.epoch))
                    world.z8 = A.vm("STOCK")
                    c["epoch"] = self.epoch
                    c["L1c"] = sum(any(q in g for q in PATS) or (v == "DENSE" and (0xE5 in g or 0xE7 in g))
                                   for g in gs)
                    cps[v].append(c)

    r = Neutral(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"], max_epochs=epochs)
    r.run()
    rec = {"material": material, "cell": cell, "seed": seed, "epochs": epochs, "mutate_calls": nmut["calls"],
           "mutate_calls_that_changed": nmut["changed"], "wall_s": round(time.time() - t0, 1), "arms": {}}
    for v in vms:
        rec["arms"][v] = [{k: c[k] for k in ("epoch", "distinct", "L1c", "stage1", "L2", "best_fid_final",
                                             "best_auth_share", "draws", "C2")}
                          | {"competent_hex": [x["hex"] for x in c["competent_genomes"]][:5]} for c in cps[v]]
    OUT.mkdir(exist_ok=True)
    (OUT / ("%s_%s_%d.json" % (material, cell, seed))).write_text(json.dumps(rec))
    return rec


if __name__ == "__main__":
    mat, cell, s0, s1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ep = int(sys.argv[5]) if len(sys.argv) > 5 else 2000
    for s in range(s0, s1):
        f = OUT / ("%s_%s_%d.json" % (mat, cell, 16_000_000 + s))
        if f.exists() and ep == 2000:
            continue
        rec = run_one(mat, cell, 16_000_000 + s, ep)
        print(mat, cell, s, rec["wall_s"], {v: sum(c["L2"] > 0 for c in cp) for v, cp in rec["arms"].items()},
              flush=True)
