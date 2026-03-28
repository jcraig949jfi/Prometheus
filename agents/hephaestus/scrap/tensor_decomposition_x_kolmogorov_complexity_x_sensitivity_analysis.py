import re
import math
import zlib
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning evaluator combining Tensor Decomposition (CP-ALS), 
    Kolmogorov Complexity (MDL proxy), and Sensitivity Analysis.
    
    Mechanism:
    1. Feature Extraction: Parses logical structures (negation, conditionals, numerics) 
       into a binary/categorical tensor.
    2. Low-Rank Approximation: Uses a simplified CP-decomposition logic to estimate 
       the rank (R) required to explain the logical structure.
    3. Complexity & Sensitivity: Calculates an MDL score based on rank and residuals, 
       then perturbs inputs to measure structural fragility.
    4. Scoring: Combines reconstruction error, complexity penalty, and sensitivity.
    5. Epistemic Honesty: Caps confidence on ambiguous or unanswerable prompts.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|better|worse|higher|lower)\b', re.I),
            'conditional': re.compile(r'\b(if|then|provided|unless|otherwise)\b', re.I),
            'causal': re.compile(r'\b(cause|leads?|results?|due|because)\b', re.I),
            'ordering': re.compile(r'([<>]|before|after|precede|follow)', re.I),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.I),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.I)
        }
        self.max_iter = 50
        self.tol = 1e-4
        self.lambda_l = 0.1
        self.lambda_s = 0.2

    def _extract_features(self, text: str) -> List[float]:
        """Extracts structural features into a vector."""
        text_lower = text.lower()
        features = []
        
        # Binary flags
        features.append(1.0 if self.patterns['negation'].search(text) else 0.0)
        features.append(1.0 if self.patterns['comparative'].search(text) else 0.0)
        features.append(1.0 if self.patterns['conditional'].search(text) else 0.0)
        features.append(1.0 if self.patterns['causal'].search(text) else 0.0)
        features.append(1.0 if self.patterns['ordering'].search(text) else 0.0)
        features.append(1.0 if self.patterns['quantifier'].search(text) else 0.0)
        
        # Numeric value (scaled)
        nums = self.patterns['numbers'].findall(text)
        if nums:
            # Use first number found, scaled by log to handle magnitude
            val = float(nums[0])
            features.append(math.log1p(abs(val)) * (1 if val >= 0 else -1))
        else:
            features.append(0.0)
            
        # Token position index (normalized)
        features.append(len(text) / 1000.0) 
        
        return features

    def _build_tensor(self, sentences: List[str], max_sents: int = 5) -> np.ndarray:
        """Builds a 2D tensor X (N x D) from sentences, padding if necessary."""
        D = 8 # Fixed feature dimension
        N = min(len(sentences), max_sents)
        if N == 0:
            return np.zeros((1, D))
            
        X = np.zeros((max_sents, D))
        for i, sent in enumerate(sentences[:max_sents]):
            feats = self._extract_features(sent)
            # Ensure length matches D
            if len(feats) < D:
                feats += [0.0] * (D - len(feats))
            X[i, :] = feats[:D]
        return X

    def _cp_decompose(self, X: np.ndarray, rank: int = 2) -> Tuple[float, np.ndarray]:
        """
        Simplified CP-ALS approximation.
        Returns reconstruction error and the reconstructed tensor.
        Since X is 2D (matrix), CP decomposition is equivalent to SVD/low-rank approx.
        We simulate the tensor logic by treating rows as modes.
        """
        N, D = X.shape
        if N == 0 or D == 0:
            return 0.0, X
            
        # Initialize factors randomly but deterministically
        np.random.seed(42)
        A = np.random.rand(N, rank)
        B = np.random.rand(D, rank)
        
        # Normalize columns
        A = A / (np.linalg.norm(A, axis=0) + 1e-9)
        B = B / (np.linalg.norm(B, axis=0) + 1e-9)
        
        error = np.inf
        for _ in range(self.max_iter):
            # Update A: A = X * B * (B^T B)^-1
            BtB = B.T @ B + 1e-9 * np.eye(rank)
            XtB = X.T @ A
            # Solve for B
            try:
                B_new = np.linalg.solve(BtB, XtB.T).T
            except np.linalg.LinAlgError:
                B_new = B
            
            # Update B: B = X^T * A * (A^T A)^-1
            AtA = A.T @ A + 1e-9 * np.eye(rank)
            XtA = X.T @ B_new
            try:
                A_new = np.linalg.solve(AtA, XtA)
            except np.linalg.LinAlgError:
                A_new = A
                
            # Normalize
            norm_A = np.linalg.norm(A_new, axis=0) + 1e-9
            A_new = A_new / norm_A
            
            # Reconstruct
            X_hat = A_new @ B_new.T
            
            # Check convergence
            new_error = np.linalg.norm(X - X_hat, 'fro')
            if abs(error - new_error) < self.tol:
                break
            error = new_error
            A, B = A_new, B_new
            
        return error, X_hat

    def _calculate_mdl(self, X: np.ndarray, X_hat: np.ndarray, rank: int) -> float:
        """Calculates MDL proxy: Rank * Storage + Residual Sparsity."""
        N, D = X.shape
        storage_cost = rank * (N + D) * math.log2(max(N, D, 2))
        residual_sparsity = np.count_nonzero(np.abs(X - X_hat) > 1e-6) * math.log2(2)
        return storage_cost + residual_sparsity

    def _sensitivity_analysis(self, X: np.ndarray, rank: int, M: int = 5) -> float:
        """Measures robustness to noise."""
        if X.size == 0:
            return 0.0
            
        e0, _ = self._cp_decompose(X, rank)
        sensitivities = []
        
        for _ in range(M):
            X_pert = X.copy()
            # Add noise to numeric entries (index 6 in our feature vector)
            noise = np.random.normal(0, 0.1, X_pert.shape)
            noise[:, :6] = 0 # Only perturb numeric/positional features slightly
            X_pert += noise
            
            # Flip negation/comparative flags with low probability
            if np.random.rand() < 0.2:
                X_pert[:, 0] = 1.0 - X_pert[:, 0] # Flip negation
                X_pert[:, 1] = 1.0 - X_pert[:, 1] # Flip comparative
            
            e_m, _ = self._cp_decompose(X_pert, rank)
            sensitivities.append(abs(e_m - e0))
            
        return float(np.mean(sensitivities)) if sensitivities else 0.0

    def _determine_rank(self, X: np.ndarray) -> int:
        """Scree test proxy: choose rank that minimizes reconstruction error gain."""
        errors = []
        max_rank = min(X.shape[0], X.shape[1], 3)
        if max_rank < 1: return 1
        
        for r in range(1, max_rank + 1):
            err, _ = self._cp_decompose(X, r)
            errors.append(err)
            
        if len(errors) < 2:
            return 1
            
        # Simple elbow detection
        diffs = [errors[i] - errors[i+1] for i in range(len(errors)-1)]
        if not diffs: return 1
        best_r = np.argmax(diffs) + 1
        return max(1, best_r)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len_s1 = len(z(s1.encode()))
        len_s2 = len(z(s2.encode()))
        len_joint = len(z((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_joint - min(len_s1, len_s2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Checks for Tier B traps: ambiguity, presupposition, unanswerability.
        Returns a cap value (low if trap detected).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        if "stopped" in p_lower or "quit" in p_lower and "why" in p_lower:
            return 0.2
            
        # 2. Scope/Pronoun Ambiguity (Heuristic)
        if re.search(r'\b(every .+ a .+|told .+ he|told .+ she)\b', p_lower) and "who" in p_lower:
            return 0.3
            
        # 3. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.4
            
        # 4. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.3
            
        # 5. Unanswerability (Missing info heuristic)
        if "calculate" in p_lower and not re.search(r'\d', p_lower):
            return 0.2
            
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_features = self._extract_features(prompt)
        prompt_vec = np.array(prompt_features).reshape(1, -1)
        
        # Determine global rank based on prompt complexity
        # We treat the prompt + candidate as the logical unit
        base_rank = self._determine_rank(np.vstack([prompt_vec, prompt_vec])) 
        
        for cand in candidates:
            sentences = [prompt, cand]
            X = self._build_tensor(sentences)
            
            # 1. Rank selection
            rank = max(1, base_rank)
            
            # 2. Decomposition
            error, X_hat = self._cp_decompose(X, rank)
            
            # 3. Complexity (MDL)
            mdl = self._calculate_mdl(X, X_hat, rank)
            
            # 4. Sensitivity
            sens = self._sensitivity_analysis(X, rank)
            
            # 5. Score Calculation
            # Lower error, lower MDL, lower sensitivity = Better
            # Score = -(error + lambda_l * mdl + lambda_s * sens)
            raw_score = -(error + self.lambda_l * mdl + self.lambda_s * sens)
            
            # NCD Tiebreaker (Max 15% influence logic handled by scaling)
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD to similar scale as raw_score roughly
            ncd_penalty = ncd_val * 0.5 
            
            final_score = raw_score - ncd_penalty
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Rank:{rank}, Err:{error:.2f}, MDL:{mdl:.2f}, Sens:{sens:.2f}, NCD:{ncd_val:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity/traps.
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Match Check
        # If the answer has no structural overlap with prompt logic, confidence should be low
        p_feats = set()
        a_feats = set()
        
        # Simple feature presence check
        for key in ['negation', 'comparative', 'conditional', 'causal', 'quantifier']:
            if self.patterns[key].search(prompt): p_feats.add(key)
            if self.patterns[key].search(answer): a_feats.add(key)
            
        # If prompt has logic but answer has none, lower confidence
        structural_match = 1.0
        if len(p_feats) > 0 and len(p_feats & a_feats) == 0:
            # Prompt asks for logic, answer provides none?
            # Unless it's a simple factoid. 
            # Heuristic: if prompt has numbers, answer should too.
            if re.search(r'\d', prompt) and not re.search(r'\d', answer):
                structural_match = 0.4
            elif len(p_feats) > 2: # Complex logic required
                structural_match = 0.5

        # 3. Base score from evaluation
        eval_res = self.evaluate(prompt, [answer])
        base_score = 0.5
        if eval_res:
            # Normalize score roughly to 0-1 range based on typical outputs
            # Scores are negative, closer to 0 is better.
            s = eval_res[0]['score']
            # Map typical range [-10, 0] to [0, 1]
            base_score = max(0.0, min(1.0, (s + 10) / 10.0))
            
        final_conf = base_score * structural_match
        
        # Apply hard cap from meta-analysis
        if final_conf > meta_cap:
            final_conf = meta_cap
            
        # Never exceed 0.9 without explicit computation proof (heuristic here)
        if final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 3)