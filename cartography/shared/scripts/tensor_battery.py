"""
Tensor Battery — GPU-native falsification tests on the dissection tensor.

Runs F24 (eta²), F25 (transportability), F1 (permutation null), and
rotation invariance directly as tensor operations on GPU. No CPU loops.

Built to test the Megethos claim: log-magnitude is a universal axis
accounting for 44% of cross-domain structure, transportable from
arithmetic domains (EC, MF, NF) to geometric domains (knots, polytopes).
"""
import sys
import json
import time
import torch
import numpy as np
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[3]
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def load_tensor():
    """Load the dissection tensor."""
    path = ROOT / "cartography/convergence/data/dissection_tensor.pt"
    data = torch.load(path, map_location='cpu', weights_only=False)
    data['tensor'] = data['tensor'].to(DEVICE)
    data['mask'] = data['mask'].to(DEVICE)

    # Build domain index
    domain_set = sorted(set(data['domains']))
    domain_to_idx = {d: i for i, d in enumerate(domain_set)}
    domain_ids = torch.tensor([domain_to_idx[d] for d in data['domains']],
                              device=DEVICE, dtype=torch.long)
    data['domain_ids'] = domain_ids
    data['domain_names'] = domain_set
    data['domain_to_idx'] = domain_to_idx
    return data


# ============================================================
# GPU-native F24: Variance Decomposition (eta²)
# ============================================================
def f24_eta_squared_gpu(values, group_labels, min_group_size=5):
    """Compute eta² (variance decomposition) entirely on GPU.

    eta² = SS_between / SS_total
    where SS_between = sum(n_k * (mean_k - grand_mean)²)
          SS_total = sum((x_i - grand_mean)²)

    Args:
        values: [N] tensor of values
        group_labels: [N] tensor of integer group IDs

    Returns: dict with eta_squared, f_statistic, per-group stats
    """
    valid = torch.isfinite(values)
    values = values[valid]
    group_labels = group_labels[valid]

    N = values.shape[0]
    grand_mean = values.mean()
    ss_total = ((values - grand_mean) ** 2).sum()

    unique_groups = group_labels.unique()
    k = len(unique_groups)

    ss_between = torch.tensor(0.0, device=DEVICE)
    group_stats = {}

    for g in unique_groups:
        mask = group_labels == g
        n_g = mask.sum()
        if n_g < min_group_size:
            continue
        mean_g = values[mask].mean()
        ss_between += n_g * (mean_g - grand_mean) ** 2
        group_stats[int(g)] = {
            "n": int(n_g),
            "mean": float(mean_g),
            "std": float(values[mask].std()) if n_g > 1 else 0.0,
        }

    eta_sq = float(ss_between / ss_total) if ss_total > 0 else 0.0

    # F-statistic
    df_between = len(group_stats) - 1
    df_within = N - len(group_stats)
    if df_between > 0 and df_within > 0:
        ms_between = float(ss_between) / df_between
        ms_within = float(ss_total - ss_between) / df_within
        f_stat = ms_between / max(ms_within, 1e-12)
    else:
        f_stat = 0.0

    # Classify
    if eta_sq >= 0.14:
        verdict = "STRONG_EFFECT"
    elif eta_sq >= 0.06:
        verdict = "MODERATE_EFFECT"
    elif eta_sq >= 0.01:
        verdict = "SMALL_EFFECT"
    else:
        verdict = "NEGLIGIBLE_EFFECT"

    return {
        "verdict": verdict,
        "eta_squared": eta_sq,
        "f_statistic": f_stat,
        "n": int(N),
        "n_groups": len(group_stats),
        "ss_between": float(ss_between),
        "ss_total": float(ss_total),
        "group_stats": group_stats,
    }


