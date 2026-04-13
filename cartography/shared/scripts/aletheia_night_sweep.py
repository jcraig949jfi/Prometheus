"""
Aletheia Night Sweep — Full exploration of the Megethos-zeroed dissection tensor.

Runs on the clean v8 tensor (769K objects x 182 dims, 27 domains).
Zeros out s13 (Megethos) and s7_cond (secondary magnitude leakage).
Then runs:
  Step 1: Load + zero Megethos
  Step 2: Strategy group correlation matrix (Megethos-zeroed vs original)
  Step 3: Full pairwise TT-Cross sweep (bond dimensions)
  Step 4: MAP-Elites on zeroed tensor
  Step 5: Random walkers (27 walkers, one per domain)
  Step 6: Summary + save

All distance computations on GPU. Aggressive sampling for speed.
Target: < 30 minutes total on RTX 5060 Ti.

2026-04-12 overnight run.
"""

import json
import time
import sys
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"[Aletheia Night Sweep] Device: {DEVICE}")
print(f"[Aletheia Night Sweep] Start: {time.strftime('%Y-%m-%d %H:%M:%S')}")
T_GLOBAL = time.time()

DATA_DIR = Path(__file__).resolve().parents[2] / "convergence" / "data"

# Strategy group definitions (from dissection_tensor.py)
STRATEGY_GROUPS = {
    "complex":     ["s1_alex", "s1_jones", "s1_ap"],
    "mod_p":       ["s3_alex", "s3_jones", "s3_ap"],
    "spectral":    ["s5_alex", "s5_jones", "s5_ap", "s5_oeis"],
    "padic":       ["s7_det", "s7_disc", "s7_cond"],
    "symmetry":    ["s9_st", "s9_endo"],
    "galois":      ["s10", "s10_galrep"],
    "zeta":        ["s12_ec", "s12_oeis", "s12_nf"],
    "disc_cond":   ["s13"],
    "operadic":    ["s22"],
    "entropy":     ["s24_alex", "s24_arith", "s24_ap", "s24_sym", "s24_oeis"],
    "attractor":   ["s6_oeis"],
    "automorphic": ["s21_auto"],
    "monodromy":   ["s11_mono"],
    "ade":         ["s19_ade"],
    "recurrence":  ["s33_recurrence"],
}
GROUP_NAMES = list(STRATEGY_GROUPS.keys())
N_GROUPS = len(GROUP_NAMES)


# ================================================================
# STEP 1: Load tensor and zero Megethos
# ================================================================
print("\n" + "=" * 80)
print("STEP 1: Load tensor and zero Megethos")
print("=" * 80)

t1 = time.time()
checkpoint = torch.load(DATA_DIR / "dissection_tensor.pt", weights_only=False, map_location='cpu')

tensor_orig = checkpoint['tensor'].clone()  # keep original for correlation comparison
tensor = checkpoint['tensor'].to(DEVICE)
mask = checkpoint['mask'].to(DEVICE)
domains = checkpoint['domains']
labels = checkpoint['labels']
strategy_slices = checkpoint['strategy_slices']

N_OBJ, N_DIM = tensor.shape
print(f"  Tensor: {N_OBJ} objects x {N_DIM} dims")
print(f"  Domains: {len(set(domains))} unique")
print(f"  Fill rate: {mask.float().mean().item() * 100:.1f}%")

# Build group slices
group_slices = {}
for gname, strat_list in STRATEGY_GROUPS.items():
    starts = [strategy_slices[s][0] for s in strat_list if s in strategy_slices]
    ends = [strategy_slices[s][1] for s in strat_list if s in strategy_slices]
    if starts:
        group_slices[gname] = (min(starts), max(ends))

# Zero s13 (Megethos / magnitude)
s13_start, s13_end = strategy_slices['s13']
print(f"  Zeroing s13 (Megethos): dims {s13_start}:{s13_end}")
tensor[:, s13_start:s13_end] = 0.0
mask[:, s13_start:s13_end] = False

# Zero s7_cond (secondary Megethos leakage)
s7c_start, s7c_end = strategy_slices['s7_cond']
print(f"  Zeroing s7_cond (Megethos leakage): dims {s7c_start}:{s7c_end}")
tensor[:, s7c_start:s7c_end] = 0.0
mask[:, s7c_start:s7c_end] = False

# Count active dims
active_dims = mask.any(dim=0).sum().item()
print(f"  Active dims after zeroing: {active_dims}/{N_DIM}")

