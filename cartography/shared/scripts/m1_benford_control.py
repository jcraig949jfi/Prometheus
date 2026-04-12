#!/usr/bin/env python3
"""
Benford/marginal control for cross-domain spectral cosines.
Layer 1 of the 7-layer falsification protocol.

Question: Are the high spectral cosines (0.96-0.99) between math domains
just because all positive-integer distributions with similar range look alike?

Control: Generate null distributions matched on range, size, and Benford compliance,
then compute spectral cosines. If nulls match the real cosines, the signal is dead.

M1 (Skullport), 2026-04-12
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from scipy import stats as sp_stats
from scipy.fft import fft

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DATA = Path("F:/Prometheus/cartography")

def spectral_signature(arr, n=512):
    s = np.sort(arr.astype(float))
    idx = np.linspace(0, len(s)-1, n).astype(int)
    resampled = s[idx]
    spectrum = np.abs(fft(resampled - np.mean(resampled)))[:n//2]
    return spectrum / (np.max(spectrum) + 1e-10)

def spectral_cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

# Load real data
print("Loading real distributions...")
with open(DATA / "number_fields/data/number_fields.json") as f:
    nf_data = json.load(f)
nf_cn = np.array([int(d["class_number"]) for d in nf_data if int(d["class_number"]) > 0], dtype=float)

with open(DATA / "knots/data/knots.json") as f:
    knot_data = json.load(f)
knot_det = np.array([k["determinant"] for k in knot_data["knots"] if (k.get("determinant") or 0) > 0], dtype=float)

import duckdb
con = duckdb.connect("F:/Prometheus/charon/data/charon.duckdb", read_only=True)
ec_cond = con.execute("SELECT conductor FROM elliptic_curves WHERE conductor > 0 LIMIT 30000").fetchnumpy()["conductor"].astype(float)
con.close()

ff5_path = Path("F:/Prometheus/cartography/finance/data/ff5_daily.json")
with open(ff5_path) as f:
    ff5 = json.load(f)
mkt_abs = np.abs(np.array([d.get("Mkt-RF", 0) for d in ff5], dtype=float))
mkt_abs = mkt_abs[mkt_abs > 0]

domains = {
    "NF_CN": nf_cn,
    "Knot_det": knot_det,
    "EC_cond": ec_cond,
    "Mkt_abs": mkt_abs,
}

# Real spectral signatures
real_specs = {name: spectral_signature(arr) for name, arr in domains.items()}

# Real pairwise cosines
print("\n" + "="*70)
print("REAL SPECTRAL COSINES")
print("="*70)
domain_names = list(domains.keys())
real_cosines = {}
for i in range(len(domain_names)):
    for j in range(i+1, len(domain_names)):
        a, b = domain_names[i], domain_names[j]
        cos = spectral_cosine(real_specs[a], real_specs[b])
        real_cosines[(a, b)] = cos
        print(f"  {a:10s} vs {b:10s}: {cos:.4f}")

# ─── NULL MODEL 1: Uniform integers in same range ───
print("\n" + "="*70)
print("NULL 1: Uniform integers (same range, same size)")
print("="*70)

rng = np.random.RandomState(42)
n_null = 200
null_cosines_uniform = {pair: [] for pair in real_cosines}

for trial in range(n_null):
    null_specs = {}
    for name, arr in domains.items():
        lo, hi = int(np.min(arr)), int(np.max(arr))
        null_arr = rng.randint(max(1, lo), max(2, hi), size=len(arr)).astype(float)
        null_specs[name] = spectral_signature(null_arr)

    for pair in real_cosines:
        a, b = pair
        null_cosines_uniform[pair].append(spectral_cosine(null_specs[a], null_specs[b]))

print(f"{'Pair':>25s}  {'Real':>6s}  {'Null mean':>9s}  {'Null std':>8s}  {'z-score':>7s}  Verdict")
for pair in real_cosines:
    real = real_cosines[pair]
    null_mean = np.mean(null_cosines_uniform[pair])
    null_std = np.std(null_cosines_uniform[pair])
    z = (real - null_mean) / (null_std + 1e-10)
    verdict = "SURVIVES" if z > 3 else "KILLED" if z < 1 else "MARGINAL"
    a, b = pair
    print(f"  {a:>10s} vs {b:<10s}  {real:.4f}  {null_mean:.4f}     {null_std:.4f}    {z:+.2f}    {verdict}")

# ─── NULL MODEL 2: Log-normal matched on mean and std ───
print("\n" + "="*70)
print("NULL 2: Log-normal (matched mean, std of log values)")
print("="*70)

null_cosines_lognorm = {pair: [] for pair in real_cosines}

for trial in range(n_null):
    null_specs = {}
    for name, arr in domains.items():
        pos = arr[arr > 0]
        log_mean = np.mean(np.log(pos))
        log_std = np.std(np.log(pos))
        null_arr = np.exp(rng.normal(log_mean, log_std, size=len(pos)))
        null_specs[name] = spectral_signature(null_arr)

    for pair in real_cosines:
        a, b = pair
        null_cosines_lognorm[pair].append(spectral_cosine(null_specs[a], null_specs[b]))

print(f"{'Pair':>25s}  {'Real':>6s}  {'Null mean':>9s}  {'Null std':>8s}  {'z-score':>7s}  Verdict")
for pair in real_cosines:
    real = real_cosines[pair]
    null_mean = np.mean(null_cosines_lognorm[pair])
    null_std = np.std(null_cosines_lognorm[pair])
    z = (real - null_mean) / (null_std + 1e-10)
    verdict = "SURVIVES" if z > 3 else "KILLED" if z < 1 else "MARGINAL"
    a, b = pair
    print(f"  {a:>10s} vs {b:<10s}  {real:.4f}  {null_mean:.4f}     {null_std:.4f}    {z:+.2f}    {verdict}")

# ─── NULL MODEL 3: Benford-compliant (leading digit follows Benford's law) ───
print("\n" + "="*70)
print("NULL 3: Benford-compliant integers (same size, Benford leading digits)")
print("="*70)

def generate_benford(n, max_val, rng):
    """Generate integers whose leading digits follow Benford's law."""
    # Benford: P(d) = log10(1 + 1/d)
    log_vals = rng.uniform(0, np.log10(max_val + 1), size=n)
    return np.floor(10**log_vals).astype(float)

