"""Diversity Forge — Quality-Diversity code generation for reasoning tools.

A separate forge pipeline that runs alongside the main Hephaestus forge.
Uses MAP-Elites (via pyribs) to maintain a coverage map of behaviorally
diverse tools instead of optimizing a single accuracy score.

Key differences from main forge:
- Mixed-format problems (not just text parsing) to force non-regex mechanisms
- Behavioral descriptors (output profile, mechanism type) instead of source NCD
- MAP-Elites archive instead of accuracy gate
- Lexicase-style per-problem evaluation instead of aggregate scoring
- Island model with different prompt strategies per island

Usage:
    python diversity_forge.py --generate --n 50     # Generate diverse tools
    python diversity_forge.py --evaluate             # Score archive against battery
    python diversity_forge.py --map                  # Visualize coverage map
    python diversity_forge.py --loop --n 20          # Continuous: generate + evaluate
"""

import argparse
import json
import logging
import os
import sys
import time
import random
import hashlib
from datetime import datetime
from pathlib import Path

import numpy as np
from ribs.archives import GridArchive
from ribs.emitters import EvolutionStrategyEmitter
from ribs.schedulers import Scheduler

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from code_extractor import extract_code
from hephaestus import (
    _inject_missing_imports, _sanitize_unicode, _fix_common_errors,
    _compute_novelty, _call_with_hard_timeout, safe_filename,
    FORGE_DIR, SCRAP_DIR, HEPHAESTUS_ROOT,
)
from validator import validate
from test_harness import load_tool_from_code

logging.basicConfig(level=logging.INFO, format="%(asctime)s [DFORGE] %(message)s")
log = logging.getLogger("diversity_forge")

DFORGE_DIR = HEPHAESTUS_ROOT / "diversity_forge"
ARCHIVE_PATH = DFORGE_DIR / "archive.json"

# Auto-load .env
_ENV = HEPHAESTUS_ROOT / ".env"
if _ENV.exists():
    for line in _ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# ---------------------------------------------------------------------------
# Mixed-format problem battery — forces non-regex mechanisms
# ---------------------------------------------------------------------------

