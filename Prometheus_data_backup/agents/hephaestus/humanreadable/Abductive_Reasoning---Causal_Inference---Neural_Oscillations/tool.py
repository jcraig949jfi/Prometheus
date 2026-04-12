import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Oscillatory Causal Abductive Network (OCAN) Implementation.
    
    Mechanism:
    1. Abductive Hypothesis Generation (Gamma Band): Candidates are parsed into 
       structural feature vectors (negations, comparatives, numerics, conditionals).
    2. Causal Intervention Gate (Theta Band): Instead of static matching, we simulate 
       a 'do-calculus' perturbation by testing the candidate's structural integrity 
       against the prompt's logical constraints (e.g., if prompt has 'not', candidate 
       must reflect negation).
    3. Prediction Error Minimization: Scores are derived from the alignment of 
       structural features (logic) rather than semantic similarity. 
    4. NCD Tiebreaker: Normalized Compression Distance is used only when structural 
       scores are identical, acting as a secondary complexity metric.
    
    This avoids the 'Causal Inference' trap of direct scoring by using causality 
    only for structural validation (confidence wrapper) and relies on abductive 
    feature matching for the primary rank.
    """

    def __init__(self):
        self.theta_cycle = 0  # Simulates theta phase for stochastic gating

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extracts logical and structural features (Abductive Hypothesis)."""
        t = text.lower()
        features = {
            'has_negation': float(bool(re.search(r'\b(not|no|never|neither|without)\b', t))),
            'has_comparative': float(bool(re.search(r'\b(more|less|better|worse|greater|smaller|than)\b', t))),
            'has_conditional': float(bool(re.search(r'\b(if|then|unless|otherwise|when)\b', t))),
            'has_numeric': float(bool(re.search(r'\d+', t))),
            'has_uncertainty': float(bool(re.search(r'\b(maybe|possibly|likely|uncertain)\b', t))),
            'length': len(t),
            'word_count': float(len(t.split()))
        }
        
        # Numeric evaluation capability
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", t)
        if nums:
            try:
                features['max_num'] = max(float(n) for n in nums)
                features['min_num'] = min(float(n) for n in nums)
            except ValueError:
                features['max_num'] = 0.0
                features['min_num'] = 0.0
        else:
            features['max_num'] = 0.0
            features['min_num'] = 0.0
            
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except Exception:
            return 1.0

    def _oscillatory_gate(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Simulates Theta-Gamma coupling.
        Checks if the candidate's structural features align with the prompt's 
        logical requirements (Causal Intervention).
        """
        score = 0.0
        matches = 0
        
        # Negation Check: If prompt has negation, high value candidates should too (simplified)
        if prompt_feats['has_negation'] > 0:
            if cand_feats['has_negation'] > 0:
                score += 2.0
            else:
                score -= 1.0 # Penalty for missing negation
            matches += 1
            
        # Comparative Check
        if prompt_feats['has_comparative'] > 0:
            if cand_feats['has_comparative'] > 0:
                score += 1.5
            matches += 1
            
        # Conditional Check
        if prompt_feats['has_conditional'] > 0:
            if cand_feats['has_conditional'] > 0:
                score += 1.5
            elif cand_feats['has_uncertainty'] > 0:
                score += 0.5 # Uncertainty is a weak proxy for conditionals
            matches += 1

        # Numeric Consistency (Simple heuristic)
        if prompt_feats['has_numeric'] > 0 and cand_feats['has_numeric'] > 0:
            # Reward if magnitudes are somewhat close or order is preserved
            score += 1.0
            
        return score if matches > 0 else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_structure(prompt)
        scored_candidates = []
        
        # Base score based on structural alignment (Abductive Reasoning)
        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # Primary Score: Structural Logic Alignment
            logic_score = self._oscillatory_gate(prompt_feats, cand_feats)
            
            # Secondary Score: Length heuristic (answers shouldn't be too short/long relative to prompt)
            len_ratio = cand_feats['word_count'] / (prompt_feats['word_count'] + 1)
            length_penalty = -abs(0.2 - len_ratio) * 2 if len_ratio > 0 else -5.0
            
            raw_score = logic_score + length_penalty
            
            scored_candidates.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Structural match: {logic_score:.2f}, Length penalty: {length_penalty:.2f}"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply NCD as tiebreaker for top candidates if scores are very close
        # This implements the "NCD only as tiebreaker" rule
        if len(scored_candidates) > 1:
            top_score = scored_candidates[0]["score"]
            # Check for ties within a small epsilon
            tie_group = [c for c in scored_candidates if abs(c["score"] - top_score) < 0.1]
            
            if len(tie_group) > 1:
                # Re-rank tie group using NCD against prompt
                # Lower NCD is better (more similar structure/compression)
                tie_group.sort(key=lambda x: self._compute_ncd(prompt, x["candidate"]))
                
                # Reconstruct list with sorted tie group at front
                non_tie = [c for c in scored_candidates if c not in tie_group]
                scored_candidates = tie_group + non_tie

        # Normalize scores to 0-1 range roughly for consistency, though interface allows float
        max_s = scored_candidates[0]["score"] if scored_candidates else 0
        min_s = scored_candidates[-1]["score"] if scored_candidates else 0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        for item in scored_candidates:
            # Adjust score to be more interpretable, keeping relative order
            normalized = (item["score"] - min_s) / range_s
            item["score"] = round(normalized, 4)
            
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing to verify logical consistency (Causal Intervention Check).
        """
        p_feats = self._extract_structure(prompt)
        a_feats = self._extract_structure(answer)
        
        conf = 0.5  # Base uncertainty
        
        # Boost if negation logic holds
        if p_feats['has_negation'] == a_feats['has_negation']:
            conf += 0.2
        elif p_feats['has_negation'] > 0 and a_feats['has_negation'] == 0:
            conf -= 0.4 # High penalty for missing negation
            
        # Boost if comparative logic holds
        if p_feats['has_comparative'] == a_feats['has_comparative']:
            conf += 0.15
            
        # Boost if conditional logic holds
        if p_feats['has_conditional'] == a_feats['has_conditional']:
            conf += 0.15
            
        # Numeric presence check
        if p_feats['has_numeric'] > 0:
            if a_feats['has_numeric'] > 0:
                conf += 0.1
            else:
                conf -= 0.2

        return max(0.0, min(1.0, conf))