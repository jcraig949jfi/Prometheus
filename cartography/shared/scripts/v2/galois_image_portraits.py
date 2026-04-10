"""
R3-2: Galois Image Portrait Classification from Trace Density

Classifies the mod-ell Galois image of each dim=1 weight-2 modular form
by comparing the empirical a_p mod ell distribution to theoretical templates
for the 63 possible images in GL_2(F_ell) (Zywina 2015).

Image types at each ell:
  - Full (GL_2 or SL_2): near-uniform distribution
  - Borel (rational isogeny): concentration on QR classes + 0
  - Split Cartan (CM, split): a_p = 0 for inert primes, nonzero for split
  - Nonsplit Cartan (CM, nonsplit): similar to split but different character
  - Normalizer of Cartan: intermediate zero-frequency
  - Exceptional (A4, S4, A5): rare, specific distributions

Uses chi-squared distance to classify each form at each ell, then
merges across ell=2,3,5,7 for a combined portrait.
"""

import json
import math
import time
from collections import Counter
from pathlib import Path

import duckdb
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[4]
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
OUTPUT_PATH = Path(__file__).resolve().parent / "galois_image_results.json"

# Prior results for cross-validation
STARVATION_PATH = Path(__file__).resolve().parent / "residue_starvation_results.json"
CT4_PATH = Path(__file__).resolve().parent / "symmetry_detection_results.json"
CT1_PATH = Path(__file__).resolve().parent / "residual_rep_results.json"


def sieve(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i):
                s[j] = False
    return [i for i in range(2, n + 1) if s[i]]


PRIMES = sieve(997)
TEST_ELLS = [2, 3, 5, 7]
MIN_GOOD = 30


# --- Theoretical templates ---

def qr_set(ell):
    """Quadratic residues mod ell (including 0)."""
    return {(x * x) % ell for x in range(ell)}


def build_templates(ell):
    """
    Build theoretical trace distribution templates for each image type at mod ell.
    Returns dict of {name: probability_vector} where vector has length ell.

    Key insight: exceptional images (A4, S4, A5) are extremely rare and their
    marginal a_p mod ell distributions are nearly indistinguishable from full
    GL_2. We classify the four main types (full, borel, cartan, norm_cartan)
    and flag "exceptional" only when the form doesn't match ANY main template
    well but also isn't CM.

    For dim=1 weight-2 newforms over Q:
    - Full: ~1/ell per residue class (Chebotarev for GL_2)
    - Borel: a_p = alpha(p) + beta(p), concentrates on 0 + QR classes
    - Cartan (CM): a_p = 0 for density 1/2 of primes (inert), rest uniform
    - Normalizer of Cartan: a_p = 0 for density ~1/2, with QR bias in nonzero
    """
    templates = {}
    qr = qr_set(ell)

    # 1. Full image: approximately uniform over F_ell
    full = np.ones(ell) / ell
    templates["full"] = full

    # 2. Borel (rational ell-isogeny): a_p = chi_1(p) + chi_2(p) mod ell
    #    Two characters chi_1, chi_2 with chi_1*chi_2 = det.
    #    a_p = 0 when chi_1(p) = -chi_2(p), more frequent than uniform.
    #    Concentrates on QR classes since chi values are roots of unity mod ell.
    borel = np.zeros(ell)
    borel[0] = 2.0 / ell  # Roughly double the zero-class weight
    for k in range(1, ell):
        if k in qr:
            borel[k] = 1.5 / (ell * max(len(qr) - 1, 1)) * (len(qr) - 1)
        else:
            borel[k] = 0.5 / (ell * max(ell - len(qr), 1)) * (ell - len(qr))
    borel /= borel.sum()
    templates["borel"] = borel

    # 3. Split Cartan (CM): a_p = 0 for inert primes (density ~1/2)
    #    For split primes, a_p = psi(p) + psi_bar(p) uniformly distributed
    cartan = np.zeros(ell)
    cartan[0] = 0.50
    for k in range(1, ell):
        cartan[k] = 0.50 / (ell - 1)
    templates["cartan"] = cartan

    # 4. Normalizer of split Cartan: like Cartan but zero-frequency is
    #    ~(ell+1)/(2*ell) for the normalizer vs ~1/2 for the Cartan itself.
    #    Also: nonzero values biased toward QR classes.
    norm = np.zeros(ell)
    norm[0] = (ell + 1) / (2.0 * ell)  # Slightly above 1/2
    remaining = 1.0 - norm[0]
    for k in range(1, ell):
        if k in qr:
            norm[k] = remaining * 0.6 / max(len(qr) - 1, 1)
        else:
            norm[k] = remaining * 0.4 / max(ell - len(qr), 1)
    norm /= norm.sum()
    templates["norm_cartan"] = norm

    # 5. Mod-2 specifics
    if ell == 2:
        # At mod 2, only 3 possible images:
        # Trivial: all a_p even (0 mod 2). Happens when 2 | a_p for all good p.
        templates["mod2_all_even"] = np.array([1.0, 0.0])
        # The "full" and other templates already cover the 50/50 case

    return templates


