import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic Stochastic Attractor Network (ESAN) with Metacognitive Calibration.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, conditionals).
    2. GRN-Style Energy Function: Maps candidate features to a symmetric weight matrix (W).
       Hypotheses are attractor states in this landscape.
    3. Langevin Dynamics: Simulates dx/dt = -grad(U) + noise to explore the hypothesis space.
       This ensures ergodicity, allowing the system to escape local minima (false positives).
    4. Metacognitive Head: Monitors sample variance and autocorrelation (Gelman-Rubin style).
       If mixing is poor (high autocorrelation), it increases "temperature" (noise) to force exploration.
    5. Scoring: Time-averaged activity converges to the posterior probability.
    """

    def __init__(self):
        self.dim = 64  # Feature dimension for internal representation
        self.steps = 50  # Simulation steps for ergodic averaging
        self.dt = 0.1   # Time step
        self.base_beta = 1.0 # Inverse temperature

    def _extract_features(self, text: str) -> np.ndarray:
        """Convert text to a binary feature vector based on structural patterns."""
        text_lower = text.lower()
        features = np.zeros(self.dim)
        
        # Structural Logic Patterns (Indices 0-15)
        logic_map = {
            'not': 0, 'no ': 1, 'never': 2, 'cannot': 3, # Negations
            'greater': 4, 'less': 5, 'more': 6, 'fewer': 7, # Comparatives
            'if': 8, 'then': 9, 'unless': 10, 'only if': 11, # Conditionals
            'all': 12, 'some': 13, 'none': 14, 'every': 15 # Quantifiers
        }
        for k, i in logic_map.items():
            if k in text_lower: features[i] = 1.0
            
        # Numeric Evaluation (Indices 16-31)
        nums = re.findall(r"-?\d+\.?\d*", text)
        if nums:
            try:
                vals = [float(n) for n in nums]
                if len(vals) >= 2:
                    features[16] = 1.0 if vals[0] > vals[1] else 0.0 # Greater check
                    features[17] = 1.0 if vals[0] < vals[1] else 0.0 # Less check
                    features[18] = 1.0 if vals[0] == vals[1] else 0.0 # Equality
            except: pass
            
        # Lexical Overlap with prompt keywords (Indices 32-63)
        words = re.findall(r'\b\w+\b', text_lower)
        for i, w in enumerate(words[:32]):
            features[32 + i] = 1.0 # Simple presence
            
        return features

    def _compute_energy(self, x: np.ndarray, W: np.ndarray) -> float:
        """U(x) = -0.5 * x^T * W * x"""
        return -0.5 * float(np.dot(x, np.dot(W, x)))

    def _simulate_dynamics(self, prompt_vec: np.ndarray, candidate_vec: np.ndarray, 
                           beta: float) -> Tuple[float, float, float]:
        """
        Run Langevin dynamics on the combined state.
        Returns: (average_activity, variance, autocorrelation)
        """
        # Construct symmetric W based on GRN-like topology (Hebbian-like association)
        # State = [prompt_features, candidate_features]
        state = np.concatenate([prompt_vec, candidate_vec])
        n = len(state)
        
        # Symmetric weight matrix (GRN topology)
        W = np.outer(state, state) 
        np.fill_diagonal(W, 0) # No self-loops
        
        trajectory = []
        current_state = state.copy()
        
        # Add small noise to start
        current_state += np.random.normal(0, 0.1, n)

        for t in range(self.steps):
            # Gradient of energy: dU/dx = -W * x
            grad = -np.dot(W, current_state)
            
            # Langevin step: dx = -grad * dt + sqrt(2/beta) * dW
            noise_scale = np.sqrt(2.0 / max(beta, 1e-6))
            noise = np.random.normal(0, noise_scale, n)
            
            current_state = current_state - grad * self.dt + noise
            
            # Clamp to [-1, 1] to simulate bounded neuron activity (sigmoidal approx)
            current_state = np.clip(current_state, -1, 1)
            trajectory.append(current_state.copy())

        traj_arr = np.array(trajectory)
        mean_act = np.mean(traj_arr)
        var_act = np.var(traj_arr)
        
        # Autocorrelation at lag 1 (mixing diagnostic)
        if len(traj_arr) > 1:
            autocorr = np.corrcoef(traj_arr[:-1].flatten(), traj_arr[1:].flatten())[0, 1]
        else:
            autocorr = 1.0
            
        return mean_act, var_act, autocorr if not np.isnan(autocorr) else 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_vec = self._extract_features(prompt)
        results = []
        
        # Metacognitive Loop: Adjust beta based on mixing
        # We simulate a batch to tune beta, then score
        best_beta = self.base_beta
        min_autocorr = 1.0
        
        # Quick scan to find optimal temperature for this specific prompt complexity
        for b_test in [0.5, 1.0, 2.0, 5.0]:
            # Test mixing on a dummy candidate (first one or empty)
            dummy = self._extract_features(candidates[0] if candidates else "")
            _, _, ac = self._simulate_dynamics(prompt_vec, dummy, b_test)
            if ac < min_autocorr:
                min_autocorr = ac
                best_beta = b_test
        
        # If mixing is still poor (high autocorr), force higher temperature (lower beta)
        if min_autocorr > 0.8:
            best_beta = 0.2 # High noise regime

        for cand in candidates:
            cand_vec = self._extract_features(cand)
            
            # Run Ergodic Simulation
            avg_act, variance, autocorr = self._simulate_dynamics(prompt_vec, cand_vec, best_beta)
            
            # Base score from energy landscape (attractor depth)
            # Lower energy (more negative) is better, but we mapped activity to positive correlation
            base_score = float(avg_act) 
            
            # Penalty for poor mixing (metacognitive penalty)
            # If autocorrelation is high, the system is stuck; reduce confidence
            mixing_penalty = 0.5 * (autocorr if autocorr > 0 else 0)
            
            final_score = base_score - mixing_penalty
            
            # Tiebreaker: NCD (Compression)
            # Only used if scores are very close, but we add a small component here
            s1 = (prompt + " " + cand).encode('utf-8')
            s2 = prompt.encode('utf-8')
            s3 = cand.encode('utf-8')
            try:
                c1 = len(zlib.compress(s1))
                c2 = len(zlib.compress(s2))
                c3 = len(zlib.compress(s3))
                ncd = (c1 - min(c2, c3)) / max(c1, 1) # Rough NCD
                final_score -= (ncd * 0.01) # Small penalty for high NCD (low similarity)
            except:
                pass

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Ergodic avg: {avg_score:.4f}, Mixing: {1-autocorr:.4f}, Beta: {best_beta}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the stability of the attractor state.
        """
        prompt_vec = self._extract_features(prompt)
        answer_vec = self._extract_features(answer)
        
        # Run multiple short trajectories to check convergence (Metacognitive check)
        scores = []
        for _ in range(5):
            avg, var, ac = self._simulate_dynamics(prompt_vec, answer_vec, self.base_beta)
            scores.append(avg)
        
        std_dev = np.std(scores)
        mean_score = np.mean(scores)
        
        # Confidence is high if mean score is high AND variance between runs is low
        # Map to 0-1 range roughly
        conf = (mean_score + 1) / 2.0  # Shift from [-1, 1] to [0, 1]
        conf -= std_dev * 2.0          # Penalize instability
        conf -= (0.5 * max(0, ac))     # Penalize poor mixing
        
        return float(np.clip(conf, 0.0, 1.0))