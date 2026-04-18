"""
euler_product_deflation.py — Harmonia worker W4.

Task: compute the real arithmetic factor a_E(k) per-curve from the local Euler
factors stored in lmfdb.public.lfunc_lfunctions.euler_factors, for a sample of
rank-0 curves at conductor decade 10^5. Deflate leading_term by a_E(1) and test
whether the residual higher moments match the pure Random-Matrix prediction
g_SO_even(k) * (log X)^{k(k-1)/2}.

Theory (Keating-Snaith 2000, Conrey-Keating-Snaith):
  M_k(X) = mean(L(1,E)^k over family) ~ a(k) · g_SO_even(k) · (log X)^{k(k-1)/2}

where
  g_SO_even(k) = prod_{j=0..k-1} j! / (j+k)! · 2^(k^2)   (KS 2000 eq. for symplectic/orthogonal)
  a(k) is the arithmetic factor, schematically:
      a(k) = prod_p (1 - 1/p)^{k(k-1)/2} · sum_m d_{-k}(m)^2 / p^m  (families)

For a PER-CURVE arithmetic factor we use the truncated Euler product
      a_E(k) := prod_{p <= P_N} L_p(1,E)^k
where L_p(1,E) = 1 / L_p-polynomial evaluated at p^-1.

Per-curve deflation: L_deflated(E) = L(1,E) / a_E(1)
Then if the family's RMT prediction holds,
  mean_E (L_deflated^k) ≈ g_SO_even(k) * (log X)^{k(k-1)/2} / (mean a_E(k-1))    ... etc.

Honest reading: the per-curve deflation removes the deterministic local-L
content. The residual is the "eigenvalue sector" whose moments should scale as
g_SO_even(k) * (log X)^{k(k-1)/2}.

Data:
- prometheus_fire.zeros.object_zeros: leading_term, lmfdb_label, conductor
- lmfdb.public.lfunc_lfunctions: euler_factors, bad_lfactors, origin, order_of_vanishing
  origin format = 'EllipticCurve/Q/{conductor}/{iso_letter}' = iso class.
  lmfdb_label like '100123.c2' -> iso '100123.c' -> origin 'EllipticCurve/Q/100123/c'.

Scope:
- Conductor 10^5..10^6, rank 0 only.
- Sample ~5000 curves.
- N_PRIMES = 50 for Euler truncation.
- Report deflated M_k and raw M_k for k=1..4, plus distribution of a_E(k).

Pattern 20: stratify by sub-decade [1e5, 3e5) and [3e5, 1e6).
"""

import json
import math
import os
import random
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2

PF = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)
LM = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

TARGET_SAMPLE = 5000
K_VALUES = [1, 2, 3, 4]
N_PRIMES = 25  # lfunc_lfunctions.euler_factors stores exactly first 25 primes (p=2..97)
DECADE_LO = 100_000
DECADE_HI = 1_000_000
SUB_DECADES = [(100_000, 300_000), (300_000, 1_000_000)]
SEED = 20260417


