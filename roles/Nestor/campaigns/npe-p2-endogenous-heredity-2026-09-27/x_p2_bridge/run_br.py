"""X-P2-BRIDGE (EXPLORE, CELL_AXIS x STATE / causal bridge; program P2 Blocks B, C, E). Declared before running.
Theory-aware by date. Operator directive 2026-09-27 (prompts/2026-09-27_endogenous_heredity_program/).

W1: fresh-state execution raised donor establishment in ffa6 (C-STATELESS-FFA6 CONFIRMED, 0.33 -> 0.81) but not
confirmably in 7ae3 (C-STATELESS: 3/8 -> 4/8). The two cells differ in exactly two axes: representation
(7ae3 Z8_64: per-byte mutation that can shift the reading frame; ffa6 Z8_SLOTTED: slot-aligned edits, no
frame shift) and structure (7ae3 WELL_MIXED; ffa6 NICHES_HIGH_MIG: 4 niches, migration 0.08; the pair epoch
pairs across niches, so structure acts through niche environments and migration only).
Questions:
  B  Which axis makes register-state persistence an establishment barrier -- representation or structure?
  C  Does a donor's success depend on copying before its own state poisons it (donor execution age at its
     certified copies)?
  E  Where along the chain does heredity fail: accepted copy -> certified causal copy -> competent descendant
     -> descendant's own certified copy -> runaway?

Scaffold (LABELLED; a mechanistic probe of establishment, never a claim about spontaneous acquisition): a
fresh-start-competent donor genome from the W1 corpus is implanted as the single founder in a random
population. Donor panel (fixed before running): for each W1 cell, the first competent genome of the first 8
DENSE_COPY runs (X-DD-DENSE-COPY, by seed) with any L2 -- 16 donors, 8 born in 7ae3 and 8 in ffa6.
Cells (7ae3's H2 B-arm cell, atlas_axis NONE, tier M, one axis changed at a time):
  C7   7ae3 as is;  C7S  7ae3 with representation Z8_SLOTTED;  C7N  7ae3 with structure NICHES_HIGH_MIG;
  CF   7ae3 with both (= ffa6's cell).
State arms: PERSIST (the X-DONOR-SWAP ATOMIC runner) and STATELESS (X-DD-STATELESS runner: fresh registers
before every interaction). Dense VM throughout (the donors are dense-VM genomes), set explicitly per job.
Runs: 16 donors x 2 seeds (21_000_000 + 2*d + k) per (cell, state): 8 arms x 32 = 256 runs, max_epochs 500.
Readouts per run (founder = the implanted organism; lineage L = organisms born from L members by accepted
replication events; causal lineage Lc = the same through P-11 causal births only):
  S1 an accepted replication event from L;  S2 a P-11 causal birth from the founder;
  S3 a non-founder member of Lc is COMPETENT (fresh-start, cached per genome) at a 20-epoch check;
  S4 a P-11 causal birth whose parent is a non-founder member of Lc;
  S5 world causal depth >= 20 by epoch 500 AND final anc0 share >= 0.9 (ESTABLISHED).
  Also: the founder's execution age (executions since its genome last changed) at each of its first 10
  causal births; the epoch of each stage.
Shortened ruler, declared: S5 is judged at epoch 500, not 2000.
Primary effect per cell: E(cell) = S5 share(STATELESS) - S5 share(PERSIST).
Classification (question B):
  SIGNAL      if E(CF) - E(C7) >= 0.25 (the split replicates with implanted donors) AND exactly one of
              E(C7S), E(C7N) is >= E(C7) + 0.20 while the other is < E(C7) + 0.10 (one axis carries it);
  WEAK_SIGNAL if the split replicates but the axis is not resolved as above;
  CLEAN_NULL  if E(CF) - E(C7) < 0.10 (with implanted donors the split does not replicate: W1's split was
              about the donors that arise, not about establishment physics).
Secondary (never decisive): donor-origin factor (7ae3-born vs ffa6-born donors in each cell), S1-S4 per
arm, founder copy ages by outcome.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
for p in (W1 / "x_dd_stateless", W1 / "x_dd_establish", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
SPEC7 = "7ae3f9c1437c8000-s54765-tL-a0"
CELLS = {"C7": {}, "C7S": {"representation": "Z8_SLOTTED"}, "C7N": {"structure": "NICHES_HIGH_MIG"},
         "CF": {"representation": "Z8_SLOTTED", "structure": "NICHES_HIGH_MIG"}}
STATES = ("PERSIST", "STATELESS")
SEED0 = 21_000_000
MAXE = 500
EVERY = 20


def donors():
    out = []
    dc = W1 / "x_dd_dense_copy" / "results"
    for cell in ("7ae3", "ffa6"):
        k = 0
        for s in range(48):
            p = dc / ("DENSE_COPY_%s_%d.json" % (cell, 16_000_000 + s))
            r = json.loads(p.read_text())
            cp = next((c for c in r["checkpoints"] if c["L2"] > 0), None)
            if cp is None:
                continue
            out.append({"origin": cell, "run_seed": r["seed"], "hex": cp["competent_genomes"][0]["hex"]})
            k += 1
            if k == 8:
                break
    return out


def jobs():
    D = donors()
    return [(cell, st, d, SEED0 + 2 * d + k) for cell in CELLS for st in STATES for d in range(len(D)) for k in range(2)]


def job(args):
    cell, st, d, seed = args
    import world
    import run_dc
    import run_de
    import run_ds
    import run_sl
    world.z8 = run_dc.dense_z8()
    D = donors()[d]
    base = run_ds.cells()[SPEC7]
    celld = dict(base["cell"], atlas_axis="NONE", **CELLS[cell])
    cache = {}
    S = {"S1": None, "S2": None, "S3": None, "S4": None, "founder": None, "L": set(), "Lc": set(),
         "age": {}, "founder_ages": [], "births_L": 0, "causal_L": 0}

    Base = run_sl.runner(world, st == "STATELESS")

    class Br(Base):
        def _pair_interact(self, i, a, b):
            pre = [(o, o.oid, bytes(self._genome(o))) for o in (a, b)]
            self._cur = {o.oid for o in (a, b)}
            super()._pair_interact(i, a, b)
            for o, oid, g in pre:
                if o.oid != oid or bytes(self._genome(o)) != g:
                    S["age"][o.oid] = 0
                else:
                    S["age"][o.oid] = S["age"].get(oid, 0) + 1

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if S["founder"] is not None and parent in S["L"]:
                S["L"].add(child)
                S["births_L"] += 1
                if S["S1"] is None:
                    S["S1"] = self.epoch
            if S["founder"] is not None and causal and parent in S["Lc"]:
                S["Lc"].add(child)
                S["causal_L"] += 1
                if parent == S["founder"]:
                    if S["S2"] is None:
                        S["S2"] = self.epoch
                    if len(S["founder_ages"]) < 10:
                        S["founder_ages"].append(S["age"].get(parent, 0))
                elif S["S4"] is None:
                    S["S4"] = self.epoch
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            if S["founder"] is None:
                f = next(o for o in self.orgs if o.anc == 0)
                S["founder"] = f.oid
                S["L"] = {f.oid}
                S["Lc"] = {f.oid}
                S["age"][f.oid] = 0
            super().step()
            if self.epoch % EVERY == 0 and S["S3"] is None:
                for o in self.orgs:
                    if o.alive and o.oid in S["Lc"] and o.oid != S["founder"]:
                        if run_de.competent(world, self, bytes(self._genome(o)), cache):
                            S["S3"] = self.epoch
                            break

    r = Br(celld, seed, tier=base["tier"], max_epochs=MAXE, implant="ACTUAL_GENOME",
           implant_bytes=bytes.fromhex(D["hex"]))
    out = r.run()
    alive = [o for o in r.orgs if o.alive]
    anc0 = sum(o.anc == 0 for o in alive) / len(alive) if alive else 0.0
    depth = out["max_causal_replication_depth"]
    rec = {"cell": cell, "state": st, "donor": d, "origin": D["origin"], "seed": seed, "depth": depth,
           "anc0": round(anc0, 4), "S1": S["S1"], "S2": S["S2"], "S3": S["S3"], "S4": S["S4"],
           "S5": depth >= 20 and anc0 >= 0.9, "founder_ages": S["founder_ages"],
           "births_L": S["births_L"], "causal_L": S["causal_L"], "epochs": r.epoch}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%s_%d_%d.json" % (cell, st, d, seed))).write_text(json.dumps(rec))
    return rec


def main():
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "DONORS.json").write_text(json.dumps(donors(), indent=1))
    todo = jobs()
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%s_%d_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    tab = {}
    for c in CELLS:
        for st in STATES:
            rows = [r for r in res if r["cell"] == c and r["state"] == st]
            n = len(rows)
            tab["%s/%s" % (c, st)] = {"n": n, **{k: round(sum(r[k] is not None for r in rows) / n, 4) for k in ("S1", "S2", "S3", "S4")},
                                      "S5": round(sum(r["S5"] for r in rows) / n, 4),
                                      "S5_by_origin": {o: [sum(r["S5"] for r in rows if r["origin"] == o),
                                                           sum(1 for r in rows if r["origin"] == o)] for o in ("7ae3", "ffa6")}}
    E = {c: round(tab[c + "/STATELESS"]["S5"] - tab[c + "/PERSIST"]["S5"], 4) for c in CELLS}
    split = E["CF"] - E["C7"]
    up = {k: E[k] >= E["C7"] + 0.20 for k in ("C7S", "C7N")}
    lo = {k: E[k] < E["C7"] + 0.10 for k in ("C7S", "C7N")}
    one_axis = (up["C7S"] and lo["C7N"]) or (up["C7N"] and lo["C7S"])
    cls = ("INVALID" if len(res) != len(todo) else "SIGNAL" if split >= 0.25 and one_axis else
           "CLEAN_NULL" if split < 0.10 else "WEAK_SIGNAL")
    ages = {}
    for st in STATES:
        for outcome in (True, False):
            v = [a for r in res if r["state"] == st and r["S5"] == outcome for a in r["founder_ages"][:1]]
            ages["%s/%s" % (st, "est" if outcome else "stall")] = {"n": len(v), "first_copy_age_0": sum(a == 0 for a in v),
                                                                    "first_copy_age_ge1": sum(a >= 1 for a in v)}
    summ = {"classification": cls, "E": E, "split_CF_minus_C7": round(split, 4), "table": tab,
            "founder_first_causal_copy_age": ages}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
