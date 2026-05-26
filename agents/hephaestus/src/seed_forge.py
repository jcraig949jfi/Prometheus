"""Seed Forge — Generate improved tools from winning exemplars.

Uses the best existing tools as seeds: shows working code to the LLM
and asks for targeted improvements based on specific weaknesses.

The DreamCoder pattern: successful programs become library primitives
that the next generation builds on.

Usage:
    python seed_forge.py --generate          # Generate children from all seeds
    python seed_forge.py --generate --n 5    # 5 children per seed
    python seed_forge.py --evaluate          # Score all children
    python seed_forge.py --lineage           # Print parent->child improvement tree
"""

import argparse
import json
import logging
import os
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openai import OpenAI
from code_extractor import extract_code
from hephaestus import (
    _inject_missing_imports, _sanitize_unicode, _fix_common_errors,
    _compute_novelty, _call_with_hard_timeout, call_api_with_fallback,
    make_client, safe_filename, FORGE_DIR, HEPHAESTUS_ROOT,
)
from validator import validate
from test_harness import load_tool_from_code
from puzzle_gen import generate_battery as gen_puzzles
from diversity_forge import evaluate_tool, STATIC_BATTERY, _run_with_timeout

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SEED] %(message)s")
log = logging.getLogger("seed_forge")

SEED_DIR = HEPHAESTUS_ROOT / "seed_forge"

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
# Seed definitions: parent code + weaknesses + improvement prompts
# ---------------------------------------------------------------------------

def _load_seed(path):
    """Load a tool's source code."""
    return Path(path).read_text(encoding="utf-8")


