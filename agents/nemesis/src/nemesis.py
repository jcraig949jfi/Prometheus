#!/usr/bin/env python3
"""Nemesis — Adversarial Co-Evolution Engine.

"Are our evaluators measuring reasoning, or have they learned to pass tests?"

Nemesis generates adversarial tasks using metamorphic relations, organizes them
in a MAP-Elites quality-diversity grid, finds minimal failing cases, and produces
failure reports + Coeus feedback.

Runs continuously by default. Pure algorithmic — no API calls, no neural models.

Usage:
    python agents/nemesis/src/nemesis.py              # continuous
    python agents/nemesis/src/nemesis.py --runonce     # single cycle
    python agents/nemesis/src/nemesis.py --target ibai_v2 --n 50
"""

import argparse
import json
import logging
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

NEMESIS_ROOT = Path(__file__).resolve().parent.parent
GRID_DIR = NEMESIS_ROOT / "grid"
REPORTS_DIR = NEMESIS_ROOT / "reports"
ADVERSARIAL_DIR = NEMESIS_ROOT / "adversarial"
HEPHAESTUS_ROOT = NEMESIS_ROOT.parent / "hephaestus"
FORGE_DIR = HEPHAESTUS_ROOT / "forge"

# Logging
LOG_PATH = NEMESIS_ROOT / "nemesis.log"
logger = logging.getLogger("nemesis")
logger.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_sh = logging.StreamHandler(sys.stdout)
_sh.setFormatter(_fmt)
logger.addHandler(_sh)
_fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
_fh.setFormatter(_fmt)
logger.addHandler(_fh)

# Import Nemesis modules
from evaluator import load_all_tools, evaluate_task
from map_elites import MAPElitesGrid, AdversarialTask, GRID_SIZE
from metamorphic import (
    METAMORPHIC_RELATIONS, compose_mrs, random_mr_chain, targeted_mr_chain,
)
from reporter import generate_report, write_adversarial_results
from shrink import shrink
from validators import validate_task

# Seed traps from Hephaestus test harness
sys.path.insert(0, str(HEPHAESTUS_ROOT / "src"))
try:
    from test_harness import TRAPS as SEED_TRAPS
except ImportError:
    SEED_TRAPS = []
    logger.warning("Could not load seed traps from Hephaestus")

try:
    from trap_generator import generate_trap_battery
    HAS_TRAP_GEN = True
except ImportError:
    HAS_TRAP_GEN = False


# ---------------------------------------------------------------------------
# Task generation
# ---------------------------------------------------------------------------

def _generate_from_seeds(rng: random.Random, n: int = 50) -> list[AdversarialTask]:
    """Generate adversarial tasks by applying MR chains to seed traps."""
    tasks = []

    # Use both static traps and generated traps as seeds
    seeds = list(SEED_TRAPS)
    if HAS_TRAP_GEN:
        seeds.extend(generate_trap_battery(n_per_category=3, seed=rng.randint(0, 99999)))

    for _ in range(n):
        seed = rng.choice(seeds)
        chain = random_mr_chain(rng, max_length=4)
        result = compose_mrs(
            seed["prompt"], seed["candidates"], seed["correct"],
            chain, rng,
            base_complexity=1, base_obfuscation=1,
        )
        if result is None:
            continue
        prompt, candidates, correct, complexity, obfuscation, applied_chain = result
        task = AdversarialTask(
            prompt=prompt, candidates=candidates, correct=correct,
            category=applied_chain[0] if applied_chain else "unknown",
            mr_chain=applied_chain,
            complexity=complexity, obfuscation=obfuscation,
            source_trap=seed.get("prompt", "")[:50],
        )
        tasks.append(task)

    return tasks


def _generate_targeted(rng: random.Random, grid: MAPElitesGrid,
                       n: int = 30) -> list[AdversarialTask]:
    """Generate tasks targeting empty cells in the grid."""
    tasks = []
    empty = grid.empty_cells()
    if not empty:
        return tasks

    seeds = list(SEED_TRAPS)
    if HAS_TRAP_GEN:
        seeds.extend(generate_trap_battery(n_per_category=2, seed=rng.randint(0, 99999)))

    for _ in range(n):
        target_row, target_col = rng.choice(empty)
        target_complexity = target_row + 1
        target_obfuscation = target_col + 1

        chain = targeted_mr_chain(target_complexity, target_obfuscation, rng)
        seed = rng.choice(seeds)
        result = compose_mrs(
            seed["prompt"], seed["candidates"], seed["correct"],
            chain, rng,
            base_complexity=1, base_obfuscation=1,
        )
        if result is None:
            continue
        prompt, candidates, correct, complexity, obfuscation, applied_chain = result
        task = AdversarialTask(
            prompt=prompt, candidates=candidates, correct=correct,
            category=applied_chain[0] if applied_chain else "targeted",
            mr_chain=applied_chain,
            complexity=complexity, obfuscation=obfuscation,
            source_trap=seed.get("prompt", "")[:50],
        )
        tasks.append(task)

    return tasks