# Build domain index
domain_counts = Counter(domains)
domain_indices = defaultdict(list)
for i, d in enumerate(domains):
    domain_indices[d].append(i)

valid_domains = sorted([d for d, c in domain_counts.items() if c >= 100])
all_domains = sorted(domain_indices.keys())
print(f"  Valid domains (>=100 objects): {len(valid_domains)}")
for d in valid_domains:
    print(f"    {d}: {domain_counts[d]}")

print(f"  Step 1 complete: {time.time() - t1:.1f}s")


# ================================================================
# STEP 2: Strategy group correlation matrix (Megethos-zeroed)
# ================================================================
print("\n" + "=" * 80)
print("STEP 2: Strategy group correlation matrix")
print("=" * 80)

t2 = time.time()


def compute_group_means(t, m, gs):
    """Compute per-object mean value in each strategy group."""
    N = t.shape[0]
    gv = torch.zeros(N, N_GROUPS, device=t.device)
    gvalid = torch.zeros(N, N_GROUPS, device=t.device, dtype=torch.bool)
    for gi, gname in enumerate(GROUP_NAMES):
        if gname not in gs:
            continue
        start, end = gs[gname]
        g_data = t[:, start:end]
        g_mask = m[:, start:end].float()
        has = g_mask.sum(dim=1) > 0
        denom = g_mask.sum(dim=1).clamp(min=1)
        gv[:, gi] = (g_data * g_mask).sum(dim=1) / denom
        gvalid[:, gi] = has
    return gv, gvalid


# Sample 50K for correlation computation (speed)
rng = np.random.RandomState(42)
sample_idx = rng.choice(N_OBJ, min(50000, N_OBJ), replace=False)
sample_t = torch.tensor(sample_idx, dtype=torch.long, device=DEVICE)

# Megethos-zeroed group means
gv_zeroed, gvalid_zeroed = compute_group_means(tensor[sample_t], mask[sample_t], group_slices)

# Original group means (for comparison)
tensor_orig_dev = tensor_orig.to(DEVICE)
mask_orig = checkpoint['mask'].to(DEVICE)
gv_orig, gvalid_orig = compute_group_means(tensor_orig_dev[sample_t], mask_orig[sample_t], group_slices)
del tensor_orig_dev, mask_orig
torch.cuda.empty_cache()

# Compute 15x15 correlation for zeroed tensor
# Use objects that have data in both groups
print("  Computing group correlation matrices...")
corr_zeroed = np.zeros((N_GROUPS, N_GROUPS))
corr_orig = np.zeros((N_GROUPS, N_GROUPS))

for i in range(N_GROUPS):
    for j in range(N_GROUPS):
        # Zeroed
        both_valid = gvalid_zeroed[:, i] & gvalid_zeroed[:, j]
        n_both = both_valid.sum().item()
        if n_both > 30:
            vi = gv_zeroed[both_valid, i].cpu().numpy()
            vj = gv_zeroed[both_valid, j].cpu().numpy()
            if vi.std() > 1e-12 and vj.std() > 1e-12:
                corr_zeroed[i, j] = np.corrcoef(vi, vj)[0, 1]

        # Original
        both_valid_o = gvalid_orig[:, i] & gvalid_orig[:, j]
        n_both_o = both_valid_o.sum().item()
        if n_both_o > 30:
            vi_o = gv_orig[both_valid_o, i].cpu().numpy()
            vj_o = gv_orig[both_valid_o, j].cpu().numpy()
            if vi_o.std() > 1e-12 and vj_o.std() > 1e-12:
                corr_orig[i, j] = np.corrcoef(vi_o, vj_o)[0, 1]

# Report top 10 surviving correlations
print("\n  Top 10 group correlations AFTER Megethos zeroing:")
corr_pairs = []
for i in range(N_GROUPS):
    for j in range(i + 1, N_GROUPS):
        corr_pairs.append((GROUP_NAMES[i], GROUP_NAMES[j],
                           corr_zeroed[i, j], corr_orig[i, j]))

corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
print(f"  {'Group A':<15} {'Group B':<15} {'Zeroed r':<12} {'Original r':<12} {'Delta':<10}")
print("  " + "-" * 64)
for ga, gb, rz, ro in corr_pairs[:10]:
    print(f"  {ga:<15} {gb:<15} {rz:>+.4f}      {ro:>+.4f}      {rz - ro:>+.4f}")

# Which correlations disappeared?
killed_corr = [(ga, gb, rz, ro) for ga, gb, rz, ro in corr_pairs
               if abs(ro) > 0.1 and abs(rz) < 0.05]
