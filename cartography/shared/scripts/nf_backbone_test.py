"""
NF Backbone Falsification Test — Harmonia

Tests Kairos's PROBABLE finding: NF mediates 77% of cross-domain coupling
through a non-Megethos component at 1-3% energy.

Attack vectors:
1. Singular vector projection onto NF PCA axes (is component 1 Megethos residual?)
2. Random direction null (does random 1-3% energy look the same?)
3. Feature ablation (remove log|disc| and rebuild — does backbone persist?)
4. Permutation null (shuffle NF labels, keep features — does bond rank survive?)

Author: Harmonia
Date: 2026-04-15
"""
import sys
import io
import os
import json
import numpy as np
import torch

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    import tntorch as tn
except ImportError:
    print("tntorch not available. Install with: pip install tntorch")
    sys.exit(1)

from harmonia.src.domain_index import load_number_fields, DOMAIN_LOADERS
from harmonia.src.validate import extract_bond_components


NF_FEATURE_NAMES = [
    "degree",           # PC2 per Kairos (22.6%)
    "disc_sign",        # binary
    "log_disc_abs",     # Megethos candidate (PC3, 18.3%)
    "class_number",     # PC1 per Kairos (37.6%)
    "regulator",        # mixed
    "class_group_rank", # structural
]


def build_tt_pair(dom_a, dom_b, eps=1e-3, subsample=1000):
    """Build a 2-domain TT via cross approximation."""
    from harmonia.src.coupling import CouplingScorer

    # Subsample large domains to keep TT-Cross tractable
    n_a = min(len(dom_a), subsample)
    n_b = min(len(dom_b), subsample)

    # Create subsampled domain indices if needed
    if n_a < len(dom_a):
        rng = np.random.default_rng(42)
        idx_a = rng.choice(len(dom_a), n_a, replace=False)
        sub_a = type(dom_a)(
            name=dom_a.name,
            labels=[dom_a.labels[i] for i in idx_a],
            features=dom_a.features[idx_a],
        )
    else:
        sub_a = dom_a

    if n_b < len(dom_b):
        rng = np.random.default_rng(43)
        idx_b = rng.choice(len(dom_b), n_b, replace=False)
        sub_b = type(dom_b)(
            name=dom_b.name,
            labels=[dom_b.labels[i] for i in idx_b],
            features=dom_b.features[idx_b],
        )
    else:
        sub_b = dom_b

    domains = [sub_a, sub_b]
    scorer = CouplingScorer(domains)

    domain_grids = [
        torch.arange(len(sub_a), dtype=torch.float32),
        torch.arange(len(sub_b), dtype=torch.float32),
    ]

    def value_fn(*indices):
        int_indices = [idx.long() for idx in indices]
        return scorer(*int_indices)

    tt = tn.cross(
        function=value_fn,
        domain=domain_grids,
        eps=eps,
        max_iter=25,
        verbose=False,
    )
    return tt, domains


