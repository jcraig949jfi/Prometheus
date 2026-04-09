"""
Open Problem Enrichment Pipeline — Build research dossiers for each problem.
==============================================================================
Takes the raw Erdos problems database and enriches each problem with:
  1. Classification (domain, type, difficulty, computational testability)
  2. Dataset relevance (which of our 21 datasets touch this problem?)
  3. OEIS cross-references (which sequences are related? can we extend them?)
  4. Related solved problems (what worked? strategy transfer)
  5. Why it's open (what approaches failed?)
  6. Candidate strategies (what could work with our tools?)
  7. Inter-problem relationships (which problems are related to each other?)

Usage:
    python enrich_problems.py                    # enrich all open problems
    python enrich_problems.py --max 50           # first 50 only
    python enrich_problems.py --tags "graph theory"  # filter by tag
"""

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared" / "scripts"))

ROOT = Path(__file__).resolve().parents[2]
PROBLEMS_FILE = ROOT / "cartography" / "open_problems" / "data" / "erdos_problems.jsonl"
ENRICHED_FILE = ROOT / "cartography" / "open_problems" / "data" / "erdos_enriched.jsonl"
RELATIONSHIPS_FILE = ROOT / "cartography" / "open_problems" / "data" / "problem_relationships.jsonl"
OEIS_NAMES = ROOT / "cartography" / "oeis" / "data" / "oeis_names.json"
NEW_TERMS_DIR = ROOT / "cartography" / "oeis" / "data" / "new_terms"

# Our dataset domains mapped to Erdos problem tags
TAG_TO_DATASETS = {
    "number theory": ["LMFDB", "NumberFields", "OEIS", "ANTEDB", "Fungrim"],
    "graph theory": ["Isogenies", "KnotInfo", "mathlib", "MMLKG"],
    "combinatorics": ["FindStat", "OEIS", "SmallGroups", "Polytopes"],
    "additive combinatorics": ["OEIS", "NumberFields", "SmallGroups"],
    "geometry": ["Lattices", "SpaceGroups", "Polytopes", "Materials"],
    "analysis": ["Fungrim", "Maass", "ANTEDB"],
    "primes": ["LMFDB", "Isogenies", "NumberFields", "OEIS", "ANTEDB"],
    "ramsey theory": ["OEIS", "SmallGroups"],
    "chromatic number": ["Isogenies", "KnotInfo"],
    "topology": ["KnotInfo", "piBase"],
    "algebra": ["SmallGroups", "NumberFields", "mathlib"],
    "probability": ["OEIS"],
    "unit fractions": ["OEIS"],
    "distances": ["Lattices", "Polytopes"],
}

# Difficulty estimation from problem structure
DIFFICULTY_SIGNALS = {
    "$500": "extreme",
    "$250": "very_hard",
    "$100": "hard",
    "$50": "moderate",
    "$25": "moderate",
    "$10": "accessible",
}


def load_problems(tag_filter=None, max_problems=0):
    problems = []
    with open(PROBLEMS_FILE) as f:
        for line in f:
            p = json.loads(line)
            if p.get("status", {}).get("state", "") not in ("open", "verifiable", "falsifiable"):
                continue
            if tag_filter:
                if tag_filter not in p.get("tags", []):
                    continue
            problems.append(p)
            if max_problems and len(problems) >= max_problems:
                break
    return problems


def load_oeis_names():
    """Load OEIS sequence names for cross-referencing."""
    if not OEIS_NAMES.exists():
        return {}
    try:
        return json.loads(OEIS_NAMES.read_text())
    except Exception:
        return {}


def load_extended_sequences():
    """Check which OEIS sequences we've extended."""
    extended = set()
    if NEW_TERMS_DIR.exists():
        for f in NEW_TERMS_DIR.glob("*.json"):
            extended.add(f.stem)
    return extended


def classify_problem(problem):
    """Classify a problem by type, testability, and relevance."""
    tags = problem.get("tags", [])
    prize = problem.get("prize", "")
    oeis_refs = problem.get("oeis", [])

    # Difficulty from prize
    difficulty = "unknown"
    for prize_str, diff in DIFFICULTY_SIGNALS.items():
        if prize_str in prize:
            difficulty = diff
            break

    # Relevant datasets
    relevant_datasets = set()
    for tag in tags:
        for ds in TAG_TO_DATASETS.get(tag, []):
            relevant_datasets.add(ds)

    # Testability assessment
    testability = "unknown"
    if oeis_refs:
        testability = "computational"  # Has OEIS refs → likely involves sequences we can compute
    if any(t in tags for t in ["graph theory", "chromatic number", "ramsey theory"]):
        testability = "constructive"  # Can search for counterexamples
    if any(t in tags for t in ["analysis", "topology"]):
        testability = "theoretical"  # Harder to test computationally

    # Problem type
    problem_type = "unknown"
    if problem.get("status", {}).get("state") == "falsifiable":
        problem_type = "conjecture"  # Could be disproved
    elif problem.get("status", {}).get("state") == "verifiable":
        problem_type = "verifiable"  # Could be verified computationally
    elif "prove" in str(problem.get("tags", [])).lower():
        problem_type = "existence"
    else:
        problem_type = "open"

    return {
        "difficulty": difficulty,
        "testability": testability,
        "problem_type": problem_type,
        "relevant_datasets": sorted(relevant_datasets),
        "n_datasets": len(relevant_datasets),
    }