null_cosines_benford = {pair: [] for pair in real_cosines}

for trial in range(n_null):
    null_specs = {}
    for name, arr in domains.items():
        null_arr = generate_benford(len(arr), int(np.max(arr)), rng)
        null_specs[name] = spectral_signature(null_arr)

    for pair in real_cosines:
        a, b = pair
        null_cosines_benford[pair].append(spectral_cosine(null_specs[a], null_specs[b]))

print(f"{'Pair':>25s}  {'Real':>6s}  {'Null mean':>9s}  {'Null std':>8s}  {'z-score':>7s}  Verdict")
for pair in real_cosines:
    real = real_cosines[pair]
    null_mean = np.mean(null_cosines_benford[pair])
    null_std = np.std(null_cosines_benford[pair])
    z = (real - null_mean) / (null_std + 1e-10)
    verdict = "SURVIVES" if z > 3 else "KILLED" if z < 1 else "MARGINAL"
    a, b = pair
    print(f"  {a:>10s} vs {b:<10s}  {real:.4f}  {null_mean:.4f}     {null_std:.4f}    {z:+.2f}    {verdict}")

# ─── SUMMARY ───
print("\n" + "="*70)
print("SUMMARY: Which cross-domain spectral similarities survive controls?")
print("="*70)

for pair in real_cosines:
    a, b = pair
    real = real_cosines[pair]
    z_uniform = (real - np.mean(null_cosines_uniform[pair])) / (np.std(null_cosines_uniform[pair]) + 1e-10)
    z_lognorm = (real - np.mean(null_cosines_lognorm[pair])) / (np.std(null_cosines_lognorm[pair]) + 1e-10)
    z_benford = (real - np.mean(null_cosines_benford[pair])) / (np.std(null_cosines_benford[pair]) + 1e-10)
    min_z = min(z_uniform, z_lognorm, z_benford)

    if min_z > 3:
        verdict = "SURVIVES ALL NULLS"
    elif min_z > 1:
        verdict = "MARGINAL (weakest null kills or nearly kills)"
    else:
        verdict = "KILLED by distributional control"

    print(f"  {a} vs {b}: real={real:.4f}, z_uniform={z_uniform:+.1f}, z_lognorm={z_lognorm:+.1f}, z_benford={z_benford:+.1f} --> {verdict}")

results = {
    "test": "benford_control",
    "real_cosines": {f"{a}_vs_{b}": v for (a, b), v in real_cosines.items()},
    "null_z_scores": {},
}
for pair in real_cosines:
    a, b = pair
    key = f"{a}_vs_{b}"
    results["null_z_scores"][key] = {
        "z_uniform": float((real_cosines[pair] - np.mean(null_cosines_uniform[pair])) / (np.std(null_cosines_uniform[pair]) + 1e-10)),
        "z_lognorm": float((real_cosines[pair] - np.mean(null_cosines_lognorm[pair])) / (np.std(null_cosines_lognorm[pair]) + 1e-10)),
        "z_benford": float((real_cosines[pair] - np.mean(null_cosines_benford[pair])) / (np.std(null_cosines_benford[pair]) + 1e-10)),
    }

with open(Path("F:/Prometheus/cartography/shared/scripts/v2/benford_control_results.json"), "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to v2/benford_control_results.json")
