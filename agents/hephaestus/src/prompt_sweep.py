"""Prompt Strategy Sweep — Test different prompting approaches across models.

The model sweep showed: all models converge on the same mechanism when given
the same prompt. This sweep tests whether different PROMPTS produce different
mechanisms from the same models.

Usage:
    python prompt_sweep.py --generate          # Run all strategies x all models
    python prompt_sweep.py --generate --strategy algo-first  # One strategy
    python prompt_sweep.py --score             # Score all outputs
    python prompt_sweep.py --matrix            # Comparison matrix
"""

import argparse
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from code_extractor import extract_code
from hephaestus import (
    _inject_missing_imports, _sanitize_unicode, _fix_common_errors,
    _compute_novelty, FORGE_DIR, safe_filename,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PSWEEP] %(message)s")
log = logging.getLogger("prompt_sweep")

HEPH_ROOT = Path(__file__).resolve().parent.parent
SWEEP_DIR = HEPH_ROOT / "prompt_sweep"

# Auto-load .env
_ENV = HEPH_ROOT / ".env"
if _ENV.exists():
    for line in _ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# ---------------------------------------------------------------------------
# Models (confirmed working, with fallback order)
# ---------------------------------------------------------------------------

MODELS = [
    {"id": "meta/llama-3.3-70b-instruct", "tag": "llama-3.3", "timeout": 60},
    {"id": "meta/llama-4-maverick-17b-128e-instruct", "tag": "maverick", "timeout": 60},
    {"id": "qwen/qwen3-next-80b-a3b-instruct", "tag": "qwen3-next", "timeout": 90},
    {"id": "qwen/qwen3.5-397b-a17b", "tag": "qwen-397B", "timeout": 120},
    {"id": "qwen/qwen3-coder-480b-a35b-instruct", "tag": "qwen3-coder", "timeout": 180},
]

# GitHub Models (if GITHUB_TOKEN available)
GITHUB_MODELS = [
    {"id": "gpt-4o-mini", "tag": "gpt4o-mini", "timeout": 60,
     "base_url": "https://models.inference.ai.azure.com",
     "api_key_env": "GITHUB_TOKEN"},
]

# ---------------------------------------------------------------------------
# Prompt Strategies
# ---------------------------------------------------------------------------

ALGORITHMS = [
    "constraint propagation with arc consistency and backtracking",
    "belief propagation on a factor graph",
    "A* search over a state space of partial evaluations",
    "Monte Carlo tree search with UCB1 selection",
    "minimax with alpha-beta pruning over candidate rankings",
    "Bayesian network inference with variable elimination",
    "genetic algorithm evolving scoring weights per problem features",
    "SAT solver reduction (encode prompt logic as clauses, solve)",
    "dynamic programming over subproblems extracted from the prompt",
    "gradient descent on a differentiable scoring function (numpy only)",
    "reservoir computing with echo state network dynamics",
    "particle filter tracking belief state across reasoning steps",
    "simulated annealing over candidate orderings",
    "Hungarian algorithm for structural alignment between prompt and answers",
    "Viterbi decoding treating reasoning as a hidden Markov model",
    "topological sort of causal dependencies then forward propagation",
    "iterative deepening depth-first search over logical implications",
    "expectation maximization for latent reasoning structure",
    "ant colony optimization for path through reasoning graph",
    "Kalman filter tracking confidence state across evidence pieces",
]

PROBLEM_TYPES = [
    "multi-step logical deduction (5+ chained implications)",
    "constraint satisfaction with dead ends requiring backtracking",
    "causal reasoning distinguishing correlation from intervention",
    "theory of mind (modeling what another agent believes)",
    "analogical transfer between unfamiliar domains",
    "probabilistic inference under uncertainty",
    "temporal reasoning with scheduling conflicts",
    "spatial reasoning about relative positions",
    "adversarial robustness (prompt tries to trick the tool)",
    "meta-reasoning (knowing when you don't know)",
]


