#!/usr/bin/env python3
"""
Reynolds Number Phase Transition in Number Fields
==================================================

Tests whether the global habitable zone Re_c = [4.37, 13.68] (from X12's
bathtub-of-death finding) applies within number field hypotheses specifically.

Method:
  1. Load 9,116 number fields from cartography/number_fields/data/number_fields.json
  2. Generate 500 hypotheses about NF structure (correlations, subset patterns,
     normalizations) across diverse feature combinations
  3. Run each through a mini battery:
       - Permutation null (z-score)
       - Effect size (Cohen's d)
       - Subset stability (80/20 split x5)
  4. Compute the Reynolds number Re = |z_score| for each hypothesis
  5. Build survival curve and find NF-specific habitable zone
  6. Compare to global [4.37, 13.68]

Output:
  - v2/nf_reynolds_results.json
"""

import json
import os
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

# ── paths ────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent          # cartography/v2
CARTO = HERE.parent                              # cartography/
REPO = CARTO.parent                              # F:/Prometheus
NF_DATA = CARTO / "number_fields" / "data" / "number_fields.json"
OUT_JSON = HERE / "nf_reynolds_results.json"

RNG = np.random.RandomState(2026)


# ── load & preprocess ────────────────────────────────────────────────────
def load_number_fields():
    """Load NF data and compute numeric features."""
    with open(NF_DATA) as f:
        raw = json.load(f)

    print(f"Loaded {len(raw)} number fields")

    records = []
    for r in raw:
        try:
            disc_abs = float(r["disc_abs"])
            class_number = float(r["class_number"])
            degree = int(r["degree"])
            disc_sign = int(r["disc_sign"])
            regulator = float(r["regulator"])
            class_group = r.get("class_group", [])
            galois_label = r.get("galois_label", "")

            # Derived features
            log_disc = np.log(disc_abs + 1)
            disc_per_degree = disc_abs / max(degree, 1)
            log_disc_per_degree = np.log(disc_per_degree + 1)
            class_group_rank = len(class_group)
            class_group_order = 1
            for g in class_group:
                class_group_order *= int(g)
            is_totally_real = disc_sign == 1
            log_regulator = np.log(regulator + 1)
            h_over_R = class_number / max(regulator, 1e-10)

            # Galois group size proxy from label (e.g., "2T1" -> T-number)
            t_number = 0
            if "T" in galois_label:
                parts = galois_label.split("T")
                try:
                    t_number = int(parts[1])
                except (ValueError, IndexError):
                    pass

            records.append({
                "degree": degree,
                "disc_abs": disc_abs,
                "log_disc": log_disc,
                "disc_sign": disc_sign,
                "class_number": class_number,
                "log_class_number": np.log(class_number + 1),
                "regulator": regulator,
                "log_regulator": log_regulator,
                "disc_per_degree": disc_per_degree,
                "log_disc_per_degree": log_disc_per_degree,
                "class_group_rank": class_group_rank,
                "class_group_order": class_group_order,
                "log_class_group_order": np.log(class_group_order + 1),
                "is_totally_real": int(is_totally_real),
                "t_number": t_number,
                "h_over_R": h_over_R,
                "log_h_over_R": np.log(abs(h_over_R) + 1) * (1 if h_over_R >= 0 else -1),
            })
        except (ValueError, TypeError, KeyError):
            continue

    return records


# ── hypothesis generation ────────────────────────────────────────────────
NUMERIC_FEATURES = [
    "degree", "disc_abs", "log_disc", "class_number", "log_class_number",
    "regulator", "log_regulator", "disc_per_degree", "log_disc_per_degree",
    "class_group_rank", "class_group_order", "log_class_group_order",
    "is_totally_real", "t_number", "h_over_R", "log_h_over_R",
]


