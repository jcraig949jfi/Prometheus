"""Behavioral fingerprint analysis for the Prometheus forge library.

Loads all v5 tools, runs each on a standardized battery, records
right/wrong as a binary vector, computes pairwise Hamming distances,
clusters tools by behavioral similarity, and reports how many genuinely
distinct reasoning strategies exist.

Usage:
    python behavioral_fingerprints.py
"""

import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
FORGE_DIR = SCRIPT_DIR.parent / "forge_v5"
OUTPUT_PATH = FORGE_DIR / "behavioral_fingerprints.json"

# Make sibling modules importable (trap generators live in src/)
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


# ---------------------------------------------------------------------------
# Architecture classification from docstring heuristics
# ---------------------------------------------------------------------------
_ARCH_A_MARKERS = [
    "Primary scoring via 58-category",
    "58-category constructive computation",
    "58-category constructive parsers",
]
_ARCH_C_MARKERS = [
    "Constructive computation + structural parsing",
]

def _classify_architecture(source: str) -> str:
    """Classify a tool's architecture from its source code."""
    # Look at the first 500 chars (docstring region)
    header = source[:500]
    for marker in _ARCH_A_MARKERS:
        if marker in header:
            return "A"
    for marker in _ARCH_C_MARKERS:
        if marker in header:
            return "C"
    # D is the default / catch-all (original struct-based tools)
    return "D"


# ---------------------------------------------------------------------------
# Tool loading
# ---------------------------------------------------------------------------
_SKIP_FILES = {
    "apply_metacognition.py", "all_scores.json", "ncd_baseline.py",
    "execution_evaluator.py", "efme_v2.py", "ibai_v2.py",
    "__init__.py",
}

def _is_tool_file(p: Path) -> bool:
    """True if p is a tool .py file (not a utility or batch file)."""
    if p.suffix != ".py":
        return False
    if p.name in _SKIP_FILES:
        return False
    if p.name.startswith("_"):
        return False
    return True


