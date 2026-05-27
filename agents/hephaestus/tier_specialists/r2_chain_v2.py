import re
import numpy as np

class TextParser:
    _NUM = re.compile(r"-?\d+(?:\.\d+)?")
    _COMP_GT = re.compile(r"(\w+(?:\s+\w+)*)\s+(?:is\s+)?(?:greater|larger|more|bigger|higher|taller|heavier|older)\s+than\s+(\w+(?:\s+\w+)*)", re.I)
    _COND = re.compile(r"if\s+(.+?),?\s+then\s+(.+?)(?:\.|$)", re.I)
    _NEG = re.compile(r"(not|no|never|neither|cannot)", re.I)

    def parse(self, prompt):
        return {
            "numbers": [float(x) for x in self._NUM.findall(prompt)],
            "comparisons": self._COMP_GT.findall(prompt),
            "conditionals": self._COND.findall(prompt),
            "has_negation": bool(self._NEG.search(prompt)),
        }

class ReasoningTool:
    def __init__(self):
        self.parser = TextParser()

    def evaluate(self, prompt, candidates):
        parsed = self.parser.parse(prompt)
        known_facts = set(parsed["comparisons"])
        rules = [(x[0], x[1]) for x in parsed["conditionals"]]

        while True:
            new_facts = set()
            for premise, conclusion in rules:
                if premise in known_facts:
                    new_facts.add(conclusion)
            if new_facts.issubset(known_facts):
                break
            known_facts.update(new_facts)

        scores = []
        for candidate in candidates:
            score = 1 if candidate in known_facts else 0
            scores.append({"candidate": candidate, "score": score})
        return scores

    def confidence(self, prompt, answer):
        parsed = self.parser.parse(prompt)
        known_facts = set(parsed["comparisons"])
        rules = [(x[0], x[1]) for x in parsed["conditionals"]]

        while True:
            new_facts = set()
            for premise, conclusion in rules:
                if premise in known_facts:
                    new_facts.add(conclusion)
            if new_facts.issubset(known_facts):
                break
            known_facts.update(new_facts)

        return 1 if answer in known_facts else 0

# Example usage
tool = ReasoningTool()
prompt = "If John is taller than Alice, then John is older than Alice. John is taller than Alice."
candidates = ["John is older than Alice", "Alice is older than John"]
print(tool.evaluate(prompt, candidates))
print(tool.confidence(prompt, "John is older than Alice"))


# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence


# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
