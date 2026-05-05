#!/usr/bin/env python3
"""
Zero Projections at Full Scale — Replication + Compound Stratification + Null Model

Replicates the 50K subsample findings (isogeny class_size and Sha suppress gap variance)
at full scale (~500K EC L-functions), adds compound stratification (rank x CM x root_number),
permutation null model, and conductor control.

Gaudin prediction for GUE nearest-neighbor variance: var = 4 - pi ≈ 0.178
"""
import json
import sys
import time
import numpy as np
import psycopg2
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Gaudin nearest-neighbor variance for GUE
GAUDIN_VAR = 4.0 - np.pi  # ≈ 0.178

DB_PARAMS = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')


def parse_zeros(zeros_str):
    """Parse '[0.258, 1.196, ...]' -> numpy array of floats."""
    if not zeros_str or zeros_str == '[]':
        return None
    try:
        s = zeros_str.strip('[] \n')
        vals = [float(x) for x in s.split(',') if x.strip()]
        if len(vals) < 2:
            return None
        return np.array(vals, dtype=np.float64)
    except (ValueError, TypeError):
        return None


def compute_gap1_normalized(zeros):
    """Compute first gap normalized by per-curve mean gap.

    gap1 = z2 - z1
    mean_gap = mean of all consecutive gaps
    returns gap1 / mean_gap
    """
    if zeros is None or len(zeros) < 2:
        return None
    gaps = np.diff(zeros)
    if len(gaps) == 0:
        return None
    mean_gap = gaps.mean()
    if mean_gap <= 0:
        return None
    return gaps[0] / mean_gap


def variance_stats(gaps):
    """Compute variance and var/Gaudin from a list of normalized gap values."""
    if len(gaps) < 10:
        return None, None
    arr = np.array(gaps)
    var = float(np.var(arr, ddof=1))
    return var, var / GAUDIN_VAR


def print_table(title, rows, columns):
    """Print a formatted table."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

    # Header
    widths = [max(len(str(c)), max(len(str(r[i])) for r in rows)) for i, c in enumerate(columns)]
    widths = [max(w, 8) for w in widths]

    header = "  ".join(f"{c:>{w}}" for c, w in zip(columns, widths))
    print(f"  {header}")
    print(f"  {'  '.join('-'*w for w in widths)}")

    for row in rows:
        line = "  ".join(f"{str(v):>{w}}" for v, w in zip(row, widths))
        print(f"  {line}")


# =============================================================
# Data loading
# =============================================================

def load_projection_data(query, label="query", limit_display=True):
    """Execute query, parse zeros, compute normalized gap1. Returns list of dicts."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    print(f"\n  Executing {label}...")
    t0 = time.time()
    cur.execute(query)
    rows = cur.fetchall()
    elapsed = time.time() - t0
    print(f"  Fetched {len(rows):,} rows in {elapsed:.1f}s")
    conn.close()

    return rows


# =============================================================
# Projection #3: Isogeny class size
# =============================================================

def run_projection_3():
    print("\n" + "="*70)
    print("  PROJECTION #3: Isogeny Class Size (full scale)")
    print("="*70)

    query = """
    SELECT e.class_size::int, l.positive_zeros, e.conductor::float
    FROM ec_curvedata e
    JOIN lfunc_lfunctions l ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1) || '/' || split_part(e.lmfdb_iso, '.', 2)
    WHERE e.rank::int = 0 AND l.positive_zeros IS NOT NULL AND l.positive_zeros != '[]' AND e.class_size::int >= 1
    LIMIT 500000
    """

    rows = load_projection_data(query, "Projection #3 (class_size)")

    # Parse and compute
    by_class = defaultdict(list)
    conductors_by_class = defaultdict(list)
    all_gaps = []
    all_class_sizes = []
    all_conductors = []

    n_parsed = 0
    for class_size, zeros_str, conductor in rows:
        zeros = parse_zeros(zeros_str)
        g1 = compute_gap1_normalized(zeros)
        if g1 is not None:
            by_class[class_size].append(g1)
            conductors_by_class[class_size].append(conductor)
            all_gaps.append(g1)
            all_class_sizes.append(class_size)
            all_conductors.append(conductor)
            n_parsed += 1

    print(f"  Parsed {n_parsed:,} valid gap measurements")

    # Results table
    table_rows = []
    for cs in sorted(by_class.keys()):
        gaps = by_class[cs]
        var, vg = variance_stats(gaps)
        if var is not None:
            table_rows.append((cs, len(gaps), f"{var:.4f}", f"{vg:.3f}"))

    print_table("Projection #3: class_size -> gap1 variance",
                table_rows, ["class_size", "n", "var", "var/Gaudin"])

    return {
        "by_class": {str(k): {"n": len(v), "var": float(np.var(v, ddof=1)), "var_gaudin": float(np.var(v, ddof=1)/GAUDIN_VAR)}
                     for k, v in by_class.items() if len(v) >= 10},
        "total_parsed": n_parsed,
    }, np.array(all_gaps), np.array(all_class_sizes), np.array(all_conductors)