# ============================================================
# GPU-native F25: Transportability (leave-one-group-out)
# ============================================================
def f25_transportability_gpu(values, primary_labels, secondary_labels,
                              min_test_n=10):
    """Leave-one-group-out transportability test on GPU.

    For each primary group: train a mean-predictor on all OTHER groups,
    test on this group. OOS R² > 0 = transportable.

    Args:
        values: [N] tensor
        primary_labels: [N] tensor of integer group IDs (domains)
        secondary_labels: [N] tensor of secondary grouping (for stratification)

    Returns: dict with weighted OOS R², per-group results
    """
    valid = torch.isfinite(values)
    values = values[valid]
    primary_labels = primary_labels[valid]
    secondary_labels = secondary_labels[valid]

    unique_primary = primary_labels.unique()
    results = {}
    weighted_r2_sum = 0.0
    weight_sum = 0.0

    for g in unique_primary:
        test_mask = primary_labels == g
        train_mask = ~test_mask
        n_test = test_mask.sum().item()
        n_train = train_mask.sum().item()

        if n_test < min_test_n or n_train < min_test_n:
            continue

        # Train: predict using mean of training set, stratified by secondary
        train_vals = values[train_mask]
        test_vals = values[test_mask]
        test_secondary = secondary_labels[test_mask]

        # Simple model: predict test values using train grand mean
        train_mean = train_vals.mean()
        predictions = torch.full_like(test_vals, train_mean)

        # Also try: predict using secondary-group means from training
        train_secondary = secondary_labels[train_mask]
        for sg in test_secondary.unique():
            sg_train_mask = train_secondary == sg
            sg_test_mask = test_secondary == sg
            if sg_train_mask.sum() >= 3:
                predictions[sg_test_mask] = train_vals[sg_train_mask].mean()

        # OOS R²
        ss_res = ((test_vals - predictions) ** 2).sum()
        ss_tot = ((test_vals - test_vals.mean()) ** 2).sum()
        oos_r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

        results[int(g)] = {"n_test": n_test, "oos_r2": oos_r2}
        weighted_r2_sum += oos_r2 * n_test
        weight_sum += n_test

    weighted_r2 = weighted_r2_sum / max(weight_sum, 1) if weight_sum > 0 else 0.0

    if weighted_r2 > 0.15:
        verdict = "UNIVERSAL"
    elif weighted_r2 > 0:
        verdict = "CONTEXT_DEPENDENT"
    else:
        verdict = "NOT_TRANSPORTABLE"

    return {
        "verdict": verdict,
        "weighted_oos_r2": weighted_r2,
        "per_group": results,
    }


# ============================================================
# GPU-native F1: Permutation null
# ============================================================
def f1_permutation_null_gpu(values, group_labels, n_perm=10000):
    """GPU-parallel permutation test for eta².

    Shuffles group labels n_perm times ON GPU, computes eta² each time.
    p-value = fraction of permuted eta² >= real eta².

    This is massively parallel: all permutations run simultaneously.
    """
    valid = torch.isfinite(values)
    values = values[valid]
    group_labels = group_labels[valid]
    N = values.shape[0]

    # Real eta²
    real_result = f24_eta_squared_gpu(values, group_labels)
    real_eta = real_result["eta_squared"]

    # Grand mean and SS_total (constant across permutations)
    grand_mean = values.mean()
    ss_total = ((values - grand_mean) ** 2).sum()

    if ss_total == 0:
        return {"p_value": 1.0, "z_score": 0.0, "real_eta2": real_eta,
                "null_mean_eta2": 0.0, "verdict": "KILLED"}

    # Generate all permutations at once: [n_perm, N] index arrays
    # For memory: batch if N * n_perm > 1e9
    batch_size = max(1, min(n_perm, int(5e8 / N)))
    null_etas = []

    for start in range(0, n_perm, batch_size):
        end = min(start + batch_size, n_perm)
        n_batch = end - start

        # Permute labels: generate random indices
        perm_indices = torch.stack([torch.randperm(N, device=DEVICE)
                                    for _ in range(n_batch)])  # [batch, N]
        perm_labels = group_labels[perm_indices]  # [batch, N]

        # Compute SS_between for each permutation
        unique_groups = group_labels.unique()
        ss_between_batch = torch.zeros(n_batch, device=DEVICE)

        for g in unique_groups:
            # For each permutation, find which values got this label
            mask = perm_labels == g  # [batch, N]
            n_g = mask.float().sum(dim=1)  # [batch]
            # Sum of values with this label
            masked_vals = values.unsqueeze(0) * mask.float()  # [batch, N]
            sum_g = masked_vals.sum(dim=1)  # [batch]
            mean_g = sum_g / n_g.clamp(min=1)  # [batch]
            ss_between_batch += n_g * (mean_g - grand_mean) ** 2

        null_eta_batch = ss_between_batch / ss_total  # [batch]
        null_etas.append(null_eta_batch)

        del perm_indices, perm_labels, ss_between_batch
        torch.cuda.empty_cache()

    null_etas = torch.cat(null_etas)
    null_mean = float(null_etas.mean())
    null_std = float(null_etas.std())

    p_value = float((null_etas >= real_eta).sum() + 1) / (n_perm + 1)
    z_score = (real_eta - null_mean) / max(null_std, 1e-12)

    verdict = "SURVIVES" if p_value < 0.001 else "KILLED"

    return {
        "verdict": verdict,
        "p_value": p_value,
        "z_score": z_score,
        "real_eta2": real_eta,
        "null_mean_eta2": null_mean,
        "null_std_eta2": null_std,
        "n_permutations": n_perm,
    }