def chi_squared_distance(observed, expected):
    """Chi-squared distance between observed and expected distributions."""
    dist = 0.0
    for i in range(len(expected)):
        if expected[i] > 1e-10:
            dist += (observed[i] - expected[i]) ** 2 / expected[i]
        elif observed[i] > 1e-10:
            dist += 100.0  # Heavy penalty for mass where none expected
    return dist


def kl_divergence(observed, expected, epsilon=1e-8):
    """KL divergence D(observed || expected) with smoothing."""
    p = observed + epsilon
    q = expected + epsilon
    p /= p.sum()
    q /= q.sum()
    return np.sum(p * np.log(p / q))


def classify_at_ell(distribution, ell, n_good):
    """
    Classify a form's a_p mod ell distribution against templates.

    Uses a decision-tree approach rather than pure nearest-template:
    1. Check zero-frequency: if P(0) > 0.35, it's Cartan/norm_Cartan territory
    2. Check starvation: if any class completely missing, likely Borel or Cartan
    3. Otherwise: chi-squared test against uniform for "full" classification
    4. Flag "anomalous" only if significantly non-uniform AND not Cartan/Borel

    Returns (best_class, chi_sq, details_dict).
    """
    total = sum(distribution.values())
    if total == 0:
        return None, None, {}

    observed = np.zeros(ell)
    for k, count in distribution.items():
        observed[int(k) % ell] += count
    observed /= observed.sum()

    zero_freq = observed[0]
    classes_hit = sum(1 for x in observed if x > 0)
    uniform = np.ones(ell) / ell

    # Chi-squared statistic against uniform (scaled by n for significance)
    chi_sq_uniform = sum((observed[i] - 1.0/ell)**2 / (1.0/ell) for i in range(ell))
    # Under H0 (uniform), chi_sq ~ chi2(ell-1); scale by n for test stat
    chi_sq_test = chi_sq_uniform * n_good

    # Decision tree
    details = {
        "zero_freq": round(float(zero_freq), 4),
        "classes_hit": int(classes_hit),
        "chi_sq_uniform": round(float(chi_sq_uniform), 6),
        "chi_sq_test_stat": round(float(chi_sq_test), 2),
    }

    # Mod-2 special handling
    if ell == 2:
        if observed[1] < 0.01:  # All even
            return "mod2_all_even", chi_sq_uniform, details
        elif abs(observed[0] - 0.5) < 0.05:
            return "full", chi_sq_uniform, details
        elif observed[0] > 0.6:
            return "borel", chi_sq_uniform, details
        else:
            return "full", chi_sq_uniform, details

    # High zero-frequency analysis
    # CM forms: P(a_p=0) ~ 0.5 at ALL primes (inert primes -> a_p=0)
    # Borel (rational ell-isogeny): elevated P(0) but typically < 0.45
    # Threshold depends on ell: at mod 3, uniform P(0)=0.333, so 0.40 is only
    # 1.2x enriched — could be Borel. At mod 5, uniform is 0.2, so 0.40 is 2x.
    #
    # Use ell-dependent thresholds:
    #   Cartan: P(0) > 1/(ell-1)  [i.e., > 0.5 for ell=3, > 0.25 for ell=5]
    #   This reflects that CM gives P(0) ~ 0.5 regardless of ell
    cartan_threshold = max(0.45, 1.0 / (ell - 1) + 0.05)  # At least 0.45
    borel_zero_threshold = 1.0 / ell * 1.3  # 30% enrichment

    if zero_freq > cartan_threshold:
        # Strong CM signal: P(0) > 0.45
        # Distinguish Cartan from normalizer by QR bias in nonzero classes
        qr = qr_set(ell)
        qr_mass = sum(observed[k] for k in range(1, ell) if k in qr)
        qnr_mass = sum(observed[k] for k in range(1, ell) if k not in qr)
        nonzero_total = qr_mass + qnr_mass

        if nonzero_total > 0:
            n_qr = len(qr) - 1  # Exclude 0
            n_qnr = ell - len(qr)
            if n_qr > 0 and n_qnr > 0:
                qr_density = (qr_mass / n_qr) if n_qr > 0 else 0
                qnr_density = (qnr_mass / n_qnr) if n_qnr > 0 else 0
                if qnr_density > 0 and qr_density / qnr_density > 1.5:
                    return "norm_cartan", chi_sq_uniform, details

        return "cartan", chi_sq_uniform, details

    # Moderate zero enrichment: Borel territory (rational ell-isogeny)
    if zero_freq > borel_zero_threshold and n_good >= 50:
        # Check if nonzero classes show QR concentration (Borel signature)
        qr = qr_set(ell)
        templates_local = build_templates(ell)
        d_borel = chi_squared_distance(observed, templates_local["borel"])
        d_full = chi_squared_distance(observed, templates_local["full"])
        if d_borel < d_full:
            return "borel", chi_sq_uniform, details

    # Missing classes: starvation = Borel territory
    if classes_hit < ell:
        # If missing a full residue class with 100+ primes, genuine starvation
        if n_good >= 50:
            return "borel", chi_sq_uniform, details

    # Moderate zero enrichment: possible Borel
    expected_zero = 1.0 / ell
    if zero_freq > expected_zero * 1.8 and n_good >= 50:
        # Significantly enriched at 0 — test Borel
        templates = build_templates(ell)
        d_borel = chi_squared_distance(observed, templates["borel"])
        d_full = chi_squared_distance(observed, templates["full"])
        if d_borel < d_full * 0.7:
            return "borel", chi_sq_uniform, details

    # Default: test uniform hypothesis
    # Critical value for chi2(ell-1) at p=0.001
    # ell=3: df=2, crit~13.8; ell=5: df=4, crit~18.5; ell=7: df=6, crit~22.5
    crit_values = {3: 13.8, 5: 18.5, 7: 22.5}
    crit = crit_values.get(ell, 3.84 * (ell - 1))

    if chi_sq_test > crit:
        # Significantly non-uniform, but not Cartan or Borel
        # Could be weak Borel or anomalous
        return "anomalous", chi_sq_uniform, details

    return "full", chi_sq_uniform, details


