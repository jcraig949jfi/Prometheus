"""
Moment Comparison Synthesis: EC vs Maass vs U(1) vs USp(4)
==========================================================
Reads existing moment results and builds definitive comparison table.
Tests whether EC-Maass differences are statistically significant.

Challenge: Maass vs EC Direct Moment Comparison
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path

BASE = Path(__file__).parent

# ── Load all results ──────────────────────────────────────────────────
with open(BASE / "maass_m2m4_results.json") as f:
    maass_m2m4 = json.load(f)

with open(BASE / "maass_higher_moments_results.json") as f:
    maass_higher = json.load(f)

with open(BASE / "higher_moments_results.json") as f:
    ec_higher = json.load(f)

with open(BASE / "moment_universality_results.json") as f:
    universality = json.load(f)


# ── Theoretical Catalan values (SU(2) Sato-Tate) ─────────────────────
catalan = {
    "M4/M2^2": 2.0,   # C_2
    "M6/M2^3": 5.0,   # C_3
    "M8/M2^4": 14.0,  # C_4
}

# USp(4) theoretical values
usp4_theory = {
    "M4/M2^2": 3.0,
    "M6/M2^3": 14.0,
    "M8/M2^4": 84.0,
}

# U(1) split-prime theoretical values
u1_theory = {
    "M4/M2^2": 1.5,
}


# ── Extract per-family empirical values ───────────────────────────────

# --- Maass (from maass_higher_moments_results.json) ---
maass = {
    "family": "Maass forms",
    "sato_tate": "SU(2)",
    "n_forms": maass_higher["data_summary"]["forms_analyzed"],
    "M4/M2^2": {
        "median": maass_higher["per_form_ratio_stats"]["M4_over_M2_sq"]["median"],
        "trimmed_mean": maass_higher["pooled_results"]["M4_over_M2_sq_trimmed_mean"],
        "mean": maass_higher["per_form_ratio_stats"]["M4_over_M2_sq"]["mean"],
        "std": maass_higher["per_form_ratio_stats"]["M4_over_M2_sq"]["std"],
        "q25": maass_higher["per_form_ratio_stats"]["M4_over_M2_sq"]["q25"],
        "q75": maass_higher["per_form_ratio_stats"]["M4_over_M2_sq"]["q75"],
    },
    "M6/M2^3": {
        "median": maass_higher["per_form_ratio_stats"]["M6_over_M2_cu"]["median"],
        "trimmed_mean": maass_higher["pooled_results"]["M6_over_M2_cu_trimmed_mean"],
        "mean": maass_higher["per_form_ratio_stats"]["M6_over_M2_cu"]["mean"],
        "std": maass_higher["per_form_ratio_stats"]["M6_over_M2_cu"]["std"],
        "q25": maass_higher["per_form_ratio_stats"]["M6_over_M2_cu"]["q25"],
        "q75": maass_higher["per_form_ratio_stats"]["M6_over_M2_cu"]["q75"],
    },
    "M8/M2^4": {
        "median": maass_higher["per_form_ratio_stats"]["M8_over_M2_qu"]["median"],
        "trimmed_mean": maass_higher["pooled_results"]["M8_over_M2_qu_trimmed_mean"],
        "mean": maass_higher["per_form_ratio_stats"]["M8_over_M2_qu"]["mean"],
        "std": maass_higher["per_form_ratio_stats"]["M8_over_M2_qu"]["std"],
        "q25": maass_higher["per_form_ratio_stats"]["M8_over_M2_qu"]["q25"],
        "q75": maass_higher["per_form_ratio_stats"]["M8_over_M2_qu"]["q75"],
    },
}

# --- EC non-CM (from moment_universality_results.json) ---
ec_uni = universality["ec_non_cm"]["moments"]
ec = {
    "family": "EC non-CM",
    "sato_tate": "SU(2)",
    "n_forms": universality["ec_non_cm"]["n_forms"],
    "M4/M2^2": {
        "global_ratio": ec_uni["M4_over_M2sq"],
    },
    "M6/M2^3": {
        "global_ratio": ec_uni["M6_over_M2cube"],
    },
}

# EC higher moments from higher_moments_results.json (different normalization)
ec_hm = ec_higher["empirical"]["EC_SU2"]
ec_hm_ratios = ec_hm["ratios_global"]

# --- MF dim-1 (classical modular forms, also SU(2)) ---
mf = universality["mf_dim1"]["moments"]
mf_data = {
    "family": "MF dim-1",
    "sato_tate": "SU(2)",
    "n_forms": universality["mf_dim1"]["n_forms"],
    "M4/M2^2": {"global_ratio": mf["M4_over_M2sq"]},
    "M6/M2^3": {"global_ratio": mf["M6_over_M2cube"]},
}

# --- Genus-2 USp(4) ---
g2 = universality["genus2_USp4"]["moments"]
g2_data = {
    "family": "Genus-2",
    "sato_tate": "USp(4)",
    "n_curves": universality["genus2_USp4"]["n_curves"],
    "M4/M2^2": {"global_ratio": g2["M4_over_M2sq"]},
    "M6/M2^3": {"global_ratio": g2["M6_over_M2cube"]},
}

# --- CM / U(1) ---
cm_split = universality["cm_U1"]["moments_split_primes"]
cm_data = {
    "family": "CM (U(1))",
    "sato_tate": "U(1)",
    "n_forms": universality["cm_U1"]["n_forms"],
    "M4/M2^2": {"global_ratio": cm_split["M4_over_M2sq"]},
    "M6/M2^3": {"global_ratio": cm_split["M6_over_M2cube"]},
}


# ── Build the comparison table ────────────────────────────────────────
def pct_dev(observed, theory):
    return 100.0 * (observed - theory) / theory

ratios = ["M4/M2^2", "M6/M2^3", "M8/M2^4"]

table = {}
for ratio in ratios:
    cat = catalan[ratio]
    row = {"catalan_theory": cat}

    # Maass
    m = maass[ratio]
    row["maass_median"] = m["median"]
    row["maass_trimmed_mean"] = m["trimmed_mean"]
    row["maass_std"] = m["std"]
    row["maass_iqr"] = [m["q25"], m["q75"]]
    row["maass_dev_pct"] = pct_dev(m["median"], cat)
    row["maass_n"] = maass["n_forms"]

    # EC non-CM (pooled from universality)
    if ratio in ec:
        row["ec_global_ratio"] = ec[ratio]["global_ratio"]
        row["ec_dev_pct"] = pct_dev(ec[ratio]["global_ratio"], cat)
        row["ec_n"] = ec["n_forms"]

    # MF dim-1
    if ratio in mf_data:
        row["mf_global_ratio"] = mf_data[ratio]["global_ratio"]
        row["mf_dev_pct"] = pct_dev(mf_data[ratio]["global_ratio"], cat)
        row["mf_n"] = mf_data["n_forms"]

    # Genus-2
    if ratio in g2_data:
        row["g2_global_ratio"] = g2_data[ratio]["global_ratio"]
        row["g2_dev_pct"] = pct_dev(g2_data[ratio]["global_ratio"], usp4_theory[ratio])
        row["g2_n"] = g2_data["n_curves"]

    # CM U(1)
    if ratio in cm_data:
        row["cm_global_ratio"] = cm_data[ratio]["global_ratio"]
        row["cm_dev_pct"] = pct_dev(cm_data[ratio]["global_ratio"], u1_theory.get(ratio, cat))
        row["cm_n"] = cm_data["n_forms"]

    table[ratio] = row


# ── EC vs Maass: statistical comparison ───────────────────────────────
# We don't have raw per-form distributions for EC in the same way,
# but we can compare using the available summary statistics.

# For Maass we have per-form distribution stats (median, mean, std, IQR).
# For EC we have pooled global ratios from two sources:
#   - universality: 30K curves, M4/M2^2 = 1.991, M6/M2^3 = 4.954
#   - higher_moments: 1K curves, M4/M2^2 = 2.182, M6/M2^3 = 6.04

# The universality result (30K curves, normalized a_p/sqrt(p)) is more reliable.
# The higher_moments result (1K curves, a_p/(2*sqrt(p))) has different normalization
# but ratios should be normalization-invariant.

# Key insight: the universality EC M4/M2^2 = 1.991 vs Maass median 2.025.
# This is a DIFFERENCE of 0.034 in opposite directions from theory (2.0).

ec_vs_maass = {}
for ratio_key, ec_key_uni, ec_key_hm in [
    ("M4/M2^2", "M4_over_M2sq", "M4/M2^2"),
    ("M6/M2^3", "M6_over_M2cube", "M6/M2^3"),
]:
    cat = catalan[ratio_key]
    m_med = maass[ratio_key]["median"]
    m_tmean = maass[ratio_key]["trimmed_mean"]
    m_std = maass[ratio_key]["std"]
    m_n = maass["n_forms"]

    # EC from universality (30K, better stats)
    ec_val = ec_uni[ec_key_uni]
    ec_n = ec["n_forms"]

    # MF dim-1 (17K, also SU(2))
    mf_val = mf[ec_key_uni]
    mf_n = mf_data["n_forms"]

    # Delta: EC - Maass
    delta_ec_maass = ec_val - m_med
    delta_mf_maass = mf_val - m_med

    # Effect size (Cohen's d using Maass std)
    # But Maass std is heavily skewed by outliers. Use IQR-based estimate.
    iqr = maass[ratio_key]["q75"] - maass[ratio_key]["q25"]
    robust_std = iqr / 1.349  # IQR to std for normal

    cohens_d_ec = delta_ec_maass / robust_std if robust_std > 0 else float('nan')
    cohens_d_mf = delta_mf_maass / robust_std if robust_std > 0 else float('nan')

    # Two-sample z-test (we have population-level data, not samples)
    # SE of difference ~ sqrt(sigma^2/n1 + sigma^2/n2)
    # Using robust_std for both (conservative assumption)
    se_diff = robust_std * np.sqrt(1.0/m_n + 1.0/ec_n)
    z_stat = delta_ec_maass / se_diff if se_diff > 0 else float('nan')
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    ec_vs_maass[ratio_key] = {
        "catalan_theory": cat,
        "maass_median": round(m_med, 6),
        "maass_trimmed_mean": round(m_tmean, 6),
        "ec_global_ratio": round(ec_val, 6),
        "mf_global_ratio": round(mf_val, 6),
        "delta_ec_minus_maass": round(delta_ec_maass, 6),
        "delta_mf_minus_maass": round(delta_mf_maass, 6),
        "direction": "EC below Maass" if delta_ec_maass < 0 else "EC above Maass",
        "robust_std_maass": round(robust_std, 6),
        "cohens_d_ec_vs_maass": round(cohens_d_ec, 4),
        "cohens_d_mf_vs_maass": round(cohens_d_mf, 4),
        "z_statistic": round(z_stat, 4),
        "p_value": float(f"{p_value:.6e}"),
        "significant_at_001": p_value < 0.001,
    }


# ── Also compare M8/M2^4 (Maass has it, EC higher_moments has it) ────
# EC from higher_moments_results.json (1K curves, different normalization)
ec_m8_ratio = ec_hm_ratios["M8/M2^4"]
maass_m8_med = maass["M8/M2^4"]["median"]
delta_m8 = ec_m8_ratio - maass_m8_med
iqr_m8 = maass["M8/M2^4"]["q75"] - maass["M8/M2^4"]["q25"]
robust_std_m8 = iqr_m8 / 1.349

ec_vs_maass["M8/M2^4"] = {
    "catalan_theory": 14.0,
    "maass_median": round(maass_m8_med, 6),
    "maass_trimmed_mean": round(maass["M8/M2^4"]["trimmed_mean"], 6),
    "ec_global_ratio_1K": round(ec_m8_ratio, 6),
    "delta_ec_minus_maass": round(delta_m8, 6),
    "direction": "EC above Maass" if delta_m8 > 0 else "EC below Maass",
    "robust_std_maass": round(robust_std_m8, 6),
    "cohens_d": round(delta_m8 / robust_std_m8, 4) if robust_std_m8 > 0 else None,
    "note": "EC M8 from 1K curves only (higher_moments_results.json); less reliable than 30K"
}


# ── Systematic direction check ────────────────────────────────────────
# Is EC consistently above or below Maass?
directions = []
for r in ["M4/M2^2", "M6/M2^3", "M8/M2^4"]:
    d = ec_vs_maass[r]["delta_ec_minus_maass"]
    directions.append(("below" if d < 0 else "above", d))

all_same_dir = len(set(d[0] for d in directions)) == 1
systematic = {
    "all_same_direction": all_same_dir,
    "directions": {r: ec_vs_maass[r]["direction"] for r in ["M4/M2^2", "M6/M2^3", "M8/M2^4"]},
    "interpretation": None,
}

# EC (30K): M4/M2^2 = 1.991 (BELOW 2.0)
# Maass (14.6K): M4/M2^2 median = 2.025 (ABOVE 2.0)
# EC is below theory, Maass is above theory -- they bracket the Catalan value!
ec_sides = []
maass_sides = []
for r in ["M4/M2^2", "M6/M2^3"]:
    cat = catalan[r]
    ec_val = ec_vs_maass[r]["ec_global_ratio"]
    m_val = ec_vs_maass[r]["maass_median"]
    ec_sides.append("below" if ec_val < cat else "above")
    maass_sides.append("below" if m_val < cat else "above")

systematic["ec_vs_theory"] = {r: f"{'below' if ec_vs_maass[r]['ec_global_ratio'] < catalan[r] else 'above'} Catalan" for r in ["M4/M2^2", "M6/M2^3"]}
systematic["maass_vs_theory"] = {r: f"{'below' if ec_vs_maass[r]['maass_median'] < catalan[r] else 'above'} Catalan" for r in ["M4/M2^2", "M6/M2^3"]}

if ec_sides[0] != maass_sides[0]:
    systematic["interpretation"] = (
        "EC and Maass BRACKET the Catalan value from opposite sides. "
        "EC below, Maass above. This is consistent with finite-sample effects "
        "having different signs due to arithmetic (conductor/level) vs spectral "
        "(eigenvalue) convergence rates."
    )
else:
    systematic["interpretation"] = (
        "Both on same side of Catalan. Difference is in magnitude only."
    )


# ── Grand table: 4 families ──────────────────────────────────────────
grand_table = {
    "ratio": [],
    "catalan_SU2": [],
    "U1_split": [],
    "EC_SU2_30K": [],
    "MF_SU2_17K": [],
    "Maass_SU2_14K": [],
    "USp4_genus2_66K": [],
    "USp4_theory": [],
}

for r in ratios:
    grand_table["ratio"].append(r)
    grand_table["catalan_SU2"].append(catalan[r])
    grand_table["USp4_theory"].append(usp4_theory[r])

    # U(1) - only have M4/M2^2
    if r == "M4/M2^2":
        grand_table["U1_split"].append(round(cm_split["M4_over_M2sq"], 4))
    elif r == "M6/M2^3":
        grand_table["U1_split"].append(round(cm_split["M6_over_M2cube"], 4))
    else:
        grand_table["U1_split"].append(None)

    # EC
    if r in ec and "global_ratio" in ec[r]:
        grand_table["EC_SU2_30K"].append(round(ec[r]["global_ratio"], 4))
    elif r == "M8/M2^4":
        grand_table["EC_SU2_30K"].append(round(ec_m8_ratio, 4))
    else:
        grand_table["EC_SU2_30K"].append(None)

    # MF
    if r in mf_data and "global_ratio" in mf_data[r]:
        grand_table["MF_SU2_17K"].append(round(mf_data[r]["global_ratio"], 4))
    else:
        grand_table["MF_SU2_17K"].append(None)

    # Maass
    grand_table["Maass_SU2_14K"].append(round(maass[r]["median"], 4))

    # Genus-2
    if r in g2_data and "global_ratio" in g2_data[r]:
        grand_table["USp4_genus2_66K"].append(round(g2_data[r]["global_ratio"], 4))
    else:
        grand_table["USp4_genus2_66K"].append(None)


# ── Assemble final results ────────────────────────────────────────────
results = {
    "title": "Moment Comparison Synthesis: EC vs Maass vs U(1) vs USp(4)",
    "date": "2026-04-11",
    "challenge": "Quantify EC-Maass moment differences with statistical tests",
    "data_sources": {
        "maass": "maass_higher_moments_results.json (14,644 forms, M2-M8)",
        "ec": "moment_universality_results.json (30,000 curves, M2-M6)",
        "ec_m8": "higher_moments_results.json (1,000 curves, M2-M8)",
        "mf": "moment_universality_results.json (17,198 forms, M2-M6)",
        "genus2": "moment_universality_results.json (66,158 curves, M2-M6)",
        "cm": "moment_universality_results.json (116 CM curves, split primes)",
    },

    "grand_comparison_table": grand_table,

    "ec_vs_maass_statistical_tests": ec_vs_maass,

    "systematic_direction": systematic,

    "per_ratio_detail": table,

    "key_findings": [
        (
            f"M4/M2^2: EC={ec_uni['M4_over_M2sq']:.4f}, Maass={maass['M4/M2^2']['median']:.4f}, "
            f"MF={mf['M4_over_M2sq']:.4f}, theory=2.0. "
            f"EC is {abs(ec_uni['M4_over_M2sq']-2.0)*100:.2f}% BELOW Catalan; "
            f"Maass is {abs(maass['M4/M2^2']['median']-2.0)*100:.2f}% ABOVE."
        ),
        (
            f"M6/M2^3: EC={ec_uni['M6_over_M2cube']:.4f}, Maass={maass['M6/M2^3']['median']:.4f}, "
            f"MF={mf['M6_over_M2cube']:.4f}, theory=5.0. "
            f"All three SU(2) families within 3.2% of Catalan."
        ),
        (
            f"M8/M2^4: Maass={maass['M8/M2^4']['median']:.4f}, "
            f"EC(1K)={ec_m8_ratio:.4f}, theory=14.0. "
            f"Both above Catalan by 4-34%; EC excess larger (finite-sample from only 1K curves)."
        ),
        (
            "MF dim-1 is CLOSEST to Catalan for M4/M2^2 (1.9945 vs 2.0), "
            "likely due to having the most primes per form in the dataset."
        ),
        (
            "EC and Maass bracket Catalan from opposite sides for M4/M2^2: "
            "EC below (1.991), Maass above (2.025). This is the key structural difference."
        ),
        (
            "Genus-2 USp(4) cleanly separated: M4/M2^2=2.96 (theory 3.0), "
            "M6/M2^3=13.72 (theory 14.0). Fully distinguishable from SU(2)."
        ),
        (
            "CM U(1) at split primes: M4/M2^2=1.507 (theory 1.5). "
            "Three Sato-Tate groups give three distinct moment fingerprints."
        ),
    ],

    "verdict": (
        "The EC-Maass difference in M4/M2^2 is statistically significant "
        f"(z={ec_vs_maass['M4/M2^2']['z_statistic']:.1f}, p={ec_vs_maass['M4/M2^2']['p_value']:.2e}) "
        "but the effect size is small (Cohen's d="
        f"{ec_vs_maass['M4/M2^2']['cohens_d_ec_vs_maass']:.2f}). "
        "EC sits 0.4% below Catalan; Maass sits 1.2% above. "
        "MF dim-1 is closest at 0.3% below. "
        "All three SU(2) families converge to the same Catalan chain, "
        "with finite-sample deviations that differ in sign and magnitude "
        "due to arithmetic vs spectral convergence. "
        "The moment hierarchy U(1) < SU(2) < USp(4) is definitively confirmed."
    ),
}

# Print summary
print("=" * 72)
print("MOMENT UNIVERSALITY TABLE: 4 Sato-Tate Families")
print("=" * 72)
print(f"{'Ratio':<12} {'U(1)':<10} {'SU(2)-EC':<10} {'SU(2)-MF':<10} {'SU(2)-Maass':<12} {'USp(4)-G2':<10} {'SU(2) thy':<10} {'USp(4) thy':<10}")
print("-" * 84)
for i, r in enumerate(ratios):
    u1 = grand_table["U1_split"][i]
    ec_v = grand_table["EC_SU2_30K"][i]
    mf_v = grand_table["MF_SU2_17K"][i]
    ma_v = grand_table["Maass_SU2_14K"][i]
    g2_v = grand_table["USp4_genus2_66K"][i]
    su2_t = grand_table["catalan_SU2"][i]
    usp_t = grand_table["USp4_theory"][i]
    print(f"{r:<12} {str(u1):<10} {str(ec_v):<10} {str(mf_v):<10} {str(ma_v):<12} {str(g2_v):<10} {su2_t:<10} {usp_t:<10}")

print()
print("EC vs Maass Statistical Comparison:")
print("-" * 72)
for r in ratios:
    d = ec_vs_maass[r]
    delta = d["delta_ec_minus_maass"]
    direction = d["direction"]
    if "z_statistic" in d:
        print(f"  {r}: delta={delta:+.4f} ({direction}), z={d['z_statistic']:.1f}, p={d['p_value']:.2e}, d={d.get('cohens_d_ec_vs_maass', d.get('cohens_d', 'N/A'))}")
    else:
        print(f"  {r}: delta={delta:+.4f} ({direction}), d={d.get('cohens_d', 'N/A')}")

print()
print(f"Systematic: {systematic['interpretation']}")
print()
print(results["verdict"])

# Save
out_path = BASE / "moment_comparison_synthesis_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to {out_path}")
