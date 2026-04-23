"""Audit: F041a — does the rank-2+ moment-slope monotone-in-nbp ladder
survive Euler-product deflation at bad primes?

Spec source:
  Agora task `audit_F041a_euler_product_deflation` (posted_by Harmonia_M2_sessionA,
  2026-04-18). Output goes to
  cartography/docs/audit_F041a_euler_product_deflation_results.json.

Method
------
For each rank-2 elliptic curve (one per isogeny class), pull leading_term
and bad_lfactors from LMFDB lfunc_lfunctions. Compute the bad-prime
local L-factor product evaluated at s=1:
    E_bad(1) = prod_{p | N}  L_p(1) = prod_{p | N}  1 / poly_p(1/p)
where poly_p is the local Euler polynomial in T = p^{-s}. Multiplicative
primes give poly = [1, +/- 1] (L_p(1) = p/(p +/- 1)); additive give
poly = [1] (L_p(1) = 1).

The Euler-deflated leading term is
    M_def := leading_term * prod_{p | N} poly_p(1/p)
which equals leading_term / E_bad(1). This removes the bad-prime arithmetic
factor predicted by CFKRS rank-2 SO(even).

We then run, per num_bad_primes stratum k in {1..6}, the OLS slope
    slope_k = OLS slope of log(M) vs log(conductor)
on both M = leading_term (raw) and M = M_def (deflated). If the raw
ladder (slope_1 < slope_2 < ... < slope_6) flattens after deflation,
F041a IS the bad-prime arithmetic factor (Pattern 30 SHARED_VARIABLE).
If it persists, F041a is real RMT structure beyond the Euler product.

Block-shuffle null
------------------
Within (nbp, conductor-decade) cells, permute the response (log M)
across rows; recompute per-stratum slopes; record null distribution.
500 perms, seed 20260417 to match NULL_BSWCD@v2 conventions.

Output
------
JSON at cartography/docs/audit_F041a_euler_product_deflation_results.json
with: per-nbp slopes (raw + deflated), null mean / std / z, deflator
distribution stats, verdict.
"""
import json
import math
import os
import sys
import io
import time
from pathlib import Path

import numpy as np
import psycopg2

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


