#!/usr/bin/env python3
"""
kill_ec_maass.py — F33-F38 adversarial tests on the EC-maass 11-channel finding.

The EC-maass explorer found 11 coupling channels at 3-sigma with a column-shuffle
null. 0/100 closest pairs share conductor=level. This script attempts to kill
or confirm each channel through 6 independent adversarial tests.

Tests:
  F33: Rank-sort null (ordinal artifact?)
  F34: Trivial 1D baseline (single dimension enough?)
  F35: Megethos false positive (magnitude leakage through correlated features?)
  F36: Permutation null on residuals (within-bin signal?)
  F37: Engineered universality (encoding structure artifact?)
  F38: Raw data verification (preprocessing artifact?)

Machine: M1 (Skullport), RTX 5060 Ti 17GB
"""
import sys
import json
import time
import numpy as np
import torch
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[3]
TENSOR_PATH = ROOT / "cartography/convergence/data/dissection_tensor.pt"
OUTPUT_PATH = ROOT / "cartography/convergence/data/kill_ec_maass_results.json"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Reproducibility
RNG = np.random.RandomState(42)
torch.manual_seed(42)

# Parameters matching the explorer
SUBSAMPLE = 2000       # max objects per domain for SVD
N_NULL_COLUMN = 30     # column-shuffle null permutations
SIGMA_THRESHOLD = 3.0  # z-score threshold for "real" channel


# ============================================================
# Helpers
# ============================================================

def load_tensor():
    """Load the saved dissection tensor."""
    print(f"Loading tensor from {TENSOR_PATH}")
    data = torch.load(TENSOR_PATH, map_location='cpu', weights_only=False)
    tensor = data["tensor"].to(DEVICE)       # [N, D]
    mask = data["mask"].to(DEVICE)            # [N, D] bool
    labels = data["labels"]                   # list of str
    domains = data["domains"]                 # list of str
    slices = data["strategy_slices"]          # dict: name -> (start, end)
    print(f"  Shape: {tensor.shape}, Device: {DEVICE}")
    print(f"  Domains: {set(domains)}")
    return tensor, mask, labels, domains, slices


def get_domain_indices(domains, name):
    """Return indices of objects belonging to a domain."""
    return [i for i, d in enumerate(domains) if d == name]


def get_non_s13_cols(slices):
    """Return column indices excluding s13."""
    s13_start, s13_end = slices["s13"]
    D = max(end for _, (_, end) in slices.items() if isinstance(_, str) or True)
    # Actually get total dims from slice ranges
    all_ends = [end for _, end in slices.values()]
    D = max(all_ends)
    cols = list(range(0, s13_start)) + list(range(s13_end, D))
    return cols


def extract_and_normalize(tensor, mask, indices, col_idx):
    """Extract rows at indices, select columns, mask, L2-normalize."""
    idx_t = torch.tensor(indices, device=DEVICE)
    col_t = torch.tensor(col_idx, device=DEVICE)
    vecs = tensor[idx_t][:, col_t]
    m = mask[idx_t][:, col_t]
    vecs = vecs * m.float()
    norms = vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return vecs / norms


def subsample_vecs(vecs, max_n):
    """Subsample rows if needed."""
    if len(vecs) <= max_n:
        return vecs
    perm = torch.randperm(len(vecs), device=DEVICE)[:max_n]
    return vecs[perm]


def compute_coupling_svd(ec_vecs, maass_vecs, max_n=SUBSAMPLE):
    """Compute coupling matrix and return top-20 singular values."""
    ec_sub = subsample_vecs(ec_vecs, max_n)
    maass_sub = subsample_vecs(maass_vecs, max_n)
    C = ec_sub @ maass_sub.T
    _, S, _ = torch.linalg.svd(C, full_matrices=False)
    sv = S[:20].cpu().numpy()
    del C, S
    torch.cuda.empty_cache()
    return sv, ec_sub, maass_sub


def column_shuffle_null(ec_sub, maass_sub, n_null=N_NULL_COLUMN):
    """Compute null distribution by column-shuffling EC vectors."""
    null_svs = []
    for _ in range(n_null):
        ec_shuf = ec_sub.clone()
        for d in range(ec_shuf.shape[1]):
            perm = torch.randperm(ec_shuf.shape[0], device=DEVICE)
            ec_shuf[:, d] = ec_shuf[perm, d]
        # Re-normalize
        norms = ec_shuf.norm(dim=1, keepdim=True).clamp(min=1e-8)
        ec_shuf = ec_shuf / norms
        C_null = ec_shuf @ maass_sub.T
        _, S_null, _ = torch.linalg.svd(C_null, full_matrices=False)
        null_svs.append(S_null[:20].cpu().numpy())
        del C_null, S_null
    torch.cuda.empty_cache()
    null_svs = np.array(null_svs)
    return null_svs.mean(axis=0), null_svs.std(axis=0)


