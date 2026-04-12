#!/usr/bin/env python3
"""
Geometric Exploration — go deeper than eta2.
Apply geometric probes to the strongest findings and look for structure
that flat statistics missed.

Three axes:
1. Congruence enrichment curve geometry (functional form, convergence)
2. Knot polynomial profile manifold (curvature, spectral structure)
3. Cross-domain geometric signatures (MI, Wasserstein, spectral matching)

M1 (Skullport), 2026-04-12
"""
import sys, os, json, re
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path("F:/Prometheus/cartography/shared/scripts").resolve())
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from geometric_probes import *
from battery_v2 import BatteryV2
from scipy import stats as sp_stats
from scipy.fft import fft

bv2 = BatteryV2()
DATA = Path("F:/Prometheus/cartography")

print("="*80)
print("GEOMETRIC EXPLORATION")
print("="*80)

# ═══════════════════════════════════════════════════════════════════════
# AXIS 1: Congruence enrichment curve geometry
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("AXIS 1: CONGRUENCE ENRICHMENT CURVE GEOMETRY")
print("="*80)

# Load from prior results
cong_path = Path(_scripts) / "v2/deep_congruence_universality_results.json"
if cong_path.exists():
    with open(cong_path) as f:
        cong_results = json.load(f)
    families = cong_results.get("families", {})
else:
    families = {}

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

for fname, enrich_dict in families.items():
    if not enrich_dict:
        continue
    ps = sorted([int(k) for k in enrich_dict.keys()])
    es = [enrich_dict[str(p)] for p in ps]
    if len(ps) < 5:
        continue

    print(f"\n  --- {fname} ---")

    # Fit candidate functional forms
    log_p = np.log(np.array(ps, dtype=float))
    log_e = np.log(np.array(es, dtype=float))
    arr_p = np.array(ps, dtype=float)
    arr_e = np.array(es, dtype=float)

    # Model 1: E(p) = a * log(p) + b
    sl1, ic1, r1, _, _ = sp_stats.linregress(log_p, arr_e)
    r2_log = r1**2

    # Model 2: E(p) = a * p^alpha (power law: log(E) = alpha*log(p) + c)
    sl2, ic2, r2, _, _ = sp_stats.linregress(log_p, log_e)
    r2_power = r2**2
    alpha = sl2

    # Model 3: E(p) = a * p + b (linear)
    sl3, ic3, r3, _, _ = sp_stats.linregress(arr_p, arr_e)
    r2_linear = r3**2

    # Model 4: E(p) = a * sqrt(p) + b
    sl4, ic4, r4, _, _ = sp_stats.linregress(np.sqrt(arr_p), arr_e)
    r2_sqrt = r4**2

    print(f"  Functional form fits:")
    print(f"    E ~ log(p):    R2={r2_log:.4f}  (E = {sl1:.3f}*log(p) + {ic1:.3f})")
    print(f"    E ~ p^alpha:   R2={r2_power:.4f}  (alpha = {alpha:.3f})")
    print(f"    E ~ p (linear): R2={r2_linear:.4f}")
    print(f"    E ~ sqrt(p):   R2={r2_sqrt:.4f}")

    best = max([("log(p)", r2_log), ("p^alpha", r2_power),
                ("linear", r2_linear), ("sqrt(p)", r2_sqrt)], key=lambda x: x[1])
    print(f"    Best fit: {best[0]} (R2={best[1]:.4f})")

    if best[0] == "p^alpha":
        print(f"    Power law exponent alpha = {alpha:.4f}")
        if 0.45 < alpha < 0.55:
            print(f"    --> CLOSE TO sqrt(p)! This could be Ramanujan-bound related")
        elif 0.95 < alpha < 1.05:
            print(f"    --> CLOSE TO linear! Enrichment ~ p")

    # Geometric probes on the enrichment curve
    curv = probe_curvature(arr_e)
    if curv:
        print(f"    Curvature: mean={curv['mean_curvature']:.4f}, convex_frac={curv['convex_fraction']:.3f}")

    growth = probe_growth_shape(arr_e)
    if growth:
        print(f"    Growth shape: poly_degree={growth['poly_degree']}, r2_poly={growth['r2_polynomial']:.4f}")

