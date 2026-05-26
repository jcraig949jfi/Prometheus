"""Composer — Combine parser tools with algorithmic engines.

The decisive test: does diverse substrate compose into something
better than either part alone?

Takes the best text parser (efme_v2, R1=79%) and wires it to
diversity-forge algorithmic engines (forward chainer, backtracker)
to create composed tools that can both parse text AND reason.

Usage:
    python composer.py --compose    # Build composed tools
    python composer.py --evaluate   # Score composed vs components
    python composer.py --compare    # Side-by-side comparison table
"""

import argparse
import json
import logging
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_harness import run_trap_battery, load_tool_from_code, TRAPS
from diversity_forge import FULL_BATTERY, evaluate_tool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [COMPOSER] %(message)s")
log = logging.getLogger("composer")

HEPH_ROOT = Path(__file__).resolve().parent.parent
COMPOSED_DIR = HEPH_ROOT / "composed_tools"


# ---------------------------------------------------------------------------
# Stage 1: Text parser (extracted from efme_v2 patterns)
# ---------------------------------------------------------------------------

class TextParser:
    """Extract structured propositions from natural language prompts."""

    _NUM = re.compile(r'-?\d+(?:\.\d+)?')
    _COMP_GT = re.compile(r'(\w+(?:\s+\w+)*)\s+(?:is\s+)?(?:greater|larger|more|bigger|higher|taller|heavier|older)\s+than\s+(\w+(?:\s+\w+)*)', re.I)
    _COMP_LT = re.compile(r'(\w+(?:\s+\w+)*)\s+(?:is\s+)?(?:less|smaller|fewer|shorter|lower|lighter|younger)\s+than\s+(\w+(?:\s+\w+)*)', re.I)
    _COND = re.compile(r'if\s+(.+?),?\s+then\s+(.+?)(?:\.|$)', re.I)
    _NEG = re.compile(r'\b(not|no|never|neither|cannot|can\'t|won\'t|doesn\'t|don\'t|isn\'t|aren\'t)\b', re.I)
    _CAUSE = re.compile(r'(.+?)\s+(?:causes|leads\s+to|results\s+in|implies)\s+(.+?)(?:\.|$)', re.I)
    _EQUAL = re.compile(r'(\w+(?:\s+\w+)*)\s+(?:equals?|=|is\s+the\s+same\s+as|is\s+equal\s+to)\s+(\w+(?:\s+\w+)*)', re.I)
    _ALL_X_ARE_Y = re.compile(r'all\s+(\w+)\s+are\s+(\w+)', re.I)
    _SVO = re.compile(r'(\w+)\s+(chased|followed|told|gave|hit|pushed|pulled|ate|saw)\s+(?:the\s+)?(\w+)', re.I)

    def parse(self, prompt: str) -> dict:
        """Extract structured features from a natural language prompt."""
        result = {
            "numbers": [float(x) for x in self._NUM.findall(prompt)],
            "comparisons_gt": self._COMP_GT.findall(prompt),
            "comparisons_lt": self._COMP_LT.findall(prompt),
            "conditionals": self._COND.findall(prompt),
            "negations": self._NEG.findall(prompt),
            "causal": self._CAUSE.findall(prompt),
            "equalities": self._EQUAL.findall(prompt),
            "universals": self._ALL_X_ARE_Y.findall(prompt),
            "svo_triples": self._SVO.findall(prompt),
            "has_negation": bool(self._NEG.search(prompt)),
            "raw": prompt,
        }

        # Build ordering from comparisons
        ordering = {}
        for a, b in result["comparisons_gt"]:
            a, b = a.strip().lower(), b.strip().lower()
            ordering[a] = ordering.get(a, set())
            ordering[a].add(("gt", b))
        for a, b in result["comparisons_lt"]:
            a, b = a.strip().lower(), b.strip().lower()
            ordering[a] = ordering.get(a, set())
            ordering[a].add(("lt", b))
        result["ordering"] = ordering

        # Build inference rules from conditionals + causals
        rules = []
        for antecedent, consequent in result["conditionals"]:
            rules.append((antecedent.strip().lower(), consequent.strip().lower()))
        for cause, effect in result["causal"]:
            rules.append((cause.strip().lower(), effect.strip().lower()))
        result["rules"] = rules

        return result


