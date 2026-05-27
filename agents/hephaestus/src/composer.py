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
                neg_patterns = [f"not {conseq_l}", f"{conseq_l} is not",
                                f"no {conseq_l}", f"{conseq_l} is false"]
                if any(np in prompt.lower() for np in neg_patterns):
                    if "no" in cand_lower or "not" in cand_lower or cand_lower == "no":
                        return 0.9, f"modus_tollens:not_{ante_l}"
                    elif "yes" in cand_lower or cand_lower == "yes":
                        return 0.1, f"modus_tollens:contradicts"

        # Affirming consequent fallacy: "If P then Q. Q. Therefore P?" -> Cannot determine
        # But NOT modus ponens: "If P then Q. P. Therefore Q?" -> Yes
        if conditionals and not has_neg:
            for ante, conseq in conditionals:
                ante_l, conseq_l = ante.lower(), conseq.lower()
                prompt_l = prompt.lower()
                # Only trigger affirming consequent if prompt states Q (consequent) is true
                # AND asks about P (antecedent). NOT if prompt states P is true.
                if (f"it is the case that {conseq_l}" in prompt_l
                    or f"{conseq_l} is true" in prompt_l
                    or f"{conseq_l} is the case" in prompt_l):
                    # Consequent affirmed — this is the fallacy
                    if "cannot" in cand_lower or "determine" in cand_lower:
                        return 0.8, "affirming_consequent:cannot_determine"
                elif (f"it is the case that {ante_l}" in prompt_l
                      or f"{ante_l} is true" in prompt_l
                      or f"{ante_l}" in prompt_l):
                    # Antecedent affirmed — this is modus ponens (valid)
                    if "yes" in cand_lower:
                        return 0.8, "modus_ponens:yes"

        # Simple negation
        if has_neg:
            if "yes" in cand_lower and ("not" in prompt.lower() or "no " in prompt.lower()):
                return 0.3, "negation_conflict"
            if "no" in cand_lower and ("not" in prompt.lower()):
                return 0.7, "negation_aligned"

        return 0.5, "no_negation_signal"


class SequenceEngine:
    """R3: Detect and extrapolate numerical sequences."""

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        numbers = parsed.get("numbers", [])
        prompt = parsed.get("raw", "")

        try:
            cand_val = float(candidate.replace("$", "").replace("%", ""))
        except (ValueError, TypeError):
            return 0.5, "non_numeric_candidate"

        # Need at least 3 numbers to detect a sequence
        if len(numbers) < 3:
            return 0.5, "too_few_numbers"

        seq = numbers

        # Check arithmetic: constant difference
        diffs = [seq[i+1] - seq[i] for i in range(len(seq)-1)]
        if len(set(round(d, 6) for d in diffs)) == 1 and diffs[0] != 0:
            predicted = seq[-1] + diffs[0]
            if abs(cand_val - predicted) < 0.01:
                return 1.0, f"arithmetic:diff={diffs[0]},next={predicted}"
            return 0.0, f"arithmetic:expected={predicted}"

        # Check geometric: constant ratio
        if all(s != 0 for s in seq[:-1]):
            ratios = [seq[i+1] / seq[i] for i in range(len(seq)-1)]
            if len(set(round(r, 6) for r in ratios)) == 1 and ratios[0] != 1:
                predicted = seq[-1] * ratios[0]
                if abs(cand_val - predicted) < 0.01:
                    return 1.0, f"geometric:ratio={ratios[0]},next={predicted}"
                return 0.0, f"geometric:expected={predicted}"

        # Check fibonacci-like: each = sum of previous two
        is_fib = all(abs(seq[i] - (seq[i-1] + seq[i-2])) < 0.01
                      for i in range(2, len(seq)))
        if is_fib and len(seq) >= 3:
            predicted = seq[-1] + seq[-2]
            if abs(cand_val - predicted) < 0.01:
                return 1.0, f"fibonacci:next={predicted}"
            return 0.0, f"fibonacci:expected={predicted}"

        # Check power: values are base^1, base^2, ...
        if seq[0] > 0:
            base = seq[1] / seq[0] if seq[0] != 0 else 0
            if base > 1:
                is_power = all(abs(seq[i] - seq[0] * (base ** i)) < 0.01
                               for i in range(len(seq)))
                if is_power:
                    predicted = seq[0] * (base ** len(seq))
                    if abs(cand_val - predicted) < 0.01:
                        return 1.0, f"power:base={base},next={predicted}"
                    return 0.0, f"power:expected={predicted}"

        # Check second differences (quadratic)
        if len(diffs) >= 2:
            dd = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
            if len(set(round(d, 6) for d in dd)) == 1 and dd[0] != 0:
                next_diff = diffs[-1] + dd[0]
                predicted = seq[-1] + next_diff
                if abs(cand_val - predicted) < 0.01:
                    return 1.0, f"quadratic:next={predicted}"
                return 0.0, f"quadratic:expected={predicted}"

        return 0.5, "no_sequence_pattern"


