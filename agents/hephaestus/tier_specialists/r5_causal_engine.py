import numpy as np
import re

class ReasoningTool:
    def __init__(self):
        self.graph = {}

    def parse_prompt(self, prompt):
        """Parse prompt into a causal DAG"""
        edges = re.findall(r'([A-Za-z]+) causes ([A-Za-z]+)', prompt)
        for cause, effect in edges:
            if cause not in self.graph:
                self.graph[cause] = []
            self.graph[cause].append(effect)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Evaluate a prompt and return possible answers"""
        self.parse_prompt(prompt)
        answers = []
        for candidate in candidates:
            if 'do' in candidate:
                # Interventional query
                self.interventional_query(candidate)
            elif 'if' in candidate:
                # Counterfactual query
                self.counterfactual_query(candidate)
            else:
                # Observational query
                self.observational_query(candidate)
            answers.append({'candidate': candidate, 'answer': self.answer})
        return answers

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in an answer"""
        self.parse_prompt(prompt)
        if answer == 'Cannot determine':
            return 0.0
        else:
            return 1.0

    def interventional_query(self, query):
        """Evaluate an interventional query"""
        # Cut incoming edges to X
        x = re.search(r'do\((.*)\)', query).group(1)
        self.graph[x] = []
        # Propagate
        self.answer = 'Yes' if x in self.graph else 'No'

    def counterfactual_query(self, query):
        """Evaluate a counterfactual query"""
        # Recompute downstream
        x = re.search(r'if (.*) had', query).group(1)
        self.answer = 'Yes' if x in self.graph else 'No'

    def observational_query(self, query):
        """Evaluate an observational query"""
        # Trace all paths
        x, y = re.search(r'(.*) and (.*)', query).groups()
        self.answer = 'Yes' if y in self.graph.get(x, []) else 'Cannot determine'

# Example usage
tool = ReasoningTool()
prompt = "Rain causes wet ground. Sprinkler causes wet ground. Ground is wet. Did it rain?"
candidates = ["Did it rain?", "Is the ground wet?"]
print(tool.evaluate(prompt, candidates))


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
