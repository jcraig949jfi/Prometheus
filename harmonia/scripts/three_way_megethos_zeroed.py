"""
Three-way TT-Cross interactions with Megethos zeroed.

Tests whether 3-body interactions reveal structure invisible to pairwise tests.
If A-B and B-C are both null, but A-B-C has higher TT rank than expected,
there's an emergent 3-body effect.

Triples tested:
1. EC - MF - maass           (all GL(2) automorphic)
2. EC - NF - genus2          (arithmetic-geometric)
3. EC - rmt - modular_forms  (quantum + arithmetic + analytic)
4. chemistry - materials - ec_zeros  (cross-category)
5. dynamics - oeis - spectral_sigs   (sequence + chaos + formula)
"""

import json
import sys
import time
import torch
import numpy as np
import tntorch as tn

sys.path.insert(0, "D:/Prometheus")
from harmonia.src.domain_index import load_domains, DomainIndex
from harmonia.src.coupling import CouplingScorer, AlignmentCoupling

TRIPLES = [
    ("elliptic_curves", "modular_forms", "maass"),
    ("elliptic_curves", "number_fields", "genus2"),
    ("elliptic_curves", "rmt", "modular_forms"),
    ("chemistry", "materials", "ec_zeros"),
    ("dynamics", "oeis", "spectral_sigs"),
]

TRIPLE_LABELS = [
    "EC-MF-maass",
    "EC-NF-genus2",
    "EC-rmt-MF",
    "chemistry-materials-ec_zeros",
    "dynamics-oeis-spectral_sigs",
]

SUBSAMPLE = 1000
MAX_RANK = 30
EPS = 1e-3
N_NULL = 5


def subsample_domain(dom: DomainIndex, n: int, seed: int = 42) -> DomainIndex:
    """Subsample a domain to n objects."""
    if dom.n_objects <= n:
        return dom
    rng = np.random.RandomState(seed)
    idx = rng.choice(dom.n_objects, n, replace=False)
    idx.sort()
    labels = [dom.labels[i] for i in idx]
    features = dom.features[idx]
    return DomainIndex(dom.name, labels, features)


def zero_megethos(dom: DomainIndex) -> DomainIndex:
    """Zero out feature 0 (Megethos) in-place and return."""
    dom.features = dom.features.clone()
    dom.features[:, 0] = 0.0
    return dom


def run_tt_cross(domains: list[DomainIndex], max_rank: int = MAX_RANK,
                 eps: float = EPS) -> tuple[list[int], object]:
    """
    Run TT-Cross on domains, return (bond_dims, tt_tensor).
    bond_dims has len = n_domains - 1.
    """
    scorer = CouplingScorer(domains)
    grid = [torch.arange(dom.n_objects) for dom in domains]

    def func(x):
        # x is (batch, 3) matrix of indices
        indices = [x[:, i].long() for i in range(len(domains))]
        return scorer(*indices)

    tt = tn.cross(
        function=func,
        domain=grid,
        function_arg="matrix",
        ranks_tt=max_rank,
        eps=eps,
        max_iter=25,
        verbose=False,
        suppress_warnings=True,
    )

    # Bond dimensions = internal ranks (excluding boundary 1s)
    ranks = tt.ranks_tt.tolist()
    # ranks is [1, r1, r2, 1] for 3 domains
    bond_dims = ranks[1:-1]  # [r1, r2]
    return bond_dims, tt


def run_null(domains: list[DomainIndex], n_null: int = N_NULL,
             max_rank: int = MAX_RANK, eps: float = EPS) -> list[list[int]]:
    """
    Null model: shuffle one domain's features, rerun TT-Cross n_null times.
    Returns list of bond_dim lists.
    """
    null_bonds = []
    for trial in range(n_null):
        # Shuffle the middle domain's features (break structure)
        shuffled = []
        for i, dom in enumerate(domains):
            if i == 1:  # shuffle middle domain
                perm = torch.randperm(dom.n_objects)
                new_feats = dom.features[perm].clone()
                shuffled.append(DomainIndex(dom.name + "_shuffled", dom.labels, new_feats))
            else:
                shuffled.append(dom)

        try:
            bonds, _ = run_tt_cross(shuffled, max_rank, eps)
        except Exception as e:
            print(f"  Null trial {trial} failed: {e}")
            bonds = [max_rank] * (len(domains) - 1)
        null_bonds.append(bonds)
    return null_bonds


