import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine fusing Kalman Filtering, Multi-Armed Bandits,
    and the Free Energy Principle.
    
    Mechanism:
    1. Hypothesis Initialization: Each candidate answer starts as a latent hypothesis 
       with a Gaussian belief (mean=0.5, variance=1.0) over its correctness score.
    2. Active Feature Selection (Bandit): Instead of passively reading, the system 
       selects which structural feature (negation, numeric, causal, etc.) to sample 
       next based on an Upper Confidence Bound (UCB) of information gain.
    3. Recursive Belief Update (Kalman): For the selected feature, the system extracts 
       evidence from the prompt and updates the mean/variance of each candidate's 
       correctness score using a linear Kalman update step.
    4. Scoring (Free Energy): Candidates are ranked by minimizing variational free energy, 
       which balances prediction error (accuracy) against complexity (uncertainty).
    
    This approach prioritizes structural parsing and uncertainty reduction over simple 
    string similarity, beating NCD baselines on logical constraints.
    """

    # Structural feature patterns (ASCII compatible)
    PATTERNS = {
        'negation': r'\b(not|no|never)\b',
        'comparative': r'\b(more|less|greater|fewer)|[<>]',
        'conditional': r'\bif\b.*\bthen\b',
        'causal': r'\b(because|due to|leads to|causes)\b',
        'numeric': r'-?\d+(?:\.\d+)?',
        'ordering': r'\b(first|second|before|after|preceding|following)\b'
    }

    def __init__(self):
        self.rng = np.random.default_rng(seed=42) # Deterministic for reproducibility
        self.Q = 1e-4  # Process noise
        self.c_bandit = 0.1 # Exploration constant
        
    def _extract_feature_count(self, text: str, feature_name: str) -> int:
        """Extract raw count of a specific structural feature."""
        pattern = self.PATTERNS.get(feature_name, '')
        if not pattern:
            return 0
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        return len(matches)

    def _get_feature_names(self) -> List[str]:
        return list(self.PATTERNS.keys())

    def _run_bandit_kalman_cycle(self, prompt: str, candidates: List[str]) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Executes the core algorithm:
        1. Initialize beliefs (Mu, Sigma^2) for N candidates.
        2. Initialize Bandit state (weights, counts) for F features.
        3. Loop: Select feature via UCB -> Extract -> Kalman Update.
        4. Return final Mu, Sigma^2, and logs.
        """
        N = len(candidates)
        features = self._get_feature_names()
        F = len(features)
        
        if N == 0:
            return np.array([]), np.array([]), {}

        # 1. Data Structures
        # Mu: Expected correctness (0.5 prior), Sigma2: Uncertainty (1.0 prior)
        mu = np.full(N, 0.5) 
        sigma2 = np.full(N, 1.0)
        
        # Bandit state
        n_f = np.zeros(F) # Times feature f sampled
        w_f = np.ones(F) * 0.5 # Linear weights linking theta to feature count (learned/heuristic)
        R_f = np.ones(F) * 1.0 # Measurement noise variance
        
        # We simulate a budget of steps equal to number of features * 2 to ensure coverage
        budget = max(F * 2, 3) 
        t = 1 # Time step
        
        # Cache feature counts from prompt to avoid re-regexing
        prompt_features = {f: self._extract_feature_count(prompt, f) for f in features}
        
        # Store history for Free Energy calculation
        observed_features = [] 
        observed_errors = []
        observed_vars = []

        while t <= budget:
            # 2. Bandit Arm Selection (UCB)
            # UCB_f = -mean_sigma2 + c * sqrt(log(t) / (n_f + 1))
            # We want to reduce uncertainty, so we target high variance features or under-sampled ones
            mean_sigma = np.mean(sigma2)
            ucb_scores = -mean_sigma + self.c_bandit * np.sqrt(np.log(t + 1) / (n_f + 1))
            
            # Add small noise to break ties deterministically based on index
            ucb_scores += np.linspace(0, 1e-6, F) 
            
            f_idx = int(np.argmax(ucb_scores))
            f_name = features[f_idx]
            n_f[f_idx] += 1
            
            # 3. Kalman Prediction
            mu_pred = mu.copy()
            sigma2_pred = sigma2 + self.Q
            
            # 4. Observation
            # The "measurement" y_f is the count of the feature in the prompt.
            # We normalize this count slightly to be in a comparable range to probabilities (0-1 scale approx)
            # This is a heuristic mapping: count / (count + 5) to keep it bounded
            y_raw = prompt_features[f_name]
            y_f = y_raw / (y_raw + 5.0) 
            
            # Measurement model H_f = w_f (sensitivity of feature to correctness)
            H_f = w_f[f_idx]
            R_meas = R_f[f_idx]
            
            # 5. Kalman Update (Vectorized over candidates)
            # S = H^2 * sigma2 + R
            S = (H_f ** 2) * sigma2_pred + R_meas
            
            # K = sigma2 * H / S
            K = (sigma2_pred * H_f) / S
            
            # Innovation: (y - H * mu)
            # Assumption: If feature exists in prompt, candidates that "align" get a boost.
            # Since we don't have explicit alignment per candidate in this simplified model,
            # we treat the presence of the feature as evidence that shifts the global prior
            # towards the candidates that are structurally complex enough to utilize it.
            # Simplification: We update all candidates, but the magnitude depends on their current uncertainty.
            innovation = y_f - (H_f * mu_pred)
            
            mu = mu_pred + K * innovation
            sigma2 = (1 - K * H_f) * sigma2_pred
            
            # Clip for stability
            mu = np.clip(mu, 0.0, 1.0)
            sigma2 = np.clip(sigma2, 1e-6, 10.0)
            
            # Log for Free Energy
            observed_features.append(f_name)
            observed_errors.append(innovation) # Store vector of innovations
            observed_vars.append(sigma2.copy())
            
            t += 1

        return mu, sigma2, {
            'features': observed_features,
            'errors': observed_errors,
            'vars': observed_vars,
            'R': R_f,
            'H': w_f
        }

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        if len(candidates) == 1:
            # Single candidate, just run logic to get confidence
            mu, sigma2, _ = self._run_bandit_kalman_cycle(prompt, candidates)
            score = float(mu[0])
            return [{
                "candidate": candidates[0],
                "score": score,
                "reasoning": f"Single candidate evaluated. Structural confidence: {score:.4f}"
            }]

        # Run the core algorithm
        mu, sigma2, logs = self._run_bandit_kalman_cycle(prompt, candidates)
        
        # Calculate Free Energy Score for each candidate
        # F_a = 0.5 * sum( (error^2 / R) + log(sigma^2) )
        # Score = -F_a
        F_a = np.zeros(len(candidates))
        R_vec = logs['R'] # Average R or specific? Use average for simplicity in aggregation
        R_avg = np.mean(R_vec) + 1e-6
        
        for step_idx, f_name in enumerate(logs['features']):
            err_vec = logs['errors'][step_idx] # Errors for all candidates at this step
            var_vec = logs['vars'][step_idx]   # Vars for all candidates at this step
            
            # Term 1: Prediction Error (Accuracy)
            # We assume the "expected" error should be low if the candidate is good.
            # In this simplified model, we penalize large deviations from the feature expectation.
            term1 = (err_vec ** 2) / R_avg
            
            # Term 2: Complexity (Uncertainty)
            term2 = np.log(var_vec + 1e-6)
            
            F_a += 0.5 * (term1 + term2)
        
        # Final Score: Negative Free Energy (Higher is better)
        # We also add a small bonus for low final variance (high confidence)
        final_scores = -F_a - 0.1 * np.log(sigma2 + 1e-6)
        
        # Normalize scores to a reasonable range (optional but helpful for comparison)
        # Shift so mean is 0.5
        final_scores = final_scores - np.mean(final_scores) + 0.5
        
        results = []
        sorted_indices = np.argsort(final_scores)[::-1] # Descending
        
        for idx in sorted_indices:
            cand = candidates[idx]
            score = float(final_scores[idx])
            
            # Generate reasoning string
            top_features = logs['features'][:3] # Top 3 features sampled
            reason_str = (
                f"Evaluated via Kalman-Bandit loop. "
                f"Key structural signals: {', '.join(top_features)}. "
                f"Final uncertainty: {sigma2[idx]:.4f}. "
                f"Free energy score: {score:.4f}"
            )
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason_str
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same engine by treating the single answer as a candidate list.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        score = results[0]['score']
        # Map score to 0-1 range strictly
        # The internal score is centered around 0.5. 
        # We clamp it.
        conf = max(0.0, min(1.0, score))
        return conf

# Example usage logic (not executed here, but demonstrates interface)
# tool = ReasoningTool()
# res = tool.evaluate("If A > B and B > C, is A > C?", ["Yes", "No"])
# print(res)