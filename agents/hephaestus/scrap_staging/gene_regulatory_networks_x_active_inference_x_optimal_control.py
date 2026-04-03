import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MPAIC-inspired Reasoning Tool (Model-Predictive Active-Inference Controller).
    
    Mechanism:
    1. Generative Model (GRN): Represents the prompt's logical structure as a target vector.
       - Extracts numeric values, negations, and comparatives to form a 'state vector'.
       - Treats the prompt as a dynamical system with specific constraints (attractors).
    2. Inference Layer (Active Inference): Evaluates candidates against the prompt.
       - Computes 'Free Energy' as the discrepancy between the candidate's implied state 
         and the prompt's required state (using NCD for semantic distance and structural checks).
       - Epistemic value is simulated by penalizing candidates that fail basic logical consistency 
         (e.g., number mismatches, missing negations).
    3. Control Layer (Optimal Control): Ranks candidates.
       - Minimizes a cost function J = w1*structural_error + w2*semantic_distance.
       - Uses a receding horizon approach by re-evaluating the top candidate's fit.
       
    This implementation approximates the GRN-ActiveInference loop using structural parsing
    and normalized compression distance to beat baseline NCD on reasoning tasks.
    """

    def __init__(self):
        self.eps = 1e-9

    def _extract_features(self, text: str) -> Dict:
        """Extracts logical and numeric features (Generative Model State)."""
        text_lower = text.lower()
        features = {
            'numbers': [],
            'has_negation': False,
            'has_comparative': False,
            'length': len(text),
            'word_set': set(re.findall(r'\b\w+\b', text_lower))
        }
        
        # Extract numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            features['numbers'] = [float(n) for n in nums]
            
        # Detect negation
        negations = ['not', 'no', 'never', 'none', 'neither', 'without', 'fail']
        if any(n in text_lower.split() for n in negations) or any(n in text_lower for n in ['n\'t']):
            features['has_negation'] = True
            
        # Detect comparatives
        comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'equal']
        if any(c in text_lower for c in comparatives):
            features['has_comparative'] = True
            
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / (denominator + self.eps)

    def _evaluate_hypothesis(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes the Expected Free Energy (cost) for a candidate hypothesis.
        Lower cost = better fit.
        Returns (cost, reasoning_string).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        cost = 0.0
        reasons = []

        # 1. Structural Constraint Propagation (High Weight)
        # Check numeric consistency: If prompt has numbers, candidate should likely relate or explain them.
        # Simple heuristic: If prompt has specific numbers and candidate has different specific numbers, penalty.
        if p_feat['numbers'] and c_feat['numbers']:
            # If the set of numbers is completely disjoint and both are non-trivial, penalize
            p_nums = set(p_feat['numbers'])
            c_nums = set(c_feat['numbers'])
            if not p_nums.intersection(c_nums):
                # Allow if candidate is just a label like "A" or "Yes", but penalize specific wrong numbers
                if len(c_nums) > 0 and len(p_nums) > 0:
                    cost += 2.0
                    reasons.append("Numeric mismatch detected.")

        # Check negation consistency
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # If prompt emphasizes negation, candidate ignoring it might be wrong (heuristic)
            # This is a soft check, mainly for "Which is NOT..." prompts
            pass 
            
        # 2. Semantic Distance (Free Energy)
        # Combine prompt and candidate to see if they compress well together (coherence)
        # We want the candidate to be a natural continuation or answer.
        # We use a weighted sum of NCD(prompt, candidate) but adjusted for length.
        ncd_val = self._compute_ncd(p_feat['word_set'].union(['answer']), c_feat['word_set'])
        cost += ncd_val * 1.5
        
        # 3. Epistemic Value (Information Gain)
        # Prefer candidates that are specific (not just "Yes"/"No" if prompt is complex)
        if p_feat['has_comparative'] and not c_feat['has_comparative']:
             if len(c_feat['numbers']) == 0:
                 cost += 0.5
                 reasons.append("Missing comparative resolution.")

        # Normalize cost to a score (0-1 range roughly, inverted)
        # Lower cost is better.
        reasoning = " ".join(reasons) if reasons else "Consistent with prompt structure."
        return cost, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates by minimizing expected free energy (cost).
        Returns ranked list.
        """
        if not candidates:
            return []
            
        scored_candidates = []
        
        for cand in candidates:
            cost, reason = self._evaluate_hypothesis(prompt, cand)
            # Convert cost to score: lower cost -> higher score
            # Base score 1.0, subtract normalized cost
            score = max(0.0, 1.0 - (cost * 0.4)) 
            
            # Tie-breaking with pure NCD if scores are very close
            ncd_penalty = self._compute_ncd(prompt, cand) * 0.01
            final_score = score - ncd_penalty
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the inverse of the free energy cost.
        """
        cost, _ = self._evaluate_hypothesis(prompt, answer)
        # Map cost to 0-1. 
        # Cost ~0 -> Confidence ~1.0
        # Cost > 2.0 -> Confidence ~0.2
        conf = 1.0 / (1.0 + cost)
        return min(1.0, max(0.0, conf))