"""BEL-RD-72 A3 stage 2 analysis (rules: BEL_RD72_PREREG.md s5; committed before any stage-2 run).
    python3 analyze_a3.py SCAN_RESULTS TEST_RESULTS OUT
Per replanted tape: y = 1 if a FUNC origin event occurs within 100 ticks in >= 1 of its 2 worlds. Scores (from stage 1):
  S_op  = log1p(SUB) + log1p(MOVE) + log1p(INS) + log1p(DEL)   (operator-aware, the hypothesis)
  S_sub = log1p(SUB)                                           (substitution-only ruler, the simpler baseline)
  S_nz  = number of non-zero bytes                             (a content baseline with no geometry)
AUC (ties = 1/2) per score, pooled over physics and per physics; paired bootstrap over tapes (2,000 resamples, rng 7205)."""
import json, math, random, sys
from collections import defaultdict


def auc(s, y):
    pos = [a for a, b in zip(s, y) if b]; neg = [a for a, b in zip(s, y) if not b]
    if not pos or not neg:
        return None
    w = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return w / (len(pos) * len(neg))


def scores(row):
    return {"S_op": sum(math.log1p(row[o]) for o in ("SUB", "MOVE", "INS", "DEL")), "S_sub": math.log1p(row["SUB"]),
            "S_nz": sum(1 for b in bytes.fromhex(row["tape"]) if b)}


def main(sres, tres, outp, B=2000):
    sc = {}
    for l in open(sres):
        x = json.loads(l)
        if not x.get("void"):
            for row in x["scan"]:
                sc[(x["cell"], row["tape"])] = scores(row)
    y = defaultdict(int); bg = defaultdict(lambda: [0, 0]); voids = 0
    for l in open(tres):
        r = json.loads(l)
        if r.get("void"):
            voids += 1; continue
        ev = bool((r.get("origin") or {}).get("origin_event"))
        if r["arm"] == "BACKGROUND":
            bg[r["cell"]][0] += ev; bg[r["cell"]][1] += 1
        else:
            y[(r["cell"], r["precursor"])] |= ev
    keys = sorted(k for k in y if k in sc)
    out = {"voids": voids, "tapes": len(keys), "completing": sum(y[k] for k in keys), "background": {c: v for c, v in bg.items()}}
    def block(ks):
        yy = [y[k] for k in ks]
        return {s: auc([sc[k][s] for k in ks], yy) for s in ("S_op", "S_sub", "S_nz")} | {"n": len(ks), "pos": sum(yy)}
    out["pooled"] = block(keys)
    out["per_physics"] = {c: block([k for k in keys if k[0] == c]) for c in sorted({k[0] for k in keys})}
    rng = random.Random(7205); d_sub, d_nz = [], []
    for _ in range(B):
        ks = [keys[rng.randrange(len(keys))] for _ in keys]; b = block(ks)
        if b["S_op"] is not None:
            d_sub.append(b["S_op"] - b["S_sub"]); d_nz.append(b["S_op"] - b["S_nz"])
    ci = lambda d: [sorted(d)[int(0.025 * len(d))], sorted(d)[int(0.975 * len(d)) - 1]] if d else None
    out["ci_op_minus_sub"] = ci(d_sub); out["ci_op_minus_nz"] = ci(d_nz)
    testable = out["completing"] >= 10 and out["tapes"] - out["completing"] >= 10
    out["A3-P1"] = (out["ci_op_minus_sub"][0] > 0) if testable else "NOT_TESTABLE"
    out["A3-P2"] = (out["ci_op_minus_nz"][0] > 0) if testable else "NOT_TESTABLE"
    out["A3-P3"] = (sum(1 for c, b in out["per_physics"].items() if b["S_op"] is not None and b["S_sub"] is not None and b["S_op"] > b["S_sub"]) >= 2) if testable else "NOT_TESTABLE"
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps({k: v for k, v in out.items()}, indent=1, default=str)); return out


if __name__ == "__main__":
    main(*sys.argv[1:4])
