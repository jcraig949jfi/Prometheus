"""BEL-RD-72 C2R analysis (prereg s9).   python3 analyze_c2r.py C2R_RESULTS C23_RESULTS OUT.json
Per C2 world (keyed by `pair`, the E1b world id): re-acquisition delay d(arm) = first census tick > at with a FUNC LO-or-BOTH
tape, minus at (20-tick census); no re-acquisition by the end -> censored (+inf). Arms: REMOVE (re-run), RESET, NEAR.
Validity: each C2R REMOVE census at a tick present in the matching C2 REMOVE run (100-tick grain) has the same alive count
and FUNC halves counts; a world failing it is reported and excluded from both tests.
C2R-P1  REMOVE faster than RESET: one-sided sign test over worlds where d differs (ties and both-censored dropped), p < 0.05
C2R-P2  REMOVE faster than NEAR: same test
NOT_TESTABLE with < 5 decided worlds. Reported: re-acquisition counts per arm, removed counts, median delays."""
import json, math, sys
INF = float("inf")


def sign_p(k, n):
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def delay(r):
    at = r["intervention"]["tick"] if r.get("intervention") else None
    for c in r["census"]:
        hf = c.get("halves_func") or {}
        if c["tick"] > at and hf.get("LO", 0) + hf.get("BOTH", 0) > 0:
            return c["tick"] - at
    return INF


def test(D, a, b):
    k = n = 0
    for w, d in D.items():
        if a not in d or b not in d or d[a] == d[b]:
            continue
        n += 1; k += d[a] < d[b]
    if n < 5:
        return {"faster": k, "decided": n, "p": None, "holds": "NOT_TESTABLE"}
    p = sign_p(k, n)
    return {"faster": k, "decided": n, "p": round(p, 6), "holds": p < 0.05}


def analyze(c2r, c23):
    D = {}; cells = {}; bad = []
    ref = {r["pair"]: {c["tick"]: (c.get("alive"), c.get("halves_func")) for c in r["census"]}
           for r in c23 if r.get("lane") == "C2" and r.get("arm") == "REMOVE"}
    for r in c2r:
        if r.get("lane") == "C2R" and r.get("arm") == "REMOVE" and r["pair"] in ref:
            cen = {c["tick"]: (c.get("alive"), c.get("halves_func")) for c in r["census"]}
            if any(cen.get(t) != v for t, v in ref[r["pair"]].items()):
                bad.append(r["pair"])
    for r in c2r:
        if r.get("void") or r.get("lane") != "C2R" or r["pair"] in bad:
            continue
        d = delay(r); D.setdefault(r["pair"], {})[r["arm"]] = d
        c = cells.setdefault(r["arm"], {"n": 0, "reacquired": 0, "delays": [], "affected": []})
        c["n"] += 1; c["reacquired"] += d < INF; c["affected"].append(r["intervention"]["affected"])
        if d < INF:
            c["delays"].append(d)
    med = lambda v: sorted(v)[len(v) // 2] if v else None
    out = {"cells": {a: {"n": c["n"], "reacquired": c["reacquired"], "median_delay": med(c["delays"]),
                         "median_affected": med(c["affected"])} for a, c in cells.items()},
           "replay_invalid": sorted(bad), "C2R-P1": test(D, "REMOVE", "RESET"), "C2R-P2": test(D, "REMOVE", "NEAR"),
           "worlds": {w: {a: (None if v == INF else v) for a, v in d.items()} for w, d in sorted(D.items())}}
    return out


if __name__ == "__main__":
    ld = lambda p: [json.loads(l) for l in open(p)]
    o = analyze(ld(sys.argv[1]), ld(sys.argv[2])); json.dump(o, open(sys.argv[3], "w"), indent=1)
    print(json.dumps({k: v for k, v in o.items() if k != "worlds"}, indent=1))
