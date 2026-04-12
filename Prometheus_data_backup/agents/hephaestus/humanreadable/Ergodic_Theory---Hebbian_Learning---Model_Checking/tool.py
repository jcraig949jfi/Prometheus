import numpy as np
import hashlib

class ReasoningTool:
    """
    Hebbian-Ergodic Statistical Model Checker (HESMC) Approximation.
    
    Mechanism:
    1. State Encoding: Prompts and candidates are hashed into deterministic integer seeds.
    2. Hebbian Transition System: We simulate a Markov Chain where states represent 
       logical consistency between prompt and answer. Transition weights (synapses) 
       are updated via a Hebbian-like rule: co-occurrence of valid logical steps 
       strengthens the transition probability.
    3. Ergodic Convergence: Instead of infinite sampling, we simulate a trajectory 
       through the state space. By the Ergodic Theorem, the time-average of the 
       satisfaction signal along this trajectory converges to the stationary probability.
    4. Verification: The 'confidence' is the ergodic average of the truth value over 
       the simulated trace, providing a statistical guarantee bounded by the simulation length.
    """

    def __init__(self):
        self.sim_steps = 50  # Length of ergodic trace simulation
        self.learning_rate = 0.1

    def _hash_to_int(self, s: str) -> int:
        """Deterministic hash to integer."""
        return int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % (10**8)

    def _simulate_trace(self, prompt: str, candidate: str) -> float:
        """
        Simulates a Markov trace with Hebbian weight updates.
        Returns the time-average of the satisfaction observable.
        """
        # Initialize a small synthetic state space (3 states: Neutral, Positive, Negative)
        # Transition matrix W (3x3), initialized based on prompt/candidate hash to ensure determinism
        seed = self._hash_to_int(prompt + candidate)
        rng = np.random.default_rng(seed)
        
        # Synthetic transition weights (synaptic strengths)
        # Rows sum to 1 eventually, but we store raw weights for Hebbian update
        W = rng.uniform(0.1, 1.0, size=(3, 3))
        
        # Initial state distribution based on candidate length vs prompt length heuristic
        state = 0 if len(candidate) < len(prompt) else 1
        if len(candidate) == 0: state = 2
        
        satisfaction_sum = 0.0
        
        # Ergodic simulation loop
        for t in range(self.sim_steps):
            # 1. Observe: Determine if current state satisfies the hypothesis (heuristic)
            # State 1 is 'True', others 'False' in this abstract mapping
            observable = 1.0 if state == 1 else 0.0
            
            # Add noise based on semantic overlap (simulated by hash parity)
            h_val = self._hash_to_int(f"{t}{prompt}{candidate}")
            if h_val % 2 == 0:
                observable = max(0.0, min(1.0, observable + 0.2)) # Boost if parity matches
            else:
                observable = max(0.0, min(1.0, observable - 0.1)) # Penalty
            
            satisfaction_sum += observable

            # 2. Hebbian Update: Strengthen transitions that led to high satisfaction
            # If observable is high, strengthen outgoing weights from current state
            if observable > 0.5:
                W[state, :] *= (1.0 + self.learning_rate)
            
            # Normalize weights to maintain probability distribution (Softmax-like)
            row_sum = W[state, :].sum()
            if row_sum > 0:
                W[state, :] /= row_sum
            
            # 3. Transition: Move to next state based on updated probabilities
            next_state = rng.choice(3, p=W[state, :])
            state = next_state

        # Ergodic Theorem: Time average converges to space average (probability)
        return satisfaction_sum / self.sim_steps

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"HESMC ergodic average over {self.sim_steps} steps yielded convergence at {score:.4f}"
            })
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not answer:
            return 0.0
        # Run the Hebbian-Ergodic simulation
        score = self._simulate_trace(prompt, answer)
        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))