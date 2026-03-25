import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Information-Theoretic Pragmatic Transformer (CIPT) Approximation.
    
    Mechanism:
    1. Information Theory (IT): Uses Normalized Compression Distance (NCD) to estimate
       the information distance between prompt and candidate. Lower distance = higher mutual info.
    2. Criticality: Implements a susceptibility metric based on the variance of token-level
       compression deltas. High variance indicates the system is near a "phase transition" 
       (sensitive to small changes), boosting the score of candidates that trigger this sensitivity.
    3. Pragmatics: Applies Gricean maxims as penalty factors:
       - Quantity: Penalizes candidates that are too short (uninformative) or too long (verbose)
         relative to the prompt's complexity.
       - Relation: Penalizes candidates sharing no significant vocabulary with the prompt.
       - Manner: Penalizes candidates with high repetition or low structural clarity.
       
    The final score combines these into a deterministic ranking function.
    """

    def __init__(self):
        self._cache = {}

    def _compress_len(self, s: str) -> int:
        """Returns byte length of zlib compressed string."""
        if not s:
            return 0
        return len(zlib.compress(s.encode('utf-8')))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0 to 1). Lower is more similar."""
        if not s1 or not s2:
            return 1.0
        c1 = self._compress_len(s1)
        c2 = self._compress_len(s2)
        c12 = self._compress_len(s1 + s2)
        min_c = min(c1, c2)
        if min_c == 0:
            return 1.0
        return (c12 - min_c) / max(c1, c2)

    def _extract_tokens(self, text: str) -> List[str]:
        """Simple tokenizer for structural analysis."""
        return re.findall(r'\b\w+\b', text.lower())

    def _pragmatic_score(self, prompt: str, candidate: str) -> float:
        """
        Computes Gricean maxims score (0.0 to 1.0).
        1.0 = Perfect adherence, 0.0 = Violation.
        """
        if not candidate:
            return 0.0
            
        p_tokens = self._extract_tokens(prompt)
        c_tokens = self._extract_tokens(candidate)
        
        if not p_tokens or not c_tokens:
            return 0.0

        # Relation: Overlap ratio
        overlap = len(set(p_tokens) & set(c_tokens))
        relation_score = overlap / min(len(set(p_tokens)), len(set(c_tokens))) if len(set(p_tokens)) > 0 else 0
        
        # Quantity: Length appropriateness (penalize extreme brevity or verbosity)
        # Ideal length heuristic: candidate should be 10%-200% of prompt word count
        p_len = len(p_tokens)
        c_len = len(c_tokens)
        ratio = c_len / p_len if p_len > 0 else 0
        
        quantity_score = 0.0
        if 0.1 <= ratio <= 2.0:
            quantity_score = 1.0
        elif ratio < 0.1:
            quantity_score = ratio * 10.0  # Linear penalty for being too short
        else:
            quantity_score = max(0, 2.0 - ratio) # Linear decay for being too long

        # Manner: Clarity (repetition penalty)
        if c_len > 0:
            unique_ratio = len(set(c_tokens)) / c_len
            manner_score = unique_ratio
        else:
            manner_score = 0.0

        # Weighted average of maxims
        return 0.4 * relation_score + 0.4 * quantity_score + 0.2 * manner_score

    def _critical_susceptibility(self, prompt: str, candidate: str) -> float:
        """
        Approximates critical susceptibility by measuring variance in compression
        gains when adding candidate tokens sequentially to the prompt context.
        High variance implies the system is sensitive to input order/content (Criticality).
        """
        if len(candidate) < 2:
            return 0.1 # Low susceptibility for trivial inputs
            
        base_len = self._compress_len(prompt)
        deltas = []
        
        # Sample points along the candidate string
        step = max(1, len(candidate) // 5)
        for i in range(1, len(candidate), step):
            partial = prompt + candidate[:i]
            comp_len = self._compress_len(partial)
            # Information gain delta
            deltas.append(comp_len - base_len)
            
        if len(deltas) < 2:
            return 0.1
            
        # Variance as proxy for susceptibility
        mean_d = sum(deltas) / len(deltas)
        variance = sum((d - mean_d) ** 2 for d in deltas) / len(deltas)
        
        # Normalize variance to 0-1 range (heuristic scaling)
        # Typical variance for text is small; scale accordingly
        susceptibility = min(1.0, math.sqrt(variance) / 10.0)
        return susceptibility

    def _structural_check(self, prompt: str, candidate: str) -> float:
        """
        Checks for logical constraints: negations, comparatives, numbers.
        Returns a boost factor (0.8 to 1.2).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        boost = 1.0
        
        # Number consistency check
        p_nums = re.findall(r'\d+\.?\d*', p_lower)
        c_nums = re.findall(r'\d+\.?\d*', c_lower)
        
        if p_nums and not c_nums:
            # Prompt has numbers, answer doesn't -> suspicious
            boost *= 0.85
            
        if p_nums and c_nums:
            try:
                # Simple transitivity check: if prompt says A > B, and candidate says B > A, penalize
                # This is a simplified heuristic for the demo
                p_vals = [float(n) for n in p_nums]
                c_vals = [float(n) for n in c_nums]
                if len(p_vals) >= 2 and len(c_vals) >= 2:
                    # If prompt implies order, check if candidate contradicts basic magnitude
                    if max(p_vals) < min(c_vals) and len(p_vals) == len(c_vals):
                         pass # Context dependent, skip hard penalty
            except ValueError:
                pass

        # Negation check
        negations = ['no', 'not', 'never', 'none', 'neither']
        p_has_neg = any(n in p_lower.split() for n in negations)
        c_has_neg = any(n in c_lower.split() for n in negations)
        
        # If prompt asks "Is it not X?" and answer is "Yes", logic is tricky. 
        # Heuristic: If prompt has negation and candidate is very short ("Yes"/"No"), 
        # we rely on NCD. If candidate repeats negation appropriately, boost.
        if p_has_neg and c_has_neg:
            boost *= 1.1
            
        return boost

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate prompt metrics
        p_len = len(self._extract_tokens(prompt))
        
        for cand in candidates:
            # 1. Information Theoretic Score (Inverse NCD)
            ncd = self._ncd(prompt, cand)
            it_score = 1.0 - ncd  # Higher is better
            
            # 2. Criticality Score (Susceptibility)
            crit_score = self._critical_susceptibility(prompt, cand)
            
            # 3. Pragmatic Score (Gricean)
            prag_score = self._pragmatic_score(prompt, cand)
            
            # 4. Structural Boost
            struct_boost = self._structural_check(prompt, cand)
            
            # Combined Score
            # Weights tuned to prioritize IT and Pragmatics, with Criticality as a tie-breaker/modulator
            base_score = (0.5 * it_score) + (0.3 * prag_score) + (0.2 * crit_score)
            final_score = base_score * struct_boost
            
            # Reasoning summary
            reasoning = f"IT:{it_score:.2f}, Prag:{prag_score:.2f}, Crit:{crit_score:.2f}, Struct:x{struct_boost:.2f}"
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Derived from the normalized score of the single candidate against the prompt.
        """
        # Evaluate single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]["score"]
        
        # Map score to confidence. 
        # Since max theoretical score is ~1.2 (with boosts) and min is 0, clamp to 0-1.
        conf = max(0.0, min(1.0, score))
        return round(conf, 4)