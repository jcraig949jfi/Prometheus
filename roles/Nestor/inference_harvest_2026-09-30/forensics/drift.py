"""Q5: within-run drift from zero-register anchoring toward explicit register setup.

    python -B drift.py      -> drift.json

corpus.json carries `first_epoch` (the first 100-epoch checkpoint at which the genome was seen COMPETENT in its run).
Per DENSE run (stratum vm x cell x origin_run) with >= 6 genomes: the 3 genomes with the earliest first_epoch and the
3 with the latest (ties broken by a seeded shuffle; early and late sets must be at different epochs). For each:
run_de.competent (rescreen), fair_assay R1/R2 (STATE_FREE as run_ci.sf), and the zero-state donor trace (which of
D/E, H/L, B/C are set by the genome before the main block copy; whether DE is set by LD DE,nn).
Paired within-run comparison: late minus early share of STATE_FREE and of explicit-destination genomes; sign test.
"""
from __future__ import annotations

import collections
import json
import math
import random
import time

import fsetup as F
import core_map as M

OUT = F.pathlib.Path(__file__).resolve().parent / "drift.json"


def features(cell, g):
    row = {"competent": F.competent(cell, g)}
    if not row["competent"]:
        return row
    fr = F.fair_rates(cell, g)
    row.update({"R1": fr["R1"], "R2": fr["R2"], "state_free": all(v >= 0.5 for v in fr.values())})
    t = M.analyse_trace(g, True, 0)
    if t["main_copy"]:
        st = t["setters"]
        tape = t["tape"]
        row.update({"dest_set": any(r in st for r in (M.D, M.E)), "src_set": any(r in st for r in (M.H, M.L)),
                    "count_set": any(r in st for r in (M.B, M.C)),
                    "dest_by_copy": any(r in st and M.is_copy(st[r][2], tape[(st[r][1] + 1) % len(tape)], True) for r in (M.D, M.E)),
                    "ld_de_nn": any(r in st and st[r][2] == 0x11 for r in (M.D, M.E)),
                    "DE_at_copy": (t["main_copy"][3][M.D] << 8) | t["main_copy"][3][M.E]})
    return row


def sign_p(pos, neg):
    n = pos + neg
    if n == 0:
        return None
    k = min(pos, neg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def main():
    t0 = time.process_time()
    cor = json.load(open(M.CORPUS))
    strata = collections.defaultdict(list)
    for x in cor:
        if x["vm"] == "DENSE":
            strata[(x["cell"], x["origin_run"])].append(x)
    rng = random.Random(20260930)
    runs = []
    for k in sorted(strata):
        s = strata[k]
        if len(s) < 6:
            continue
        rng.shuffle(s)
        s.sort(key=lambda x: x["first_epoch"])
        early, late = s[:3], s[-3:]
        if early[-1]["first_epoch"] >= late[0]["first_epoch"]:
            continue
        rec = {"cell": k[0], "run": k[1], "n": len(s), "early": [], "late": []}
        for nm, grp in (("early", early), ("late", late)):
            for x in grp:
                f = features(k[0], bytes.fromhex(x["hex"]))
                f["first_epoch"] = x["first_epoch"]
                rec[nm].append(f)
        runs.append(rec)
        print(k, len(s), round(time.process_time() - t0, 1), flush=True)

    def share(rows, key):
        c = [r for r in rows if r.get("competent") and key in r]
        return sum(r[key] for r in c) / len(c) if c else None

    summ = {}
    for key in ("state_free", "dest_set", "ld_de_nn", "src_set", "count_set", "dest_by_copy"):
        d = [(share(r["late"], key), share(r["early"], key)) for r in runs]
        d = [(a, b) for a, b in d if a is not None and b is not None]
        pos = sum(a > b for a, b in d)
        neg = sum(a < b for a, b in d)
        pool_e = [x[key] for r in runs for x in r["early"] if x.get("competent") and key in x]
        pool_l = [x[key] for r in runs for x in r["late"] if x.get("competent") and key in x]
        summ[key] = {"runs": len(d), "late_gt_early": pos, "late_lt_early": neg, "tie": len(d) - pos - neg,
                     "sign_p": sign_p(pos, neg), "pooled_early": [sum(pool_e), len(pool_e)], "pooled_late": [sum(pool_l), len(pool_l)]}
    out = {"n_runs": len(runs), "summary": summ, "runs": runs, "cpu_s": round(time.process_time() - t0, 1)}
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps(summ, indent=1), out["cpu_s"])


if __name__ == "__main__":
    main()
