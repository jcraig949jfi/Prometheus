#!/usr/bin/env python3
"""
spectral_tail_isogeny.py -- Test whether low-lying L-function zero density
predicts isogeny class geometry.

Bridges the analytic side (zeros) to the algebraic side (isogeny classes)
without using a_p.

Metrics extracted per curve:
  - first_zero_height: imaginary part of the lowest-lying zero
  - micro_spacing_mean: mean gap between the first few zeros
  - spectral_tail_density: fraction of first 5 zeros below threshold 5.0

Isogeny targets:
  - class_size: number of curves in the isogeny class
  - class_deg: degree of the isogeny class
  - max_isogeny_deg: max degree from isogeny_degrees array

Tests:
  - Spearman correlations (raw + within-conductor-bin)
  - F33 ordinal artifact check
  - F34 trivial baseline (conductor alone)
  - Permutation null (1000 shuffles)
  - Stratification by rank and root_number

Kill prediction: conductor explains everything; zeros add nothing beyond
what conductor already determines about isogeny class structure.
"""

import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# 1. Load data from DuckDB
# ---------------------------------------------------------------------------

def load_data():
    import duckdb
    db_path = Path(__file__).resolve().parents[3] / "charon" / "data" / "charon.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)
    rows = con.execute("""
        SELECT e.lmfdb_label, e.conductor, e.rank, e.analytic_rank,
               e.class_size, e.class_deg, e.isogeny_degrees,
               o.zeros_vector, o.root_number, o.n_zeros_stored
        FROM elliptic_curves e
        JOIN object_zeros o ON e.object_id = o.object_id
        WHERE o.zeros_vector IS NOT NULL
          AND e.isogeny_degrees IS NOT NULL
          AND e.class_size IS NOT NULL
          AND e.class_deg IS NOT NULL
    """).fetchall()
    con.close()

    data = []
    for (label, cond, rank, arank, csz, cdeg, isodeg,
         zeros, root_num, n_zeros) in rows:
        if zeros is None or len(zeros) < 3:
            continue
        # First n_zeros_stored entries are actual zeros; trailing entries are metadata
        # Filter out sentinel values (e.g. -1.0 for central zero in rank>=1)
        nz = int(n_zeros) if n_zeros is not None else len(zeros)
        actual_zeros = [float(z) for z in zeros[:nz] if z is not None and z > 0]
        if len(actual_zeros) < 3:
            continue
        data.append({
            "label": label,
            "conductor": int(cond),
            "rank": int(rank) if rank is not None else None,
            "analytic_rank": int(arank) if arank is not None else None,
            "class_size": int(csz),
            "class_deg": int(cdeg),
            "isogeny_degrees": [int(d) for d in isodeg] if isodeg else [],
            "zeros": actual_zeros,
            "root_number": float(root_num) if root_num is not None else None,
            "n_zeros": nz,
        })
    return data


# ---------------------------------------------------------------------------
# 2. Feature extraction from zeros
# ---------------------------------------------------------------------------

def extract_features(rec):
    """Extract spectral features from low-lying zeros."""
    zeros = sorted(rec["zeros"])  # ensure ascending
    first_k = zeros[:5]

    first_zero = first_k[0]
    gaps = [first_k[i+1] - first_k[i] for i in range(len(first_k) - 1)]
    micro_spacing_mean = float(np.mean(gaps)) if gaps else 0.0

    # Spectral tail density: fraction of first 5 zeros below 5.0
    below = sum(1 for z in first_k if z < 5.0)
    tail_density = below / len(first_k)

    max_iso = max(rec["isogeny_degrees"]) if rec["isogeny_degrees"] else 1

    return {
        "first_zero": first_zero,
        "micro_spacing_mean": micro_spacing_mean,
        "tail_density": tail_density,
        "log_conductor": float(np.log(rec["conductor"])) if rec["conductor"] > 0 else 0.0,
        "class_size": rec["class_size"],
        "class_deg": rec["class_deg"],
        "max_iso_deg": max_iso,
        "rank": rec["rank"],
        "root_number": rec["root_number"],
    }


