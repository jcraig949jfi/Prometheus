#!/usr/bin/env python3
"""
C10: Constraint Collapse Phenomena — Generalizing the Hasse Squeeze
===================================================================
Tests whether super-exponential collapse of solution spaces under
cumulative constraints is a universal pattern across mathematics.

Systems tested:
  1. GL_2 vs GSp_4 congruence collapse
  2. Lattice class numbers vs dimension
  3. Number field counts vs degree (bounded discriminant)
  4. OEIS sequence survival under cumulative constraints
  5. Isogeny graph supersingular points vs prime
  6. Model fitting: exponential, super-exponential (Gaussian), power-law
  7. Universal scaling synthesis
"""

import json
import gzip
import math
import os
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit
from scipy.special import gammaln

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parents[3]  # F:/Prometheus/cartography
RESULTS = {}


# ── Model definitions ──────────────────────────────────────────────

def model_exp(x, A, B):
    """Exponential: A * exp(-B * x)"""
    return A * np.exp(-B * x)

def model_superexp(x, A, B):
    """Super-exponential (Gaussian): A * exp(-B * x^2)"""
    return A * np.exp(-B * x**2)

def model_power(x, A, alpha):
    """Power law: A * x^(-alpha)"""
    return A * np.power(x.astype(float), -alpha)


def aic(n, k, rss):
    """AIC given n data points, k parameters, residual sum of squares."""
    if rss <= 0 or n <= k + 1:
        return float('inf')
    return n * np.log(rss / n) + 2 * k

def bic(n, k, rss):
    """BIC given n data points, k parameters, residual sum of squares."""
    if rss <= 0 or n <= k + 1:
        return float('inf')
    return n * np.log(rss / n) + k * np.log(n)


