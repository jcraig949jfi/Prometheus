"""
tamagawa_mediation.py — Test whether the Tamagawa product mediates
the isogeny class size effect on zero-gap variance.

Hypothesis (P1): Larger isogeny classes → more bad primes → larger
Tamagawa product → larger L(1,E) via BSD → stronger zero repulsion
→ lower gap variance.  If true, controlling for num_bad_primes
(Tamagawa proxy) should eliminate the class_size effect.

LMFDB ec_curvedata has no direct tamagawa_product column, so we use
num_bad_primes as a proxy (each bad prime contributes c_p >= 1 to the
Tamagawa product; more bad primes → larger product on average).
"""

import psycopg2
import numpy as np
import json
from collections import defaultdict
from scipy import stats

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')

# ── helpers ───────────────────────────────────────────────────────────────

def parse_zeros(z_str):
    if not z_str or z_str == '[]':
        return None
    try:
        zeros = json.loads(z_str)
        if len(zeros) < 2:
            return None
        return np.array(zeros, dtype=np.float64)
    except Exception:
        return None


def gap1_normed(zeros, conductor):
    """Return gap1 normalised by mean spacing ~ pi / log(N/2pi)."""
    spacing = np.pi / np.log(max(conductor, 3) / (2 * np.pi)) if conductor > 2 * np.pi else 1.0
    return zeros[0] / spacing


def var_over_gaudin(g1_normed_arr):
    """Variance of normalised gap1 divided by GUE/Gaudin prediction (0.178)."""
    if len(g1_normed_arr) < 10:
        return np.nan, len(g1_normed_arr)
    return float(np.var(g1_normed_arr) / 0.178), len(g1_normed_arr)


def partial_spearman(x, y, z):
    """Spearman partial correlation of x,y controlling for z.
    Uses rank-transform then standard partial-correlation formula."""
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    rz = stats.rankdata(z)
    # residualise
    def resid(a, b):
        slope, intercept = np.polyfit(b, a, 1)
        return a - (slope * b + intercept)
    rx_z = resid(rx, rz)
    ry_z = resid(ry, rz)
    r, p = stats.pearsonr(rx_z, ry_z)
    return r, p


# ══════════════════════════════════════════════════════════════════════════
# STEP 1: Does class_size correlate with num_bad_primes?
# ══════════════════════════════════════════════════════════════════════════

