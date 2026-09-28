"""X-A3-ENDOSTATE-R (EXPLORE, RULER REPAIR / re-measurement of X-P2-ENDOSTATE; ARC3 Blocks S, G). Declared before running.
Theory-aware. LIGHT (existing genomes only; <= 2 processes; no world runs).

X-P2-ENDOSTATE (CLEAN_NULL: early 0.85 vs late 0.88 robust in persistent-register runaway lineages; "establishment sorts
already-robust founders") used the single-k self-state ruler that X-A3-FORENSIC-16000006 showed to be a one-point snapshot of
CYCLING carried state. Question: with repaired rulers, is the P2 reading (no within-population rise in state robustness) still
supported?
Sample: EXACTLY X-P2-ENDOSTATE's 353 genomes (its RESULTS.json: cell, seed, tag a/b/c = first/middle/last checkpoint).
Rulers (each declared here):
  CYCLE_ROBUST  copy rate (X-DD-SELFSTATE method) after k = 1..6 own executions >= 0.25 x the fresh rate at >= 5 of the 6 k,
                among genomes with fresh rate > 0;
  STATE_FREE    fresh-start-style competence (X-A3-FAIR fair_assay: both organisms enter the state) rate >= 0.5 over 20 seeds
                from BOTH fixed random entry states R1 and R2 of X-A3-FAIR (a genome that sets every register it uses).
Per run (same runs as X-P2-ENDOSTATE with >= 3 measurable genomes at both a and c): share at a and at c, per ruler.
Classification (per ruler, reported separately; the graph class is taken from STATE_FREE, the less state-schedule-dependent
ruler): SIGNAL if in >= 70% of runs the share at c exceeds a by >= 0.20; CLEAN_NULL if <= 30% of runs rise AND the pooled shares
differ by <= 0.10; WEAK_SIGNAL otherwise.
Declared caveat: population-level shares cannot separate within-lineage change from replacement (T-INS-LINEAGE).
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
W1 = ROOT / "npe-w1-donor-discovery-2026-09-26"
ES = ROOT / "npe-p2-endogenous-heredity-2026-09-27" / "x_p2_endostate"
FAIR = HERE.parent / "x_a3_fair"
for p in (FAIR, W1 / "x_dd_selfstate", W1 / "x_dd_nocopy_context", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          ROOT / "c9x-explore-2026-09-24" / "x_donor_swap", ROOT / "z80atlas-verify-2026-09-22", ROOT.parent / "lib"):
    sys.path.insert(0, str(p))


def job(r):
    import world
    import run_dc
    import run_dd
    import run_ds
    import run_fair
    import run_ss
    run_ss.HERE = HERE / "scratch"
    run_ss.KMAX = 6
    k = run_ss.job(("ANY", r["cell"], r["seed"], r["hex"]))["rates_by_k"]
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[r["cell"]]]
    R = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    g = bytes.fromhex(r["hex"])
    sf = all(run_fair.fair_assay(world, R, g, e, "ESR" + r["hex"], 20) >= 0.5 for e in ("R1", "R2"))
    return {**{x: r[x] for x in ("cell", "seed", "tag", "epoch", "hex")}, "rates_k": k,
            "measurable": k[0] > 0, "cycle_robust": k[0] > 0 and sum(v >= 0.25 * k[0] for v in k[1:7]) >= 5, "state_free": sf,
            "old_robust": r["robust"]}


def classify(res, key):
    runs = sorted({(r["cell"], r["seed"]) for r in res})
    ok, rise, pe_s, pe_n, pl_s, pl_n = 0, 0, 0, 0, 0, 0
    for key_ in runs:
        a = [r for r in res if (r["cell"], r["seed"]) == key_ and r["tag"] == "a" and r["measurable"]]
        c = [r for r in res if (r["cell"], r["seed"]) == key_ and r["tag"] == "c" and r["measurable"]]
        if len(a) >= 3 and len(c) >= 3:
            ok += 1
            sa, sc = sum(r[key] for r in a) / len(a), sum(r[key] for r in c) / len(c)
            rise += (sc - sa) >= 0.20
            pe_s += sum(r[key] for r in a); pe_n += len(a); pl_s += sum(r[key] for r in c); pl_n += len(c)
    pe, pl = (pe_s / pe_n if pe_n else 0), (pl_s / pl_n if pl_n else 0)
    cls = ("INVALID" if not ok else "SIGNAL" if rise >= 0.7 * ok else
           "CLEAN_NULL" if rise <= 0.3 * ok and abs(pl - pe) <= 0.10 else "WEAK_SIGNAL")
    return {"classification": cls, "runs_measurable": ok, "runs_with_rise": rise, "pooled_early": round(pe, 4), "pooled_late": round(pl, 4)}


def main():
    (HERE / "scratch" / "results").mkdir(parents=True, exist_ok=True)
    src = json.loads((ES / "RESULTS.json").read_text())
    with mp.Pool(2, maxtasksperchild=25) as pool:
        res = list(pool.imap(job, src))
    (HERE / "RESULTS.json").write_text(json.dumps(res))
    summ = {"STATE_FREE": classify(res, "state_free"), "CYCLE_ROBUST": classify(res, "cycle_robust"),
            "agreement_old_vs_cycle": sum(r["old_robust"] == r["cycle_robust"] for r in res if r["measurable"]),
            "measurable": sum(r["measurable"] for r in res)}
    summ["classification"] = summ["STATE_FREE"]["classification"]
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