def generate_hypotheses(records, target=500):
    """
    Generate diverse hypotheses about number field structure.

    Types:
      A) Pairwise correlation (feature X ~ feature Y)
      B) Subset comparison (feature X differs across subsets defined by feature Z)
      C) Normalized ratio (X/Y correlates with Z)
      D) Nonlinear (X^2 or sqrt(|X|) correlates with Y)
      E) Conditional (correlation of X,Y within a degree-filtered subset)
    """
    hypotheses = []

    # Type A: pairwise correlations (all pairs)
    pairs = list(combinations(NUMERIC_FEATURES, 2))
    RNG.shuffle(pairs)
    for fx, fy in pairs[:120]:
        hypotheses.append({
            "type": "correlation",
            "description": f"{fx} correlates with {fy}",
            "feature_x": fx,
            "feature_y": fy,
            "subset": "all",
        })

    # Type B: subset comparison (feature differs across degree groups)
    for feat in NUMERIC_FEATURES:
        for split_feat, split_val, split_name in [
            ("degree", 2, "degree=2 vs degree>2"),
            ("is_totally_real", 1, "totally_real vs not"),
            ("class_group_rank", 0, "trivial_class_group vs nontrivial"),
        ]:
            hypotheses.append({
                "type": "subset_comparison",
                "description": f"{feat} differs between {split_name}",
                "feature_x": feat,
                "split_feature": split_feat,
                "split_value": split_val,
            })

    # Type C: normalized ratios
    ratio_triples = [
        ("class_number", "disc_abs", "degree"),
        ("class_number", "regulator", "degree"),
        ("regulator", "disc_abs", "class_number"),
        ("class_group_order", "disc_abs", "degree"),
        ("log_class_number", "log_disc", "degree"),
        ("log_regulator", "log_disc", "class_number"),
        ("h_over_R", "log_disc", "degree"),
        ("class_group_rank", "degree", "log_disc"),
        ("t_number", "degree", "class_number"),
        ("log_class_group_order", "log_disc", "regulator"),
    ]
    for num, denom, target_feat in ratio_triples:
        hypotheses.append({
            "type": "ratio_correlation",
            "description": f"({num}/{denom}) correlates with {target_feat}",
            "numerator": num,
            "denominator": denom,
            "target": target_feat,
            "subset": "all",
        })

    # Type D: nonlinear
    nonlin_transforms = [
        ("square", lambda x: x**2),
        ("sqrt_abs", lambda x: np.sqrt(np.abs(x))),
        ("log1p_abs", lambda x: np.log1p(np.abs(x))),
    ]
    for fx, fy in pairs[:60]:
        for tname, _ in nonlin_transforms:
            hypotheses.append({
                "type": "nonlinear",
                "description": f"{tname}({fx}) correlates with {fy}",
                "feature_x": fx,
                "transform": tname,
                "feature_y": fy,
                "subset": "all",
            })

    # Type E: conditional (within degree subsets)
    for deg in [2, 3, 4]:
        for fx, fy in pairs[:30]:
            hypotheses.append({
                "type": "conditional",
                "description": f"{fx} ~ {fy} within degree={deg}",
                "feature_x": fx,
                "feature_y": fy,
                "degree_filter": deg,
            })

    # Type F: interaction terms (X*Y correlates with Z)
    interaction_triples = list(combinations(NUMERIC_FEATURES, 3))
    RNG.shuffle(interaction_triples)
    for fx, fy, fz in interaction_triples[:40]:
        hypotheses.append({
            "type": "nonlinear",
            "description": f"({fx} * {fy}) correlates with {fz}",
            "feature_x": fx,
            "transform": "interaction",
            "feature_y": fy,
            "interaction_target": fz,
            "subset": "all",
        })

    # Type G: residual after degree (partial correlation proxy)
    for fx, fy in pairs[:30]:
        hypotheses.append({
            "type": "conditional",
            "description": f"{fx} ~ {fy} within degree=2",
            "feature_x": fx,
            "feature_y": fy,
            "degree_filter": 2,
        })

    RNG.shuffle(hypotheses)
    hypotheses = hypotheses[:target]
    print(f"Generated {len(hypotheses)} hypotheses")
    return hypotheses


