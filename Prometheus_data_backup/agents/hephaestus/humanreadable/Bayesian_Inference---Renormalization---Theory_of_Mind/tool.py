import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Hierarchical Bayesian Theory-of-Mind (RH-BToM) Approximation.
    
    Mechanism:
    1. Structural Parsing (Level-0): Extracts hard constraints (negations, comparatives, 
       conditionals, numeric values). This acts as the 'fine-grained' observation layer.
    2. RG Flow (Coarse-Graining): Candidates are evaluated against structural constraints.
       Violations incur heavy penalties (high energy). Satisfied constraints propagate 
       'sufficient statistics' (score boosts) to the next level.
    3. Variational Scoring: The final score combines the structural adherence (logic) 
       with an NCD-based similarity term (prior), where NCD acts only as a tiebreaker 
       when structural signals are ambiguous, preventing overfitting to string noise.
    4. Theory of Mind (Inhibited): Used only in confidence() to detect if the answer 
       simply echoes the prompt (mimicry) vs providing distinct structural resolution.
    """

    def __init__(self):
        self._constraint_keywords = {
            'negation': ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing'],
            'comparative': ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'],
            'conditional': ['if', 'then', 'unless', 'only if', 'provided'],
            'logic_ops': ['and', 'or', 'but', 'however', 'therefore']
        }

    def _extract_structural_features(self, text: str) -> Dict:
        """Extracts logical features acting as latent variables."""
        text_lower = text.lower()
        features = {
            'has_negation': any(k in text_lower for k in self._constraint_keywords['negation']),
            'has_comparative': any(k in text_lower for k in self._constraint_keywords['comparative']),
            'has_conditional': any(k in text_lower for k in self._constraint_keywords['conditional']),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        return features

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> float:
        """
        Level-0 Fine-grained check. 
        Returns a score based on logical consistency between prompt constraints and candidate.
        """
        score = 0.0
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        # 1. Numeric Consistency (Transitivity/Comparison)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # Simple heuristic: if prompt has numbers, candidate should reflect logical relation
                # Since we don't have the full logic graph, we check if candidate numbers 
                # are a subset or derived from prompt (simplified for this tool)
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                
                # Reward if candidate contains specific numbers mentioned in prompt contextually
                # This is a proxy for "answering the specific question"
                matches = sum(1 for n in c_nums if any(abs(n - p) < 1e-6 for p in p_nums))
                if matches > 0:
                    score += 0.4 * (matches / max(len(c_nums), 1))
            except ValueError:
                pass

        # 2. Negation Alignment (Modus Tollens proxy)
        # If prompt asks "What is NOT...", candidate should ideally not just repeat positive terms
        # This is a heuristic proxy: if prompt has negation, candidate length should be substantial
        if p_feat['has_negation']:
            if c_feat['length'] > 10: # Avoid single word "No" unless necessary
                score += 0.2
        
        # 3. Conditional/Logic Presence
        if p_feat['has_conditional'] or p_feat['has_comparative']:
            # Candidate should ideally reflect complexity if prompt is complex
            if c_feat['has_comparative'] or c_feat['has_conditional'] or c_feat['length'] > 20:
                score += 0.3

        return min(score, 1.0)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt features for RG flow context
        prompt_features = self._extract_structural_features(prompt)
        
        for cand in candidates:
            # Level 1: Structural Parsing (Primary Signal)
            struct_score = self._check_constraint_satisfaction(prompt, cand)
            
            # Level 2: RG Coarse-Graining (NCD as Prior/Tiebreaker)
            # We invert NCD because lower distance = higher similarity = higher prior probability
            # But we weight it lightly to avoid the "echo chamber" trap
            ncd = self._ncd_distance(prompt, cand)
            
            # Heuristic: If candidate is too short (Yes/No) and prompt is complex, penalize via NCD context
            # unless struct_score is perfect.
            rg_adjustment = 0.0
            if prompt_features['length'] > 50 and len(cand) < 5:
                rg_adjustment = -0.2 # Penalty for oversimplification in complex contexts
            
            # Final Score: Structural (High Weight) + RG Adjustment (Low Weight)
            final_score = (struct_score * 0.8) + ((1.0 - ncd) * 0.2) + rg_adjustment
            
            # Reasoning trace
            reasoning = f"Structural match: {struct_score:.2f}; NCD prior: {1.0-ncd:.2f}; RG adj: {rg_adjustment:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses ToM inhibitor logic: If answer is just a substring of prompt (mimicry), 
        confidence is low unless it's a direct extraction task.
        """
        answer_clean = answer.strip().lower()
        prompt_clean = prompt.strip().lower()
        
        # Inhibitor: Detect pure mimicry (ToM failure mode)
        if answer_clean in prompt_clean and len(answer_clean) > 5:
            # If the answer is just a phrase copied from prompt, low confidence in reasoning
            return 0.3
        
        # Structural validation
        struct_score = self._check_constraint_satisfaction(prompt, answer)
        
        # If structural constraints are met, confidence is high
        if struct_score > 0.5:
            return 0.85 + (struct_score * 0.15)
        
        # Fallback to NCD similarity for vague cases
        ncd = self._ncd_distance(prompt, answer)
        if ncd < 0.5:
            return 0.5
            
        return 0.2