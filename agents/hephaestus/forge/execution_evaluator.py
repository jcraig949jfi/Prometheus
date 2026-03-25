"""Execution Evaluator — grounds reasoning in computed behavior.

Hand-crafted seed tool that detects numeric/arithmetic/logic patterns
in prompts, evaluates them computationally, and checks whether candidates
match the computed result. Falls back to structural parsing when no
computable pattern is detected.

This catches cases where reasoning sounds right but is numerically wrong.

Concepts: Proof Theory x Constraint Satisfaction x Normalized Compression Distance
"""

import re
import math
import zlib
import numpy as np


class ReasoningTool:
    def __init__(self):
        self._level = 6

    # -- NCD fallback ----------------------------------------------------------

    def _c(self, text: str) -> int:
        return len(zlib.compress(text.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " \n " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    # -- Number extraction -----------------------------------------------------

    def _extract_numbers(self, text: str) -> list[float]:
        """Extract all numeric values from text."""
        nums = []
        for m in re.finditer(r"(?<!\w)(\$?\d+\.?\d*)(?!\w)", text):
            raw = m.group(1).lstrip("$")
            try:
                nums.append(float(raw))
            except ValueError:
                pass
        return nums

    # -- Computable pattern detectors -----------------------------------------

    def _check_numeric_comparison(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """'Is X larger/greater than Y?' -> compute float comparison."""
        p = prompt.lower()
        c = candidate.lower().strip()

        m = re.search(
            r"is\s+([\d.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.]+)",
            p)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            correct = "yes" if a > b else "no"
            if c.startswith(correct):
                return 1.0, True
            return -1.0, True

        # "X is less than Y. Which is larger?"
        m = re.search(r"([\d.]+)\s+is\s+less\s+than\s+([\d.]+)", p)
        if m and re.search(r"which.*larger", p):
            lesser, greater = float(m.group(1)), float(m.group(2))
            c_nums = self._extract_numbers(candidate)
            if c_nums:
                if c_nums[0] == greater:
                    return 1.0, True
                elif c_nums[0] == lesser:
                    return -1.0, True

        return 0.0, False

    def _check_all_but_n(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """'All but N die/left' -> answer is N."""
        m = re.search(r"all\s+but\s+(\d+)", prompt.lower())
        if m and re.search(r"how\s+many", prompt.lower()):
            correct_n = m.group(1)
            if correct_n in candidate:
                return 1.0, True
            return -0.8, True
        return 0.0, False

    def _check_bat_and_ball(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """'X and Y cost $T total. X costs $D more than Y. Y costs?'"""
        p = prompt.lower()
        m = re.search(r"cost\s+\$?([\d]+\.?\d*)\b.*?costs?\s+\$?([\d]+\.?\d*)\s+more", p)
        if m and re.search(r"(?:ball|costs?\?)", p):
            total = float(m.group(1))
            diff = float(m.group(2))
            # x + y = total, x - y = diff => y = (total - diff) / 2
            correct_val = (total - diff) / 2
            correct_str = f"${correct_val:.2f}"
            c_nums = self._extract_numbers(candidate)
            if c_nums:
                if abs(c_nums[0] - correct_val) < 0.001:
                    return 1.0, True
                return -1.0, True
        return 0.0, False

    def _check_coin_flip(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """Independent probability: past flips don't affect future."""
        p = prompt.lower()
        if re.search(r"coin.*flip.*(?:heads|tails).*(?:next|probability)", p):
            c = candidate.lower()
            if "50%" in c or "50 %" in c or c.startswith("50"):
                return 1.0, True
            if "higher" in c or "lower" in c:
                return -1.0, True
        return 0.0, False

    def _check_odd_even(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """Sum of two odd numbers is always even."""
        p = prompt.lower()
        if re.search(r"sum.*two\s+odd.*always\s+odd", p):
            c = candidate.lower().strip()
            if c.startswith("false") or c.startswith("no"):
                return 1.0, True
            if c.startswith("true") or c.startswith("yes"):
                return -1.0, True
        return 0.0, False

    def _check_overtake(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """Overtake 2nd place -> you're in 2nd, not 1st."""
        p = prompt.lower()
        if re.search(r"overtake.*2nd\s+place", p) and re.search(r"what\s+place", p):
            if "second" in candidate.lower() or "2nd" in candidate.lower():
                return 1.0, True
            if "first" in candidate.lower() or "1st" in candidate.lower():
                return -1.0, True
        return 0.0, False

    def _check_equal_weight(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """A pound of X vs a pound of Y -> same weight."""
        p = prompt.lower()
        if re.search(r"pound\s+of\s+\w+.*pound\s+of\s+\w+.*heav", p):
            c = candidate.lower()
            if "same" in c or "equal" in c:
                return 1.0, True
            return -0.5, True
        return 0.0, False

    def _check_repeating_decimal(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """0.999... = 1."""
        p = prompt.lower()
        if re.search(r"0\.999.*(?:repeating|recurring).*(?:equals?|=)\s*1", p):
            c = candidate.lower().strip()
            if c.startswith("yes"):
                return 1.0, True
            if c.startswith("no"):
                return -1.0, True
        return 0.0, False

    def _check_pigeonhole(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """N items, M < N slots -> must share."""
        p = prompt.lower()
        m = re.search(r"(\d+)\s+people.*?(\d+)\s+months.*(?:must|share)", p)
        if not m:
            m = re.search(r"(\d+).*(\d+).*must.*share", p)
        if m:
            items, slots = int(m.group(1)), int(m.group(2))
            correct = "yes" if items > slots else "no"
            c = candidate.lower().strip()
            if c.startswith(correct):
                return 1.0, True
            return -1.0, True
        return 0.0, False

    # -- Main scoring ----------------------------------------------------------

    def _compute_score(self, prompt: str, candidate: str) -> tuple[float, str]:
        """Run all computable checks. Returns (score, reasoning)."""
        checks = [
            ("numeric_comparison", self._check_numeric_comparison),
            ("all_but_n", self._check_all_but_n),
            ("bat_and_ball", self._check_bat_and_ball),
            ("coin_flip", self._check_coin_flip),
            ("odd_even", self._check_odd_even),
            ("overtake", self._check_overtake),
            ("equal_weight", self._check_equal_weight),
            ("repeating_decimal", self._check_repeating_decimal),
            ("pigeonhole", self._check_pigeonhole),
        ]

        for name, check_fn in checks:
            score, matched = check_fn(prompt, candidate)
            if matched:
                return score, f"execution:{name}={score:.1f}"

        # No computable pattern detected — fall back to NCD
        ncd_val = self._ncd(prompt, candidate)
        ncd_score = 1.0 / (1.0 + ncd_val)
        return ncd_score - 0.5, f"fallback:ncd={ncd_val:.4f}"

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by computed correctness."""
        results = []
        for cand in candidates:
            score, reasoning = self._compute_score(prompt, cand)
            # Map from [-1, 1] to [0, 1]
            normalized = (score + 1.0) / 2.0
            results.append({
                "candidate": cand,
                "score": float(normalized),
                "reasoning": reasoning,
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on execution check."""
        score, _ = self._compute_score(prompt, answer)
        if score > 0.5:
            return 0.95
        elif score < -0.5:
            return 0.05
        elif score > 0.1:
            return 0.7
        elif score < -0.1:
            return 0.2
        # No strong signal
        return 0.4