PUZZLE_BATTERY = [
    # --- Constraint satisfaction ---
    {
        "type": "constraint",
        "prompt": "Fill a 3x3 grid so each row and column contains exactly {1,2,3}. "
                  "Given: row0=[_,3,_], row1=[_,_,1], row2=[2,_,_]. What is row0[0]?",
        "candidates": ["1", "2", "3"],
        "correct": "1",
        "category": "constraint_satisfaction",
    },
    {
        "type": "constraint",
        "prompt": "Three people (A,B,C) sit in a row. A is not next to B. C is in the middle. "
                  "Who sits on the left?",
        "candidates": ["A", "B", "C"],
        "correct": "B",
        "category": "constraint_satisfaction",
    },
    {
        "type": "constraint",
        "prompt": "Assign colors R,G,B to nodes 1-4. Edges: 1-2, 2-3, 3-4, 1-4. "
                  "Adjacent nodes must differ. Node 1=R, Node 3=R. What color is Node 2?",
        "candidates": ["R", "G", "B", "Impossible"],
        "correct": "G",
        "category": "graph_coloring",
    },
    # --- State tracking ---
    {
        "type": "state",
        "prompt": "Start with x=0. Step 1: x=x+5. Step 2: x=x*2. Step 3: x=x-3. What is x?",
        "candidates": ["7", "12", "10", "8"],
        "correct": "7",
        "category": "state_tracking",
    },
    {
        "type": "state",
        "prompt": "A stack starts empty. Push 3, Push 7, Pop, Push 1, Push 4, Pop. "
                  "What is on top of the stack?",
        "candidates": ["1", "3", "4", "7"],
        "correct": "1",
        "category": "state_tracking",
    },
    {
        "type": "state",
        "prompt": "Register A=10, B=5. Step 1: A=A-B. Step 2: B=B+A. Step 3: A=A*2. "
                  "What is B?",
        "candidates": ["10", "15", "5", "20"],
        "correct": "10",
        "category": "register_machine",
    },
    # --- Sequence / pattern prediction ---
    {
        "type": "sequence",
        "prompt": "Sequence: 2, 6, 18, 54, ?. What comes next?",
        "candidates": ["108", "162", "72", "216"],
        "correct": "162",
        "category": "sequence_prediction",
    },
    {
        "type": "sequence",
        "prompt": "Sequence: 1, 1, 2, 3, 5, 8, ?. What comes next?",
        "candidates": ["11", "13", "15", "10"],
        "correct": "13",
        "category": "sequence_prediction",
    },
    {
        "type": "sequence",
        "prompt": "Pattern: AAB, AAB, AAB. Which continues the pattern?",
        "candidates": ["AAB", "ABA", "BAA", "ABB"],
        "correct": "AAB",
        "category": "pattern_continuation",
    },
    # --- Graph / path problems ---
    {
        "type": "graph",
        "prompt": "Cities: A-B(3), A-C(1), B-D(1), C-D(5), C-B(1). "
                  "Shortest path from A to D? Give the distance.",
        "candidates": ["3", "4", "6", "5"],
        "correct": "3",
        "category": "shortest_path",
    },
    {
        "type": "graph",
        "prompt": "Graph edges: A->B, B->C, C->A, B->D. "
                  "Is there a path from D to A?",
        "candidates": ["Yes", "No"],
        "correct": "No",
        "category": "reachability",
    },
    # --- Mathematical computation ---
    {
        "type": "math",
        "prompt": "What is 17 mod 5?",
        "candidates": ["2", "3", "4", "1"],
        "correct": "2",
        "category": "modular_arithmetic",
    },
    {
        "type": "math",
        "prompt": "If f(x) = 2x + 3, what is f(f(2))?",
        "candidates": ["17", "14", "11", "10"],
        "correct": "17",
        "category": "function_composition",
    },
    {
        "type": "math",
        "prompt": "How many ways can you arrange 3 books on a shelf?",
        "candidates": ["3", "6", "9", "27"],
        "correct": "6",
        "category": "combinatorics",
    },
    # --- Planning ---
    {
        "type": "planning",
        "prompt": "You have a wolf, a goat, and a cabbage. You must cross a river in a boat "
                  "that holds you + one item. Wolf eats goat if alone. Goat eats cabbage if alone. "
                  "What do you take first?",
        "candidates": ["Wolf", "Goat", "Cabbage"],
        "correct": "Goat",
        "category": "planning",
    },
    {
        "type": "planning",
        "prompt": "Tower of Hanoi: 2 disks on peg A, move to peg C. "
                  "Minimum number of moves?",
        "candidates": ["2", "3", "4", "5"],
        "correct": "3",
        "category": "planning",
    },
    # --- Adversarial / trick ---
    {
        "type": "adversarial",
        "prompt": "I have 3 apples. I eat 2. Then I buy 5 more. How many do I have?",
        "candidates": ["6", "3", "5", "8"],
        "correct": "6",
        "category": "arithmetic_chain",
    },
    {
        "type": "adversarial",
        "prompt": "A train leaves at 2pm going 60mph. Another leaves the same station "
                  "at 3pm going 80mph same direction. When does the second catch up?",
        "candidates": ["5pm", "6pm", "7pm", "Never"],
        "correct": "6pm",
        "category": "rate_problem",
    },
]

# Also include some standard text reasoning (the existing battery covers these)
TEXT_BATTERY = [
    {"type": "text", "prompt": "Is 9.11 larger than 9.9?",
     "candidates": ["Yes", "No"], "correct": "No", "category": "numeric_comparison"},
    {"type": "text", "prompt": "A bat and ball cost $1.10. Bat costs $1 more. Ball costs?",
     "candidates": ["$0.10", "$0.05"], "correct": "$0.05", "category": "arithmetic_trap"},
    {"type": "text", "prompt": "If Alice is taller than Bob, and Bob is taller than Carol, who is tallest?",
     "candidates": ["Carol", "Alice", "Bob"], "correct": "Alice", "category": "transitivity"},
    {"type": "text", "prompt": "Coin flipped heads 5 times. Next flip probability of heads?",
     "candidates": ["Higher than 50%", "50%"], "correct": "50%", "category": "independence"},
    {"type": "text", "prompt": "If it is raining, the ground is wet. The ground is not wet. Is it raining?",
     "candidates": ["Yes", "No", "Maybe"], "correct": "No", "category": "modus_tollens"},
]

FULL_BATTERY = PUZZLE_BATTERY + TEXT_BATTERY

# ---------------------------------------------------------------------------
# Prompt templates for diversity — one per "island"
# ---------------------------------------------------------------------------