print(f"\n  Correlations KILLED by Megethos zeroing ({len(killed_corr)}):")
for ga, gb, rz, ro in killed_corr[:5]:
    print(f"    {ga} <-> {gb}: {ro:+.4f} -> {rz:+.4f}")

step2_results = {
    'corr_zeroed': {f"{GROUP_NAMES[i]}_{GROUP_NAMES[j]}": round(float(corr_zeroed[i, j]), 4)
                    for i in range(N_GROUPS) for j in range(i + 1, N_GROUPS)},
    'corr_orig': {f"{GROUP_NAMES[i]}_{GROUP_NAMES[j]}": round(float(corr_orig[i, j]), 4)
                  for i in range(N_GROUPS) for j in range(i + 1, N_GROUPS)},
    'top_10_zeroed': [{'a': ga, 'b': gb, 'r_zeroed': round(rz, 4), 'r_orig': round(ro, 4)}
                      for ga, gb, rz, ro in corr_pairs[:10]],
    'killed_correlations': [{'a': ga, 'b': gb, 'r_zeroed': round(rz, 4), 'r_orig': round(ro, 4)}
                            for ga, gb, rz, ro in killed_corr],
}
print(f"  Step 2 complete: {time.time() - t2:.1f}s")


# ================================================================
# STEP 3: Full pairwise TT-Cross sweep (Megethos-zeroed)
# ================================================================
print("\n" + "=" * 80)
print("STEP 3: Full pairwise TT-Cross sweep (Megethos-zeroed)")
print("=" * 80)

t3 = time.time()
MAX_SAMPLE = 500
N_NULL = 10


def compute_coupling_matrix(idx_a, idx_b):
    """Coupling matrix C[i,j] = cosine_sim(A_i, B_j) on shared dims."""
    vecs_a = tensor[idx_a]
    vecs_b = tensor[idx_b]
    mask_a = mask[idx_a]
    mask_b = mask[idx_b]

    shared_dims = mask_a.any(dim=0) & mask_b.any(dim=0)
    n_shared = shared_dims.sum().item()
    if n_shared < 3:
        return None, 0

    va = vecs_a[:, shared_dims] * mask_a[:, shared_dims].float()
    vb = vecs_b[:, shared_dims] * mask_b[:, shared_dims].float()

    va_norm = F.normalize(va, p=2, dim=1)
    vb_norm = F.normalize(vb, p=2, dim=1)

    C = va_norm @ vb_norm.T
    return C, n_shared


def effective_rank(C, threshold=0.01):
    """Effective rank = # singular values > threshold * s_1."""
    U, S, Vh = torch.linalg.svd(C, full_matrices=False)
    s1 = S[0].item()
    if s1 < 1e-12:
        return 0, 0.0, S.cpu().numpy()
    cutoff = threshold * s1
    rank = (S > cutoff).sum().item()
    return rank, s1, S.cpu().numpy()


# Sample per domain
domain_samples = {}
for d in valid_domains:
    idx = np.array(domain_indices[d])
    if len(idx) > MAX_SAMPLE:
        idx = rng.choice(idx, MAX_SAMPLE, replace=False)
    domain_samples[d] = idx

pairs = list(combinations(valid_domains, 2))
print(f"  Total domain pairs: {len(pairs)}")
print(f"  Sample per domain: {MAX_SAMPLE}")
print(f"  Null permutations: {N_NULL}")

