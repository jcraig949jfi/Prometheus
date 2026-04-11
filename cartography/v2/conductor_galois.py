"""
Conductor Factorization Fingerprint vs Galois Image

Does the prime factorization pattern of an EC's conductor predict its
Galois image type? We build a "conductor fingerprint" — the vector of
exponents [e_2, e_3, e_5, e_7, ...] for the first 10 primes — and test
whether these fingerprints cluster by Galois image classification.

Galois image sources:
  1. CM discriminant (cm field): CM vs non-CM, and finer CM classes
  2. Isogeny structure: maximal isogeny degree as proxy for Borel subgroup
  3. Cross-reference with galois_image_portraits.py results (mod-ell portraits)

Metrics: MI, ARI, enrichment, per-prime discriminative power.
Null: 1000 random permutations of Galois labels.
"""

import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
PORTRAIT_PATH = REPO_ROOT / "cartography" / "shared" / "scripts" / "v2" / "galois_image_results.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "conductor_galois_results.json"

FIRST_10_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
N_PERMUTATIONS = 1000


def factorize(n):
    """Return dict of {prime: exponent} for n."""
    factors = {}
    if n <= 1:
        return factors
    for p in FIRST_10_PRIMES:
        if p * p > n and n > 1:
            break
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
    # remaining large prime factor (not in first 10)
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def conductor_fingerprint(conductor):
    """Exponent vector for first 10 primes."""
    facts = factorize(conductor)
    return tuple(facts.get(p, 0) for p in FIRST_10_PRIMES)


def mutual_information(labels_x, labels_y):
    """Compute MI between two label arrays."""
    n = len(labels_x)
    if n == 0:
        return 0.0
    cx = Counter(labels_x)
    cy = Counter(labels_y)
    cxy = Counter(zip(labels_x, labels_y))

    mi = 0.0
    for (x, y), nxy in cxy.items():
        px = cx[x] / n
        py = cy[y] / n
        pxy = nxy / n
        if pxy > 0 and px > 0 and py > 0:
            mi += pxy * math.log2(pxy / (px * py))
    return mi


def entropy(labels):
    """Shannon entropy in bits."""
    n = len(labels)
    if n == 0:
        return 0.0
    counts = Counter(labels)
    h = 0.0
    for c in counts.values():
        p = c / n
        if p > 0:
            h -= p * math.log2(p)
    return h


def adjusted_rand_index(labels_x, labels_y):
    """Compute ARI between two clusterings."""
    n = len(labels_x)
    if n < 2:
        return 0.0

    # Build contingency table
    cx_vals = sorted(set(labels_x))
    cy_vals = sorted(set(labels_y))
    cx_map = {v: i for i, v in enumerate(cx_vals)}
    cy_map = {v: i for i, v in enumerate(cy_vals)}

    contingency = np.zeros((len(cx_vals), len(cy_vals)), dtype=np.int64)
    for x, y in zip(labels_x, labels_y):
        contingency[cx_map[x], cy_map[y]] += 1

    # Row and column sums
    a = contingency.sum(axis=1)
    b = contingency.sum(axis=0)

    # Combinations
    def comb2(x):
        return x * (x - 1) / 2

    sum_comb_nij = sum(comb2(contingency[i, j])
                       for i in range(len(cx_vals))
                       for j in range(len(cy_vals)))
    sum_comb_a = sum(comb2(ai) for ai in a)
    sum_comb_b = sum(comb2(bj) for bj in b)
    comb_n = comb2(n)

    if comb_n == 0:
        return 0.0

    expected = sum_comb_a * sum_comb_b / comb_n
    max_index = 0.5 * (sum_comb_a + sum_comb_b)

    if max_index == expected:
        return 1.0 if sum_comb_nij == expected else 0.0

    ari = (sum_comb_nij - expected) / (max_index - expected)
    return ari


def per_prime_mi(fingerprints, galois_labels):
    """MI between each individual prime exponent and galois labels."""
    results = {}
    for i, p in enumerate(FIRST_10_PRIMES):
        exponents = [fp[i] for fp in fingerprints]
        mi = mutual_information(exponents, galois_labels)
        h_exp = entropy(exponents)
        h_gal = entropy(galois_labels)
        nmi = mi / min(h_exp, h_gal) if min(h_exp, h_gal) > 0 else 0.0
        results[str(p)] = {
            "mi_bits": round(mi, 6),
            "nmi": round(nmi, 6),
            "h_exponent": round(h_exp, 4),
            "exponent_distribution": dict(Counter(exponents).most_common(10))
        }
    return results