# ---------------------------------------------------------------------------
# Stage 2: Algorithmic engines
# ---------------------------------------------------------------------------

class ForwardChainEngine:
    """Forward-chaining inference over parsed rules."""

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        rules = parsed.get("rules", [])
        cand_lower = candidate.lower()

        if not rules:
            return 0.5, "no_rules_found"

        # Build graph and propagate
        graph = defaultdict(list)
        facts = set()

        for antecedent, consequent in rules:
            graph[antecedent].append(consequent)
            facts.add(antecedent)

        # Forward chain
        derived = set()
        queue = deque(facts)
        while queue:
            current = queue.popleft()
            if current in derived:
                continue
            derived.add(current)
            for conclusion in graph.get(current, []):
                if conclusion not in derived:
                    queue.append(conclusion)

        # Score: does the candidate match any derived fact?
        if cand_lower in derived:
            return 1.0, f"derived:{cand_lower}"
        # Partial match
        for fact in derived:
            if cand_lower in fact or fact in cand_lower:
                return 0.8, f"partial_match:{fact}"
        return 0.2, "not_derived"


class OrderingEngine:
    """Resolve ordering/comparison queries from parsed comparisons."""

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        ordering = parsed.get("ordering", {})
        cand_lower = candidate.lower()

        if not ordering:
            return 0.5, "no_ordering"

        # Build a directed graph of gt/lt relationships
        gt_graph = defaultdict(set)  # a -> b means a > b
        for entity, relations in ordering.items():
            for rel_type, other in relations:
                if rel_type == "gt":
                    gt_graph[entity].add(other)
                elif rel_type == "lt":
                    gt_graph[other].add(entity)

        # Transitive closure (find who's greatest/least)
        all_entities = set(gt_graph.keys())
        for v in gt_graph.values():
            all_entities |= v

        # Count: how many entities is each greater than?
        rank = {}
        for entity in all_entities:
            # BFS to count all entities reachable via "greater than"
            visited = set()
            q = deque([entity])
            while q:
                curr = q.popleft()
                for lesser in gt_graph.get(curr, set()):
                    if lesser not in visited:
                        visited.add(lesser)
                        q.append(lesser)
            rank[entity] = len(visited)

        # Check if candidate matches the tallest/shortest/etc
        prompt_lower = parsed.get("raw", "").lower()
        if any(w in prompt_lower for w in ["tallest", "greatest", "largest", "heaviest", "oldest", "most"]):
            best = max(rank, key=rank.get) if rank else None
            if best and (cand_lower == best or cand_lower in best or best in cand_lower):
                return 1.0, f"greatest:{best}"
        elif any(w in prompt_lower for w in ["shortest", "smallest", "least", "lightest", "youngest"]):
            best = min(rank, key=rank.get) if rank else None
            if best and (cand_lower == best or cand_lower in best or best in cand_lower):
                return 1.0, f"least:{best}"

        # General: candidate appears in ranked entities
        for entity, r in rank.items():
            if cand_lower in entity or entity in cand_lower:
                return 0.5 + 0.5 * (r / max(len(all_entities), 1)), f"ranked:{entity}={r}"

        return 0.3, "not_in_ordering"


