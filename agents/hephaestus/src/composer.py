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


class ProbabilisticFallacyEngine:
    """R3: Detect probabilistic and logical fallacies.

    Handles: quantifier inversion, conditional probability asymmetry,
    conjunction fallacy, base rate neglect, expected value comparison.
    """

    _ALL_X_ARE_Y = re.compile(r"[Aa]ll\s+(\w+)\s+are\s+(\w+)")
    _PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
    _FRACTION = re.compile(r"(\d+)\s+in\s+(\d+)")
    _DOLLAR = re.compile(r"\$\s*(\d+(?:,\d+)*(?:\.\d+)?)")
    _CHANCE = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*chance\s+of\s+(?:winning\s+)?\$?\s*(\d+(?:,\d+)*(?:\.\d+)?)", re.I)

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        prompt = parsed.get("raw", "")
        prompt_l = prompt.lower()
        cand_lower = candidate.lower()

        # 1. Quantifier inversion: "All X are Y. Are all Y also X?" -> No
        universals = self._ALL_X_ARE_Y.findall(prompt)
        if universals:
            subj, pred = universals[0]
            # Check if question asks the inverse
            inverse_q = (f"all {pred.lower()}" in prompt_l and
                         ("also" in prompt_l or "are all" in prompt_l))
            if inverse_q:
                if "no" in cand_lower or "not necessarily" in cand_lower:
                    return 0.95, f"quantifier_inversion:all_{subj}_are_{pred}_not_reverse"
                if "yes" in cand_lower:
                    return 0.05, "quantifier_inversion:inverse_fallacy"

        # 2. Conditional probability asymmetry: P(B|A) != P(A|B)
        pcts = self._PERCENT.findall(prompt)
        if pcts and ("probability" in prompt_l or "likely" in prompt_l):
            # "X% of A are B. Is a B also an A?"
            if "is the probability" in prompt_l or "is a" in prompt_l:
                if any(w in prompt_l for w in ["same", "equal", "identical"]):
                    if "no" in cand_lower or "not" in cand_lower:
                        return 0.9, "cond_prob_asymmetry:not_same"
                    if "yes" in cand_lower:
                        return 0.1, "cond_prob_asymmetry:fallacy"

        # 3. Conjunction fallacy: P(A and B) <= P(A)
        if "which is more" in prompt_l or "which is less" in prompt_l:
            # Check if candidates differ by conjunction
            and_candidates = [c for c in [candidate] if " and " in c.lower()]
            simple_candidates = [c for c in [candidate] if " and " not in c.lower()]
            if and_candidates and ("more likely" in prompt_l or "more probable" in prompt_l):
                # Conjunction is LESS likely
                return 0.15, "conjunction_fallacy:conjunction_less_likely"
            if simple_candidates and ("more likely" in prompt_l or "more probable" in prompt_l):
                return 0.85, "conjunction_fallacy:simple_more_likely"

        # 4. Base rate neglect: compute Bayesian posterior
        fractions = self._FRACTION.findall(prompt)
        if fractions and pcts:
            try:
                base_num, base_denom = int(fractions[0][0]), int(fractions[0][1])
                base_rate = base_num / base_denom
                test_accuracy = float(pcts[0]) / 100.0
                false_positive = 1.0 - test_accuracy if len(pcts) < 2 else float(pcts[1]) / 100.0

                # P(disease|positive) = P(pos|disease)*P(disease) / P(pos)
                p_pos = test_accuracy * base_rate + false_positive * (1 - base_rate)
                posterior = (test_accuracy * base_rate) / p_pos if p_pos > 0 else 0

                # The correct answer is usually "low" (< 50%) for rare diseases
                try:
                    cand_num = cand_lower.replace("%", "").replace("about", "").replace("roughly", "").replace("approximately", "").strip()
                    cand_pct = float(cand_num)
                    if abs(cand_pct / 100 - posterior) < 0.15:
                        return 0.9, f"base_rate:posterior={posterior:.1%}"
                    else:
                        return 0.1, f"base_rate:expected={posterior:.1%},got={cand_pct}%"
                except ValueError:
                    if posterior < 0.5 and ("low" in cand_lower or "unlikely" in cand_lower):
                        return 0.8, f"base_rate:posterior_low={posterior:.1%}"
            except (ValueError, ZeroDivisionError):
                pass

        # 5. Expected value comparison
        chances = self._CHANCE.findall(prompt)
        if len(chances) >= 2:
            try:
                evs = []
                for pct_str, val_str in chances:
                    prob = float(pct_str) / 100
                    val = float(val_str.replace(",", ""))
                    evs.append((prob * val, f"{pct_str}%*${val_str}"))

                # Find which game has higher EV
                best_ev = max(evs, key=lambda x: x[0])
                # Check if candidate mentions the right game
                for i, (ev, desc) in enumerate(evs):
                    game_label = chr(65 + i)  # A, B, C
                    if game_label.lower() in cand_lower or f"game {game_label.lower()}" in cand_lower:
                        if ev == best_ev[0]:
                            return 0.9, f"expected_value:game_{game_label}=EV{ev:.0f}"
                        else:
                            return 0.1, f"expected_value:wrong_game"
            except (ValueError, IndexError):
                pass

        return 0.5, "no_probabilistic_signal"


