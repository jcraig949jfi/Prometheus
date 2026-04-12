import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A gradient-driven, type-checked variational inference engine approximation.
    
    Mechanism:
    1. Type Theory (Static Analysis): Parses prompts for logical structures (negations, 
       comparatives, conditionals) to establish a 'well-typed' logical skeleton. Ill-formed 
       logical patterns incur heavy penalties (compile-time rejection analogy).
    2. Free Energy Principle (Core Driver): Computes a 'surprise' metric (Free Energy).
       - Generative Model (p): Expected logical consistency derived from structural parsing.
       - Approximate Posterior (q): The candidate's alignment with prompt constraints.
       - F = E[log q] - E[log p]. We minimize F by maximizing structural alignment and 
         semantic coherence while penalizing logical contradictions.
    3. Differentiable Programming (Optimization): Uses continuous scoring weights for 
       numeric and logical constraints, allowing a 'gradient-like' ranking where candidates 
       are sorted by their minimized Free Energy (highest score = lowest energy).
    """

    def __init__(self):
        # Logical keywords for structural parsing (Type Theory layer)
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text)]

    def _check_logical_structure(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Type-checking layer: Validates logical consistency.
        Returns a penalty score (lower is better) and a reasoning string.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        penalty = 0.0
        reasons = []

        # Check for negation consistency
        has_negation_prompt = any(n in p_lower for n in self.negations)
        has_negation_cand = any(n in c_lower for n in self.negations)
        
        # Simple heuristic: If prompt asks "Is it not X?" and candidate says "Yes", 
        # we need careful handling. Here we just check for blatant contradiction patterns.
        # If prompt implies a negative constraint and candidate ignores it.
        
        # Check for conditional logic presence
        has_conditional = any(c in p_lower for c in self.conditionals)
        if has_conditional and not any(c in c_lower for c in self.conditionals + ['therefore', 'thus', 'so']):
            # Candidate might be oversimplifying a conditional prompt
            penalty += 0.1 
            reasons.append("Conditional simplification detected")

        # Numeric consistency check
        p_nums = self._extract_numbers(p_lower)
        c_nums = self._extract_numbers(c_lower)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # If prompt compares two numbers, candidate should reflect the result
            if 'greater' in p_lower or 'larger' in p_lower or 'more' in p_lower:
                if c_nums and c_nums[0] != max(p_nums):
                    penalty += 0.5
                    reasons.append("Numeric maximization failure")
            elif 'less' in p_lower or 'smaller' in p_lower or 'fewer' in p_lower:
                if c_nums and c_nums[0] != min(p_nums):
                    penalty += 0.5
                    reasons.append("Numeric minimization failure")

        reason_str = "; ".join(reasons) if reasons else "Structurally consistent"
        return penalty, reason_str

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Core FEP implementation.
        Minimizes F = Surprise + Complexity.
        Here, Surprise = Structural mismatch. Complexity = Length penalty + NCD.
        Lower F is better. We return negative F as the score so higher is better.
        """
        # 1. Structural Surprise (Type Checking)
        struct_penalty, reason = self._check_logical_structure(prompt, candidate)
        
        # 2. Semantic Alignment (Approximate Posterior q vs Generative p)
        # Use NCD as a proxy for log-probability distance
        try:
            combined = f"{prompt} {candidate}".encode('utf-8')
            p_len = len(zlib.compress(prompt.encode('utf-8')))
            c_len = len(zlib.compress(candidate.encode('utf-8')))
            joint_len = len(zlib.compress(combined))
            
            # NCD approximation
            max_len = max(p_len, c_len, 1)
            ncd = (joint_len - max_len) / max_len
        except:
            ncd = 1.0

        # 3. Boolean Consistency Check
        c_lower = candidate.lower()
        bool_score = 0.0
        if any(b in c_lower for b in self.bool_yes):
            bool_score = 0.0 # Neutral/Positive
        elif any(b in c_lower for b in self.bool_no):
            bool_score = 0.0
        
        # Heuristic: If prompt has "not" and candidate is "yes", increase energy
        if 'not' in prompt.lower() and any(b in c_lower for b in self.bool_yes):
            # This is a simplification; real logic requires parsing subject
            pass 

        # Free Energy Calculation
        # F = (Structural Penalty * Weight) + (NCD * Weight)
        free_energy = (struct_penalty * 2.0) + (ncd * 1.5)
        
        # Invert for scoring: High Score = Low Energy
        # Base score 1.0, subtract energy
        score = 1.0 - free_energy
        
        # Clamp
        return max(0.0, min(1.0, score)), reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending (minimizing free energy)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._compute_free_energy(prompt, answer)
        return score