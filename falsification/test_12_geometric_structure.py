"""
Falsification Test 12: Does the 9x246 matrix have intrinsic geometric structure?

CLAIM: The matrix has rank/curvature beyond what random fill produces.
APPROACH: Build weighted matrices (not binary), compute SVD, compare to null ensemble.
"""

import json
import numpy as np
import duckdb
from collections import defaultdict

np.random.seed(42)
N_RANDOM = 1000

DB_PATH = "noesis/v2/noesis_v2.duckdb"
con = duckdb.connect(DB_PATH, read_only=True)

# ============================================================
# PART 1: Build the 9x246 operator-hub weighted matrix
# from depth2_matrix (op-pair -> hub, with confidence)
# ============================================================

# Get operator and hub lists
# depth2_matrix uses short names (CONCENTRATE), damage_operators uses D_CONCENTRATE
# Use the short names from depth2_matrix directly
operators = [r[0] for r in con.execute("SELECT DISTINCT op1 FROM depth2_matrix ORDER BY op1").fetchall()]
hubs = [r[0] for r in con.execute("SELECT comp_id FROM abstract_compositions ORDER BY comp_id").fetchall()]

op_idx = {o: i for i, o in enumerate(operators)}
hub_idx = {h: i for i, h in enumerate(hubs)}

print(f"Operators: {len(operators)}, Hubs: {len(hubs)}")

# Build from cross_domain_edges: count edges per (operator, hub)
# Map resolution_id -> hub via abstract_compositions
# Actually, depth2_matrix directly has (op1, op2, hub_id, confidence)
# We want: for each (damage_operator, hub), a weight.
#
# Strategy A: From depth2_matrix, aggregate by first operator x hub
#   weight = sum of confidence scores (HIGH=3, MEDIUM=2, LOW=1)
# Strategy B: From cross_domain_edges, count edges per operator
#   (but edges link resolutions, not hubs directly)
#
# Let's use depth2_matrix which has 9 ops x 246 hubs directly.
# The matrix is op1 x hub_id, summing confidence weights over op2.

conf_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

# Build 9x246 matrix from depth2_matrix
rows = con.execute("SELECT op1, hub_id, confidence FROM depth2_matrix").fetchall()
mat_depth2 = np.zeros((len(operators), len(hubs)))
for op1, hub_id, conf in rows:
    if op1 in op_idx and hub_id in hub_idx:
        mat_depth2[op_idx[op1], hub_idx[hub_id]] += conf_map.get(conf, 1)

print(f"\n=== DEPTH2 MATRIX (op1 x hub, confidence-weighted) ===")
print(f"Shape: {mat_depth2.shape}")
print(f"Nonzero: {np.count_nonzero(mat_depth2)} / {mat_depth2.size} ({100*np.count_nonzero(mat_depth2)/mat_depth2.size:.1f}%)")
print(f"Min/Max/Mean: {mat_depth2.min():.1f} / {mat_depth2.max():.1f} / {mat_depth2.mean():.2f}")
print(f"Row sums range: {mat_depth2.sum(axis=1).min():.0f} - {mat_depth2.sum(axis=1).max():.0f}")
print(f"Col sums range: {mat_depth2.sum(axis=0).min():.0f} - {mat_depth2.sum(axis=0).max():.0f}")

# SVD
U, S, Vt = np.linalg.svd(mat_depth2, full_matrices=False)
real_rank = np.linalg.matrix_rank(mat_depth2)
print(f"\nRank: {real_rank}")
print(f"Singular values: {np.round(S, 2)}")
print(f"Top SV explains: {100*S[0]**2/np.sum(S**2):.1f}% of variance")
print(f"Top 2 SVs explain: {100*np.sum(S[:2]**2)/np.sum(S**2):.1f}% of variance")
print(f"Top 3 SVs explain: {100*np.sum(S[:3]**2)/np.sum(S**2):.1f}% of variance")

# Effective rank (Shannon entropy based)
s_norm = S / S.sum()
s_norm = s_norm[s_norm > 0]
effective_rank = np.exp(-np.sum(s_norm * np.log(s_norm)))
print(f"Effective rank (Shannon): {effective_rank:.2f}")

