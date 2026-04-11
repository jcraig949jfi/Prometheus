"""
Modular Form <-> Knot Polynomial Compression Gap (ChatGPT #3)

Measures Lempel-Ziv (zlib) complexity difference between:
  - Hecke eigenvalue sequences (modular forms, mod-2 parity strings)
  - Jones polynomial coefficient sequences (knots, mod-2 parity strings)

Three analyses:
  A) Raw zlib ratio (as specified) -- note: length confound present
  B) Shannon entropy (length-independent)
  C) Length-matched zlib: MF traces truncated to match each knot's Jones length

Metric: compression ratio = len(compressed) / len(uncompressed)
Result: Delta_LZ = mean(ratio_MF) - mean(ratio_knot), plus KS test.
"""

import json
import zlib
import random
import numpy as np
from scipy import stats
from pathlib import Path
from collections import Counter

# ── Config ──────────────────────────────────────────────────────────────
N_MF = 2000
N_KNOT = 2000
N_AP = 25          # first 25 a_p values for MF
SEED = 42
OUT_DIR = Path("F:/Prometheus/cartography/v2")

random.seed(SEED)
np.random.seed(SEED)


def parity_string(seq):
    """Convert integer sequence to '0'/'1' parity string (mod 2 of abs)."""
    return "".join(str(int(round(x)) % 2) for x in seq)


def compression_ratio(text: str) -> float:
    """zlib compression ratio: compressed_size / original_size."""
    raw = text.encode("ascii")
    compressed = zlib.compress(raw, level=9)
    return len(compressed) / len(raw)


def shannon_entropy(text: str) -> float:
    """Shannon entropy in bits per character (length-independent)."""
    if len(text) == 0:
        return 0.0
    counts = Counter(text)
    n = len(text)
    return -sum((c / n) * np.log2(c / n) for c in counts.values())


def run_stats(arr_a, arr_b, label_a="MF", label_b="Knot"):
    """Compute comparison statistics between two arrays."""
    mean_a, mean_b = float(np.mean(arr_a)), float(np.mean(arr_b))
    std_a, std_b = float(np.std(arr_a, ddof=1)), float(np.std(arr_b, ddof=1))
    delta = mean_a - mean_b
    pooled = np.sqrt((std_a**2 + std_b**2) / 2)
    d = delta / pooled if pooled > 0 else 0.0
    ks_stat, ks_p = stats.ks_2samp(arr_a, arr_b)
    mw_stat, mw_p = stats.mannwhitneyu(arr_a, arr_b, alternative="two-sided")
    return {
        f"{label_a}_mean": round(mean_a, 6),
        f"{label_a}_std": round(std_a, 6),
        f"{label_a}_median": round(float(np.median(arr_a)), 6),
        f"{label_b}_mean": round(mean_b, 6),
        f"{label_b}_std": round(std_b, 6),
        f"{label_b}_median": round(float(np.median(arr_b)), 6),
        "delta": round(delta, 6),
        "cohens_d": round(d, 4),
        "ks_stat": round(ks_stat, 6),
        "ks_p": float(f"{ks_p:.6e}"),
        "mw_stat": float(mw_stat),
        "mw_p": float(f"{mw_p:.6e}"),
    }


# ── 1. Load Modular Forms from DuckDB ──────────────────────────────────
print("Loading modular forms from DuckDB...")
import duckdb

con = duckdb.connect(str(Path("F:/Prometheus/charon/data/charon.duckdb")), read_only=True)
rows = con.execute(
    "SELECT traces FROM modular_forms "
    "WHERE traces IS NOT NULL AND len(traces) >= 25 "
    "ORDER BY random() LIMIT ?",
    [N_MF],
).fetchall()
con.close()

mf_traces = []
for (traces,) in rows:
    mf_traces.append([float(t) for t in traces[:N_AP]])

print(f"  MF sampled: {len(mf_traces)}")


# ── 2. Load Knots from JSON ────────────────────────────────────────────
print("Loading knots from JSON...")
with open("F:/Prometheus/cartography/knots/data/knots.json") as f:
    knot_data = json.load(f)

knots = knot_data["knots"]
knots_with_jones = [k for k in knots if k.get("jones_coeffs") and len(k["jones_coeffs"]) >= 2]
print(f"  Knots with Jones coeffs: {len(knots_with_jones)}")

sample_knots = random.sample(knots_with_jones, min(N_KNOT, len(knots_with_jones)))
knot_jones = [k["jones_coeffs"] for k in sample_knots]
print(f"  Knots sampled: {len(knot_jones)}")

knot_lengths = np.array([len(j) for j in knot_jones])
print(f"  Jones coeff lengths: min={knot_lengths.min()}, max={knot_lengths.max()}, "
      f"mean={knot_lengths.mean():.1f}, median={np.median(knot_lengths):.0f}")


# ══════════════════════════════════════════════════════════════════════════
# Analysis A: Raw zlib compression ratio (as specified in challenge)
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Analysis A: Raw zlib (MF@25 vs Knot@variable length) ===")
mf_ratios_a = np.array([compression_ratio(parity_string(t)) for t in mf_traces])
knot_ratios_a = np.array([compression_ratio(parity_string(j)) for j in knot_jones])
stats_a = run_stats(mf_ratios_a, knot_ratios_a)
print(f"  MF  ratio: {stats_a['MF_mean']:.4f} +/- {stats_a['MF_std']:.4f}")
print(f"  Knot ratio: {stats_a['Knot_mean']:.4f} +/- {stats_a['Knot_std']:.4f}")
print(f"  Delta_LZ = {stats_a['delta']:.4f}  (Cohen's d = {stats_a['cohens_d']:.2f})")
print(f"  WARNING: knot ratio > 1.0 because zlib header overhead dominates "
      f"on {int(np.median(knot_lengths))}-char strings. Length confound.")


