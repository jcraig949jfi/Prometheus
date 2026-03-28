"""
Universal Embedder — Behavioral embedding for ANY computational object.

Embeds formulas, algorithms, data structures, state machines, recursive
functions, iterative processes, and Arcanum specimens into the same
vector space using behavioral fingerprinting.

The key insight: we don't care WHAT something is. We care what it DOES
across a standardized battery of probes. Two objects that respond
identically to the same probes are identical in the embedding space,
regardless of whether one is a number theory formula and the other
is a graph traversal algorithm.

The probes are designed to elicit different KINDS of behavior:
- Scalar probes: what does it do with a single number?
- Sequence probes: what does it do with an ordered list?
- Matrix probes: what does it do with a 2D structure?
- Stress probes: what happens at extremes (0, inf, negative, huge)?
- Iteration probes: does it converge, diverge, cycle, or chaos?
- Sensitivity probes: does a tiny input change cause a tiny or huge output change?
- Structural probes: does the output have patterns, symmetry, sparsity?
"""

import numpy as np
import hashlib
import time
from typing import Any, Callable, Dict, List, Optional

# Standardized probe battery
# Each probe tests a different aspect of computational behavior
PROBES = {
    # Scalar behavior: what does it do with numbers?
    "scalar_zero": 0,
    "scalar_one": 1,
    "scalar_small": 0.001,
    "scalar_pi": 3.14159265,
    "scalar_e": 2.71828183,
    "scalar_negative": -1.0,
    "scalar_large": 1000,
    "scalar_prime": 17,

    # Sequence behavior: what does it do with ordered data?
    "seq_ascending": np.arange(1, 21, dtype=float),
    "seq_descending": np.arange(20, 0, -1, dtype=float),
    "seq_random": np.array([7, 2, 9, 4, 1, 8, 3, 6, 5, 0], dtype=float),
    "seq_constant": np.ones(10, dtype=float) * 5,
    "seq_alternating": np.array([1, -1, 1, -1, 1, -1, 1, -1, 1, -1], dtype=float),
    "seq_primes": np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=float),
    "seq_fibonacci": np.array([1, 1, 2, 3, 5, 8, 13, 21, 34, 55], dtype=float),
    "seq_geometric": np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512], dtype=float),

    # Matrix behavior: what does it do with 2D structure?
    "mat_identity": np.eye(5, dtype=float),
    "mat_random": np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float),
    "mat_symmetric": np.array([[1, 2, 3], [2, 5, 6], [3, 6, 9]], dtype=float),
    "mat_sparse": np.array([[1, 0, 0, 0], [0, 0, 2, 0], [0, 0, 0, 0], [0, 3, 0, 4]], dtype=float),
}


def _extract_features(result: Any) -> np.ndarray:
    """
    Extract a fixed-length feature vector from ANY computational output.
    This is the magic — it normalizes scalars, arrays, matrices, dicts,
    booleans, strings, and complex objects into the same vector format.
    """
    features = np.zeros(12, dtype=np.float32)

    if result is None:
        features[0] = -1  # null signal
        return features

    # Scalar
    if isinstance(result, (int, float, np.integer, np.floating)):
        val = float(result)
        if np.isnan(val):
            features[0] = -2  # NaN signal
        elif np.isinf(val):
            features[0] = 1 if val > 0 else -1
            features[1] = 999  # infinity marker
        else:
            features[0] = np.tanh(val)  # squash to [-1, 1]
            features[1] = np.sign(val)
            features[2] = np.log1p(abs(val))  # magnitude
        features[3] = 0  # dimensionality = 0 (scalar)
        return features

    # Boolean
    if isinstance(result, (bool, np.bool_)):
        features[0] = 1.0 if result else 0.0
        features[3] = 0
        return features

    # Complex
    if isinstance(result, (complex, np.complexfloating)):
        features[0] = np.tanh(result.real)
        features[1] = np.tanh(result.imag)
        features[2] = np.log1p(abs(result))
        features[3] = 0.5  # complex marker
        return features

    # String (hash it)
    if isinstance(result, str):
        h = int(hashlib.md5(result.encode()).hexdigest()[:8], 16) / 2**32
        features[0] = h
        features[3] = -0.5  # string marker
        return features

    # Array-like
    try:
        arr = np.asarray(result, dtype=float)
        if arr.size == 0:
            features[0] = -3  # empty
            return features

        flat = arr.flatten()
        finite = flat[np.isfinite(flat)]

        if len(finite) == 0:
            features[0] = -2  # all NaN/inf
            return features

        features[0] = np.tanh(np.mean(finite))          # central tendency
        features[1] = np.tanh(np.std(finite))            # spread
        features[2] = np.tanh(np.median(finite))         # robustness
        features[3] = min(arr.ndim / 5.0, 1.0)           # dimensionality
        features[4] = np.log1p(arr.size)                  # size (log scale)
        features[5] = len(finite) / max(flat.size, 1)     # finite ratio

        # Structural features
        if len(finite) > 1:
            diffs = np.diff(finite)
            features[6] = np.tanh(np.mean(diffs))          # trend
            features[7] = np.tanh(np.std(diffs))            # variability of change
            features[8] = np.mean(diffs > 0)                # monotonicity
            features[9] = np.mean(np.abs(diffs) < 1e-10)    # constancy (repeating)

            # Autocorrelation at lag 1 (periodicity detection)
            if len(finite) > 2:
                centered = finite - np.mean(finite)
                var = np.var(finite)
                if var > 1e-10:
                    features[10] = np.clip(
                        np.mean(centered[:-1] * centered[1:]) / var, -1, 1
                    )

        # Sparsity
        features[11] = np.mean(np.abs(flat) < 1e-10)  # fraction of zeros

        return features

    except (ValueError, TypeError):
        pass

    # Dict
    if isinstance(result, dict):
        features[0] = np.tanh(len(result))
        features[3] = 0.75  # dict marker
        # Try to extract numeric values
        vals = []
        for v in result.values():
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                pass
        if vals:
            features[1] = np.tanh(np.mean(vals))
            features[2] = np.tanh(np.std(vals))
        return features

    # Tuple/list of non-numeric
    if isinstance(result, (list, tuple)):
        features[0] = np.tanh(len(result))
        features[3] = 0.6  # list marker
        return features

    # Unknown type — hash it
    features[0] = 0.5
    features[3] = 1.0  # unknown marker
    return features


