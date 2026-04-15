#!/usr/bin/env python3
"""
Ergon Autonomous Explorer: Tensor-native evolutionary hypothesis search.

Uses the precomputed tensor from tensor_builder.py and the full-battery
tensor_executor.py. Imports gene_schema, archive, and kill_taxonomy from
forge/v3 (the original explorer stays untouched).

Throughput: ~57 hyp/sec (vs 9.3 in forge/v3).
"""
import sys
import json
import time
import random
import logging
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter

_root = Path(__file__).resolve().parent.parent  # Prometheus/
_forge_v3 = str(_root / "forge/v3")
if _forge_v3 not in sys.path:
    sys.path.insert(0, _forge_v3)
sys.path.insert(0, str(Path(__file__).parent))

from gene_schema import Hypothesis
from constrained_operators import random_hypothesis, mutate_single, crossover
from archive import Archive
from kill_taxonomy import init_db, add_kill, get_all_kills
from tensor_builder import build_tensor
from tensor_executor import TensorExecutor
from shadow_archive import ShadowArchive

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


# ============================================================
# Structured Logger
# ============================================================

def setup_logging(run_id):
    """Set up structured JSON logging + console output."""
    log_path = LOGS_DIR / f"{run_id}.jsonl"

    logger = logging.getLogger("ergon")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # JSON file handler — every event as a structured line
    fh = logging.FileHandler(str(log_path), encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            entry = {
                "ts": datetime.now().isoformat(),
                "level": record.levelname,
                "event": record.getMessage(),
            }
            if hasattr(record, "data"):
                entry["data"] = record.data
            return json.dumps(entry, default=str)

    fh.setFormatter(JSONFormatter())
    logger.addHandler(fh)

    # Console handler — human-readable
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    return logger, log_path


def log_event(logger, event, data=None, level=logging.INFO):
    """Log a structured event with optional data dict. Flushes to disk immediately."""
    record = logger.makeRecord(
        "ergon", level, "", 0, event, (), None
    )
    if data:
        record.data = data
    logger.handle(record)
    # Flush to disk so monitoring tools see writes immediately
    for handler in logger.handlers:
        handler.flush()


# ============================================================
# Generation
# ============================================================

def run_generation(archive, gen, n_hypotheses=20, rng=None, executor=None, shadow=None):
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
        hypotheses.append(h)

    # Validate all
    valid = []
    for h in hypotheses:
        errors = h.validate()
        if not errors:
            valid.append(h)

    # Execute all via tensor executor
    results = []
    for h in valid:
        result = executor.execute(h)
        archive.update(h, result)
        if shadow is not None:
            shadow.record(h, result)
        results.append({"hypothesis": h.id, **result})

    return results


# ============================================================
# Main Explorer
# ============================================================

def run_explorer(n_generations=100, n_per_gen=20, seed=42, log_interval=10,
                 checkpoint_interval=500):
    """Run the full autonomous explorer with tensor-native execution."""
    rng = random.Random(seed)
    run_id = f"ergon_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Initialize
    db_path = init_db()
    archive = Archive()
    shadow = ShadowArchive()
    all_results = []
    start_time = time.time()

    # Set up logging
    logger, log_path = setup_logging(run_id)

    log_event(logger, "run_started", {
        "run_id": run_id,
        "n_generations": n_generations,
        "n_per_gen": n_per_gen,
        "seed": seed,
        "log_interval": log_interval,
        "checkpoint_interval": checkpoint_interval,
        "hypothesis_space": "~3.1B",
    })

    print("=" * 80)
    print(f"ERGON EXPLORER — {n_generations} generations × {n_per_gen} hypotheses")
    print(f"Run ID: {run_id}")
    print(f"Log: {log_path}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 80)

    # Build tensor once at startup
    print("\nBuilding precomputed tensor...")
    tensor_start = time.time()
    tensor_path = Path(__file__).parent / "tensor.npz"
    if tensor_path.exists():
        print(f"  Loading cached tensor from {tensor_path}")
        executor = TensorExecutor(tensor_path=str(tensor_path))
    else:
        tensor = build_tensor(verbose=True)
        tensor.save(tensor_path)
        executor = TensorExecutor(tensor=tensor)

    tensor_time = time.time() - tensor_start
    log_event(logger, "tensor_ready", {
        "shape": [executor.tensor.n_objects, executor.tensor.n_features],
        "domains": list(executor.tensor.domain_boundaries.keys()),
        "load_time_s": round(tensor_time, 2),
        "source": "cache" if tensor_path.exists() else "built",
    })
    print(f"  Tensor ready in {tensor_time:.2f}s")
    print(f"  Shape: {executor.tensor.n_objects} objects × {executor.tensor.n_features} features")
    print(f"  Domains: {list(executor.tensor.domain_boundaries.keys())}")
    print()

    # Tracking for rate stats
    last_checkpoint_time = time.time()
    last_checkpoint_tested = 0

    for gen in range(n_generations):
        gen_start = time.time()
        results = run_generation(archive, gen, n_per_gen, rng, executor=executor, shadow=shadow)
        all_results.extend(results)
        archive.generation = gen
        gen_time = time.time() - gen_start

        # Per-generation structured log (DEBUG level — file only)
        gen_kills = Counter(r.get("kill_test", "") for r in results if r.get("kill_test"))
        gen_survived = sum(1 for r in results if r.get("survival_depth", 0) > 0)
        gen_deep = sum(1 for r in results if r.get("survival_depth", 0) >= 3)

        log_event(logger, "generation_complete", {
            "gen": gen,
            "tested": len(results),
            "survived": gen_survived,
            "deep": gen_deep,
            "gen_time_s": round(gen_time, 2),
            "kills": dict(gen_kills.most_common(3)),
        }, level=logging.DEBUG)

        # Console progress at log_interval
        if gen % log_interval == 0 or gen == n_generations - 1:
            summary = archive.summary()
            elapsed = time.time() - start_time

            # Compute recent throughput
            interval_tested = summary["total_tested"] - last_checkpoint_tested
            interval_time = time.time() - last_checkpoint_time
            recent_rate = interval_tested / interval_time if interval_time > 0 else 0

            msg = (f"  Gen {gen:5d}/{n_generations} | "
                   f"tested={summary['total_tested']:6d} | "
                   f"cells={summary['cells_filled']:3d} | "
                   f"max_depth={summary['max_depth']:2d} | "
                   f"this_gen: {gen_survived}/{len(results)} survived | "
                   f"deep={gen_deep} | "
                   f"{recent_rate:.1f} hyp/s | "
                   f"{elapsed/60:.1f}m")
            print(msg)

            log_event(logger, "progress", {
                "gen": gen,
                "total_tested": summary["total_tested"],
                "cells_filled": summary["cells_filled"],
                "max_depth": summary["max_depth"],
                "depth_distribution": summary["depth_distribution"],
                "top_kill_modes": dict(list(summary["top_kill_modes"].items())[:5]),
                "void_cells": len(archive.get_void_cells()),
                "elapsed_s": round(elapsed, 1),
                "recent_rate_hyp_s": round(recent_rate, 1),
                "overall_rate_hyp_s": round(summary["total_tested"] / elapsed, 1) if elapsed > 0 else 0,
                "executor_stats": executor.stats(),
                "shadow": shadow.summary(),
            })

            last_checkpoint_time = time.time()
            last_checkpoint_tested = summary["total_tested"]

        # Periodic checkpoint save
        if gen > 0 and gen % checkpoint_interval == 0:
            ckpt_path = RESULTS_DIR / f"checkpoint_{run_id}_gen{gen}.json"
            archive.save(ckpt_path)
            shadow_path = RESULTS_DIR / f"shadow_{run_id}_gen{gen}.json"
            shadow.save(shadow_path)
            log_event(logger, "checkpoint_saved", {
                "gen": gen,
                "path": str(ckpt_path),
                "shadow_path": str(shadow_path),
                "cells": len(archive.grid),
            })
            print(f"  ** Checkpoint saved: {ckpt_path}")

    # Final report
    elapsed = time.time() - start_time
    summary = archive.summary()
    ex_stats = executor.stats()

    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    print(f"  Run ID: {run_id}")
    print(f"  Time: {elapsed:.0f}s ({elapsed/60:.1f} min, {elapsed/3600:.2f} hr)")
    print(f"  Generations: {n_generations}")
    print(f"  Total tested: {summary['total_tested']}")
    print(f"  Cells filled: {summary['cells_filled']}")
    print(f"  Max survival depth: {summary['max_depth']}")
    print(f"  Depth distribution: {summary['depth_distribution']}")
    print(f"  Top kill modes: {summary['top_kill_modes']}")
    print(f"  Void cells remaining: {len(archive.get_void_cells())}")
    print(f"  Hypotheses/second: {summary['total_tested']/elapsed:.1f}")
    print(f"  Prefiltered (taxonomy): {ex_stats['prefiltered_taxonomy']}")
    print(f"  Prefiltered (megethos): {ex_stats['prefiltered_megethos']}")

    # Shadow archive summary
    shadow_summary = shadow.summary()
    print(f"\n  SHADOW ARCHIVE (negative space):")
    print(f"    Unique cells explored: {shadow_summary['unique_cells_explored']}")
    print(f"    Domain pairs explored: {shadow_summary['domain_pairs_explored']}")
    print(f"    Confirmed dead zones: {shadow_summary['confirmed_dead_zones']}")
    print(f"    Gradient zones: {shadow_summary['gradient_zones']}")
    if shadow_summary["top_gradient_zones"]:
        print(f"    Top gradients:")
        for gz in shadow_summary["top_gradient_zones"][:3]:
            cell = gz["cell"]
            print(f"      {cell[0][:12]}×{cell[1][:12]} {cell[2][:12]}×{cell[3][:12]} {cell[4]} | "
                  f"score={gz['score']:.3f} depth={gz['best_depth']} n={gz['n_tested']}")

    dead_zones = shadow.get_dead_zones(min_tests=5)
    if dead_zones:
        print(f"    Top dead zones (tested 5+, depth<=1):")
        for key, cell in dead_zones[:5]:
            print(f"      {key[0][:12]}×{key[1][:12]} {key[2][:12]}×{key[3][:12]} {key[4]} | "
                  f"n={cell.n_tested} kill={cell.dominant_kill}")

    # Top survivors
    if archive.grid:
        print(f"\n  TOP SURVIVORS:")
        top = sorted(archive.grid.values(), key=lambda h: -h.survival_depth)[:10]
        for h in top:
            print(f"    depth={h.survival_depth} z={h.fitness:+.1f} | "
                  f"{h.domain_a[:12]:12s} × {h.domain_b[:12]:12s} | "
                  f"{h.feature_a[:15]:15s} × {h.feature_b[:15]:15s} | "
                  f"{h.coupling}")

    # Save final archive, shadow archive, and full results log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = RESULTS_DIR / f"archive_{timestamp}.json"
    archive.save(archive_path)

    shadow_path = RESULTS_DIR / f"shadow_{timestamp}.json"
    shadow.save(shadow_path)

    results_path = RESULTS_DIR / f"run_{timestamp}.jsonl"
    with open(results_path, "w") as f:
        for r in all_results:
            f.write(json.dumps(r, default=str) + "\n")

    log_event(logger, "run_complete", {
        "run_id": run_id,
        "elapsed_s": round(elapsed, 1),
        "elapsed_hr": round(elapsed / 3600, 2),
        "total_tested": summary["total_tested"],
        "cells_filled": summary["cells_filled"],
        "max_depth": summary["max_depth"],
        "depth_distribution": summary["depth_distribution"],
        "top_kill_modes": summary["top_kill_modes"],
        "void_cells": len(archive.get_void_cells()),
        "overall_rate_hyp_s": round(summary["total_tested"] / elapsed, 1),
        "executor_stats": ex_stats,
        "shadow_summary": shadow_summary,
        "archive_path": str(archive_path),
        "shadow_path": str(shadow_path),
        "results_path": str(results_path),
    })

    print(f"\n  Archive: {archive_path}")
    print(f"  Shadow:  {shadow_path}")
    print(f"  Results: {results_path}")
    print(f"  Log:     {log_path}")

    return archive, all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ergon Autonomous Explorer (tensor-native)")
    parser.add_argument("--generations", type=int, default=10, help="Number of generations")
    parser.add_argument("--per-gen", type=int, default=20, help="Hypotheses per generation")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--log-interval", type=int, default=5, help="Log every N generations")
    parser.add_argument("--checkpoint-interval", type=int, default=500, help="Save checkpoint every N generations")
    args = parser.parse_args()

    run_explorer(args.generations, args.per_gen, args.seed, args.log_interval, args.checkpoint_interval)
