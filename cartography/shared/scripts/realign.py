"""
Realignment Pipeline — Run after any major data change.
========================================================
Rebuilds the concept index, tensor bridges, and verifies known truths.
Run this after: new datasets, expanded datasets, new verb extractors,
or any change to search_engine.py paths.

Usage:
    python realign.py          # full realignment
    python realign.py --quick  # skip known truth battery (faster)
"""

import sys
import time
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(description="Realignment pipeline")
    parser.add_argument("--quick", action="store_true", help="Skip known truth battery")
    args = parser.parse_args()

    total_t0 = time.time()

    # Step 1: Verify all datasets are available
    print("=" * 70)
    print("  STEP 1: Dataset inventory check")
    print("=" * 70)
    from search_engine import inventory, SEARCH_REGISTRY
    inv = inventory()
    ok = sum(1 for v in inv.values() if v["available"])
    total = len(inv)
    print(f"  Datasets: {ok}/{total} available")
    for k, v in inv.items():
        status = "OK" if v["available"] else "MISSING"
        print(f"    {k}: {status} | {len(v['searches'])} searches | {v['description'][:50]}")
    print(f"  Total search functions: {len(SEARCH_REGISTRY)}")
    if ok < total:
        print(f"  WARNING: {total - ok} datasets missing!")

    # Step 2: Rebuild concept index
    print()
    print("=" * 70)
    print("  STEP 2: Rebuild concept index (nouns + verbs)")
    print("=" * 70)
    t0 = time.time()
    from concept_index import build_index, find_bridges
    stats = build_index()
    print(f"  Concepts: {stats.get('total_concepts', '?')}")
    print(f"  Links: {stats.get('total_links', '?')}")
    print(f"  Time: {time.time() - t0:.1f}s")

    # Step 3: Rebuild tensor bridges
    print()
    print("=" * 70)
    print("  STEP 3: Rebuild tensor bridges (SVD bond dimensions)")
    print("=" * 70)
    t0 = time.time()
    import subprocess
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "tensor_bridge.py")],
        capture_output=True, text=True, timeout=300
    )
    # Extract key stats from output
    for line in result.stdout.split("\n"):
        if any(kw in line for kw in ["datasets:", "objects:", "concepts:", "bond_dim=", "Done"]):
            print(f"  {line.strip()}")
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-200:]}")
    print(f"  Time: {time.time() - t0:.1f}s")

    # Step 4: Known truth battery (unless --quick)
    if not args.quick:
        print()
        print("=" * 70)
        print("  STEP 4: Known truth battery (180 tests)")
        print("=" * 70)
        t0 = time.time()
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "known_truth_expansion.py")],
            capture_output=True, text=True, timeout=600
        )
        # Extract summary
        for line in result.stdout.split("\n"):
            if any(kw in line for kw in ["KNOWN TRUTH BATTERY:", "Layer", "FAILURES"]):
                print(f"  {line.strip()}")
        if result.returncode != 0:
            print(f"  WARNING: Battery had errors")
            # Show failures
            for line in result.stdout.split("\n"):
                if "FAIL" in line:
                    print(f"  {line.strip()}")
        print(f"  Time: {time.time() - t0:.1f}s")
    else:
        print()
        print("  STEP 4: SKIPPED (--quick mode)")

    # Step 5: Summary
    total_elapsed = time.time() - total_t0
    print()
    print("=" * 70)
    print(f"  REALIGNMENT COMPLETE in {total_elapsed:.1f}s")
    print("=" * 70)
    print(f"  Datasets: {ok}/{total}")
    print(f"  Search functions: {len(SEARCH_REGISTRY)}")
    print(f"  Run explorers and overnight terminals AFTER this completes.")
    print(f"  Ghost nodes, steering vectors, and abstraction depths are now STALE")
    print(f"  until their scripts are re-run.")


if __name__ == "__main__":
    main()