# ---------------------------------------------------------------------------
# 3. Statistical tests
# ---------------------------------------------------------------------------

def spearman_safe(x, y):
    """Spearman rho with NaN handling."""
    mask = np.isfinite(x) & np.isfinite(y)
    if np.sum(mask) < 10:
        return float("nan"), 1.0
    rho, p = stats.spearmanr(x[mask], y[mask])
    return float(rho), float(p)


def within_conductor_correlation(log_cond, metric, target, n_bins=10):
    """Spearman rho within conductor bins (equal-frequency)."""
    try:
        bins = np.quantile(log_cond, np.linspace(0, 1, n_bins + 1))
        bin_idx = np.digitize(log_cond, bins[1:-1])
    except Exception:
        return {"median_rho": None, "n_bins": 0, "rhos": []}

    rhos = []
    for b in np.unique(bin_idx):
        mask = bin_idx == b
        if np.sum(mask) < 20:
            continue
        t_sub = target[mask]
        m_sub = metric[mask]
        if len(np.unique(t_sub)) < 2 or len(np.unique(m_sub)) < 2:
            continue
        rho, _ = stats.spearmanr(m_sub, t_sub)
        if not np.isnan(rho):
            rhos.append(float(rho))

    return {
        "median_rho": float(np.median(rhos)) if rhos else None,
        "n_bins": len(rhos),
        "rhos": [round(r, 4) for r in rhos],
    }


def partial_correlation_conductor(metric, target, log_cond):
    """Partial Spearman: residualize both metric and target against log_cond."""
    mask = np.isfinite(metric) & np.isfinite(target) & np.isfinite(log_cond)
    if np.sum(mask) < 30:
        return {"partial_rho": None, "p_value": None}

    m, t, c = metric[mask], target[mask], log_cond[mask]
    # Rank-transform then residualize
    rm = stats.rankdata(m)
    rt = stats.rankdata(t)
    rc = stats.rankdata(c)

    # Residuals from linear regression on conductor rank
    from numpy.polynomial.polynomial import polyfit
    coef_m = np.polyfit(rc, rm, 1)
    res_m = rm - np.polyval(coef_m, rc)
    coef_t = np.polyfit(rc, rt, 1)
    res_t = rt - np.polyval(coef_t, rc)

    rho, p = stats.spearmanr(res_m, res_t)
    return {"partial_rho": float(rho), "p_value": float(p)}


def f33_ordinal_check(metric, target):
    """F33: sort both independently; if rho ~ real rho, it's ordinal artifact."""
    real_rho, _ = spearman_safe(metric, target)
    sorted_rho, _ = spearman_safe(np.sort(metric), np.sort(target))
    return {
        "real_rho": round(real_rho, 6),
        "sorted_rho": round(sorted_rho, 6),
        "ordinal_artifact": bool(abs(sorted_rho - real_rho) < 0.05),
    }


def f34_trivial_baseline(log_cond, target):
    """F34: conductor alone predicts target. If rho(cond, target) ~ rho(metric, target),
    metric adds nothing."""
    rho, p = spearman_safe(log_cond, target)
    return {"cond_rho": round(rho, 6), "cond_p": float(p)}


def permutation_null(metric, target, n_perm=1000, seed=42):
    """Shuffle target labels, recompute Spearman rho. Return p-value."""
    real_rho, _ = spearman_safe(metric, target)
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        shuffled = rng.permutation(target)
        perm_rho, _ = spearman_safe(metric, shuffled)
        if abs(perm_rho) >= abs(real_rho):
            count += 1
    return {
        "real_rho": round(real_rho, 6),
        "p_value": round(count / n_perm, 4),
        "n_permutations": n_perm,
    }


# ---------------------------------------------------------------------------
# 4. Run a full test battery for one (metric, target) pair
# ---------------------------------------------------------------------------