# =============================================================
# Projection #5: Sha order
# =============================================================

def run_projection_5():
    print("\n" + "="*70)
    print("  PROJECTION #5: Sha Order (full scale)")
    print("="*70)

    query = """
    SELECT e.sha::int, l.positive_zeros, e.conductor::float
    FROM ec_curvedata e
    JOIN lfunc_lfunctions l ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1) || '/' || split_part(e.lmfdb_iso, '.', 2)
    WHERE e.rank::int = 0 AND l.positive_zeros IS NOT NULL AND l.positive_zeros != '[]'
    LIMIT 500000
    """

    rows = load_projection_data(query, "Projection #5 (sha)")

    by_sha = defaultdict(list)
    n_parsed = 0
    for sha, zeros_str, conductor in rows:
        zeros = parse_zeros(zeros_str)
        g1 = compute_gap1_normalized(zeros)
        if g1 is not None:
            by_sha[sha].append(g1)
            n_parsed += 1

    print(f"  Parsed {n_parsed:,} valid gap measurements")

    # Only show sha values with enough data
    table_rows = []
    for sha in sorted(by_sha.keys()):
        gaps = by_sha[sha]
        if len(gaps) < 30:
            continue
        var, vg = variance_stats(gaps)
        if var is not None:
            table_rows.append((sha, len(gaps), f"{var:.4f}", f"{vg:.3f}"))

    print_table("Projection #5: sha -> gap1 variance",
                table_rows, ["sha", "n", "var", "var/Gaudin"])

    return {
        "by_sha": {str(k): {"n": len(v), "var": float(np.var(v, ddof=1)), "var_gaudin": float(np.var(v, ddof=1)/GAUDIN_VAR)}
                   for k, v in by_sha.items() if len(v) >= 30},
        "total_parsed": n_parsed,
    }


# =============================================================
# Projection #7: Compound (rank x CM x root_number)
# =============================================================

def run_projection_7():
    print("\n" + "="*70)
    print("  PROJECTION #7: Compound (rank x CM x signD)")
    print("="*70)

    query = """
    SELECT e.rank::int, e.cm::int, e."signD"::int, l.positive_zeros
    FROM ec_curvedata e
    JOIN lfunc_lfunctions l ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1) || '/' || split_part(e.lmfdb_iso, '.', 2)
    WHERE l.positive_zeros IS NOT NULL AND l.positive_zeros != '[]'
    LIMIT 500000
    """

    rows = load_projection_data(query, "Projection #7 (compound)")

    by_compound = defaultdict(list)
    n_parsed = 0
    for rank, cm, signD, zeros_str in rows:
        zeros = parse_zeros(zeros_str)
        g1 = compute_gap1_normalized(zeros)
        if g1 is not None:
            cm_flag = 1 if cm != 0 else 0
            key = (rank, cm_flag, signD)
            by_compound[key].append(g1)
            n_parsed += 1

    print(f"  Parsed {n_parsed:,} valid gap measurements")

    table_rows = []
    for key in sorted(by_compound.keys()):
        gaps = by_compound[key]
        if len(gaps) < 30:
            continue
        var, vg = variance_stats(gaps)
        if var is not None:
            rank, cm_flag, signD = key
            cm_label = "CM" if cm_flag else "non-CM"
            sign_label = f"w={'+1' if signD > 0 else '-1'}"
            table_rows.append((f"r={rank}", cm_label, sign_label, len(gaps), f"{var:.4f}", f"{vg:.3f}"))

    print_table("Projection #7: (rank, CM, signD) -> gap1 variance",
                table_rows, ["rank", "CM", "sign", "n", "var", "var/Gaudin"])

    return {
        "by_compound": {f"r{k[0]}_cm{k[1]}_s{k[2]}": {"n": len(v), "var": float(np.var(v, ddof=1)), "var_gaudin": float(np.var(v, ddof=1)/GAUDIN_VAR)}
                        for k, v in by_compound.items() if len(v) >= 30},
        "total_parsed": n_parsed,
    }


