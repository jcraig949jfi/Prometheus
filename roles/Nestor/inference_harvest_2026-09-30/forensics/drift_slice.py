"""Q5 supplement: world-register dependence of the copy operands (slice.py logic) for the drift.py genomes.

    python -B drift_slice.py      -> drift_slice.json
For each competent early/late genome of drift.json: the passing side (core_map.pass_side), the zero-state trace on
that side, the backward slice of the main copy's B,C,D,E,H,L; WORLD_EL = the copy's E or L (the only address bytes
that matter modulo the 128-byte tape) still depends on an entry register at trace start.
"""
from __future__ import annotations

import json
import math

import core_map as M
import slice as SL

HERE = M.OUT.parent


def world_regs(g):
    cnt = M.pass_side(g, True)
    side = 0 if cnt[0] >= cnt[1] else 1
    t = M.analyse_trace(g, True, side)
    if not t["main_copy"]:
        return side, None
    _, need = SL.backward(t["trace"], t["tape"], t["main_copy"][0], set("BCDEHL"), True, len(t["tape"]))
    return side, sorted(x for x in need if isinstance(x, str))


def main():
    d = json.load(open(HERE / "drift.json"))
    # re-derive the genome hexes exactly as drift.py selected them
    import collections
    import random
    cor = json.load(open(M.CORPUS))
    strata = collections.defaultdict(list)
    for x in cor:
        if x["vm"] == "DENSE":
            strata[(x["cell"], x["origin_run"])].append(x)
    rng = random.Random(20260930)
    sel = {}
    for k in sorted(strata):
        s = strata[k]
        if len(s) < 6:
            continue
        rng.shuffle(s)
        s.sort(key=lambda x: x["first_epoch"])
        early, late = s[:3], s[-3:]
        if early[-1]["first_epoch"] >= late[0]["first_epoch"]:
            continue
        sel[k] = (early, late)
    out = []
    for r in d["runs"]:
        early, late = sel[(r["cell"], r["run"])]
        row = {"run": r["run"], "cell": r["cell"]}
        for h, grp, meas in (("early", early, r["early"]), ("late", late, r["late"])):
            row[h] = []
            for x, m in zip(grp, meas):
                assert x["first_epoch"] == m["first_epoch"]
                if not m.get("competent"):
                    continue
                side, w = world_regs(bytes.fromhex(x["hex"]))
                row[h].append({"state_free": m["state_free"], "side": side, "world_regs": w,
                               "world_EL": None if w is None else bool(set(w) & {"E", "L"})})
        out.append(row)

    def share(rows, key):
        v = [x[key] for x in rows if x.get(key) is not None]
        return sum(v) / len(v) if v else None
    summ = {}
    for key in ("world_EL",):
        pairs = [(share(r["late"], key), share(r["early"], key)) for r in out]
        pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
        pos, neg = sum(a > b for a, b in pairs), sum(a < b for a, b in pairs)
        n = pos + neg
        p = min(1.0, 2 * sum(math.comb(n, i) for i in range(min(pos, neg) + 1)) / 2 ** n) if n else None
        summ[key] = {"runs": len(pairs), "late_gt_early": pos, "late_lt_early": neg, "sign_p": p,
                     "pooled_early": [sum(x[key] for r in out for x in r["early"] if x[key] is not None),
                                      sum(x[key] is not None for r in out for x in r["early"])],
                     "pooled_late": [sum(x[key] for r in out for x in r["late"] if x[key] is not None),
                                     sum(x[key] is not None for r in out for x in r["late"])]}
    side1 = {h: [sum(x["side"] == 1 for r in out for x in r[h]), sum(1 for r in out for x in r[h])] for h in ("early", "late")}
    (HERE / "drift_slice.json").write_text(json.dumps({"summary": summ, "side1": side1, "runs": out}, indent=1))
    print(json.dumps(summ), side1)


if __name__ == "__main__":
    main()
