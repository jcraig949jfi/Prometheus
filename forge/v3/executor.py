#!/usr/bin/env python3
"""
Executor: Translates a Hypothesis into a computable test, runs it, returns results.

The hard part: mapping 51 features × 24 domains into actual data + computation.
Strategy: lazy data loading + feature extraction registry + battery integration.
"""
import sys
import json
import math
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.stats import spearmanr, pearsonr, ks_2samp
from scipy.spatial.distance import cdist

_root = Path(__file__).resolve().parents[2]
_scripts = str(_root / "cartography/shared/scripts")
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from gene_schema import Hypothesis, DOMAINS, FEATURES
from battery_v2 import BatteryV2

bv2 = BatteryV2()
rng = np.random.default_rng(42)

# ============================================================
# Lazy Data Cache
# ============================================================
_data_cache = {}


def _load_domain(domain):
    """Lazy-load domain data. Returns list of dicts with raw fields."""
    if domain in _data_cache:
        return _data_cache[domain]

    data_root = _root / "cartography"

    objects = []

    if domain == "elliptic_curves":
        import psycopg2
        try:
            from prometheus_data.config import get_pg_dsn
            con = psycopg2.connect(**get_pg_dsn("lmfdb"))
        except Exception:
            con = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
        cur = con.cursor()
        cur.execute("""
            SELECT conductor::bigint, rank::int, torsion::int, cm::int
            FROM ec_curvedata WHERE conductor::bigint > 0 LIMIT 10000
        """)
        rows = cur.fetchall()
        con.close()
        for cond, rank, tors, cm in rows:
            objects.append({"conductor": cond, "rank": rank or 0, "torsion": tors or 1,
                           "cm": cm or 0, "ap": []})

    elif domain == "modular_forms":
        import psycopg2
        try:
            from prometheus_data.config import get_pg_dsn
            con = psycopg2.connect(**get_pg_dsn("lmfdb"))
        except Exception:
            con = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
        cur = con.cursor()
        cur.execute("""
            SELECT level::int, weight::int, dim::int FROM mf_newforms WHERE level::int > 0 LIMIT 10000
        """)
        rows = cur.fetchall()
        con.close()
        for level, weight, dim in rows:
            objects.append({"level": level, "weight": weight, "dim": dim or 1})

    elif domain == "number_fields":
        nf_path = data_root / "number_fields/data/number_fields.json"
        if nf_path.exists():
            raw = json.load(open(nf_path, encoding="utf-8"))
            for f in raw[:10000]:
                try:
                    objects.append({
                        "discriminant": float(f.get("disc_abs", 0)),
                        "class_number": float(f.get("class_number", 0)),
                        "regulator": float(f.get("regulator", 0)),
                        "degree": int(float(f.get("degree", 0))),
                    })
                except: pass

    elif domain == "genus2_curves":
        g2_path = data_root / "genus2/data/genus2_curves_full.json"
        if g2_path.exists():
            raw = json.load(open(g2_path, encoding="utf-8"))
            for c in raw[:10000]:
                if c.get("conductor", 0) > 0:
                    import ast
                    t = c.get("torsion", [])
                    if isinstance(t, str):
                        try: t = ast.literal_eval(t)
                        except: t = []
                    order = 1
                    if isinstance(t, list):
                        for x in t: order *= x
                    objects.append({
                        "conductor": c["conductor"],
                        "discriminant": abs(c.get("discriminant", 0)),
                        "torsion": order,
                        "st_group": c.get("st_group", ""),
                        "root_number": c.get("root_number", 0),
                    })

    elif domain == "maass_forms":
        maass_path = data_root / "maass/data/maass_with_coefficients.json"
        if maass_path.exists():
            raw = json.load(open(maass_path, encoding="utf-8"))
            for m in raw[:5000]:
                coeffs = m.get("coefficients", [])
                objects.append({
                    "level": m.get("level", 0),
                    "spectral_parameter": m.get("spectral_parameter", 0),
                    "coefficients": coeffs[:25] if isinstance(coeffs, list) else [],
                })

    elif domain == "knots":
        knot_path = data_root / "knots/data/knots.json"
        if knot_path.exists():
            raw = json.load(open(knot_path, encoding="utf-8"))
            for k in raw.get("knots", raw if isinstance(raw, list) else [])[:10000]:
                objects.append({
                    "crossing_number": k.get("crossing_number", 0),
                    "determinant": k.get("determinant", 0),
                    "alex_coeffs": k.get("alex_coeffs", []),
                    "jones_coeffs": k.get("jones_coeffs", []),
                })

    elif domain == "superconductors":
        import csv, io
        csv_path = data_root / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
        if csv_path.exists():
            import re
            with open(csv_path) as f:
                lines = [l for l in f if not l.startswith("#")]
            for row in csv.DictReader(io.StringIO("".join(lines))):
                try:
                    tc = float(row.get("tc", ""))
                    sg = row.get("spacegroup_2", "").strip()
                    sc_class = row.get("sc_class", "").strip()
                    if tc > 0 and sg:
                        objects.append({"tc": tc, "sg": sg, "sc_class": sc_class})
                except: pass

    # Fallback: empty domain
    if not objects:
        objects = [{"_empty": True}]

    _data_cache[domain] = objects
    return objects


