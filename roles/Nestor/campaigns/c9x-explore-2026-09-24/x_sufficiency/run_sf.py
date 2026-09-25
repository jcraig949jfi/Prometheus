"""X-SUFFICIENCY (EXPLORE, MEASUREMENT; child of X-STATE). Declared before running.

X-STATE: inside a runaway, 98% of P-11 copies pass with FRESH registers (genome-sufficient),
whereas the founder genome copies only from its observed register state (X-POSITION: 0/16
panel donors copy from fresh registers). Hypothesis: runaway = the emergence of a
register-independent (genome-sufficient) copier.

Test: C-RUNAWAY's splice-off seeds - all 7 runaways, and the 14 lowest-index non-runaway seeds
that had >= 1 P-11 event. Replay epochs 1-200 of each; for up to 60 P-11-passing events sampled
evenly, re-assay with fresh registers. Readout per seed: genome-sufficient share of P-11 copies
and the epoch of the first genome-sufficient copy.
Declared prediction: every runaway seed has a genome-sufficient share >= 0.5 by epoch 200; the
non-runaway seeds have share < 0.2 (or no genome-sufficient copy). Classification: SIGNAL if
>= 6/7 runaways and >= 12/14 non-runaways meet it; CLEAN_NULL if the shares do not separate
(medians within 0.2); WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
C9 = ROOT.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"


def job(args):
    s, runaway = args
    import p11
    import world
    import z8
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    cell = dict(arm["cell"], atlas_axis="NONE")
    cap = []
    real = p11.assay

    def capturing(z8m, **kw):
        out = real(z8m, **kw)
        if out["pass"]:
            cap.append(dict(kw))
        return out
    p11.assay = capturing
    try:
        world.Runner(cell, 9_990_500 + s, tier=arm["tier"], max_epochs=200, implant="ACTUAL_GENOME",
                     implant_bytes=bytes.fromhex(arm["kwargs"]["implant_hex"])).run()
    finally:
        p11.assay = real
    step = max(1, len(cap) // 60)
    sample = cap[::step][:60]
    suff, first = 0, None
    for kw in sample:
        f = real(z8, **dict(kw, st_a=(None, 0, 0), st_b=(None, 0, 0), seed=("X-SUFF",) + tuple(kw["seed"])))
        if f["pass"]:
            suff += 1
            ep = kw["seed"][2]
            first = ep if first is None else min(first, ep)
    return {"s": s, "runaway": runaway, "p11_passes": len(cap), "sampled": len(sample),
            "sufficient_share": round(suff / len(sample), 3) if sample else None, "first_sufficient_epoch": first}


def main():
    res = json.loads((ROOT / "c_runaway_confirm" / "RESULTS.json").read_text())
    off = sorted((r for r in res if r["arm"] == "NO_RECOMB"), key=lambda r: r["s"])
    run = [r["s"] for r in off if r["depth"] >= 20]
    non = [r["s"] for r in off if r["depth"] < 20 and r["p11_events"] > 0][:14]
    todo = [(s, True) for s in run] + [(s, False) for s in non]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        out = pool.map(job, todo)
    (HERE / "RESULTS.json").write_text(json.dumps(out, indent=1))
    R = [o for o in out if o["runaway"]]
    N = [o for o in out if not o["runaway"]]
    r_ok = sum(1 for o in R if (o["sufficient_share"] or 0) >= 0.5)
    n_ok = sum(1 for o in N if (o["sufficient_share"] or 0) < 0.2)
    mr = statistics.median((o["sufficient_share"] or 0) for o in R)
    mn = statistics.median((o["sufficient_share"] or 0) for o in N)
    cls = ("SIGNAL" if r_ok >= 6 and n_ok >= 12 else "CLEAN_NULL" if abs(mr - mn) < 0.2 else "WEAK_SIGNAL")
    summ = {"classification": cls, "runaways_meeting": "%d/%d" % (r_ok, len(R)),
            "non_runaways_meeting": "%d/%d" % (n_ok, len(N)), "median_share_runaway": mr,
            "median_share_non_runaway": mn}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))
    for o in out:
        print(o)


if __name__ == "__main__":
    main()