class StateEngine:
    """R4: Simulate state machines, register operations, and stack operations."""

    _STATE_TRANS = re.compile(
        r"[Ss]tate\s+(\w+)\s*\+?\s*input\s*'?(\w)'?\s*->\s*[Ss]tate\s+(\w+)")
    _REGISTER = re.compile(r"(\w)=(\w)([+\-*/])(\d+)")
    _START_VAL = re.compile(r"(?:start|begin|initial).*?(\w)\s*=\s*(-?\d+)", re.I)
    _PUSH = re.compile(r"[Pp]ush\s+(\d+)")
    _POP = re.compile(r"[Pp]op")
    _INPUT_SEQ = re.compile(r"input\s+sequence[:\s]+([01]+)", re.I)
    _START_STATE = re.compile(r"[Ss]tarting\s+(?:in\s+)?[Ss]tate\s+(\w+)")

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        prompt = parsed.get("raw", "")
        if len(prompt) > 2000:
            return 0.5, "prompt_too_long"
        cand_lower = candidate.strip()

        # Try state machine simulation
        transitions = self._STATE_TRANS.findall(prompt)
        if transitions:
            return self._simulate_state_machine(prompt, transitions, cand_lower)

        # Try register machine
        start_match = self._START_VAL.search(prompt)
        ops = self._REGISTER.findall(prompt)
        if start_match and ops:
            return self._simulate_register(prompt, start_match, ops, cand_lower)

        # Try stack operations
        pushes = self._PUSH.findall(prompt)
        pops = self._POP.findall(prompt)
        if pushes:
            return self._simulate_stack(prompt, cand_lower)

        # Try step-by-step computation: "Start with x=N. Step 1: x=x+M..."
        if "step" in prompt.lower() and "x=" in prompt.lower():
            return self._simulate_steps(prompt, cand_lower)

        return 0.5, "no_state_signal"

    def _simulate_state_machine(self, prompt, transitions, candidate):
        # Build transition table
        table = {}
        for state, inp, next_state in transitions:
            table.setdefault(state, {})[inp] = next_state

        # Find start state and input sequence
        start = self._START_STATE.search(prompt)
        seq = self._INPUT_SEQ.search(prompt)
        if not start or not seq:
            return 0.5, "incomplete_state_machine"

        current = start.group(1)
        for symbol in seq.group(1):
            if current in table and symbol in table[current]:
                current = table[current][symbol]
            else:
                return 0.5, f"undefined_transition:{current},{symbol}"

        if candidate == current:
            return 1.0, f"state_machine:final={current}"
        return 0.0, f"state_machine:expected={current},got={candidate}"

    def _simulate_register(self, prompt, start_match, ops, candidate):
        var = start_match.group(1)
        value = int(start_match.group(2))

        for _, _, op, operand in ops:
            n = int(operand)
            if op == '+': value += n
            elif op == '-': value -= n
            elif op == '*': value *= n
            elif op == '/' and n != 0: value = value // n

        try:
            if abs(float(candidate) - value) < 0.01:
                return 1.0, f"register:result={value}"
            return 0.0, f"register:expected={value}"
        except ValueError:
            return 0.5, "register:non_numeric_candidate"

    def _simulate_stack(self, prompt, candidate):
        stack = []
        # Process operations in order
        for token in re.finditer(r"(?:Push|Pop)\s*(\d*)", prompt, re.I):
            text = token.group(0).strip().lower()
            if text.startswith("push"):
                val = token.group(1)
                if val:
                    stack.append(int(val))
            elif text.startswith("pop") and stack:
                stack.pop()

        if not stack:
            return 0.5, "empty_stack"

        top = str(stack[-1])
        if candidate == top:
            return 1.0, f"stack:top={top}"
        return 0.0, f"stack:expected={top}"

    def _simulate_steps(self, prompt, candidate):
        # Parse "Start with x=N. Step K: x=x+M."
        start = re.search(r"x\s*=\s*(-?\d+)", prompt)
        if not start:
            return 0.5, "no_start_value"
        value = int(start.group(1))

        steps = re.findall(r"[Ss]tep\s+\d+:\s*x\s*=\s*x\s*([+\-*/])\s*(\d+)", prompt)
        for op, operand in steps:
            n = int(operand)
            if op == '+': value += n
            elif op == '-': value -= n
            elif op == '*': value *= n
            elif op == '/' and n != 0: value = value // n

        try:
            if abs(float(candidate) - value) < 0.01:
                return 1.0, f"steps:result={value}"
            return 0.0, f"steps:expected={value}"
        except ValueError:
            return 0.5, "steps:non_numeric_candidate"


