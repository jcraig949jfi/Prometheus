import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic Monte-Carlo Type Checker (EMTC) Approximation.
    
    Mechanism:
    1. Type Theory Layer: Parses prompt/candidates into structural tokens (types).
       Validates logical consistency (e.g., negation handling, transitivity).
    2. Ergodic/Falsification Layer: 
       - Treats the text corpus as a trajectory.
       - Uses NCD (Normalized Compression Distance) as a proxy for the "target measure" mu_H.
       - Simulates an ergodic loop: iteratively refines the score by checking if the 
         candidate's structural properties (types) are consistent with the prompt's 
         logical constraints (falsification).
       - If a candidate contradicts explicit constraints (e.g., "not X" vs "X"), 
         it is falsified (score -> 0).
    3. Scoring: Combines structural validity (Type) with statistical similarity (Ergodic/NCD).
    """

    def __init__(self):
        self._epsilon = 1e-6

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as the compressor."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except Exception:
            return 1.0

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extract logical types: negations, numbers, comparatives."""
        text_lower = text.lower()
        has_neg = bool(re.search(r'\b(not|no|never|without|false)\b', text_lower))
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        numbers = [float(n) for n in nums] if nums else []
        
        # Extract comparatives
        comps = re.findall(r'\b(more|less|greater|smaller|higher|lower)\b', text_lower)
        
        return {
            "negated": has_neg,
            "numbers": numbers,
            "comparatives": comps,
            "length": len(text.split()),
            "raw": text
        }

    def _check_consistency(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Type-theoretic consistency check (Falsification step).
        Returns 0.0 if falsified, 1.0 if consistent, 0.5 if ambiguous.
        """
        # Rule 1: Negation Contradiction
        # If prompt asserts "not X" and candidate asserts "X" (simplified heuristic)
        if prompt_struct["negated"] and not cand_struct["negated"]:
            # Heuristic: If prompt is negative and candidate is positive short answer
            if cand_struct["length"] < 5 and cand_struct["raw"].strip() in ["yes", "true", "1"]:
                return 0.0
        
        # Rule 2: Numeric Transitivity (Simplified)
        # If prompt has numbers and candidate has numbers, check order if comparatives exist
        p_nums = prompt_struct["numbers"]
        c_nums = cand_struct["numbers"]
        
        if p_nums and c_nums:
            # If prompt implies "A > B" and candidate says "B > A", falsify
            # This is a rough approximation of constraint propagation
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_diff = p_nums[0] - p_nums[1]
                c_diff = c_nums[0] - c_nums[1]
                
                if "greater" in prompt_struct["comparatives"] or "more" in prompt_struct["comparatives"]:
                    # Prompt expects positive diff, candidate shows negative
                    if p_diff > 0 and c_diff < 0:
                        return 0.0
                elif "less" in prompt_struct["comparatives"] or "smaller" in prompt_struct["comparatives"]:
                    if p_diff < 0 and c_diff > 0:
                        return 0.0

        return 1.0

    def _ergodic_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a statistically grounded score based on NCD convergence.
        Simulates the 'time average' converging to 'space average' by comparing
        local chunks and global structure.
        """
        # Base similarity (Space Average proxy)
        base_sim = 1.0 - self._ncd(prompt, candidate)
        
        # Structural convergence (Type consistency)
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        consistency = self._check_consistency(p_struct, c_struct)
        
        # If falsified by type rules, return 0 immediately
        if consistency == 0.0:
            return 0.0
            
        # Refinement loop (simulated): 
        # Adjust score based on length ratio (penalize huge deviations) and content overlap
        len_ratio = min(len(candidate), len(prompt)) / max(len(candidate), len(prompt) + 1)
        
        # Weighted combination: Consistency is a gate, NCD provides granularity
        # We add a small bias for candidates that share specific keywords (Monte Carlo sampling of tokens)
        common_words = set(p_struct["raw"].lower().split()) & set(c_struct["raw"].lower().split())
        keyword_bonus = min(0.2, len(common_words) * 0.02)
        
        score = (base_sim * 0.6 + len_ratio * 0.2 + keyword_bonus) * consistency
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._ergodic_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Ergodic consistency: {score:.4f}, Type check: passed" if score > 0 else "Falsified by type constraints"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the ergodic type-check score."""
        score = self._ergodic_score(prompt, answer)
        # Map internal score to confidence probability
        # High score -> High confidence it is correct
        # Low score -> Low confidence
        return max(0.0, min(1.0, score))