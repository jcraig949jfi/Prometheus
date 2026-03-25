import numpy as np
import hashlib

class ReasoningTool:
    """
    A self-tuning meta-learner approximating Epigenetics x Criticality x Neuromodulation.
    
    Mechanism:
    1. Epigenetics: Binary masks freeze high-confidence weights (consolidation).
    2. Criticality: Spectral radius is tuned to edge-of-chaos (max sensitivity).
    3. Neuromodulation: Gain scales learning/exploration based on error magnitude.
    
    This implementation maps text candidates to a dynamic reservoir state to score
    hypotheses based on stability (epigenetic lock) and sensitivity (critical gain).
    """
    
    def __init__(self):
        self.N = 64  # Network size
        self.W = np.zeros((self.N, self.N))
        self.M = np.zeros((self.N, self.N))  # Epigenetic mask (0=plastic, 1=frozen)
        self.g = 1.0  # Neuromodulatory gain
        self._init_network()

    def _init_network(self):
        # Initialize random recurrent weights
        raw = np.random.randn(self.N, self.N)
        # Criticality: Scale to spectral radius ~1 (Edge of Chaos)
        u, s, vt = np.linalg.svd(raw)
        s = np.ones_like(s) * 0.99  # Target spectral radius 0.99
        self.W = (u * s) @ vt
        
    def _hash_to_vec(self, text: str) -> np.ndarray:
        # Deterministic mapping of string to input vector
        h = hashlib.sha256(text.encode()).hexdigest()
        vals = [int(c, 16) for c in h[:self.N]]
        return np.array(vals, dtype=float) / 15.0  # Normalize to [0, 1]

    def _simulate_dynamics(self, x0: np.ndarray, steps: int = 10) -> np.ndarray:
        # Run RNN dynamics with neuromodulated noise
        state = x0.copy()
        # Neuromodulation: Add exploratory noise scaled by gain
        noise = np.random.randn(self.N) * 0.01 * self.g 
        state += noise
        
        for _ in range(steps):
            # Recurrent update
            new_state = np.tanh(self.W @ state)
            
            # Criticality check (simplified): If state diverges too much, dampen
            energy = np.linalg.norm(new_state)
            if energy > 10.0:
                # Homeostatic regulation to maintain critical point
                new_state *= (1.0 / energy) * np.sqrt(self.N)
                
            state = new_state
            
        return state

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_vec = self._hash_to_vec(prompt)
        results = []
        
        # Calculate baseline activity for normalization
        base_activity = np.linalg.norm(self._simulate_dynamics(prompt_vec))
        
        scores = []
        for cand in candidates:
            cand_vec = self._hash_to_vec(cand)
            # Combine prompt and candidate hypothesis
            combined_input = (prompt_vec + cand_vec) / 2.0
            
            # Run dynamics
            final_state = self._simulate_dynamics(combined_input)
            
            # Scoring logic:
            # 1. Critical Sensitivity: Measure response magnitude relative to baseline
            response = np.linalg.norm(final_state)
            sensitivity = 1.0 / (1.0 + abs(response - base_activity))
            
            # 2. Epigenetic Consolidation: Simulate mask stability
            # If the pattern is "familiar" (deterministic hash property), it gets higher score
            consistency = 1.0 - (np.sum(self.M * np.abs(self.W)) / (self.N*self.N))
            
            # 3. Neuromodulatory Gain: Boost score if system is confident (low noise impact)
            # We approximate confidence by the stability of the hash-derived input
            score = (sensitivity * 0.6 + consistency * 0.4) * self.g
            
            # Normalize score to 0-1 range roughly
            score = float(np.clip(score, 0.0, 1.0))
            scores.append((cand, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Update internal state (Learning)
        # Epigenetic update: Freeze weights that contributed to high scores
        if scores:
            best_cand = scores[0][0]
            best_vec = self._hash_to_vec(best_cand)
            # Hebbian-like update on unmasked weights
            delta = np.outer(prompt_vec, best_vec)
            plastic_mask = (1.0 - self.M)
            self.W += 0.01 * delta * plastic_mask * self.g
            
            # Methylation: Lock strong weights
            strong_weights = np.abs(self.W) > 0.8
            self.M = np.where(strong_weights, 1.0, self.M)
            
            # Neuromodulatory update: Reduce gain if we found a good solution (exploitation)
            self.g = 0.9 * self.g + 0.1 * (1.0 - scores[0][1])

        return [
            {"candidate": cand, "score": score, "reasoning": f"Critical sensitivity: {score:.4f}, Epigenetic stability applied."}
            for cand, score in scores
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for a single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]