"""
Operation Tensor — Feature-encode all 81 operations for direct chain scoring.

The concept tensor works at the wrong granularity for chain construction.
"Prime Number Theory x Topology" is one concept pair but covers dozens of
operation pairs with wildly different type signatures and behaviors.

The operation tensor works at the right granularity: each of the 81
operations gets a feature vector encoding:
  1. Its parent concept's features (inherited from concept_tensor)
  2. Type signature (input_type, output_type one-hot encoded)
  3. Type compatibility (which operations it can chain with)

The pairwise interaction matrix directly encodes "can A feed into B?"
alongside "is A→B interesting?" — no post-hoc filtering needed.

Usage:
    from operation_tensor import OperationTensor
    ot = OperationTensor()
    ot.build()

    # Top 100 executable chains ranked by interest
    chains = ot.top_k_chains(100)

    # Sample chains weighted by tensor score (for experiments)
    chains = ot.sample_chains(100)
"""

import numpy as np
import random as _random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

ORGANISMS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ORGANISMS_DIR.parent))


# ============================================================
# Type vocabulary — all input/output types across organisms
# ============================================================

TYPE_VOCABULARY = [
    "scalar", "integer", "real", "float", "number", "complex_value",
    "boolean",
    "array", "vector", "timeseries", "sequence", "list",
    "probability_distribution", "probability_distribution_pair",
    "population_vector", "observation_vector",
    "prime_list", "coordinate_list", "gap_sequence",
    "matrix", "adjacency_matrix", "distance_matrix", "joint_distribution",
    "matrix_vector", "matrix_pair", "timeseries_pair", "vector_pair",
    "state_vector", "trajectory", "spectrum", "persistence_diagram",
    "dict", "factorization", "lattice_structure", "algebraic_structure",
    "geometric_structure", "classification", "partition_count",
    "density_comparison", "analytic_estimate", "statistical_estimate",
    "boolean_with_detail", "prime_pair_list", "sumset", "solution",
    "integer_pair", "integer_triple", "rational",
    "modular_params", "geometric_params", "params",
    "function_string", "function_string_pair",
    "set_and_integer", "set_pair",
]

# Groups of compatible types (types that can connect)
NUMERIC_TYPES = {"scalar", "integer", "real", "float", "number", "complex_value"}
ARRAY_TYPES = {"array", "vector", "timeseries", "sequence", "list",
               "probability_distribution", "population_vector",
               "observation_vector", "prime_list", "coordinate_list",
               "gap_sequence"}
MATRIX_TYPES = {"matrix", "adjacency_matrix", "distance_matrix", "joint_distribution"}
STRUCT_TYPES = {"dict", "factorization", "lattice_structure", "algebraic_structure",
                "geometric_structure", "classification", "partition_count"}


def types_compatible(out_type: str, in_type: str) -> bool:
    """Check if output type can feed into input type."""
    if out_type == in_type:
        return True
    if out_type in NUMERIC_TYPES and in_type in NUMERIC_TYPES:
        return True
    if out_type in ARRAY_TYPES and in_type in ARRAY_TYPES:
        return True
    if out_type in MATRIX_TYPES and in_type in MATRIX_TYPES:
        return True
    return False


def type_to_onehot(type_name: str) -> np.ndarray:
    """Encode a type as a one-hot vector over the vocabulary."""
    vec = np.zeros(len(TYPE_VOCABULARY), dtype=np.float32)
    if type_name in TYPE_VOCABULARY:
        vec[TYPE_VOCABULARY.index(type_name)] = 1.0
    else:
        # Soft match: check type groups
        if type_name in NUMERIC_TYPES:
            for t in NUMERIC_TYPES:
                if t in TYPE_VOCABULARY:
                    vec[TYPE_VOCABULARY.index(t)] = 0.3
        elif type_name in ARRAY_TYPES:
            for t in ARRAY_TYPES:
                if t in TYPE_VOCABULARY:
                    vec[TYPE_VOCABULARY.index(t)] = 0.2
    return vec


# ============================================================
# Operation Feature Encoding
# ============================================================

