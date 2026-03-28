"""
Explorer Modes — Four ways to navigate the tensor-embedded concept space.

Each mode answers a different question:
  1. FRONTIER SEEKER:  "Where is the emptiest space? What's unexplored?"
  2. BRIDGE BUILDER:   "What connects two distant clusters?"
  3. EFFICIENCY HUNTER: "Is there a simpler way to do what this does?"
  4. NOVELTY MINER:    "Which combination produces something NONE of its parts can?"

These are the use cases for Poros's exploration of the Lattice.
"""

import numpy as np
import sys, warnings, time
warnings.filterwarnings('ignore')

# ============================================================
# Distance functions — different ways to measure "closeness"
# ============================================================

def euclidean(a, b):
    """Raw distance in embedding space. Lower = more similar."""
    return float(np.linalg.norm(a - b))

def cosine_sim(a, b):
    """Angle between vectors. 1.0 = identical direction, 0 = orthogonal, -1 = opposite."""
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def behavioral_overlap(a, b, threshold=0.1):
    """What fraction of probe responses are similar? Higher = more behavioral overlap."""
    # Compare 12-feature chunks (one per probe)
    n_probes = len(a) // 12
    similar = 0
    for p in range(n_probes):
        chunk_a = a[p*12:(p+1)*12]
        chunk_b = b[p*12:(p+1)*12]
        if np.linalg.norm(chunk_a - chunk_b) < threshold * (np.linalg.norm(chunk_a) + 1e-10):
            similar += 1
    return similar / n_probes

def emergent_potential(a, b):
    """How much NEW structure would combining a and b produce?
    High when a and b are different but complementary."""
    # Complementarity: how different are they?
    diff = np.abs(a - b)
    complementarity = np.mean(diff)

    # Resonance: where both are strong (non-zero), multiply
    both_active = (np.abs(a) > 0.1) & (np.abs(b) > 0.1)
    resonance = np.mean(np.abs(a[both_active] * b[both_active])) if np.any(both_active) else 0

    # Emergent = high complementarity AND high resonance
    # (different but mutually amplifying)
    return float(complementarity * resonance)


# ============================================================
# Build the embedding space from our actual objects
# ============================================================

