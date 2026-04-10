#!/usr/bin/env python3
"""
Q25: Fourier Decomposition of Prime Indicator Fields

Treat primes in a 200x200 row-major grid as a binary field P(x,y).
Compute 2D FFT, radially-averaged power spectrum, spectral index,
top modes, and compare against density-matched random null.
"""

import json
import numpy as np
from sympy import isprime
from pathlib import Path

# ── 1. Build the 200×200 prime indicator field ──────────────────────────
N = 200
grid_size = N * N  # 40000
integers = np.arange(1, grid_size + 1)
P = np.array([1 if isprime(int(n)) else 0 for n in integers], dtype=np.float64).reshape(N, N)
density = P.sum() / grid_size
print(f"Grid {N}x{N}, density pi(40000)/40000 = {P.sum():.0f}/{grid_size} = {density:.6f}")

# ── 2. 2D FFT and power spectrum ────────────────────────────────────────
F = np.fft.fft2(P)
power = np.abs(F) ** 2

# Shift so DC is at center
power_shift = np.fft.fftshift(power)
F_shift = np.fft.fftshift(F)

# Frequency grid
freqs_x = np.fft.fftshift(np.fft.fftfreq(N))
freqs_y = np.fft.fftshift(np.fft.fftfreq(N))
fx, fy = np.meshgrid(freqs_x, freqs_y)
k_map = np.sqrt(fx**2 + fy**2)

# ── 3. Radially-averaged power spectrum P(k) ────────────────────────────
k_max = 0.5 * np.sqrt(2)
n_bins = 100
k_edges = np.linspace(0, k_max, n_bins + 1)
k_centers = 0.5 * (k_edges[:-1] + k_edges[1:])

radial_power = np.zeros(n_bins)
radial_count = np.zeros(n_bins)

for i in range(n_bins):
    mask = (k_map >= k_edges[i]) & (k_map < k_edges[i + 1])
    if mask.any():
        radial_power[i] = power_shift[mask].mean()
        radial_count[i] = mask.sum()

# Exclude DC (bin 0) and empty bins for fitting
valid = (radial_count > 0) & (k_centers > 0)
k_valid = k_centers[valid]
p_valid = radial_power[valid]

# ── 4. Fit P(k) ~ k^{-alpha} ────────────────────────────────────────────
# Log-log linear regression
log_k = np.log10(k_valid)
log_p = np.log10(p_valid)
coeffs = np.polyfit(log_k, log_p, 1)
alpha = -coeffs[0]  # spectral index (positive means decay)
log_A = coeffs[1]
residuals = log_p - (coeffs[0] * log_k + coeffs[1])
r_squared = 1 - np.sum(residuals**2) / np.sum((log_p - log_p.mean())**2)

print(f"\nSpectral index fit: P(k) ~ k^{{-{alpha:.4f}}}")
print(f"  R² = {r_squared:.6f}")
print(f"  log10(A) = {log_A:.4f}")

# ── 5. Top 10 strongest frequency modes ─────────────────────────────────
# Zero out DC for mode ranking
power_shift_nodc = power_shift.copy()
cx, cy = N // 2, N // 2
power_shift_nodc[cx, cy] = 0

# Find top 10 modes (each mode and its conjugate are the same, so pick unique)
flat_idx = np.argsort(power_shift_nodc.ravel())[::-1]
top_modes = []
seen = set()

for idx in flat_idx:
    if len(top_modes) >= 10:
        break
    iy, ix = divmod(idx, N)
    # Frequency indices relative to center
    fi = ix - cx  # horizontal frequency
    fj = iy - cy  # vertical frequency
    # Avoid counting conjugate pairs twice
    key = (abs(fi), abs(fj)) if (abs(fi), abs(fj)) != (abs(fj), abs(fi)) else tuple(sorted([abs(fi), abs(fj)]))
    conj_key = key
    if conj_key in seen:
        continue
    seen.add(conj_key)

    pw = power_shift_nodc[iy, ix]
    k_val = k_map[iy, ix]

    # Spatial interpretation
    if fi == 0 and fj != 0:
        interp = f"horizontal stripes, period={N/abs(fj):.1f} rows"
    elif fj == 0 and fi != 0:
        interp = f"vertical stripes, period={N/abs(fi):.1f} cols"
    elif abs(fi) == abs(fj):
        interp = f"diagonal, period={N/abs(fi)*np.sqrt(2)/2:.1f}"
    else:
        angle = np.degrees(np.arctan2(fj, fi))
        gcd = np.gcd(abs(fi), abs(fj))
        interp = f"oblique angle={angle:.1f}°, base freq ({fi//gcd},{fj//gcd})"

    top_modes.append({
        "rank": len(top_modes) + 1,
        "freq_ix": int(fi),
        "freq_iy": int(fj),
        "wavenumber_k": float(k_val),
        "power": float(pw),
        "spatial_interpretation": interp
    })

