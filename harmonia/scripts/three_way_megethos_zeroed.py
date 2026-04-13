"""
Three-way TT-Cross interactions with Megethos zeroed.

Tests whether 3-body interactions reveal structure invisible to pairwise tests.

Strategy: Instead of just looking at TT bond dimensions (which saturate at
max_rank for both real and null), we:
1. Build the coupling tensor via random sampling (N x N x N is too large)
2. Use TT-Cross with eps-based convergence to get the approximation
3. Measure the approximation error (relative) at a FIXED rank for real vs null
4. If real data is better approximated at low rank, it has more structure

Additionally, we compute the "3-body residual": the fraction of variance in
f(i,j,k) NOT explained by pairwise terms f(i,j) + f(j,k) + f(i,k).
"""

import json
import sys
import time
import torch
import numpy as np
import tntorch as tn

sys.path.insert(0, "D:/Prometheus")
from harmonia.src.domain_index import load_domains, DomainIndex
from harmonia.src.coupling import CouplingScorer

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
N_NULL = 5
# Focus on the low ranks where differences would appear
# (everything converges to zero error by rank ~6-8 for both real and null)
TEST_RANKS = [2, 3, 4, 5, 6, 8]
N_EVAL_POINTS = 3000  # random points to evaluate approximation error


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


def compute_coupling_scores(scorer, domains, indices):
    """Compute coupling scores for given index tuples."""
    grid_indices = [indices[:, d].long() for d in range(len(domains))]
    return scorer(*grid_indices)


def eval_tt_batch(tt, indices):
    """Evaluate TT tensor at a batch of index tuples."""
    result = tt.cores[0][0, indices[:, 0], :]  # (batch, r0)
    for d in range(1, len(tt.cores)):
        sliced = tt.cores[d][:, indices[:, d], :].permute(1, 0, 2)  # (batch, r_{d-1}, r_d)
        result = torch.einsum('br,brs->bs', result, sliced)
    return result.squeeze(-1)


def measure_tt_approx_error(domains, scorer, rank, n_eval=N_EVAL_POINTS, seed=0):
    """
    Fit TT-Cross at a fixed rank, then measure approximation error on
    held-out random index tuples.

    Returns relative error = ||f - f_tt|| / ||f|| estimated on random samples.
    """
    grid = [torch.arange(dom.n_objects) for dom in domains]

    def func(x):
        indices = [x[:, i].long() for i in range(len(domains))]
        return scorer(*indices)

    # Fit TT at fixed rank
    tt = tn.cross(
        function=func,
        domain=grid,
        function_arg="matrix",
        ranks_tt=rank,
        eps=1e-6,  # Tight eps so rank is the binding constraint
        max_iter=15,
        verbose=False,
        suppress_warnings=True,
    )

    # Get actual converged ranks
    actual_ranks = tt.ranks_tt.tolist()[1:-1]

    # Evaluate on random test points
    rng = np.random.RandomState(seed)
    test_indices = torch.zeros(n_eval, len(domains), dtype=torch.long)
    for d in range(len(domains)):
        test_indices[:, d] = torch.from_numpy(
            rng.randint(0, domains[d].n_objects, n_eval)
        )

    # True values
    true_vals = func(test_indices)

    # TT-approximated values via manual core contraction
    tt_vals = eval_tt_batch(tt, test_indices)

    # Relative error
    residual = (true_vals.float() - tt_vals.float())
    rel_error = residual.norm().item() / true_vals.float().norm().clamp(min=1e-8).item()

    return rel_error, actual_ranks


def measure_three_body_residual(domains, scorer, n_samples=10000, seed=42):
    """
    Measure 3-body residual: variance in f(i,j,k) not explained by
    pairwise terms f_AB(i,j) + f_BC(j,k) + f_AC(i,k).

    We estimate the pairwise contributions by sampling.
    """
    rng = np.random.RandomState(seed)
    n = n_samples

    # Generate random triples
    idx = torch.zeros(n, 3, dtype=torch.long)
    for d in range(3):
        idx[:, d] = torch.from_numpy(rng.randint(0, domains[d].n_objects, n))

    # Full 3-way score
    full_scores = compute_coupling_scores(scorer, domains, idx).float()

    # Pairwise scores (using 2-domain CouplingScorer for each pair)
    pair_scores = torch.zeros(n)
    for a, b in [(0,1), (1,2), (0,2)]:
        pair_doms = [domains[a], domains[b]]
        pair_scorer = CouplingScorer(pair_doms)
        pair_idx = torch.stack([idx[:, a], idx[:, b]], dim=1)
        ps = pair_scorer.score_batch(pair_idx).float()
        pair_scores += ps

    # Linear regression of full_scores on pair_scores to find best fit
    # This avoids scale mismatch between sum-of-3-pairs and single-triple
    full_mean = full_scores.mean()
    pair_centered = pair_scores - pair_scores.mean()
    full_centered = full_scores - full_mean
    beta = (pair_centered * full_centered).sum() / (pair_centered ** 2).sum().clamp(min=1e-8)
    pairwise_pred = full_mean + beta * pair_centered
    residual = full_scores - pairwise_pred

    # R-squared: how much variance does pairwise explain?
    ss_total = ((full_scores - full_mean) ** 2).sum().item()
    ss_residual = (residual ** 2).sum().item()

    if ss_total < 1e-12:
        r_squared = 1.0
        three_body_frac = 0.0
    else:
        r_squared = 1.0 - ss_residual / ss_total
        three_body_frac = ss_residual / ss_total

    return {
        "r_squared_pairwise": round(r_squared, 6),
        "three_body_fraction": round(three_body_frac, 6),
        "full_std": round(full_scores.std().item(), 6),
        "residual_std": round(residual.std().item(), 6),
    }


