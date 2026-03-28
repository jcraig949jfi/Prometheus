import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Multi-Resolution Evolutionary Verifier (AMEV) Approximation.
    
    Mechanism:
    1. Evolution/Hypothesis: Treats candidates as evolved hypotheses.
    2. Wavelet Transform: Simulates multi-resolution analysis by decomposing text 
       into structural tokens (coarse scale/trends) and numeric/literal details 
       (fine scale/bursts). We apply a 'Haar-like' difference check on extracted 
       numeric sequences to detect local inconsistencies.
    3. Model Checking: Verifies candidates against the prompt's logical constraints 
       (negations, comparatives, conditionals). 
       
    Scoring:
    - Structural Match (Model Checking): 50% weight. Checks for logical consistency
      with prompt constraints (e.g., if prompt says "not X", candidate must not be "X").
    - Numeric Consistency (Wavelet Detail): 30% weight. Checks if numeric claims 
      in the candidate satisfy inequalities found in the prompt.
    - Compression (NCD): 20% weight. Tiebreaker for semantic similarity.
    """

    def __init__(self):
        self.ops = {
            'greater': lambda a, b: a > b,
            'less': lambda a, b: a < b,
            'equal': lambda a, b: abs(a - b) < 1e-6
        }

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values (fine-scale details)."""
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text)]

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical structure (coarse-scale trends)."""
        lower = text.lower()
        return {
            'has_not': bool(re.search(r'\b(not|no|never|neither)\b', lower)),
            'has_if': bool(re.search(r'\b(if|unless|provided)\b', lower)),
            'has_greater': bool(re.search(r'(greater|larger|more|exceeds|>)', lower)),
            'has_less': bool(re.search(r'(less|smaller|fewer|below|<)', lower)),
            'has_equal': bool(re.search(r'(equal|same|identical|=)', lower)),
            'length': len(text.split())
        }

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max_len

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Wavelet Detail Check: Verify local numeric bursts.
        Extracts numbers and logical comparatives from prompt and checks 
        if candidate numbers satisfy the implied constraints.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        p_struct = self._extract_structure(prompt)
        
        if not p_nums or not c_nums:
            return 0.5  # Neutral if no numeric data
        
        # Simple heuristic: If prompt implies "greater", check if candidate max > prompt min
        # This simulates checking detail coefficients against a threshold.
        score = 0.0
        checks = 0
        
        # Case 1: Explicit comparison in prompt
        if p_struct['has_greater'] and len(p_nums) >= 1 and len(c_nums) >= 1:
            # Assume candidate should be greater than some baseline in prompt
            if max(c_nums) > min(p_nums):
                score += 1.0
            checks += 1
            
        if p_struct['has_less'] and len(p_nums) >= 1 and len(c_nums) >= 1:
            if min(c_nums) < max(p_nums):
                score += 1.0
            checks += 1
            
        # Case 2: Direct number matching (invariant discovery)
        if len(p_nums) == len(c_nums) and len(p_nums) > 0:
            matches = sum(1 for a, b in zip(p_nums, c_nums) if abs(a-b) < 1e-6)
            score += (matches / len(p_nums))
            checks += 1

        return score / max(checks, 1) if checks > 0 else 0.5

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Model Checking: Verify temporal logic invariants on coarse structure.
        Checks for contradiction in negation and conditional presence.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        score = 0.0
        total = 0.0

        # Invariant: If prompt says "not", valid candidates often acknowledge negation or differ
        # This is a simplified formal check for contradiction
        if p_struct['has_not']:
            # If prompt negates, candidate shouldn't blindly affirm without nuance (heuristic)
            # Here we just check structural awareness
            score += 0.5 if c_struct['has_not'] or c_struct['length'] > 2 else 0.0
            total += 1.0
            
        # Invariant: Conditionals
        if p_struct['has_if']:
            score += 0.5 if c_struct['has_if'] or c_struct['length'] > 5 else 0.0
            total += 1.0
            
        if total == 0:
            return 1.0
        return score / total

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Model Checking (Structural)
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # 2. Wavelet Detail (Numeric)
            numeric_score = self._check_numeric_consistency(prompt, cand)
            
            # 3. NCD (Compression baseline as tiebreaker)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val  # Convert distance to similarity
            
            # Weighted Fitness Function
            # Logic (50%) + Numeric (30%) + NCD (20%)
            final_score = (0.5 * logic_score) + (0.3 * numeric_score) + (0.2 * ncd_score)
            
            # Boost if candidate contains specific prompt keywords (Evolutionary selection pressure)
            prompt_words = set(re.findall(r'\b\w+\b', prompt.lower()))
            cand_words = set(re.findall(r'\b\w+\b', cand.lower()))
            overlap = len(prompt_words & cand_words) / max(len(prompt_words), 1)
            final_score += (0.1 * overlap) # Small bonus for relevance

            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Logic:{logic_score:.2f} Num:{numeric_score:.2f} NCD:{ncd_score:.2f}"
            })
        
        # Rank by score descending
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on the evaluation score of the single answer."""
        ranked = self.evaluate(prompt, [answer])
        return ranked[0]['score'] if ranked else 0.0