ttcross_results = []
for pi, (da, db) in enumerate(pairs):
    idx_a = domain_samples[da]
    idx_b = domain_samples[db]

    C, n_shared = compute_coupling_matrix(
        torch.tensor(idx_a, dtype=torch.long, device=DEVICE),
        torch.tensor(idx_b, dtype=torch.long, device=DEVICE),
    )

    if C is None:
        continue

    rank, s1, svals = effective_rank(C)
    mean_coupling = C.mean().item()

    # Null: shuffle domain labels
    null_ranks = []
    merged = np.concatenate([idx_a, idx_b])
    na, nb = len(idx_a), len(idx_b)
    for _ in range(N_NULL):
        perm = rng.permutation(len(merged))
        shuf_a = merged[perm[:na]]
        shuf_b = merged[perm[na:na + nb]]
        Cn, ns = compute_coupling_matrix(
            torch.tensor(shuf_a, dtype=torch.long, device=DEVICE),
            torch.tensor(shuf_b, dtype=torch.long, device=DEVICE),
        )
        if Cn is not None:
            nr, _, _ = effective_rank(Cn)
            null_ranks.append(nr)

    null_mean = float(np.mean(null_ranks)) if null_ranks else 0.0
    null_std = float(np.std(null_ranks)) if null_ranks else 0.0
    exceeds_null = rank > (null_mean + 2 * null_std) if null_ranks else False
    excess = rank - null_mean

    rec = {
        'domain_a': da,
        'domain_b': db,
        'bond_dim': rank,
        'excess_bond_dim': round(excess, 2),
        'mean_coupling': round(mean_coupling, 6),
        'top_5_svals': [round(float(s), 4) for s in svals[:5]],
        's1': round(s1, 4),
        'n_shared_dims': n_shared,
        'n_a': na,
        'n_b': nb,
        'null_bond_dim_mean': round(null_mean, 2),
        'null_bond_dim_std': round(null_std, 2),
        'exceeds_null': bool(exceeds_null),
    }
    ttcross_results.append(rec)

    if (pi + 1) % 25 == 0:
        elapsed = time.time() - t3
        print(f"  [{pi + 1}/{len(pairs)}] {elapsed:.1f}s")

# Sort by excess bond dimension
ttcross_results.sort(key=lambda r: (-r['excess_bond_dim'], -r['bond_dim']))

exceeds_count = sum(1 for r in ttcross_results if r['exceeds_null'])
print(f"\n  Sweep complete: {len(ttcross_results)} pairs in {time.time() - t3:.1f}s")
print(f"  Pairs exceeding null (2-sigma): {exceeds_count} ({100 * exceeds_count / max(len(ttcross_results), 1):.1f}%)")

print(f"\n  TOP 20 DOMAIN PAIRS (by excess bond dim over null):")
print(f"  {'Rank':<5} {'Domain A':<14} {'Domain B':<14} {'Bond':<6} {'Null':<8} {'Excess':<8} {'2sig?':<6} {'Shared':<7}")
print("  " + "-" * 70)
for i, r in enumerate(ttcross_results[:20]):
    print(f"  {i + 1:<5} {r['domain_a']:<14} {r['domain_b']:<14} "
          f"{r['bond_dim']:<6} {r['null_bond_dim_mean']:<8} "
          f"{r['excess_bond_dim']:<8} "
          f"{'YES' if r['exceeds_null'] else 'no':<6} "
          f"{r['n_shared_dims']:<7}")

print(f"  Step 3 complete: {time.time() - t3:.1f}s")


# ================================================================
# STEP 4: MAP-Elites on Megethos-zeroed tensor
# ================================================================
print("\n" + "=" * 80)
print("STEP 4: MAP-Elites on Megethos-zeroed tensor")
print("=" * 80)

t4 = time.time()

# Strategy groups to use (excluding zeroed ones)
ZEROED_GROUPS = {"disc_cond"}  # s13
# s7_cond is part of padic group -- we keep padic but it has s7_det, s7_disc still active
ME_GROUP_NAMES = [g for g in GROUP_NAMES if g not in ZEROED_GROUPS]
N_ME_GROUPS = len(ME_GROUP_NAMES)
N_BINS = 3

print(f"  MAP-Elites grid: {N_ME_GROUPS} groups x {N_BINS} bins each")
print(f"  Groups: {ME_GROUP_NAMES}")

# Compute group means for full tensor
print(f"  Computing group means for {N_OBJ} objects...")
gv_full, gvalid_full = compute_group_means(tensor, mask, group_slices)

# Discretize into bins (quantile-based)
obj_bins = torch.zeros(N_OBJ, N_ME_GROUPS, device=DEVICE, dtype=torch.long)
for gi, gname in enumerate(ME_GROUP_NAMES):
    gidx = GROUP_NAMES.index(gname)
    valid = gvalid_full[:, gidx]
    vals = gv_full[valid, gidx]
    if vals.numel() < 10:
        obj_bins[:, gi] = N_BINS  # absent
        continue
    quantiles = torch.linspace(0, 1, N_BINS + 1, device=DEVICE)
    edges = torch.quantile(vals, quantiles)
    bins = torch.bucketize(gv_full[:, gidx], edges[1:-1])
    obj_bins[:, gi] = bins
    obj_bins[~valid, gi] = N_BINS  # absent sentinel

# For cross-domain NN distance, sample aggressively
# Process in chunks of 10K objects
print(f"  Computing cross-domain nearest neighbors (sampled)...")
SAMPLE_PER_DOM_ME = 500
chunk_size = 10000

