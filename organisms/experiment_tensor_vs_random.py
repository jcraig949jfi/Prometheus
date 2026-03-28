"""
Experiment: Tensor-guided vs Random exploration.

The existence proof for Noesis: does tensor navigation find better
compositions than random sampling?

Method:
  1. Load all organisms and their operations
  2. Sample 100 random composition chains
  3. Sample 100 tensor-guided chains (top-scoring from navigator)
  4. Execute both sets on test inputs
  5. Compare: success rate, score distribution, novelty

If tensor-guided chains have a meaningfully higher success/score rate,
the tensor shortcut provides real signal, not just speed.
"""

import json
import hashlib
import time
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ORGANISMS_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ORGANISMS_DIR / "tensor_vs_random_results"
OUTPUT_DIR.mkdir(exist_ok=True)

# Import organism infrastructure
import sys
sys.path.insert(0, str(ORGANISMS_DIR.parent))

from organisms import ALL_ORGANISMS
from organisms.base import MathematicalOrganism
from organisms.concept_tensor import get_concept_names, get_feature_matrix, compute_triple_tensor_fast
from organisms.tensor_navigator import TensorTrainNavigator
from organisms.operation_tensor import OperationTensor


def load_all_organisms() -> Dict[str, MathematicalOrganism]:
    """Load all organisms from the package registry, including auto-generated ones."""
    organisms = {}
    for cls in ALL_ORGANISMS:
        org = cls()
        organisms[org.name] = org

    # Also load generated organisms
    try:
        from organisms.generated import ALL_GENERATED
        for cls in ALL_GENERATED:
            org = cls()
            organisms[org.name] = org
    except ImportError:
        pass

    return organisms


# Mapping from concept names (Title Case) to organism names (snake_case).
# Every organism must map to exactly one of the 95 Lattice concepts so that
# the tensor navigator can score its pairs. Sub-field organisms map to the
# nearest parent concept.
CONCEPT_TO_ORGANISM = {
    "Information Theory": "information_theory",
    "Topology": "topology",
    "Chaos Theory": "chaos_theory",
    "Bayesian Inference": "bayesian_inference",
    "Nash Equilibrium": "game_theory",
    "Immune Systems": "immune_systems",
    "Network Science": "network_science",
    "Matched Filtering": "signal_processing",
    "Statistical Mechanics": "statistical_mechanics",
    "Dynamical Systems": "dynamical_systems",
    "Prime Number Theory": "prime_theory",
}
# Multi-organism concept mappings: several organisms share the same concept
# (number theory variants all map to Prime Number Theory, etc.)
ORGANISM_TO_CONCEPT = {v: k for k, v in CONCEPT_TO_ORGANISM.items()}
ORGANISM_TO_CONCEPT.update({
    "algebraic_number_theory": "Prime Number Theory",
    "analytic_number_theory": "Prime Number Theory",
    "geometric_number_theory": "Fractal Geometry",
    "probabilistic_number_theory": "Prime Number Theory",
    "combinatorial_number_theory": "Prime Number Theory",
    "computational_number_theory": "Prime Number Theory",
    "number_geometry_bridge": "Topology",
})


# Standard test inputs covering all semantic types
TEST_INPUTS = {
    "scalar": [0.5, 2.0, 7.0, 13.0],
    "integer": [7, 13, 50, 100],
    "array": [
        np.array([0.1, 0.2, 0.3, 0.4]),
        np.linspace(0, 1, 20),
        np.random.RandomState(42).rand(10),
    ],
    "matrix": [
        np.eye(5),
        np.random.RandomState(42).randn(4, 4),
    ],
}


def _run_with_timeout(func, args, timeout):
    """Run func(*args) with a hard thread-based timeout. Returns (result, error)."""
    import threading
    result_holder = [None]
    error_holder = [None]

    def target():
        try:
            result_holder[0] = func(*args)
        except Exception as e:
            error_holder[0] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return None, TimeoutError("hard timeout")
    return result_holder[0], error_holder[0]


