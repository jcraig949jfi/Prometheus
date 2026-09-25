"""C-ENERGY (CONFIRM lane, fresh and frozen). Parent: X-ENERGY-INHERIT (EXPLORE SIGNAL:
depth >= 2 in 7/19 cells with energy inheritance vs 1/19 without).

NOTHING HERE MAY CHANGE AFTER COMMIT: cells, seeds, arms, endpoint, rule, allocation.

Claim under test: in FREE non-pair physics under energy-economy pressures, the seeded
copier's lineage stops at depth 1 because a newborn starts with zero energy; transferring
half the parent's energy at birth (energy conserved) lets children replicate.

Fresh sample: tier-M FREE-physics (ENDOGENOUS_COPY / ENDOGENOUS_PARTIAL / CONSTRUCTIVE),
copy_primitive BLOCK, pressure in {COMPETITION, METABOLIC, RESOURCE_GATED}, from the 1,255
random-start predecessor runs, EXCLUDING every cell used by X-NONPAIR-SEARCH or C-SELFLOC;
the first 40 in ascending sha256(run_id). Seeds 9_850_000 + k (never used).
Arms (shared seed): BASE = implant + free self-location + in-place search (as SEED_LOC);
INHERIT = BASE + half-energy transfer at every accepted endogenous birth.
Primary endpoint: max_causal_replication_depth >= 2 (a child replicated).
Rule: CONFIRMED iff  (#INHERIT>=2) - (#BASE>=2) >= 4  AND  the exact one-sided sign test on
discordant cells (INHERIT>=2 & BASE<2 versus the reverse) gives p < 0.05.
Declared prediction, reported not decided: the effect is in COMPETITION and METABOLIC,
absent in RESOURCE_GATED (as in the exploration).

    python run_ce.py [workers] -> CELLS.json, RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CAMP = ROOT.parent
C9 = CAMP / "z80atlas-verify-2026-09-22"
FOR = CAMP / "z80atlas-forensics-2026-09-23"
sys.path.insert(0, str(C9))
ENERGY = ("COMPETITION", "METABOLIC", "RESOURCE_GATED")


def cells():
    runs = [json.loads(l) for l in open(FOR / "FROZEN_FUNNEL_RUNS.jsonl")]
    used = {c["source_run"] for f in (ROOT / "x_nonpair_search" / "CELLS.json",
                                       ROOT / "c_selfloc_confirm" / "CELLS.json")
            for c in json.loads(f.read_text())}
    sys.path.insert(0, str(FOR))
    import forensic
    cand = []
    for r in runs:
        if r["physics"] == "OVERWRITE" or r["tier"] != "M" or r["copy_primitive"] != "BLOCK" \
                or r["run_id"] in used:
            continue
        cfg, _ = forensic.frozen_record(r["run_id"])
        if cfg["job"]["cell"]["pressure"] in ENERGY:
            cand.append({"source_run": r["run_id"], "physics": r["physics"], "cell": cfg["job"]["cell"]})
    cand.sort(key=lambda c: hashlib.sha256(c["source_run"].encode()).hexdigest())
    return cand[:40]


def job(args):
    k, cell, arm = args
    import world
    import z8
    motif, _ = z8.asm("ALLOC\nLDIR\nBIRTH\nHALT")

    class Base(world.Runner):
        def step(self):
            for o in self.orgs:
                if o.alive:
                    g = self._mutate(self._genome(o))
                    self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                    self.mem[o.slot:o.slot + len(g)] = g
                    o.length = len(g)
            return super().step()

        def _execute(self, o):
            r = list(o.regs) if o.regs is not None else [0] * 8
            r[4], r[5] = (o.slot >> 8) & 0xFF, o.slot & 0xFF
            r[0], r[1] = (o.length >> 8) & 0xFF, o.length & 0xFF
            o.regs = r
            return super()._execute(o)

    class Inherit(Base):
        def _on_birth(self, o, ctx, dst, cnt, partial):
            n0 = len(self.orgs)
            ok = super()._on_birth(o, ctx, dst, cnt, partial)
            if ok and len(self.orgs) > n0:
                child = self.orgs[-1]
                half = o.energy * 0.5
                o.energy -= half
                child.energy += half
            return ok

    R = Inherit if arm == "INHERIT" else Base
    s = R(cell, 9_850_000 + k, tier="M", implant="ACTUAL_GENOME", implant_bytes=motif).run()
    return {"k": k, "arm": arm, "pressure": cell["pressure"],
            "max_causal_depth": s["max_causal_replication_depth"]}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cs = cells()
    (HERE / "CELLS.json").write_text(json.dumps(cs, indent=1))
    todo = [(k, c["cell"], arm) for k, c in enumerate(cs) for arm in ("BASE", "INHERIT")]
    with mp.Pool(workers) as pool:
        res = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    B = {r["k"]: r for r in res if r["arm"] == "BASE"}
    I = {r["k"]: r for r in res if r["arm"] == "INHERIT"}
    b2 = sum(B[k]["max_causal_depth"] >= 2 for k in B)
    i2 = sum(I[k]["max_causal_depth"] >= 2 for k in I)
    up = sum(1 for k in B if I[k]["max_causal_depth"] >= 2 > B[k]["max_causal_depth"])
    down = sum(1 for k in B if B[k]["max_causal_depth"] >= 2 > I[k]["max_causal_depth"])
    n = up + down
    p = sum(math.comb(n, x) for x in range(up, n + 1)) / 2 ** n if n else 1.0
    per = {}
    for pr in ENERGY:
        ks = [k for k in B if B[k]["pressure"] == pr]
        per[pr] = {"cells": len(ks), "BASE_ge2": sum(B[k]["max_causal_depth"] >= 2 for k in ks),
                   "INHERIT_ge2": sum(I[k]["max_causal_depth"] >= 2 for k in ks)}
    v = {"verdict": "CONFIRMED" if (i2 - b2 >= 4 and p < 0.05) else "NOT_CONFIRMED",
         "cells": len(cs), "BASE_depth_ge2": b2, "INHERIT_depth_ge2": i2,
         "discordant_up": up, "discordant_down": down, "sign_test_p": p,
         "per_pressure_prediction_readout": per}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