# ── mini battery ─────────────────────────────────────────────────────────
def extract_xy(records, hyp):
    """Extract (x, y) arrays for a hypothesis."""
    arr = records  # full set by default

    if hyp["type"] == "conditional":
        deg = hyp["degree_filter"]
        arr = [r for r in records if r["degree"] == deg]
        if len(arr) < 30:
            return None, None
        x = np.array([r[hyp["feature_x"]] for r in arr], dtype=float)
        y = np.array([r[hyp["feature_y"]] for r in arr], dtype=float)
        return x, y

    if hyp["type"] == "correlation":
        x = np.array([r[hyp["feature_x"]] for r in arr], dtype=float)
        y = np.array([r[hyp["feature_y"]] for r in arr], dtype=float)
        return x, y

    if hyp["type"] == "subset_comparison":
        feat = hyp["feature_x"]
        sf = hyp["split_feature"]
        sv = hyp["split_value"]
        group_a = np.array([r[feat] for r in arr if r[sf] == sv], dtype=float)
        group_b = np.array([r[feat] for r in arr if r[sf] != sv], dtype=float)
        if len(group_a) < 10 or len(group_b) < 10:
            return None, None
        # Return as (group_a, group_b) — special case
        return group_a, group_b

    if hyp["type"] == "ratio_correlation":
        num = np.array([r[hyp["numerator"]] for r in arr], dtype=float)
        denom = np.array([r[hyp["denominator"]] for r in arr], dtype=float)
        denom = np.where(np.abs(denom) < 1e-10, 1e-10, denom)
        ratio = num / denom
        target = np.array([r[hyp["target"]] for r in arr], dtype=float)
        return ratio, target

    if hyp["type"] == "nonlinear":
        x = np.array([r[hyp["feature_x"]] for r in arr], dtype=float)
        y = np.array([r[hyp["feature_y"]] for r in arr], dtype=float)
        if hyp["transform"] == "square":
            x = x**2
        elif hyp["transform"] == "sqrt_abs":
            x = np.sqrt(np.abs(x))
        elif hyp["transform"] == "log1p_abs":
            x = np.log1p(np.abs(x))
        elif hyp["transform"] == "interaction":
            x = x * y
            y = np.array([r[hyp["interaction_target"]] for r in arr], dtype=float)
        return x, y

    return None, None


def permutation_null(x, y, n_perm=1000, is_two_sample=False):
    """
    Permutation test.
    For correlations: permute y, measure Pearson r.
    For two-sample: permute labels, measure mean difference.
    Returns (observed_stat, z_score, p_value).
    """
    if is_two_sample:
        obs = float(np.mean(x) - np.mean(y))
        combined = np.concatenate([x, y])
        n_a = len(x)
        null_stats = np.empty(n_perm)
        for i in range(n_perm):
            RNG.shuffle(combined)
            null_stats[i] = combined[:n_a].mean() - combined[n_a:].mean()
    else:
        # Pearson correlation
        x_c = x - x.mean()
        y_c = y - y.mean()
        sx = np.sqrt(np.sum(x_c**2))
        sy = np.sqrt(np.sum(y_c**2))
        if sx < 1e-15 or sy < 1e-15:
            return 0.0, 0.0, 1.0
        obs = float(np.sum(x_c * y_c) / (sx * sy))
        null_stats = np.empty(n_perm)
        for i in range(n_perm):
            y_perm = RNG.permutation(y_c)
            null_stats[i] = np.sum(x_c * y_perm) / (sx * np.sqrt(np.sum(y_perm**2) + 1e-30))

    null_mean = null_stats.mean()
    null_std = null_stats.std()
    if null_std < 1e-15:
        return obs, 0.0, 1.0

    z = (obs - null_mean) / null_std
    p = (np.sum(np.abs(null_stats - null_mean) >= np.abs(obs - null_mean)) + 1) / (n_perm + 1)
    return obs, float(z), float(p)


