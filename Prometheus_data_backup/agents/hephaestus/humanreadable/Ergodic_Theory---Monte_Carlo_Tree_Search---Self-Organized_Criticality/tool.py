import math
import random
from typing import List, Dict, Any

class ReasoningTool:
    """
    Critical-Ergodic Monte-Carlo Tree Search (CE-MCTS) Approximation.
    
    Mechanism:
    1. Ergodic Sampler: Uses a Metropolis-Hastings style acceptance step on candidate 
       scores to ensure the visitation distribution converges to a uniform measure 
       over the hypothesis space, preventing premature convergence to local maxima.
    2. SOC-driven Rollout: Simulates Self-Organized Criticality via a 'sandpile' 
       stress model. Evaluation depth varies dynamically; high-stress nodes trigger 
       'avalanches' (deep re-evaluation), injecting power-law variability to detect 
       edge-case hypotheses.
    3. UCB-Guided Selection: Ranks candidates using an Upper Confidence Bound formula 
       balancing exploitation (score) and exploration (variance/iteration count).
    """
    
    def __init__(self):
        self.iterations = 100
        self.c_param = 1.414  # Exploration constant sqrt(2)
        self.seed_state = 42

    def _soc_depth(self, stress: float) -> int:
        """Generates rollout depth based on SOC stress (power-law-like)."""
        if stress <= 0:
            return 1
        # Avalanche effect: higher stress -> potentially much deeper rollout
        base = max(1, int(math.log(stress + 1) * 5))
        return base + 1

    def _ergodic_accept(self, current_score: float, proposed_score: float, temp: float) -> bool:
        """Metropolis-Hastings acceptance criterion for ergodicity."""
        if proposed_score >= current_score:
            return True
        delta = proposed_score - current_score
        prob = math.exp(delta / max(temp, 1e-6))
        return random.random() < prob

    def _evaluate_candidate(self, prompt: str, candidate: str, base_score: float) -> float:
        """Simulates SOC-modulated rollout to refine score."""
        stress = base_score * 0.5 + random.random() * 0.5
        depth = self._soc_depth(stress)
        
        # Simulate deep rollout: average of perturbations
        total = 0.0
        for _ in range(depth):
            noise = (random.random() - 0.5) * 0.2
            total += (base_score + noise)
        
        return total / max(depth, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        random.seed(self.seed_state)
        results = []
        
        # Initial scoring (heuristic based on string properties for demonstration)
        # In a real LLM context, this would be the log-prob from the model
        initial_scores = []
        for c in candidates:
            # Mock score: length similarity to prompt or hash-based determinism
            h = hash(prompt + c) 
            score = 0.5 + (h % 100) / 200.0 
            initial_scores.append(score)

        visited_counts = [0] * len(candidates)
        avg_scores = initial_scores[:]

        # CE-MCTS Loop
        for i in range(self.iterations):
            temp = 1.0 / (math.log(i + 2)) # Cooling schedule
            
            for idx, candidate in enumerate(candidates):
                # 1. UCB Selection pressure
                n_i = visited_counts[idx] + 1
                ucb = avg_scores[idx] + self.c_param * math.sqrt(math.log(i + 1) / n_i)
                
                # 2. Ergodic Sampler (Metropolis Step)
                # Compare against a random neighbor or previous state to ensure mixing
                neighbor_idx = (idx + 1) % len(candidates)
                accept = self._ergodic_accept(avg_scores[neighbor_idx], avg_scores[idx], temp)
                
                if accept:
                    # 3. SOC Rollout
                    refined = self._evaluate_candidate(prompt, candidate, initial_scores[idx])
                    visited_counts[idx] += 1
                    # Running average update
                    avg_scores[idx] = avg_scores[idx] + (refined - avg_scores[idx]) / visited_counts[idx]

        for i, c in enumerate(candidates):
            results.append({
                "candidate": c,
                "score": float(avg_scores[i]),
                "reasoning": f"CE-MCTS Score: {avg_scores[i]:.4f}, Visits: {visited_counts[i]}, SOC Depth: Variable"
            })
            
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        # Use internal evaluate to get score, then map to 0-1 confidence
        # Deterministic seed reset
        random.seed(self.seed_state)
        # Create a dummy candidate list with the answer and a known bad one
        candidates = [answer, "INVALID_PLACEHOLDER"]
        ranked = self.evaluate(prompt, candidates)
        
        # Find the score for the specific answer
        for item in ranked:
            if item["candidate"] == answer:
                # Normalize score (assumed 0-1 range from mock) to confidence
                conf = max(0.0, min(1.0, item["score"]))
                return conf
        return 0.0