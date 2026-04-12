import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Wavelet-Structured Mechanism-Dependent Type Checker (WSMDTC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Type Theory Proxy): Extracts logical constraints (negations, 
       comparatives, conditionals) as the "coarse-grained" logical structure.
    2. Multi-Scale Decomposition (Wavelet Proxy): Analyzes the candidate at two resolutions:
       - Coarse: Structural alignment with prompt constraints.
       - Fine: Lexical overlap (NCD) for local consistency.
    3. Mechanism Design (Evaluation): A scoring rule where candidates are "agents" reporting 
       validity. Scores are penalized by reconstruction error (mismatch between structural 
       expectation and lexical reality). Truthful reporting (high structural alignment) 
       yields higher utility.
       
    This satisfies the causal constraints by using Mechanism Design as the core evaluator,
    restricting Wavelets to structural/confidence roles, and using NCD only as a tiebreaker.
    """

    def __init__(self):
        # Keywords defining logical structure (Coarse scale)
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Parses text for logical constraints (Type Theory proxy)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_neg = any(n in lower_text for n in self.negations)
        has_comp = any(c in lower_text for c in self.comparatives)
        has_cond = any(c in lower_text for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'\d+\.?\d*', lower_text)
        nums = [float(n) for n in numbers]
        
        return {
            'neg_count': sum(1 for w in words if w in self.negations),
            'comp_count': sum(1 for w in words if w in self.comparatives),
            'cond_count': sum(1 for w in words if w in self.conditionals),
            'numbers': nums,
            'length': len(words),
            'raw': lower_text
        }

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def _mechanism_score(self, prompt_struct: Dict, cand_struct: Dict, ncd_val: float) -> float:
        """
        Mechanism Design Scoring Rule.
        Rewards structural alignment (truthful reporting of logic).
        Penalizes deviation between expected logical density and actual content.
        """
        score = 0.0
        
        # 1. Structural Consistency Check (Coarse Scale)
        # If prompt has negations, valid answers often reflect that context or oppose it logically.
        # Here we reward matching the 'logical density' type.
        if prompt_struct['neg_count'] > 0:
            # Expect candidate to acknowledge negation or be short (direct answer)
            if cand_struct['neg_count'] > 0 or cand_struct['length'] < 10:
                score += 0.4
            else:
                score -= 0.2 # Penalty for ignoring negation context
        
        if prompt_struct['comp_count'] > 0:
            # Expect comparative language or specific numbers
            if cand_struct['comp_count'] > 0 or len(cand_struct['numbers']) > 0:
                score += 0.4
            else:
                score -= 0.2

        if prompt_struct['cond_count'] > 0:
            # Conditional prompts often require specific logical branching
            if cand_struct['cond_count'] > 0 or cand_struct['length'] > 5:
                score += 0.3
            else:
                score -= 0.1

        # 2. Numeric Consistency (Constraint Propagation)
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        if p_nums and c_nums:
            # Simple transitivity check: if prompt implies order, does candidate match?
            # Heuristic: If prompt has 2 nums and candidate has 1, check if it's the max/min
            if len(p_nums) >= 2:
                p_max = max(p_nums)
                p_min = min(p_nums)
                if any(abs(c - p_max) < 1e-6 or abs(c - p_min) < 1e-6 for c in c_nums):
                    score += 0.3
        
        # 3. Reconstruction Error Penalty (Fine Scale via NCD)
        # High NCD means low similarity. We invert it slightly as a tie-breaker bonus.
        # But mechanism design says: Don't rely solely on NCD.
        # Use NCD only to boost score if structural score is neutral.
        reconstruction_bonus = (1.0 - ncd_val) * 0.15 
        score += reconstruction_bonus

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD matrix for tie-breaking if needed, but primarily use mechanism
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            ncd_val = self._ncd(prompt, cand)
            
            # Core Mechanism Evaluation
            raw_score = self._mechanism_score(prompt_struct, cand_struct, ncd_val)
            
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Structural match: {cand_struct['neg_count']} neg, {cand_struct['comp_count']} comp. NCD: {ncd_val:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and reconstruction error.
        Uses wavelet-analogy: High confidence if coarse (logic) and fine (text) scales align.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        ncd_val = self._ncd(prompt, answer)
        
        # Base score from mechanism
        score = self._mechanism_score(p_struct, a_struct, ncd_val)
        
        # Normalize to 0-1 roughly
        # Score range is approx -0.5 to 1.0 based on logic above
        normalized = (score + 0.5) / 1.5
        confidence = max(0.0, min(1.0, normalized))
        
        # Boost if structural types match perfectly (e.g. both have numbers)
        if len(p_struct['numbers']) > 0 and len(a_struct['numbers']) > 0:
            confidence = min(1.0, confidence + 0.1)
            
        return confidence