def embed(fn: Callable, timeout: float = 2.0) -> Dict:
    """
    Embed ANY callable into the universal vector space.

    Returns a dict with:
      - address: np.ndarray of shape (n_probes * 12,) — the embedding coordinates
      - meta: dict of metadata about the embedding
      - probe_results: per-probe raw results (for debugging)
    """
    all_features = []
    probe_results = {}
    n_success = 0
    n_error = 0
    n_timeout = 0
    total_time = 0

    for probe_name, probe_input in PROBES.items():
        t0 = time.perf_counter()
        try:
            result = fn(probe_input)
            elapsed = time.perf_counter() - t0
            total_time += elapsed

            if elapsed > timeout:
                features = np.zeros(12, dtype=np.float32)
                features[0] = -4  # timeout signal
                n_timeout += 1
            else:
                features = _extract_features(result)
                n_success += 1

            probe_results[probe_name] = {
                "output_type": type(result).__name__,
                "elapsed_ms": elapsed * 1000,
                "features": features.tolist(),
            }

        except Exception as e:
            features = np.zeros(12, dtype=np.float32)
            features[0] = -5  # error signal
            features[1] = hash(type(e).__name__) % 100 / 100  # error type signature
            n_error += 1

            probe_results[probe_name] = {
                "error": f"{type(e).__name__}: {str(e)[:100]}",
                "features": features.tolist(),
            }

        all_features.append(features)

    address = np.concatenate(all_features)  # shape: (n_probes * 12,)

    meta = {
        "n_probes": len(PROBES),
        "n_success": n_success,
        "n_error": n_error,
        "n_timeout": n_timeout,
        "success_rate": n_success / len(PROBES),
        "total_time_ms": total_time * 1000,
        "address_dim": len(address),
        "address_norm": float(np.linalg.norm(address)),
    }

    return {
        "address": address,
        "meta": meta,
        "probe_results": probe_results,
    }


def distance(embedding_a: Dict, embedding_b: Dict) -> float:
    """Euclidean distance between two embeddings."""
    return float(np.linalg.norm(embedding_a["address"] - embedding_b["address"]))


def cosine_similarity(embedding_a: Dict, embedding_b: Dict) -> float:
    """Cosine similarity between two embeddings."""
    a, b = embedding_a["address"], embedding_b["address"]
    norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def find_neighbors(target: Dict, library: List[Dict], top_k: int = 10) -> List:
    """Find the top_k nearest neighbors to target in the library."""
    distances = []
    for i, item in enumerate(library):
        d = distance(target, item)
        distances.append((i, d, item.get("name", f"item_{i}")))
    distances.sort(key=lambda x: x[1])
    return distances[:top_k]