def cohens_d_corr(r, n):
    """Effect size from correlation: d = 2r / sqrt(1-r^2)."""
    r = np.clip(r, -0.999, 0.999)
    return 2 * r / np.sqrt(1 - r**2)


def cohens_d_two_sample(x, y):
    """Standard two-sample Cohen's d."""
    nx, ny = len(x), len(y)
    mx, my = np.mean(x), np.mean(y)
    vx, vy = np.var(x, ddof=1), np.var(y, ddof=1)
    pooled = np.sqrt(((nx - 1) * vx + (ny - 1) * vy) / (nx + ny - 2))
    if pooled < 1e-15:
        return 0.0
    return float((mx - my) / pooled)


def subset_stability(x, y, n_splits=5, is_two_sample=False):
    """
    Test stability: compute statistic on 80% subsets, check consistency.
    Returns (mean_stat, std_stat, cv).
    """
    stats = []
    n = len(x) if not is_two_sample else len(x) + len(y)

    for _ in range(n_splits):
        if is_two_sample:
            idx_a = RNG.choice(len(x), size=int(0.8 * len(x)), replace=False)
            idx_b = RNG.choice(len(y), size=int(0.8 * len(y)), replace=False)
            sub_x, sub_y = x[idx_a], y[idx_b]
            stats.append(float(np.mean(sub_x) - np.mean(sub_y)))
        else:
            idx = RNG.choice(len(x), size=int(0.8 * len(x)), replace=False)
            sub_x, sub_y = x[idx], y[idx]
            xc = sub_x - sub_x.mean()
            yc = sub_y - sub_y.mean()
            sx = np.sqrt(np.sum(xc**2))
            sy = np.sqrt(np.sum(yc**2))
            if sx < 1e-15 or sy < 1e-15:
                stats.append(0.0)
            else:
                stats.append(float(np.sum(xc * yc) / (sx * sy)))

    stats = np.array(stats)
    mean_s = float(stats.mean())
    std_s = float(stats.std())
    cv = std_s / (abs(mean_s) + 1e-15)
    return mean_s, std_s, cv


# ── run mini battery on one hypothesis ───────────────────────────────────
def run_battery(records, hyp):
    """
    Mini battery: permutation null + effect size + subset stability.
    Returns dict with results and verdict.
    """
    is_two_sample = hyp["type"] == "subset_comparison"
    x, y = extract_xy(records, hyp)

    if x is None or y is None:
        return {"verdict": "SKIP", "reason": "insufficient_data"}
    if len(x) < 20:
        return {"verdict": "SKIP", "reason": "too_few_samples"}

    # Remove non-finite
    if not is_two_sample:
        mask = np.isfinite(x) & np.isfinite(y)
        x, y = x[mask], y[mask]
        if len(x) < 20:
            return {"verdict": "SKIP", "reason": "too_few_finite"}

    # F1: Permutation null
    obs_stat, z_score, p_value = permutation_null(x, y, n_perm=1000, is_two_sample=is_two_sample)

    # F3: Effect size
    if is_two_sample:
        d = cohens_d_two_sample(x, y)
    else:
        d = cohens_d_corr(obs_stat, len(x))

    # Subset stability
    mean_sub, std_sub, cv = subset_stability(x, y, n_splits=5, is_two_sample=is_two_sample)

    # Verdicts
    kill_tests = []

    # F1: permutation null — must have p < 0.05
    if p_value > 0.05:
        kill_tests.append("F1_permutation_null")

    # F3: effect size — Cohen's d must be >= 0.2 (small effect)
    if abs(d) < 0.2:
        kill_tests.append("F3_effect_size")

    # Subset stability — CV must be < 1.0 (not wildly unstable)
    if cv > 1.0:
        kill_tests.append("F5_subset_stability")

    # "Too good to be true" — |z| > 50 is suspicious (likely trivial/tautological)
    if abs(z_score) > 50:
        kill_tests.append("F11_too_good_to_be_true")

    # Effect size too large — |d| > 5 likely artifact
    if abs(d) > 5.0:
        kill_tests.append("F12_effect_artifact")

    verdict = "SURVIVES" if len(kill_tests) == 0 else "KILLED"

    return {
        "verdict": verdict,
        "kill_tests": kill_tests,
        "Re_z": abs(z_score),
        "Re_d": abs(d),
        "z_score": z_score,
        "p_value": p_value,
        "cohens_d": d,
        "obs_stat": obs_stat,
        "subset_cv": cv,
        "subset_mean": mean_sub,
        "subset_std": std_sub,
        "n_samples": len(x) if not is_two_sample else len(x) + len(y),
    }


