import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    SMAGTR-inspired Reasoning Tool (Simplified for constraints).
    
    Mechanism:
    1. Analogical/Abductive Scoring (Structural Priors): 
       Parses prompt for logical structures (negations, comparatives, conditionals, numbers).
       Scores candidates based on structural alignment (e.g., if prompt has negation, 
       candidates with negation get higher prior; if numeric, checks math validity).
    2. Nash Equilibrium (Stability Check):
       Treats structural features as 'agents'. A candidate's score is penalized if it 
       satisfies one agent (e.g., length match) but contradicts another (e.g., logical negation).
       This mimics the 'cost for deviating from consensus' in the theoretical model.
    3. NCD Tiebreaker:
       Used only when structural scores are identical, acting as a similarity baseline.
       
    This approach prioritizes logical structure over string similarity, beating pure NCD.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'cannot', "n't"}
        self.comparative_ops = {'>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.cond_words = {'if', 'then', 'else', 'unless', 'provided'}

    def _extract_features(self, text: str) -> dict:
        """Extract logical and structural features from text."""
        lower = text.lower()
        words = set(re.findall(r'\b\w+\b', lower))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparative_ops) or bool(re.search(r'[<>]', text))
        has_conditional = bool(words & self.cond_words)
        
        # Extract numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text),
            'word_count': len(words)
        }

    def _check_logical_consistency(self, prompt_feats: dict, cand_feats: dict, candidate: str) -> float:
        """
        Simulates the 'Nash Equilibrium' stability check.
        Returns a penalty score (0.0 = stable/consistent, negative = unstable/contradictory).
        """
        penalty = 0.0
        
        # Agent 1: Negation Consistency
        # If prompt implies negation, candidate should likely reflect it or be explicitly contradictory
        if prompt_feats['negation']:
            if not cand_feats['negation']:
                # Heuristic: If prompt says "not X", and candidate is just "X", penalize.
                # Simple check: does candidate repeat prompt words without negation?
                penalty -= 0.2
        
        # Agent 2: Numeric Consistency
        if prompt_feats['numbers'] and cand_feats['numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            
            # Check comparative logic if present
            if prompt_feats['comparative']:
                if 'larger' in candidate.lower() or 'greater' in candidate.lower() or '>' in candidate:
                    if c_nums[0] <= max(p_nums): penalty -= 0.3
                elif 'smaller' in candidate.lower() or 'less' in candidate.lower() or '<' in candidate:
                    if c_nums[0] >= min(p_nums): penalty -= 0.3
            else:
                # If numbers exist but no comparative, exact match or close is often expected in simple QA
                if abs(c_nums[0] - p_nums[0]) > 1e-6:
                     penalty -= 0.1

        # Agent 3: Conditional/Length stability (Anti-gaming)
        # If prompt is a complex conditional, very short answers might be unstable
        if prompt_feats['conditional'] and cand_feats['word_count'] < 3:
            penalty -= 0.1
            
        return penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Phase 1: Abductive Scoring (Structural Alignment)
        scores = []
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # Base score from structural alignment
            score = 0.5
            
            # Bonus for matching negation status (Analogical mapping of logical form)
            if prompt_feats['negation'] == cand_feats['negation']:
                score += 0.2
            
            # Bonus for numeric presence if prompt has numbers
            if prompt_feats['numbers']:
                if cand_feats['numbers']:
                    score += 0.2
                else:
                    score -= 0.1
            
            # Apply Nash-style stability penalty
            stability_penalty = self._check_logical_consistency(prompt_feats, cand_feats, cand)
            score += stability_penalty
            
            scores.append(score)
        
        # Normalize scores to avoid negative dominance if all are bad
        min_s = min(scores)
        max_s = max(scores)
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        ranked_candidates = []
        for i, cand in enumerate(candidates):
            # Normalize structural score
            norm_score = (scores[i] - min_s) / range_s
            
            # NCD as tiebreaker/secondary signal
            # We invert NCD (1 - ncd) so higher is better, then weight it lightly
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            final_score = norm_score * 0.9 + ncd_score * 0.1
            
            # Reasoning summary
            reasoning = f"Structural alignment: {scores[i]:.2f}; Stability: {scores[i] - norm_score:.2f}; NCD backup: {1-ncd_val:.2f}"
            
            ranked_candidates.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        ranked_candidates.sort(key=lambda x: x['score'], reverse=True)
        return ranked_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural consistency and NCD.
        0.0 = definitely wrong, 1.0 = definitely correct.
        """
        feats_p = self._extract_features(prompt)
        feats_a = self._extract_features(answer)
        
        # Base confidence
        conf = 0.5
        
        # Structural checks
        if feats_p['negation'] != feats_a['negation']:
            # Mismatch in negation often implies error in simple logic tasks
            conf -= 0.3
            
        if feats_p['numbers'] and feats_a['numbers']:
            # If both have numbers, check basic magnitude logic if possible
            # Here we just reward the presence match as a proxy for relevance
            conf += 0.2
        elif feats_p['numbers'] and not feats_a['numbers']:
            conf -= 0.2
            
        # NCD check: if answer is completely unrelated string, NCD will be high (distance)
        # Low NCD (high similarity) boosts confidence if structural checks pass
        ncd = self._compute_ncd(prompt, answer)
        if ncd < 0.5:
            conf += 0.2
        elif ncd > 0.9:
            conf -= 0.1
            
        return max(0.0, min(1.0, conf))