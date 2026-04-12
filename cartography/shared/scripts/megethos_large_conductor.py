"""
Megethos Large-Conductor Test — Does b/a converge to e² at scale?

Queries the LMFDB PostgreSQL mirror for elliptic curve data at much larger
conductor ranges than our local DuckDB (which caps ~5000). Tests whether
the Bathos sigmoid's midpoint b/a converges to e² = 7.389... as more
data is included.

Usage:
    python megethos_large_conductor.py
"""
import sys
sys.set_int_max_str_digits(100000)

import json
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

E_SQUARED = np.e ** 2  # 7.38905609893...


def get_connection():
    import psycopg2
    return psycopg2.connect(
        host='devmirror.lmfdb.xyz',
        port=5432,
        dbname='lmfdb',
        user='lmfdb',
        password='lmfdb',
        connect_timeout=30,
    )


def sigmoid(x, a, b):
    return 1 / (1 + np.exp(-(a * x - b)))


def fit_sigmoid_on_range(conductors, ranks, max_cond=None, label=""):
    """Bin by ln(conductor), compute P(rank>=1), fit sigmoid."""
    if max_cond is not None:
        mask = conductors <= max_cond
        cond = conductors[mask]
        rnk = ranks[mask]
    else:
        cond = conductors
        rnk = ranks

    if len(cond) < 100:
        return None

    M = np.log(cond.astype(float))
    high_rank = (rnk >= 1).astype(float)

    # Adaptive binning: aim for ~20 curves per bin minimum
    n_bins = min(80, max(15, len(cond) // 50))
    M_sorted = np.sort(M)
    lo = np.percentile(M, 2)
    hi = np.percentile(M, 98)
    edges = np.linspace(lo, hi, n_bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    probs = []
    counts = []
    for i in range(n_bins):
        bin_mask = (M >= edges[i]) & (M < edges[i + 1])
        n = bin_mask.sum()
        if n >= 10:
            probs.append(high_rank[bin_mask].mean())
            counts.append(n)
        else:
            probs.append(np.nan)
            counts.append(0)

    valid = ~np.isnan(probs)
    M_fit = centers[valid]
    P_fit = np.array(probs)[valid]

    if len(M_fit) < 5:
        return None

    try:
        popt, pcov = curve_fit(sigmoid, M_fit, P_fit, p0=[0.3, 2.0], maxfev=50000)
    except RuntimeError:
        return None

    a, b = popt
    perr = np.sqrt(np.diag(pcov))

    P_pred = sigmoid(M_fit, a, b)
    ss_res = np.sum((P_fit - P_pred) ** 2)
    ss_tot = np.sum((P_fit - P_fit.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    ratio = b / a
    diff_pct = abs(ratio - E_SQUARED) / E_SQUARED * 100

    result = {
        "label": label,
        "max_conductor": int(max_cond) if max_cond else int(cond.max()),
        "n_curves": int(len(cond)),
        "a": float(a),
        "a_err": float(perr[0]),
        "b": float(b),
        "b_err": float(perr[1]),
        "r2": float(r2),
        "b_over_a": float(ratio),
        "e_squared": float(E_SQUARED),
        "pct_diff_from_e2": float(diff_pct),
        "n_bins_used": int(valid.sum()),
    }

    tag = f"  [{label}]" if label else ""
    print(f"{tag} N={len(cond):>8d}, max_cond={int(cond.max()):>12,d}")
    print(f"       a={a:.6f}±{perr[0]:.6f}, b={b:.6f}±{perr[1]:.6f}, R²={r2:.4f}")
    print(f"       b/a = {ratio:.6f}  (e² = {E_SQUARED:.6f}, diff = {diff_pct:.2f}%)")

    return result


def main():
    print("=" * 70)
    print("MEGETHOS LARGE-CONDUCTOR TEST")
    print(f"Target: does b/a converge to e² = {E_SQUARED:.6f}?")
    print("=" * 70)

    # ── Step 1: Probe the database ──────────────────────────────────
    print("\nConnecting to LMFDB PostgreSQL mirror...")
    conn = get_connection()
    cur = conn.cursor()

    # Check conductor range
    print("Checking conductor range...")
    cur.execute("SELECT MIN(conductor), MAX(conductor), COUNT(*) FROM ec_curvedata")
    cmin, cmax, ctotal = cur.fetchone()
    print(f"  Conductor range: [{cmin:,d}, {cmax:,d}]")
    print(f"  Total curves: {ctotal:,d}")

    # Check column names to be safe
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'ec_curvedata'
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cur.fetchall()]
    print(f"  Columns (first 20): {cols[:20]}")

    # Check rank availability
    cur.execute("""
        SELECT COUNT(*) FROM ec_curvedata
        WHERE rank IS NOT NULL AND conductor IS NOT NULL
    """)
    n_with_rank = cur.fetchone()[0]
    print(f"  Curves with rank: {n_with_rank:,d}")

    # Distribution by conductor magnitude
    print("\n  Conductor distribution:")
    for exp in [3, 4, 5, 6, 7, 8]:
        lo_val = 10 ** (exp - 1) if exp > 1 else 1
        hi_val = 10 ** exp
        cur.execute(
            "SELECT COUNT(*) FROM ec_curvedata WHERE conductor >= %s AND conductor < %s",
            (lo_val, hi_val)
        )
        n = cur.fetchone()[0]
        print(f"    [{lo_val:>12,d}, {hi_val:>12,d}): {n:>10,d} curves")

    # ── Step 2: Fetch data in batches ───────────────────────────────
    print("\nFetching EC data from LMFDB...")

    # Strategy: sample across conductor ranges to get ~100K total
    # Use TABLESAMPLE or LIMIT with ORDER BY for efficiency
    ranges = [
        (1,         1_000,     30_000, "cond<1K"),
        (1_000,     5_000,     20_000, "1K-5K"),
        (5_000,     10_000,    15_000, "5K-10K"),
        (10_000,    50_000,    15_000, "10K-50K"),
        (50_000,    100_000,   10_000, "50K-100K"),
        (100_000,   500_000,   10_000, "100K-500K"),
        (500_000,   1_000_000, 5_000,  "500K-1M"),
        (1_000_000, 10_000_000, 5_000, "1M-10M"),
    ]

    all_conductors = []
    all_ranks = []
    all_torsion = []

    for lo, hi, limit, tag in ranges:
        print(f"  Fetching {tag} (limit {limit:,d})...", end=" ", flush=True)
        cur.execute("""
            SELECT conductor, rank, analytic_rank, torsion
            FROM ec_curvedata
            WHERE conductor >= %s AND conductor < %s
              AND rank IS NOT NULL
            ORDER BY conductor
            LIMIT %s
        """, (lo, hi, limit))
        rows = cur.fetchall()
        print(f"got {len(rows):,d} rows")

        for cond, rank, arank, torsion in rows:
            all_conductors.append(int(cond))
            all_ranks.append(int(rank) if rank is not None else 0)
            all_torsion.append(int(torsion) if torsion is not None else 1)

    conn.close()

    conductors = np.array(all_conductors, dtype=np.float64)
    ranks = np.array(all_ranks, dtype=np.int32)
    torsion = np.array(all_torsion, dtype=np.int32)

    print(f"\nTotal fetched: {len(conductors):,d} curves")
    print(f"  Conductor range: [{conductors.min():.0f}, {conductors.max():.0f}]")
    print(f"  Rank distribution: {dict(zip(*np.unique(ranks, return_counts=True)))}")

    # ── Step 3: Convergence test ────────────────────────────────────
    print("\n" + "=" * 70)
    print("CONVERGENCE TEST: b/a vs max_conductor")
    print("=" * 70)

    thresholds = [1_000, 5_000, 10_000, 50_000, 100_000,
                  500_000, 1_000_000, 5_000_000, 10_000_000]

    convergence_results = []
    for thresh in thresholds:
        n_avail = (conductors <= thresh).sum()
        if n_avail < 200:
            continue
        res = fit_sigmoid_on_range(
            conductors, ranks,
            max_cond=thresh,
            label=f"cond<{thresh:,d}"
        )
        if res is not None:
            convergence_results.append(res)

    # Full dataset
    print("\n--- Full dataset ---")
    full_res = fit_sigmoid_on_range(conductors, ranks, label="FULL")

    # ── Step 4: Summary ─────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("CONVERGENCE SUMMARY")
    print("=" * 70)
    print(f"{'Max Conductor':>15s}  {'N':>8s}  {'b/a':>10s}  {'e²':>10s}  {'diff%':>8s}  {'R²':>6s}")
    print("-" * 65)
    for r in convergence_results:
        print(f"{r['max_conductor']:>15,d}  {r['n_curves']:>8,d}  "
              f"{r['b_over_a']:>10.6f}  {E_SQUARED:>10.6f}  "
              f"{r['pct_diff_from_e2']:>7.2f}%  {r['r2']:>6.4f}")

    if convergence_results:
        final = convergence_results[-1]
        print(f"\nFinal b/a = {final['b_over_a']:.6f}")
        print(f"e²        = {E_SQUARED:.6f}")
        print(f"Difference: {final['pct_diff_from_e2']:.2f}%")

        if final['pct_diff_from_e2'] < 1.0:
            print("VERDICT: b/a is within 1% of e² — consistent with convergence")
        elif final['pct_diff_from_e2'] < 5.0:
            print("VERDICT: b/a is within 5% of e² — suggestive but not conclusive")
        else:
            print("VERDICT: b/a diverges from e² — constant identification likely wrong")

    # ── Step 5: Plot ────────────────────────────────────────────────
    if HAS_PLT and len(convergence_results) >= 3:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Panel 1: b/a convergence
        ax = axes[0]
        max_conds = [r['max_conductor'] for r in convergence_results]
        ratios = [r['b_over_a'] for r in convergence_results]
        ax.semilogx(max_conds, ratios, 'bo-', markersize=8, label='b/a (fitted)')
        ax.axhline(E_SQUARED, color='r', linestyle='--', linewidth=2,
                    label=f'e² = {E_SQUARED:.4f}')
        ax.set_xlabel('Max conductor included')
        ax.set_ylabel('b/a (sigmoid midpoint in M-space)')
        ax.set_title('Convergence of b/a to e²')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Panel 2: Sigmoid fit on full data
        ax = axes[1]
        M_all = np.log(conductors)
        B_all = (ranks >= 1).astype(float)
        n_bins = 60
        lo = np.percentile(M_all, 2)
        hi = np.percentile(M_all, 98)
        edges = np.linspace(lo, hi, n_bins + 1)
        centers = (edges[:-1] + edges[1:]) / 2
        probs = []
        for i in range(n_bins):
            mask = (M_all >= edges[i]) & (M_all < edges[i + 1])
            if mask.sum() >= 10:
                probs.append(B_all[mask].mean())
            else:
                probs.append(np.nan)
        probs = np.array(probs)
        valid = ~np.isnan(probs)

        ax.plot(centers[valid], probs[valid], 'ko', markersize=4, alpha=0.6,
                label='Observed P(rank≥1)')
        if full_res:
            M_smooth = np.linspace(lo, hi, 200)
            ax.plot(M_smooth, sigmoid(M_smooth, full_res['a'], full_res['b']),
                    'r-', linewidth=2, label=f'Sigmoid fit (b/a={full_res["b_over_a"]:.3f})')
            ax.axvline(full_res['b_over_a'], color='blue', linestyle=':',
                       alpha=0.5, label=f'M₅₀ = {full_res["b_over_a"]:.2f}')
        ax.set_xlabel('M = ln(conductor)')
        ax.set_ylabel('P(rank ≥ 1)')
        ax.set_title('Bathos Sigmoid — Full LMFDB Sample')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_path = OUT_DIR / "megethos_large_conductor.png"
        plt.savefig(str(plot_path), dpi=150)
        print(f"\nPlot saved: {plot_path}")
        plt.close()

    # ── Step 6: Save JSON ───────────────────────────────────────────
    output = {
        "description": "Megethos large-conductor test: does b/a converge to e²?",
        "e_squared": float(E_SQUARED),
        "total_curves": int(len(conductors)),
        "conductor_range": [int(conductors.min()), int(conductors.max())],
        "rank_distribution": {str(k): int(v) for k, v in
                              zip(*np.unique(ranks, return_counts=True))},
        "convergence": convergence_results,
        "full_fit": full_res,
    }

    out_path = OUT_DIR / "megethos_large_conductor.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Results saved: {out_path}")


if __name__ == "__main__":
    main()