ISLAND_PROMPTS = {
    "solver": """\
Write a Python class called ReasoningTool that SOLVES problems by computation.

It must handle:
- Arithmetic and algebra (actually compute, don't pattern match)
- Constraint satisfaction (backtracking, arc consistency)
- State tracking across multiple steps
- Sequence/pattern prediction

The class must have:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
  Returns sorted list of {{"candidate": str, "score": float, "reasoning": str}}
- confidence(self, prompt: str, answer: str) -> float

Requirements:
- Use ONLY numpy and Python stdlib
- Do NOT use zlib/NCD compression distance
- Do NOT rely on regex keyword matching as the primary scoring method
- Actually PARSE numbers and COMPUTE answers
- Under 200 lines
""",

    "searcher": """\
Write a Python class called ReasoningTool that uses SEARCH to evaluate answers.

Implement one of these search algorithms:
- Backtracking constraint solver
- BFS/DFS over a state graph built from the prompt
- A* with a heuristic derived from prompt structure
- Branch-and-bound over candidate orderings

The class must have:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float

Requirements:
- Use ONLY numpy and Python stdlib
- The search must actually EXPLORE a space, not just score candidates
- Must handle dead ends gracefully (backtrack, not crash)
- Under 200 lines
""",

    "reasoner": """\
Write a Python class called ReasoningTool that builds an INFERENCE ENGINE.

The tool should:
- Parse the prompt into a set of logical propositions and rules
- Build an inference graph (forward or backward chaining)
- Derive which candidate is supported by the most complete chain
- Track which propositions are assumed vs derived

The class must have:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float

Requirements:
- Use ONLY numpy and Python stdlib
- Must implement actual inference (not keyword matching)
- Must distinguish between "derived from evidence" and "assumed"
- Under 200 lines
""",

    "calculator": """\
Write a Python class called ReasoningTool that is a COMPUTATIONAL ENGINE.

It must:
- Extract ALL numbers and mathematical operations from the prompt
- Build an expression tree or computation graph
- Actually evaluate the math (don't pattern-match known problems)
- Handle: basic arithmetic, modular arithmetic, function composition,
  combinatorics (permutations/combinations), rate/distance/time

The class must have:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float

Requirements:
- Use ONLY numpy and Python stdlib
- Must COMPUTE answers, not look them up
- Return confidence based on whether computation succeeded
- Under 200 lines
""",

    "planner": """\
Write a Python class called ReasoningTool that uses PLANNING to solve problems.

The tool should:
- Parse the prompt to identify: initial state, goal state, available actions, constraints
- Use forward search or means-ends analysis to find action sequences
- Score candidates based on whether they match achievable goal states
- Handle ordering constraints and preconditions

The class must have:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float

Requirements:
- Use ONLY numpy and Python stdlib
- Must model state transitions explicitly
- Must handle constraints (things that can't coexist, ordering requirements)
- Under 200 lines
""",
}

# ---------------------------------------------------------------------------
# Models (fallback chain, fastest first)
# ---------------------------------------------------------------------------

MODELS = [
    # GitHub Models first (free, separate endpoint, no NVIDIA contention)
    {"id": "gpt-4o-mini", "timeout": 90,
     "base_url": "https://models.inference.ai.azure.com",
     "api_key_env": "GITHUB_TOKEN"},
    # NVIDIA fallback
    {"id": "meta/llama-3.3-70b-instruct", "timeout": 60},
    {"id": "meta/llama-4-maverick-17b-128e-instruct", "timeout": 60},
    {"id": "qwen/qwen3-next-80b-a3b-instruct", "timeout": 90},
    {"id": "qwen/qwen3.5-397b-a17b", "timeout": 120},
]


def _make_client(timeout=120, base_url=None, api_key_env="NVIDIA_API_KEY"):
    key = os.environ.get(api_key_env)
    if not key:
        return None
    return OpenAI(
        base_url=base_url or "https://integrate.api.nvidia.com/v1",
        api_key=key, timeout=float(timeout),
    )


def _call_with_fallback(prompt):
    """Try models in order, fall back on failure."""
    for m in MODELS:
        client = _make_client(
            timeout=m["timeout"],
            base_url=m.get("base_url"),
            api_key_env=m.get("api_key_env", "NVIDIA_API_KEY"),
        )
        if client is None:
            continue
        try:
            content = _call_with_hard_timeout(client, m["id"], prompt,
                                              timeout_sec=300)
            return content, m["id"]
        except Exception as e:
            log.warning("  %s failed: %s", m["id"].split("/")[-1], str(e)[:60])
            continue
    return None, None


# ---------------------------------------------------------------------------
# Behavioral evaluation
# ---------------------------------------------------------------------------

def _run_with_timeout(fn, args, timeout_sec=5):
    """Run a function with a hard timeout. Returns result or None."""
    import threading
    result = [None]
    done = threading.Event()

    def _worker():
        try:
            result[0] = fn(*args)
        except Exception:
            pass
        finally:
            done.set()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    done.wait(timeout=timeout_sec)
    return result[0]


