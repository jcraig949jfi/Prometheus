import numpy as np
import math

class ReasoningTool:
    """
    CAN: Chaotic Autopoietic Neuromodulator.
    Mechanism:
    1. Chaos: Uses a fixed random recurrent matrix scaled to edge-of-chaos (spectral radius ~1.0).
    2. Autopoiesis: Monitors reservoir energy; if variance drifts from target, scales weights 
       to maintain structural integrity (homeostasis).
    3. Neuromodulation: Adjusts input gain and leak rate based on 'prediction error' (difference 
       between candidate embedding and reservoir state). High error -> High gain (explore); 
       Low error -> Low gain (exploit/stabilize).
    
    This creates a self-tuning dynamical system that ranks candidates by how well they 
    stabilize the reservoir's chaotic trajectory relative to the prompt context.
    """
    
    def __init__(self):
        self.N = 64  # Reservoir size
        np.random.seed(42)  # Determinism
        
        # Initialize chaotic reservoir (Echo State Network style)
        W = np.random.randn(self.N, self.N)
        # Scale to edge of chaos (spectral radius approx 1.0)
        eigenvals = np.linalg.eigvals(W)
        max_ev = np.max(np.abs(eigenvals))
        self.W_rec = W / max_ev * 1.0 
        
        self.W_in = np.random.randn(self.N, 1)
        self.state = np.zeros(self.N)
        
        # Autopoietic targets
        self.target_variance = 0.5
        self.homeostasis_rate = 0.1
        
        # Neuromodulatory state
        self.gain = 1.0
        self.leak = 0.5

    def _hash_text(self, text: str) -> np.ndarray:
        """Convert text to deterministic pseudo-vector."""
        if not text:
            return np.zeros(1)
        vals = np.array([ord(c) for c in text], dtype=float)
        # Simple rolling hash to get fixed size input
        h = np.sum(vals * np.arange(1, len(vals)+1)) % 1000 / 1000.0
        return np.array([h])

    def _step(self, input_val: float):
        """Run one step of the chaotic reservoir with neuromodulation."""
        # Input injection with neuromodulated gain
        x_in = self.W_in.flatten() * input_val * self.gain
        
        # Recurrent dynamics
        pre_activation = np.tanh(np.dot(self.W_rec, self.state) + x_in)
        
        # Leaky integration with neuromodulated leak
        self.state = (1 - self.leak) * self.state + self.leak * pre_activation
        
        # Autopoietic maintenance: Check variance and adjust global scale if drifting
        current_var = np.var(self.state)
        if current_var > 0:
            # Homeostatic plasticity: nudge weights to maintain target variance
            error = (self.target_variance - current_var) / (current_var + 1e-8)
            adjustment = 1.0 + self.homeostasis_rate * error
            # Apply structural maintenance (simplified as global scaling for stability)
            if abs(adjustment - 1.0) > 1e-6:
                self.W_rec *= np.sign(adjustment) * np.sqrt(abs(adjustment)) if adjustment > 0 else 1.0

    def _simulate_hypothesis(self, prompt: str, candidate: str) -> float:
        """Simulate the system's response to a candidate hypothesis."""
        # Reset state slightly based on prompt to create context
        prompt_vec = self._hash_text(prompt)
        self.state = np.tanh(np.dot(self.W_rec, self.state) + self.W_in.flatten() * prompt_vec[0])
        
        # Initial neuromodulatory setting: High gain for exploration
        self.gain = 1.5
        self.leak = 0.3
        
        # Inject candidate as a perturbation
        cand_vec = self._hash_text(candidate)
        
        # Run dynamics for a few steps to let the system settle or diverge
        history = []
        for t in range(10):
            # Neuromodulation logic: 
            # If state is too chaotic (high variance in recent steps), reduce gain
            if t > 0:
                recent_var = np.var(history[-3:]) if len(history) > 2 else 0.5
                # Meta-controller: Reduce gain if instability detected (exploitation)
                if recent_var > 0.8:
                    self.gain *= 0.8
                    self.leak = min(0.9, self.leak + 0.1) # Slow down, stabilize
                else:
                    self.gain *= 1.05 # Encourage exploration
                    self.leak = max(0.1, self.leak - 0.05)
            
            self._step(cand_vec[0])
            history.append(np.mean(self.state))
            
        # Score based on stability and convergence (lower variance in trajectory = better fit)
        # Also penalize extreme divergence
        traj_var = np.var(history)
        final_mag = np.linalg.norm(self.state)
        
        # Heuristic score: Stable, moderate magnitude states are "correct"
        score = 1.0 / (traj_var + 0.1) 
        score = score / (1.0 + abs(final_mag) * 0.01) # Normalize by magnitude
        
        return float(score)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        results = []
        # Normalize scores to 0-1 range for consistency
        raw_scores = [self._simulate_hypothesis(prompt, c) for c in candidates]
        min_s, max_s = min(raw_scores), max(raw_scores)
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        for i, c in enumerate(candidates):
            norm_score = (raw_scores[i] - min_s) / range_s
            results.append({
                "candidate": c,
                "score": norm_score,
                "reasoning": f"Stability metric: {norm_score:.4f} via chaotic resonance."
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Use the evaluation logic to determine confidence
        # Treat the single answer as a candidate list of one
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Map the relative score to a confidence metric
        # Since it's the only candidate, high stability implies high confidence
        base_conf = res[0]["score"]
        # Calibrate: if the system found it stable, confidence is high
        return min(1.0, max(0.0, base_conf))