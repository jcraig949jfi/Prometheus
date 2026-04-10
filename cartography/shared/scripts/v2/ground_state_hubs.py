#!/usr/bin/env python3
"""
OSC-5: Identify Ground State Hubs from Coefficient Behavior Alone

A "ground state hub" = lowest-conductor form in a twist orbit of size >= 3.
Can we identify such hubs WITHOUT computing twists, purely from coefficient
structural features?

Pipeline:
  1. Reconstruct twist orbits from CT4 pairs (connected components)
  2. Identify ground state hubs (lowest conductor in each orbit of size >= 3)
  3. Compute structural profile for every dim=1 weight=2 form
  4. Compare hubs vs non-hubs; find discriminating features
  5. Train classifier; predict undiscovered hubs in the full 17,314

Charon — Cross-Domain Cartographer, Project Prometheus
"""

import json
import math
import time
from collections import Counter, defaultdict, deque
from pathlib import Path

import duckdb
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[4]
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
V2_DIR = Path(__file__).resolve().parent
CT4_PATH = V2_DIR / "symmetry_detection_results.json"
STARVATION_PATH = V2_DIR / "residue_starvation_results.json"
GALOIS_PATH = V2_DIR / "galois_image_results.json"
OUTPUT_PATH = V2_DIR / "ground_state_hub_results.json"


def sieve(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i):
                s[j] = False
    return [i for i in range(2, n + 1) if s[i]]


PRIMES = sieve(997)


# ── Step 1: Reconstruct twist orbits ─────────────────────────────────────

def build_twist_orbits():
    """Build twist orbits as connected components from CT4 twist pairs."""
    with open(CT4_PATH) as f:
        ct4 = json.load(f)

    # Gather ALL pair types: quadratic, cross-level, character invariance
    all_pairs = []
    for p in ct4["quadratic_twists"]["pairs"]:
        all_pairs.append((p["form_f"], p["form_g"]))
    for p in ct4["cross_level_twists"]["pairs"]:
        all_pairs.append((p["form_f"], p["form_g"]))
    for m in ct4["character_invariance"]["matches"]:
        all_pairs.append((m["form_f"], m["form_g"]))

    # Build adjacency graph
    adj = defaultdict(set)
    for a, b in all_pairs:
        adj[a].add(b)
        adj[b].add(a)

    # BFS to find connected components
    visited = set()
    components = []
    for node in adj:
        if node not in visited:
            comp = []
            q = deque([node])
            while q:
                n = q.popleft()
                if n in visited:
                    continue
                visited.add(n)
                comp.append(n)
                for nb in adj[n]:
                    if nb not in visited:
                        q.append(nb)
            components.append(sorted(comp))

    return components, all_pairs


def extract_conductor(label):
    """Extract integer conductor from LMFDB label like '15.2.a.a'."""
    return int(label.split(".")[0])


def identify_ground_state_hubs(components):
    """
    Ground state hub = lowest-conductor form in an orbit of size >= 3.
    Returns: dict mapping hub_label -> orbit members
    """
    hubs = {}
    for comp in components:
        if len(comp) < 3:
            continue
        # Lowest conductor
        best = min(comp, key=extract_conductor)
        hubs[best] = comp
    return hubs


# ── Step 2: Compute structural profile for every form ────────────────────