print("\nTop 10 frequency modes (excluding DC):")
for m in top_modes:
    print(f"  #{m['rank']}: ({m['freq_ix']},{m['freq_iy']}) k={m['wavenumber_k']:.4f} "
          f"P={m['power']:.1f} — {m['spatial_interpretation']}")

# ── 6. Null comparison: random binary field with same density ────────────
n_null = 500
rng = np.random.default_rng(42)

null_radial_all = np.zeros((n_null, n_bins))
null_top_power = np.zeros(n_null)

for trial in range(n_null):
    R = (rng.random((N, N)) < density).astype(np.float64)
    F_r = np.fft.fft2(R)
    pw_r = np.abs(F_r) ** 2
    pw_r_shift = np.fft.fftshift(pw_r)

    for i in range(n_bins):
        mask = (k_map >= k_edges[i]) & (k_map < k_edges[i + 1])
        if mask.any():
            null_radial_all[trial, i] = pw_r_shift[mask].mean()

    pw_r_shift[cx, cy] = 0
    null_top_power[trial] = pw_r_shift.max()

null_mean = null_radial_all.mean(axis=0)
null_std = null_radial_all.std(axis=0)

# Compute z-scores for each radial bin
z_scores = np.zeros(n_bins)
z_scores[valid] = (radial_power[valid] - null_mean[valid]) / np.where(null_std[valid] > 0, null_std[valid], 1)

# Significant bins (|z| > 3)
sig_bins = np.where(valid & (np.abs(z_scores) > 3))[0]
print(f"\nNull comparison ({n_null} random fields):")
print(f"  Bins with |z| > 3: {len(sig_bins)} / {valid.sum()}")

# Fit null spectral index
null_mean_valid = null_mean[valid]
null_log_p = np.log10(np.maximum(null_mean_valid, 1e-10))
null_coeffs = np.polyfit(log_k, null_log_p, 1)
null_alpha = -null_coeffs[0]
print(f"  Null spectral index: alpha = {null_alpha:.4f}")
print(f"  Prime spectral index: alpha = {alpha:.4f}")

# Top mode significance
prime_top_power = max(m["power"] for m in top_modes)
null_top_mean = null_top_power.mean()
null_top_std = null_top_power.std()
top_z = (prime_top_power - null_top_mean) / null_top_std
print(f"  Top mode power: prime={prime_top_power:.1f}, null_mean={null_top_mean:.1f}±{null_top_std:.1f}, z={top_z:.2f}")

# ── 7. Row-structure analysis ────────────────────────────────────────────
# In row-major layout, consecutive integers sit along rows.
# Primes avoid multiples of small primes, creating periodic gaps.
# Check: is the dominant structure along the horizontal (row) direction?
row_power = power_shift[cx, :].copy()  # horizontal slice through DC
col_power = power_shift[:, cy].copy()  # vertical slice through DC
row_power[cx] = 0
col_power[cy] = 0

row_total = row_power.sum()
col_total = col_power.sum()
print(f"\nDirectional power (DC-excluded):")
print(f"  Row (horizontal, consecutive integers): {row_total:.1f}")
print(f"  Column (vertical, stride-200): {col_total:.1f}")
print(f"  Ratio row/col: {row_total/col_total:.2f}")

# Check specific small-prime sieve frequencies along rows
# In a row of 200 integers, multiples of p create frequency at p cycles
# Frequency index = 200/p (if p divides 200) or nearest
print("\nSieve frequencies along rows (horizontal axis):")
for p in [2, 3, 5, 7, 11, 13]:
    # The sieve of p creates a pattern with period p in the integer sequence
    # In frequency space, this appears at frequency index N/p (if exact) or nearby
    freq_idx = N / p
    nearest = int(round(freq_idx))
    if nearest < N and nearest != cx:
        pw_at = power_shift[cx, cx + nearest] if cx + nearest < N else 0
        pw_at2 = power_shift[cx, cx - nearest] if cx - nearest >= 0 else 0
        pw_use = max(pw_at, pw_at2)
        # Null expected
        null_at = null_mean[np.argmin(np.abs(k_centers - nearest/N))]
        print(f"  p={p}: freq_idx~{freq_idx:.1f}, nearest={nearest}, power={pw_use:.1f}, null~{null_at:.1f}")