# ============================================================
# PART 2: Null ensemble -- random matrices with same marginals
# ============================================================

print(f"\n=== NULL ENSEMBLE ({N_RANDOM} random matrices with same marginals) ===")

row_sums = mat_depth2.sum(axis=1)
col_sums = mat_depth2.sum(axis=0)
total = mat_depth2.sum()

# Generate random matrices preserving marginals using iterative proportional fitting
# Start from outer product of marginals, add noise, re-normalize
random_ranks = []
random_sv1_frac = []
random_sv_spectra = []
random_effective_ranks = []

for trial in range(N_RANDOM):
    # Method: sample from Poisson with rate = row_sum * col_sum / total,
    # then scale to match marginals (Sinkhorn)
    expected = np.outer(row_sums, col_sums) / total
    rand_mat = np.random.poisson(expected).astype(float)

    # Sinkhorn normalization to match marginals (5 iterations)
    for _ in range(10):
        # Scale rows
        rs = rand_mat.sum(axis=1, keepdims=True)
        rs[rs == 0] = 1
        rand_mat *= (row_sums.reshape(-1, 1) / rs)
        # Scale cols
        cs = rand_mat.sum(axis=0, keepdims=True)
        cs[cs == 0] = 1
        rand_mat *= (col_sums.reshape(1, -1) / cs)

    _, S_rand, _ = np.linalg.svd(rand_mat, full_matrices=False)
    random_ranks.append(np.linalg.matrix_rank(rand_mat))
    random_sv1_frac.append(S_rand[0]**2 / np.sum(S_rand**2))
    random_sv_spectra.append(S_rand)

    s_n = S_rand / S_rand.sum()
    s_n = s_n[s_n > 0]
    random_effective_ranks.append(np.exp(-np.sum(s_n * np.log(s_n))))

random_ranks = np.array(random_ranks)
random_sv1_frac = np.array(random_sv1_frac)
random_effective_ranks = np.array(random_effective_ranks)

print(f"Random rank: mean={random_ranks.mean():.2f}, std={random_ranks.std():.2f}")
print(f"Real rank: {real_rank}")
print(f"Random eff rank: mean={random_effective_ranks.mean():.2f}, std={random_effective_ranks.std():.2f}")
print(f"Real eff rank: {effective_rank:.2f}")

# p-value for rank
rank_p = np.mean(random_ranks <= real_rank)
eff_rank_p = np.mean(random_effective_ranks <= effective_rank)
print(f"p-value (rank <= real): {rank_p:.4f}")
print(f"p-value (eff_rank <= real): {eff_rank_p:.4f}")

# Compare SV1 dominance
real_sv1_frac = S[0]**2 / np.sum(S**2)
sv1_p = np.mean(random_sv1_frac >= real_sv1_frac)
print(f"\nSV1 dominance: real={100*real_sv1_frac:.1f}%, random mean={100*random_sv1_frac.mean():.1f}%")
print(f"p-value (random SV1 >= real): {sv1_p:.4f}")

# Spectral gap: ratio S[0]/S[1]
spectral_gap = S[0] / S[1] if S[1] > 0 else float('inf')
random_gaps = np.array([sp[0]/sp[1] if sp[1] > 0 else float('inf') for sp in random_sv_spectra])
gap_p = np.mean(random_gaps >= spectral_gap)
print(f"Spectral gap (S1/S2): real={spectral_gap:.2f}, random mean={random_gaps.mean():.2f}")
print(f"p-value (random gap >= real): {gap_p:.4f}")

# ============================================================
# PART 3: Also try op2 as the row dimension (pair-based)
# ============================================================

# Build using BOTH op1 and op2: 9x9x246 tensor → flatten to 81x246
print(f"\n=== OP-PAIR TENSOR (81x246) ===")
mat_pair = np.zeros((len(operators)*len(operators), len(hubs)))
for op1, op2, hub_id, conf in con.execute("SELECT op1, op2, hub_id, confidence FROM depth2_matrix").fetchall():
    if op1 in op_idx and op2 in op_idx and hub_id in hub_idx:
        pair_i = op_idx[op1] * len(operators) + op_idx[op2]
        mat_pair[pair_i, hub_idx[hub_id]] += conf_map.get(conf, 1)

