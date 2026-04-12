import numpy as np
import math

class ReasoningTool:
    """
    Ergodic Global-Workspace Optimal Controller (EGWOC) Approximation.
    
    Mechanism:
    1. Global Workspace: Candidates compete via softmax gating based on estimated value.
       The 'winning' hypothesis is the one with the highest current estimated utility.
    2. Ergodic Sampling: Instead of infinite time-averaging, we perform a fixed-budget
       deterministic rollout (pseudo-random but seeded) over the 'semantic space' of the
       candidate string. We treat the string's hash-derived vector as a trajectory in
       a latent space, computing an empirical average cost (L) over N steps.
    3. Optimal Control: We solve a simplified Finite-Horizon HJB problem where the
       control signal minimizes the cumulative cost. Here, 'cost' is the distance between
       the candidate's semantic signature and the prompt's requirement signature.
       The 'control' is the selection weight.
       
    This implementation approximates the theoretical architecture using deterministic
    hash-based pseudo-randomness to simulate ergodic rollouts without external models.
    """

    def __init__(self):
        self.ergodic_steps = 100
        np.random.seed(42)  # Determinism

    def _hash_to_vec(self, s: str, dim: int = 10) -> np.ndarray:
        """Deterministic mapping of string to vector space."""
        vec = np.zeros(dim)
        for i, char in enumerate(s):
            idx = ord(char) % dim
            vec[idx] += (ord(char) * (i + 1))
        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-9)

    def _ergodic_rollout(self, prompt_vec: np.ndarray, candidate_vec: np.ndarray) -> float:
        """
        Simulates ergodic sampling by averaging cost over a trajectory.
        Cost L is the Euclidean distance in latent space.
        """
        total_cost = 0.0
        # Deterministic pseudo-trajectory based on combined hash
        combined_seed = int(np.sum(prompt_vec * candidate_vec) * 1000)
        rng = np.random.RandomState(combined_seed)
        
        for t in range(self.ergodic_steps):
            # Perturb state slightly (simulating dynamics)
            noise = rng.normal(0, 0.01, size=prompt_vec.shape)
            state = candidate_vec + noise
            
            # Instantaneous cost: distance to prompt requirement
            cost = np.linalg.norm(state - prompt_vec)
            total_cost += cost
            
        return total_cost / self.ergodic_steps

    def _solve_hjb(self, costs: np.ndarray, temperatures: np.ndarray) -> np.ndarray:
        """
        Solves for optimal control weights using a softmax-gated HJB approximation.
        Minimizes expected cumulative cost.
        """
        # Convert costs to values (negative cost)
        values = -costs
        # Softmax gating (Boltzmann distribution)
        # Scale by temperature to adjust exploration/exploitation
        adjusted_values = values / (temperatures + 1e-9)
        max_val = np.max(adjusted_values)
        exp_vals = np.exp(adjusted_values - max_val)
        return exp_vals / (np.sum(exp_vals) + 1e-9)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        prompt_vec = self._hash_to_vec(prompt)
        costs = []
        candidate_data = []

        # 1. Ergodic Sampling Layer: Estimate cost for each hypothesis
        for cand in candidates:
            cand_vec = self._hash_to_vec(cand)
            # Run ergodic rollout to get empirical average cost
            avg_cost = self._ergodic_rollout(prompt_vec, cand_vec)
            costs.append(avg_cost)
            candidate_data.append({"candidate": cand, "vec": cand_vec})

        costs = np.array(costs)
        
        # 2. Global Workspace & Optimal Control Layer
        # Assume uniform initial temperature, could be adaptive in full system
        temps = np.ones(len(candidates)) * 0.5 
        weights = self._solve_hjb(costs, temps)
        
        # Normalize scores to 0-1 range based on weights (higher weight = lower cost = better)
        # Invert costs for scoring so higher is better
        max_cost = np.max(costs) + 1e-9
        scores = (max_cost - costs) / (max_cost + 1e-9)
        
        # Refine scores with workspace weights
        final_scores = scores * weights
        final_scores = final_scores / np.max(final_scores) # Normalize to max 1.0

        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(final_scores[i]),
                "reasoning": f"Hypothesis '{cand[:20]}...' evaluated via ergodic rollout. "
                             f"Empirical cost: {costs[i]:.4f}. "
                             f"Workspace gating weight: {weights[i]:.4f}."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Score is already normalized 0-1 approx
        return min(1.0, max(0.0, res[0]["score"]))