# ============================================================
# GPU-native rotation invariance test for a specific axis
# ============================================================
def rotation_invariance_gpu(tensor, mask, axis_values, n_rotations=100):
    """Test if an axis's relationship to the tensor survives random rotation.

    Computes correlation between axis_values and each tensor dimension,
    then checks if those correlations survive random orthogonal rotations.
    """
    N, D = tensor.shape
    valid = torch.isfinite(axis_values)
    axis = axis_values[valid]
    t = tensor[valid]
    m = mask[valid]

    # Original correlations: axis vs each dim
    axis_centered = axis - axis.mean()
    axis_std = axis.std().clamp(min=1e-8)

    orig_corrs = []
    for d in range(D):
        col = t[:, d]
        col_valid = m[:, d]
        if col_valid.sum() < 30:
            orig_corrs.append(0.0)
            continue
        v = col[col_valid]
        a = axis_centered[col_valid]
        r = (a * (v - v.mean())).sum() / (a.std() * v.std() * len(v)).clamp(min=1e-8)
        orig_corrs.append(float(r))

    orig_corrs = torch.tensor(orig_corrs, device=DEVICE)
    orig_norm = orig_corrs.norm()

    # Random rotations
    changes = []
    for _ in range(n_rotations):
        # Random orthogonal matrix via QR
        Q, _ = torch.linalg.qr(torch.randn(D, D, device=DEVICE))
        rotated = t @ Q
        rotated_mask = m  # mask structure unchanged

        rot_corrs = []
        for d in range(min(D, 30)):  # sample 30 dims for speed
            col = rotated[:, d]
            col_valid = rotated_mask[:, d]
            if col_valid.sum() < 30:
                rot_corrs.append(0.0)
                continue
            v = col[col_valid]
            a = axis_centered[col_valid]
            r = (a * (v - v.mean())).sum() / (a.std() * v.std() * len(v)).clamp(min=1e-8)
            rot_corrs.append(float(r))

        rot_corrs = torch.tensor(rot_corrs, device=DEVICE)
        change = (orig_corrs[:30] - rot_corrs).norm() / orig_corrs[:30].norm().clamp(min=1e-8)
        changes.append(float(change))

    mean_change = np.mean(changes)
    verdict = "ROTATION_INVARIANT" if mean_change < 0.5 else "COORDINATE_DEPENDENT"

    return {
        "verdict": verdict,
        "mean_fractional_change": mean_change,
        "std_change": float(np.std(changes)),
        "n_rotations": n_rotations,
    }


# ============================================================
# Megethos extractor: compute the universal magnitude axis
# ============================================================
def extract_megethos(data):
    """Extract Megethos (log-magnitude) for every object in the tensor.

    For each domain, Megethos = log of the natural size metric:
      EC:       log(conductor)
      MF:       log(level)
      NF:       log(|discriminant|)
      genus2:   log(conductor)
      knot:     log(crossing_number)
      lattice:  log(determinant)
      group:    log(order)
      maass:    log(level)
      OEIS:     log(max term magnitude)
      Lzeros:   log(conductor)
      obj_zeros: log(analytic_rank + 1) [weak proxy]
      fungrim:  log(n_symbols)

    Returns: [N] tensor of Megethos values (NaN where not computable)
    """
    tensor = data['tensor']
    mask = data['mask']
    slices = data['strategy_slices']
    N = tensor.shape[0]

    megethos = torch.full((N,), float('nan'), device=DEVICE)

    # s13 (disc_cond) dim 0 = log1p(|disc or conductor|) — already encoded!
    # After normalization it's z-scored, but the RELATIVE ordering is preserved.
    s13_start = slices['s13'][0]
    s13_mask = mask[:, s13_start]
    megethos[s13_mask] = tensor[s13_mask, s13_start]

    # For objects without s13, try s7_cond dim 0 (log of p-adic content)
    s7_start = slices['s7_cond'][0]
    s7_mask = mask[:, s7_start] & ~s13_mask  # only fill where s13 is missing
    megethos[s7_mask] = tensor[s7_mask, s7_start]

    print(f"  Megethos computed: {torch.isfinite(megethos).sum().item()}/{N} "
          f"({torch.isfinite(megethos).sum().item()/N*100:.1f}%)")
    return megethos


