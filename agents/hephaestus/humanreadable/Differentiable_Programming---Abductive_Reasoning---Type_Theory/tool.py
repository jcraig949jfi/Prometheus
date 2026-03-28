import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A Differentiable, Type-Guided Abductive Program Synthesizer (Simulated).
    
    Mechanism:
    1. Abductive Hypothesis Generation: Parses prompts for structural constraints 
       (negations, comparatives, conditionals) to form a "type signature" of the logic.
    2. Differentiable Scoring: Candidates are scored against this signature. 
       - Structural adherence yields high gradients (score).
       - Numeric consistency is evaluated via float conversion.
       - NCD acts as a regularization term (tiebreaker) for semantic similarity.
    3. Type Guidance: Candidates failing basic logical "type checks" (e.g., answering 
       positive when prompt has negation) are penalized heavily, simulating the 
       rejection of ill-typed terms in a dependently typed lambda calculus.
    """

    def __init__(self):
        self._keywords_neg = ['no', 'not', 'never', 'none', 'cannot', 'impossible', 'false']
        self._keywords_comp = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self._keywords_cond = ['if', 'then', 'unless', 'only if', 'when']

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features acting as type constraints."""
        t = text.lower()
        return {
            'neg_count': sum(1 for k in self._keywords_neg if r'\b' + k + r'\b' in t),
            'comp_present': any(k in t for k in self._keywords_comp),
            'cond_present': any(k in t for k in self._keywords_cond),
            'has_numbers': bool(re.search(r'\d+', t)),
            'length': len(t)
        }

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Differentiable check for numeric logic (0.0 to 1.0)."""
        # Extract all numbers from prompt and candidate
        p_nums = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
        c_nums = re.findall(r"[-+]?\d*\.\d+|\d+", candidate)
        
        if not p_nums:
            return 1.0 # No numbers to check
        
        # Simple heuristic: if prompt has numbers and candidate has none, slight penalty
        if not c_nums:
            # Check if candidate is a word-answer that might imply a number logic
            if any(x in candidate.lower() for x in ['yes', 'no', 'true', 'false']):
                return 1.0 
            return 0.7

        try:
            # Check magnitude consistency if comparatives are present
            if any(k in prompt.lower() for k in self._keywords_comp):
                p_val = float(p_nums[0])
                c_val = float(c_nums[0]) if c_nums else 0
                if '>' in prompt or 'greater' in prompt or 'more' in prompt:
                    return 1.0 if c_val >= p_val else 0.2
                if '<' in prompt or 'less' in prompt or 'fewer' in prompt:
                    return 1.0 if c_val <= p_val else 0.2
        except ValueError:
            pass
        
        return 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0=identical, 1=disjoint)."""
        if not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        score = 1.0
        reasons = []

        # 1. Abductive Type Check: Negation Consistency
        # If prompt strongly implies negation, candidate should reflect it or not contradict
        if p_feat['neg_count'] > 0:
            # Heuristic: If prompt says "not", candidate saying "yes" might be wrong depending on context
            # Simulating type safety: strict negation handling
            if 'yes' in candidate.lower() and 'not' in prompt.lower():
                # This is a simplification of dependent type checking
                if 'not' in prompt.lower().split('yes')[0]: # Crude context window
                     score -= 0.3
                     reasons.append("Negation conflict detected")

        # 2. Structural Constraint: Conditional Logic
        if p_feat['cond_present']:
            if not any(k in candidate.lower() for k in ['if', 'then', 'else', 'yes', 'no', 'true', 'false']):
                score -= 0.2
                reasons.append("Conditional structure weak")

        # 3. Numeric Evaluation
        num_score = self._check_numeric_consistency(prompt, candidate)
        if num_score < 1.0:
            score -= (1.0 - num_score) * 0.5
            reasons.append("Numeric inconsistency")

        # 4. NCD Tiebreaker (Regularization)
        # Prefer candidates that compress well with the prompt (semantic closeness)
        ncd_val = self._ncd(prompt, candidate)
        # Normalize NCD impact: low NCD is good. 
        ncd_bonus = (1.0 - ncd_val) * 0.15 
        score += ncd_bonus
        
        # Length penalty for extremely short answers in complex prompts (Occam's razor with lower bound)
        if p_feat['length'] > 50 and len(candidate) < 3:
            score -= 0.1
            reasons.append("Answer too brief for complex prompt")

        reason_str = "; ".join(reasons) if reasons else "Structural fit"
        return max(0.0, min(1.0, score)), reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            sc, rs = self._score_candidate(prompt, cand)
            scored.append({"candidate": cand, "score": sc, "reasoning": rs})
        
        # Sort descending by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        sc, _ = self._score_candidate(prompt, answer)
        return round(sc, 4)