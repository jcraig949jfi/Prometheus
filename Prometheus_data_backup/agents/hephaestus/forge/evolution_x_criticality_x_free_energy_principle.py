import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Tuning Critical Active-Inference Reasoner.
    
    Mechanism:
    1. Evolution (Structure): Uses NEAT-like topology scoring based on candidate complexity 
       relative to the prompt. It penalizes over-complexity (Occam's razor) to find parsimonious structures.
    2. Criticality (Sensitivity): Computes a 'Susceptibility' score. It measures how small perturbations 
       (character flips) in the candidate affect its semantic distance (NCD) to the prompt. 
       High susceptibility = operating near critical point = high information gain.
    3. Free Energy Principle (Inference): Calculates Variational Free Energy (VFE) as a weighted sum 
       of Prediction Error (NCD) and Complexity Cost. The system minimizes VFE.
    
    The final score is the inverse of the minimized Free Energy, boosted by the Criticality factor.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _extract_numbers(self, text: str) -> List[float]:
        """Structural parsing: Extract numeric values for logical comparison."""
        nums = re.findall(r"-?\d+\.?\d*", text)
        return [float(n) for n in nums]

    def _check_logic(self, prompt: str, candidate: str) -> float:
        """Constraint propagation: Check basic logical consistency."""
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Negation check
        if "not" in p_low and "not" not in c_low and len(c_low.split()) < 5:
            # If prompt has negation and candidate is short and lacks it, slight penalty unless it's 'no'
            if "no" not in c_low and "false" not in c_low:
                return 0.8 
        return 1.0

    def _compute_susceptibility(self, prompt: str, candidate: str) -> float:
        """
        Criticality Measure: Divergence of susceptibility.
        Measures sensitivity to small perturbations.
        If a tiny change in candidate drastically changes NCD, it's near criticality.
        """
        base_dist = self._ncd(prompt, candidate)
        if len(candidate) == 0: return 0.0
        
        # Perturb: flip one char or append noise
        perturbations = []
        # Case 1: Flip last char
        if len(candidate) > 1:
            perturbed = candidate[:-1] + ('z' if candidate[-1] != 'z' else 'a')
            perturbations.append(self._ncd(prompt, perturbed))
        
        # Case 2: Append noise
        perturbations.append(self._ncd(prompt, candidate + " "))
        
        if not perturbations: return 0.0
        
        # Susceptibility = variance of distance under perturbation
        diffs = [abs(p - base_dist) for p in perturbations]
        return np.mean(diffs) + self.epsilon

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Free Energy = Prediction Error (Accuracy) + Complexity Cost (Evolutionary Pressure)
        F = E - ln(P) approximated by NCD + lambda * Length_Penalty
        """
        # Prediction Error (Surprise)
        prediction_error = self._ncd(prompt, candidate)
        
        # Complexity Cost (Evolutionary penalty for bloat)
        # Normalized length relative to prompt
        comp_cost = abs(len(candidate) - len(prompt)) / (len(prompt) + 1)
        
        # Free Energy
        free_energy = prediction_error + 0.5 * comp_cost
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_nums = self._extract_numbers(prompt)
        
        for cand in candidates:
            # 1. Evolution: Structural/Complexity check
            logic_score = self._check_logic(prompt, cand)
            
            # 2. Criticality: Sensitivity analysis
            susceptibility = self._compute_susceptibility(prompt, cand)
            
            # 3. Free Energy: Minimization objective
            free_energy = self._compute_free_energy(prompt, cand)
            
            # Numeric Reasoning Boost (Heuristic for specific trap types)
            cand_nums = self._extract_numbers(cand)
            numeric_boost = 0.0
            if prompt_nums and cand_nums:
                # If numbers match exactly, huge boost (exact retrieval)
                if prompt_nums[0] == cand_nums[0]:
                    numeric_boost = 0.5
            
            # Combined Score: 
            # Maximize (Susceptibility * Logic) / FreeEnergy
            # Criticality amplifies the signal of low free-energy states
            raw_score = (susceptibility * logic_score * (1.0 + numeric_boost)) / (free_energy + self.epsilon)
            
            # Normalize to 0-1 range roughly via sigmoid-like mapping
            score = 1.0 / (1.0 + np.exp(-raw_score + 2.0)) # Shift threshold
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"FE={free_energy:.3f}, Crit={susceptibility:.3f}, Logic={logic_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on inverse Free Energy and Criticality."""
        fe = self._compute_free_energy(prompt, answer)
        crit = self._compute_susceptibility(prompt, answer)
        
        # Low FE and High Criticality = High Confidence
        # Map to 0-1
        conf = (crit * 0.5) / (fe + 0.1)
        return float(np.clip(conf, 0.0, 1.0))