def run_test_pair(name, metric, target, log_cond):
    """Full battery for one metric-target pair."""
    print(f"\n{'-'*60}")
    print(f"  {name}")
    print(f"{'-'*60}")

    rho, p = spearman_safe(metric, target)
    print(f"  Raw Spearman rho = {rho:.4f}  p = {p:.2e}")

    wcb = within_conductor_correlation(log_cond, metric, target)
    print(f"  Within-conductor-bin median rho = {wcb['median_rho']}"
          f"  ({wcb['n_bins']} bins)")

    pc = partial_correlation_conductor(metric, target, log_cond)
    print(f"  Partial rho (controlling conductor) = {pc['partial_rho']}")

    f33 = f33_ordinal_check(metric, target)
    print(f"  F33 ordinal: real={f33['real_rho']:.4f}  sorted={f33['sorted_rho']:.4f}"
          f"  artifact={f33['ordinal_artifact']}")

    f34 = f34_trivial_baseline(log_cond, target)
    print(f"  F34 trivial baseline: cond_rho={f34['cond_rho']:.4f}")

    perm = permutation_null(metric, target)
    print(f"  Permutation null: rho={perm['real_rho']:.4f}  p={perm['p_value']:.4f}")

    # Verdict
    kills = []
    if f33["ordinal_artifact"]:
        kills.append("F33_ordinal")
    if f34["cond_rho"] != 0 and abs(rho) > 0:
        ratio = abs(rho) / max(abs(f34["cond_rho"]), 1e-10)
        if ratio < 1.2:
            kills.append("F34_trivial_baseline")
    if perm["p_value"] > 0.05:
        kills.append("permutation_null")
    if wcb["median_rho"] is not None and abs(wcb["median_rho"]) < 0.02:
        kills.append("within_bin_vanishes")

    verdict = "KILLED" if kills else "SURVIVES"
    print(f"  Verdict: {verdict}  {kills if kills else ''}")

    return {
        "name": name,
        "raw_rho": round(rho, 6),
        "raw_p": float(p),
        "within_conductor_bin": wcb,
        "partial_correlation": pc,
        "f33_ordinal": f33,
        "f34_trivial_baseline": f34,
        "permutation_null": perm,
        "verdict": verdict,
        "kill_reasons": kills,
    }


# ---------------------------------------------------------------------------
# 5. Stratified analysis
# ---------------------------------------------------------------------------

def stratified_analysis(features, metric_key, target_key):
    """Run correlations stratified by rank and root_number."""
    results = {}

    # By rank
    for r in [0, 1, 2]:
        mask = np.array([f["rank"] == r for f in features])
        if np.sum(mask) < 30:
            results[f"rank_{r}"] = {"n": int(np.sum(mask)), "rho": None}
            continue
        m = np.array([f[metric_key] for f, ok in zip(features, mask) if ok])
        t = np.array([f[target_key] for f, ok in zip(features, mask) if ok])
        rho, p = spearman_safe(m, t)
        results[f"rank_{r}"] = {"n": int(np.sum(mask)), "rho": round(rho, 6), "p": float(p)}

    # By root_number
    for rn in [1.0, -1.0]:
        mask = np.array([f["root_number"] == rn for f in features])
        if np.sum(mask) < 30:
            results[f"root_number_{int(rn)}"] = {"n": int(np.sum(mask)), "rho": None}
            continue
        m = np.array([f[metric_key] for f, ok in zip(features, mask) if ok])
        t = np.array([f[target_key] for f, ok in zip(features, mask) if ok])
        rho, p = spearman_safe(m, t)
        results[f"root_number_{int(rn)}"] = {"n": int(np.sum(mask)), "rho": round(rho, 6), "p": float(p)}

    return results