def count_channels(real_sv, null_mean, null_std, threshold=SIGMA_THRESHOLD):
    """Count channels exceeding null by threshold sigma."""
    z_scores = (real_sv - null_mean) / np.maximum(null_std, 1e-8)
    n = int(np.sum(z_scores > threshold))
    return n, z_scores


def print_sv_table(real_sv, null_mean, null_std, z_scores, label=""):
    """Pretty-print singular value comparison."""
    if label:
        print(f"\n  {label}")
    print(f"  {'SV':>3s}  {'Real':>10s}  {'Null_mu':>10s}  {'Null_sd':>10s}  {'z':>10s}  {'Pass?':>6s}")
    for i in range(min(15, len(real_sv))):
        exceeds = z_scores[i] > SIGMA_THRESHOLD
        print(f"  {i:3d}  {real_sv[i]:10.3f}  {null_mean[i]:10.3f}  {null_std[i]:10.3f}  "
              f"{z_scores[i]:10.2f}  {'YES' if exceeds else 'no':>6s}")


# ============================================================
# F33: Rank-sort null
# ============================================================
def f33_rank_sort(tensor, mask, ec_idx, maass_idx, col_idx, baseline_null_mean,
                  baseline_null_std):
    """Sort each dimension independently — breaks cross-feature correlations
    but preserves marginals. If 11 channels still appear, signal is ordinal."""
    print(f"\n{'='*60}")
    print(f"F33: Rank-sort null")
    print(f"{'='*60}")

    # Extract raw (masked) vectors
    ec_raw = extract_and_normalize(tensor, mask, ec_idx, col_idx)
    maass_raw = extract_and_normalize(tensor, mask, maass_idx, col_idx)

    ec_sub = subsample_vecs(ec_raw, SUBSAMPLE)
    maass_sub = subsample_vecs(maass_raw, SUBSAMPLE)

    # Rank-sort each dimension of BOTH ec and maass independently
    ec_sorted = ec_sub.clone()
    maass_sorted = maass_sub.clone()
    for d in range(ec_sorted.shape[1]):
        ec_sorted[:, d] = ec_sorted[:, d].sort()[0]
    for d in range(maass_sorted.shape[1]):
        maass_sorted[:, d] = maass_sorted[:, d].sort()[0]

    # Re-normalize
    ec_sorted = ec_sorted / ec_sorted.norm(dim=1, keepdim=True).clamp(min=1e-8)
    maass_sorted = maass_sorted / maass_sorted.norm(dim=1, keepdim=True).clamp(min=1e-8)

    # SVD
    C = ec_sorted @ maass_sorted.T
    _, S, _ = torch.linalg.svd(C, full_matrices=False)
    sorted_sv = S[:20].cpu().numpy()

    # Use the SAME baseline null for comparison
    n_channels, z_scores = count_channels(sorted_sv, baseline_null_mean, baseline_null_std)

    print_sv_table(sorted_sv, baseline_null_mean, baseline_null_std, z_scores,
                   "Rank-sorted SVD vs column-shuffle null")

    verdict = "KILLED" if n_channels >= 11 else "SURVIVES"
    reason = (f"Rank-sorted data produces {n_channels} channels "
              f"(original: 11). " +
              ("Same count => signal is ordinal artifact." if n_channels >= 11
               else "Fewer channels => cross-feature correlations matter."))

    print(f"\n  VERDICT: {verdict} — {reason}")

    del C, S, ec_sorted, maass_sorted
    torch.cuda.empty_cache()

    return {
        "test": "F33_rank_sort",
        "verdict": verdict,
        "n_channels_sorted": n_channels,
        "n_channels_original": 11,
        "reason": reason,
        "sorted_sv": sorted_sv.tolist(),
        "z_scores": z_scores.tolist(),
    }