pair_rank = np.linalg.matrix_rank(mat_pair)
_, S_pair, _ = np.linalg.svd(mat_pair, full_matrices=False)
print(f"Shape: {mat_pair.shape}, Rank: {pair_rank}")
print(f"Max possible rank: {min(mat_pair.shape)}")
print(f"Top 5 SVs: {np.round(S_pair[:5], 2)}")
top3_var = 100*np.sum(S_pair[:3]**2)/np.sum(S_pair**2)
top5_var = 100*np.sum(S_pair[:5]**2)/np.sum(S_pair**2)
print(f"Top 3 SVs explain: {top3_var:.1f}% of variance")
print(f"Top 5 SVs explain: {top5_var:.1f}% of variance")

# ============================================================
# PART 4: Ethnomathematics 153x11 primitive vector matrix
# ============================================================

print(f"\n=== ETHNOMATHEMATICS (153 traditions x primitives) ===")

rows_ethno = con.execute("SELECT system_id, enriched_primitive_vector FROM ethnomathematics WHERE enriched_primitive_vector IS NOT NULL").fetchall()

# Collect all primitive names
all_prims = set()
parsed = []
for sys_id, vec_str in rows_ethno:
    try:
        vec = json.loads(vec_str)
        for item in vec:
            all_prims.add(item[0])
        parsed.append((sys_id, vec))
    except:
        pass

prim_list = sorted(all_prims)
prim_idx = {p: i for i, p in enumerate(prim_list)}
print(f"Primitives found: {prim_list}")
print(f"Traditions parsed: {len(parsed)}")

mat_ethno = np.zeros((len(parsed), len(prim_list)))
for i, (sys_id, vec) in enumerate(parsed):
    for prim, weight in vec:
        if prim in prim_idx:
            mat_ethno[i, prim_idx[prim]] = weight

print(f"Shape: {mat_ethno.shape}")
print(f"Nonzero: {np.count_nonzero(mat_ethno)} / {mat_ethno.size} ({100*np.count_nonzero(mat_ethno)/mat_ethno.size:.1f}%)")

ethno_rank = np.linalg.matrix_rank(mat_ethno)
_, S_ethno, _ = np.linalg.svd(mat_ethno, full_matrices=False)
print(f"Rank: {ethno_rank} (max possible: {min(mat_ethno.shape)})")
print(f"Singular values: {np.round(S_ethno, 3)}")
ethno_top3 = 100*np.sum(S_ethno[:3]**2)/np.sum(S_ethno**2)
print(f"Top 3 SVs explain: {ethno_top3:.1f}% of variance")

# Ethnomathematics null ensemble
ethno_row_sums = mat_ethno.sum(axis=1)
ethno_col_sums = mat_ethno.sum(axis=0)
ethno_total = mat_ethno.sum()

ethno_random_ranks = []
ethno_random_eff_ranks = []
for trial in range(N_RANDOM):
    expected = np.outer(ethno_row_sums, ethno_col_sums) / ethno_total
    # Use continuous noise for continuous data
    rand_mat = np.abs(np.random.normal(expected, np.sqrt(np.abs(expected) + 0.01)))
    for _ in range(10):
        rs = rand_mat.sum(axis=1, keepdims=True)
        rs[rs == 0] = 1
        rand_mat *= (ethno_row_sums.reshape(-1, 1) / rs)
        cs = rand_mat.sum(axis=0, keepdims=True)
        cs[cs == 0] = 1
        rand_mat *= (ethno_col_sums.reshape(1, -1) / cs)

    ethno_random_ranks.append(np.linalg.matrix_rank(rand_mat))
    _, Se, _ = np.linalg.svd(rand_mat, full_matrices=False)
    s_n = Se / Se.sum()
    s_n = s_n[s_n > 0]
    ethno_random_eff_ranks.append(np.exp(-np.sum(s_n * np.log(s_n))))

