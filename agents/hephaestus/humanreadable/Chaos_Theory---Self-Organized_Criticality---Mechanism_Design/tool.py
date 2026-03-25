import numpy as np
import hashlib

class ReasoningTool:
    """
    Chaos-SOC-Mechanism Design Inference Engine.
    
    Mechanism:
    1. Encoding: Candidates are hashed to initial belief states (x0) in [0,1].
    2. Chaos: Beliefs evolve via Logistic Map (r=3.99) to simulate sensitive 
       dependence on initial conditions, preventing premature convergence.
    3. SOC (Sandpile): Agents form a directed ring. If a belief change (delta) 
       exceeds a threshold, the agent 'topples', propagating stress to neighbors.
       This creates avalanches of re-evaluation.
    4. Mechanism Design (BTS Approx): Scores are adjusted by a 'surprise' metric.
       Candidates that survive large avalanches (high stress) yet maintain coherence
       receive a truthfulness bonus, simulating Bayesian Truth Serum incentives.
    """

    def __init__(self):
        self.r = 3.99  # Chaotic parameter
        self.threshold = 0.15 # Sandpile toppling threshold
        self.n_agents = 20   # Population size per candidate
        self.steps = 50      # Simulation steps

    def _hash_to_float(self, s: str) -> float:
        """Deterministic mapping of string to [0.05, 0.95]."""
        h = hashlib.sha256(s.encode()).hexdigest()
        val = int(h[:8], 16) / (16**8)
        return 0.05 + 0.90 * val

    def _logistic_map(self, x: float) -> float:
        return self.r * x * (1.0 - x)

    def _simulate_dynamics(self, prompt: str, candidate: str) -> dict:
        seed_str = f"{prompt}:{candidate}"
        base_seed = self._hash_to_float(seed_str)
        
        # Initialize population beliefs
        beliefs = np.array([base_seed + np.random.uniform(-0.01, 0.01) 
                            for _ in range(self.n_agents)])
        beliefs = np.clip(beliefs, 0.01, 0.99)
        
        total_stress = 0.0
        avalanche_size = 0
        current_avalanche = 0
        
        # Interaction topology: Directed Ring (i -> i+1)
        for t in range(self.steps):
            new_beliefs = np.copy(beliefs)
            deltas = np.zeros_like(beliefs)
            active_topple = False
            
            # 1. Chaotic Update & Delta Calculation
            for i in range(self.n_agents):
                old_val = beliefs[i]
                new_val = self._logistic_map(old_val)
                new_beliefs[i] = new_val
                deltas[i] = abs(new_val - old_val)
            
            # 2. SOC Toppling Logic
            # If any agent exceeds threshold, it topples and affects neighbor
            for i in range(self.n_agents):
                if deltas[i] > self.threshold:
                    current_avalanche += 1
                    active_topple = True
                    # Perturb neighbor (directed ring: i affects (i+1)%N)
                    neighbor = (i + 1) % self.n_agents
                    # Inject chaotic noise based on the magnitude of the toppling
                    perturbation = (deltas[i] - self.threshold) * (np.random.rand() - 0.5)
                    new_beliefs[neighbor] = np.clip(new_beliefs[neighbor] + perturbation, 0.01, 0.99)
            
            if active_topple:
                avalanche_size += 1
            
            total_stress += np.sum(deltas)
            beliefs = new_beliefs

        # 3. Scoring (Mechanism Design Layer)
        # Final score is mean belief, penalized by instability (variance) 
        # but rewarded if it survived large avalanches (BTS proxy for 'truthful' robustness)
        final_score = float(np.mean(beliefs))
        variance = float(np.var(beliefs))
        
        # BTS Proxy: High stress (avalanche_size) with low final variance implies 
        # a robust consensus despite chaos -> High Truthfulness Bonus
        bonus = 0.0
        if avalanche_size > 5:
            bonus = 0.2 * (avalanche_size / self.steps) * (1.0 / (variance + 0.01))
            
        raw_score = final_score * (1.0 + bonus) - (variance * 0.5)
        return {
            "score": max(0.0, min(1.0, raw_score)),
            "avalanche": avalanche_size,
            "stress": total_stress
        }

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            sim = self._simulate_dynamics(prompt, cand)
            results.append({
                "candidate": cand,
                "score": sim["score"],
                "reasoning": f"Chaos-SOC dynamics yielded score {sim['score']:.4f} after {sim['avalanche']} avalanche events with total stress {sim['stress']:.4f}."
            })
        # Rank by score descending
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        res = self._simulate_dynamics(prompt, answer)
        return float(max(0.0, min(1.0, res["score"])))