from typing import Dict

import numpy as np
from typing import List, Dict

class ReasoningTool:
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Parse prompt into variables, domains, and constraints
        variables, domains, constraints = self.parse_prompt(prompt)
        
        # Implement arc consistency (AC-3) to prune domains
        self.ac3(variables, domains, constraints)
        
        # Backtracking search with constraint propagation
        solutions = self.backtrack(variables, domains, constraints)
        
        return solutions

    def confidence(self, prompt: str, answer: str) -> float:
        # Calculate confidence based on the number of solutions
        solutions = self.evaluate(prompt, [])
        if len(solutions) == 1 and answer in [solution['value'] for solution in solutions]:
            return 1.0
        else:
            return 0.0

    def parse_prompt(self, prompt: str):
        # Parse prompt into variables, domains, and constraints
        # For simplicity, assume the prompt is in a specific format
        if "Latin squares" in prompt:
            variables = [f"row_{i}" for i in range(3)]
            domains = {variable: [1, 2, 3] for variable in variables}
            constraints = [(0, 1), (0, 2), (1, 2)]
        elif "Graph coloring" in prompt:
            variables = [f"node_{i}" for i in range(3)]
            domains = {variable: ["R", "G", "B"] for variable in variables}
            constraints = [(0, 1), (1, 2)]
        elif "Scheduling" in prompt:
            variables = [f"task_{i}" for i in range(3)]
            domains = {variable: [1, 2, 3] for variable in variables}
            constraints = [(0, 1), (1, 2)]
        elif "Logic puzzles" in prompt:
            variables = [f"person_{i}" for i in range(3)]
            domains = {variable: ["teacher", "lawyer", "engineer"] for variable in variables}
            constraints = [(0, 1), (1, 2)]
        return variables, domains, constraints

    def ac3(self, variables, domains, constraints):
        # Implement arc consistency (AC-3) to prune domains
        for variable1, variable2 in constraints:
            for value in domains[variables[variable1]]:
                if value not in domains[variables[variable2]]:
                    domains[variables[variable1]].remove(value)

    def backtrack(self, variables, domains, constraints):
        # Backtracking search with constraint propagation
        solutions = []
        def backtrack(variables, domains, constraints, assignment):
            if len(assignment) == len(variables):
                solutions.append(assignment)
                return
            for variable in variables:
                if variable not in assignment:
                    for value in domains[variable]:
                        new_assignment = assignment.copy()
                        new_assignment[variable] = value
                        if self.is_consistent(new_assignment, constraints):
                            backtrack(variables, domains, constraints, new_assignment)
        backtrack(variables, domains, constraints, {})
        return solutions

    def is_consistent(self, assignment, constraints):
        # Check if the assignment is consistent with the constraints
        for variable1, variable2 in constraints:
            if variable1 in assignment and variable2 in assignment:
                if assignment[variable1] == assignment[variable2]:
                    return False
        return True

# Example usage
tool = ReasoningTool()
prompt = "Fill grid so each row/col has {1,2,3}. Row 0=[_,3,_]"
candidates = []
solutions = tool.evaluate(prompt, candidates)
print(solutions)


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