def main():
    results = {
        "experiment": "3-way TT-Cross with Megethos zeroed",
        "date": "2026-04-12",
        "method": (
            "Two complementary approaches: "
            "(1) TT-Cross approximation error at fixed ranks (real vs null) — "
            "if real data has lower error at the same rank, it has more low-rank structure. "
            "(2) Three-body residual — fraction of variance not explained by pairwise terms."
        ),
        "params": {
            "subsample": SUBSAMPLE,
            "test_ranks": TEST_RANKS,
            "n_eval_points": N_EVAL_POINTS,
            "n_null_trials": N_NULL,
            "eps": 1e-3,
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
        scorer = CouplingScorer(domains)

        # --- Part 1: Three-body residual ---
        print("  Computing 3-body residual...")
        residual_info = measure_three_body_residual(domains, scorer)
        print(f"    R^2 (pairwise): {residual_info['r_squared_pairwise']:.4f}")
        print(f"    3-body fraction: {residual_info['three_body_fraction']:.4f}")

        # --- Part 2: TT-Cross at fixed ranks, real vs null ---
        print("  Measuring TT approx error at fixed ranks...")
        real_errors = {}
        for rank in TEST_RANKS:
            err, actual_r = measure_tt_approx_error(domains, scorer, rank, seed=0)
            real_errors[rank] = {"rel_error": round(err, 6), "actual_ranks": actual_r}
            print(f"    rank={rank}: rel_error={err:.4f}, actual_ranks={actual_r}")

        # Null: shuffle middle domain
        print(f"  Running {N_NULL} null trials per rank...")
        null_errors = {r: [] for r in TEST_RANKS}
        for trial in range(N_NULL):
            perm = torch.randperm(domains[1].n_objects)
            shuffled_feats = domains[1].features[perm].clone()
            shuffled_dom = DomainIndex(domains[1].name + "_shuf", domains[1].labels, shuffled_feats)
            null_doms = [domains[0], shuffled_dom, domains[2]]
            null_scorer = CouplingScorer(null_doms)

            for rank in TEST_RANKS:
                err, _ = measure_tt_approx_error(null_doms, null_scorer, rank, seed=trial+100)
                null_errors[rank].append(round(err, 6))

        # Compare real vs null at each rank
        rank_analysis = {}
        any_significant = False
        for rank in TEST_RANKS:
            null_arr = np.array(null_errors[rank])
            null_mean = null_arr.mean()
            null_std = null_arr.std()
            real_err = real_errors[rank]["rel_error"]

            # Lower error = more structure = GOOD. So z < -2 means real has MORE structure
            if null_std > 1e-8:
                z = (real_err - null_mean) / null_std
            else:
                z = 0.0

            rank_analysis[rank] = {
                "real_error": real_err,
                "null_mean": round(float(null_mean), 6),
                "null_std": round(float(null_std), 6),
                "z_score": round(float(z), 2),
                "null_errors": null_errors[rank],
            }

            if z < -2.0:
                any_significant = True

            print(f"    rank={rank}: real={real_err:.4f}, null={null_mean:.4f}+/-{null_std:.4f}, z={z:.2f}")

        # Verdict
        if any_significant:
            verdict = "CANDIDATE - real data has significantly lower TT approx error than null"
            candidates.append(label)
        elif residual_info["three_body_fraction"] > 0.1:
            verdict = "MARGINAL - large 3-body residual but TT error not significantly different"
        else:
            verdict = "NULL - no 3-body effect detected"

        print(f"  Verdict: {verdict}")

        results["triples"][label] = {
            "domains": list(triple),
            "three_body_residual": residual_info,
            "rank_analysis": {str(k): v for k, v in rank_analysis.items()},
            "real_errors": {str(k): v for k, v in real_errors.items()},
            "verdict": verdict,
        }

    # Summary
    results["summary"] = {
        "n_triples_tested": len(TRIPLES),
        "candidates": candidates,
        "n_candidates": len(candidates),
        "interpretation": (
            "Candidates show 3-body coupling where TT-Cross approximation error "
            "at fixed rank is significantly lower for real data than null (shuffled). "
            "This means the real coupling tensor has more low-rank structure than noise."
            if candidates else
            "No 3-body effects detected. All triples' coupling tensors are equally "
            "well (or poorly) approximated by low-rank TT at every tested rank, "
            "meaning real and shuffled data have comparable structure. "
            "The Megethos-zeroed landscape is genuinely flat for 3-body interactions."
        ),
    }

    # Save
    out_path = "D:/Prometheus/harmonia/results/three_way_megethos_zeroed.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(candidates)} candidates out of {len(TRIPLES)} triples")
    if candidates:
        for c in candidates:
            r = results["triples"][c]
            print(f"  {c}: 3-body frac={r['three_body_residual']['three_body_fraction']}")
    else:
        print("  No 3-body effects survive Megethos zeroing.")


if __name__ == "__main__":
    main()
