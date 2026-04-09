"""
Explorer Loop — Autonomous zero-cost exploration agent.
========================================================
Runs continuously alongside the 8 DeepSeek terminals.
No API calls. Pure computation. Rebuilds the shadow tensor
after each sweep and targets the gaps.

Loop:
  1. Void scan (find disconnected/weak pairs)
  2. Bridge hunt (generate + test hypotheses from bridges)
  3. MAP-Elites illumination (fill empty bins)
  4. Rebuild shadow tensor (update the dark matter map)
  5. Sleep, repeat

Usage:
    python explorer_loop.py                  # run forever
    python explorer_loop.py --sweeps 5       # run 5 sweeps then stop
    python explorer_loop.py --interval 300   # 5 min between sweeps
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Windows low-priority: don't compete with the 8 DeepSeek terminals
try:
    import psutil
    psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    print("  [explorer] Set to BELOW_NORMAL priority")
except Exception:
    try:
        os.nice(10)  # Unix fallback
    except Exception:
        pass


def _yield():
    """Yield CPU between phases so terminals aren't starved."""
    time.sleep(0.5)


FRONTIER_TARGETS = Path(__file__).resolve().parents[3] / "cartography" / "convergence" / "data" / "frontier_targets.jsonl"


def _load_frontier_priorities():
    """Load frontier targets from the novelty scorer and extract priority datasets.

    Returns a set of dataset names that appear in high-novelty concepts,
    plus the raw list of frontier entries for logging.
    Returns (priority_datasets: set, frontier_entries: list).
    If the file doesn't exist, returns (set(), []).
    """
    if not FRONTIER_TARGETS.exists():
        return set(), []

    entries = []
    priority_datasets = set()
    try:
        with open(FRONTIER_TARGETS) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                    # Only count concepts spanning 2+ datasets as frontier bridges
                    if entry.get("n_datasets", 0) >= 2:
                        for ds in entry.get("datasets", []):
                            priority_datasets.add(ds)
                except (json.JSONDecodeError, KeyError):
                    pass
    except Exception as e:
        print(f"    WARNING: Could not load frontier targets: {e}")
        return set(), []

    return priority_datasets, entries


def _boost_void_results_by_frontier(void_results, priority_datasets):
    """Re-sort void scan results so pairs involving frontier datasets come first.

    Pairs are scored by how many of their two datasets appear in the
    priority set (0, 1, or 2), then by their original concept overlap score.
    Returns a new sorted list (does not mutate the original).
    """
    if not priority_datasets:
        return void_results

    def _frontier_score(vr):
        pair = vr.get("pair", "")
        parts = pair.split("--")
        hits = sum(1 for p in parts if p in priority_datasets)
        concept_score = (vr.get("concept_overlap") or {}).get("score", 0)
        return (-hits, -concept_score)

    return sorted(void_results, key=_frontier_score)


def run_sweep(sweep_num):
    """Run one complete exploration sweep."""
    print(f"\n{'='*70}")
    print(f"  EXPLORER SWEEP #{sweep_num} -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    t0 = time.time()

    # Phase 0: Frontier targeting (novelty scorer steering)
    print(f"\n  [0/4] Frontier Targeting...")
    priority_datasets, frontier_entries = _load_frontier_priorities()
    if priority_datasets:
        frontier_concepts = [e for e in frontier_entries if e.get("n_datasets", 0) >= 2]
        print(f"    Loaded {len(frontier_entries)} frontier targets, "
              f"{len(frontier_concepts)} span 2+ datasets")
        print(f"    Priority datasets ({len(priority_datasets)}): "
              f"{', '.join(sorted(priority_datasets)[:10])}"
              f"{'...' if len(priority_datasets) > 10 else ''}")
        for fc in frontier_concepts[:5]:
            print(f"      {fc['concept_id']:25s}  novelty={fc['novelty_score']:.3f}  "
                  f"datasets={fc['n_datasets']}")
    else:
        print(f"    No frontier targets found — falling back to unsteered exploration")
    _yield()

    # Phase 1: Void scan
    print(f"\n  [1/4] Void Scanner...")
    try:
        from void_scanner import scan_voids
        scan_voids()
    except Exception as e:
        print(f"    ERROR: {e}")
    _yield()

    # Phase 2: Bridge hunt (frontier-steered if targets available)
    print(f"\n  [2/4] Bridge Hunter...")
    try:
        from bridge_hunter import hunt_bridges
        hunt_bridges(priority_datasets=priority_datasets if priority_datasets else None)
    except Exception as e:
        print(f"    ERROR: {e}")
    _yield()

    # Phase 3: MAP-Elites illumination
    print(f"\n  [3/4] MAP-Elites Illuminator...")
    try:
        from map_elites import illuminate
        illuminate(n_sweeps=1)
    except Exception as e:
        print(f"    ERROR: {e}")
    _yield()

    # Phase 4: Rebuild shadow tensor
    print(f"\n  [4/4] Shadow Tensor Rebuild...")
    try:
        from shadow_tensor import build_shadow_tensor, show_hot_cells
        shadow = build_shadow_tensor()
        show_hot_cells(shadow)
    except Exception as e:
        print(f"    ERROR: {e}")

    elapsed = time.time() - t0
    print(f"\n  Sweep #{sweep_num} complete in {elapsed:.1f}s")
    return elapsed


def main():
    parser = argparse.ArgumentParser(description="Explorer Loop — zero-cost autonomous agent")
    parser.add_argument("--sweeps", type=int, default=0, help="Number of sweeps (0=infinite)")
    parser.add_argument("--interval", type=int, default=600, help="Seconds between sweeps (default 10min)")
    args = parser.parse_args()

    print("=" * 70)
    print("  EXPLORER LOOP — Zero-cost autonomous exploration")
    print(f"  Sweeps: {'infinite' if args.sweeps == 0 else args.sweeps}")
    print(f"  Interval: {args.interval}s between sweeps")
    print(f"  No API calls. Pure computation.")
    print("=" * 70)

    sweep = 0
    while True:
        sweep += 1
        if args.sweeps > 0 and sweep > args.sweeps:
            break

        elapsed = run_sweep(sweep)

        if args.sweeps > 0 and sweep >= args.sweeps:
            break

        # Wait between sweeps — the DeepSeek terminals are generating
        # new data that the next sweep will pick up
        wait = max(10, args.interval - elapsed)
        print(f"\n  Waiting {wait:.0f}s for terminals to generate new data...")
        time.sleep(wait)

    print(f"\n  Explorer loop finished after {sweep} sweeps.")


if __name__ == "__main__":
    main()
