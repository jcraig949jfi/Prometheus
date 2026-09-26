"""C-SWAP-ACQUIRE (CONFIRM lane, fresh and frozen). Parent: X-SWAP-ANCESTRY (EXPLORE, SIGNAL).

NOTHING HERE MAY CHANGE AFTER COMMIT: cells, seeds, arms, endpoints, rules, allocation.

Observation chain: X-DONOR-SWAP ran 7ae3's 64-byte genome as the single founder in foreign panel
cells with ATOMIC write-back. In cells 9cba (self_location PC_RELATIVE) and e160 (NONE) the genome's
fresh-state P-11 copy rate is 0.0 (the ops mask lacks the PRIMITIVE self-location op it uses), yet
one run in each (1/8, 1/8) produced runaway causal heredity; X-SWAP-ANCESTRY showed both runaway
populations are founder-descended (anc == 0 share 0.99 and 1.0), and a random implant gave 0/8 in
both cells (X-SWAP-ORIGIN). Claim under test: in cells where the founder itself cannot copy, the
founder's lineage can still reach runaway heredity -- and the genome, not the ATOMIC world alone,
is what makes it possible.

Scope (declared, post hoc selected on the exploratory result): cells 9cba7113df39009e-s3882-tL-a0
and e16055dd06cff594-s37315-tL-a0, their frozen H2 B-arm cell with atlas_axis NONE and the manifest
tier; ATOMIC write-back exactly as C-ATOMIC (runner of X-DONOR-SWAP, amendment A1 included).
Arms: GENOME = 7ae3's genome implanted as the single founder; RANDOM = RANDOM_MATCHED 64-byte implant.
Seeds: fresh, 13_000_000 + s, s < 120, per cell per arm (240 runs per arm, 480 total). One job per
process.
Endpoint: founder-descended runaway = world max causal replication depth >= 20 AND final share of
live organisms with anc == 0 >= 0.9.
CONFIRMED iff pooled count(GENOME) - count(RANDOM) >= 8 AND one-sided Fisher exact p < 0.001
(GENOME > RANDOM). NOT_CONFIRMED otherwise.
Eligibility (computed before freezing): the p bar binds before the count bar -- with RANDOM = 0 the
minimum GENOME count is 10 (13 if RANDOM = 1, 15 if 2). Power with RANDOM = 0: true rate 3% -> 0.19,
4% -> 0.49, 5% -> 0.76, 6.25% -> 0.94, 8% -> 0.99 (exploratory point estimate 2/16 = 12.5%, a
single event per cell, so the true rate may be far lower). Below ~4% the rule fails by design and
the claim is not made.
Secondary, never decisive: per-cell counts; world runaways regardless of ancestry; founder
causal depth; runaway runs whose anc0_share < 0.9 (reported as a defect signature if any occur in
GENOME).

    python run_csa.py -> RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "x_swap_origin"))
sys.path.insert(0, str(HERE.parent / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
CELLS = ("9cba7113df39009e-s3882-tL-a0", "e16055dd06cff594-s37315-tL-a0")
ARMS = ("GENOME", "RANDOM")
N = 120
SEED0 = 13_000_000


def key(sp, seed, armname):
    return "%s_%d_%s" % (sp[:16], seed, armname)


def jobs():
    return [(sp, SEED0 + s, a) for sp in CELLS for s in range(N) for a in ARMS]


def job(args):
    sp, seed, armname = args
    import world
    import run_ds
    import run_so
    arm = run_ds.cells()[sp]
    kw = dict(implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    if armname == "RANDOM":
        kw = dict(implant="RANDOM_MATCHED", implant_bytes=run_ds.donor_genome(), implant_len=64)
    r = run_so.tracked(world, run_ds.runner_cls(world))(dict(arm["cell"], atlas_axis="NONE"), seed,
                                                        tier=arm["tier"], **kw)
    out = r.run()
    alive = [o for o in r.orgs if o.alive]
    rec = {"specimen": sp, "seed": seed, "arm": armname, "depth": out["max_causal_replication_depth"],
           "founder_depth": r.fdepth, "p11_events": out["p11_events"],
           "anc0_share": round(sum(o.anc == 0 for o in alive) / len(alive), 4) if alive else 0.0}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / (key(sp, seed, armname) + ".json")).write_text(json.dumps(rec))
    return rec


def fisher(a, b, n1, n2):
    k0 = a + b
    return (sum(math.comb(n1, x) * math.comb(n2, k0 - x) for x in range(a, min(n1, k0) + 1))
            / math.comb(n1 + n2, k0)) if k0 else 1.0


def hit(r):
    return r["depth"] >= 20 and r["anc0_share"] >= 0.9


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [j for j in jobs() if key(*j) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    assert len(res) == len(jobs()), (len(res), len(jobs()))
    by = {a: [r for r in res if r["arm"] == a] for a in ARMS}
    c = {a: sum(hit(r) for r in by[a]) for a in ARMS}
    n = {a: len(by[a]) for a in ARMS}
    p = fisher(c["GENOME"], c["RANDOM"], n["GENOME"], n["RANDOM"])
    verdict = "CONFIRMED" if c["GENOME"] - c["RANDOM"] >= 8 and p < 0.001 else "NOT_CONFIRMED"
    sec = {a: {"per_cell": {sp[:4]: sum(hit(r) for r in by[a] if r["specimen"] == sp) for sp in CELLS},
               "world_runaways": sum(r["depth"] >= 20 for r in by[a]),
               "founder_rooted": sum(r["founder_depth"] >= 20 for r in by[a]),
               "runaway_not_descended": sum(r["depth"] >= 20 and r["anc0_share"] < 0.9 for r in by[a]),
               "max_depth": max(r["depth"] for r in by[a])} for a in ARMS}
    v = {"verdict": verdict, "endpoint_counts": c, "n_per_arm": n, "count_diff": c["GENOME"] - c["RANDOM"],
         "fisher_p": p, "secondary": sec}
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=0))
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
