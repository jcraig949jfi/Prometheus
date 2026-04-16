#!/usr/bin/env python3
"""
Projection Test — Are Harmonia bond dimensions just shared PC1?

For each surviving domain pair:
1. Load both domains via Harmonia's loaders
2. Compute PC1 of each domain's feature matrix
3. Residualize: remove PC1 projection from all features
4. Rerun TT-Cross on the residualized domains
5. Compare bond dimensions: original vs residualized

If bond dim collapses → shared magnitude axis (projection artifact)
If bond dim survives → structure beyond the dominant axis

Also tests: remove top-K PCs (K=1,2,3) to see how many shared axes
need to be removed before structure disappears.
"""
import sys
import time
import json
import torch
import numpy as np
from pathlib import Path
from datetime import datetime

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from harmonia.src.domain_index import DomainIndex, load_domains
from harmonia.src.coupling import DistributionalCoupling
from harmonia.src.engine import HarmoniaEngine


def residualize_pc(domain, n_components=1):
    """Remove top-N principal components from a domain's feature matrix.

    Returns a new DomainIndex with residualized features.
    """
    feats = domain.features.clone()
    # Center
    mu = feats.mean(dim=0)
    centered = feats - mu

    # SVD to get principal components
    U, S, Vh = torch.linalg.svd(centered, full_matrices=False)

    # Remove top-N components
    for i in range(min(n_components, len(S))):
        # Project onto PC_i and subtract
        pc = Vh[i]  # (D,)
        projection = (centered @ pc).unsqueeze(1) * pc.unsqueeze(0)  # (N, D)
        centered = centered - projection

    # Re-normalize (z-score)
    std = centered.std(dim=0).clamp(min=1e-8)
    normalized = centered / std
    normalized[torch.isnan(normalized)] = 0.0

    return DomainIndex(
        name=f"{domain.name}_resid_pc{n_components}",
        labels=domain.labels,
        features=normalized,
    )


def run_tt_cross(domain_a, domain_b, max_rank=15, subsample=2000):
    """Run TT-Cross on a domain pair, return bond dimension and singular values."""
    domains = [domain_a, domain_b]

    # Subsample if needed
    for i, dom in enumerate(domains):
        if dom.n_objects > subsample:
            perm = torch.randperm(dom.n_objects)[:subsample]
            domains[i] = DomainIndex(
                dom.name,
                [dom.labels[j] for j in perm.tolist()],
                dom.features[perm],
            )

    scorer = DistributionalCoupling(domains)

    import tntorch as tn
    grids = [torch.arange(d.n_objects, dtype=torch.float32) for d in domains]

    def value_fn(*indices):
        return scorer(*[idx.long() for idx in indices])

    tt = tn.cross(
        function=value_fn,
        domain=grids,
        eps=1e-4,
        rmax=max_rank,
        max_iter=100,
    )

    ranks = tt.ranks_tt.tolist()
    bond_dim = max(ranks[1:-1]) if len(ranks) > 2 else ranks[1]

    # Get singular values
    core = tt.cores[0]
    unfolded = core.reshape(-1, core.shape[-1])
    try:
        svs = torch.linalg.svdvals(unfolded).tolist()[:10]
    except Exception:
        svs = []

    return bond_dim, svs, ranks


