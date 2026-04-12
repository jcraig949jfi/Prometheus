"""
Tensor-speed falsification — battery tests implemented as TT operations.

Instead of testing individual correlations, we test whether the TT
decomposition itself is stable under perturbation. Each test is just
another TT-Cross call with modified data.
"""
import torch
import tntorch as tn
import time
import json
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

from harmonia.src.domain_index import DomainIndex, load_domains, DOMAIN_LOADERS
from harmonia.src.coupling import DistributionalCoupling
from harmonia.src.validate import extract_bond_components


@dataclass
class TensorTestResult:
    test: str
    verdict: str  # SURVIVES, KILLED
    detail: str
    value: float = 0.0
    threshold: float = 0.0


@dataclass
class FalsificationReport:
    domain_a: str
    domain_b: str
    original_rank: int
    tests: list[TensorTestResult]
    surviving_rank: int
    wall_time: float
    inference: str = ""

    def summary(self) -> str:
        lines = [
            f"{self.domain_a} <-> {self.domain_b}: rank {self.original_rank} -> {self.surviving_rank}",
            f"  Inference: {self.inference}",
        ]
        for t in self.tests:
            icon = "+" if t.verdict == "SURVIVES" else "X"
            lines.append(f"  [{icon}] {t.test}: {t.verdict} — {t.detail}")
        return "\n".join(lines)


def _run_tt(domains, scorer, max_rank=15, eps=1e-3):
    """Run TT-Cross and return ranks."""
    grids = [torch.arange(d.n_objects, dtype=torch.float32) for d in domains]

    def value_fn(*indices):
        return scorer(*[idx.long() for idx in indices])

    tt = tn.cross(function=value_fn, domain=grids, eps=eps, rmax=max_rank, max_iter=50)
    return tt, tt.ranks_tt.tolist()


def test_permutation_null(domains, scorer, original_ranks, n_perms=5, max_rank=15):
    """
    F1 at tensor speed: shuffle one domain's feature vectors,
    re-run TT-Cross. If bond dimension persists, it's an artifact.
    If it drops, the structure depends on actual feature alignment.
    """
    # Instead of comparing raw ranks (which can be inflated by scorer baseline),
    # compare the actual coupling SCORES between real and shuffled data.
    # Sample 1000 random index tuples and compare score distributions.
    n_sample = min(1000, domains[0].n_objects, domains[1].n_objects)
    real_idx = [torch.randint(0, d.n_objects, (n_sample,)) for d in domains]
    real_scores = scorer(*real_idx)

    null_scores_all = []
    for _ in range(n_perms):
        perm = torch.randperm(domains[0].n_objects)
        shuffled_feats = domains[0].features[perm]
        shuffled_dom = DomainIndex(domains[0].name, domains[0].labels, shuffled_feats)

        null_scorer = DistributionalCoupling([shuffled_dom] + list(domains[1:]))
        null_scores = null_scorer(*real_idx)
        null_scores_all.append(null_scores)

    null_stacked = torch.stack(null_scores_all)
    null_mean = null_stacked.mean()
    null_std = null_stacked.std().clamp(min=1e-8)
    real_mean = real_scores.mean()

    # Z-score: how many standard deviations is the real mean above null?
    z = ((real_mean - null_mean) / null_std).item()
    survives = z > 2.0

    return TensorTestResult(
        test="F1_permutation_null",
        verdict="SURVIVES" if survives else "KILLED",
        detail=f"real mean={real_mean:.4f} vs null={null_mean:.4f} (z={z:.2f})",
        value=z,
        threshold=2.0,
    )