# =============================================================
# NULL MODEL: Permutation test for Projection #3
# =============================================================

def run_null_model(all_gaps, all_class_sizes, all_conductors, n_perms=200):
    print("\n" + "="*70)
    print("  NULL MODEL: Permutation test (class_size within conductor deciles)")
    print("="*70)

    # Assign conductor decile bins
    log_cond = np.log10(all_conductors + 1)
    deciles = np.digitize(log_cond, np.percentile(log_cond, np.arange(10, 100, 10)))

    unique_classes = sorted(set(all_class_sizes))

    # Observed: variance per class_size
    observed_vars = {}
    for cs in unique_classes:
        mask = all_class_sizes == cs
        if mask.sum() >= 10:
            observed_vars[cs] = float(np.var(all_gaps[mask], ddof=1))

    # Observed monotone slope (linear regression of var vs class_size)
    obs_cs = np.array(sorted(observed_vars.keys()))
    obs_v = np.array([observed_vars[c] for c in obs_cs])
    if len(obs_cs) >= 2:
        obs_slope = np.polyfit(obs_cs, obs_v, 1)[0]
    else:
        obs_slope = 0.0

    print(f"  Observed slope (var vs class_size): {obs_slope:.6f}")
    print(f"  Running {n_perms} permutations within conductor decile bins...")

    perm_slopes = []
    t0 = time.time()

    for i in range(n_perms):
        # Permute class_size labels within each conductor decile
        perm_cs = all_class_sizes.copy()
        for d in range(10):
            mask = deciles == d
            idx = np.where(mask)[0]
            np.random.shuffle(perm_cs[idx])

        # Compute variance per class_size under permutation
        perm_vars = {}
        for cs in unique_classes:
            mask = perm_cs == cs
            if mask.sum() >= 10:
                perm_vars[cs] = float(np.var(all_gaps[mask], ddof=1))

        p_cs = np.array(sorted(perm_vars.keys()))
        p_v = np.array([perm_vars[c] for c in p_cs])
        if len(p_cs) >= 2:
            perm_slopes.append(np.polyfit(p_cs, p_v, 1)[0])

    elapsed = time.time() - t0

    perm_slopes = np.array(perm_slopes)
    z_score = (obs_slope - perm_slopes.mean()) / (perm_slopes.std() + 1e-15)
    p_value = (np.sum(perm_slopes <= obs_slope) + 1) / (n_perms + 1)  # one-tailed: observed is negative

    print(f"  Permutation mean slope: {perm_slopes.mean():.6f} +/- {perm_slopes.std():.6f}")
    print(f"  Observed slope:         {obs_slope:.6f}")
    print(f"  z-score:                {z_score:.2f}")
    print(f"  p-value (one-tailed):   {p_value:.4f}")
    print(f"  ({n_perms} permutations in {elapsed:.1f}s)")

    if abs(z_score) > 3:
        verdict = "SIGNIFICANT: monotone trend survives conductor-controlled permutation"
    elif abs(z_score) > 2:
        verdict = "MARGINAL: trend partially survives permutation"
    else:
        verdict = "NOT SIGNIFICANT: trend may be conductor confound"

    print(f"  Verdict: {verdict}")

    return {
        "observed_slope": float(obs_slope),
        "perm_mean_slope": float(perm_slopes.mean()),
        "perm_std_slope": float(perm_slopes.std()),
        "z_score": float(z_score),
        "p_value": float(p_value),
        "n_perms": n_perms,
        "verdict": verdict,
    }


# =============================================================
# CONDUCTOR CONTROL: class_size=1 only, binned by conductor decade
# =============================================================

