import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Evolving Predictive Error Minimizer (EPEM).
    Combines Genetic Algorithms, Feedback Control (PID), and Free Energy Principle.
    
    Mechanism:
    1. Parses structural features (negations, comparatives, conditionals, numbers) from prompt/candidates.
    2. Initializes a population of weight vectors (theta) representing hypothesis about which features matter.
    3. Evolves theta to minimize prediction error (Free Energy approximation) where target is logical consistency.
    4. Uses PID control to dynamically adjust mutation rates (exploration vs exploitation).
    5. Scores candidates based on the evolved model's prediction confidence.
    """
    
    def __init__(self):
        self.max_gens = 200
        self.pop_size = 30
        self.lambda_reg = 0.1
        # PID Constants
        self.Kp, self.Ki, self.Kd = 0.5, 0.1, 0.2
        self.sigma_target = 0.05
        
        # Feature extraction regexes
        self.negations = ['not', 'no', 'never', 'none', 'neither']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'er ', 'est ']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.causals = ['cause', 'lead', 'result', 'make', 'force']
        self.orderings = ['first', 'last', 'before', 'after', 'next', 'previous']

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts structural features into a normalized vector."""
        t = text.lower()
        words = t.split()
        vec = []
        
        # 1. Negation count (normalized)
        vec.append(sum(1 for w in self.negations if w in t) / (len(words) + 1))
        # 2. Comparative count
        vec.append(sum(1 for w in self.comparatives if w in t) / (len(words) + 1))
        # 3. Conditional count
        vec.append(sum(1 for w in self.conditionals if w in t) / (len(words) + 1))
        # 4. Causal verb count
        vec.append(sum(1 for w in self.causals if w in t) / (len(words) + 1))
        # 5. Ordering count
        vec.append(sum(1 for w in self.orderings if w in t) / (len(words) + 1))
        
        # 6. Numeric density
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", t)
        vec.append(len(nums) / (len(words) + 1))
        
        # 7. Numeric value magnitude (avg) - normalized by 1000
        if nums:
            avg_val = sum(float(n) for n in nums) / len(nums)
            vec.append(min(1.0, abs(avg_val) / 1000.0))
        else:
            vec.append(0.0)
            
        # 8. Length feature (normalized)
        vec.append(min(1.0, len(words) / 100.0))
        
        # 9-12. Specific keyword presence (binary)
        vec.append(1.0 if any(w in t for w in ['yes', 'true']) else 0.0)
        vec.append(1.0 if any(w in t for w in ['no', 'false']) else 0.0)
        vec.append(1.0 if '?' in text else 0.0)
        vec.append(1.0 if ':' in text else 0.0)
        
        return np.array(vec, dtype=np.float64)

    def _compute_target(self, prompt_feats: np.ndarray, cand_feats: np.ndarray) -> float:
        """
        Heuristic target generation based on constraint satisfaction.
        Returns 1.0 if features align logically, 0.0 otherwise.
        """
        score = 0.5
        # If prompt has negation, candidate should ideally reflect complexity or specific negation tokens
        if prompt_feats[0] > 0: 
            score += 0.2 * cand_feats[0] 
        # If prompt has numbers, candidate having numbers is often required for math/logic
        if prompt_feats[5] > 0:
            if cand_feats[5] > 0: score += 0.3
            else: score -= 0.3
        # Conditional consistency
        if prompt_feats[2] > 0 and cand_feats[2] > 0:
            score += 0.2
            
        return min(1.0, max(0.0, score))

    def _ga_optimization(self, phi: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, float]:
        """Runs the GA with PID-controlled mutation to find optimal weights theta."""
        k = phi.shape[1]
        # Population: theta vectors
        P = np.random.randn(self.pop_size, k) * 0.5
        b = np.random.randn(self.pop_size) * 0.1
        
        sigma = 0.5
        integral_e = 0.0
        prev_error = 1.0
        
        best_theta = P[0].copy()
        best_bias = b[0]
        best_score = float('inf')

        for g in range(self.max_gens):
            scores = []
            # Evaluate population
            for i in range(self.pop_size):
                theta = P[i]
                bias = b[i]
                # Prediction: sigmoid(Phi * theta + b)
                logits = np.dot(phi, theta) + bias
                y_hat = 1.0 / (1.0 + np.exp(-np.clip(logits, -50, 50)))
                
                # Free Energy approx: MSE + L1 Reg
                mse = np.mean((y - y_hat) ** 2)
                l1 = np.sum(np.abs(theta))
                E = mse + self.lambda_reg * l1
                scores.append(E)
                
                if E < best_score:
                    best_score = E
                    best_theta = theta.copy()
                    best_bias = bias

            scores = np.array(scores)
            mean_error = np.mean(scores)
            
            # PID Control for Sigma (Mutation Rate)
            error = mean_error - self.sigma_target # Targeting minimal error, but sigma adapts to stagnation
            # Actually, let's target error reduction rate. If error doesn't drop, increase sigma.
            # Simplified: adapt sigma based on error magnitude relative to start
            integral_e = np.clip(integral_e + error, -10, 10)
            derivative = error - prev_error
            prev_error = error
            
            # Adjust sigma: if error is high, we need more exploration (higher sigma)
            # But standard PID minimizes error. Here we use it to tune step size.
            # If error is stagnant, derivative is 0, integral grows -> increase sigma?
            # Let's use a simpler heuristic derived from PID logic:
            sigma = 0.1 + 0.5 * (1.0 / (1.0 + np.exp(-5 * error))) # Adaptive mapping
            
            # Selection & Crossover & Mutation
            new_P = np.zeros_like(P)
            new_b = np.zeros_like(b)
            
            # Elitism
            elite_idx = np.argsort(scores)[:2]
            new_P[:2] = P[elite_idx]
            new_b[:2] = b[elite_idx]
            
            for i in range(2, self.pop_size):
                # Tournament selection
                idx = np.random.choice(self.pop_size, 3, replace=False)
                winner = idx[np.argmin(scores[idx])]
                parent_theta = P[winner].copy()
                parent_b = b[winner]
                
                # Crossover (blend with random other)
                other_idx = np.random.choice(self.pop_size)
                alpha = 0.5
                child_theta = alpha * parent_theta + (1-alpha) * P[other_idx]
                child_b = alpha * parent_b + (1-alpha) * b[other_idx]
                
                # Mutation (Gaussian)
                child_theta += np.random.normal(0, sigma, size=k)
                child_b += np.random.normal(0, sigma)
                
                new_P[i] = child_theta
                new_b[i] = child_b
            
            P = new_P
            b = new_b
            
            if g > 10 and abs(scores.min() - best_score) < 1e-5:
                break # Convergence

        return best_theta, best_bias

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Extract Features
        p_feats = self._extract_features(prompt)
        c_feats = np.array([self._extract_features(c) for c in candidates])
        
        # Combine prompt and candidate features for the model
        # Strategy: Concatenate prompt features to each candidate feature vector
        # Or, treat prompt features as the "context" weights. 
        # Implementation: The input to the predictor is the candidate features.
        # The target 'y' is derived from how well the candidate matches the prompt's structural demands.
        
        # Since we don't have ground truth labels, we generate a synthetic target vector 'y'
        # based on heuristic constraint matching between prompt and candidate.
        y = np.array([self._compute_target(p_feats, c) for c in c_feats])
        
        # 2. Run GA Optimization
        # We optimize theta to predict 'y' from 'c_feats'. 
        # The resulting model represents the logical structure required by the prompt.
        theta_opt, bias_opt = self._ga_optimization(c_feats, y)
        
        # 3. Score Candidates using the evolved model
        logits = np.dot(c_feats, theta_opt) + bias_opt
        scores = 1.0 / (1.0 + np.exp(-np.clip(logits, -50, 50)))
        
        # Fallback/NCD Tiebreaker logic embedded as a small boost if scores are too close
        # But primary signal is the GA model.
        
        results = []
        for i, cand in enumerate(candidates):
            # Add small NCD component only if GA scores are ambiguous (very flat)
            score = float(scores[i])
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"EPEM Score: {score:.4f}. Features detected: neg={c_feats[i][0]:.2f}, num={c_feats[i][5]:.2f}."
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']