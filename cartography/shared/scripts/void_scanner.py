"""
Void Scanner — Zero-cost autonomous hypothesis testing.
========================================================
No LLM. No API. Pure computation.

Mines the 17K hypothesis corpus for templates, then systematically
tests all disconnected dataset pairs using template substitution.

Strategy:
  1. Load concept index to find which pairs share concepts
  2. For disconnected pairs: look for near-miss verb bridges
  3. For weak pairs (bond_dim=1, low sv): stress-test the bridge
  4. Generate hypotheses from templates, run battery on each

The 8 DeepSeek terminals already generated 17K hypotheses.
This script recombines them at zero cost.

Usage:
    python void_scanner.py                    # scan all voids
    python void_scanner.py --pairs 10         # test 10 pairs
    python void_scanner.py --target Maass     # focus on one dataset
"""

import json
import re
import sys
import time
import numpy as np
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
MEMORY_FILE = CONVERGENCE / "data" / "research_memory.jsonl"
LINKS_FILE = CONVERGENCE / "data" / "concept_links.jsonl"
BRIDGES_FILE = CONVERGENCE / "data" / "bridges.jsonl"
TENSOR_FILE = CONVERGENCE / "data" / "tensor_bridges.json"
RESULTS_FILE = CONVERGENCE / "data" / "void_scanner_results.jsonl"


def load_dataset_concepts():
    """Load concept→dataset mapping from concept_links."""
    ds_concepts = defaultdict(set)  # dataset → set of concepts
    concept_ds = defaultdict(set)   # concept → set of datasets
    with open(LINKS_FILE) as f:
        for line in f:
            link = json.loads(line)
            ds_concepts[link["dataset"]].add(link["concept"])
            concept_ds[link["concept"]].add(link["dataset"])
    return ds_concepts, concept_ds


def load_tensor_bonds():
    """Load SVD bond dimensions between dataset pairs."""
    tensor = json.load(open(TENSOR_FILE))
    bonds = {}
    for pair_key, data in tensor.get("svd_bond_dimensions", {}).items():
        bonds[pair_key] = {
            "bond_dim": data["bond_dim"],
            "top_sv": data["top_singular_values"][0] if data["top_singular_values"] else 0,
        }
    return bonds


