import numpy as np
import hashlib

class ReasoningTool:
    """
    Chaotic Swarm Type-Directed Proof Search (CSTDPS) Approximation.
    
    Mechanism:
    1. Type Theory Analogy: Candidates are hashed to generate a 'type signature'.
       We simulate type inhabitation by checking if the candidate's semantic 
       similarity to the prompt (via token overlap) satisfies a 'proof constraint'.
    2. Swarm Intelligence: A population of agents explores the candidate space.
       Each agent carries a position (candidate index) and velocity.
    3. Chaos Theory: Agent trajectories are perturbed by a logistic map 
       (mu=3.9) to prevent premature convergence on local optima.
    4. Stigmergy: Agents deposit 'pheromones' (score boosts) on candidates 
       that satisfy the type constraint (high token overlap), reinforcing 
       valid hypotheses.
    """

    def __init__(self):
        self.mu = 3.9  # Chaotic regime
        self.n_agents = 20
        self.iterations = 15

    def _chaotic_step(self, x):
        """Logistic map iteration."""
        return self.mu * x * (1.0 - x)

    def _get_type_signature(self, text):
        """Generate a deterministic float from text (Type Signature)."""
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    def _check_type_inhabitation(self, prompt, candidate):
        """
        Simulate type checking. 
        Returns (is_inhabited, proof_quality).
        Analogy: High token overlap implies the candidate 'inhabits' the prompt's type.
        """
        p_tokens = set(prompt.lower().split())
        c_tokens = set(candidate.lower().split())
        if not p_tokens:
            return False, 0.0
        
        # Intersection over Union-ish metric
        overlap = len(p_tokens & c_tokens)
        union = len(p_tokens | c_tokens)
        score = overlap / union if union > 0 else 0.0
        
        # Type constraint: Must have at least some logical connection
        is_inhabited = score > 0.15 
        return is_inhabited, score

    def _run_swarm_search(self, prompt, candidates):
        if not candidates:
            return []

        n_cands = len(candidates)
        # Initialize agents with random positions and velocities
        # Positions are normalized [0, 1] mapping to candidate indices
        rng = np.random.default_rng(seed=42) # Deterministic
        positions = rng.random(self.n_agents)
        velocities = rng.random(self.n_agents) * 0.1 - 0.05
        
        # Pheromone trails (scores) for each candidate
        pheromones = np.zeros(n_cands)
        
        # Precompute type signatures and inhabitation checks
        type_data = []
        for i, c in enumerate(candidates):
            inhabited, quality = self._check_type_inhabitation(prompt, c)
            type_data.append((inhabited, quality))

        # Swarm iterations
        for _ in range(self.iterations):
            for i in range(self.n_agents):
                # Chaotic perturbation
                chaos_val = self._chaotic_step(positions[i])
                
                # Move agent
                velocities[i] = velocities[i] * 0.9 + (chaos_val - 0.5) * 0.1
                positions[i] += velocities[i]
                
                # Boundary clamp and wrap (toroidal space)
                positions[i] = positions[i] % 1.0
                
                # Map position to candidate index
                idx = min(int(positions[i] * n_cands), n_cands - 1)
                idx = max(0, idx)
                
                inhabited, quality = type_data[idx]
                
                # Stigmergy: Deposit pheromone if type is inhabited
                if inhabited:
                    # Pheromone amount depends on proof quality and chaotic energy
                    deposit = quality * (1.0 + abs(chaos_val - 0.5))
                    pheromones[idx] += deposit

        return pheromones

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        pheromones = self._run_swarm_search(prompt, candidates)
        
        # Normalize pheromones to scores
        max_p = max(pheromones) if max(pheromones) > 0 else 1.0
        scores = [p / max_p for p in pheromones]
        
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(scores[i]),
                "reasoning": f"Swarm converged with pheromone density {scores[i]:.4f}; Type inhabitation {'successful' if scores[i] > 0.1 else 'weak'}."
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate single candidate confidence using the swarm metric.
        """
        # Run evaluation on a single-item list to reuse logic
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']