"""
Explorer: Phase Scout — Which transition-zone sequence is closest to waking up?
================================================================================
Deep dive on the ~472 sequences at the phase transition threshold (5-10 verb
concepts, depth >= 2.0) to predict which one is closest to becoming a hub.

Computes a "wakeup score" based on hub references, verb count, depth, and
cross-dataset presence.  For the top 20, identifies what single new
cross-reference would collapse their depth the most.

Usage:
    python explorer_phase_scout.py
"""

import json
import math
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths & imports
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from search_engine import (
    _load_oeis, _oeis_cache,
    _load_oeis_crossrefs, _oeis_xref_cache, _oeis_xref_reverse,
    _load_oeis_names, _oeis_names_cache,
)

REPO = Path(__file__).resolve().parents[3]
DATA_DIR = REPO / "cartography" / "convergence" / "data"
DEPTHS_FILE = DATA_DIR / "abstraction_depths.json"
LINKS_FILE = DATA_DIR / "concept_links.jsonl"
OUTPUT_FILE = DATA_DIR / "phase_scout_report.json"

# Import the keyword list and extractor from phase_transition.py
from phase_transition import (
    MATH_KEYWORDS,
    extract_verb_concepts_from_name,
)

# Hub threshold: sequences with total xref degree above this are hubs
HUB_DEGREE_THRESHOLD = 50

# Transition zone parameters
MIN_VERB_CONCEPTS = 5
MAX_VERB_CONCEPTS = 10
MIN_DEPTH = 2.0


# ---------------------------------------------------------------------------
# Load concept links: dataset membership per concept, per object
# ---------------------------------------------------------------------------

def load_concept_links():
    """
    Load concept_links.jsonl and return:
      - ds_concepts: {dataset: set of concept names}
      - concept_objects: {concept: set of (dataset, object_id)}
      - object_concepts: {(dataset, object_id): set of concept names}
    """
    ds_concepts = defaultdict(set)
    concept_objects = defaultdict(set)
    object_concepts = defaultdict(set)

    if not LINKS_FILE.exists():
        print(f"  WARNING: {LINKS_FILE} not found")
        return ds_concepts, concept_objects, object_concepts

    print("[Scout] Loading concept_links.jsonl...")
    count = 0
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                ds = rec["dataset"]
                obj = rec["object_id"]
                con = rec["concept"]
                ds_concepts[ds].add(con)
                concept_objects[con].add((ds, obj))
                object_concepts[(ds, obj)].add(con)
                count += 1
            except (json.JSONDecodeError, KeyError):
                pass
    print(f"  Loaded {count:,} links across {len(ds_concepts)} datasets")
    return ds_concepts, concept_objects, object_concepts


# ---------------------------------------------------------------------------
# Build set of hub sequences
# ---------------------------------------------------------------------------

def find_hub_sequences():
    """Return set of OEIS sequence IDs with total xref degree > HUB_DEGREE_THRESHOLD."""
    hubs = set()
    all_ids = set(_oeis_xref_cache.keys()) | set(_oeis_xref_reverse.keys())
    for seq_id in all_ids:
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        if out_deg + in_deg > HUB_DEGREE_THRESHOLD:
            hubs.add(seq_id)
    return hubs


# ---------------------------------------------------------------------------
# Check cross-dataset presence of a keyword
# ---------------------------------------------------------------------------

def keyword_to_dataset_presence(keyword, ds_concepts):
    """
    Check which datasets contain verb concepts matching a keyword.
    Returns list of dataset names.
    """
    verb_name = f"verb_involves_{keyword}"
    present_in = []
    for ds, concepts in ds_concepts.items():
        if verb_name in concepts:
            present_in.append(ds)
    return present_in


# ---------------------------------------------------------------------------
# Compute entropy of verb concept distribution
# ---------------------------------------------------------------------------