def step1_class_size_vs_bad_primes():
    print("=" * 72)
    print("STEP 1: Does class_size correlate with num_bad_primes? (rank-0)")
    print("=" * 72)

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT class_size::int, num_bad_primes::int, COUNT(*),
               AVG(conductor::float), AVG(sha::float), AVG(regulator::float)
        FROM ec_curvedata
        WHERE rank::int = 0 AND class_size::int >= 1
        GROUP BY class_size::int, num_bad_primes::int
        ORDER BY class_size::int, num_bad_primes::int
    """)
    rows = cur.fetchall()
    conn.close()

    print(f"\n{'cls_sz':>6} {'nbp':>4} {'count':>10} {'avg_cond':>14} {'avg_sha':>8} {'avg_reg':>10}")
    print("-" * 56)
    for r in rows:
        print(f"{r[0]:>6} {r[1]:>4} {r[2]:>10} {r[3]:>14.1f} {r[4]:>8.2f} {r[5]:>10.6f}")

    # Marginal: mean num_bad_primes by class_size
    cs_nbp = defaultdict(lambda: {'total': 0, 'weighted_nbp': 0})
    for cs, nbp, cnt, *_ in rows:
        cs_nbp[cs]['total'] += cnt
        cs_nbp[cs]['weighted_nbp'] += nbp * cnt

    print("\n--- Mean num_bad_primes by class_size ---")
    for cs in sorted(cs_nbp):
        mean_nbp = cs_nbp[cs]['weighted_nbp'] / cs_nbp[cs]['total']
        print(f"  class_size={cs:>2}: mean(num_bad_primes) = {mean_nbp:.3f}  (N={cs_nbp[cs]['total']})")

    return rows


# ══════════════════════════════════════════════════════════════════════════
# STEP 2: Fetch zeros + compute gap variance by (class_size, nbp_bin)
# ══════════════════════════════════════════════════════════════════════════

def step2_gap_variance_by_cell():
    print("\n" + "=" * 72)
    print("STEP 2: Gap variance by (class_size, num_bad_primes) cells")
    print("=" * 72)

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT e.class_size::int, e.num_bad_primes::int, e.sha::int,
               l.positive_zeros, e.conductor::float,
               e.stable_faltings_height::float
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/'
                        || split_part(e.lmfdb_iso, '.', 1)
                        || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
          AND e.iso_nlabel::int = 0
        LIMIT 200000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Fetched {len(rows)} rank-0 curves (iso_nlabel=0)")

    # Parse zeros, compute normalised gap1
    data = []  # (class_size, nbp, sha, gap1_normed, conductor, faltings_height)
    for cs, nbp, sha, z_str, cond, fh in rows:
        zeros = parse_zeros(z_str)
        if zeros is None:
            continue
        g1n = gap1_normed(zeros, cond)
        data.append((cs, nbp, sha, g1n, cond, fh))

    print(f"  Parsed {len(data)} curves with valid zeros")

    # ── 2a: Marginal variance by class_size (replicate baseline) ──
    print("\n--- 2a: Marginal var/Gaudin by class_size ---")
    by_cs = defaultdict(list)
    for cs, nbp, sha, g1n, cond, fh in data:
        by_cs[cs].append(g1n)

    cs_var = {}
    for cs in sorted(by_cs):
        vg, n = var_over_gaudin(np.array(by_cs[cs]))
        cs_var[cs] = (vg, n)
        print(f"  class_size={cs:>2}: var/Gaudin = {vg:.4f}  (n={n})")

    # ── 2b: Marginal variance by num_bad_primes ──
    print("\n--- 2b: Marginal var/Gaudin by num_bad_primes ---")
    by_nbp = defaultdict(list)
    for cs, nbp, sha, g1n, cond, fh in data:
        by_nbp[nbp].append(g1n)

    for nbp in sorted(by_nbp):
        vg, n = var_over_gaudin(np.array(by_nbp[nbp]))
        if n >= 20:
            print(f"  num_bad_primes={nbp}: var/Gaudin = {vg:.4f}  (n={n})")

    # ── 2c: Variance within (class_size, nbp_bin) cells ──
    # Bin nbp: 1, 2, 3, 4+
    def nbp_bin(n):
        return min(n, 4)

    print("\n--- 2c: var/Gaudin by (class_size, nbp_bin) ---")
    cells = defaultdict(list)
    for cs, nbp, sha, g1n, cond, fh in data:
        cells[(cs, nbp_bin(nbp))].append(g1n)

    print(f"{'cls_sz':>6} {'nbp_bin':>7} {'N':>8} {'var/Gaudin':>12}")
    print("-" * 36)
    for key in sorted(cells.keys()):
        cs, nb = key
        vg, n = var_over_gaudin(np.array(cells[key]))
        if n >= 20:
            print(f"{cs:>6} {nb:>7} {n:>8} {vg:>12.4f}")

    # ── 2d: CRITICAL TEST — within fixed nbp_bin, does class_size still predict variance? ──
    print("\n--- 2d: CRITICAL — class_size effect WITHIN fixed nbp_bin ---")
    for nb in sorted(set(nbp_bin(d[1]) for d in data)):
        vals = {}
        for cs in sorted(set(d[0] for d in data)):
            arr = np.array([d[3] for d in data if d[0] == cs and nbp_bin(d[1]) == nb])
            if len(arr) >= 20:
                vg, n = var_over_gaudin(arr)
                vals[cs] = (vg, n)
        if len(vals) >= 2:
            parts = ', '.join(f"cs={cs}: {vg:.3f}(n={n})" for cs, (vg, n) in sorted(vals.items()))
            print(f"  nbp_bin={nb}: {parts}")

    return data


# ══════════════════════════════════════════════════════════════════════════
# STEP 3: Partial Spearman correlation
# ══════════════════════════════════════════════════════════════════════════

def step3_partial_correlation(data):
    print("\n" + "=" * 72)
    print("STEP 3: Partial Spearman correlation analysis")
    print("=" * 72)

    cs_arr = np.array([d[0] for d in data], dtype=float)
    nbp_arr = np.array([d[1] for d in data], dtype=float)
    g1n_arr = np.array([d[3] for d in data], dtype=float)

    # Raw correlations (individual-level)
    r_cs_g1, p_cs_g1 = stats.spearmanr(cs_arr, g1n_arr)
    r_nbp_g1, p_nbp_g1 = stats.spearmanr(nbp_arr, g1n_arr)
    r_cs_nbp, p_cs_nbp = stats.spearmanr(cs_arr, nbp_arr)

    print(f"\n  Raw Spearman correlations (individual-level, N={len(data)}):")
    print(f"    r(class_size, gap1_normed) = {r_cs_g1:.4f}  p = {p_cs_g1:.2e}")
    print(f"    r(num_bad_primes, gap1_normed) = {r_nbp_g1:.4f}  p = {p_nbp_g1:.2e}")
    print(f"    r(class_size, num_bad_primes) = {r_cs_nbp:.4f}  p = {p_cs_nbp:.2e}")

    # Partial: class_size → gap1, controlling num_bad_primes
    r_partial_cs, p_partial_cs = partial_spearman(cs_arr, g1n_arr, nbp_arr)
    print(f"\n  Partial Spearman r(class_size, gap1 | num_bad_primes):")
    print(f"    r_partial = {r_partial_cs:.4f}  p = {p_partial_cs:.2e}")

    # Partial: num_bad_primes → gap1, controlling class_size
    r_partial_nbp, p_partial_nbp = partial_spearman(nbp_arr, g1n_arr, cs_arr)
    print(f"\n  Partial Spearman r(num_bad_primes, gap1 | class_size):")
    print(f"    r_partial = {r_partial_nbp:.4f}  p = {p_partial_nbp:.2e}")

    # ── Group-level: compute variance per (cs, nbp_bin) then correlate ──
    print("\n  --- Group-level partial correlation (variance per cell) ---")

    def nbp_bin(n):
        return min(n, 4)

    cells = defaultdict(list)
    for cs, nbp, sha, g1n, cond, fh in data:
        cells[(cs, nbp_bin(nbp))].append(g1n)

    cell_cs, cell_nbp, cell_var = [], [], []
    for (cs, nb), vals in cells.items():
        vg, n = var_over_gaudin(np.array(vals))
        if n >= 30:
            cell_cs.append(cs)
            cell_nbp.append(nb)
            cell_var.append(vg)

    cell_cs = np.array(cell_cs, dtype=float)
    cell_nbp = np.array(cell_nbp, dtype=float)
    cell_var = np.array(cell_var, dtype=float)

    if len(cell_cs) >= 5:
        r_raw, p_raw = stats.spearmanr(cell_cs, cell_var)
        print(f"    Raw r(class_size, var/Gaudin) = {r_raw:.4f}  p = {p_raw:.3f}  (N_cells={len(cell_cs)})")

        r_part, p_part = partial_spearman(cell_cs, cell_var, cell_nbp)
        print(f"    Partial r(class_size, var/Gaudin | nbp_bin) = {r_part:.4f}  p = {p_part:.3f}")

        r_nbp_raw, p_nbp_raw = stats.spearmanr(cell_nbp, cell_var)
        print(f"    Raw r(nbp_bin, var/Gaudin) = {r_nbp_raw:.4f}  p = {p_nbp_raw:.3f}")

    # Interpretation
    print("\n  INTERPRETATION:")
    drop = abs(r_cs_g1) - abs(r_partial_cs)
    pct_drop = drop / abs(r_cs_g1) * 100 if abs(r_cs_g1) > 1e-6 else 0
    print(f"    Individual-level: |r| dropped from {abs(r_cs_g1):.4f} to {abs(r_partial_cs):.4f}")
    print(f"    That is a {pct_drop:.1f}% reduction when controlling for num_bad_primes.")
    if pct_drop > 50:
        print("    → num_bad_primes (Tamagawa proxy) SUBSTANTIALLY mediates the effect.")
    elif pct_drop > 20:
        print("    → num_bad_primes PARTIALLY mediates the effect (some independent signal remains).")
    else:
        print("    → num_bad_primes does NOT mediate the effect — class_size acts independently.")

    return r_cs_g1, r_partial_cs, r_cs_nbp


# ══════════════════════════════════════════════════════════════════════════
# STEP 4: Faltings height vs class_size (period channel)
# ══════════════════════════════════════════════════════════════════════════

def step4_faltings_height(data):
    print("\n" + "=" * 72)
    print("STEP 4: Does stable_faltings_height vary with class_size?")
    print("       (If so, the real period Omega also varies → L-value channel)")
    print("=" * 72)

    # Filter to those with faltings height
    fh_data = [(cs, fh) for cs, nbp, sha, g1n, cond, fh in data if fh is not None]
    if not fh_data:
        print("  No faltings height data available.")
        return

    by_cs = defaultdict(list)
    for cs, fh in fh_data:
        by_cs[cs].append(fh)

    print(f"\n{'cls_sz':>6} {'N':>8} {'mean_fh':>10} {'std_fh':>10} {'median_fh':>10}")
    print("-" * 48)
    for cs in sorted(by_cs):
        arr = np.array(by_cs[cs])
        if len(arr) >= 10:
            print(f"{cs:>6} {len(arr):>8} {arr.mean():>10.4f} {arr.std():>10.4f} {np.median(arr):>10.4f}")

    # Spearman correlation
    cs_vals = np.array([d[0] for d in fh_data], dtype=float)
    fh_vals = np.array([d[1] for d in fh_data], dtype=float)
    mask = np.isfinite(fh_vals)
    r, p = stats.spearmanr(cs_vals[mask], fh_vals[mask])
    print(f"\n  Spearman r(class_size, faltings_height) = {r:.4f}  p = {p:.2e}  (N={mask.sum()})")

    if abs(r) > 0.05 and p < 0.01:
        print("  → Faltings height varies with class_size → period contributes to L-value channel.")
    else:
        print("  → Faltings height does NOT meaningfully vary with class_size.")


# ══════════════════════════════════════════════════════════════════════════
# STEP 5: Conductor-controlled check (conductor confound)
# ══════════════════════════════════════════════════════════════════════════

def step5_conductor_control(data):
    print("\n" + "=" * 72)
    print("STEP 5: Conductor-controlled check")
    print("       (conductor correlates with both num_bad_primes and gap1)")
    print("=" * 72)

    cs_arr = np.array([d[0] for d in data], dtype=float)
    nbp_arr = np.array([d[1] for d in data], dtype=float)
    g1n_arr = np.array([d[3] for d in data], dtype=float)
    cond_arr = np.array([d[4] for d in data], dtype=float)

    # Triple partial: class_size → gap1, controlling for BOTH nbp and conductor
    # Residualise each variable against both confounders
    def resid_2(target, c1, c2):
        X = np.column_stack([c1, c2])
        beta = np.linalg.lstsq(X, target, rcond=None)[0]
        return target - X @ beta

    rx = stats.rankdata(cs_arr)
    ry = stats.rankdata(g1n_arr)
    rz1 = stats.rankdata(nbp_arr)
    rz2 = stats.rankdata(cond_arr)

    rx_res = resid_2(rx, rz1, rz2)
    ry_res = resid_2(ry, rz1, rz2)

    r_double, p_double = stats.pearsonr(rx_res, ry_res)
    print(f"\n  Partial Spearman r(class_size, gap1 | nbp, conductor) = {r_double:.4f}  p = {p_double:.2e}")

    # Also partial: nbp → gap1 controlling for class_size + conductor
    rnbp_res = resid_2(rz1, rx, rz2)
    ry_res2 = resid_2(ry, rx, rz2)
    r_nbp_double, p_nbp_double = stats.pearsonr(rnbp_res, ry_res2)
    print(f"  Partial Spearman r(nbp, gap1 | class_size, conductor) = {r_nbp_double:.4f}  p = {p_nbp_double:.2e}")

    return r_double, p_double


# ══════════════════════════════════════════════════════════════════════════
# STEP 6: Verdict
# ══════════════════════════════════════════════════════════════════════════

def verdict(r_raw, r_partial, r_cs_nbp, r_double, p_double):
    print("\n" + "=" * 72)
    print("VERDICT on P1: Does Tamagawa product mediate class_size → variance?")
    print("=" * 72)

    pct_drop_single = (abs(r_raw) - abs(r_partial)) / abs(r_raw) * 100 if abs(r_raw) > 1e-6 else 0
    pct_drop_double = (abs(r_raw) - abs(r_double)) / abs(r_raw) * 100 if abs(r_raw) > 1e-6 else 0

    print(f"""
  Raw r(class_size, gap1)                = {r_raw:.4f}
  r(class_size, num_bad_primes)          = {r_cs_nbp:.4f}
  Partial r (controlling nbp)            = {r_partial:.4f}  ({pct_drop_single:.1f}% reduction)
  Partial r (controlling nbp + cond)     = {r_double:.4f}  ({pct_drop_double:.1f}% reduction, p={p_double:.2e})
