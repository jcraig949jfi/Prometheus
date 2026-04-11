"""
OEIS Near-Duplicate Detection
==============================
Detects sequences that share identical initial terms.
Measures redundancy in the OEIS database via hashing.
"""

import json
import os
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "oeis" / "data"
STRIPPED_FILE = DATA_DIR / "stripped_new.txt"
NAMES_FILE = DATA_DIR / "names.txt"
OUT_FILE = Path(__file__).parent / "oeis_duplicates_results.json"

MAX_SEQS = 10000  # cap for analysis


def load_sequences(path, max_seqs=None):
    """Load sequences from OEIS stripped format."""
    seqs = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: A000001 ,0,1,1,1,2,...,
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            seq_id = parts[0]
            terms_str = parts[1].strip().strip(",")
            if not terms_str:
                continue
            try:
                terms = [int(x) for x in terms_str.split(",") if x.strip()]
            except ValueError:
                continue
            seqs[seq_id] = terms
            if max_seqs and len(seqs) >= max_seqs:
                break
    return seqs


def load_names(path):
    """Load sequence names from OEIS names file."""
    names = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) == 2:
                names[parts[0]] = parts[1]
    return names


def find_collisions(seqs, n_terms):
    """Find sequences with identical first n_terms terms.
    Returns dict: hash -> list of seq_ids."""
    buckets = defaultdict(list)
    for seq_id, terms in seqs.items():
        if len(terms) >= n_terms:
            key = tuple(terms[:n_terms])
            buckets[key].append(seq_id)
    # Keep only collisions (2+ sequences)
    return {k: v for k, v in buckets.items() if len(v) >= 2}


def analyze_pair(terms_a, terms_b):
    """Classify the relationship between two sequences."""
    # Check if one is a shifted version of the other
    min_len = min(len(terms_a), len(terms_b))

    # Check constant offset
    if min_len >= 2:
        diffs = [terms_a[i] - terms_b[i] for i in range(min_len)]
        if len(set(diffs)) == 1 and diffs[0] != 0:
            return f"constant_offset_{diffs[0]}"

    # Check if identical for full overlap
    if terms_a[:min_len] == terms_b[:min_len]:
        return "identical_full_overlap"

    # Find divergence point
    for i in range(min_len):
        if terms_a[i] != terms_b[i]:
            return f"diverge_at_term_{i}"

    return "identical_full_overlap"


def main():
    print("Loading sequences...")
    seqs = load_sequences(STRIPPED_FILE, max_seqs=MAX_SEQS)
    print(f"  Loaded {len(seqs)} sequences")

    print("Loading names...")
    names = load_names(NAMES_FILE)
    print(f"  Loaded {len(names)} names")

    # Length statistics
    lengths = [len(t) for t in seqs.values()]
    have_15 = sum(1 for l in lengths if l >= 15)
    have_20 = sum(1 for l in lengths if l >= 20)
    have_5 = sum(1 for l in lengths if l >= 5)
    print(f"  Sequences with >=5 terms: {have_5}")
    print(f"  Sequences with >=15 terms: {have_15}")
    print(f"  Sequences with >=20 terms: {have_20}")

    results = {
        "n_sequences_loaded": len(seqs),
        "n_with_5_plus_terms": have_5,
        "n_with_15_plus_terms": have_15,
        "n_with_20_plus_terms": have_20,
    }

    # === Analysis at multiple prefix lengths ===
    for n_terms in [5, 10, 15, 20, 25]:
        print(f"\n--- Collisions at {n_terms} terms ---")
        collisions = find_collisions(seqs, n_terms)
        n_collision_groups = len(collisions)
        n_seqs_in_collisions = sum(len(v) for v in collisions.values())
        largest_group = max((len(v) for v in collisions.values()), default=0)

        print(f"  Collision groups: {n_collision_groups}")
        print(f"  Sequences involved: {n_seqs_in_collisions}")
        print(f"  Largest group size: {largest_group}")

        # Collect detailed info for interesting cases
        detailed_groups = []
        for key, group_ids in sorted(collisions.items(), key=lambda x: -len(x[1])):
            if len(detailed_groups) >= 20:
                break
            group_info = {
                "prefix": list(key[:8]),  # first 8 terms for display
                "n_matching": len(group_ids),
                "sequences": [],
            }
            for sid in group_ids[:10]:  # cap at 10 per group
                full_terms = seqs[sid]
                entry = {
                    "id": sid,
                    "name": names.get(sid, "?"),
                    "n_terms": len(full_terms),
                }
                group_info["sequences"].append(entry)

            # Classify relationships within group
            if len(group_ids) >= 2:
                rel = analyze_pair(seqs[group_ids[0]], seqs[group_ids[1]])
                group_info["relationship"] = rel
                # Find where they actually diverge (if they do within available terms)
                a, b = seqs[group_ids[0]], seqs[group_ids[1]]
                min_l = min(len(a), len(b))
                diverge = None
                for i in range(min_l):
                    if a[i] != b[i]:
                        diverge = i
                        break
                group_info["diverge_at"] = diverge if diverge is not None else f"identical_through_{min_l}"

            detailed_groups.append(group_info)

        key_name = f"collisions_{n_terms}_terms"
        results[key_name] = {
            "n_groups": n_collision_groups,
            "n_sequences_involved": n_seqs_in_collisions,
            "largest_group": largest_group,
            "top_groups": detailed_groups,
        }

    # === Keyword analysis of duplicated sequences ===
    print("\n--- Analyzing keywords of 15-term duplicates ---")
    collisions_15 = find_collisions(seqs, 15)
    dup_ids = set()
    for group in collisions_15.values():
        dup_ids.update(group)

    # Check if duplicates cluster by keyword
    keyword_counts = defaultdict(int)
    for sid in dup_ids:
        name = names.get(sid, "")
        # Extract rough category from name
        name_lower = name.lower()
        for kw in ["walk", "lattice", "path", "tree", "graph", "partition",
                    "prime", "fibonacci", "catalan", "triangle", "polygon",
                    "permutation", "binary", "decimal", "digit", "number of",
                    "a(n) =", "floor", "ceiling", "round", "sum", "product"]:
            if kw in name_lower:
                keyword_counts[kw] += 1

    results["keyword_analysis_15term_dups"] = {
        "n_unique_sequences_in_dup_groups": len(dup_ids),
        "keyword_frequencies": dict(sorted(keyword_counts.items(), key=lambda x: -x[1])[:20]),
    }

    # === Summary statistics ===
    print("\n=== SUMMARY ===")
    for n in [5, 10, 15, 20, 25]:
        key = f"collisions_{n}_terms"
        r = results[key]
        print(f"  {n}-term matches: {r['n_groups']} groups, {r['n_sequences_involved']} sequences")

    # Redundancy rate
    if have_15 > 0:
        dup_rate_15 = results["collisions_15_terms"]["n_sequences_involved"] / have_15
        results["redundancy_rate_15_terms"] = round(dup_rate_15, 6)
        print(f"\n  15-term redundancy rate: {dup_rate_15:.4%} of eligible sequences")

    if have_20 > 0:
        dup_rate_20 = results["collisions_20_terms"]["n_sequences_involved"] / have_20
        results["redundancy_rate_20_terms"] = round(dup_rate_20, 6)
        print(f"  20-term redundancy rate: {dup_rate_20:.4%} of eligible sequences")

    # Save
    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
