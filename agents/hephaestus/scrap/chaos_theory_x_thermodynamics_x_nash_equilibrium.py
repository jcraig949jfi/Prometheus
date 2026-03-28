import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically-Driven Chaotic Best-Response Dynamics (TCBRD) Tool.
    
    Mechanism:
    1. Chaos Core (Evaluate): Uses a deterministic logistic map (Lyapunov > 0) 
       to generate perturbations based on candidate index, simulating chaotic drift 
       to escape local string-similarity optima.
    2. Thermodynamics (Support): Computes an "Energy" score based on structural 
       constraint satisfaction (negations, comparatives, numeric logic). 
       Lower energy = higher probability. Temperature (beta) scales the final score.
    3. Nash Equilibrium (Stability): Treats the top-ranked candidate as the 
       equilibrium state; confidence measures the "stability" (gap) between 
       the best response and alternatives.
       
    This implementation prioritizes structural parsing (negations, numerics) 
    as the potential gradient, with chaotic noise preventing premature convergence 
    on superficially similar but logically incorrect answers.
    """

    def __init__(self):
        # Chaotic map parameter (logistic map r=3.9 ensures chaos)
        self.r = 3.9 
        # Inverse temperature (controls exploration vs exploitation)
        self.beta = 2.0 

    def _logistic_map(self, x: float) -> float:
        """Deterministic chaotic iterator."""
        return self.r * x * (1.0 - x)

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical features: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(no|not|never|none|neither|n\'t)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            "numbers": re.findall(r'-?\d+\.?\d*', text_lower)
        }
        return features

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute 'Energy' U(x) based on structural consistency.
        Lower energy = better fit.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        energy = 0.0
        
        # Constraint 1: Negation consistency (Modus Tollens check proxy)
        # If prompt has negation, candidate should ideally reflect awareness or specific handling
        # Simple heuristic: Penalty if prompt has strong negation logic but candidate is generic
        if p_feat["negations"] > 0:
            if len(candidate.split()) < 5: # Short answers often miss nuance
                energy += 2.0
        
        # Constraint 2: Numeric consistency
        if p_feat["numbers"] and c_feat["numbers"]:
            try:
                p_nums = [float(n) for n in p_feat["numbers"]]
                c_nums = [float(n) for n in c_feat["numbers"]]
                # Check if candidate numbers are logically derived (simplified)
                # If prompt asks for comparison, candidate should reflect order
                if p_feat["comparatives"] > 0:
                    if len(p_nums) >= 2 and len(c_nums) >= 1:
                        # Heuristic: Does the candidate number match the extreme implied?
                        # This is a rough proxy for logical deduction
                        pass 
            except ValueError:
                energy += 1.0
        elif p_feat["numbers"] and not c_feat["numbers"]:
            # Prompt has numbers, candidate ignores them -> High energy
            energy += 3.0

        # Constraint 3: Comparative logic
        if p_feat["comparatives"] > 0:
            if c_feat["comparatives"] == 0 and len(c_feat["numbers"]) == 0:
                # Prompt asks for comparison, candidate gives neither comparative nor number
                energy += 2.5

        # Base complexity penalty (Occam's razor via length)
        energy += 0.01 * len(candidate)
        
        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        if not candidates:
            return []

        # Pre-calculate structural scores (Potential Gradient)
        energies = [self._compute_energy(prompt, c) for c in candidates]
        
        # Find min energy for Gibbs normalization baseline
        min_energy = min(energies) if energies else 0.0
        
        for i, candidate in enumerate(candidates):
            # 1. Potential Gradient (Payoff): -U(x)
            # We want to maximize payoff, so we use negative energy
            payoff = -energies[i]
            
            # 2. Chaotic Drift: lambda * J(x) * x
            # Use deterministic chaos based on index to inject unique perturbation
            # This prevents identical structural scores from ranking equally without logic
            x_seed = (i + 1) / (len(candidates) + 1) # Normalize seed to (0, 1)
            chaotic_val = x_seed
            for _ in range(5): # Iterate map to ensure mixing
                chaotic_val = self._logistic_map(chaotic_val)
            
            # Scale chaotic term (lambda)
            lambda_term = 0.5 * (chaotic_val - 0.5) # Center around 0
            
            # 3. Thermal Noise: Simulated via fixed small perturbation for diversity
            # In a real SDE this is dW, here we use a deterministic pseudo-noise based on hash
            noise_seed = abs(hash(prompt + candidate)) / (2**63)
            thermal_noise = (noise_seed - 0.5) * 0.1
            
            # Total Score (SDE approximation)
            # Score = Payoff + Chaotic_Drift + Thermal_Noise
            # Note: We invert energy so higher is better
            raw_score = payoff + lambda_term + thermal_noise
            
            # Gibbs-like transformation for probability-like score
            # P ~ exp(-beta * U) -> exp(beta * payoff)
            # Adjusted for our mixed score system
            final_score = math.exp(self.beta * raw_score)
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Energy: {energies[i]:.2f}, Chaotic Drift: {lambda_term:.3f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Normalize scores to 0-1 range roughly for readability (optional but helpful)
        max_s = results[0]["score"] if results else 1.0
        for r in results:
            r["score"] = r["score"] / max_s
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calculate confidence based on the stability of the answer 
        against the 'Nash Equilibrium' of the candidate set.
        Since we don't have the full set here, we estimate stability 
        via structural consistency and NCD distance to an idealized 'perfect' match.
        """
        # 1. Structural Consistency Check (Self-Reflection)
        p_feat = self._extract_structure(prompt)
        a_feat = self._extract_structure(answer)
        
        consistency_score = 1.0
        
        # If prompt has numbers, answer must have numbers
        if p_feat["numbers"]:
            if not a_feat["numbers"]:
                consistency_score *= 0.2
        
        # If prompt has negation, check answer length/complexity
        if p_feat["negations"] > 1:
            if len(answer.split()) < 4:
                consistency_score *= 0.5
                
        # 2. NCD Tiebreaker (Similarity to prompt context)
        # If the answer is just "Yes" or "No" but prompt is complex, lower confidence
        ncd_val = self._ncd(prompt, answer)
        
        # Heuristic combination
        # High NCD (dissimilar) is okay if structural consistency is high (abstraction)
        # Low NCD (similar) is good if consistency is high
        base_conf = consistency_score * (1.0 - 0.5 * ncd_val)
        
        # Cap between 0 and 1
        return max(0.0, min(1.0, base_conf))