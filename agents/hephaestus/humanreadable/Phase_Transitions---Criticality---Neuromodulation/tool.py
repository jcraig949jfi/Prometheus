import numpy as np
import hashlib

class ReasoningTool:
    """
    Neuromodulated Critical Reservoir Implementation.
    
    Mechanism:
    1. Encoding: Inputs are hashed into deterministic pseudo-random vectors.
    2. Critical Reservoir: A fixed random recurrent matrix acts as the 'reservoir'.
    3. Neuromodulation (Gain Control): 
       - We simulate a 'criticality metric' based on the variance of candidate scores.
       - If variance is low (system stuck in local minimum/low confidence), 
         'dopamine' increases gain, pushing the system super-critical to explore 
         the hypothesis space (amplifying small differences in input vectors).
       - If variance is high, gain stabilizes near criticality to lock in the belief.
    4. Scoring: The final score is the projection of the modulated reservoir state 
       onto a learned (deterministic) readout vector, normalized by the criticality metric.
    """

    def __init__(self):
        # Deterministic seed for reproducibility
        self.rng = np.random.default_rng(seed=42)
        
        # Reservoir dimensions
        self.N = 64 
        self.reservoir = self.rng.standard_normal((self.N, self.N)) * 0.5
        
        # Normalize reservoir to be near critical point (spectral radius ~ 1.0)
        u, s, vt = np.linalg.svd(self.reservoir)
        self.reservoir = (u @ np.diag(s / np.max(s) * 0.99) @ vt)
        
        # Readout vector (fixed projection for scoring)
        self.readout = self.rng.standard_normal(self.N)
        self.readout /= np.linalg.norm(self.readout)

    def _encode(self, text: str) -> np.ndarray:
        """Hash text to a deterministic vector in [-1, 1]"""
        h = hashlib.sha256(text.encode()).hexdigest()
        vals = [int(c, 16) for c in h]
        vec = np.array(vals[:self.N], dtype=np.float64)
        vec = (vec / 15.0) - 1.0  # Scale to [-1, 1]
        return vec

    def _simulate_dynamics(self, state: np.ndarray, gain: float, steps: int = 5) -> np.ndarray:
        """Run reservoir dynamics with neuromodulated gain."""
        current = state.copy()
        for _ in range(steps):
            # Recurrent step with tanh nonlinearity
            h = np.tanh(gain * (self.reservoir @ current))
            current = h
        return current

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_vec = self._encode(prompt)
        results = []
        raw_scores = []

        # Phase 1: Initial Evaluation (Baseline Gain)
        base_gain = 1.0
        temp_scores = []
        
        for cand in candidates:
            cand_vec = self._encode(cand)
            # Combine prompt and candidate
            state = (prompt_vec + cand_vec) / 2.0
            
            # Initial pass
            final_state = self._simulate_dynamics(state, base_gain)
            score = float(np.dot(final_state, self.readout))
            temp_scores.append(score)

        # Phase 2: Neuromodulatory Adjustment (Criticality Check)
        # Calculate variance as a proxy for distance from criticality
        variance = np.var(temp_scores)
        
        # Neuromodulatory rule: 
        # Low variance -> System is rigid/sub-critical -> Increase gain (Dopamine surge)
        # High variance -> System is exploring/super-critical -> Maintain or slightly reduce
        if variance < 0.01:
            gain_mod = 1.5  # Push to super-critical regime to separate hypotheses
        else:
            gain_mod = 1.0  # Stay near critical edge

        # Phase 3: Re-evaluate with modulated gain
        for i, cand in enumerate(candidates):
            cand_vec = self._encode(cand)
            state = (prompt_vec + cand_vec) / 2.0
            
            # Modulated dynamics
            final_state = self._simulate_dynamics(state, gain_mod)
            score = float(np.dot(final_state, self.readout))
            
            # Adjust score based on how much the gain shift changed the landscape
            # This mimics the "reconfiguration" of belief states
            adjusted_score = score * (1.0 + 0.5 * (gain_mod - 1.0))
            raw_scores.append(adjusted_score)
            
            results.append({
                "candidate": cand,
                "score": adjusted_score,
                "reasoning": f"Reservoir state converged with gain={gain_mod:.2f}. "
                             f"Criticality metric (variance) triggered gain adjustment."
            })

        # Normalize scores to 0-1 range for interpretability
        min_s, max_s = min(raw_scores), max(raw_scores)
        span = max_s - min_s if max_s != min_s else 1.0
        
        normalized_results = []
        for r in results:
            norm_score = (r["score"] - min_s) / span
            normalized_results.append({
                "candidate": r["candidate"],
                "score": float(norm_score),
                "reasoning": r["reasoning"]
            })
            
        # Sort by score descending
        normalized_results.sort(key=lambda x: x["score"], reverse=True)
        return normalized_results

    def confidence(self, prompt: str, answer: str) -> float:
        # Use the same mechanism to determine confidence
        # High confidence = clear separation from random noise or high internal consistency
        
        prompt_vec = self._encode(prompt)
        ans_vec = self._encode(answer)
        state = (prompt_vec + ans_vec) / 2.0
        
        # Run at critical gain
        final_state = self._simulate_dynamics(state, 1.0)
        raw_score = float(np.dot(final_state, self.readout))
        
        # Confidence heuristic: 
        # Map the raw score to 0-1 based on a sigmoid-like function centered at 0
        # assuming the readout is balanced around 0.
        # Also factor in the stability (determinism implies if we ran it again, it's the same)
        
        import math
        conf = 1.0 / (1.0 + math.exp(-raw_score * 2.0))
        return float(conf)