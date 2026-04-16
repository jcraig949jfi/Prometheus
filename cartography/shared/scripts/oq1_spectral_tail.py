"""
OQ1 Spectral Tail Test — Harmonia's pre-registered falsification.

Tests whether L-function zero spacings predict elliptic curve rank
beyond what conductor alone explains.

Pre-registered attacks:
1. Montgomery-Odlyzko calibration (GUE baseline)
2. Conductor-conditional null
3. Rank-stratified density check
4. Bootstrap stability (1000 samples)
5. Cross-family transport

Author: Harmonia (Cross-Domain Cartographer)
Date: 2026-04-15
"""
import sys
import io
import json
import os
import numpy as np
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import psycopg2

DB_HOST = '192.168.1.176'
DB_PORT = 5432
DB_NAME = 'lmfdb'
DB_USER = 'lmfdb'
DB_PASS = 'lmfdb'


def get_connection():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
                            user=DB_USER, password=DB_PASS)


def parse_zeros(zeros_str):
    """Parse positive_zeros from LMFDB text format to float array."""
    if not zeros_str or zeros_str in ('', '[]', 'None'):
        return None
    try:
        # LMFDB stores as comma-separated or JSON array
        if zeros_str.startswith('['):
            vals = json.loads(zeros_str)
        else:
            vals = [float(x.strip()) for x in zeros_str.split(',') if x.strip()]
        return np.array(vals, dtype=np.float64)
    except (json.JSONDecodeError, ValueError):
        return None


def compute_spacings(zeros):
    """Compute normalized spacings between consecutive zeros."""
    if zeros is None or len(zeros) < 2:
        return None
    sorted_z = np.sort(zeros)
    gaps = np.diff(sorted_z)
    # Normalize by mean spacing (local density)
    mean_gap = np.mean(gaps)
    if mean_gap < 1e-15:
        return None
    return gaps / mean_gap


def gue_nearest_neighbor_pdf(s, n_points=1000):
    """Wigner surmise approximation to GUE nearest-neighbor spacing."""
    return (32 / np.pi**2) * s**2 * np.exp(-4 * s**2 / np.pi)


def ks_test_gue(spacings):
    """KS test against Wigner surmise (GUE approximation)."""
    if spacings is None or len(spacings) < 10:
        return None, None
    from scipy import stats
    # CDF of Wigner surmise
    def gue_cdf(s):
        return 1 - np.exp(-4 * s**2 / np.pi)
    sorted_s = np.sort(spacings)
    n = len(sorted_s)
    ecdf = np.arange(1, n + 1) / n
    theoretical = gue_cdf(sorted_s)
    ks_stat = np.max(np.abs(ecdf - theoretical))
    # p-value approximation
    p_value = stats.kstwobign.sf(ks_stat * np.sqrt(n))
    return ks_stat, p_value


def pull_ec_zeros_sample(conn, conductor_min, conductor_max, limit=5000):
    """Pull EC L-function zeros in a conductor range."""
    cur = conn.cursor()
    # Join EC data with lfunc zeros via origin field
    query = """
    SELECT e.lmfdb_label, e.conductor::int, e.rank::int, e.analytic_rank::int,
           e.cm::int, l.positive_zeros, l.order_of_vanishing
    FROM ec_curvedata e
    JOIN lfunc_lfunctions l ON l.origin = 'EllipticCurve/Q/' || e.lmfdb_iso
    WHERE e.conductor::numeric >= %s AND e.conductor::numeric < %s
    AND l.positive_zeros IS NOT NULL AND l.positive_zeros != '' AND l.positive_zeros != '[]'
    LIMIT %s
    """
    cur.execute(query, (conductor_min, conductor_max, limit))
    rows = cur.fetchall()
    cur.close()
    return rows


