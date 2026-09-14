"""Round-2 Step A analysis over per_ic.jsonl: H1 (ensemble invariance at
fixed k), H2/H3 (N-collapse under m vs |2k-N|), H6 (signed asymmetry),
and the curve tables used for Step-B predictions.

Binomial arithmetic only. z between two proportions p1 (n1), p2 (n2) uses
the pooled SE; a bin needs >= 20 ICs on each side to be scored.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
R2 = REPO / "roles" / "Theophrastus" / "crucible" / "round2"
MIN_N = 20


def load(path=None) -> List[dict]:
    p = Path(path or (R2 / "per_ic.jsonl"))
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def z_two(p1, n1, p2, n2) -> float:
    if n1 == 0 or n2 == 0:
        return float("nan")
    p = (p1 * n1 + p2 * n2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0 if p1 == p2 else float("inf")
    return (p1 - p2) / se


def bin_m(m: float, width: float = 0.01) -> float:
    return round(math.floor(m / width) * width, 4)


def table(recs, key_fn) -> Dict:
    """key -> (successes, n)."""
    out = defaultdict(lambda: [0, 0])
    for r in recs:
        k = key_fn(r)
        out[k][0] += int(r["success"]); out[k][1] += 1
    return out


def compare(tA, tB) -> dict:
    """Bins present on both sides with >= MIN_N; per-bin z; summary."""
    bins = sorted(set(tA) & set(tB))
    rows, zs = [], []
    for b in bins:
        sA, nA = tA[b]; sB, nB = tB[b]
        if nA < MIN_N or nB < MIN_N:
            continue
        z = z_two(sA / nA, nA, sB / nB, nB)
        rows.append({"bin": b, "pA": round(sA / nA, 4), "nA": nA, "pB": round(sB / nB, 4), "nB": nB, "z": round(z, 2)})
        zs.append(z)
    chi = sum(z * z for z in zs if math.isfinite(z))
    return {"bins_scored": len(zs), "max_abs_z": round(max((abs(z) for z in zs), default=0.0), 2),
            "chi2": round(chi, 1), "dof": len(zs),
            "n_bins_abs_z_ge_3": sum(1 for z in zs if abs(z) >= 3), "rows": rows}


def h1_ensemble_invariance(recs) -> dict:
    """At fixed (rule, N, m-bin): P_iid vs P_unif success rate."""
    out = {}
    for rule in sorted({r["rule"] for r in recs}):
        for N in sorted({r["N"] for r in recs if r["rule"] == rule}):
            A = [r for r in recs if r["rule"] == rule and r["N"] == N and r["ensemble"] in ("P_iid", "P_iid_T")]
            B = [r for r in recs if r["rule"] == rule and r["N"] == N and r["ensemble"] == "P_unif"]
            if not A or not B:
                continue
            out["%s/N%d" % (rule, N)] = compare(table(A, lambda r: bin_m(r["m"])), table(B, lambda r: bin_m(r["m"])))
    return out


def h23_world_collapse(recs) -> dict:
    """At fixed rule: N=149 vs N=599 curves, keyed by m-bin AND by |2k-N|."""
    out = {}
    for rule in sorted({r["rule"] for r in recs}):
        A = [r for r in recs if r["rule"] == rule and r["N"] == 149]
        B = [r for r in recs if r["rule"] == rule and r["N"] == 599]
        if not A or not B:
            continue
        out[rule] = {"by_m": compare(table(A, lambda r: bin_m(r["m"])), table(B, lambda r: bin_m(r["m"]))),
                     "by_abs_count": compare(table(A, lambda r: (r["abs_count_margin"] // 4) * 4),
                                             table(B, lambda r: (r["abs_count_margin"] // 4) * 4))}
    return out


def h6_signed_asymmetry(recs) -> dict:
    out = {}
    for rule in sorted({r["rule"] for r in recs}):
        for N in sorted({r["N"] for r in recs if r["rule"] == rule}):
            S = [r for r in recs if r["rule"] == rule and r["N"] == N]
            lo = [r for r in S if r["signed_m"] < 0]
            hi = [r for r in S if r["signed_m"] > 0]
            out["%s/N%d" % (rule, N)] = compare(table(lo, lambda r: bin_m(r["m"])), table(hi, lambda r: bin_m(r["m"])))
    return out


def curve(recs, rule: str, N: int, width: float = 0.01) -> Dict[float, Tuple[int, int]]:
    S = [r for r in recs if r["rule"] == rule and r["N"] == N]
    t = table(S, lambda r: bin_m(r["m"], width))
    return {b: (v[0], v[1]) for b, v in sorted(t.items())}


def predict(curve_t: Dict[float, Tuple[int, int]], ms: List[float], width: float = 0.01) -> dict:
    """Predict the accuracy of a cell whose realised margins are `ms` from a
    curve table; bins with no data fall to the nearest scored bin (recorded).
    Returns mean prediction and its SE (sum of per-bin binomial variances of
    the curve estimate, weighted)."""
    scored = {b: v for b, v in curve_t.items() if v[1] >= MIN_N}
    if not scored:
        return {"pred": float("nan"), "se": float("nan"), "fallbacks": len(ms)}
    keys = sorted(scored)
    tot, var, fb = 0.0, 0.0, 0
    for m in ms:
        b = bin_m(m, width)
        if b not in scored:
            b = min(keys, key=lambda x: abs(x - b)); fb += 1
        s, n = scored[b]
        p = s / n
        tot += p
        var += p * (1 - p) / n
    n_ms = len(ms)
    return {"pred": tot / n_ms, "se": math.sqrt(var) / n_ms, "fallbacks": fb, "n": n_ms}


def main():
    recs = load()
    rep = {"n_records": len(recs),
           "H1_ensemble_invariance_at_fixed_m": h1_ensemble_invariance(recs),
           "H2H3_world_collapse": h23_world_collapse(recs),
           "H6_signed_asymmetry": h6_signed_asymmetry(recs)}
    (R2 / "stepA_tests.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    def short(d):
        return {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in d.items()}
    print("H1 (P_iid vs P_unif at fixed m):"); print(json.dumps(short(rep["H1_ensemble_invariance_at_fixed_m"]), indent=1))
    print("H2/H3 (N149 vs N599 at fixed m | fixed |2k-N|):")
    for rule, v in rep["H2H3_world_collapse"].items():
        print(" ", rule, "by_m:", {k: x for k, x in v["by_m"].items() if k != "rows"},
              "| by_abs_count:", {k: x for k, x in v["by_abs_count"].items() if k != "rows"})
    print("H6 (signed asymmetry d<1/2 vs d>1/2 at fixed |m|):"); print(json.dumps(short(rep["H6_signed_asymmetry"]), indent=1))


if __name__ == "__main__":
    main()
