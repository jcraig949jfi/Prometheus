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


def load_all_organisms() -> Dict[str, MathematicalOrganism]:
    """Load all organisms from the package registry."""
    organisms = {}
    for cls in ALL_ORGANISMS:
        org = cls()
        organisms[org.name] = org
    return organisms


# Mapping from concept names (Title Case) to organism names (snake_case)
CONCEPT_TO_ORGANISM = {
    "Information Theory": "information_theory",
    "Topology": "topology",
    "Chaos Theory": "chaos_theory",
    "Bayesian Inference": "bayesian_inference",
    "Game Theory": "game_theory",
    "Immune Systems": "immune_systems",
    "Network Science": "network_science",
    "Signal Processing": "signal_processing",
    "Statistical Mechanics": "statistical_mechanics",
    "Dynamical Systems": "dynamical_systems",
    "Prime Number Theory": "prime_theory",
    "Algebraic Number Theory": "algebraic_number_theory",
    "Analytic Number Theory": "analytic_number_theory",
    "Geometric Number Theory": "geometric_number_theory",
    "Probabilistic Number Theory": "probabilistic_number_theory",
    "Combinatorial Number Theory": "combinatorial_number_theory",
    "Computational Number Theory": "computational_number_theory",
}


# Standard test inputs matching the Poros explorer
TEST_INPUTS = {
    "scalar": [0.5, 2.0, 7.0, 13.0, 100.0],
    "array": [
        np.array([0.1, 0.2, 0.3, 0.4]),
        np.array([1, 2, 3, 5, 8, 13]),
        np.linspace(0, 1, 20),
        np.random.RandomState(42).rand(10),
    ],
    "probability_distribution": [
        np.array([0.25, 0.25, 0.25, 0.25]),
        np.array([0.1, 0.2, 0.3, 0.4]),
        np.array([0.01, 0.09, 0.9]),
    ],
    "integer": [7, 13, 50, 100, 997],
}


def execute_chain(organisms: Dict, chain: List[Tuple[str, str]], timeout: float = 2.0) -> Dict:
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
                    fn = org.get_operation(op_name)
                    if fn is None:
                        raise ValueError(f"Unknown operation: {org_name}.{op_name}")

                    start = time.perf_counter()
                    result = fn(result)
                    elapsed = time.perf_counter() - start

                    if elapsed > timeout:
                        raise TimeoutError(f"Operation took {elapsed:.1f}s")

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


def sample_random_chains(organisms: Dict, n: int = 100, max_len: int = 2) -> List[List[Tuple[str, str]]]:
    """Sample random composition chains from available organisms."""
    org_names = list(organisms.keys())
    chains = []

    for _ in range(n * 3):  # oversample to get n unique
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
) -> List[List[Tuple[str, str]]]:
    """
    Sample chains guided by tensor navigator top-K triples.
    For each high-scoring triple, create chains from available organisms/operations.
    """
    frontier = nav.top_k_triples(k=n * 2, diversity_cap=5)

    chains = []
    for entry in frontier:
        if len(chains) >= n:
            break

        concepts = entry["concepts"]
        # Map concepts to organisms
        org_names = []
        for concept in concepts:
            org_name = CONCEPT_TO_ORGANISM.get(concept)
            if org_name and org_name in organisms:
                org_names.append(org_name)

        if len(org_names) < 2:
            continue

        # Create chains from pairs of organisms in this triple
        for i in range(len(org_names)):
            for j in range(len(org_names)):
                if i == j or len(chains) >= n:
                    continue
                org_a = organisms[org_names[i]]
                org_b = organisms[org_names[j]]
                ops_a = list(org_a.operations.keys())
                ops_b = list(org_b.operations.keys())
                if ops_a and ops_b:
                    chain = [
                        (org_names[i], random.choice(ops_a)),
                        (org_names[j], random.choice(ops_b)),
                    ]
                    chains.append(chain)

    return chains[:n]


