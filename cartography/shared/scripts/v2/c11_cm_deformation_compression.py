"""
Challenge 11: Compress CM Deformation Paths via ST Ratio
==========================================================
CM curves have M₂/M₄ = 1.46 (USp(4)-consistent).
Within CM families at the same level, do deformation paths collapse
to 1D when projected onto the M₂/M₄ = 1.46 constraint surface?
"""
import json, time, math
import numpy as np
import duckdb
from scipy import stats
from pathlib import Path
from collections import defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "c11_cm_compression_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def prime_factors(n):
    f = set(); d = 2
    while d*d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f

def main():
    t0 = time.time()
    print("=== C11: Compress CM Deformation via ST Ratio ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level
    """).fetchall()
    con.close()

    ap_primes = sieve(50)
    N_AP = 15

    # Build data structures
    by_level = defaultdict(list)
    for label, level, ap_json, is_cm in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap[:N_AP]]
        if len(ap_vals) < N_AP: continue
        bad = prime_factors(level)
        # Compute normalized moments
        good_vals = []
        for i, p in enumerate(ap_primes[:N_AP]):
            if i < len(ap_vals) and p not in bad:
                bound = 2 * math.sqrt(p)
                if bound > 0: good_vals.append(ap_vals[i] / bound)
        if len(good_vals) < 8: continue
        arr = np.array(good_vals)
        m2 = float(np.mean(arr**2))
        m4 = float(np.mean(arr**4))
        ratio = m2 / m4 if m4 > 0 else 0

        by_level[level].append({
            "label": label, "ap": np.array(ap_vals, dtype=float),
            "is_cm": bool(is_cm), "m2": m2, "m4": m4, "ratio": ratio,
        })

    # Separate CM and non-CM families
    cm_families = defaultdict(list)
    ncm_families = defaultdict(list)
    for level, group in by_level.items():
        cm = [f for f in group if f["is_cm"]]
        ncm = [f for f in group if not f["is_cm"]]
        if len(cm) >= 3: cm_families[level] = cm
        if len(ncm) >= 3: ncm_families[level] = ncm

    print(f"  CM families (≥3 forms): {len(cm_families)}")
    print(f"  Non-CM families (≥3 forms): {len(ncm_families)}")

    # PCA on raw a_p for CM families
    cm_pc1_raw = []
    cm_pc1_compressed = []
    for level, group in cm_families.items():
        X = np.array([g["ap"] for g in group])
        X_c = X - X.mean(axis=0)
        U, S, Vt = np.linalg.svd(X_c, full_matrices=False)
        raw_pc1 = float(S[0]**2 / np.sum(S**2))
        cm_pc1_raw.append(raw_pc1)

        # Compress: project onto constraint surface M₂/M₄ ≈ 1.46
        # Weight each form by how close its ratio is to 1.46
        TARGET_RATIO = 1.46
        weights = np.array([np.exp(-10 * (g["ratio"] - TARGET_RATIO)**2) for g in group])
        weights /= weights.sum()
        X_w = X_c * weights[:, None]
        Uw, Sw, Vtw = np.linalg.svd(X_w, full_matrices=False)
        comp_pc1 = float(Sw[0]**2 / np.sum(Sw**2)) if np.sum(Sw**2) > 0 else 0
        cm_pc1_compressed.append(comp_pc1)

    # Same for non-CM
    ncm_pc1_raw = []
    ncm_pc1_compressed = []
    TARGET_NCM = 2.25
    for level, group in ncm_families.items():
        X = np.array([g["ap"] for g in group])
        X_c = X - X.mean(axis=0)
        U, S, Vt = np.linalg.svd(X_c, full_matrices=False)
        raw_pc1 = float(S[0]**2 / np.sum(S**2))
        ncm_pc1_raw.append(raw_pc1)

        weights = np.array([np.exp(-10 * (g["ratio"] - TARGET_NCM)**2) for g in group])
        weights /= weights.sum()
        X_w = X_c * weights[:, None]
        Uw, Sw, Vtw = np.linalg.svd(X_w, full_matrices=False)
        comp_pc1 = float(Sw[0]**2 / np.sum(Sw**2)) if np.sum(Sw**2) > 0 else 0
        ncm_pc1_compressed.append(comp_pc1)

    print(f"\n  CM families:")
    print(f"    Raw PC1: mean={np.mean(cm_pc1_raw):.4f}")
    print(f"    ST-compressed PC1: mean={np.mean(cm_pc1_compressed):.4f}")
    print(f"    Compression gain: {np.mean(cm_pc1_compressed)/np.mean(cm_pc1_raw):.2f}x")

    print(f"\n  Non-CM families:")
    print(f"    Raw PC1: mean={np.mean(ncm_pc1_raw):.4f}")
    print(f"    ST-compressed PC1: mean={np.mean(ncm_pc1_compressed):.4f}")
    print(f"    Compression gain: {np.mean(ncm_pc1_compressed)/np.mean(ncm_pc1_raw):.2f}x")

    # M₂/M₄ variation within families
    cm_ratio_cv = []
    for level, group in cm_families.items():
        ratios = [g["ratio"] for g in group]
        if np.mean(ratios) > 0:
            cm_ratio_cv.append(float(np.std(ratios) / np.mean(ratios)))

    ncm_ratio_cv = []
    for level, group in ncm_families.items():
        ratios = [g["ratio"] for g in group]
        if np.mean(ratios) > 0:
            ncm_ratio_cv.append(float(np.std(ratios) / np.mean(ratios)))

    print(f"\n  M₂/M₄ within-family CV:")
    print(f"    CM: {np.mean(cm_ratio_cv):.4f}")
    print(f"    Non-CM: {np.mean(ncm_ratio_cv):.4f}")

    # Does ST ratio separate CM families into lower dimension?
    collapsed = sum(1 for p in cm_pc1_compressed if p > 0.8)
    total_cm = len(cm_pc1_compressed)
    collapse_rate = collapsed / total_cm if total_cm > 0 else 0

    elapsed = time.time() - t0
    output = {
        "challenge": "C11", "title": "CM Deformation Compression via ST Ratio",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_cm_families": len(cm_families),
        "n_ncm_families": len(ncm_families),
        "cm_raw_pc1": round(float(np.mean(cm_pc1_raw)), 4),
        "cm_compressed_pc1": round(float(np.mean(cm_pc1_compressed)), 4),
        "cm_compression_gain": round(float(np.mean(cm_pc1_compressed)/max(np.mean(cm_pc1_raw),1e-6)), 4),
        "ncm_raw_pc1": round(float(np.mean(ncm_pc1_raw)), 4),
        "ncm_compressed_pc1": round(float(np.mean(ncm_pc1_compressed)), 4),
        "cm_ratio_cv": round(float(np.mean(cm_ratio_cv)), 4) if cm_ratio_cv else None,
        "ncm_ratio_cv": round(float(np.mean(ncm_ratio_cv)), 4) if ncm_ratio_cv else None,
        "collapse_rate": round(collapse_rate, 4),
        "assessment": None,
    }

    cm_gain = float(np.mean(cm_pc1_compressed)/max(np.mean(cm_pc1_raw),1e-6))
    ncm_gain = float(np.mean(ncm_pc1_compressed)/max(np.mean(ncm_pc1_raw),1e-6))
    if cm_gain > 1.3 and collapse_rate > 0.5:
        output["assessment"] = (
            f"COLLAPSE ACHIEVED: ST regularization compresses CM PC1 from {np.mean(cm_pc1_raw):.0%} to "
            f"{np.mean(cm_pc1_compressed):.0%} ({cm_gain:.1f}x gain). {collapse_rate:.0%} of families "
            f"collapse to single trajectory. The M₂/M₄=1.46 constraint IS a structural compressor.")
    elif cm_gain > 1.1:
        output["assessment"] = (
            f"PARTIAL COMPRESSION: CM gain={cm_gain:.2f}x (PC1 {np.mean(cm_pc1_raw):.0%}→{np.mean(cm_pc1_compressed):.0%}). "
            f"Non-CM gain={ncm_gain:.2f}x. ST ratio helps but does not fully collapse deformations.")
    else:
        output["assessment"] = (
            f"NO COMPRESSION: ST regularization does NOT collapse CM deformations "
            f"(gain={cm_gain:.2f}x). PC1 remains at {np.mean(cm_pc1_compressed):.0%}. "
            f"Deformation paths are ORTHOGONAL to the M₂/M₄ constraint — they vary in a subspace invisible to moments.")

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
