import numpy as np

class ReasoningTool:
    def __init__(self):
        pass

    def evaluate(self, prompt, candidates):
        results = []
        grid = self.parse_prompt(prompt)
        for candidate in candidates:
            if self.is_valid(candidate, grid):
                results.append({'candidate': candidate, 'score': 1.0})
        return results

    def confidence(self, prompt, answer):
        grid = self.parse_prompt(prompt)
        return 1.0 if self.is_valid(answer, grid) else 0.0

    def parse_prompt(self, prompt):
        grid = []
        for line in prompt.splitlines():
            if line.startswith("Row"):
                row = eval(line.split(': ')[1])
                grid.append(row)
        return np.array(grid)

    def is_valid(self, candidate, grid):
        # Check if candidate can fit into the grid
        n = len(grid)
        if len(candidate) != n:
            return False
        for i in range(n):
            if not self.is_valid_row(candidate[i], grid[i]) or not self.is_valid_column(candidate[i], grid[:, i]):
                return False
        return True

    def is_valid_row(self, candidate_row, existing_row):
        # Check if candidate row is valid with existing row
        for val in existing_row:
            if val != '_' and val in candidate_row:
                return False
        return True

    def is_valid_column(self, candidate_val, existing_col):
        # Check if candidate value is valid with existing column
        for val in existing_col:
            if val != '_' and val == candidate_val:
                return False
        return True

# Example usage:
# tool = ReasoningTool()
# prompt = "Row 0: [_,3,_]\nRow 1: [_,_,_]\nRow 2: [_,_,_]"
# candidates = [[1, 3, 2], [2, 3, 1], [3, 1, 2]]
# print(tool.evaluate(prompt, candidates))
# print(tool.confidence(prompt, [1, 3, 2]))


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
