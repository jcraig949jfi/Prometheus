#!/usr/bin/env python3
"""
Autonomous Explorer: The main evolutionary loop.

Generate → Execute → Update → Repeat.
No LLM calls. Pure local computation.
The machine takes the failures. We take the survivors.
"""
import sys
import json
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from gene_schema import Hypothesis, random_hypothesis, mutate_single, crossover
from executor import execute
from archive import Archive
from kill_taxonomy import init_db, add_kill, get_all_kills

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def run_generation(archive, gen, n_hypotheses=20, rng=None):
    """Run one generation of the evolutionary loop."""
    if rng is None:
        rng = random.Random()

    hypotheses = []

    # Strategy mix:
    # 40% random (exploration)
    # 30% mutation of archive elites (exploitation)
    # 20% crossover of archive elites (recombination)
    # 10% targeted void filling (diversity)

    n_random = int(n_hypotheses * 0.4)
    n_mutate = int(n_hypotheses * 0.3)
    n_crossover = int(n_hypotheses * 0.2)
    n_void = n_hypotheses - n_random - n_mutate - n_crossover

    # Random
    for _ in range(n_random):
        hypotheses.append(random_hypothesis(gen, rng))

    # Mutation from archive
    if archive.grid:
        for _ in range(n_mutate):
            parents = archive.select_parents(1)
            if parents:
                hypotheses.append(mutate_single(parents[0], gen, rng))
            else:
                hypotheses.append(random_hypothesis(gen, rng))

    # Crossover from archive
    if len(archive.grid) >= 2:
        for _ in range(n_crossover):
            parents = archive.select_parents(2)
            if len(parents) >= 2:
                hypotheses.append(crossover(parents[0], parents[1], gen, rng))
            else:
                hypotheses.append(random_hypothesis(gen, rng))
    else:
        for _ in range(n_crossover):
            hypotheses.append(random_hypothesis(gen, rng))

    # Void-targeted
    void_cells = list(archive.get_void_cells())
    for _ in range(n_void):
        h = random_hypothesis(gen, rng)
        # Try to target a void cell by biasing domain selection
        if void_cells:
            target = rng.choice(void_cells)
            # Parse the domain key to get domain categories
            # (simplified — just randomize within constraints)
        hypotheses.append(h)

    # Validate all
    valid = []
    for h in hypotheses:
        errors = h.validate()
        if not errors:
            valid.append(h)

    # Execute all
    results = []
    for h in valid:
        result = execute(h)
        archive.update(h, result)
        results.append({"hypothesis": h.id, **result})

    return results


def run_explorer(n_generations=100, n_per_gen=20, seed=42, log_interval=10):
    """Run the full autonomous explorer."""
    rng = random.Random(seed)

    # Initialize
    db_path = init_db()
    archive = Archive()
    all_results = []
    start_time = time.time()

    print("=" * 80)
    print(f"AUTONOMOUS EXPLORER — {n_generations} generations × {n_per_gen} hypotheses")
    print(f"Total hypothesis space: ~3.1 billion")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 80)

    for gen in range(n_generations):
        gen_start = time.time()
        results = run_generation(archive, gen, n_per_gen, rng)
        all_results.extend(results)
        archive.generation = gen
        gen_time = time.time() - gen_start

        # Log progress
        if gen % log_interval == 0 or gen == n_generations - 1:
            summary = archive.summary()
            survived = sum(1 for r in results if r.get("survival_depth", 0) > 0)
            deep = sum(1 for r in results if r.get("survival_depth", 0) >= 3)

            print(f"  Gen {gen:4d}/{n_generations} | "
                  f"tested={summary['total_tested']:5d} | "
                  f"cells={summary['cells_filled']:3d} | "
                  f"max_depth={summary['max_depth']} | "
                  f"this_gen: {survived}/{len(results)} survived | "
                  f"deep={deep} | "
                  f"{gen_time:.1f}s")

    # Final report
    elapsed = time.time() - start_time
    summary = archive.summary()

    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    print(f"  Time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"  Generations: {n_generations}")
    print(f"  Total tested: {summary['total_tested']}")
    print(f"  Cells filled: {summary['cells_filled']}")
    print(f"  Max survival depth: {summary['max_depth']}")
    print(f"  Depth distribution: {summary['depth_distribution']}")
    print(f"  Top kill modes: {summary['top_kill_modes']}")
    print(f"  Void cells remaining: {len(archive.get_void_cells())}")
    print(f"  Hypotheses/second: {summary['total_tested']/elapsed:.1f}")

    # Top survivors
    if archive.grid:
        print(f"\n  TOP SURVIVORS:")
        top = sorted(archive.grid.values(), key=lambda h: -h.survival_depth)[:10]
        for h in top:
            print(f"    depth={h.survival_depth} z={h.fitness:+.1f} | "
                  f"{h.domain_a[:12]:12s} × {h.domain_b[:12]:12s} | "
                  f"{h.feature_a[:15]:15s} × {h.feature_b[:15]:15s} | "
                  f"{h.coupling}")

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive.save(RESULTS_DIR / f"archive_{timestamp}.json")

    log_path = RESULTS_DIR / f"run_{timestamp}.jsonl"
    with open(log_path, "w") as f:
        for r in all_results:
            f.write(json.dumps(r, default=str) + "\n")

    print(f"\n  Saved: {RESULTS_DIR / f'archive_{timestamp}.json'}")
    print(f"  Log: {log_path}")

    return archive, all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Explorer")
    parser.add_argument("--generations", type=int, default=10, help="Number of generations")
    parser.add_argument("--per-gen", type=int, default=20, help="Hypotheses per generation")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--log-interval", type=int, default=5, help="Log every N generations")
    args = parser.parse_args()

    run_explorer(args.generations, args.per_gen, args.seed, args.log_interval)