def main():
    print("=" * 70)
    print("  NOESIS EXPERIMENT: TENSOR-GUIDED vs RANDOM EXPLORATION")
    print("  Does tensor navigation find better compositions?")
    print("=" * 70)
    print()

    random.seed(42)
    np.random.seed(42)

    # Load organisms
    print("  Loading organisms...")
    organisms = load_all_organisms()
    print(f"    {len(organisms)} organisms loaded: {', '.join(sorted(organisms.keys()))}")
    print()

    # Build tensor navigator
    print("  Building tensor navigator...")
    nav = TensorTrainNavigator(rank=10)
    nav.build()
    stats = nav.stats()
    print(f"    {stats['n_concepts']} concepts, built in {stats['build_time_s']:.3f}s")
    print()

    n_chains = 100

    # Sample random chains
    print(f"  Sampling {n_chains} RANDOM chains...")
    random_chains = sample_random_chains(organisms, n=n_chains)
    print(f"    Got {len(random_chains)} chains")

    # Sample tensor-guided chains
    print(f"  Sampling {n_chains} TENSOR-GUIDED chains...")
    tensor_chains = sample_tensor_guided_chains(organisms, nav, n=n_chains)
    print(f"    Got {len(tensor_chains)} chains")
    print()

    # Execute random chains
    print("  Executing RANDOM chains...")
    t0 = time.perf_counter()
    random_results = []
    for i, chain in enumerate(random_chains):
        result = execute_chain(organisms, chain)
        result["chain"] = [f"{org}.{op}" for org, op in chain]
        random_results.append(result)
        if (i + 1) % 25 == 0:
            print(f"    {i+1}/{len(random_chains)} done...")
    random_time = time.perf_counter() - t0
    print(f"    Completed in {random_time:.1f}s")
    print()

    # Execute tensor-guided chains
    print("  Executing TENSOR-GUIDED chains...")
    t0 = time.perf_counter()
    tensor_results = []
    for i, chain in enumerate(tensor_chains):
        result = execute_chain(organisms, chain)
        result["chain"] = [f"{org}.{op}" for org, op in chain]
        tensor_results.append(result)
        if (i + 1) % 25 == 0:
            print(f"    {i+1}/{len(tensor_chains)} done...")
    tensor_time = time.perf_counter() - t0
    print(f"    Completed in {tensor_time:.1f}s")
    print()

    # Compare
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print()

    def summarize(results, label):
        executed = sum(1 for r in results if r["executed"])
        scores = [r["score"] for r in results]
        success_rates = [r["success_rate"] for r in results if r["executed"]]
        novelties = [r["novelty"] for r in results if r["executed"]]

        print(f"  {label}:")
        print(f"    Chains tested:    {len(results)}")
        print(f"    Executed (>0):    {executed} ({executed/len(results)*100:.0f}%)")
        print(f"    Mean score:       {np.mean(scores):.4f}")
        print(f"    Median score:     {np.median(scores):.4f}")
        print(f"    Max score:        {np.max(scores):.4f}")
        if success_rates:
            print(f"    Mean success rate:{np.mean(success_rates):.4f}")
        if novelties:
            print(f"    Mean novelty:     {np.mean(novelties):.4f}")
        print()

        return {
            "n_chains": len(results),
            "n_executed": executed,
            "execution_rate": executed / len(results) if results else 0,
            "mean_score": float(np.mean(scores)),
            "median_score": float(np.median(scores)),
            "max_score": float(np.max(scores)),
            "mean_success_rate": float(np.mean(success_rates)) if success_rates else 0,
            "mean_novelty": float(np.mean(novelties)) if novelties else 0,
        }

    random_summary = summarize(random_results, "RANDOM")
    tensor_summary = summarize(tensor_results, "TENSOR-GUIDED")

    # Head-to-head
    print("  HEAD-TO-HEAD:")
    for metric in ["execution_rate", "mean_score", "median_score", "mean_success_rate", "mean_novelty"]:
        r = random_summary[metric]
        t = tensor_summary[metric]
        winner = "TENSOR" if t > r else "RANDOM" if r > t else "TIE"
        diff = (t - r) / r * 100 if r > 0 else float("inf")
        print(f"    {metric:25s}  random={r:.4f}  tensor={t:.4f}  "
              f"{'%+.1f%%' % diff:>8s}  [{winner}]")
    print()

    # Top 10 from each
    print("  TOP 10 RANDOM:")
    for r in sorted(random_results, key=lambda x: -x["score"])[:10]:
        print(f"    [{r['score']:.4f}] {' -> '.join(r['chain'])}")
    print()

    print("  TOP 10 TENSOR-GUIDED:")
    for r in sorted(tensor_results, key=lambda x: -x["score"])[:10]:
        print(f"    [{r['score']:.4f}] {' -> '.join(r['chain'])}")
    print()

    # Save
    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_chains_per_group": n_chains,
        "n_organisms": len(organisms),
        "random_summary": random_summary,
        "tensor_summary": tensor_summary,
        "random_results": random_results,
        "tensor_results": tensor_results,
    }
    output_path = OUTPUT_DIR / "tensor_vs_random.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  Full results saved to {output_path}")

    # Verdict
    print()
    if tensor_summary["mean_score"] > random_summary["mean_score"] * 1.1:
        print("  VERDICT: Tensor guidance provides meaningful signal (>10% improvement)")
    elif tensor_summary["mean_score"] > random_summary["mean_score"]:
        print("  VERDICT: Tensor guidance shows slight improvement (needs more data)")
    else:
        print("  VERDICT: Tensor guidance does not outperform random (scoring function needs work)")


if __name__ == "__main__":
    main()