def factorize(n):
    """Return prime factorization as dict {p: e}."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def compute_mod_ell_fingerprint(ap_values, good_mask, ell):
    """Compute mod-ell residue vector for a_p values at good primes."""
    fp = []
    for i, (ap, good) in enumerate(zip(ap_values, good_mask)):
        if good:
            fp.append(int(ap) % ell)
    return tuple(fp)


def compute_autocorrelation_kstar(ap_values, good_mask, max_lag=50):
    """Find the lag with strongest autocorrelation in a_p sequence."""
    vals = [ap for ap, g in zip(ap_values, good_mask) if g]
    if len(vals) < max_lag + 10:
        return 0, 0.0
    arr = np.array(vals, dtype=float)
    arr = arr - arr.mean()
    norm = np.dot(arr, arr)
    if norm < 1e-12:
        return 0, 0.0
    best_lag, best_corr = 0, 0.0
    for lag in range(1, min(max_lag + 1, len(arr) // 2)):
        c = np.dot(arr[:-lag], arr[lag:]) / norm
        if abs(c) > abs(best_corr):
            best_lag, best_corr = lag, c
    return best_lag, best_corr


def compute_ell_c(fingerprints_by_ell, all_fingerprints_by_ell):
    """
    ell_c = the smallest prime ell where this form's mod-ell fingerprint
    has NO matches among other forms (i.e., it becomes isolated).
    """
    test_ells = [2, 3, 5, 7, 11, 13]
    for ell in test_ells:
        if ell not in fingerprints_by_ell:
            continue
        my_fp = fingerprints_by_ell[ell]
        count = all_fingerprints_by_ell[ell].get(my_fp, 0)
        if count <= 1:  # only itself
            return ell
    return None  # never isolated up to ell=13


def compute_structural_profiles(con, hubs, starvation_map, galois_map):
    """
    Compute structural feature vector for every dim=1 weight=2 form.
    Returns dict: label -> feature_dict
    """
    print("  Loading all dim=1 weight=2 forms from DuckDB...")
    rows = con.execute("""
        SELECT lmfdb_label, level, is_cm, is_rm, self_twist_type,
               sato_tate_group, ap_coeffs, traces, fricke_eigenval
        FROM modular_forms
        WHERE dim = 1 AND weight = 2
        ORDER BY level, lmfdb_label
    """).fetchall()
    print(f"  Loaded {len(rows)} forms")

    # Parse ap_coeffs for each form
    form_data = {}
    for row in rows:
        label, level, is_cm, is_rm, st_type, st_group, ap_raw, traces_raw, fricke = row
        ap_list = json.loads(ap_raw) if ap_raw else []
        # For dim=1, each entry is [a_p]; extract scalars
        ap_values = [entry[0] if isinstance(entry, list) else entry for entry in ap_list]
        # good_mask: True if prime doesn't divide level
        good_mask = [p % level != 0 and level % p != 0 for p in PRIMES[:len(ap_values)]]
        form_data[label] = {
            "level": level,
            "is_cm": is_cm,
            "is_rm": is_rm,
            "self_twist_type": st_type,
            "st_group": st_group,
            "ap_values": ap_values,
            "good_mask": good_mask,
            "fricke": fricke,
        }

    # ── Compute mod-ell fingerprints for all forms ──
    print("  Computing mod-ell fingerprints...")
    test_ells = [2, 3, 5, 7, 11, 13]
    form_fingerprints = {}  # label -> {ell: fingerprint}
    all_fp_counts = {ell: Counter() for ell in test_ells}

    for label, fd in form_data.items():
        fps = {}
        for ell in test_ells:
            fp = compute_mod_ell_fingerprint(fd["ap_values"], fd["good_mask"], ell)
            fps[ell] = fp
            all_fp_counts[ell][fp] += 1
        form_fingerprints[label] = fps

    # ── Compute neighborhood sizes and ell_c ──
    print("  Computing neighborhoods and ell_c...")
    profiles = {}
    for label, fd in form_data.items():
        level = fd["level"]
        ap = fd["ap_values"]
        good = fd["good_mask"]

        # Zero frequency: fraction of a_p = 0 among good primes
        n_good = sum(good[:len(ap)])
        n_zero = sum(1 for i, (a, g) in enumerate(zip(ap, good)) if g and a == 0)
        zero_freq = n_zero / n_good if n_good > 0 else 0.0

        # Starvation level: number of primes at which form is starved
        starv_info = starvation_map.get(label, {})
        starvation_count = len(starv_info)

        # Galois image class
        galois_class = galois_map.get(label, "unknown")

        # Mod-ell neighborhood sizes
        fps = form_fingerprints[label]
        mod2_nbrs = all_fp_counts[2].get(fps.get(2, ()), 0) - 1  # exclude self
        mod3_nbrs = all_fp_counts[3].get(fps.get(3, ()), 0) - 1
        mod5_nbrs = all_fp_counts[5].get(fps.get(5, ()), 0) - 1

        # ell_c
        ell_c = compute_ell_c(fps, all_fp_counts)

        # Conductor factorization
        factors = factorize(level)
        n_prime_factors = len(factors)
        v2_N = factors.get(2, 0)

        # Autocorrelation k*
        k_star, k_corr = compute_autocorrelation_kstar(ap, good)

        # Is this a hub?
        is_hub = label in hubs

        profiles[label] = {
            "label": label,
            "level": level,
            "is_cm": bool(fd["is_cm"]),
            "is_hub": is_hub,
            "orbit_size": len(hubs[label]) if is_hub else 0,
            "zero_freq": round(zero_freq, 6),
            "starvation_count": starvation_count,
            "galois_class": galois_class,
            "mod2_nbrs": mod2_nbrs,
            "mod3_nbrs": mod3_nbrs,
            "mod5_nbrs": mod5_nbrs,
            "ell_c": ell_c,
            "n_prime_factors": n_prime_factors,
            "v2_N": v2_N,
            "k_star": k_star,
            "k_star_corr": round(k_corr, 6),
            "fricke": fd["fricke"],
        }

    return profiles


def load_starvation_map():
    """Load per-form starvation data: label -> {prime: info}."""
    with open(STARVATION_PATH) as f:
        data = json.load(f)
    smap = {}
    for sf in data["starved_forms"]:
        smap[sf["label"]] = sf["starvation"]
    return smap


def load_galois_map(con):
    """
    Classify all forms' combined Galois image from coefficient data.
    Since galois_image_results.json only has 100 samples, we recompute
    a simplified classification for all 17K forms.
    """
    print("  Computing simplified Galois image classification...")
    rows = con.execute("""
        SELECT lmfdb_label, level, is_cm, ap_coeffs
        FROM modular_forms WHERE dim = 1 AND weight = 2
    """).fetchall()

    gmap = {}
    for label, level, is_cm, ap_raw in rows:
        ap_list = json.loads(ap_raw) if ap_raw else []
        ap_values = [entry[0] if isinstance(entry, list) else entry for entry in ap_list]
        n = min(len(ap_values), len(PRIMES))
        good = [PRIMES[i] for i in range(n) if level % PRIMES[i] != 0]
        good_ap = [ap_values[i] for i in range(n) if level % PRIMES[i] != 0]

        if not good_ap:
            gmap[label] = "unknown"
            continue

        # Mod-2 check: fraction of even a_p
        n_even = sum(1 for a in good_ap if int(a) % 2 == 0)
        even_frac = n_even / len(good_ap)

        # Mod-3 check: fraction of a_p ≡ 0 mod 3
        n_div3 = sum(1 for a in good_ap if int(a) % 3 == 0)
        div3_frac = n_div3 / len(good_ap)

        if is_cm:
            gmap[label] = "CM_cartan"
        elif even_frac > 0.95:
            if div3_frac > 0.45:
                gmap[label] = "borel_isogeny_2plus"
            else:
                gmap[label] = "borel_mod2"
        elif div3_frac > 0.45:
            gmap[label] = "borel_mod3"
        else:
            gmap[label] = "full_image"

    return gmap


# ── Step 3: Compare hubs vs non-hubs ────────────────────────────────────

def compare_hubs_vs_nonhubs(profiles, hubs):
    """Statistical comparison of feature distributions."""
    hub_labels = set(hubs.keys())
    # Also get all forms that are in ANY orbit of size >= 3 (not just hubs)
    in_orbit = set()
    for comp_members in hubs.values():
        in_orbit.update(comp_members)

    # Three groups: hubs, non-hub orbit members, background (not in any size>=3 orbit)
    hub_profiles = [p for p in profiles.values() if p["is_hub"]]
    orbit_nonhub = [p for p in profiles.values() if p["label"] in in_orbit and not p["is_hub"]]
    background = [p for p in profiles.values() if p["label"] not in in_orbit]

    numeric_features = [
        "zero_freq", "starvation_count", "mod2_nbrs", "mod3_nbrs",
        "mod5_nbrs", "n_prime_factors", "v2_N", "k_star", "k_star_corr",
        "level",
    ]

    comparisons = {}
    for feat in numeric_features:
        h_vals = [p[feat] for p in hub_profiles if p[feat] is not None]
        o_vals = [p[feat] for p in orbit_nonhub if p[feat] is not None]
        b_vals = [p[feat] for p in background if p[feat] is not None]

        comparisons[feat] = {
            "hub_mean": round(float(np.mean(h_vals)), 6) if h_vals else None,
            "hub_std": round(float(np.std(h_vals)), 6) if h_vals else None,
            "orbit_nonhub_mean": round(float(np.mean(o_vals)), 6) if o_vals else None,
            "background_mean": round(float(np.mean(b_vals)), 6) if b_vals else None,
            "background_std": round(float(np.std(b_vals)), 6) if b_vals else None,
            "n_hub": len(h_vals),
            "n_background": len(b_vals),
        }

        # Effect size (Cohen's d) hub vs background
        if h_vals and b_vals and np.std(b_vals) > 0:
            d = (np.mean(h_vals) - np.mean(b_vals)) / np.std(b_vals)
            comparisons[feat]["cohens_d"] = round(float(d), 4)

    # ell_c comparison (categorical)
    ell_c_hub = Counter(p["ell_c"] for p in hub_profiles)
    ell_c_bg = Counter(p["ell_c"] for p in background)
    comparisons["ell_c_distribution"] = {
        "hub": {str(k): v for k, v in sorted(ell_c_hub.items(), key=lambda x: (x[0] is None, x[0]))},
        "background": {str(k): v for k, v in sorted(ell_c_bg.items(), key=lambda x: (x[0] is None, x[0]))}
    }

    # Galois class comparison
    gc_hub = Counter(p["galois_class"] for p in hub_profiles)
    gc_bg = Counter(p["galois_class"] for p in background)
    comparisons["galois_class_distribution"] = {
        "hub": dict(gc_hub),
        "background": dict(gc_bg),
    }

    return comparisons


# ── Step 4: Train classifier ────────────────────────────────────────────

def train_classifier(profiles, hubs):
    """
    Train a simple classifier to predict ground state hubs from features.
    Uses logistic regression and decision tree for comparison.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import classification_report

    feature_names = [
        "zero_freq", "starvation_count", "mod2_nbrs", "mod3_nbrs",
        "mod5_nbrs", "n_prime_factors", "v2_N", "k_star", "k_star_corr",
        "level",
    ]

    # Build feature matrix
    labels_list = sorted(profiles.keys())
    X = []
    y = []
    for label in labels_list:
        p = profiles[label]
        feats = []
        for fn in feature_names:
            val = p[fn]
            if val is None:
                feats.append(0)
            else:
                feats.append(float(val))
        X.append(feats)
        y.append(1 if p["is_hub"] else 0)

    X = np.array(X)
    y = np.array(y)

    print(f"  Training set: {len(y)} forms, {y.sum()} hubs, {len(y)-y.sum()} non-hubs")

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Logistic regression with cross-validation
    lr = LogisticRegression(class_weight="balanced", max_iter=1000, C=1.0)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    lr_scores = cross_val_score(lr, X_scaled, y, cv=skf, scoring="f1")
    print(f"  Logistic Regression CV F1: {lr_scores.mean():.4f} ± {lr_scores.std():.4f}")

    # Decision tree
    dt = DecisionTreeClassifier(class_weight="balanced", max_depth=5, random_state=42)
    dt_scores = cross_val_score(dt, X_scaled, y, cv=skf, scoring="f1")
    print(f"  Decision Tree CV F1: {dt_scores.mean():.4f} ± {dt_scores.std():.4f}")

    # Fit on full data for predictions and feature importances
    lr.fit(X_scaled, y)
    dt.fit(X_scaled, y)

    # Feature importances
    lr_coefs = dict(zip(feature_names, [round(float(c), 4) for c in lr.coef_[0]]))
    dt_importances = dict(zip(feature_names, [round(float(c), 4) for c in dt.feature_importances_]))

    # Predictions on full dataset
    lr_probs = lr.predict_proba(X_scaled)[:, 1]
    lr_preds = lr.predict(X_scaled)
    dt_preds = dt.predict(X_scaled)

    # Find predicted hubs that are NOT known hubs
    in_orbit = set()
    for comp_members in hubs.values():
        in_orbit.update(comp_members)

    predicted_hubs_lr = []
    predicted_hubs_dt = []
    for i, label in enumerate(labels_list):
        if lr_preds[i] == 1 and label not in in_orbit:
            predicted_hubs_lr.append({
                "label": label,
                "level": profiles[label]["level"],
                "prob": round(float(lr_probs[i]), 4),
                "zero_freq": profiles[label]["zero_freq"],
                "galois_class": profiles[label]["galois_class"],
                "mod2_nbrs": profiles[label]["mod2_nbrs"],
            })
        if dt_preds[i] == 1 and label not in in_orbit:
            predicted_hubs_dt.append({
                "label": label,
                "level": profiles[label]["level"],
                "prob": round(float(lr_probs[i]), 4),
            })

    # Sort by probability
    predicted_hubs_lr.sort(key=lambda x: -x["prob"])
    predicted_hubs_dt.sort(key=lambda x: -x["prob"])

    # Most discriminating feature
    best_lr_feat = max(lr_coefs, key=lambda k: abs(lr_coefs[k]))
    best_dt_feat = max(dt_importances, key=lambda k: dt_importances[k])

    return {
        "logistic_regression": {
            "cv_f1_mean": round(float(lr_scores.mean()), 4),
            "cv_f1_std": round(float(lr_scores.std()), 4),
            "coefficients": lr_coefs,
            "most_discriminating": best_lr_feat,
            "n_predicted_hubs_total": int(lr_preds.sum()),
            "n_predicted_novel_hubs": len(predicted_hubs_lr),
            "novel_hubs_top20": predicted_hubs_lr[:20],
        },
        "decision_tree": {
            "cv_f1_mean": round(float(dt_scores.mean()), 4),
            "cv_f1_std": round(float(dt_scores.std()), 4),
            "feature_importances": dt_importances,
            "most_discriminating": best_dt_feat,
            "n_predicted_hubs_total": int(dt_preds.sum()),
            "n_predicted_novel_hubs": len(predicted_hubs_dt),
            "novel_hubs_top20": predicted_hubs_dt[:20],
        },
        "feature_names": feature_names,
        "all_predicted_novel_lr": predicted_hubs_lr,
        "all_predicted_novel_dt": predicted_hubs_dt,
    }


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("OSC-5: Ground State Hub Identification")
    print("=" * 60)

    # Step 1: Build twist orbits
    print("\n[1] Building twist orbits from CT4 pairs...")
    components, all_pairs = build_twist_orbits()
    size_dist = Counter(len(c) for c in components)
    print(f"  Total twist pairs: {len(all_pairs)}")
    print(f"  Connected components: {len(components)}")
    print(f"  Size distribution: {dict(sorted(size_dist.items(), reverse=True))}")

    # Identify ground state hubs (lowest conductor in orbits of size >= 3)
    hubs = identify_ground_state_hubs(components)
    print(f"\n  Ground state hubs (orbit size >= 3): {len(hubs)}")
    for hub, members in sorted(hubs.items(), key=lambda x: extract_conductor(x[0])):
        print(f"    {hub} (N={extract_conductor(hub)}): orbit size {len(members)}")
        print(f"      members: {members}")

    # Step 2: Load auxiliary data and compute profiles
    print("\n[2] Computing structural profiles for all 17,314 forms...")
    starvation_map = load_starvation_map()
    print(f"  Starvation data for {len(starvation_map)} forms")

    con = duckdb.connect(str(DB_PATH), read_only=True)
    galois_map = load_galois_map(con)
    print(f"  Galois image classified for {len(galois_map)} forms")

    profiles = compute_structural_profiles(con, hubs, starvation_map, galois_map)
    con.close()
    print(f"  Profiles computed for {len(profiles)} forms")

    # Step 3: Compare hubs vs non-hubs
    print("\n[3] Comparing ground state hubs vs background...")
    comparisons = compare_hubs_vs_nonhubs(profiles, hubs)

    print("\n  Feature comparison (hub mean vs background mean, Cohen's d):")
    for feat in ["zero_freq", "starvation_count", "mod2_nbrs", "mod3_nbrs",
                 "mod5_nbrs", "n_prime_factors", "v2_N", "k_star", "level"]:
        c = comparisons[feat]
        d = c.get("cohens_d", "N/A")
        print(f"    {feat:20s}: hub={c['hub_mean']:10.4f}  bg={c['background_mean']:10.4f}  d={d}")

    print(f"\n  ell_c distribution:")
    print(f"    Hubs: {comparisons['ell_c_distribution']['hub']}")
    bg_ell_c = comparisons["ell_c_distribution"]["background"]
    total_bg = sum(bg_ell_c.values())
    print(f"    Background (top): ", end="")
    for k in sorted(bg_ell_c, key=lambda x: -bg_ell_c[x])[:5]:
        print(f"{k}:{bg_ell_c[k]} ({100*bg_ell_c[k]/total_bg:.1f}%) ", end="")
    print()

    print(f"\n  Galois class distribution:")
    print(f"    Hubs: {comparisons['galois_class_distribution']['hub']}")

    # Step 4: Train classifier
    print("\n[4] Training hub classifier...")
    try:
        classifier_results = train_classifier(profiles, hubs)
        print(f"\n  Logistic Regression:")
        print(f"    CV F1: {classifier_results['logistic_regression']['cv_f1_mean']:.4f}")
        print(f"    Most discriminating feature: {classifier_results['logistic_regression']['most_discriminating']}")
        print(f"    Coefficients: {classifier_results['logistic_regression']['coefficients']}")
        print(f"    Predicted hubs (total): {classifier_results['logistic_regression']['n_predicted_hubs_total']}")
        print(f"    Novel predicted hubs (no known twist partners): {classifier_results['logistic_regression']['n_predicted_novel_hubs']}")

        print(f"\n  Decision Tree:")
        print(f"    CV F1: {classifier_results['decision_tree']['cv_f1_mean']:.4f}")
        print(f"    Most discriminating feature: {classifier_results['decision_tree']['most_discriminating']}")
        print(f"    Feature importances: {classifier_results['decision_tree']['feature_importances']}")
        print(f"    Predicted hubs (total): {classifier_results['decision_tree']['n_predicted_hubs_total']}")
        print(f"    Novel predicted hubs: {classifier_results['decision_tree']['n_predicted_novel_hubs']}")

        if classifier_results["logistic_regression"]["novel_hubs_top20"]:
            print(f"\n  Top 20 predicted novel hubs (LR):")
            for h in classifier_results["logistic_regression"]["novel_hubs_top20"]:
                print(f"    {h['label']:20s} prob={h['prob']:.4f} zero_freq={h['zero_freq']:.4f} galois={h['galois_class']} mod2_nbrs={h['mod2_nbrs']}")
    except ImportError:
        print("  sklearn not available — skipping classifier")
        classifier_results = {"error": "sklearn not installed"}

    # Step 5: Topological anchor analysis
    print("\n[5] Topological anchor signature analysis...")
    hub_profiles_list = [profiles[h] for h in hubs]

    # Is it purely arithmetic?
    print("  Is hub status purely arithmetic (= smallest conductor)?")
    print("  By definition yes for 'ground state'. The question is: does coefficient")
    print("  behavior PREDICT which forms are ground states of large orbits?")

    # Check if any feature alone separates perfectly
    for feat in ["zero_freq", "mod2_nbrs", "mod3_nbrs", "level"]:
        h_vals = sorted([p[feat] for p in hub_profiles_list])
        print(f"    Hub {feat} range: {min(h_vals)}-{max(h_vals)}")

    elapsed = time.time() - t0

    # ── Assemble results ──
    hub_details = {}
    for hub, members in hubs.items():
        p = profiles[hub]
        hub_details[hub] = {
            "orbit_size": len(members),
            "orbit_members": members,
            "conductor": p["level"],
            "zero_freq": p["zero_freq"],
            "starvation_count": p["starvation_count"],
            "galois_class": p["galois_class"],
            "mod2_nbrs": p["mod2_nbrs"],
            "mod3_nbrs": p["mod3_nbrs"],
            "mod5_nbrs": p["mod5_nbrs"],
            "ell_c": p["ell_c"],
            "n_prime_factors": p["n_prime_factors"],
            "v2_N": p["v2_N"],
            "k_star": p["k_star"],
            "k_star_corr": p["k_star_corr"],
            "is_cm": p["is_cm"],
            "fricke": p["fricke"],
        }

    results = {
        "metadata": {
            "challenge": "OSC-5",
            "description": "Ground State Hub Identification from Coefficient Behavior",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_seconds": round(elapsed, 1),
            "total_forms": len(profiles),
            "total_twist_pairs": len(all_pairs),
            "total_components": len(components),
            "orbit_size_distribution": {str(k): v for k, v in sorted(size_dist.items())},
        },
        "ground_state_hubs": {
            "count": len(hubs),
            "definition": "lowest-conductor form in twist orbit of size >= 3",
            "hubs": hub_details,
        },
        "feature_comparison": comparisons,
        "classifier": classifier_results,
        "topological_anchor_analysis": {
            "question": "What marks a form as the center of a large twist orbit?",
            "findings": [],  # filled below
        },
    }

    # Fill in findings
    findings = []
    if isinstance(classifier_results, dict) and "logistic_regression" in classifier_results:
        lr = classifier_results["logistic_regression"]
        dt = classifier_results["decision_tree"]
        findings.append(f"LR most discriminating feature: {lr['most_discriminating']}")
        findings.append(f"DT most discriminating feature: {dt['most_discriminating']}")
        findings.append(f"LR CV F1: {lr['cv_f1_mean']:.4f}, DT CV F1: {dt['cv_f1_mean']:.4f}")
        findings.append(f"Novel predicted hubs (LR): {lr['n_predicted_novel_hubs']}")
        findings.append(f"Novel predicted hubs (DT): {dt['n_predicted_novel_hubs']}")

    # Check if it's purely conductor-driven
    hub_conductors = [extract_conductor(h) for h in hubs]
    findings.append(f"Hub conductor range: {min(hub_conductors)}-{max(hub_conductors)}")
    findings.append(f"Hub conductor mean: {np.mean(hub_conductors):.1f}")

    results["topological_anchor_analysis"]["findings"] = findings

    # Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {OUTPUT_PATH}")
    print(f"  Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