# ═══════════════════════════════════════════════════════════════════════
# AXIS 2: Knot polynomial profile manifold
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("AXIS 2: KNOT POLYNOMIAL PROFILE MANIFOLD")
print("="*80)

with open(DATA / "knots/data/knots.json") as f:
    knot_data = json.load(f)
knots = knot_data["knots"]

angles = np.linspace(0, 2*np.pi, 13, endpoint=False)
unit_pts = np.exp(1j * angles)

def eval_poly(coeffs, min_power, t):
    return sum(c * t**(min_power + k) for k, c in enumerate(coeffs))

# Build profile matrix
profiles = []
crossings = []
for k in knots:
    jones = k.get("jones")
    if not jones or not isinstance(jones, dict):
        continue
    coeffs = jones.get("coefficients", [])
    if not coeffs:
        continue
    profile = np.array([abs(eval_poly(coeffs, jones["min_power"], t)) for t in unit_pts])
    if np.any(~np.isfinite(profile)):
        continue
    profiles.append(profile)
    cn = k.get("crossing_number") or 0
    if cn == 0:
        m = re.match(r'(\d+)', k.get("name", ""))
        cn = int(m.group(1)) if m else 0
    crossings.append(cn)

profiles = np.array(profiles)
crossings = np.array(crossings)
print(f"Profiles: {profiles.shape}")

# 2a. Spectral structure of profiles (FFT of each profile)
print("\n  --- Profile spectral structure ---")
fft_profiles = np.abs(fft(profiles, axis=1))
# Which harmonics dominate?
mean_fft = np.mean(fft_profiles, axis=0)
print(f"  Mean FFT magnitudes: {np.round(mean_fft, 2)}")
dominant_harmonic = np.argmax(mean_fft[1:]) + 1
print(f"  Dominant harmonic (excluding DC): k={dominant_harmonic}")

# 2b. Profile PCA — intrinsic dimensionality
print("\n  --- Profile PCA ---")
centered = profiles - np.mean(profiles, axis=0)
try:
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    explained = (S**2) / np.sum(S**2)
    cum_explained = np.cumsum(explained)
    dim_90 = np.searchsorted(cum_explained, 0.90) + 1
    dim_95 = np.searchsorted(cum_explained, 0.95) + 1
    dim_99 = np.searchsorted(cum_explained, 0.99) + 1
    print(f"  Singular values: {np.round(S[:6], 2)}")
    print(f"  Variance explained: {np.round(explained[:6]*100, 1)}%")
    print(f"  Dimensions for 90%: {dim_90}, 95%: {dim_95}, 99%: {dim_99}")
    print(f"  Participation ratio: {(np.sum(S**2)**2) / np.sum(S**4):.2f}")
except Exception as e:
    print(f"  SVD failed: {e}")

# 2c. Profile curvature by crossing number
print("\n  --- Profile curvature by crossing ---")
for cn in sorted(set(crossings)):
    mask = crossings == cn
    if sum(mask) < 20:
        continue
    cn_profiles = profiles[mask]
    # Mean curvature of the profile (second derivative around the unit circle)
    mean_prof = np.mean(cn_profiles, axis=0)
    d1 = np.diff(mean_prof)
    d2 = np.diff(d1)
    mean_curv = np.mean(np.abs(d2))
    print(f"  Crossing {cn}: n={sum(mask)}, mean |curvature|={mean_curv:.4f}, profile norm={np.linalg.norm(mean_prof):.2f}")

