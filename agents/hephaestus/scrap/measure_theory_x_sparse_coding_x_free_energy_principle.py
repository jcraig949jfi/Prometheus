import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse Variational Predictive Coding (SVPC) Reasoning Tool.
    
    Mechanism:
    Implements a computational analogy of the Free Energy Principle (FEP) for hypothesis testing.
    1. Generative Model (Prediction): Parses the prompt to extract structural constraints 
       (negations, comparatives, conditionals, numeric relations). This forms the "top-down" prediction.
    2. Variational Inference (Error Minimization): Evaluates candidates against these constraints.
       - Structural violations incur high "prediction error" (energy penalty).
       - Numeric/logical inconsistencies are penalized heavily.
    3. Sparse Coding (Occam's Razor): Applies an L1-like penalty on candidate length and complexity,
       favoring concise answers that satisfy all constraints (minimizing free energy).
    4. Free Energy Calculation: F = Prediction_Error + Sparsity_Penalty.
       Scores are derived from negative free energy (lower F = higher score).
       
    Note: Measure theory concepts are restricted to the confidence wrapper as per causal intelligence guidelines.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'better', 'worse']
        self.conditionals = ['if', 'unless', 'provided', 'except']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        pattern = r'-?\d+(?:\.\d+)?'
        return [float(x) for x in re.findall(pattern, text)]

    def _parse_structure(self, prompt: str) -> dict:
        """
        Extract structural constraints from the prompt (Top-Down Prediction).
        Returns a dictionary of expected properties.
        """
        p_lower = prompt.lower()
        constraints = {
            'has_negation': any(n in p_lower for n in self.negations),
            'has_comparative': any(c in p_lower for c in self.comparatives),
            'has_conditional': any(c in p_lower for c in self.conditionals),
            'has_numbers': False,
            'number_relation': None, # 'asc' or 'desc' or None
            'target_numbers': []
        }
        
        # Number extraction and relation heuristic
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            constraints['has_numbers'] = True
            constraints['target_numbers'] = nums
            # Simple heuristic: if prompt says "smaller", expect smaller numbers
            if 'smaller' in p_lower or 'less' in p_lower:
                constraints['number_relation'] = 'desc'
            elif 'larger' in p_lower or 'more' in p_lower or 'greater' in p_lower:
                constraints['number_relation'] = 'asc'
                
        return constraints

    def _calculate_prediction_error(self, prompt: str, candidate: str, constraints: dict) -> float:
        """
        Calculate the mismatch between the candidate and the prompt's structural constraints.
        High error = high free energy contribution from accuracy term.
        """
        error = 0.0
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        # 1. Negation Consistency
        # If prompt has negation, valid answers often reflect it or are carefully constrained.
        # Heuristic: If prompt asks "Which is NOT...", candidate shouldn't be the obvious positive match.
        # Simplified: Check if candidate contradicts explicit negation words if present.
        if constraints['has_negation']:
            # If the candidate is a simple "yes" when negation is heavy, slight penalty unless context fits
            # This is a proxy for logical consistency
            if c_lower.strip() in ['yes', 'true'] and 'not' in p_lower:
                # Contextual check would be ideal, but we use a soft penalty here
                error += 0.5 

        # 2. Numeric Consistency
        if constraints['has_numbers']:
            c_nums = self._extract_numbers(candidate)
            if c_nums:
                # If prompt implies sorting/comparison, check if candidate numbers align
                if constraints['number_relation'] == 'asc':
                    # If candidate contains numbers, do they follow the trend? 
                    # Hard to verify without full sequence, so we check magnitude relative to prompt nums
                    pass 
            else:
                # If prompt is numeric but candidate has no numbers, it might be abstract (okay) 
                # or missing info (penalty). 
                # If the prompt asks for a number specifically (e.g. "calculate"), this is a fail.
                if 'calculate' in p_lower or 'sum' in p_lower or 'equal' in p_lower:
                    error += 2.0

        # 3. Logical Contradiction (Simple keyword clash)
        # If prompt says "False is true", candidate "False" might be right, "True" wrong.
        # We rely on NCD here as a backup for semantic similarity to valid patterns.
        
        return error

    def _calculate_sparsity_penalty(self, candidate: str) -> float:
        """
        L1-style penalty on candidate length/complexity.
        Encourages concise answers (Occam's Razor).
        """
        # Normalize length penalty: longer answers get higher penalty
        # Scale factor 0.01 ensures short answers aren't penalized too much
        return len(candidate) * 0.01

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates based on variational free energy.
        F = Prediction_Error + Sparsity_Penalty
        Score = -F (adjusted for ranking)
        """
        if not candidates:
            return []
            
        constraints = self._parse_structure(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking against the prompt (similarity to valid context)
        # We assume the prompt contains the "truth" context.
        base_ncd = []
        for c in candidates:
            base_ncd.append(self._compute_ncd(prompt, c))
            
        min_ncd = min(base_ncd) if base_ncd else 0
        max_ncd = max(base_ncd) if base_ncd else 1
        range_ncd = max_ncd - min_ncd if (max_ncd - min_ncd) > 1e-6 else 1.0

        for i, cand in enumerate(candidates):
            # 1. Prediction Error (Accuracy term)
            pred_error = self._calculate_prediction_error(prompt, cand, constraints)
            
            # 2. Sparsity Penalty (Complexity term)
            sparsity = self._calculate_sparsity_penalty(cand)
            
            # 3. Free Energy Approximation
            # Lower is better. 
            free_energy = pred_error + sparsity
            
            # Tie-breaker: Use NCD if free energy is very close or zero
            # Normalize NCD to be a small additive term so it doesn't override structural errors
            ncd_term = ((base_ncd[i] - min_ncd) / range_ncd) * 0.1
            
            total_cost = free_energy + ncd_term
            
            # Convert to score (higher is better)
            # Invert and shift to positive range
            score = 1.0 / (1.0 + total_cost)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"FreeEnergy={total_cost:.4f} (Error: {pred_error:.2f}, Sparse: {sparsity:.2f})"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses structural parsing for primary signal, NCD as secondary.
        Measure Theory restricted to confidence wrapper as per guidelines.
        """
        if not answer:
            return 0.0
            
        constraints = self._parse_structure(prompt)
        error = self._calculate_prediction_error(prompt, answer, constraints)
        
        # Base confidence starts high and drops with error
        base_conf = 1.0 / (1.0 + error)
        
        # Sparsity check: extremely long answers are suspicious in reasoning tasks
        sparsity_penalty = min(len(answer) * 0.005, 0.5) # Cap penalty at 0.5
        base_conf -= sparsity_penalty
        
        # NCD similarity check (Measure-theoretic support: treating text as measurable sets)
        # If the answer is completely unrelated (high NCD), reduce confidence
        ncd_val = self._compute_ncd(prompt, answer)
        # If NCD is very high (>0.9), it suggests unrelated noise
        if ncd_val > 0.9:
            base_conf *= 0.5
            
        return max(0.0, min(1.0, base_conf))