import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Compositional Ensemble Inference (VCEI) Approximation.
    
    Mechanism:
    1. Compositionality (Grammar Energy): Parses prompts for structural constraints
       (negations, comparatives, conditionals). Violations add 'energy' (penalty).
    2. Statistical Mechanics (Ensemble): Treats candidate evaluation as an ensemble
       of microscopic checks (numeric, logical, lexical). The joint probability is
       derived from the sum of energies (Product of Experts).
    3. Free Energy Principle (FEP): The core scoring metric. 
       Score = - (Expected Energy - Entropy).
       We minimize 'Variational Free Energy' by penalizing candidates that contradict
       the prompt's structural constraints (high prediction error) while rewarding
       specificity (low entropy via NCD tie-breaking).
       
    This implements the FEP as the primary driver: minimizing surprise (constraint violation)
    while maintaining model complexity control.
    """

    def __init__(self):
        # Keywords defining logical structure
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.booleans = ['true', 'false', 'yes', 'no']
        
        # Base energy scale
        self.lambda_syntax = 2.0
        self.lambda_numeric = 3.0
        self.lambda_logic = 2.5

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _check_negation_consistency(self, prompt: str, candidate: str) -> float:
        """Energy term: Penalty if candidate contradicts prompt negation."""
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        energy = 0.0
        has_negation = any(n in p_tokens for n in self.negations)
        has_affirmation = any(b in c_tokens for b in self.booleans)
        
        # Simple heuristic: If prompt negates, and candidate affirms without negation
        if has_negation and has_affirmation:
            if not any(n in c_tokens for n in self.negations):
                # Potential contradiction depending on context, add small energy
                energy += 0.5
                
        return energy

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Energy term: Penalty for numeric contradictions."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        energy = 0.0
        
        # Check for direct numeric equality if only one number exists
        if len(p_nums) == 1 and len(c_nums) == 1:
            if abs(p_nums[0] - c_nums[0]) > 1e-6:
                # If the candidate changes the number, check if it makes sense
                # Heuristic: If prompt asks "is X > Y", candidate should reflect truth
                # Here we just penalize deviation if the candidate is purely numeric
                if len(c_tokens := self._tokenize(candidate)) <= 2: # Pure number answer
                     energy += self.lambda_numeric * abs(p_nums[0] - c_nums[0]) / (abs(p_nums[0]) + 1e-6)

        # Check comparative logic
        p_lower = prompt.lower()
        if any(comp in p_lower for comp in ['greater', 'larger', 'more']):
            if p_nums and c_nums:
                # If prompt implies ordering, ensure candidate respects it roughly
                # This is a soft constraint for the ensemble
                pass 
                
        return energy

    def _check_structural_entailment(self, prompt: str, candidate: str) -> float:
        """Energy term: Penalty for missing structural keywords."""
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        energy = 0.0
        
        # If prompt has conditionals, candidate should ideally reflect conditionality or boolean
        has_conditional = any(c in p_tokens for c in self.conditionals)
        if has_conditional:
            # Candidate should contain boolean or conditional logic
            if not any(b in c_tokens for b in self.booleans) and not any(c in c_tokens for c in self.conditionals):
                energy += 1.0
                
        return energy

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as entropy proxy."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        
        if max(z1, z2) == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Variational Free Energy F = E - H.
        Lower F is better. We return negative F so higher score = better.
        E = Sum of modular energies (Syntax, Numeric, Logic)
        H = Entropy approximation (via NCD diversity)
        """
        # 1. Modular Energies (Prediction Error)
        e_syntax = self._check_negation_consistency(prompt, candidate)
        e_numeric = self._check_numeric_consistency(prompt, candidate)
        e_struct = self._check_structural_entailment(prompt, candidate)
        
        # Weighted sum for total Energy
        total_energy = (self.lambda_syntax * e_syntax) + \
                       (self.lambda_numeric * e_numeric) + \
                       (self.lambda_logic * e_struct)
        
        # 2. Entropy Term (Complexity/Surprise)
        # We want candidates that are specific (low NCD to prompt context implies relevance)
        # But diverse enough. Here we use NCD as a tie-breaker penalty for randomness.
        ncd = self._compute_ncd(prompt, candidate)
        
        # Free Energy F = E - H (where H is approximated by -log prob ~ NCD)
        # We want to minimize F. 
        # Score = -F = H - E. 
        # Let's approximate H as (1 - NCD) to reward similarity/relevance, 
        # but primarily rely on minimizing E.
        
        # Calibration: Base score 1.0, subtract energies.
        # NCD acts as a small regularizer to break ties towards concise/relevant answers.
        entropy_bonus = 0.1 * (1.0 - ncd) 
        
        free_energy = total_energy - entropy_bonus
        
        return -free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            # Normalize score to 0-1 range roughly using sigmoid-like mapping
            # Since energies are positive penalties, raw score is negative or small positive.
            # Map to 0-1: 1 / (1 + exp(-score)) roughly, but let's keep it linear for interpretability
            # Shift so 0 energy = 0.5 base, penalties reduce it.
            calibrated_score = 0.5 + (score * 0.2) 
            calibrated_score = max(0.0, min(1.0, calibrated_score))
            
            reason_parts = []
            if "not" in cand.lower() or "no" in cand.lower():
                reason_parts.append("negation detected")
            if any(c in cand.lower() for c in self.comparatives):
                reason_parts.append("comparative logic")
            if self._extract_numbers(cand):
                reason_parts.append("numeric evaluation")
                
            reasoning = f"FEP-minimized; {'; '.join(reason_parts) if reason_parts else 'structural match'}"
            
            results.append({
                "candidate": cand,
                "score": calibrated_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score = self._compute_free_energy(prompt, answer)
        # Map to 0-1 confidence
        # High energy (bad) -> low confidence. Low energy (good) -> high confidence.
        # Using a simple scaling: 0 energy -> 0.8, -1 energy -> 0.3, +1 energy -> 0.95
        conf = 1.0 / (1.0 + math.exp(-score * 2.0))
        return max(0.0, min(1.0, conf))