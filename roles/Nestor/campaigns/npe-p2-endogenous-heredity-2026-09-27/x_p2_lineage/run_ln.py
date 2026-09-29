"""X-P2-LINEAGE (EXPLORE, MEASUREMENT / localization of the X-P2-ENDOSTATE null; P2 Blocks F, N). Declared before
running. Theory-aware by date.

X-P2-ENDOSTATE: in 13 persistent-register runaway runs of X-DD-DENSE-COPY the early competent genomes include
self-poisoning ones and the late competent genomes are state-robust; Hamming distance cannot tell whether the late
robust genomes DESCEND from the early poisoned donor (within-lineage modification of the reproductive machinery --
a candidate endogenous transition) or REPLACED it (a different, already-robust lineage took over).
Question: do the late state-robust competent genomes belong to the first donor's lineage?

Sample: the 13 runs of X-P2-ENDOSTATE with a poisoned early genome and robust late genomes (listed in PLAN.json at
launch), replayed exactly (DENSE_COPY arm of X-DD-DENSE-COPY: dense VM, ATOMIC runner, same cell and seed; world
depth must equal the record).
Lineage L: D0 = the live organisms whose genome is COMPETENT (fresh-start, X-DD-ESTABLISH's cached screen) at the
first 20-epoch check where any is; L grows by every accepted replication event (any birth, causal or not) whose
parent is in L. An organism leaves L only by being overwritten by a non-L source (it then carries the source's
lineage).
Every 100 epochs: for each distinct live genome that is COMPETENT, whether it is STATE_ROBUST (X-DD-SELFSTATE method,
10 seeds x 2 sides: rate_1 >= 0.25 rate_0) and whether any organism carrying it is in L. Also L's share of the live
population and whether D0's own genome is still present.
Per run at the last checkpoint: share of robust competent genomes that are in L.
Classification: SIGNAL (modification within the donor's lineage) if in >= 70% of runs >= 80% of late robust
competent genomes are in L; CLEAN_NULL (replacement) if in >= 70% of runs <= 20% are in L; WEAK_SIGNAL otherwise.
INVALID if any replay depth differs from its record.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
ES = HERE.parent / "x_p2_endostate"
for p in (W1 / "x_dd_selfstate", W1 / "x_dd_establish", W1 / "x_dd_nocopy_context", W1 / "x_dd_dense_copy",
          W1 / "x_donor_discovery", HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))


def plan():
    res = json.loads((ES / "RESULTS.json").read_text())
    runs = sorted({(r["cell"], r["seed"]) for r in res})
    out = []
    for key in runs:
        rows = [r for r in res if (r["cell"], r["seed"]) == key]
        if any(r["tag"] == "a" and r["rate0"] > 0 and not r["robust"] for r in rows) and \
                any(r["tag"] == "c" and r["robust"] for r in rows):
            rec = json.loads((W1 / "x_dd_dense_copy" / "results" / ("DENSE_COPY_%s_%d.json" % key)).read_text())
            out.append((key[0], key[1], rec["depth"]))
    return out


def robust(world, r, g, cache, cell, seed):
    if g in cache:
        return cache[g]
    import run_ss
    run_ss.HERE = HERE / "scratch"
    rec = run_ss.job(("ANY", cell, seed, g.hex()))
    k = rec["rates_by_k"]
    cache[g] = (k[0] > 0, k[0] > 0 and k[1] >= 0.25 * k[0])
    return cache[g]


def job(args):
    cell, seed, recorded = args
    import world
    import run_dc
    import run_dd
    import run_de
    import run_ds
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    ccache, rcache = {}, {}
    S = {"d0": None, "d0_genomes": set(), "L": set(), "cps": []}

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
                comp = [o for o in alive if run_de.competent(world, self, bytes(self._genome(o)), ccache)]
                if comp:
                    S["d0"] = self.epoch
                    S["L"] = {o.oid for o in comp}
                    S["d0_genomes"] = {bytes(self._genome(o)) for o in comp}
            if S["d0"] is not None and self.epoch % 100 == 0:
                inL = {}
                for o in alive:
                    g = bytes(self._genome(o))
                    inL[g] = inL.get(g, False) or (o.oid in S["L"])
                rows = []
                for g, l in inL.items():
                    if run_de.competent(world, self, g, ccache):
                        comp0, rob = robust(world, self, g, rcache, cell, seed)
                        rows.append((rob, l))
                S["cps"].append({"epoch": self.epoch, "L_share": round(sum(o.oid in S["L"] for o in alive) / len(alive), 4),
                                 "d0_genome_present": any(bytes(self._genome(o)) in S["d0_genomes"] for o in alive),
                                 "competent": len(rows), "robust": sum(r for r, _ in rows),
                                 "robust_in_L": sum(r and l for r, l in rows), "nonrobust_in_L": sum((not r) and l for r, l in rows)})

    r = Ln(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"], "recorded_depth": recorded,
           "d0_epoch": S["d0"], "checkpoints": S["cps"]}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def main():
    (HERE / "scratch" / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    todo = plan()
    (HERE / "PLAN.json").write_text(json.dumps(todo))
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(min(10, len(todo)), maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%d" % (t[0], t[1]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mism = [(r["cell"], r["seed"]) for r in res if r["depth"] != r["recorded_depth"]]
    per = []
    for r in res:
        last = next((c for c in reversed(r["checkpoints"]) if c["robust"] > 0), None)
        per.append({"cell": r["cell"], "seed": r["seed"], "d0_epoch": r["d0_epoch"],
                    "last_robust_in_L_share": round(last["robust_in_L"] / last["robust"], 4) if last else None,
                    "last_L_share": last["L_share"] if last else None,
                    "d0_genome_present_last": last["d0_genome_present"] if last else None})
    v = [p["last_robust_in_L_share"] for p in per if p["last_robust_in_L_share"] is not None]
    hi = sum(x >= 0.8 for x in v)
    lo = sum(x <= 0.2 for x in v)
    cls = ("INVALID" if mism or len(res) != len(todo) or not v else "SIGNAL" if hi >= 0.7 * len(v) else
           "CLEAN_NULL" if lo >= 0.7 * len(v) else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches": mism, "n": len(v), "runs_mostly_in_L": hi,
            "runs_mostly_outside_L": lo, "per_run": per}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