def evaluate_tool(tool, battery=None) -> dict:
    """Run a tool against the mixed battery. Return per-category results."""
    if battery is None:
        battery = FULL_BATTERY

    results = {}
    correct_total = 0
    total = 0
    category_correct = {}
    category_total = {}

    for problem in battery:
        cat = problem.get("category", "unknown")
        category_total[cat] = category_total.get(cat, 0) + 1
        total += 1

        # Hard 5s timeout per problem — tools that hang on eval() get skipped
        ranked = _run_with_timeout(
            tool.evaluate, (problem["prompt"], problem["candidates"]), timeout_sec=5
        )
        try:
            if ranked and ranked[0].get("candidate") == problem["correct"]:
                correct_total += 1
                category_correct[cat] = category_correct.get(cat, 0) + 1
        except Exception:
            pass

    # Behavioral descriptor: which problem TYPES does it solve?
    type_scores = {}
    for cat in category_total:
        type_scores[cat] = (category_correct.get(cat, 0) /
                            category_total[cat]) if category_total[cat] > 0 else 0.0

    return {
        "accuracy": correct_total / total if total > 0 else 0.0,
        "correct": correct_total,
        "total": total,
        "type_scores": type_scores,
        "category_correct": category_correct,
        "category_total": category_total,
    }


def compute_behavioral_descriptors(eval_result: dict) -> tuple:
    """Compute 2D behavioral descriptors for MAP-Elites archive.

    Descriptor 1: puzzle_ratio — fraction of correct answers on puzzle problems
                   (constraint, state, sequence, graph, math, planning)
    Descriptor 2: text_ratio — fraction of correct answers on text problems

    A tool that solves ONLY puzzles lands at (high, low).
    A tool that solves ONLY text lands at (low, high).
    A tool that solves both lands at (high, high) — the rare gem.
    """
    ts = eval_result.get("type_scores", {})

    puzzle_cats = ["constraint_satisfaction", "graph_coloring", "state_tracking",
                   "register_machine", "sequence_prediction", "pattern_continuation",
                   "shortest_path", "reachability", "modular_arithmetic",
                   "function_composition", "combinatorics", "planning",
                   "arithmetic_chain", "rate_problem"]
    text_cats = ["numeric_comparison", "arithmetic_trap", "transitivity",
                 "independence", "modus_tollens"]

    puzzle_scores = [ts.get(c, 0.0) for c in puzzle_cats if c in ts]
    text_scores = [ts.get(c, 0.0) for c in text_cats if c in ts]

    puzzle_ratio = np.mean(puzzle_scores) if puzzle_scores else 0.0
    text_ratio = np.mean(text_scores) if text_scores else 0.0

    return (float(puzzle_ratio), float(text_ratio))


# ---------------------------------------------------------------------------
# Archive management
# ---------------------------------------------------------------------------

def create_archive():
    """Create a MAP-Elites GridArchive with 2D behavioral descriptors."""
    return GridArchive(
        solution_dim=1,  # placeholder — we store tool paths separately
        dims=[10, 10],   # 10x10 grid = 100 cells
        ranges=[(0.0, 1.0), (0.0, 1.0)],  # puzzle_ratio x text_ratio
    )


def save_archive_state(archive, tools_metadata):
    """Save archive state + tool metadata to disk."""
    DFORGE_DIR.mkdir(parents=True, exist_ok=True)
    state = {
        "timestamp": datetime.now().isoformat(),
        "archive_size": len(archive),
        "tools": tools_metadata,
    }
    ARCHIVE_PATH.write_text(json.dumps(state, indent=2, default=str),
                            encoding="utf-8")


# ---------------------------------------------------------------------------
# Generation loop
# ---------------------------------------------------------------------------

