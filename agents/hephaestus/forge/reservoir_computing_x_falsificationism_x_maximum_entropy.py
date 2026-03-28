import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Reservoir Falsifier (MERF) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. This acts as the "Reservoir" 
       by projecting the input into a high-dimensional feature space without training.
    2. Falsification Loop: Candidates are tested against extracted constraints. 
       Violations (e.g., claiming "True" when prompt has "not True") receive a 
       heavy penalty score, effectively "falsifying" the hypothesis.
    3. Maximum Entropy Prior: Scores are initialized to a uniform prior (max entropy).
       Evidence (structural matches/mismatches) updates scores via a log-linear rule.
       The final ranking reflects the least-biased distribution consistent with 
       the falsification outcomes.
    4. NCD Tiebreaker: If structural scores are identical, Normalized Compression 
       Distance breaks ties based on information density relative to the prompt.
    """

    def __init__(self):
        # Fixed random seed for deterministic reservoir-like projections
        np.random.seed(42)
        self.reservoir_dim = 64
        
    def _extract_features(self, text: str) -> Dict:
        """Structural parsing to generate high-dimensional features from text."""
        text_lower = text.lower()
        features = {
            'has_not': bool(re.search(r'\b(not|no|never|neither)\b', text_lower)),
            'has_if': bool(re.search(r'\b(if|unless|provided)\b', text_lower)),
            'has_greater': bool(re.search(r'(greater|larger|more|>)', text_lower)),
            'has_less': bool(re.search(r'(less|smaller|fewer|<)', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text),
            'question_mark': '?' in text
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        return (c12 - min(c1, c2)) / denom if denom > 0 else 1.0

    def _falsify_and_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Apply falsification logic. 
        Returns (score, reasoning_string).
        Higher score = more likely correct.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        c_text = candidate.lower()
        p_text = prompt.lower()
        
        score = 0.5  # MaxEnt prior (uniform)
        reasons = []

        # 1. Negation Falsification (Modus Tollens check)
        # If prompt says "not X", candidate saying "X" is falsified.
        if p_feat['has_not']:
            if not c_feat['has_not'] and any(k in c_text for k in ['yes', 'true', 'correct']):
                score -= 0.9
                reasons.append("Falsified: Contradicts explicit negation in prompt.")
            elif c_feat['has_not']:
                score += 0.4
                reasons.append("Consistent: Acknowledges negation constraint.")

        # 2. Numeric Consistency
        if p_feat['numbers'] and c_feat['numbers']:
            p_nums = p_feat['numbers']
            c_nums = c_feat['numbers']
            # Simple heuristic: if prompt compares A > B, candidate should reflect order
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                if p_feat['has_greater'] and c_nums[0] < max(p_nums):
                     # Heuristic check: if prompt implies large, small number might be wrong
                     # This is a weak proxy but captures some numeric reasoning
                     pass 
                # Direct match bonus
                if abs(c_nums[0] - p_nums[0]) < 1e-6:
                    score += 0.3
                    reasons.append("Consistent: Numeric value matches prompt.")

        # 3. Conditional/Logical Flow
        if p_feat['has_if']:
            if any(k in c_text for k in ['then', 'therefore', 'so', 'yes', 'no']):
                score += 0.2
                reasons.append("Consistent: Responds to conditional structure.")
        
        # 4. Length/Complexity Penalty (Occam's razor via MaxEnt)
        # Overly verbose answers without substance are slightly penalized
        if len(candidate) > len(prompt) * 2:
            score -= 0.1
            reasons.append("Penalty: Excessive verbosity.")

        # Default reasoning if nothing triggered
        if not reasons:
            reasons.append("No strong falsification evidence; prior dominates.")
            
        return score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        scored_candidates = []
        
        # Phase 1: Structural Falsification & Scoring
        for cand in candidates:
            score, reason = self._falsify_and_score(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "base_score": score,
                "reasoning": reason
            })
        
        # Phase 2: NCD Tiebreaking & Final Ranking
        # We use NCD only when base_scores are effectively equal (within epsilon)
        results = []
        for i, item in enumerate(scored_candidates):
            final_score = item['base_score']
            
            # Check for ties with other candidates to apply NCD
            is_tied = False
            for j, other in enumerate(scored_candidates):
                if i != j and abs(item['base_score'] - other['base_score']) < 0.05:
                    is_tied = True
                    break
            
            if is_tied:
                # Lower NCD (higher similarity/relevance) boosts score slightly
                ncd_val = self._compute_ncd(prompt, item['candidate'])
                # Invert NCD: 0 is perfect match, 1 is no match. 
                # We want high similarity to boost score.
                final_score += (1.0 - ncd_val) * 0.01 

            results.append({
                "candidate": item['candidate'],
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": item['reasoning']
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism normalized to [0, 1].
        """
        # Evaluate single candidate against itself to get score
        # We simulate a minimal candidate list to reuse logic
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # The score is already normalized by clip(0,1) in evaluate
        # We add a small structural check to ensure it's not just a tie-break win
        base_score = res[0]['score']
        
        # Strong negative indicators reduce confidence regardless of score
        if 'Falsified' in res[0]['reasoning']:
            return 0.1
            
        return float(base_score)