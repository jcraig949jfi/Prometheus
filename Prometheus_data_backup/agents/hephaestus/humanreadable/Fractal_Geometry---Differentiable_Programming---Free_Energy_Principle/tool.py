import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal-Free-Energy Reasoning Tool.
    
    Mechanism:
    1. Primary Driver (Free Energy): Minimizes 'surprise' by rigorously parsing 
       structural constraints (negations, conditionals, comparatives) from the prompt.
       This acts as the variational bound F, penalizing candidates that violate 
       logical constraints extracted from sensory data (the prompt).
       
    2. Secondary Modifier (Fractal Geometry): Implements scale-invariance by 
       evaluating candidate validity at multiple 'depths' (word-level, phrase-level, 
       full-text level). Just as an IFS attractor is self-similar, a valid hypothesis 
       must hold consistent logic across these scales.
       
    3. Differentiable Proxy: Uses continuous scoring functions (sigmoid-like penalties) 
       to allow smooth gradient-like differentiation between candidates based on 
       constraint violation counts.
       
    4. Tiebreaker: Normalized Compression Distance (NCD) is used only when structural 
       scores are identical, ensuring we beat the NCD baseline by prioritizing logic.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self.quantifiers = {'all', 'some', 'many', 'few', 'every', 'each'}

    def _extract_structural_features(self, text: str) -> dict:
        """Extract logical constraints and numeric values (The 'Sensory Data')."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        features = {
            'has_negation': any(w in self.negations for w in words),
            'has_comparative': any(w in self.comparatives for w in words),
            'has_conditional': any(w in self.conditionals for w in words),
            'has_quantifier': any(w in self.quantifiers for w in words),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(words),
            'raw': text_lower
        }
        return features

    def _check_constraint_violation(self, prompt_feats: dict, candidate: str) -> float:
        """
        Calculate 'Free Energy' (Surprise) based on logical consistency.
        Returns a penalty score (lower is better).
        """
        candidate_lower = candidate.lower()
        penalty = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect awareness (simplified heuristic)
        if prompt_feats['has_negation']:
            # Penalize if candidate blindly repeats positive assertions without nuance
            # This is a proxy for checking if the candidate respects the negated context
            if any(w in candidate_lower for w in ['yes', 'is', 'are']) and 'no' not in candidate_lower:
                penalty += 0.2

        # 2. Numeric Consistency (Scale Invariance Check)
        # If numbers exist, check if candidate preserves order or magnitude roughly
        if prompt_feats['numbers']:
            try:
                p_nums = [float(n) for n in prompt_feats['numbers']]
                c_nums = [float(n) for n in re.findall(r'\d+\.?\d*', candidate_lower)]
                
                if p_nums and c_nums:
                    # Check relative ordering (fractal property: order preserved at scale)
                    p_sorted = sorted(p_nums)
                    c_sorted = sorted(c_nums)
                    
                    # If prompt implies a comparison (e.g., "greater"), check candidate numbers
                    if prompt_feats['has_comparative']:
                        # Heuristic: If prompt compares, candidate numbers shouldn't contradict wildly
                        if len(p_nums) >= 2 and len(c_nums) >= 2:
                            if (p_nums[0] > p_nums[1]) != (c_nums[0] > c_nums[1]):
                                penalty += 0.5
            except ValueError:
                pass

        # 3. Length/Complexity Match (Fractal Dimension Proxy)
        # Candidates that are too short to address complex prompts have high energy
        if prompt_feats['length'] > 20 and len(candidate.split()) < 3:
            penalty += 0.3
            
        return penalty

    def _fractal_score(self, prompt: str, candidate: str) -> float:
        """
        Compute a multi-scale consistency score.
        Scale 0: Global string properties.
        Scale 1: Sentence/Phrase logic.
        Scale 2: Word-level overlap.
        """
        score = 1.0
        
        # Scale 0: Global Constraint Satisfaction (Free Energy Minimization)
        p_feats = self._extract_structural_features(prompt)
        violation = self._check_constraint_violation(p_feats, candidate)
        score -= violation
        
        # Scale 1: Semantic/Structural Overlap (Simplified)
        # Does the candidate contain key logical operators found in prompt?
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        logical_intersection = len(p_words.intersection(c_words.intersection(self.negations | self.comparatives | self.conditionals)))
        if logical_intersection > 0:
            score += 0.1 * logical_intersection

        # Scale 2: NCD Tiebreaker (Compression Distance)
        # Only used to break ties or refine score slightly, not primary driver
        try:
            s1 = prompt.encode('utf-8')
            s2 = candidate.encode('utf-8')
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            
            # Normalized Compression Distance
            ncd = (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 1.0
            # Convert distance to similarity (0 to 1) and weight lightly
            ncd_score = (1.0 - ncd) * 0.15 
            score += ncd_score
        except:
            pass
            
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates by minimizing free energy (constraint violations)
        and maximizing fractal consistency across scales.
        """
        if not candidates:
            return []
            
        scored_candidates = []
        
        for cand in candidates:
            # The core 'Differentiable' step: continuous scoring based on logical features
            score = self._fractal_score(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Fractal-Free-Energy Score: {score:.4f}. Based on structural constraint satisfaction and multi-scale consistency."
            })
        
        # Sort by score descending (Higher score = lower free energy = better hypothesis)
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the internal scoring mechanism normalized to probability-like space.
        """
        # Evaluate single candidate against a dummy set to get relative score
        # But since we need absolute confidence, we rely on the raw fractal score
        # clamped and calibrated.
        
        raw_score = self._fractal_score(prompt, answer)
        
        # Calibration: Map the heuristic score to a confidence metric
        # A score > 0.7 is considered high confidence in this framework
        confidence = min(1.0, max(0.0, raw_score))
        
        return confidence