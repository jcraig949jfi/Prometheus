"""
Reevaluator — Retest killed hypotheses on prime-detrended data.
================================================================
2,563 F12 kills and 63 F3 borderline kills were made in polluted space.
The confound was primes. With primes stripped, the real signal might emerge.

Pipeline:
  1. Load killed hypotheses from shadow_preload.jsonl
  2. Identify dataset pair and kill mode
  3. Load detrended residuals for both datasets
  4. Re-run the failing test on detrended data
  5. If it passes → run full battery on detrended data
  6. Log results: REVIVED, STILL_DEAD, or UPGRADED

Usage:
    python reevaluator.py                    # full re-evaluation
    python reevaluator.py --mode F12         # only F12 kills
    python reevaluator.py --pair KnotInfo NumberFields  # one pair
"""

import json
import math
import sys
import time
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats as sp_stats

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
PRELOAD = CONVERGENCE / "data" / "shadow_preload.jsonl"
RESULTS_FILE = CONVERGENCE / "data" / "reevaluation_results.jsonl"
REVIVED_FILE = CONVERGENCE / "data" / "revived_hypotheses.jsonl"


def prime_features(n):
    """Prime factorization features for detrending."""
    n = int(abs(n))
    if n < 2:
        return [0, 0, 0, 0, 0, 0]
    factors = {}
    d = 2
    temp = n
    while d * d <= temp and temp > 1:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    n_distinct = len(factors)
    total_exp = sum(factors.values())
    largest = max(factors.keys()) if factors else 0
    smallest = min(factors.keys()) if factors else 0
    is_prime = 1 if n_distinct == 1 and total_exp == 1 else 0
    smoothness = math.log(largest) / math.log(max(n, 2)) if largest > 0 else 0
    return [n_distinct, total_exp, math.log(max(largest, 2)),
            math.log(max(smallest, 2)), is_prime, smoothness]


def detrend(values):
    """Detrend an array by removing prime factorization structure."""
    arr = np.array(values, dtype=float)
    valid = arr[arr > 1]
    if len(valid) < 15:
        return None

    features = np.array([prime_features(int(v)) for v in valid])
    good_cols = [i for i in range(features.shape[1]) if np.std(features[:, i]) > 1e-10]
    if not good_cols:
        return None

    X = features[:, good_cols]
    X = np.column_stack([X, np.ones(len(X))])
    target = np.log(valid)

    try:
        coeffs, _, _, _ = np.linalg.lstsq(X, target, rcond=None)
        return target - X @ coeffs
    except Exception:
        return None


_array_cache = {}