def enrich_oeis_connections(problem, oeis_names, extended_seqs):
    """Enrich with OEIS cross-reference details."""
    oeis_refs = problem.get("oeis", [])
    connections = []

    for ref in oeis_refs:
        seq_id = ref if ref.startswith("A") else f"A{ref}"
        entry = {
            "sequence": seq_id,
            "name": oeis_names.get(seq_id, "unknown"),
            "we_extended": seq_id in extended_seqs,
        }
        connections.append(entry)

    return {
        "oeis_connections": connections,
        "n_oeis_refs": len(connections),
        "n_extended_by_us": sum(1 for c in connections if c["we_extended"]),
    }


def find_related_problems(problems):
    """Find relationships between problems based on shared tags and OEIS refs."""
    # Build indices
    tag_index = defaultdict(set)
    oeis_index = defaultdict(set)

    for p in problems:
        num = p["number"]
        for tag in p.get("tags", []):
            tag_index[tag].add(num)
        for ref in p.get("oeis", []):
            oeis_index[ref].add(num)

    # Find related pairs
    relationships = []
    seen = set()

    for p in problems:
        num = p["number"]
        related = Counter()

        for tag in p.get("tags", []):
            for other in tag_index[tag]:
                if other != num:
                    related[other] += 1  # shared tag

        for ref in p.get("oeis", []):
            for other in oeis_index[ref]:
                if other != num:
                    related[other] += 3  # shared OEIS ref is stronger signal

        top_related = related.most_common(5)
        for other_num, score in top_related:
            pair = tuple(sorted([num, other_num]))
            if pair not in seen:
                seen.add(pair)
                # Find shared elements
                other = next((q for q in problems if q["number"] == other_num), None)
                if other:
                    shared_tags = set(p.get("tags", [])) & set(other.get("tags", []))
                    shared_oeis = set(p.get("oeis", [])) & set(other.get("oeis", []))
                    relationships.append({
                        "problem_a": num,
                        "problem_b": other_num,
                        "score": score,
                        "shared_tags": sorted(shared_tags),
                        "shared_oeis": sorted(shared_oeis),
                    })

    relationships.sort(key=lambda x: x["score"], reverse=True)
    return relationships


def suggest_strategies(problem, classification):
    """Suggest candidate strategies based on problem characteristics."""
    strategies = []
    tags = problem.get("tags", [])
    testability = classification["testability"]

    if testability == "computational":
        strategies.append({
            "strategy": "sequence_extension",
            "description": "Extend related OEIS sequences to higher terms. Longer sequences may reveal patterns that resolve the conjecture.",
            "tool": "term_extender.py",
        })
        strategies.append({
            "strategy": "constant_telescope",
            "description": "Check if growth rates or limits of related sequences match known constants.",
            "tool": "constant_telescope.py",
        })

    if testability == "constructive" or "graph theory" in tags:
        strategies.append({
            "strategy": "counterexample_search",
            "description": "Evolve random structures toward counterexamples (Wagner pattern). Generate candidate graphs/objects, evaluate against conjecture, mutate best candidates.",
            "tool": "search_evolver.py / evolve_diverse.py",
        })

    if classification["n_datasets"] >= 2:
        strategies.append({
            "strategy": "cross_domain_probe",
            "description": f"Test structural connections between relevant datasets: {', '.join(classification['relevant_datasets'][:4])}",
            "tool": "expected_bridges.py",
        })

    if "primes" in tags or "number theory" in tags:
        strategies.append({
            "strategy": "prime_detrend_then_test",
            "description": "Apply microscope prime detrending to related sequences, then test residuals for hidden structure.",
            "tool": "microscope.py",
        })

    if problem.get("formalized", {}).get("state") == "yes":
        strategies.append({
            "strategy": "formal_verification",
            "description": "Problem is formalized in Lean. Can test partial results or reductions computationally.",
            "tool": "mathlib integration",
        })

    if not strategies:
        strategies.append({
            "strategy": "structural_embedding",
            "description": "Parse problem statement formulas into operator trees. Compare structural fingerprint against solved problems to find strategy transfer candidates.",
            "tool": "formula_graph_builder.py",
        })

    return strategies