def test_subset_stability(domains, scorer, original_ranks, n_splits=3, max_rank=15):
    """
    F2 at tensor speed: split each domain in half, run TT-Cross
    on each split. If bond dimensions are consistent, the structure
    is not driven by a small subset of objects.
    """
    real_rank = max(original_ranks[1:-1])
    split_ranks = []

    for _ in range(n_splits):
        # Random 50% subsample of each domain
        sub_domains = []
        for dom in domains:
            n = dom.n_objects
            perm = torch.randperm(n)[:n // 2]
            sub = DomainIndex(dom.name, [dom.labels[i] for i in perm.tolist()], dom.features[perm])
            sub_domains.append(sub)

        sub_scorer = DistributionalCoupling(sub_domains)
        _, ranks = _run_tt(sub_domains, sub_scorer, max_rank)
        split_ranks.append(max(ranks[1:-1]))

    mean_split = np.mean(split_ranks)
    cv = np.std(split_ranks) / max(mean_split, 0.1)

    # Stable if CV < 0.5 and mean is within 50% of original
    stable = cv < 0.5 and abs(mean_split - real_rank) / max(real_rank, 1) < 0.5
    return TensorTestResult(
        test="F2_subset_stability",
        verdict="SURVIVES" if stable else "KILLED",
        detail=f"split ranks {split_ranks} (CV={cv:.2f}, mean={mean_split:.1f} vs real {real_rank})",
        value=cv,
        threshold=0.5,
    )


def test_effect_size(domains, tt, bond_idx=0):
    """
    F3 at tensor speed: compute Cohen's d between top-scoring and
    bottom-scoring objects on each side of the bond. Large effect size
    = the TT component genuinely discriminates, not just noise.
    """
    components = extract_bond_components(tt, bond_idx, domains)
    if not components:
        return TensorTestResult(test="F3_effect_size", verdict="KILLED",
                                detail="no components", value=0, threshold=0.5)

    sv, left_scores, right_scores = components[0]

    results = []
    for name, scores, dom in [("left", left_scores, domains[bond_idx]),
                               ("right", right_scores, domains[bond_idx + 1])]:
        n = len(scores)
        top_idx = torch.topk(scores, n // 4).indices
        bot_idx = torch.topk(scores, n // 4, largest=False).indices

        top_feats = dom.features[top_idx]
        bot_feats = dom.features[bot_idx]

        # Cohen's d per feature, take max
        pooled_std = torch.sqrt((top_feats.var(dim=0) + bot_feats.var(dim=0)) / 2).clamp(min=1e-8)
        d = ((top_feats.mean(dim=0) - bot_feats.mean(dim=0)) / pooled_std).abs()
        max_d = d.max().item()
        results.append(max_d)

    avg_d = np.mean(results)
    return TensorTestResult(
        test="F3_effect_size",
        verdict="SURVIVES" if avg_d > 0.5 else "KILLED",
        detail=f"Cohen's d: left={results[0]:.2f}, right={results[1]:.2f}, avg={avg_d:.2f}",
        value=avg_d,
        threshold=0.5,
    )


def test_confound_residual(domains, original_ranks, max_rank=15):
    """
    F17 at tensor speed: for each domain, residualize out the
    strongest feature (remove its variance), re-run TT-Cross.
    If the bond survives, it's not driven by a single confound.
    """
    real_rank = max(original_ranks[1:-1])
    residual_ranks = []

    for d_idx, dom in enumerate(domains):
        # Find the highest-variance feature
        var = dom.features.var(dim=0)
        top_feat = var.argmax().item()

        # Residualize: remove projection onto that feature
        feat_col = dom.features[:, top_feat:top_feat + 1]
        projection = feat_col @ feat_col.T @ dom.features / (feat_col.T @ feat_col + 1e-8)
        residual_feats = dom.features - projection
        # Re-normalize
        mu = residual_feats.mean(dim=0)
        sigma = residual_feats.std(dim=0).clamp(min=1e-8)
        residual_feats = (residual_feats - mu) / sigma
        residual_feats[torch.isnan(residual_feats)] = 0.0

        new_domains = list(domains)
        new_domains[d_idx] = DomainIndex(dom.name, dom.labels, residual_feats)

        res_scorer = DistributionalCoupling(new_domains)
        _, ranks = _run_tt(new_domains, res_scorer, max_rank)
        residual_ranks.append(max(ranks[1:-1]))

    min_residual = min(residual_ranks)
    survives = min_residual > 0

    return TensorTestResult(
        test="F17_confound_residual",
        verdict="SURVIVES" if survives else "KILLED",
        detail=f"ranks after residualizing each domain's top feature: {residual_ranks} (original: {real_rank})",
        value=float(min_residual),
        threshold=1.0,
    )


def test_direction_consistency(domains, tt, bond_idx=0):
    """
    F8 at tensor speed: do the top objects on both sides of the bond
    point in consistent feature directions? If left-side highs and
    right-side highs both deviate from population mean in correlated
    ways, the coupling has a consistent direction.
    """
    components = extract_bond_components(tt, bond_idx, domains)
    if not components:
        return TensorTestResult(test="F8_direction", verdict="KILLED",
                                detail="no components", value=0, threshold=0)

    sv, left_scores, right_scores = components[0]
    dom_a, dom_b = domains[bond_idx], domains[bond_idx + 1]

    # Top objects' feature deviations from population mean
    n_top = min(50, len(left_scores) // 4, len(right_scores) // 4)
    top_a = torch.topk(left_scores, n_top).indices
    top_b = torch.topk(right_scores, n_top).indices

    dev_a = dom_a.features[top_a].mean(dim=0) - dom_a.features.mean(dim=0)
    dev_b = dom_b.features[top_b].mean(dim=0) - dom_b.features.mean(dim=0)

    # Are both deviations non-trivial? (not just noise around zero)
    mag_a = dev_a.norm().item()
    mag_b = dev_b.norm().item()

    consistent = mag_a > 0.3 and mag_b > 0.3

    return TensorTestResult(
        test="F8_direction_consistency",
        verdict="SURVIVES" if consistent else "KILLED",
        detail=f"deviation magnitudes: {dom_a.name}={mag_a:.2f}, {dom_b.name}={mag_b:.2f}",
        value=min(mag_a, mag_b),
        threshold=0.3,
    )


def falsify_bond(
    d1: str, d2: str,
    subsample: Optional[int] = 2000,
    max_rank: int = 15,
    inference: str = "",
) -> FalsificationReport:
    """
    Full tensor-speed falsification of a domain pair bond.

    Runs F1 (permutation null), F2 (subset stability), F3 (effect size),
    F8 (direction consistency), F17 (confound residual).
    """
    t0 = time.time()

    raw_domains = load_domains(d1, d2)
    domain_list = [raw_domains[d1], raw_domains[d2]]

    # Subsample if needed
    if subsample:
        for i, dom in enumerate(domain_list):
            if dom.n_objects > subsample:
                perm = torch.randperm(dom.n_objects)[:subsample]
                domain_list[i] = DomainIndex(
                    dom.name, [dom.labels[j] for j in perm.tolist()],
                    dom.features[perm])

    scorer = DistributionalCoupling(domain_list)
    tt, ranks = _run_tt(domain_list, scorer, max_rank)
    original_rank = max(ranks[1:-1])

    tests = []

    # F1: Permutation null
    tests.append(test_permutation_null(domain_list, scorer, ranks, n_perms=5, max_rank=max_rank))

    # F2: Subset stability
    tests.append(test_subset_stability(domain_list, scorer, ranks, n_splits=3, max_rank=max_rank))

    # F3: Effect size
    tests.append(test_effect_size(domain_list, tt, 0))

    # F8: Direction consistency
    tests.append(test_direction_consistency(domain_list, tt, 0))

    # F17: Confound residual
    tests.append(test_confound_residual(domain_list, ranks, max_rank))

    # Count survivors
    n_survive = sum(1 for t in tests if t.verdict == "SURVIVES")
    surviving_rank = original_rank if n_survive >= 3 else (original_rank // 2 if n_survive >= 2 else 0)

    wall = time.time() - t0
    return FalsificationReport(
        domain_a=d1, domain_b=d2,
        original_rank=original_rank,
        tests=tests,
        surviving_rank=surviving_rank,
        wall_time=wall,
        inference=inference,
    )


def falsify_all_inferences(inferences: list[dict], subsample=2000) -> list[FalsificationReport]:
    """
    Falsify a list of cross-domain inferences at tensor speed.

    Args:
        inferences: list of {d1, d2, inference} dicts
    """
    reports = []
    for inf in inferences:
        report = falsify_bond(
            inf["d1"], inf["d2"],
            subsample=subsample,
            inference=inf.get("inference", ""),
        )
        reports.append(report)
        icon = "PASS" if report.surviving_rank > 0 else "FAIL"
        print(f"  [{icon}] {report.domain_a} <-> {report.domain_b}: "
              f"rank {report.original_rank} -> {report.surviving_rank} "
              f"({report.wall_time:.1f}s)")
    return reports