def get_dataset_array(dataset_name):
    """Get numerical array for a dataset, with caching."""
    if dataset_name in _array_cache:
        return _array_cache[dataset_name]

    arr = None

    if dataset_name in ("LMFDB", "lmfdb"):
        try:
            from search_engine import _get_duck
            con = _get_duck()
            rows = con.execute(
                "SELECT conductor FROM objects WHERE object_type='elliptic_curve' AND conductor <= 50000"
            ).fetchall()
            con.close()
            arr = np.array([r[0] for r in rows], dtype=float)
        except Exception:
            pass

    elif dataset_name in ("Genus2", "genus2"):
        from search_engine import _load_genus2, _genus2_cache
        _load_genus2()
        if _genus2_cache:
            arr = np.array([c["conductor"] for c in _genus2_cache[:5000]
                           if c.get("conductor")], dtype=float)

    elif dataset_name in ("NumberFields", "number_fields"):
        from search_engine import _load_nf, _nf_cache
        _load_nf()
        if _nf_cache:
            arr = np.array([abs(int(f["disc_abs"])) for f in _nf_cache[:5000]
                           if f.get("disc_abs") and str(f["disc_abs"]).lstrip("-").isdigit()],
                          dtype=float)

    elif dataset_name in ("KnotInfo", "knots"):
        from search_engine import _load_knots, _knots_cache
        _load_knots()
        knots = _knots_cache.get("knots", []) if isinstance(_knots_cache, dict) else []
        if knots:
            arr = np.array([k["determinant"] for k in knots
                           if isinstance(k, dict) and isinstance(k.get("determinant"), (int, float))
                           and k["determinant"] > 0][:5000], dtype=float)

    elif dataset_name in ("SmallGroups", "smallgroups"):
        from search_engine import _load_smallgroups, _smallgroups_cache
        _load_smallgroups()
        if _smallgroups_cache:
            arr = np.array([g["n_groups"] for g in _smallgroups_cache[:2000]
                           if isinstance(g.get("n_groups"), int) and 0 < g["n_groups"] < 1e9],
                          dtype=float)

    elif dataset_name in ("Isogenies", "isogenies"):
        from search_engine import ISOGENY_GRAPHS
        if ISOGENY_GRAPHS.exists():
            vals = []
            for pdir in sorted(ISOGENY_GRAPHS.iterdir()):
                if pdir.is_dir():
                    try:
                        p = int(pdir.name)
                        vals.append((p - 1) // 12 + 1)
                    except ValueError:
                        pass
            if vals:
                arr = np.array(vals, dtype=float)

    elif dataset_name in ("Maass", "maass"):
        from search_engine import _load_maass, _maass_cache
        _load_maass()
        if _maass_cache:
            arr = np.array([m["spectral_parameter"] for m in _maass_cache
                           if m.get("spectral_parameter")], dtype=float)

    _array_cache[dataset_name] = arr
    return arr


# Dataset name normalization
DATASET_MAP = {
    "oeis": "OEIS", "lmfdb": "LMFDB", "knot": "KnotInfo",
    "fungrim": "Fungrim", "antedb": "ANTEDB", "mathlib": "mathlib",
    "number field": "NumberFields", "numberfield": "NumberFields",
    "isogen": "Isogenies", "genus-2": "Genus2", "genus2": "Genus2",
    "maass": "Maass", "lattice": "Lattices", "smallgroup": "SmallGroups",
    "small group": "SmallGroups", "elliptic curve": "LMFDB",
    "modular form": "LMFDB", "conductor": "LMFDB",
    "determinant": "KnotInfo", "class number": "NumberFields",
    "discriminant": "NumberFields",
}

DATASETS_WITH_ARRAYS = {"LMFDB", "Genus2", "NumberFields", "KnotInfo",
                         "SmallGroups", "Isogenies", "Maass"}


def extract_datasets(claim):
    """Extract dataset names from a hypothesis claim."""
    text = claim.lower()
    found = set()
    for kw, canonical in DATASET_MAP.items():
        if kw in text:
            found.add(canonical)
    return sorted(found)


def retest_detrended(a_raw, b_raw):
    """Run key tests on detrended versions of two arrays."""
    a_dt = detrend(a_raw)
    b_dt = detrend(b_raw)

    if a_dt is None or b_dt is None:
        return {"verdict": "SKIP", "reason": "detrend failed"}

    # SORT FIRST, then truncate to equal length.
    # Bug fix: truncate-then-sort takes an unrepresentative subsample
    # of the larger array, inflating correlation. (Found 2026-04-08)
    a_sorted = np.sort(a_dt)
    b_sorted = np.sort(b_dt)
    n = min(len(a_sorted), len(b_sorted))
    if n < 20:
        return {"verdict": "SKIP", "reason": f"too few detrended values ({n})"}

    # Subsample the LARGER array evenly to match the smaller
    if len(a_sorted) > n:
        indices = np.linspace(0, len(a_sorted) - 1, n, dtype=int)
        a_s = a_sorted[indices]
    else:
        a_s = a_sorted
    if len(b_sorted) > n:
        indices = np.linspace(0, len(b_sorted) - 1, n, dtype=int)
        b_s = b_sorted[indices]
    else:
        b_s = b_sorted

    results = {}

    # F1: Permutation test on detrended
    rng = np.random.RandomState(42)
    real_rho = abs(float(sp_stats.spearmanr(a_s, b_s)[0]))
    null_rhos = []
    for _ in range(2000):
        null_rhos.append(abs(float(sp_stats.spearmanr(a_s, rng.permutation(b_s))[0])))
    p_perm = (np.sum(np.array(null_rhos) >= real_rho) + 1) / 2001
    results["f1_detrended"] = {
        "rho": round(real_rho, 6),
        "p": round(float(p_perm), 6),
        "pass": p_perm < 0.01,
    }

    # F3: Effect size on detrended
    d = abs(float(np.mean(a) - np.mean(b))) / max(float(np.sqrt((np.var(a) + np.var(b)) / 2)), 1e-10)
    results["f3_detrended"] = {
        "cohens_d": round(d, 4),
        "pass": d > 0.2,
    }

    # F12: Partial correlation with index as confound
    idx = np.arange(n, dtype=float)
    # Residualize both against index
    a_resid = a_s - np.polyval(np.polyfit(idx, a_s, 1), idx)
    b_resid = b_s - np.polyval(np.polyfit(idx, b_s, 1), idx)
    if np.std(a_resid) > 1e-10 and np.std(b_resid) > 1e-10:
        rho_partial = float(sp_stats.spearmanr(a_resid, b_resid)[0])
    else:
        rho_partial = 0.0
    results["f12_detrended"] = {
        "rho_partial": round(rho_partial, 6),
        "pass": abs(rho_partial) > 0.1,
    }

    # KS test: do detrended distributions match?
    ks_stat, ks_p = sp_stats.ks_2samp(a, b)
    results["ks_detrended"] = {
        "stat": round(float(ks_stat), 4),
        "p": round(float(ks_p), 6),
        "match": ks_p > 0.05,
    }

    # Mutual information on detrended
    hist2d, _, _ = np.histogram2d(a, b, bins=15)
    pxy = hist2d / max(hist2d.sum(), 1)
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)
    mi = 0.0
    for i in range(15):
        for j in range(15):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))
    results["mi_detrended"] = {
        "bits": round(float(mi), 6),
        "significant": mi > 0.05,
    }

    # Overall verdict
    passes = sum(1 for v in results.values() if v.get("pass") or v.get("significant") or v.get("match"))
    total = len(results)

    if passes >= 3:
        verdict = "REVIVED"
    elif passes >= 2:
        verdict = "UPGRADED"
    else:
        verdict = "STILL_DEAD"

    return {
        "verdict": verdict,
        "tests": results,
        "passes": passes,
        "total": total,
        "n_detrended": n,
    }