def classify_combined(per_ell_classes):
    """
    Combine per-ell classifications into a single Galois image portrait.

    Priority (reflecting mathematical rarity):
    1. Cartan at any ell >= 3 -> CM (ell=2 Cartan is ambiguous)
    2. Normalizer of Cartan at 2+ ells -> CM (normalizer variant)
    3. mod2_all_even -> reducible mod 2 (rational 2-isogeny)
    4. Borel at 2+ ells -> rational ell-isogeny
    5. Full at all ells -> surjective Galois image (the generic case)
    6. Anomalous -> potential exceptional or statistical fluctuation
    """
    classes = {ell: info["class"] for ell, info in per_ell_classes.items()
               if info.get("class")}

    if not classes:
        return "insufficient_data"

    # 1. Cartan at 2+ ells is strong CM signal (single-ell Cartan has high FPR)
    cartan_ells = [ell for ell, c in classes.items()
                   if c == "cartan" and ell >= 3]
    if len(cartan_ells) >= 2:
        return "CM_cartan"
    if len(cartan_ells) == 1:
        # Single-ell Cartan: weak signal, report as possible CM
        return f"possible_CM_mod{cartan_ells[0]}"

    # 2. Normalizer of Cartan at 2+ ells
    norm_ells = [ell for ell, c in classes.items() if c == "norm_cartan"]
    if len(norm_ells) >= 2:
        return "CM_normalizer_cartan"
    if len(norm_ells) == 1:
        return f"possible_norm_cartan_mod{norm_ells[0]}"

    # 3. Mod-2 all even (rational 2-isogeny, very common)
    if classes.get(2) == "mod2_all_even":
        # Check if also Borel at other ells
        borel_others = sum(1 for e, c in classes.items() if e != 2 and c == "borel")
        if borel_others >= 1:
            return "borel_isogeny_2plus"
        return "borel_mod2"

    # 4. Borel at any ell >= 3
    borel_ells = [ell for ell, c in classes.items() if c == "borel" and ell >= 3]
    if len(borel_ells) >= 2:
        return "borel_isogeny"
    if len(borel_ells) == 1:
        return f"borel_mod{borel_ells[0]}"

    # 5. Check for anomalous
    anom_count = sum(1 for c in classes.values() if c == "anomalous")
    full_count = sum(1 for c in classes.values() if c == "full")

    if anom_count >= 2:
        return "anomalous_multi"
    if anom_count == 1 and full_count >= 2:
        return "full_image"  # One anomalous ell is likely statistical noise

    # 6. Default: full image (the generic case for most elliptic curves)
    if full_count >= len(classes) - 1:
        return "full_image"

    return "mixed"