def enrichment_analysis(fingerprints, galois_labels):
    """For each galois class, find overrepresented fingerprint patterns."""
    fp_by_class = defaultdict(list)
    for fp, gl in zip(fingerprints, galois_labels):
        fp_by_class[gl].append(fp)

    global_dist = Counter(fingerprints)
    n_total = len(fingerprints)

    results = {}
    for gl, fps in fp_by_class.items():
        n_class = len(fps)
        class_dist = Counter(fps)
        enrichments = []
        for fp, count in class_dist.most_common(10):
            expected = global_dist[fp] / n_total * n_class
            if expected > 0:
                enrichment = count / expected
                enrichments.append({
                    "fingerprint": [int(x) for x in fp],
                    "count": count,
                    "expected": round(expected, 2),
                    "enrichment": round(enrichment, 3)
                })
        results[gl] = {
            "n_curves": n_class,
            "top_enriched": sorted(enrichments, key=lambda x: -x["enrichment"])[:5]
        }
    return results


def build_galois_classification(rows, portrait_map):
    """
    Build a multi-level Galois image classification:
    Level 1: CM vs non-CM
    Level 2: CM discriminant / non-CM isogeny type
    Level 3: Cross-reference with mod-ell portrait if available
    """
    classifications = {"level1": [], "level2": [], "level3": []}

    for label, conductor, cm, isogeny_degrees, torsion in rows:
        # Level 1: CM vs non-CM
        l1 = "CM" if cm != 0 else "non-CM"
        classifications["level1"].append(l1)

        # Level 2: finer
        if cm != 0:
            l2 = f"CM_{cm}"
        else:
            max_isog = max(isogeny_degrees) if isogeny_degrees else 1
            if max_isog == 1:
                l2 = "non-CM_trivial_isog"
            elif max_isog <= 4:
                l2 = f"non-CM_isog_{max_isog}"
            else:
                l2 = f"non-CM_isog_{max_isog}+"

        classifications["level2"].append(l2)

        # Level 3: use portrait if available
        # EC label N.iso_class.number -> MF label N.2.a.iso_letter
        # We map by conductor since isogeny class -> single newform
        iso_label = label.rsplit(".", 1)[0]  # e.g. "11.a" from "11.a1"
        # Translate: 11.a -> 11.2.a.a
        parts = iso_label.split(".")
        if len(parts) == 2:
            mf_label = f"{parts[0]}.2.a.{parts[1]}"
        else:
            mf_label = None

        portrait_class = portrait_map.get(mf_label, "unknown")
        if portrait_class != "unknown":
            l3 = portrait_class
        else:
            l3 = l2  # fallback to level 2
        classifications["level3"].append(l3)

    return classifications