# ---------------------------------------------------------------------------
# 6. Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("SPECTRAL TAIL -> ISOGENY CLASS GEOMETRY TEST")
    print("=" * 70)

    # Load
    print("\nLoading data from charon.duckdb...")
    raw = load_data()
    print(f"  Loaded {len(raw)} curves with zeros + isogeny data")

    # Extract features
    features = [extract_features(r) for r in raw]
    print(f"  Extracted features for {len(features)} curves")

    # Build arrays
    first_zero = np.array([f["first_zero"] for f in features])
    micro_spacing = np.array([f["micro_spacing_mean"] for f in features])
    tail_density = np.array([f["tail_density"] for f in features])
    log_cond = np.array([f["log_conductor"] for f in features])
    class_size = np.array([f["class_size"] for f in features], dtype=float)
    class_deg = np.array([f["class_deg"] for f in features], dtype=float)
    max_iso = np.array([f["max_iso_deg"] for f in features], dtype=float)

    # Summary statistics
    print(f"\n  first_zero:      mean={np.mean(first_zero):.3f}  std={np.std(first_zero):.3f}")
    print(f"  micro_spacing:   mean={np.mean(micro_spacing):.3f}  std={np.std(micro_spacing):.3f}")
    print(f"  tail_density:    mean={np.mean(tail_density):.3f}  std={np.std(tail_density):.3f}")
    print(f"  class_size:      mean={np.mean(class_size):.2f}  unique={len(np.unique(class_size))}")
    print(f"  class_deg:       mean={np.mean(class_deg):.2f}  unique={len(np.unique(class_deg))}")
    print(f"  max_iso_deg:     mean={np.mean(max_iso):.2f}  unique={len(np.unique(max_iso))}")

    # Distribution of targets
    for tname, tarr in [("class_size", class_size), ("class_deg", class_deg), ("max_iso_deg", max_iso)]:
        vals, cnts = np.unique(tarr, return_counts=True)
        top5 = sorted(zip(cnts, vals), reverse=True)[:5]
        print(f"  {tname} top values: {[(int(v), int(c)) for c, v in top5]}")

    results = {"n_curves": len(features), "tests": {}}

    # ---------------------------------------------------------------------------
    # Core tests: 3 metrics x 3 targets = 9 pairs
    # ---------------------------------------------------------------------------
    metrics = [
        ("first_zero", first_zero),
        ("micro_spacing", micro_spacing),
        ("tail_density", tail_density),
    ]
    targets = [
        ("class_size", class_size),
        ("class_deg", class_deg),
        ("max_iso_deg", max_iso),
    ]

    for mname, marr in metrics:
        for tname, tarr in targets:
            key = f"{mname}_vs_{tname}"
            result = run_test_pair(key, marr, tarr, log_cond)
            results["tests"][key] = result

    # ---------------------------------------------------------------------------
    # Stratified analysis for the most promising pairs
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STRATIFIED ANALYSIS (by rank and root_number)")
    print("=" * 70)

    strat_results = {}
    for mname in ["first_zero", "micro_spacing_mean", "tail_density"]:
        for tname in ["class_size", "class_deg"]:
            key = f"{mname}_vs_{tname}"
            sr = stratified_analysis(features, mname, tname)
            strat_results[key] = sr
            print(f"\n  {key}:")
            for stratum, info in sr.items():
                print(f"    {stratum}: n={info['n']}  rho={info.get('rho')}")

    results["stratified"] = strat_results

    # ---------------------------------------------------------------------------
    # Summary verdicts
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    n_survive = 0
    n_killed = 0
    for key, res in results["tests"].items():
        v = res["verdict"]
        if v == "SURVIVES":
            n_survive += 1
        else:
            n_killed += 1
        print(f"  {key}: {v}  (rho={res['raw_rho']:.4f})")

    results["summary"] = {
        "total_tests": len(results["tests"]),
        "survived": n_survive,
        "killed": n_killed,
        "conclusion": (
            "No evidence that low-lying zeros predict isogeny class geometry "
            "beyond conductor."
            if n_killed >= 7 else
            "Some spectral-isogeny correlations survive the battery."
        ),
    }
    print(f"\n  {n_survive}/{len(results['tests'])} survived, "
          f"{n_killed}/{len(results['tests'])} killed")
    print(f"  Conclusion: {results['summary']['conclusion']}")

    # ---------------------------------------------------------------------------
    # Save results
    # ---------------------------------------------------------------------------
    out_dir = Path(__file__).resolve().parents[3] / "cartography" / "convergence" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "spectral_tail_isogeny_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
