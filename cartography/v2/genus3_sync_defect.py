"""
Genus-3 Frobenius Synchronization Defect (ChatGPT Harder #11)

Measures deviation from perfect phase locking across primes for
genus-3 Frobenius eigenvalues.

For each curve:
  1. Normalize traces: x_p = a_p / (2*g*sqrt(p)) where g=3
     This maps to [-1, 1] (single phase cycle), appropriate for genus-3
  2. Phase coherence: R = |mean(exp(2*pi*i * x_p))| across primes
  3. Null model: USp(6) Sato-Tate iid draws (1000 Monte Carlo fake curves)
  4. Synchronization defect = 1 - R_observed / R_null
     (0 = matches null, positive = less coherent)
"""

import json
import numpy as np
from pathlib import Path

# ── paths ──
DATA_PATH = Path(__file__).parent.parent / "shared" / "scripts" / "v2" / "genus3_sage_output.json"
OUT_JSON = Path(__file__).parent / "genus3_sync_defect_results.json"

np.random.seed(42)
GENUS = 3
N_NULL = 1000


def load_data():
    with open(DATA_PATH) as f:
        data = json.load(f)
    return data["results"]


def phase_coherence(x_vals):
    """R = |mean(exp(2*pi*i * x))|"""
    phases = np.exp(2j * np.pi * np.array(x_vals))
    return float(np.abs(np.mean(phases)))


def usp6_rejection_sample(n_samples, rng):
    """
    Sample traces from USp(6) Haar measure via rejection sampling.
    The Weyl integration formula gives density proportional to:
      prod_{i<j}(cos(t_i) - cos(t_j))^2 * prod_i sin^2(t_i)
    for angles t_i in [0, pi].
    Trace = 2*(cos(t_1) + cos(t_2) + cos(t_3)), range [-6, 6].
    """
    traces = []
    batch = max(n_samples * 20, 5000)
    while len(traces) < n_samples:
        thetas = rng.uniform(0, np.pi, size=(batch, 3))
        cos_t = np.cos(thetas)
        sin_t = np.sin(thetas)

        d01 = (cos_t[:, 0] - cos_t[:, 1]) ** 2
        d02 = (cos_t[:, 0] - cos_t[:, 2]) ** 2
        d12 = (cos_t[:, 1] - cos_t[:, 2]) ** 2
        vander = d01 * d02 * d12
        sin2 = np.prod(sin_t ** 2, axis=1)
        weight = vander * sin2

        max_w = weight.max()
        if max_w == 0:
            continue
        accept = rng.uniform(0, max_w, size=batch) < weight
        raw_traces = 2.0 * cos_t[accept].sum(axis=1)
        traces.extend(raw_traces.tolist())

    return np.array(traces[:n_samples])