# ============================================================
# Feature Extraction Registry
# ============================================================

def _extract_feature(objects, feature_name):
    """Extract a numeric array from domain objects for a given feature name."""
    values = []
    for obj in objects:
        val = None

        # Direct field match
        if feature_name in obj:
            try:
                val = float(obj[feature_name])
            except (TypeError, ValueError):
                pass

        # Computed features
        if val is None:
            if feature_name == "log_conductor" and "conductor" in obj:
                val = math.log(max(obj["conductor"], 1))
            elif feature_name == "log_discriminant" and "discriminant" in obj:
                val = math.log(max(obj["discriminant"], 1))
            elif feature_name == "n_bad_primes" and "conductor" in obj:
                c = int(obj["conductor"])
                count = 0
                for p in [2, 3, 5, 7, 11, 13]:
                    if c % p == 0: count += 1
                val = float(count)
            elif feature_name == "ap_kurtosis" and "ap" in obj and len(obj["ap"]) >= 5:
                arr = np.array(obj["ap"], dtype=float)
                if np.std(arr) > 0:
                    val = float(np.mean(((arr - np.mean(arr)) / np.std(arr))**4))
            elif feature_name == "coefficient_entropy" and "coefficients" in obj and len(obj["coefficients"]) >= 5:
                arr = np.abs(np.array(obj["coefficients"][:20], dtype=float))
                total = np.sum(arr)
                if total > 0:
                    p = arr / total
                    p = p[p > 0]
                    val = float(-np.sum(p * np.log2(p)))
            elif feature_name == "alexander_degree" and "alex_coeffs" in obj:
                val = float(len(obj.get("alex_coeffs", [])))
            elif feature_name == "jones_degree" and "jones_coeffs" in obj:
                val = float(len(obj.get("jones_coeffs", [])))
            elif feature_name == "homo_lumo_gap" and "gap" in obj:
                val = float(obj["gap"])
            elif feature_name == "f_vector_sum" and "f_vector" in obj:
                val = float(sum(obj["f_vector"]))
            elif feature_name == "ap_compression_lz" and "ap" in obj and len(obj["ap"]) >= 5:
                import zlib
                s = ",".join(str(x) for x in obj["ap"])
                val = float(len(zlib.compress(s.encode())) / len(s.encode()))

        if val is not None and np.isfinite(val):
            values.append(val)
        else:
            values.append(float("nan"))

    return np.array(values, dtype=float)


# ============================================================
# Coupling Functions
# ============================================================

