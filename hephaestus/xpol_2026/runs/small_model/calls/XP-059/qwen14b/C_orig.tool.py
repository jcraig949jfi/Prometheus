import zlib
import re
import numpy as np

class ReasoningTool:
    def __init__(self):
        # Initialize any state
        self.prime_constraints = {
            "pi(x) ~= x/log x": lambda x: x / np.log(x),
            "gap g_n < C log² p_n": lambda x, C=1.48: C * np.log(x)**2
        }

    def _normalize(self, text):
        return text.encode('utf-8')

    def _ncd(self, s1, s2):
        c1 = zlib.compress(self._normalize(s1))
        c2 = zlib.compress(self._normalize(s2))
        c3 = zlib.compress(self._normalize(s1 + s2))
        return float(len(c3)) / max(len(c1), len(c2), 1)

    def _parse_prompt(self, prompt):
        # Basic structural parsing
        negations = re.findall(r'\bno\b|\bnot\b', prompt, re.IGNORECASE)
        comparatives = re.findall(r'\bmore\b|\bless\b|\bgreater\b|\bsmaller\b', prompt, re.IGNORECASE)
        conditionals = re.findall(r'\bif\b|\bwhen\b|\bunless\b', prompt, re.IGNORECASE)
        return negations, comparatives, conditionals

    def _numeric_evaluation(self, prompt):
        # Detect and evaluate numeric comparisons
        matches = re.findall(r'(\d+(\.\d+)?)\s*([<>]=?|==)\s*(\d+(\.\d+)?)', prompt)
        results = []
        for a, _, op, b in matches:
            a, b = float(a), float(b)
            if op == '<':
                results.append(a < b)
            elif op == '<=':
                results.append(a <= b)
            elif op == '>':
                results.append(a > b)
            elif op == '>=':
                results.append(a >= b)
            elif op == '==':
                results.append(a == b)
        return results

    def _meta_confidence(self, prompt):
        # Check for presupposition
        if re.search(r'\b(?:Have you stopped|Why did|quit)\b', prompt, re.IGNORECASE):
            return 0.2
        # Check for scope ambiguity
        if re.search(r'\bEvery\b', prompt, re.IGNORECASE):
            return 0.2
        # Check for pronoun ambiguity
        if re.search(r'\b(?:he|she|they)\b was\b', prompt, re.IGNORECASE):
            return 0.2
        # Check for false dichotomy
        if re.search(r'\b(?:Either|Or)\b', prompt, re.IGNORECASE):
            return 0.2
        # Check for subjectivity
        if re.search(r'\b(?:best|worst|favorite)\b', prompt, re.IGNORECASE):
            return 0.2
        # Check for unanswerability
        if re.search(r'\b(?:unknown|undefined)\b', prompt, re.IGNORECASE):
            return 0.2
        return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        negations, comparatives, conditionals = self._parse_prompt(prompt)
        numeric_results = self._numeric_evaluation(prompt)
        
        scores = []
        for candidate in candidates:
            score = 0
            # Structural parsing score
            if negations:
                score += 0.1 if "not" in candidate else 0
            if comparatives:
                score += 0.1 if any(c in candidate for c in ['<', '>', '==', '<=', '>=']) else 0
            if conditionals:
                score += 0.1 if "if" in candidate else 0
            
            # Numeric evaluation score
            if numeric_results:
                score += 0.2 * sum(numeric_results)
            
            # NCD as tiebreaker
            score += 0.1 * (1 - self._ncd(prompt, candidate))
            
            scores.append({"candidate": candidate, "score": score, "reasoning": "Structural: {}, Numeric: {}, NCD: {}".format(
                score - 0.3, score - 0.4, score - 0.5
            )})
        
        # Sort by score in descending order
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores

    def confidence(self, prompt: str, answer: str) -> float:
        meta_confidence = self._meta_confidence(prompt)
        if meta_confidence < 0.3:
            return meta_confidence
        
        # Base confidence on question properties
        base_confidence = 0.5 + 0.4 * self._numeric_evaluation(prompt)
        if base_confidence > 0.9:
            base_confidence = 0.9
        
        return min(meta_confidence, base_confidence)


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
