"""Recompute C3-3 preflight region quantities that the producer ASSERTS.

Harmonia[m2-f541bed9], 2026-09-14. Independent of archaeon/producer code: the
edges are copied from C3_3_PREFLIGHT.json, the binomial is exact, the band is
from ruling 3e. Writes JSON to argv[1].
"""
import json
import math
import sys
from bisect import bisect_left, bisect_right

import numpy as np

N_BITS = 128
EDGES = [57, 59, 61, 63, 64, 65, 67, 69, 71]
BAND = (1 / 3.0, 3.0)
CORPUS = 120
PREFLIGHT_N = 60
OBS_PREFLIGHT = {"pc00": 8, "pc01": 4, "pc02": 9, "pc03": 9, "pc04": 1,
                 "pc05": 4, "pc06": 3, "pc07": 10, "pc08": 5, "pc09": 7}

pmf = [math.comb(N_BITS, k) / 2.0 ** N_BITS for k in range(N_BITS + 1)]


def masses(convention):
    m = [0.0] * (len(EDGES) + 1)
    for k, p in enumerate(pmf):
        i = bisect_right(EDGES, k) if convention == "right" else bisect_left(EDGES, k)
        m[i] += p
    return m


def binom_sf(n, p, k):
    """P(X >= k)."""
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def binom_cdf(n, p, k):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(0, k + 1))


def ratios(values, regions, n_regions):
    """The producer's D3-style ratio: region var / pooled within of the others."""
    by = [values[regions == r] for r in range(n_regions)]
    var = [np.var(v, ddof=1) if len(v) >= 2 else None for v in by]
    out = {}
    for r in range(n_regions):
        if var[r] is None:
            continue
        num = sum((len(by[o]) - 1) * var[o] for o in range(n_regions)
                  if o != r and var[o] is not None)
        df = sum(len(by[o]) - 1 for o in range(n_regions)
                 if o != r and var[o] is not None)
        if df > 0:
            out[r] = var[r] / (num / df)
    return out


def mc(m, n_tables, reps, rng):
    outside_any = 0
    outside_counts = []
    eligible = []
    for _ in range(reps):
        regions = rng.choice(len(m), size=n_tables, p=m)
        values = rng.normal(0.5, 0.0049, size=n_tables)
        rr = ratios(values, regions, len(m))
        k = sum(1 for v in rr.values() if not (BAND[0] <= v <= BAND[1]))
        outside_counts.append(k)
        eligible.append(len(rr))
        outside_any += k > 0
    oc = np.array(outside_counts)
    return {"reps": reps, "n_tables": n_tables,
            "P_any_region_outside_band": outside_any / reps,
            "mean_regions_outside": float(oc.mean()),
            "mean_regions_with_ratio": float(np.mean(eligible)),
            "P_outside_ge2": float((oc >= 2).mean())}


def main():
    rng = np.random.default_rng(20260914)
    res = {"edges": EDGES, "band": BAND, "corpus": CORPUS}
    for conv in ("right", "left"):
        m = masses(conv)
        exp120 = [CORPUS * p for p in m]
        pge8 = [binom_sf(CORPUS, p, 8) for p in m]
        res[conv] = {
            "region_mass": [round(p, 5) for p in m],
            "expected_at_120": [round(e, 2) for e in exp120],
            "P_ge8_at_120": [round(p, 4) for p in pge8],
            "expected_regions_ge8": round(sum(pge8), 3),
            "P_all_10_regions_ge8_indep_approx": round(float(np.prod(pge8)), 4),
            "expected_at_60": [round(PREFLIGHT_N * p, 2) for p in m],
            "P_le_observed_at_60": {
                "pc%02d" % i: round(binom_cdf(PREFLIGHT_N, p, OBS_PREFLIGHT["pc%02d" % i]), 4)
                for i, p in enumerate(m)},
            "mc_band_at_60": mc(m, PREFLIGHT_N, 4000, rng),
            "mc_band_at_120": mc(m, CORPUS, 4000, rng),
        }
    # chi-square of preflight occupancy vs each convention
    for conv in ("right", "left"):
        m = masses(conv)
        chi = sum((OBS_PREFLIGHT["pc%02d" % i] - PREFLIGHT_N * p) ** 2 / (PREFLIGHT_N * p)
                  for i, p in enumerate(m))
        res[conv]["chi2_preflight_occupancy_df9"] = round(chi, 3)
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    print(json.dumps({c: {k: res[c][k] for k in ("region_mass", "expected_regions_ge8",
                                                 "chi2_preflight_occupancy_df9")}
                      for c in ("right", "left")}, indent=1))


if __name__ == "__main__":
    main()