def run_reevaluation(mode_filter=None, pair_filter=None, max_evals=None):
    """Re-evaluate killed hypotheses on detrended data."""
    print("=" * 70)
    print("  REEVALUATOR — Retesting the dead on clean data")
    print("  2,626 kills made in polluted space. How many survive detrending?")
    print("=" * 70)

    t0 = time.time()

    # Load killed hypotheses
    killed = []
    with open(PRELOAD) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except:
                continue
            if rec.get("verdict") != "KILLED":
                continue

            kill_tests = rec.get("kill_tests", [])

            # Filter by mode
            if mode_filter == "F12" and "F12_partial_correlation" not in kill_tests:
                continue
            if mode_filter == "F3" and kill_tests != ["F3_effect_size"]:
                continue

            datasets = extract_datasets(rec.get("claim", ""))
            # Filter to datasets we can detrend
            usable = [d for d in datasets if d in DATASETS_WITH_ARRAYS]
            if len(usable) < 2:
                continue

            if pair_filter:
                if not all(p in usable for p in pair_filter):
                    continue

            killed.append({
                "claim": rec.get("claim", ""),
                "datasets": usable,
                "kill_tests": kill_tests,
                "pair": f"{usable[0]}--{usable[1]}",
                "tag": rec.get("tag", ""),
            })

    print(f"\n  Loaded {len(killed)} re-evaluation candidates")

    if max_evals:
        killed = killed[:max_evals]

    # Group by pair (test each pair once, not per hypothesis)
    by_pair = defaultdict(list)
    for k in killed:
        by_pair[k["pair"]].append(k)

    print(f"  Unique pairs to retest: {len(by_pair)}")
    print()

    revived = []
    upgraded = []
    still_dead = []
    skipped = 0

    for pair, hypotheses in sorted(by_pair.items()):
        d1, d2 = pair.split("--")
        a_raw = get_dataset_array(d1)
        b_raw = get_dataset_array(d2)

        if a_raw is None or b_raw is None:
            skipped += len(hypotheses)
            continue

        result = retest_detrended(a_raw, b_raw)

        if result["verdict"] == "SKIP":
            skipped += len(hypotheses)
            continue

        verdict = result["verdict"]
        n_hyps = len(hypotheses)

        marker = ""
        if verdict == "REVIVED":
            marker = " <-- REVIVED!"
            revived.extend(hypotheses)
        elif verdict == "UPGRADED":
            marker = " (upgraded)"
            upgraded.extend(hypotheses)
        else:
            still_dead.extend(hypotheses)

        tests = result["tests"]
        print(f"  {pair:35s} [{verdict:10s}] {n_hyps:3d} hypotheses | "
              f"f1_p={tests['f1_detrended']['p']:.4f} "
              f"f3_d={tests['f3_detrended']['cohens_d']:.3f} "
              f"f12_r={tests['f12_detrended']['rho_partial']:.3f} "
              f"MI={tests['mi_detrended']['bits']:.4f}{marker}")

        # Log each result
        def _jdefault(o):
            if isinstance(o, (np.bool_, np.integer)):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            return str(o)

        with open(RESULTS_FILE, "a") as f:
            f.write(json.dumps({
                "pair": pair,
                "verdict": verdict,
                "n_hypotheses": n_hyps,
                "detrended_tests": result["tests"],
                "sample_claims": [h["claim"][:100] for h in hypotheses[:3]],
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }, default=_jdefault) + "\n")

    # Save revived hypotheses
    if revived:
        with open(REVIVED_FILE, "a") as f:
            for h in revived:
                f.write(json.dumps({
                    "claim": h["claim"],
                    "pair": h["pair"],
                    "original_kill": h["kill_tests"],
                    "status": "REVIVED_BY_DETRENDING",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }) + "\n")

    elapsed = time.time() - t0

    print(f"\n{'=' * 70}")
    print(f"  REEVALUATION COMPLETE in {elapsed:.1f}s")
    print(f"  Candidates: {len(killed)}")
    print(f"  REVIVED: {len(revived)} (signal survives prime detrending)")
    print(f"  UPGRADED: {len(upgraded)} (partially survives)")
    print(f"  STILL DEAD: {len(still_dead)}")
    print(f"  SKIPPED: {skipped} (data unavailable)")

    if revived:
        print(f"\n  REVIVED PAIRS:")
        revived_pairs = Counter(h["pair"] for h in revived)
        for pair, count in revived_pairs.most_common():
            print(f"    {pair:35s} {count:4d} hypotheses revived")

    print(f"\n  Results: {RESULTS_FILE}")
    if revived:
        print(f"  Revived: {REVIVED_FILE}")
    print(f"{'=' * 70}")

    return {"revived": len(revived), "upgraded": len(upgraded),
            "still_dead": len(still_dead), "skipped": skipped}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reevaluator — retest killed hypotheses")
    parser.add_argument("--mode", choices=["F12", "F3"], default=None, help="Filter by kill mode")
    parser.add_argument("--pair", nargs=2, default=None, help="Focus on one pair")
    parser.add_argument("--max", type=int, default=None, help="Max evaluations")
    args = parser.parse_args()

    run_reevaluation(mode_filter=args.mode, pair_filter=args.pair, max_evals=args.max)