class ComputationEngine:
    """Actually compute numeric answers."""

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        numbers = parsed.get("numbers", [])
        prompt = parsed.get("raw", "")

        # Try to extract and compute the answer
        try:
            cand_val = float(candidate.replace("$", "").replace("%", ""))
        except (ValueError, TypeError):
            cand_val = None

        # Bat-and-ball type: "X costs $Y more than Z, total is $T"
        if "more than" in prompt.lower() and "cost" in prompt.lower() and len(numbers) >= 2:
            total = numbers[0]
            diff = numbers[1] if len(numbers) > 1 else numbers[0]
            # ball = (total - diff) / 2
            computed = (total - diff) / 2
            if cand_val is not None and abs(cand_val - computed) < 0.01:
                return 1.0, f"computed:{computed}"
            elif cand_val is not None:
                return 0.0, f"computed:{computed},got:{cand_val}"

        # "All but N" pattern
        if "all but" in prompt.lower() and len(numbers) >= 2:
            total = numbers[0]
            remaining = numbers[1]
            if cand_val is not None and abs(cand_val - remaining) < 0.01:
                return 1.0, f"all_but:{remaining}"

        # Modular arithmetic
        if "mod" in prompt.lower() and len(numbers) >= 2:
            result = numbers[0] % numbers[1]
            if cand_val is not None and abs(cand_val - result) < 0.01:
                return 1.0, f"mod:{result}"

        # Comparison: which is larger/smaller
        if len(numbers) >= 2 and any(w in prompt.lower() for w in ["larger", "greater", "bigger"]):
            answer = max(numbers)
            if cand_val is not None and abs(cand_val - answer) < 0.01:
                return 1.0, f"max:{answer}"

        # Sequence prediction
        if len(numbers) >= 3:
            # Check geometric
            ratios = [numbers[i+1]/numbers[i] for i in range(len(numbers)-1) if numbers[i] != 0]
            if ratios and all(abs(r - ratios[0]) < 0.01 for r in ratios):
                predicted = numbers[-1] * ratios[0]
                if cand_val is not None and abs(cand_val - predicted) < 0.01:
                    return 1.0, f"geometric_next:{predicted}"

        # Simple: does candidate match any number in the prompt?
        if cand_val is not None:
            for n in numbers:
                if abs(cand_val - n) < 0.01:
                    return 0.6, f"number_match:{n}"

        return 0.5, "no_computation"


class NegationEngine:
    """Handle negation and modus tollens patterns."""

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        prompt = parsed.get("raw", "")
        cand_lower = candidate.lower()
        has_neg = parsed.get("has_negation", False)
        conditionals = parsed.get("conditionals", [])

        # Modus tollens: "If P then Q. Not Q. Therefore not P."
        if has_neg and conditionals:
            for ante, conseq in conditionals:
                ante_l, conseq_l = ante.lower(), conseq.lower()
                # Check if prompt negates the consequent
                neg_patterns = [f"not {conseq_l}", f"{conseq_l} is not", f"no {conseq_l}"]
                if any(np in prompt.lower() for np in neg_patterns):
                    # Modus tollens: P is false
                    if "no" in cand_lower or "not" in cand_lower or cand_lower == "no":
                        return 0.9, f"modus_tollens:not_{ante_l}"
                    elif "yes" in cand_lower or cand_lower == "yes":
                        return 0.1, f"modus_tollens:contradicts"

        # Simple negation: prompt says "not X", candidate says X
        if has_neg:
            if "yes" in cand_lower and ("not" in prompt.lower() or "no " in prompt.lower()):
                return 0.3, "negation_conflict"
            if "no" in cand_lower and ("not" in prompt.lower()):
                return 0.7, "negation_aligned"

        return 0.5, "no_negation_signal"


# ---------------------------------------------------------------------------
# The Composed Tool
# ---------------------------------------------------------------------------

