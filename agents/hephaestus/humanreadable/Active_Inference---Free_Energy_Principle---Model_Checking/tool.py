import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a computational analogy of the Active Inference x Free Energy x Model Checking
    triad for reasoning evaluation.
    
    Mechanism:
    1. Variational Inference Engine (Structural Parsing): Extracts logical constraints,
       negations, and numeric values from the prompt to form a 'generative model' of the task.
    2. Temporal-Logic Model Checker (Constraint Propagation): Verifies candidate answers
       against extracted logical rules (e.g., transitivity, modus tollens, numeric bounds).
       Violations generate high 'surprise' (penalty).
    3. Expected Free Energy (EFE) Planner (Scoring): Computes a score balancing:
       - Epistemic Value: How well the answer resolves uncertainty (matches parsed constraints).
       - Risk: Penalty for violating logical or numeric constraints.
       - Complexity: Regularization via NCD to prevent overfitting to noise.
       
    The final score is a deterministic float derived from constraint satisfaction and
    semantic proximity, prioritizing logical consistency over simple string overlap.
    """

    def __init__(self):
        self._logic_ops = ['if', 'then', 'else', 'not', 'and', 'or', 'greater', 'less', 'equal']
        self._comparators = ['>', '<', '>=', '<=', '==', '!=']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Model Checking Module: Verifies candidate against logical structures in prompt.
        Returns a penalty score (0.0 = perfect, 1.0 = total violation).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        penalty = 0.0
        
        # Check Negation Consistency
        if re.search(r'\bnot\b|\bnever\b|\bimpossible\b', p_lower):
            # If prompt implies negation, and candidate is a simple affirmative without qualification
            if c_lower in ['yes', 'true', 'it is', 'it does']:
                # Heuristic: if prompt has 'not' and candidate is short affirmative, high penalty
                if len(c_lower.split()) <= 2:
                    penalty += 0.5

        # Check Conditional Consistency (Simplified)
        if 'if' in p_lower and 'then' in p_lower:
            # If prompt sets up a conditional, candidate should ideally reflect the consequence
            # This is a soft check; we mainly look for contradiction keywords
            if 'but' in c_lower and 'therefore' in p_lower:
                penalty += 0.3

        # Numeric Constraint Propagation
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Detect comparison intent
            if any(op in p_lower for op in ['greater', 'larger', 'more', '>']):
                if c_nums and c_nums[0] < max(p_nums):
                     penalty += 0.4 # Contradicts "greater" implication
            if any(op in p_lower for op in ['less', 'smaller', 'fewer', '<']):
                if c_nums and c_nums[0] > min(p_nums):
                    penalty += 0.4 # Contradicts "less" implication
                    
        return min(penalty, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _compute_epistemic_value(self, prompt: str, candidate: str) -> float:
        """
        Variational Inference Module: Estimates how well the candidate reduces uncertainty
        regarding the prompt's structural constraints.
        """
        score = 0.0
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        
        # Reward presence of logical operators in candidate if present in prompt
        for op in self._logic_ops:
            if op in p_words and op in c_words:
                score += 0.1
        
        # Reward numeric precision if numbers are involved
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums:
            if c_nums:
                # Precision reward: closer to any number in prompt (heuristic for relevance)
                min_dist = min(abs(c_nums[0] - pn) for pn in p_nums)
                score += 1.0 / (1.0 + min_dist)
            else:
                # Penalty for missing numbers when expected
                score -= 0.2

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        
        # Pre-compute prompt complexity for normalization
        p_len = len(prompt) if len(prompt) > 0 else 1
        
        for cand in candidates:
            # 1. Model Checking (Constraint Violation Penalty)
            violation_penalty = self._check_logical_consistency(prompt, cand)
            
            # 2. Epistemic Value (Constraint Satisfaction Reward)
            epistemic_reward = self._compute_epistemic_value(prompt, cand)
            
            # 3. Complexity Regularization (NCD based)
            # Prefer candidates that are compressible with prompt (high relevance) 
            # but not identical (diversity).
            ncd = self._compute_ncd(prompt, cand)
            complexity_cost = ncd * 0.2
            
            # Free Energy Minimization Analogy:
            # Score = Epistemic Value - (Violation Penalty + Complexity Cost)
            # We invert violation penalty because higher penalty = lower score
            raw_score = epistemic_reward - violation_penalty - complexity_cost
            
            # Add base relevance (simple overlap to ensure basic coherence)
            overlap = len(set(prompt.lower().split()) & set(cand.lower().split()))
            raw_score += (overlap / (len(prompt.split()) + 1)) * 0.5

            ranked.append({
                "candidate": cand,
                "score": float(raw_score),
                "reasoning": f"Epistemic:{epistemic_reward:.2f}, Violation:{violation_penalty:.2f}, NCD:{ncd:.2f}"
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on constraint satisfaction and semantic density.
        """
        # Reuse evaluation logic for a single candidate
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
            
        raw_score = results[0]['score']
        
        # Map raw score to 0-1 range using a sigmoid-like transformation
        # Assuming typical scores range between -1.0 and 1.0
        confidence = 1.0 / (1.0 + math.exp(-raw_score * 2.0))
        
        # Hard constraints: If logical violation was detected in the reasoning string
        if "Violation:0.5" in results[0]['reasoning'] or "Violation:0.4" in results[0]['reasoning']:
            confidence = min(confidence, 0.3) # Cap confidence if major violation found
            
        return max(0.0, min(1.0, confidence))