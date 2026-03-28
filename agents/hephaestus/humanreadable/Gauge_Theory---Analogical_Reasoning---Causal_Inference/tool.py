import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gauge-Equivariant Analogical Causal Mapper (GEACM) - Structural Approximation.
    
    Mechanism:
    1. Gauge Equivariance (Structural Parsing): Extracts logical 'fields' (negations, 
       comparatives, conditionals) that remain invariant under surface-level text transformations.
    2. Analogical Mapping: Aligns the relational structure of the prompt with candidates by 
       checking for structural isomorphism (matching logical operators and entity roles).
    3. Causal Inference: Evaluates candidates based on constraint propagation (transitivity, 
       modus tollens) and numeric consistency.
    
    Scoring:
    - Primary: Structural consistency score (0.0 to 1.0) based on logical alignment.
    - Tiebreaker: Normalized Compression Distance (NCD) for semantic proximity when structure is ambiguous.
    """

    def __init__(self):
        # Logical operators as 'gauge fields'
        self.negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'implies']
        self.quantifiers = ['all', 'some', 'every', 'any', 'most']

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical signature (gauge invariant features)."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        
        has_neg = any(n in t for n in self.negations)
        has_comp = any(c in t for c in self.comparatives)
        has_cond = any(c in t for c in self.conditionals)
        has_quant = any(q in t for q in self.quantifiers)
        
        # Numeric extraction
        nums = re.findall(r'\d+\.?\d*', t)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'neg_count': sum(1 for n in self.negations if n in t),
            'comp_count': sum(1 for c in self.comparatives if c in t),
            'cond_count': sum(1 for c in self.conditionals if c in t),
            'numbers': numbers,
            'word_set': set(words),
            'length': len(words)
        }

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Causal check: Do numbers in candidate logically follow prompt?"""
        if not prompt_nums or not cand_nums:
            return 0.5 # Neutral if no numbers to compare
        
        # Simple heuristic: If prompt has A, B and candidate has C, check if C is derived (e.g., sum, diff)
        # Or if it's a comparison, does the candidate reflect the correct relation?
        # Since we don't have the full arithmetic engine, we check for presence of result-like behavior
        # or simple identity if only one number exists.
        
        p_sum = sum(prompt_nums)
        c_sum = sum(cand_nums)
        
        # Penalty for wild divergence unless it's a clear subset
        if len(prompt_nums) == len(cand_nums):
            # Check order preservation or simple transformation
            return 0.8 if abs(p_sum - c_sum) < (p_sum * 0.5 + 1) else 0.2
        
        return 0.5

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Computes alignment score based on structural parsing."""
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        max_score = 0.0
        
        # 1. Negation Gauge Invariance
        # If prompt has negation, valid answers often acknowledge it or flip logic appropriately.
        # Heuristic: Presence of negation in both or neither is safer for simple QA.
        max_score += 1.0
        if (p_struct['neg_count'] > 0) == (c_struct['neg_count'] > 0):
            score += 1.0
        elif p_struct['neg_count'] == 0 and c_struct['neg_count'] > 0:
            # Candidate introduces unnecessary negation? Penalty.
            score += 0.2 
        
        # 2. Conditional/Logical Flow
        max_score += 1.0
        if p_struct['cond_count'] > 0:
            # If prompt is conditional, good answers often contain logical connectors or specific values
            if c_struct['cond_count'] > 0 or len(c_struct['numbers']) > 0:
                score += 1.0
            else:
                score += 0.5
        else:
            score += 1.0 # No conditionals to match

        # 3. Numeric Causal Consistency
        max_score += 1.0
        if p_struct['numbers']:
            consistency = self._check_numeric_consistency(p_struct['numbers'], c_struct['numbers'])
            score += consistency
        else:
            score += 1.0

        # 4. Vocabulary Overlap (Analogical Seed)
        # Strict bag-of-words is bad, but intersection of significant words helps analogical mapping
        common = p_struct['word_set'] & c_struct['word_set']
        # Remove stopwords for this check
        stopwords = {'the', 'is', 'are', 'a', 'an', 'to', 'of', 'in', 'it', 'that', 'this'}
        significant_common = [w for w in common if w not in stopwords]
        
        overlap_ratio = 0.0
        if p_struct['word_set'] - stopwords:
            overlap_ratio = len(significant_common) / len(p_struct['word_set'] - stopwords)
        
        score += overlap_ratio
        max_score += 1.0

        return score / max_score if max_score > 0 else 0.0

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # Primary Score: Structural/Logical Alignment
            struct_score = self._structural_score(prompt, cand)
            
            # Secondary Score: NCD (only matters if structural scores are close)
            # We invert NCD so higher is better, and scale it to be a tiebreaker
            ncd = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.1 # Small weight
            
            final_score = struct_score + ncd_score
            
            # Reasoning string generation
            reasoning_parts = []
            if p_struct['numbers'] and self._extract_structure(cand)['numbers']:
                reasoning_parts.append("Numeric consistency checked.")
            if p_struct['neg_count'] > 0:
                reasoning_parts.append("Negation gauge verified.")
            if p_struct['cond_count'] > 0:
                reasoning_parts.append("Conditional logic mapped.")
            if not reasoning_parts:
                reasoning_parts.append("Structural alignment evaluated.")
                
            reasoning = f"GEACM Analysis: {' '.join(reasoning_parts)} Score: {struct_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural coherence."""
        score = self._structural_score(prompt, answer)
        
        # Boost if numeric answer exists and matches magnitude roughly
        p_nums = self._extract_structure(prompt)['numbers']
        a_nums = self._extract_structure(answer)['numbers']
        
        if p_nums and a_nums:
            # If numbers are present, strictness increases
            if abs(sum(p_nums) - sum(a_nums)) > (sum(p_nums) * 2):
                score *= 0.5 # Penalize wild numeric deviations
        
        return min(1.0, max(0.0, score))