def execute_chain(organisms: Dict, chain: List[Tuple[str, str]], timeout: float = 1.0) -> Dict:
    """
    Execute a composition chain on test inputs.
    Returns {executed: bool, score: float, output_hash: str, error: str|None}.
    """
    successes = 0
    attempts = 0
    outputs = []

    for input_type, inputs in TEST_INPUTS.items():
        for test_input in inputs:
            attempts += 1
            try:
                result = test_input
                for org_name, op_name in chain:
                    if org_name not in organisms:
                        raise ValueError(f"Unknown organism: {org_name}")
                    org = organisms[org_name]

                    result, err = _run_with_timeout(org.execute, (op_name, result), timeout)
                    if err is not None:
                        raise err
                    if result is None:
                        raise ValueError("None result")

                    # Check for garbage output
                    if isinstance(result, (np.ndarray, np.generic)):
                        if np.any(np.isnan(result)) or np.any(np.isinf(result)):
                            raise ValueError("NaN/Inf in output")
                        if isinstance(result, np.ndarray) and result.size > 1_000_000:
                            raise ValueError(f"Output too large: {result.size}")

                successes += 1
                # Hash the output for novelty detection
                if isinstance(result, np.ndarray):
                    h = hashlib.md5(result.tobytes()).hexdigest()[:8]
                else:
                    h = hashlib.md5(str(result).encode()).hexdigest()[:8]
                outputs.append(h)

            except Exception:
                pass

    success_rate = successes / attempts if attempts > 0 else 0
    unique_outputs = len(set(outputs))
    novelty = unique_outputs / len(outputs) if outputs else 0

    # Combined score (same weighting philosophy as Poros)
    score = 0.5 * success_rate + 0.3 * novelty + 0.2 * min(len(outputs) / 10, 1.0)

    return {
        "executed": successes > 0,
        "success_rate": success_rate,
        "successes": successes,
        "attempts": attempts,
        "unique_outputs": unique_outputs,
        "novelty": novelty,
        "score": score,
    }


def _get_all_compatible_chains(organisms: Dict) -> List[Tuple[str, str, str, str]]:
    """
    Precompute all type-compatible (org_a, op_a, org_b, op_b) tuples.
    Returns list of (org_a_name, op_a_name, org_b_name, op_b_name).
    """
    compat = []
    org_names = list(organisms.keys())
    for name_a in org_names:
        org_a = organisms[name_a]
        for name_b in org_names:
            if name_a == name_b:
                continue
            org_b = organisms[name_b]
            for op_a, op_b in org_a.compatible_chains(org_b):
                compat.append((name_a, op_a, name_b, op_b))
    return compat


def sample_random_chains(
    organisms: Dict, n: int = 100, max_len: int = 2, type_filtered: bool = False
) -> List[List[Tuple[str, str]]]:
    """
    Sample random composition chains from available organisms.

    If type_filtered=True, only sample from type-compatible operation pairs.
    If type_filtered=False (default), pick any operations regardless of types.
    """
    if type_filtered:
        compat = _get_all_compatible_chains(organisms)
        if not compat:
            return []
        chains = []
        for _ in range(n):
            entry = random.choice(compat)
            chains.append([(entry[0], entry[1]), (entry[2], entry[3])])
        return chains

    org_names = list(organisms.keys())
    chains = []
    for _ in range(n * 3):
        if len(chains) >= n:
            break
        chain_len = random.randint(2, max_len)
        chain = []
        for _ in range(chain_len):
            org_name = random.choice(org_names)
            org = organisms[org_name]
            ops = list(org.operations.keys())
            if ops:
                op_name = random.choice(ops)
                chain.append((org_name, op_name))
        if len(chain) >= 2:
            chains.append(chain)
    return chains[:n]