# ---------------------------------------------------------------------------
# Main cycle
# ---------------------------------------------------------------------------

def _generate_boundary(rng: random.Random, grid: MAPElitesGrid,
                       tools: dict, n: int = 20) -> list[AdversarialTask]:
    """Generate tasks targeting each tool's decision boundary using difficulty model."""
    tasks = []
    seeds = list(SEED_TRAPS)
    if HAS_TRAP_GEN:
        seeds.extend(generate_trap_battery(n_per_category=2, seed=rng.randint(0, 99999)))

    # For each weak tool, generate tasks using its boundary MRs
    weak = grid.difficulty_model.weakest_tools(n=5)
    for tool_name, _ in weak:
        boundary_mrs = grid.difficulty_model.boundary_mrs(tool_name, n=3)
        if not boundary_mrs:
            continue
        for _ in range(n // max(len(weak), 1)):
            seed = rng.choice(seeds)
            # Build chain from boundary MRs + some random
            chain = list(boundary_mrs[:2])
            chain.extend(random_mr_chain(rng, max_length=2))
            result = compose_mrs(
                seed["prompt"], seed["candidates"], seed["correct"],
                chain, rng, base_complexity=1, base_obfuscation=1,
            )
            if result is None:
                continue
            prompt, candidates, correct, complexity, obfuscation, applied_chain = result
            task = AdversarialTask(
                prompt=prompt, candidates=candidates, correct=correct,
                category="boundary_" + tool_name[:20],
                mr_chain=applied_chain,
                complexity=complexity, obfuscation=obfuscation,
                source_trap=seed.get("prompt", "")[:50],
            )
            tasks.append(task)
    return tasks


def run_cycle(grid: MAPElitesGrid, tools: dict, rng: random.Random,
              n_random: int = 50, n_targeted: int = 30) -> dict:
    """Run one Nemesis cycle: generate, validate, evaluate, place, shrink.

    Returns cycle stats dict.
    """
    cycle_start = time.time()

    # 1. Generate candidate tasks (three strategies)
    logger.info("Generating %d random + %d targeted + boundary tasks...", n_random, n_targeted)
    candidates = _generate_from_seeds(rng, n_random)
    candidates.extend(_generate_targeted(rng, grid, n_targeted))
    candidates.extend(_generate_boundary(rng, grid, tools, n=20))
    logger.info("Generated %d candidate tasks", len(candidates))

    # 2. Validate (ground truth cross-check)
    validated = []
    rejected = 0
    for task in candidates:
        valid, reason = validate_task(task.prompt, task.candidates, task.correct)
        if valid:
            validated.append(task)
        else:
            rejected += 1
    logger.info("Validated: %d, rejected: %d", len(validated), rejected)

    # 3. Evaluate all tools against validated tasks
    logger.info("Evaluating %d tasks against %d tools...", len(validated), len(tools))
    for task in validated:
        evaluate_task(task, tools)

    # 4. Novelty check + grid placement
    placed = 0
    for task in validated:
        if task.disagreement < 0.01 and not task.blind_spot:
            continue  # uninformative (all tools agree and are correct)
        if grid.novelty_check(task):
            if grid.place(task):
                placed += 1

    logger.info("Placed %d tasks in grid (now %d/%d filled)",
                placed, grid.n_filled, GRID_SIZE ** 2)

    # 5. Update per-tool difficulty model
    for task in validated:
        for tool_name, result in task.tool_results.items():
            for mr_name in task.mr_chain:
                grid.difficulty_model.update(
                    tool_name, mr_name, result.get("correct", False)
                )

    # 6. Shrink new failures to minimal cases + track lineage
    n_shrunk = 0
    n_lineage = 0
    for task in validated:
        if task.tools_broken == 0:
            continue

        # Track lineage: if this task's source_trap was itself an adversarial task
        # that broke tools, increment lineage depth
        for existing in grid.tasks:
            if (existing.prompt and task.source_trap
                    and existing.prompt[:30] in task.source_trap):
                task.parent_id = existing.prompt[:50]
                task.lineage_depth = existing.lineage_depth + 1
                if task.lineage_depth > 1:
                    n_lineage += 1
                break

        # Find the first tool that failed and shrink
        for tool_name, result in task.tool_results.items():
            if not result.get("correct", True):
                tool = tools.get(tool_name)
                if tool is None:
                    continue

                def tool_fn(p, c, _t=tool):
                    ranked = _t.evaluate(p, c)
                    return ranked[0]["candidate"] if ranked else None

                try:
                    min_prompt, min_cands, _, simplifications = shrink(
                        task.prompt, task.candidates, task.correct, tool_fn
                    )
                    if simplifications:
                        n_shrunk += 1
                        task.prompt = min_prompt
                        task.candidates = min_cands
                except Exception:
                    pass
                break

    logger.info("Shrunk %d tasks to minimal failing cases, %d with lineage depth > 1",
                n_shrunk, n_lineage)

    cycle_time = time.time() - cycle_start

    stats = {
        "generated": len(candidates),
        "validated": len(validated),
        "rejected": rejected,
        "placed": placed,
        "shrunk": n_shrunk,
        "grid_filled": grid.n_filled,
        "grid_empty": grid.n_empty,
        "blind_spots": len(grid.blind_spots()),
        "cycle_seconds": round(cycle_time, 1),
    }
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Nemesis — Adversarial Co-Evolution Engine"
    )
    parser.add_argument("--runonce", action="store_true",
                        help="Run one cycle and exit (default: continuous)")
    parser.add_argument("--poll-interval", type=float, default=120,
                        help="Seconds between cycles in continuous mode")
    parser.add_argument("--n-random", type=int, default=50,
                        help="Random adversarial tasks per cycle")
    parser.add_argument("--n-targeted", type=int, default=30,
                        help="Targeted (empty-cell) tasks per cycle")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    # Setup directories
    GRID_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ADVERSARIAL_DIR.mkdir(parents=True, exist_ok=True)

    # Load or create grid
    grid = MAPElitesGrid()
    grid_path = GRID_DIR / "grid.json"
    if grid_path.exists():
        grid.load(grid_path)
        logger.info("Loaded existing grid: %d/%d filled", grid.n_filled, GRID_SIZE ** 2)
    else:
        logger.info("Starting with empty grid")

    # Graceful shutdown
    shutdown = [False]

    def handle_signal(sig, frame):
        shutdown[0] = True
        logger.info("Shutdown requested, finishing current cycle...")

    signal.signal(signal.SIGINT, handle_signal)

    logger.info("=" * 60)
    logger.info("NEMESIS — Adversarial Co-Evolution Engine")
    logger.info("Mode: %s", "runonce" if args.runonce else "continuous")
    logger.info("=" * 60)

    cycle = 0
    while not shutdown[0]:
        cycle += 1
        logger.info("--- Cycle %d ---", cycle)

        # Reload tools each cycle (picks up newly forged tools)
        tools = load_all_tools(FORGE_DIR)
        if not tools:
            logger.warning("No tools found in %s", FORGE_DIR)
            if args.runonce:
                break
            logger.info("Waiting %ds for tools...", int(args.poll_interval))
            time.sleep(args.poll_interval)
            continue

        # Run cycle
        stats = run_cycle(grid, tools, rng,
                          n_random=args.n_random,
                          n_targeted=args.n_targeted)

        # Save grid
        grid.save(grid_path)

        # Generate report
        report = generate_report(grid, tools, REPORTS_DIR)

        # Write adversarial results for Coeus
        write_adversarial_results(
            grid, ADVERSARIAL_DIR / "adversarial_results.jsonl"
        )

        # Summary
        logger.info("Cycle %d complete: generated=%d placed=%d shrunk=%d "
                     "grid=%d/%d blind_spots=%d (%.1fs)",
                     cycle, stats["generated"], stats["placed"], stats["shrunk"],
                     stats["grid_filled"], GRID_SIZE ** 2,
                     stats["blind_spots"], stats["cycle_seconds"])

        if args.runonce:
            break

        if not shutdown[0]:
            logger.info("Sleeping %ds before next cycle...", int(args.poll_interval))
            slept = 0.0
            while slept < args.poll_interval and not shutdown[0]:
                time.sleep(min(5.0, args.poll_interval - slept))
                slept += 5.0

    # Final save
    grid.save(grid_path)
    logger.info("=" * 60)
    logger.info("NEMESIS SHUTDOWN")
    logger.info("  Cycles: %d", cycle)
    logger.info("  Grid: %d/%d filled", grid.n_filled, GRID_SIZE ** 2)
    logger.info("  Blind spots: %d", len(grid.blind_spots()))
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
