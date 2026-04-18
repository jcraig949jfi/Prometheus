"""
convergence_by_class_size.py — Q5 + P5: Is the isogeny effect on gap variance
a finite-conductor transient or structural?

Test: Does var/Gaudin converge to 1.0 for ALL isogeny class sizes as conductor
increases (just at different rates)? Or does it stay stratified even at high N?

Method:
  - Bin by (class_size, conductor_decade)
  - Compute var/Gaudin in each bin
  - Fit var/Gaudin = A + B / log(N)^alpha per class_size
  - If A ≈ 1.0 for all: finite-conductor transient (Katz-Sarnak wins)
  - If A differs by class_size: structural violation
  - If A < 1.0 for some: super-regular (convergence overshoots)
"""

import psycopg2
import numpy as np
import json
from collections import defaultdict
from scipy.optimize import curve_fit

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def parse_zeros(z_str):
    """Parse positive_zeros string into float array."""
    if not z_str or z_str == '[]':
        return None
    try:
        zeros = json.loads(z_str)
        if len(zeros) < 2:
            return None
        return np.array(zeros, dtype=np.float64)
    except Exception:
        return None


def conductor_bin_label(log_cond):
    """Assign conductor decade bin."""
    if log_cond < 3:
        return '<3'
    elif log_cond < 4:
        return '3-4'
    elif log_cond < 5:
        return '4-5'
    elif log_cond < 6:
        return '5-6'
    else:
        return '6+'


GAUDIN_VAR = 0.178  # Gaudin variance for GUE gap1


def compute_var_gaudin(gap1_values, conductors):
    """Compute var(gap1/mean_spacing) / Gaudin for a set of curves."""
    normed = []
    for g1, N in zip(gap1_values, conductors):
        spacing = np.pi / np.log(max(N, 3) / (2 * np.pi)) if N > 2 * np.pi else 1.0
        normed.append(g1 / spacing)
    normed = np.array(normed)
    if len(normed) < 10:
        return np.nan, len(normed)
    return np.var(normed) / GAUDIN_VAR, len(normed)


# ---------------------------------------------------------------------------
# convergence model: var/Gaudin = A + B / log(N)^alpha
# ---------------------------------------------------------------------------

def convergence_model(log_N, A, B, alpha):
    return A + B / log_N**alpha


def fit_convergence(bin_centers, var_gaudin_values, weights=None):
    """Fit var/Gaudin = A + B / log(N)^alpha.
    bin_centers: log10(conductor) midpoints
    var_gaudin_values: measured var/Gaudin
    Returns (A, B, alpha) or None on failure.
    """
    # Convert log10(conductor) to log(conductor) = ln(10) * log10(N)
    log_N = np.log(10) * np.array(bin_centers)
    y = np.array(var_gaudin_values)

    mask = np.isfinite(y) & np.isfinite(log_N) & (log_N > 0)
    log_N = log_N[mask]
    y = y[mask]

    if len(y) < 3:
        return None

    try:
        # Initial guess: A=1.0 (Katz-Sarnak), B=1.0, alpha=1.0
        popt, pcov = curve_fit(convergence_model, log_N, y,
                               p0=[1.0, 1.0, 1.0],
                               bounds=([0.0, -10, 0.01], [3.0, 50, 5.0]),
                               maxfev=10000)
        perr = np.sqrt(np.diag(pcov))
        return popt, perr
    except Exception as e:
        print(f"    Fit failed: {e}")
        return None


# ---------------------------------------------------------------------------
# main analysis
# ---------------------------------------------------------------------------

