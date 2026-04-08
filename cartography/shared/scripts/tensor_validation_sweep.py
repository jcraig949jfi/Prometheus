"""
Tensor Validation Sweep — separate genuine structure from arithmetic confounds.
================================================================================
python tensor_validation_sweep.py [--top N] [--out PATH]

For each dataset pair with non-zero SVD bond dimension, computes:
  1. Shared concepts (bridge points) between the two datasets
  2. Correlation matrix between objects projected onto shared concepts
  3. Partial correlation controlling for the dominant confound
  4. Classification: TAUTOLOGICAL / STRUCTURAL / MIXED

No LLM calls.  Pure numpy/scipy computation over concept_links.jsonl.
"""

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy import sparse, stats

# ---------------------------------------------------------------------------
# Paths (relative to script location, same convention as tensor_bridge.py)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parents[1] / "convergence" / "data"
LINKS_PATH = DATA_DIR / "concept_links.jsonl"
BRIDGES_PATH = DATA_DIR / "tensor_bridges.json"
OUTPUT_PATH = DATA_DIR / "tensor_validation_sweep.json"

# ---------------------------------------------------------------------------
# Concept classification
# ---------------------------------------------------------------------------

# Patterns that are arithmetic / tautological confounds
TAUTOLOGICAL_PATTERNS = [
    re.compile(r"^integer_\d+$"),
    re.compile(r"^conductor_\d+$"),
    re.compile(r"^determinant_\d+$"),
    re.compile(r"^crossing_\d+$"),
    re.compile(r"^degree_\d+$"),
    re.compile(r"^dimension_\d+$"),
    re.compile(r"^rank_\d+$"),
    re.compile(r"^fvector_"),
    re.compile(r"^point_group_"),
    re.compile(r"^spacegroup_\d+$"),
    re.compile(r"^crystal_"),
]

GENERIC_CONCEPTS = {
    "prime", "odd", "even", "small_integer", "medium_integer", "large_integer",
    "perfect_square", "perfect_cube", "supersingular",
}

# Structural = verb-based or domain-specific relational concepts
STRUCTURAL_PATTERN = re.compile(r"^verb_")

# Domain-specific non-numeric concepts that indicate real structure
DOMAIN_PREFIXES = [
    "has_", "namespace_", "topic_", "mizar_", "galois_", "ramification_",
    "collection_", "graph_", "topo_", "object_type_", "symbol_", "extension_",
    "class_",
]


def classify_concept(concept: str) -> str:
    """Classify a single concept as TAUTOLOGICAL, STRUCTURAL, or GENERIC."""
    if concept in GENERIC_CONCEPTS:
        return "GENERIC"
    for pat in TAUTOLOGICAL_PATTERNS:
        if pat.match(concept):
            return "TAUTOLOGICAL"
    if STRUCTURAL_PATTERN.match(concept):
        return "STRUCTURAL"
    for prefix in DOMAIN_PREFIXES:
        if concept.startswith(prefix):
            return "STRUCTURAL"
    # Unrecognized — treat as potentially structural
    return "STRUCTURAL"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_links(path: Path):
    """Load concept_links.jsonl.  Returns links list and index dicts."""
    links = []
    datasets = set()
    objects = set()
    concepts = set()

    with open(path) as f:
        for line in f:
            rec = json.loads(line)
            ds = rec["dataset"]
            obj = rec["object_id"]
            con = rec["concept"]
            links.append((ds, obj, con))
            datasets.add(ds)
            objects.add((ds, obj))
            concepts.add(con)

    dataset_idx = {d: i for i, d in enumerate(sorted(datasets))}
    object_idx = {o: i for i, o in enumerate(sorted(objects))}
    concept_idx = {c: i for i, c in enumerate(sorted(concepts))}

    return links, dataset_idx, object_idx, concept_idx


