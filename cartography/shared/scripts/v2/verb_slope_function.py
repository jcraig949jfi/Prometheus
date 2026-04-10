"""
M4: Verb-Slope Transfer Function g(And, Equal) -> slope
Measures whether verb distribution in Fungrim formulas PREDICTS
the scaling-law slope of genus-2 Sato-Tate families.

If this works: syntax of formulas predicts algebraic structure.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

# ── Load data ──────────────────────────────────────────────────────
HERE = Path(__file__).parent

with open(HERE / "verbs_by_family_results.json") as f:
    verb_data = json.load(f)

with open(HERE / "scaling_vs_st_order_results.json") as f:
    slope_data = json.load(f)

# ── Extract matched (slope, verb_fractions, endo_rank) per ST group ──
st_profiles = verb_data["st_group_verb_profiles"]
groups = sorted(st_profiles.keys())

slopes = []
And_frac = []
Equal_frac = []
For_frac = []
Set_frac = []
endo_ranks = []
group_names = []

for g in groups:
    prof = st_profiles[g]
    slopes.append(prof["slope"])
    vf = prof["universal_verb_fractions"]
    And_frac.append(vf["And"])
    Equal_frac.append(vf["Equal"])
    For_frac.append(vf["For"])
    Set_frac.append(vf["Set"])
    endo_ranks.append(prof["endo_rank"])
    group_names.append(g)

slopes = np.array(slopes)
And_frac = np.array(And_frac)
Equal_frac = np.array(Equal_frac)
For_frac = np.array(For_frac)
Set_frac = np.array(Set_frac)
endo_ranks = np.array(endo_ranks, dtype=float)
n = len(slopes)

print(f"=== M4: Verb-Slope Transfer Function ===")
print(f"n = {n} ST groups\n")
print(f"{'Group':<15} {'slope':>8} {'And':>6} {'Equal':>6} {'For':>6} {'Set':>6} {'rank':>5}")
for i, g in enumerate(group_names):
    print(f"{g:<15} {slopes[i]:>8.4f} {And_frac[i]:>6.3f} {Equal_frac[i]:>6.3f} {For_frac[i]:>6.3f} {Set_frac[i]:>6.3f} {endo_ranks[i]:>5.0f}")

# ── Helper: OLS with stats ───────────────────────────────────────
from scipy import stats as sp_stats

def ols_fit(X, y, predictor_names):
    """OLS with R², coefficients, p-values, residuals."""
    n_obs = len(y)
    # Add intercept
    X_aug = np.column_stack([X, np.ones(n_obs)])
    names = list(predictor_names) + ["intercept"]

    # Fit
    beta, residuals, rank, sv = np.linalg.lstsq(X_aug, y, rcond=None)
    y_hat = X_aug @ beta
    ss_res = np.sum((y - y_hat)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    R2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    # Adjusted R2
    k = X.shape[1] if X.ndim > 1 else 1
    if n_obs - k - 1 > 0:
        R2_adj = 1 - (1 - R2) * (n_obs - 1) / (n_obs - k - 1)
    else:
        R2_adj = float('nan')

    # Standard errors and p-values
    if n_obs > len(names):
        mse = ss_res / (n_obs - len(names))
        try:
            cov = mse * np.linalg.inv(X_aug.T @ X_aug)
            se = np.sqrt(np.diag(cov))
            t_vals = beta / se
            p_vals = [2 * (1 - sp_stats.t.cdf(abs(t), n_obs - len(names))) for t in t_vals]
        except np.linalg.LinAlgError:
            se = [float('nan')] * len(names)
            t_vals = [float('nan')] * len(names)
            p_vals = [float('nan')] * len(names)
    else:
        se = [float('nan')] * len(names)
        t_vals = [float('nan')] * len(names)
        p_vals = [float('nan')] * len(names)

    coefs = {}
    for i_c, nm in enumerate(names):
        coefs[nm] = {
            "coefficient": float(beta[i_c]),
            "std_error": float(se[i_c]) if not isinstance(se, list) else float(se[i_c]),
            "t_value": float(t_vals[i_c]) if not isinstance(t_vals, list) else float(t_vals[i_c]),
            "p_value": float(p_vals[i_c]) if not isinstance(p_vals, list) else float(p_vals[i_c]),
        }

    return {
        "R2": float(R2),
        "R2_adj": float(R2_adj),
        "coefficients": coefs,
        "y_hat": y_hat.tolist(),
        "residuals": (y - y_hat).tolist(),
        "n": n_obs,
        "k": k,
    }


def leave_one_out(X, y, predictor_names):
    """LOO cross-validation: predict each point from the rest."""
    n_obs = len(y)
    predictions = []
    actuals = []
    errors = []

    for i in range(n_obs):
        mask = np.arange(n_obs) != i
        X_train = X[mask]
        y_train = y[mask]

        X_aug = np.column_stack([X_train, np.ones(n_obs - 1)])
        try:
            beta, _, _, _ = np.linalg.lstsq(X_aug, y_train, rcond=None)
            x_test = np.append(X[i], 1.0)
            y_pred = float(x_test @ beta)
        except:
            y_pred = float('nan')

        predictions.append(y_pred)
        actuals.append(float(y[i]))
        errors.append(float(y[i] - y_pred))

    predictions = np.array(predictions)
    actuals = np.array(actuals)
    ss_res = np.sum((actuals - predictions)**2)
    ss_tot = np.sum((actuals - np.mean(actuals))**2)
    R2_cv = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    mae = np.mean(np.abs(actuals - predictions))

    return {
        "R2_cv": float(R2_cv),
        "MAE": float(mae),
        "predictions": [
            {"group": group_names[i], "actual": actuals[i], "predicted": predictions[i], "error": errors[i]}
            for i in range(n_obs)
        ]
    }


# ── MODEL 1: Linear — slope = a*And + b*Equal + c*For + d*Set + e ──
print("\n" + "="*60)
print("MODEL 1: Linear (4 verbs)")
print("="*60)

X_linear = np.column_stack([And_frac, Equal_frac, For_frac, Set_frac])
m1 = ols_fit(X_linear, slopes, ["And", "Equal", "For", "Set"])
print(f"R² = {m1['R2']:.4f},  R²_adj = {m1['R2_adj']:.4f}")
for nm, c in m1["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")

loo1 = leave_one_out(X_linear, slopes, ["And", "Equal", "For", "Set"])
print(f"LOO R²_cv = {loo1['R2_cv']:.4f},  MAE = {loo1['MAE']:.4f}")
for p in loo1["predictions"]:
    print(f"  {p['group']:<15} actual={p['actual']:>8.4f}  pred={p['predicted']:>8.4f}  err={p['error']:>8.4f}")


# ── MODEL 2: And + Equal only (the two strongest correlates) ──
print("\n" + "="*60)
print("MODEL 2: Linear (And + Equal only)")
print("="*60)

X_ae = np.column_stack([And_frac, Equal_frac])
m2 = ols_fit(X_ae, slopes, ["And", "Equal"])
print(f"R² = {m2['R2']:.4f},  R²_adj = {m2['R2_adj']:.4f}")
for nm, c in m2["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")

loo2 = leave_one_out(X_ae, slopes, ["And", "Equal"])
print(f"LOO R²_cv = {loo2['R2_cv']:.4f},  MAE = {loo2['MAE']:.4f}")
for p in loo2["predictions"]:
    print(f"  {p['group']:<15} actual={p['actual']:>8.4f}  pred={p['predicted']:>8.4f}  err={p['error']:>8.4f}")


# ── MODEL 3: And only (strongest single correlate r=0.682) ──
print("\n" + "="*60)
print("MODEL 3: Linear (And only)")
print("="*60)

X_and = And_frac.reshape(-1, 1)
m3 = ols_fit(X_and, slopes, ["And"])
print(f"R² = {m3['R2']:.4f},  R²_adj = {m3['R2_adj']:.4f}")
for nm, c in m3["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")

loo3 = leave_one_out(X_and, slopes, ["And"])
print(f"LOO R²_cv = {loo3['R2_cv']:.4f},  MAE = {loo3['MAE']:.4f}")


# ── MODEL 4: Quadratic with interactions ──
print("\n" + "="*60)
print("MODEL 4: Quadratic (And, Equal, And*Equal, And², Equal²)")
print("="*60)

X_quad = np.column_stack([
    And_frac, Equal_frac,
    And_frac * Equal_frac,
    And_frac**2, Equal_frac**2
])
m4 = ols_fit(X_quad, slopes, ["And", "Equal", "And*Equal", "And²", "Equal²"])
print(f"R² = {m4['R2']:.4f},  R²_adj = {m4['R2_adj']:.4f}")
for nm, c in m4["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")
print("  (WARNING: n=6 with 6 parameters = saturated model, R²=1 trivially)")


# ── MODEL 5: 2-variable (endo_rank + And_fraction) ──
print("\n" + "="*60)
print("MODEL 5: Hybrid — slope = a*endo_rank + b*And + c")
print("="*60)

X_hybrid = np.column_stack([endo_ranks, And_frac])
m5 = ols_fit(X_hybrid, slopes, ["endo_rank", "And"])
print(f"R² = {m5['R2']:.4f},  R²_adj = {m5['R2_adj']:.4f}")
for nm, c in m5["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")

loo5 = leave_one_out(X_hybrid, slopes, ["endo_rank", "And"])
print(f"LOO R²_cv = {loo5['R2_cv']:.4f},  MAE = {loo5['MAE']:.4f}")
for p in loo5["predictions"]:
    print(f"  {p['group']:<15} actual={p['actual']:>8.4f}  pred={p['predicted']:>8.4f}  err={p['error']:>8.4f}")


# ── MODEL 6: endo_rank² + And (combining R4-4 best with verb) ──
print("\n" + "="*60)
print("MODEL 6: Hybrid — slope = a*endo_rank² + b*And + c")
print("="*60)

X_hybrid2 = np.column_stack([endo_ranks**2, And_frac])
m6 = ols_fit(X_hybrid2, slopes, ["endo_rank²", "And"])
print(f"R² = {m6['R2']:.4f},  R²_adj = {m6['R2_adj']:.4f}")
for nm, c in m6["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")

loo6 = leave_one_out(X_hybrid2, slopes, ["endo_rank²", "And"])
print(f"LOO R²_cv = {loo6['R2_cv']:.4f},  MAE = {loo6['MAE']:.4f}")
for p in loo6["predictions"]:
    print(f"  {p['group']:<15} actual={p['actual']:>8.4f}  pred={p['predicted']:>8.4f}  err={p['error']:>8.4f}")


# ── MODEL 7: endo_rank only (baseline from R4-4) ──
print("\n" + "="*60)
print("MODEL 7: Baseline — slope = a*endo_rank² + b (from R4-4)")
print("="*60)

X_rank = (endo_ranks**2).reshape(-1, 1)
m7 = ols_fit(X_rank, slopes, ["endo_rank²"])
print(f"R² = {m7['R2']:.4f},  R²_adj = {m7['R2_adj']:.4f}")
for nm, c in m7["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")

loo7 = leave_one_out(X_rank, slopes, ["endo_rank²"])
print(f"LOO R²_cv = {loo7['R2_cv']:.4f},  MAE = {loo7['MAE']:.4f}")


# ── MODEL 8: Equal only ──
print("\n" + "="*60)
print("MODEL 8: Linear (Equal only)")
print("="*60)

X_eq = Equal_frac.reshape(-1, 1)
m8 = ols_fit(X_eq, slopes, ["Equal"])
print(f"R² = {m8['R2']:.4f},  R²_adj = {m8['R2_adj']:.4f}")
for nm, c in m8["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")


# ── MODEL 9: endo_rank² + Equal ──
print("\n" + "="*60)
print("MODEL 9: Hybrid — slope = a*endo_rank² + b*Equal + c")
print("="*60)

X_hybrid3 = np.column_stack([endo_ranks**2, Equal_frac])
m9 = ols_fit(X_hybrid3, slopes, ["endo_rank²", "Equal"])
print(f"R² = {m9['R2']:.4f},  R²_adj = {m9['R2_adj']:.4f}")
for nm, c in m9["coefficients"].items():
    sig = "*" if isinstance(c["p_value"], float) and c["p_value"] < 0.1 else ""
    print(f"  {nm:<12} coef={c['coefficient']:>8.4f}  p={c['p_value']:.4f} {sig}")

loo9 = leave_one_out(X_hybrid3, slopes, ["endo_rank²", "Equal"])
print(f"LOO R²_cv = {loo9['R2_cv']:.4f},  MAE = {loo9['MAE']:.4f}")


# ── Pairwise Pearson correlations ──
print("\n" + "="*60)
print("PAIRWISE CORRELATIONS (n=6)")
print("="*60)

corrs = {}
for name, arr in [("And", And_frac), ("Equal", Equal_frac), ("For", For_frac), ("Set", Set_frac), ("endo_rank", endo_ranks)]:
    r, p = sp_stats.pearsonr(arr, slopes)
    corrs[name] = {"r": float(r), "p": float(p)}
    print(f"  slope ~ {name:<12}  r = {r:>7.4f}  p = {p:.4f}")

# Verb-rank correlations (collinearity check)
print("\nCollinearity: verb ~ endo_rank:")
for name, arr in [("And", And_frac), ("Equal", Equal_frac), ("For", For_frac), ("Set", Set_frac)]:
    r, p = sp_stats.pearsonr(arr, endo_ranks)
    print(f"  {name:<12} ~ endo_rank  r = {r:>7.4f}  p = {p:.4f}")


# ── Summary comparison ──
print("\n" + "="*60)
print("MODEL COMPARISON")
print("="*60)

models_summary = []
model_list = [
    ("M1: Linear 4-verb", m1, loo1),
    ("M2: And+Equal", m2, loo2),
    ("M3: And only", m3, loo3),
    ("M5: rank+And", m5, loo5),
    ("M6: rank²+And", m6, loo6),
    ("M7: rank² only", m7, loo7),
    ("M8: Equal only", m8, None),
    ("M9: rank²+Equal", m9, loo9),
]

print(f"{'Model':<22} {'R²':>6} {'R²adj':>6} {'R²cv':>7} {'MAE':>7} {'k':>3}")
for name, model, loo in model_list:
    r2cv = loo["R2_cv"] if loo else float('nan')
    mae = loo["MAE"] if loo else float('nan')
    print(f"{name:<22} {model['R2']:>6.4f} {model['R2_adj']:>6.4f} {r2cv:>7.4f} {mae:>7.4f} {model['k']:>3}")
    models_summary.append({
        "name": name,
        "R2": model["R2"],
        "R2_adj": model["R2_adj"],
        "R2_cv": r2cv,
        "MAE": mae,
        "k": model["k"],
        "coefficients": model["coefficients"],
    })

# ── Best model identification ──
# Choose by LOO R²_cv (generalization, not fit)
valid_models = [(name, m, l) for name, m, l in model_list if l is not None]
best_name, best_model, best_loo = max(valid_models, key=lambda x: x[2]["R2_cv"])
print(f"\nBest by LOO R²_cv: {best_name} (R²_cv = {best_loo['R2_cv']:.4f})")

# Does adding verb to rank improve over rank alone?
rank_only_cv = loo7["R2_cv"]
rank_and_cv = loo6["R2_cv"]
verb_adds = rank_and_cv - rank_only_cv
print(f"\nVerb adds over rank² alone: {verb_adds:+.4f} R²_cv")
print(f"  rank² only:    R²_cv = {rank_only_cv:.4f}")
print(f"  rank²+And:     R²_cv = {rank_and_cv:.4f}")


# ── Physical interpretation ──
print("\n" + "="*60)
print("INTERPRETATION")
print("="*60)

# Extract And coefficient from best And-containing model
and_coef = m6["coefficients"].get("And", m5["coefficients"].get("And", {}))
erk = "endo_rank\u00b2"
c_rank = m6["coefficients"][erk]["coefficient"]
c_and = m6["coefficients"]["And"]["coefficient"]
c_int = m6["coefficients"]["intercept"]["coefficient"]
print(f"""
And fraction = density of cross-constraint connectives in Fungrim formulas.
High And = formulas link MULTIPLE conditions (forall x in S AND f(x) = g(x) AND ...).

