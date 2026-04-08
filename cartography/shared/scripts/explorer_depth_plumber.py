"""
Explorer: Depth Plumber — What lives at the bottom of the abstraction axis?
============================================================================
Loads abstraction depths from the BFS-computed depth map and explores the
deepest objects (depth >= 10). For each, gathers name, terms, cross-reference
count, and entropy, then classifies them:

  - "Connected deep": high depth but still references core sequences (depth 0)
  - "Isolated deep":  high depth AND low cross-ref degree (true frontier)
  - "Dead end":       high depth AND zero cross-references (mathematical cul-de-sac)

Answers the key question: is the bottom of the abstraction axis EMPTY or POPULATED?

Usage:
    python explorer_depth_plumber.py
"""

import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

# --- Imports from search_engine ---
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from search_engine import (
    _load_oeis, _oeis_cache,
    _load_oeis_crossrefs, _oeis_xref_cache, _oeis_xref_reverse,
    _load_oeis_names, _oeis_names_cache,
)

REPO = Path(__file__).resolve().parents[3]
DEPTHS_FILE = REPO / "cartography" / "convergence" / "data" / "abstraction_depths.json"
OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
OUTPUT_FILE = OUTPUT_DIR / "depth_plumber_report.json"

# Parameters
DEEP_THRESHOLD = 10    # Minimum depth to qualify as "deep"
LOW_DEGREE = 3         # Max total degree to be "isolated"
TOP_N_REPORT = 30      # Top N deepest to display in detail


# ---------------------------------------------------------------------------
# Load abstraction depths (all datasets)
# ---------------------------------------------------------------------------

