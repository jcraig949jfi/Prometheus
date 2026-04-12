import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    HIC-MDL Optimizer (Holographic Incentive-Compatible MDL).
    
    Mechanism:
    1. Structural Parsing (The Boundary): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid "boundary" representation.
    2. Mechanism Design (The Scoring Rule): Candidates are "experts" bidding on validity.
       They gain rewards for matching structural constraints and lose rewards for 
       violating them (strictly proper scoring rule analogy).
    3. Kolmogorov Approximation (The Prior): Used ONLY as a tie-breaking penalty 
       for excessive length/complexity when structural scores are equal, avoiding 
       direct reliance on K-complexity for primary logic.
    4. Holographic Analogy: The score represents the information density fit between 
       the prompt's logical surface area and the candidate's encoding.
    """

    def __init__(self):
        # Logical patterns for structural parsing
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r'\bfalse\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b']
        self.numeric_pattern = r'-?\d+\.?\d*'

    def _extract_structure(self, text: str) -> dict:
        """Parses text into a structural signature (The Boundary)."""
        text_lower = text.lower()
        has_neg = any(re.search(p, text_lower) for p in self.negation_patterns)
        has_comp = any(re.search(p, text_lower) for p in self.comparative_patterns)
        has_cond = any(re.search(p, text_lower) for p in self.conditional_patterns)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(self.numeric_pattern, text)]
        numbers.sort()
        
        return {
            "neg_count": sum(len(re.findall(p, text_lower)) for p in self.negation_patterns),
            "comp_count": sum(len(re.findall(p, text_lower)) for p in self.comparative_patterns),
            "cond_count": sum(len(re.findall(p, text_lower)) for p in self.conditional_patterns),
            "numbers": numbers,
            "length": len(text)
        }

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Evaluates numeric logic (e.g., transitivity, magnitude)."""
        if not prompt_nums or not cand_nums:
            return 0.0
        
        # Simple heuristic: Does the candidate preserve the order or magnitude relation?
        # If prompt has [2, 5] and candidate implies 5 > 2, score high.
        # Here we check if candidate numbers are a subset or consistent range.
        p_min, p_max = min(prompt_nums), max(prompt_nums)
        c_min, c_max = min(cand_nums), max(cand_nums)
        
        score = 0.0
        # Reward if candidate numbers fall within or logically extend prompt range
        if p_min <= c_min and c_max <= p_max:
            score += 0.5
        # Reward if candidate resolves a comparison correctly (heuristic)
        if len(prompt_nums) >= 2 and len(cand_nums) >= 1:
            if prompt_nums[-1] > prompt_nums[0] and c_max > c_min:
                score += 0.5
            elif prompt_nums[-1] < prompt_nums[0] and c_max < c_min:
                score += 0.5
        return score

    def _structural_match_score(self, prompt_struct: dict, cand_struct: dict) -> float:
        """
        Mechanism Design Layer: Scores the candidate based on structural alignment.
        This acts as the 'proper scoring rule' where experts (candidates) are rewarded
        for aligning with the prompt's logical constraints.
        """
        score = 0.0
        
        # Negation alignment: Candidate must reflect prompt's negation density roughly
        if prompt_struct["neg_count"] > 0:
            if cand_struct["neg_count"] > 0:
                score += 2.0  # Reward detecting negation
            else:
                score -= 5.0  # Heavy penalty for missing negation (critical failure)
        else:
            if cand_struct["neg_count"] > 0:
                score -= 1.0  # Slight penalty for hallucinating negation

        # Comparative alignment
        if prompt_struct["comp_count"] > 0:
            if cand_struct["comp_count"] > 0:
                score += 1.5
        elif cand_struct["comp_count"] > 0:
            score -= 0.5

        # Conditional alignment
        if prompt_struct["cond_count"] > 0:
            if cand_struct["cond_count"] > 0:
                score += 1.5
        
        # Numeric consistency
        if prompt_struct["numbers"] and cand_struct["numbers"]:
            score += self._check_numeric_consistency(prompt_struct["numbers"], cand_struct["numbers"])
        elif prompt_struct["numbers"] and not cand_struct["numbers"]:
            # Penalty if prompt has numbers but candidate ignores them completely
            score -= 0.5
            
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance (tie-breaker only)."""
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            if max(c1, c2) == 0: return 0.0
            return float(c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt compression for NCD tie-breaking
        prompt_comp = zlib.compress(prompt.encode())
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Primary Score: Structural/Mechanism Design alignment
            score = self._structural_match_score(prompt_struct, cand_struct)
            
            # 2. Secondary Score: NCD as tie-breaker (only if structural score is close)
            # We subtract a tiny fraction of NCD to break ties favoring similarity
            ncd_val = self._ncd_distance(prompt, cand)
            score -= (ncd_val * 0.001) 

            # 3. Kolmogorov Penalty (MDL): Penalize excessive length if scores are equal
            # Using length as proxy for complexity K(x) ~ |x|
            complexity_penalty = len(cand) * 1e-6
            score -= complexity_penalty

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match: {score:.4f}, NCD penalty: {ncd_val:.4f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment strength.
        Uses the internal scoring mechanism normalized to [0, 1].
        """
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]["score"]
        
        # Map raw score to 0-1 range
        # Heuristic: 
        # > 2.0: Very High confidence (strong structural match)
        # 0.0 to 2.0: Moderate
        # < 0.0: Low
        if raw_score >= 2.0:
            return 0.95
        elif raw_score >= 1.0:
            return 0.8
        elif raw_score >= 0.0:
            return 0.6
        elif raw_score >= -2.0:
            return 0.3
        else:
            return 0.1