# 2d. Mutual information between profile angles
print("\n  --- MI between angle evaluations ---")
n_bins = 30
for i in range(0, 13, 4):
    for j in range(i+1, 13, 4):
        a = profiles[:, i]
        b = profiles[:, j]
        # Compute MI via histograms
        hist_ab, _, _ = np.histogram2d(a, b, bins=n_bins)
        hist_a = np.sum(hist_ab, axis=1)
        hist_b = np.sum(hist_ab, axis=0)
        # Normalize
        p_ab = hist_ab / np.sum(hist_ab)
        p_a = hist_a / np.sum(hist_a)
        p_b = hist_b / np.sum(hist_b)
        # MI
        mi = 0
        for ii in range(n_bins):
            for jj in range(n_bins):
                if p_ab[ii, jj] > 0 and p_a[ii] > 0 and p_b[jj] > 0:
                    mi += p_ab[ii, jj] * np.log(p_ab[ii, jj] / (p_a[ii] * p_b[jj]))
        print(f"  MI(angle[{i}], angle[{j}]) = {mi:.4f} bits")

# ═══════════════════════════════════════════════════════════════════════
# AXIS 3: Cross-domain geometric signatures
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("AXIS 3: CROSS-DOMAIN GEOMETRIC SIGNATURES")
print("="*80)

# Load number field class numbers and knot determinants
with open(DATA / "number_fields/data/number_fields.json") as f:
    nf_data = json.load(f)

nf_cn = np.array([int(d["class_number"]) for d in nf_data if int(d["class_number"]) > 0], dtype=float)
knot_det = np.array([k["determinant"] for k in knots if (k.get("determinant") or 0) > 0], dtype=float)

# 3a. Geometric probes on each domain independently
print("\n  --- Shape comparison: NF class numbers vs knot determinants ---")
curv_nf = probe_curvature(nf_cn[:5000])
curv_kn = probe_curvature(knot_det)
if curv_nf and curv_kn:
    print(f"  NF class numbers: mean_curv={curv_nf['mean_curvature']:.6f}, convex={curv_nf['convex_fraction']:.3f}, sign_changes={curv_nf['sign_changes']}")
    print(f"  Knot determinants: mean_curv={curv_kn['mean_curvature']:.6f}, convex={curv_kn['convex_fraction']:.3f}, sign_changes={curv_kn['sign_changes']}")

growth_nf = probe_growth_shape(nf_cn[:5000])
growth_kn = probe_growth_shape(knot_det)
if growth_nf and growth_kn:
    print(f"  NF growth: poly_degree={growth_nf['poly_degree']}, r2={growth_nf['r2_polynomial']:.4f}")
    print(f"  Knot growth: poly_degree={growth_kn['poly_degree']}, r2={growth_kn['r2_polynomial']:.4f}")

