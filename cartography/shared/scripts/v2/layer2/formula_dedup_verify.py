"""
Formula Dedup + Verification — Separate true duplicates from structural isomorphisms.
======================================================================================
Two formulas are duplicates IFF they produce the same outputs for the same inputs.
Same skeleton + different outputs = structural isomorphism = bridge candidate.

Usage:
    python formula_dedup_verify.py                    # full verification
    python formula_dedup_verify.py --max 10000        # cap formulas
    python formula_dedup_verify.py --sample 5000      # random sample
"""

import argparse
import hashlib
import json
import sys
import time
import random
import math
import numpy as np
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from formula_to_executable import tree_to_callable

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "cartography" / "convergence" / "data"
TREES_FILE = DATA / "formula_trees.jsonl"
FORMULAS_FILE = DATA / "openwebmath_formulas.jsonl"

# Test points for evaluation — mix of simple and transcendental
# to distinguish formulas that agree on integers but differ on reals
TEST_POINTS = [
    {"x": 1.0, "y": 1.0, "z": 1.0, "a": 1.0, "b": 1.0, "t": 1.0, "n": 1.0},
    {"x": 2.0, "y": 3.0, "z": 0.5, "a": 2.0, "b": 3.0, "t": 2.0, "n": 2.0},
    {"x": math.pi, "y": math.e, "z": 0.1, "a": math.pi, "b": math.e, "t": math.pi, "n": 3.0},
    {"x": -1.0, "y": 0.5, "z": 2.0, "a": -1.0, "b": 0.5, "t": -1.0, "n": 4.0},
    {"x": 0.7, "y": 1.3, "z": 0.3, "a": 0.7, "b": 1.3, "t": 0.7, "n": 5.0},
]

EPSILON = 1e-8  # tolerance for "same output"


def evaluate_formula(func, variables):
    """Evaluate a compiled formula at all test points. Returns list of outputs or None."""
    outputs = []
    for point in TEST_POINTS:
        var_vals = {v: point.get(v, 1.0) for v in variables}
        try:
            result = func(var_vals)
            if isinstance(result, np.ndarray):
                result = float(result.flat[0])
            result = float(result)
            if not math.isfinite(result):
                result = None
        except Exception:
            result = None
        outputs.append(result)
    return outputs


def outputs_match(out_a, out_b):
    """Check if two output vectors are the same within epsilon."""
    if len(out_a) != len(out_b):
        return False
    n_comparable = 0
    n_match = 0
    for a, b in zip(out_a, out_b):
        if a is None or b is None:
            continue
        n_comparable += 1
        if abs(a - b) < EPSILON * (1 + abs(a) + abs(b)):
            n_match += 1
    # Need at least 3 comparable points, all matching
    return n_comparable >= 3 and n_match == n_comparable