def _strategy_algo_first(concepts, idx):
    """Prompt: implement a specific algorithm."""
    algo = ALGORITHMS[idx % len(ALGORITHMS)]
    return f"""Write a Python class called ReasoningTool that implements {algo}
to evaluate candidate answers to reasoning questions.

The class must have:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
  Returns sorted list of {{"candidate": str, "score": float, "reasoning": str}}
- confidence(self, prompt: str, answer: str) -> float
  Returns float in [0.0, 1.0]

Requirements:
- Use ONLY numpy and Python stdlib (no torch, sklearn, etc.)
- The algorithm must actually be implemented, not just named in comments
- Parse the prompt to extract logical structure (negations, comparatives, conditionals)
- Score candidates based on how well they satisfy the extracted constraints
- Keep under 200 lines

The concepts to draw inspiration from: {', '.join(concepts)}
But the PRIMARY requirement is implementing {algo} correctly.
"""


def _strategy_gap_fill(concepts, idx):
    """Prompt: fill a specific capability gap."""
    problem = PROBLEM_TYPES[idx % len(PROBLEM_TYPES)]
    return f"""Write a Python class called ReasoningTool that excels at:
{problem}

The class must have:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
  Returns sorted list of {{"candidate": str, "score": float, "reasoning": str}}
- confidence(self, prompt: str, answer: str) -> float
  Returns float in [0.0, 1.0]

Requirements:
- Use ONLY numpy and Python stdlib
- Do NOT use NCD (zlib compression distance) as the primary scoring method
- Do NOT just pattern-match keywords — implement actual computation
- The tool should FAIL gracefully on problems outside its specialty (return 0.5)
- Keep under 200 lines

Concepts for inspiration: {', '.join(concepts)}
"""


def _strategy_adversarial(concepts, idx):
    """Prompt: solve problems that existing tools get wrong."""
    return f"""The following reasoning problems are consistently solved WRONG by existing tools:
- "A bat and ball cost $1.10. Bat costs $1 more than ball. What does ball cost?" (tools say $0.10, correct is $0.05)
- "If Alice is taller than Bob, and Bob is taller than Carol, who is shortest?" (tools confuse ordering)
- "Coin flipped heads 5 times. Probability of heads next?" (tools say >50%, correct is 50%)
- "13 people, 12 months. Must two share a birth month?" (tools sometimes say No)
- Presupposition traps like "Have you stopped doing X?" (tools answer Yes/No instead of rejecting)

Write a Python class called ReasoningTool that CORRECTLY solves these types of problems.
Focus on actual COMPUTATION, not keyword matching.

The class must have:
- evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
- confidence(self, prompt: str, answer: str) -> float

Requirements:
- Use ONLY numpy and Python stdlib
- Actually COMPUTE arithmetic answers (don't regex for "$0.05")
- Actually TRACK ordering relations (build a partial order, query it)
- Actually CHECK probability independence (don't just match "fair coin")
- Keep under 200 lines

Draw from: {', '.join(concepts)}
"""


def _strategy_exemplar(concepts, idx):
    """Prompt: here's a working tool, build a DIFFERENT approach."""
    return f"""Here is a working but MEDIOCRE reasoning tool (scores 35% on our battery):

```python
class ReasoningTool:
    def evaluate(self, prompt, candidates):
        import re, zlib
        results = []
        for c in candidates:
            # NCD similarity
            c1 = len(zlib.compress(prompt.encode()))
            c2 = len(zlib.compress(c.encode()))
            c12 = len(zlib.compress((prompt + c).encode()))
            ncd = (c12 - min(c1,c2)) / max(c1,c2)
            score = 1.0 - ncd
            results.append({{"candidate": c, "score": score, "reasoning": "NCD"}})
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt, answer):
        return 0.5
```

This tool ONLY measures compression similarity. It cannot:
- Do arithmetic
- Track logical ordering
- Detect presuppositions
- Reason about causality
- Handle negation correctly

Write a COMPLETELY DIFFERENT ReasoningTool that does NOT use NCD/compression.
Instead implement genuine reasoning using: {', '.join(concepts)}

Requirements:
- evaluate(self, prompt, candidates) -> list[dict]
- confidence(self, prompt, answer) -> float
- ONLY numpy and stdlib
- Must NOT use zlib.compress anywhere
- Must implement actual computation/logic
- Under 200 lines
"""


def _strategy_concept_first(concepts, idx):
    """Control: same as the original forge prompt style."""
    from prompts import build_code_gen_prompt, select_frame
    frame = select_frame()
    response_text = f"Combining {', '.join(concepts)} for reasoning evaluation."
    ratings = {"reasoning": 7, "metacognition": 6, "hypothesis_generation": 7, "implementability": 8}
    return build_code_gen_prompt(concepts, response_text, ratings, frame=frame)


