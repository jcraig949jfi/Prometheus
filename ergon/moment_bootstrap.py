"""
Keating-Snaith moment ratio bootstrap confidence intervals.

Tests whether non-monotonic behavior of R_k(X) = M_k(X) / (log X)^{k(k-1)/2}
across conductor bins for rank-0 EC curves is a sample artifact or genuine.

Harmonia sessionC (W1) flagged non-monotonicity at k=3 and k=4.

Observable: stable_faltings_height (invariant under isogeny, monotonically
related to the Arakelov-theoretic canonical height / period).
Also runs faltings_height and szpiro_ratio as cross-checks.

No L-value (leading_term) available in ec_curvedata -- that lives in
lfunc_lfunctions (342GB table). Faltings height is the best available proxy.
"""

import sys
import time
import numpy as np
import psycopg2

# ── Config ──────────────────────────────────────────────────────────────────
N_BOOTSTRAP = 1000
CI_LEVEL = 0.95
K_VALUES = [1, 2, 3, 4]
SEED = 42

DB_PARAMS = dict(host='localhost', port=5432, dbname='lmfdb',
                 user='lmfdb', password='lmfdb')


def load_rank0_data():
    """Load rank-0 EC curves: conductor, stable_faltings_height, faltings_height, szpiro_ratio."""
    print("Loading rank-0 curves from Postgres...")
    t0 = time.time()
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("""
        SELECT conductor::bigint,
               stable_faltings_height::double precision,
               faltings_height::double precision,
               szpiro_ratio::double precision
        FROM ec_curvedata
        WHERE rank = '0'
          AND stable_faltings_height IS NOT NULL
          AND conductor IS NOT NULL
          AND szpiro_ratio IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()
    dt = time.time() - t0
    print(f"  Loaded {len(rows):,} curves in {dt:.1f}s")

    conductors = np.array([r[0] for r in rows], dtype=np.float64)
    stable_fh = np.array([r[1] for r in rows], dtype=np.float64)
    fh = np.array([r[2] for r in rows], dtype=np.float64)
    szpiro = np.array([r[3] for r in rows], dtype=np.float64)

    return conductors, stable_fh, fh, szpiro


def make_bins(conductors):
    """Bin by conductor decade (log10 bins)."""
    log10_N = np.log10(conductors)
    lo = int(np.floor(log10_N.min()))
    hi = int(np.ceil(log10_N.max()))
    edges = np.arange(lo, hi + 1)
    bin_idx = np.digitize(log10_N, edges) - 1
    # Clamp to valid range
    bin_idx = np.clip(bin_idx, 0, len(edges) - 2)
    return edges, bin_idx


def compute_Rk(obs, conductors, k):
    """Compute R_k = mean(obs^k) / (log(median_conductor))^{k(k-1)/2}."""
    if len(obs) == 0:
        return np.nan
    Mk = np.mean(obs ** k)
    exponent = k * (k - 1) / 2.0
    med_N = np.median(conductors)
    if med_N <= 1:
        return np.nan
    denom = (np.log(med_N)) ** exponent
    if denom == 0:
        return Mk  # k=1 case: exponent=0, denom=1
    return Mk / denom


def bootstrap_Rk(obs, conductors, k, rng, n_boot=N_BOOTSTRAP):
    """Bootstrap R_k: resample within bin, return array of R_k values."""
    n = len(obs)
    results = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        results[i] = compute_Rk(obs[idx], conductors[idx], k)
    return results


def run_analysis(conductors, observable, obs_name):
    """Full analysis for one observable."""
    print(f"\n{'='*80}")
    print(f"  Observable: {obs_name}")
    print(f"{'='*80}")

    # Use absolute value for observables that can be negative (faltings heights)
    # Moment ratios require positive values
    if np.any(observable < 0):
        print(f"  Note: {np.sum(observable < 0):,} negative values -- using |obs| for moments")
        observable = np.abs(observable)

    # Filter zeros/NaN
    valid = np.isfinite(observable) & (observable > 0)
    obs = observable[valid]
    cond = conductors[valid]
    print(f"  Using {len(obs):,} curves (after filtering)")

    edges, bin_idx = make_bins(cond)
    n_bins = len(edges) - 1

    rng = np.random.default_rng(SEED)

    # Storage: [bin, k] -> (Rk, ci_lo, ci_hi, n_samples)
    results = {}

    alpha = (1 - CI_LEVEL) / 2

    for b in range(n_bins):
        mask = bin_idx == b
        n_in_bin = mask.sum()
        if n_in_bin < 30:
            continue

        obs_bin = obs[mask]
        cond_bin = cond[mask]
        lo_decade = edges[b]
        hi_decade = edges[b + 1]
        med_cond = np.median(cond_bin)

        for k in K_VALUES:
            rk_point = compute_Rk(obs_bin, cond_bin, k)
            boot = bootstrap_Rk(obs_bin, cond_bin, k, rng)
            ci_lo = np.percentile(boot, 100 * alpha)
            ci_hi = np.percentile(boot, 100 * (1 - alpha))
            results[(b, k)] = {
                'Rk': rk_point,
                'ci_lo': ci_lo,
                'ci_hi': ci_hi,
                'n': n_in_bin,
                'decade_lo': lo_decade,
                'decade_hi': hi_decade,
                'med_cond': med_cond,
            }

    # ── Print results table ─────────────────────────────────────────────
    bins_present = sorted(set(b for (b, _) in results))

    for k in K_VALUES:
        exponent = k * (k - 1) / 2
        print(f"\n  k={k}  (KS exponent = {exponent})")
        print(f"  {'Decade':>12s}  {'N':>8s}  {'med(N)':>12s}  {'R_k':>12s}  {'95% CI lo':>12s}  {'95% CI hi':>12s}  {'Overlap?':>10s}")
        print(f"  {'-'*12}  {'-'*8}  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*10}")

        prev_ci = None
        for b in bins_present:
            if (b, k) not in results:
                continue
            r = results[(b, k)]
            # Check overlap with previous bin's CI
            overlap_str = ""
            if prev_ci is not None:
                overlaps = r['ci_lo'] <= prev_ci[1] and r['ci_hi'] >= prev_ci[0]
                overlap_str = "YES" if overlaps else "NO"
            prev_ci = (r['ci_lo'], r['ci_hi'])

            decade_label = f"10^{r['decade_lo']}-10^{r['decade_hi']}"
            print(f"  {decade_label:>12s}  {r['n']:>8,d}  {r['med_cond']:>12.0f}  "
                  f"{r['Rk']:>12.6f}  {r['ci_lo']:>12.6f}  {r['ci_hi']:>12.6f}  {overlap_str:>10s}")

    # ── Monotonicity verdict ────────────────────────────────────────────
    print(f"\n  Monotonicity verdict per k:")
    for k in [3, 4]:
        exponent = k * (k - 1) / 2
        rk_series = []
        for b in bins_present:
            if (b, k) in results:
                r = results[(b, k)]
                rk_series.append((r['decade_lo'], r['Rk'], r['ci_lo'], r['ci_hi']))

        if len(rk_series) < 2:
            print(f"    k={k}: insufficient bins")
            continue

        # Check if any consecutive pair has non-overlapping CIs with reversed direction
        non_monotonic_real = False
        non_monotonic_locations = []
        for i in range(len(rk_series) - 1):
            d0, rk0, lo0, hi0 = rk_series[i]
            d1, rk1, lo1, hi1 = rk_series[i + 1]
            # Direction reversal
            if i > 0:
                _, rk_prev, _, _ = rk_series[i - 1]
                going_up = rk0 > rk_prev
                going_down_now = rk1 < rk0
                if going_up and going_down_now:
                    # Non-monotonic: does CI confirm?
                    overlaps = lo1 <= hi0 and hi1 >= lo0
                    if not overlaps:
                        non_monotonic_real = True
                        non_monotonic_locations.append(f"10^{d0}-10^{d1}")
                elif not going_up and not going_down_now:
                    overlaps = lo1 <= hi0 and hi1 >= lo0
                    if not overlaps:
                        non_monotonic_real = True
                        non_monotonic_locations.append(f"10^{d0}-10^{d1}")

        # Simpler check: any reversal at all?
        directions = []
        for i in range(len(rk_series) - 1):
            directions.append(rk_series[i + 1][1] - rk_series[i][1])
        sign_changes = sum(1 for i in range(len(directions) - 1)
                           if directions[i] * directions[i + 1] < 0)

        # For each sign change, check if CIs separate
        separated_reversals = 0
        for i in range(len(directions) - 1):
            if directions[i] * directions[i + 1] < 0:
                # Reversal at bin i+1
                b_peak = i + 1
                r_before = rk_series[b_peak]
                r_after = rk_series[b_peak + 1]
                overlaps = r_after[2] <= r_before[3] and r_after[3] >= r_before[2]
                if not overlaps:
                    separated_reversals += 1

        if sign_changes == 0:
            print(f"    k={k}: MONOTONIC (no sign changes detected)")
        elif separated_reversals == 0:
            print(f"    k={k}: {sign_changes} sign change(s) BUT all CIs overlap -> SAMPLE ARTIFACT")
        else:
            print(f"    k={k}: {separated_reversals}/{sign_changes} reversal(s) with non-overlapping CIs -> REAL DISCREPANCY")
            for loc in non_monotonic_locations:
                print(f"           at {loc}")

    return results


def main():
    conductors, stable_fh, fh, szpiro = load_rank0_data()

    # Primary analysis: stable Faltings height
    run_analysis(conductors, stable_fh, "stable_faltings_height (|·|)")

    # Cross-checks
    run_analysis(conductors, fh, "faltings_height (|·|)")
    run_analysis(conductors, szpiro, "szpiro_ratio")

    # ── Final summary ───────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print("  SUMMARY")
    print(f"{'='*80}")
    print("""
  L-value (leading_term) is not in ec_curvedata -- lives in lfunc_lfunctions
  (342GB table). Used three proxy observables instead:
    1. stable_faltings_height: isogeny-invariant, best L-value proxy
    2. faltings_height: model-dependent variant
    3. szpiro_ratio: discriminant/conductor ratio

  If ALL three show consistent non-monotonicity with separated CIs,
  the signal is robust and likely a genuine CFKRS discrepancy.
  If only one shows it, it may be an observable-specific artifact.
  If none show it, the original finding was likely a sample size artifact
  (or it requires actual L-values to detect).
""")


if __name__ == '__main__':
    main()
