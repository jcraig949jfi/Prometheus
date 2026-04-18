"""
DHKMS theoretical prediction for GUE first-gap deficit at rank-0 EC curves.

Compares Harmonia's observed 31% non-excised residual against what the
Duenez-Huynh-Keating-Miller-Snaith (2012) model predicts.

CRITICAL FINDING from data inspection:
  The JSON metadata says gue_var_baseline = 0.178 (Gaudin, exact GUE).
  Verification: bin 0 has var=0.0809, deficit_pct=54.57.
  Check: (1 - 0.0809/0.178)*100 = 54.55 -- matches.
  So the deficit is ALREADY measured vs exact GUE, NOT vs Wigner surmise.
  The 31% residual is therefore a GENUINE deficit beyond exact GUE.

The question becomes: does DHKMS finite-conductor correction explain it?

For EC L-functions of conductor N, the effective matrix size is:
  N_eff = log(N / (2*pi*e)) / 2

At finite N_eff, the spacing variance is HIGHER than the Gaudin limit,
so the observed deficit (var < Gaudin) goes in the WRONG DIRECTION
for a finite-N correction. Finite-N effects make var LARGER, not smaller.

This means the 31% residual is genuinely anomalous from the DHKMS perspective.
"""

import json
import numpy as np
from pathlib import Path

# -- Constants --
VAR_WIGNER = 4 / np.pi - 1          # 0.27324 -- 2x2 GUE Wigner surmise variance
VAR_GAUDIN = 0.178                   # exact infinite-GUE (Gaudin distribution) variance

# -- Load Harmonia results --
results_path = Path(__file__).parent.parent / "cartography" / "docs" / "wsw_F011_rank0_residual_results.json"
with open(results_path) as f:
    data = json.load(f)

bins = data["per_conductor_bin"]
baseline = data["_meta"]["gue_var_baseline"]

print("=" * 90)
print("DHKMS Prediction vs Harmonia Observed Deficit (rank-0 EC curves)")
print("=" * 90)
print()

# -- Verify baseline --
b0 = bins[0]
check = (1 - b0["var"] / baseline) * 100
print(f"Baseline verification:")
print(f"  JSON gue_var_baseline = {baseline}")
print(f"  Bin 0: var={b0['var']:.5f}, deficit_pct={b0['deficit_pct']:.2f}")
print(f"  Check: (1 - {b0['var']:.5f}/{baseline})*100 = {check:.2f}  [matches: {abs(check - b0['deficit_pct']) < 0.1}]")
print()
print(f"  ==> Harmonia used Gaudin (exact GUE) as baseline, NOT Wigner surmise.")
print(f"  ==> The 31% residual is a genuine deficit below exact infinite-GUE variance.")
print()

# -- Reference variances --
print(f"Reference variances:")
print(f"  Wigner surmise (2x2 GUE):     {VAR_WIGNER:.6f}")
print(f"  Gaudin (exact infinite GUE):   {VAR_GAUDIN:.6f}  <-- this is the baseline used")
print()

# -- Compute DHKMS effective matrix size --
def N_eff_DHKMS(log_cond):
    """Effective matrix size from DHKMS for EC family."""
    return (log_cond - np.log(2 * np.pi * np.e)) / 2

# -- Finite-N GUE spacing variance --
# At finite N, the spacing variance is ABOVE Gaudin:
#   var(N) ~ var_Gaudin * (1 + c/N^2)
# where c ~ 0.7 for GUE (Forrester).
# This means the PREDICTED deficit vs Gaudin at finite N is NEGATIVE
# (variance is above baseline, not below).

def var_finite_GUE(N_eff, c=0.7):
    """Finite-N GUE spacing variance (above Gaudin for small N)."""
    if N_eff <= 0:
        return 1.0
    return VAR_GAUDIN * (1 + c / N_eff**2)

def deficit_vs_gaudin(var_obs):
    """Deficit percentage relative to exact Gaudin distribution."""
    return (1 - var_obs / VAR_GAUDIN) * 100

# -- Per-bin analysis --
print(f"{'Bin':>3}  {'log(N)':>7}  {'N':>8}  {'N_eff':>6}  {'var_obs':>8}  "
      f"{'def_obs%':>8}  {'var_DHKMS':>9}  {'def_DHKMS%':>10}  {'genuine%':>10}")
print("-" * 100)

observed_deficits = []
dhkms_deficits = []
genuine_list = []

for b in bins:
    log_N = b["mean_log_cond"]
    cond = np.exp(log_N)
    var_obs = b["var"]
    def_obs = b["deficit_pct"]

    n_eff = N_eff_DHKMS(log_N)
    var_dhkms = var_finite_GUE(n_eff)
    def_dhkms = deficit_vs_gaudin(var_dhkms)

    # Genuine anomaly = what's left after DHKMS correction
    # def_obs is already vs Gaudin; def_dhkms predicts a NEGATIVE deficit (var > Gaudin)
    # So genuine = def_obs - def_dhkms (def_dhkms is negative, so genuine > def_obs)
    genuine = def_obs - def_dhkms

    observed_deficits.append(def_obs)
    dhkms_deficits.append(def_dhkms)
    genuine_list.append(genuine)

    print(f"{b['bin']:>3}  {log_N:>7.3f}  {cond:>8.1f}  {n_eff:>6.3f}  {var_obs:>8.5f}  "
          f"{def_obs:>8.2f}  {var_dhkms:>9.5f}  {def_dhkms:>10.2f}  {genuine:>10.2f}")