def pull_ec_zeros_by_label(conn, limit=1000):
    """Pull EC L-function zeros — try direct label match first."""
    cur = conn.cursor()
    # Try using origin LIKE pattern
    query = """
    SELECT l.origin, l.conductor, l.positive_zeros, l.order_of_vanishing, l.root_number
    FROM lfunc_lfunctions l
    WHERE l.origin LIKE 'EllipticCurve/Q/%%'
    AND l.positive_zeros IS NOT NULL AND l.positive_zeros != '' AND l.positive_zeros != '[]'
    LIMIT %s
    """
    cur.execute(query, (limit,))
    rows = cur.fetchall()
    cur.close()
    return rows


def attack_1_montgomery_odlyzko(all_spacings):
    """Attack 1: Verify GUE baseline. If zeros don't match GUE, something is wrong."""
    print("\n=== ATTACK 1: Montgomery-Odlyzko GUE Calibration ===")
    if len(all_spacings) == 0:
        print("  NO DATA. Cannot run.")
        return None

    combined = np.concatenate(all_spacings)
    ks_stat, p_value = ks_test_gue(combined)
    print(f"  Combined spacings: {len(combined)}")
    print(f"  Mean spacing: {np.mean(combined):.4f} (should be ~1.0)")
    print(f"  Variance: {np.var(combined):.4f} (GUE Wigner: ~0.178)")
    print(f"  KS statistic vs Wigner surmise: {ks_stat:.6f}")
    print(f"  KS p-value: {p_value:.6e}")

    if p_value < 0.01:
        print("  RESULT: GUE DEVIATION DETECTED (p < 0.01). Baseline is NOT GUE.")
        print("  This means either: (a) zeros are improperly unfolded, or")
        print("  (b) there is genuine deviation. Must resolve before testing spectral tail.")
        return {"status": "GUE_DEVIATION", "ks": ks_stat, "p": p_value}
    else:
        print(f"  RESULT: GUE baseline CONFIRMED (p = {p_value:.4f})")
        return {"status": "GUE_CONFIRMED", "ks": ks_stat, "p": p_value}


def attack_2_conductor_conditional(data_by_rank, conductor_bins):
    """Attack 2: Does spectral tail survive after conditioning on conductor?"""
    print("\n=== ATTACK 2: Conductor-Conditional Null ===")
    # Within each conductor bin, compare spacing distributions across ranks
    from scipy import stats

    results = []
    for cond_min, cond_max in conductor_bins:
        bin_data = {}
        for rank, entries in data_by_rank.items():
            spacings = []
            for label, cond, zeros in entries:
                if cond_min <= cond < cond_max:
                    sp = compute_spacings(zeros)
                    if sp is not None:
                        spacings.extend(sp.tolist())
            if len(spacings) > 10:
                bin_data[rank] = np.array(spacings)

        if len(bin_data) >= 2:
            ranks_present = sorted(bin_data.keys())
            # KS test between rank-0 and rank-1 spacings within this conductor bin
            if 0 in bin_data and 1 in bin_data:
                ks, p = stats.ks_2samp(bin_data[0], bin_data[1])
                results.append({
                    "cond_range": f"{cond_min}-{cond_max}",
                    "n_rank0": len(bin_data[0]),
                    "n_rank1": len(bin_data[1]),
                    "ks": ks, "p": p
                })
                verdict = "DIFFERENT" if p < 0.01 else "SAME"
                print(f"  [{cond_min}-{cond_max}] rank0 n={len(bin_data[0])}, rank1 n={len(bin_data[1])}: KS={ks:.4f}, p={p:.4e} -> {verdict}")

    if not results:
        print("  NO DATA in conductor bins. Cannot run.")
        return None

    # If all bins show p > 0.01, the spectral tail is KILLED by conductor conditioning
    surviving = sum(1 for r in results if r["p"] < 0.01)
    total = len(results)
    print(f"\n  Bins with rank-dependent spacing (p<0.01): {surviving}/{total}")
    if surviving == 0:
        print("  KILL: Spectral tail does NOT survive conductor conditioning.")
        print("  The apparent rank-dependence was a conductor confound.")
        return {"status": "KILLED", "surviving_bins": 0, "total_bins": total}
    else:
        print(f"  SURVIVES: {surviving}/{total} conductor bins show rank-dependent spacing.")
        return {"status": "SURVIVES", "surviving_bins": surviving, "total_bins": total, "details": results}