PG = dict(host="192.168.1.176", port=5432, user="lmfdb", password="lmfdb", dbname="lmfdb")
SEED = 20260417
N_PERMS = 500
DEC_BIN_WIDTH = 1.0  # log10(N) decade
NBP_BINS = (1, 2, 3, 4, 5, 6)
OUT_PATH = Path("cartography/docs/audit_F041a_euler_product_deflation_results.json")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def fetch_data():
    log("connecting to LMFDB...")
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    # Stratified-by-nbp sample to keep the audit window short while preserving
    # statistical power. Per-stratum cap PER_STRATUM_CAP gives ~6 * cap rows.
    # F041a's original effect at nbp=1..6 was visible at 5K per stratum.
    PER_STRATUM_CAP = 5000
    sql_ec = """
        SELECT  e.lmfdb_label, e.conductor, e.num_bad_primes,
                'EllipticCurve/Q/' || e.conductor || '/'
                       || split_part(e.lmfdb_iso, '.', 2) AS origin_key
          FROM  (
              SELECT *,
                     ROW_NUMBER() OVER (
                       PARTITION BY num_bad_primes
                       ORDER BY md5(lmfdb_label)
                     ) AS rn
                FROM ec_curvedata
               WHERE rank = '2'
                 AND "Cnumber" = '1'
                 AND num_bad_primes IN ('1','2','3','4','5','6')
          ) e
         WHERE  e.rn <= %s
    """
    log(f"  step 1: pulling rank=2 primary EC stratified sample (cap={PER_STRATUM_CAP}/nbp)...")
    t0 = time.time()
    cur.execute(sql_ec, (PER_STRATUM_CAP,))
    ec_rows = cur.fetchall()
    log(f"    fetched {len(ec_rows)} EC rows in {time.time()-t0:.1f}s")

    # Build origin -> (label, cond, nbp) map
    ec_by_origin = {row[3]: (row[0], row[1], row[2]) for row in ec_rows}
    origins = list(ec_by_origin.keys())

    # Bulk-fetch lfunc rows in chunks of 1000
    log(f"  step 2: bulk-fetching lfunc rows for {len(origins)} origins...")
    fetched = []
    chunk_size = 1000
    t0 = time.time()
    for chunk_start in range(0, len(origins), chunk_size):
        chunk = origins[chunk_start:chunk_start + chunk_size]
        cur.execute(
            "SELECT origin, leading_term, bad_lfactors FROM lfunc_lfunctions "
            "WHERE origin = ANY(%s) AND leading_term IS NOT NULL AND bad_lfactors IS NOT NULL",
            (chunk,),
        )
        chunk_rows = cur.fetchall()
        for origin, leading, bad_lf in chunk_rows:
            label, cond, nbp = ec_by_origin[origin]
            fetched.append((label, cond, nbp, leading, bad_lf))
        if (chunk_start // chunk_size) % 5 == 0:
            log(f"    progress: {chunk_start + len(chunk)}/{len(origins)}, kept {len(fetched)}, {time.time()-t0:.1f}s elapsed")
    log(f"    bulk fetch done: {len(fetched)} joined rows in {time.time()-t0:.1f}s")
    rows = fetched
    cur.close()
    conn.close()
    return rows


def parse_bad_lfactors(s):
    """Parse the text-encoded bad_lfactors field; return list of (p, [coeffs])."""
    return json.loads(s)


def deflator_log(N, bad_lfactors_str):
    """Return log( prod_{p|N} poly_p(1/p) ) from the bad_lfactors text."""
    items = parse_bad_lfactors(bad_lfactors_str)
    log_total = 0.0
    for p, poly in items:
        # poly_p(1/p) = sum_i coeffs[i] * p^{-i}
        v = sum(c * (p ** (-i)) for i, c in enumerate(poly))
        if v <= 0:
            # shouldn't happen for L-factor at central value > 1
            return float("nan")
        log_total += math.log(v)
    return log_total


def ols_slope(x, y):
    """Plain OLS slope; x and y are 1-D numpy arrays."""
    if len(x) < 2:
        return float("nan")
    xm = x - x.mean()
    ym = y - y.mean()
    denom = (xm * xm).sum()
    if denom == 0:
        return float("nan")
    return float((xm * ym).sum() / denom)


def per_nbp_slopes(log_N, log_M, nbp):
    out = {}
    for k in NBP_BINS:
        mask = nbp == k
        n = int(mask.sum())
        if n < 50:
            out[k] = {"slope": None, "n": n, "note": "too few"}
            continue
        s = ols_slope(log_N[mask], log_M[mask])
        out[k] = {"slope": s, "n": n}
    return out


def null_slopes(log_N, log_M, nbp, decade, n_perms=N_PERMS, seed=SEED):
    """Block-shuffle within (nbp, decade) cell. Permute log_M only.

    Returns dict[k] = {mean, std, p99, n_perms}.
    """
    rng = np.random.default_rng(seed)
    keys = list(zip(nbp.tolist(), decade.tolist()))
    # group indices by (nbp, decade)
    groups = {}
    for i, key in enumerate(keys):
        groups.setdefault(key, []).append(i)

    null_per_k = {k: [] for k in NBP_BINS}
    for perm_i in range(n_perms):
        log_M_perm = log_M.copy()
        for key, idxs in groups.items():
            if len(idxs) < 2:
                continue
            arr = np.array(idxs)
            perm = rng.permutation(len(arr))
            log_M_perm[arr] = log_M[arr[perm]]
        for k in NBP_BINS:
            mask = nbp == k
            if mask.sum() < 50:
                continue
            s = ols_slope(log_N[mask], log_M_perm[mask])
            null_per_k[k].append(s)

    out = {}
    for k in NBP_BINS:
        arr = np.asarray(null_per_k[k])
        if len(arr) == 0:
            out[k] = {"mean": None, "std": None, "n_perms": 0}
            continue
        out[k] = {
            "mean": float(arr.mean()),
            "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
            "p99_abs": float(np.quantile(np.abs(arr - arr.mean()), 0.99)),
            "n_perms": len(arr),
        }
    return out


def main():
    rows = fetch_data()
    n_raw = len(rows)
    log("parsing rows...")
    parsed = []
    parse_errors = 0
    for label, cond, nbp, leading, bad_lf in rows:
        try:
            N = int(cond)
            k = int(nbp)
            M = float(leading)
            if k not in NBP_BINS:
                continue
            if M <= 0:
                continue
            d_log = deflator_log(N, bad_lf)
            if not math.isfinite(d_log):
                continue
            parsed.append((label, N, k, M, d_log))
        except Exception:
            parse_errors += 1
    log(f"  parsed: {len(parsed)} kept, {parse_errors} parse errors, {n_raw-len(parsed)-parse_errors} filtered")

    if not parsed:
        raise SystemExit("no usable rows")

    labels = [r[0] for r in parsed]
    N_arr = np.array([r[1] for r in parsed], dtype=np.float64)
    nbp_arr = np.array([r[2] for r in parsed], dtype=np.int64)
    M_arr = np.array([r[3] for r in parsed], dtype=np.float64)
    d_log = np.array([r[4] for r in parsed], dtype=np.float64)

    log_N = np.log(N_arr)
    log_M_raw = np.log(M_arr)
    log_M_def = log_M_raw + d_log  # deflated = M * prod poly_p(1/p)

    decade = np.floor(log_N / math.log(10)).astype(np.int64)

    # per-stratum n
    nbp_n = {int(k): int((nbp_arr == k).sum()) for k in NBP_BINS}
    log(f"  per-nbp n: {nbp_n}")

    # deflator stats (per-nbp summary)
    deflator_stats = {}
    for k in NBP_BINS:
        mask = nbp_arr == k
        if mask.sum() == 0:
            continue
        d = d_log[mask]
        deflator_stats[int(k)] = {
            "mean_log_deflator": float(d.mean()),
            "std_log_deflator": float(d.std(ddof=1)) if mask.sum() > 1 else 0.0,
            "min": float(d.min()),
            "max": float(d.max()),
            "n": int(mask.sum()),
        }

    log("computing raw per-nbp slopes...")
    raw_slopes = per_nbp_slopes(log_N, log_M_raw, nbp_arr)
    log(f"  {raw_slopes}")

    log("computing deflated per-nbp slopes...")
    def_slopes = per_nbp_slopes(log_N, log_M_def, nbp_arr)
    log(f"  {def_slopes}")

    log(f"running block-shuffle null on RAW (n_perms={N_PERMS})...")
    t0 = time.time()
    null_raw = null_slopes(log_N, log_M_raw, nbp_arr, decade)
    log(f"  raw null: {time.time()-t0:.1f}s")

    log(f"running block-shuffle null on DEFLATED (n_perms={N_PERMS})...")
    t0 = time.time()
    null_def = null_slopes(log_N, log_M_def, nbp_arr, decade)
    log(f"  deflated null: {time.time()-t0:.1f}s")

    # z-scores per stratum
    def z_scores(slopes, null):
        out = {}
        for k in NBP_BINS:
            obs = slopes.get(k, {}).get("slope")
            n = null.get(k, {})
            if obs is None or n.get("std") in (None, 0.0):
                out[int(k)] = None
                continue
            z = (obs - n["mean"]) / n["std"]
            out[int(k)] = {"slope_observed": obs, "null_mean": n["mean"], "null_std": n["std"], "z": z, "n_perms": n["n_perms"], "n": slopes[k]["n"]}
        return out

    z_raw = z_scores(raw_slopes, null_raw)
    z_def = z_scores(def_slopes, null_def)

    # ladder amplitude: max - min slope across nbp bins
    def ladder_amp(slopes):
        vals = [v["slope"] for v in slopes.values() if v.get("slope") is not None]
        if len(vals) < 2:
            return None
        return float(max(vals) - min(vals))

    amp_raw = ladder_amp(raw_slopes)
    amp_def = ladder_amp(def_slopes)
    amp_ratio = (amp_def / amp_raw) if (amp_raw and amp_raw > 0) else None

    # corr(nbp, slope)
    def slope_nbp_corr(slopes):
        ks, vs = [], []
        for k, v in slopes.items():
            if v.get("slope") is not None:
                ks.append(int(k))
                vs.append(v["slope"])
        if len(ks) < 3:
            return None
        ks = np.array(ks, dtype=float)
        vs = np.array(vs, dtype=float)
        return float(np.corrcoef(ks, vs)[0, 1])

    corr_raw = slope_nbp_corr(raw_slopes)
    corr_def = slope_nbp_corr(def_slopes)

    # verdict
    if amp_ratio is None:
        verdict = "INCONCLUSIVE_NO_AMPLITUDE"
    elif amp_ratio < 0.20:
        verdict = "COLLAPSE  (deflator absorbs >=80% of ladder amplitude — F041a IS the bad-prime arithmetic factor; Pattern 30 SHARED_VARIABLE)"
    elif amp_ratio < 0.50:
        verdict = "PARTIAL_COLLAPSE  (deflator absorbs 50-80% — Pattern 30 PARTIAL holds; F041a is mostly arithmetic but has residual)"
    elif amp_ratio < 0.80:
        verdict = "PARTIAL_PERSIST  (deflator absorbs 20-50% — F041a survives mostly, residual real)"
    else:
        verdict = "PERSIST  (deflator absorbs <20% — F041a is real RMT structure beyond Euler factor; promotion case)"

    out = {
        "task_id": "audit_F041a_euler_product_deflation",
        "instance": "Harmonia_M2_auditor",
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "spec": (
            "Test whether F041a's rank-2 monotone-in-nbp slope ladder survives "
            "Euler-product deflation at bad primes. Deflator = prod_{p|N} poly_p(1/p) "
            "from lmfdb.lfunc_lfunctions.bad_lfactors evaluated at s=1."
        ),
        "data": {
            "rank": 2,
            "primary_per_iso": True,
            "n_total": len(parsed),
            "per_nbp_n": nbp_n,
            "data_source_commit": "lmfdb prometheus_sci snapshot at run time",
        },
        "deflator_stats_per_nbp": deflator_stats,
        "raw": {
            "per_nbp_slopes": raw_slopes,
            "ladder_amplitude": amp_raw,
            "corr_nbp_slope": corr_raw,
            "block_null_z_scores": z_raw,
        },
        "deflated": {
            "per_nbp_slopes": def_slopes,
            "ladder_amplitude": amp_def,
            "corr_nbp_slope": corr_def,
            "block_null_z_scores": z_def,
        },
        "comparison": {
            "amp_ratio_def_over_raw": amp_ratio,
            "amp_change_absolute": (amp_def - amp_raw) if (amp_raw is not None and amp_def is not None) else None,
        },
        "verdict": verdict,
        "null_protocol": {
            "type": "block_shuffle",
            "stratifier": "(num_bad_primes, conductor_decade)",
            "shuffle_col": "log_leading_term",
            "n_perms": N_PERMS,
            "seed": SEED,
            "note": "Joint stratifier per null_protocol_v1.md Class 2 stricter variant.",
        },
        "method_notes": [
            "Deflator computed from bad_lfactors poly evaluated at T = 1/p.",
            "Curve cohort: rank=2 EC, one per isogeny class (Cnumber='1').",
            "Local Euler factor at multiplicative p: poly = [1, +/-1] -> L_p(1) = p/(p +/- 1).",
            "Local Euler factor at additive p: poly = [1] -> L_p(1) = 1 (no contribution).",
            "Deflated leading_term replaces bad-prime contribution with 1; retains good-prime structure + RMT factor.",
        ],
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as fh:
        json.dump(out, fh, indent=2)
    log(f"wrote {OUT_PATH}")
    log(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