# ============================================================
# F34: Trivial 1D baseline
# ============================================================
def f34_trivial_1d(tensor, mask, ec_idx, maass_idx, col_idx, slices,
                   baseline_null_mean, baseline_null_std):
    """Match EC-maass on single strongest dimension (s21_auto dim 0).
    If trivial 1D matching produces similar SVD, full tensor adds nothing."""
    print(f"\n{'='*60}")
    print(f"F34: Trivial 1D baseline")
    print(f"{'='*60}")

    ec_vecs = extract_and_normalize(tensor, mask, ec_idx, col_idx)
    maass_vecs = extract_and_normalize(tensor, mask, maass_idx, col_idx)

    # Find s21_auto dim 0 in the reduced (s13-excluded) column space
    s13_start, s13_end = slices["s13"]
    s21_start, s21_end = slices["s21_auto"]

    # Map global s21_auto dim 0 to local column index
    global_dim = s21_start  # dim 0 of s21_auto
    if global_dim < s13_start:
        local_dim = global_dim
    elif global_dim >= s13_end:
        local_dim = global_dim - (s13_end - s13_start)
    else:
        # s21 is inside s13 range — shouldn't happen
        local_dim = 0
        print("  WARNING: s21_auto overlaps s13, using dim 0 as fallback")

    print(f"  Target dimension: s21_auto dim 0 (global={global_dim}, local={local_dim})")

    ec_sub = subsample_vecs(ec_vecs, SUBSAMPLE)
    maass_sub = subsample_vecs(maass_vecs, SUBSAMPLE)

    # For each EC object, find closest maass on this single dimension
    ec_1d = ec_sub[:, local_dim]     # [Nec]
    maass_1d = maass_sub[:, local_dim]  # [Nm]

    # Compute 1D distance matrix and find nearest neighbors
    dist_1d = (ec_1d.unsqueeze(1) - maass_1d.unsqueeze(0)).abs()  # [Nec, Nm]
    nn_idx = dist_1d.argmin(dim=1)  # [Nec]

    # Now compute full coupling for these 1D-matched pairs
    # Build a "matched" coupling: each EC paired with its 1D-nearest maass
    matched_maass = maass_sub[nn_idx]  # [Nec, D']

    # Full coupling between the 1D-matched pairs
    C_trivial = ec_sub @ matched_maass.T
    _, S_trivial, _ = torch.linalg.svd(C_trivial, full_matrices=False)
    trivial_sv = S_trivial[:20].cpu().numpy()

    # Also compute the actual full coupling for comparison
    C_full = ec_sub @ maass_sub.T
    _, S_full, _ = torch.linalg.svd(C_full, full_matrices=False)
    full_sv = S_full[:20].cpu().numpy()

    n_channels_trivial, z_trivial = count_channels(trivial_sv, baseline_null_mean,
                                                    baseline_null_std)
    n_channels_full, z_full = count_channels(full_sv, baseline_null_mean,
                                             baseline_null_std)

    print_sv_table(trivial_sv, baseline_null_mean, baseline_null_std, z_trivial,
                   "Trivial 1D-matched SVD")

    # Compare: does trivial matching explain the channels?
    # If trivial produces similar channel count and SV magnitudes, killed
    sv_ratio = trivial_sv[0] / max(full_sv[0], 1e-8)
    verdict = "KILLED" if (n_channels_trivial >= 9 and sv_ratio > 0.8) else "SURVIVES"
    reason = (f"1D matching: {n_channels_trivial} channels (vs full {n_channels_full}), "
              f"SV ratio={sv_ratio:.3f}. " +
              ("Single dim explains most structure." if verdict == "KILLED"
               else "Full tensor captures structure beyond single dim."))

    print(f"\n  VERDICT: {verdict} — {reason}")

    del C_trivial, C_full, S_trivial, S_full, dist_1d
    torch.cuda.empty_cache()

    return {
        "test": "F34_trivial_1d",
        "verdict": verdict,
        "n_channels_trivial": n_channels_trivial,
        "n_channels_full": n_channels_full,
        "sv_ratio": float(sv_ratio),
        "reason": reason,
        "trivial_sv": trivial_sv.tolist(),
        "full_sv": full_sv.tolist(),
    }