def load_tool(path: Path):
    """Load a ReasoningTool from a .py file. Returns (tool, arch) or raises."""
    source = path.read_text(encoding="utf-8")
    arch = _classify_architecture(source)

    mod_name = f"_fingerprint_{path.stem}"
    spec = importlib.util.spec_from_file_location(mod_name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tool = mod.ReasoningTool()
    # Clean up to avoid module leaks
    sys.modules.pop(mod_name, None)
    return tool, arch


# ---------------------------------------------------------------------------
# Battery generation
# ---------------------------------------------------------------------------
def _generate_battery():
    """Generate the standardized battery (seed=42, n_per_category=2)."""
    from trap_generator_extended import generate_full_battery
    battery = generate_full_battery(n_per_category=2, seed=42)
    if not battery:
        raise RuntimeError("generate_full_battery returned empty list")
    return battery


# ---------------------------------------------------------------------------
# Evaluation: run one tool on the full battery -> binary vector
# ---------------------------------------------------------------------------
def _evaluate_tool(tool, battery: list[dict]) -> np.ndarray:
    """Run tool.evaluate on each battery item. Returns binary vector (1=correct)."""
    results = np.zeros(len(battery), dtype=np.int8)
    for i, trap in enumerate(battery):
        prompt = trap["prompt"]
        candidates = trap["candidates"]
        correct = trap["correct"]
        try:
            ranked = tool.evaluate(prompt, candidates)
            if ranked and ranked[0]["candidate"] == correct:
                results[i] = 1
        except Exception:
            results[i] = 0
    return results


# ---------------------------------------------------------------------------
# Hamming distance (normalized)
# ---------------------------------------------------------------------------
def hamming_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized Hamming distance in [0, 1]."""
    n = len(a)
    if n == 0:
        return 0.0
    return float(np.sum(a != b)) / n


# ---------------------------------------------------------------------------
# Agglomerative clustering (single-linkage with distance threshold)
# ---------------------------------------------------------------------------
def agglomerative_cluster(dist_matrix: np.ndarray, threshold: float) -> np.ndarray:
    """Agglomerative clustering (complete-linkage) with distance threshold.

    Returns an array of cluster labels (0-indexed).
    Uses complete-linkage: merges clusters whose maximum inter-point
    distance is below threshold.

    Maintains a condensed inter-cluster distance matrix for efficiency.
    """
    n = len(dist_matrix)
    if n == 0:
        return np.array([], dtype=int)

    # Each point starts as its own cluster; membership[cid] = list of original indices
    membership = {i: [i] for i in range(n)}
    active = set(range(n))

    # Condensed inter-cluster distance (complete-linkage = max pairwise)
    # Initially just the original distances
    cl_dist = {}
    for i in range(n):
        for j in range(i + 1, n):
            cl_dist[(i, j)] = float(dist_matrix[i, j])

    next_id = n

    while len(active) > 1:
        # Find closest pair among active clusters
        best_dist = float("inf")
        best_pair = None
        for ci in active:
            for cj in active:
                if cj <= ci:
                    continue
                key = (ci, cj) if ci < cj else (cj, ci)
                d = cl_dist.get(key, float("inf"))
                if d < best_dist:
                    best_dist = d
                    best_pair = (ci, cj)

        if best_dist >= threshold or best_pair is None:
            break

        ci, cj = best_pair
        new_id = next_id
        next_id += 1
        membership[new_id] = membership[ci] + membership[cj]

        # Update distances: new cluster distance to each remaining cluster
        # Complete-linkage: max of the two merged clusters' distances
        for ck in active:
            if ck == ci or ck == cj:
                continue
            key_i = (min(ci, ck), max(ci, ck))
            key_j = (min(cj, ck), max(cj, ck))
            d_new = max(cl_dist.get(key_i, float("inf")),
                        cl_dist.get(key_j, float("inf")))
            cl_dist[(min(new_id, ck), max(new_id, ck))] = d_new

        # Remove merged clusters
        active.discard(ci)
        active.discard(cj)
        active.add(new_id)
        del membership[ci]
        del membership[cj]

    # Assign final labels
    result = np.zeros(n, dtype=int)
    for label_id, cid in enumerate(sorted(active)):
        for idx in membership[cid]:
            result[idx] = label_id

    return result


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------
def main():
    print("=" * 72)
    print("  Behavioral Fingerprint Analysis — Prometheus Forge v5")
    print("=" * 72)

    # 1. Generate battery
    print("\n[1/5] Generating standardized battery (seed=42, n_per_category=2)...")
    battery = _generate_battery()
    n_items = len(battery)
    categories = sorted(set(t.get("category", "unknown") for t in battery))
    print(f"  Battery: {n_items} items across {len(categories)} categories")

    # 2. Discover and load tools
    print("\n[2/5] Loading v5 tools...")
    tool_files = sorted(p for p in FORGE_DIR.iterdir() if _is_tool_file(p))
    print(f"  Found {len(tool_files)} tool files")

    tools = []       # list of (name, tool, arch)
    load_errors = []
    for p in tool_files:
        try:
            tool, arch = load_tool(p)
            tools.append((p.stem, tool, arch))
        except Exception as e:
            load_errors.append((p.stem, str(e)))

    print(f"  Loaded: {len(tools)} | Errors: {len(load_errors)}")
    if load_errors:
        for name, err in load_errors[:5]:
            print(f"    SKIP {name}: {err}")
        if len(load_errors) > 5:
            print(f"    ... and {len(load_errors) - 5} more")

    n_tools = len(tools)
    if n_tools < 2:
        print("ERROR: Need at least 2 tools to analyze. Exiting.")
        sys.exit(1)

    # 3. Run battery on all tools
    print(f"\n[3/5] Running {n_items}-item battery on {n_tools} tools...")
    names = []
    archs = []
    fingerprints = np.zeros((n_tools, n_items), dtype=np.int8)

    t0 = time.time()
    for i, (name, tool, arch) in enumerate(tools):
        fingerprints[i] = _evaluate_tool(tool, battery)
        names.append(name)
        archs.append(arch)
        acc = fingerprints[i].sum() / n_items
        if (i + 1) % 50 == 0 or i == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (n_tools - i - 1) / rate if rate > 0 else 0
            print(f"    [{i+1:3d}/{n_tools}] {name[:55]:55s} acc={acc:.2%}  "
                  f"({rate:.1f} tools/s, ETA {eta:.0f}s)")

    elapsed_total = time.time() - t0
    print(f"  Done in {elapsed_total:.1f}s ({n_tools/elapsed_total:.1f} tools/s)")

    # Per-tool accuracy
    accuracies = fingerprints.sum(axis=1) / n_items

    # 4. Compute pairwise Hamming distance matrix
    print("\n[4/5] Computing pairwise Hamming distances...")
    dist_matrix = np.zeros((n_tools, n_tools), dtype=np.float32)
    for i in range(n_tools):
        for j in range(i + 1, n_tools):
            d = hamming_distance(fingerprints[i], fingerprints[j])
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d

    # 5. Cluster and analyze
    print("\n[5/5] Clustering and analyzing...")

    REDUNDANCY_THRESHOLD = 0.05   # Hamming < 5% = nearly identical
    CLUSTER_THRESHOLD = 0.15      # Distance threshold for distinct profiles

    # Cluster all tools
    labels = agglomerative_cluster(dist_matrix, CLUSTER_THRESHOLD)
    n_clusters = len(set(labels))

    # Find redundant pairs
    redundant_pairs = []
    for i in range(n_tools):
        for j in range(i + 1, n_tools):
            if dist_matrix[i, j] < REDUNDANCY_THRESHOLD:
                redundant_pairs.append((names[i], names[j], float(dist_matrix[i, j])))
    redundant_pairs.sort(key=lambda x: x[2])

    # Find maximally complementary pairs (high disagreement)
    complementary_pairs = []
    for i in range(n_tools):
        for j in range(i + 1, n_tools):
            complementary_pairs.append((names[i], names[j], float(dist_matrix[i, j])))
    complementary_pairs.sort(key=lambda x: x[2], reverse=True)

    # Mean distance to all others (uniqueness score)
    mean_distances = []
    for i in range(n_tools):
        others = [dist_matrix[i, j] for j in range(n_tools) if j != i]
        md = float(np.mean(others)) if others else 0.0
        mean_distances.append((names[i], archs[i], md, float(accuracies[i])))
    mean_distances.sort(key=lambda x: x[2], reverse=True)

    # Per-architecture breakdown
    arch_counts = {}
    arch_clusters = {}
    for arch_label in ["A", "C", "D"]:
        indices = [i for i in range(n_tools) if archs[i] == arch_label]
        arch_counts[arch_label] = len(indices)
        if len(indices) >= 2:
            sub_dist = np.zeros((len(indices), len(indices)), dtype=np.float32)
            for ii, i in enumerate(indices):
                for jj, j in enumerate(indices):
                    sub_dist[ii, jj] = dist_matrix[i, j]
            sub_labels = agglomerative_cluster(sub_dist, CLUSTER_THRESHOLD)
            arch_clusters[arch_label] = len(set(sub_labels))
        elif len(indices) == 1:
            arch_clusters[arch_label] = 1
        else:
            arch_clusters[arch_label] = 0

    # Cluster membership listing
    cluster_members = {}
    for i, lbl in enumerate(labels):
        cluster_members.setdefault(int(lbl), []).append({
            "name": names[i],
            "arch": archs[i],
            "accuracy": round(float(accuracies[i]), 4),
        })

    # -----------------------------------------------------------------------
    # Report
    # -----------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("  RESULTS")
    print("=" * 72)

    print(f"\n  Tools analyzed:       {n_tools}")
    print(f"  Battery items:        {n_items}")
    print(f"  Mean accuracy:        {float(accuracies.mean()):.2%}")
    print(f"  Accuracy range:       [{float(accuracies.min()):.2%}, {float(accuracies.max()):.2%}]")

    print(f"\n  DISTINCT BEHAVIORAL PROFILES (threshold={CLUSTER_THRESHOLD}):")
    print(f"    Total clusters:     {n_clusters}")

    print(f"\n  PER-ARCHITECTURE BREAKDOWN:")
    for arch_label in ["A", "C", "D"]:
        n_arch = arch_counts.get(arch_label, 0)
        n_cl = arch_clusters.get(arch_label, 0)
        if n_arch > 0:
            arch_indices = [i for i in range(n_tools) if archs[i] == arch_label]
            arch_acc = float(np.mean([accuracies[i] for i in arch_indices]))
            print(f"    Arch {arch_label}: {n_arch:3d} tools -> {n_cl:2d} distinct profiles  "
                  f"(mean acc {arch_acc:.2%})")

    print(f"\n  REDUNDANT PAIRS (Hamming < {REDUNDANCY_THRESHOLD}):")
    print(f"    Count: {len(redundant_pairs)}")
    if redundant_pairs:
        for a, b, d in redundant_pairs[:10]:
            print(f"      {d:.4f}  {a[:40]}  <->  {b[:40]}")
        if len(redundant_pairs) > 10:
            print(f"      ... and {len(redundant_pairs) - 10} more")

    print(f"\n  MAXIMALLY COMPLEMENTARY PAIRS (top 10):")
    for a, b, d in complementary_pairs[:10]:
        print(f"      {d:.4f}  {a[:40]}  <->  {b[:40]}")

    print(f"\n  TOP 20 MOST UNIQUE TOOLS (highest mean distance to all others):")
    for rank, (name, arch, md, acc) in enumerate(mean_distances[:20], 1):
        print(f"    {rank:2d}. [{arch}] mean_dist={md:.4f}  acc={acc:.2%}  {name}")

    print(f"\n  CLUSTER SIZES:")
    sizes = sorted([(lbl, len(members)) for lbl, members in cluster_members.items()],
                   key=lambda x: x[1], reverse=True)
    for lbl, sz in sizes[:20]:
        sample = cluster_members[lbl][:3]
        sample_str = ", ".join(f"{m['name'][:35]}" for m in sample)
        if sz > 3:
            sample_str += f", ... (+{sz - 3})"
        print(f"    Cluster {lbl:2d}: {sz:3d} tools  e.g. {sample_str}")
    if len(sizes) > 20:
        print(f"    ... and {len(sizes) - 20} more clusters")

    # -----------------------------------------------------------------------
    # Save full JSON
    # -----------------------------------------------------------------------
    output = {
        "meta": {
            "n_tools": n_tools,
            "n_battery_items": n_items,
            "n_categories": len(categories),
            "categories": categories,
            "cluster_threshold": CLUSTER_THRESHOLD,
            "redundancy_threshold": REDUNDANCY_THRESHOLD,
            "load_errors": len(load_errors),
        },
        "summary": {
            "n_distinct_profiles": n_clusters,
            "mean_accuracy": round(float(accuracies.mean()), 4),
            "accuracy_std": round(float(accuracies.std()), 4),
            "accuracy_min": round(float(accuracies.min()), 4),
            "accuracy_max": round(float(accuracies.max()), 4),
            "n_redundant_pairs": len(redundant_pairs),
            "per_architecture": {
                arch: {
                    "n_tools": arch_counts.get(arch, 0),
                    "n_profiles": arch_clusters.get(arch, 0),
                }
                for arch in ["A", "C", "D"]
            },
        },
        "tools": {
            names[i]: {
                "architecture": archs[i],
                "accuracy": round(float(accuracies[i]), 4),
                "fingerprint": fingerprints[i].tolist(),
                "cluster": int(labels[i]),
                "mean_distance": round(float(np.mean(
                    [dist_matrix[i, j] for j in range(n_tools) if j != i]
                )), 4) if n_tools > 1 else 0.0,
            }
            for i in range(n_tools)
        },
        "clusters": {
            str(lbl): members
            for lbl, members in sorted(cluster_members.items())
        },
        "redundant_pairs": [
            {"tool_a": a, "tool_b": b, "hamming": round(d, 4)}
            for a, b, d in redundant_pairs
        ],
        "complementary_pairs": [
            {"tool_a": a, "tool_b": b, "hamming": round(d, 4)}
            for a, b, d in complementary_pairs[:50]
        ],
        "top_unique": [
            {"name": name, "arch": arch, "mean_distance": round(md, 4), "accuracy": round(acc, 4)}
            for name, arch, md, acc in mean_distances[:20]
        ],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\n  Full data saved to: {OUTPUT_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    main()
