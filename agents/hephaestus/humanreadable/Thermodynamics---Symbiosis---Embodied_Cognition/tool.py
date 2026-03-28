import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Symbiotic Active-Inference Holobiont (SAIH) Approximation.
    
    Mechanism:
    1. Embodied Cognition (Structural Parsing): Extracts logical constraints 
       (negations, comparatives, conditionals) as the agent's "sensorimotor" ground truth.
    2. Thermodynamics (Entropy Cost): Calculates a 'viability score' based on 
       constraint satisfaction. Violating hard constraints incurs high 'entropy' (penalty).
    3. Symbiosis (Resource Coupling): Uses Normalized Compression Distance (NCD) 
       as a shared resource metric. Candidates must be compressible relative to the 
       prompt (high mutual information) to survive. 
       
    The final score minimizes variational free energy: F = Entropy_Cost - Lambda * Resource_Sharing.
    """

    def __init__(self):
        self.lambda_resource = 0.4  # Weight for symbiotic coupling
        self.entropy_penalty = 10.0 # Penalty for logical violation

    def _structural_parse(self, text: str) -> Dict:
        """Extracts logical 'sensorimotor' contingencies from text."""
        text_lower = text.lower()
        return {
            'has_negation': bool(re.search(r'\b(no|not|never|without|impossible)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'has_numeric': bool(re.search(r'\d+', text_lower)),
            'length': len(text)
        }

    def _check_constraints(self, prompt: str, candidate: str) -> float:
        """
        Thermodynamic Cost Function.
        Checks if the candidate violates structural constraints implied by the prompt.
        Returns 0.0 (low entropy) if valid, negative penalty if invalid.
        """
        p_struct = self._structural_parse(prompt)
        c_struct = self._structural_parse(candidate)
        cost = 0.0

        # Modus Tollens / Negation check
        # If prompt establishes a negative constraint, candidate shouldn't be blindly positive
        if p_struct['has_negation'] and not c_struct['has_negation']:
            # Heuristic: If prompt is negative, a very short affirmative might be wrong
            if c_struct['length'] < 10 and candidate.strip().lower() in ['yes', 'true', '1']:
                cost -= self.entropy_penalty

        # Comparative consistency
        if p_struct['has_comparative'] and not c_struct['has_comparative']:
            # If prompt compares, answer usually needs qualification or specific selection
            # Soft penalty if candidate is generic
            if len(candidate.split()) < 3:
                cost -= (self.entropy_penalty * 0.5)

        # Conditional logic
        if p_struct['has_conditional']:
            # Candidates for conditionals often need 'if', 'yes', 'no', or specific outcomes
            # No hard penalty, but structural mismatch reduces viability
            if not any(k in c_struct for k in ['has_conditional', 'has_negation']) and len(candidate) < 5:
                cost -= (self.entropy_penalty * 0.2)

        return cost

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a proxy for mutual information."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Normalized to 0-1 where 0 is identical, 1 is disjoint
        numerator = len_combined - min(len_s1, len_s2)
        denominator = max(len_s1, len_s2)
        
        if denominator == 0:
            return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_features = self._structural_parse(prompt)
        
        for cand in candidates:
            # 1. Thermodynamic Cost (Constraint Satisfaction)
            energy_cost = self._check_constraints(prompt, cand)
            
            # 2. Symbiotic Resource (NCD Mutual Information)
            # Low NCD means high similarity/shared information (Good for symbiosis)
            # We invert NCD so high value = high resource sharing
            ncd_val = self._ncd(prompt, cand)
            resource_share = 1.0 - ncd_val
            
            # 3. Free Energy Minimization
            # F = Cost - Lambda * Resource
            # We want to minimize F, so Score = -F = -Cost + Lambda * Resource
            # Since energy_cost is negative for violations, -cost adds positive penalty for violations
            score = (-energy_cost) + (self.lambda_resource * resource_share)
            
            # Structural Boost: If prompt has numbers, boost candidates with numbers
            if prompt_features['has_numeric'] and self._structural_parse(cand)['has_numeric']:
                score += 0.5

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Thermo-cost: {energy_cost:.2f}, Symbiosis: {resource_share:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and compression synergy.
        0.0 = High entropy (contradictory/unrelated), 1.0 = Low entropy (aligned).
        """
        # Evaluate single candidate against prompt
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
            
        base_score = ranked[0]['score']
        
        # Normalize to 0-1 range heuristically
        # Base score is roughly -10 to +1.5. 
        # Map [-5, 2] -> [0, 1]
        normalized = (base_score + 5.0) / 7.0
        return max(0.0, min(1.0, normalized))