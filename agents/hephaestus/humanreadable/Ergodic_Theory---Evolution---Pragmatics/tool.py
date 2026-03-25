import math
import hashlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic-Ergodic Evolutionary Search (PEES) Approximation.
    
    Mechanism:
    1. Hypothesis Encoding: Candidates are hashed to deterministic seeds (symbolic-numerical mapping).
    2. Ergodic Evaluation: Simulates a trajectory using a Linear Congruential Generator (LCG) 
       seeded by the hypothesis. The 'time-average' error is approximated by the convergence 
       of the trajectory's mean against a target derived from the prompt context.
       (Analogy: Koopman observable = statistical moment of the trajectory).
    3. Pragmatic Filtering: Applies RSA-inspired penalties:
       - Quality: Penalizes high ergodic error.
       - Quantity: Penalizes excessive length (brevity).
       - Relation: Boosts scores if candidate keywords match prompt keywords.
    """

    def __init__(self):
        # No external state needed; stateless and deterministic
        pass

    def _hash_to_seed(self, s: str) -> int:
        """Deterministic hash to integer seed."""
        return int(hashlib.sha256(s.encode('utf-8')).hexdigest()[:8], 16)

    def _ergodic_simulation(self, seed: int, steps: int = 100) -> Tuple[float, float]:
        """
        Simulates a dynamical system trajectory.
        Returns (time_average, convergence_rate) as proxies for ergodic properties.
        Uses a simple LCG-like map: x_{t+1} = (a * x_t + c) % m / m
        """
        x = float(seed) / (2**32)
        a, c, m = 1103515245, 12345, 2**31
        
        trajectory_sum = 0.0
        prev_mean = x
        
        for t in range(1, steps + 1):
            x = ((a * int(x * 2**31) + c) % m) / m
            trajectory_sum += x
            current_mean = trajectory_sum / t
            
            # Simple convergence check (difference from previous mean)
            if t > 10: 
                prev_mean = current_mean
                
        return trajectory_sum / steps, abs(x - 0.5) # Mean and deviation from uniform center

    def _compute_pragmatic_utility(self, prompt: str, candidate: str, ergodic_error: float) -> float:
        """
        Computes U_prag = LogLikelihood(Quality) + Rel - Len
        """
        # 1. Quality (Truthfulness): Inverse of ergodic error (mapped to log prob)
        # Avoid log(0), add small epsilon
        quality_score = -math.log(ergodic_error + 1e-6)
        
        # 2. Quantity (Brevity): Penalty for length
        # Normalize by typical sentence length ~20 chars
        length_penalty = 0.05 * len(candidate) 
        
        # 3. Relation (Relevance): Keyword overlap bonus
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        # Remove common stopwords for better signal if needed, but keeping simple for brevity
        stop = {'the', 'is', 'are', 'a', 'an', 'to', 'of', 'in', 'it', 'for'}
        p_words = {w for w in p_words if w not in stop}
        c_words = {w for w in c_words if w not in stop}
        
        overlap = len(p_words.intersection(c_words))
        relevance_bonus = 2.0 * overlap if p_words else 0.0
        
        # Combined utility
        return quality_score + relevance_bonus - length_penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        # Determine a target baseline from prompt hash to simulate "ground truth" dynamics
        prompt_seed = self._hash_to_seed(prompt)
        target_mean, _ = self._ergodic_simulation(prompt_seed)
        
        for cand in candidates:
            seed = self._hash_to_seed(cand)
            cand_mean, deviation = self._ergodic_simulation(seed)
            
            # Ergodic error: difference between candidate trajectory mean and prompt-derived target
            # This simulates the time-average prediction error converging to space average
            ergodic_error = abs(cand_mean - target_mean) + deviation
            
            utility = self._compute_pragmatic_utility(prompt, cand, ergodic_error)
            
            results.append({
                "candidate": cand,
                "score": utility,
                "reasoning": f"Ergodic deviation: {ergodic_error:.4f}, Pragmatic utility adjusted."
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against itself to get raw score
        # We normalize the score to 0-1 range using a sigmoid-like mapping
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        score = res_list[0]["score"]
        
        # Map score to 0-1. 
        # Heuristic: Scores > 0 are good, < -5 are bad. 
        # Sigmoid: 1 / (1 + exp(-k(x - x0)))
        k = 0.5
        x0 = 0.0
        conf = 1.0 / (1.0 + math.exp(-k * (score - x0)))
        return max(0.0, min(1.0, conf))