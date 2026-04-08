"""
Ghost Node Detector — Predict missing mathematical theorems from structural convergence.
=========================================================================================
A "ghost node" is a concept-pair that multiple datasets agree on, but at least
one dataset is *missing* — despite having both concepts individually.  That gap
is a predicted theorem: a mathematical relationship the geometry says must exist.

Ghost types
-----------
STRUCTURAL_GHOST  verb concept pair, 3+ datasets agree  -> high-confidence prediction
ARITHMETIC_GHOST  integer concept pair                   -> likely coincidence
BRIDGE_GHOST      connects two currently-disconnected dataset clusters -> highest priority

Usage:
    python ghost_node_detector.py
"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

CONVERGENCE = SCRIPT_DIR.parents[1] / "convergence"
LINKS_FILE = CONVERGENCE / "data" / "concept_links.jsonl"
OUTPUT_FILE = CONVERGENCE / "data" / "ghost_nodes.json"

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------
MIN_CONCEPT_FREQ = 5       # ignore concepts appearing fewer times (noise)
MAX_CONCEPT_FREQ = 10000   # ignore concepts appearing more times (trivial)
MIN_DATASETS_WITH_PAIR = 2 # concept pair must appear in 2+ datasets
TOP_N = 50                 # report top N ghosts

PRIORITY = {
    "BRIDGE_GHOST":     3.0,
    "STRUCTURAL_GHOST": 2.0,
    "ARITHMETIC_GHOST": 0.5,
}


def _concept_type(concept: str) -> str:
    """Classify a concept by its prefix."""
    if concept.startswith("verb_"):
        return "verb"
    if concept.startswith("integer_"):
        return "integer"
    return "other"


def _pair_kind(c1: str, c2: str) -> str:
    """Determine the structural kind of a concept pair."""
    t1, t2 = _concept_type(c1), _concept_type(c2)
    if t1 == "integer" and t2 == "integer":
        return "integer"
    if t1 == "verb" or t2 == "verb":
        return "verb"
    return "other"


# ---------------------------------------------------------------------------
# Step 1 — Load concept links and build indices
# ---------------------------------------------------------------------------
def load_links():
    """
    Returns
    -------
    concept_freq : dict[str, int]
        Number of (dataset, object) pairs per concept.
    concept_datasets : dict[str, set[str]]
        Which datasets each concept appears in.
    obj_concepts : dict[(dataset, object_id), set[str]]
        Concepts for each object.
    dataset_concepts : dict[dataset, dict[concept, set[object_id]]]
        Per-dataset: which objects carry each concept.
    """
    print("[1/7] Loading concept links …")
    t0 = time.time()

    concept_freq: dict[str, int] = defaultdict(int)
    concept_datasets: dict[str, set] = defaultdict(set)
    obj_concepts: dict[tuple, set] = defaultdict(set)
    dataset_concepts: dict[str, dict] = defaultdict(lambda: defaultdict(set))

    with open(LINKS_FILE) as f:
        for line in f:
            r = json.loads(line)
            c, ds, oid = r["concept"], r["dataset"], r["object_id"]
            concept_freq[c] += 1
            concept_datasets[c].add(ds)
            obj_concepts[(ds, oid)].add(c)
            dataset_concepts[ds][c].add(oid)

    elapsed = time.time() - t0
    print(f"       {len(concept_freq):,} concepts, "
          f"{sum(len(v) for v in dataset_concepts.values()):,} dataset-concept entries, "
          f"{elapsed:.1f}s")
    return concept_freq, concept_datasets, obj_concepts, dataset_concepts


# ---------------------------------------------------------------------------
# Step 2 — Filter concepts and build eligible set
# ---------------------------------------------------------------------------
def filter_concepts(concept_freq, concept_datasets):
    """Keep concepts that are in the useful frequency band AND span 3+ datasets."""
    print("[2/7] Filtering concepts …")
    eligible = {
        c for c, freq in concept_freq.items()
        if MIN_CONCEPT_FREQ <= freq <= MAX_CONCEPT_FREQ
           and len(concept_datasets[c]) >= 3
    }
    print(f"       {len(eligible):,} concepts pass frequency + dataset filter "
          f"(from {len(concept_freq):,})")
    return eligible


# ---------------------------------------------------------------------------
# Step 3 — Build concept co-occurrence per dataset (sparse)
# ---------------------------------------------------------------------------
def build_cooccurrence(obj_concepts, eligible, dataset_concepts):
    """
    For each dataset, find concept pairs that co-occur on the same object.

    Returns
    -------
    pair_datasets : dict[(c1,c2), set[str]]
        Which datasets have at least one object carrying both c1 AND c2.
    pair_counts : dict[(c1,c2), int]
        Total number of objects (across all datasets) carrying both.
    """
    print("[3/7] Building concept co-occurrence (per dataset) …")
    t0 = time.time()

    pair_datasets: dict[tuple, set] = defaultdict(set)
    pair_counts: dict[tuple, int] = defaultdict(int)

    all_datasets = sorted(dataset_concepts.keys())

    for ds in all_datasets:
        ds_data = dataset_concepts[ds]
        # For this dataset, find which eligible concepts appear
        ds_eligible = sorted(c for c in ds_data if c in eligible)
        if len(ds_eligible) < 2:
            continue

        # Build inverted index: object -> eligible concepts
        obj_to_concepts: dict[str, list] = defaultdict(list)
        for c in ds_eligible:
            for oid in ds_data[c]:
                obj_to_concepts[oid].append(c)

        # Enumerate pairs per object (only objects with 2+ eligible concepts)
        ds_pair_set: set = set()
        for oid, concepts in obj_to_concepts.items():
            if len(concepts) < 2:
                continue
            concepts.sort()
            # Cap per-object pair enumeration to avoid combinatorial blow-up
            if len(concepts) > 100:
                concepts = concepts[:100]
            for i in range(len(concepts)):
                for j in range(i + 1, len(concepts)):
                    pair = (concepts[i], concepts[j])
                    pair_counts[pair] += 1
                    ds_pair_set.add(pair)

        for pair in ds_pair_set:
            pair_datasets[pair].add(ds)

        print(f"       {ds:20s}: {len(ds_eligible):5d} concepts, "
              f"{len(obj_to_concepts):6d} objects, "
              f"{len(ds_pair_set):8d} pairs")

    elapsed = time.time() - t0
    print(f"       Total pairs with 1+ dataset: {len(pair_counts):,}  ({elapsed:.1f}s)")
    return pair_datasets, pair_counts


# ---------------------------------------------------------------------------
# Step 4 — Detect ghost nodes
# ---------------------------------------------------------------------------
def detect_ghosts(pair_datasets, pair_counts, concept_datasets, dataset_concepts, eligible):
    """
    For each qualifying pair (c1, c2) present in 3+ datasets:
      - datasets_have: datasets that have an object with BOTH c1 and c2
      - datasets_should: datasets that have objects with c1 AND objects with c2
        (individually), so they *could* have a combined object
      - datasets_missing: datasets_should - datasets_have

    A ghost exists wherever datasets_missing is non-empty.

    Two detection modes:
      Mode A — Co-occurrence gap: pair exists in 2+ datasets, but a dataset
               that has both concepts individually lacks a combined object.
      Mode B — Expectation ghost: concepts c1 and c2 each appear in 3+
               datasets; some dataset has both individually (10+ objects each)
               but the pair was never observed there, even though other
               datasets DO have the pair.  The "pair" may not yet be in
               pair_datasets at all for that dataset.
    """
    print("[4/7] Detecting ghost nodes …")
    t0 = time.time()

    ghosts = []
    qualifying_pairs = 0

    # --- Mode A: co-occurrence gaps ---
    for pair, ds_have in pair_datasets.items():
        if len(ds_have) < MIN_DATASETS_WITH_PAIR:
            continue
        qualifying_pairs += 1

        c1, c2 = pair
        ds_c1 = concept_datasets[c1]
        ds_c2 = concept_datasets[c2]
        ds_should = ds_c1 & ds_c2          # datasets that have BOTH concepts individually
        ds_missing = ds_should - ds_have   # have both individually, but no combined object

        if not ds_missing:
            continue

        # Gravitational pull
        n_have = len(ds_have)
        n_should = len(ds_should)
        total_objects = pair_counts[pair]
        pull = (n_have * total_objects) / max(n_should, 1)

        ghosts.append({
            "c1": c1,
            "c2": c2,
            "datasets_have": sorted(ds_have),
            "datasets_missing": sorted(ds_missing),
            "datasets_should": sorted(ds_should),
            "n_have": n_have,
            "n_should": n_should,
            "n_missing": len(ds_missing),
            "total_objects": total_objects,
            "pull": pull,
            "mode": "co-occurrence_gap",
        })

    # --- Mode B: expectation ghosts ---
    # For concept pairs in eligible set, find datasets where both concepts
    # have substantial presence but no co-occurring object.
    MIN_INDIVIDUAL_OBJECTS = 5  # each concept must have 5+ objects in the dataset

    seen_pairs = set(pair_datasets.keys())
    eligible_list = sorted(eligible)

    # Group eligible concepts by dataset presence
    # For each dataset, find pairs of eligible concepts that both appear with
    # decent frequency but have NO co-occurring object
    all_ds = sorted(dataset_concepts.keys())
    for ds in all_ds:
        ds_data = dataset_concepts[ds]
        # Eligible concepts with sufficient presence in this dataset
        ds_concepts = [c for c in eligible_list
                       if c in ds_data and len(ds_data[c]) >= MIN_INDIVIDUAL_OBJECTS]
        if len(ds_concepts) < 2:
            continue

        # Which pairs already exist in this dataset?
        ds_existing_pairs = {p for p, dsh in pair_datasets.items() if ds in dsh}

        for i in range(len(ds_concepts)):
            for j in range(i + 1, len(ds_concepts)):
                pair = (ds_concepts[i], ds_concepts[j])
                if pair in ds_existing_pairs:
                    continue  # already co-occurs here
                # Check if this pair exists in OTHER datasets
                other_ds = pair_datasets.get(pair, set())
                if not other_ds:
                    continue  # nobody has this pair -> no evidence
                # Ghost: other datasets have it, this one doesn't
                c1, c2 = pair
                n_have = len(other_ds)
                total_objects = pair_counts.get(pair, 0)
                ds_should_set = concept_datasets[c1] & concept_datasets[c2]
                n_should = len(ds_should_set)
                pull = (n_have * total_objects) / max(n_should, 1)

                ghosts.append({
                    "c1": c1,
                    "c2": c2,
                    "datasets_have": sorted(other_ds),
                    "datasets_missing": [ds],
                    "datasets_should": sorted(ds_should_set),
                    "n_have": n_have,
                    "n_should": n_should,
                    "n_missing": 1,
                    "total_objects": total_objects,
                    "pull": pull,
                    "mode": "expectation_ghost",
                })

    # Deduplicate: same (c1, c2, missing_ds) may appear from both modes
    seen = set()
    deduped = []
    for g in ghosts:
        key = (g["c1"], g["c2"], tuple(g["datasets_missing"]))
        if key not in seen:
            seen.add(key)
            deduped.append(g)
    ghosts = deduped

    elapsed = time.time() - t0
    print(f"       {qualifying_pairs:,} qualifying pairs (mode A), "
          f"{len(ghosts):,} ghost nodes total  ({elapsed:.1f}s)")
    return ghosts


# ---------------------------------------------------------------------------
# Step 5 — Classify ghosts and compute bridge-ness
# ---------------------------------------------------------------------------
def classify_ghosts(ghosts, pair_datasets):
    """
    Assign a type to each ghost:
      STRUCTURAL_GHOST — verb pair, 3+ datasets agree
      ARITHMETIC_GHOST — integer pair -> likely coincidence
      BRIDGE_GHOST     — connects two currently-disconnected dataset clusters

    Bridge detection: build a graph of which dataset pairs are ALREADY
    connected by at least one shared concept pair.  A ghost is a bridge
    only if its missing dataset has NO existing concept-pair connection
    to the datasets that have the pair.
    """
    print("[5/7] Classifying ghosts …")

    # Build dataset connectivity from ALL known co-occurring pairs
    dataset_pair_connected: set = set()
    for pair, ds_set in pair_datasets.items():
        ds_list = sorted(ds_set)
        for i in range(len(ds_list)):
            for j in range(i + 1, len(ds_list)):
                dataset_pair_connected.add((ds_list[i], ds_list[j]))

    print(f"       Dataset connectivity: {len(dataset_pair_connected)} connected pairs")

    for g in ghosts:
        kind = _pair_kind(g["c1"], g["c2"])

        # Check if filling this ghost would bridge a genuinely disconnected
        # dataset pair (one that shares NO concept-pair currently)
        is_bridge = False
        for ds_missing in g["datasets_missing"]:
            for ds_have in g["datasets_have"]:
                pair_key = (min(ds_missing, ds_have), max(ds_missing, ds_have))
                if pair_key not in dataset_pair_connected:
                    is_bridge = True
                    break
            if is_bridge:
                break

        # Classify: verb/integer first, bridge upgrades priority
        if kind == "verb":
            base_type = "STRUCTURAL_GHOST"
        elif kind == "integer":
            base_type = "ARITHMETIC_GHOST"
        else:
            base_type = "STRUCTURAL_GHOST" if g["n_have"] >= 3 else "ARITHMETIC_GHOST"

        # Bridge overrides only for non-integer pairs (integer bridges are noise)
        if is_bridge and kind != "integer":
            g["ghost_type"] = "BRIDGE_GHOST"
        else:
            g["ghost_type"] = base_type

        g["priority_multiplier"] = PRIORITY[g["ghost_type"]]
        g["score"] = g["pull"] * g["priority_multiplier"]

    # Sort descending by score
    ghosts.sort(key=lambda g: g["score"], reverse=True)
    type_counts = defaultdict(int)
    for g in ghosts:
        type_counts[g["ghost_type"]] += 1
    print(f"       Types: {dict(type_counts)}")
    return ghosts


# ---------------------------------------------------------------------------
# Step 6 — Generate predictions
# ---------------------------------------------------------------------------
def generate_predictions(ghosts):
    """Attach a human-readable prediction string to each ghost."""
    print("[6/7] Generating predictions …")

    for g in ghosts:
        have_str = ", ".join(g["datasets_have"][:5])
        missing_str = ", ".join(g["datasets_missing"][:3])
        g["prediction"] = (
            f"Dataset(s) [{missing_str}] should contain an object connecting "
            f"'{g['c1']}' to '{g['c2']}', because datasets [{have_str}] "
            f"all have such objects ({g['total_objects']} total). "
            f"Type: {g['ghost_type']}, pull={g['pull']:.1f}, score={g['score']:.1f}."
        )
    return ghosts


# ---------------------------------------------------------------------------
# Step 7 — Output
# ---------------------------------------------------------------------------
def save_results(ghosts):
    """Save top N ghosts to JSON."""
    print(f"[7/7] Saving top {TOP_N} ghosts to {OUTPUT_FILE} …")

    top = ghosts[:TOP_N]
    report = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_ghosts": len(ghosts),
        "top_n": TOP_N,
        "type_summary": {},
        "ghosts": top,
    }

    # Type summary across ALL ghosts
    from collections import Counter
    type_counts = Counter(g["ghost_type"] for g in ghosts)
    report["type_summary"] = dict(type_counts)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*72}")
    print(f"Ghost Node Report — {len(ghosts):,} total ghosts, top {min(TOP_N, len(top))} shown")
    print(f"{'='*72}")
    for i, g in enumerate(top[:20], 1):
        print(f"\n#{i:2d}  [{g['ghost_type']:17s}]  score={g['score']:.1f}  pull={g['pull']:.1f}")
        print(f"     Pair: {g['c1']}  x  {g['c2']}")
        print(f"     Have ({g['n_have']}): {', '.join(g['datasets_have'][:5])}")
        print(f"     Missing ({g['n_missing']}): {', '.join(g['datasets_missing'][:5])}")
        print(f"     -> {g['prediction'][:120]}…" if len(g['prediction']) > 120
              else f"     -> {g['prediction']}")

    print(f"\nFull results: {OUTPUT_FILE}")
    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()

    concept_freq, concept_datasets, obj_concepts, dataset_concepts = load_links()
    eligible = filter_concepts(concept_freq, concept_datasets)
    pair_datasets, pair_counts = build_cooccurrence(
        obj_concepts, eligible, dataset_concepts
    )
    ghosts = detect_ghosts(pair_datasets, pair_counts, concept_datasets, dataset_concepts, eligible)
    ghosts = classify_ghosts(ghosts, pair_datasets)
    ghosts = generate_predictions(ghosts)
    report = save_results(ghosts)

    print(f"\nDone in {time.time() - t_start:.1f}s total.")
    return report


if __name__ == "__main__":
    main()