STRATEGIES = {
    "algo-first": _strategy_algo_first,
    "gap-fill": _strategy_gap_fill,
    "adversarial": _strategy_adversarial,
    "exemplar": _strategy_exemplar,
    "concept-first": _strategy_concept_first,  # control
}

# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def _make_client(base_url=None, api_key_env="NVIDIA_API_KEY", timeout=120):
    key = os.environ.get(api_key_env)
    if not key:
        return None
    return OpenAI(
        base_url=base_url or "https://integrate.api.nvidia.com/v1",
        api_key=key,
        timeout=float(timeout),
    )


def _call_with_fallback(prompt, models, temperature=0.4, max_tokens=4096):
    """Try models in order, fall back on 429/timeout/error."""
    for m in models:
        client = _make_client(
            base_url=m.get("base_url"),
            api_key_env=m.get("api_key_env", "NVIDIA_API_KEY"),
            timeout=m["timeout"],
        )
        if client is None:
            continue
        try:
            resp = client.chat.completions.create(
                model=m["id"],
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content, m["tag"]
        except Exception as e:
            err = str(e)
            if "429" in err:
                log.warning("  429 from %s, trying next model", m["tag"])
                time.sleep(5.0)
                continue
            elif "timeout" in err.lower() or "timed out" in err.lower():
                log.warning("  Timeout from %s, trying next model", m["tag"])
                continue
            else:
                log.warning("  Error from %s: %s", m["tag"], err[:80])
                continue
    return None, None


def generate_sweep(strategies=None, n_candidates=20, models=None):
    """Generate tools across prompt strategies with model fallback."""
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)

    if strategies is None:
        strategies = list(STRATEGIES.keys())
    if models is None:
        models = MODELS[:]
        # Add GitHub models if token available
        if os.environ.get("GITHUB_TOKEN"):
            models.extend(GITHUB_MODELS)
            log.info("GitHub Models added to fallback chain")

    # Load frozen candidates for concept names
    candidates_path = HEPH_ROOT / "model_sweep" / "candidates_100.json"
    if candidates_path.exists():
        all_candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    else:
        log.error("No frozen candidates found. Run model_sweep.py --freeze first.")
        return

    # Use first n_candidates
    candidates = all_candidates[:n_candidates]

    for strategy_name in strategies:
        strategy_fn = STRATEGIES[strategy_name]
        output_dir = SWEEP_DIR / strategy_name
        output_dir.mkdir(parents=True, exist_ok=True)
        results_path = output_dir / "results.jsonl"

        # Resume support
        done_keys = set()
        if results_path.exists():
            for line in results_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        done_keys.add(json.loads(line)["key"])
                    except Exception:
                        pass

        log.info("=" * 60)
        log.info("Strategy: %s (%d candidates, %d already done)",
                 strategy_name, len(candidates), len(done_keys))
        log.info("=" * 60)

        generated = 0
        for i, cand in enumerate(candidates):
            if cand["key"] in done_keys:
                continue

            concepts = cand["concept_names"]
            prompt = strategy_fn(concepts, i)

            log.info("[%s] [%d/%d] %s", strategy_name, i + 1, len(candidates),
                     " + ".join(concepts))

            response, model_used = _call_with_fallback(prompt, models)

            if response is None:
                result = {
                    "key": cand["key"], "concept_names": concepts,
                    "strategy": strategy_name, "model": None,
                    "status": "all_models_failed",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                code, extract_status = extract_code(response)
                if code:
                    code = _sanitize_unicode(code)
                    code = _inject_missing_imports(code)
                    code = _fix_common_errors(code)
                    fname = safe_filename(concepts)
                    (output_dir / f"{fname}.py").write_text(code, encoding="utf-8")

                result = {
                    "key": cand["key"], "concept_names": concepts,
                    "strategy": strategy_name, "model": model_used,
                    "status": "generated" if code else "no_code",
                    "code_length": len(code) if code else 0,
                    "timestamp": datetime.now().isoformat(),
                }
                if code:
                    generated += 1

            with open(results_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result) + "\n")

            time.sleep(1.0)

        log.info("[%s] Complete: %d generated", strategy_name, generated)


# ---------------------------------------------------------------------------
# Scoring + Matrix (reuse model_sweep infrastructure)
# ---------------------------------------------------------------------------