# Build reference set for neighbor search
ref_indices = []
for dom in all_domains:
    idx_list = domain_indices[dom]
    if len(idx_list) > SAMPLE_PER_DOM_ME:
        ref_indices.extend(rng.choice(idx_list, SAMPLE_PER_DOM_ME, replace=False).tolist())
    else:
        ref_indices.extend(idx_list)
ref_idx_t = torch.tensor(ref_indices, device=DEVICE, dtype=torch.long)
ref_tensor = tensor[ref_idx_t]
ref_mask = mask[ref_idx_t]
ref_domains = [domains[i] for i in ref_indices]
print(f"  Reference set: {len(ref_indices)} objects")

# We don't do full N_OBJ x ref NN search (too slow for 769K).
# Instead, sample 2000 objects per domain and find their cross-domain NN.
me_sample_per_dom = 2000
me_indices = []
for dom in all_domains:
    idx_list = domain_indices[dom]
    if len(idx_list) > me_sample_per_dom:
        me_indices.extend(rng.choice(idx_list, me_sample_per_dom, replace=False).tolist())
    else:
        me_indices.extend(idx_list)

me_indices = np.array(me_indices)
N_ME = len(me_indices)
print(f"  MAP-Elites sample: {N_ME} objects")

nn_dist_me = torch.full((N_ME,), float('inf'), device=DEVICE)
nn_idx_me = torch.zeros(N_ME, device=DEVICE, dtype=torch.long)

for c0 in range(0, N_ME, chunk_size):
    c1 = min(c0 + chunk_size, N_ME)
    chunk_real_idx = torch.tensor(me_indices[c0:c1], dtype=torch.long, device=DEVICE)
    chunk_t = tensor[chunk_real_idx]
    chunk_m = mask[chunk_real_idx]
    chunk_doms = [domains[me_indices[i]] for i in range(c0, c1)]

    # Batched distance to reference set
    Na = c1 - c0
    Nb = len(ref_indices)

    # Process in sub-batches to avoid OOM
    sub_batch = 2000
    for sb0 in range(0, Na, sub_batch):
        sb1 = min(sb0 + sub_batch, Na)
        q_t = chunk_t[sb0:sb1]
        q_m = chunk_m[sb0:sb1]

        # Cosine sim instead of Euclidean (faster, more meaningful)
        q_norm = F.normalize(q_t * q_m.float(), p=2, dim=1)
        r_norm = F.normalize(ref_tensor * ref_mask.float(), p=2, dim=1)
        sim = q_norm @ r_norm.T  # (sub_batch, Nb)
        dists = 1 - sim  # cosine distance

        # Mask out same-domain
        for qi in range(sb1 - sb0):
            qi_dom = chunk_doms[sb0 + qi]
            for ri, rd in enumerate(ref_domains):
                if rd == qi_dom:
                    dists[qi, ri] = float('inf')

            # Actually, vectorized same-domain masking
            # (the loop above is too slow for large Nb)
        # Redo same-domain masking vectorized
        # Build domain match mask
        qi_dom_list = chunk_doms[sb0:sb1]
        for qi in range(sb1 - sb0):
            dom_mask_vec = torch.tensor(
                [1.0 if ref_domains[ri] == qi_dom_list[qi] else 0.0
                 for ri in range(Nb)], device=DEVICE)
            dists[qi] += dom_mask_vec * 1e6

        min_d, min_j = dists.min(dim=1)
        global_qi = c0 + sb0
        for qi in range(sb1 - sb0):
            if min_d[qi] < nn_dist_me[global_qi + qi]:
                nn_dist_me[global_qi + qi] = min_d[qi]
                nn_idx_me[global_qi + qi] = ref_idx_t[min_j[qi]]

        del sim, dists, q_norm
        torch.cuda.empty_cache()

    if c1 % 20000 < chunk_size:
        print(f"    {c1}/{N_ME} processed")

# Build archive
print(f"  Building MAP-Elites archive...")
archive = {}
obj_bins_np = obj_bins.cpu().numpy()
nn_dist_np = nn_dist_me.cpu().numpy()

for qi in range(N_ME):
    real_idx = me_indices[qi]
    cell = tuple(obj_bins_np[real_idx, :N_ME_GROUPS].tolist())
    dist = nn_dist_np[qi]
    if np.isinf(dist) or dist > 1e5:
        continue
    if cell not in archive or dist < archive[cell]['quality']:
        archive[cell] = {
            'champion': labels[real_idx],
            'quality': float(dist),
            'domain': domains[real_idx],
            'nn_domain': domains[nn_idx_me[qi].item()],
            'group_profile': {
                ME_GROUP_NAMES[g]: int(obj_bins_np[real_idx, g])
                for g in range(N_ME_GROUPS)
            },
        }

