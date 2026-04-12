#!/usr/bin/env python3
"""
Finance Domain Expansion: Sector->Returns + Factor Analysis through Prometheus battery.
The SC_class->Tc analog for markets. Tests BREAK_SYMMETRY across market regimes.

Known ground truths for calibration:
- Size effect (SMB > 0 historically)
- Value premium (HML > 0 historically)
- Momentum (MOM > 0 historically)
- Volatility clustering (GARCH)
- Fat tails (M4/M2 >> 3)

Battery v6 (F24+F24b+F25+F27). Machine: M1 (Skullport), 2026-04-12
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

DATA = Path("F:/Prometheus/cartography/finance/data")

# Load data
with open(DATA / "ff5_daily.json") as f:
    ff5 = json.load(f)
with open(DATA / "ff_10industry_daily.json") as f:
    ind = json.load(f)
with open(DATA / "ff_momentum_daily.json") as f:
    mom = json.load(f)

print(f"FF5 factors: {len(ff5)} days")
print(f"10 Industry: {len(ind)} days")
print(f"Momentum: {len(mom)} days")

sectors = ['NoDur', 'Durbl', 'Manuf', 'Enrgy', 'HiTec', 'Telcm', 'Shops', 'Hlth', 'Utils', 'Other']

# ─── CALIBRATION: Known ground truths ───
print("\n" + "="*70)
print("CALIBRATION: Known financial ground truths")
print("="*70)

# Size effect
smb = np.array([d.get('SMB', 0) for d in ff5], dtype=float)
print(f"SMB (size effect): mean={np.mean(smb):.4f}%/day, t={np.mean(smb)/np.std(smb)*np.sqrt(len(smb)):.2f}")
print(f"  {'CONFIRMED' if np.mean(smb) > 0 else 'REVERSED'} (expect positive)")

# Value premium
hml = np.array([d.get('HML', 0) for d in ff5], dtype=float)
print(f"HML (value premium): mean={np.mean(hml):.4f}%/day, t={np.mean(hml)/np.std(hml)*np.sqrt(len(hml)):.2f}")
print(f"  {'CONFIRMED' if np.mean(hml) > 0 else 'REVERSED'} (expect positive)")

# Momentum
mom_vals = np.array([d.get('Mom', 0) for d in mom], dtype=float)
print(f"MOM (momentum): mean={np.mean(mom_vals):.4f}%/day, t={np.mean(mom_vals)/np.std(mom_vals)*np.sqrt(len(mom_vals)):.2f}")
print(f"  {'CONFIRMED' if np.mean(mom_vals) > 0 else 'REVERSED'} (expect positive)")

# Fat tails
mkt = np.array([d.get('Mkt-RF', 0) for d in ff5], dtype=float)
mkt_normed = mkt / np.std(mkt)
m4m2_mkt = np.mean(mkt_normed**4) / (np.mean(mkt_normed**2)**2)
print(f"Market returns M4/M2: {m4m2_mkt:.2f} (Gaussian=3.0, expect >>3)")
print(f"  {'CONFIRMED' if m4m2_mkt > 5 else 'WEAK'} fat tails")

# ─── TEST 1: F24 - Sector -> Annual Returns ───
print("\n" + "="*70)
print("TEST 1: F24 - Sector -> Annual Returns (SC_class -> Tc analog)")
print("="*70)

# Compute annual returns per sector
annual_returns = defaultdict(lambda: defaultdict(float))
for d in ind:
    year = d["date"][:4]
    for s in sectors:
        if s in d:
            annual_returns[year][s] = annual_returns[year].get(s, 0) + d[s]

# Build arrays: each observation is (year, sector, return)
ret_vals = []
sec_labels = []
year_labels = []
for year in sorted(annual_returns.keys()):
    if int(year) < 1960:  # focus on modern era
        continue
    for s in sectors:
        if s in annual_returns[year]:
            ret_vals.append(annual_returns[year][s])
            sec_labels.append(s)
            year_labels.append(year)

ret_vals = np.array(ret_vals)
sec_labels = np.array(sec_labels)
year_labels = np.array(year_labels)

v1, r1 = bv2.F24_variance_decomposition(ret_vals, sec_labels)
print(f"Verdict: {v1}, eta2 = {r1.get('eta_squared', 0):.4f}")
for label, gs in sorted(r1.get("group_stats", {}).items()):
    print(f"  {label:6s}: n={gs['n']}, mean={gs['mean']:.2f}%/yr, std={gs['std']:.2f}")

v1b, r1b = bv2.F24b_metric_consistency(ret_vals, sec_labels)
print(f"F24b: {v1b}")

# ─── TEST 2: BREAK_SYMMETRY - Does sector->returns change across regimes? ───
print("\n" + "="*70)
print("TEST 2: BREAK_SYMMETRY - Sector->returns across market regimes")
print("="*70)

# Define regimes by market return (bull/bear/neutral)
regime_labels = []
for y in year_labels:
    year_mkt = annual_returns[y].get('Other', 0)  # proxy
    all_year_rets = [annual_returns[y].get(s, 0) for s in sectors]
    avg = np.mean(all_year_rets) if all_year_rets else 0
    if avg > 15:
        regime_labels.append("bull")
    elif avg < -5:
        regime_labels.append("bear")
    else:
        regime_labels.append("neutral")
regime_labels = np.array(regime_labels)

print(f"Regime distribution: {dict(zip(*np.unique(regime_labels, return_counts=True)))}")

# F25: does sector->returns transfer across regimes?
v2, r2 = bv2.F25_transportability(ret_vals, sec_labels, regime_labels)
print(f"F25 verdict: {v2}")
if "weighted_oos_r2" in r2:
    print(f"Weighted OOS R2: {r2['weighted_oos_r2']:.4f}")
if "per_partition" in r2:
    for p in r2["per_partition"]:
        print(f"  Held-out regime '{p['held_out']}': n={p['n_test']}, OOS R2={p['r2_oos']:.4f}")

# Within-regime F24
for regime in ["bull", "bear", "neutral"]:
    mask = regime_labels == regime
    if sum(mask) < 20:
        continue
    v, r = bv2.F24_variance_decomposition(ret_vals[mask], sec_labels[mask])
    print(f"  {regime}: n={sum(mask)}, sector->returns eta2={r.get('eta_squared', 0):.4f} ({v})")

# ─── TEST 3: F24 - Decade -> Returns (temporal non-stationarity) ───
print("\n" + "="*70)
print("TEST 3: F24 - Decade -> Returns (temporal non-stationarity)")
print("="*70)

decade_labels = np.array([y[:3] + "0s" for y in year_labels])
v3, r3 = bv2.F24_variance_decomposition(ret_vals, decade_labels)
print(f"Verdict: {v3}, eta2 = {r3.get('eta_squared', 0):.4f}")

# F25: do sector rankings transfer across decades?
v3b, r3b = bv2.F25_transportability(ret_vals, sec_labels, decade_labels)
print(f"F25 sector->returns across decades: {v3b}")
if "weighted_oos_r2" in r3b:
    print(f"Weighted OOS R2: {r3b['weighted_oos_r2']:.4f}")

# ─── TEST 4: Sector return distributions - M4/M2 per sector ───
print("\n" + "="*70)
print("TEST 4: Distributional shape by sector (daily returns)")
print("="*70)

for s in sectors:
    s_rets = np.array([d[s] for d in ind if s in d and int(d["date"][:4]) >= 1960], dtype=float)
    if len(s_rets) < 100:
        continue
    normed = s_rets / np.std(s_rets)
    m4m2 = np.mean(normed**4) / (np.mean(normed**2)**2)
    from scipy import stats as sp_stats
    skew = sp_stats.skew(s_rets)
    kurt = sp_stats.kurtosis(s_rets)
    print(f"  {s:6s}: n={len(s_rets)}, mean={np.mean(s_rets):.4f}, std={np.std(s_rets):.4f}, M4/M2={m4m2:.2f}, skew={skew:.3f}, kurt={kurt:.2f}")

# ─── TEST 5: Factor -> Sector returns (F24) ───
print("\n" + "="*70)
print("TEST 5: Market factor -> sector dispersion (F24)")
print("="*70)

# Build daily sector dispersion (cross-sectional std of sector returns)
dispersion = []
mkt_daily = []
for d in ind:
    if int(d["date"][:4]) < 1960:
        continue
    rets = [d.get(s, 0) for s in sectors]
    if all(r == 0 for r in rets):
        continue
    dispersion.append(np.std(rets))
    # Find matching market return
    date = d["date"]
    mkt_match = [f for f in ff5 if f["date"] == date]
    if mkt_match:
        mkt_daily.append(abs(mkt_match[0].get("Mkt-RF", 0)))
    else:
        mkt_daily.append(0)

dispersion = np.array(dispersion)
mkt_daily = np.array(mkt_daily)

# Group market days into quintiles
if len(mkt_daily) > 100:
    mkt_quintiles = np.array(["Q" + str(min(5, 1 + int(np.searchsorted(
        np.percentile(mkt_daily, [20, 40, 60, 80]), m)))) for m in mkt_daily])

    v5, r5 = bv2.F24_variance_decomposition(dispersion, mkt_quintiles)
    print(f"Market abs return quintile -> sector dispersion: {v5}, eta2={r5.get('eta_squared', 0):.4f}")
    for label, gs in sorted(r5.get("group_stats", {}).items()):
        print(f"  {label}: mean dispersion={gs['mean']:.4f}")

# ─── TEST 6: VIX-analog (rolling vol) -> sector rankings ───
print("\n" + "="*70)
print("TEST 6: Rolling volatility regime -> sector rankings")
print("="*70)

# Compute 21-day rolling vol of market
mkt_returns_all = np.array([d.get('Mkt-RF', 0) for d in ff5], dtype=float)
window = 21
rolling_vol = np.array([np.std(mkt_returns_all[max(0,i-window):i+1])
                        for i in range(len(mkt_returns_all))])

# Classify into vol regimes
vol_median = np.median(rolling_vol[rolling_vol > 0])
vol_labels_all = np.array(["high_vol" if v > vol_median else "low_vol" for v in rolling_vol])

# Match with industry data
ff5_dates = {d["date"]: i for i, d in enumerate(ff5)}
sector_ret_by_regime = defaultdict(lambda: defaultdict(list))

for d in ind:
    if d["date"] in ff5_dates:
        idx = ff5_dates[d["date"]]
        regime = vol_labels_all[idx]
        for s in sectors:
            if s in d:
                sector_ret_by_regime[regime][s].append(d[s])

print("Mean daily returns by vol regime:")
for regime in ["low_vol", "high_vol"]:
    means = {s: np.mean(sector_ret_by_regime[regime][s])
             for s in sectors if sector_ret_by_regime[regime][s]}
    ranked = sorted(means.items(), key=lambda x: -x[1])
    print(f"  {regime}: {', '.join(f'{s}:{m:.3f}' for s, m in ranked[:5])}")

# Rank correlation between regimes
from scipy import stats as sp_stats
low_means = [np.mean(sector_ret_by_regime["low_vol"][s]) for s in sectors]
high_means = [np.mean(sector_ret_by_regime["high_vol"][s]) for s in sectors]
rho, p = sp_stats.spearmanr(low_means, high_means)
print(f"Sector rank correlation (low_vol vs high_vol): rho={rho:.4f}, p={p:.4f}")
if abs(rho) < 0.3:
    print("  -> BREAK_SYMMETRY: sector rankings CHANGE across vol regimes")
elif rho > 0.7:
    print("  -> SYMMETRIZE: sector rankings STABLE across vol regimes")
else:
    print("  -> MODERATE: partial stability")

# ─── TEST 7: F25 - Factor returns across decades ───
print("\n" + "="*70)
print("TEST 7: F25 - Do factor premia transfer across decades?")
print("="*70)

factor_names = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']
for fname in factor_names:
    fvals = np.array([d.get(fname, 0) for d in ff5], dtype=float)
    dec_labels = np.array([d["date"][:3] + "0s" for d in ff5])
    unique_decs = sorted(set(dec_labels))

    # Mean return per decade
    dec_means = {}
    for dec in unique_decs:
        mask = dec_labels == dec
        dec_means[dec] = np.mean(fvals[mask])

    means_str = ", ".join(f"{d}:{dec_means[d]:.3f}" for d in unique_decs)
    print(f"  {fname:6s}: {means_str}")

    # Sign consistency
    signs = [1 if dec_means[d] > 0 else -1 for d in unique_decs]
    sign_consistency = sum(1 for s in signs if s == signs[0]) / len(signs)
    print(f"          Sign consistency: {sign_consistency:.0%} ({'STABLE' if sign_consistency >= 0.7 else 'UNSTABLE'})")

# ─── TEST 8: F27 - Tautology check ───
print("\n" + "="*70)
print("TEST 8: F27 - Consequence check")
print("="*70)
v8, r8 = bv2.F27_consequence_check("sector", "returns")
print(f"F27 verdict: {v8}")

# ─── CLASSIFICATION ───
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)

sector_eta2 = r1.get("eta_squared", 0)
decade_eta2 = r3.get("eta_squared", 0)

print(f"Sector -> annual returns eta2: {sector_eta2:.4f}")
print(f"Decade -> returns eta2: {decade_eta2:.4f}")
print(f"F24b: {v1b}")
print(f"F25 across regimes: {v2}")
print(f"F25 across decades: {v3b}")
print(f"Sector rank correlation (low vs high vol): rho={rho:.4f}")
print(f"Market M4/M2: {m4m2_mkt:.2f}")

print(f"\nCalibration:")
print(f"  Size effect (SMB): {'PASS' if np.mean(smb) > 0 else 'FAIL'}")
print(f"  Value premium (HML): {'PASS' if np.mean(hml) > 0 else 'FAIL'}")
print(f"  Momentum: {'PASS' if np.mean(mom_vals) > 0 else 'FAIL'}")
print(f"  Fat tails: {'PASS' if m4m2_mkt > 5 else 'FAIL'}")

if sector_eta2 >= 0.14:
    classification = "LAW"
elif sector_eta2 >= 0.01:
    classification = "TENDENCY"
else:
    classification = "NEGLIGIBLE"

print(f"\n-> Sector->returns: {classification}")

# Compare to SC_class->Tc
print(f"\nComparison to SC_class->Tc:")
print(f"  SC_class->Tc eta2 = 0.570 (CONDITIONAL LAW)")
print(f"  Sector->returns eta2 = {sector_eta2:.4f}")
if sector_eta2 < 0.06:
    print(f"  -> Finance sectors explain MUCH LESS variance than SC classes")
    print(f"  -> Markets are noisier; categorical structure is weaker")
else:
    print(f"  -> Comparable categorical structure")

results = {
    "test": "Finance Domain Expansion",
    "datasets": {
        "ff5_daily": len(ff5),
        "industry_10": len(ind),
        "momentum": len(mom),
    },
    "calibration": {
        "smb_positive": bool(np.mean(smb) > 0),
        "hml_positive": bool(np.mean(hml) > 0),
        "mom_positive": bool(np.mean(mom_vals) > 0),
        "fat_tails_m4m2": float(m4m2_mkt),
    },
    "sector_returns_eta2": sector_eta2,
    "decade_eta2": decade_eta2,
    "f24b_verdict": v1b,
    "f25_regime_verdict": v2,
    "f25_decade_verdict": v3b if 'v3b' in dir() else None,
    "vol_regime_rank_rho": float(rho),
    "classification": classification,
    "break_symmetry": abs(rho) < 0.3,
}

out_path = Path("F:/Prometheus/cartography/finance/data/finance_battery_results.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {out_path}")