# 3b. FFT comparison
print("\n  --- Spectral signatures ---")
def spectral_signature(arr, n=512):
    """FFT of sorted values — the spectral fingerprint of a distribution."""
    s = np.sort(arr)
    # Resample to fixed size
    idx = np.linspace(0, len(s)-1, n).astype(int)
    resampled = s[idx]
    spectrum = np.abs(fft(resampled - np.mean(resampled)))[:n//2]
    return spectrum / (np.max(spectrum) + 1e-10)

spec_nf = spectral_signature(nf_cn)
spec_kn = spectral_signature(knot_det)

# Cosine similarity of spectral signatures
cos_spec = np.dot(spec_nf, spec_kn) / (np.linalg.norm(spec_nf) * np.linalg.norm(spec_kn) + 1e-10)
print(f"  Spectral cosine (NF CN vs knot det): {cos_spec:.4f}")

# Also compare to EC conductors
import duckdb
con = duckdb.connect("F:/Prometheus/charon/data/charon.duckdb", read_only=True)
ec_cond = con.execute("SELECT conductor FROM elliptic_curves WHERE conductor > 0 LIMIT 30000").fetchnumpy()["conductor"].astype(float)
con.close()

spec_ec = spectral_signature(ec_cond)
cos_nf_ec = np.dot(spec_nf, spec_ec) / (np.linalg.norm(spec_nf) * np.linalg.norm(spec_ec) + 1e-10)
cos_kn_ec = np.dot(spec_kn, spec_ec) / (np.linalg.norm(spec_kn) * np.linalg.norm(spec_ec) + 1e-10)
print(f"  Spectral cosine (NF CN vs EC cond): {cos_nf_ec:.4f}")
print(f"  Spectral cosine (knot det vs EC cond): {cos_kn_ec:.4f}")

# 3c. Wasserstein distance (optimal transport)
print("\n  --- Wasserstein distances (normalized) ---")
# Normalize to [0,1]
def normalize_cdf(arr):
    s = np.sort(arr)
    return (s - s[0]) / (s[-1] - s[0] + 1e-10)

w_nf_kn = sp_stats.wasserstein_distance(normalize_cdf(nf_cn[:3000]), normalize_cdf(knot_det[:3000]))
w_nf_ec = sp_stats.wasserstein_distance(normalize_cdf(nf_cn[:3000]), normalize_cdf(ec_cond[:3000]))
w_kn_ec = sp_stats.wasserstein_distance(normalize_cdf(knot_det[:3000]), normalize_cdf(ec_cond[:3000]))
print(f"  W(NF CN, knot det): {w_nf_kn:.4f}")
print(f"  W(NF CN, EC cond): {w_nf_ec:.4f}")
print(f"  W(knot det, EC cond): {w_kn_ec:.4f}")

# 3d. Finance vs math spectral comparison
print("\n  --- Finance vs math spectral comparison ---")
ff5_path = Path("F:/Prometheus/cartography/finance/data/ff5_daily.json")
if ff5_path.exists():
    with open(ff5_path) as f:
        ff5 = json.load(f)
    mkt_rets = np.array([d.get("Mkt-RF", 0) for d in ff5], dtype=float)
    spec_mkt = spectral_signature(np.abs(mkt_rets[mkt_rets != 0]))

    cos_mkt_nf = np.dot(spec_mkt, spec_nf) / (np.linalg.norm(spec_mkt) * np.linalg.norm(spec_nf) + 1e-10)
    cos_mkt_kn = np.dot(spec_mkt, spec_kn) / (np.linalg.norm(spec_mkt) * np.linalg.norm(spec_kn) + 1e-10)
    cos_mkt_ec = np.dot(spec_mkt, spec_ec) / (np.linalg.norm(spec_mkt) * np.linalg.norm(spec_ec) + 1e-10)
    print(f"  Spectral cosine (|market returns| vs NF CN): {cos_mkt_nf:.4f}")
    print(f"  Spectral cosine (|market returns| vs knot det): {cos_mkt_kn:.4f}")
    print(f"  Spectral cosine (|market returns| vs EC cond): {cos_mkt_ec:.4f}")

# ═══════════════════════════════════════════════════════════════════════
# SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("SYNTHESIS")
print("="*80)

print("""
Questions answered:
1. CONGRUENCE CURVE: What functional form does enrichment follow?
2. KNOT MANIFOLD: What's the intrinsic dimensionality of profile space?
3. CROSS-DOMAIN: Do spectral signatures match across domains?

Questions opened:
- If enrichment ~ p^alpha, what determines alpha?
- If profile space is low-dimensional, what are the axes?
- If spectral signatures differ, what makes each domain's distribution unique?
""")

results = {
    "test": "geometric_exploration",
    "profile_dimensionality_90": int(dim_90) if 'dim_90' in dir() else None,
    "profile_dimensionality_95": int(dim_95) if 'dim_95' in dir() else None,
    "spectral_cosine_nf_kn": float(cos_spec),
    "spectral_cosine_nf_ec": float(cos_nf_ec),
    "spectral_cosine_kn_ec": float(cos_kn_ec),
    "wasserstein_nf_kn": float(w_nf_kn),
    "wasserstein_nf_ec": float(w_nf_ec),
    "wasserstein_kn_ec": float(w_kn_ec),
}
with open(Path(_scripts) / "v2/geometric_exploration_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to v2/geometric_exploration_results.json")