def build_space():
    """Embed a diverse set of computational objects."""
    from universal_embedder import embed

    objects = {
        # Pure math
        "square": lambda x: np.asarray(x, dtype=float) ** 2,
        "sqrt": lambda x: np.sqrt(np.abs(np.asarray(x, dtype=float))),
        "sin": lambda x: np.sin(np.asarray(x, dtype=float)),
        "cos": lambda x: np.cos(np.asarray(x, dtype=float)),
        "exp": lambda x: np.exp(np.clip(np.asarray(x, dtype=float), -10, 10)),
        "log": lambda x: np.log(np.abs(np.asarray(x, dtype=float)) + 1e-10),
        "tanh": lambda x: np.tanh(np.asarray(x, dtype=float)),
        "reciprocal": lambda x: 1.0 / (np.asarray(x, dtype=float) + 1e-10),
        "abs": lambda x: np.abs(np.asarray(x, dtype=float)),

        # Algorithms
        "sort": lambda x: np.sort(np.asarray(x, dtype=float).flatten()),
        "reverse": lambda x: np.asarray(x, dtype=float).flatten()[::-1],
        "cumsum": lambda x: np.cumsum(np.asarray(x, dtype=float).flatten()),
        "diff": lambda x: np.diff(np.asarray(x, dtype=float).flatten()),
        "unique": lambda x: np.unique(np.asarray(x, dtype=float).flatten()),
        "argsort": lambda x: np.argsort(np.asarray(x, dtype=float).flatten()).astype(float),

        # Reductions
        "mean": lambda x: np.mean(np.asarray(x, dtype=float)),
        "std": lambda x: np.std(np.asarray(x, dtype=float)),
        "max": lambda x: np.max(np.asarray(x, dtype=float)),
        "min": lambda x: np.min(np.asarray(x, dtype=float)),
        "sum": lambda x: np.sum(np.asarray(x, dtype=float)),
        "prod": lambda x: np.prod(np.clip(np.asarray(x, dtype=float).flatten()[:10], -10, 10)),
        "median": lambda x: np.median(np.asarray(x, dtype=float)),

        # Matrix ops
        "transpose": lambda x: np.asarray(x, dtype=float).T if np.asarray(x).ndim >= 2 else np.asarray(x, dtype=float),
        "trace": lambda x: np.trace(np.asarray(x, dtype=float)) if np.asarray(x).ndim == 2 else 0.0,
        "det": lambda x: np.linalg.det(np.asarray(x, dtype=float)) if np.asarray(x).ndim == 2 and np.asarray(x).shape[0] == np.asarray(x).shape[1] else 0.0,
        "eigvals": lambda x: np.sort(np.abs(np.linalg.eigvals(np.asarray(x, dtype=float)))) if np.asarray(x).ndim == 2 and np.asarray(x).shape[0] == np.asarray(x).shape[1] else np.array([0.0]),
        "svd_singular": lambda x: np.linalg.svd(np.asarray(x, dtype=float), compute_uv=False) if np.asarray(x).ndim == 2 else np.array([0.0]),
        "norm": lambda x: np.linalg.norm(np.asarray(x, dtype=float)),

        # Signal processing
        "fft_magnitude": lambda x: np.abs(np.fft.fft(np.asarray(x, dtype=float).flatten())),
        "autocorrelate": lambda x: np.correlate(np.asarray(x, dtype=float).flatten(), np.asarray(x, dtype=float).flatten(), mode='full'),
        "convolve_self": lambda x: np.convolve(np.asarray(x, dtype=float).flatten()[:20], np.asarray(x, dtype=float).flatten()[:20], mode='same'),

        # Iterative/chaotic
        "logistic_r3_5": lambda x: np.array([3.5 * float(np.mean(np.abs(np.asarray(x, dtype=float)))) % 1 * (1 - float(np.mean(np.abs(np.asarray(x, dtype=float)))) % 1)]),
        "collatz_step": lambda x: np.where(np.asarray(x, dtype=float) % 2 == 0, np.asarray(x, dtype=float) / 2, 3 * np.asarray(x, dtype=float) + 1),

        # Boolean/classification
        "is_positive": lambda x: float(np.all(np.asarray(x, dtype=float) > 0)),
        "is_sorted": lambda x: float(np.all(np.diff(np.asarray(x, dtype=float).flatten()) >= 0)) if np.asarray(x).size > 1 else 1.0,
        "count_nonzero": lambda x: float(np.count_nonzero(np.asarray(x, dtype=float))),
        "sign": lambda x: np.sign(np.asarray(x, dtype=float)),

        # Number theory
        "mod7": lambda x: np.asarray(x, dtype=float) % 7,
        "floor": lambda x: np.floor(np.asarray(x, dtype=float)),
        "gcd_with_6": lambda x: np.array([np.gcd(int(abs(float(np.mean(np.asarray(x, dtype=float))))), 6)], dtype=float),

        # Compression
        "compress_ratio": lambda x: len(__import__('zlib').compress(np.asarray(x, dtype=float).tobytes())) / max(np.asarray(x, dtype=float).nbytes, 1),
    }

    embeddings = {}
    for name, fn in objects.items():
        result = embed(fn)
        result["name"] = name
        embeddings[name] = result

    return embeddings


# ============================================================
# EXPLORER MODE 1: FRONTIER SEEKER
# "Where is nobody? What region of the space is emptiest?"
# ============================================================

def frontier_seek(embeddings, top_k=5):
    """Find the objects most isolated from everything else.
    These live on the frontier — the edge of the known space.
    The space AROUND them is unexplored."""

    names = list(embeddings.keys())
    addresses = np.array([embeddings[n]["address"] for n in names])

    # For each object, compute mean distance to all others
    isolation = []
    for i, name in enumerate(names):
        dists = np.array([euclidean(addresses[i], addresses[j]) for j in range(len(names)) if j != i])
        mean_dist = np.mean(dists)
        min_dist = np.min(dists)
        isolation.append((name, mean_dist, min_dist))

    isolation.sort(key=lambda x: -x[1])  # Most isolated first
    return isolation[:top_k]


# ============================================================
# EXPLORER MODE 2: BRIDGE BUILDER
# "What connects cluster A to cluster B?"
# ============================================================

