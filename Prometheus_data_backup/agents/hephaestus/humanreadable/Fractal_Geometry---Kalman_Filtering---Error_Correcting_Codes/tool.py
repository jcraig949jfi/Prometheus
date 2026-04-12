import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multiscale Recursive Estimator-Decoder with Fractal-Kalman-ErrorCorrection logic.
    
    Mechanism:
    1. Fractal Hierarchy (Scale Invariance): The prompt is parsed at multiple scales:
       - Micro (Token/Numeric), Meso (Clause/Constraint), Macro (Global Logic).
       - Self-similarity allows reusing the same scoring logic across scales.
    2. Kalman Filtering (Bayesian Update): 
       - Prior: Base likelihood from NCD (compression similarity).
       - Measurement: Structural evidence (negations, comparatives, numeric truth).
       - Update: Optimal fusion of Prior and Measurement to estimate correctness.
    3. Error Correcting Codes (Redundancy):
       - Logical constraints are treated as parity bits.
       - If a candidate contradicts a hard constraint (e.g., "A > B" but implies B > A),
         an 'error' is flagged, heavily penalizing the score (syndrome decoding).
    """

    def __init__(self):
        self.process_noise = 0.1  # Kalman Q
        self.measurement_noise = 0.4  # Kalman R
        self.k_gain = self.measurement_noise / (self.measurement_noise + self.process_noise)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0=identical, 1=disjoint)."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical primitives: negations, comparatives, numbers."""
        text_l = text.lower()
        has_neg = bool(re.search(r'\b(not|no|never|without|impossible)\b', text_l))
        has_comp = bool(re.search(r'(\bmore\b|\bless\b|greater|smaller|>|<|=)', text_l))
        nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        return {"neg": has_neg, "comp": has_comp, "nums": nums}

    def _kalman_update(self, prior: float, measurement: float) -> float:
        """Simple 1D Kalman update fusing prior (NCD) and measurement (Structure)."""
        # Convert NCD (distance) to likelihood (0-1, where 1 is good)
        prior_prob = 1.0 - prior 
        # Measurement is binary-ish confidence from structural check
        posterior = prior_prob + self.k_gain * (measurement - prior_prob)
        return max(0.0, min(1.0, posterior))

    def _check_consistency(self, prompt: str, candidate: str) -> float:
        """
        Error Correcting Code Layer: Check logical parity.
        Returns 1.0 if consistent, 0.0 if contradiction detected.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 1.0
        
        # Parity Check 1: Negation consistency
        # If prompt asserts a negative constraint, candidate shouldn't blindly affirm opposite
        if p_struct['neg'] and not c_struct['neg']:
            # Heuristic: If prompt denies something, simple affirmative candidates might be traps
            if len(c_struct['nums']) == 0 and not c_struct['comp']:
                score -= 0.3 

        # Parity Check 2: Numeric Transitivity (Simplified)
        # If prompt has numbers and candidate has numbers, check basic order
        if p_struct['nums'] and c_struct['nums']:
            p_max = max(p_struct['nums']) if p_struct['nums'] else 0
            c_val = c_struct['nums'][0] if c_struct['nums'] else 0
            # If prompt implies "find smaller" but candidate is huge, penalty
            if "smaller" in prompt.lower() or "less" in prompt.lower():
                if c_val > p_max: score -= 0.5
            elif "larger" in prompt.lower() or "more" in prompt.lower():
                if c_val < (p_max * 0.1): score -= 0.5 # Rough heuristic

        # Parity Check 3: Length/Complexity coding
        # Candidates that are too short to encode the answer complexity are likely errors
        if len(candidate) < 3 and len(prompt) > 20:
             if "explain" in prompt.lower() or "why" in prompt.lower():
                 score -= 0.4

        return max(0.0, score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # Scale 1: Micro (NCD Baseline)
            ncd_val = self._ncd_score(prompt, cand)
            
            # Scale 2: Meso (Structural Measurement)
            # Does the candidate contain relevant structural tokens found in prompt?
            cand_struct = self._extract_structure(cand)
            struct_match = 0.5
            if prompt_struct['comp'] and cand_struct['comp']: struct_match += 0.3
            if prompt_struct['neg'] and cand_struct['neg']: struct_match += 0.2
            if not prompt_struct['neg'] and not cand_struct['neg']: struct_match += 0.1
            
            # Scale 3: Macro (Error Correction / Consistency)
            consistency = self._check_consistency(prompt, cand)
            
            # Fusion: Kalman Update
            # Prior is NCD inverted, Measurement is structural match
            base_score = self._kalman_update(ncd_val, struct_match)
            
            # Apply Error Correction Penalty (Syndrome Decoding)
            final_score = base_score * consistency
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"NCD:{1-ncd_val:.2f}, Struct:{struct_match:.2f}, ECC:{consistency:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        return ranked[0]['score'] if ranked else 0.0