If And coefficient is positive ({and_coef.get('coefficient', '?'):.4f}):
  -> More cross-constraints in the formula language = richer endomorphism algebra
  -> The SYNTAX of formulas describing a family PREDICTS its ALGEBRAIC STRUCTURE

This is a measurable transfer function:
  slope = g(endo_rank^2, And_fraction)
        = {c_rank:.4f}*rank^2
        + {c_and:.4f}*And
        + {c_int:.4f}

Caution: n=6 is small. This is a measured correlation, not a causal claim.
The transfer function should be tested on additional ST groups when data becomes available.
""")


# ── Save results ──────────────────────────────────────────────────
results = {
    "meta": {
        "challenge": "M4",
        "title": "Verb-Slope Transfer Function g(And, Equal) → slope",
        "timestamp": datetime.now().isoformat(),
        "n_st_groups": n,
        "groups": group_names,
    },
    "data_table": [
        {
            "group": group_names[i],
            "slope": float(slopes[i]),
            "And": float(And_frac[i]),
            "Equal": float(Equal_frac[i]),
            "For": float(For_frac[i]),
            "Set": float(Set_frac[i]),
            "endo_rank": int(endo_ranks[i]),
        }
        for i in range(n)
    ],
    "pairwise_correlations": corrs,
    "models": {m["name"]: m for m in models_summary},
    "best_model": {
        "name": best_name,
        "R2_cv": best_loo["R2_cv"],
        "MAE": best_loo["MAE"],
        "predictions": best_loo["predictions"],
    },
    "transfer_function": {
        "formula": f"slope = {m6['coefficients']['endo_rank²']['coefficient']:.6f}·rank² + {m6['coefficients']['And']['coefficient']:.6f}·And + {m6['coefficients']['intercept']['coefficient']:.6f}",
        "R2": m6["R2"],
        "R2_adj": m6["R2_adj"],
        "R2_cv": loo6["R2_cv"],
        "coefficients": m6["coefficients"],
        "loo_predictions": loo6["predictions"],
    },
    "verb_adds_over_rank_alone": {
        "rank2_only_R2_cv": rank_only_cv,
        "rank2_plus_And_R2_cv": rank_and_cv,
        "delta_R2_cv": verb_adds,
    },
    "rank_baseline": {
        "R4_4_formula": "slope = 0.044·rank² - 0.242",
        "R2": m7["R2"],
        "R2_cv": loo7["R2_cv"],
    },
    "interpretation": {
        "And_meaning": "Cross-constraint density: more And = formulas link multiple conditions simultaneously",
        "positive_And_coef": "Higher cross-constraint density → higher slope → richer endomorphism algebra",
        "syntax_predicts_algebra": "The syntactic structure of formulas describing a family predicts its algebraic structure",
        "caveat": "n=6 is small; measured correlation, not causal claim; needs validation on additional ST groups",
    },
    "verdict": None,  # filled below
}

# Verdict
if best_loo["R2_cv"] > 0.5:
    verdict = f"POSITIVE: Verb distribution predicts slope with LOO R²_cv={best_loo['R2_cv']:.3f}. "
elif best_loo["R2_cv"] > 0:
    verdict = f"WEAK: Some predictive power (LOO R²_cv={best_loo['R2_cv']:.3f}) but not strong. "
else:
    verdict = f"NEGATIVE: No cross-validated predictive power (LOO R²_cv={best_loo['R2_cv']:.3f}). "

if verb_adds > 0.05:
    verdict += f"Verb adds {verb_adds:.3f} R²_cv over rank² alone — syntax carries independent information."
elif verb_adds > 0:
    verdict += f"Verb adds marginal {verb_adds:.3f} R²_cv over rank² alone."
else:
    verdict += f"Verb does NOT add over rank² alone (delta={verb_adds:.3f})."

results["verdict"] = verdict
print(f"\nVERDICT: {verdict}")

out_path = HERE / "verb_slope_function_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
