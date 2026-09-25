"""X-DOSE-CURVE (EXPLORE, DOSE; child of C-CRITICAL-MASS). Declared before running.

C-CRITICAL-MASS CONFIRMED that 4 founders beat 1 (depth >= 5: 41/80 vs 5/80). Post hoc, the
k=4 rate also exceeds the INDEPENDENT-FOUNDERS prediction 1-(1-p1)^k (pooled: 73/144 observed vs
45 expected; runaways 24 vs 8). That comparison plugs in a noisy p1. Question: is establishment
SUPERADDITIVE (founders help each other: a true critical mass), or is each founder an
independent lottery ticket?

Single coordinate (DOSE): founders k in {1, 2, 4, 8}; implanted 7ae3 donor genome, splice OFF,
C9 arm-B physics, tier M. 64 fresh seeds 9_997_000 + s, shared across k. One job per process.
Endpoint: P-11 depth >= 5 (secondary: runaway, depth >= 20).
Test: fit the 1-parameter independence model s(k) = 1-(1-p)^k by maximum likelihood to all four
arms; likelihood-ratio test against the saturated 4-rate model (chi-square, df = 3).
Classification: SIGNAL (superadditive) if LRT p < 0.01 AND observed > fitted at both k=4 and k=8;
CLEAN_NULL (independent founders) if LRT p > 0.2; WEAK_SIGNAL otherwise.
Declared prediction: SIGNAL.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
KS = (1, 2, 4, 8)
N = 64


def job(args):
    s, k = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])

    class K(world.Runner):
        _extra = k - 1

        def _seed_genome(self):
            if self._extra > 0:
                self._extra -= 1
                return self._pad(genome)
            return super()._seed_genome()

    out = K(dict(arm["cell"], atlas_axis="NONE"), 9_997_000 + s, tier=arm["tier"],
            implant="ACTUAL_GENOME", implant_bytes=genome).run()
    r = {"s": s, "k": k, "depth": out["max_causal_replication_depth"], "p11_events": out["p11_events"]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d_k%d.json" % (s, k))).write_text(json.dumps(r))
    return r


def loglik(x, n, q):
    q = min(max(q, 1e-12), 1 - 1e-12)
    return x * math.log(q) + (n - x) * math.log(1 - q)


def fit_independence(xs, n):
    best = (-1e300, None)
    for i in range(1, 100000):
        p = i / 100000
        ll = sum(loglik(xs[k], n, 1 - (1 - p) ** k) for k in KS)
        if ll > best[0]:
            best = (ll, p)
    return best


def chi2_sf_df3(x):
    # survival function of chi-square with 3 degrees of freedom
    return math.erfc(math.sqrt(x / 2)) + math.sqrt(2 * x / math.pi) * math.exp(-x / 2)


def analyse(res, thr):
    xs = {k: sum(r["depth"] >= thr for r in res if r["k"] == k) for k in KS}
    ll0, p = fit_independence(xs, N)
    ll1 = sum(loglik(xs[k], N, xs[k] / N) for k in KS)
    stat = max(0.0, 2 * (ll1 - ll0))
    fitted = {k: round(N * (1 - (1 - p) ** k), 2) for k in KS}
    return xs, p, stat, chi2_sf_df3(stat), fitted


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [(s, k) for s in range(N) for k in KS if "%03d_k%d" % (s, k) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    xs, p, stat, pv, fitted = analyse(res, 5)
    above = all(xs[k] > fitted[k] for k in (4, 8))
    cls = "SIGNAL" if pv < 0.01 and above else "CLEAN_NULL" if pv > 0.2 else "WEAK_SIGNAL"
    rx, rp, rstat, rpv, rfit = analyse(res, 20)
    out = {"classification": cls, "n_per_k": N, "depth_ge5": xs, "indep_p1": p, "indep_fitted": fitted,
           "lrt_stat": round(stat, 3), "lrt_p": pv,
           "secondary_runaway": {"counts": rx, "indep_p1": rp, "indep_fitted": rfit, "lrt_p": rpv},
           "max_depth": {k: max(r["depth"] for r in res if r["k"] == k) for k in KS}, "n_results": len(res)}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
