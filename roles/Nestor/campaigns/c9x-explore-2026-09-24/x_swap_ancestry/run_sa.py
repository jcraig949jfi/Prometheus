"""X-SWAP-ANCESTRY (EXPLORE, MEASUREMENT; child of X-ATOMIC-RANDOM). Declared before running.

X-ATOMIC-RANDOM (SIGNAL): in 7ae3's cell a random implant gives 0/80 world-level runaways vs the
genome's 46/80, and in every genome runaway 100% of the final population carries the founder
ancestry marker (anc == 0) even where the founder's CERTIFIED causal chain stops at depth 5-22. So
"not founder-rooted" (X-SWAP-ORIGIN, X-ROOT-AUDIT) meant "outside the P-11-certified causal
lineage", not "native". X-SWAP-ORIGIN labelled the foreign 9cba/e160 runaways NATIVE on that
narrower basis. Question: are the X-DONOR-SWAP foreign runaways that are not founder-rooted
(9cba s5, e160 s0, ffa6 s2, ffa6 s4) descended from the implanted founder by ancestry?

Replay those four runs (same cell, seed, ATOMIC runner, 7ae3 implant) with the X-SWAP-ORIGIN
tracker plus the final share of live organisms with anc == 0. Positive reference: ffa6 s5 (founder-
rooted, founder depth 161) replayed alongside.
INVALID if any replay's world depth differs from the recorded X-DONOR-SWAP depth.
Per run: DESCENDED if anc0_share >= 0.9; NATIVE if anc0_share <= 0.1; MIXED otherwise.
Classification: SIGNAL if 9cba s5 and e160 s0 are both DESCENDED (the genome's lineage runs away in
cells where the founder itself cannot copy from a fresh state); CLEAN_NULL if both NATIVE;
WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DS = HERE.parent / "x_donor_swap"
sys.path.insert(0, str(HERE.parent / "x_swap_origin"))
sys.path.insert(0, str(DS))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
RUNS = [("9cba", 5), ("e160", 0), ("ffa6", 2), ("ffa6", 4), ("ffa6", 5)]


def job(args):
    short, s = args
    import world
    import run_ds
    import run_so
    sp = next(k for k in run_ds.cells() if k.startswith(short))
    arm = run_ds.cells()[sp]
    r = run_so.tracked(world, run_ds.runner_cls(world))(dict(arm["cell"], atlas_axis="NONE"), 11_000_000 + s,
                                                        tier=arm["tier"], implant="ACTUAL_GENOME",
                                                        implant_bytes=run_ds.donor_genome())
    out = r.run()
    alive = [o for o in r.orgs if o.alive]
    rec = {"specimen": sp, "s": s, "depth": out["max_causal_replication_depth"], "founder_depth": r.fdepth,
           "anc0_share": round(sum(o.anc == 0 for o in alive) / len(alive), 4) if alive else 0.0,
           "recorded_depth": json.loads((DS / "results" / ("%s_%d.json" % (sp[:16], s))).read_text())["depth"]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (short, s))).write_text(json.dumps(rec))
    return rec


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(5, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in RUNS if "%s_%d" % t not in done]))
    res = {"%s_%d" % t: json.loads((HERE / "results" / ("%s_%d.json" % t)).read_text()) for t in RUNS}
    mism = [k for k, r in res.items() if r["depth"] != r["recorded_depth"]]
    lab = {k: ("DESCENDED" if r["anc0_share"] >= 0.9 else "NATIVE" if r["anc0_share"] <= 0.1 else "MIXED")
           for k, r in res.items()}
    test = [lab["9cba_5"], lab["e160_0"]]
    cls = ("INVALID" if mism else "SIGNAL" if test == ["DESCENDED"] * 2 else
           "CLEAN_NULL" if test == ["NATIVE"] * 2 else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches": mism, "labels": lab, "runs": res}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