# ============================================================
# F35: Megethos false positive (extended zeroing)
# ============================================================
def f35_megethos_leak(tensor, mask, ec_idx, maass_idx, slices,
                      baseline_null_mean, baseline_null_std):
    """Zero s13 AND s7_cond AND any dimension correlating >0.5 with s13 dim 0.
    If channels drop, Megethos was still leaking through correlated features."""
    print(f"\n{'='*60}")
    print(f"F35: Megethos false positive (extended zeroing)")
    print(f"{'='*60}")

    N, D = tensor.shape
    s13_start, s13_end = slices["s13"]
    mag_col = s13_start  # s13 dim 0 = log magnitude

    # Find all dimensions correlating > 0.5 with s13 dim 0
    mag_vals = tensor[:, mag_col].float()
    mag_valid = mask[:, mag_col]

    # Compute correlation of each dim with magnitude
    corr_with_mag = []
    for d in range(D):
        col = tensor[:, d].float()
        both_valid = mag_valid & mask[:, d]
        n_valid = both_valid.sum().item()
        if n_valid < 100:
            corr_with_mag.append(0.0)
            continue
        x = mag_vals[both_valid]
        y = col[both_valid]
        x_m = x - x.mean()
        y_m = y - y.mean()
        num = (x_m * y_m).sum()
        den = (x_m.norm() * y_m.norm()).clamp(min=1e-8)
        corr_with_mag.append(abs(float(num / den)))

    corr_with_mag = np.array(corr_with_mag)

    # Columns to zero: s13, s7_cond, anything with |r| > 0.5
    zero_cols = set(range(s13_start, s13_end))
    if "s7_cond" in slices:
        s7_start, s7_end = slices["s7_cond"]
        zero_cols.update(range(s7_start, s7_end))

    high_corr = np.where(corr_with_mag > 0.5)[0]
    zero_cols.update(high_corr.tolist())

    # Map strategy names for reporting
    zeroed_strategies = set()
    for col in zero_cols:
        for sname, (start, end) in slices.items():
            if start <= col < end:
                zeroed_strategies.add(sname)
                break

    print(f"  s13 dims: {s13_end - s13_start}")
    print(f"  s7_cond dims: {slices.get('s7_cond', (0,0))[1] - slices.get('s7_cond', (0,0))[0]}")
    print(f"  High-corr dims (|r|>0.5 with s13): {len(high_corr)}")
    print(f"  Total zeroed dims: {len(zero_cols)}")
    print(f"  Zeroed strategies: {sorted(zeroed_strategies)}")

    # Build column index excluding ALL zeroed columns
    all_ends = [end for _, end in slices.values()]
    D_total = max(all_ends)
    col_idx = [c for c in range(D_total) if c not in zero_cols]

    print(f"  Remaining dims: {len(col_idx)}")

    # Extract and normalize
    ec_vecs = extract_and_normalize(tensor, mask, ec_idx, col_idx)
    maass_vecs = extract_and_normalize(tensor, mask, maass_idx, col_idx)

    real_sv, ec_sub, maass_sub = compute_coupling_svd(ec_vecs, maass_vecs)
    null_mean, null_std = column_shuffle_null(ec_sub, maass_sub)
    n_channels, z_scores = count_channels(real_sv, null_mean, null_std)

    print_sv_table(real_sv, null_mean, null_std, z_scores,
                   "Extended-zeroed SVD (own null)")

    # Also compare against baseline null
    n_channels_vs_base, z_vs_base = count_channels(real_sv, baseline_null_mean,
                                                     baseline_null_std)

    verdict = "KILLED" if n_channels < 8 else "SURVIVES"
    reason = (f"Extended zeroing: {n_channels} channels (own null), "
              f"{n_channels_vs_base} channels (baseline null). "
              f"Zeroed {len(zero_cols)} dims across {sorted(zeroed_strategies)}. " +
              ("Channels dropped => Megethos leaking." if verdict == "KILLED"
               else "Channels persist => signal is not magnitude."))

    print(f"\n  VERDICT: {verdict} — {reason}")

    del ec_vecs, maass_vecs
    torch.cuda.empty_cache()

    return {
        "test": "F35_megethos_leak",
        "verdict": verdict,
        "n_channels_own_null": n_channels,
        "n_channels_baseline_null": n_channels_vs_base,
        "n_zeroed_dims": len(zero_cols),
        "zeroed_strategies": sorted(zeroed_strategies),
        "n_high_corr_dims": int(len(high_corr)),
        "reason": reason,
        "sv": real_sv.tolist(),
        "z_scores": z_scores.tolist(),
    }