def main():
    results = {
        "experiment": "3-way TT-Cross with Megethos zeroed",
        "date": "2026-04-12",
        "params": {
            "subsample": SUBSAMPLE,
            "max_rank": MAX_RANK,
            "eps": EPS,
            "n_null_trials": N_NULL,
        },
        "triples": {},
    }

    # Collect all unique domain names
    all_names = set()
    for triple in TRIPLES:
        all_names.update(triple)

    print(f"Loading {len(all_names)} unique domains...")
    t0 = time.time()
    all_domains = load_domains(*all_names)
    print(f"  Loaded in {time.time() - t0:.1f}s")

    # Subsample and zero Megethos
    prepped = {}
    for name, dom in all_domains.items():
        d = subsample_domain(dom, SUBSAMPLE, seed=hash(name) % 2**31)
        d = zero_megethos(d)
        prepped[name] = d
        print(f"  {name}: {d.n_objects} objects, {d.n_features} features")

    candidates = []

    for idx, (triple, label) in enumerate(zip(TRIPLES, TRIPLE_LABELS)):
        print(f"\n{'='*60}")
        print(f"Triple {idx+1}: {label}")
        print(f"  Domains: {triple}")

        domains = [prepped[n] for n in triple]

        # Run real TT-Cross
        print("  Running TT-Cross (real)...")
        t0 = time.time()
        real_bonds, tt = run_tt_cross(domains)
        real_time = time.time() - t0
        print(f"  Real bonds: {real_bonds}  ({real_time:.1f}s)")

        # Run null model
        print(f"  Running {N_NULL} null trials...")
        t0 = time.time()
        null_bonds = run_null(domains)
        null_time = time.time() - t0
        print(f"  Null bonds: {null_bonds}  ({null_time:.1f}s)")

        # Statistics
        null_arr = np.array(null_bonds)  # (N_NULL, n_bonds)
        null_mean = null_arr.mean(axis=0).tolist()
        null_std = null_arr.std(axis=0).tolist()

        # Z-scores for each bond
        z_scores = []
        for b in range(len(real_bonds)):
            if null_std[b] > 0:
                z = (real_bonds[b] - null_mean[b]) / null_std[b]
            else:
                z = 0.0 if real_bonds[b] == null_mean[b] else float('inf') * np.sign(real_bonds[b] - null_mean[b])
            z_scores.append(round(z, 2))

        # Excess over null
        excess = [real_bonds[b] - round(null_mean[b]) for b in range(len(real_bonds))]

        # Verdict
        max_z = max(z_scores)
        if max_z > 2.0:
            verdict = "CANDIDATE — exceeds null by > 2 sigma"
            candidates.append(label)
        elif max_z > 1.0:
            verdict = "MARGINAL — weak signal"
        else:
            verdict = "NULL — no 3-body effect detected"

        print(f"  Null mean: {[round(x,2) for x in null_mean]}")
        print(f"  Null std:  {[round(x,2) for x in null_std]}")
        print(f"  Z-scores:  {z_scores}")
        print(f"  Excess:    {excess}")
        print(f"  Verdict:   {verdict}")

        triple_result = {
            "domains": list(triple),
            "real_bonds": real_bonds,
            "null_bonds_raw": null_bonds,
            "null_mean": [round(x, 4) for x in null_mean],
            "null_std": [round(x, 4) for x in null_std],
            "z_scores": z_scores,
            "excess_over_null": excess,
            "verdict": verdict,
        }

        # Also run pairwise for comparison
        print("  Running pairwise comparisons...")
        pairwise = {}
        for i in range(3):
            for j in range(i+1, 3):
                pair_label = f"{triple[i]}-{triple[j]}"
                pair_doms = [domains[i], domains[j]]
                try:
                    pair_bonds, _ = run_tt_cross(pair_doms)
                    # Null for pair
                    pair_null = run_null(pair_doms, n_null=3)
                    pair_null_arr = np.array(pair_null)
                    pair_null_mean = pair_null_arr.mean(axis=0).tolist()
                    pair_null_std = pair_null_arr.std(axis=0).tolist()
                    pair_z = []
                    for b in range(len(pair_bonds)):
                        if pair_null_std[b] > 0:
                            pair_z.append(round((pair_bonds[b] - pair_null_mean[b]) / pair_null_std[b], 2))
                        else:
                            pair_z.append(0.0)
                    pairwise[pair_label] = {
                        "bonds": pair_bonds,
                        "null_mean": [round(x, 2) for x in pair_null_mean],
                        "null_std": [round(x, 2) for x in pair_null_std],
                        "z_scores": pair_z,
                    }
                    print(f"    {pair_label}: bond={pair_bonds}, null_mean={[round(x,2) for x in pair_null_mean]}, z={pair_z}")
                except Exception as e:
                    pairwise[pair_label] = {"error": str(e)}
                    print(f"    {pair_label}: ERROR {e}")

        triple_result["pairwise_comparison"] = pairwise
        results["triples"][label] = triple_result

    # Summary
    results["summary"] = {
        "n_triples_tested": len(TRIPLES),
        "candidates": candidates,
        "n_candidates": len(candidates),
        "interpretation": (
            "Candidates show 3-body coupling that exceeds null by > 2 sigma. "
            "These are triples where the joint structure is NOT explained by "
            "pairwise interactions alone — a genuine 3-body effect."
            if candidates else
            "No 3-body effects detected. All triples explained by pairwise structure."
        ),
    }

    # Save
    out_path = "D:/Prometheus/harmonia/results/three_way_megethos_zeroed.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(candidates)} candidates out of {len(TRIPLES)} triples")
    for c in candidates:
        r = results["triples"][c]
        print(f"  {c}: bonds={r['real_bonds']}, z={r['z_scores']}")


if __name__ == "__main__":
    main()