def load_depths() -> dict:
    """Load abstraction_depths.json. Returns the full dict with dataset keys."""
    if not DEPTHS_FILE.exists():
        print(f"  ERROR: {DEPTHS_FILE} not found")
        return {}
    with open(DEPTHS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Compute Shannon entropy of first differences
# ---------------------------------------------------------------------------

def sequence_entropy(terms: list[int], max_diffs: int = 30) -> float:
    """Shannon entropy of first differences (bits)."""
    if len(terms) < 2:
        return 0.0
    diffs = [terms[i + 1] - terms[i] for i in range(min(len(terms) - 1, max_diffs))]
    if not diffs:
        return 0.0
    counts = Counter(diffs)
    total = len(diffs)
    return -sum(
        (c / total) * math.log2(c / total)
        for c in counts.values() if c > 0
    )


# ---------------------------------------------------------------------------
# Get cross-reference degree
# ---------------------------------------------------------------------------

def xref_degree(seq_id: str) -> tuple[int, int]:
    """Return (out_degree, in_degree) for a sequence."""
    out_deg = len(_oeis_xref_cache.get(seq_id, set()))
    in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
    return out_deg, in_deg


def references_core(seq_id: str, core_ids: set[str]) -> bool:
    """Check if seq_id references any core (depth-0) sequence."""
    out_refs = _oeis_xref_cache.get(seq_id, set())
    in_refs = _oeis_xref_reverse.get(seq_id, set())
    return bool((out_refs | in_refs) & core_ids)


# ---------------------------------------------------------------------------
# Classify deep sequences
# ---------------------------------------------------------------------------

def classify(seq_id: str, depth: int, core_ids: set[str]) -> str:
    """Classify a deep sequence into one of three categories."""
    out_deg, in_deg = xref_degree(seq_id)
    total_deg = out_deg + in_deg

    if total_deg == 0:
        return "dead_end"
    elif references_core(seq_id, core_ids):
        return "connected_deep"
    elif total_deg <= LOW_DEGREE:
        return "isolated_deep"
    else:
        return "connected_deep"  # has refs, just not to cores


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    print("=" * 70)
    print("Explorer: Depth Plumber — What lives at the bottom?")
    print("=" * 70)

    # 1. Load depth data
    print("\n[1] Loading abstraction depths...")
    all_depths = load_depths()
    if not all_depths:
        return

    metadata = all_depths.get("metadata", {})
    print(f"    Datasets: {[k for k in all_depths if k != 'metadata']}")
    for k, v in metadata.items():
        print(f"    {k}: {v}")

    # 2. Load OEIS data for enrichment
    print("\n[2] Loading OEIS sequences, names, cross-references...")
    _load_oeis()
    _load_oeis_names()
    _load_oeis_crossrefs()

    # 3. Collect ALL depths across datasets
    print("\n[3] Analyzing depth distribution across all datasets...")

    # Combined depth distribution
    all_entries = []  # list of (dataset, obj_id, depth)
    for dataset in all_depths:
        if dataset == "metadata":
            continue
        depth_map = all_depths[dataset]
        for obj_id, depth in depth_map.items():
            all_entries.append((dataset, obj_id, depth))

    print(f"    Total objects with depth assignments: {len(all_entries):,}")

    # Depth distribution
    depth_dist = Counter(depth for _, _, depth in all_entries)
    print(f"\n    Depth distribution (all datasets):")
    for d in sorted(depth_dist.keys()):
        print(f"      depth {d:3d}: {depth_dist[d]:>8,} objects")

    # 4. Find deep objects (depth >= DEEP_THRESHOLD)
    # Also try adaptive threshold: if DEEP_THRESHOLD yields nothing, use max/2
    max_depth = max(depth_dist.keys()) if depth_dist else 0
    effective_threshold = DEEP_THRESHOLD
    deep_entries = [(ds, oid, d) for ds, oid, d in all_entries if d >= effective_threshold]

    if not deep_entries and max_depth > 0:
        effective_threshold = max(1, max_depth // 2)
        deep_entries = [(ds, oid, d) for ds, oid, d in all_entries if d >= effective_threshold]
        print(f"\n    No objects at depth >= {DEEP_THRESHOLD}. "
              f"Adapting threshold to {effective_threshold} (max_depth={max_depth})")

    print(f"\n[4] Deep objects (depth >= {effective_threshold}): {len(deep_entries):,}")

    # Dataset breakdown for deep objects
    deep_by_dataset = Counter(ds for ds, _, _ in deep_entries)
    for ds, cnt in deep_by_dataset.most_common():
        print(f"    {ds}: {cnt:,}")

    # 5. Identify core (depth-0) OEIS sequences for reference checks
    oeis_depths = all_depths.get("oeis", {})
    core_ids = {sid for sid, d in oeis_depths.items() if d == 0}
    print(f"\n[5] Core (depth-0) OEIS sequences: {len(core_ids):,}")

    # 6. Enrich deep objects
    print(f"\n[6] Enriching deep objects with names, terms, entropy, cross-refs...")
    deep_records = []

    for dataset, obj_id, depth in deep_entries:
        record = {
            "dataset": dataset,
            "id": obj_id,
            "depth": depth,
            "name": "",
            "first_10_terms": [],
            "entropy": None,
            "out_degree": 0,
            "in_degree": 0,
            "total_degree": 0,
            "references_core": False,
            "classification": "unknown",
        }

        if dataset == "oeis":
            record["name"] = _oeis_names_cache.get(obj_id, "")
            terms = _oeis_cache.get(obj_id, [])
            record["first_10_terms"] = terms[:10]
            if terms:
                record["entropy"] = round(sequence_entropy(terms), 4)
            out_d, in_d = xref_degree(obj_id)
            record["out_degree"] = out_d
            record["in_degree"] = in_d
            record["total_degree"] = out_d + in_d
            record["references_core"] = references_core(obj_id, core_ids)
            record["classification"] = classify(obj_id, depth, core_ids)

        elif dataset == "mathlib":
            # Mathlib modules: use the module name as label
            record["name"] = obj_id  # e.g. Mathlib.CategoryTheory.Monad.EquivMon
            record["classification"] = "mathlib_deep"

        elif dataset == "mmlkg":
            record["name"] = obj_id
            record["classification"] = "mmlkg_deep"

        deep_records.append(record)

    # Sort by depth descending, then by total_degree ascending (most isolated first)
    deep_records.sort(key=lambda r: (-r["depth"], r["total_degree"]))

    # 7. Classification counts (OEIS only, since we have xref data)
    oeis_deep = [r for r in deep_records if r["dataset"] == "oeis"]
    class_counts = Counter(r["classification"] for r in oeis_deep)
    print(f"\n[7] Classification of deep OEIS sequences:")
    for cls, cnt in class_counts.most_common():
        print(f"    {cls:20s}: {cnt:,}")

    # 8. Report top N deepest
    print(f"\n[8] Top {TOP_N_REPORT} deepest objects (all datasets):")
    for i, r in enumerate(deep_records[:TOP_N_REPORT]):
        name_short = r["name"][:60] if r["name"] else "(no name)"
        print(f"  [{i+1:2d}] depth={r['depth']:2d} | {r['dataset']:8s} | "
              f"{r['id']:15s} | deg={r['total_degree']:3d} | "
              f"class={r['classification']:16s} | {name_short}")
        if r["first_10_terms"]:
            print(f"       terms: {r['first_10_terms']}")

    # 9. Answer the question
    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print("VERDICT: Is the bottom of the abstraction axis EMPTY or POPULATED?")
    print(f"{'=' * 70}")
    if len(deep_entries) == 0:
        verdict = "EMPTY"
        explanation = (
            f"No objects found at depth >= {effective_threshold}. "
            f"The abstraction axis thins out rapidly. Max depth = {max_depth}."
        )
    elif len(deep_entries) < 50:
        verdict = "SPARSELY POPULATED"
        explanation = (
            f"Only {len(deep_entries)} objects at depth >= {effective_threshold}. "
            f"The bottom is a sparse frontier, not a void."
        )
    else:
        verdict = "POPULATED"
        explanation = (
            f"{len(deep_entries):,} objects at depth >= {effective_threshold}. "
            f"The bottom is occupied — mathematical knowledge extends deep."
        )

    # Enrich with isolation analysis
    if oeis_deep:
        n_dead = class_counts.get("dead_end", 0)
        n_isolated = class_counts.get("isolated_deep", 0)
        n_connected = class_counts.get("connected_deep", 0)
        explanation += (
            f"\n  OEIS deep objects: {len(oeis_deep)} total — "
            f"{n_connected} connected, {n_isolated} isolated, {n_dead} dead ends."
        )

    print(f"  Verdict: {verdict}")
    print(f"  {explanation}")
    print(f"  Elapsed: {elapsed:.1f}s")

    # 10. Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "parameters": {
            "deep_threshold_requested": DEEP_THRESHOLD,
            "deep_threshold_effective": effective_threshold,
            "low_degree_for_isolated": LOW_DEGREE,
            "max_depth_in_data": max_depth,
        },
        "depth_distribution": {str(k): v for k, v in sorted(depth_dist.items())},
        "total_objects": len(all_entries),
        "deep_objects_count": len(deep_entries),
        "deep_by_dataset": dict(deep_by_dataset.most_common()),
        "classification_counts_oeis": dict(class_counts.most_common()),
        "core_oeis_count": len(core_ids),
        "verdict": verdict,
        "explanation": explanation,
        "elapsed_seconds": round(elapsed, 1),
        "top_deep_records": deep_records[:100],
        "all_deep_records": deep_records,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
