import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Predictive-Error-Minimizing Belief Network with Lyapunov Stability Scoring.
    
    Mechanism:
    1. Parses text into propositional nodes and directed edges (Network Science).
    2. Simulates belief propagation via gradient descent on Variational Free Energy (FEP).
    3. Estimates dynamical stability via numerical Lyapunov exponents (Chaos Theory).
    4. Scores candidates based on low prediction error (low F) and high stability (negative lambda).
    """
    
    def __init__(self):
        self.alpha = 0.1
        self.steps = 20
        self.beta = -0.5  # Penalty for instability

    def _parse_text(self, text: str) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """Extract nodes, feature vectors, and adjacency matrix."""
        text = text.lower()
        # Simple regex extraction of logical units
        sentences = re.split(r'[.\n]', text)
        nodes = []
        features = []
        
        # Extract propositions
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            # Normalize
            sent = re.sub(r'\s+', ' ', sent)
            nodes.append(sent)
            # Feature vector: [has_negation, has_conditional, has_comparative, length_norm]
            f_neg = 1.0 if re.search(r'\b(not|no|never|unless)\b', sent) else 0.0
            f_cond = 1.0 if re.search(r'\b(if|then|leads to|because)\b', sent) else 0.0
            f_comp = 1.0 if re.search(r'\b(greater|less|more|twice|>|<)\b', sent) else 0.0
            f_len = min(len(sent) / 100.0, 1.0)
            features.append([f_neg, f_cond, f_comp, f_len])
            
        if not nodes:
            return [], np.array([]), np.array([])

        n = len(nodes)
        F = np.array(features)
        W = np.zeros((n, n))
        
        # Build adjacency based on logical flow and similarity
        for i in range(n):
            for j in range(i+1, n):
                # Conditional logic: if i contains 'if' and j is subsequent, link i->j
                if re.search(r'\b(if|because)\b', nodes[i]) and j == i + 1:
                    W[i, j] = 1.0
                # Transitivity/Similarity link
                overlap = len(set(nodes[i].split()) & set(nodes[j].split()))
                if overlap > 0:
                    weight = min(overlap / 5.0, 1.0)
                    W[i, j] = weight
                    W[j, i] = weight * 0.5 # Asymmetric influence
                    
        # Self-loops for stability
        np.fill_diagonal(W, 0.2)
        return nodes, F, W

    def _run_dynamics(self, W: np.ndarray, init_b: np.ndarray) -> Tuple[float, float]:
        """Run Free Energy minimization and estimate Lyapunov exponent."""
        if W.size == 0:
            return 0.0, 0.0
            
        n = W.shape[0]
        b = init_b.copy()
        pi = np.ones(n) # Precision
        eps = 1e-6
        
        lyap_sum = 0.0
        T_count = 0
        
        for t in range(self.steps):
            # Prediction
            b_hat = 1.0 / (1.0 + np.exp(-W.T @ b))
            
            # Free Energy Components
            diff = b - b_hat
            F = 0.5 * np.sum(pi * diff**2) - np.sum(b * np.log(b + eps) + (1-b) * np.log(1-b + eps))
            
            # Gradient of F w.r.t b
            # dF/db = pi * (b - b_hat) - (log(b) - log(1-b)) + derivative of b_hat term approx
            # Simplified gradient descent step for demonstration
            grad = pi * diff - (np.log(b + eps) - np.log(1 - b + eps))
            b_new = b - self.alpha * grad
            b_new = np.clip(b_new, 0.01, 0.99)
            
            # Numerical Jacobian for Lyapunov (finite difference)
            J_norm = 0.0
            for i in range(n):
                b_pert = b.copy()
                b_pert[i] += 1e-4
                b_hat_p = 1.0 / (1.0 + np.exp(-W.T @ b_pert))
                diff_p = b_pert - b_hat_p
                grad_p = pi * diff_p - (np.log(b_pert + eps) - np.log(1 - b_pert + eps))
                # Approx derivative of update step
                J_norm += np.linalg.norm(grad - grad_p) / 1e-4
            
            if J_norm > 0:
                lyap_sum += np.log(J_norm + 1e-6)
                T_count += 1
                
            b = b_new
            
        lambda_max = (lyap_sum / T_count) if T_count > 0 else 0.0
        return -F, lambda_max # Return negative F because we want to maximize score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        # Parse prompt structure to establish baseline logic
        p_nodes, p_feat, p_W = self._parse_text(prompt)
        
        if len(p_nodes) == 0:
            # Fallback if parsing fails
            return [{"candidate": c, "score": 0.0, "reasoning": "Parsing failed"} for c in candidates]

        for cand in candidates:
            # Combine prompt and candidate for context
            full_text = f"{prompt} {cand}"
            c_nodes, c_feat, c_W = self._parse_text(full_text)
            
            if len(c_nodes) == 0:
                score = -100.0
                reason = "No logical structure detected."
            else:
                # Initialize belief state from features
                init_b = np.mean(c_feat, axis=0) if c_feat.size > 0 else np.random.rand(len(c_nodes))
                if init_b.ndim == 0: init_b = np.array([0.5])
                init_b = np.tile(init_b, len(c_nodes))[:len(c_nodes)] # Match node count
                init_b = np.clip(init_b, 0.1, 0.9)
                
                # Run dynamics
                neg_F, lambda_max = self._run_dynamics(c_W, init_b)
                
                # Scoring: High stability (negative lambda) and Low Free Energy (high neg_F)
                # Normalize slightly to prevent explosion
                score = neg_F + self.beta * max(0, lambda_max)
                
                reason = f"Stability: {lambda_max:.4f}, Prediction Error: {-neg_F:.4f}"
            
            results.append({"candidate": cand, "score": float(score), "reasoning": reason})
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on relative score ranking."""
        # Generate a few dummy alternatives to create a comparison distribution
        dummies = [f"{answer} (variant {i})" for i in range(3)]
        # In a real scenario, we might perturb the answer. Here we just check against itself and noise.
        # To save compute and ensure determinism, we evaluate the single pair's internal consistency.
        
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]["score"]
        
        # Map raw score to 0-1 using a sigmoid-like mapping centered around typical values
        # Heuristic: Scores often range -10 to 10 in this simple model
        conf = 1.0 / (1.0 + np.exp(-0.5 * raw_score))
        return float(np.clip(conf, 0.01, 0.99))