# ============================================================
# F36: Permutation null on residuals (within-bin)
# ============================================================
def f36_within_bin_permutation(tensor, mask, ec_idx, maass_idx, col_idx, slices,
                                baseline_null_mean, baseline_null_std):
    """Within each Megethos bin, randomly permute EC and maass objects.
    If 11 channels persist, signal is NOT magnitude-driven at bin level."""
    print(f"\n{'='*60}")
    print(f"F36: Within-bin permutation null")
    print(f"{'='*60}")

    N, D = tensor.shape
    s13_start, _ = slices["s13"]
    mag_col = s13_start

    # Assign all objects to magnitude bins (same as normalize: 10 bins)
    n_bins = 10
    mag_vals = tensor[:, mag_col].cpu().numpy()
    mag_valid = mask[:, mag_col].cpu().numpy()

    # Compute bin edges from all valid objects
    valid_mags = mag_vals[mag_valid.astype(bool)]
    if len(valid_mags) == 0:
        print("  ERROR: No valid magnitude values")
        return {"test": "F36_within_bin", "verdict": "ERROR", "reason": "No valid magnitudes"}

    quantiles = np.quantile(valid_mags, np.linspace(0, 1, n_bins + 1))
    bin_assign = np.digitize(mag_vals, quantiles[1:-1])  # 0 to n_bins-1

    # For each EC and maass, get their bin
    ec_bins = np.array([bin_assign[i] for i in ec_idx])
    maass_bins = np.array([bin_assign[i] for i in maass_idx])

    print(f"  EC bin distribution: {np.bincount(ec_bins, minlength=n_bins)}")
    print(f"  maass bin distribution: {np.bincount(maass_bins, minlength=n_bins)}")

    # Within-bin permutation: for each bin, shuffle EC indices and maass indices
    # independently, then reassemble. This preserves within-bin composition
    # but breaks any cross-domain coupling WITHIN each bin.
    n_reps = 10
    within_bin_channels = []

    col_t = torch.tensor(col_idx, device=DEVICE)

    for rep in range(n_reps):
        # Build permuted EC and maass vectors
        # For each bin, randomly reassign EC objects to other EC objects in same bin
        ec_perm_indices = np.copy(np.array(ec_idx))
        maass_perm_indices = np.copy(np.array(maass_idx))

        for b in range(n_bins):
            ec_in_bin = np.where(ec_bins == b)[0]
            maass_in_bin = np.where(maass_bins == b)[0]
            if len(ec_in_bin) > 1:
                RNG.shuffle(ec_in_bin)
                # Reassign: the i-th EC in this bin gets features of perm[i]-th EC
                ec_perm_indices[np.where(ec_bins == b)[0]] = np.array(ec_idx)[ec_in_bin]
            if len(maass_in_bin) > 1:
                RNG.shuffle(maass_in_bin)
                maass_perm_indices[np.where(maass_bins == b)[0]] = np.array(maass_idx)[maass_in_bin]

        # Extract permuted vectors
        ec_perm_vecs = extract_and_normalize(tensor, mask, ec_perm_indices.tolist(), col_idx)
        maass_perm_vecs = extract_and_normalize(tensor, mask, maass_perm_indices.tolist(), col_idx)

        sv, _, _ = compute_coupling_svd(ec_perm_vecs, maass_perm_vecs)
        n_ch, _ = count_channels(sv, baseline_null_mean, baseline_null_std)
        within_bin_channels.append(n_ch)

        del ec_perm_vecs, maass_perm_vecs
        torch.cuda.empty_cache()

    mean_channels = np.mean(within_bin_channels)
    print(f"  Within-bin permuted channels per rep: {within_bin_channels}")
    print(f"  Mean: {mean_channels:.1f}")

    # Also compute the real (un-permuted) channel count for comparison
    ec_vecs = extract_and_normalize(tensor, mask, ec_idx, col_idx)
    maass_vecs = extract_and_normalize(tensor, mask, maass_idx, col_idx)
    real_sv, _, _ = compute_coupling_svd(ec_vecs, maass_vecs)
    n_real, z_real = count_channels(real_sv, baseline_null_mean, baseline_null_std)

    # If within-bin permutation preserves channels, signal is within-bin
    # (and thus potentially magnitude-driven at bin level)
    # If channels drop, signal requires specific cross-bin structure
    verdict = "KILLED" if mean_channels >= 9 else "SURVIVES"
    reason = (f"Within-bin permutation: {mean_channels:.1f} channels (real: {n_real}). " +
              ("Channels persist within bins => bin-level confound." if verdict == "KILLED"
               else "Channels drop => signal is NOT just magnitude bins."))

    print(f"\n  VERDICT: {verdict} — {reason}")

    del ec_vecs, maass_vecs
    torch.cuda.empty_cache()

    return {
        "test": "F36_within_bin_permutation",
        "verdict": verdict,
        "n_channels_real": n_real,
        "mean_channels_permuted": float(mean_channels),
        "per_rep_channels": within_bin_channels,
        "reason": reason,
    }


