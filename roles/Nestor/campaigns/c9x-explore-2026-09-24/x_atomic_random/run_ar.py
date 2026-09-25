"""X-ATOMIC-RANDOM (EXPLORE, CONTROL / missing null; child of X-ROOT-AUDIT). Declared before running.

X-ROOT-AUDIT (WEAK_SIGNAL): of C-ATOMIC C1's 46/80 ATOMIC world-level runaways only 12 are rooted
in the implanted 7ae3 founder's causal lineage (founder-rooted 12/80 vs 0/80, p = 1.6e-4; C1's 0.25
effect bar missed). C-ATOMIC compared ATOMIC vs BASE with the 7ae3 genome implanted in BOTH arms;
it never ran ATOMIC without the genome. Question: in 7ae3's cell, does ATOMIC write-back produce
world-level runaway heredity without the 7ae3 genome?

Arm R: 7ae3's cell (atlas_axis NONE, manifest tier), ATOMIC (X-DONOR-SWAP runner = C-ATOMIC logic),
implant RANDOM_MATCHED (64 random bytes), seeds 12_000_000 + s, s < 80 (C1's seeds; the worlds
diverge from the first interaction, so pairing is nominal).
Arm G (replay check + ancestry reference): the 7ae3 genome, ATOMIC, seeds s < 16; each world depth
must equal the recorded C-ATOMIC depth.
Readouts per run: world runaway (max causal depth >= 20), founder_depth (X-SWAP-ORIGIN tracker),
and at the end the share of live organisms carrying the founder ancestry marker (anc == 0,
inherited through ANY birth or overwrite).
INVALID if any arm-G world depth differs from the recorded C-ATOMIC depth.
Classification (question: is the genome needed for C1's world-level effect; reference = C1's
recorded 46/80): SIGNAL (genome needed) if arm-R runaways <= 10/80 AND one-sided Fisher p < 0.001
against 46/80; CLEAN_NULL (genome not needed) if arm-R runaways >= 30/80; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAT = HERE.parent / "c_atomic" / "results"
sys.path.insert(0, str(HERE.parent / "x_swap_origin"))
sys.path.insert(0, str(HERE.parent / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
NR, NG, REF = 80, 16, 46


def job(args):
    armname, seed = args
    import world
    import run_ds
    import run_so
    arm = run_ds.cells()[SPEC]
    kw = dict(implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    if armname == "R":
        kw = dict(implant="RANDOM_MATCHED", implant_bytes=run_ds.donor_genome(), implant_len=64)
    r = run_so.tracked(world, run_ds.runner_cls(world))(dict(arm["cell"], atlas_axis="NONE"), seed,
                                                        tier=arm["tier"], **kw)
    out = r.run()
    alive = [o for o in r.orgs if o.alive]
    rec = {"arm": armname, "seed": seed, "depth": out["max_causal_replication_depth"],
           "founder_depth": r.fdepth,
           "anc0_share": round(sum(o.anc == 0 for o in alive) / len(alive), 4) if alive else 0.0}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (armname, seed))).write_text(json.dumps(rec))
    return rec


def fisher(a, b, n):
    k0 = a + b
    return (sum(math.comb(n, x) * math.comb(n, k0 - x) for x in range(a, min(n, k0) + 1))
            / math.comb(2 * n, k0)) if k0 else 1.0


def desc(rows):
    ra = [r for r in rows if r["depth"] >= 20]
    return {"n": len(rows), "world_runaways": len(ra),
            "founder_rooted": sum(r["founder_depth"] >= 20 for r in rows),
            "mean_anc0_share_runaways": round(sum(r["anc0_share"] for r in ra) / len(ra), 4) if ra else None,
            "mean_anc0_share_all": round(sum(r["anc0_share"] for r in rows) / len(rows), 4) if rows else None}


def main():
    todo = [("G", 12_000_000 + s) for s in range(NG)] + [("R", 12_000_000 + s) for s in range(NR)]
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    G = [r for r in res if r["arm"] == "G"]
    R = [r for r in res if r["arm"] == "R"]
    mism = [r["seed"] for r in G
            if r["depth"] != json.loads((CAT / ("%s_%d_ATOMIC.json" % (SPEC[:16], r["seed"]))).read_text())["depth"]]
    rr = sum(r["depth"] >= 20 for r in R)
    p = fisher(REF, rr, NR)
    cls = ("INVALID" if mism or len(res) != len(todo) else "SIGNAL" if rr <= 10 and p < 0.001 else
           "CLEAN_NULL" if rr >= 30 else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches_G": mism, "reference_C1_ATOMIC_runaways": "%d/%d" % (REF, NR),
            "fisher_p_ref_vs_R": p, "G": desc(G), "R": desc(R), "runs": res}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