def generate_diverse(n_per_island: int = 10):
    """Generate tools from each island prompt, evaluate, add to archive."""
    DFORGE_DIR.mkdir(parents=True, exist_ok=True)
    code_dir = DFORGE_DIR / "tools"
    code_dir.mkdir(exist_ok=True)

    archive = create_archive()
    tools_metadata = []

    # Load existing if resuming
    if ARCHIVE_PATH.exists():
        try:
            state = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))
            tools_metadata = state.get("tools", [])
            log.info("Loaded %d existing tools from archive", len(tools_metadata))
        except Exception:
            pass

    total_generated = 0
    total_valid = 0
    total_archived = 0

    for island_name, island_prompt in ISLAND_PROMPTS.items():
        log.info("=" * 60)
        log.info("Island: %s", island_name)
        log.info("=" * 60)

        for i in range(n_per_island):
            log.info("[%s] [%d/%d] Generating...", island_name, i + 1, n_per_island)

            response, model_used = _call_with_fallback(island_prompt)
            if response is None:
                log.warning("  All models failed, skipping")
                continue

            code, status = extract_code(response)
            if not code:
                log.warning("  No code extracted")
                continue

            code = _sanitize_unicode(code)
            code = _inject_missing_imports(code)
            code = _fix_common_errors(code)

            valid, reason = validate(code)
            if not valid:
                log.warning("  Invalid: %s", reason[:60])
                continue

            total_valid += 1

            # Evaluate against mixed battery
            try:
                tool = load_tool_from_code(code)
                eval_result = evaluate_tool(tool)
            except Exception as e:
                log.warning("  Eval error: %s", str(e)[:60])
                continue

            total_generated += 1

            # Compute behavioral descriptors
            puzzle_ratio, text_ratio = compute_behavioral_descriptors(eval_result)
            accuracy = eval_result["accuracy"]

            log.info("  acc=%.0f%% puzzle=%.0f%% text=%.0f%% model=%s",
                     accuracy * 100, puzzle_ratio * 100, text_ratio * 100,
                     model_used.split("/")[-1] if model_used else "?")

            # Save the tool
            tool_id = f"{island_name}_{i:03d}_{hashlib.md5(code.encode()).hexdigest()[:8]}"
            tool_path = code_dir / f"{tool_id}.py"
            tool_path.write_text(code, encoding="utf-8")

            # Add to archive (MAP-Elites: keep best per cell)
            try:
                archive.add(
                    [0.0],  # placeholder solution
                    accuracy,  # objective (fitness)
                    [puzzle_ratio, text_ratio],  # behavioral descriptors
                )
                total_archived += 1
            except Exception:
                pass

            meta = {
                "tool_id": tool_id,
                "island": island_name,
                "model": model_used,
                "accuracy": accuracy,
                "puzzle_ratio": puzzle_ratio,
                "text_ratio": text_ratio,
                "type_scores": eval_result["type_scores"],
                "code_length": len(code),
                "timestamp": datetime.now().isoformat(),
            }
            tools_metadata.append(meta)

            time.sleep(1.0)

    # Save archive
    save_archive_state(archive, tools_metadata)

    log.info("=" * 60)
    log.info("DIVERSITY FORGE COMPLETE")
    log.info("  Generated: %d valid tools", total_generated)
    log.info("  Archived: %d (MAP-Elites cells filled: %d/100)",
             total_archived, len(archive))
    log.info("  Saved to: %s", DFORGE_DIR)
    log.info("=" * 60)

    # Print coverage map
    print_coverage_map(tools_metadata)


def print_coverage_map(tools_metadata):
    """Print ASCII coverage map of puzzle vs text capability."""
    grid = np.zeros((10, 10), dtype=int)
    for t in tools_metadata:
        px = min(int(t["puzzle_ratio"] * 10), 9)
        tx = min(int(t["text_ratio"] * 10), 9)
        grid[9 - tx][px] += 1  # y-axis inverted for display

    print("\n  COVERAGE MAP (puzzle_ratio x text_ratio)")
    print("  " + "".join(f"{i*10:>4}%" for i in range(10)))
    for row_idx, row in enumerate(grid):
        text_pct = (9 - row_idx) * 10
        cells = ""
        for count in row:
            if count == 0:
                cells += "   ."
            elif count < 5:
                cells += f"  {count:2d}"
            else:
                cells += f"  {count:2d}"
        print(f"{text_pct:>3}%{cells}")
    print("      " + "-" * 40)
    print("      puzzle_ratio -->")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Diversity Forge")
    parser.add_argument("--generate", action="store_true",
                        help="Generate diverse tools from island prompts")
    parser.add_argument("--n", type=int, default=10,
                        help="Tools per island (default 10, 5 islands = 50 total)")
    parser.add_argument("--map", action="store_true",
                        help="Print coverage map from existing archive")
    parser.add_argument("--loop", action="store_true",
                        help="Continuous: generate + evaluate in loop")
    args = parser.parse_args()

    if args.generate or args.loop:
        generate_diverse(n_per_island=args.n)

    if args.map:
        if ARCHIVE_PATH.exists():
            state = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))
            print_coverage_map(state.get("tools", []))
        else:
            log.error("No archive found. Run --generate first.")

    if args.loop:
        log.info("Loop mode: sleeping 5 min then regenerating...")
        while True:
            time.sleep(300)
            generate_diverse(n_per_island=args.n)


if __name__ == "__main__":
    main()
