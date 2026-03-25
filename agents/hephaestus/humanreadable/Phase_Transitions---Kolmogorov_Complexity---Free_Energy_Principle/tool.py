import zlib
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Phase-Transition Inference (VPTI) Approximation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives) 
       to form a "high-bias" structural score (Free Energy minimization).
    2. Approximate Kolmogorov Complexity: Uses zlib compression length as a proxy 
       for hypothesis complexity (C(z)).
    3. Phase Transition Control: 
       - Calculates a "prediction error" based on structural mismatch.
       - If error is high, the system crosses a critical beta threshold, shifting 
         weight from simple structural heuristics to complex description length analysis.
       - This mimics the transition from low-complexity/high-bias to high-complexity/low-bias regimes.
    4. Scoring: Combines structural validity and complexity penalties dynamically.
    """

    def __init__(self):
        # Critical temperature for phase transition
        self.beta_critical = 0.5
        # Base complexity penalty weight
        self.lambda_complexity = 0.005 

    def _get_compression_length(self, text: str) -> int:
        """Approximate Kolmogorov complexity via zlib."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _parse_structure(self, prompt: str, candidate: str) -> Tuple[float, List[str]]:
        """
        Extract structural features: negations, comparatives, numbers.
        Returns a score (0-1) and a list of detected constraints.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        constraints = []

        # 1. Negation Check
        negations = ['not', 'no', 'never', 'cannot', 'impossible']
        has_negation_prompt = any(n in p_lower for n in negations)
        has_negation_cand = any(n in c_lower for n in negations)
        
        if has_negation_prompt:
            constraints.append("negation_present")
            if has_negation_cand:
                score += 0.4
            else:
                score -= 0.4 # Penalty for missing negation
        
        # 2. Numeric Comparison Logic
        numbers_p = re.findall(r"-?\d+\.?\d*", p_lower)
        numbers_c = re.findall(r"-?\d+\.?\d*", c_lower)
        
        if numbers_p and numbers_c:
            try:
                # Simple heuristic: if prompt asks for comparison, candidate should reflect order
                vals_p = [float(n) for n in numbers_p]
                vals_c = [float(n) for n in numbers_c]
                
                # Check if candidate preserves relative magnitude found in prompt context
                if len(vals_p) >= 2 and len(vals_c) >= 1:
                    # Detect comparative keywords
                    is_greater = any(k in p_lower for k in ['larger', 'greater', 'more', 'higher', 'max'])
                    is_lesser = any(k in p_lower for k in ['smaller', 'less', 'lower', 'min'])
                    
                    max_p = max(vals_p)
                    min_p = min(vals_p)
                    
                    if is_greater and vals_c[0] == max_p:
                        score += 0.5
                    elif is_lesser and vals_c[0] == min_p:
                        score += 0.5
                    elif is_greater and vals_c[0] == min_p:
                        score -= 0.5
                    elif is_lesser and vals_c[0] == max_p:
                        score -= 0.5
            except ValueError:
                pass

        # 3. Constraint Propagation (Simple keyword overlap for logic chains)
        logic_keys = ['if', 'then', 'because', 'therefore', 'so']
        if any(k in p_lower for k in logic_keys):
            # Candidate should ideally share key logical connectors or terms
            common_terms = set(p_lower.split()) & set(c_lower.split())
            if len(common_terms) > 2:
                score += 0.2
        
        return min(1.0, max(0.0, score)), constraints

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute the variational free energy analogue.
        F = Prediction_Error + Beta * Complexity
        """
        # 1. Prediction Error (Structural Mismatch)
        # We invert the structural score to get an 'error' term. 
        # High structural alignment = Low error.
        struct_score, _ = self._parse_structure(prompt, candidate)
        prediction_error = 1.0 - struct_score
        
        # 2. Complexity Term (Kolmogorov Approx)
        # Normalize complexity by prompt length to get relative complexity
        c_len = self._get_compression_length(candidate)
        p_len = max(1, self._get_compression_length(prompt))
        relative_complexity = c_len / p_len
        
        # 3. Phase Transition Mechanism
        # If prediction error is high, we are in a 'crisis' state.
        # We increase beta to allow higher complexity hypotheses (phase transition).
        # If error is low, we stay in low-complexity phase (Occam's razor).
        if prediction_error > 0.6:
            beta = 1.5  # High temp: Explore complex solutions
        else:
            beta = 0.2  # Low temp: Exploit simple solutions
            
        # Free Energy Calculation
        free_energy = prediction_error + (beta * self.lambda_complexity * relative_complexity)
        
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        energies = []
        
        # First pass: calculate energies
        for cand in candidates:
            energy = self._calculate_free_energy(prompt, cand)
            energies.append(energy)
        
        # Normalize energies to scores (lower energy = higher score)
        # Using softmax-like transformation with temperature
        min_e = min(energies)
        max_e = max(energies)
        range_e = max_e - min_e if max_e > min_e else 1.0
        
        for i, cand in enumerate(candidates):
            # Normalize energy to 0-1 range (inverted so high score = good)
            norm_energy = (energies[i] - min_e) / range_e
            score = 1.0 - norm_energy
            
            # Add small deterministic tie-breaker based on length (prefer concise)
            score -= (len(cand) * 1e-6)
            
            results.append({
                "candidate": cand,
                "score": round(score, 6),
                "reasoning": f"Free energy: {energies[i]:.4f}. Phase state: {'High-Complexity' if energies[i] > 0.5 else 'Low-Complexity'}."
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Derived from the inverse of the free energy normalized to probability space.
        """
        energy = self._calculate_free_energy(prompt, answer)
        
        # Map energy to confidence. 
        # Low energy (<0.2) -> High confidence (~0.9+)
        # High energy (>1.0) -> Low confidence (~0.1-)
        # Using exponential decay for smooth mapping
        confidence = math.exp(-2.0 * energy)
        
        return min(1.0, max(0.0, confidence))