# ============================================================
# F37: Engineered universality
# ============================================================
def f37_engineered_universality(tensor, mask, ec_idx, maass_idx, col_idx,
                                 baseline_null_mean, baseline_null_std):
    """Swap EC features with random maass features and vice versa.
    If 11 channels still appear, signal is in encoding, not objects."""
    print(f"\n{'='*60}")
    print(f"F37: Engineered universality (feature swap)")
    print(f"{'='*60}")

    # Extract original vectors
    ec_vecs = extract_and_normalize(tensor, mask, ec_idx, col_idx)
    maass_vecs = extract_and_normalize(tensor, mask, maass_idx, col_idx)

    ec_sub = subsample_vecs(ec_vecs, SUBSAMPLE)
    maass_sub = subsample_vecs(maass_vecs, SUBSAMPLE)

    # Swap: give EC objects random maass features, and vice versa
    n_ec = ec_sub.shape[0]
    n_maass = maass_sub.shape[0]

    # Randomly sample maass vectors to replace EC
    maass_for_ec = maass_sub[torch.randint(n_maass, (n_ec,), device=DEVICE)]
    ec_for_maass = ec_sub[torch.randint(n_ec, (n_maass,), device=DEVICE)]

    # SVD of swapped coupling
    C_swap = maass_for_ec @ ec_for_maass.T
    _, S_swap, _ = torch.linalg.svd(C_swap, full_matrices=False)
    swap_sv = S_swap[:20].cpu().numpy()

    n_channels_swap, z_swap = count_channels(swap_sv, baseline_null_mean,
                                              baseline_null_std)

    print_sv_table(swap_sv, baseline_null_mean, baseline_null_std, z_swap,
                   "Feature-swapped SVD")

    # Also try: same domain paired with itself (maass-maass)
    C_self = maass_sub @ maass_sub.T
    _, S_self, _ = torch.linalg.svd(C_self, full_matrices=False)
    self_sv = S_self[:20].cpu().numpy()
    n_channels_self, z_self = count_channels(self_sv, baseline_null_mean,
                                              baseline_null_std)
    print(f"\n  Self-coupling (maass-maass): {n_channels_self} channels")

    verdict = "KILLED" if n_channels_swap >= 9 else "SURVIVES"
    reason = (f"Swapped features: {n_channels_swap} channels. " +
              f"Self-coupling: {n_channels_self}. " +
              ("Encoding structure alone produces channels." if verdict == "KILLED"
               else "Swapped features don't reproduce channels => signal is object-specific."))

    print(f"\n  VERDICT: {verdict} — {reason}")

    del C_swap, C_self, S_swap, S_self
    torch.cuda.empty_cache()

    return {
        "test": "F37_engineered_universality",
        "verdict": verdict,
        "n_channels_swap": n_channels_swap,
        "n_channels_self": n_channels_self,
        "reason": reason,
        "swap_sv": swap_sv.tolist(),
        "z_swap": z_swap.tolist(),
    }


