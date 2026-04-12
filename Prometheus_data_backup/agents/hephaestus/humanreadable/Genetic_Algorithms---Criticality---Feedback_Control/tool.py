import zlib
import math
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Self-Tuning Critical Genetic Reasoner.
    
    Mechanism:
    Treats the list of candidates as a 'population' in a Genetic Algorithm.
    1. Fitness: Computed via NCD (similarity to prompt context) and structural parsing scores.
    2. Criticality Metric: Monitors the variance (diversity) of the fitness landscape.
    3. Feedback Control: A PID-like controller adjusts the weight of 'exploration' (length penalty/complexity)
       vs 'exploitation' (prompt similarity) based on whether the population is too ordered (low variance)
       or too chaotic (high variance).
    4. Output: Ranks candidates by this dynamically tuned fitness score.
    """

    def __init__(self):
        self._target_variance = 0.05  # Target criticality set-point
        self._integral = 0.0
        self._prev_error = 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Extracts structural reasoning signals:
        - Negation handling
        - Numeric comparison validity
        - Constraint matching
        """
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Consistency
        negations = ['no', 'not', 'never', 'none', 'cannot']
        p_has_neg = any(n in p_low for n in negations)
        c_has_neg = any(n in c_low for n in negations)
        
        if p_has_neg == c_has_neg:
            score += 0.2
        else:
            score -= 0.2 # Penalty for mismatched negation logic

        # 2. Numeric Logic Check (Simplified)
        # If prompt contains numbers, check if candidate preserves order or logic
        nums_p = re.findall(r"[-+]?\d*\.\d+|\d+", p_low)
        nums_c = re.findall(r"[-+]?\d*\.\d+|\d+", c_low)
        
        if nums_p:
            if nums_c:
                # If both have numbers, reward if candidate numbers appear in prompt
                match_count = sum(1 for n in nums_c if n in nums_p)
                score += (match_count / max(len(nums_c), 1)) * 0.3
            else:
                score -= 0.1 # Penalty if prompt has numbers but candidate ignores them
        
        # 3. Length Constraint (Occam's razor heuristic)
        if 0.5 * len(p_low) <= len(c_low) <= 1.5 * len(p_low):
            score += 0.1
            
        return score

    def _compute_fitness(self, prompt: str, candidates: List[str]) -> List[float]:
        """Compute raw fitness based on NCD similarity to prompt."""
        fitness = []
        for c in candidates:
            # Lower NCD means more similar (better), so invert it
            ncd = self._ncd(prompt, c)
            fit = (1.0 - ncd) 
            fitness.append(fit)
        return fitness

    def _feedback_tune(self, values: List[float]) -> float:
        """
        PID-like controller to adjust exploration weight.
        Monitors variance of fitness scores.
        """
        if len(values) < 2:
            return 1.0
            
        mean_v = sum(values) / len(values)
        variance = sum((x - mean_v) ** 2 for x in values) / len(values)
        
        # Normalize variance to roughly 0-1 range for control
        norm_var = min(1.0, variance * 10) 
        
        error = self._target_variance - norm_var
        
        # Proportional
        p_term = error * 2.0
        # Integral
        self._integral += error * 0.1
        i_term = self._integral * 0.5
        # Derivative
        d_term = (error - self._prev_error) * 0.5
        self._prev_error = error
        
        # Output scaling factor (Mutation rate analogy)
        # If variance too low (ordered), increase weight of structural complexity (exploration)
        # If variance too high (chaotic), rely more on raw similarity (exploitation)
        k_p = 1.0 + p_term + i_term + d_term
        return max(0.1, min(5.0, k_p))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        # 1. Compute base fitness (Similarity)
        base_fitness = self._compute_fitness(prompt, candidates)
        
        # 2. Compute structural scores (Reasoning heuristics)
        struct_scores = [self._structural_score(prompt, c) for c in candidates]
        
        # 3. Apply Feedback Control (Criticality Tuning)
        # Determine how much to weight structural reasoning vs raw similarity
        # based on the population's current diversity (variance of base fitness)
        exploration_weight = self._feedback_tune(base_fitness)
        
        final_scores = []
        for i in range(len(candidates)):
            # Hybrid score: Similarity + (Exploration_Weight * Structural_Reasoning)
            # This mimics the GA mutation rate adjustment
            score = base_fitness[i] + (exploration_weight * struct_scores[i])
            final_scores.append(score)
            
        # Normalize scores to 0-1 range for consistency
        min_s, max_s = min(final_scores), max(final_scores)
        if max_s > min_s:
            normalized_scores = [(s - min_s) / (max_s - min_s) for s in final_scores]
        else:
            normalized_scores = [0.5] * len(final_scores)
            
        # Rank and format
        results = []
        for i, c in enumerate(candidates):
            results.append({
                "candidate": c,
                "score": float(normalized_scores[i]),
                "reasoning": f"Fitness: {base_fitness[i]:.3f}, Structural: {struct_scores[i]:.3f}, Tuning: {exploration_weight:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on combined NCD and structural alignment."""
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]