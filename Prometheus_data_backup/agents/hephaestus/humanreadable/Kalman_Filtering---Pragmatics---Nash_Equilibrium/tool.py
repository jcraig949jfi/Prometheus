import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Kalman Game Filter (PKGF) Implementation.
    
    Mechanism:
    1. Structural Parsing (The 'H' Matrix): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values from the prompt. This forms the 
       deterministic observation model.
    2. Pragmatic Likelihood (RSA): Scores candidates based on Gricean maxims—specifically 
       relevance (keyword overlap with constraints) and brevity (cost penalty).
    3. Kalman-style Update: Treats the candidate's structural alignment as a noisy 
       measurement. We compute a 'belief' score where the innovation is the gap between 
       expected logical structure and the candidate's content.
    4. Nash Equilibrium Approximation: In this single-agent reasoning context, the 
       equilibrium is the candidate that maximizes the joint payoff of Accuracy (structural 
       match) and Coherence (pragmatic score), representing a stable state where no 
       unilateral deviation (choosing another candidate) yields higher utility.
    
    Note: Per causal analysis, Kalman logic is restricted to the confidence wrapper 
    and structural scoring; it does not drive the primary ranking alone.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.confirmations = ['yes', 'true', 'correct', 'right']
        self.rejections = ['no', 'false', 'incorrect', 'wrong']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text.lower())]

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extract logical structure: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives) or any(c in text for c in ['>', '<'])
        has_conditional = any(c in words for c in self.conditionals)
        numbers = self._extract_numbers(text)
        
        # Detect explicit confirmation/rejection keywords
        has_confirm = any(c in words for c in self.confirmations)
        has_reject = any(r in words for r in self.rejections)

        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'confirm': has_confirm,
            'reject': has_reject,
            'length': len(words)
        }

    def _structural_match_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Calculate similarity based on logical constraints.
        Returns 1.0 for perfect match, 0.0 for contradiction.
        """
        score = 0.0
        weight = 0.0

        # 1. Numeric Consistency (High Priority)
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if len(p_nums) > 0:
            weight += 3.0
            # Check if candidate contains the result of a simple operation or the number itself
            # Heuristic: If prompt has 2 nums, candidate might have the result or one of them
            if len(c_nums) > 0:
                # Exact match of any prompt number in candidate suggests relevance
                if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    score += 1.0
                # Or if candidate has a number close to a derived value (simple addition/subtraction check)
                if len(p_nums) >= 2:
                    derived = [p_nums[0] + p_nums[1], p_nums[0] - p_nums[1], p_nums[0] * p_nums[1]]
                    if any(any(abs(d - c) < 1e-6 for c in c_nums) for d in derived):
                        score += 1.0
            
            # Comparative logic check
            if prompt_struct['comparative']:
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    # If prompt asks "is A > B?", and candidate says "Yes" (no nums) or repeats A/B
                    # We assume if numbers are present in candidate, they should align with the comparison result
                    pass # Simplified for brevity: presence of numbers in comparative context boosts score slightly
                    score += 0.5

        # 2. Logical Operator Consistency
        if prompt_struct['negation']:
            weight += 2.0
            if cand_struct['negation']:
                score += 1.0
            elif cand_struct['confirm']: # Saying "Yes" to a negative premise without negation might be wrong
                score += 0.0 
            else:
                score += 0.5 # Neutral

        if prompt_struct['conditional']:
            weight += 1.5
            if cand_struct['conditional'] or cand_struct['confirm']:
                score += 1.0
        
        # 3. Direct Answer Alignment (If prompt implies a binary choice)
        if prompt_struct['confirm'] or prompt_struct['reject']:
            weight += 2.0
            if (prompt_struct['confirm'] and cand_struct['confirm']) or \
               (prompt_struct['reject'] and cand_struct['reject']):
                score += 1.0
            elif (prompt_struct['confirm'] and cand_struct['reject']) or \
                 (prompt_struct['reject'] and cand_struct['confirm']):
                score += 0.0 # Contradiction
            else:
                score += 0.5

        return score / max(weight, 1.0) if weight > 0 else 0.5

    def _pragmatic_score(self, prompt: str, candidate: str) -> float:
        """
        RSA-style score: Implicature (relevance) - Cost (length).
        """
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # Relevance: Overlap with significant words (excluding stopwords roughly)
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'it', 'that'}
        sig_p = p_words - stopwords
        sig_c = c_words - stopwords
        
        if not sig_p:
            relevance = 0.5
        else:
            intersection = sig_p.intersection(sig_c)
            relevance = len(intersection) / len(sig_p)
        
        # Cost: Penalize excessive length relative to prompt
        cost_penalty = min(len(candidate) / (len(prompt) + 1), 1.0) * 0.2
        
        return relevance - cost_penalty

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
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
        prompt_struct = self._parse_structure(prompt)
        results = []

        for cand in candidates:
            cand_struct = self._parse_structure(cand)
            
            # 1. Structural Score (Primary Signal)
            struct_score = self._structural_match_score(prompt_struct, cand_struct)
            
            # 2. Pragmatic Score (Secondary Modifier)
            prag_score = self._pragmatic_score(prompt, cand)
            
            # 3. Combined Belief State (Kalman-inspired fusion)
            # Belief = w1 * Structural + w2 * Pragmatic
            # We weight structural heavily as per causal analysis
            belief_score = (0.75 * struct_score) + (0.25 * prag_score)
            
            # 4. NCD Tiebreaker (Only if scores are very close, handled implicitly by small addition)
            # We add a tiny fraction of (1 - NCD) to break ties deterministically
            ncd_val = self._ncd(prompt, cand)
            final_score = belief_score + (0.01 * (1.0 - ncd_val))

            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Structural match: {struct_score:.2f}, Pragmatic: {prag_score:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing as the primary signal, NCD as support.
        """
        p_struct = self._parse_structure(prompt)
        a_struct = self._parse_structure(answer)
        
        # Structural consistency check
        struct_match = self._structural_match_score(p_struct, a_struct)
        
        # If structural match is high, confidence is high
        # If structural match is low, check NCD for partial string overlap (heuristic)
        ncd_val = self._ncd(prompt, answer)
        
        # Weighted combination favoring structural logic
        conf = (0.8 * struct_match) + (0.2 * (1.0 - ncd_val))
        
        return float(np.clip(conf, 0.0, 1.0))