def fit_models(x, y, label="system"):
    """Fit exponential, super-exponential, and power-law models. Return best."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    # Filter out zeros/negatives for fitting
    mask = (y > 0) & (x > 0)
    x_fit, y_fit = x[mask], y[mask]
    n = len(x_fit)

    if n < 3:
        return {"label": label, "n_points": int(n), "error": "too few points for fitting"}

    results = {}

    # 1. Exponential
    try:
        popt, _ = curve_fit(model_exp, x_fit, y_fit, p0=[y_fit[0], 0.5], maxfev=10000)
        y_pred = model_exp(x_fit, *popt)
        rss = np.sum((y_fit - y_pred)**2)
        results["exponential"] = {
            "params": {"A": float(popt[0]), "B": float(popt[1])},
            "rss": float(rss),
            "aic": float(aic(n, 2, rss)),
            "bic": float(bic(n, 2, rss)),
        }
    except Exception as e:
        results["exponential"] = {"error": str(e)}

    # 2. Super-exponential (Gaussian)
    try:
        popt, _ = curve_fit(model_superexp, x_fit, y_fit, p0=[y_fit[0], 0.1], maxfev=10000)
        y_pred = model_superexp(x_fit, *popt)
        rss = np.sum((y_fit - y_pred)**2)
        results["super_exponential"] = {
            "params": {"A": float(popt[0]), "B": float(popt[1])},
            "rss": float(rss),
            "aic": float(aic(n, 2, rss)),
            "bic": float(bic(n, 2, rss)),
        }
    except Exception as e:
        results["super_exponential"] = {"error": str(e)}

    # 3. Power law
    try:
        popt, _ = curve_fit(model_power, x_fit, y_fit, p0=[y_fit[0], 2.0], maxfev=10000)
        y_pred = model_power(x_fit, *popt)
        rss = np.sum((y_fit - y_pred)**2)
        results["power_law"] = {
            "params": {"A": float(popt[0]), "alpha": float(popt[1])},
            "rss": float(rss),
            "aic": float(aic(n, 2, rss)),
            "bic": float(bic(n, 2, rss)),
        }
    except Exception as e:
        results["power_law"] = {"error": str(e)}

    # Determine best model by AIC
    best_name, best_aic = None, float('inf')
    for name, r in results.items():
        if "aic" in r and r["aic"] < best_aic:
            best_aic = r["aic"]
            best_name = name

    return {
        "label": label,
        "n_points": int(n),
        "x": x_fit.tolist(),
        "y": y_fit.tolist(),
        "fits": results,
        "best_model": best_name,
    }


# ══════════════════════════════════════════════════════════════════
# SYSTEM 1: GL_2 vs GSp_4 congruence collapse
# ══════════════════════════════════════════════════════════════════

def system1_congruences():
    print("\n=== SYSTEM 1: GL_2 vs GSp_4 Congruence Collapse ===")

    # Known data
    gl2 = {2: 5000, 3: 800, 5: 190, 7: 50, 11: 2, 13: 0}  # approximate GL_2 counts
    gsp4 = {2: 733, 3: 37, 5: 0, 7: 0, 11: 0}

    # For GL_2: theoretical model N(ell) ~ C / ell^(k*P)
    # k=1 constraint per prime for GL_2, k=2 for GSp_4
    # Fit log N vs log ell to get effective k*P

    # GL_2 fit (use points where count > 0)
    gl2_ells = np.array([e for e, c in gl2.items() if c > 0], dtype=float)
    gl2_counts = np.array([c for c in gl2.values() if c > 0], dtype=float)

    gsp4_ells = np.array([e for e, c in gsp4.items() if c > 0], dtype=float)
    gsp4_counts = np.array([c for c in gsp4.values() if c > 0], dtype=float)

    # Fit power law: N = A * ell^(-alpha)
    # log N = log A - alpha * log ell

    def fit_power_slope(ells, counts, name):
        log_ell = np.log(ells)
        log_n = np.log(counts)
        # Linear regression
        slope, intercept = np.polyfit(log_ell, log_n, 1)
        r_squared = 1 - np.sum((log_n - (slope * log_ell + intercept))**2) / np.sum((log_n - np.mean(log_n))**2)
        print(f"  {name}: log-log slope = {slope:.3f} (effective k*P), R^2 = {r_squared:.4f}")
        return {"slope": float(slope), "intercept": float(intercept), "r_squared": float(r_squared)}

    gl2_fit = fit_power_slope(gl2_ells, gl2_counts, "GL_2")
    gsp4_fit = fit_power_slope(gsp4_ells, gsp4_counts, "GSp_4")

    # Ratio of slopes should reflect k_GSp4 / k_GL2 ~ 2
    slope_ratio = abs(gsp4_fit["slope"]) / abs(gl2_fit["slope"])
    print(f"  Slope ratio GSp_4/GL_2 = {slope_ratio:.3f} (theory predicts ~2.0)")

    # Also fit the exponential and super-exponential models
    gl2_model_fit = fit_models(gl2_ells, gl2_counts, "GL_2")
    gsp4_model_fit = fit_models(gsp4_ells, gsp4_counts, "GSp_4")

    result = {
        "gl2": {
            "data": {str(k): v for k, v in gl2.items()},
            "log_log_fit": gl2_fit,
            "model_fits": gl2_model_fit,
        },
        "gsp4": {
            "data": {str(k): v for k, v in gsp4.items()},
            "log_log_fit": gsp4_fit,
            "model_fits": gsp4_model_fit,
        },
        "slope_ratio": float(slope_ratio),
        "theory_prediction": 2.0,
        "interpretation": (
            f"GSp_4 collapses {slope_ratio:.1f}x faster than GL_2 in log-log. "
            f"Theory predicts 2x (k=2 vs k=1). "
            f"{'Consistent' if 1.5 < slope_ratio < 3.0 else 'Inconsistent'} with Hasse squeeze."
        ),
    }

    print(f"  Interpretation: {result['interpretation']}")
    return result


# ══════════════════════════════════════════════════════════════════
# SYSTEM 2: Lattice class numbers
# ══════════════════════════════════════════════════════════════════

def system2_lattices():
    print("\n=== SYSTEM 2: Lattice Class Numbers vs Dimension ===")

    path = BASE / "lmfdb_dump" / "lat_lattices.json"
    data = json.loads(path.read_text())
    columns = data["columns"]
    records = data["records"]

    dim_idx = columns.index("dim")
    cn_idx = columns.index("class_number")

    # Group by dimension
    dim_counts = defaultdict(int)
    dim_cn1 = defaultdict(int)

    for r in records:
        dim = r[dim_idx] if isinstance(r, list) else r["dim"]
        cn = r[cn_idx] if isinstance(r, list) else r["class_number"]
        cn_val = int(cn) if not isinstance(cn, int) else cn
        dim_counts[dim] += 1
        if cn_val == 1:
            dim_cn1[dim] += 1

    dims = sorted(dim_counts.keys())
    fractions = []
    dim_list = []
    for d in dims:
        if dim_counts[d] >= 5:  # need enough data
            f = dim_cn1[d] / dim_counts[d]
            fractions.append(f)
            dim_list.append(d)
            print(f"  dim={d}: {dim_counts[d]} lattices, {dim_cn1[d]} with class_number=1 ({f:.3f})")

    # Fit models
    model_fit = fit_models(dim_list, fractions, "lattice_cn1_fraction")

    # Also track class number distribution
    cn_dist = defaultdict(int)
    for r in records:
        cn = r[cn_idx] if isinstance(r, list) else r["class_number"]
        cn_val = int(cn) if not isinstance(cn, int) else cn
        cn_dist[cn_val] += 1

    top_cn = sorted(cn_dist.items(), key=lambda x: -x[1])[:10]
    print(f"  Top class numbers: {top_cn}")

    result = {
        "total_lattices": len(records),
        "dimensions": dim_list,
        "cn1_fractions": fractions,
        "counts_per_dim": {str(d): dim_counts[d] for d in dims},
        "cn1_per_dim": {str(d): dim_cn1[d] for d in dims},
        "model_fits": model_fit,
        "top_class_numbers": {str(k): v for k, v in top_cn},
        "collapse_observed": any(f < 0.1 for f in fractions[-3:]) if len(fractions) >= 3 else False,
    }
    return result


# ══════════════════════════════════════════════════════════════════
# SYSTEM 3: Number field discriminant growth
# ══════════════════════════════════════════════════════════════════

def system3_number_fields():
    print("\n=== SYSTEM 3: Number Field Counts vs Degree ===")

    path = BASE / "number_fields" / "data" / "number_fields.json"
    fields = json.loads(path.read_text())

    degree_counts = Counter()
    for f in fields:
        degree_counts[f["degree"]] += 1

    degrees = sorted(degree_counts.keys())
    counts = [degree_counts[d] for d in degrees]

    for d in degrees:
        print(f"  degree={d}: {degree_counts[d]} fields")

    model_fit = fit_models(degrees, counts, "number_fields_by_degree")

    result = {
        "total_fields": len(fields),
        "degrees": degrees,
        "counts": counts,
        "model_fits": model_fit,
        "collapse_observed": counts[-1] < counts[0] / 10 if counts else False,
        "interpretation": (
            "As degree grows with bounded discriminant, fewer fields exist. "
            "This follows from the Hermite bound: only finitely many fields of "
            "given degree with |disc| < B."
        ),
    }
    return result


# ══════════════════════════════════════════════════════════════════
# SYSTEM 4: OEIS sequence survival under constraints
# ══════════════════════════════════════════════════════════════════

def system4_oeis():
    print("\n=== SYSTEM 4: OEIS Sequence Survival Under Constraints ===")

    path = BASE / "oeis" / "data" / "stripped_full.gz"

    # Load sequences (sample for speed)
    sequences = {}
    with gzip.open(str(path), 'rt') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(' ,', 1)
            if len(parts) < 2:
                parts = line.split(',', 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0].strip()
            terms_str = parts[1].strip().rstrip(',')
            if not terms_str:
                continue
            try:
                terms = [int(t) for t in terms_str.split(',') if t.strip()]
                if len(terms) >= 5:
                    sequences[seq_id] = terms[:20]  # first 20 terms for speed
            except (ValueError, OverflowError):
                continue

    total = len(sequences)
    print(f"  Loaded {total} sequences with >= 5 terms")

    # Build prime sieve up to 10M for fast lookup
    SIEVE_LIMIT = 10_000_000
    sieve = bytearray(b'\x01') * (SIEVE_LIMIT + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(SIEVE_LIMIT**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    prime_set = set()  # only used for fallback

    def is_prime(n):
        if n < 2: return False
        if n <= SIEVE_LIMIT: return bool(sieve[n])
        # Trial division fallback for large n
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0: return False
            i += 6
        return True

    small_squares = [p*p for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]]

    def is_squarefree(n):
        if n == 0: return False
        n = abs(n)
        for sq in small_squares:
            if sq > n: break
            if n % sq == 0: return False
        return True

    # Constraint levels (cumulative):
    # 0: all sequences
    # 1: all terms >= 0 (non-negative)
    # 2: all terms > 0 (positive)
    # 3: all terms are squarefree
    # 4: all terms are prime (for terms > 1)
    # 5: terms are monotonically increasing
    # 6: consecutive differences are positive and increasing

    constraints = [
        ("all", lambda terms: True),
        ("non_negative", lambda terms: all(t >= 0 for t in terms)),
        ("positive", lambda terms: all(t > 0 for t in terms)),
        ("squarefree", lambda terms: all(is_squarefree(t) for t in terms if t != 0)),
        ("all_prime_gt1", lambda terms: all(
            (t <= SIEVE_LIMIT and is_prime(t)) or (t > SIEVE_LIMIT and False)
            for t in terms if t > 1
        ) and any(t > 1 for t in terms)),
        ("monotone_increasing", lambda terms: all(terms[i] < terms[i+1] for i in range(len(terms)-1))),
        ("increasing_gaps", lambda terms: len(terms) >= 3 and all(
            (terms[i+1] - terms[i]) < (terms[i+2] - terms[i+1]) for i in range(len(terms)-2)
        )),
    ]

    # Apply constraints cumulatively
    surviving = set(sequences.keys())
    constraint_levels = []
    survival_counts = []

    for i, (name, test) in enumerate(constraints):
        new_surviving = set()
        for sid in surviving:
            try:
                if test(sequences[sid]):
                    new_surviving.add(sid)
            except Exception:
                pass
        surviving = new_surviving
        constraint_levels.append(i)
        survival_counts.append(len(surviving))
        pct = 100 * len(surviving) / total if total > 0 else 0
        print(f"  Constraint {i} ({name}): {len(surviving)} survive ({pct:.1f}%)")

    model_fit = fit_models(constraint_levels, survival_counts, "oeis_survival")

    result = {
        "total_sequences": total,
        "constraint_names": [c[0] for c in constraints],
        "constraint_levels": constraint_levels,
        "survival_counts": survival_counts,
        "survival_fractions": [c / total for c in survival_counts],
        "model_fits": model_fit,
    }
    return result


# ══════════════════════════════════════════════════════════════════
# SYSTEM 5: Isogeny graph constraints
# ══════════════════════════════════════════════════════════════════

def system5_isogenies():
    print("\n=== SYSTEM 5: Isogeny Graph Supersingular Points ===")

    graph_dir = BASE / "isogenies" / "data" / "graphs"

    # Collect metadata for each prime
    prime_data = {}
    primes_dirs = sorted([d for d in os.listdir(str(graph_dir))
                          if os.path.isdir(str(graph_dir / d))],
                         key=lambda x: int(x))

    # Sample primes across the range
    sample_primes = primes_dirs[:50] + primes_dirs[::len(primes_dirs)//50 + 1]
    sample_primes = sorted(set(sample_primes), key=lambda x: int(x))[:100]

    for pdir in sample_primes:
        p = int(pdir)
        meta_path = graph_dir / pdir / f"{pdir}_metadata.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                nodes = meta.get("nodes", 0)
                # Deuring mass formula: ~(p-1)/12 supersingular j-invariants
                deuring_predicted = (p - 1) / 12.0
                prime_data[p] = {
                    "nodes": nodes,
                    "deuring_predicted": deuring_predicted,
                    "ratio": nodes / deuring_predicted if deuring_predicted > 0 else 0,
                }

                # Check ell-isogeny degree constraints
                ell_data = meta.get("ell", {})
                prime_data[p]["ell_constraints"] = {}
                for ell_str, ell_info in ell_data.items():
                    prime_data[p]["ell_constraints"][ell_str] = {
                        "diameter": ell_info.get("diameter", None),
                    }
            except Exception:
                pass

    primes = sorted(prime_data.keys())
    nodes_list = [prime_data[p]["nodes"] for p in primes]
    deuring_list = [prime_data[p]["deuring_predicted"] for p in primes]
    ratios = [prime_data[p]["ratio"] for p in primes]

    print(f"  Sampled {len(primes)} primes")
    print(f"  Node/Deuring ratio: mean={np.mean(ratios):.3f}, std={np.std(ratios):.3f}")

    # As ell grows, how does diameter shrink? (constraint tightening)
    ell_diameter_data = defaultdict(list)
    for p in primes:
        for ell_str, info in prime_data[p].get("ell_constraints", {}).items():
            if info["diameter"] is not None:
                ell_diameter_data[int(ell_str)].append(info["diameter"])

    ell_means = {}
    for ell in sorted(ell_diameter_data.keys()):
        diams = ell_diameter_data[ell]
        ell_means[ell] = np.mean(diams)
        print(f"  ell={ell}: mean diameter={np.mean(diams):.2f} (n={len(diams)})")

    # Fit diameter collapse as ell grows
    if len(ell_means) >= 3:
        ell_vals = list(ell_means.keys())
        diam_vals = list(ell_means.values())
        diameter_fit = fit_models(ell_vals, diam_vals, "isogeny_diameter_vs_ell")
    else:
        diameter_fit = {"error": "insufficient ell values"}

    result = {
        "n_primes_sampled": len(primes),
        "deuring_ratio_mean": float(np.mean(ratios)),
        "deuring_ratio_std": float(np.std(ratios)),
        "deuring_interpretation": (
            "Nodes closely track (p-1)/12 Deuring prediction"
            if abs(np.mean(ratios) - 1.0) < 0.2 else
            "Nodes deviate from Deuring prediction"
        ),
        "ell_diameter_means": {str(k): float(v) for k, v in ell_means.items()},
        "diameter_model_fits": diameter_fit,
        "sample_data": {str(p): prime_data[p] for p in primes[:10]},
    }
    return result


# ══════════════════════════════════════════════════════════════════
# SYSTEM 6 & 7: Synthesis
# ══════════════════════════════════════════════════════════════════

def synthesis(results):
    print("\n=== SYNTHESIS: Universal Scaling Law? ===")

    # Collect normalized collapse curves
    normalized_curves = {}

    for system_name, system_data in results.items():
        if system_name == "synthesis":
            continue

        mf = system_data.get("model_fits", system_data.get("diameter_model_fits"))
        if mf is None:
            # Try nested
            for key in ["gl2", "gsp4"]:
                if key in system_data:
                    mf = system_data[key].get("model_fits")
                    if mf and "x" in mf and "y" in mf:
                        x = np.array(mf["x"])
                        y = np.array(mf["y"])
                        # Normalize: x -> [0,1], y -> [0,1]
                        if len(x) > 1 and max(y) > 0:
                            x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else x
                            y_norm = y / y.max()
                            normalized_curves[f"{system_name}_{key}"] = {
                                "x_normalized": x_norm.tolist(),
                                "y_normalized": y_norm.tolist(),
                                "best_model": mf.get("best_model"),
                            }
            continue

        if mf and "x" in mf and "y" in mf:
            x = np.array(mf["x"])
            y = np.array(mf["y"])
            if len(x) > 1 and max(y) > 0:
                x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else x
                y_norm = y / y.max()
                normalized_curves[system_name] = {
                    "x_normalized": x_norm.tolist(),
                    "y_normalized": y_norm.tolist(),
                    "best_model": mf.get("best_model"),
                }

    # Determine best model across systems
    model_votes = Counter()
    for name, curve in normalized_curves.items():
        if curve.get("best_model"):
            model_votes[curve["best_model"]] += 1
            print(f"  {name}: best model = {curve['best_model']}")

    dominant_model = model_votes.most_common(1)[0] if model_votes else ("none", 0)

    print(f"\n  Model votes: {dict(model_votes)}")
    print(f"  Dominant model: {dominant_model[0]} ({dominant_model[1]} systems)")

    # Check if collapse is universal
    all_collapse = True
    for name, sdata in results.items():
        if name == "synthesis":
            continue
        if isinstance(sdata, dict):
            co = sdata.get("collapse_observed")
            if co is not None and not co:
                all_collapse = False

    synth = {
        "normalized_curves": normalized_curves,
        "model_votes": dict(model_votes),
        "dominant_model": dominant_model[0],
        "universal_collapse": all_collapse,
        "interpretation": (
            f"The dominant decay model across {len(normalized_curves)} systems is "
            f"'{dominant_model[0]}'. "
            f"{'All systems show collapse under increasing constraints.' if all_collapse else 'Not all systems show clear collapse.'} "
            f"The Hasse squeeze mechanism — independent constraints per prime "
            f"producing super-exponential solution-space shrinkage — "
            f"{'appears' if dominant_model[0] == 'super_exponential' else 'does not clearly appear'} "
            f"universal across these mathematical domains."
        ),
    }

    print(f"\n  VERDICT: {synth['interpretation']}")
    return synth


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("C10: Constraint Collapse Phenomena — Generalizing the Hasse Squeeze")
    print("=" * 70)

    results = {}

    # System 1
    results["congruence_collapse"] = system1_congruences()

    # System 2
    results["lattice_class_numbers"] = system2_lattices()

    # System 3
    results["number_field_counts"] = system3_number_fields()

    # System 4
    results["oeis_survival"] = system4_oeis()

    # System 5
    results["isogeny_graphs"] = system5_isogenies()

    # Synthesis
    results["synthesis"] = synthesis(results)

    # Save results
    out_path = Path(__file__).parent / "constraint_collapse_results.json"
    with open(str(out_path), "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {out_path}")
    print("Done.")


if __name__ == "__main__":
    main()