# ============================================================
# F38: Raw data verification
# ============================================================
def f38_raw_verification(tensor, mask, ec_idx, maass_idx, col_idx, slices,
                          baseline_null_mean, baseline_null_std):
    """Use raw (un-normalized) tensor values. If coupling structure matches
    the normalized version, finding is robust to preprocessing."""
    print(f"\n{'='*60}")
    print(f"F38: Raw data verification (pre-normalization)")
    print(f"{'='*60}")

    # The tensor in dissection_tensor.pt may already be normalized.
    # "Raw" here means: use the tensor values WITHOUT L2 normalization per row.
    # We still zero s13 and apply the mask, but skip the row-wise L2 norm.
    # This tests whether L2 normalization creates artificial coupling.

    idx_ec = torch.tensor(ec_idx, device=DEVICE)
    idx_maass = torch.tensor(maass_idx, device=DEVICE)
    col_t = torch.tensor(col_idx, device=DEVICE)

    ec_raw = tensor[idx_ec][:, col_t] * mask[idx_ec][:, col_t].float()
    maass_raw = tensor[idx_maass][:, col_t] * mask[idx_maass][:, col_t].float()

    # Subsample
    if len(ec_raw) > SUBSAMPLE:
        perm = torch.randperm(len(ec_raw), device=DEVICE)[:SUBSAMPLE]
        ec_raw = ec_raw[perm]
    if len(maass_raw) > SUBSAMPLE:
        perm = torch.randperm(len(maass_raw), device=DEVICE)[:SUBSAMPLE]
        maass_raw = maass_raw[perm]

    # Approach 1: Raw (no L2 norm) — use cosine similarity via manual computation
    # to avoid scale issues
    ec_norms = ec_raw.norm(dim=1, keepdim=True).clamp(min=1e-8)
    maass_norms = maass_raw.norm(dim=1, keepdim=True).clamp(min=1e-8)
    # Cosine is the same as L2-normed dot product, so this won't differ.
    # Instead, use raw dot product (Frobenius inner product) without normalization
    C_raw = ec_raw @ maass_raw.T  # raw dot products, scale-sensitive
    _, S_raw, _ = torch.linalg.svd(C_raw, full_matrices=False)
    raw_sv = S_raw[:20].cpu().numpy()

    # Null for raw
    null_raw_svs = []
    for _ in range(N_NULL_COLUMN):
        ec_shuf = ec_raw.clone()
        for d in range(ec_shuf.shape[1]):
            perm = torch.randperm(ec_shuf.shape[0], device=DEVICE)
            ec_shuf[:, d] = ec_shuf[perm, d]
        C_null = ec_shuf @ maass_raw.T
        _, S_null, _ = torch.linalg.svd(C_null, full_matrices=False)
        null_raw_svs.append(S_null[:20].cpu().numpy())
        del C_null, S_null
    null_raw_svs = np.array(null_raw_svs)
    raw_null_mean = null_raw_svs.mean(axis=0)
    raw_null_std = null_raw_svs.std(axis=0)

    n_channels_raw, z_raw = count_channels(raw_sv, raw_null_mean, raw_null_std)

    print_sv_table(raw_sv, raw_null_mean, raw_null_std, z_raw,
                   "Raw (un-normalized) SVD with own null")

    # Approach 2: Standardize each dimension (z-score) instead of L2-norm
    ec_std = ec_raw.clone()
    maass_std = maass_raw.clone()
    for d in range(ec_std.shape[1]):
        col_ec = ec_std[:, d]
        col_maass = maass_std[:, d]
        all_vals = torch.cat([col_ec, col_maass])
        mu = all_vals.mean()
        sd = all_vals.std().clamp(min=1e-8)
        ec_std[:, d] = (col_ec - mu) / sd
        maass_std[:, d] = (col_maass - mu) / sd

    # L2-norm after z-scoring
    ec_std = ec_std / ec_std.norm(dim=1, keepdim=True).clamp(min=1e-8)
    maass_std = maass_std / maass_std.norm(dim=1, keepdim=True).clamp(min=1e-8)

    C_std = ec_std @ maass_std.T
    _, S_std, _ = torch.linalg.svd(C_std, full_matrices=False)
    std_sv = S_std[:20].cpu().numpy()

    # Null for standardized
    null_std_svs = []
    for _ in range(N_NULL_COLUMN):
        ec_shuf = ec_std.clone()
        for d in range(ec_shuf.shape[1]):
            perm = torch.randperm(ec_shuf.shape[0], device=DEVICE)
            ec_shuf[:, d] = ec_shuf[perm, d]
        norms = ec_shuf.norm(dim=1, keepdim=True).clamp(min=1e-8)
        ec_shuf = ec_shuf / norms
        C_null = ec_shuf @ maass_std.T
        _, S_null, _ = torch.linalg.svd(C_null, full_matrices=False)
        null_std_svs.append(S_null[:20].cpu().numpy())
        del C_null, S_null
    null_std_svs = np.array(null_std_svs)
    std_null_mean = null_std_svs.mean(axis=0)
    std_null_std = null_std_svs.std(axis=0)

    n_channels_std, z_std = count_channels(std_sv, std_null_mean, std_null_std)

    print_sv_table(std_sv, std_null_mean, std_null_std, z_std,
                   "Z-scored + L2-normed SVD with own null")

    # Verdict: robust if both raw and z-scored give similar channel counts
    both_similar = (n_channels_raw >= 8 and n_channels_std >= 8)
    verdict = "SURVIVES" if both_similar else "KILLED"
    reason = (f"Raw dot product: {n_channels_raw} channels. "
              f"Z-scored: {n_channels_std} channels. " +
              ("Both preprocessing approaches produce similar channels => robust."
               if verdict == "SURVIVES"
               else "Channel count preprocessing-dependent => fragile finding."))

    print(f"\n  VERDICT: {verdict} — {reason}")

    del C_raw, C_std, S_raw, S_std
    torch.cuda.empty_cache()

    return {
        "test": "F38_raw_verification",
        "verdict": verdict,
        "n_channels_raw": n_channels_raw,
        "n_channels_zscore": n_channels_std,
        "reason": reason,
        "raw_sv": raw_sv.tolist(),
        "z_raw": z_raw.tolist(),
        "std_sv": std_sv.tolist(),
        "z_std": z_std.tolist(),
    }


