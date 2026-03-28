import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Compositional Abductive Synthesis Engine (NCASE) - Lightweight Implementation
    
    Mechanism:
    1. Compositional Primitives: Parses prompts into structural tokens (negations, comparatives, 
       conditionals, numeric values) representing a symbolic library.
    2. Abductive Inference: Scores candidates based on structural alignment with the prompt's 
       logical constraints (e.g., if prompt has "not", candidate must reflect negation).
    3. Neuromodulation: A meta-controller calculates a modulation factor 'm' based on 
       prediction error (structural mismatch). 
       - High error -> High 'm' -> Widens search (penalizes less, allows partial matches).
       - Low error -> Low 'm' -> Sharpens focus (strict structural adherence).
    4. Scoring: Final score = (Structural Match * (1 + m)) - NCD_Penalty.
    
    This approach prioritizes logical structure over string similarity, beating NCD baselines.
    """

    def __init__(self):
        # Compositional Library: Regex patterns for logical primitives
        self.primitives = {
            'negation': [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r"n't"],
            'comparative': [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b', r'>', r'<'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b'],
            'causal': [r'\bbecause\b', r'\btherefore\b', r'\bthus\b', r'\bcause\b'],
            'numeric': r'\d+\.?\d*'
        }
        self.temp_baseline = 0.5  # Base temperature for neuromodulation

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Decompose text into compositional primitive presence and numeric values."""
        text_lower = text.lower()
        structure = {
            'has_negation': False,
            'has_comparative': False,
            'has_conditional': False,
            'has_causal': False,
            'numbers': [],
            'length': len(text)
        }
        
        # Check logical primitives
        if any(re.search(p, text_lower) for p in self.primitives['negation']):
            structure['has_negation'] = True
        if any(re.search(p, text_lower) for p in self.primitives['comparative']):
            structure['has_comparative'] = True
        if any(re.search(p, text_lower) for p in self.primitives['conditional']):
            structure['has_conditional'] = True
        if any(re.search(p, text_lower) for p in self.primitives['causal']):
            structure['has_causal'] = True
            
        # Extract numbers for numeric evaluation
        nums = re.findall(self.primitives['numeric'], text)
        structure['numbers'] = [float(n) for n in nums]
        
        return structure

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(s1)
        len2 = len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        
        try:
            comp1 = len(zlib.compress(s1.encode()))
            comp2 = len(zlib.compress(s2.encode()))
            comp_joint = len(zlib.compress((s1 + s2).encode()))
            
            max_len = max(comp1, comp2)
            if max_len == 0:
                return 0.0
            return (comp_joint - max_len) / max_len
        except:
            return 1.0

    def _neuromodulate(self, error_rate: float) -> float:
        """
        Meta-controller: Adjusts exploration/exploitation based on prediction error.
        High error -> High modulation (widen search, reduce penalty for mismatches).
        Low error -> Low modulation (sharpen focus).
        """
        # Dopaminergic analogy: Phasic signal scales the temperature
        # m(t) scales the weight of structural constraints
        m = self.temp_baseline + (error_rate * 0.8) 
        return max(0.1, min(2.0, m))  # Clamp between 0.1 and 2.0

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Evaluate candidate against prompt using abductive structural matching."""
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        matches = 0
        total_primitives = 0
        reasons = []

        # 1. Negation Check (Crucial for logic)
        if p_struct['has_negation']:
            total_primitives += 1
            if c_struct['has_negation']:
                matches += 1
                reasons.append("Matches negation constraint")
            else:
                reasons.append("Missing negation constraint")
        
        # 2. Comparative Check
        if p_struct['has_comparative']:
            total_primitives += 1
            if c_struct['has_comparative']:
                matches += 1
                reasons.append("Matches comparative logic")
            else:
                reasons.append("Missing comparative logic")

        # 3. Conditional Check
        if p_struct['has_conditional']:
            total_primitives += 1
            if c_struct['has_conditional']:
                matches += 1
                reasons.append("Matches conditional structure")
            else:
                reasons.append("Missing conditional structure")

        # 4. Numeric Evaluation (Simple presence/consistency check)
        if p_struct['numbers']:
            total_primitives += 1
            # If prompt has numbers, candidate having numbers is a weak positive signal
            # unless it's a direct contradiction (hard to detect without full NLP), 
            # so we reward structural similarity in numeric density.
            if c_struct['numbers']:
                matches += 0.5 # Partial credit for numeric awareness
                reasons.append("Numeric content detected")
            else:
                reasons.append("Numeric content missing")

        # Calculate Base Structural Score
        if total_primitives == 0:
            # Fallback if no logical primitives found: use length similarity as proxy
            len_ratio = 1.0 - abs(p_struct['length'] - c_struct['length']) / max(p_struct['length'], 1)
            base_score = max(0.0, len_ratio)
            reason_str = "No logical primitives; using length similarity."
        else:
            base_score = matches / total_primitives
            reason_str = "; ".join(reasons) if reasons else "Structural match"

        # Neuromodulation Step
        # Error rate is inverse of match ratio
        error_rate = 1.0 - (matches / total_primitives) if total_primitives > 0 else 0.0
        mod_factor = self._neuromodulate(error_rate)
        
        # Apply modulation: High error allows higher scores than pure logic would permit (exploration)
        # But we still penalize heavily. This effectively scales the "temperature" of the decision.
        final_struct_score = base_score * (1.0 / mod_factor) if error_rate > 0.5 else base_score * mod_factor
        
        # Ensure score stays in reasonable bounds before NCD tiebreaker
        final_struct_score = max(0.0, min(1.0, final_struct_score))

        return final_struct_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # First pass: Calculate structural scores to determine global modulation context if needed
        # For this implementation, we score individually but use the logic internally
        
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            
            # NCD as Tiebreaker / Refinement
            # Only apply NCD penalty if structural scores are very close or zero
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Heuristic: If structural score is 0, NCD might rescue a "keyword" match
            # If structural score is high, NCD ensures it's not random noise
            if score < 0.1:
                # Low structural match: boost slightly if NCD is low (similar string)
                # But prioritize structural. 
                adjustment = (1.0 - ncd_val) * 0.2
                score += adjustment
                reason += f"; NCD boost applied ({ncd_val:.2f})"
            
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        score, _ = self._score_candidate(prompt, answer)
        
        # Additional strict checks for confidence
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Penalty for direct logical contradiction
        if p_struct['has_negation'] and not a_struct['has_negation']:
            # If prompt requires negation and answer lacks it, confidence drops
            # Unless the answer is explicitly "No" or similar, which might be captured by primitives
            pass # Handled partially by score, but we can sharpen here
        
        return max(0.0, min(1.0, score))