n_cells = len(archive)
domain_counts_me = Counter(v['domain'] for v in archive.values())
cross_pairs_me = Counter(
    tuple(sorted([v['domain'], v['nn_domain']]))
    for v in archive.values()
)
best_entries = sorted(archive.values(), key=lambda x: x['quality'])[:20]

# Which groups are most represented in top-100 cells?
top_100 = sorted(archive.values(), key=lambda x: x['quality'])[:100]
group_repr = Counter()
for entry in top_100:
    for gname, bin_val in entry['group_profile'].items():
        if bin_val < N_BINS:
            group_repr[gname] += 1

print(f"\n  MAP-Elites complete: {time.time() - t4:.1f}s")
print(f"  Occupied cells: {n_cells}")
print(f"  Domain distribution:")
for dom, cnt in domain_counts_me.most_common():
    print(f"    {dom}: {cnt} cells")
print(f"  Top cross-domain convergence pairs:")
for pair, cnt in cross_pairs_me.most_common(10):
    print(f"    {pair[0]} <-> {pair[1]}: {cnt} cells")
print(f"  Strategy groups in top-100 cells (convergence drivers):")
for gname, cnt in group_repr.most_common():
    print(f"    {gname}: {cnt}/100")
print(f"  Top-10 champions (lowest cross-domain distance):")
for entry in best_entries[:10]:
    print(f"    {entry['champion']:35s} [{entry['domain']:>8s}]"
          f" -> [{entry['nn_domain']:>8s}]  d={entry['quality']:.4f}")

# Serialize archive
archive_json = {}
for cell, entry in archive.items():
    key = "_".join(str(b) for b in cell)
    archive_json[key] = entry

step4_results = {
    'n_cells': n_cells,
    'domain_distribution': dict(domain_counts_me),
    'top_cross_pairs': [{'a': p[0], 'b': p[1], 'count': c}
                        for p, c in cross_pairs_me.most_common(20)],
    'group_representation_top100': dict(group_repr),
    'top_20_champions': best_entries[:20],
    'archive_size': len(archive_json),
}
print(f"  Step 4 complete: {time.time() - t4:.1f}s")


# ================================================================
# STEP 5: Random walkers on Megethos-zeroed tensor
# ================================================================
print("\n" + "=" * 80)
print("STEP 5: Random walkers (27 walkers, one per domain)")
print("=" * 80)

t5 = time.time()
N_WALKERS = len(all_domains)  # one per domain
N_STEPS = 200
K_NEIGHBORS = 10

print(f"  Walkers: {N_WALKERS} (one per domain)")
print(f"  Steps: {N_STEPS}, K neighbors: {K_NEIGHBORS}")

# Initialize walkers
walkers = []
for dom in all_domains:
    seed = rng.choice(domain_indices[dom])
    walkers.append({
        'seed_domain': dom,
        'current_idx': seed,
        'trajectory': [],
        'visited_domains': Counter(),
        'domain_switches': 0,
    })

# Reference set already built above (ref_idx_t, ref_tensor, ref_mask, ref_domains)
# Rebuild reference with cosine-normalized vectors for speed
ref_norm = F.normalize(ref_tensor * ref_mask.float(), p=2, dim=1)

print(f"  Reference set: {len(ref_indices)} objects")
print(f"  Running walks...")

