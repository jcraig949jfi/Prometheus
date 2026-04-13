"""
TT-Cross Bond Dimension Sweep — Megethos Zeroed

For each domain pair with >=100 objects each:
1. Sample up to 1000 objects per domain
2. Zero out s13 (Megethos/magnitude) dimensions (cols 129-133)
3. Build coupling matrix C[i,j] = cosine_sim(A_i, B_j) using only
   dimensions where BOTH objects have data (via mask)
4. SVD of C -> effective rank = # singular values > 1% of s_1
5. Compare to null (shuffled domain labels, 10 permutations)

The surviving metric from the adversarial session. Everything else is dead.
"""

import json
import time
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from collections import Counter
from itertools import combinations

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {DEVICE}")

# ── Load tensor ──────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parents[2] / "convergence" / "data"
t = torch.load(DATA_DIR / "dissection_tensor.pt", weights_only=False)

tensor = t['tensor'].to(DEVICE)   # (601033, 182)
mask = t['mask'].to(DEVICE)       # (601033, 182)
domains = t['domains']            # list of str
labels = t['labels']
strategy_slices = t['strategy_slices']

N_OBJ, N_DIM = tensor.shape
print(f"Tensor: {N_OBJ} objects x {N_DIM} dims")

# ── Zero out s13 (Megethos) ──────────────────────────────────
s13_start, s13_end = strategy_slices['s13']
print(f"Zeroing s13 (Megethos): dims {s13_start}:{s13_end}")
tensor[:, s13_start:s13_end] = 0.0
mask[:, s13_start:s13_end] = False

# ── Build domain index ───────────────────────────────────────
domain_counts = Counter(domains)
domain_indices = {}
for i, d in enumerate(domains):
    domain_indices.setdefault(d, []).append(i)

# Filter domains with >= 100 objects
valid_domains = sorted([d for d, c in domain_counts.items() if c >= 100])
print(f"Valid domains (>=100 objects): {len(valid_domains)}")
for d in valid_domains:
    print(f"  {d}: {domain_counts[d]}")

# ── Sampling ─────────────────────────────────────────────────
MAX_SAMPLE = 1000
rng = np.random.RandomState(42)

domain_samples = {}
for d in valid_domains:
    idx = np.array(domain_indices[d])
    if len(idx) > MAX_SAMPLE:
        idx = rng.choice(idx, MAX_SAMPLE, replace=False)
    domain_samples[d] = idx


def compute_coupling_matrix(idx_a, idx_b):
    """
    Build coupling matrix C[i,j] = cosine_sim(A_i, B_j)
    using only dims where BOTH have data.
    Returns C on CPU as numpy.
    """
    vecs_a = tensor[idx_a]  # (na, 182)
    vecs_b = tensor[idx_b]  # (nb, 182)
    mask_a = mask[idx_a]    # (na, 182)
    mask_b = mask[idx_b]    # (nb, 182)

    # For each pair (i,j), the valid dims are mask_a[i] & mask_b[j].
    # Computing per-pair masks for all pairs is expensive.
    # Approximation: use dims where ANY object in A has data AND ANY in B has data.
    # This is the union of active dims for the domain pair.
    shared_dims = mask_a.any(dim=0) & mask_b.any(dim=0)  # (182,)
    n_shared = shared_dims.sum().item()

    if n_shared < 3:
        return None, 0

    # Zero out non-shared dims and compute cosine sim on shared subset
    va = vecs_a[:, shared_dims]  # (na, n_shared)
    vb = vecs_b[:, shared_dims]  # (nb, n_shared)
    ma = mask_a[:, shared_dims]  # (na, n_shared)
    mb = mask_b[:, shared_dims]  # (nb, n_shared)

    # Zero out individually missing values
    va = va * ma.float()
    vb = vb * mb.float()

    # Normalize each vector
    va_norm = F.normalize(va, p=2, dim=1)  # (na, n_shared)
    vb_norm = F.normalize(vb, p=2, dim=1)  # (nb, n_shared)

    # Coupling matrix
    C = va_norm @ vb_norm.T  # (na, nb)
    return C, n_shared