def load_svd_results(path: Path) -> dict:
    """Load precomputed SVD bond dimensions from tensor_bridges.json."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("svd_bond_dimensions", {})


# ---------------------------------------------------------------------------
# Build per-dataset concept profiles
# ---------------------------------------------------------------------------

def build_dataset_concept_profiles(links, dataset_idx, object_idx, concept_idx):
    """
    For each dataset, build a sparse matrix: rows=objects_in_dataset, cols=concepts.
    Also build per-dataset object lists (local indices).

    Returns:
        ds_matrices: {ds_name: sparse CSR (n_ds_objects x n_concepts)}
        ds_obj_lists: {ds_name: list of (dataset, object_id) tuples in row order}
    """
    n_con = len(concept_idx)

    # Group links by dataset
    ds_links = defaultdict(list)  # ds -> list of (obj, concept)
    for ds, obj, con in links:
        ds_links[ds].append((obj, con))

    ds_matrices = {}
    ds_obj_lists = {}

    for ds in sorted(dataset_idx):
        # Build local object index for this dataset
        local_objs = sorted(set(obj for obj, _ in ds_links[ds]))
        local_obj_idx = {o: i for i, o in enumerate(local_objs)}

        rows, cols, data = [], [], []
        for obj, con in ds_links[ds]:
            rows.append(local_obj_idx[obj])
            cols.append(concept_idx[con])
            data.append(1.0)

        mat = sparse.csr_matrix(
            (data, (rows, cols)),
            shape=(len(local_objs), n_con),
            dtype=np.float64,
        )
        # Deduplicate
        mat.data[:] = np.minimum(mat.data, 1.0)

        ds_matrices[ds] = mat
        ds_obj_lists[ds] = [(ds, o) for o in local_objs]

    return ds_matrices, ds_obj_lists


# ---------------------------------------------------------------------------
# Shared concept analysis for a dataset pair
# ---------------------------------------------------------------------------

def find_shared_concepts(ds_matrices, ds1, ds2, concept_idx):
    """
    Find concepts that appear in BOTH datasets.
    Returns list of (concept_name, count_ds1, count_ds2).
    """
    inv_con = {v: k for k, v in concept_idx.items()}

    # Column sums = how many objects in each dataset have each concept
    freq1 = np.asarray(ds_matrices[ds1].sum(axis=0)).ravel()
    freq2 = np.asarray(ds_matrices[ds2].sum(axis=0)).ravel()

    shared_mask = (freq1 > 0) & (freq2 > 0)
    shared_indices = np.where(shared_mask)[0]

    results = []
    for ci in shared_indices:
        results.append((inv_con[ci], int(freq1[ci]), int(freq2[ci])))

    # Sort by geometric mean of frequencies (most impactful first)
    results.sort(key=lambda x: -(x[1] * x[2]) ** 0.5)
    return results


def compute_correlation_matrix(ds_matrices, ds1, ds2, concept_idx, shared_concepts):
    """
    Project both datasets onto the shared concept subspace and compute
    the correlation between concept usage vectors.

    For each shared concept c, we have:
      - v1[c] = fraction of ds1 objects that have concept c
      - v2[c] = fraction of ds2 objects that have concept c

    Returns (raw_corr, concept_vectors_ds1, concept_vectors_ds2, shared_concept_names)
    """
    if not shared_concepts:
        return 0.0, np.array([]), np.array([]), []

    shared_names = [sc[0] for sc in shared_concepts]
    shared_cidx = [concept_idx[name] for name in shared_names]

    # Concept frequency vectors (fraction of objects with each concept)
    n1 = ds_matrices[ds1].shape[0]
    n2 = ds_matrices[ds2].shape[0]

    freq1 = np.asarray(ds_matrices[ds1][:, shared_cidx].sum(axis=0)).ravel() / max(n1, 1)
    freq2 = np.asarray(ds_matrices[ds2][:, shared_cidx].sum(axis=0)).ravel() / max(n2, 1)

    # Pearson correlation between the two frequency vectors
    if len(freq1) < 2 or np.std(freq1) == 0 or np.std(freq2) == 0:
        raw_corr = 0.0
    else:
        raw_corr, _ = stats.pearsonr(freq1, freq2)

    return float(raw_corr), freq1, freq2, shared_names


def compute_partial_correlation(freq1, freq2, shared_names, concept_idx):
    """
    Compute partial correlation after removing the arithmetic confound.

    The confound: integer_N concepts create spurious correlation because
    both datasets share small integers by coincidence.

    Strategy: extract the "integer value" from integer_N concepts, build
    a confound vector, and partial it out.
    """
    if len(freq1) < 3:
        return 0.0, "insufficient_concepts"

    # Build confound vector: for integer_N concepts, use N as the value.
    # For other numeric concepts (conductor_N, determinant_N), use N.
    # For non-numeric concepts, use 0.
    confound = np.zeros(len(shared_names))
    n_numeric = 0
    for i, name in enumerate(shared_names):
        m = re.search(r"_(\d+\.?\d*)$", name)
        if m:
            confound[i] = float(m.group(1))
            n_numeric += 1
        elif name in GENERIC_CONCEPTS:
            # Generic concepts get a small arbitrary value to mark them
            confound[i] = 1.0
            n_numeric += 1

    confound_type = "numeric_value"

    if n_numeric < 2 or np.std(confound) == 0:
        # No numeric confound to remove — partial corr = raw corr
        return float(stats.pearsonr(freq1, freq2)[0]) if np.std(freq1) > 0 and np.std(freq2) > 0 else 0.0, "no_confound"

    # Partial correlation: corr(freq1, freq2 | confound)
    # r_12.3 = (r_12 - r_13 * r_23) / sqrt((1 - r_13^2)(1 - r_23^2))
    def safe_pearsonr(a, b):
        if np.std(a) == 0 or np.std(b) == 0:
            return 0.0
        return float(stats.pearsonr(a, b)[0])

    r12 = safe_pearsonr(freq1, freq2)
    r13 = safe_pearsonr(freq1, confound)
    r23 = safe_pearsonr(freq2, confound)

    denom = ((1 - r13**2) * (1 - r23**2)) ** 0.5
    if denom < 1e-10:
        partial_r = 0.0
    else:
        partial_r = (r12 - r13 * r23) / denom

    return float(partial_r), confound_type


# ---------------------------------------------------------------------------
# Pair-level validation
# ---------------------------------------------------------------------------

def validate_pair(ds_matrices, ds1, ds2, concept_idx, svd_info):
    """Full validation for one dataset pair."""
    shared_concepts = find_shared_concepts(ds_matrices, ds1, ds2, concept_idx)

    # Classify each shared concept
    classifications = Counter()
    concept_details = []
    for name, c1, c2 in shared_concepts:
        cls = classify_concept(name)
        classifications[cls] += 1
        concept_details.append({
            "concept": name,
            "type": cls,
            "count_ds1": c1,
            "count_ds2": c2,
            "geometric_mean": round((c1 * c2) ** 0.5, 2),
        })

    # Compute correlations
    raw_corr, freq1, freq2, shared_names = compute_correlation_matrix(
        ds_matrices, ds1, ds2, concept_idx, shared_concepts
    )

    partial_corr, confound_type = compute_partial_correlation(
        freq1, freq2, shared_names, concept_idx
    )

    # Determine verdict
    n_taut = classifications.get("TAUTOLOGICAL", 0) + classifications.get("GENERIC", 0)
    n_struct = classifications.get("STRUCTURAL", 0)
    n_total = n_taut + n_struct

    if n_total == 0:
        verdict = "NO_CONNECTION"
    elif n_struct == 0:
        verdict = "TAUTOLOGICAL"
    elif n_taut == 0:
        verdict = "STRUCTURAL"
    else:
        struct_frac = n_struct / n_total
        if struct_frac >= 0.6:
            verdict = "STRUCTURAL"
        elif struct_frac <= 0.2:
            verdict = "TAUTOLOGICAL"
        else:
            verdict = "MIXED"

    # Refine verdict using partial correlation
    # If partial corr drops dramatically, the connection is confound-driven
    if abs(raw_corr) > 0.01 and confound_type != "no_confound":
        corr_retention = abs(partial_corr) / max(abs(raw_corr), 1e-10)
        if corr_retention < 0.3 and verdict != "TAUTOLOGICAL":
            verdict = "TAUTOLOGICAL"  # Correlation collapses after removing confound
    else:
        corr_retention = 1.0

    # Top 5 shared concepts by impact (geometric mean of counts)
    top5 = concept_details[:5]

    # Top 5 structural concepts specifically
    top5_structural = [cd for cd in concept_details if cd["type"] == "STRUCTURAL"][:5]

    return {
        "pair": f"{ds1}--{ds2}",
        "bond_dim": svd_info.get("bond_dim", 0),
        "top_singular_value": svd_info.get("top_singular_values", [0])[0],
        "shape": svd_info.get("shape", [0, 0]),
        "n_shared_concepts": len(shared_concepts),
        "n_tautological": n_taut,
        "n_structural": n_struct,
        "structural_fraction": round(n_struct / max(n_total, 1), 3),
        "raw_correlation": round(raw_corr, 6),
        "partial_correlation": round(partial_corr, 6),
        "confound_type": confound_type,
        "correlation_retention": round(corr_retention, 3),
        "verdict": verdict,
        "top5_concepts": top5,
        "top5_structural_concepts": top5_structural,
    }


# ---------------------------------------------------------------------------
# Report printing
# ---------------------------------------------------------------------------

VERDICT_SYMBOLS = {
    "STRUCTURAL": "[GENUINE]",
    "MIXED": "[ MIXED ]",
    "TAUTOLOGICAL": "[CONFOUND]",
    "NO_CONNECTION": "[ EMPTY ]",
}


def print_report(results):
    """Print a human-readable validation report."""
    print()
    print("=" * 78)
    print("TENSOR VALIDATION SWEEP — Genuine Structure vs Arithmetic Confound")
    print("=" * 78)

    # Sort by bond_dim descending, then by structural fraction
    results.sort(key=lambda r: (-r["bond_dim"], -r["structural_fraction"]))

    for r in results:
        sym = VERDICT_SYMBOLS.get(r["verdict"], "[?????]")
        print(f"\n  {sym} {r['pair']}")
        print(f"    Bond dim: {r['bond_dim']}  |  Top SV: {r['top_singular_value']:.1f}  |  Shape: {r['shape']}")
        print(f"    Shared concepts: {r['n_shared_concepts']} "
              f"(structural: {r['n_structural']}, tautological: {r['n_tautological']})")
        print(f"    Raw correlation:     {r['raw_correlation']:+.4f}")
        print(f"    Partial correlation: {r['partial_correlation']:+.4f}  "
              f"(confound: {r['confound_type']}, retention: {r['correlation_retention']:.1%})")

        if r["top5_structural_concepts"]:
            concepts_str = ", ".join(
                f"{c['concept']}({c['count_ds1']}/{c['count_ds2']})"
                for c in r["top5_structural_concepts"]
            )
            print(f"    Top structural: {concepts_str}")

        if r["top5_concepts"]:
            concepts_str = ", ".join(
                f"{c['concept']}[{c['type'][0]}]"
                for c in r["top5_concepts"]
            )
            print(f"    Top 5 overall:  {concepts_str}")

    # Summary
    verdicts = Counter(r["verdict"] for r in results)
    print(f"\n{'=' * 78}")
    print("SUMMARY")
    print(f"{'=' * 78}")
    print(f"  Pairs analyzed: {len(results)}")
    for v in ["STRUCTURAL", "MIXED", "TAUTOLOGICAL", "NO_CONNECTION"]:
        if verdicts.get(v, 0) > 0:
            pairs = [r["pair"] for r in results if r["verdict"] == v]
            print(f"  {VERDICT_SYMBOLS[v]:10s} {verdicts[v]:2d}  — {', '.join(pairs)}")

    genuine = [r for r in results if r["verdict"] == "STRUCTURAL"]
    if genuine:
        print(f"\n  GENUINE STRUCTURAL CONNECTIONS:")
        for r in genuine:
            top_struct = [c["concept"] for c in r["top5_structural_concepts"]]
            print(f"    {r['pair']:30s}  bond_dim={r['bond_dim']}  "
                  f"partial_r={r['partial_correlation']:+.4f}  "
                  f"via {', '.join(top_struct[:3])}")

    confounds = [r for r in results if r["verdict"] == "TAUTOLOGICAL"]
    if confounds:
        print(f"\n  ARITHMETIC CONFOUNDS (connection is just shared integers):")
        for r in confounds:
            top_taut = [c["concept"] for c in r["top5_concepts"] if c["type"] != "STRUCTURAL"][:3]
            print(f"    {r['pair']:30s}  bond_dim={r['bond_dim']}  "
                  f"raw_r={r['raw_correlation']:+.4f} -> partial_r={r['partial_correlation']:+.4f}  "
                  f"via {', '.join(top_taut) if top_taut else 'generic'}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Tensor Validation Sweep: separate genuine bridges from confounds"
    )
    parser.add_argument("--top", type=int, default=10,
                        help="Number of top pairs to analyze (by bond_dim)")
    parser.add_argument("--out", type=str, default=str(OUTPUT_PATH),
                        help="Output JSON path")
    args = parser.parse_args()

    t0 = time.time()

    print("=" * 78)
    print("TENSOR VALIDATION SWEEP")
    print("=" * 78)

    # 1. Load concept links
    print("\n[1/4] Loading concept links...")
    links, dataset_idx, object_idx, concept_idx = load_links(LINKS_PATH)
    print(f"  {len(links):,} links, {len(dataset_idx)} datasets, "
          f"{len(concept_idx):,} concepts, {len(object_idx):,} objects")

    # 2. Load SVD results
    print("\n[2/4] Loading SVD bond dimensions...")
    svd_results = load_svd_results(BRIDGES_PATH)
    nonzero = {k: v for k, v in svd_results.items() if v.get("bond_dim", 0) > 0}
    print(f"  {len(nonzero)} pairs with non-zero bond dimension")

    # Sort by bond_dim descending, take top N
    sorted_pairs = sorted(nonzero.items(), key=lambda x: -x[1]["bond_dim"])
    target_pairs = sorted_pairs[:args.top]

    # 3. Build per-dataset matrices
    print("\n[3/4] Building per-dataset concept matrices...")
    ds_matrices, ds_obj_lists = build_dataset_concept_profiles(
        links, dataset_idx, object_idx, concept_idx
    )
    for ds, mat in sorted(ds_matrices.items()):
        print(f"  {ds:15s}: {mat.shape[0]:>6,} objects x {mat.shape[1]:>6,} concepts, "
              f"nnz={mat.nnz:>8,}")

    # 4. Validate each pair
    print(f"\n[4/4] Validating top {len(target_pairs)} connected pairs...")
    validation_results = []

    for pair_key, svd_info in target_pairs:
        ds1, ds2 = pair_key.split("--")
        result = validate_pair(ds_matrices, ds1, ds2, concept_idx, svd_info)
        validation_results.append(result)

    # Print report
    print_report(validation_results)

    # Save results
    elapsed = time.time() - t0
    output = {
        "meta": {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_pairs_analyzed": len(validation_results),
            "top_k": args.top,
            "n_links": len(links),
            "n_concepts": len(concept_idx),
            "elapsed_seconds": round(elapsed, 2),
        },
        "pairs": validation_results,
        "summary": {
            "structural": [r["pair"] for r in validation_results if r["verdict"] == "STRUCTURAL"],
            "mixed": [r["pair"] for r in validation_results if r["verdict"] == "MIXED"],
            "tautological": [r["pair"] for r in validation_results if r["verdict"] == "TAUTOLOGICAL"],
        },
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {out_path}")
    print(f"Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