def _build_seeds():
    """Build seed definitions from existing winning tools."""
    seeds = []

    # Seed 1: Composed tool's computation engine — extend with state tracking
    composer_path = Path(__file__).resolve().parent / "composer.py"
    if composer_path.exists():
        seeds.append({
            "name": "composed_plus_state",
            "parent": "composer.py (ComputationEngine + OrderingEngine)",
            "prompt": """\
Here is a working ReasoningTool that combines multiple engines to solve puzzles.
It correctly handles: arithmetic, modular math, ordering/transitivity, modus tollens,
and constraint satisfaction.

It FAILS on:
- State machine simulation (can't track state through transitions)
- Sequence prediction beyond geometric (can't detect fibonacci or power rules)
- Complex graph problems (shortest path sometimes wrong)

Your task: Write an IMPROVED ReasoningTool that keeps everything that works
AND adds:
1. A state machine simulator (parse transition table, simulate step by step)
2. Better sequence detection (check geometric, arithmetic, fibonacci, power rules)
3. Graph shortest path (Dijkstra or BFS on parsed edge list)

Requirements:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float
- ONLY numpy and stdlib
- Under 250 lines
- Must COMPUTE answers, not pattern-match

Here is the working code to build on (keep what works, add what's missing):

```python
{code}
```""",
            "code_source": "composer_engines",
        })

    # Seed 2: Forward chaining reasoner — add NL parsing front-end
    reasoner_files = sorted(HEPHAESTUS_ROOT.glob("diversity_forge/tools/reasoner_*.py"))
    if reasoner_files:
        seeds.append({
            "name": "reasoner_plus_nlp",
            "parent": reasoner_files[0].name,
            "prompt": """\
Here is a working forward-chaining inference engine. It builds a rule graph
and propagates beliefs using BFS. It works perfectly on structured input
like "A -> B\\nB -> C\\nA" but CANNOT parse natural language prompts.

Your task: Write an IMPROVED ReasoningTool that keeps the forward-chaining
engine AND adds a natural language parser front-end that extracts:
- "If X then Y" -> rule: X -> Y
- "X is taller than Y" -> ordering: X > Y
- "not X" / "X is false" -> negation of X
- Numbers and arithmetic operations
- "All X are Y" -> universal rule

The parser converts natural language to structured rules, then the
forward-chaining engine reasons over them.

Requirements:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float
- ONLY numpy and stdlib
- Under 250 lines

Here is the working inference engine to build on:

```python
{code}
```""",
            "code_source": "reasoner",
        })

    # Seed 3: Start fresh — state machine specialist
    seeds.append({
        "name": "state_machine_specialist",
        "parent": "none (from scratch)",
        "prompt": """\
Write a Python ReasoningTool that specializes in STATE MACHINE problems.

It must:
1. Parse a transition table from natural language:
   "State A + input '0' -> State B" etc.
2. Parse the initial state and input sequence
3. SIMULATE the state machine step by step
4. Return the final state as the answer

Also handle these related problem types:
- Register machines: "x=10, Step 1: x=x+5, Step 2: x=x*2, What is x?"
- Stack operations: "Push 3, Push 7, Pop, Push 1, What is on top?"
- Counter/accumulator: tracking a value through operations

Requirements:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float
- ONLY numpy and stdlib
- Under 200 lines
- Must actually SIMULATE, not pattern-match
""",
        "code_source": "fresh",
    })

    # Seed 4: Graph specialist
    seeds.append({
        "name": "graph_specialist",
        "parent": "none (from scratch)",
        "prompt": """\
Write a Python ReasoningTool that specializes in GRAPH problems.

It must:
1. Parse graph edges from text: "A-B(3), B-C(1), A-C(5)" -> adjacency list
2. Implement Dijkstra's shortest path algorithm
3. Implement BFS reachability ("Is there a path from X to Y?")
4. Handle both directed and undirected graphs

Also handle:
- Simple connectivity: "Can X reach Y?"
- Graph coloring: "Adjacent nodes must differ, what color is node X?"

Requirements:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float
- ONLY numpy and stdlib
- Under 200 lines
- Must implement ACTUAL graph algorithms, not keyword matching
""",
        "code_source": "fresh",
    })

    # Seed 5: Sequence/pattern specialist
    seeds.append({
        "name": "sequence_specialist",
        "parent": "none (from scratch)",
        "prompt": """\
Write a Python ReasoningTool that specializes in SEQUENCE and PATTERN problems.

It must detect and extrapolate these sequence types:
1. Arithmetic: constant difference (2, 5, 8, 11 -> diff=3, next=14)
2. Geometric: constant ratio (3, 6, 12, 24 -> ratio=2, next=48)
3. Fibonacci-like: each = sum of previous two (1, 1, 2, 3, 5 -> next=8)
4. Power: base^n (2, 4, 8, 16 -> base=2, next=32)
5. Polynomial: try differences of differences

Strategy: try each rule type, check which fits, predict next.

Also handle:
- Pattern continuation: "AAB, AAB, AAB, ?" -> "AAB"
- Modular arithmetic: "What is N mod M?"

Requirements:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float
- ONLY numpy and stdlib
- Under 200 lines
- Must COMPUTE, not pattern-match
""",
        "code_source": "fresh",
    })

    return seeds


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def _get_seed_code(seed):
    """Get the parent code to include in the prompt."""
    if seed["code_source"] == "composer_engines":
        # Extract the engine classes from composer.py
        composer_path = Path(__file__).resolve().parent / "composer.py"
        code = composer_path.read_text(encoding="utf-8")
        # Find from "class TextParser" to "class ComposedReasoningTool"
        start = code.find("class TextParser:")
        end = code.find("class ComposedReasoningTool:")
        if start >= 0 and end >= 0:
            return code[start:end].strip()
        return code[:3000]

    elif seed["code_source"] == "reasoner":
        reasoner_files = sorted(HEPHAESTUS_ROOT.glob("diversity_forge/tools/reasoner_*.py"))
        if reasoner_files:
            code = reasoner_files[0].read_text(encoding="utf-8")
            # Strip auto-fix wrappers
            if "# --- Auto-fix" in code:
                code = code[:code.index("# --- Auto-fix")]
            return code.strip()
        return ""

    elif seed["code_source"] == "fresh":
        return ""  # No parent code for fresh seeds

    return ""


