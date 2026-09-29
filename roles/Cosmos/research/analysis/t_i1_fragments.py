"""T-I1 fragment test: are the atoms of mined C0-C2 laws re-expressions of the certificate's own economics?

Declared BEFORE running (committed first; exploratory Z1 analysis on already-spent rows, no holdout touched).

Probe battery: the committed sealed-universe rows of C0/C2 (720 worlds: D and E with v3 coordinates, F with
v4 coordinates; roles/Cosmos/campaigns/{c0b/run_21fd1b2cc/G5_holdout.json, c0e/C0E.json, c2/F_adjudication.json}).
Using rows from different coordinate maps as one battery is a disclosed simplification: the battery only
fixes WHICH worlds each atom is evaluated on (Aphrodite's quotient idea: identity = value vector over a
frozen probe set).

Definition-rung atoms (zero-parameter, from the certificate; c0e/PREREG.md post-hoc section):
  R1  G exp(-N) - C >= 0.10        R2  C K / 2 >= 0.10        R3  Q < 1
For every mined atom a (expr, direction, threshold) the statistic is
  agree(a) = max over r in {R1,R2,R3} of max(mean(a == r), mean(a != r)).
Null: 2,000 random expressions of the SAME grammar size (capped at 5) over terminals {C,N,K,G,Q}, each thresholded at the
quantile that gives the SAME positive rate as a on the battery (marginal-matched), and scored the same way.
Decision rule (per atom): REEXPRESSES_RUNG if agree(a) > the null's 99th percentile AND agree(a) >= 0.90;
otherwise NOT_RUNG. Seed 20260929. The T-I1 recurrence analysis is dead for an atom that re-expresses the
rung: its recurrence carries no information beyond the certificate.

python roles/Cosmos/research/analysis/t_i1_fragments.py  ->  prints a table and writes t_i1_fragments.json
"""
import json
import random
from pathlib import Path

import numpy as np

from prometheus.cosmos.miner import enumerate_exprs, evaluate_expr, size

ROOT = Path(__file__).resolve().parents[4]
CAMP = ROOT / "roles" / "Cosmos" / "campaigns"
TERMS = ("C", "N", "K", "G", "Q")
SEED, NNULL = 20260929, 2000


def battery():
    sets = [json.load(open(CAMP / "c0b" / "run_21fd1b2cc" / "G5_holdout.json"))["rows"],
            json.load(open(CAMP / "c0e" / "C0E.json"))["G5E"]["rows"],
            json.load(open(CAMP / "c2" / "F_adjudication.json"))["B_c1_v4"]["rows"]]
    rows = [r["coords"] for s in sets for r in s]
    return {k: np.array([r[k] for r in rows], float) for k in TERMS}


V = lambda n: ("var", n)
def sub(a, b): return ("sub", a, b)
def mul(a, b): return ("mul", a, b)
def add(a, b): return ("add", a, b)
def div(a, b): return ("div", a, b)
def dec(a): return ("dec", a)
def log(a): return ("log", a)


C, N, K, G, Q = V("C"), V("N"), V("K"), V("G"), V("Q")
# (graveyard/result id, expression, direction '<=' or '>=', threshold) -- transcribed from GRAVEYARD.md / RESULTS.md
ATOMS = [
    ("G-0001a", mul(sub(N, K), C), "<=", -0.1584),
    ("G-0001b", sub(C, dec(mul(C, N))), "<=", -0.136),
    ("G-0002a", mul(add(C, K), C), ">=", 0.1647),
    ("G-0002b", sub(C, mul(G, dec(N))), "<=", -0.06142),
    ("G-0003a", mul(C, K), ">=", 0.1608),
    ("G-0003b", sub(C, mul(G, dec(N))), "<=", -0.08702),
    ("G-0004a", sub(Q, mul(C, K)), "<=", 0.872),
    ("G-0004b", div(K, add(N, log(C))), "<=", -0.6075),
    ("G-0004c", add(mul(C, log(C)), Q), "<=", 0.9112),
    ("G-0005a", sub(C, mul(G, dec(N))), "<=", -0.1026),
    ("G-0005b", add(mul(C, K), dec(Q)), ">=", 0.5122),
    ("R-0001a", sub(C, add(G, dec(N))), "<=", -1.055),
    ("R-0001b", mul(sub(C, log(Q)), K), ">=", 0.179),
    ("R-0002a", log(sub(Q, mul(C, K))), "<=", -0.158),
    ("R-0002b", sub(C, mul(G, dec(N))), "<=", -0.102),
]


def truth(e, d, t, X):
    v = evaluate_expr(e, X)
    v = np.where(np.isfinite(v), v, np.nan)
    out = (v <= t) if d == "<=" else (v >= t)
    return np.where(np.isnan(v), False, out)


def rung(X):
    return [(X["G"] * np.exp(-X["N"]) - X["C"]) >= 0.10, (X["C"] * X["K"] / 2) >= 0.10, X["Q"] < 1]


def agree(a, R):
    return max(max(np.mean(a == r), np.mean(a != r)) for r in R)


def main():
    X = battery()
    R = rung(X)
    pool = {}
    for e in enumerate_exprs(TERMS, 5):
        pool.setdefault(size(e), []).append(e)
    rng = random.Random(SEED)
    out = []
    for aid, e, d, t in ATOMS:
        a = truth(e, d, t, X)
        rate = float(np.mean(a))
        s = min(size(e), 5)
        null = []
        for _ in range(NNULL):
            ev = evaluate_expr(rng.choice(pool[s]), X)
            ev = np.where(np.isfinite(ev), ev, np.nan)
            if np.all(np.isnan(ev)) or rate in (0.0, 1.0):
                continue
            thr = np.nanquantile(ev, rate)
            null.append(agree(np.where(np.isnan(ev), False, ev <= thr), R))
        null = np.array(null)
        obs = agree(a, R)
        q99 = float(np.quantile(null, 0.99))
        verdict = "REEXPRESSES_RUNG" if (obs > q99 and obs >= 0.90) else "NOT_RUNG"
        out.append({"atom": aid, "size": size(e), "pos_rate": round(rate, 3), "agree": round(obs, 3),
                    "null_q50": round(float(np.median(null)), 3), "null_q99": round(q99, 3),
                    "p": round(float(np.mean(null >= obs)), 4), "verdict": verdict})
    for r in out:
        print("{atom:8s} size {size}  pos {pos_rate:.3f}  agree {agree:.3f}  null q50 {null_q50:.3f} "
              "q99 {null_q99:.3f}  p {p:.4f}  {verdict}".format(**r))
    json.dump(out, open(Path(__file__).with_suffix(".json"), "w"), indent=1)


if __name__ == "__main__":
    main()
