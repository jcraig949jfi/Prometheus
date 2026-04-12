"""
Coupling Score — The value function that TT-Cross calls.

Given indices into N mathematical domains, computes a statistical coupling
score that measures how much structure exists at that combination of objects.

The score is designed so that:
  - 0.0 = no detectable coupling (noise)
  - 1.0 = maximum coupling (perfect co-constraint)

TT-Cross adaptively samples this function to discover which domain
combinations have low-rank (real) structure vs high-rank (noise).
"""
import torch
from typing import Optional
from harmonia.src.domain_index import DomainIndex


class CouplingScorer:
    """
    Computes pairwise feature coupling between objects across domains.

    For a set of domain indices (i, j, k, ...), the coupling score
    measures how aligned the feature vectors are across all domain pairs.
    Uses cosine similarity aggregated across pairs, transformed to [0, 1].

    This is the lightweight version — fast enough for TT-Cross's ~10K evals.
    The battery validates the structure TT-Cross discovers afterward.
    """

    def __init__(self, domains: list[DomainIndex], device: str = "cpu"):
        self.domains = domains
        self.n_domains = len(domains)
        self.device = device

        # Precompute normalized features for cosine similarity
        self._normed = []
        for dom in domains:
            f = dom.features.to(device)
            norms = f.norm(dim=1, keepdim=True).clamp(min=1e-8)
            self._normed.append(f / norms)

        # Precompute cross-domain projection matrices for feature alignment.
        # When domains have different feature dimensions, we project both
        # into a shared space via random projection (preserves distances).
        self._projections = {}
        max_dim = max(dom.n_features for dom in domains)
        for i, dom in enumerate(domains):
            if dom.n_features < max_dim:
                # Random projection to shared dimension
                torch.manual_seed(42 + i)
                proj = torch.randn(dom.n_features, max_dim, device=device)
                proj = proj / proj.norm(dim=1, keepdim=True)
                self._projections[i] = proj
            else:
                self._projections[i] = None
        self._shared_dim = max_dim

    def _project(self, domain_idx: int, obj_indices: torch.Tensor) -> torch.Tensor:
        """Get projected feature vectors for objects in a domain."""
        feats = self._normed[domain_idx][obj_indices]  # (batch, D_i)
        proj = self._projections[domain_idx]
        if proj is not None:
            feats = feats @ proj  # (batch, shared_dim)
            feats = feats / feats.norm(dim=1, keepdim=True).clamp(min=1e-8)
        return feats

    def score_batch(self, indices: torch.Tensor) -> torch.Tensor:
        """
        Compute coupling scores for a batch of multi-domain index tuples.

        Args:
            indices: (batch, n_domains) integer tensor of object indices

        Returns:
            (batch,) float tensor of coupling scores in [0, 1]
        """
        batch_size = indices.shape[0]

        # Project all domains into shared space
        projected = []
        for d in range(self.n_domains):
            projected.append(self._project(d, indices[:, d]))

        # Compute mean pairwise cosine similarity across all domain pairs
        n_pairs = 0
        total_sim = torch.zeros(batch_size, device=self.device)
        for i in range(self.n_domains):
            for j in range(i + 1, self.n_domains):
                # Cosine similarity (already normalized)
                sim = (projected[i] * projected[j]).sum(dim=1)
                total_sim += sim
                n_pairs += 1

        mean_sim = total_sim / max(n_pairs, 1)

        # Transform from [-1, 1] cosine range to [0, 1] score
        score = (mean_sim + 1.0) / 2.0
        return score

    def __call__(self, *grid_indices) -> torch.Tensor:
        """
        TT-Cross compatible interface.

        Args:
            *grid_indices: N tensors, each shape (batch,) with integer indices
                          into the corresponding domain

        Returns:
            (batch,) float tensor of coupling scores
        """
        indices = torch.stack(grid_indices, dim=-1)  # (batch, n_domains)
        return self.score_batch(indices)


class DistributionalCoupling(CouplingScorer):
    """
    Extended coupling scorer that uses M4/M2^2 (kurtosis ratio) to detect
    non-Gaussian structure in feature distributions conditioned on other domains.

    This is closer to what the battery actually measures — tail behavior
    and distributional deviation, not just pairwise similarity.
    """

    def __init__(self, domains: list[DomainIndex], device: str = "cpu",
                 window: int = 50):
        super().__init__(domains, device)
        self.window = window

        # Precompute M4/M2^2 for each feature in each domain
        self._kurtosis = []
        for dom in domains:
            f = dom.features.to(device)
            m2 = (f ** 2).mean(dim=0)
            m4 = (f ** 4).mean(dim=0)
            # M4/M2^2 — Gaussian = 3.0, excess signals non-trivial structure
            k = m4 / (m2 ** 2).clamp(min=1e-8)
            self._kurtosis.append(k)

    def score_batch(self, indices: torch.Tensor) -> torch.Tensor:
        """
        Coupling score combining cosine alignment with distributional
        deviation. Objects whose features deviate from Gaussian in
        correlated ways score higher.
        """
        batch_size = indices.shape[0]

        projected = []
        for d in range(self.n_domains):
            projected.append(self._project(d, indices[:, d]))

        # Cosine component (same as parent)
        n_pairs = 0
        cosine_sum = torch.zeros(batch_size, device=self.device)
        for i in range(self.n_domains):
            for j in range(i + 1, self.n_domains):
                sim = (projected[i] * projected[j]).sum(dim=1)
                cosine_sum += sim
                n_pairs += 1
        cosine_score = (cosine_sum / max(n_pairs, 1) + 1.0) / 2.0

        # Kurtosis deviation component — how much do selected objects
        # deviate from the domain-level kurtosis?
        kurtosis_score = torch.zeros(batch_size, device=self.device)
        for d in range(self.n_domains):
            feats = self._normed[d][indices[:, d]]  # (batch, D_d)
            # Per-object deviation from domain kurtosis
            obj_k = feats ** 4 / (feats ** 2 + 1e-8) ** 2
            domain_k = self._kurtosis[d].unsqueeze(0)
            deviation = (obj_k - domain_k).abs().mean(dim=1)
            kurtosis_score += deviation

        kurtosis_score = kurtosis_score / self.n_domains
        # Normalize to [0, 1] via sigmoid
        kurtosis_score = torch.sigmoid(kurtosis_score - 1.0)

        # Weighted combination: cosine alignment + distributional signal
        score = 0.6 * cosine_score + 0.4 * kurtosis_score
        return score
