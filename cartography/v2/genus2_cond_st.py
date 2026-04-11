#!/usr/bin/env python3
"""
Genus-2 Conductor Factorization vs Sato-Tate Group
===================================================
Does the prime factorization pattern of genus-2 conductors predict
the Sato-Tate group? Compare to EC result (MI=0.886, z=225).
"""

import json, sys
import numpy as np
from collections import Counter
from pathlib import Path
from sympy import factorint

# ── Config ──────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "genus2" / "data" / "genus2_curves_full.json"
OUT_PATH  = Path(__file__).parent / "genus2_cond_st_results.json"
FP_PRIMES = [2, 3, 5, 7, 11]  # fingerprint primes (first 5)
N_PERM    = 2000
sys.stdout.reconfigure(line_buffering=True)

# ── Load data ───────────────────────────────────────────────────────
print("Loading genus-2 curves...")
curves = json.loads(DATA_PATH.read_text())
print(f"  {len(curves)} curves loaded")

# ── Build conductor fingerprints ────────────────────────────────────
print("Factorizing conductors...")
fingerprints = []
st_labels = []

for c in curves:
    N = c["conductor"]
    st = c["st_group"]
    factors = factorint(N)
    fp = tuple(factors.get(p, 0) for p in FP_PRIMES)
    fingerprints.append(fp)
    st_labels.append(st)

fingerprints = np.array(fingerprints, dtype=np.int32)
st_labels = np.array(st_labels)
unique_st = sorted(set(st_labels))
print(f"  {len(unique_st)} distinct ST groups")

# ── Fast MI using integer-encoded categories ────────────────────────
def encode_fp(fps):
    """Encode fingerprint rows as single integers for fast hashing."""
    # Max exponent per prime is small (< 20), use base-20 encoding
    base = 20
    codes = np.zeros(len(fps), dtype=np.int64)
    for col in range(fps.shape[1]):
        codes = codes * base + fps[:, col]
    return codes

def encode_labels(labels):
    """Map string labels to integer codes."""
    uniq = sorted(set(labels))
    mapping = {s: i for i, s in enumerate(uniq)}
    return np.array([mapping[s] for s in labels], dtype=np.int32), uniq

def fast_mi(fp_codes, label_codes, n_fp_cats, n_label_cats):
    """Compute MI using numpy histograms - much faster than Counter."""
    n = len(fp_codes)
    # Joint histogram
    joint_idx = fp_codes.astype(np.int64) * n_label_cats + label_codes
    joint_counts = np.bincount(joint_idx)
    joint_counts = joint_counts[joint_counts > 0]
    p_joint = joint_counts / n

    # Marginals
    fp_counts = np.bincount(fp_codes)
    fp_counts = fp_counts[fp_counts > 0]
    p_fp = fp_counts / n

    label_counts = np.bincount(label_codes)
    label_counts = label_counts[label_counts > 0]
    p_label = label_counts / n

    H_joint = -np.sum(p_joint * np.log2(p_joint))
    H_fp = -np.sum(p_fp * np.log2(p_fp))
    H_label = -np.sum(p_label * np.log2(p_label))

    mi = H_fp + H_label - H_joint
    nmi = mi / max(H_label, 1e-30)
    return mi, nmi, H_label, H_fp

# Encode for fast computation
print("Encoding...")
fp_codes_raw = encode_fp(fingerprints)
# Re-map to dense codes
fp_uniq, fp_codes = np.unique(fp_codes_raw, return_inverse=True)
fp_codes = fp_codes.astype(np.int32)
n_fp_cats = len(fp_uniq)

st_codes, st_names = encode_labels(st_labels)
n_st_cats = len(st_names)
print(f"  {n_fp_cats} unique fingerprints, {n_st_cats} ST groups")

# ── Compute MI ──────────────────────────────────────────────────────
print("Computing MI...")
mi, nmi, H_st, H_fp = fast_mi(fp_codes, st_codes, n_fp_cats, n_st_cats)
print(f"  MI = {mi:.4f} bits")
print(f"  NMI = {nmi:.4f} (normalized by H(ST)={H_st:.4f})")

# ── Permutation null ───────────────────────────────────────────────
print(f"Running {N_PERM} permutations...")
rng = np.random.default_rng(42)
null_mis = np.empty(N_PERM)
for i in range(N_PERM):
    perm_st = rng.permutation(st_codes)
    pmi, _, _, _ = fast_mi(fp_codes, perm_st, n_fp_cats, n_st_cats)
    null_mis[i] = pmi
    if (i+1) % 500 == 0:
        print(f"  {i+1}/{N_PERM}")

null_mean = np.mean(null_mis)
null_std = np.std(null_mis)
z_score = (mi - null_mean) / max(null_std, 1e-30)
print(f"  Null: mean={null_mean:.6f}, std={null_std:.6f}")
print(f"  z-score = {z_score:.1f}")

# ── Per-prime discriminative power ──────────────────────────────────
print("\nPer-prime MI with ST group:")
prime_mis = {}
for i, p in enumerate(FP_PRIMES):
    exp_col = fingerprints[:, i].astype(np.int32)
    n_cats = int(exp_col.max()) + 1
    pmi, pnmi, _, _ = fast_mi(exp_col, st_codes, n_cats, n_st_cats)
    prime_mis[str(p)] = {"mi": round(float(pmi), 6), "nmi": round(float(pnmi), 6)}
    print(f"  p={p}: MI={pmi:.4f}, NMI={pnmi:.4f}")

