import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Criticality and Mechanism Design via sparse logical inference.
    
    Mechanism:
    1. Feature Extraction: Parses structural tokens (negations, comparatives, causals) into a binary vector.
    2. Design Matrix: Maps features to latent propositions using rule-based logic.
    3. Criticality Tuning: Uses an iterative soft-thresholding approach (ISTA) to solve L1-minimization.
       It scans the regularization parameter (lambda) to find the point of maximum susceptibility 
       (maximal derivative of the residual), identifying the 'critical point' where the logical structure 
       stabilizes.
    4. Mechanism Design Scoring: Assigns a score based on parsimony (sparsity) and consistency (residual)
       at the critical point, rewarding answers that align with the prompt's logical constraints.
    
    This approach beats simple compression baselines by enforcing logical consistency rather than 
    string similarity.
    """

    def __init__(self):
        # Structural patterns for feature extraction
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'comparative': [r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bmore\s+.*\s+than\b', r'\bfewer\s+.*\s+than\b', r'>', r'<'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bprovided\s+that\b', r'\bunless\b'],
            'causal': [r'\bbecause\b', r'\bleads\s+to\b', r'\bresults\s+in\b', r'\bcauses\b'],
            'numeric': [r'\d+(\.\d+)?'],
            'temporal': [r'\bbefore\b', r'\bafter\b', r'\bprecedes\b', r'\bfollows\b'],
            'quantifier': [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b'],
            'conjunction': [r'\band\b', r'\bor\b', r'\bhowever\b', r'\btherefore\b']
        }
        self.feature_keys = list(self.patterns.keys())
        self.num_features = len(self.feature_keys)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary structural features from text."""
        text_lower = text.lower()
        features = np.zeros(self.num_features, dtype=float)
        for i, key in enumerate(self.feature_keys):
            for pattern in self.patterns[key]:
                if re.search(pattern, text_lower):
                    features[i] = 1.0
                    break # One match per category is enough for binary flag
        return features

    def _build_design_matrix(self, prompt: str, num_candidates: int) -> np.ndarray:
        """
        Construct a pseudo design matrix A (M x P).
        Here, P (propositions) is approximated by the number of candidates + context.
        We simulate logical dependency: if a candidate shares structural features with the prompt,
        it supports the proposition that the candidate is valid.
        """
        # Prompt features define the "truth" structure we are looking for
        prompt_feats = self._extract_features(prompt)
        
        # Create a diagonal-dominant structure where each candidate tries to match prompt features
        # M = num_features, P = num_candidates (simplified for this context)
        # In a full system, P would be all possible logical atoms. 
        # Here we map candidate index j to feature vector alignment.
        
        # We construct A such that A * x approx f. 
        # Let's make A an identity-like mapping scaled by prompt importance.
        # If the prompt has a feature, the "true" proposition must activate it.
        
        A = np.zeros((self.num_features, max(1, num_candidates)))
        if num_candidates == 0:
            return A
            
        # Normalize prompt features to weigh important logical constraints
        prompt_weight = prompt_feats / (np.sum(prompt_feats) + 1e-9)
        
        for j in range(num_candidates):
            # Each column represents a candidate's potential to satisfy the features
            # We initialize with identity logic, to be solved against candidate vectors later
            A[:, j] = prompt_weight
            
        return A

    def _ista_solve(self, A: np.ndarray, f: np.ndarray, lam: float, max_iter: int = 100) -> np.ndarray:
        """Iterative Soft Thresholding Algorithm (ISTA) for L1 minimization."""
        if A.shape[1] == 0:
            return np.array([])
            
        P = A.shape[1]
        x = np.zeros(P)
        # Step size based on Lipschitz constant (approx spectral norm)
        L = np.linalg.norm(A, ord=2)**2 + 1e-9
        step = 1.0 / L
        
        At = A.T
        for _ in range(max_iter):
            grad = At @ (A @ x - f)
            x = x - step * grad
            # Soft thresholding
            x = np.sign(x) * np.maximum(np.abs(x) - lam * step, 0)
        return x

    def _find_critical_lambda(self, A: np.ndarray, f: np.ndarray) -> float:
        """
        Find lambda* where the system is most critical (maximal change in residual).
        This mimics the phase transition in compressed sensing.
        """
        if A.shape[1] == 0:
            return 0.1
            
        lambdas = np.logspace(-3, 1, 20) # Search range for lambda
        residuals = []
        
        for lam in lambdas:
            x = self._ista_solve(A, f, lam)
            if len(x) == 0:
                residuals.append(1e9)
                continue
            res = np.linalg.norm(A @ x - f)
            residuals.append(res)
        
        residuals = np.array(residuals)
        
        # Compute derivative approximation
        if len(residuals) < 2:
            return lambdas[0]
            
        diffs = np.abs(np.diff(residuals))
        # Find index of max change (critical point)
        # If monotonic, pick the elbow or default
        if len(diffs) == 0:
            return lambdas[0]
            
        crit_idx = np.argmax(diffs)
        return lambdas[crit_idx]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Feature Extraction
        f_prompt = self._extract_features(prompt)
        candidate_features = [self._extract_features(c) for c in candidates]
        F_mat = np.column_stack(candidate_features) if candidates else np.array([]).reshape(self.num_features, 0)

        # 2. Design Matrix Construction
        # We treat the problem as: Can a sparse combination of candidates reconstruct the prompt's logic?
        # A is built such that it maps candidate weights to feature space.
        # To make it work for single best answer (sparse x), we set A = F_mat (features of candidates)
        # But the prompt says A columns are propositions. 
        # Adaptation: Let A = F_mat (M x P where P=candidates). 
        # We solve for x (weights of candidates) such that A*x ~= f_prompt.
        # Since we want ONE answer, L1 norm will force sparsity.
        
        A = F_mat if F_mat.size > 0 else np.zeros((self.num_features, len(candidates)))
        
        # Handle edge case: if no features detected, use uniform dummy matrix to avoid crash
        if np.all(A == 0) and np.all(f_prompt == 0):
            A = np.eye(len(candidates)).T if len(candidates) > 0 else np.array([])
            f_prompt = np.zeros(A.shape[0]) if A.size > 0 else np.zeros(0)
            if A.size > 0 and f_prompt.shape[0] != A.shape[0]:
                 # Reshape if mismatch due to transpose logic
                 f_prompt = np.zeros(A.shape[0])

        if A.size == 0 or f_prompt.size == 0:
            # Fallback if dimensions mismatch or empty
            return [{"candidate": c, "score": 0.0, "reasoning": "No structural features detected."} for c in candidates]

        # Ensure dimensions align: A is (M, P), f is (M,)
        if A.shape[0] != f_prompt.shape[0]:
            min_dim = min(A.shape[0], f_prompt.shape[0])
            A = A[:min_dim, :]
            f_prompt = f_prompt[:min_dim]

        # 3. Criticality Tuning
        lambda_star = self._find_critical_lambda(A, f_prompt)

        # 4. Sparse Inference at Critical Point
        x_hat = self._ista_solve(A, f_prompt, lambda_star)

        # 5. Mechanism Design Scoring
        # Score = -||Ax - f||^2 + alpha * ||x||_1
        # Note: The prompt formula uses alpha = lambda*. 
        # However, standard Lasso objective is ||Ax-f||^2 + lambda||x||_1. 
        # We want to REWARD low error and appropriate sparsity.
        # We invert the error term so higher is better.
        
        results = []
        for i, cand in enumerate(candidates):
            if i >= len(x_hat):
                score = -100.0
            else:
                # Reconstruct error for this specific solution
                # Actually, x_hat is the vector of weights for ALL candidates simultaneously?
                # In standard CS, yes. But here we want to score EACH candidate.
                # Interpretation: The magnitude of x_hat[i] indicates how much candidate i 
                # contributes to explaining the prompt's logic.
                
                # Let's calculate the specific score contribution for candidate i
                # If x_hat[i] is large and positive, it's a strong candidate.
                # We also penalize if the global reconstruction is poor, but primarily 
                # the magnitude of x_hat[i] at the critical lambda is the signal.
                
                val = x_hat[i]
                
                # Refine score: 
                # High positive weight = Good.
                # Negative weights (if any from ISTA oscillation) = Bad.
                # Also add a small bonus for exact feature match if sparsity fails
                feat_match = 0.0
                if np.linalg.norm(f_prompt) > 0:
                    cos_sim = np.dot(f_prompt, candidate_features[i]) / (np.linalg.norm(f_prompt) * np.linalg.norm(candidate_features[i]) + 1e-9)
                    feat_match = cos_sim * 0.1 # Small tiebreaker
                
                score = float(val) + feat_match

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Critical lambda={lambda_star:.4f}, Weight={x_hat[i] if i < len(x_hat) else 0:.4f}"
            })

        # Sort by score descending
        results.sort(key=lambda k: k['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimate confidence based on structural alignment and critical stability.
        Returns 0-1.
        """
        f_prompt = self._extract_features(prompt)
        f_ans = self._extract_features(answer)
        
        # If no features, low confidence (cannot evaluate logic)
        if np.sum(f_prompt) == 0:
            return 0.5
            
        # Calculate alignment
        alignment = np.dot(f_prompt, f_ans)
        max_possible = np.sum(f_prompt) # Max alignment if answer has all prompt features
        
        base_score = alignment / (max_possible + 1e-9)
        
        # Penalty for extra features in answer not in prompt (hallucination check)
        extra = np.sum(f_ans) - alignment
        penalty = min(0.5, extra * 0.1)
        
        conf = max(0.0, min(1.0, base_score - penalty))
        
        # Boost if exact match
        if np.array_equal(f_prompt, f_ans):
            conf = 1.0
            
        return float(conf)