def scan():
    print(f"Connecting to {DB_PATH}")
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    total = conn.execute(
        "SELECT count(*) FROM modular_forms WHERE dim=1 AND weight>=2 AND ap_coeffs IS NOT NULL"
    ).fetchone()[0]
    print(f"Scanning {total} dim=1 forms for Galois image portraits")

    # Load prior results for cross-validation
    starvation_data = {}
    if STARVATION_PATH.exists():
        with open(STARVATION_PATH) as f:
            starv = json.load(f)
            for form in starv.get("starved_forms", []):
                starvation_data[form["label"]] = form

    t0 = time.time()

    # Build templates once
    all_templates = {ell: build_templates(ell) for ell in TEST_ELLS}

    # Per-form results
    form_classifications = []
    # Aggregate stats
    combined_counts = Counter()
    per_ell_counts = {ell: Counter() for ell in TEST_ELLS}
    cm_validation = {"cm_as_cartan": 0, "cm_as_other": 0, "cm_total": 0,
                     "noncm_as_cartan": 0, "noncm_total": 0}
    exceptional_forms = []
    starved_validation = {"starved_correct_borel": 0, "starved_total": 0}

    batch = 5000
    offset = 0
    processed = 0

    while True:
        rows = conn.execute(f"""
            SELECT lmfdb_label, level, weight, ap_coeffs, is_cm, is_rm,
                   self_twist_type, sato_tate_group
            FROM modular_forms
            WHERE dim=1 AND weight>=2 AND ap_coeffs IS NOT NULL
            ORDER BY level, weight
            LIMIT {batch} OFFSET {offset}
        """).fetchall()
        if not rows:
            break

        for label, level, weight, ap_str, is_cm, is_rm, twist, st in rows:
            try:
                ap = [int(x[0]) for x in json.loads(ap_str)]
            except Exception:
                continue

            processed += 1
            is_cm_bool = bool(is_cm)

            # Compute distributions at each ell
            per_ell = {}
            feature_vector = []

            for ell in TEST_ELLS:
                # Good primes: exclude p | level and p = ell
                good_vals = [ap[i] for i, p in enumerate(PRIMES)
                             if i < len(ap) and level % p != 0 and p != ell]

                if len(good_vals) < MIN_GOOD:
                    per_ell[ell] = {"class": None, "chi_sq": None, "distribution": {}}
                    feature_vector.extend([0.0] * ell)
                    continue

                # Build distribution
                dist = Counter()
                for v in good_vals:
                    dist[v % ell] += 1

                # Normalize
                total_vals = sum(dist.values())
                norm_dist = {k: c / total_vals for k, c in dist.items()}

                # Classify
                best_class, chi_sq, all_dists = classify_at_ell(dist, ell, len(good_vals))
                per_ell[ell] = {
                    "class": best_class,
                    "chi_sq": round(chi_sq, 6) if chi_sq else None,
                    "distribution": {str(k): round(v, 6) for k, v in norm_dist.items()},
                    "raw_counts": {str(k): int(v) for k, v in dist.items()},
                    "n_good_primes": len(good_vals),
                }

                # Feature vector
                obs = np.zeros(ell)
                for k, c in dist.items():
                    obs[k % ell] += c
                obs /= obs.sum()
                feature_vector.extend(obs.tolist())

                per_ell_counts[ell][best_class] += 1

            # Combined classification
            combined = classify_combined(per_ell)
            combined_counts[combined] += 1

            # Validation against known CM
            if is_cm_bool:
                cm_validation["cm_total"] += 1
                if combined in ("CM_cartan", "normalizer_cartan"):
                    cm_validation["cm_as_cartan"] += 1
                else:
                    cm_validation["cm_as_other"] += 1
            else:
                cm_validation["noncm_total"] += 1
                if combined in ("CM_cartan", "normalizer_cartan"):
                    cm_validation["noncm_as_cartan"] += 1

            # Validation against starvation
            if label in starvation_data:
                starved_validation["starved_total"] += 1
                if "borel" in combined.lower() or "cartan" in combined.lower():
                    starved_validation["starved_correct_borel"] += 1

            # Track exceptional forms
            if "exceptional" in combined:
                exceptional_forms.append({
                    "label": label,
                    "level": level,
                    "is_cm": is_cm_bool,
                    "combined_class": combined,
                    "per_ell": {str(e): {"class": v["class"], "chi_sq": v.get("chi_sq")}
                                for e, v in per_ell.items()},
                })

            # Store compact result
            form_classifications.append({
                "label": label,
                "level": level,
                "is_cm": is_cm_bool,
                "combined_class": combined,
                "per_ell_classes": {str(e): v["class"] for e, v in per_ell.items()},
                "zero_freqs": {str(e): round(v["distribution"].get("0", 0.0), 4)
                               for e, v in per_ell.items() if v["distribution"]},
            })

            if processed % 2000 == 0:
                print(f"  Processed {processed}/{total}...")

        offset += batch

    elapsed = time.time() - t0
    print(f"Processed {processed} forms in {elapsed:.1f}s")

    # --- Analysis ---

    # Zero-frequency statistics by combined class
    zero_freq_by_class = {}
    for fc in form_classifications:
        cls = fc["combined_class"]
        if cls not in zero_freq_by_class:
            zero_freq_by_class[cls] = {str(ell): [] for ell in TEST_ELLS}
        for ell_str, zf in fc["zero_freqs"].items():
            if zf > 0:
                zero_freq_by_class[cls][ell_str].append(zf)

    zero_freq_summary = {}
    for cls, ell_data in zero_freq_by_class.items():
        zero_freq_summary[cls] = {}
        for ell_str, vals in ell_data.items():
            if vals:
                zero_freq_summary[cls][ell_str] = {
                    "mean": round(np.mean(vals), 4),
                    "std": round(np.std(vals), 4),
                    "min": round(min(vals), 4),
                    "max": round(max(vals), 4),
                    "n": len(vals),
                }

    # Check the 8 mod-7 starved forms specifically
    mod7_starved = []
    if STARVATION_PATH.exists():
        with open(STARVATION_PATH) as f:
            starv = json.load(f)
            for form in starv.get("starved_forms", []):
                if "7" in form.get("starvation", {}):
                    label = form["label"]
                    # Find in our classifications
                    match = [fc for fc in form_classifications if fc["label"] == label]
                    if match:
                        mod7_starved.append({
                            "label": label,
                            "starvation_info": form["starvation"]["7"],
                            "our_class": match[0]["combined_class"],
                            "per_ell": match[0]["per_ell_classes"],
                            "zero_freqs": match[0]["zero_freqs"],
                        })

    # Build results
    results = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_forms": processed,
            "test_ells": TEST_ELLS,
            "min_good_primes": MIN_GOOD,
            "primes_up_to": PRIMES[-1],
            "n_primes": len(PRIMES),
            "elapsed_seconds": round(elapsed, 1),
        },
        "combined_classification": {
            "distribution": dict(combined_counts.most_common()),
            "total_classified": sum(combined_counts.values()),
        },
        "per_ell_classification": {
            str(ell): dict(per_ell_counts[ell].most_common())
            for ell in TEST_ELLS
        },
        "cm_validation": cm_validation,
        "starvation_validation": starved_validation,
        "zero_frequency_by_class": zero_freq_summary,
        "exceptional_forms": exceptional_forms[:50],  # Cap for file size
        "exceptional_count": len(exceptional_forms),
        "mod7_starved_check": mod7_starved,
        "sample_classifications": form_classifications[:100],
    }

    # --- CT1 cluster comparison ---
    if CT1_PATH.exists():
        with open(CT1_PATH) as f:
            ct1 = json.load(f)
        # Check if large clusters correspond to small-image classifications
        cluster_image_analysis = {}
        for ell_str in ["3", "5", "7"]:
            if ell_str in ct1.get("hubs", {}):
                hub_analysis = []
                for hub in ct1["hubs"][ell_str][:10]:
                    hub_labels = hub.get("labels_sample", [])
                    # Find our classifications for these labels
                    matches = [fc for fc in form_classifications if fc["label"] in hub_labels]
                    class_dist = Counter(m["combined_class"] for m in matches)
                    hub_analysis.append({
                        "cluster_size": hub["size"],
                        "sampled": len(matches),
                        "class_distribution": dict(class_dist),
                    })
                cluster_image_analysis[ell_str] = hub_analysis

        results["ct1_cluster_comparison"] = cluster_image_analysis

    # Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")

    # Print summary
    print("\n=== GALOIS IMAGE PORTRAIT SUMMARY ===")
    print(f"\nTotal forms classified: {processed}")
    print(f"\nCombined classification distribution:")
    for cls, cnt in combined_counts.most_common():
        print(f"  {cls:25s}: {cnt:6d}  ({100*cnt/processed:.1f}%)")

    print(f"\nCM validation:")
    print(f"  CM forms classified as Cartan: {cm_validation['cm_as_cartan']}/{cm_validation['cm_total']}")
    print(f"  CM forms classified otherwise: {cm_validation['cm_as_other']}/{cm_validation['cm_total']}")
    print(f"  Non-CM falsely as Cartan:      {cm_validation['noncm_as_cartan']}/{cm_validation['noncm_total']}")

    print(f"\nStarvation validation:")
    print(f"  Starved forms as Borel/Cartan: {starved_validation['starved_correct_borel']}/{starved_validation['starved_total']}")

    print(f"\nExceptional forms found: {len(exceptional_forms)}")
    if exceptional_forms:
        print("  First 10:")
        for ef in exceptional_forms[:10]:
            print(f"    {ef['label']} -> {ef['combined_class']}")

    print(f"\nMod-7 starved forms check ({len(mod7_starved)} found):")
    for m7 in mod7_starved[:10]:
        print(f"  {m7['label']}: classified as {m7['our_class']}, "
              f"zero_freqs={m7['zero_freqs']}")

    print(f"\nPer-ell classification:")
    for ell in TEST_ELLS:
        print(f"\n  mod {ell}:")
        for cls, cnt in per_ell_counts[ell].most_common():
            print(f"    {cls:25s}: {cnt:6d}")

    return results


if __name__ == "__main__":
    scan()