def run_conductor_control(all_gaps, all_class_sizes, all_conductors):
    print("\n" + "="*70)
    print("  CONDUCTOR CONTROL: class_size=1, binned by conductor decade")
    print("="*70)

    mask = all_class_sizes == 1
    gaps_cs1 = all_gaps[mask]
    cond_cs1 = all_conductors[mask]

    log_cond = np.log10(cond_cs1 + 1)

    # Bin by conductor decade
    decade_min = int(np.floor(log_cond.min()))
    decade_max = int(np.ceil(log_cond.max()))

    table_rows = []
    result = {}
    for d in range(decade_min, decade_max):
        dmask = (log_cond >= d) & (log_cond < d + 1)
        if dmask.sum() < 30:
            continue
        g = gaps_cs1[dmask]
        var = float(np.var(g, ddof=1))
        vg = var / GAUDIN_VAR
        cond_range = f"10^{d}-10^{d+1}"
        table_rows.append((cond_range, int(dmask.sum()), f"{var:.4f}", f"{vg:.3f}"))
        result[f"decade_{d}"] = {"n": int(dmask.sum()), "var": var, "var_gaudin": vg}

    print_table("Conductor control: class_size=1 only, gap1 variance by conductor decade",
                table_rows, ["conductor", "n", "var", "var/Gaudin"])

    # Check if variance decreases with conductor
    decades = sorted(result.keys())
    vars_by_decade = [result[d]["var"] for d in decades]
    if len(vars_by_decade) >= 2:
        slope = np.polyfit(range(len(vars_by_decade)), vars_by_decade, 1)[0]
        if abs(slope) < 0.005:
            verdict = "FLAT: class_size=1 variance does NOT depend on conductor — class_size effect is genuine"
        elif slope < 0:
            verdict = f"DECREASING (slope={slope:.4f}): conductor partially explains the effect"
        else:
            verdict = f"INCREASING (slope={slope:.4f}): opposite direction — class_size effect is genuine"
        print(f"\n  Variance slope across decades: {slope:.6f}")
        print(f"  Verdict: {verdict}")
        result["slope"] = float(slope)
        result["verdict"] = verdict

    return result


# =============================================================
# Main
# =============================================================

if __name__ == "__main__":
    print("="*70)
    print("  ZERO PROJECTIONS — Full Scale Replication")
    print(f"  {datetime.now().isoformat()}")
    print(f"  Gaudin variance (GUE): {GAUDIN_VAR:.4f}")
    print("="*70)

    results = {"timestamp": datetime.now().isoformat(), "gaudin_var": GAUDIN_VAR}

    # Projection #3: Isogeny class size
    t0 = time.time()
    p3_results, all_gaps, all_class_sizes, all_conductors = run_projection_3()
    results["projection_3_class_size"] = p3_results
    results["projection_3_time_s"] = time.time() - t0

    # Projection #5: Sha order
    t0 = time.time()
    p5_results = run_projection_5()
    results["projection_5_sha"] = p5_results
    results["projection_5_time_s"] = time.time() - t0

    # Projection #7: Compound
    t0 = time.time()
    p7_results = run_projection_7()
    results["projection_7_compound"] = p7_results
    results["projection_7_time_s"] = time.time() - t0

    # Null model
    t0 = time.time()
    null_results = run_null_model(all_gaps, all_class_sizes, all_conductors, n_perms=200)
    results["null_model"] = null_results
    results["null_model_time_s"] = time.time() - t0

    # Conductor control
    t0 = time.time()
    cond_results = run_conductor_control(all_gaps, all_class_sizes, all_conductors)
    results["conductor_control"] = cond_results
    results["conductor_control_time_s"] = time.time() - t0

    # Save
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "zero_projections_full.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Saved results to {out_path}")

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)

    # P3 summary
    p3 = results["projection_3_class_size"]["by_class"]
    cs_keys = sorted(p3.keys(), key=lambda x: int(x))
    if len(cs_keys) >= 2:
        first_vg = p3[cs_keys[0]]["var_gaudin"]
        last_vg = p3[cs_keys[-1]]["var_gaudin"]
        print(f"  P3 (class_size): {cs_keys[0]}→{cs_keys[-1]}: var/Gaudin {first_vg:.3f} → {last_vg:.3f}")

    # P5 summary
    p5 = results["projection_5_sha"]["by_sha"]
    sha_keys = sorted(p5.keys(), key=lambda x: int(x))
    if len(sha_keys) >= 2:
        first_vg = p5[sha_keys[0]]["var_gaudin"]
        last_key = [k for k in sha_keys if p5[k]["n"] >= 30][-1]
        last_vg = p5[last_key]["var_gaudin"]
        print(f"  P5 (sha): {sha_keys[0]}→{last_key}: var/Gaudin {first_vg:.3f} → {last_vg:.3f}")

    # Null model
    nm = results["null_model"]
    print(f"  Null model: z={nm['z_score']:.2f}, p={nm['p_value']:.4f}")
    print(f"    {nm['verdict']}")

    # Conductor control
    cc = results["conductor_control"]
    if "verdict" in cc:
        print(f"  Conductor control: {cc['verdict']}")

    print(f"\n  Total time: projection #3 {results['projection_3_time_s']:.0f}s, "
          f"#5 {results['projection_5_time_s']:.0f}s, "
          f"#7 {results['projection_7_time_s']:.0f}s, "
          f"null {results['null_model_time_s']:.0f}s")