def main():
    parser = argparse.ArgumentParser(description="Formula Dedup + Verification")
    parser.add_argument("--max", type=int, default=50000, help="Max formulas to process")
    parser.add_argument("--sample", type=int, default=0, help="Random sample size (0=sequential)")
    args = parser.parse_args()

    print("=" * 70)
    print("  FORMULA DEDUP VERIFICATION")
    print("  Same skeleton + same outputs = duplicate")
    print("  Same skeleton + different outputs = STRUCTURAL ISOMORPHISM")
    print("=" * 70)

    t0 = time.time()

    # Phase 1: Load formulas and group by skeleton
    print("\n  Phase 1: Loading operadic signatures...")
    sig_file = DATA / "operadic_signatures.jsonl"
    if not sig_file.exists():
        print("  ERROR: operadic_signatures.jsonl not found. Run operadic_signatures.py first.")
        return

    skeleton_groups = defaultdict(list)  # skeleton_hash -> [(hash, domain, skeleton_str)]
    with open(sig_file) as f:
        for i, line in enumerate(f):
            if args.max and i >= args.max:
                break
            try:
                d = json.loads(line)
                sh = d.get("skeleton_hash", "")
                h = d.get("hash", "")
                domain = d.get("domain", "unknown")
                skel = d.get("skeleton_str", "")
                if sh and h:
                    skeleton_groups[sh].append((h, domain, skel))
            except Exception:
                pass

    n_total = sum(len(v) for v in skeleton_groups.values())
    n_groups = len(skeleton_groups)
    multi_groups = {k: v for k, v in skeleton_groups.items() if len(v) >= 2}
    cross_domain_groups = {k: v for k, v in multi_groups.items()
                           if len({d for _, d, _ in v}) >= 2}

    print(f"  {n_total:,} formulas in {n_groups:,} skeleton groups")
    print(f"  {len(multi_groups):,} groups with 2+ formulas")
    print(f"  {len(cross_domain_groups):,} groups with 2+ domains (verification targets)")

    # Phase 2: Load trees for cross-domain groups
    print("\n  Phase 2: Loading formula trees for cross-domain groups...")
    target_hashes = set()
    for group in cross_domain_groups.values():
        for h, _, _ in group:
            target_hashes.add(h)

    print(f"  Need {len(target_hashes):,} formula trees")

    trees = {}
    with open(TREES_FILE) as f:
        for i, line in enumerate(f):
            if len(trees) >= len(target_hashes):
                break
            try:
                d = json.loads(line)
                h = d.get("hash", "")
                if h in target_hashes:
                    trees[h] = d
            except Exception:
                pass
            if i % 1000000 == 0 and i > 0:
                print(f"    scanned {i // 1000000}M trees, found {len(trees)}/{len(target_hashes)}")

    print(f"  Found {len(trees):,} / {len(target_hashes):,} trees")

    # Phase 3: Verify — evaluate and compare
    print("\n  Phase 3: Evaluating and comparing...")
    true_duplicates = []
    structural_isomorphisms = []
    eval_failures = 0
    n_compared = 0

    for skeleton_hash, group in cross_domain_groups.items():
        # Get evaluable formulas from this group
        evaluable = []
        for h, domain, skel in group:
            if h not in trees:
                continue
            tree = trees[h]
            try:
                func, variables, success = tree_to_callable(tree)
                if success and func is not None:
                    outputs = evaluate_formula(func, variables)
                    if any(o is not None for o in outputs):
                        evaluable.append((h, domain, skel, outputs, variables))
            except Exception:
                eval_failures += 1

        if len(evaluable) < 2:
            continue

        # Compare all pairs within group
        for i in range(len(evaluable)):
            for j in range(i + 1, len(evaluable)):
                h_a, dom_a, skel_a, out_a, vars_a = evaluable[i]
                h_b, dom_b, skel_b, out_b, vars_b = evaluable[j]

                if dom_a == dom_b:
                    continue  # only care about cross-domain

                n_compared += 1
                match = outputs_match(out_a, out_b)

                entry = {
                    "hash_a": h_a, "domain_a": dom_a,
                    "hash_b": h_b, "domain_b": dom_b,
                    "skeleton_hash": skeleton_hash,
                    "skeleton_str": skel_a[:100],
                    "outputs_match": match,
                    "outputs_a": [round(o, 6) if o is not None else None for o in out_a],
                    "outputs_b": [round(o, 6) if o is not None else None for o in out_b],
                    "vars_a": vars_a[:5],
                    "vars_b": vars_b[:5],
                }

                if match:
                    true_duplicates.append(entry)
                else:
                    structural_isomorphisms.append(entry)

    elapsed = time.time() - t0

    # Save results
    dupes_file = DATA / "verified_duplicates.jsonl"
    isos_file = DATA / "structural_isomorphisms.jsonl"

    with open(dupes_file, "w") as f:
        for d in true_duplicates:
            f.write(json.dumps(d, default=str) + "\n")

    with open(isos_file, "w") as f:
        for d in structural_isomorphisms:
            f.write(json.dumps(d, default=str) + "\n")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  VERIFICATION COMPLETE — {elapsed:.1f}s")
    print(f"  Cross-domain groups verified: {len(cross_domain_groups):,}")
    print(f"  Pairs compared: {n_compared:,}")
    print(f"  Eval failures: {eval_failures:,}")
    print(f"  TRUE DUPLICATES: {len(true_duplicates):,} (same outputs — merge safely)")
    print(f"  STRUCTURAL ISOMORPHISMS: {len(structural_isomorphisms):,} (different outputs — BRIDGE CANDIDATES)")

    if structural_isomorphisms:
        print(f"\n  === TOP STRUCTURAL ISOMORPHISMS ===")
        # Sort by output divergence (most different = most interesting)
        for iso in structural_isomorphisms[:15]:
            oa = [o for o in iso["outputs_a"] if o is not None]
            ob = [o for o in iso["outputs_b"] if o is not None]
            if oa and ob:
                divergence = sum(abs(a - b) for a, b in zip(oa, ob) if a is not None and b is not None)
            else:
                divergence = 0
            print(f"    {iso['hash_a'][:12]} ({iso['domain_a']}) <-> {iso['hash_b'][:12]} ({iso['domain_b']})")
            print(f"      skeleton: {iso['skeleton_str'][:60]}")
            print(f"      outputs_a: {iso['outputs_a'][:3]}")
            print(f"      outputs_b: {iso['outputs_b'][:3]}")
            print(f"      divergence: {divergence:.4f}")
            print()

    if true_duplicates:
        print(f"\n  === SAMPLE TRUE DUPLICATES ===")
        for d in true_duplicates[:5]:
            print(f"    {d['hash_a'][:12]} ({d['domain_a']}) == {d['hash_b'][:12]} ({d['domain_b']})")
            print(f"      skeleton: {d['skeleton_str'][:60]}")

    print(f"\n  Duplicates: {dupes_file.name}")
    print(f"  Isomorphisms: {isos_file.name}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