ethno_random_ranks = np.array(ethno_random_ranks)
ethno_random_eff_ranks = np.array(ethno_random_eff_ranks)

s_ethno_norm = S_ethno / S_ethno.sum()
s_ethno_norm = s_ethno_norm[s_ethno_norm > 0]
ethno_eff_rank = np.exp(-np.sum(s_ethno_norm * np.log(s_ethno_norm)))

ethno_rank_p = np.mean(ethno_random_ranks <= ethno_rank)
ethno_eff_rank_p = np.mean(ethno_random_eff_ranks <= ethno_eff_rank)

print(f"\nEthno random rank: mean={ethno_random_ranks.mean():.2f}, std={ethno_random_ranks.std():.2f}")
print(f"Ethno real rank: {ethno_rank}")
print(f"Ethno p-value (rank <= real): {ethno_rank_p:.4f}")
print(f"Ethno eff rank: real={ethno_eff_rank:.2f}, random mean={ethno_random_eff_ranks.mean():.2f}")
print(f"Ethno eff rank p-value: {ethno_eff_rank_p:.4f}")

# ============================================================
# PART 5: Additional test — Tradition-Hub matrix
# ============================================================

print(f"\n=== TRADITION-HUB MATRIX ===")
thm_rows = con.execute("""
    SELECT tradition_id, hub_id, confidence
    FROM tradition_hub_matrix
""").fetchall()

traditions = sorted(set(r[0] for r in thm_rows))
trad_idx = {t: i for i, t in enumerate(traditions)}

mat_thm = np.zeros((len(traditions), len(hubs)))
for trad, hub, conf in thm_rows:
    if trad in trad_idx and hub in hub_idx:
        mat_thm[trad_idx[trad], hub_idx[hub]] += conf_map.get(conf, 1)

print(f"Shape: {mat_thm.shape}")
thm_rank = np.linalg.matrix_rank(mat_thm)
_, S_thm, _ = np.linalg.svd(mat_thm, full_matrices=False)
thm_top3 = 100*np.sum(S_thm[:3]**2)/np.sum(S_thm**2)
thm_top5 = 100*np.sum(S_thm[:5]**2)/np.sum(S_thm**2)
print(f"Rank: {thm_rank} (max possible: {min(mat_thm.shape)})")
print(f"Top 5 SVs: {np.round(S_thm[:5], 2)}")
print(f"Top 3/5 SVs explain: {thm_top3:.1f}% / {thm_top5:.1f}% of variance")

con.close()

# ============================================================
# VERDICT
# ============================================================

print("\n" + "="*70)
print("VERDICT")
print("="*70)

evidence_parts = []

# Main 9x246 matrix assessment
# Key question: is rank lower than random? Is there spectral concentration?
if rank_p < 0.05:
    evidence_parts.append(f"9x246 matrix: rank {real_rank} is significantly LOW vs random (mean={random_ranks.mean():.1f}, p={rank_p:.4f})")
elif rank_p > 0.95:
    evidence_parts.append(f"9x246 matrix: rank {real_rank} is significantly HIGH vs random (mean={random_ranks.mean():.1f}, p={rank_p:.4f})")
else:
    evidence_parts.append(f"9x246 matrix: rank {real_rank} is NOT significantly different from random (mean={random_ranks.mean():.1f}, p={rank_p:.4f})")

evidence_parts.append(f"Effective rank: real={effective_rank:.2f} vs random mean={random_effective_ranks.mean():.2f} (p={eff_rank_p:.4f})")
evidence_parts.append(f"SV1 dominance: real={100*real_sv1_frac:.1f}% vs random={100*random_sv1_frac.mean():.1f}% (p={sv1_p:.4f})")
evidence_parts.append(f"Spectral gap: real={spectral_gap:.2f} vs random={random_gaps.mean():.2f} (p={gap_p:.4f})")
evidence_parts.append(f"81x246 pair tensor rank: {pair_rank}/{min(mat_pair.shape)} (top3 var: {top3_var:.1f}%)")
evidence_parts.append(f"Ethnomathematics 153x{len(prim_list)} rank: {ethno_rank}/{min(mat_ethno.shape)} (random mean={ethno_random_ranks.mean():.1f}, p={ethno_rank_p:.4f})")
evidence_parts.append(f"Tradition-hub {mat_thm.shape[0]}x{mat_thm.shape[1]} rank: {thm_rank}/{min(mat_thm.shape)} (top3 var: {thm_top3:.1f}%)")