def bridge_build(embeddings, cluster_a_names, cluster_b_names, top_k=5):
    """Find objects that are close to BOTH clusters.
    These are bridges — they connect otherwise distant regions."""

    names = list(embeddings.keys())
    addresses = {n: embeddings[n]["address"] for n in names}

    # Compute centroid of each cluster
    centroid_a = np.mean([addresses[n] for n in cluster_a_names], axis=0)
    centroid_b = np.mean([addresses[n] for n in cluster_b_names], axis=0)

    # For each non-cluster object, compute distance to both centroids
    bridges = []
    cluster_names = set(cluster_a_names) | set(cluster_b_names)
    for name in names:
        if name in cluster_names:
            continue
        dist_a = euclidean(addresses[name], centroid_a)
        dist_b = euclidean(addresses[name], centroid_b)
        # Bridge score: close to both = low sum of distances
        bridge_score = dist_a + dist_b
        balance = 1.0 - abs(dist_a - dist_b) / (dist_a + dist_b + 1e-10)  # 1.0 = equidistant
        bridges.append((name, bridge_score, balance, dist_a, dist_b))

    bridges.sort(key=lambda x: x[1])  # Closest to both clusters first
    return bridges[:top_k]


# ============================================================
# EXPLORER MODE 3: EFFICIENCY HUNTER
# "Is there a simpler object that does roughly what this complex one does?"
# ============================================================

def efficiency_hunt(embeddings, target_name, max_distance=8.0, top_k=5):
    """Find objects behaviorally similar to target but simpler.
    Simpler = higher success rate, fewer probes triggered, faster execution."""

    target = embeddings[target_name]
    target_addr = target["address"]
    target_complexity = target["meta"]["total_time_ms"]

    candidates = []
    for name, emb in embeddings.items():
        if name == target_name:
            continue
        dist = euclidean(target_addr, emb["address"])
        if dist > max_distance:
            continue

        complexity = emb["meta"]["total_time_ms"]
        success = emb["meta"]["success_rate"]

        # Efficiency = behavioral similarity / complexity
        similarity = 1.0 / (1.0 + dist)
        if complexity > 0:
            efficiency = similarity / complexity
        else:
            efficiency = similarity * 10  # Very fast = bonus

        candidates.append((name, dist, complexity, efficiency, success))

    candidates.sort(key=lambda x: -x[3])  # Highest efficiency first
    return candidates[:top_k]


# ============================================================
# EXPLORER MODE 4: NOVELTY MINER
# "Which PAIR produces the most emergent structure?"
# ============================================================

def novelty_mine(embeddings, top_k=10):
    """Find pairs with highest emergent potential.
    High emergent = different from each other but mutually amplifying."""

    names = list(embeddings.keys())
    addresses = {n: embeddings[n]["address"] for n in names}

    pairs = []
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            if j <= i:
                continue

            ep = emergent_potential(addresses[a], addresses[b])
            dist = euclidean(addresses[a], addresses[b])
            overlap = behavioral_overlap(addresses[a], addresses[b])

            pairs.append((a, b, ep, dist, overlap))

    pairs.sort(key=lambda x: -x[2])  # Highest emergent potential first
    return pairs[:top_k]


# ============================================================
# EXPLORER MODE 5: ANOMALY DETECTOR (bonus)
# "What doesn't fit? What's weird?"
# ============================================================

def anomaly_detect(embeddings, top_k=5):
    """Find objects whose embedding is unusual — high norm, strange probe patterns,
    or very different success rates from the population."""

    names = list(embeddings.keys())
    norms = {n: embeddings[n]["meta"]["address_norm"] for n in names}
    successes = {n: embeddings[n]["meta"]["success_rate"] for n in names}

    mean_norm = np.mean(list(norms.values()))
    std_norm = np.std(list(norms.values()))
    mean_success = np.mean(list(successes.values()))

    anomalies = []
    for name in names:
        norm_z = abs(norms[name] - mean_norm) / (std_norm + 1e-10)
        success_deviation = abs(successes[name] - mean_success)
        anomaly_score = norm_z + success_deviation * 5
        anomalies.append((name, anomaly_score, norms[name], successes[name]))

    anomalies.sort(key=lambda x: -x[1])
    return anomalies[:top_k]


# ============================================================
# RUN ALL MODES
# ============================================================

