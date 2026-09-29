"""X-A3-SFLINEAGE (EXPLORE, MEASUREMENT / lineage identity of the state-freedom rise; ARC3 Blocks G, T; Thread T-STATE-1).
Declared before running. Theory-aware. LIGHT (5 replays, <= 2 processes).

X-A3-ENDOSTATE-R: in persistent-register (CARRIED, dense VM) runaway populations the share of STATE_FREE competent genomes (competent
from both fixed random entry states R1, R2 of X-A3-FAIR) rises 0.32 -> 0.65; in 5 runs from ~0 to high (7ae3 16000006, 16000021;
ffa6 16000003, 16000005, 16000030). Question: are the late state-free genomes DESCENDED from first donors that were NOT state-free
(internalization of register initialization within a lineage), or did another lineage replace them?
Method (X-P2-LINEAGE's tracker): replay exactly (same cell, seed, dense VM, ATOMIC runner; world depth must equal the record). D0 = the
live organisms COMPETENT (zero-state cached screen) at the first 20-epoch check with any; each distinct D0 genome is measured for
STATE_FREE. L = D0 + every accepted replication whose parent is in L (a member overwritten by a non-L source leaves L). Every 100 epochs
for each distinct live competent genome: STATE_FREE, and whether any organism carrying it is in L.
Per run: D0_ALL_NOT_FREE (every D0 genome not state-free); at the last checkpoint with any state-free competent genome, the share of
state-free competent genomes that are in L.
Classification: SIGNAL (within-lineage internalization) if in >= 3 of the runs with D0_ALL_NOT_FREE, >= 80% of late state-free genomes
are in L; CLEAN_NULL (replacement / sorting) if in >= 70% of all runs <= 20% are in L or D0 already held a state-free genome;
WEAK_SIGNAL otherwise. INVALID on any replay mismatch.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
W1 = ROOT / "npe-w1-donor-discovery-2026-09-26"
FAIR = HERE.parent / "x_a3_fair"
for p in (FAIR, W1 / "x_dd_establish", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          ROOT / "c9x-explore-2026-09-24" / "x_donor_swap", ROOT / "z80atlas-verify-2026-09-22", ROOT.parent / "lib"):
    sys.path.insert(0, str(p))
RUNS = [("7ae3", 16000006), ("7ae3", 16000021), ("ffa6", 16000003), ("ffa6", 16000005), ("ffa6", 16000030)]


def job(args):
    cell, seed = args
    import world
    import run_dc
    import run_dd
    import run_de
    import run_ds
    import run_fair
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    rec_depth = json.loads((W1 / "x_dd_dense_copy" / "results" / ("DENSE_COPY_%s_%d.json" % (cell, seed))).read_text())["depth"]
    cc, sfc = {}, {}
    S = {"d0": None, "d0_free": None, "L": set(), "cps": []}

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
                    gs = sorted({bytes(self._genome(o)) for o in comp})
                    S["d0_free"] = [sf(self, g) for g in gs]
            if S["d0"] is not None and self.epoch % 100 == 0:
                inL = {}
                for o in alive:
                    g = bytes(self._genome(o))
                    inL[g] = inL.get(g, False) or (o.oid in S["L"])
                rows = [(sf(self, g), l) for g, l in inL.items() if run_de.competent(world, self, g, cc)]
                S["cps"].append({"epoch": self.epoch, "L_share": round(sum(o.oid in S["L"] for o in alive) / len(alive), 4),
                                 "competent": len(rows), "free": sum(f for f, _ in rows), "free_in_L": sum(f and l for f, l in rows)})

    r = Ln(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"], "recorded_depth": rec_depth,
           "d0_epoch": S["d0"], "d0_free": S["d0_free"], "checkpoints": S["cps"]}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def main():
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(2, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in RUNS if "%s_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mism = [(r["cell"], r["seed"]) for r in res if r["depth"] != r["recorded_depth"]]
    per = []
    for r in res:
        last = next((c for c in reversed(r["checkpoints"]) if c["free"] > 0), None)
        per.append({"cell": r["cell"], "seed": r["seed"], "d0_epoch": r["d0_epoch"], "d0_free": r["d0_free"],
                    "d0_all_not_free": bool(r["d0_free"]) and not any(r["d0_free"]),
                    "late_free_in_L_share": round(last["free_in_L"] / last["free"], 4) if last else None,
                    "late_L_share": last["L_share"] if last else None})
    clean = [p for p in per if p["d0_all_not_free"] and p["late_free_in_L_share"] is not None]
    within = sum(p["late_free_in_L_share"] >= 0.8 for p in clean)
    repl = sum((p["late_free_in_L_share"] is not None and p["late_free_in_L_share"] <= 0.2) or not p["d0_all_not_free"] for p in per)
    cls = ("INVALID" if mism or len(res) != len(RUNS) else "SIGNAL" if within >= 3 else
           "CLEAN_NULL" if repl >= 0.7 * len(per) else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches": mism, "runs_d0_all_not_free": len(clean),
            "within_lineage_runs": within, "per_run": per}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