for step in range(N_STEPS):
    # Gather current positions
    walker_real_idx = [w['current_idx'] for w in walkers]
    walker_t = tensor[torch.tensor(walker_real_idx, dtype=torch.long, device=DEVICE)]
    walker_m = mask[torch.tensor(walker_real_idx, dtype=torch.long, device=DEVICE)]
    walker_norm = F.normalize(walker_t * walker_m.float(), p=2, dim=1)

    # Cosine distance to reference set
    sim = walker_norm @ ref_norm.T  # (N_WALKERS, Nref)
    dists = 1 - sim

    for wi, w in enumerate(walkers):
        curr_dom = domains[w['current_idx']]
        d_row = dists[wi]

        # Find K nearest
        k = min(K_NEIGHBORS, d_row.numel())
        vals, top_j = torch.topk(d_row, k, largest=False)

        # Score: prefer novel domain
        best_score = -float('inf')
        best_ref = None
        for ki in range(k):
            j = top_j[ki].item()
            nd = ref_domains[j]
            dist_val = vals[ki].item()
            if dist_val > 1e5:
                continue
            dom_novel = 0.0 if nd == curr_dom else 1.0
            visit_penalty = w['visited_domains'].get(nd, 0) / max(step + 1, 1)
            score = dom_novel - visit_penalty - 0.1 * dist_val
            if score > best_score:
                best_score = score
                best_ref = ref_indices[j]

        if best_ref is None:
            best_ref = w['current_idx']

        # Record
        prev_dom = domains[w['current_idx']]
        new_dom = domains[best_ref]
        if new_dom != prev_dom:
            w['domain_switches'] += 1

        w['trajectory'].append({
            'step': step,
            'obj': labels[w['current_idx']],
            'domain': prev_dom,
            'nn_dist': float(vals[0].item()) if vals.numel() > 0 else None,
        })
        w['visited_domains'][new_dom] += 1
        w['current_idx'] = best_ref

    if (step + 1) % 50 == 0:
        print(f"    Step {step + 1}/{N_STEPS}")

    del sim, dists
    torch.cuda.empty_cache()

# Analyze walkers
print(f"\n  Walk analysis:")
walker_results = []
connectivity_matrix = defaultdict(lambda: defaultdict(int))  # dom_a -> dom_b -> switches

for w in walkers:
    traj = w['trajectory']
    dom_sequence = [s['domain'] for s in traj]
    domains_visited = len(set(dom_sequence))
    dists_w = [s['nn_dist'] for s in traj
               if s['nn_dist'] is not None and s['nn_dist'] < 1e5]
    mean_dist = float(np.mean(dists_w)) if dists_w else None

    # Track domain-to-domain transitions
    for i in range(1, len(dom_sequence)):
        if dom_sequence[i] != dom_sequence[i - 1]:
            connectivity_matrix[dom_sequence[i - 1]][dom_sequence[i]] += 1

    print(f"  Walker from {w['seed_domain']:>12s}: "
          f"switches={w['domain_switches']:>3d}/{N_STEPS}, "
          f"domains_visited={domains_visited:>2d}, "
          f"mean_dist={mean_dist:.4f}" if mean_dist else
          f"  Walker from {w['seed_domain']:>12s}: "
          f"switches={w['domain_switches']:>3d}/{N_STEPS}, "
          f"domains_visited={domains_visited:>2d}, "
          f"mean_dist=inf")

    walker_results.append({
        'seed_domain': w['seed_domain'],
        'domain_switches': w['domain_switches'],
        'domains_visited': domains_visited,
        'mean_nn_dist': mean_dist,
        'visited_counts': dict(w['visited_domains']),
        # Don't serialize full trajectory to keep JSON manageable
        'trajectory_summary': {
            'start_domain': dom_sequence[0] if dom_sequence else None,
            'end_domain': dom_sequence[-1] if dom_sequence else None,
            'unique_domains': sorted(set(dom_sequence)),
        }
    })

# Domain connectivity summary
print(f"\n  Domain connectivity (total switches):")
conn_summary = Counter()
for d1 in connectivity_matrix:
    for d2 in connectivity_matrix[d1]:
        key = tuple(sorted([d1, d2]))
        conn_summary[key] += connectivity_matrix[d1][d2]

# Domains that connect
connected_domains = set()
isolated_domains = set(all_domains)
for (d1, d2), cnt in conn_summary.most_common(20):
    print(f"    {d1} <-> {d2}: {cnt} transitions")
    connected_domains.add(d1)
    connected_domains.add(d2)
    isolated_domains.discard(d1)
    isolated_domains.discard(d2)

# Which domains are walkers NOT switching into?
print(f"\n  Isolated domains (never reached by cross-domain walk):")
for dom in sorted(isolated_domains):
    print(f"    {dom}")

step5_results = {
    'walkers': walker_results,
    'connectivity': [{'a': d1, 'b': d2, 'transitions': cnt}
                     for (d1, d2), cnt in conn_summary.most_common(30)],
    'connected_domains': sorted(connected_domains),
    'isolated_domains': sorted(isolated_domains),
}
print(f"  Step 5 complete: {time.time() - t5:.1f}s")


# ================================================================
# STEP 6: Summary
# ================================================================
print("\n" + "=" * 80)
print("STEP 6: SUMMARY — Honest findings")
print("=" * 80)

t6 = time.time()