def verb_entropy(verbs):
    """Shannon entropy of verb concept set (uniform = max entropy)."""
    n = len(verbs)
    if n <= 1:
        return 0.0
    # Uniform distribution over n items
    return math.log2(n)


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def run_phase_scout():
    t0 = time.time()

    # 1. Load abstraction depths
    print("[Scout] Loading abstraction depths...")
    with open(DEPTHS_FILE, "r", encoding="utf-8") as f:
        depths_data = json.load(f)
    oeis_depths = depths_data.get("oeis", {})
    print(f"  Loaded {len(oeis_depths):,} OEIS depth entries")

    # 2. Load OEIS cross-references and names
    print("[Scout] Loading OEIS cross-references...")
    _load_oeis_crossrefs()
    _load_oeis_names()

    # 3. Load concept links
    ds_concepts, concept_objects, object_concepts = load_concept_links()

    # 4. Build hub set
    print("[Scout] Identifying hub sequences...")
    hubs = find_hub_sequences()
    print(f"  Found {len(hubs):,} hub sequences (degree > {HUB_DEGREE_THRESHOLD})")

    # 5. Build a set of "interesting" concept keywords for cross-dataset checking
    # These keywords map to concepts in concept_links that also appear as OEIS verbs
    interesting_keywords = set()
    for kw in MATH_KEYWORDS:
        verb = f"verb_involves_{kw}"
        for ds in ds_concepts:
            if verb in ds_concepts[ds]:
                interesting_keywords.add(kw)
                break
    print(f"  {len(interesting_keywords)} keywords appear in both OEIS names and concept links")

    # 6. Scan all OEIS sequences for transition zone members
    print("[Scout] Scanning for transition-zone sequences...")
    all_seq_ids = set(oeis_depths.keys()) | set(_oeis_xref_cache.keys()) | set(_oeis_xref_reverse.keys())

    transition_seqs = []
    for seq_id in sorted(all_seq_ids):
        name = _oeis_names_cache.get(seq_id, "")
        depth = oeis_depths.get(seq_id, None)
        if depth is None:
            continue

        # Extract verb concepts from name
        verbs = extract_verb_concepts_from_name(name)
        n_verb = len(verbs)

        # Filter: transition zone
        if not (MIN_VERB_CONCEPTS <= n_verb <= MAX_VERB_CONCEPTS and depth >= MIN_DEPTH):
            continue

        # Compute degree
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        total_degree = out_deg + in_deg

        # Count hub references: how many of this sequence's xrefs are hubs?
        all_refs = _oeis_xref_cache.get(seq_id, set()) | _oeis_xref_reverse.get(seq_id, set())
        hub_refs = len(all_refs & hubs)

        # Extract raw keywords (strip verb_involves_ prefix)
        raw_keywords = set()
        for v in verbs:
            kw = v.replace("verb_involves_", "")
            raw_keywords.add(kw)

        # Check cross-dataset presence
        datasets_present = set()
        for kw in raw_keywords:
            for ds in keyword_to_dataset_presence(kw, ds_concepts):
                datasets_present.add(ds)

        # Compute entropy
        ent = verb_entropy(verbs)

        # Compute wakeup score: hub_refs * verb_count / (depth + 1)
        wakeup_score = hub_refs * n_verb / (depth + 1.0)

        transition_seqs.append({
            "seq_id": seq_id,
            "name": name,
            "depth": depth,
            "degree": total_degree,
            "n_verb_concepts": n_verb,
            "hub_refs": hub_refs,
            "entropy": round(ent, 4),
            "datasets_present": sorted(datasets_present),
            "n_datasets": len(datasets_present),
            "verbs": sorted(verbs),
            "raw_keywords": sorted(raw_keywords),
            "wakeup_score": round(wakeup_score, 6),
        })

    print(f"  Found {len(transition_seqs)} sequences in transition zone "
          f"({MIN_VERB_CONCEPTS}-{MAX_VERB_CONCEPTS} verbs, depth >= {MIN_DEPTH})")

    # 7. Rank by wakeup score
    transition_seqs.sort(key=lambda x: -x["wakeup_score"])

    # Print top 20
    print(f"\n[Scout] Top 20 by wakeup score:")
    print(f"  {'Rank':<5} {'SeqID':<10} {'Wake':>8} {'Hubs':>5} {'Verbs':>6} "
          f"{'Depth':>6} {'Deg':>5} {'DS':>3}  Name")
    print("  " + "-" * 90)
    for i, s in enumerate(transition_seqs[:20], 1):
        safe_name = s["name"][:50].encode("ascii", "replace").decode("ascii")
        print(f"  {i:<5} {s['seq_id']:<10} {s['wakeup_score']:>8.3f} "
              f"{s['hub_refs']:>5} {s['n_verb_concepts']:>6} "
              f"{s['depth']:>6.2f} {s['degree']:>5} {s['n_datasets']:>3}  {safe_name}")

    # 8. For top 20: identify the single best new cross-reference
    print(f"\n[Scout] Analyzing optimal new connections for top 20...")
    top_20_analysis = []

    for s in transition_seqs[:20]:
        seq_id = s["seq_id"]
        current_refs = _oeis_xref_cache.get(seq_id, set()) | _oeis_xref_reverse.get(seq_id, set())

        # Strategy: the best new xref is a hub that this sequence does NOT
        # already reference, whose keywords overlap most with this sequence.
        # A connection to a high-degree hub with shared verbs would collapse depth.

        best_candidate = None
        best_overlap = 0
        best_candidate_degree = 0
        seq_keywords = set(s["raw_keywords"])

        for hub_id in hubs:
            if hub_id in current_refs or hub_id == seq_id:
                continue  # already connected

            hub_name = _oeis_names_cache.get(hub_id, "")
            hub_verbs = extract_verb_concepts_from_name(hub_name)
            hub_keywords = {v.replace("verb_involves_", "") for v in hub_verbs}

            overlap = seq_keywords & hub_keywords
            hub_deg = len(_oeis_xref_cache.get(hub_id, set())) + len(_oeis_xref_reverse.get(hub_id, set()))

            # Score: overlap size * hub degree (connecting to higher-degree
            # hub with more keyword overlap = bigger depth collapse)
            score = len(overlap) * hub_deg
            if score > best_overlap or (score == best_overlap and hub_deg > best_candidate_degree):
                best_overlap = score
                best_candidate = hub_id
                best_candidate_degree = hub_deg

        suggested_connection = None
        if best_candidate:
            hub_name = _oeis_names_cache.get(best_candidate, "")
            hub_verbs = extract_verb_concepts_from_name(hub_name)
            hub_keywords = {v.replace("verb_involves_", "") for v in hub_verbs}
            shared = sorted(seq_keywords & hub_keywords)
            suggested_connection = {
                "target_seq_id": best_candidate,
                "target_name": hub_name,
                "target_degree": best_candidate_degree,
                "shared_keywords": shared,
                "n_shared_keywords": len(shared),
                "expected_depth_reduction": round(
                    s["depth"] * len(shared) / (s["depth"] + best_candidate_degree), 4
                ),
            }

        entry = dict(s)
        entry["suggested_connection"] = suggested_connection
        top_20_analysis.append(entry)

    # 9. Summary stats
    wakeup_scores = [s["wakeup_score"] for s in transition_seqs]
    hub_ref_counts = [s["hub_refs"] for s in transition_seqs]
    ds_counts = [s["n_datasets"] for s in transition_seqs]

    summary = {
        "total_transition_zone": len(transition_seqs),
        "zone_criteria": {
            "min_verb_concepts": MIN_VERB_CONCEPTS,
            "max_verb_concepts": MAX_VERB_CONCEPTS,
            "min_depth": MIN_DEPTH,
        },
        "hub_threshold_degree": HUB_DEGREE_THRESHOLD,
        "total_hubs": len(hubs),
        "wakeup_score_stats": {
            "max": round(max(wakeup_scores), 4) if wakeup_scores else 0,
            "min": round(min(wakeup_scores), 4) if wakeup_scores else 0,
            "mean": round(sum(wakeup_scores) / len(wakeup_scores), 4) if wakeup_scores else 0,
            "median": round(sorted(wakeup_scores)[len(wakeup_scores) // 2], 4) if wakeup_scores else 0,
        },
        "hub_ref_stats": {
            "max": max(hub_ref_counts) if hub_ref_counts else 0,
            "mean": round(sum(hub_ref_counts) / len(hub_ref_counts), 2) if hub_ref_counts else 0,
            "zero_hub_refs": sum(1 for h in hub_ref_counts if h == 0),
        },
        "cross_dataset_stats": {
            "max_datasets": max(ds_counts) if ds_counts else 0,
            "mean_datasets": round(sum(ds_counts) / len(ds_counts), 2) if ds_counts else 0,
            "in_zero_datasets": sum(1 for d in ds_counts if d == 0),
        },
    }

    elapsed = time.time() - t0

    # 10. Build and save output
    output = {
        "meta": {
            "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "description": "Phase scout: predict which transition-zone sequence wakes up next",
            "elapsed_seconds": round(elapsed, 2),
        },
        "summary": summary,
        "top_20_wakeup_candidates": top_20_analysis,
        "all_transition_zone": transition_seqs,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[Scout] Saved {OUTPUT_FILE}")
    print(f"[Scout] Done in {elapsed:.1f}s")
    print(f"\n[Scout] VERDICT: Top candidate = {top_20_analysis[0]['seq_id']} "
          f"({top_20_analysis[0]['name'][:60]})")
    if top_20_analysis[0].get("suggested_connection"):
        sc = top_20_analysis[0]["suggested_connection"]
        print(f"  Best new connection: -> {sc['target_seq_id']} "
              f"(degree {sc['target_degree']}, "
              f"{sc['n_shared_keywords']} shared keywords)")

    return output


if __name__ == "__main__":
    run_phase_scout()
