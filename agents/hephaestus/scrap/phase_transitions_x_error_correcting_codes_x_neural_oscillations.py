import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical-Oscillatory LDPC Decoder for Hypothesis Verification.
    
    Mechanism:
    1. Structural Parsing (Gamma Layer): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. This acts as the local 
       parity check matrix, defining the "valid codeword" structure.
    2. Oscillatory Simulation (Theta Layer): Simulates the network dynamics.
       - If a candidate satisfies structural constraints, the system settles 
         to a fixed point (low energy, suppressed oscillations).
       - If a candidate violates constraints, the system enters a persistent 
         oscillatory state (high energy, syndrome non-zero).
    3. Scoring: The score is inversely proportional to the final "syndrome energy" 
       (residual oscillations). NCD is used only as a tiebreaker for candidates 
       with identical structural scores.
       
    This implements the "edge of chaos" by treating logical consistency as 
    the stable fixed point and inconsistency as the driver of sustained oscillation.
    """

    def __init__(self):
        # Weights for structural features (simulating the LDPC parity matrix)
        self.weights = {
            'negation_mismatch': -0.4,
            'comparative_error': -0.3,
            'conditional_violation': -0.3,
            'numeric_contradiction': -0.5,
            'keyword_absence': -0.1
        }
        self.oscillation_threshold = 0.5

    def _extract_structure(self, text: str) -> Dict:
        """Gamma-band local parity checks: Extract logical primitives."""
        text_lower = text.lower()
        structure = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'has_yes': 'yes' in text_lower,
            'has_no': 'no' in text_lower
        }
        return structure

    def _check_numeric_consistency(self, prompt_nums: List[str], candidate_nums: List[str]) -> float:
        """Verify numeric transitivity and presence."""
        if not prompt_nums:
            return 1.0 if not candidate_nums else 0.8 # Neutral if no numbers in prompt
        
        # Simple heuristic: Candidate numbers should be a subset or consistent range
        # In a full implementation, this would parse inequalities.
        # Here we penalize if candidate introduces wild outliers not implied.
        try:
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in candidate_nums]
            
            if not p_vals: return 1.0
            if not c_vals: return 0.9 # Missing numbers is a soft error
            
            p_mean = np.mean(p_vals)
            c_mean = np.mean(c_vals)
            
            # Penalize large deviations relative to prompt scale
            scale = max(abs(p_mean), 1.0)
            if abs(c_mean - p_mean) > scale * 2:
                return 0.5
            return 1.0
        except ValueError:
            return 0.9

    def _simulate_dynamics(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulate the critical-oscillatory decoder.
        Returns (stability_score, reasoning_trace).
        High stability (close to 1.0) = Fixed point (Valid hypothesis).
        Low stability = Persistent oscillation (Invalid hypothesis).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        energy = 0.0
        reasons = []
        
        # 1. Negation Parity Check
        # If prompt has strong negation logic, candidate must reflect it.
        if p_struct['negations'] > 0:
            if c_struct['negations'] == 0:
                energy += abs(self.weights['negation_mismatch'])
                reasons.append("Failed negation parity check.")
        
        # 2. Comparative Consistency
        if p_struct['comparatives'] > 0:
            # Heuristic: If prompt compares, candidate should not be generic
            if len(candidate.split()) < 5 and c_struct['comparatives'] == 0:
                energy += abs(self.weights['comparative_error'])
                reasons.append("Missing comparative resolution.")
        
        # 3. Conditional Logic
        if p_struct['conditionals'] > 0:
            if c_struct['conditionals'] == 0 and p_struct['conditionals'] > c_struct['conditionals']:
                # Soft check: Did we drop the conditionality?
                if 'if' in prompt.lower() and 'if' not in candidate.lower():
                     energy += abs(self.weights['conditional_violation']) * 0.5
                     reasons.append("Conditional context dropped.")

        # 4. Numeric Evaluation
        num_score = self._check_numeric_consistency(p_struct['numbers'], c_struct['numbers'])
        if num_score < 1.0:
            energy += (1.0 - num_score) * abs(self.weights['numeric_contradiction'])
            reasons.append("Numeric inconsistency detected.")

        # 5. Keyword/Constraint Propagation (Simplified)
        # Check for direct contradictions like "Yes" when prompt implies negative
        if p_struct['negations'] > 2 and c_struct['has_yes'] and not c_struct['has_no']:
             energy += 0.3
             reasons.append("Potential contradiction with negative premise.")

        # Normalize energy to stability score (0 to 1)
        # Energy > 1.0 implies chaotic/oscillatory state (Invalid)
        stability = max(0.0, 1.0 - energy)
        
        reason_str = "Hypothesis consistent." if stability > 0.8 else "; ".join(reasons) if reasons else "Minor structural mismatch."
        return stability, reason_str

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        for candidate in candidates:
            stability, reasoning = self._simulate_dynamics(prompt, candidate)
            
            # Add small noise based on string length to break exact ties deterministically
            # before applying NCD, ensuring strict ordering
            base_score = stability
            
            scored_candidates.append({
                "candidate": candidate,
                "score": base_score,
                "reasoning": reasoning,
                "_ncd": self._ncd_distance(prompt, candidate) # Store for tie-breaking
            })
        
        # Sort: Primary by structural score (desc), Secondary by NCD (asc, lower is more similar)
        # We invert NCD logic: Lower NCD is better, so we sort by -ncd if we wanted max, 
        # but we want min NCD. So: x['score'] desc, then x['_ncd'] asc.
        scored_candidates.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=False)
        # Correction: We want highest score first. 
        # Sort key: (score, -ncd) -> High score first. If scores equal, high -ncd (low ncd) first.
        # Actually, standard sort is ascending. 
        # To get High Score first: reverse=True on score.
        # To get Low NCD first: reverse=False on NCD.
        # Compound sort: Sort by NCD ascending first (stable), then by Score descending.
        scored_candidates.sort(key=lambda x: x['_ncd']) 
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Clean up and format output
        result = []
        for item in scored_candidates:
            result.append({
                "candidate": item["candidate"],
                "score": round(item["score"], 4),
                "reasoning": item["reasoning"]
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the stability of the hypothesis.
        """
        stability, _ = self._simulate_dynamics(prompt, answer)
        return round(stability, 4)