# How many domain pairs have genuine coupling beyond magnitude?
genuine_pairs = [r for r in ttcross_results if r['exceeds_null']]
print(f"\n  1. GENUINE COUPLINGS (bond dim > null at 2-sigma): {len(genuine_pairs)} / {len(ttcross_results)}")
for r in genuine_pairs[:15]:
    print(f"     {r['domain_a']:<14} <-> {r['domain_b']:<14}  "
          f"bond={r['bond_dim']}, null={r['null_bond_dim_mean']:.1f}+/-{r['null_bond_dim_std']:.1f}, "
          f"shared_dims={r['n_shared_dims']}")

# Which strategy groups drive those couplings?
# Look at which groups have data for the genuine pairs
print(f"\n  2. STRATEGY GROUPS DRIVING GENUINE COUPLINGS:")
if group_repr:
    for gname, cnt in group_repr.most_common(10):
        print(f"     {gname}: appears in {cnt}/100 top MAP-Elites cells")

# Surviving correlations
surviving_corr = [(ga, gb, rz, ro) for ga, gb, rz, ro in corr_pairs
                  if abs(rz) > 0.1]
print(f"\n  3. SURVIVING GROUP CORRELATIONS (|r| > 0.1 after zeroing): {len(surviving_corr)}")
for ga, gb, rz, ro in surviving_corr[:10]:
    print(f"     {ga} <-> {gb}: r={rz:+.4f} (was {ro:+.4f})")

# Cross-domain signals
print(f"\n  4. CROSS-DOMAIN SIGNALS:")
print(f"     MAP-Elites occupied cells: {n_cells}")
print(f"     Connected domains (random walk): {len(connected_domains)}/{len(all_domains)}")
print(f"     Isolated domains: {sorted(isolated_domains)}")
print(f"     Top convergence pair: "
      f"{cross_pairs_me.most_common(1)[0] if cross_pairs_me else 'none'}")

# What to explore next
print(f"\n  5. RECOMMENDATIONS:")
if len(genuine_pairs) == 0:
    print(f"     - ZERO genuine couplings survive Megethos zeroing.")
    print(f"     - The tensor may contain no cross-domain structure beyond magnitude.")
    print(f"     - Consider: is the representation right, or is absence the finding?")
elif len(genuine_pairs) <= 5:
    print(f"     - Only {len(genuine_pairs)} pairs survive. Focus on THOSE pairs.")
    for r in genuine_pairs:
        print(f"       * {r['domain_a']} <-> {r['domain_b']}: drill into shared dims")
    print(f"     - Run targeted per-dimension ablation on survivors")
else:
    print(f"     - {len(genuine_pairs)} pairs survive. Check for shared confound.")
    print(f"     - Run partial-correlation controlling for top group")

total_time = time.time() - T_GLOBAL
print(f"\n  Total runtime: {total_time:.1f}s ({total_time / 60:.1f} minutes)")
print(f"  Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")


# ================================================================
# Save all results
# ================================================================
out_path = DATA_DIR / "aletheia_night_sweep.json"
output = {
    'metadata': {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'device': str(DEVICE),
        'n_objects': N_OBJ,
        'n_dims': N_DIM,
        'active_dims_after_zeroing': active_dims,
        'n_domains': len(all_domains),
        'n_valid_domains': len(valid_domains),
        'zeroed_strategies': ['s13', 's7_cond'],
        'total_runtime_seconds': round(total_time, 1),
    },
    'step2_correlations': step2_results,
    'step3_ttcross': {
        'n_pairs': len(ttcross_results),
        'n_exceeds_null': exceeds_count,
        'results': ttcross_results,
    },
    'step4_map_elites': step4_results,
    'step5_random_walk': step5_results,
    'summary': {
        'genuine_coupling_pairs': len(genuine_pairs),
        'genuine_pairs': [{'a': r['domain_a'], 'b': r['domain_b'],
                           'bond_dim': r['bond_dim'],
                           'null_mean': r['null_bond_dim_mean'],
                           'excess': r['excess_bond_dim']}
                          for r in genuine_pairs],
        'surviving_correlations': [{'a': ga, 'b': gb, 'r': round(rz, 4)}
                                   for ga, gb, rz, ro in surviving_corr],
        'connected_domains': sorted(connected_domains),
        'isolated_domains': sorted(isolated_domains),
        'map_elites_cells': n_cells,
    }
}

with open(out_path, 'w') as f:
    json.dump(output, f, indent=2, default=str)
print(f"\n  Results saved to {out_path}")
print(f"\n[Aletheia Night Sweep] DONE.")