def sample_tensor_guided_chains(
    organisms: Dict,
    nav: TensorTrainNavigator,
    n: int = 100,
    type_filtered: bool = False,
) -> List[List[Tuple[str, str]]]:
    """
    Sample chains guided by tensor navigator scores.

    If type_filtered=True, only sample from type-compatible operation pairs,
    weighted by the tensor score of the organism pair. This combines
    tensor's conceptual targeting with type-system guarantees.

    If type_filtered=False, pick organism pairs by tensor score but
    randomly select operations (may not type-match).
    """
    # Build reverse map: organism_name -> concept_name
    org_to_concept = dict(ORGANISM_TO_CONCEPT)
    name_to_idx = {name: i for i, name in enumerate(nav.concept_names)}

    if type_filtered:
        # Precompute all compatible chains grouped by organism pair
        compat = _get_all_compatible_chains(organisms)
        if not compat:
            return []

        # Group by organism pair, score at PAIR level (not chain level)
        from collections import defaultdict
        pair_ops: Dict[Tuple[str, str], List[Tuple[str, str]]] = defaultdict(list)
        for org_a, op_a, org_b, op_b in compat:
            pair_ops[(org_a, org_b)].append((op_a, op_b))

        # Score each organism PAIR by tensor (not each chain)
        scored_pairs = []
        for (org_a, org_b), ops in pair_ops.items():
            concept_a = org_to_concept.get(org_a)
            concept_b = org_to_concept.get(org_b)
            if not concept_a or not concept_b:
                continue
            idx_a = name_to_idx.get(concept_a)
            idx_b = name_to_idx.get(concept_b)
            if idx_a is None or idx_b is None:
                continue
            tensor_score = float(nav.pairwise["combined"][idx_a, idx_b])
            scored_pairs.append((org_a, org_b, ops, tensor_score))

        if not scored_pairs:
            return []

        # Sample PAIRS weighted by tensor score, then pick random op within pair
        weights = np.array([s for *_, s in scored_pairs])
        weights = weights / weights.sum()
        indices = np.random.choice(len(scored_pairs), size=n, replace=True, p=weights)

        chains = []
        for idx in indices:
            org_a, org_b, ops, _ = scored_pairs[idx]
            op_a, op_b = random.choice(ops)
            chains.append([(org_a, op_a), (org_b, op_b)])
        return chains

    # Original behavior: tensor-weighted organism pairs, random operations
    org_pairs_scored = []
    org_names = list(organisms.keys())
    for i, org_a in enumerate(org_names):
        concept_a = org_to_concept.get(org_a)
        if not concept_a or concept_a not in name_to_idx:
            continue
        idx_a = name_to_idx[concept_a]

        for j, org_b in enumerate(org_names):
            if i == j:
                continue
            concept_b = org_to_concept.get(org_b)
            if not concept_b or concept_b not in name_to_idx:
                continue
            idx_b = name_to_idx[concept_b]

            score = float(nav.pairwise["combined"][idx_a, idx_b])
            if score > 0:
                org_pairs_scored.append((org_a, org_b, score))

    if not org_pairs_scored:
        return []

    pairs = [(a, b) for a, b, _ in org_pairs_scored]
    weights = np.array([s for _, _, s in org_pairs_scored])
    weights = weights / weights.sum()

    chains = []
    indices = np.random.choice(len(pairs), size=n, replace=True, p=weights)
    for idx in indices:
        org_a, org_b = pairs[idx]
        ops_a = list(organisms[org_a].operations.keys())
        ops_b = list(organisms[org_b].operations.keys())
        if ops_a and ops_b:
            chain = [
                (org_a, random.choice(ops_a)),
                (org_b, random.choice(ops_b)),
            ]
            chains.append(chain)

    return chains[:n]