def attack_3_rank_density(data_by_rank):
    """Attack 3: Are zeros simply denser for higher-rank curves?"""
    print("\n=== ATTACK 3: Rank-Stratified Density Check ===")
    for rank in sorted(data_by_rank.keys()):
        entries = data_by_rank[rank]
        n_zeros_list = [len(z) for _, _, z in entries if z is not None]
        if n_zeros_list:
            print(f"  Rank {rank}: {len(entries)} curves, mean zeros/curve={np.mean(n_zeros_list):.1f}, "
                  f"median={np.median(n_zeros_list):.0f}")

    # If higher-rank curves just have more zeros stored, the spacing difference
    # could be an artifact of LMFDB's computation depth, not mathematics
    rank0_nz = [len(z) for _, _, z in data_by_rank.get(0, []) if z is not None]
    rank1_nz = [len(z) for _, _, z in data_by_rank.get(1, []) if z is not None]
    if rank0_nz and rank1_nz:
        from scipy import stats
        t_stat, p_val = stats.ttest_ind(rank0_nz, rank1_nz)
        print(f"\n  Zero count difference (rank 0 vs 1): t={t_stat:.2f}, p={p_val:.4e}")
        if p_val < 0.01:
            print("  WARNING: Different number of stored zeros by rank.")
            print("  This is a tabulation artifact, not mathematics.")
            print("  Must normalize by stored zero count before comparing spacings.")
            return {"status": "TABULATION_BIAS", "t": t_stat, "p": p_val}
        else:
            print("  Zero counts similar across ranks. Good.")
            return {"status": "NO_BIAS", "t": t_stat, "p": p_val}
    print("  Insufficient data for comparison.")
    return None


def attack_4_bootstrap(data_by_rank, n_bootstrap=1000):
    """Attack 4: Bootstrap stability of the rank-spacing signal."""
    print(f"\n=== ATTACK 4: Bootstrap Stability ({n_bootstrap} samples) ===")
    from scipy import stats

    rank0_spacings = []
    rank1_spacings = []
    for label, cond, zeros in data_by_rank.get(0, []):
        sp = compute_spacings(zeros)
        if sp is not None:
            rank0_spacings.append(sp)
    for label, cond, zeros in data_by_rank.get(1, []):
        sp = compute_spacings(zeros)
        if sp is not None:
            rank1_spacings.append(sp)

    if len(rank0_spacings) < 10 or len(rank1_spacings) < 10:
        print("  Insufficient data for bootstrap.")
        return None

    # Original effect: difference in mean spacing variance
    orig_var0 = np.var(np.concatenate(rank0_spacings))
    orig_var1 = np.var(np.concatenate(rank1_spacings))
    orig_effect = orig_var1 - orig_var0

    # Bootstrap
    bootstrap_effects = []
    rng = np.random.default_rng(42)
    for _ in range(n_bootstrap):
        boot0 = [rank0_spacings[i] for i in rng.integers(0, len(rank0_spacings), len(rank0_spacings))]
        boot1 = [rank1_spacings[i] for i in rng.integers(0, len(rank1_spacings), len(rank1_spacings))]
        v0 = np.var(np.concatenate(boot0))
        v1 = np.var(np.concatenate(boot1))
        bootstrap_effects.append(v1 - v0)

    bootstrap_effects = np.array(bootstrap_effects)
    ci_lo, ci_hi = np.percentile(bootstrap_effects, [2.5, 97.5])
    p_zero = np.mean(bootstrap_effects < 0) if orig_effect > 0 else np.mean(bootstrap_effects > 0)

    print(f"  Original effect (var_rank1 - var_rank0): {orig_effect:.6f}")
    print(f"  Bootstrap 95% CI: [{ci_lo:.6f}, {ci_hi:.6f}]")
    print(f"  P(effect crosses zero): {p_zero:.4f}")

    if ci_lo > 0 or ci_hi < 0:
        print(f"  SURVIVES: CI does not cross zero. Effect is stable.")
        return {"status": "SURVIVES", "effect": orig_effect, "ci": [ci_lo, ci_hi]}
    else:
        print(f"  KILLED: CI crosses zero. Effect is NOT stable.")
        return {"status": "KILLED", "effect": orig_effect, "ci": [ci_lo, ci_hi]}