class CausalEngine:
    """R5: Causal reasoning — distinguish correlation from causation."""

    _CAUSES = re.compile(r"(\w[\w\s]*?)\s+(?:causes|leads\s+to|results\s+in)\s+(\w[\w\s]*?)(?:\.|,|$)", re.I)
    _CORRELATION = re.compile(r"(?:correlat|associat|linked|related)", re.I)

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        prompt = parsed.get("raw", "")
        cand_lower = candidate.lower()

        # Check for correlation-vs-causation framing
        has_correlation_language = bool(self._CORRELATION.search(prompt))
        causal_edges = self._CAUSES.findall(prompt)

        # Key pattern: "correlation" in prompt -> answer is "Cannot determine" / "No"
        if has_correlation_language:
            if "can we conclude" in prompt.lower() or "does" in prompt.lower():
                if "cannot" in cand_lower or "no" in cand_lower:
                    return 0.9, "correlation_not_causation"
                elif "yes" in cand_lower:
                    return 0.1, "correlation_fallacy"

        # Build causal DAG
        if causal_edges:
            dag = defaultdict(set)
            for cause, effect in causal_edges:
                dag[cause.strip().lower()].add(effect.strip().lower())

            # Check if multiple causes lead to same effect (common effect)
            effects = defaultdict(list)
            for cause, effs in dag.items():
                for e in effs:
                    effects[e].append(cause)

            # Common-effect pattern: "X causes Z. Y causes Z. Z observed. Did X happen?"
            for effect, causes in effects.items():
                if len(causes) > 1 and effect in prompt.lower():
                    # Multiple causes -> cannot determine which one
                    if "cannot" in cand_lower or "no" in cand_lower:
                        return 0.8, f"common_effect:{effect}"

            # Direct causation check
            for cause, effs in dag.items():
                if cause in prompt.lower():
                    for e in effs:
                        if e in cand_lower or cand_lower in e:
                            return 0.7, f"causal_path:{cause}->{e}"

        # Post-hoc fallacy: "X happened before Y. Did X cause Y?"
        if "before" in prompt.lower() and "cause" in prompt.lower():
            if "cannot" in cand_lower or "no" in cand_lower:
                return 0.8, "post_hoc_fallacy"

        return 0.5, "no_causal_signal"


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
            (0.15, "chain", ForwardChainEngine()),
            (0.15, "order", OrderingEngine()),
            (0.20, "compute", ComputationEngine()),
            (0.10, "negate", NegationEngine()),
            (0.15, "sequence", SequenceEngine()),
            (0.15, "state", StateEngine()),
            (0.10, "causal", CausalEngine()),
        ]

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        parsed = self.parser.parse(prompt)

        results = []
        for candidate in candidates:
            total_score = 0.0
            total_weight = 0.0
            reasons = []

            for weight, name, engine in self.engines:
                try:
                    score, reason = engine.score(parsed, candidate)
                except Exception:
                    score, reason = 0.5, "engine_error"
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
