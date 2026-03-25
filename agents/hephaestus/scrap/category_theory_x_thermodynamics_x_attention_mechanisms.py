import numpy as np
from typing import List, Dict
import math

class ReasoningTool:
    """
    CTAT-inspired Reasoning Tool.
    Mechanism: Simulates a thermodynamic attention system where candidate scores are 
    derived from a Boltzmann distribution of 'energy' (semantic dissimilarity). 
    Confidence is inversely proportional to the computed entropy production (uncertainty),
    mimicking the free-energy principle's use of entropy to gauge model fit.
    """
    def __init__(self):
        self.temperature = 0.5  # Controls exploration vs exploitation
        np.random.seed(42)      # Determinism

    def _tokenize(self, text: str) -> set:
        return set(text.lower().split())

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        # Energy E is inverse similarity. Higher distance = Higher Energy.
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        if not p_tokens or not c_tokens:
            return 1.0
        
        # Jaccard distance as proxy for energy
        intersection = len(p_tokens & c_tokens)
        union = len(p_tokens | c_tokens)
        similarity = intersection / union if union > 0 else 0
        return 1.0 - similarity

    def _softmax(self, energies: List[float]) -> List[float]:
        # Boltzmann distribution: alpha = exp(-E/T) / sum(exp(-E/T))
        exp_vals = [math.exp(-e / self.temperature) for e in energies]
        total = sum(exp_vals)
        if total == 0: return [0.0] * len(energies)
        return [e / total for e in exp_vals]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        energies = [self._compute_energy(prompt, c) for c in candidates]
        weights = self._softmax(energies)
        
        # Rank by score (higher weight = lower energy = better)
        ranked = sorted(zip(candidates, weights, energies), key=lambda x: x[1], reverse=True)
        
        results = []
        for cand, score, energy in ranked:
            # Reasoning based on thermodynamic interpretation
            reason = f"Low energy state ({energy:.2f}); high probability mass ({score:.4f})."
            results.append({"candidate": cand, "score": score, "reasoning": reason})
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate against a dummy set containing only the answer to isolate its thermodynamics
        # In a full system, this would compare the single state to the partition function Z
        energy = self._compute_energy(prompt, answer)
        
        # Simulate a baseline 'noise' energy to compute relative stability
        # If energy is low (high similarity), confidence approaches 1
        # We map energy [0, 1] to confidence [1, 0] using a sigmoid-like decay
        confidence = 1.0 / (1.0 + math.exp((energy - 0.5) / self.temperature))
        
        return max(0.0, min(1.0, confidence))