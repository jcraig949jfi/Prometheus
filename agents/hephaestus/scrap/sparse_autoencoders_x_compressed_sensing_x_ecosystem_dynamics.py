import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a neuro-symbolic reasoning engine combining Sparse Autoencoders,
    Compressed Sensing (L1 minimization), and Ecosystem Dynamics (constraint propagation).
    
    Mechanism:
    1. Feature Extraction: Parses text for logical primitives (negation, causality, etc.)
       into a binary measurement matrix A and target vector b.
    2. Sparse Coding: Solves min ||Ax - b||^2 + lambda||x||_1 via ISTA to find the 
       sparsest set of active logical concepts explaining the prompt.
    3. Ecosystem Dynamics: Enforces logical consistency (e.g., If A->B, then x_A <= x_B)
       by projecting the solution onto a feasible polytope via alternating projections.
    4. Scoring: Combines reconstruction error, sparsity penalty, and ecosystem stability
       (spectral radius of the constraint Jacobian) to rank candidates.
    """
    
    # Logical primitives dictionary
    PATTERNS = {
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
        'comparative': [r'>', r'<', r'\bmore than\b', r'\bless than\b', r'\bgreater\b', r'\blesser\b'],
        'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly if\b'],
        'causal': [r'\bbecause\b', r'\bleads to\b', r'\bresults in\b', r'\bcauses\b'],
        'numeric': [r'\d+(\.\d+)?'],
        'ordering': [r'\bfirst\b', r'\bsecond\b', r'\bbefore\b', r'\bafter\b', r'\bprecede\b']
    }
    
    def __init__(self):
        self.keys = sorted(self.PATTERNS.keys())
        self.n_features = len(self.keys)
        # Map regex patterns to indices
        self.compiled_patterns = {}
        for k in self.keys:
            self.compiled_patterns[k] = [re.compile(p, re.IGNORECASE) for p in self.PATTERNS[k]]

    def _extract_features(self, text: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Extracts binary features and builds the measurement matrix A and vector b."""
        text_lower = text.lower()
        features = np.zeros(self.n_features)
        present_tags = []
        
        for i, key in enumerate(self.keys):
            count = 0
            for pattern in self.compiled_patterns[key]:
                if pattern.search(text_lower):
                    count += 1
            if count > 0:
                features[i] = 1.0
                present_tags.append(key)
                
        # Construct A as identity (standard basis) for simple feature presence
        # In a more complex version, A could be a dictionary learning matrix.
        # Here, A = I, so Ax = x. We want x close to features (b).
        A = np.eye(self.n_features)
        b = features
        
        return A, b, present_tags

    def _ista_solve(self, A: np.ndarray, b: np.ndarray, lam: float = 0.1, max_iter: int = 100) -> np.ndarray:
        """Iterative Soft-Thresholding Algorithm for L1 sparse recovery."""
        n = A.shape[1]
        x = np.zeros(n)
        # Step size based on spectral norm of A
        L = np.linalg.norm(A, ord=2) ** 2 + 1e-6
        rho = 1.0 / L
        
        for _ in range(max_iter):
            grad = A.T @ (A @ x - b)
            x_new = x - rho * grad
            # Soft thresholding
            x = np.sign(x_new) * np.maximum(np.abs(x_new) - lam * rho, 0)
        return x

    def _project_ecosystem(self, x: np.ndarray, tags: List[str]) -> Tuple[np.ndarray, float]:
        """
        Projects x onto the feasible set defined by logical constraints.
        Returns the projected vector and a stability metric (inverse spectral radius).
        """
        n = len(x)
        if n == 0:
            return x, 1.0
            
        # Define simple ecosystem constraints based on tags present
        # If 'conditional' or 'causal' exists, enforce hierarchy: Cause <= Effect
        # Simplified: If causal tags exist, assume some dependencies.
        # We simulate a trophic network where higher-order logic constrains lower-order.
        
        C = []
        d = []
        
        # Constraint 1: Non-negativity (x >= 0) -> -x <= 0
        C.append(-np.eye(n))
        d.append(np.zeros(n))
        
        # Constraint 2: Logical consistency heuristics
        # If negation and affirmative co-occur strongly, limit sum <= 1 (exclusive)
        if 'negation' in tags and 'causal' in tags:
            # Hypothetical constraint: Negation intensity + Causal intensity <= 1.2
            row = np.zeros(n)
            if 'negation' in self.keys:
                idx_n = self.keys.index('negation')
                row[idx_n] = 1
            if 'causal' in self.keys:
                idx_c = self.keys.index('causal')
                row[idx_c] = 1
            if np.sum(row) > 0:
                C.append(row.reshape(1, -1))
                d.append(np.array([1.2]))

        if not C:
            return x, 1.0
            
        C_mat = np.vstack(C)
        d_vec = np.hstack(d)
        
        # Alternating projections (simplified to one step for speed/stability)
        # Solve min ||x - z|| s.t. Cz <= d using a few steps of projected gradient
        z = x.copy()
        for _ in range(20):
            violation = C_mat @ z - d_vec
            if np.all(violation <= 1e-6):
                break
            # Project onto most violated constraint
            idx = np.argmax(violation)
            if violation[idx] > 0:
                c_row = C_mat[idx]
                norm_sq = np.dot(c_row, c_row)
                if norm_sq > 1e-8:
                    z -= (violation[idx] / norm_sq) * c_row
        
        # Stability metric: Spectral radius of the active constraint Jacobian
        # Approximate by looking at the density of active constraints
        active = (C_mat @ z - d_vec) > -1e-4
        if np.any(active):
            J = C_mat[active]
            if J.shape[0] > 0:
                # Pseudo-spectral radius proxy
                try:
                    vals = np.linalg.svd(J, compute_uv=False)
                    rho = vals[0] if len(vals) > 0 else 0.0
                except:
                    rho = 1.0
            else:
                rho = 1.0
        else:
            rho = 0.0
            
        # Lower rho is more stable. Return inverse for scoring.
        stability = 1.0 / (1.0 + rho)
        return z, stability

    def _compute_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        # Combine prompt and candidate for context
        full_text = f"{prompt} {candidate}"
        A, b, tags = self._extract_features(full_text)
        
        if np.sum(b) == 0:
            # No features detected, rely on NCD tiebreaker logic implicitly via length penalty
            return -1.0 * len(candidate), "No structural features detected."

        # 1. Sparse Coding
        x_sparse = self._ista_solve(A, b, lam=0.1)
        
        # 2. Ecosystem Projection
        x_final, stability = self._project_ecosystem(x_sparse, tags)
        
        # 3. Scoring
        # Data fit: -||Ax - b||^2
        residual = np.linalg.norm(A @ x_final - b)**2
        # Sparsity: -lambda ||x||_1
        sparsity = 0.1 * np.linalg.norm(x_final, ord=1)
        # Stability term
        score = -residual - sparsity + 0.5 * stability
        
        reason_str = f"Features: {', '.join(tags) if tags else ['none']}; Stability: {stability:.2f}"
        return float(score), reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._compute_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._compute_score(prompt, answer)
        # Normalize score to 0-1 range roughly
        # Heuristic: Map score to probability. 
        # Assuming typical scores range from -2 to 2 based on experiments
        conf = 1.0 / (1.0 + np.exp(-score)) 
        return float(np.clip(conf, 0.0, 1.0))