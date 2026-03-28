"""
Tensor Navigator — Tensor train compression and navigation of the concept space.

Compresses the full 95^3 interaction tensor into a tensor train (TT) format
that fits in kilobytes instead of megabytes, and supports:

1. Top-K extraction: find the K highest-scoring triples without decompressing
2. Region queries: score any (i, j, k) triple in microseconds via TT cores
3. Incremental update: add new concepts without full recomputation
4. Exploration tracking: mark explored vs unexplored regions
5. Frontier detection: find the highest-scoring UNEXPLORED triples

The TT cores ARE the navigable map. This replaces brute-force LLM-based
search with microsecond tensor operations.

Usage:
    python tensor_navigator.py                     # Full scan + report
    python tensor_navigator.py --top 50            # Top 50 triples
    python tensor_navigator.py --unexplored        # Only unexplored triples
    python tensor_navigator.py --rank 15           # Higher rank = more accuracy
    python tensor_navigator.py --save lattice.json # Export for other agents
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import tensorly as tl
from tensorly.decomposition import tensor_train

# Project imports
ORGANISMS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ORGANISMS_DIR.parent))
from organisms.concept_tensor import (
    get_concept_names,
    get_feature_matrix,
    compute_triple_tensor_fast,
    compute_pairwise_interactions,
    compute_type_compatibility_matrix,
    N_FEATURES,
    FEATURE_NAMES,
)

TT_CACHE = ORGANISMS_DIR / "tensor_cache"
TT_CACHE.mkdir(exist_ok=True)


# ============================================================
# Tensor Train Operations
# ============================================================

class TensorTrainNavigator:
    """
    Navigates the compressed concept interaction space.

    The navigator holds:
    - TT cores: the compressed representation of the full interaction tensor
    - Concept names: the index mapping
    - Exploration mask: which triples have been explored
    - Scores cache: precomputed from TT for fast top-K
    """

    def __init__(self, rank: int = 10):
        self.rank = rank
        self.cores = None
        self.concept_names: List[str] = []
        self.n_concepts = 0
        self.full_tensor: Optional[np.ndarray] = None
        self.explored: Optional[np.ndarray] = None  # Boolean mask
        self.pairwise: Optional[Dict[str, np.ndarray]] = None
        self._build_time = 0.0
        self._compression_ratio = 0.0

    def build(self, use_type_compat: bool = True) -> "TensorTrainNavigator":
        """
        Build the full pipeline: encode -> interact -> compress.
        Uses only hand-seeded mathematical features (no Coeus/Nous data).

        If use_type_compat=True (default), bakes type compatibility awareness
        into the tensor scores: pairs with organisms but zero compatible
        operations get zeroed, pairs with many compatible ops get boosted.

        Returns self for chaining.
        """
        t0 = time.perf_counter()

        # Step 1: Feature matrix (pure mathematical properties, no LLM data)
        matrix, _ = get_feature_matrix()

        self.concept_names = get_concept_names()
        self.n_concepts = len(self.concept_names)

        # Step 1.5: Type compatibility matrix (from actual organisms)
        type_compat = None
        type_boost = None
        if use_type_compat:
            type_compat, _ = compute_type_compatibility_matrix()
            n_compat_pairs = int(np.sum((type_compat + type_compat.T) > 0) / 2)
            self._n_compat_pairs = n_compat_pairs

        # Step 2: Compute pairwise interactions (type-aware if available)
        self.pairwise = compute_pairwise_interactions(matrix, type_compat=type_compat)
        type_boost = self.pairwise.get("type_boost")

        # Step 3: Compute full triple tensor (type-aware if available)
        self.full_tensor = compute_triple_tensor_fast(matrix, type_boost=type_boost)

        # Step 4: Tensor train decomposition
        tt_rank = [1, self.rank, self.rank, 1]
        self.cores = tensor_train(tl.tensor(self.full_tensor), rank=tt_rank)

        # Step 5: Measure reconstruction error
        self._compute_reconstruction_error()

        # Step 6: Initialize exploration mask (empty — populated by real composition data only)
        self.explored = np.zeros(
            (self.n_concepts, self.n_concepts, self.n_concepts), dtype=bool
        )

        # Compute stats
        full_entries = self.n_concepts ** 3
        tt_entries = sum(c.size for c in self.cores)
        self._compression_ratio = full_entries / tt_entries if tt_entries > 0 else 0
        self._build_time = time.perf_counter() - t0

        return self

    def _compute_reconstruction_error(self):
        """
        Measure how much information the TT compression loses.

        Computes per-concept error concentration to detect whether
        TT is smoothing away unexpected structure (the frontier we
        care about most). If errors cluster in specific concept regions,
        those regions may contain the novel bridges that rank-limited
        TT discards as noise.
        """
        if self.cores is None or self.full_tensor is None:
            return

        # Reconstruct full tensor from TT cores
        reconstructed = tl.tt_to_tensor(self.cores)
        error = self.full_tensor - reconstructed

        # Global error stats
        self._recon_rmse = float(np.sqrt(np.mean(error ** 2)))
        self._recon_max_error = float(np.max(np.abs(error)))
        tensor_range = float(np.max(self.full_tensor) - np.min(self.full_tensor))
        self._recon_nrmse = self._recon_rmse / tensor_range if tensor_range > 0 else 0.0

        # Per-concept error: for each concept, how much error is in
        # all triples involving that concept?
        N = self.n_concepts
        per_concept_mse = np.zeros(N, dtype=np.float64)
        for i in range(N):
            # All triples where concept i participates (3 slices)
            slice_err = np.concatenate([
                error[i, :, :].flatten(),
                error[:, i, :].flatten(),
                error[:, :, i].flatten(),
            ])
            per_concept_mse[i] = np.mean(slice_err ** 2)

        self._per_concept_rmse = np.sqrt(per_concept_mse).astype(np.float32)

        # Identify concepts where TT struggles most (top error concentrators)
        ranked = np.argsort(self._per_concept_rmse)[::-1]
        self._error_hotspots = [
            (self.concept_names[idx], float(self._per_concept_rmse[idx]))
            for idx in ranked[:10]
        ]

        # Per-triple error for the top-K triples (do the highest-scoring
        # triples have higher or lower error than average?)
        flat_scores = self.full_tensor.flatten()
        top_100_idx = np.argsort(flat_scores)[-100:]
        top_100_errors = np.abs(error.flatten()[top_100_idx])
        self._top100_mean_error = float(np.mean(top_100_errors))
        self._top100_max_error = float(np.max(top_100_errors))

    def tt_query(self, i: int, j: int, k: int) -> float:
        """
        Query the TT-approximated score for triple (i, j, k).
        This is O(rank^2) instead of O(N^3).
        """
        if self.cores is None:
            raise RuntimeError("Navigator not built. Call .build() first.")
        # Contract the TT cores at indices i, j, k
        result = self.cores[0][:, i, :]  # (1, rank)
        result = result @ self.cores[1][:, j, :]  # (1, rank)
        result = result @ self.cores[2][:, k, :]  # (1, 1)
        return float(result.squeeze())

    def top_k_triples(
        self,
        k: int = 100,
        unexplored_only: bool = False,
        min_score: float = 0.0,
        diversity_cap: int = 0,
    ) -> List[Dict]:
        """
        Find the top-K highest-scoring concept triples.

        For small N (95), we reconstruct from TT and do argsort.
        For larger N, we'd use greedy TT traversal — but 95^3 fits in 3MB
        so reconstruction is fine and exact.

        If diversity_cap > 0, no single concept can appear in more than
        diversity_cap triples (ensures diverse frontier, not just
        "Category Theory + everything").
        """
        if self.full_tensor is None:
            raise RuntimeError("Navigator not built. Call .build() first.")

        tensor = self.full_tensor.copy()

        # Mask explored if requested
        if unexplored_only and self.explored is not None:
            tensor[self.explored] = 0.0

        # Mask diagonal (same-concept)
        for i in range(self.n_concepts):
            tensor[i, i, :] = 0
            tensor[i, :, i] = 0
            tensor[:, i, i] = 0

        # Mask below min_score
        tensor[tensor < min_score] = 0.0

        # Find top-K unique triples
        flat = tensor.flatten()
        top_indices = np.argsort(flat)[::-1]

        results = []
        seen = set()
        concept_counts: Dict[int, int] = {}
        for idx in top_indices:
            if len(results) >= k:
                break

            i = int(idx // (self.n_concepts * self.n_concepts))
            remainder = int(idx % (self.n_concepts * self.n_concepts))
            j = int(remainder // self.n_concepts)
            k_idx = int(remainder % self.n_concepts)

            # Canonical ordering for dedup
            triple = tuple(sorted([i, j, k_idx]))
            if triple in seen or len(set(triple)) < 3:
                continue

            # Diversity cap check
            if diversity_cap > 0:
                a, b, c = triple
                if (concept_counts.get(a, 0) >= diversity_cap or
                    concept_counts.get(b, 0) >= diversity_cap or
                    concept_counts.get(c, 0) >= diversity_cap):
                    continue

            seen.add(triple)

            score = float(tensor[i, j, k_idx])
            if score <= 0:
                break

            a, b, c = triple
            is_explored = bool(self.explored[a, b, c]) if self.explored is not None else False

            # Update diversity counts
            for idx_c in [a, b, c]:
                concept_counts[idx_c] = concept_counts.get(idx_c, 0) + 1

            results.append({
                "rank": len(results) + 1,
                "concepts": [
                    self.concept_names[a],
                    self.concept_names[b],
                    self.concept_names[c],
                ],
                "indices": [a, b, c],
                "score": score,
                "explored": is_explored,
                "pairwise_scores": {
                    f"{self.concept_names[a]}_x_{self.concept_names[b]}": float(self.pairwise["combined"][a, b]),
                    f"{self.concept_names[a]}_x_{self.concept_names[c]}": float(self.pairwise["combined"][a, c]),
                    f"{self.concept_names[b]}_x_{self.concept_names[c]}": float(self.pairwise["combined"][b, c]),
                },
            })

        return results

    def top_k_pairs(self, k: int = 50, unexplored_only: bool = False) -> List[Dict]:
        """Find the top-K highest-scoring concept pairs."""
        if self.pairwise is None:
            raise RuntimeError("Navigator not built. Call .build() first.")

        combined = self.pairwise["combined"].copy()

        # Mask diagonal
        np.fill_diagonal(combined, 0.0)

        flat = combined.flatten()
        top_indices = np.argsort(flat)[::-1]

        results = []
        seen = set()
        for idx in top_indices:
            if len(results) >= k:
                break
            i, j = divmod(int(idx), self.n_concepts)
            pair = (min(i, j), max(i, j))
            if pair in seen or i == j:
                continue
            seen.add(pair)

            a, b = pair
            results.append({
                "rank": len(results) + 1,
                "concepts": [self.concept_names[a], self.concept_names[b]],
                "score": float(combined[a, b]),
                "novelty": float(self.pairwise["novelty"][a, b]),
                "complementarity": float(self.pairwise["complementarity"][a, b]),
                "resonance": float(self.pairwise["resonance"][a, b]),
            })

        return results

    def frontier(self, k: int = 100, diversity_cap: int = 0) -> List[Dict]:
        """
        The exploration frontier: highest-scoring UNEXPLORED triples.
        This is the main output for steering Nous/Hephaestus.

        diversity_cap: max times any concept can appear. 0 = no limit.
        """
        return self.top_k_triples(k=k, unexplored_only=True, diversity_cap=diversity_cap)

    def concept_heat_map(self) -> List[Dict]:
        """
        For each concept, compute its total interaction energy
        (sum of all triple scores involving it). High-energy concepts
        are the most promising exploration targets.
        """
        if self.full_tensor is None:
            raise RuntimeError("Navigator not built.")

        energies = []
        for i, name in enumerate(self.concept_names):
            total = float(np.sum(self.full_tensor[i, :, :]))
            unexplored_energy = 0.0
            if self.explored is not None:
                mask = ~self.explored[i, :, :]
                unexplored_energy = float(np.sum(self.full_tensor[i, :, :] * mask))

            energies.append({
                "concept": name,
                "total_energy": total,
                "unexplored_energy": unexplored_energy,
                "exploration_ratio": 1.0 - (unexplored_energy / total if total > 0 else 0),
            })

        energies.sort(key=lambda x: -x["unexplored_energy"])
        return energies

    def stats(self) -> Dict:
        """Return navigator statistics."""
        n_explored = int(np.sum(self.explored)) // 6 if self.explored is not None else 0
        total_triples = self.n_concepts * (self.n_concepts - 1) * (self.n_concepts - 2) // 6

        result = {
            "n_concepts": self.n_concepts,
            "n_features": N_FEATURES,
            "total_pairs": self.n_concepts * (self.n_concepts - 1) // 2,
            "total_triples": total_triples,
            "explored_triples": n_explored,
            "unexplored_triples": total_triples - n_explored,
            "exploration_pct": n_explored / total_triples * 100 if total_triples > 0 else 0,
            "tt_rank": self.rank,
            "tt_entries": sum(c.size for c in self.cores) if self.cores else 0,
            "full_entries": self.n_concepts ** 3,
            "compression_ratio": self._compression_ratio,
            "build_time_s": self._build_time,
            "tensor_memory_mb": self.full_tensor.nbytes / 1024 / 1024 if self.full_tensor is not None else 0,
            "tt_memory_kb": sum(c.nbytes for c in self.cores) / 1024 if self.cores else 0,
        }

        # Reconstruction error stats (if computed)
        if hasattr(self, "_recon_rmse"):
            result["reconstruction"] = {
                "rmse": self._recon_rmse,
                "nrmse": self._recon_nrmse,
                "max_error": self._recon_max_error,
                "top100_mean_error": self._top100_mean_error,
                "top100_max_error": self._top100_max_error,
                "error_hotspots": self._error_hotspots,
            }

        return result

    def export_frontier(self, path: str, k: int = 100):
        """Export the exploration frontier as JSON for Nous/Hephaestus."""
        frontier = self.frontier(k=k)
        heat = self.concept_heat_map()
        stats = self.stats()

        payload = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "stats": stats,
            "frontier": frontier,
            "concept_heat_map": heat[:20],  # Top 20 hottest concepts
            "top_pairs": self.top_k_pairs(k=20),
        }

        with open(path, "w") as f:
            json.dump(payload, f, indent=2)

    def export_for_nous(self, path: Optional[str] = None) -> str:
        """
        Export frontier as a Nous-compatible concept triple list.
        Format matches what Nous expects for targeted exploration.
        """
        if path is None:
            path = str(ORGANISMS_DIR / "tensor_frontier.json")

        frontier = self.frontier(k=200)

        # Format for Nous: list of concept name triples
        triples = []
        for entry in frontier:
            triples.append({
                "concepts": entry["concepts"],
                "tensor_score": entry["score"],
                "explored": entry["explored"],
            })

        with open(path, "w") as f:
            json.dump({"frontier_triples": triples, "source": "tensor_navigator"}, f, indent=2)

        return path


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Tensor Navigator - Explore the concept space")
    parser.add_argument("--top", type=int, default=20, help="Number of top triples to show")
    parser.add_argument("--unexplored", action="store_true", help="Only show unexplored triples")
    parser.add_argument("--rank", type=int, default=10, help="TT rank (higher = more accurate)")
    parser.add_argument("--save", type=str, default=None, help="Export frontier to JSON")
    parser.add_argument("--pairs", action="store_true", help="Show top pairs instead of triples")
    parser.add_argument("--heat", action="store_true", help="Show concept heat map")
    parser.add_argument("--export-nous", action="store_true", help="Export frontier for Nous")
    parser.add_argument("--diversity", type=int, default=0,
                        help="Max times any concept appears in results (0=unlimited)")
    parser.add_argument("--diagnostics", action="store_true",
                        help="Show TT reconstruction error diagnostics")
    args = parser.parse_args()

    print("=" * 70)
    print("  TENSOR NAVIGATOR — Concept Space Exploration at Computational Speed")
    print("=" * 70)
    print()

    nav = TensorTrainNavigator(rank=args.rank)
    nav.build()

    s = nav.stats()
    print(f"  Concepts:       {s['n_concepts']}")
    print(f"  Features:       {s['n_features']} dimensions")
    print(f"  Total triples:  {s['total_triples']:,}")
    print(f"  Explored:       {s['explored_triples']:,} ({s['exploration_pct']:.1f}%)")
    print(f"  Unexplored:     {s['unexplored_triples']:,}")
    print(f"  TT rank:        {s['tt_rank']}")
    print(f"  Compression:    {s['compression_ratio']:.0f}x "
          f"({s['tensor_memory_mb']:.1f} MB -> {s['tt_memory_kb']:.1f} KB)")
    print(f"  Build time:     {s['build_time_s']:.3f}s")
    print()

    # Reconstruction error diagnostics
    if "reconstruction" in s:
        r = s["reconstruction"]
        print(f"  Reconstruction Error:")
        print(f"    RMSE:           {r['rmse']:.6f}")
        print(f"    NRMSE:          {r['nrmse']:.4f} ({r['nrmse']*100:.2f}% of tensor range)")
        print(f"    Max error:      {r['max_error']:.6f}")
        print(f"    Top-100 mean:   {r['top100_mean_error']:.6f}")
        print(f"    Top-100 max:    {r['top100_max_error']:.6f}")
        print()

    if args.diagnostics and "reconstruction" in s:
        r = s["reconstruction"]
        print("TT RECONSTRUCTION ERROR — PER-CONCEPT HOTSPOTS:")
        print("-" * 60)
        print("  Concepts where TT loses the most information.")
        print("  High error = TT may be smoothing away novel structure.")
        print()
        max_err = r["error_hotspots"][0][1] if r["error_hotspots"] else 1.0
        for name, err in r["error_hotspots"]:
            bar = "#" * int(err / max_err * 40) if max_err > 0 else ""
            print(f"  {name:35s} RMSE={err:.6f}  {bar}")
        print()
        if r["top100_mean_error"] > r["rmse"] * 1.5:
            print("  WARNING: Top-100 triples have higher error than average.")
            print("  The highest-scoring regions may be least accurately represented.")
            print("  Consider increasing --rank to improve frontier accuracy.")
        elif r["top100_mean_error"] < r["rmse"] * 0.5:
            print("  GOOD: Top-100 triples have lower error than average.")
            print("  High-scoring regions are well-represented by the TT.")
        else:
            print("  OK: Error is roughly uniform across the tensor.")
        print()

    if args.heat:
        print("CONCEPT HEAT MAP (top 20 by unexplored energy):")
        print("-" * 60)
        heat = nav.concept_heat_map()
        for h in heat[:20]:
            bar = "#" * int(h["unexplored_energy"] / heat[0]["unexplored_energy"] * 30)
            print(f"  {h['concept']:35s} {h['unexplored_energy']:8.1f}  {bar}")
        print()

    if args.pairs:
        pairs = nav.top_k_pairs(k=args.top)
        print(f"TOP {len(pairs)} CONCEPT PAIRS:")
        print("-" * 70)
        for p in pairs:
            print(f"  {p['rank']:3d}. [{p['score']:.4f}] {p['concepts'][0]} x {p['concepts'][1]}")
            print(f"       nov={p['novelty']:.3f} comp={p['complementarity']:.3f} res={p['resonance']:.3f}")
        print()
    else:
        triples = nav.top_k_triples(k=args.top, unexplored_only=args.unexplored,
                                     diversity_cap=args.diversity)
        label = "UNEXPLORED" if args.unexplored else "ALL"
        print(f"TOP {len(triples)} CONCEPT TRIPLES ({label}):")
        print("-" * 70)
        for t in triples:
            explored_tag = " [EXPLORED]" if t["explored"] else ""
            print(f"  {t['rank']:3d}. [{t['score']:.4f}] "
                  f"{t['concepts'][0]} x {t['concepts'][1]} x {t['concepts'][2]}"
                  f"{explored_tag}")
        print()

    if args.save:
        nav.export_frontier(args.save, k=args.top)
        print(f"Frontier exported to {args.save}")

    if args.export_nous:
        path = nav.export_for_nous()
        print(f"Nous frontier exported to {path}")


if __name__ == "__main__":
    main()