# Decision logic
significant_structure = False
reasons = []

# Check if SV1 dominance exceeds random
if sv1_p < 0.05:
    significant_structure = True
    reasons.append("SV1 dominance significantly exceeds random")

# Check effective rank
if eff_rank_p < 0.05:
    significant_structure = True
    reasons.append("Effective rank significantly lower than random")

# Check spectral gap
if gap_p < 0.05:
    significant_structure = True
    reasons.append("Spectral gap significantly exceeds random")

# Check ethnomathematics
if ethno_rank_p < 0.05 or ethno_eff_rank_p < 0.05:
    significant_structure = True
    reasons.append("Ethnomathematics matrix shows structural rank deficit")

if significant_structure:
    result = "PASS"
    confidence = "HIGH" if len(reasons) >= 2 else "MODERATE"
elif rank_p < 0.1 or sv1_p < 0.1 or gap_p < 0.1:
    result = "INCONCLUSIVE"
    confidence = "LOW"
else:
    result = "FAIL"
    confidence = "HIGH" if all(p > 0.3 for p in [rank_p, sv1_p, gap_p]) else "MODERATE"

evidence_str = "; ".join(evidence_parts)
if reasons:
    evidence_str += "; PASS reasons: " + ", ".join(reasons)

print(f"\nResult: {result} (confidence: {confidence})")
for e in evidence_parts:
    print(f"  {e}")
if reasons:
    print(f"  PASS reasons: {', '.join(reasons)}")

# Implications
if result == "PASS":
    implications = "Supports claim that operator-hub relationships have latent geometric structure beyond random connectivity. Strengthens the 'Geometry of Impossibility' thesis that impossibility theorems share structural DNA."
elif result == "FAIL":
    implications = "The operator-hub matrix is statistically indistinguishable from random fill with same marginals. The 'geometric structure' claim may be an artifact of high fill rate. Weakens structural claims in Noesis papers."
else:
    implications = "Mixed signals -- some structural indicators but not conclusive. More targeted tests needed."

# Save results
output = {
    "test": 12,
    "paper": "Geometry of Impossibility",
    "claim": "The 9x246 matrix has intrinsic geometric structure (rank, curvature) beyond what random fill would produce",
    "result": result,
    "confidence": confidence,
    "evidence": evidence_str,
    "singular_values": [round(float(s), 4) for s in S],
    "real_rank": int(real_rank),
    "random_rank_mean": round(float(random_ranks.mean()), 2),
    "random_rank_std": round(float(random_ranks.std()), 2),
    "p_value": round(float(min(rank_p, eff_rank_p, sv1_p, gap_p)), 4),
    "effective_rank_real": round(float(effective_rank), 2),
    "effective_rank_random_mean": round(float(random_effective_ranks.mean()), 2),
    "sv1_dominance_real": round(float(100*real_sv1_frac), 1),
    "sv1_dominance_random_mean": round(float(100*random_sv1_frac.mean()), 1),
    "sv1_p_value": round(float(sv1_p), 4),
    "spectral_gap_real": round(float(spectral_gap), 2),
    "spectral_gap_random_mean": round(float(random_gaps.mean()), 2),
    "spectral_gap_p_value": round(float(gap_p), 4),
    "ethnomathematics_rank": int(ethno_rank),
    "ethnomathematics_max_rank": min(mat_ethno.shape),
    "ethnomathematics_rank_p": round(float(ethno_rank_p), 4),
    "pair_tensor_rank": int(pair_rank),
    "pair_tensor_max_rank": min(mat_pair.shape),
    "implications_for_other_papers": implications
}

with open("falsification/test_12_result.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to falsification/test_12_result.json")