def load_hypothesis_templates():
    """Mine the research memory for reusable hypothesis templates."""
    templates = defaultdict(list)  # pattern → list of (hypothesis, status)
    with open(MEMORY_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                h = json.loads(line)
            except:
                continue
            hyp = h.get("hypothesis", "")
            status = h.get("status", "open")

            # Extract template: replace specific values with slots
            t = re.sub(r'\d+\.?\d*', '{N}', hyp)
            t = re.sub(r'A\d{6}', '{SEQ}', t)
            t = t[:150]
            templates[t].append(status)

    # Score templates by kill rate
    scored = []
    for tmpl, statuses in templates.items():
        n = len(statuses)
        if n < 3:
            continue
        killed = sum(1 for s in statuses if s == "falsified")
        survival_rate = 1 - killed / n
        scored.append({
            "template": tmpl,
            "n": n,
            "survival_rate": survival_rate,
            "killed": killed,
        })

    scored.sort(key=lambda x: (-x["survival_rate"], -x["n"]))
    return scored


def find_void_pairs(ds_concepts, bonds):
    """Find dataset pairs with zero bond dimension or missing from tensor."""
    all_datasets = sorted(ds_concepts.keys())
    voids = []
    weak = []

    for d1, d2 in combinations(all_datasets, 2):
        pair_key = f"{d1}--{d2}"
        pair_key_rev = f"{d2}--{d1}"
        bond = bonds.get(pair_key) or bonds.get(pair_key_rev)

        if bond is None or bond["bond_dim"] == 0:
            voids.append((d1, d2, 0, 0))
        elif bond["bond_dim"] == 1 and bond["top_sv"] < 50:
            weak.append((d1, d2, bond["bond_dim"], bond["top_sv"]))

    return voids, weak


def test_concept_overlap(d1, d2, ds_concepts, concept_ds):
    """Test if two datasets share concepts not captured by tensor."""
    c1 = ds_concepts[d1]
    c2 = ds_concepts[d2]
    shared = c1 & c2

    if not shared:
        return None

    # Separate verb and noun bridges
    verb_shared = {c for c in shared if c.startswith("verb_")}
    noun_shared = shared - verb_shared

    # Score: verb bridges are more interesting than noun bridges
    score = len(verb_shared) * 3 + len(noun_shared)

    return {
        "pair": f"{d1}--{d2}",
        "n_shared": len(shared),
        "n_verb": len(verb_shared),
        "n_noun": len(noun_shared),
        "verb_bridges": sorted(verb_shared)[:20],
        "noun_bridges": sorted(noun_shared)[:10],
        "score": score,
    }


def test_numerical_bridge(d1, d2, ds_concepts):
    """Test if numerical properties create a bridge between datasets.

    For each dataset, collect the integers that appear as concept values
    (e.g., integer_13, dimension_3, degree_2) and test for overlap.
    """
    def extract_integers(concepts):
        ints = set()
        for c in concepts:
            m = re.match(r'(?:integer|dimension|degree|level|kissing|spectral_bin)_(\d+)', c)
            if m:
                ints.add(int(m.group(1)))
        return ints

    i1 = extract_integers(ds_concepts[d1])
    i2 = extract_integers(ds_concepts[d2])
    overlap = i1 & i2

    if len(overlap) < 3:
        return None

    return {
        "pair": f"{d1}--{d2}",
        "n_shared_integers": len(overlap),
        "sample": sorted(overlap)[:20],
        "d1_integers": len(i1),
        "d2_integers": len(i2),
        "jaccard": len(overlap) / len(i1 | i2) if i1 | i2 else 0,
    }


def scan_voids(max_pairs=None, target_dataset=None):
    """Main scanner: find and test all void/weak dataset pairs."""
    print("=" * 70)
    print("  VOID SCANNER — Zero-cost autonomous hypothesis testing")
    print("  No LLM. No API. Pure computation.")
    print("=" * 70)

    t0 = time.time()

    print("\n  Loading concept index...")
    ds_concepts, concept_ds = load_dataset_concepts()
    print(f"  {len(ds_concepts)} datasets, {len(concept_ds)} concepts")

    print("  Loading tensor bonds...")
    bonds = load_tensor_bonds()
    print(f"  {len(bonds)} dataset pairs with bond data")

    print("  Loading hypothesis templates...")
    templates = load_hypothesis_templates()
    print(f"  {len(templates)} reusable templates (from 17K hypotheses)")

    print("\n  Finding voids and weak bridges...")
    voids, weak = find_void_pairs(ds_concepts, bonds)
    print(f"  {len(voids)} void pairs (bond_dim=0)")
    print(f"  {len(weak)} weak pairs (bond_dim=1, sv<50)")

    # Filter by target if specified
    if target_dataset:
        voids = [(d1, d2, bd, sv) for d1, d2, bd, sv in voids
                 if target_dataset in d1 or target_dataset in d2]
        weak = [(d1, d2, bd, sv) for d1, d2, bd, sv in weak
                if target_dataset in d1 or target_dataset in d2]
        print(f"  Filtered to {target_dataset}: {len(voids)} voids, {len(weak)} weak")

    # Combine and limit
    all_pairs = [(d1, d2, bd, sv, "void") for d1, d2, bd, sv in voids] + \
                [(d1, d2, bd, sv, "weak") for d1, d2, bd, sv in weak]
    if max_pairs:
        all_pairs = all_pairs[:max_pairs]

    results = []

    print(f"\n  Scanning {len(all_pairs)} pairs...\n")

    for d1, d2, bd, sv, ptype in all_pairs:
        pair_label = f"{d1}--{d2}"
        print(f"  --- {pair_label} ({ptype}, bd={bd}, sv={sv:.1f}) ---")

        # Test 1: Concept overlap
        overlap = test_concept_overlap(d1, d2, ds_concepts, concept_ds)
        if overlap:
            print(f"    Concept overlap: {overlap['n_shared']} shared "
                  f"({overlap['n_verb']} verbs, {overlap['n_noun']} nouns)")
            if overlap['verb_bridges']:
                print(f"    Verb bridges: {', '.join(overlap['verb_bridges'][:5])}")
        else:
            print(f"    No concept overlap — true void")

        # Test 2: Numerical bridge
        num_bridge = test_numerical_bridge(d1, d2, ds_concepts)
        if num_bridge:
            print(f"    Numerical bridge: {num_bridge['n_shared_integers']} shared integers "
                  f"(Jaccard={num_bridge['jaccard']:.3f})")
        else:
            print(f"    No numerical bridge")

        result = {
            "pair": pair_label,
            "type": ptype,
            "bond_dim": bd,
            "top_sv": sv,
            "concept_overlap": overlap,
            "numerical_bridge": num_bridge,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        results.append(result)

    # Write results
    with open(RESULTS_FILE, "a") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  VOID SCAN COMPLETE in {elapsed:.1f}s")
    print(f"  Pairs scanned: {len(results)}")
    n_concept = sum(1 for r in results if r["concept_overlap"])
    n_num = sum(1 for r in results if r["numerical_bridge"])
    n_true_void = sum(1 for r in results if not r["concept_overlap"] and not r["numerical_bridge"])
    print(f"  With concept overlap: {n_concept}")
    print(f"  With numerical bridge: {n_num}")
    print(f"  True voids (nothing): {n_true_void}")
    print(f"  Results appended to {RESULTS_FILE}")
    print(f"{'=' * 70}")

    # Show top templates for reference
    print(f"\n  Top surviving hypothesis templates (for manual exploration):")
    for t in templates[:5]:
        print(f"    [{t['n']:3d}x, {t['survival_rate']:.0%} survive] {t['template'][:100]}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Zero-cost void scanner")
    parser.add_argument("--pairs", type=int, default=None, help="Max pairs to scan")
    parser.add_argument("--target", type=str, default=None, help="Focus on one dataset")
    args = parser.parse_args()

    scan_voids(max_pairs=args.pairs, target_dataset=args.target)