# ============================================================
# Main
# ============================================================
def main():
    t0 = time.time()
    results = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "tests": {}}

    # ---- Load data ----
    tensor, mask, labels, domains, slices = load_tensor()
    ec_idx = get_domain_indices(domains, "EC")
    maass_idx = get_domain_indices(domains, "maass")
    print(f"  EC: {len(ec_idx)}, maass: {len(maass_idx)}")

    if not ec_idx or not maass_idx:
        print("ERROR: Missing EC or maass data in tensor")
        return

    results["counts"] = {"EC": len(ec_idx), "maass": len(maass_idx)}

    # ---- Get s13-excluded columns ----
    col_idx = get_non_s13_cols(slices)
    print(f"  Dims after s13 exclusion: {len(col_idx)}")

    # ---- Compute baseline (original 11-channel finding) ----
    print(f"\n{'='*60}")
    print(f"BASELINE: Reproducing the 11-channel finding")
    print(f"{'='*60}")

    ec_vecs = extract_and_normalize(tensor, mask, ec_idx, col_idx)
    maass_vecs = extract_and_normalize(tensor, mask, maass_idx, col_idx)
    baseline_sv, ec_sub, maass_sub = compute_coupling_svd(ec_vecs, maass_vecs)
    baseline_null_mean, baseline_null_std = column_shuffle_null(ec_sub, maass_sub)
    baseline_channels, baseline_z = count_channels(baseline_sv, baseline_null_mean,
                                                    baseline_null_std)

    print_sv_table(baseline_sv, baseline_null_mean, baseline_null_std, baseline_z,
                   "Baseline SVD")
    print(f"\n  Baseline channels: {baseline_channels}")

    results["baseline"] = {
        "n_channels": baseline_channels,
        "sv": baseline_sv.tolist(),
        "null_mean": baseline_null_mean.tolist(),
        "null_std": baseline_null_std.tolist(),
        "z_scores": baseline_z.tolist(),
    }

    del ec_vecs, maass_vecs, ec_sub, maass_sub
    torch.cuda.empty_cache()

    # ---- Run F33-F38 ----
    results["tests"]["F33"] = f33_rank_sort(
        tensor, mask, ec_idx, maass_idx, col_idx,
        baseline_null_mean, baseline_null_std)

    results["tests"]["F34"] = f34_trivial_1d(
        tensor, mask, ec_idx, maass_idx, col_idx, slices,
        baseline_null_mean, baseline_null_std)

    results["tests"]["F35"] = f35_megethos_leak(
        tensor, mask, ec_idx, maass_idx, slices,
        baseline_null_mean, baseline_null_std)

    results["tests"]["F36"] = f36_within_bin_permutation(
        tensor, mask, ec_idx, maass_idx, col_idx, slices,
        baseline_null_mean, baseline_null_std)

    results["tests"]["F37"] = f37_engineered_universality(
        tensor, mask, ec_idx, maass_idx, col_idx,
        baseline_null_mean, baseline_null_std)

    results["tests"]["F38"] = f38_raw_verification(
        tensor, mask, ec_idx, maass_idx, col_idx, slices,
        baseline_null_mean, baseline_null_std)

    # ---- Summary ----
    print(f"\n{'='*60}")
    print(f"FINAL TALLY")
    print(f"{'='*60}")
    print(f"  Baseline: {baseline_channels} channels at 3-sigma")
    print()

    survived = 0
    killed = 0
    for test_id in ["F33", "F34", "F35", "F36", "F37", "F38"]:
        r = results["tests"][test_id]
        v = r["verdict"]
        print(f"  {test_id}: {v} — {r['reason']}")
        if v == "SURVIVES":
            survived += 1
        elif v == "KILLED":
            killed += 1

    results["summary"] = {
        "survived": survived,
        "killed": killed,
        "total": 6,
        "honest_verdict": (
            f"{survived}/6 tests survived. "
            f"{'FINDING CONFIRMED' if survived >= 5 else 'FINDING WEAKENED' if survived >= 3 else 'FINDING KILLED'}."
        ),
    }

    print(f"\n  HONEST TALLY: {survived} SURVIVED, {killed} KILLED out of 6 tests")
    if survived >= 5:
        print(f"  => FINDING CONFIRMED: 11-channel EC-maass coupling is robust")
    elif survived >= 3:
        print(f"  => FINDING WEAKENED: Some channels are real, some may be artifact")
    else:
        print(f"  => FINDING KILLED: Most channels are artifact")

    # ---- Save ----
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT_PATH}")

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