# ── survival curve & habitable zone (reused from reynolds_number.py) ────
def survival_curve(re_values, survived, n_bins=30):
    """Bin Re values and compute survival rate."""
    re_arr = np.array(re_values)
    surv_arr = np.array(survived)

    percentiles = np.linspace(0, 100, n_bins + 1)
    edges = np.percentile(re_arr, percentiles)
    edges = np.unique(edges)

    centers, rates, counts = [], [], []
    for i in range(len(edges) - 1):
        if i < len(edges) - 2:
            mask = (re_arr >= edges[i]) & (re_arr < edges[i + 1])
        else:
            mask = (re_arr >= edges[i]) & (re_arr <= edges[i + 1])
        n = mask.sum()
        if n < 3:
            continue
        centers.append(float((edges[i] + edges[i + 1]) / 2))
        rates.append(float(surv_arr[mask].mean()))
        counts.append(int(n))

    return centers, rates, counts


def find_habitable_zone(centers, rates, threshold=0.5):
    """Find Re range where survival rate > threshold."""
    if len(centers) < 5:
        return None, None, None, None

    c = np.array(centers)
    r = np.array(rates)

    kernel = np.ones(3) / 3
    smoothed = np.convolve(r, kernel, mode="valid")
    c_smooth = c[1:-1][:len(smoothed)]

    peak_idx = int(np.argmax(smoothed))
    peak_Re = float(c_smooth[peak_idx])
    peak_survival = float(smoothed[peak_idx])

    above = smoothed >= threshold
    if not above.any():
        return None, None, peak_Re, peak_survival

    first_above = int(np.where(above)[0][0])
    last_above = int(np.where(above)[0][-1])

    return float(c_smooth[first_above]), float(c_smooth[last_above]), peak_Re, peak_survival


