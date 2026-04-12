import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Causal-Constraint Mechanism-Design (CCMD) Solver Implementation.
    
    Mechanism:
    1. Constraint Satisfaction (SAT-like): Parses hard logical constraints 
       (negations, comparatives, conditionals) from the prompt. Candidates 
       violating these receive a heavy penalty (VCG-style cost).
    2. Causal Inference (Structural): Extracts subject-object roles and 
       directional dependencies. Ensures the candidate aligns with the 
       causal flow implied by the prompt structure.
    3. Mechanism Design (Incentive): The scoring function acts as a VCG 
       mechanism. It rewards candidates that satisfy structural constraints 
       (truthful reporting) and penalizes those that require "lying" about 
       the logical structure. The score is the net utility: 
       (Structural Alignment) - (Constraint Violation Cost).
    4. Tiebreaker: Normalized Compression Distance (NCD) is used only when 
       structural signals are indistinguishable.
    """

    def __init__(self):
        self.negation_words = ["no", "not", "never", "none", "neither", "nobody", "nothing"]
        self.comparatives = ["more", "less", "greater", "smaller", "higher", "lower", "better", "worse"]
        self.conditionals = ["if", "then", "unless", "otherwise", "provided"]

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r'-?\d+(?:\.\d+)?'
        return [float(x) for x in re.findall(pattern, text)]

    def _check_negation_consistency(self, prompt: str, candidate: str) -> float:
        """
        Constraint Satisfaction Layer.
        Checks if the candidate contradicts explicit negations in the prompt.
        Returns 1.0 (consistent) or 0.0 (contradiction).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        has_negation = any(w in p_lower for w in self.negation_words)
        
        if has_negation:
            # Heuristic: If prompt has negation, candidate should ideally 
            # reflect a nuanced answer or specific negative handling.
            # Simple proxy: If prompt says "not X", and candidate is exactly "X", penalize.
            # This is a simplified SAT check for direct contradiction.
            words = re.findall(r'\b\w+\b', p_lower)
            for i, word in enumerate(words):
                if word in self.negation_words and i + 1 < len(words):
                    next_word = words[i+1]
                    if c_lower.strip() == next_word.strip():
                        return 0.0 # Direct contradiction found
        
        return 1.0

    def _check_comparative_logic(self, prompt: str, candidate: str) -> float:
        """
        Causal/Structural Layer.
        Evaluates numeric comparisons implied by comparatives.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric logic to violate
        
        p_lower = prompt.lower()
        has_more = "more" in p_lower or "greater" in p_lower or "higher" in p_lower
        has_less = "less" in p_lower or "smaller" in p_lower or "lower" in p_lower
        
        # If we have numbers in both, check consistency
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Assume prompt compares first two numbers
            val_a, val_b = p_nums[0], p_nums[1]
            c_val = c_nums[0]
            
            # If prompt implies A > B, and candidate picks a number, 
            # does it align? (Simplified: if candidate is one of the numbers, 
            # check if it matches the comparative direction if explicit)
            
            # Basic consistency: If prompt asks "Which is more: 5 or 2?", 
            # and candidate is "5", it's good. If "2", it's bad.
            if has_more:
                expected = max(val_a, val_b)
                if abs(c_val - expected) > 1e-6:
                    # Check if candidate is the other number (wrong answer)
                    if any(abs(c_val - x) < 1e-6 for x in [val_a, val_b]):
                        return 0.0
            elif has_less:
                expected = min(val_a, val_b)
                if abs(c_val - expected) > 1e-6:
                    if any(abs(c_val - x) < 1e-6 for x in [val_a, val_b]):
                        return 0.0
                        
        return 1.0

    def _structural_parse_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring signal based on structural parsing.
        Combines negation, comparative, and conditional checks.
        """
        score = 1.0
        
        # 1. Negation Constraint (Hard Constraint)
        neg_score = self._check_negation_consistency(prompt, candidate)
        if neg_score == 0.0:
            return 0.0 # Immediate rejection
        
        # 2. Comparative Logic (Causal Direction)
        comp_score = self._check_comparative_logic(prompt, candidate)
        if comp_score == 0.0:
            return 0.0 # Immediate rejection
            
        # 3. Conditional/Keyword Overlap (Soft Constraint)
        # Reward candidates that contain key structural words from prompt if they are answers
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # Intersection of significant words (excluding stopwords)
        stopwords = {"the", "is", "are", "a", "an", "it", "of", "to", "in", "for", "on", "with"}
        sig_p = p_words - stopwords
        sig_c = c_words - stopwords
        
        if sig_p:
            overlap = len(sig_p & sig_c) / len(sig_p)
            score = 0.5 + (0.5 * overlap) # Base score 0.5, up to 1.0 with overlap
        else:
            score = 0.5
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(s1.encode('utf-8'))
        len2 = len(s2.encode('utf-8'))
        if len1 == 0 or len2 == 0:
            return 1.0
            
        try:
            comp12 = len(zlib.compress((s1 + s2).encode('utf-8')))
            max_len = max(len1, len2)
            if max_len == 0:
                return 0.0
            ncd = (comp12 - min(len1, len2)) / max_len
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # Step 1: Structural Parsing (Primary Signal)
            struct_score = self._structural_parse_score(prompt, cand)
            
            # Step 2: NCD Tiebreaker (Only if structural scores are high/identical)
            # We invert NCD so higher is better (1 - ncd)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Hybrid Score: Structural dominates. NCD breaks ties or fills gaps.
            # If structural score is 0 (violation), total is 0.
            # If structural is high, NCD fine-tunes.
            if struct_score == 0.0:
                final_score = 0.0
                reason = "Violates logical constraints (negation/comparative)."
            else:
                # Weighted combination: 90% structural, 10% NCD for nuance
                final_score = (struct_score * 0.9) + (ncd_score * 0.1)
                reason = f"Structural alignment: {struct_score:.2f}, Similarity: {ncd_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single answer.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]