class OperationTensor:
    """
    Feature-encodes all operations across all organisms and scores
    their pairwise interactions for chain construction.
    """

    def __init__(self):
        self.operations: List[Dict] = []  # {organism, op_name, input_type, output_type}
        self.feature_matrix: Optional[np.ndarray] = None
        self.pairwise_scores: Optional[np.ndarray] = None
        self.type_compat_matrix: Optional[np.ndarray] = None
        self.concept_features: Optional[Dict[str, np.ndarray]] = None
        self._built = False

    def build(self) -> "OperationTensor":
        """Build the operation tensor from all loaded organisms."""
        from organisms import ALL_ORGANISMS
        from organisms.concept_tensor import CONCEPT_FEATURES

        # Try to load generated organisms
        try:
            from organisms.generated import ALL_GENERATED
        except ImportError:
            ALL_GENERATED = []

        # Map organism names to concept features
        org_to_concept = {
            "information_theory": "Information Theory",
            "topology": "Topology",
            "chaos_theory": "Chaos Theory",
            "bayesian_inference": "Bayesian Inference",
            "game_theory": "Nash Equilibrium",
            "immune_systems": "Immune Systems",
            "network_science": "Network Science",
            "signal_processing": "Matched Filtering",
            "statistical_mechanics": "Statistical Mechanics",
            "dynamical_systems": "Dynamical Systems",
            "prime_theory": "Prime Number Theory",
            "algebraic_number_theory": "Prime Number Theory",
            "analytic_number_theory": "Prime Number Theory",
            "geometric_number_theory": "Fractal Geometry",
            "probabilistic_number_theory": "Prime Number Theory",
            "combinatorial_number_theory": "Prime Number Theory",
            "computational_number_theory": "Prime Number Theory",
            "number_geometry_bridge": "Topology",
            # Generated organisms — map to nearest concept
            "numpy": "Tensor Decomposition",
            "scipy_linalg": "Tensor Decomposition",
            "scipy_signal": "Wavelet Transforms",
            "scipy_stats": "Bayesian Inference",
            "scipy_special": "Fourier Transforms",
            "math": "Information Theory",
            "cmath": "Information Theory",
            "statistics": "Bayesian Inference",
        }

        # Load all operations from both hand-built and generated organisms
        all_organism_classes = list(ALL_ORGANISMS) + list(ALL_GENERATED)
        self.operations = []
        for cls in all_organism_classes:
            org = cls()
            concept_name = org_to_concept.get(org.name)
            concept_feat = None
            if concept_name and concept_name in CONCEPT_FEATURES:
                concept_feat = np.array(CONCEPT_FEATURES[concept_name], dtype=np.float32)

            for op_name, meta in org.operations.items():
                self.operations.append({
                    "organism": org.name,
                    "op_name": op_name,
                    "input_type": meta.get("input_type", "any"),
                    "output_type": meta.get("output_type", "any"),
                    "concept_name": concept_name,
                    "concept_features": concept_feat,
                })

        N = len(self.operations)
        n_type_dims = len(TYPE_VOCABULARY)

        # Build feature matrix for each operation:
        # [30 concept features | n_type_dims input_type | n_type_dims output_type]
        feat_dim = 30 + 2 * n_type_dims
        self.feature_matrix = np.zeros((N, feat_dim), dtype=np.float32)

        for i, op in enumerate(self.operations):
            # Concept features (first 30 dims)
            if op["concept_features"] is not None:
                self.feature_matrix[i, :30] = op["concept_features"]

            # Input type encoding
            self.feature_matrix[i, 30:30 + n_type_dims] = type_to_onehot(op["input_type"])

            # Output type encoding
            self.feature_matrix[i, 30 + n_type_dims:] = type_to_onehot(op["output_type"])

        # Build type compatibility matrix (NxN boolean)
        self.type_compat_matrix = np.zeros((N, N), dtype=np.float32)
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                # Can op_i's output feed into op_j's input?
                if types_compatible(
                    self.operations[i]["output_type"],
                    self.operations[j]["input_type"]
                ):
                    self.type_compat_matrix[i, j] = 1.0

        # Build pairwise interaction scores
        # Score = concept_interest * type_compatibility
        self._compute_pairwise_scores()

        self._built = True
        return self

    def _compute_pairwise_scores(self):
        """
        Compute pairwise scores between all operations.

        Score(i→j) = type_compatible(i,j) * (complementarity(i,j) + resonance(i,j))

        Only non-zero when the operations can actually chain.
        """
        N = len(self.operations)
        self.pairwise_scores = np.zeros((N, N), dtype=np.float32)

        concept_feats = self.feature_matrix[:, :30]  # Just the concept dimensions

        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                if self.type_compat_matrix[i, j] == 0:
                    continue  # Not type-compatible = 0 score

                # Must be from different organisms
                if self.operations[i]["organism"] == self.operations[j]["organism"]:
                    continue

                # Complementarity: how different are the parent concepts?
                comp = float(np.mean(np.abs(concept_feats[i] - concept_feats[j])))

                # Resonance: shared strengths
                res = float(np.mean(concept_feats[i] * concept_feats[j]))

                # Novelty: outer product off-diagonal energy
                interface = np.outer(concept_feats[i], concept_feats[j])
                diag_e = np.sum(np.diag(interface) ** 2)
                total_e = np.sum(interface ** 2)
                nov = 1.0 - diag_e / total_e if total_e > 0 else 0.0

                # Type match bonus: exact match gets higher score than group match
                out_type = self.operations[i]["output_type"]
                in_type = self.operations[j]["input_type"]
                type_bonus = 1.2 if out_type == in_type else 1.0

                score = (0.4 * nov + 0.35 * comp + 0.25 * res) * type_bonus
                self.pairwise_scores[i, j] = score

    def top_k_chains(self, k: int = 100) -> List[Dict]:
        """
        Return the top-K highest-scoring operation chains.
        All returned chains are guaranteed type-compatible and cross-organism.
        """
        if not self._built:
            raise RuntimeError("Call .build() first")

        N = len(self.operations)
        flat = self.pairwise_scores.flatten()
        top_indices = np.argsort(flat)[::-1]

        results = []
        seen = set()
        for idx in top_indices:
            if len(results) >= k:
                break
            i, j = divmod(int(idx), N)
            score = float(self.pairwise_scores[i, j])
            if score <= 0:
                break

            key = (i, j)
            if key in seen:
                continue
            seen.add(key)

            op_i = self.operations[i]
            op_j = self.operations[j]

            results.append({
                "rank": len(results) + 1,
                "chain": [(op_i["organism"], op_i["op_name"]),
                          (op_j["organism"], op_j["op_name"])],
                "chain_str": f"{op_i['organism']}.{op_i['op_name']} -> {op_j['organism']}.{op_j['op_name']}",
                "score": score,
                "type_flow": f"{op_i['output_type']} -> {op_j['input_type']}",
                "concepts": [op_i["concept_name"], op_j["concept_name"]],
            })

        return results

    def sample_chains(self, n: int = 100, temperature: float = 1.0) -> List[List[Tuple[str, str]]]:
        """
        Sample n chains weighted by tensor score with temperature control.

        temperature=1.0: proportional to score (default)
        temperature>1.0: more uniform (more exploration)
        temperature<1.0: more concentrated (more exploitation)
        """
        if not self._built:
            raise RuntimeError("Call .build() first")

        # Get all non-zero-scoring pairs
        nonzero = np.argwhere(self.pairwise_scores > 0)
        if len(nonzero) == 0:
            return []

        scores = np.array([float(self.pairwise_scores[i, j]) for i, j in nonzero])

        # Apply temperature
        if temperature != 1.0:
            scores = scores ** (1.0 / temperature)

        weights = scores / scores.sum()

        indices = np.random.choice(len(nonzero), size=n, replace=True, p=weights)

        chains = []
        for idx in indices:
            i, j = nonzero[idx]
            op_i = self.operations[i]
            op_j = self.operations[j]
            chains.append([
                (op_i["organism"], op_i["op_name"]),
                (op_j["organism"], op_j["op_name"]),
            ])

        return chains

    def stats(self) -> Dict:
        """Return operation tensor statistics."""
        if not self._built:
            return {"built": False}

        N = len(self.operations)
        n_compat = int(np.sum(self.type_compat_matrix > 0))
        n_scored = int(np.sum(self.pairwise_scores > 0))
        scores = self.pairwise_scores[self.pairwise_scores > 0]

        return {
            "n_operations": N,
            "n_organisms": len(set(op["organism"] for op in self.operations)),
            "n_type_compatible_pairs": n_compat,
            "n_cross_organism_scored": n_scored,
            "score_mean": float(np.mean(scores)) if len(scores) > 0 else 0,
            "score_std": float(np.std(scores)) if len(scores) > 0 else 0,
            "score_max": float(np.max(scores)) if len(scores) > 0 else 0,
            "feature_dim": self.feature_matrix.shape[1] if self.feature_matrix is not None else 0,
        }


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import time

    print("=" * 70)
    print("  OPERATION TENSOR — Operation-Level Chain Scoring")
    print("=" * 70)
    print()

    t0 = time.perf_counter()
    ot = OperationTensor()
    ot.build()
    build_time = time.perf_counter() - t0

    s = ot.stats()
    print(f"  Operations:              {s['n_operations']}")
    print(f"  Organisms:               {s['n_organisms']}")
    print(f"  Type-compatible pairs:   {s['n_type_compatible_pairs']}")
    print(f"  Cross-organism scored:   {s['n_cross_organism_scored']}")
    print(f"  Feature dimensions:      {s['feature_dim']}")
    print(f"  Score range:             {s['score_mean']:.4f} +/- {s['score_std']:.4f} (max {s['score_max']:.4f})")
    print(f"  Build time:              {build_time:.3f}s")
    print()

    # Top 20 chains
    top = ot.top_k_chains(20)
    print("  TOP 20 OPERATION CHAINS:")
    print("  " + "-" * 68)
    for c in top:
        print(f"  {c['rank']:3d}. [{c['score']:.4f}] {c['chain_str']}")
        print(f"       type: {c['type_flow']}  concepts: {c['concepts'][0]} -> {c['concepts'][1]}")
    print()

    # Concept diversity in top 50
    top50 = ot.top_k_chains(50)
    from collections import Counter
    concepts = Counter()
    for c in top50:
        for cn in c["concepts"]:
            if cn:
                concepts[cn] += 1
    print(f"  Concept diversity in top 50 chains:")
    for name, count in concepts.most_common():
        print(f"    {name:30s} {count}")