# ── Per-ST-group: characteristic exponent profiles ──────────────────
print("\nST group fingerprint profiles:")
st_profiles = {}
for st in unique_st:
    mask = st_labels == st
    count = int(np.sum(mask))
    if count < 2:
        continue
    mean_fp = fingerprints[mask].mean(axis=0)
    profile = {str(p): round(float(mean_fp[i]), 3) for i, p in enumerate(FP_PRIMES)}
    st_profiles[st] = {"count": count, "mean_exponents": profile}
    print(f"  {st} (n={count}): {profile}")

# ── Prime support only ──────────────────────────────────────────────
print("\nPrime-support-only MI:")
support = (fingerprints > 0).astype(np.int32)
sup_codes_raw = encode_fp(support)
sup_uniq, sup_codes = np.unique(sup_codes_raw, return_inverse=True)
sup_codes = sup_codes.astype(np.int32)
mi_support, nmi_support, _, _ = fast_mi(sup_codes, st_codes, len(sup_uniq), n_st_cats)
print(f"  MI(support) = {mi_support:.4f}, NMI = {nmi_support:.4f}")

# ── Binary: USp(4) vs rest ──────────────────────────────────────────
binary_codes = (st_labels != "USp(4)").astype(np.int32)
mi_binary, nmi_binary, H_binary, _ = fast_mi(fp_codes, binary_codes, n_fp_cats, 2)
print(f"\nBinary (USp(4) vs rest): MI={mi_binary:.4f}, NMI={nmi_binary:.4f}, H={H_binary:.4f}")

# ── Assemble results ───────────────────────────────────────────────
results = {
    "experiment": "genus2_conductor_st_prediction",
    "description": "Does prime factorization of genus-2 conductor predict Sato-Tate group?",
    "data": {
        "source": str(DATA_PATH.name),
        "n_curves": len(curves),
        "n_st_groups": len(unique_st),
        "n_unique_fingerprints": int(n_fp_cats),
        "st_distribution": {st: int(np.sum(st_labels == st)) for st in unique_st},
        "fingerprint_primes": FP_PRIMES
    },
    "mutual_information": {
        "mi_bits": round(float(mi), 6),
        "nmi": round(float(nmi), 6),
        "H_st": round(float(H_st), 6),
        "H_fp": round(float(H_fp), 6)
    },
    "permutation_test": {
        "n_perms": N_PERM,
        "null_mean": round(float(null_mean), 6),
        "null_std": round(float(null_std), 6),
        "z_score": round(float(z_score), 1),
        "p_value": float(np.mean(null_mis >= mi))
    },
    "per_prime_mi": prime_mis,
    "prime_support_only": {
        "mi_bits": round(float(mi_support), 6),
        "nmi": round(float(nmi_support), 6)
    },
    "binary_usp4_vs_rest": {
        "mi_bits": round(float(mi_binary), 6),
        "nmi": round(float(nmi_binary), 6),
        "H_binary": round(float(H_binary), 6)
    },
    "st_profiles": st_profiles,
    "comparison_to_ec": {
        "ec_mi": 0.886,
        "ec_z": 225,
        "genus2_mi": round(float(mi), 6),
        "genus2_z": round(float(z_score), 1),
        "interpretation": None
    },
    "tautology_assessment": None
}

# ── Interpretation ──────────────────────────────────────────────────
if z_score > 50:
    sig = "extremely significant"
elif z_score > 10:
    sig = "highly significant"
elif z_score > 3:
    sig = "significant"
else:
    sig = "not significant"

tautology = (
    "PARTIALLY TAUTOLOGICAL. The Sato-Tate group is determined by the endomorphism "
    "algebra (over Q-bar), which constrains both the ST group and the conductor's prime "
    "factorization via local reduction types. Unlike EC where conductor directly encodes "
    "CM (fully tautological), genus-2 has genuine predictive content because: "
    "(1) the mapping from endo algebra to conductor exponents is many-to-one, "
    "(2) conductor also encodes non-endomorphism information (e.g., Tamagawa numbers), "
    f"(3) MI={mi:.3f} bits (z={z_score:.0f}) with {nmi:.1%} of ST entropy "
    "explained shows the conductor fingerprint is a strong but imperfect proxy."
)
if nmi > 0.5:
    tautology += " However, the high NMI suggests most of the signal IS coming through the endo->conductor channel."
elif nmi < 0.1:
    tautology += " The low NMI confirms conductor fingerprint captures very little ST information."

results["tautology_assessment"] = tautology
results["comparison_to_ec"]["interpretation"] = (
    f"Genus-2 MI={mi:.3f} vs EC MI=0.886. "
    f"Genus-2 z={z_score:.0f} vs EC z=225. "
    + ("Genus-2 shows WEAKER conductor->ST coupling, consistent with richer endo structure."
       if mi < 0.886 else "Genus-2 shows COMPARABLE or STRONGER coupling.")
)

OUT_PATH.write_text(json.dumps(results, indent=2))
print(f"\nResults saved to {OUT_PATH}")
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"MI = {mi:.4f} bits (NMI = {nmi:.4f})")
print(f"z-score = {z_score:.1f} ({sig})")
print(f"EC comparison: MI=0.886/z=225 vs genus-2 MI={mi:.4f}/z={z_score:.1f}")
print(f"Most discriminative prime: {max(prime_mis, key=lambda p: prime_mis[p]['mi'])}")
print(f"\nTautology: {tautology[:200]}...")