class TemporalComputationEngine:
    """R4: Temporal and rate-based computation.

    Handles: inverse proportion, time duration across midnight,
    relative day arithmetic, frequency LCM, age reasoning,
    scheduling conflict detection.
    """

    _WORKERS_DAYS = re.compile(
        r"(\d+)\s+(\w+)\s+can\s+\w+.*?in\s+(\d+)\s+days", re.I)
    _HOW_MANY_DAYS = re.compile(
        r"[Hh]ow\s+many\s+days.*?(\d+)\s+(\w+)", re.I)
    _TIME_RANGE = re.compile(
        r"(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?\s*(?:to|-)\s*(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?",
        re.I)
    _TIME_SIMPLE = re.compile(
        r"(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?", re.I)
    _EVERY_N_DAYS = re.compile(r"every\s+(\d+)\s+days", re.I)
    _TODAY_IS = re.compile(r"[Tt]oday\s+is\s+(\w+day)", re.I)
    _AGE_IS = re.compile(r"(\w+)\s+is\s+(\d+)\s+years?\s+old", re.I)
    _AGE_TIMES = re.compile(r"(\w+)\s+is\s+(\d+)\s+times?\s+(?:as\s+old\s+as\s+)?(\w+)", re.I)
    _AGE_PLUS = re.compile(r"(\w+)\s+is\s+(\d+)\s+years?\s+older\s+than\s+(\w+)", re.I)

    DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    def score(self, parsed: dict, candidate: str) -> tuple[float, str]:
        prompt = parsed.get("raw", "")
        prompt_l = prompt.lower()
        cand_lower = candidate.lower().strip()

        try:
            cand_val = float(cand_lower.split()[0].replace(",", ""))
        except (ValueError, IndexError):
            cand_val = None

        # 1. Rate / inverse proportion
        workers_match = self._WORKERS_DAYS.search(prompt)
        how_many = self._HOW_MANY_DAYS.search(prompt)
        if workers_match and how_many:
            try:
                w1 = int(workers_match.group(1))
                d1 = int(workers_match.group(3))
                w2 = int(how_many.group(1))
                # workers * days = constant
                total_work = w1 * d1
                d2 = total_work / w2
                if cand_val is not None and abs(cand_val - d2) < 0.5:
                    return 1.0, f"inverse_proportion:{w1}*{d1}={total_work}/{w2}={d2}"
                elif cand_val is not None:
                    return 0.0, f"inverse_proportion:expected={d2}"
            except (ValueError, ZeroDivisionError):
                pass

        # 2. Time duration (including across midnight)
        times = self._TIME_SIMPLE.findall(prompt)
        if len(times) >= 2 and ("duration" in prompt_l or "how long" in prompt_l):
            try:
                def to_minutes(h, m, ampm):
                    h, m = int(h), int(m)
                    if ampm:
                        ampm = ampm.upper()
                        if ampm == "PM" and h != 12:
                            h += 12
                        elif ampm == "AM" and h == 12:
                            h = 0
                    return h * 60 + m

                start = to_minutes(*times[0])
                end = to_minutes(*times[1])
                if end < start:
                    duration = (24 * 60 - start) + end  # across midnight
                else:
                    duration = end - start

                hours = duration // 60
                mins = duration % 60
                duration_strs = [
                    f"{hours} hours and {mins} minutes",
                    f"{hours} hours {mins} minutes",
                    f"{hours}h {mins}m",
                    f"{hours}:{mins:02d}",
                ]

                for ds in duration_strs:
                    if ds.lower() in cand_lower or cand_lower in ds.lower():
                        return 1.0, f"duration:{duration}min={hours}h{mins}m"

                # Try numeric match (total minutes or hours)
                if cand_val is not None:
                    if abs(cand_val - duration) < 1:
                        return 1.0, f"duration_minutes:{duration}"
                    if abs(cand_val - hours) < 0.1 and mins == 0:
                        return 1.0, f"duration_hours:{hours}"
            except (ValueError, IndexError):
                pass

        # 3. Relative day arithmetic
        today_match = self._TODAY_IS.search(prompt)
        if today_match:
            today = today_match.group(1).lower()
            if today in self.DAYS:
                today_idx = self.DAYS.index(today)
                # Parse "day after tomorrow" = +2, "yesterday" = -1, etc.
                offset = 0
                parts = prompt_l.split("?")[0] if "?" in prompt_l else prompt_l
                if "day after tomorrow" in parts:
                    offset += 2
                elif "tomorrow" in parts:
                    offset += 1
                if "yesterday" in parts:
                    offset -= 1
                if "day before" in parts:
                    offset -= 1
                if "two days after" in parts:
                    offset += 2
                if "three days after" in parts:
                    offset += 3

                result_day = self.DAYS[(today_idx + offset) % 7]
                if cand_lower == result_day or result_day in cand_lower:
                    return 1.0, f"relative_day:{today}+{offset}={result_day}"
                elif cand_lower in self.DAYS:
                    return 0.0, f"relative_day:expected={result_day}"

        # 4. Frequency coincidence (LCM)
        every_matches = self._EVERY_N_DAYS.findall(prompt)
        if len(every_matches) >= 2:
            try:
                import math
                a, b = int(every_matches[0]), int(every_matches[1])
                lcm = (a * b) // math.gcd(a, b)
                if cand_val is not None and abs(cand_val - lcm) < 0.5:
                    return 1.0, f"lcm:{a},{b}={lcm}"
                elif cand_val is not None:
                    return 0.0, f"lcm:expected={lcm}"
            except ValueError:
                pass

        # 5. Age reasoning (solve linear equations)
        ages = {}
        for name, age_str in self._AGE_IS.findall(prompt):
            ages[name.lower()] = int(age_str)

        for name, mult_str, ref in self._AGE_TIMES.findall(prompt):
            ref_age = ages.get(ref.lower())
            if ref_age is not None:
                ages[name.lower()] = ref_age * int(mult_str)

        for name, diff_str, ref in self._AGE_PLUS.findall(prompt):
            ref_age = ages.get(ref.lower())
            if ref_age is not None:
                ages[name.lower()] = ref_age + int(diff_str)

        if ages and cand_val is not None:
            for name, age in ages.items():
                if abs(cand_val - age) < 0.5:
                    return 1.0, f"age:{name}={age}"
            # Check if any computed age matches
            all_ages = list(ages.values())
            if cand_val in all_ages or any(abs(cand_val - a) < 0.5 for a in all_ages):
                return 0.9, f"age_match:{cand_val}"

        # 6. Scheduling conflict
        ranges = self._TIME_RANGE.findall(prompt)
        if len(ranges) >= 2 and ("can you attend" in prompt_l or "conflict" in prompt_l
                                  or "overlap" in prompt_l):
            try:
                def parse_range(m):
                    h1, m1, ap1, h2, m2, ap2 = m
                    def to_min(h, m, ap):
                        h, m = int(h), int(m)
                        if ap:
                            ap = ap.upper()
                            if ap == "PM" and h != 12: h += 12
                            elif ap == "AM" and h == 12: h = 0
                        return h * 60 + m
                    return to_min(h1, m1, ap1), to_min(h2, m2, ap2)

                intervals = [parse_range(r) for r in ranges]
                # Check overlap
                has_conflict = False
                for i in range(len(intervals)):
                    for j in range(i + 1, len(intervals)):
                        s1, e1 = intervals[i]
                        s2, e2 = intervals[j]
                        if s1 < e2 and s2 < e1:
                            has_conflict = True

                if not has_conflict:
                    if "yes" in cand_lower:
                        return 0.9, "no_conflict:can_attend"
                    if "no" in cand_lower:
                        return 0.1, "no_conflict:wrong"
                else:
                    if "no" in cand_lower:
                        return 0.9, "has_conflict:cannot_attend"
                    if "yes" in cand_lower:
                        return 0.1, "has_conflict:wrong"
            except (ValueError, IndexError):
                pass

        return 0.5, "no_temporal_signal"


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
            (0.12, "chain", ForwardChainEngine()),
            (0.12, "order", OrderingEngine()),
            (0.15, "compute", ComputationEngine()),
            (0.08, "negate", NegationEngine()),
            (0.12, "sequence", SequenceEngine()),
            (0.10, "state", StateEngine()),
            (0.05, "causal", CausalEngine()),
            (0.14, "prob_fallacy", ProbabilisticFallacyEngine()),
            (0.12, "temporal", TemporalComputationEngine()),
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