def effective_rank(C, threshold=0.01):
    """Effective rank = # singular values > threshold * s_1."""
    # SVD on GPU
    U, S, Vh = torch.linalg.svd(C, full_matrices=False)
    s1 = S[0].item()
    if s1 < 1e-12:
        return 0, 0.0, S.cpu().numpy()
    cutoff = threshold * s1
    rank = (S > cutoff).sum().item()
    return rank, s1, S.cpu().numpy()


# ── Main sweep ───────────────────────────────────────────────
pairs = list(combinations(valid_domains, 2))
print(f"\nTotal domain pairs: {len(pairs)}")
print("Running sweep...\n")

results = []
t0 = time.time()
N_NULL = 10

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

    # Null: shuffle domain labels (merge both pools, resplit)
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

    rec = {
        'domain_a': da,
        'domain_b': db,
        'bond_dim': rank,
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
    results.append(rec)

    if (pi + 1) % 20 == 0:
        elapsed = time.time() - t0
        print(f"  [{pi+1}/{len(pairs)}] {elapsed:.1f}s")

elapsed = time.time() - t0
print(f"\nSweep complete: {len(results)} pairs in {elapsed:.1f}s")

# ── Sort by bond dimension ───────────────────────────────────
results.sort(key=lambda r: (-r['bond_dim'], -r['mean_coupling']))

# ── Save ─────────────────────────────────────────────────────
out_path = DATA_DIR / "ttcross_megethos_zeroed_sweep.json"
with open(out_path, 'w') as f:
    json.dump({
        'metadata': {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'device': str(DEVICE),
            'n_objects': N_OBJ,
            'n_dims': N_DIM,
            's13_zeroed': [s13_start, s13_end],
            'max_sample': MAX_SAMPLE,
            'n_null_permutations': N_NULL,
            'threshold': 0.01,
            'n_valid_domains': len(valid_domains),
            'n_pairs_computed': len(results),
            'elapsed_seconds': round(elapsed, 1),
        },
        'results': results,
    }, f, indent=2)
print(f"\nSaved to {out_path}")

# ── Report ───────────────────────────────────────────────────
print("\n" + "=" * 80)
print("TOP 20 DOMAIN PAIRS BY BOND DIMENSION (Megethos zeroed)")
print("=" * 80)
print(f"{'Rank':<5} {'Domain A':<12} {'Domain B':<12} {'Bond':<6} {'Null':<8} {'Exceeds':<8} {'MeanCoup':<10} {'SharedD':<8} {'s1':<8}")
print("-" * 80)
for i, r in enumerate(results[:20]):
    print(f"{i+1:<5} {r['domain_a']:<12} {r['domain_b']:<12} "
          f"{r['bond_dim']:<6} {r['null_bond_dim_mean']:<8} "
          f"{'YES' if r['exceeds_null'] else 'no':<8} "
          f"{r['mean_coupling']:<10} {r['n_shared_dims']:<8} {r['s1']:<8}")

# ── Summary stats ────────────────────────────────────────────
exceeds_count = sum(1 for r in results if r['exceeds_null'])
print(f"\n--- SUMMARY ---")
print(f"Total pairs computed: {len(results)}")
print(f"Pairs exceeding null (2-sigma): {exceeds_count} ({100*exceeds_count/max(len(results),1):.1f}%)")
print(f"Max bond dim: {results[0]['bond_dim'] if results else 'N/A'}")
print(f"Median bond dim: {results[len(results)//2]['bond_dim'] if results else 'N/A'}")

# Bond dim distribution
from collections import Counter as Ctr
bd_dist = Ctr(r['bond_dim'] for r in results)
print(f"\nBond dimension distribution:")
for bd in sorted(bd_dist.keys()):
    print(f"  bond_dim={bd}: {bd_dist[bd]} pairs")
