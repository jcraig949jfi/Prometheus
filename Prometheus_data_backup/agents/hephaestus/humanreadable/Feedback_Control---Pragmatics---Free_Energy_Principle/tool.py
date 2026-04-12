import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Active-Inference with Pragmatic-Guided Precision Control.
    
    Mechanism:
    1. Generative Model (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a 'prior' expectation of the answer structure.
    2. Pragmatic Evaluator (Gricean Maxims): Computes a 'relevance' score based on 
       keyword overlap and constraint satisfaction. This acts as the precision weight.
    3. Feedback Control (PID-style Gain): 
       - Error = Discrepancy between candidate length/content and prompt expectations.
       - Proportional: Immediate penalty for constraint violation.
       - Integral: Accumulated penalty for missing key logical operators.
       - Derivative: Penalty for abrupt deviations in semantic density (approximated).
    4. Free Energy Minimization: The final score is derived from minimizing the 
       weighted prediction error (Free Energy = Error / Precision).
    """

    def __init__(self):
        # Logical operators and comparators for structural parsing
        self.comparators = ['>', '<', '>=', '<=', 'greater', 'less', 'equal', 'more', 'fewer']
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.quantifiers = ['all', 'some', 'every', 'each', 'any']
        
        # Base precision parameters
        self.base_precision = 0.5
        self.pid_kp = 0.6  # Proportional gain
        self.pid_ki = 0.2  # Integral gain
        self.pid_kd = 0.1  # Derivative gain

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict:
        """Structural parsing to extract logical constraints."""
        tokens = self._tokenize(text)
        has_negation = any(n in tokens for n in self.negations)
        has_comparator = any(c in text for c in self.comparators) or any(c in tokens for c in self.comparators)
        has_conditional = any(c in tokens for c in self.conditionals)
        has_quantifier = any(q in tokens for q in self.quantifiers)
        
        # Numeric detection
        numbers = re.findall(r"[-+]?\d*\.?\d+", text)
        has_numbers = len(numbers) > 0
        
        return {
            'negation': has_negation,
            'comparator': has_comparator,
            'conditional': has_conditional,
            'quantifier': has_quantifier,
            'numbers': numbers,
            'length': len(tokens),
            'raw_numbers': numbers
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _pragmatic_relevance(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluates relevance based on Gricean Maxims (Quantity, Relation, Manner).
        Returns a precision weight (0.0 to 1.0).
        """
        score = 0.0
        count = 0

        # Relation: Does the candidate share logical operators with the prompt?
        # If prompt has negation, relevant candidates often acknowledge it or answer directly.
        if prompt_struct['negation']:
            # Simple heuristic: if prompt is negative, candidate shouldn't be random gibberish
            score += 0.5 if cand_struct['length'] > 2 else 0.1
            count += 0.5
        else:
            score += 0.5
            count += 0.5

        # Quantity: Information density match (rough approximation via number presence)
        if prompt_struct['numbers']:
            # If prompt has numbers, candidate having numbers is highly relevant (Relation/Quantity)
            if cand_struct['numbers']:
                score += 1.0
            else:
                score += 0.2
            count += 1.0
        else:
            score += 0.5
            count += 0.5

        # Manner: Clarity (approximated by length ratio stability)
        len_ratio = min(cand_struct['length'], prompt_struct['length']) / max(cand_struct['length'], prompt_struct['length'], 1)
        score += len_ratio
        count += 1.0

        return score / count if count > 0 else 0.1

    def _pid_controlled_error(self, prompt_struct: Dict, cand_struct: Dict, candidate: str) -> float:
        """
        Computes prediction error with PID-style gain tuning.
        Treats logical consistency as the setpoint.
        """
        error_terms = []

        # Proportional Term: Immediate structural mismatch
        # If prompt has numbers, candidate lacking them is a large error (unless it's a yes/no question context)
        p_term = 0.0
        if prompt_struct['numbers'] and not cand_struct['numbers']:
            # Check if candidate is a known non-numeric answer (Yes/No/True/False)
            lower_c = candidate.lower().strip()
            if lower_c not in ['yes', 'no', 'true', 'false', 'correct', 'incorrect']:
                p_term = 0.8
        error_terms.append(p_term)

        # Integral Term: Persistent bias (Length mismatch as proxy for completeness)
        # Large deviations in length suggest missing information (under-fitting) or verbosity (over-fitting)
        len_diff = abs(prompt_struct['length'] - cand_struct['length'])
        i_term = min(len_diff / 20.0, 1.0) * 0.5
        error_terms.append(i_term)

        # Derivative Term: Anticipating instability (Special char noise)
        # High special char ratio implies rapid fluctuation/noise
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', candidate))
        d_term = min(special_chars / 5.0, 1.0) * 0.3
        error_terms.append(d_term)

        # Weighted sum mimicking PID output
        total_error = (self.pid_kp * error_terms[0]) + \
                      (self.pid_ki * error_terms[1]) + \
                      (self.pid_kd * error_terms[2])
        
        return min(total_error, 1.0)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Minimizes Variational Free Energy.
        F = Error - (Precision * Complexity_reward)
        Here simplified to: Score = Precision * (1 - Error)
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Pragmatic Precision Weight
        precision = self._pragmatic_relevance(p_struct, c_struct, prompt, candidate)
        
        # 2. Prediction Error (PID controlled)
        error = self._pid_controlled_error(p_struct, c_struct, candidate)
        
        # 3. NCD as a tiebreaker for semantic similarity (low weight)
        ncd = self._compute_ncd(prompt, candidate)
        
        # Free Energy minimization objective:
        # We want high precision and low error.
        base_score = (1.0 - error) * precision
        
        # Adjust by NCD (if strings are too different semantically, penalize slightly)
        # But NCD is noisy, so keep weight low (0.1)
        final_score = base_score * 0.9 + (1.0 - ncd) * 0.1
        
        return max(0.0, min(1.0, final_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            reasoning = f"Precision-weighted error minimization. Structural match: {self._extract_structure(cand)}"
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score = self._compute_free_energy(prompt, answer)
        return round(score, 4)