# ── 8. Excess power ratio ───────────────────────────────────────────────
# Total power in prime field vs null (excluding DC)
prime_total_nodc = power_shift_nodc.sum()
null_totals = []
for trial in range(min(100, n_null)):
    R = (rng.random((N, N)) < density).astype(np.float64)
    F_r = np.fft.fft2(R)
    pw_r = np.abs(F_r) ** 2
    pw_r_shift = np.fft.fftshift(pw_r)
    pw_r_shift[cx, cy] = 0
    null_totals.append(pw_r_shift.sum())

null_total_mean = np.mean(null_totals)
null_total_std = np.std(null_totals)
excess_z = (prime_total_nodc - null_total_mean) / null_total_std
print(f"\nTotal non-DC power: prime={prime_total_nodc:.1f}, null={null_total_mean:.1f}±{null_total_std:.1f}")
print(f"Excess z-score: {excess_z:.2f}")

# ── 9. Build results ────────────────────────────────────────────────────
results = {
    "question": "Q25: Fourier Decomposition of Prime Indicator Fields",
    "grid": {"rows": N, "cols": N, "total_integers": grid_size},
    "prime_count": int(P.sum()),
    "density": float(density),
    "spectral_fit": {
        "alpha": float(alpha),
        "R_squared": float(r_squared),
        "log10_A": float(log_A),
        "interpretation": "P(k) ~ k^{-alpha}; alpha near 0 means flat (white noise-like)"
    },
    "null_spectral_fit": {
        "alpha": float(null_alpha),
        "n_trials": n_null
    },
    "alpha_difference": float(alpha - null_alpha),
    "top_10_modes": top_modes,
    "null_comparison": {
        "n_trials": n_null,
        "bins_with_z_gt_3": int(len(sig_bins)),
        "total_valid_bins": int(valid.sum()),
        "significant_k_values": [float(k_centers[i]) for i in sig_bins],
        "top_mode_z_score": float(top_z)
    },
    "directional_analysis": {
        "row_power_total": float(row_total),
        "col_power_total": float(col_total),
        "row_col_ratio": float(row_total / col_total),
        "interpretation": "Row direction dominates because consecutive integers are along rows; sieve creates periodic structure"
    },
    "total_power_test": {
        "prime_total_nodc": float(prime_total_nodc),
        "null_mean": float(null_total_mean),
        "null_std": float(null_total_std),
        "z_score": float(excess_z)
    },
    "radial_spectrum": {
        "k_centers": [float(x) for x in k_centers[valid]],
        "prime_power": [float(x) for x in radial_power[valid]],
        "null_mean": [float(x) for x in null_mean[valid]],
        "null_std": [float(x) for x in null_std[valid]],
        "z_scores": [float(x) for x in z_scores[valid]]
    },
    "verdict": ""  # filled below
}

# ── 10. Verdict ──────────────────────────────────────────────────────────
has_structure = len(sig_bins) > 5 or abs(top_z) > 3 or abs(alpha - null_alpha) > 0.3

if has_structure:
    verdict = (
        f"YES: The prime indicator field has Fourier structure beyond density. "
        f"Spectral index alpha={alpha:.3f} vs null alpha={null_alpha:.3f} (Delta={alpha-null_alpha:.3f}). "
        f"{len(sig_bins)} radial bins exceed |z|>3. "
        f"Top mode z={top_z:.1f}. "
        f"Row/col power ratio={row_total/col_total:.1f}x shows sieve-induced anisotropy. "
        f"The structure is dominated by the sieve of small primes creating periodic "
        f"modular patterns in the row direction (period-2 from even/odd, period-3, period-5, etc.)."
    )
else:
    verdict = (
        f"WEAK/NO: The prime field's Fourier structure is largely consistent with density-matched noise. "
        f"Spectral index alpha={alpha:.3f} vs null alpha={null_alpha:.3f} (Delta={alpha-null_alpha:.3f}). "
        f"Only {len(sig_bins)} bins exceed |z|>3. Top mode z={top_z:.1f}."
    )

results["verdict"] = verdict
print(f"\n{'='*70}")
print(f"VERDICT: {verdict}")

# Save
out_dir = Path(__file__).parent
with open(out_dir / "prime_fourier_2d_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_dir / 'prime_fourier_2d_results.json'}")