def attack_5_permutation_null(data_by_rank, n_perms=500):
    """Attack 5: Permutation test — shuffle rank labels, measure effect."""
    print(f"\n=== ATTACK 5: Permutation Null ({n_perms} permutations) ===")
    from scipy import stats

    all_entries = []
    for rank, entries in data_by_rank.items():
        for label, cond, zeros in entries:
            sp = compute_spacings(zeros)
            if sp is not None:
                all_entries.append((rank, np.var(sp)))

    if len(all_entries) < 20:
        print("  Insufficient data.")
        return None

    ranks = np.array([e[0] for e in all_entries])
    vars_ = np.array([e[1] for e in all_entries])

    # Real effect: correlation between rank and spacing variance
    real_corr, _ = stats.spearmanr(ranks, vars_)
    print(f"  Real Spearman rho(rank, spacing_variance): {real_corr:.6f}")

    # Permutation null
    rng = np.random.default_rng(42)
    null_corrs = []
    for _ in range(n_perms):
        perm_ranks = rng.permutation(ranks)
        corr, _ = stats.spearmanr(perm_ranks, vars_)
        null_corrs.append(corr)

    null_corrs = np.array(null_corrs)
    z_score = (real_corr - np.mean(null_corrs)) / (np.std(null_corrs) + 1e-15)
    p_value = np.mean(np.abs(null_corrs) >= np.abs(real_corr))

    print(f"  Null mean: {np.mean(null_corrs):.6f}, std: {np.std(null_corrs):.6f}")
    print(f"  Z-score: {z_score:.2f}")
    print(f"  Permutation p-value: {p_value:.4f}")

    if p_value < 0.01:
        print(f"  SURVIVES: Real correlation is outside permutation null (p={p_value:.4f})")
        return {"status": "SURVIVES", "rho": real_corr, "z": z_score, "p": p_value}
    else:
        print(f"  KILLED: Real correlation is within permutation null (p={p_value:.4f})")
        return {"status": "KILLED", "rho": real_corr, "z": z_score, "p": p_value}


