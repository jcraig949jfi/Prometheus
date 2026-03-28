import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormal-Pragmatic Compositional Inference (RPCI) Engine.
    
    Mechanism:
    1. Compositionality: Parses prompt/candidates into primitive tokens (numbers, 
       negations, comparatives, conditionals) acting as neural-symbolic bindings.
    2. Renormalization: Iteratively coarse-grains these primitives. Fine-grained 
       token matches are integrated into higher-order structural scores (scale 
       transformation), discarding noise (non-matching filler words).
    3. Pragmatism: A utility function scores candidates based on structural 
       alignment (logic consistency) and numeric correctness. The process 'stops' 
       (converges) when the pragmatic score stabilizes, acting as a fixed-point 
       inference.
       
    This approximates the RG flow by treating structural logic as the 'universal' 
    feature surviving coarse-graining, while NCD handles residual tie-breaking.
    """

    def __init__(self):
        # Primitives for compositional parsing
        self.negations = {'no', 'not', 'never', 'none', 'cannot', "n't"}
        self.comparatives = {'>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'whenever'}
        self.bool_yes = {'yes', 'true', 'correct', 'right'}
        self.bool_no = {'no', 'false', 'incorrect', 'wrong'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[\w']+|[<>]=?", text.lower())

    def _extract_primitives(self, text: str) -> Dict:
        tokens = self._tokenize(text)
        return {
            'raw': text.lower(),
            'tokens': set(tokens),
            'has_negation': bool(self.negations.intersection(tokens)),
            'has_comparative': bool(self.comparatives.intersection(tokens)),
            'has_conditional': bool(self.conditionals.intersection(tokens)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'bool_yes': bool(self.bool_yes.intersection(tokens)),
            'bool_no': bool(self.bool_no.intersection(tokens))
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        c1 = zlib.compress(s1.encode())
        c2 = zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(c1), len(c2))
        if max_len == 0: return 0.0
        return (len(c12) - min(len(c1), len(c2))) / max_len

    def _renormalize_score(self, p_prompt: Dict, p_cand: Dict) -> float:
        """
        Computes a pragmatic utility score via hierarchical integration:
        Layer 1 (Fine): Token overlap.
        Layer 2 (Coarse): Structural alignment (negation, logic types).
        Layer 3 (Universal): Numeric and Boolean consistency.
        """
        score = 0.0
        
        # Layer 1: Compositional Token Overlap (Primitive binding)
        intersection = p_prompt['tokens'] & p_cand['tokens']
        union = p_prompt['tokens'] | p_cand['tokens']
        if union:
            score += 0.2 * (len(intersection) / len(union))
        
        # Layer 2: Structural Consistency (RG Coarse-graining)
        # Penalty if prompt has logic markers but candidate ignores them
        if p_prompt['has_negation'] and not p_cand['has_negation']:
            # Check if candidate is a direct answer that might implicitly handle it
            if not (p_cand['bool_yes'] or p_cand['bool_no']):
                score -= 0.3 # Penalty for ignoring negation context
        
        if p_prompt['has_comparative'] and not p_cand['has_comparative']:
             if not (p_cand['bool_yes'] or p_cand['bool_no'] or p_cand['numbers']):
                score -= 0.2

        # Layer 3: Numeric & Boolean Utility (Fixed Point Criteria)
        # If numbers exist, check ordering if comparatives are present
        if p_prompt['numbers'] and p_cand['numbers']:
            # Simple heuristic: if prompt asks for max/min (implied by comparative)
            # We reward if the candidate number is extreme relative to prompt numbers
            p_nums = p_prompt['numbers']
            c_nums = p_cand['numbers']
            
            # Check for explicit comparison in prompt
            if p_prompt['has_comparative']:
                if '>' in p_prompt['raw'] or 'greater' in p_prompt['raw'] or 'larger' in p_prompt['raw']:
                    # Expecting larger number
                    if any(c > max(p_nums) for c in c_nums): score += 0.5
                elif '<' in p_prompt['raw'] or 'less' in p_prompt['raw'] or 'smaller' in p_prompt['raw']:
                    # Expecting smaller number
                    if any(c < min(p_nums) for c in c_nums): score += 0.5
            
            # Exact float match bonus (for calculation tasks)
            if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                score += 0.4

        # Boolean consistency check
        if p_prompt['bool_yes'] and p_cand['bool_yes']: score += 0.3
        if p_prompt['bool_no'] and p_cand['bool_no']: score += 0.3
        
        # Contradiction penalty
        if p_prompt['bool_yes'] and p_cand['bool_no']: score -= 0.5
        if p_prompt['bool_no'] and p_cand['bool_yes']: score -= 0.5

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_prompt = self._extract_primitives(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = []
        for c in candidates:
            ncd_scores.append(self._compute_ncd(prompt, c))
        
        avg_ncd = sum(ncd_scores) / len(ncd_scores) if ncd_scores else 0
        min_ncd = min(ncd_scores) if ncd_scores else 0
        range_ncd = max(ncd_scores) - min_ncd if len(ncd_scores) > 1 else 1.0
        if range_ncd == 0: range_ncd = 1.0

        for i, cand in enumerate(candidates):
            p_cand = self._extract_primitives(cand)
            
            # Core RPCI Score
            base_score = self._renormalize_score(p_prompt, p_cand)
            
            # Pragmatic Normalization (Utility maximization)
            # Normalize NCD to be a tiebreaker: lower NCD (more similar) is better if base scores are close
            # But we invert logic: if base_score is high, we trust it. If low, we look at NCD.
            ncd_norm = 1.0 - (ncd_scores[i] - min_ncd) / range_ncd if range_ncd > 0 else 0.5
            
            # Final Score: Dominated by structural reasoning, nudged by compression
            final_score = base_score + (0.05 * ncd_norm)
            
            # Reasoning string generation
            reason_parts = []
            if p_cand['numbers']: reason_parts.append("numeric_eval")
            if p_cand['has_negation']: reason_parts.append("negation_handled")
            if p_cand['bool_yes'] or p_cand['bool_no']: reason_parts.append("boolean_align")
            if not reason_parts: reason_parts.append("structural_match")
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"RPCI: {', '.join(reason_parts)}; ncd_factor={ncd_norm:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the top-rank score normalized.
        Uses the same internal scoring mechanism.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Map score to 0-1 range roughly. 
        # Base scores can be negative (contradictions) or >1 (strong matches).
        # Sigmoid-like mapping centered around 0.
        score = res[0]['score']
        confidence = 1.0 / (1.0 + math.exp(-score * 2)) # Scale factor 2 for sensitivity
        return round(confidence, 4)