# ============================================================
# Test: embed some wildly different computational objects
# ============================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))

    print("=== UNIVERSAL EMBEDDER ===")
    print(f"Probes: {len(PROBES)}")
    print(f"Features per probe: 12")
    print(f"Embedding dimension: {len(PROBES) * 12}")
    print()

    # Embed wildly different things
    objects = {
        # Pure math formulas
        "square": lambda x: np.asarray(x) ** 2,
        "sqrt": lambda x: np.sqrt(np.abs(np.asarray(x))),
        "sin": lambda x: np.sin(np.asarray(x)),
        "exp": lambda x: np.exp(np.clip(np.asarray(x), -10, 10)),
        "log": lambda x: np.log(np.abs(np.asarray(x)) + 1e-10),
        "reciprocal": lambda x: 1.0 / (np.asarray(x) + 1e-10),

        # Algorithms
        "sort": lambda x: np.sort(np.asarray(x).flatten()),
        "reverse": lambda x: np.asarray(x).flatten()[::-1],
        "cumsum": lambda x: np.cumsum(np.asarray(x).flatten()),
        "diff": lambda x: np.diff(np.asarray(x).flatten()),

        # Statistical operations
        "mean": lambda x: np.mean(np.asarray(x)),
        "std": lambda x: np.std(np.asarray(x)),
        "entropy": lambda x: -np.sum(p * np.log2(p + 1e-10) for p in np.abs(np.asarray(x).flatten()) / (np.sum(np.abs(np.asarray(x))) + 1e-10)) if np.sum(np.abs(np.asarray(x))) > 0 else 0,

        # Matrix operations
        "transpose": lambda x: np.asarray(x).T if np.asarray(x).ndim >= 2 else np.asarray(x),
        "determinant": lambda x: np.linalg.det(np.asarray(x)) if np.asarray(x).ndim == 2 and np.asarray(x).shape[0] == np.asarray(x).shape[1] else 0,
        "eigenvalues": lambda x: np.linalg.eigvals(np.asarray(x)) if np.asarray(x).ndim == 2 and np.asarray(x).shape[0] == np.asarray(x).shape[1] else np.array([0]),

        # Boolean/classification
        "is_positive": lambda x: np.all(np.asarray(x) > 0),
        "is_sorted": lambda x: np.all(np.diff(np.asarray(x).flatten()) >= 0) if np.asarray(x).size > 1 else True,
        "count_nonzero": lambda x: np.count_nonzero(np.asarray(x)),

        # Iterative/chaotic
        "logistic_map": lambda x: np.array([3.9 * float(np.mean(np.asarray(x))) * (1 - float(np.mean(np.asarray(x))))]),

        # Compression
        "compress_len": lambda x: len(__import__('zlib').compress(np.asarray(x).tobytes())),
    }

    print(f"Embedding {len(objects)} computational objects...")
    print()

    embeddings = {}
    for name, fn in objects.items():
        result = embed(fn)
        result["name"] = name
        embeddings[name] = result
        rate = result["meta"]["success_rate"]
        dim = result["meta"]["address_dim"]
        t = result["meta"]["total_time_ms"]
        print(f"  {name:20s}: {rate:.0%} success, {dim}D address, {t:.1f}ms")

    print()

    # Find neighbors for each object
    library = list(embeddings.values())
    print("=== NEAREST NEIGHBORS ===")
    print()

    for name in ["sin", "sort", "eigenvalues", "logistic_map", "is_positive"]:
        target = embeddings[name]
        neighbors = find_neighbors(target, library, top_k=4)
        neighbor_str = ", ".join(f"{n[2]}({n[1]:.2f})" for n in neighbors if n[2] != name)
        print(f"  {name:20s} neighbors: {neighbor_str}")

    print()
    print("=== EMBEDDING SPACE STATISTICS ===")
    addresses = np.array([e["address"] for e in library])
    print(f"  Shape: {addresses.shape}")
    print(f"  Mean norm: {np.mean([np.linalg.norm(a) for a in addresses]):.2f}")
    print(f"  Std of norms: {np.std([np.linalg.norm(a) for a in addresses]):.2f}")

    # Pairwise distance matrix
    n = len(library)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i, j] = distance(library[i], library[j])
    print(f"  Mean pairwise distance: {np.mean(dist_matrix[dist_matrix > 0]):.2f}")
    print(f"  Min pairwise distance: {np.min(dist_matrix[dist_matrix > 0]):.2f}")
    print(f"  Max pairwise distance: {np.max(dist_matrix):.2f}")

    # Find the most surprising neighbors (closest pair from different "types")
    names = [e["name"] for e in library]
    closest = []
    for i in range(n):
        for j in range(i+1, n):
            closest.append((names[i], names[j], dist_matrix[i, j]))
    closest.sort(key=lambda x: x[2])
    print()
    print("CLOSEST PAIRS (potential novel connections):")
    for a, b, d in closest[:10]:
        print(f"  {d:.3f}: {a} <-> {b}")