def main():
    print("=" * 70)
    print("OQ1 SPECTRAL TAIL TEST — Harmonia Pre-Registered Falsification")
    print("=" * 70)
    print()

    conn = get_connection()

    # Step 1: Pull EC L-function zero data
    print("Pulling EC L-function zeros from Postgres...")
    print("(This may take a while on the 341GB table)")

    # Try small sample first to understand data format
    rows = pull_ec_zeros_by_label(conn, limit=100)
    print(f"  Got {len(rows)} EC L-function records with zeros")

    if len(rows) == 0:
        print("NO EC L-FUNCTION ZEROS FOUND. Test cannot proceed.")
        print("Possible causes:")
        print("  1. Origin field format mismatch")
        print("  2. No zeros stored for EC L-functions")
        print("  3. positive_zeros column is empty for EC records")
        conn.close()
        return

    # Parse and examine first record
    origin, cond, zeros_str, ov, rn = rows[0]
    print(f"  Sample: origin={origin}, cond={cond}, order={ov}, root_number={rn}")
    print(f"  Zeros (first 200): {str(zeros_str)[:200]}")

    zeros = parse_zeros(str(zeros_str))
    if zeros is not None:
        print(f"  Parsed {len(zeros)} zeros. First 5: {zeros[:5]}")
    else:
        print("  FAILED TO PARSE ZEROS. Checking format...")
        print(f"  Raw type: {type(zeros_str)}, repr: {repr(str(zeros_str)[:300])}")
        conn.close()
        return

    # Step 2: Pull larger sample — need to join with EC for rank info
    print("\nPulling joined EC + lfunc data...")

    # Build conductor bins (log-spaced, 6 bins as per Kairos design)
    conductor_bins = [
        (1, 1000),
        (1000, 10000),
        (10000, 50000),
        (50000, 200000),
        (200000, 500000),
        (500000, 10000000),
    ]

    data_by_rank = defaultdict(list)
    all_spacings = []
    total_pulled = 0

    for cond_min, cond_max in conductor_bins:
        print(f"  Pulling conductor [{cond_min}, {cond_max})...", end=" ", flush=True)
        rows = pull_ec_zeros_sample(conn, cond_min, cond_max, limit=2000)
        print(f"got {len(rows)} rows")
        total_pulled += len(rows)

        for label, cond, rank, analytic_rank, cm, zeros_str, ov in rows:
            zeros = parse_zeros(str(zeros_str))
            if zeros is not None and len(zeros) >= 5:
                data_by_rank[rank].append((label, cond, zeros))
                sp = compute_spacings(zeros)
                if sp is not None:
                    all_spacings.append(sp)

    print(f"\nTotal pulled: {total_pulled}")
    print(f"Parsed with >= 5 zeros: {sum(len(v) for v in data_by_rank.values())}")
    for rank in sorted(data_by_rank.keys()):
        print(f"  Rank {rank}: {len(data_by_rank[rank])} curves")

    if total_pulled == 0 or len(all_spacings) == 0:
        print("\nNO USABLE DATA. Test cannot proceed.")
        conn.close()
        return

    # Run all 5 attacks
    results = {}

    results["attack_1"] = attack_1_montgomery_odlyzko(all_spacings)
    results["attack_2"] = attack_2_conductor_conditional(data_by_rank, conductor_bins)
    results["attack_3"] = attack_3_rank_density(data_by_rank)
    results["attack_4"] = attack_4_bootstrap(data_by_rank)
    results["attack_5"] = attack_5_permutation_null(data_by_rank)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    kills = 0
    survives = 0
    for name, result in results.items():
        if result is None:
            status = "NO_DATA"
        else:
            status = result.get("status", "UNKNOWN")
        if "KILL" in status:
            kills += 1
        elif "SURVIV" in status:
            survives += 1
        print(f"  {name}: {status}")

    print(f"\n  KILLS: {kills}  SURVIVES: {survives}  NO_DATA: {5 - kills - survives}")

    if kills > 0:
        print(f"\n  VERDICT: SPECTRAL TAIL IS {'WEAKENED' if survives > 0 else 'KILLED'}")
        print(f"  {kills} attack(s) succeeded. The signal {'partially' if survives > 0 else 'fully'} collapses under proper controls.")
    elif survives == 5:
        print(f"\n  VERDICT: SPECTRAL TAIL SURVIVES ALL 5 ATTACKS")
        print("  This is genuine structure. Promote from POSSIBLE to PROBABLE.")
    else:
        print(f"\n  VERDICT: INCONCLUSIVE ({survives} survive, {5 - kills - survives} no data)")

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'oq1_spectral_tail_results.json')
    with open(output_path, 'w') as f:
        json.dump({
            "test": "OQ1_spectral_tail",
            "date": "2026-04-15",
            "author": "Harmonia",
            "total_curves": total_pulled,
            "by_rank": {str(k): len(v) for k, v in data_by_rank.items()},
            "results": {k: v for k, v in results.items() if v is not None},
            "kills": kills,
            "survives": survives,
        }, f, indent=2, default=str)
    print(f"\n  Results saved to {output_path}")

    conn.close()


if __name__ == "__main__":
    main()