# ============================================================
# Main: Test the Megethos claim
# ============================================================
def test_megethos():
    print(f"Device: {DEVICE}")
    if DEVICE.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Load
    print("\nLoading tensor...", flush=True)
    data = load_tensor()
    tensor = data['tensor']
    mask = data['mask']
    domain_ids = data['domain_ids']
    domain_names = data['domain_names']
    N, D = tensor.shape
    print(f"  {N} objects x {D} dims, {len(domain_names)} domains")

    # Extract Megethos
    print("\nExtracting Megethos axis...", flush=True)
    megethos = extract_megethos(data)

    # ============================================================
    # TEST 1: F24 — Does Megethos vary by domain? (eta²)
    # ============================================================
    print(f"\n{'='*60}")
    print("F24: Megethos variance decomposition by domain")
    print(f"{'='*60}")
    t0 = time.time()
    f24 = f24_eta_squared_gpu(megethos, domain_ids)
    print(f"  eta² = {f24['eta_squared']:.4f}")
    print(f"  F = {f24['f_statistic']:.1f}")
    print(f"  Verdict: {f24['verdict']}")
    print(f"  Prediction: eta² > 0.40 (44% of variance)")
    print(f"  Result: {'CONFIRMED' if f24['eta_squared'] > 0.40 else 'REFUTED' if f24['eta_squared'] < 0.14 else 'PARTIAL'}")
    for gid, stats in sorted(f24['group_stats'].items()):
        dname = domain_names[gid] if gid < len(domain_names) else f"domain_{gid}"
        print(f"    {dname:12s}: n={stats['n']:6d}, mean={stats['mean']:+.3f}, std={stats['std']:.3f}")
    print(f"  [{time.time()-t0:.1f}s]")

    # ============================================================
    # TEST 2: F25 — Does Megethos transport across domains?
    # ============================================================
    print(f"\n{'='*60}")
    print("F25: Megethos transportability (arithmetic -> geometric)")
    print(f"{'='*60}")
    t0 = time.time()

    # Primary: domain. Secondary: crude magnitude bin.
    valid_meg = torch.isfinite(megethos)
    meg_valid = megethos[valid_meg]
    # Create secondary labels: quartile bins of megethos itself
    quartiles = torch.quantile(meg_valid, torch.tensor([0.25, 0.5, 0.75], device=DEVICE))
    secondary = torch.zeros(N, device=DEVICE, dtype=torch.long)
    secondary[valid_meg] = torch.bucketize(meg_valid, quartiles)

    f25 = f25_transportability_gpu(megethos, domain_ids, secondary)
    print(f"  Weighted OOS R² = {f25['weighted_oos_r2']:.4f}")
    print(f"  Verdict: {f25['verdict']}")
    print(f"  Per-domain OOS R²:")
    for gid, stats in sorted(f25['per_group'].items()):
        dname = domain_names[gid] if gid < len(domain_names) else f"domain_{gid}"
        print(f"    {dname:12s}: OOS R² = {stats['oos_r2']:+.4f} (n={stats['n_test']})")
    print(f"  [{time.time()-t0:.1f}s]")

    # ============================================================
    # TEST 3: F1 — Permutation null (is Megethos domain-structure real?)
    # ============================================================
    print(f"\n{'='*60}")
    print("F1: Permutation null (10K shuffles on GPU)")
    print(f"{'='*60}")
    t0 = time.time()

    # Subsample for speed
    n_sample = min(50000, N)
    idx = torch.randperm(N, device=DEVICE)[:n_sample]
    f1 = f1_permutation_null_gpu(megethos[idx], domain_ids[idx], n_perm=10000)
    print(f"  Real eta² = {f1['real_eta2']:.4f}")
    print(f"  Null mean eta² = {f1['null_mean_eta2']:.6f}")
    print(f"  z-score = {f1['z_score']:.1f}")
    print(f"  p-value = {f1['p_value']:.6f}")
    print(f"  Verdict: {f1['verdict']}")
    print(f"  [{time.time()-t0:.1f}s]")

    # ============================================================
    # TEST 4: Rotation invariance of Megethos axis
    # ============================================================
    print(f"\n{'='*60}")
    print("Rotation invariance of Megethos axis")
    print(f"{'='*60}")
    t0 = time.time()

    # Subsample for rotation test
    idx = torch.randperm(N, device=DEVICE)[:20000]
    rot = rotation_invariance_gpu(tensor[idx], mask[idx], megethos[idx], n_rotations=50)
    print(f"  Mean fractional change: {rot['mean_fractional_change']:.3f}")
    print(f"  Verdict: {rot['verdict']}")
    print(f"  [{time.time()-t0:.1f}s]")

    # ============================================================
    # TEST 5: Arithmetic -> Geometric transport (specific test)
    # ============================================================
    print(f"\n{'='*60}")
    print("F25-specific: Train on arithmetic, test on geometric")
    print(f"{'='*60}")
    t0 = time.time()

    arithmetic_domains = {'EC', 'MF', 'NF', 'Lzeros', 'obj_zeros', 'maass'}
    geometric_domains = {'knot', 'lattice', 'group', 'genus2'}

    arith_mask = torch.zeros(N, dtype=torch.bool, device=DEVICE)
    geo_mask = torch.zeros(N, dtype=torch.bool, device=DEVICE)
    for i, d in enumerate(data['domains']):
        if d in arithmetic_domains:
            arith_mask[i] = True
        elif d in geometric_domains:
            geo_mask[i] = True

    valid_arith = arith_mask & torch.isfinite(megethos)
    valid_geo = geo_mask & torch.isfinite(megethos)

    train_vals = megethos[valid_arith]
    test_vals = megethos[valid_geo]
    train_mean = train_vals.mean()

    # OOS R²: predict geometric Megethos using arithmetic mean
    ss_res = ((test_vals - train_mean) ** 2).sum()
    ss_tot = ((test_vals - test_vals.mean()) ** 2).sum()
    oos_r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

    print(f"  Arithmetic domains: {valid_arith.sum().item()} objects, mean Megethos = {train_mean:.3f}")
    print(f"  Geometric domains: {valid_geo.sum().item()} objects, mean Megethos = {test_vals.mean():.3f}")
    print(f"  OOS R² (arith->geo) = {oos_r2:.4f}")
    print(f"  Verdict: {'TRANSPORTABLE' if oos_r2 > 0 else 'NOT_TRANSPORTABLE'}")

    # Per geometric domain
    for d in sorted(geometric_domains):
        d_idx = data['domain_to_idx'].get(d)
        if d_idx is None:
            continue
        d_mask = (domain_ids == d_idx) & torch.isfinite(megethos)
        if d_mask.sum() < 10:
            continue
        d_vals = megethos[d_mask]
        ss_res_d = ((d_vals - train_mean) ** 2).sum()
        ss_tot_d = ((d_vals - d_vals.mean()) ** 2).sum()
        r2_d = float(1 - ss_res_d / ss_tot_d) if ss_tot_d > 0 else 0.0
        print(f"    {d:12s}: OOS R² = {r2_d:+.4f} (n={d_mask.sum().item()}, "
              f"mean={d_vals.mean():.3f})")
    print(f"  [{time.time()-t0:.1f}s]")

    # ============================================================
    # CLASSIFICATION
    # ============================================================
    print(f"\n{'='*60}")
    print("MEGETHOS CLASSIFICATION")
    print(f"{'='*60}")

    results = {
        "claim": "Megethos (log-magnitude) is a universal axis accounting for 44% of cross-domain structure",
        "f24": f24,
        "f25": f25,
        "f1": f1,
        "rotation": rot,
        "arithmetic_to_geometric_r2": oos_r2,
    }

    print(f"  F24 eta²:           {f24['eta_squared']:.4f} (prediction: >0.40)")
    print(f"  F25 OOS R²:         {f25['weighted_oos_r2']:.4f}")
    print(f"  F1 permutation:     p={f1['p_value']:.6f}, z={f1['z_score']:.1f}")
    print(f"  Rotation invariance: {rot['verdict']} ({rot['mean_fractional_change']:.3f})")
    print(f"  Arith->Geo R²:     {oos_r2:.4f}")

    if f24['eta_squared'] > 0.40 and f1['p_value'] < 0.001 and oos_r2 > 0:
        classification = "CONFIRMED: Universal axis, transportable, significant"
    elif f24['eta_squared'] > 0.14 and f1['p_value'] < 0.001:
        classification = "PARTIAL: Strong effect, significant, but weaker than 44% claim"
    elif f1['p_value'] < 0.001:
        classification = "REAL BUT WEAK: Statistically significant but small effect"
    else:
        classification = "KILLED: Not significant"

    print(f"\n  >>> {classification} <<<")
    results["classification"] = classification

    # Save
    out = ROOT / "cartography/convergence/data/megethos_battery_results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out.name}")

    return results


if __name__ == "__main__":
    test_megethos()