def run_group(organisms, chains, label):
    """Execute a group of chains and return results + summary."""
    results = []
    for i, chain in enumerate(chains):
        result = execute_chain(organisms, chain)
        result["chain"] = [f"{org}.{op}" for org, op in chain]
        results.append(result)

    executed = sum(1 for r in results if r["executed"])
    scores = [r["score"] for r in results]
    success_rates = [r["success_rate"] for r in results if r["executed"]]
    novelties = [r["novelty"] for r in results if r["executed"]]

    summary = {
        "n_chains": len(results),
        "n_executed": executed,
        "execution_rate": executed / len(results) if results else 0,
        "mean_score": float(np.mean(scores)) if scores else 0,
        "median_score": float(np.median(scores)) if scores else 0,
        "max_score": float(np.max(scores)) if scores else 0,
        "mean_success_rate": float(np.mean(success_rates)) if success_rates else 0,
        "mean_novelty": float(np.mean(novelties)) if novelties else 0,
    }

    print(f"  {label}:")
    print(f"    Chains tested:    {summary['n_chains']}")
    print(f"    Executed (>0):    {executed} ({summary['execution_rate']*100:.0f}%)")
    print(f"    Mean score:       {summary['mean_score']:.4f}")
    print(f"    Max score:        {summary['max_score']:.4f}")
    if success_rates:
        print(f"    Mean success rate:{summary['mean_success_rate']:.4f}")
    if novelties:
        print(f"    Mean novelty:     {summary['mean_novelty']:.4f}")
    print()

    return results, summary