def main():
    t0 = time.time()

    # Load EC data
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, conductor, cm, isogeny_degrees, torsion
        FROM elliptic_curves
        ORDER BY conductor
    """).fetchall()
    con.close()
    print(f"Loaded {len(rows)} elliptic curves")

    # Load portrait classifications
    portrait_map = {}
    if PORTRAIT_PATH.exists():
        with open(PORTRAIT_PATH) as f:
            portrait_data = json.load(f)
        for sample in portrait_data.get("sample_classifications", []):
            portrait_map[sample["label"]] = sample["combined_class"]
        print(f"Loaded {len(portrait_map)} portrait classifications")

    # Build conductor fingerprints
    conductors = [r[1] for r in rows]
    fingerprints = [conductor_fingerprint(c) for c in conductors]
    n_unique_fp = len(set(fingerprints))
    print(f"Unique fingerprints: {n_unique_fp}")

    # Build Galois classifications
    classifications = build_galois_classification(rows, portrait_map)

    results = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "n_curves": len(rows),
            "n_unique_fingerprints": n_unique_fp,
            "primes_used": FIRST_10_PRIMES,
            "n_permutations": N_PERMUTATIONS
        },
        "levels": {}
    }

    # Analyze each classification level
    for level_name in ["level1", "level2", "level3"]:
        galois_labels = classifications[level_name]
        label_dist = Counter(galois_labels)
        print(f"\n=== {level_name} ===")
        print(f"Classes: {len(label_dist)}")
        for cls, cnt in label_dist.most_common(10):
            print(f"  {cls}: {cnt}")

        # Discretize fingerprints to strings for MI/ARI
        fp_strings = ["_".join(str(x) for x in fp) for fp in fingerprints]

        # Observed MI
        mi_obs = mutual_information(fp_strings, galois_labels)
        h_fp = entropy(fp_strings)
        h_gal = entropy(galois_labels)
        nmi_obs = mi_obs / min(h_fp, h_gal) if min(h_fp, h_gal) > 0 else 0.0

        # ARI between fingerprint clusters and galois labels
        ari_obs = adjusted_rand_index(fp_strings, galois_labels)

        # Per-prime analysis
        pp_mi = per_prime_mi(fingerprints, galois_labels)

        # Enrichment
        enrichment = enrichment_analysis(fingerprints, galois_labels)

        # Null distribution: permute galois labels
        rng = np.random.default_rng(42)
        mi_null = []
        ari_null = []
        galois_arr = np.array(galois_labels)
        for _ in range(N_PERMUTATIONS):
            perm = rng.permutation(galois_arr)
            perm_list = perm.tolist()
            mi_null.append(mutual_information(fp_strings, perm_list))
            ari_null.append(adjusted_rand_index(fp_strings, perm_list))

        mi_null = np.array(mi_null)
        ari_null = np.array(ari_null)
        mi_z = (mi_obs - mi_null.mean()) / mi_null.std() if mi_null.std() > 0 else 0.0
        ari_z = (ari_obs - ari_null.mean()) / ari_null.std() if ari_null.std() > 0 else 0.0

        # Per-prime null
        pp_null_mi = {str(p): [] for p in FIRST_10_PRIMES}
        for _ in range(N_PERMUTATIONS):
            perm = rng.permutation(galois_arr).tolist()
            for i, p in enumerate(FIRST_10_PRIMES):
                exponents = [fp[i] for fp in fingerprints]
                pp_null_mi[str(p)].append(mutual_information(exponents, perm))

        pp_results = {}
        for p_str, obs in pp_mi.items():
            null_vals = np.array(pp_null_mi[p_str])
            z = (obs["mi_bits"] - null_vals.mean()) / null_vals.std() if null_vals.std() > 0 else 0.0
            pp_results[p_str] = {
                **obs,
                "null_mean": round(float(null_vals.mean()), 6),
                "null_std": round(float(null_vals.std()), 6),
                "z_score": round(float(z), 2)
            }

        # Rank primes by z-score
        ranked_primes = sorted(pp_results.items(), key=lambda x: -x[1]["z_score"])
        most_discriminative = [{"prime": int(p), "z_score": v["z_score"], "mi_bits": v["mi_bits"], "nmi": v["nmi"]}
                               for p, v in ranked_primes]

        print(f"\nMI = {mi_obs:.6f} bits (z = {mi_z:.1f})")
        print(f"NMI = {nmi_obs:.6f}")
        print(f"ARI = {ari_obs:.6f} (z = {ari_z:.1f})")
        print(f"Most discriminative primes: {[x['prime'] for x in most_discriminative[:3]]}")

        level_result = {
            "n_classes": len(label_dist),
            "class_distribution": {k: v for k, v in label_dist.most_common()},
            "mi_bits": round(mi_obs, 6),
            "nmi": round(nmi_obs, 6),
            "h_fingerprint": round(h_fp, 4),
            "h_galois": round(h_gal, 4),
            "ari": round(ari_obs, 6),
            "null_mi_mean": round(float(mi_null.mean()), 6),
            "null_mi_std": round(float(mi_null.std()), 6),
            "mi_z_score": round(float(mi_z), 2),
            "null_ari_mean": round(float(ari_null.mean()), 6),
            "null_ari_std": round(float(ari_null.std()), 6),
            "ari_z_score": round(float(ari_z), 2),
            "per_prime": pp_results,
            "most_discriminative_primes": most_discriminative,
            "enrichment_by_class": {k: v for k, v in enrichment.items()
                                    if v["n_curves"] >= 5}  # skip tiny classes
        }
        results["levels"][level_name] = level_result

    # Summary
    l1 = results["levels"]["level1"]
    l2 = results["levels"]["level2"]
    l3 = results["levels"]["level3"]
    results["summary"] = {
        "level1_CM_vs_nonCM": {
            "mi_bits": l1["mi_bits"],
            "mi_z": l1["mi_z_score"],
            "ari": l1["ari"],
            "ari_z": l1["ari_z_score"],
            "verdict": "significant" if l1["mi_z_score"] > 5 else "weak" if l1["mi_z_score"] > 2 else "not significant"
        },
        "level2_fine_classification": {
            "mi_bits": l2["mi_bits"],
            "mi_z": l2["mi_z_score"],
            "ari": l2["ari"],
            "ari_z": l2["ari_z_score"],
            "verdict": "significant" if l2["mi_z_score"] > 5 else "weak" if l2["mi_z_score"] > 2 else "not significant"
        },
        "level3_portrait_enhanced": {
            "mi_bits": l3["mi_bits"],
            "mi_z": l3["mi_z_score"],
            "ari": l3["ari"],
            "ari_z": l3["ari_z_score"],
            "verdict": "significant" if l3["mi_z_score"] > 5 else "weak" if l3["mi_z_score"] > 2 else "not significant"
        },
        "top_discriminative_primes_level2": [
            x["prime"] for x in l2["most_discriminative_primes"][:5]
        ],
        "interpretation": (
            "Conductor factorization fingerprints encode bad reduction type. "
            "CM curves have specific conductor constraints (e.g., CM by -3 forces 3|N with specific exponent). "
            "Non-CM isogeny structure correlates with conductor via rational isogenies requiring specific bad primes. "
            "The question is whether this is structurally informative beyond the tautological constraint."
        )
    }

    elapsed = time.time() - t0
    results["metadata"]["elapsed_seconds"] = round(elapsed, 1)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
