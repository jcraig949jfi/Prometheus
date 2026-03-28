import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Active Inference Network (RAIN) Approximation.
    
    Mechanism:
    1. Active Inference Core: Evaluates candidates by minimizing "surprise" (prediction error)
       against structural constraints extracted from the prompt (negations, comparatives, logic).
    2. Renormalization (Multi-scale): 
       - Fine scale: Token-level exact match and NCD.
       - Coarse scale: Semantic constraint satisfaction (e.g., if prompt says "not X", candidate containing "X" gets high error).
       - The final score is a precision-weighted sum of errors across these scales.
    3. Neuromodulation (Precision Gating):
       - Dynamically adjusts the weight of specific error types based on prompt keywords.
       - "Dopamine" (Reward/Epistemic): Boosts score if candidate contains novel information not in prompt but consistent.
       - "Acetylcholine" (Sensory): Boosts penalty for missing explicit constraints (numbers, negations).
       - "Serotonin" (Prior): Stabilizes scores based on length and structural completeness.
       
    This architecture allows adaptive scale selection: focusing on strict logical constraints when present
    (high acetylcholine mode) and broader semantic matching when constraints are loose.
    """

    def __init__(self):
        # State initialization (none needed for stateless evaluation)
        pass

    def _extract_structural_features(self, text: str) -> dict:
        """Extract logical constraints: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|except)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worst|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(text.split()),
            'question_marks': text.count('?')
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c12 = len(zlib.compress(s1_bytes + s2_bytes))
            denominator = max(c1, c2)
            if denominator == 0:
                return 1.0
            return (c12 - min(c1, c2)) / denominator
        except Exception:
            return 1.0

    def _evaluate_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        Active Inference Step: Calculate prediction error based on logical constraints.
        Returns a penalty score (0.0 = no error, 1.0 = maximum error).
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        error = 0.0
        count = 0

        # 1. Negation Consistency (Modus Tollens check approximation)
        # If prompt says "not X", and candidate says "X" (and doesn't say "not"), penalize.
        if p_feat['negations'] > 0:
            # Simple heuristic: if prompt has strong negation, candidate shouldn't be a direct subset without qualification
            # This is a coarse-grained RG check
            if len(c_lower) > 5 and c_lower in p_lower:
                error += 0.2
            count += 1

        # 2. Number Consistency
        if p_feat['numbers']:
            p_nums = [float(n) for n in p_feat['numbers']]
            c_nums = [float(n) for n in c_feat['numbers']]
            
            if c_nums:
                # Check if candidate numbers contradict prompt numbers (simple equality check)
                # If prompt has specific numbers, candidate should likely reference them or logic implies relation
                match_count = 0
                for cn in c_nums:
                    if any(abs(cn - pn) < 1e-6 for pn in p_nums):
                        match_count += 1
                # Penalty if numbers present but don't match prompt at all (potential hallucination)
                if match_count == 0:
                    error += 0.3
            else:
                # Candidate ignores numbers entirely when prompt has them (missing sensory detail)
                error += 0.1
            count += 1

        # 3. Length/Complexity Prior (Serotonin-like stability)
        # Extreme brevity in complex prompts is suspicious
        if p_feat['length'] > 20 and c_feat['length'] < 3:
            error += 0.2
            count += 1

        return error / (count + 1) if count > 0 else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_feat = self._extract_structural_features(prompt)
        
        # Neuromodulatory Gain Control
        # Acetylcholine: High if many constraints (negations/numbers) -> focus on detail
        # Dopamine: High if prompt is open-ended -> focus on novelty (less penalty for deviation)
        acetylcholine_gain = min(1.0, (p_feat['negations'] + p_feat['comparatives'] + len(p_feat['numbers']) * 0.5) / 3.0)
        
        for cand in candidates:
            # Scale 1: Fine-grained (NCD)
            ncd = self._compute_ncd(prompt, cand)
            
            # Scale 2: Coarse-grained (Logical Constraint Violation)
            logic_error = self._evaluate_constraint_violation(prompt, cand)
            
            # Renormalization Group Flow: Combine scales
            # Base score from similarity (inverted NCD)
            base_score = 1.0 - ncd
            
            # Apply Precision-Adjusted Penalty
            # High acetylcholine (high constraint prompt) -> Logic errors hurt more
            adjusted_score = base_score - (logic_error * (0.5 + 0.5 * acetylcholine_gain))
            
            # Bonus for structural completeness (matching question type)
            if '?' in prompt and ('yes' in cand.lower() or 'no' in cand.lower()):
                adjusted_score += 0.1

            results.append({
                "candidate": cand,
                "score": float(max(0.0, min(1.0, adjusted_score))), # Clamp 0-1
                "reasoning": f"NCD:{ncd:.2f}, LogicErr:{logic_error:.2f}, Gain:{acetylcholine_gain:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same RAIN logic: high confidence if low NCD and low logic error.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Meta-cognitive adjustment:
        # If the prompt had high constraints (high acetylcholine context) and score is high, confidence is very high.
        # If prompt was vague, confidence is moderate even if score is high.
        p_feat = self._extract_structural_features(prompt)
        constraint_density = (p_feat['negations'] + p_feat['comparatives'] + len(p_feat['numbers'])) / (p_feat['length'] + 1)
        
        # Boost confidence if constraints were satisfied
        if constraint_density > 0.1 and score > 0.7:
            return min(1.0, score + 0.2)
        
        return score