def _compute_coupling(values_a, values_b, method):
    """Compute coupling between two feature arrays."""
    # Align: use min length, drop nans
    n = min(len(values_a), len(values_b))
    a = values_a[:n]
    b = values_b[:n]
    mask = np.isfinite(a) & np.isfinite(b)
    a = a[mask]
    b = b[mask]

    if len(a) < 20:
        return {"method": method, "value": float("nan"), "p_value": 1.0, "n": len(a)}

    if method == "spearman":
        rho, p = spearmanr(a, b)
        return {"method": "spearman", "value": float(rho), "p_value": float(p), "n": len(a)}
    elif method == "pearson":
        r, p = pearsonr(a, b)
        return {"method": "pearson", "value": float(r), "p_value": float(p), "n": len(a)}
    elif method == "mutual_information":
        # Binned MI
        from sklearn.metrics import mutual_info_score
        n_bins = min(30, len(a) // 10)
        if n_bins < 3:
            return {"method": "mi", "value": 0.0, "p_value": 1.0, "n": len(a)}
        ad = np.digitize(a, np.linspace(a.min() - 1e-10, a.max() + 1e-10, n_bins + 1))
        bd = np.digitize(b, np.linspace(b.min() - 1e-10, b.max() + 1e-10, n_bins + 1))
        mi = mutual_info_score(ad, bd) / max(np.log(2), 1)
        return {"method": "mi", "value": float(mi), "p_value": 0.0, "n": len(a)}  # p needs permutation
    elif method == "ks_statistic":
        stat, p = ks_2samp(a, b)
        return {"method": "ks", "value": float(stat), "p_value": float(p), "n": len(a)}
    elif method == "wasserstein":
        from scipy.stats import wasserstein_distance
        wd = wasserstein_distance(a, b)
        return {"method": "wasserstein", "value": float(wd), "p_value": 0.0, "n": len(a)}
    else:
        # Default to spearman
        rho, p = spearmanr(a, b)
        return {"method": "spearman", "value": float(rho), "p_value": float(p), "n": len(a)}


# ============================================================
# Permutation Null
# ============================================================

def _permutation_null(values_a, values_b, method, n_perms=200):
    """Compute permutation null for the coupling."""
    real = _compute_coupling(values_a, values_b, method)
    if np.isnan(real["value"]):
        return real, 0.0, 1.0

    null_values = []
    for _ in range(n_perms):
        shuffled = values_b.copy()
        rng.shuffle(shuffled)
        null = _compute_coupling(values_a, shuffled, method)
        if not np.isnan(null["value"]):
            null_values.append(null["value"])

    if not null_values:
        return real, 0.0, 1.0

    null_arr = np.array(null_values)
    z = (real["value"] - np.mean(null_arr)) / np.std(null_arr) if np.std(null_arr) > 0 else 0
    p = (np.sum(np.abs(null_arr) >= abs(real["value"])) + 1) / (len(null_arr) + 1)

    return real, float(z), float(p)


# ============================================================
# Main Executor
# ============================================================

def execute(hypothesis: Hypothesis) -> dict:
    """Execute a hypothesis: load data, extract features, compute coupling, run null.

    Returns a result dict with: coupling, z_score, p_value, survival_depth, kill_test.
    """
    result = {
        "hypothesis_id": hypothesis.id,
        "status": "error",
        "coupling": {},
        "z_score": 0.0,
        "p_value": 1.0,
        "survival_depth": 0,
        "kill_test": "",
        "notes": "",
    }

    try:
        # Load domains
        objects_a = _load_domain(hypothesis.domain_a)
        objects_b = _load_domain(hypothesis.domain_b)

        if objects_a[0].get("_empty") or objects_b[0].get("_empty"):
            result["status"] = "no_data"
            result["kill_test"] = "data_unavailable"
            result["notes"] = f"Domain {hypothesis.domain_a} or {hypothesis.domain_b} has no data"
            return result

        # Extract features
        feat_a = _extract_feature(objects_a, hypothesis.feature_a)
        feat_b = _extract_feature(objects_b, hypothesis.feature_b)

        # Subsample to resolution
        n = hypothesis.resolution
        if len(feat_a) > n:
            idx = rng.choice(len(feat_a), n, replace=False)
            feat_a = feat_a[idx]
        if len(feat_b) > n:
            idx = rng.choice(len(feat_b), n, replace=False)
            feat_b = feat_b[idx]

        # Drop NaN
        valid_a = np.sum(np.isfinite(feat_a))
        valid_b = np.sum(np.isfinite(feat_b))

        if valid_a < 20 or valid_b < 20:
            result["status"] = "insufficient_data"
            result["kill_test"] = "F1_insufficient"
            result["notes"] = f"Feature extraction yielded {valid_a}/{valid_b} valid values"
            return result

        # Compute coupling with permutation null
        coupling, z_score, p_value = _permutation_null(feat_a, feat_b, hypothesis.coupling)

        result["coupling"] = coupling
        result["z_score"] = z_score
        result["p_value"] = p_value
        result["status"] = "executed"

        # Survival depth: how many tests does it pass?
        depth = 0

        # F1: permutation null (z > 2)
        if abs(z_score) > 2:
            depth += 1
        else:
            result["survival_depth"] = depth
            result["kill_test"] = "F1_permutation_null"
            return result

        # F3: effect size (|coupling| > 0.05)
        if abs(coupling.get("value", 0)) > 0.05:
            depth += 1
        else:
            result["survival_depth"] = depth
            result["kill_test"] = "F3_effect_size"
            return result

        # F24: permutation-calibrated eta² (for categorical features)
        # Skip for continuous — just check z > 3
        if abs(z_score) > 3:
            depth += 1
        else:
            result["survival_depth"] = depth
            result["kill_test"] = "F24_permutation"
            return result

        # Reached depth 3 — a genuine signal candidate
        result["survival_depth"] = depth
        result["status"] = "survived"
        result["notes"] = f"Survived {depth} tests: coupling={coupling['value']:.4f}, z={z_score:.1f}"

    except Exception as e:
        result["status"] = "error"
        result["notes"] = str(e)[:200]
        result["kill_test"] = "execution_error"

    return result


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    from gene_schema import random_hypothesis, Hypothesis

    print("Executor Test")
    print("=" * 70)

    # Test with a known signal: SC_class -> Tc
    h_known = Hypothesis(
        id="test_known",
        domain_a="superconductors",
        domain_b="superconductors",
        feature_a="tc",
        feature_b="tc",
        coupling="spearman",
        resolution=2000,
    )
    print(f"\nKnown signal (Tc self-correlation):")
    r = execute(h_known)
    print(f"  Status: {r['status']}, z={r['z_score']:.1f}, depth={r['survival_depth']}")

    # Test with a known null: random domains
    h_null = Hypothesis(
        id="test_null",
        domain_a="elliptic_curves",
        domain_b="knots",
        feature_a="conductor",
        feature_b="determinant",
        coupling="spearman",
        resolution=500,
    )
    print(f"\nExpected null (EC conductor vs knot determinant):")
    r = execute(h_null)
    print(f"  Status: {r['status']}, z={r['z_score']:.1f}, depth={r['survival_depth']}, kill={r['kill_test']}")

    # Test with random hypotheses
    print(f"\n5 random hypotheses:")
    import random as _random
    _rng = _random.Random(42)
    for i in range(5):
        h = random_hypothesis(0, _rng)
        h.resolution = 500  # fast
        r = execute(h)
        print(f"  {h.domain_a[:12]:12s} x {h.domain_b[:12]:12s} | {h.feature_a[:15]:15s} x {h.feature_b[:15]:15s} | "
              f"z={r['z_score']:+6.1f} | depth={r['survival_depth']} | {r['kill_test'] or 'SURVIVED'}")