class ComposedReasoningTool:
    """Compose a text parser with multiple algorithmic engines.

    Stage 1: Parse prompt into structured propositions
    Stage 2: Run each engine, collect scores
    Stage 3: Aggregate via weighted ensemble
    """

    def __init__(self):
        self.parser = TextParser()
        self.engines = [
            (0.25, "chain", ForwardChainEngine()),
            (0.25, "order", OrderingEngine()),
            (0.30, "compute", ComputationEngine()),
            (0.20, "negate", NegationEngine()),
        ]

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        parsed = self.parser.parse(prompt)

        results = []
        for candidate in candidates:
            total_score = 0.0
            total_weight = 0.0
            reasons = []

            for weight, name, engine in self.engines:
                score, reason = engine.score(parsed, candidate)
                if score != 0.5:  # Non-default = engine has signal
                    total_score += weight * score
                    total_weight += weight
                    reasons.append(f"{name}:{score:.1f}")
                    if score >= 0.9:
                        # Strong signal from one engine — trust it
                        total_score = score
                        total_weight = 1.0
                        reasons = [f"{name}:DECISIVE:{score:.1f}"]
                        break

            # Fallback to equal scoring if no engine had signal
            if total_weight == 0:
                final_score = 0.5
                reasons.append("no_signal")
            else:
                final_score = total_score / total_weight

            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": " ".join(reasons),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        results = self.evaluate(prompt, [answer])
        if results:
            return max(0.0, min(1.0, results[0]["score"]))
        return 0.5


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_composed():
    """Run the composed tool and components separately, compare."""
    from test_harness import _run_battery, _NCDBaseline, CATEGORY_TIER
    from trap_generator_extended import generate_full_battery

    battery_186 = generate_full_battery(n_per_category=2, seed=42)
    puzzle_battery = FULL_BATTERY

    composed = ComposedReasoningTool()
    ncd = _NCDBaseline()

    print("=" * 80)
    print("COMPOSITION TEST: Parser + Engines vs NCD Baseline")
    print("=" * 80)

    # Run composed tool on 186-probe battery
    composed_results = _run_battery(composed, battery_186)
    ncd_results = _run_battery(ncd, battery_186)

    print(f"\n186-probe battery:")
    print(f"  Composed: acc={composed_results['accuracy']:.0%} cal={composed_results['calibration']:.0%}")
    print(f"  NCD base: acc={ncd_results['accuracy']:.0%} cal={ncd_results['calibration']:.0%}")
    print(f"  Delta:    acc={composed_results['accuracy']-ncd_results['accuracy']:+.0%}")

    # Per-tier breakdown
    print(f"\nPer-tier breakdown:")
    for tier in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
        c_correct, c_total = 0, 0
        n_correct, n_total = 0, 0
        for cr, nr, trap in zip(composed_results['trap_results'], ncd_results['trap_results'], battery_186):
            t = CATEGORY_TIER.get(trap.get('category', ''))
            if t == tier:
                c_total += 1; n_total += 1
                if cr.get('is_correct'): c_correct += 1
                if nr.get('is_correct'): n_correct += 1
        if c_total > 0:
            print(f"  {tier}: composed={c_correct}/{c_total} ({c_correct/c_total:.0%})  "
                  f"ncd={n_correct}/{n_total} ({n_correct/n_total:.0%})  "
                  f"delta={c_correct/c_total - n_correct/n_total:+.0%}")

    # Run on puzzle battery
    puzzle_result = evaluate_tool(composed, puzzle_battery)
    ncd_puzzle = evaluate_tool(ncd, puzzle_battery)

    print(f"\nPuzzle battery ({len(puzzle_battery)} problems):")
    print(f"  Composed: acc={puzzle_result['accuracy']:.0%}")
    print(f"  NCD base: acc={ncd_puzzle['accuracy']:.0%}")

    print(f"\nPer-category:")
    for cat in sorted(puzzle_result['type_scores'].keys()):
        c_score = puzzle_result['type_scores'].get(cat, 0)
        n_score = ncd_puzzle['type_scores'].get(cat, 0)
        marker = " ***" if c_score > n_score else ""
        print(f"  {cat:30} composed={c_score:.0%} ncd={n_score:.0%}{marker}")


def main():
    parser = argparse.ArgumentParser(description="Composer")
    parser.add_argument("--evaluate", action="store_true",
                        help="Evaluate composed tool vs components")
    args = parser.parse_args()

    if args.evaluate:
        evaluate_composed()
    else:
        # Default: just run evaluation
        evaluate_composed()


if __name__ == "__main__":
    main()