def generate_seeds(n_per_seed=3):
    """Generate children from each seed."""
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    tools_dir = SEED_DIR / "tools"
    tools_dir.mkdir(exist_ok=True)
    lineage_path = SEED_DIR / "lineage.jsonl"

    client = make_client()
    seeds = _build_seeds()

    # Evaluation batteries
    static = STATIC_BATTERY
    generated = gen_puzzles(n=30, seed=777)  # Fresh seed for anti-memorization
    full_battery = static + generated

    log.info("Seeds: %d, children per seed: %d, battery: %d problems",
             len(seeds), n_per_seed, len(full_battery))

    all_results = []

    for seed in seeds:
        log.info("=" * 60)
        log.info("Seed: %s (parent: %s)", seed["name"], seed["parent"])
        log.info("=" * 60)

        parent_code = _get_seed_code(seed)
        prompt = seed["prompt"].format(code=parent_code) if "{code}" in seed["prompt"] else seed["prompt"]

        for i in range(n_per_seed):
            log.info("[%s] Child %d/%d generating...", seed["name"], i + 1, n_per_seed)

            # Use llama-3.3 as primary (fastest, handles long prompts better)
            response, model_used = call_api_with_fallback(client, prompt, "meta/llama-3.3-70b-instruct")
            if response is None:
                log.warning("  API failed, skipping")
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

            # Evaluate on both batteries
            try:
                tool = load_tool_from_code(code)

                # Safe eval with timeout per problem
                correct_static = 0
                correct_gen = 0
                cat_scores = {}

                for p in full_battery:
                    cat = p.get("category", "?")
                    if cat not in cat_scores:
                        cat_scores[cat] = {"correct": 0, "total": 0}
                    cat_scores[cat]["total"] += 1

                    result = _run_with_timeout(
                        tool.evaluate, (p["prompt"], p["candidates"]), timeout_sec=5
                    )
                    if result and result[0].get("candidate") == p["correct"]:
                        cat_scores[cat]["correct"] += 1
                        if p in static:
                            correct_static += 1
                        else:
                            correct_gen += 1

                total = len(full_battery)
                total_correct = correct_static + correct_gen
                accuracy = total_correct / total if total > 0 else 0

            except Exception as e:
                log.warning("  Eval error: %s", str(e)[:60])
                continue

            # Save
            child_id = f"{seed['name']}_{i:02d}_{hashlib.md5(code.encode()).hexdigest()[:8]}"
            tool_path = tools_dir / f"{child_id}.py"
            tool_path.write_text(code, encoding="utf-8")

            # Category breakdown
            cat_summary = {}
            for cat, data in cat_scores.items():
                cat_summary[cat] = round(data["correct"] / data["total"], 2) if data["total"] > 0 else 0

            entry = {
                "child_id": child_id,
                "seed_name": seed["name"],
                "parent": seed["parent"],
                "model": model_used,
                "accuracy": round(accuracy, 4),
                "correct_static": correct_static,
                "correct_generated": correct_gen,
                "total": total,
                "static_acc": round(correct_static / len(static), 4) if static else 0,
                "generated_acc": round(correct_gen / len(generated), 4) if generated else 0,
                "category_scores": cat_summary,
                "code_length": len(code),
                "timestamp": datetime.now().isoformat(),
            }

            with open(lineage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            all_results.append(entry)

            log.info("  %s: acc=%.0f%% (static=%.0f%% gen=%.0f%%) model=%s",
                     child_id, accuracy * 100,
                     entry["static_acc"] * 100, entry["generated_acc"] * 100,
                     model_used.split("/")[-1] if model_used else "?")

            # Show category highlights
            strong = [(c, s) for c, s in cat_summary.items() if s >= 0.5]
            if strong:
                log.info("  Strong categories: %s",
                         ", ".join(f"{c}={s:.0%}" for c, s in sorted(strong, key=lambda x: -x[1])[:5]))

            time.sleep(2.0)

    # Summary
    log.info("=" * 60)
    log.info("SEED FORGE COMPLETE: %d children generated", len(all_results))
    if all_results:
        best = max(all_results, key=lambda r: r["accuracy"])
        log.info("  Best: %s acc=%.0f%%", best["child_id"], best["accuracy"] * 100)
        avg = sum(r["accuracy"] for r in all_results) / len(all_results)
        log.info("  Average accuracy: %.0f%%", avg * 100)
    log.info("=" * 60)

    return all_results


def print_lineage():
    """Print the parent->child improvement tree."""
    lineage_path = SEED_DIR / "lineage.jsonl"
    if not lineage_path.exists():
        log.error("No lineage data. Run --generate first.")
        return

    entries = []
    for line in lineage_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))

    # Group by seed
    by_seed = {}
    for e in entries:
        by_seed.setdefault(e["seed_name"], []).append(e)

    # Reference: NCD baseline on static puzzles ~25%, composed ~45%
    print("\n" + "=" * 80)
    print("LINEAGE: Seed -> Children (reference: NCD ~25%, Composed ~45%)")
    print("=" * 80)

    for seed_name, children in sorted(by_seed.items()):
        print(f"\n  Seed: {seed_name} (parent: {children[0]['parent']})")
        children.sort(key=lambda c: -c["accuracy"])
        for c in children:
            static = c.get("static_acc", 0)
            gen = c.get("generated_acc", 0)
            print(f"    {c['child_id']}: acc={c['accuracy']:.0%} "
                  f"(static={static:.0%} gen={gen:.0%}) "
                  f"len={c['code_length']}")
            # Show what it's good at
            strong = [(cat, s) for cat, s in c.get("category_scores", {}).items() if s >= 0.5]
            if strong:
                print(f"      Strong: {', '.join(f'{c}={s:.0%}' for c, s in sorted(strong, key=lambda x: -x[1])[:6])}")

    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Seed Forge")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--n", type=int, default=3, help="Children per seed")
    parser.add_argument("--lineage", action="store_true")
    args = parser.parse_args()

    if args.generate:
        generate_seeds(n_per_seed=args.n)

    if args.lineage:
        print_lineage()


if __name__ == "__main__":
    main()
