"""X-ACQUIRE (EXPLORE, MEASUREMENT / mechanism; child of X-SWAP-ANCESTRY). Declared before running.

X-SWAP-ANCESTRY (SIGNAL): the 9cba s5 and e160 s0 runaways of X-DONOR-SWAP are founder-descended
(anc == 0 share 0.99, 1.0), though the founder genome's fresh-state P-11 copy rate in those cells is
0.0. Question: did the descendants ACQUIRE fresh-state copy competence (a genome change), or do they
replicate without it (carried register state / partner context)?

Replay 9cba s5 and e160 s0 (ATOMIC, 7ae3 implant, as X-DONOR-SWAP; world depth must match the
record). At the end, take every live organism's genome; assay each DISTINCT genome (up to the 40
most frequent) with P-11 from a fresh state in that cell, K = 20 seeds, donor on either side (the
X-DONOR-SWAP assay). A genome is COMPETENT if it passes >= 50% of seeds. Readout: population-weighted
share of live organisms with a competent genome; for the most frequent genome, bytes changed vs the
padded founder and its assay rate.
Controls: the founder genome assayed with the same function in each cell (expected 0.0) and in
7ae3's own cell (expected ~0.95). INVALID if the 7ae3-cell founder control passes < 50%, or a
replay depth mismatches.
Classification: SIGNAL (acquired competence) if the competent share >= 0.5 in both cells; CLEAN_NULL
(replication without fresh-state competence) if < 0.05 in both; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import collections
import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DS = HERE.parent / "x_donor_swap"
sys.path.insert(0, str(DS))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
RUNS = [("9cba", 5), ("e160", 0)]
K = 20
TOP = 40


def assay(world, r, g, tag):
    n, tl = r.L, world._pow2(2 * r.L)
    fresh, hits = (None, 0, 0), 0
    for k in range(K):
        ok = False
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            ok = ok or world.p11.assay(world.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=fresh, st_b=fresh,
                                       budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=r.copy_mut,
                                       victim_side=1 - side, seed=("X-ACQUIRE", tag, k, side))["pass"]
        hits += ok
    return hits / K


def job(args):
    short, s = args
    import world
    import run_ds
    sp = next(k for k in run_ds.cells() if k.startswith(short))
    arm = run_ds.cells()[sp]
    r = run_ds.runner_cls(world)(dict(arm["cell"], atlas_axis="NONE"), 11_000_000 + s, tier=arm["tier"],
                                 implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    out = r.run()
    recorded = json.loads((DS / "results" / ("%s_%d.json" % (sp[:16], s))).read_text())["depth"]
    alive = [o for o in r.orgs if o.alive]
    cnt = collections.Counter(bytes(r._pad(r._genome(o))) for o in alive)
    top = cnt.most_common(TOP)
    rates = {g.hex(): assay(world, r, g, (short, i)) for i, (g, _) in enumerate(top)}
    covered = sum(c for _, c in top)
    comp = sum(c for g, c in top if rates[g.hex()] >= 0.5)
    f = bytes(r._pad(run_ds.donor_genome()))
    g0 = top[0][0]
    rec = {"cell": short, "s": s, "depth": out["max_causal_replication_depth"], "recorded_depth": recorded,
           "alive": len(alive), "distinct": len(cnt), "assayed_cover": round(covered / len(alive), 4),
           "competent_share": round(comp / len(alive), 4),
           "founder_rate_here": assay(world, r, f, (short, "founder")),
           "top_genome": g0.hex(), "top_count": top[0][1], "top_rate": rates[g0.hex()],
           "top_bytes_changed": sum(a != b for a, b in zip(g0, f)) + abs(len(g0) - len(f)),
           "rates": [[g.hex(), c, rates[g.hex()]] for g, c in top]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (short, s))).write_text(json.dumps(rec))
    return rec


def ctrl(_):
    import world
    import run_ds
    arm = run_ds.cells()[run_ds.DONOR]
    r = world.Runner(dict(arm["cell"], atlas_axis="NONE"), 1, tier=arm["tier"],
                     implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    return assay(world, r, r._pad(run_ds.donor_genome()), ("7ae3", "control"))


def main():
    with mp.Pool(2, maxtasksperchild=1) as pool:
        c = pool.apply_async(ctrl, (0,))
        res = pool.map(job, RUNS)
        c7 = c.get()
    mism = [(x["cell"], x["s"]) for x in res if x["depth"] != x["recorded_depth"]]
    sh = [x["competent_share"] for x in res]
    cls = ("INVALID" if mism or c7 < 0.5 else "SIGNAL" if min(sh) >= 0.5 else
           "CLEAN_NULL" if max(sh) < 0.05 else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches": mism, "control_founder_7ae3_cell": c7,
            "runs": [{k: v for k, v in x.items() if k != "rates"} for x in res]}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
