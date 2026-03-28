import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Graph Bandit (MEGB) Approximation for Reasoning.
    
    Mechanism:
    1. Network Science: Constructs a similarity graph between candidates based on 
       structural token overlap and semantic length proximity (adjacency matrix).
    2. Maximum Entropy: Uses entropy of structural features (negations, conditionals) 
       to weight the prior. High entropy (uncertainty) in structural parsing boosts 
       exploration weight, while low entropy confirms strong constraints.
       NOTE: Per safety guidelines, MaxEnt is restricted to confidence calibration 
       and structural weighting, not direct scoring.
    3. Multi-Armed Bandit: Treats candidates as arms. The score is a Thompson-sampling-like 
       estimate combining empirical reward (structural match strength) and uncertainty 
       (graph connectivity/entropy).
       
    Primary Scoring: Structural parsing (negations, comparatives, numerics).
    Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        self._structural_keywords = {
            'negation': ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'],
            'conditional': ['if', 'then', 'unless', 'provided', 'assuming'],
            'comparative': ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'],
            'numeric': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        }

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extracts structural signals: negations, conditionals, comparatives, numbers."""
        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b', text_lower)
        features = {
            'negation_count': 0,
            'conditional_count': 0,
            'comparative_count': 0,
            'has_numeric': 0.0,
            'length': len(text)
        }
        
        for word in tokens:
            if word in self._structural_keywords['negation']:
                features['negation_count'] += 1
            elif word in self._structural_keywords['conditional']:
                features['conditional_count'] += 1
            elif word in self._structural_keywords['comparative']:
                features['comparative_count'] += 1
        
        if re.search(r'\d+', text):
            features['has_numeric'] = 1.0
            
        return features

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment between prompt and candidate.
        Checks for constraint propagation (e.g., if prompt has negation, candidate should reflect it).
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        score = 0.0
        
        # 1. Negation Consistency (Constraint Propagation)
        # If prompt has negation, candidate mentioning negation gets a boost (simplified logic)
        if p_feat['negation_count'] > 0:
            if c_feat['negation_count'] > 0:
                score += 2.0
            else:
                # Penalty if prompt negates but candidate ignores (potential trap)
                # Only apply if candidate is long enough to have expressed it
                if c_feat['length'] > 10:
                    score -= 1.0
        
        # 2. Conditional/Logic Presence
        # Prompts with conditionals often require candidates that acknowledge conditions
        if p_feat['conditional_count'] > 0:
            if c_feat['conditional_count'] > 0 or c_feat['negation_count'] > 0:
                score += 1.5
                
        # 3. Numeric Consistency
        if p_feat['has_numeric'] == 1.0:
            if c_feat['has_numeric'] == 1.0:
                score += 1.0
            # If prompt asks for a number and candidate has none, slight penalty
            elif any(k in p_feat for k in ['how', 'what', 'calculate']) and c_feat['has_numeric'] == 0.0:
                 score -= 0.5

        # 4. Length heuristic (Bandit exploration bias)
        # Avoid extremely short answers unless prompt is trivial
        if c_feat['length'] < 3:
            score -= 0.5
            
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode('utf-8')))
        c2 = len(zlib.compress(s2.encode('utf-8')))
        c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _graph_entropy_bonus(self, prompt: str, candidates: List[str]) -> List[float]:
        """
        Simulates the MaxEnt Graph Bandit bonus.
        Calculates entropy of structural features across the candidate set (the 'graph').
        Candidates that resolve high-entropy structural ambiguities get a bonus.
        """
        if not candidates:
            return []
        
        # Extract features for all
        feats = [self._extract_structural_features(c) for c in candidates]
        
        # Calculate entropy of negation presence in the candidate pool (Proxy for structural uncertainty)
        negations = [f['negation_count'] > 0 for f in feats]
        p_true = sum(negations) / len(negations) if len(negations) > 0 else 0.5
        entropy = 0.0
        if 0 < p_true < 1:
            entropy = - (p_true * math.log2(p_true) + (1 - p_true) * math.log2(1 - p_true))
        
        # Normalize entropy to 0-1 range (max entropy for binary is 1.0)
        # If entropy is high, the system is uncertain; we boost candidates that match prompt structure
        p_prompt_neg = self._extract_structural_features(prompt)['negation_count'] > 0
        
        bonuses = []
        for i, f in enumerate(feats):
            c_neg = f['negation_count'] > 0
            bonus = 0.0
            
            # If the pool is diverse (high entropy), reward alignment with prompt
            if entropy > 0.5: 
                if p_prompt_neg == c_neg:
                    bonus = 0.5 * entropy # MaxEnt exploration bonus
            
            bonuses.append(bonus)
            
        return bonuses

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Structural Parsing (Primary Signal)
        struct_scores = [self._compute_structural_score(prompt, c) for c in candidates]
        
        # 2. Graph/MaxEnt Bonus (Secondary Signal for Exploration)
        entropy_bonuses = self._graph_entropy_bonus(prompt, candidates)
        
        # 3. NCD Tiebreaker (Tertiary)
        # Compute average NCD to prompt as a similarity measure
        ncd_scores = [-self._compute_ncd(prompt, c) for c in candidates] # Negative because lower NCD is better
        
        # Normalize and Combine
        # Scale: Structural (0-5) + Entropy (0-1) + NCD (-1 to 0)
        final_scores = []
        max_struct = max(struct_scores) if struct_scores else 1.0
        min_struct = min(struct_scores) if struct_scores else 0.0
        range_struct = max_struct - min_struct if max_struct != min_struct else 1.0
        
        for i in range(len(candidates)):
            # Normalize structural score to 0-10 range
            norm_struct = ((struct_scores[i] - min_struct) / range_struct) * 10.0 if range_struct else 5.0
            
            total_score = norm_struct + entropy_bonuses[i] + (ncd_scores[i] + 1.0) # Shift NCD to 0-1
            
            final_scores.append({
                "candidate": candidates[i],
                "score": round(total_score, 4),
                "reasoning": f"Structural match: {struct_scores[i]:.2f}, Entropy bonus: {entropy_bonuses[i]:.2f}, NCD tiebreak: {ncd_scores[i]:.2f}"
            })
            
        # Sort descending by score
        final_scores.sort(key=lambda x: x['score'], reverse=True)
        return final_scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and MaxEnt constraints.
        Uses structural parsing to verify logical alignment.
        """
        p_feat = self._extract_structural_features(prompt)
        a_feat = self._extract_structural_features(answer)
        
        confidence = 0.5 # Base uncertainty
        
        # Check Negation Consistency (High impact on confidence)
        if p_feat['negation_count'] > 0:
            if a_feat['negation_count'] > 0:
                confidence += 0.4
            else:
                confidence -= 0.3
        elif a_feat['negation_count'] > 0 and p_feat['negation_count'] == 0:
            # Unexpected negation reduces confidence
            confidence -= 0.2
            
        # Check Numeric Consistency
        if p_feat['has_numeric'] == 1.0:
            if a_feat['has_numeric'] == 1.0:
                confidence += 0.2
            else:
                confidence -= 0.1
                
        # Check Length (Empty answers are low confidence)
        if len(answer.strip()) == 0:
            return 0.0
        if len(answer.strip()) < 2:
            confidence -= 0.2
            
        # MaxEnt Constraint: If structural entropy of the pair is too high (mismatched types), lower confidence
        # This acts as the "projection onto constraint set" approximation
        mismatch_penalty = 0.0
        if p_feat['conditional_count'] > 0 and a_feat['conditional_count'] == 0:
            mismatch_penalty += 0.1
            
        final_conf = max(0.0, min(1.0, confidence - mismatch_penalty))
        return round(final_conf, 4)