print()
print("=" * 90)
print("SUMMARY")
print("=" * 90)
print()

mean_def_obs = np.mean(observed_deficits)
mean_def_dhkms = np.mean(dhkms_deficits)
mean_genuine = np.mean(genuine_list)

print(f"Mean observed deficit vs Gaudin:       {mean_def_obs:.2f}%")
print(f"Mean DHKMS predicted deficit vs Gaudin: {mean_def_dhkms:.2f}%")
print(f"  (Negative = finite-N pushes variance ABOVE Gaudin)")
print(f"Mean genuine anomaly (obs - DHKMS):    {mean_genuine:.2f}%")
print()

# -- Harmonia's extrapolated residual --
eps0 = data["fit_power_law"]["epsilon_0_asymptotic_deficit_pct"]
eps0_se = data["fit_power_law"]["se_epsilon_0"]
print(f"Harmonia's extrapolated residual (conductor -> inf): {eps0:.2f}% +/- {eps0_se:.2f}%")
print()

# At conductor -> inf, N_eff -> inf, so DHKMS predicts deficit -> 0% (var -> Gaudin)
print(f"DHKMS prediction at N -> inf: deficit = 0% (var converges to Gaudin)")
print(f"Harmonia measured: deficit = {eps0:.2f}% at N -> inf")
print()

print("=" * 90)
print("VERDICT")
print("=" * 90)
print()
print(f"The DHKMS model predicts ZERO deficit at large conductor (vs Gaudin).")
print(f"At finite conductor, DHKMS predicts the variance should be ABOVE Gaudin")
print(f"(negative deficit), meaning the observed data has even MORE suppression")
print(f"than what would be anomalous in the infinite-N limit.")
print()
print(f"Decomposition of the 31.1% asymptotic residual:")
print(f"  - Explained by Wigner-to-Gaudin reference error:  0.0%  (Harmonia already used Gaudin)")
print(f"  - Explained by DHKMS finite-N correction:         0.0%  (correction goes wrong direction)")
print(f"  - Genuinely anomalous:                           {eps0:.1f}%  (100% of the residual)")
print()
print(f"The 31% deficit is ENTIRELY unexplained by DHKMS. In fact, DHKMS makes")
print(f"it WORSE: at the observed conductor range (N ~ 40-270, N_eff ~ 0.5-1.4),")
print(f"the finite-matrix correction predicts variance ABOVE Gaudin, so the true")
print(f"anomaly is even larger than 31%.")
print()

# -- Additional check: what if the gaps aren't mean-normalized? --
print("=" * 90)
print("SANITY CHECK: Mean normalization")
print("=" * 90)
print()
print(f"The JSON reports raw variance of gaps, not variance of gaps/mean(gap).")
print(f"If mean(gap) != 1, the comparison to Gaudin (which assumes mean=1) is affected.")
print(f"")
print(f"If Harmonia's gaps have mean m, then:")
print(f"  var_raw = m^2 * var_normalized")
print(f"  deficit should be computed from var_normalized = var_raw / m^2")
print(f"")
print(f"For the observed var ~ 0.10 to match Gaudin (0.178):")
print(f"  We'd need m = sqrt(0.10 / 0.178) = {np.sqrt(0.10 / 0.178):.3f}")
print(f"  i.e., mean gap = {np.sqrt(0.10 / 0.178):.3f} instead of 1.0")
print(f"")
print(f"This is a {(1 - np.sqrt(0.10 / 0.178))*100:.1f}% mean deviation -- plausible if")
print(f"the unfolding procedure has a systematic bias at low conductor.")
print(f"")
print(f"CHECK: Harmonia's pooled analysis reported mean_gap = 0.944.")
print(f"Normalizing: var_normalized = 0.10 / 0.944^2 = {0.10 / 0.944**2:.4f}")
print(f"Deficit vs Gaudin after normalizing: {(1 - 0.10/0.944**2/0.178)*100:.1f}%")
print(f"")
print(f"Even after mean-normalization, a ~37% deficit remains.")
print(f"The mean-normalization explains only ~{46.4 - (1 - 0.10/0.944**2/0.178)*100:.0f} percentage points.")
print()

# -- Final quantitative summary --
print("=" * 90)
print("FINAL ACCOUNTING")
print("=" * 90)
print()

mean_var = np.mean([b["var"] for b in bins])
mean_gap_est = 0.944  # from Harmonia pooled
var_norm = mean_var / mean_gap_est**2
def_norm = (1 - var_norm / VAR_GAUDIN) * 100

print(f"  Mean raw variance across bins:        {mean_var:.5f}")
print(f"  Estimated mean gap (from Harmonia):    {mean_gap_est}")
print(f"  Mean-normalized variance:              {var_norm:.5f}")
print(f"  Deficit vs Gaudin (after normalizing): {def_norm:.1f}%")
print()
print(f"  DHKMS finite-N correction at N_eff~1:  makes deficit ~{-np.mean(dhkms_deficits):.0f}% WORSE")
print(f"    (pushes expected variance to ~{var_finite_GUE(1.0):.3f}, above Gaudin)")
print()
print(f"  CONCLUSION: {def_norm:.0f}% of the gap variance deficit is genuine.")
print(f"  DHKMS explains 0% of it. The finite-conductor correction goes the wrong way.")
print(f"  The only possible mundane explanation is systematic unfolding error at low conductor.")