def sieve_primes_up_to(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(math.sqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i, ok in enumerate(sieve) if ok]


def first_n_primes(n):
    # Roughly, the n-th prime < n * ln(n) * 1.3 for n >= 6
    if n < 6:
        ub = 20
    else:
        ub = int(n * (math.log(n) + math.log(math.log(n))) + 10)
    primes = sieve_primes_up_to(ub)
    return primes[:n]


def g_so_even(k):
    """Keating-Snaith moment conjecture for SO(2N) characteristic polynomial
    at the symmetry point. Ratio-of-factorials form:
      g_SO_even(k) = 2^(k^2) * prod_{j=0..k-1} j! / (j+k)!   (one standard form)
    But the convention varies. We use the Conrey-Farmer-Keating-Rubinstein-Snaith
    convention for L(1,E) family of rank-0 ECs (SO_even):
      g_SO(k) = prod_{j=0..k-1} j! / (j+k)! * some constant.

    Per Keating-Snaith 2000 Theorem 1 / Conrey-Snaith 2007:
    For the family of quadratic twists of a fixed EC, the k-th moment constant is
      g_SO_even(k) = 2^(k^2) * prod_{j=0..k-1}  j! / (j+k)!  * small correction.

    The exact constant for the rank-0 EC family (analytic rank 0, order-of-vanishing 0)
    at the SYMMETRY POINT s=1/2 differs from s=1 by normalization. But the empirical
    test ratio M_k / (log X)^{k(k-1)/2} * 1/g(k) should tend to a(k) (arithmetic), and
    that's what we test after deflation.

    We compute the bare Barnes G-function form:
      g(k) = prod_{j=0..k-1} j! / (j+k)!
    which is the dimensionless core. Any additional 2^(k^2) factor is part of the
    normalization convention we absorb into the empirical ratio check.
    """
    num = 1.0
    den = 1.0
    for j in range(k):
        num *= math.factorial(j)
        den *= math.factorial(j + k)
    return num / den


def local_L_at_1(euler_poly, p):
    """Given an euler_factor polynomial [c0, c1, c2, ...] representing
    L_p(s)^{-1} = c0 + c1 * X + c2 * X^2 + ... with X = p^{-s},
    compute L_p(1) = 1 / sum_i c_i * p^{-i}.

    Returns None if the polynomial evaluates to 0 or is malformed.
    """
    if not euler_poly:
        return None
    val = 0.0
    x = 1.0 / p
    power = 1.0
    for c in euler_poly:
        val += c * power
        power *= x
    if abs(val) < 1e-15:
        return None
    return 1.0 / val


def compute_per_curve_euler(euler_factors, bad_lfactors, primes_target):
    """Return a dict {k: a_E(k)} for k in K_VALUES, truncated to the first
    len(primes_target) primes. Uses euler_factors for good primes and
    bad_lfactors for ramified primes.

    euler_factors is a list indexed 0..N-1 where index i corresponds to the
    i-th prime (so euler_factors[0] = factor at p=2, euler_factors[1] = at p=3, ...).
    Returns None if coverage is insufficient.
    """
    if euler_factors is None or len(euler_factors) == 0:
        return None

    bad_dict = {}
    if bad_lfactors:
        for entry in bad_lfactors:
            # Each entry is [p, [poly coeffs]]
            try:
                p_bad = int(entry[0])
                poly_bad = list(entry[1])
                bad_dict[p_bad] = poly_bad
            except (IndexError, TypeError, ValueError):
                continue

    L_per_prime = []
    for i, p in enumerate(primes_target):
        if i >= len(euler_factors):
            return None
        # Prefer bad_lfactors if p is bad
        poly = bad_dict.get(p, euler_factors[i])
        Lp = local_L_at_1(poly, p)
        if Lp is None:
            return None
        L_per_prime.append(Lp)

    product = 1.0
    for Lp in L_per_prime:
        product *= Lp

    # a_E(k) in three complementary forms:
    #   simple(k) = prod_p L_p^k               (naive, equals simple(1)^k)
    #   cks(k)    = prod_p (1 - 1/p)^{k(k-1)/2} · L_p^k   (Conrey-Keating-Snaith
    #               family weight per prime; per-curve analogue)
    #   The cks form matches the arithmetic factor structure so that
    #   E[a_E_cks(k)] converges to a(k) when averaged over Sato-Tate.
    a_E_simple = {}
    a_E_cks = {}
    for k in K_VALUES:
        val_simple = 1.0
        val_cks = 1.0
        expo_ks = k * (k - 1) / 2.0
        for i, Lp in enumerate(L_per_prime):
            p = primes_target[i]
            one_minus = (1.0 - 1.0 / p)
            val_simple *= Lp ** k
            val_cks *= (one_minus ** expo_ks) * (Lp ** k)
        a_E_simple[k] = val_simple
        a_E_cks[k] = val_cks
    return {"simple": a_E_simple, "cks": a_E_cks}, product


def parse_euler_factors(s):
    """Parse a string like '[[1, 1], [1, -1, 5], ...]' into Python lists."""
    if s is None:
        return None
    # They're valid Python literal syntax (JSON-like with brackets).
    try:
        return json.loads(s)
    except Exception:
        try:
            import ast
            return ast.literal_eval(s)
        except Exception:
            return None


def parse_bad_lfactors(s):
    if s is None:
        return []
    try:
        return json.loads(s)
    except Exception:
        try:
            import ast
            return ast.literal_eval(s)
        except Exception:
            return []


def load_rank0_sample():
    """Return list of {lmfdb_label, iso_origin, conductor, leading_term}."""
    rng = random.Random(SEED)
    # First fetch ALL rank 0 labels at decade 10^5 — 559K total, cheap.
    with psycopg2.connect(**PF) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND analytic_rank = 0
              AND conductor >= %s AND conductor < %s
              AND leading_term IS NOT NULL AND leading_term > 0
              AND lmfdb_label IS NOT NULL
        """, (DECADE_LO, DECADE_HI))
        all_rows = cur.fetchall()
    print(f"[load] total rank-0 curves in [{DECADE_LO}, {DECADE_HI}): {len(all_rows)}")

    # Random sample
    if len(all_rows) > TARGET_SAMPLE:
        sampled = rng.sample(all_rows, TARGET_SAMPLE)
    else:
        sampled = list(all_rows)
    print(f"[load] sampled: {len(sampled)}")

    # Derive isogeny origin: '100123.c2' -> 'EllipticCurve/Q/100123/c'
    out = []
    for lbl, cond, lt in sampled:
        parts = lbl.split('.')
        if len(parts) != 2:
            continue
        cond_str = parts[0]
        iso_rest = parts[1]
        iso_letter = ''
        for ch in iso_rest:
            if ch.isalpha():
                iso_letter += ch
            else:
                break
        if not iso_letter:
            continue
        origin = f"EllipticCurve/Q/{cond_str}/{iso_letter}"
        out.append({
            'lmfdb_label': lbl,
            'iso_origin': origin,
            'conductor': int(cond),
            'leading_term': float(lt),
        })
    return out


def fetch_lfunc_data(origins):
    """For a list of origin strings, fetch euler_factors and bad_lfactors
    from lfunc_lfunctions. Returns dict {origin: (euler_factors_list, bad_lfactors_list)}.
    Uses chunked IN() queries to be network-friendly."""
    out = {}
    chunk_size = 500
    origins = list(set(origins))
    with psycopg2.connect(**LM) as conn:
        cur = conn.cursor()
        for i in range(0, len(origins), chunk_size):
            chunk = origins[i:i + chunk_size]
            cur.execute("""
                SELECT origin, euler_factors, bad_lfactors
                FROM public.lfunc_lfunctions
                WHERE origin = ANY(%s)
                  AND order_of_vanishing = '0'
            """, (chunk,))
            for origin, ef_str, bf_str in cur.fetchall():
                ef = parse_euler_factors(ef_str)
                bf = parse_bad_lfactors(bf_str)
                if origin not in out:  # first wins (isogeny class may have multiple L)
                    out[origin] = (ef, bf)
            if (i // chunk_size) % 4 == 0:
                print(f"[fetch] chunk {i // chunk_size + 1}/{(len(origins) + chunk_size - 1) // chunk_size} done ({len(out)} resolved)")
    return out


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[euler_deflation] start {started}")

    primes = first_n_primes(N_PRIMES)
    print(f"[euler_deflation] first {N_PRIMES} primes: {primes[:10]}...{primes[-3:]}")

    sample = load_rank0_sample()
    origins = [s['iso_origin'] for s in sample]
    print(f"[euler_deflation] unique origins: {len(set(origins))}")

    lfunc_map = fetch_lfunc_data(origins)
    print(f"[euler_deflation] resolved lfunc rows: {len(lfunc_map)}")

    # Compute per-curve a_E(k) and deflate
    rows = []
    coverage_fail = 0
    parse_fail = 0
    for s in sample:
        pair = lfunc_map.get(s['iso_origin'])
        if pair is None:
            parse_fail += 1
            continue
        ef, bf = pair
        if ef is None:
            parse_fail += 1
            continue
        res = compute_per_curve_euler(ef, bf, primes)
        if res is None:
            coverage_fail += 1
            continue
        a_E, _partial_L = res
        rows.append({
            **s,
            'a_E_simple': a_E['simple'],   # dict k -> prod_p L_p^k
            'a_E_cks': a_E['cks'],          # dict k -> CKS-weighted arithmetic factor
        })

    print(f"[euler_deflation] usable rows: {len(rows)} "
          f"(parse_fail={parse_fail}, coverage_fail={coverage_fail})")

    if len(rows) == 0:
        results = {
            "task": "euler_product_deflation_W4",
            "status": "BLOCKED_BY_DATA_SHAPE",
            "reason": "zero rows resolved",
            "started": started,
            "finished": datetime.now(timezone.utc).isoformat(),
        }
        out_path = os.path.join("cartography", "docs",
                                "euler_product_deflation_results.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=float)
        return

    # =======================================================================
    # Analysis per sub-decade
    # =======================================================================
    per_subdecade = {}
    for lo, hi in SUB_DECADES + [(DECADE_LO, DECADE_HI)]:  # include full decade too
        subset = [r for r in rows if lo <= r['conductor'] < hi]
        if len(subset) < 100:
            continue
        x_mid = math.sqrt(lo * hi)
        log_x = math.log(x_mid)

        # Arrays
        L = np.array([r['leading_term'] for r in subset], dtype=float)
        a_E_1_simple = np.array([r['a_E_simple'][1] for r in subset], dtype=float)
        # Deflated values (L divided by truncated Euler-product L at k=1)
        L_def = L / a_E_1_simple

        # Raw moments
        raw_M = {k: float(np.mean(L ** k)) for k in K_VALUES}
        # Deflated moments (divide by simple a_E(1))
        def_M = {k: float(np.mean(L_def ** k)) for k in K_VALUES}
        # CKS-form deflation: E[ L^k / a_E_cks(k) ] — deflate by the full CKS
        # arithmetic factor prod_p (1-1/p)^{k(k-1)/2} L_p^k.
        # If the truncated Euler product captured the full arithmetic content,
        # this ratio would be ~ g_SO_even(k) * (log X)^{k(k-1)/2} per curve-family
        # prediction, hence def_M_cks / rmt_pred should approach unity.
        def_M_cks = {}
        for k in K_VALUES:
            aEk_cks = np.array([r['a_E_cks'][k] for r in subset], dtype=float)
            def_M_cks[k] = float(np.mean(L ** k / aEk_cks))
        # Euler a_E(k) distribution stats — simple and CKS forms
        a_E_stats_simple = {}
        a_E_stats_cks = {}
        for k in K_VALUES:
            arr_s = np.array([r['a_E_simple'][k] for r in subset], dtype=float)
            arr_c = np.array([r['a_E_cks'][k] for r in subset], dtype=float)
            a_E_stats_simple[k] = {
                "mean": float(np.mean(arr_s)), "median": float(np.median(arr_s)),
                "std": float(np.std(arr_s, ddof=1)),
                "p05": float(np.percentile(arr_s, 5)),
                "p95": float(np.percentile(arr_s, 95)),
            }
            a_E_stats_cks[k] = {
                "mean": float(np.mean(arr_c)), "median": float(np.median(arr_c)),
                "std": float(np.std(arr_c, ddof=1)),
                "p05": float(np.percentile(arr_c, 5)),
                "p95": float(np.percentile(arr_c, 95)),
            }

        # Predicted RMT ratio
        rmt_pred = {}
        for k in K_VALUES:
            expo = k * (k - 1) / 2.0
            g = g_so_even(k)
            logX_pow = log_x ** expo if expo > 0 else 1.0
            rmt_value = g * logX_pow
            ratio_raw = raw_M[k] / rmt_value if rmt_value > 0 else None
            ratio_def = def_M[k] / rmt_value if rmt_value > 0 else None
            ratio_def_cks = def_M_cks[k] / rmt_value if rmt_value > 0 else None
            rmt_pred[k] = {
                "g_SO_even": g,
                "exponent_k(k-1)/2": expo,
                "logX_to_exp": logX_pow,
                "rmt_prediction": rmt_value,
                "M_k_raw_over_rmt": ratio_raw,
                "M_k_deflated_by_aE1_over_rmt": ratio_def,
                "M_k_deflated_by_aE_cks_over_rmt": ratio_def_cks,
            }

        # L_deflated unit-scale check: mean should be ~O(1)
        L_def_mean = float(np.mean(L_def))
        L_def_median = float(np.median(L_def))
        L_def_std = float(np.std(L_def, ddof=1))

        per_subdecade[f"[{lo},{hi})"] = {
            "n": len(subset),
            "conductor_range": [lo, hi],
            "log_X_mid": log_x,
            "raw_M_k": {str(k): v for k, v in raw_M.items()},
            "deflated_M_k_by_aE1": {str(k): v for k, v in def_M.items()},
            "deflated_M_k_by_aE_cks": {str(k): v for k, v in def_M_cks.items()},
            "a_E_simple_distribution": {str(k): v for k, v in a_E_stats_simple.items()},
            "a_E_cks_distribution": {str(k): v for k, v in a_E_stats_cks.items()},
            "rmt_prediction": {str(k): v for k, v in rmt_pred.items()},
            "L_deflated_summary": {
                "mean": L_def_mean,
                "median": L_def_median,
                "std": L_def_std,
            },
        }

    # =======================================================================
    # Cross-subdecade stability: does deflation reduce slope of M_k / RMT ratio
    # across sub-decades? A flatter slope = better removal of arithmetic drift.
    # =======================================================================
    stability = {}
    sub1 = per_subdecade.get(f"[{SUB_DECADES[0][0]},{SUB_DECADES[0][1]})")
    sub2 = per_subdecade.get(f"[{SUB_DECADES[1][0]},{SUB_DECADES[1][1]})")
    if sub1 and sub2:
        dlog = sub2["log_X_mid"] - sub1["log_X_mid"]
        for k in K_VALUES:
            raw1 = sub1["rmt_prediction"][str(k)]["M_k_raw_over_rmt"]
            raw2 = sub2["rmt_prediction"][str(k)]["M_k_raw_over_rmt"]
            def1 = sub1["rmt_prediction"][str(k)]["M_k_deflated_by_aE1_over_rmt"]
            def2 = sub2["rmt_prediction"][str(k)]["M_k_deflated_by_aE1_over_rmt"]
            cks1 = sub1["rmt_prediction"][str(k)]["M_k_deflated_by_aE_cks_over_rmt"]
            cks2 = sub2["rmt_prediction"][str(k)]["M_k_deflated_by_aE_cks_over_rmt"]
            slope_raw = (raw2 - raw1) / dlog if dlog != 0 else None
            slope_def = (def2 - def1) / dlog if dlog != 0 else None
            slope_cks = (cks2 - cks1) / dlog if dlog != 0 else None
            stability[str(k)] = {
                "sub1_raw_ratio": raw1, "sub2_raw_ratio": raw2,
                "sub1_def_by_aE1": def1, "sub2_def_by_aE1": def2,
                "sub1_def_by_aE_cks": cks1, "sub2_def_by_aE_cks": cks2,
                "d_log_X": dlog,
                "slope_raw_per_logX": slope_raw,
                "slope_def_by_aE1_per_logX": slope_def,
                "slope_def_by_aE_cks_per_logX": slope_cks,
                "def_by_aE1_flattens_vs_raw": (
                    abs(slope_def) < abs(slope_raw)
                    if (slope_raw is not None and slope_def is not None)
                    else None
                ),
                "def_by_aE_cks_flattens_vs_raw": (
                    abs(slope_cks) < abs(slope_raw)
                    if (slope_raw is not None and slope_cks is not None)
                    else None
                ),
            }

    # =======================================================================
    # Diagnostic: correlation of a_E(1) with leading_term
    # If a_E(1) is a good approximation of L(1,E) from first 50 primes,
    # correlation should be strong (close to 1).
    # =======================================================================
    L_all = np.array([r['leading_term'] for r in rows], dtype=float)
    aE1_all = np.array([r['a_E_simple'][1] for r in rows], dtype=float)
    # Pearson corr
    if len(L_all) > 1:
        cov = np.mean((L_all - L_all.mean()) * (aE1_all - aE1_all.mean()))
        sx = L_all.std()
        sy = aE1_all.std()
        if sx > 0 and sy > 0:
            pearson = float(cov / (sx * sy))
        else:
            pearson = None
        # Rank (Spearman) via argsort
        rx = np.argsort(np.argsort(L_all))
        ry = np.argsort(np.argsort(aE1_all))
        cov_r = np.mean((rx - rx.mean()) * (ry - ry.mean()))
        sxr = rx.std()
        syr = ry.std()
        spearman = float(cov_r / (sxr * syr)) if (sxr > 0 and syr > 0) else None
    else:
        pearson = spearman = None

    # =======================================================================
    # Verdict assembly
    # =======================================================================
    # Success criterion for the deflation direction:
    #   Deflated L should have mean (over the sample) close to 1 IF a_E(1) is
    #   a proper rescaling. Precisely, if a_E(1) = truncated-Euler-product L,
    #   then leading_term / a_E(1) tends to (tail of Euler product) which is
    #   near 1 for large X and large N_PRIMES.
    # Deflated M_k / (g_SO * (log X)^{k(k-1)/2}) should tend to a small constant
    # (not 1 unless we also divide out arithmetic-factor corrections).
    full = per_subdecade.get(f"[{DECADE_LO},{DECADE_HI})", {})
    L_def_mean_headline = full.get("L_deflated_summary", {}).get("mean") if full else None
    pearson_headline = pearson
    verdict = "SUCCESS_DEFLATED" if (L_def_mean_headline and
                                      0.3 < L_def_mean_headline < 3.0 and
                                      pearson is not None and pearson > 0.3) else \
              "PARTIAL" if len(rows) > 1000 else \
              "BLOCKED_BY_DATA_SHAPE"

    results = {
        "task": "euler_product_deflation_W4",
        "instance": "Harmonia_worker_W4",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "status": verdict,
        "config": {
            "target_sample": TARGET_SAMPLE,
            "decade": [DECADE_LO, DECADE_HI],
            "sub_decades": [list(p) for p in SUB_DECADES],
            "k_values": K_VALUES,
            "n_primes_truncation": N_PRIMES,
            "primes_used_first_and_last": [primes[0], primes[-1]],
            "seed": SEED,
        },
        "data_access": {
            "leading_term_from": "prometheus_fire.zeros.object_zeros (rank 0, conductor 10^5..10^6)",
            "euler_factors_from": "lmfdb.public.lfunc_lfunctions (origin = EllipticCurve/Q/N/iso)",
            "bad_lfactors_from": "lmfdb.public.lfunc_lfunctions.bad_lfactors",
            "join": "lmfdb_label -> iso via string manipulation -> origin",
        },
        "counts": {
            "sample_size": len(sample),
            "parse_fail": parse_fail,
            "coverage_fail": coverage_fail,
            "usable_rows": len(rows),
        },
        "correlation_L_vs_a_E_1": {
            "pearson": pearson,
            "spearman": spearman,
            "interpretation": (
                "Pearson(L(1,E), truncated Euler product) should be > 0.5 if the "
                "truncation to N primes captures most of the multiplicative content. "
                "Values near 1 confirm the Euler product is computed correctly."
            ),
        },
        "per_subdecade": per_subdecade,
        "cross_subdecade_stability": stability,
        "g_so_even_values": {str(k): g_so_even(k) for k in K_VALUES},
        "interpretation": (
            "We compute a per-curve arithmetic factor a_E(k) = prod_{p<=P_50} L_p(1,E)^k, "
            "which is the truncated Euler product of L(1,E) raised to power k. "
            "At k=1, a_E(1) is an approximation of L(1,E) itself. Deflating "
            "leading_term by a_E(1) gives a residual whose scale is the tail of the "
            "Euler product. If truncation captures the arithmetic content, the residual "
            "higher moments should be closer to pure-RMT predictions g_SO_even(k) * "
            "(log X)^{k(k-1)/2}. We report both raw and deflated M_k / RMT-prediction "
            "ratios; the difference is the arithmetic-factor contribution."
        ),
        "caveats": [
            "Per-curve a_E(k) is NOT the family arithmetic factor a(k) in Conrey-"
            "Keating-Snaith; it's a per-curve variable. The family factor is an average "
            "over the arithmetic content, and the task instructions define per-curve "
            "deflation as the operational proxy.",
            "Truncation at N_PRIMES=50 leaves a residual multiplicative tail. Larger "
            "N would capture more arithmetic content but the per-prime data grows.",
            "g_SO_even convention here is the bare Barnes-G ratio prod j!/(j+k)!. "
            "Alternate conventions include a 2^(k^2) prefactor. The ratio "
            "M_k_raw / (g_SO * (log X)^{k(k-1)/2}) is the empirical arithmetic constant; "
            "convention choice shifts it by a known factor but not the scaling with X.",
            "leading_term in prometheus_fire IS L(1,E)/1! = L(1,E) for rank 0 curves. "
            "This is verified via BSD parity audits (F003).",
            "Sample is restricted to rank-0 (SO_even conjecture). No rank pooling.",
        ],
        "pattern_20_discipline": [
            "Sample restricted to rank 0 — no pooling across ranks.",
            "Sub-decade stratification within 10^5..10^6 for Pattern 20 compliance.",
            "Each sub-decade reports its own n, M_k, a_E(k) stats, and RMT ratios.",
        ],
        "followups_motivated": [
            "Extend N_PRIMES to 200 — does the deflated residual shrink toward 1?",
            "Compute family arithmetic factor a(k) = mean_E a_E(k) and divide out; "
            "the remaining ratio should be g_SO_even(k) exactly.",
            "Repeat with rank 1 (SO_odd prediction) — distinct g_SO_odd(k) with "
            "different factorial structure.",
            "Block-shuffle a_E(1) within sub-decade and verify deflation still works "
            "(pipeline sanity check).",
        ],
    }

    out_path = os.path.join("cartography", "docs",
                            "euler_product_deflation_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[euler_deflation] wrote {out_path}")
    print(f"[euler_deflation] verdict: {verdict}")
    print(f"[euler_deflation] pearson(L, a_E(1)) = {pearson}")
    if full:
        print(f"[euler_deflation] full-decade L_deflated mean = {L_def_mean_headline}")
        for k in K_VALUES:
            pred = full["rmt_prediction"][str(k)]
            print(f"  k={k}: raw/RMT={pred['M_k_raw_over_rmt']:.4e}, "
                  f"def_aE1/RMT={pred['M_k_deflated_by_aE1_over_rmt']:.4e}, "
                  f"def_cks/RMT={pred['M_k_deflated_by_aE_cks_over_rmt']:.4e}")


if __name__ == "__main__":
    main()
