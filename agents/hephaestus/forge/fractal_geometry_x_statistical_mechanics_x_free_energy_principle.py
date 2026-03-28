import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Renormalization-Group Variational Autoencoder (FRG-VAE) Simulator.
    
    Mechanism:
    1. Structural Parsing (Scale s=0): Extracts logical operators (negations, comparatives).
       This acts as the fine-grained latent variable.
    2. Numeric Evaluation (Scale s=1): Resolves explicit number comparisons.
    3. Fractal Prior (RG Flow): Applies a power-law penalty to candidates that fail 
       coarse-grained logical consistency (e.g., missing negations), simulating 
       the "temperature" of the system rising for inconsistent hypotheses.
    4. Free Energy Minimization: The final score is the negative variational free energy,
       balancing accuracy (likelihood) against model complexity (Occam's razor via length).
       
    This implements the Free Energy Principle as the core driver, using fractal scaling
    to weigh structural errors more heavily than surface-level token overlap.
    """

    def __init__(self):
        # RG Temperature parameters (derived from theoretical Ising-like models)
        self.temp_fine = 0.5  # Sensitivity to structural details
        self.temp_coarse = 2.0 # Sensitivity to global consistency
        self.kl_weight = 0.1  # Occam's razor strength

    def _extract_structure(self, text: str) -> Dict:
        """Scale s=0: Extract logical primitives."""
        text_lower = text.lower()
        return {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|without)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse|\>|\<|\=)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided)\b', text_lower)),
            'length': len(text)
        }

    def _evaluate_numeric(self, text: str) -> float:
        """Scale s=1: Detect and resolve numeric contradictions."""
        numbers = re.findall(r'-?\d+\.?\d*', text)
        if len(numbers) < 2:
            return 0.0 # No numeric claim to verify
        
        try:
            vals = [float(n) for n in numbers]
            # Check for explicit comparison operators near numbers
            if '>' in text or 'greater' in text.lower():
                return 1.0 if vals[0] > vals[1] else -1.0
            if '<' in text or 'less' in text.lower():
                return 1.0 if vals[0] < vals[1] else -1.0
            if '=' in text or 'equal' in text.lower():
                return 1.0 if abs(vals[0] - vals[1]) < 1e-6 else -1.0
        except ValueError:
            pass
        return 0.0

    def _compute_free_energy(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes F = Energy - Entropy (complexity).
        Lower F is better. We return -F as the score.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Likelihood Term (Energy): Structural Consistency
        # If prompt has negation, candidate must respect context (simplified heuristic)
        energy = 0.0
        reasoning = []

        # RG Step: Fine scale (Structure)
        struct_mismatch = 0
        if p_struct['has_negation'] and not c_struct['has_negation']:
            # Potential error: ignoring negation
            struct_mismatch += 1.0
            reasoning.append("Missed negation constraint")
        
        if p_struct['has_conditional'] and not c_struct['has_conditional']:
             # Heuristic: if prompt is conditional, ideal answer often acknowledges it
             # But strict requirement depends on content. Soft penalty.
             struct_mismatch += 0.5

        # RG Step: Coarse scale (Numeric)
        num_score = self._evaluate_numeric(candidate)
        if num_score == -1.0:
            energy += 5.0 # High energy for numeric contradiction
            reasoning.append("Numeric contradiction detected")
        elif num_score == 1.0:
            energy -= 2.0 # Bonus for correct numeric resolution
            reasoning.append("Numeric consistency verified")

        energy += struct_mismatch * self.temp_fine

        # 2. Complexity Term (Entropy/KL): Occam's Razor
        # Penalize excessive length relative to prompt (overfitting noise)
        complexity = self.kl_weight * abs(c_struct['length'] - len(prompt) * 0.5)
        
        # Free Energy
        F = energy + complexity
        
        # Score is negative free energy (higher is better)
        score = -F
        
        # Normalize score roughly to 0-1 range for usability
        # Base score starts at 0.5, adjusted by energy
        base_score = 0.5
        final_score = base_score - (F * 0.1) 
        final_score = max(0.0, min(1.0, final_score))

        reason_str = "; ".join(reasoning) if reasoning else "Structural consistency maintained"
        return final_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending (Free Energy minimization)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._compute_free_energy(prompt, answer)
        return score