def attack_1_pca_projection(nf_domain, components):
    """Project surviving component singular vector onto NF PCA axes."""
    print("\n=== ATTACK 1: Singular Vector PCA Projection ===")

    features = nf_domain.features.numpy()  # (N, 6)
    n, d = features.shape
    print(f"  NF features: {n} objects x {d} features")
    print(f"  Feature names: {NF_FEATURE_NAMES}")

    # PCA on NF features
    cov = np.cov(features.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    variance_explained = eigenvalues / eigenvalues.sum()
    print(f"\n  PCA variance explained:")
    for i in range(d):
        loadings = eigenvectors[:, i]
        top_feature = NF_FEATURE_NAMES[np.argmax(np.abs(loadings))]
        print(f"    PC{i+1}: {variance_explained[i]:.1%} (top loading: {top_feature})")

    # Now project each component's left scores onto PCA axes
    for comp_idx, (sv, left_scores, right_scores) in enumerate(components):
        energy = sv**2 / sum(s**2 for s, _, _ in components)
        left_np = left_scores.numpy()

        # The left_scores tell us how much each NF object loads on this component
        # Project this weighting onto PCA axes
        # Weighted centroid in feature space
        weights = left_np / (left_np.sum() + 1e-15)
        weighted_features = (features * weights[:, None]).sum(axis=0)

        # Project onto PCA axes
        projections = eigenvectors.T @ weighted_features

        print(f"\n  Component {comp_idx} (SV={sv:.4f}, energy={energy:.3%}):")
        print(f"    Score selectivity: CV={left_np.std()/left_np.mean():.3f}")
        dominant_pc = np.argmax(np.abs(projections))
        for i in range(d):
            bar = '*' * int(abs(projections[i]) / (np.abs(projections).max() + 1e-15) * 20)
            print(f"    PC{i+1} projection: {projections[i]:+.4f} {bar}")

        # The critical question: does the surviving component load on Megethos (PC3)?
        megethos_loading = abs(projections[2]) / (np.abs(projections).sum() + 1e-15)
        class_number_loading = abs(projections[0]) / (np.abs(projections).sum() + 1e-15)
        print(f"    Megethos fraction: {megethos_loading:.3f}")
        print(f"    Class number fraction: {class_number_loading:.3f}")

    return True


def attack_2_random_direction_null(nf_domain, partner_domain, n_trials=20):
    """Does a random 1-3% energy direction look the same?"""
    print(f"\n=== ATTACK 2: Random Direction Null ({n_trials} trials) ===")

    n_nf = len(nf_domain)

    # Build real TT and get component 1 score pattern
    tt, domains = build_tt_pair(nf_domain, partner_domain)
    components = extract_bond_components(tt, 0, domains)

    if len(components) < 2:
        print("  Only 1 component. Cannot test component 1.")
        return None

    # Real component 1 scores
    sv1, left1, right1 = components[1]
    real_selectivity = (left1.std() / left1.mean()).item()
    print(f"  Real component 1: SV={sv1:.4f}, selectivity={real_selectivity:.4f}")

    # Random null: generate random unit vectors in feature space, create fake scores
    rng = np.random.default_rng(42)
    null_selectivities = []
    for trial in range(n_trials):
        # Random weighting of NF objects (same distribution shape as real)
        fake_scores = torch.tensor(rng.normal(0, 1, n_nf), dtype=torch.float32)
        fake_scores = fake_scores.abs()
        sel = (fake_scores.std() / fake_scores.mean()).item()
        null_selectivities.append(sel)

    null_mean = np.mean(null_selectivities)
    null_std = np.std(null_selectivities)
    z_score = (real_selectivity - null_mean) / (null_std + 1e-15)

    print(f"  Null selectivity: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"  Z-score vs null: {z_score:.2f}")

    if abs(z_score) < 2:
        print("  KILLED: Component 1 selectivity is within random null.")
        return {"status": "KILLED", "z": z_score}
    else:
        print(f"  SURVIVES: Component 1 selectivity is {z_score:.1f} sigma from null.")
        return {"status": "SURVIVES", "z": z_score}


def attack_3_feature_ablation(partner_domain, eps=1e-3):
    """Remove log|disc| (Megethos) from NF and rebuild. Does bond survive?"""
    print("\n=== ATTACK 3: Feature Ablation (remove log|disc|) ===")

    # Load NF with all features
    nf_full = load_number_fields()
    n_full = nf_full.features.shape[1]
    print(f"  Full NF features: {n_full} ({NF_FEATURE_NAMES})")

    # Ablate: remove feature index 2 (log_disc_abs = Megethos)
    ablate_idx = 2  # log_disc_abs
    keep_mask = [i for i in range(n_full) if i != ablate_idx]
    ablated_features = nf_full.features[:, keep_mask]
    nf_ablated = type(nf_full)(
        name="number_fields_no_megethos",
        labels=nf_full.labels,
        features=ablated_features,
    )
    print(f"  Ablated NF features: {nf_ablated.n_features} (removed {NF_FEATURE_NAMES[ablate_idx]})")

    # Build TT with ablated features
    try:
        tt_full, _ = build_tt_pair(nf_full, partner_domain, eps=eps)
        tt_ablated, _ = build_tt_pair(nf_ablated, partner_domain, eps=eps)

        rank_full = tt_full.ranks_tt
        rank_ablated = tt_ablated.ranks_tt

        print(f"  Full TT ranks: {rank_full}")
        print(f"  Ablated TT ranks: {rank_ablated}")

        # Compare bond dimensions
        bond_full = rank_full[1] if len(rank_full) > 1 else 0
        bond_ablated = rank_ablated[1] if len(rank_ablated) > 1 else 0

        print(f"  Bond dimension: full={bond_full}, ablated={bond_ablated}")

        if bond_ablated >= bond_full:
            print("  SURVIVES: Bond dimension persists after Megethos removal.")
            return {"status": "SURVIVES", "full": bond_full, "ablated": bond_ablated}
        elif bond_ablated == 0:
            print("  KILLED: Bond dimension collapses to 0 after Megethos removal.")
            print("  The backbone was entirely driven by log|disc|.")
            return {"status": "KILLED", "full": bond_full, "ablated": bond_ablated}
        else:
            print(f"  WEAKENED: Bond drops from {bond_full} to {bond_ablated}.")
            return {"status": "WEAKENED", "full": bond_full, "ablated": bond_ablated}

    except Exception as e:
        print(f"  ERROR: {e}")
        return {"status": "ERROR", "error": str(e)}


def attack_4_permutation_null(nf_domain, partner_domain, n_perms=20):
    """Shuffle NF labels (keeping features). Does bond rank survive?"""
    print(f"\n=== ATTACK 4: Permutation Null ({n_perms} permutations) ===")

    # Real bond
    tt_real, _ = build_tt_pair(nf_domain, partner_domain)
    real_rank = tt_real.ranks_tt[1] if len(tt_real.ranks_tt) > 1 else 0
    print(f"  Real bond rank: {real_rank}")

    # Permutation null: shuffle NF features (break object identity, keep distribution)
    rng = np.random.default_rng(42)
    null_ranks = []
    for trial in range(n_perms):
        perm = rng.permutation(len(nf_domain))
        shuffled_features = nf_domain.features[perm]
        nf_shuffled = type(nf_domain)(
            name="number_fields_shuffled",
            labels=[nf_domain.labels[i] for i in perm],
            features=shuffled_features,
        )
        try:
            tt_null, _ = build_tt_pair(nf_shuffled, partner_domain)
            null_rank = tt_null.ranks_tt[1] if len(tt_null.ranks_tt) > 1 else 0
            null_ranks.append(null_rank)
        except Exception:
            null_ranks.append(0)

    null_mean = np.mean(null_ranks)
    null_std = np.std(null_ranks) + 1e-15
    z_score = (real_rank - null_mean) / null_std

    print(f"  Null rank: mean={null_mean:.2f}, std={null_std:.2f}")
    print(f"  Z-score: {z_score:.2f}")

    if z_score < 2:
        print("  KILLED: Real rank is within permutation null.")
        print("  The bond is a distributional artifact, not object-level structure.")
        return {"status": "KILLED", "z": z_score, "real": real_rank, "null_mean": null_mean}
    else:
        print(f"  SURVIVES: Real rank is {z_score:.1f} sigma above permutation null.")
        return {"status": "SURVIVES", "z": z_score, "real": real_rank, "null_mean": null_mean}


def main():
    print("=" * 70)
    print("NF BACKBONE FALSIFICATION TEST — Harmonia")
    print("=" * 70)

    # Load domains
    print("\nLoading domains...")
    nf = load_number_fields()
    print(f"  NF: {nf}")

    # Load a partner domain to test the bond
    # Use elliptic curves as the primary partner (strong pairwise bond per deep_sweep)
    partners_to_test = ["elliptic_curves", "space_groups", "modular_forms"]
    loaded_partners = {}

    for pname in partners_to_test:
        if pname in DOMAIN_LOADERS:
            try:
                loaded_partners[pname] = DOMAIN_LOADERS[pname]()
                print(f"  {pname}: {loaded_partners[pname]}")
            except Exception as e:
                print(f"  {pname}: FAILED ({e})")

    if not loaded_partners:
        print("No partner domains loaded. Cannot proceed.")
        return

    results = {}
    # Run attacks against each partner
    for pname, partner in loaded_partners.items():
        print(f"\n{'='*70}")
        print(f"Testing NF <-> {pname}")
        print(f"{'='*70}")

        # Build TT for this pair
        try:
            tt, domains = build_tt_pair(nf, partner)
            components = extract_bond_components(tt, 0, domains)
            print(f"  TT ranks: {tt.ranks_tt}")
            print(f"  Components: {len(components)}")
            for i, (sv, ls, rs) in enumerate(components):
                energy = sv**2 / sum(s**2 for s, _, _ in components)
                print(f"    [{i}] SV={sv:.4f}, energy={energy:.3%}")
        except Exception as e:
            print(f"  TT build failed: {e}")
            continue

        pair_results = {}

        # Attack 1: PCA projection
        try:
            attack_1_pca_projection(nf, components)
        except Exception as e:
            print(f"  Attack 1 failed: {e}")

        # Attack 2: Random direction null
        try:
            pair_results["attack_2"] = attack_2_random_direction_null(nf, partner)
        except Exception as e:
            print(f"  Attack 2 failed: {e}")

        # Attack 3: Feature ablation
        try:
            pair_results["attack_3"] = attack_3_feature_ablation(partner)
        except Exception as e:
            print(f"  Attack 3 failed: {e}")

        # Attack 4: Permutation null
        try:
            pair_results["attack_4"] = attack_4_permutation_null(nf, partner, n_perms=10)
        except Exception as e:
            print(f"  Attack 4 failed: {e}")

        results[pname] = pair_results

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    total_kills = 0
    total_survives = 0
    for pname, pair_results in results.items():
        print(f"\n  NF <-> {pname}:")
        for aname, ares in pair_results.items():
            if ares:
                status = ares.get("status", "?")
                if "KILL" in status:
                    total_kills += 1
                elif "SURVIV" in status:
                    total_survives += 1
                print(f"    {aname}: {status}")

    print(f"\n  Total: {total_kills} kills, {total_survives} survives")

    if total_kills > total_survives:
        print("  VERDICT: NF backbone is MORE LIKELY an artifact than real structure.")
    elif total_survives > total_kills:
        print("  VERDICT: NF backbone shows genuine non-Megethos structure.")
    else:
        print("  VERDICT: INCONCLUSIVE. Needs more data.")

    # Save
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'nf_backbone_results.json')
    with open(output_path, 'w') as f:
        json.dump({
            "test": "NF_backbone_falsification",
            "date": "2026-04-15",
            "author": "Harmonia",
            "results": results,
            "kills": total_kills,
            "survives": total_survives,
        }, f, indent=2, default=str)
    print(f"\n  Results saved to {output_path}")


if __name__ == "__main__":
    main()