# ── main ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("NF Reynolds Number Phase Transition Analysis")
    print("=" * 70)

    # Load
    records = load_number_fields()
    print(f"  {len(records)} valid NF records")

    # Generate hypotheses
    hypotheses = generate_hypotheses(records, target=500)

    # Run battery
    results = []
    n_surv, n_kill, n_skip = 0, 0, 0
    for i, hyp in enumerate(hypotheses):
        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/500] survived={n_surv} killed={n_kill} skipped={n_skip}")
        res = run_battery(records, hyp)
        res["hypothesis"] = hyp
        results.append(res)
        if res["verdict"] == "SURVIVES":
            n_surv += 1
        elif res["verdict"] == "KILLED":
            n_kill += 1
        else:
            n_skip += 1

    print(f"\n  Final: {n_surv} survived, {n_kill} killed, {n_skip} skipped")

    # Filter to non-skipped
    active = [r for r in results if r["verdict"] != "SKIP"]
    print(f"  Active hypotheses: {len(active)}")

    if len(active) < 20:
        print("ERROR: too few active hypotheses")
        return

    # Build survival curve
    re_values = [r["Re_z"] for r in active]
    survived = [1 if r["verdict"] == "SURVIVES" else 0 for r in active]

    centers, rates, counts = survival_curve(re_values, survived, n_bins=30)
    Re_low, Re_high, peak_Re, peak_surv = find_habitable_zone(centers, rates, threshold=0.5)

    # Also do Cohen's d curve
    re_d_values = [r["Re_d"] for r in active]
    d_centers, d_rates, d_counts = survival_curve(re_d_values, survived, n_bins=30)
    d_low, d_high, d_peak, d_peak_surv = find_habitable_zone(d_centers, d_rates, threshold=0.5)

    # Kill analysis by quartile
    re_arr = np.array(re_values)
    surv_arr = np.array(survived)
    q25, q50, q75 = np.percentile(re_arr, [25, 50, 75])

    quartile_kills = {}
    for label, lo, hi in [("Q1", 0, q25), ("Q2", q25, q50), ("Q3", q50, q75), ("Q4", q75, 1e30)]:
        subset = [r for r in active if lo <= r["Re_z"] < hi]
        n = len(subset)
        if n == 0:
            continue
        s = sum(1 for r in subset if r["verdict"] == "SURVIVES")
        kills = Counter()
        for r in subset:
            for t in r.get("kill_tests", []):
                kills[t] += 1
        quartile_kills[label] = {
            "n": n,
            "re_range": [round(lo, 3), round(hi, 3)],
            "survival_rate": round(s / n, 4),
            "top_killers": dict(kills.most_common(5)),
        }

    # Hypothesis type breakdown
    type_stats = defaultdict(lambda: {"n": 0, "survived": 0, "re_z_sum": 0})
    for r in active:
        t = r["hypothesis"]["type"]
        type_stats[t]["n"] += 1
        type_stats[t]["survived"] += (1 if r["verdict"] == "SURVIVES" else 0)
        type_stats[t]["re_z_sum"] += r["Re_z"]

    type_summary = {}
    for t, s in type_stats.items():
        type_summary[t] = {
            "n": s["n"],
            "survival_rate": round(s["survived"] / s["n"], 4) if s["n"] > 0 else 0,
            "mean_Re_z": round(s["re_z_sum"] / s["n"], 3) if s["n"] > 0 else 0,
        }

    # Compare to global habitable zone
    global_low, global_high = 4.372, 13.681

    shift = None
    if Re_low is not None and Re_high is not None:
        shift = {
            "nf_low_minus_global_low": round(Re_low - global_low, 3),
            "nf_high_minus_global_high": round(Re_high - global_high, 3),
            "nf_width": round(Re_high - Re_low, 3),
            "global_width": round(global_high - global_low, 3),
            "width_ratio": round((Re_high - Re_low) / (global_high - global_low), 3),
            "center_shift": round(((Re_low + Re_high) / 2) - ((global_low + global_high) / 2), 3),
        }

    # Determine verdict
    if Re_low is not None and Re_high is not None:
        overlap_low = max(Re_low, global_low)
        overlap_high = min(Re_high, global_high)
        overlap = max(0, overlap_high - overlap_low)
        union = max(Re_high, global_high) - min(Re_low, global_low)
        iou = overlap / union if union > 0 else 0

        if iou > 0.6:
            comparison_verdict = "MATCHES_GLOBAL"
            comparison_detail = f"IoU={iou:.3f} — NF habitable zone overlaps strongly with global"
        elif iou > 0.2:
            comparison_verdict = "SHIFTED"
            comparison_detail = f"IoU={iou:.3f} — NF habitable zone partially overlaps with global"
        else:
            comparison_verdict = "DISTINCT"
            comparison_detail = f"IoU={iou:.3f} — NF habitable zone is substantially different from global"
    else:
        comparison_verdict = "NO_ZONE_FOUND"
        comparison_detail = "Could not identify a clear habitable zone in NF data"
        iou = None

    # Build output
    output = {
        "global_reference": {
            "Re_c_low": global_low,
            "Re_c_high": global_high,
            "habitable_zone_width": round(global_high - global_low, 3),
            "source": "X12 reynolds_number_results.json"
        },
        "nf_specific": {
            "total_hypotheses": len(hypotheses),
            "active_hypotheses": len(active),
            "survived": n_surv,
            "killed": n_kill,
            "skipped": n_skip,
            "survival_rate": round(n_surv / len(active), 4) if len(active) > 0 else 0,
        },
        "nf_habitable_zone_Re_z": {
            "Re_c_low": round(Re_low, 3) if Re_low is not None else None,
            "Re_c_high": round(Re_high, 3) if Re_high is not None else None,
            "habitable_zone_width": round(Re_high - Re_low, 3) if (Re_low and Re_high) else None,
            "peak_Re": round(peak_Re, 3) if peak_Re is not None else None,
            "peak_survival": round(peak_surv, 4) if peak_surv is not None else None,
        },
        "nf_habitable_zone_Re_d": {
            "Re_c_low": round(d_low, 3) if d_low is not None else None,
            "Re_c_high": round(d_high, 3) if d_high is not None else None,
            "peak_Re": round(d_peak, 3) if d_peak is not None else None,
            "peak_survival": round(d_peak_surv, 4) if d_peak_surv is not None else None,
        },
        "comparison_to_global": {
            "verdict": comparison_verdict,
            "detail": comparison_detail,
            "IoU": round(iou, 4) if iou is not None else None,
            "shift": shift,
        },
        "survival_curve_Re_z": {
            "bin_centers": [round(c, 3) for c in centers],
            "survival_rates": [round(r, 4) for r in rates],
            "bin_counts": counts,
        },
        "survival_curve_Re_d": {
            "bin_centers": [round(c, 3) for c in d_centers],
            "survival_rates": [round(r, 4) for r in d_rates],
            "bin_counts": d_counts,
        },
        "quartile_analysis": quartile_kills,
        "hypothesis_type_breakdown": type_summary,
        "Re_z_distribution": {
            "mean": round(float(np.mean(re_values)), 3),
            "median": round(float(np.median(re_values)), 3),
            "std": round(float(np.std(re_values)), 3),
            "min": round(float(np.min(re_values)), 3),
            "max": round(float(np.max(re_values)), 3),
            "mean_survivors": round(float(np.mean([r["Re_z"] for r in active if r["verdict"] == "SURVIVES"])), 3) if n_surv > 0 else None,
            "mean_killed": round(float(np.mean([r["Re_z"] for r in active if r["verdict"] == "KILLED"])), 3) if n_kill > 0 else None,
        },
        "sample_survivors": [],
        "sample_killed": [],
    }

    # Add sample survivors/killed for interpretability
    survivors = sorted([r for r in active if r["verdict"] == "SURVIVES"], key=lambda r: r["Re_z"])
    killed_list = sorted([r for r in active if r["verdict"] == "KILLED"], key=lambda r: r["Re_z"])

    for r in survivors[:10]:
        output["sample_survivors"].append({
            "description": r["hypothesis"]["description"],
            "type": r["hypothesis"]["type"],
            "Re_z": round(r["Re_z"], 3),
            "cohens_d": round(r["cohens_d"], 3),
            "p_value": round(r["p_value"], 5),
        })

    for r in killed_list[:10]:
        output["sample_killed"].append({
            "description": r["hypothesis"]["description"],
            "type": r["hypothesis"]["type"],
            "Re_z": round(r["Re_z"], 3),
            "cohens_d": round(r["cohens_d"], 3),
            "kill_tests": r["kill_tests"],
        })

    # Save
    with open(OUT_JSON, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {OUT_JSON}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Global habitable zone:  [{global_low:.3f}, {global_high:.3f}]  (width={global_high-global_low:.3f})")
    if Re_low is not None and Re_high is not None:
        print(f"  NF habitable zone:      [{Re_low:.3f}, {Re_high:.3f}]  (width={Re_high-Re_low:.3f})")
    else:
        print(f"  NF habitable zone:      NOT FOUND")
    print(f"  Comparison:             {comparison_verdict}")
    print(f"  Detail:                 {comparison_detail}")
    print(f"  Survival rate:          {output['nf_specific']['survival_rate']}")
    print(f"  Re_z mean (surv):       {output['Re_z_distribution']['mean_survivors']}")
    print(f"  Re_z mean (kill):       {output['Re_z_distribution']['mean_killed']}")
    print()


if __name__ == "__main__":
    main()