def test_pair(name_a, name_b, subsample=2000, max_rank=15):
    """Test a single domain pair: original vs PC-residualized."""
    print(f"\n{'='*70}")
    print(f"  {name_a} x {name_b}")
    print(f"{'='*70}")

    # Load domains
    domains = load_domains(name_a, name_b)
    da = domains[name_a]
    db = domains[name_b]
    print(f"  Loaded: {da.name}({da.n_objects}x{da.n_features}) x {db.name}({db.n_objects}x{db.n_features})")

    # Report PC1 variance explained
    for name, dom in [(name_a, da), (name_b, db)]:
        feats = dom.features - dom.features.mean(dim=0)
        _, S, _ = torch.linalg.svd(feats, full_matrices=False)
        var_explained = (S ** 2) / (S ** 2).sum()
        print(f"  {name} PC variance: PC1={var_explained[0]:.1%}, PC2={var_explained[1]:.1%}, PC3={var_explained[2]:.1%}")

    results = {}

    # Original
    t0 = time.time()
    bond, svs, ranks = run_tt_cross(da, db, max_rank, subsample)
    elapsed = time.time() - t0
    print(f"\n  Original:    bond_dim={bond:2d}  SVs=[{', '.join(f'{s:.2f}' for s in svs[:5])}]  ({elapsed:.1f}s)")
    results["original"] = {"bond_dim": bond, "svs": svs[:5]}

    # Remove PC1 from both
    for n_pc in [1, 2, 3]:
        da_resid = residualize_pc(da, n_pc)
        db_resid = residualize_pc(db, n_pc)
        t0 = time.time()
        bond_r, svs_r, ranks_r = run_tt_cross(da_resid, db_resid, max_rank, subsample)
        elapsed = time.time() - t0
        delta = bond_r - results["original"]["bond_dim"]
        marker = "COLLAPSED" if bond_r <= 1 else ("REDUCED" if delta < 0 else "SURVIVED")
        print(f"  Minus PC1-{n_pc}: bond_dim={bond_r:2d}  SVs=[{', '.join(f'{s:.2f}' for s in svs_r[:5])}]  ({elapsed:.1f}s)  [{marker}]")
        results[f"minus_pc1_to_{n_pc}"] = {"bond_dim": bond_r, "svs": svs_r[:5], "verdict": marker}

    # Also test: remove PC1 from ONLY domain A (asymmetric test)
    da_resid1 = residualize_pc(da, 1)
    t0 = time.time()
    bond_asym, svs_asym, _ = run_tt_cross(da_resid1, db, max_rank, subsample)
    elapsed = time.time() - t0
    print(f"  Asymmetric:  bond_dim={bond_asym:2d}  SVs=[{', '.join(f'{s:.2f}' for s in svs_asym[:5])}]  ({elapsed:.1f}s)  [PC1 removed from {name_a} only]")
    results["asymmetric_a_only"] = {"bond_dim": bond_asym, "svs": svs_asym[:5]}

    return results


# ============================================================
# Main
# ============================================================

PAIRS = [
    ("elliptic_curves", "maass"),
    ("knots", "maass"),
    ("maass", "number_fields"),
    ("genus2", "number_fields"),
    ("genus2", "knots"),
    ("knots", "number_fields"),
    ("elliptic_curves", "number_fields"),
    ("elliptic_curves", "knots"),
]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Projection test: are bond dimensions just shared PC1?")
    parser.add_argument("--pairs", type=int, default=len(PAIRS), help="Number of pairs to test")
    parser.add_argument("--subsample", type=int, default=2000, help="Subsample size")
    args = parser.parse_args()

    print("=" * 70)
    print("  PROJECTION TEST — Shared PC1 or genuine multi-axis structure?")
    print(f"  {datetime.now().isoformat()}")
    print("=" * 70)

    all_results = {}
    for name_a, name_b in PAIRS[:args.pairs]:
        try:
            results = test_pair(name_a, name_b, subsample=args.subsample)
            all_results[f"{name_a}_x_{name_b}"] = results
        except Exception as e:
            print(f"  ERROR: {e}")
            all_results[f"{name_a}_x_{name_b}"] = {"error": str(e)}

    # Summary
    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(f"  {'Pair':35s} {'Original':>8s} {'−PC1':>8s} {'−PC1-2':>8s} {'−PC1-3':>8s} {'Verdict'}")
    print(f"  {'-'*35} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*20}")

    for pair, res in all_results.items():
        if "error" in res:
            print(f"  {pair:35s} ERROR: {res['error'][:40]}")
            continue
        orig = res.get("original", {}).get("bond_dim", "?")
        m1 = res.get("minus_pc1_to_1", {}).get("bond_dim", "?")
        m2 = res.get("minus_pc1_to_2", {}).get("bond_dim", "?")
        m3 = res.get("minus_pc1_to_3", {}).get("bond_dim", "?")

        if isinstance(m1, int) and isinstance(orig, int):
            if m1 <= 1:
                verdict = "PROJECTION (PC1)"
            elif m1 < orig:
                verdict = f"PARTIAL (lost {orig - m1})"
            else:
                verdict = "GENUINE STRUCTURE"
        else:
            verdict = "?"

        print(f"  {pair:35s} {str(orig):>8s} {str(m1):>8s} {str(m2):>8s} {str(m3):>8s} {verdict}")

    # Save
    out_path = Path(__file__).parent / "results" / f"projection_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  Saved: {out_path}")
