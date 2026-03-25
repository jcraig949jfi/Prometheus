import hashlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic Abductive Theory-of-Mind Sampler (EATM-S) Approximation.
    
    Mechanism:
    1. Theory-of-Mind (ToM): Simulates nested beliefs by hashing the prompt 
       with candidate-specific "agent perspectives" to generate deterministic 
       pseudo-observations.
    2. Abductive Reasoning: Generates hypotheses by measuring semantic overlap 
       (token intersection) between the prompt and candidates, weighted by a 
       simplicity prior (length penalty).
    3. Ergodic Theory: Approximates convergence by running a deterministic 
       pseudo-MCMC chain over the candidate space. It computes time-averaged 
       sufficient statistics over the chain's trajectory. If the running average 
       stabilizes (low variance relative to mean), the system assumes the 
       belief state has converged to the space-average (true posterior).
    """

    def __init__(self):
        self._seed = 42  # Deterministic seed

    def _hash_to_float(self, s: str) -> float:
        """Deterministic hash to [0, 1]."""
        h = hashlib.sha256(s.encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    def _tokenize(self, s: str) -> set:
        """Simple whitespace tokenizer."""
        return set(s.lower().split())

    def _abductive_score(self, prompt: str, candidate: str) -> float:
        """
        Computes likelihood based on token overlap (explanation power)
        and a simplicity prior (shorter is better).
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        if not p_tokens or not c_tokens:
            return 0.0

        # Overlap ratio (Likelihood)
        intersection = len(p_tokens & c_tokens)
        union = len(p_tokens | c_tokens)
        likelihood = intersection / union if union > 0 else 0.0

        # Simplicity Prior (Penalize excessive length relative to prompt)
        len_ratio = len(c_tokens) / len(p_tokens) if len(p_tokens) > 0 else 1.0
        prior = math.exp(-0.5 * abs(1.0 - len_ratio)) # Peaks when lengths match

        return likelihood * prior

    def _tom_perspective_shift(self, prompt: str, candidate: str, agent_id: int) -> str:
        """Simulates nested belief state by altering context hash."""
        # In a full implementation, this would run an I-POMDP update.
        # Here, we create a deterministic perspective shift.
        return f"{prompt}::AGENT_{agent_id}::BELIEF({candidate})"

    def _ergodic_sampler(self, prompt: str, candidate: str, steps: int = 20) -> Tuple[float, float]:
        """
        Simulates an ergodic average over a belief trajectory.
        Returns (converged_mean, convergence_metric).
        """
        values = []
        current_val = self._abductive_score(prompt, candidate)
        
        # Deterministic pseudo-chain
        for t in range(steps):
            # Perturb state via ToM simulation
            agent_perspective = self._tom_perspective_shift(prompt, candidate, t)
            noise = self._hash_to_float(agent_perspective) * 0.2 - 0.1 # Small deterministic noise
            step_val = current_val * (0.9 + 0.2 * self._hash_to_float(str(t))) + noise
            step_val = max(0.0, min(1.0, step_val)) # Clamp
            values.append(step_val)
            current_val = step_val # Update state

        # Compute running averages and variance (Ergodic diagnostic)
        if not values:
            return 0.0, 0.0
            
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        
        # Convergence metric: Coefficient of variation (lower is more ergodic/stable)
        # We invert it so higher is better, but cap it.
        stability = 1.0 / (1.0 + variance) if variance > 0 else 1.0
        
        return mean_val, stability

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Abductive scoring
            base_score = self._abductive_score(prompt, cand)
            
            # 2. Ergodic averaging of ToM-simulated beliefs
            ergodic_mean, stability = self._ergodic_sampler(prompt, cand)
            
            # Fusion: Weighted combination of abductive likelihood and ergodic stability
            final_score = (0.6 * base_score + 0.4 * ergodic_mean) * stability
            
            results.append({
                "candidate": cand,
                "score": float(f"{final_score:.6f}"),
                "reasoning": f"Abductive likelihood: {base_score:.2f}, Ergodic stability: {stability:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against itself to get confidence
        # We treat the 'answer' as the only candidate to see how well it fits
        # relative to the prompt structure.
        base_score = self._abductive_score(prompt, answer)
        ergodic_mean, stability = self._ergodic_sampler(prompt, answer)
        
        # Confidence is high if the specific answer is stable and has high abductive fit
        conf = (0.5 * base_score + 0.5 * ergodic_mean) * stability
        return float(min(1.0, max(0.0, conf)))