#!/usr/bin/env python3
"""Finance deep: Rolling BREAK_SYMMETRY analysis.
Does sector differentiation track volatility? Sharp or smooth transition?
M1 (Skullport), 2026-04-12
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path("F:/Prometheus/cartography/shared/scripts").resolve())
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)
from battery_v2 import BatteryV2
bv2 = BatteryV2()
from scipy import stats as sp_stats

DATA = Path("F:/Prometheus/cartography/finance/data")

with open(DATA / "ff5_daily.json") as f:
    ff5 = json.load(f)
with open(DATA / "ff_10industry_daily.json") as f:
    ind = json.load(f)

sectors = ['NoDur', 'Durbl', 'Manuf', 'Enrgy', 'HiTec', 'Telcm', 'Shops', 'Hlth', 'Utils', 'Other']

# Build date-aligned arrays
ff5_dates = {d["date"]: d for d in ff5}
ind_dates = {d["date"]: d for d in ind}
common_dates = sorted(set(ff5_dates.keys()) & set(ind_dates.keys()))
common_dates = [d for d in common_dates if int(d[:4]) >= 1963]
print(f"Common dates (1963+): {len(common_dates)}")

mkt_returns = np.array([ff5_dates[d].get("Mkt-RF", 0) for d in common_dates])
sector_matrix = np.array([[ind_dates[d].get(s, 0) for s in sectors] for d in common_dates])

# --- TEST 1: Rolling 252-day cross-sectional dispersion ---
print("\n" + "="*70)
print("TEST 1: Rolling sector dispersion vs rolling market volatility")
print("="*70)

window = 252  # 1 year
rolling_disp = []
rolling_vol = []
rolling_eta2 = []

for i in range(window, len(common_dates), 21):  # monthly steps
    chunk_mkt = mkt_returns[i-window:i]
    chunk_sec = sector_matrix[i-window:i]

    vol = np.std(chunk_mkt)
    disp = np.mean(np.std(chunk_sec, axis=1))
    rolling_vol.append(vol)
    rolling_disp.append(disp)

    # Compute eta2 for this window
    flat_rets = chunk_sec.flatten()
    flat_labels = np.array([sectors[j] for _ in range(window) for j in range(10)])
    if len(set(flat_labels)) >= 2:
        _, r = bv2.F24_variance_decomposition(flat_rets, flat_labels)
        rolling_eta2.append(r.get("eta_squared", 0))
    else:
        rolling_eta2.append(0)

rolling_vol = np.array(rolling_vol)
rolling_disp = np.array(rolling_disp)
rolling_eta2 = np.array(rolling_eta2)

rho_vd, p_vd = sp_stats.spearmanr(rolling_vol, rolling_disp)
rho_ve, p_ve = sp_stats.spearmanr(rolling_vol, rolling_eta2)
print(f"Correlation vol vs dispersion: rho={rho_vd:.4f}, p={p_vd:.2e}")
print(f"Correlation vol vs sector eta2: rho={rho_ve:.4f}, p={p_ve:.2e}")

# Quintiles of rolling vol -> mean eta2
vol_quintiles = np.percentile(rolling_vol, [20, 40, 60, 80])
for q, (lo, hi) in enumerate(zip([0]+list(vol_quintiles), list(vol_quintiles)+[999])):
    mask = (rolling_vol >= lo) & (rolling_vol < hi)
    if sum(mask) > 0:
        print(f"  Vol Q{q+1} [{lo:.2f}-{hi:.2f}]: mean eta2={np.mean(rolling_eta2[mask]):.4f}, n={sum(mask)}")

# --- TEST 2: Transition sharpness ---
print("\n" + "="*70)
print("TEST 2: Is the vol->differentiation transition sharp or smooth?")
print("="*70)

# Fit linear and step function, compare R2
log_vol = np.log(rolling_vol + 0.001)

# Linear
slope, intercept, r_lin, p_lin, se = sp_stats.linregress(log_vol, rolling_eta2)
r2_linear = r_lin**2

# Step function at median vol
median_vol = np.median(rolling_vol)
step_pred = np.where(rolling_vol > median_vol,
                     np.mean(rolling_eta2[rolling_vol > median_vol]),
                     np.mean(rolling_eta2[rolling_vol <= median_vol]))
ss_res_step = np.sum((rolling_eta2 - step_pred)**2)
ss_tot = np.sum((rolling_eta2 - np.mean(rolling_eta2))**2)
r2_step = 1 - ss_res_step / ss_tot if ss_tot > 0 else 0

print(f"Linear model R2: {r2_linear:.4f}")
print(f"Step function R2: {r2_step:.4f}")
print(f"-> {'SMOOTH transition (linear better)' if r2_linear > r2_step else 'SHARP transition (step better)'}")

# --- TEST 3: Sector ranking stability across vol regimes ---
print("\n" + "="*70)
print("TEST 3: Sector mean returns by vol regime (rolling)")
print("="*70)

lo_mask = rolling_vol < np.percentile(rolling_vol, 33)
hi_mask = rolling_vol > np.percentile(rolling_vol, 67)

# Get sector means in each regime
lo_periods = [i for i, m in enumerate(lo_mask) if m]
hi_periods = [i for i, m in enumerate(hi_mask) if m]

def sector_means_for_periods(periods):
    means = {}
    for s_idx, s in enumerate(sectors):
        rets = []
        for p_idx in periods:
            start = window + p_idx * 21
            end = min(start + 252, len(common_dates))
            rets.extend(sector_matrix[start:end, s_idx])
        means[s] = np.mean(rets) if rets else 0
    return means

lo_means = sector_means_for_periods(lo_periods)
hi_means = sector_means_for_periods(hi_periods)

print("Low vol regime rankings:")
for s, m in sorted(lo_means.items(), key=lambda x: -x[1]):
    print(f"  {s:6s}: {m:.4f}")
print("High vol regime rankings:")
for s, m in sorted(hi_means.items(), key=lambda x: -x[1]):
    print(f"  {s:6s}: {m:.4f}")

lo_ranks = [lo_means[s] for s in sectors]
hi_ranks = [hi_means[s] for s in sectors]
rho_rank, p_rank = sp_stats.spearmanr(lo_ranks, hi_ranks)
print(f"\nRank correlation (low vs high vol): rho={rho_rank:.4f}, p={p_rank:.4f}")

# --- TEST 4: Decade-by-decade sector eta2 ---
print("\n" + "="*70)
print("TEST 4: Sector eta2 by decade")
print("="*70)

for decade_start in range(1960, 2030, 10):
    decade_end = decade_start + 10
    mask = [(int(d[:4]) >= decade_start and int(d[:4]) < decade_end) for d in common_dates]
    mask = np.array(mask)
    if sum(mask) < 252:
        continue
    dec_rets = sector_matrix[mask].flatten()
    dec_labels = np.array([sectors[j] for _ in range(sum(mask)) for j in range(10)])
    v, r = bv2.F24_variance_decomposition(dec_rets, dec_labels)
    print(f"  {decade_start}s: n_days={sum(mask)}, sector eta2={r.get('eta_squared',0):.4f} ({v})")

# --- Classification ---
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)
print(f"Vol-dispersion correlation: rho={rho_vd:.4f}")
print(f"Vol-eta2 correlation: rho={rho_ve:.4f}")
print(f"Transition type: {'SMOOTH' if r2_linear > r2_step else 'SHARP'}")
print(f"Sector rank stability across vol: rho={rho_rank:.4f}")

if abs(rho_ve) > 0.3:
    print("-> CONFIRMED: sector differentiation tracks volatility (BREAK_SYMMETRY)")
else:
    print("-> NOT CONFIRMED: sector differentiation independent of volatility")

results = {
    "test": "finance_rolling_symmetry",
    "vol_dispersion_rho": float(rho_vd),
    "vol_eta2_rho": float(rho_ve),
    "r2_linear": float(r2_linear),
    "r2_step": float(r2_step),
    "rank_stability_rho": float(rho_rank),
    "transition": "SMOOTH" if r2_linear > r2_step else "SHARP",
}
with open(DATA / "finance_rolling_symmetry_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to finance_rolling_symmetry_results.json")