def main():
    print("=" * 70)
    print("  NOESIS EXPERIMENT: TENSOR-GUIDED vs RANDOM EXPLORATION")
    print("  4-way comparison: random / random+types / tensor / tensor+types")
    print("=" * 70)
    print()

    random.seed(42)
    np.random.seed(42)

    # Load organisms
    print("  Loading organisms...")
    organisms = load_all_organisms()
    print(f"    {len(organisms)} organisms loaded")

    # Count compatible chains
    compat = _get_all_compatible_chains(organisms)
    compat_pairs = set((a, c) for a, _, c, _ in compat)
    print(f"    {len(compat)} type-compatible operation chains across {len(compat_pairs)} organism pairs")
    print()

    # Build tensor navigators (with and without type awareness)
    print("  Building tensor navigator (type-aware)...")
    nav = TensorTrainNavigator(rank=10)
    nav.build(use_type_compat=True)
    stats = nav.stats()
    print(f"    {stats['n_concepts']} concepts, built in {stats['build_time_s']:.3f}s")
    print()

    # Build operation tensor
    print("  Building operation tensor...")
    op_tensor = OperationTensor()
    op_tensor.build()
    op_stats = op_tensor.stats()
    print(f"    {op_stats['n_operations']} operations, {op_stats['n_cross_organism_scored']} scored chains")
    print()

    n_chains = 100

    # === Sample all 5 strategies ===
    print(f"  Sampling {n_chains} chains per strategy...")

    random.seed(42); np.random.seed(42)
    chains_random = sample_random_chains(organisms, n=n_chains, type_filtered=False)

    random.seed(42); np.random.seed(42)
    chains_random_typed = sample_random_chains(organisms, n=n_chains, type_filtered=True)

    random.seed(42); np.random.seed(42)
    chains_tensor = sample_tensor_guided_chains(organisms, nav, n=n_chains, type_filtered=False)

    random.seed(42); np.random.seed(42)
    chains_tensor_typed = sample_tensor_guided_chains(organisms, nav, n=n_chains, type_filtered=True)

    random.seed(42); np.random.seed(42)
    chains_op_tensor = op_tensor.sample_chains(n=n_chains)

    print(f"    Random:           {len(chains_random)} chains")
    print(f"    Random+Types:     {len(chains_random_typed)} chains")
    print(f"    Tensor:           {len(chains_tensor)} chains")
    print(f"    Tensor+Types:     {len(chains_tensor_typed)} chains")
    print(f"    Op Tensor:        {len(chains_op_tensor)} chains")
    print()

    # === Execute all 4 ===
    print("=" * 70)
    print("  EXECUTING ALL STRATEGIES")
    print("=" * 70)
    print()

    r_random, s_random = run_group(organisms, chains_random, "RANDOM (unfiltered)")
    r_random_typed, s_random_typed = run_group(organisms, chains_random_typed, "RANDOM + TYPE FILTER")
    r_tensor, s_tensor = run_group(organisms, chains_tensor, "TENSOR (unfiltered)")
    r_tensor_typed, s_tensor_typed = run_group(organisms, chains_tensor_typed, "TENSOR + TYPE FILTER")
    r_op_tensor, s_op_tensor = run_group(organisms, chains_op_tensor, "OPERATION TENSOR")

    # === Head-to-head ===
    print("=" * 70)
    print("  HEAD-TO-HEAD COMPARISON")
    print("=" * 70)
    print()

    strategies = [
        ("Random", s_random),
        ("Rand+Types", s_random_typed),
        ("Tensor", s_tensor),
        ("Tens+Types", s_tensor_typed),
        ("OpTensor", s_op_tensor),
    ]

    header = f"  {'Metric':25s}"
    for name, _ in strategies:
        header += f"  {name:>14s}"
    header += "  Winner"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for metric in ["execution_rate", "mean_score", "mean_success_rate", "mean_novelty"]:
        values = [(name, s[metric]) for name, s in strategies]
        best_name = max(values, key=lambda x: x[1])[0]
        row = f"  {metric:25s}"
        for name, val in values:
            row += f"  {val:14.4f}"
        row += f"  [{best_name}]"
        print(row)
    print()

    # === The key comparison: Random+Types vs Op Tensor ===
    print("  KEY QUESTION: Does the operation tensor beat random+types?")
    r_val = s_random_typed["mean_score"]
    o_val = s_op_tensor["mean_score"]
    if r_val > 0:
        diff_pct = (o_val - r_val) / r_val * 100
        print(f"    Random+Types mean score:  {r_val:.4f}")
        print(f"    OpTensor mean score:      {o_val:.4f}")
        print(f"    Difference:               {diff_pct:+.1f}%")
    print()

    # === Top 5 from each strategy ===
    for label, results in [("RANDOM+TYPES", r_random_typed), ("OP TENSOR", r_op_tensor)]:
        print(f"  TOP 5 {label}:")
        for r in sorted(results, key=lambda x: -x["score"])[:5]:
            print(f"    [{r['score']:.4f}] {' -> '.join(r['chain'])}")
        print()

    # === Save ===
    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_chains_per_group": n_chains,
        "n_organisms": len(organisms),
        "n_compatible_ops": len(compat),
        "n_compatible_pairs": len(compat_pairs),
        "summaries": {name: s for name, s in strategies},
        "random_results": r_random,
        "random_typed_results": r_random_typed,
        "tensor_results": r_tensor,
        "tensor_typed_results": r_tensor_typed,
        "op_tensor_results": r_op_tensor,
    }
    output_path = OUTPUT_DIR / "tensor_vs_random.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  Full results saved to {output_path}")

    # === Verdict ===
    print()
    ot_exec = s_op_tensor["execution_rate"]
    rt_exec = s_random_typed["execution_rate"]
    ot_score = s_op_tensor["mean_score"]
    rt_score = s_random_typed["mean_score"]

    if ot_exec > rt_exec and ot_score > rt_score * 1.1:
        print("  VERDICT: Operation tensor wins on both execution rate AND score (>10%)")
        print("  The tensor provides real signal at operation granularity.")
    elif ot_exec > rt_exec:
        print("  VERDICT: Operation tensor wins on execution rate. Score signal needs tuning.")
    elif ot_score > rt_score:
        print("  VERDICT: Operation tensor finds higher-quality chains but fewer execute.")
    else:
        print("  VERDICT: Operation tensor does not yet outperform random+types.")


if __name__ == "__main__":
    main()
