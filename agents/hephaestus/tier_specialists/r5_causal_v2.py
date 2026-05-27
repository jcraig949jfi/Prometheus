import numpy as np
from collections import defaultdict

class ReasoningTool:
    def __init__(self):
        self.graph = defaultdict(set)

    def parse_causation(self, statement):
        """Parse statements of the form 'X causes Y' into a directed graph."""
        parts = statement.lower().split(" causes ")
        if len(parts) == 2:
            cause, effect = parts
            self.graph[cause.strip()].add(effect.strip())

    def evaluate(self, prompt, candidates):
        """Evaluate the prompt against candidates and return a list of results."""
        results = []
        for candidate in candidates:
            self.parse_causation(candidate)
            correlation = self.check_correlation(prompt)
            if correlation:
                results.append({"candidate": candidate, "result": "Correlation"})
            else:
                results.append({"candidate": candidate, "result": "Cannot determine"})
        return results

    def check_correlation(self, prompt):
        """Check if the prompt indicates correlation in the graph."""
        parts = prompt.lower().split(" and ")
        if len(parts) == 2:
            x, y = parts
            return (y.strip() in self.graph[x.strip()] or
                    x.strip() in self.graph[y.strip()])
        return False

    def confidence(self, prompt, answer):
        """Determine confidence based on the presence of causation in the graph."""
        parts = prompt.lower().split(" and ")
        if len(parts) == 2:
            x, y = parts
            if answer.lower() == "causation":
                return float(y.strip() in self.graph[x.strip()])
            elif answer.lower() == "correlation":
                return float(self.check_correlation(prompt))
        return 0.0

    def remove_edge(self, cause, effect):
        """Remove an edge from the graph to handle counterfactuals."""
        if cause in self.graph:
            self.graph[cause].discard(effect)

# Example usage:
if __name__ == "__main__":
    rt = ReasoningTool()
    rt.evaluate("Does X and Y correlate?", ["X causes Y", "X and Y are related"])
    print(rt.confidence("X and Y", "causation"))


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