""")

    if pct_drop_single > 50:
        print("  P1 SUPPORTED: num_bad_primes (Tamagawa proxy) substantially mediates")
        print("  the class_size → gap variance link. The BSD channel (more bad primes →")
        print("  larger Tamagawa product → larger L(1,E) → stronger zero repulsion)")
        print("  accounts for most of the effect.")
    elif pct_drop_single > 20:
        print("  P1 PARTIALLY SUPPORTED: num_bad_primes mediates part of the effect,")
        print("  but class_size retains an independent structural contribution.")
        print("  The BSD channel is active but does not fully explain the pattern.")
    else:
        print("  P1 REJECTED: Controlling for num_bad_primes does NOT reduce the")
        print("  class_size effect. The two channels (isogeny structure vs Tamagawa/BSD)")
        print("  appear to act independently.")

    if abs(r_double) > 0.01 and p_double < 0.01:
        print(f"\n  After controlling for BOTH nbp and conductor, class_size still has")
        print(f"  r={r_double:.4f} (p={p_double:.2e}) — residual structural effect survives.")
    else:
        print(f"\n  After controlling for both nbp and conductor, class_size effect")
        print(f"  is eliminated (r={r_double:.4f}, p={p_double:.2e}).")


# ══════════════════════════════════════════════════════════════════════════
# main
# ══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Tamagawa Mediation Analysis (Q1 + P1)")
    print("Does num_bad_primes (Tamagawa proxy) mediate class_size -> gap variance?")
    print()

    step1_class_size_vs_bad_primes()
    data = step2_gap_variance_by_cell()
    r_raw, r_partial, r_cs_nbp = step3_partial_correlation(data)
    step4_faltings_height(data)
    r_double, p_double = step5_conductor_control(data)
    verdict(r_raw, r_partial, r_cs_nbp, r_double, p_double)