def score_all():
    """Score all generated tools through the full battery."""
    from validator import validate
    from test_harness import run_trap_battery, load_tool_from_code

    scored_path = SWEEP_DIR / "scored_matrix.jsonl"

    for strat_dir in sorted(SWEEP_DIR.iterdir()):
        if not strat_dir.is_dir():
            continue
        strategy = strat_dir.name

        for py_file in sorted(strat_dir.glob("*.py")):
            code = py_file.read_text(encoding="utf-8")
            result = {"strategy": strategy, "file": py_file.name}

            valid, reason = validate(code)
            result["valid"] = valid
            result["validation_reason"] = reason

            if valid:
                try:
                    tool = load_tool_from_code(code)
                    battery = run_trap_battery(tool)
                    result["accuracy"] = battery["accuracy"]
                    result["calibration"] = battery["calibration"]
                    result["passed"] = battery["passed"]
                    result["tier_breakdown"] = battery.get("tier_breakdown", {})
                except Exception as e:
                    result["runtime_error"] = str(e)[:200]

                try:
                    novelty = _compute_novelty(code)
                    result["novelty_min_ncd"] = novelty["min_ncd"]
                except Exception:
                    pass

            with open(scored_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result) + "\n")

            log.info("[%s] %s: valid=%s acc=%s",
                     strategy, py_file.name[:40], valid,
                     f"{result.get('accuracy', 0):.0%}" if "accuracy" in result else "N/A")


def print_matrix():
    """Print comparison across strategies."""
    import numpy as np
    from collections import defaultdict

    scored_path = SWEEP_DIR / "scored_matrix.jsonl"
    if not scored_path.exists():
        log.error("No scored results. Run --score first.")
        return

    strategies = defaultdict(lambda: {"total": 0, "valid": 0, "passed": 0,
                                       "accuracies": [], "novelties": [], "tiers": defaultdict(list)})

    for line in scored_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        s = strategies[r["strategy"]]
        s["total"] += 1
        if r.get("valid"):
            s["valid"] += 1
            if r.get("passed"):
                s["passed"] += 1
            if "accuracy" in r:
                s["accuracies"].append(r["accuracy"])
            if "novelty_min_ncd" in r:
                s["novelties"].append(r["novelty_min_ncd"])
            if r.get("tier_breakdown"):
                for tier, data in r["tier_breakdown"].items():
                    if isinstance(data, dict):
                        s["tiers"][tier].append(data.get("accuracy", 0))

    print("\n" + "=" * 110)
    print(f"{'Strategy':<15} {'n':>4} {'Valid':>5} {'Pass':>4} {'Rate':>6} "
          f"{'MeanAcc':>8} {'R1':>6} {'R2':>6} {'R3':>6} {'R4':>6} {'R5':>6} {'R6':>6} {'Novelty':>8}")
    print("-" * 110)

    for name in ["concept-first", "algo-first", "gap-fill", "adversarial", "exemplar"]:
        if name not in strategies:
            continue
        s = strategies[name]
        accs = s["accuracies"]
        novs = s["novelties"]
        rate = s["passed"] / s["total"] * 100 if s["total"] > 0 else 0
        acc_str = f"{np.mean(accs)*100:.1f}%" if accs else "N/A"
        nov_str = f"{np.mean(novs):.3f}" if novs else "N/A"

        tier_strs = []
        for t in ["R1", "R2", "R3", "R4", "R5", "R6"]:
            vals = s["tiers"].get(t, [])
            tier_strs.append(f"{np.mean(vals)*100:.1f}%" if vals else "  N/A")

        print(f"{name:<15} {s['total']:>4} {s['valid']:>5} {s['passed']:>4} {rate:>5.1f}% "
              f"{acc_str:>8} {' '.join(tier_strs)} {nov_str:>8}")

    print("=" * 110)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Prompt strategy sweep")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--strategy", type=str, default=None,
                        choices=list(STRATEGIES.keys()))
    parser.add_argument("--score", action="store_true")
    parser.add_argument("--matrix", action="store_true")
    parser.add_argument("--n", type=int, default=20,
                        help="Candidates per strategy (default 20)")
    args = parser.parse_args()

    if args.generate:
        strats = [args.strategy] if args.strategy else None
        generate_sweep(strategies=strats, n_candidates=args.n)

    if args.score:
        score_all()

    if args.matrix:
        print_matrix()


if __name__ == "__main__":
    main()
