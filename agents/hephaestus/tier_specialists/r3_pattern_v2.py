import math

import re
import numpy as np

class ReasoningTool:
    def evaluate(self, prompt, candidates):
        numbers = list(map(float, re.findall(r"-?\d+(?:\.\d+)?", prompt)))
        
        if len(numbers) > 1:
            # Check for arithmetic sequence
            if len(set(np.diff(numbers))) == 1:
                next_number = numbers[-1] + np.diff(numbers)[0]
            # Check for geometric sequence
            elif len(set(np.diff(np.log(numbers)))) == 1:
                next_number = numbers[-1] * np.exp(np.diff(np.log(numbers))[0])
            # Check for Fibonacci sequence
            elif len(numbers) > 2 and all(numbers[i] == numbers[i-1] + numbers[i-2] for i in range(2, len(numbers))):
                next_number = numbers[-1] + numbers[-2]
            # Check for powers sequence
            elif len(set(np.log(numbers))) == 1:
                next_number = numbers[-1] * numbers[-1] / numbers[-2]
            else:
                next_number = None
            
            if next_number is not None:
                scores = [1.0 if abs(float(candidate) - next_number) < 1e-6 else 0.0 for candidate in candidates]
                return [{'candidate': candidate, 'score': score} for candidate, score in zip(candidates, scores)]
        
        # Check for modular arithmetic
        if 'mod' in prompt:
            match = re.search(r'(\d+) mod (\d+)', prompt)
            if match:
                n, m = map(int, match.groups())
                answer = n % m
                scores = [1.0 if float(candidate) == answer else 0.0 for candidate in candidates]
                return [{'candidate': candidate, 'score': score} for candidate, score in zip(candidates, scores)]
        
        # Check for function composition
        if 'f(' in prompt and 'f(' in prompt[prompt.index('f(') + 2:]:
            match = re.search(r'f\((\d+)\)=([^\)]+), what is f\((f\((\d+)\))\)', prompt)
            if match:
                x, f_x, y = match.groups()
                f_x = eval(f_x.replace('x', y))
                answer = eval(f_x.replace('x', str(f_x)))
                scores = [1.0 if float(candidate) == answer else 0.0 for candidate in candidates]
                return [{'candidate': candidate, 'score': score} for candidate, score in zip(candidates, scores)]
        
        # Check for combinatorics
        if 'arrange' in prompt:
            match = re.search(r'(\d+) items', prompt)
            if match:
                n = int(match.group(1))
                answer = np.math.factorial(n)
                scores = [1.0 if float(candidate) == answer else 0.0 for candidate in candidates]
                return [{'candidate': candidate, 'score': score} for candidate, score in zip(candidates, scores)]
        
        # Fall back to basic NL scoring
        scores = [0.5 for _ in candidates]
        return [{'candidate': candidate, 'score': score} for candidate, score in zip(candidates, scores)]

    def confidence(self, prompt, answer):
        numbers = list(map(float, re.findall(r"-?\d+(?:\.\d+)?", prompt)))
        if len(numbers) > 1:
            # Check for arithmetic sequence
            if len(set(np.diff(numbers))) == 1:
                next_number = numbers[-1] + np.diff(numbers)[0]
            # Check for geometric sequence
            elif len(set(np.diff(np.log(numbers)))) == 1:
                next_number = numbers[-1] * np.exp(np.diff(np.log(numbers))[0])
            # Check for Fibonacci sequence
            elif len(numbers) > 2 and all(numbers[i] == numbers[i-1] + numbers[i-2] for i in range(2, len(numbers))):
                next_number = numbers[-1] + numbers[-2]
            # Check for powers sequence
            elif len(set(np.log(numbers))) == 1:
                next_number = numbers[-1] * numbers[-1] / numbers[-2]
            else:
                next_number = None
            
            if next_number is not None:
                return 1.0 if abs(float(answer) - next_number) < 1e-6 else 0.0
        
        # Check for modular arithmetic
        if 'mod' in prompt:
            match = re.search(r'(\d+) mod (\d+)', prompt)
            if match:
                n, m = map(int, match.groups())
                answer_mod = n % m
                return 1.0 if float(answer) == answer_mod else 0.0
        
        # Check for function composition
        if 'f(' in prompt and 'f(' in prompt[prompt.index('f(') + 2:]:
            match = re.search(r'f\((\d+)\)=([^\)]+), what is f\((f\((\d+)\))\)', prompt)
            if match:
                x, f_x, y = match.groups()
                f_x = eval(f_x.replace('x', y))
                answer_comp = eval(f_x.replace('x', str(f_x)))
                return 1.0 if float(answer) == answer_comp else 0.0
        
        # Check for combinatorics
        if 'arrange' in prompt:
            match = re.search(r'(\d+) items', prompt)
            if match:
                n = int(match.group(1))
                answer_comb = np.math.factorial(n)
                return 1.0 if float(answer) == answer_comb else 0.0
        
        # Fall back to basic NL scoring
        return 0.5


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
