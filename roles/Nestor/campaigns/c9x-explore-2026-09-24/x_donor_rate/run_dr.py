"""X-DONOR-RATE (EXPLORE, MEASUREMENT / localization; child of C-ATOMIC). Declared before running.

C-ATOMIC: removing tape-write erosion confirms runaway heredity for 7ae3 (46/80 vs 1/80) but not
across the other 15 H2 panel specimens (1/120 vs 0/120); there, runs rarely make even one causal
copy. Hypothesis: a donor's INTRINSIC copy competence - the probability that one interaction
yields a P-11 causal copy - is the first barrier, and 7ae3 is exceptional on it.

Measurement (no world runs): for each of the 16 panel donors (C9 arm-B implant genome, padded as
the world pads it, the specimen's frozen cell with atlas_axis NONE), 200 P-11 assays per tape side
from a fresh state (as a freshly placed implant), each with its own seed; the partner half is
randomized by the assay itself. Readout per specimen: pass rate (either side counts per seed).
Outcome to compare against (already frozen data, C-ATOMIC ATOMIC arm): share of runs with >= 1
P-11 event, and depth >= 5.
Classification: SIGNAL if 7ae3 has the highest pass rate AND Spearman(pass rate, ATOMIC any-copy
share) over the 16 specimens >= 0.6; CLEAN_NULL if Spearman < 0.2 or 7ae3 is not in the top 3;
WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
CAT = HERE.parent / "c_atomic" / "results"
sys.path.insert(0, str(C9))
K = 200


def job(sp):
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == sp)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])
    r = world.Runner(dict(arm["cell"], atlas_axis="NONE"), 1, tier=arm["tier"],
                     implant="ACTUAL_GENOME", implant_bytes=genome)
    g = r._pad(genome)
    n, tl = r.L, world._pow2(2 * r.L)
    fresh = (None, 0, 0)
    passes = {0: 0, 1: 0}
    either = 0
    for k in range(K):
        hit = False
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            kw = dict(n=n, tape_len=tl, ga=ga, gb=gb, st_a=fresh, st_b=fresh, budget=r.t["slice"],
                      ops_mask=r._ops_mask(), cmr=r.copy_mut, victim_side=1 - side,
                      seed=("X-DONOR-RATE", sp, k, side))
            ok = world.p11.assay(world.z8, **kw)["pass"]
            passes[side] += ok
            hit = hit or ok
        either += hit
    return {"specimen": sp, "rate": either / K, "side0": passes[0] / K, "side1": passes[1] / K}


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for m in range(i, j + 1):
                r[o[m]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def main():
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    sps = sorted({b["specimen"] for b in man["bundles"] if b["hypothesis_id"] == "H2"})
    with mp.Pool(10, maxtasksperchild=1) as pool:
        rates = pool.map(job, sps)
    cat = [json.loads(p.read_text()) for p in CAT.glob("*.json")]
    for r in rates:
        rows = [c for c in cat if c["specimen"] == r["specimen"] and c["arm"] == "ATOMIC"]
        r["atomic_any_copy"] = round(sum(c["p11_events"] > 0 for c in rows) / len(rows), 4)
        r["atomic_depth_ge5"] = round(sum(c["depth"] >= 5 for c in rows) / len(rows), 4)
    rates.sort(key=lambda r: -r["rate"])
    rho = spearman([r["rate"] for r in rates], [r["atomic_any_copy"] for r in rates])
    top = [r["specimen"][:4] for r in rates[:3]]
    cls = ("SIGNAL" if top[0] == "7ae3" and rho >= 0.6 else
           "CLEAN_NULL" if rho < 0.2 or "7ae3" not in top else "WEAK_SIGNAL")
    summ = {"classification": cls, "spearman_rate_vs_atomic_any_copy": round(rho, 3), "top3": top,
            "per_specimen": rates}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
