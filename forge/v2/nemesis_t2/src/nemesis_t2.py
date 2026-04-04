"""
Tier 2 Nemesis — Adversarial co-evolution for T2 tools.

Loads forged T2 tools, generates adversarial cases using metamorphic
relations over T2 trap seeds, evaluates tools, and maintains a MAP-Elites
grid. Feeds blind spots back to Hephaestus T2 via targeted forge requests.

Reuses T1 Nemesis support modules (metamorphic, evaluator, map_elites,
shrink, reporter) which are generic across tiers.

Usage:
    python nemesis_t2.py --poll-interval 120
    python nemesis_t2.py --runonce
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import signal
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SRC = Path(__file__).resolve().parent
_NEMESIS_T2 = _SRC.parent                 # forge/v2/nemesis_t2
_FORGE_V2 = _NEMESIS_T2.parent            # forge/v2
_FORGE = _FORGE_V2.parent                 # forge
_REPO = _FORGE.parent                     # F:\Prometheus

# T2 tool source
T2_FORGE_DIR = _FORGE_V2 / "hephaestus_t2" / "forge"

# T2 Nemesis output directories
GRID_DIR = _NEMESIS_T2 / "grid"
REPORTS_DIR = _NEMESIS_T2 / "reports"
ADVERSARIAL_DIR = _NEMESIS_T2 / "adversarial"
GRID_PATH = GRID_DIR / "grid_t2.json"

for _d in [GRID_DIR, REPORTS_DIR, ADVERSARIAL_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# Add T1 Nemesis modules to path (reuse generic support code)
sys.path.insert(0, str(_REPO / "agents" / "nemesis" / "src"))
sys.path.insert(0, str(_REPO / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_FORGE))
sys.path.insert(0, str(_FORGE / "tester_quarantine"))

from metamorphic import (
    compose_mrs,
    random_mr_chain,
    targeted_mr_chain,
    METAMORPHIC_RELATIONS,
)
from evaluator import load_tool, evaluate_task
from map_elites import MAPElitesGrid, AdversarialTask, GRID_SIZE
from shrink import shrink
from reporter import generate_report, write_targeted_forge_requests, write_adversarial_results
from trap_generator_t2 import generate_t2_battery

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nemesis_t2")

# ---------------------------------------------------------------------------
# Shutdown
# ---------------------------------------------------------------------------

_shutdown = [False]


def _signal_handler(sig, frame):
    logger.info("Shutdown requested — finishing current cycle...")
    _shutdown[0] = True


signal.signal(signal.SIGINT, _signal_handler)

# ---------------------------------------------------------------------------
# Tool loading (T2-specific paths)
# ---------------------------------------------------------------------------

def load_all_t2_tools() -> dict:
    """Load all forged T2 tools from the T2 forge directory."""
    tools = {}
    if not T2_FORGE_DIR.exists():
        return tools
    for py in sorted(T2_FORGE_DIR.glob("*.py")):
        if py.name.startswith("_"):
            continue
        try:
            tool = load_tool(py)
            tools[py.stem] = tool
            logger.debug("Loaded %s", py.stem)
        except Exception as e:
            logger.debug("Skip %s: %s", py.stem, e)
    logger.info("Loaded %d T2 tools from %s", len(tools), T2_FORGE_DIR)
    return tools


# ---------------------------------------------------------------------------
# Seed trap generation (T2 battery as seeds)
# ---------------------------------------------------------------------------

def generate_seed_traps(rng: random.Random, n_per_category: int = 3) -> list[dict]:
    """Generate T2 battery traps to use as adversarial seeds."""
    seed = rng.randint(0, 99999)
    return generate_t2_battery(n_per_category=n_per_category, seed=seed)


# ---------------------------------------------------------------------------
# Adversarial task generation (three strategies, same as T1)
# ---------------------------------------------------------------------------

def generate_from_seeds(
    rng: random.Random, n: int = 50,
) -> list[AdversarialTask]:
    """Strategy 1: Random MR chains on T2 trap seeds."""
    seeds = generate_seed_traps(rng)
    tasks = []

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
            prompt=prompt,
            candidates=candidates,
            correct=correct,
            category=seed.get("category", applied_chain[0] if applied_chain else "unknown"),
            mr_chain=applied_chain,
            complexity=complexity,
            obfuscation=obfuscation,
            source_trap=seed.get("prompt", "")[:50],
        )
        tasks.append(task)

    return tasks


def generate_targeted(
    rng: random.Random, grid: MAPElitesGrid, n: int = 30,
) -> list[AdversarialTask]:
    """Strategy 2: Target empty cells in the MAP-Elites grid."""
    empty = grid.empty_cells()
    if not empty:
        return []

    seeds = generate_seed_traps(rng)
    tasks = []

    for _ in range(n):
        target_row, target_col = rng.choice(empty)
        target_complexity = target_row + 1
        target_obfuscation = target_col + 1

        seed = rng.choice(seeds)
        chain = targeted_mr_chain(target_complexity, target_obfuscation, rng)
        result = compose_mrs(
            seed["prompt"], seed["candidates"], seed["correct"],
            chain, rng,
            base_complexity=1, base_obfuscation=1,
        )
        if result is None:
            continue

        prompt, candidates, correct, complexity, obfuscation, applied_chain = result
        task = AdversarialTask(
            prompt=prompt,
            candidates=candidates,
            correct=correct,
            category=seed.get("category", "targeted"),
            mr_chain=applied_chain,
            complexity=complexity,
            obfuscation=obfuscation,
            source_trap=seed.get("prompt", "")[:50],
        )
        tasks.append(task)

    return tasks


def generate_boundary(
    rng: random.Random, grid: MAPElitesGrid, tools: dict, n: int = 20,
) -> list[AdversarialTask]:
    """Strategy 3: Target decision boundaries of weakest tools."""
    weak = grid.difficulty_model.weakest_tools(n=5)
    if not weak:
        return []

    seeds = generate_seed_traps(rng)
    tasks = []

    for tool_name, _ in weak:
        boundary_mrs = grid.difficulty_model.boundary_mrs(tool_name, n=3)
        if not boundary_mrs:
            continue

        per_tool = max(1, n // len(weak))
        for _ in range(per_tool):
            seed = rng.choice(seeds)
            chain = list(boundary_mrs[:2])
            chain.extend(random_mr_chain(rng, max_length=2))

            result = compose_mrs(
                seed["prompt"], seed["candidates"], seed["correct"],
                chain, rng,
                base_complexity=1, base_obfuscation=1,
            )
            if result is None:
                continue

            prompt, candidates, correct, complexity, obfuscation, applied_chain = result
            task = AdversarialTask(
                prompt=prompt,
                candidates=candidates,
                correct=correct,
                category=seed.get("category", "boundary"),
                mr_chain=applied_chain,
                complexity=complexity,
                obfuscation=obfuscation,
                source_trap=seed.get("prompt", "")[:50],
            )
            tasks.append(task)

    return tasks


# ---------------------------------------------------------------------------
# Cycle
# ---------------------------------------------------------------------------

def run_cycle(
    grid: MAPElitesGrid,
    tools: dict,
    rng: random.Random,
    n_random: int = 50,
    n_targeted: int = 30,
    n_boundary: int = 20,
) -> dict:
    """Run one adversarial cycle. Returns cycle stats."""
    stats = {
        "generated": 0, "placed": 0, "blind_spots": 0,
        "shrunk": 0, "tools_evaluated": len(tools),
    }

    # Phase 1: Generate adversarial tasks
    tasks = []
    tasks.extend(generate_from_seeds(rng, n_random))
    tasks.extend(generate_targeted(rng, grid, n_targeted))
    if tools:
        tasks.extend(generate_boundary(rng, grid, tools, n_boundary))

    stats["generated"] = len(tasks)
    logger.info("Generated %d adversarial tasks (%d seed, %d targeted, %d boundary)",
                len(tasks), n_random, n_targeted, n_boundary)

    if not tasks or not tools:
        return stats

    # Phase 2: Evaluate all tools against each task
    for task in tasks:
        if _shutdown[0]:
            break
        try:
            evaluate_task(task, tools)
        except Exception as e:
            logger.debug("Eval error: %s", e)
            continue

        # Update difficulty model
        for tool_name, result in (task.tool_results or {}).items():
            for mr_name in (task.mr_chain or []):
                grid.difficulty_model.update(
                    tool_name, mr_name,
                    passed=result.get("correct", False),
                )

        if task.blind_spot:
            stats["blind_spots"] += 1

    # Phase 3: Lineage tracking
    existing_tasks = grid.tasks
    for task in tasks:
        for existing in existing_tasks:
            if (existing.prompt and task.source_trap
                    and existing.prompt[:30] in task.source_trap):
                task.parent_id = existing.prompt[:50]
                task.lineage_depth = existing.lineage_depth + 1
                break

    # Phase 4: Shrink failing cases
    for task in tasks:
        if _shutdown[0]:
            break
        if not hasattr(task, 'tools_broken') or task.tools_broken == 0:
            continue

        for tool_name, result in (task.tool_results or {}).items():
            if not result.get("correct", True):
                tool = tools.get(tool_name)
                if tool is None:
                    continue

                def tool_fn(p, c, _t=tool):
                    try:
                        ranked = _t.evaluate(p, c)
                        return ranked[0]["candidate"] if ranked else None
                    except Exception:
                        return None

                try:
                    min_prompt, min_cands, _, simplifications = shrink(
                        task.prompt, task.candidates, task.correct, tool_fn,
                    )
                    if simplifications:
                        stats["shrunk"] += 1
                        task.prompt = min_prompt
                        task.candidates = min_cands
                except Exception as e:
                    logger.debug("Shrink failed: %s", e)
                break  # One shrink per task

    # Phase 5: Place in grid (novelty + fitness check)
    for task in tasks:
        if grid.novelty_check(task):
            if grid.place(task):
                stats["placed"] += 1

    grid._generation += 1
    return stats


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Tier 2 Nemesis — Adversarial co-evolution",
    )
    parser.add_argument("--poll-interval", type=float, default=120,
                        help="Seconds between cycles (default: 120)")
    parser.add_argument("--n-random", type=int, default=50,
                        help="Random adversarial tasks per cycle (default: 50)")
    parser.add_argument("--n-targeted", type=int, default=30,
                        help="Targeted (empty cell) tasks per cycle (default: 30)")
    parser.add_argument("--n-boundary", type=int, default=20,
                        help="Boundary-targeting tasks per cycle (default: 20)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed")
    parser.add_argument("--runonce", action="store_true",
                        help="Run one cycle and exit")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else int(time.time())
    rng = random.Random(seed)

    # Load or create grid
    grid = MAPElitesGrid()
    if GRID_PATH.exists():
        try:
            grid.load(GRID_PATH)
            logger.info("Loaded grid from %s (%d/%d cells filled)",
                        GRID_PATH.name, grid.n_filled, GRID_SIZE * GRID_SIZE)
        except Exception as e:
            logger.warning("Failed to load grid: %s — starting fresh", e)
            grid = MAPElitesGrid()
    else:
        logger.info("No existing grid — starting fresh")

    logger.info("=" * 60)
    logger.info("  Tier 2 Nemesis — Adversarial Co-Evolution")
    logger.info("=" * 60)
    logger.info("  Grid: %d/%d cells filled", grid.n_filled, GRID_SIZE * GRID_SIZE)
    logger.info("  Tool source: %s", T2_FORGE_DIR)
    logger.info("  Poll interval: %.0fs", args.poll_interval)
    logger.info("  Tasks/cycle: %d random + %d targeted + %d boundary",
                args.n_random, args.n_targeted, args.n_boundary)
    logger.info("=" * 60)

    cycle = 0

    while not _shutdown[0]:
        cycle += 1
        logger.info("\n--- Cycle %d ---", cycle)

        # Load T2 tools (re-scan each cycle for new tools)
        tools = load_all_t2_tools()
        if not tools:
            logger.warning("No T2 tools found in %s", T2_FORGE_DIR)
            if args.runonce:
                break
            logger.info("Waiting %.0fs for tools...", args.poll_interval)
            slept = 0.0
            while slept < args.poll_interval and not _shutdown[0]:
                time.sleep(min(5.0, args.poll_interval - slept))
                slept += 5.0
            continue

        # Run adversarial cycle
        stats = run_cycle(
            grid, tools, rng,
            n_random=args.n_random,
            n_targeted=args.n_targeted,
            n_boundary=args.n_boundary,
        )

        logger.info(
            "Cycle %d: %d generated, %d placed, %d blind spots, %d shrunk",
            cycle, stats["generated"], stats["placed"],
            stats["blind_spots"], stats["shrunk"],
        )
        logger.info("Grid: %d/%d cells filled", grid.n_filled, GRID_SIZE * GRID_SIZE)

        # Save grid
        grid.save(GRID_PATH)

        # Write outputs
        try:
            report_text = generate_report(grid, tools, REPORTS_DIR)
            logger.info("Report written to %s", REPORTS_DIR)
        except Exception as e:
            logger.warning("Report generation failed: %s", e)

        try:
            write_adversarial_results(grid, ADVERSARIAL_DIR / "adversarial_results_t2.jsonl")
        except Exception as e:
            logger.warning("Adversarial results write failed: %s", e)

        try:
            write_targeted_forge_requests(grid, ADVERSARIAL_DIR / "targeted_forge_requests_t2.jsonl")
        except Exception as e:
            logger.warning("Forge requests write failed: %s", e)

        if args.runonce:
            break

        # Sleep with interruptible chunks
        logger.info("Sleeping %.0fs...", args.poll_interval)
        slept = 0.0
        while slept < args.poll_interval and not _shutdown[0]:
            chunk = min(5.0, args.poll_interval - slept)
            time.sleep(chunk)
            slept += chunk

    logger.info("\n" + "=" * 60)
    logger.info("  Nemesis T2 shutdown.")
    logger.info("  Final grid: %d/%d cells, %d blind spots",
                grid.n_filled, GRID_SIZE * GRID_SIZE, len(grid.blind_spots()))
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