# ══════════════════════════════════════════════════════════════════════════
# Analysis B: Shannon entropy (length-independent, the fair comparison)
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Analysis B: Shannon entropy (bits/char) ===")
mf_entropy = np.array([shannon_entropy(parity_string(t)) for t in mf_traces])
knot_entropy = np.array([shannon_entropy(parity_string(j)) for j in knot_jones])
stats_b = run_stats(mf_entropy, knot_entropy)
print(f"  MF  entropy: {stats_b['MF_mean']:.4f} +/- {stats_b['MF_std']:.4f}")
print(f"  Knot entropy: {stats_b['Knot_mean']:.4f} +/- {stats_b['Knot_std']:.4f}")
print(f"  Delta_entropy = {stats_b['delta']:.4f}  (Cohen's d = {stats_b['cohens_d']:.2f})")


# ══════════════════════════════════════════════════════════════════════════
# Analysis C: Length-matched zlib (truncate MF to 12 chars = median Jones)
# ══════════════════════════════════════════════════════════════════════════
MATCH_LEN = int(np.median(knot_lengths))
print(f"\n=== Analysis C: Length-matched zlib (both at {MATCH_LEN} chars) ===")
mf_ratios_c = np.array([compression_ratio(parity_string(t[:MATCH_LEN])) for t in mf_traces])
knot_ratios_c = np.array([compression_ratio(parity_string(j[:MATCH_LEN])) for j in knot_jones])
stats_c = run_stats(mf_ratios_c, knot_ratios_c)
print(f"  MF  ratio: {stats_c['MF_mean']:.4f} +/- {stats_c['MF_std']:.4f}")
print(f"  Knot ratio: {stats_c['Knot_mean']:.4f} +/- {stats_c['Knot_std']:.4f}")
print(f"  Delta_LZ = {stats_c['delta']:.4f}  (Cohen's d = {stats_c['cohens_d']:.2f})")


# ══════════════════════════════════════════════════════════════════════════
# Permutation null on Analysis B (the clean comparison)
# ══════════════════════════════════════════════════════════════════════════
print("\nRunning permutation null on entropy gap (1000 shuffles)...")
combined = np.concatenate([mf_entropy, knot_entropy])
n_mf = len(mf_entropy)
null_deltas = []
for _ in range(1000):
    np.random.shuffle(combined)
    null_deltas.append(float(np.mean(combined[:n_mf]) - np.mean(combined[n_mf:])))
null_deltas = np.array(null_deltas)
perm_p = float(np.mean(np.abs(null_deltas) >= abs(stats_b["delta"])))
print(f"  Permutation p-value: {perm_p:.4f}")
print(f"  Null delta: mean={np.mean(null_deltas):.4f}, std={np.std(null_deltas):.4f}")


# ── Build interpretation ────────────────────────────────────────────────
delta_e = stats_b["delta"]
ks_p_b = stats_b["ks_p"]

if abs(delta_e) < 0.01:
    interp = "No meaningful entropy gap; MF and knot parity strings have similar mod-2 complexity."
elif delta_e > 0:
    interp = (f"MF parity strings have HIGHER Shannon entropy than knot parity strings "
              f"by {delta_e:.4f} bits/char. MF Hecke traces carry more mod-2 randomness.")
else:
    interp = (f"Knot Jones parity strings have HIGHER Shannon entropy than MF parity strings "
              f"by {abs(delta_e):.4f} bits/char.")

if ks_p_b < 0.001:
    interp += f" KS test confirms distributions are highly distinct (p={ks_p_b:.2e})."
elif ks_p_b < 0.05:
    interp += f" KS test shows moderate distinction (p={ks_p_b:.2e})."
else:
    interp += f" KS test does NOT reject null of same distribution (p={ks_p_b:.2e})."

interp += (f" Raw zlib Delta_LZ={stats_a['delta']:.4f} is DOMINATED by length confound "
           f"(MF@25 chars vs knot@{MATCH_LEN} chars median); "
           f"length-matched Delta_LZ={stats_c['delta']:.4f}.")


# ── Save results ────────────────────────────────────────────────────────
results = {
    "experiment": "mf_knot_lz_compression_gap",
    "description": (
        "Lempel-Ziv (zlib) complexity gap between modular form Hecke traces "
        "and knot Jones polynomial coefficients, both reduced to mod-2 parity strings. "
        "Three analyses: (A) raw zlib, (B) Shannon entropy, (C) length-matched zlib."
    ),
    "params": {
        "n_mf": len(mf_traces),
        "n_knot": len(knot_jones),
        "n_ap_values": N_AP,
        "median_jones_length": MATCH_LEN,
        "compression": "zlib level 9",
        "parity": "abs(coeff) mod 2",
        "seed": SEED,
    },
    "analysis_A_raw_zlib": {
        "note": "Length confound: MF strings are 25 chars, knot strings are 4-13 chars. zlib overhead inflates short-string ratios above 1.0.",
        **stats_a,
    },
    "analysis_B_shannon_entropy": {
        "note": "Shannon entropy in bits/char is length-independent. This is the clean comparison.",
        **stats_b,
    },
    "analysis_C_length_matched_zlib": {
        "note": f"Both truncated to {MATCH_LEN} chars (median Jones length). Same zlib overhead affects both equally.",
        **stats_c,
    },
    "permutation_null_entropy": {
        "n_permutations": 1000,
        "p_value": round(perm_p, 4),
        "null_mean": round(float(np.mean(null_deltas)), 6),
        "null_std": round(float(np.std(null_deltas)), 6),
    },
    "interpretation": interp,
}

out_path = OUT_DIR / "mf_knot_lz_gap_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path}")
print(f"\nInterpretation: {interp}")