def main():
    results_list = load_data()
    rng = np.random.default_rng(42)

    curve_results = []
    all_R_obs = []
    all_R_obs_raw = []

    for curve in results_list:
        cid = curve["id"]
        a_p = curve["a_p"]
        primes = sorted(int(p) for p in a_p.keys())
        n_primes = len(primes)

        # ── Primary: genus-aware normalization x_p = a_p / (2*g*sqrt(p)) ──
        # Maps to [-1, 1], single phase cycle
        x_p = [int(a_p[str(p)]) / (2.0 * GENUS * np.sqrt(p)) for p in primes]
        R_obs = phase_coherence(x_p)
        all_R_obs.append(R_obs)

        # ── Secondary: raw normalization x_p = a_p / (2*sqrt(p)) ──
        x_p_raw = [int(a_p[str(p)]) / (2.0 * np.sqrt(p)) for p in primes]
        R_obs_raw = phase_coherence(x_p_raw)
        all_R_obs_raw.append(R_obs_raw)

        # ── Null: USp(6) Sato-Tate ──
        R_nulls = []
        R_nulls_raw = []
        for _ in range(N_NULL):
            null_traces = usp6_rejection_sample(n_primes, rng)
            # Genus-aware: trace / (2*g) maps to [-1, 1]
            x_null = null_traces / (2.0 * GENUS)
            R_nulls.append(phase_coherence(x_null))
            # Raw: trace / 2 maps to [-3, 3]
            x_null_raw = null_traces / 2.0
            R_nulls_raw.append(phase_coherence(x_null_raw))

        R_null_mean = float(np.mean(R_nulls))
        R_null_std = float(np.std(R_nulls))

        R_null_raw_mean = float(np.mean(R_nulls_raw))

        # Synchronization defect (primary)
        defect = 1.0 - R_obs / R_null_mean if R_null_mean > 0 else 0.0
        z_score = (R_obs - R_null_mean) / R_null_std if R_null_std > 0 else 0.0

        # Defect (raw)
        defect_raw = 1.0 - R_obs_raw / R_null_raw_mean if R_null_raw_mean > 0 else 0.0

        curve_results.append({
            "id": cid,
            "n_primes": n_primes,
            "R_observed": round(R_obs, 6),
            "R_null_mean": round(R_null_mean, 6),
            "R_null_std": round(R_null_std, 6),
            "sync_defect": round(defect, 6),
            "z_score": round(z_score, 4),
            "R_observed_raw": round(R_obs_raw, 6),
            "sync_defect_raw": round(defect_raw, 6),
        })

    # Aggregate
    defects = [c["sync_defect"] for c in curve_results]
    defects_raw = [c["sync_defect_raw"] for c in curve_results]
    z_scores = [c["z_score"] for c in curve_results]

    summary = {
        "description": "Genus-3 Frobenius synchronization defect (ChatGPT Harder #11)",
        "method": (
            "Phase coherence R = |mean(exp(2*pi*i * x_p))| where "
            "x_p = a_p/(2*g*sqrt(p)) with g=3 (genus-aware, single-cycle normalization)"
        ),
        "secondary_method": "Also computed with x_p = a_p/(2*sqrt(p)) (raw, multi-wrap)",
        "null_model": f"USp(6) Sato-Tate rejection sampling, {N_NULL} Monte Carlo curves per real curve",
        "defect_formula": "1 - R_observed / R_null_mean (0 = matches null, positive = less coherent)",
        "n_curves": len(curve_results),
        "aggregate": {
            "defect_mean": round(float(np.mean(defects)), 6),
            "defect_median": round(float(np.median(defects)), 6),
            "defect_std": round(float(np.std(defects)), 6),
            "defect_min": round(float(np.min(defects)), 6),
            "defect_max": round(float(np.max(defects)), 6),
            "defect_q25": round(float(np.percentile(defects, 25)), 6),
            "defect_q75": round(float(np.percentile(defects, 75)), 6),
            "defect_raw_mean": round(float(np.mean(defects_raw)), 6),
            "defect_raw_median": round(float(np.median(defects_raw)), 6),
            "R_observed_mean": round(float(np.mean(all_R_obs)), 6),
            "R_observed_std": round(float(np.std(all_R_obs)), 6),
            "z_score_mean": round(float(np.mean(z_scores)), 4),
            "z_score_std": round(float(np.std(z_scores)), 4),
            "n_significant_z2": sum(1 for z in z_scores if abs(z) > 2),
        },
        "curves": curve_results,
    }

    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    print("Genus-3 Frobenius Synchronization Defect")
    print("=" * 50)
    print(f"Curves analyzed: {len(curve_results)}")
    print(f"Null model: USp(6) Sato-Tate, {N_NULL} MC samples/curve")
    print()
    print("Primary (genus-aware, x_p = a_p/(6*sqrt(p))):")
    print(f"  Defect mean:   {np.mean(defects):.4f}")
    print(f"  Defect median: {np.median(defects):.4f}")
    print(f"  Defect std:    {np.std(defects):.4f}")
    print(f"  Defect range:  [{np.min(defects):.4f}, {np.max(defects):.4f}]")
    print(f"  Defect IQR:    [{np.percentile(defects, 25):.4f}, {np.percentile(defects, 75):.4f}]")
    print(f"  R_obs mean:    {np.mean(all_R_obs):.4f}")
    print()
    print("Secondary (raw, x_p = a_p/(2*sqrt(p))):")
    print(f"  Defect mean:   {np.mean(defects_raw):.4f}")
    print(f"  Defect median: {np.median(defects_raw):.4f}")
    print()
    print(f"Z-scores: mean={np.mean(z_scores):.4f}, std={np.std(z_scores):.4f}")
    print(f"Significant |z| > 2: {sum(1 for z in z_scores if abs(z) > 2)} / {len(z_scores)}")
    print()
    print(f"Results saved to {OUT_JSON}")


if __name__ == "__main__":
    main()
