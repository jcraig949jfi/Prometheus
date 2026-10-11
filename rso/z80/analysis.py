"""C-017-T030 analysis: the preregistered decision rule (PREREGISTRATION.md s5). Unit = the RUN; every number is an integer count.

Q1  per ground-truth class c in ENDO / EXT / ENV / INS, over the unforged runs of c's arms that have >= 1 functional organism:
    wrong_c <= w_max(n_c), the largest w with P(X <= w | Binomial(n_c, 1/5)) <= 1/100: the exact one-sided test that the class's
    misattribution rate is below 1 in 5. MIXED, OTHER, REFUSED and any other class count as wrong. w_max undefined (n_c < 21)
    -> UNDERPOWERED. The four tests are an intersection-union test: no multiplicity correction.
Q2  origin (INSERTED / ARISEN), same rule, pooled over every unforged functional run whose arm declares an origin.
Q3  forgeries, zero tolerance: LABELS and PLANT leave class and origin equal to their source run's; PHYS, TAPE and GEN are refused
    with REPLAY_MISMATCH. Each kind must be present.
Q4  the label reader (b1), the bytes-only detector (b2) and the recipe reader (b4, v1.1.0) scored by Q1 must each FAIL Q1; a
    baseline that passes makes the arm set uninformative about attribution. b1 / b2 have no ENV output; b4 does (PREREG s5).
Verdict: NOT_QUALIFIED if Q1, Q2 or Q3 fails; else UNDERPOWERED if a Q1 class or Q2 is unpowered; else UNINFORMATIVE if Q4 fails;
else ATTRIBUTION_QUALIFIED.

    python -m rso.z80.analysis ROWS.jsonl.gz [...]       prints the verdict JSON
"""
import gzip
import json
import sys
from fractions import Fraction

from rso.witness.ruler import tail_le

CLASSES = ("ENDO", "EXT", "ENV", "INS")
BOUND, ALPHA = Fraction(1, 5), Fraction(1, 100)
INVARIANT, REFUSE = ("LABELS", "PLANT"), ("PHYS", "TAPE", "GEN")
BASELINES = ("b1", "b2", "b4")                                       # v1.1.0: b4, the recipe reader (assay.b4)


def w_max(n, bound=BOUND, alpha=ALPHA):
    if n <= 0 or tail_le(n, 0, bound) > alpha:
        return None
    w = 0
    while w < n and tail_le(n, w + 1, bound) <= alpha:
        w += 1
    return w


def _test(n, wrong):
    w = w_max(n)
    return {"n": n, "wrong": wrong, "w_max": w, "pass": w is not None and wrong <= w, "powered": w is not None}


def q1(rows, key="cls"):
    out = {}
    for c in CLASSES:
        R = [r for r in rows if not r["forgery"] and r["gt"] == c and r[key] != "NONE"]
        out[c] = _test(len(R), sum(r[key] != c for r in R))
    return out


def verdict(rows):
    failed, unpowered = [], []
    Q1 = q1(rows)
    for c, t in Q1.items():
        if not t["powered"]:
            unpowered.append("Q1:" + c)
        elif not t["pass"]:
            failed.append("Q1:" + c)
    R2 = [r for r in rows if not r["forgery"] and r["origin_gt"] and r["cls"] != "NONE"]
    Q2 = _test(len(R2), sum(r["origin"] != r["origin_gt"] for r in R2))
    if not Q2["powered"]:
        unpowered.append("Q2")
    elif not Q2["pass"]:
        failed.append("Q2")
    Q3 = {}
    for kind in INVARIANT + REFUSE:
        R = [r for r in rows if r["forgery"] == kind]
        if kind in INVARIANT:
            bad = sum(r["cls"] != r["source_cls"] or r["origin"] != r["source_origin"] or r["refused"] != "" for r in R)
        else:
            bad = sum(r["cls"] != "REFUSED" or r["refused"] != "REPLAY_MISMATCH" for r in R)
        Q3[kind] = {"n": len(R), "bad": bad}
        if not R or bad:
            failed.append("Q3:" + kind)
    Q4 = {b: q1(rows, b) for b in BASELINES}
    baseline_passes = [b for b, q in Q4.items() if all(t["pass"] for t in q.values())]
    if failed:
        v = "NOT_QUALIFIED"
    elif unpowered:
        v = "UNDERPOWERED"
    elif baseline_passes:
        v = "UNINFORMATIVE"
    else:
        v = "ATTRIBUTION_QUALIFIED"
    return {"verdict": v, "failed": failed, "unpowered": unpowered, "baselines_passing_q1": baseline_passes,
            "q1": Q1, "q2": Q2, "q3": Q3, "q4": Q4, "confusion": confusion(rows)}


def confusion(rows):
    m = {}
    for r in rows:
        k = r["arm"] + ("/" + r["forgery"] if r["forgery"] else "")
        m.setdefault(k, {}).setdefault(r["cls"], 0)
        m[k][r["cls"]] += 1
    return m


def load(paths):
    rows = []
    for p in paths:
        with gzip.open(p, "rt", encoding="utf-8") as f:
            rows += [json.loads(line) for line in f if line.strip()]
    return rows


if __name__ == "__main__":
    print(json.dumps(verdict(load(sys.argv[1:])), indent=1, sort_keys=True, default=str))