if __name__ == "__main__":
    print("Building embedding space...")
    embeddings = build_space()
    print(f"Embedded {len(embeddings)} objects in 240D space")
    print()

    # MODE 1: FRONTIER
    print("=" * 60)
    print("MODE 1: FRONTIER SEEKER")
    print("'Where is the emptiest space?'")
    print("=" * 60)
    frontiers = frontier_seek(embeddings)
    for name, mean_d, min_d in frontiers:
        print(f"  {name:20s}: mean_dist={mean_d:.2f}, nearest_neighbor={min_d:.2f}")
    print()
    print("  >> These objects are MOST ISOLATED. The space around them is unexplored.")
    print("  >> A new formula embedded near one of these would be a FRONTIER DISCOVERY.")
    print()

    # MODE 2: BRIDGE
    print("=" * 60)
    print("MODE 2: BRIDGE BUILDER")
    print("'What connects math formulas to algorithms?'")
    print("=" * 60)
    math_cluster = ["sin", "cos", "exp", "log", "sqrt", "square"]
    algo_cluster = ["sort", "reverse", "cumsum", "diff", "argsort"]
    bridges = bridge_build(embeddings, math_cluster, algo_cluster)
    for name, score, balance, da, db in bridges:
        print(f"  {name:20s}: bridge_score={score:.2f}, balance={balance:.2f} "
              f"(dist_to_math={da:.2f}, dist_to_algo={db:.2f})")
    print()
    print("  >> These objects CONNECT the math and algorithm clusters.")
    print("  >> They might reveal how mathematical structure translates to computation.")
    print()

    # MODE 3: EFFICIENCY
    print("=" * 60)
    print("MODE 3: EFFICIENCY HUNTER")
    print("'Is there a simpler way to do what eigvals does?'")
    print("=" * 60)
    efficiencies = efficiency_hunt(embeddings, "eigvals")
    for name, dist, complexity, eff, success in efficiencies:
        print(f"  {name:20s}: distance={dist:.2f}, complexity={complexity:.1f}ms, "
              f"efficiency={eff:.2f}, success={success:.0%}")
    print()
    print("  >> These objects BEHAVE LIKE eigvals but are SIMPLER/FASTER.")
    print("  >> Could any of them replace eigvals in a composition chain?")
    print()

    # MODE 4: NOVELTY
    print("=" * 60)
    print("MODE 4: NOVELTY MINER")
    print("'Which pairs have the most emergent potential?'")
    print("=" * 60)
    novels = novelty_mine(embeddings)
    for a, b, ep, dist, overlap in novels:
        print(f"  {a:15s} x {b:15s}: emergent={ep:.4f}, dist={dist:.2f}, overlap={overlap:.0%}")
    print()
    print("  >> These pairs are DIFFERENT but COMPLEMENTARY.")
    print("  >> Composing them is most likely to produce something NEITHER can do alone.")
    print()

    # MODE 5: ANOMALY
    print("=" * 60)
    print("MODE 5: ANOMALY DETECTOR")
    print("'What doesn't fit?'")
    print("=" * 60)
    anomalies = anomaly_detect(embeddings)
    for name, score, norm, success in anomalies:
        print(f"  {name:20s}: anomaly={score:.2f}, norm={norm:.2f}, success={success:.0%}")
    print()
    print("  >> These objects have UNUSUAL embeddings.")
    print("  >> They might be computational primitives that don't fit any category")
    print("  >> — which makes them candidates for ARCANUM classification.")
    print()

    # THE BIG PICTURE
    print("=" * 60)
    print("THE EXPLORATION LOOP")
    print("=" * 60)
    print()
    print("  1. FRONTIER SEEKER finds the emptiest regions")
    print("     -> Poros targets those regions in the next Siege")
    print()
    print("  2. NOVELTY MINER finds high-emergent pairs")
    print("     -> Poros composes them and tests for value")
    print()
    print("  3. BRIDGE BUILDER connects distant clusters")
    print("     -> Cross-domain discoveries (topology x number theory)")
    print()
    print("  4. EFFICIENCY HUNTER finds simpler alternatives")
    print("     -> Compression of the Lattice (fewer nodes, same coverage)")
    print()
    print("  5. ANOMALY DETECTOR finds things that don't fit")
    print("     -> Arcanum specimens (emergent objects with no category)")
    print()
    print("  Each mode feeds the others:")
    print("    Frontier discoveries become new nodes")
    print("    -> changes the novelty landscape")
    print("    -> creates new bridge opportunities")
    print("    -> may obsolete old nodes (efficiency)")
    print("    -> may produce anomalies (Arcanum)")
    print("    -> the frontier shifts")
    print("    -> LOOP")