def enrich_all(problems, oeis_names, extended_seqs):
    """Enrich all problems."""
    enriched = []
    for i, p in enumerate(problems):
        classification = classify_problem(p)
        oeis_info = enrich_oeis_connections(p, oeis_names, extended_seqs)
        strategies = suggest_strategies(p, classification)

        entry = {
            **p,
            "classification": classification,
            "oeis_info": oeis_info,
            "strategies": strategies,
            "n_strategies": len(strategies),
        }
        enriched.append(entry)

        if (i + 1) % 100 == 0:
            print(f"  Enriched {i + 1}/{len(problems)}")

    return enriched


def main():
    parser = argparse.ArgumentParser(description="Enrich Open Problems")
    parser.add_argument("--max", type=int, default=0, help="Max problems (0=all)")
    parser.add_argument("--tags", type=str, default=None, help="Filter by tag")
    args = parser.parse_args()

    print("=" * 70)
    print("  OPEN PROBLEM ENRICHMENT PIPELINE")
    print("=" * 70)

    t0 = time.time()

    # Load data
    print("  Loading problems...")
    problems = load_problems(tag_filter=args.tags, max_problems=args.max)
    print(f"  {len(problems)} open/testable problems loaded")

    print("  Loading OEIS names...")
    oeis_names = load_oeis_names()
    print(f"  {len(oeis_names)} OEIS names loaded")

    print("  Loading extended sequences...")
    extended = load_extended_sequences()
    print(f"  {len(extended)} sequences extended by us")

    # Enrich
    print(f"\n  Enriching {len(problems)} problems...")
    enriched = enrich_all(problems, oeis_names, extended)

    # Find relationships
    print(f"  Finding inter-problem relationships...")
    relationships = find_related_problems(problems)

    # Save
    with open(ENRICHED_FILE, "w") as f:
        for e in enriched:
            f.write(json.dumps(e, default=str) + "\n")

    with open(RELATIONSHIPS_FILE, "w") as f:
        for r in relationships:
            f.write(json.dumps(r) + "\n")

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  ENRICHMENT COMPLETE — {elapsed:.1f}s")
    print(f"  Problems enriched: {len(enriched)}")
    print(f"  Relationships found: {len(relationships)}")

    # Stats
    diff_dist = Counter(e["classification"]["difficulty"] for e in enriched)
    test_dist = Counter(e["classification"]["testability"] for e in enriched)
    n_with_oeis = sum(1 for e in enriched if e["oeis_info"]["n_oeis_refs"] > 0)
    n_extended = sum(1 for e in enriched if e["oeis_info"]["n_extended_by_us"] > 0)
    n_multi_ds = sum(1 for e in enriched if e["classification"]["n_datasets"] >= 2)

    print(f"\n  Difficulty: {dict(diff_dist.most_common())}")
    print(f"  Testability: {dict(test_dist.most_common())}")
    print(f"  With OEIS refs: {n_with_oeis}")
    print(f"  Sequences we already extended: {n_extended}")
    print(f"  Touch 2+ of our datasets: {n_multi_ds}")

    # Top dataset relevance
    ds_counts = Counter()
    for e in enriched:
        for ds in e["classification"]["relevant_datasets"]:
            ds_counts[ds] += 1
    print(f"\n  Dataset relevance:")
    for ds, count in ds_counts.most_common(10):
        print(f"    {ds:20s} {count:>4} problems")

    # Most connected problems
    problem_connections = Counter()
    for r in relationships:
        problem_connections[r["problem_a"]] += 1
        problem_connections[r["problem_b"]] += 1
    print(f"\n  Most connected problems:")
    for num, n_conn in problem_connections.most_common(10):
        p = next((e for e in enriched if e["number"] == num), {})
        tags = ", ".join(p.get("tags", [])[:3])
        print(f"    #{num:>5s} ({n_conn} connections) [{tags}]")

    # Problems we can attack RIGHT NOW (extended sequences + multiple datasets)
    immediate = [e for e in enriched
                 if e["oeis_info"]["n_extended_by_us"] > 0
                 and e["classification"]["n_datasets"] >= 2]
    if immediate:
        print(f"\n  === IMMEDIATE TARGETS ({len(immediate)}) ===")
        print(f"  (We already extended their OEIS sequences AND have relevant datasets)")
        for e in immediate[:15]:
            seqs = [c["sequence"] for c in e["oeis_info"]["oeis_connections"] if c["we_extended"]]
            print(f"    #{e['number']:>5s} [{e['classification']['difficulty']:>8s}] "
                  f"seqs={','.join(seqs[:3])} ds={','.join(e['classification']['relevant_datasets'][:3])}")

    print(f"\n  Output: {ENRICHED_FILE}")
    print(f"  Relationships: {RELATIONSHIPS_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
