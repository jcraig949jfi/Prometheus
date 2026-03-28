import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Complexity-Sensitive Equilibrium-Tracking Algorithm (CETA) Approximation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, conditionals).
    2. Hypothesis Evaluation: Scores candidates based on constraint satisfaction (Payoff).
    3. Complexity Penalty: Uses NCD (approximating Kolmogorov complexity) to penalize verbose/unstable hypotheses.
    4. Phase Transition Detection: Applies a sigmoidal 'temperature' function to the net score. 
       This mimics the abrupt shift from disordered (high error/complexity) to ordered (low error/simple) states.
       Candidates that satisfy logic AND are concise cross the critical threshold (lambda*), receiving high scores.
    """

    def __init__(self):
        self.comparators = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower', '>', '<']
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _count_pattern(self, text: str, patterns: List[str]) -> int:
        lower_text = text.lower()
        return sum(1 for p in patterns if p in lower_text)

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Returns 1.0 if numeric logic holds, 0.5 if ambiguous, 0.0 if contradicted."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 0.5 # No numeric data to verify
        
        # Simple heuristic: If prompt implies an order and candidate respects it
        # Check for comparative keywords in prompt
        has_comp = any(c in prompt.lower() for c in self.comparators)
        
        if has_comp:
            # If prompt has comparators, we expect the candidate to reflect the sorted order or specific value
            # This is a simplified check: does the candidate contain the max/min correctly?
            p_max = max(p_nums)
            c_vals = c_nums
            
            # If prompt asks for largest/greater, candidate should likely contain the max
            if 'greater' in prompt.lower() or 'larger' in prompt.lower() or 'max' in prompt.lower():
                if c_vals and max(c_vals) == p_max:
                    return 1.0
                elif c_vals:
                    return 0.0 # Wrong number selected
            
            if 'less' in prompt.lower() or 'smaller' in prompt.lower() or 'min' in prompt.lower():
                p_min = min(p_nums)
                if c_vals and min(c_vals) == p_min:
                    return 1.0
                elif c_vals:
                    return 0.0

        # Fallback: exact match of numbers implies consistency
        if set(c_nums).issubset(set(p_nums)):
            return 1.0
            
        return 0.5

    def _check_structural_logic(self, prompt: str, candidate: str) -> float:
        """Checks negations and conditionals."""
        score = 0.0
        count = 0
        
        # Negation consistency
        p_neg = self._count_pattern(prompt, self.negations)
        c_neg = self._count_pattern(candidate, self.negations)
        
        # Heuristic: If prompt has strong negation, candidate should acknowledge it (either by repeating or answering appropriately)
        # This is hard to perfect without NLI, so we use a soft penalty for mismatched negation density
        if p_neg > 0:
            count += 1
            if c_neg > 0 or len(self._extract_numbers(candidate)) > 0: # Acknowledged complexity
                score += 1.0
            else:
                # Candidate ignores negation context, risky
                score += 0.5 
        else:
            count += 1
            score += 1.0 # No negation to worry about

        # Conditional presence
        if any(c in prompt.lower() for c in self.conditionals):
            count += 1
            # Candidate should ideally be a full sentence or structured answer if prompt is conditional
            if len(candidate.split()) > 1 or any(c in candidate.lower() for c in self.conditionals):
                score += 1.0
            else:
                score += 0.7
        else:
            count += 1
            score += 1.0

        return score / count if count > 0 else 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 0.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def _complexity_cost(self, candidate: str) -> float:
        """Approximates Kolmogorov Complexity cost via compression length."""
        try:
            return len(zlib.compress(candidate.encode('utf-8'))) / 1000.0
        except:
            return 1.0

    def _phase_transition_score(self, payoff: float, complexity: float, lambda_param: float = 0.5) -> float:
        """
        Computes the CETA score.
        Score = Payoff - lambda * Complexity
        Then applies a sigmoidal mapping to simulate the phase transition.
        High payoff + Low complexity -> Sharp rise to 1.0
        Low payoff or High complexity -> Drop to 0.0
        """
        net_energy = payoff - (lambda_param * complexity)
        
        # Sigmoid activation to simulate the abrupt phase transition at critical lambda
        # Shift so that net_energy > 0.5 maps to high probability
        k = 10.0  # Steepness of the transition
        x0 = 0.5  # Critical point
        
        try:
            score = 1.0 / (1.0 + math.exp(-k * (net_energy - x0)))
        except OverflowError:
            score = 1.0 if net_energy > x0 else 0.0
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features
        prompt_nums = self._extract_numbers(prompt)
        
        for cand in candidates:
            # 1. Structural Payoff (Nash Strategy: Minimize Error)
            struct_score = self._check_structural_logic(prompt, cand)
            numeric_score = self._check_numeric_logic(prompt, cand)
            
            # Weighted payoff: Numeric logic is often decisive in reasoning tasks
            payoff = 0.4 * struct_score + 0.6 * numeric_score
            
            # 2. Complexity Cost (Kolmogorov Penalty)
            # Shorter, compressible answers are preferred if payoff is equal
            complexity = self._complexity_cost(cand)
            
            # 3. CETA Scoring with Phase Transition
            final_score = self._phase_transition_score(payoff, complexity)
            
            # Tie-breaking with NCD if scores are extremely close (not primary driver)
            ncd_val = self._ncd(prompt, cand)
            
            reasoning = f"Structural:{struct_score:.2f} Numeric:{numeric_score:.2f} Complexity:{complexity:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the CETA score of the single answer."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']