import random
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical-Adaptive Program Synthesizer (CAPS) Approximation.
    
    Mechanism:
    1. Program Synthesis Analogy: Candidates are treated as 'programs' in a search space.
    2. Self-Organized Criticality (SOC): We simulate a sandpile. Each evaluation step adds 'stress'.
       If stress exceeds a threshold, an 'avalanche' occurs (a burst of re-evaluation/refinement).
       The system tracks avalanche sizes to estimate the critical exponent.
    3. Adaptive Control: A controller adjusts the 'mutation rate' (randomness in scoring) based on 
       how close the current avalanche dynamics are to a target power-law distribution (criticality).
       This balances exploration (high mutation) vs exploitation (low mutation).
       
    The result is a scoring system that dynamically adjusts its sensitivity to errors based on 
    the statistical history of 'failures' (avalanches), mimicking a system poised at the edge of chaos.
    """

    def __init__(self):
        # SOC State: Stress level and history of avalanche sizes
        self.stress = 0.0
        self.threshold = 10.0
        self.avalanche_history = [] 
        self.max_history = 50
        
        # Adaptive Control State
        self.mutation_rate = 0.1  # Exploration factor
        self.target_exponent = 1.5 # Target power law exponent for criticality
        
        # Determinism seed
        self._seed = 42
        random.seed(self._seed)

    def _update_soc(self, error_magnitude: float) -> int:
        """
        Simulates adding stress to the sandpile. 
        Returns the size of the resulting avalanche (number of topples).
        """
        self.stress += error_magnitude
        avalanche_size = 0
        
        # Topple if critical
        while self.stress >= self.threshold:
            self.stress -= self.threshold
            avalanche_size += 1
            # Redistribute stress (simplified dissipation)
            self.stress += 0.5 * random.random() 
            
        if avalanche_size > 0:
            self.avalanche_history.append(avalanche_size)
            if len(self.avalanche_history) > self.max_history:
                self.avalanche_history.pop(0)
                
        return avalanche_size

    def _adapt_control(self):
        """
        Adjusts mutation rate based on the estimated power-law exponent of avalanches.
        If avalanches are too small (sub-critical), increase exploration.
        If too large (super-critical), decrease exploration.
        """
        if len(self.avalanche_history) < 5:
            return

        # Estimate exponent using log-log linear regression approximation
        # Frequency ~ Size^-alpha
        counts = {}
        for s in self.avalanche_history:
            counts[s] = counts.get(s, 0) + 1
            
        if len(counts) < 2:
            return

        xs = [] # log(size)
        ys = [] # log(frequency)
        for size, freq in counts.items():
            if size > 0 and freq > 0:
                xs.append(math.log(size + 1e-6))
                ys.append(math.log(freq + 1e-6))
        
        if len(xs) < 2:
            return

        # Simple linear regression for slope
        n = len(xs)
        sum_x = sum(xs)
        sum_y = sum(ys)
        sum_xy = sum(x*y for x, y in zip(xs, ys))
        sum_xx = sum(x*x for x in xs)
        
        denom = n * sum_xx - sum_x * sum_x
        if abs(denom) < 1e-6:
            return
            
        slope = (n * sum_xy - sum_x * sum_y) / denom
        estimated_exponent = -slope

        # Adaptive step: Move mutation rate towards keeping exponent near target
        # If exponent is too high (steep dropoff, small avalanches), we need more stress/diversity -> increase mutation
        # If exponent is too low (flat, huge avalanches), we need stability -> decrease mutation
        error = estimated_exponent - self.target_exponent
        self.mutation_rate -= 0.05 * error
        
        # Clamp mutation rate
        self.mutation_rate = max(0.01, min(0.5, self.mutation_rate))

    def _compute_base_score(self, prompt: str, candidate: str) -> float:
        """
        Heuristic scoring based on string matching and length constraints.
        Simulates a basic program checker.
        """
        if not candidate.strip():
            return 0.0
            
        prompt_words = set(prompt.lower().split())
        cand_words = set(candidate.lower().split())
        
        # Overlap ratio
        intersection = len(prompt_words & cand_words)
        union = len(prompt_words | cand_words)
        overlap = (intersection / union) if union > 0 else 0.0
        
        # Penalty for being too short or too long relative to prompt
        len_ratio = len(candidate) / (len(prompt) + 1)
        len_score = 1.0 / (1.0 + abs(len_ratio - 0.5)) # Prefer length ~ half of prompt
        
        return (overlap * 0.7 + len_score * 0.3)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # 1. Base evaluation (Synthesis check)
            base_score = self._compute_base_score(prompt, cand)
            
            # 2. Calculate error magnitude for SOC (distance from perfect 1.0)
            error_mag = (1.0 - base_score) * 10.0
            
            # 3. SOC Step: Add stress, check for avalanche
            avalanche = self._update_soc(error_mag)
            
            # 4. Adaptive Control: Tune parameters if enough history
            if len(self.avalanche_history) >= 5:
                self._adapt_control()
            
            # 5. Apply mutation noise based on adaptive rate
            # Higher mutation rate = more variance in score (exploration)
            noise = random.gauss(0, self.mutation_rate)
            final_score = base_score + noise
            
            # Clamp score
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Base:{base_score:.2f}, Stress:{self.stress:.2f}, MutRate:{self.mutation_rate:.2f}"
            if avalanche > 0:
                reasoning += f" [AVALANCHE: {avalanche}]"
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for a single candidate
        # We treat the single answer as the only candidate to get its score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]