def main():
    print("=" * 75)
    print("Q5 + P5: Isogeny class_size effect — transient or structural?")
    print("=" * 75)

    # --- Step 1: Query ---
    print("\n[1] Querying database...")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT e.class_size::int, e.conductor::float, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                        || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
          AND e.class_size::int IN (1, 2, 4)
          AND e.iso_nlabel::int = 0
        LIMIT 300000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Fetched {len(rows)} rank-0 curves (iso_nlabel=0, class_size in {{1,2,4}})")

    # --- Step 2: Parse zeros and compute gap1 ---
    print("\n[2] Parsing zeros and computing gap1...")
    # data[class_size][conductor_bin] = {'gap1': [], 'cond': []}
    data = defaultdict(lambda: defaultdict(lambda: {'gap1': [], 'cond': []}))
    parsed = 0
    for cs, cond, z_str in rows:
        zeros = parse_zeros(z_str)
        if zeros is None:
            continue
        gap1 = zeros[0]  # first zero = gap from origin
        log_cond = np.log10(max(cond, 1))
        blab = conductor_bin_label(log_cond)
        data[cs][blab]['gap1'].append(gap1)
        data[cs][blab]['cond'].append(cond)
        parsed += 1

    print(f"  Parsed {parsed} curves with valid zeros")

    # --- Step 3: Compute var/Gaudin table ---
    print("\n[3] var/Gaudin by (class_size, conductor_decade)")
    bins_ordered = ['<3', '3-4', '4-5', '5-6', '6+']
    bin_midpoints = {'<3': 2.0, '3-4': 3.5, '4-5': 4.5, '5-6': 5.5, '6+': 6.5}
    class_sizes = sorted(data.keys())

    # Header
    header = f"{'cond_bin':>10}"
    for cs in class_sizes:
        header += f"  cs={cs:>2} (N)"
    print(f"\n{header}")
    print("-" * (10 + 18 * len(class_sizes)))

    # Store results for fitting
    results = defaultdict(lambda: {'centers': [], 'vg': [], 'n': []})

    for blab in bins_ordered:
        row = f"{blab:>10}"
        for cs in class_sizes:
            if blab in data[cs] and len(data[cs][blab]['gap1']) >= 10:
                g1s = data[cs][blab]['gap1']
                conds = data[cs][blab]['cond']
                vg, n = compute_var_gaudin(g1s, conds)
                row += f"  {vg:>6.3f} ({n:>5})"
                results[cs]['centers'].append(bin_midpoints[blab])
                results[cs]['vg'].append(vg)
                results[cs]['n'].append(n)
            else:
                n = len(data[cs][blab]['gap1']) if blab in data[cs] else 0
                row += f"  {'---':>6} ({n:>5})"
        print(row)

    # --- Step 4: Fit convergence model ---
    print("\n" + "=" * 75)
    print("[4] Convergence fits: var/Gaudin = A + B / ln(N)^alpha")
    print("=" * 75)

    fit_results = {}
    for cs in class_sizes:
        centers = np.array(results[cs]['centers'])
        vg = np.array(results[cs]['vg'])
        ns = np.array(results[cs]['n'])

        print(f"\n  class_size = {cs}:")
        print(f"    Data points: {len(centers)}")
        for c, v, n in zip(centers, vg, ns):
            print(f"      log10(N)={c:.1f}: var/Gaudin={v:.4f} (n={n})")

        result = fit_convergence(centers, vg)
        if result is not None:
            (A, B, alpha), (A_err, B_err, alpha_err) = result
            print(f"    Fit: A = {A:.4f} +/- {A_err:.4f}")
            print(f"         B = {B:.4f} +/- {B_err:.4f}")
            print(f"         alpha = {alpha:.4f} +/- {alpha_err:.4f}")
            fit_results[cs] = {'A': A, 'B': B, 'alpha': alpha,
                               'A_err': A_err, 'B_err': B_err, 'alpha_err': alpha_err}
        else:
            print(f"    Fit FAILED (not enough data or poor convergence)")

    # --- Step 5: Verdict ---
    print("\n" + "=" * 75)
    print("[5] VERDICT ON Q5: Transient vs Structural?")
    print("=" * 75)

    if not fit_results:
        print("\n  INCONCLUSIVE: Could not fit convergence model.")
        return

    # Check if A values cluster near 1.0
    A_values = {cs: r['A'] for cs, r in fit_results.items()}
    A_errors = {cs: r['A_err'] for cs, r in fit_results.items()}

    print(f"\n  Asymptotic values (A = var/Gaudin as N → ∞):")
    for cs in sorted(A_values):
        A = A_values[cs]
        err = A_errors[cs]
        verdict = ""
        if abs(A - 1.0) < 2 * err:
            verdict = "CONSISTENT with 1.0 (Katz-Sarnak)"
        elif A < 1.0:
            verdict = "BELOW 1.0 (super-regular)"
        else:
            verdict = "ABOVE 1.0 (excess variance)"
        print(f"    class_size={cs}: A = {A:.4f} +/- {err:.4f}  → {verdict}")

    # Check stratification
    if len(A_values) >= 2:
        A_list = list(A_values.values())
        A_spread = max(A_list) - min(A_list)
        max_err = max(A_errors.values())

        print(f"\n  Spread in A values: {A_spread:.4f}")
        print(f"  Max fitting error:  {max_err:.4f}")

        if A_spread < 2 * max_err:
            print("\n  → VERDICT: Differences are WITHIN fitting error.")
            print("    Consistent with finite-conductor transient (Katz-Sarnak).")
            print("    All class sizes appear to converge to the same asymptote.")
        else:
            print(f"\n  → VERDICT: Spread ({A_spread:.4f}) EXCEEDS 2x fitting error ({2*max_err:.4f}).")
            print("    Evidence for STRUCTURAL stratification by class_size.")
            print("    The isogeny effect persists even at high conductor.")

    # Convergence rates
    print(f"\n  Convergence rates (alpha):")
    for cs in sorted(fit_results):
        r = fit_results[cs]
        print(f"    class_size={cs}: alpha = {r['alpha']:.3f} +/- {r['alpha_err']:.3f}")

    # Raw trend check (model-free)
    print("\n" + "=" * 75)
    print("[6] Model-free trend check")
    print("=" * 75)
    print("\n  var/Gaudin at lowest vs highest conductor bin by class_size:")
    for cs in class_sizes:
        vg_list = results[cs]['vg']
        centers = results[cs]['centers']
        if len(vg_list) >= 2:
            direction = "DECREASING" if vg_list[-1] < vg_list[0] else "INCREASING"
            delta = vg_list[-1] - vg_list[0]
            print(f"    class_size={cs}: {vg_list[0]:.4f} → {vg_list[-1]:.4f} "
                  f"(Δ={delta:+.4f}, {direction})")

    # Gap between class sizes at highest conductor bin
    highest_bin_vg = {}
    for cs in class_sizes:
        if results[cs]['vg']:
            highest_bin_vg[cs] = results[cs]['vg'][-1]

    if len(highest_bin_vg) >= 2:
        print(f"\n  At highest conductor bin, class_size gap:")
        cs_list = sorted(highest_bin_vg.keys())
        for i in range(len(cs_list)):
            for j in range(i+1, len(cs_list)):
                cs_i, cs_j = cs_list[i], cs_list[j]
                delta = highest_bin_vg[cs_j] - highest_bin_vg[cs_i]
                print(f"    cs={cs_j} - cs={cs_i} = {delta:+.4f}")

    print("\n" + "=" * 75)
    print("DONE")
    print("=" * 75)


if __name__ == '__main__':
    main()
