"""
P5 / Bochner-Riesz: numerical Bochner-Riesz multiplier on a 2D and 3D
test function, measuring L^p norm ratios across delta and p.

The Bochner-Riesz multiplier of order delta is

    (T^delta f)^(xi) = (1 - |xi|^2)_+^delta f^(xi)

The conjecture: T^delta is bounded on L^p(R^n) iff |1/p - 1/2| <= (delta + 1/2)/n.

In n=2: Carleson-Sjolin 1972 proves it.
In n>=3: open in general.

This script computes the ratio ||T^delta f||_{L^p} / ||f||_{L^p} on a
periodic grid (using FFT) for a Gaussian test function in 2D and 3D,
across a sweep of (p, delta) values.
"""
import numpy as np

def br_multiplier(N, n_dim, delta):
    """Build (1 - |k|^2)_+^delta multiplier on a centered cube of frequencies."""
    k1d = np.fft.fftfreq(N, d=1.0/N)  # frequencies, in cycles per unit
    coords = np.meshgrid(*[k1d] * n_dim, indexing='ij')
    # normalize so that the unit ball |xi| <= 1 covers a fraction of the spectrum
    # We treat the discrete frequencies as living in box [-N/2, N/2]; rescale by 1/(N/4)
    # so that |k| <= N/4 corresponds to |xi| <= 1.
    scale = N / 4
    norm2 = sum(c**2 for c in coords) / scale**2
    m = np.where(norm2 < 1, (1 - norm2) ** delta, 0.0)
    return m

def gaussian_test(N, n_dim, sigma=4.0):
    """Centered Gaussian of std sigma in space, on N^n_dim grid."""
    coords = np.meshgrid(*[np.arange(N) - N // 2] * n_dim, indexing='ij')
    r2 = sum(c**2 for c in coords)
    return np.exp(-r2 / (2 * sigma**2))

def lp_norm(f, p):
    return (np.sum(np.abs(f) ** p)) ** (1 / p)

def br_ratio(N, n_dim, delta, p, f=None):
    if f is None:
        f = gaussian_test(N, n_dim)
    f_hat = np.fft.fftn(f)
    m = br_multiplier(N, n_dim, delta)
    out = np.real(np.fft.ifftn(m * f_hat))
    return lp_norm(out, p) / lp_norm(f, p)

# Conjectured threshold
def threshold_p_for_delta(delta, n_dim):
    """|1/p - 1/2| <= (delta + 1/2)/n, so 1/p in [1/2 - (delta+1/2)/n, 1/2 + (delta+1/2)/n]"""
    half_band = (delta + 0.5) / n_dim
    inv_p_lo = max(0.0, 0.5 - half_band)
    inv_p_hi = min(1.0, 0.5 + half_band)
    p_lo = 1.0 / inv_p_hi if inv_p_hi > 0 else np.inf
    p_hi = 1.0 / inv_p_lo if inv_p_lo > 0 else np.inf
    return p_lo, p_hi

# 2D: known proven (Carleson-Sjolin)
print("=== n=2: Bochner-Riesz multiplier on Gaussian (Carleson-Sjolin proven) ===")
N2 = 128
deltas_2d = [0.0, 0.25, 0.5, 0.75, 1.0]
ps_2d = [1.5, 2.0, 3.0, 4.0, 6.0, 8.0]
print(f"{'delta':>6} {'(p_lo,p_hi)':>16} " + " ".join([f"p={p:>5.2f}" for p in ps_2d]))
for d in deltas_2d:
    plo, phi = threshold_p_for_delta(d, 2)
    ratios = []
    for p in ps_2d:
        ratios.append(br_ratio(N2, 2, d, p))
    print(f"{d:>6.2f} {f'({plo:.2f},{phi:.2f})':>16} " + " ".join([f"  {r:>5.4f}" for r in ratios]))

# 3D: open (full conjecture)
print()
print("=== n=3: Bochner-Riesz multiplier on Gaussian (full conjecture OPEN) ===")
N3 = 48
deltas_3d = [0.0, 0.25, 0.5, 1.0, 1.5]
ps_3d = [1.5, 2.0, 3.0, 4.0, 6.0]
print(f"{'delta':>6} {'(p_lo,p_hi)':>16} " + " ".join([f"p={p:>5.2f}" for p in ps_3d]))
for d in deltas_3d:
    plo, phi = threshold_p_for_delta(d, 3)
    ratios = []
    for p in ps_3d:
        ratios.append(br_ratio(N3, 3, d, p))
    print(f"{d:>6.2f} {f'({plo:.2f},{phi:.2f})':>16} " + " ".join([f"  {r:>5.4f}" for r in ratios]))

# Critical value delta_crit(p, n) = n*|1/p - 1/2| - 1/2, conjecturally minimal delta for L^p boundedness
print()
print("=== Critical-delta probe: ratio at conjectural endpoint ===")
print("For each p, compute T^delta_crit f, ratio ||T^delta f||_{L^p} / ||f||_{L^p}")
for n_dim, N in [(2, 128), (3, 48)]:
    print(f"  n = {n_dim}:")
    for p in [1.5, 4.0, 6.0]:
        d_crit = max(0.0, n_dim * abs(1/p - 0.5) - 0.5)
        if d_crit < 0:
            continue
        r = br_ratio(N, n_dim, d_crit + 0.05, p)  # just above critical
        r_below = br_ratio(N, n_dim, max(0.0, d_crit - 0.05), p)
        print(f"    p={p:.2f}  delta_crit={d_crit:.3f}  ratio(above)={r:.4f}  ratio(below)={r_below:.4f}")
