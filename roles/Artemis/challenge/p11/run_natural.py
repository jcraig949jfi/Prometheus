"""PREREG_P11.md s4.2: fresh-state re-application to the 57 P-11 survivors of S1-C. A NEW forensic assay: nothing in
P11_REASSAY.* is rescored. -> results/NATURAL_REAPPLY.jsonl, results/NATURAL_SUMMARY.json
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import random
import time
from collections import Counter

from common import (OUT, REASSAY, Z8SUB, FRESH, REP_LEN, MUT_RATE, SLICE, pow2, mask_for, shabytes, fid,
                    file_hashes, p11)
import specimens as S
import harness as Hn
import certs as CE

K_NAT = 50


class LogTape(bytearray):
    def __init__(self, *a):
        super().__init__(*a)
        self.log = []

    def __setitem__(self, i, v):
        if isinstance(i, int):
            self.log.append((i, v))
        super().__setitem__(i, v)


def audit(G, side, n, TL, budget, mask):
    tape = LogTape(TL)
    vb = shabytes("AUDIT", G.hex(), n=n)
    ga, gb = (G, vb) if side == 0 else (vb, G)
    tape[0:n] = ga
    tape[n:2 * n] = gb
    tape.log = []
    out = {}
    for who, start in ((0, 0), (1, n)):
        ctx = Z8SUB.Ctx(tape, start, n, policy=Z8SUB.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=who)
        ctx.regs, ctx.fz, ctx.fc = None, 0, 0
        mark = len(tape.log)
        Z8SUB.run(ctx, start, budget, ops_enabled=mask)
        if who == side:
            w = tape.log[mark:]
            v0 = n if side == 0 else 0
            inv = [(a, v) for a, v in w if v0 <= a < v0 + n]
            cells = len({a for a, _ in inv})
            out = {"donor_steps": ctx.ops, "donor_writes": len(w), "victim_writes": len(inv),
                   "victim_cells_written": cells, "distinct_values_written": len({v for _, v in inv}),
                   "top_values": [["%02x" % v, c] for v, c in Counter(v for _, v in inv).most_common(3)],
                   "steps_per_victim_cell": round(ctx.ops / cells, 2) if cells else None}
    return out


def job(row):
    t0 = time.time()
    cell, tier, rid = row["cell"], row["tier"], row["run_id"]
    G = bytes.fromhex(row["first_p11_event"]["donor_genome"])
    n = REP_LEN[cell["representation"]]
    TL, budget, mask, cmr = pow2(2 * n), SLICE[tier], mask_for(cell), MUT_RATE[cell["mutation_rate"]]
    import world
    r = world.Runner(dict(cell), 1, tier=tier)
    xcheck = {"L": r.L == n, "mask": r._ops_mask() == mask, "slice": r.t["slice"] == budget,
              "cmr": r.copy_mut == cmr, "genome_len": len(G) == n}
    rec = {"run_id": rid, "copy_primitive": cell["copy_primitive"], "representation": cell["representation"],
           "self_location": cell["self_location"], "tier": tier, "n": n, "budget": budget, "mask": mask, "cmr": cmr,
           "max_p11_depth_S1C": row["max_p11_depth"], "genome": G.hex(), "param_crosscheck": xcheck,
           "has_ED_B0_B8": (b"\xed\xb0" in G) or (b"\xed\xb8" in G), "DOM_diag": CE.dom(G)}
    sides = {}
    for side in (0, 1):
        passes, fids = 0, []
        for k in range(K_NAT):
            ga, gb = (G, bytes(n)) if side == 0 else (bytes(n), G)
            res = p11.assay(Z8SUB, n=n, tape_len=TL, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH, budget=budget,
                            ops_mask=mask, cmr=cmr, victim_side=1 - side, seed=("P11-NAT", rid, k, side))
            passes += res["pass"]
            fids += [d["fid_final"] for d in res["draws"]]
        sd = {"fresh_p11_rate": round(passes / K_NAT, 4), "recertified": passes / K_NAT >= 0.5,
              "mean_fid_final": round(sum(fids) / len(fids), 4)}
        if sd["recertified"]:
            sp = S.Spec(rid, "natural", "pair", "z8", n, budget, mask, G, None, "unknown", "NAT", side=side)
            rows, _ = CE.cvt(lambda g_, gg, kk: Hn.step(Z8SUB, sp, g_, gg, kk), G, rid, False)
            sd.update(CE.score(rows, n))
            # FERT: children of seed k = 0 (tag "P11-NAT") re-assayed as donors
            ga, gb = (G, bytes(n)) if side == 0 else (bytes(n), G)
            seed0 = ("P11-NAT", rid, 0, side)
            kids = []
            for k in range(3):
                vr = random.Random(p11.event_seed(seed0, "victim", k))
                vb = bytes(vr.randrange(256) for _ in range(n))
                tape, _, _, _ = p11.interact(Z8SUB, n=n, tape_len=TL, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                             budget=budget, ops_mask=mask, cmr=cmr,
                                             rng=random.Random(p11.event_seed(seed0, "copy", k)),
                                             victim_side=1 - side, victim_bytes=vb)
                v0 = n if side == 0 else 0
                kids.append(bytes(tape[v0:v0 + n]))
            kp = []
            for k, ch in enumerate(kids):
                cga, cgb = (ch, bytes(n)) if side == 0 else (bytes(n), ch)
                kp.append(bool(p11.assay(Z8SUB, n=n, tape_len=TL, ga=cga, gb=cgb, st_a=FRESH, st_b=FRESH,
                                         budget=budget, ops_mask=mask, cmr=cmr, victim_side=1 - side,
                                         seed=("FERT-NAT", rid, k, side))["pass"]))
            sd["FERT"] = {"accept": sum(kp) >= 2, "children_pass": kp}
            sd["SHUF_diag"] = CE.shuf(G, sd["mean_fid_final"], rid)
            sd["audit"] = audit(G, side, n, TL, budget, mask)
        sides[side] = sd
    rec["sides"] = sides
    rec["recertified"] = any(s["recertified"] for s in sides.values())
    best = [s for s in sides.values() if s["recertified"]]
    for c in ("CVT1", "CVT2", "CVTR"):
        rec[c + "_TB"] = max((s[c]["TB"] for s in best), default=None)
    rec["LOCAL"] = any(s["LOCAL"]["accept"] for s in best) if best else None
    rec["FERT"] = any(s["FERT"]["accept"] for s in best) if best else None
    rec["seconds"] = round(time.time() - t0, 2)
    return rec


def cp_ci(k, n):
    """Exact Clopper-Pearson 95% interval by bisection on the binomial tail (stdlib)."""
    if n == 0:
        return None

    def cdf(x, p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))

    def bis(f, lo=0.0, hi=1.0):
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else bis(lambda p: 1 - cdf(k - 1, p) < 0.025)
    hi = 1.0 if k == n else bis(lambda p: cdf(k, p) > 0.025)
    return [round(lo, 4), round(hi, 4)]


def main():
    OUT.mkdir(exist_ok=True)
    rows = [json.loads(l) for l in open(REASSAY)]
    surv = [r for r in rows if r.get("n_p11_events", 0) > 0]
    t0 = time.time()
    with mp.Pool(2, maxtasksperchild=4) as pool:
        recs = pool.map(job, surv, chunksize=1)
    with open(OUT / "NATURAL_REAPPLY.jsonl", "w", encoding="ascii") as fh:
        for r in recs:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    summ = {"note": "Fresh-state re-assay (registers/victims of the original events are not committed). NEW file; "
                    "S1-C P11_REASSAY.* are not rescored.",
            "n_donors": len(recs), "param_crosscheck_all_ok": all(all(r["param_crosscheck"].values()) for r in recs),
            "wall_seconds": round(time.time() - t0, 1), "files": file_hashes()}
    strata = {}
    for r in recs:
        hom = r["DOM_diag"]["dominant_share"] >= 0.9
        key = "%s|%s" % (r["copy_primitive"], "dom>=0.9" if hom else "dom<0.9")
        s = strata.setdefault(key, Counter())
        s["donors"] += 1
        s["recertified"] += r["recertified"]
        if r["recertified"]:
            for c in ("CVT1", "CVT2", "CVTR"):
                s[c + "_TB>=1"] += r[c + "_TB"] >= 1
            s["FERT"] += bool(r["FERT"])
            s["LOCAL"] += bool(r["LOCAL"])
    summ["strata"] = {k: dict(v) for k, v in sorted(strata.items())}
    rec_ = [r for r in recs if r["recertified"]]
    for c in ("CVT2", "CVTR"):
        z = sum(1 for r in rec_ if r[c + "_TB"] < 1)
        summ["N3_zero_bit_share_" + c] = {"k": z, "n": len(rec_), "share": round(z / len(rec_), 4) if rec_ else None,
                                          "CI95": cp_ci(z, len(rec_))}
    byte_ = [r for r in rec_ if r["copy_primitive"] == "BYTEWISE"]
    block = [r for r in rec_ if r["copy_primitive"] == "BLOCK"]
    summ["BYTEWISE_recertified"] = len(byte_)
    summ["BLOCK_recertified"] = len(block)
    summ["depth2_runs"] = {r["run_id"]: {"recertified": r["recertified"], "CVT2_TB": r["CVT2_TB"],
                                         "CVTR_TB": r["CVTR_TB"]} for r in recs if r["max_p11_depth_S1C"] >= 2}
    (OUT / "NATURAL_SUMMARY.json").write_text(json.dumps(summ, indent=1, sort_keys=True))
    print(json.dumps(summ, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
