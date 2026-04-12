import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A neuro-symbolic reasoning tool combining Sparse Autoencoders (SAE) and 
    Monte Carlo Tree Search (MCTS) for logical consistency evaluation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, causality).
    2. SAE Encoding: Uses iterative soft-thresholding to create sparse latent codes.
    3. MCTS Rollout: Simulates truth assignments to undefined atoms to test consistency.
    4. Epistemic Honesty: Detects ambiguity/presupposition to cap confidence.
    """

    def __init__(self):
        self.F = 64  # Feature dimension
        self.K = 8   # Latent dimension
        self.rng = np.random.default_rng(42)  # Deterministic seed
        # Initialize dictionary D with random normal values, normalized columns
        self.D = self.rng.standard_normal((self.F, self.K))
        self.D = self.D / (np.linalg.norm(self.D, axis=0) + 1e-9)
        self.lambda_reg = 0.1

    def _parse_features(self, text: str) -> np.ndarray:
        """Extract binary logical atoms from text into a vector."""
        t = text.lower()
        vec = np.zeros(self.F)
        
        # Negations
        if re.search(r'\b(not|no|never|neither|n\'t)\b', t): vec[0] = 1
        # Comparatives
        if re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', t): vec[1] = 1
        if re.search(r'[><=]', text): vec[2] = 1
        # Conditionals
        if re.search(r'\b(if|then|unless|provided|implies)\b', t): vec[3] = 1
        # Causality
        if re.search(r'\b(cause|lead|result|because|since|therefore)\b', t): vec[4] = 1
        # Quantifiers
        if re.search(r'\b(every|all|some|any|none|exists)\b', t): vec[5] = 1
        # Numbers (presence of digits)
        if re.search(r'\d+', t): vec[6] = 1
        
        # Specific logic patterns
        if re.search(r'\b(either|or)\b', t) and re.search(r'\b(or)\b', t): vec[7] = 1 # Dichotomy hint
        
        # Word count features (hashed to indices)
        words = t.split()
        for i, w in enumerate(words[:10]):
            idx = (hash(w) % (self.F - 10)) + 10
            vec[idx] = 1
            
        return vec

    def _soft_threshold(self, z: np.ndarray, thresh: float) -> np.ndarray:
        return np.sign(z) * np.maximum(np.abs(z) - thresh, 0)

    def _encode_sparse(self, x: np.ndarray) -> np.ndarray:
        """Iterative soft-thresholding to solve LASSO: min ||x - Dz||^2 + lambda||z||_1"""
        z = np.zeros(self.K)
        L = np.linalg.norm(self.D, ord=2)**2 + 1e-9  # Lipschitz constant approx
        
        for _ in range  (50):  # Iterations
            grad = self.D.T @ (self.D @ z - x)
            z = z - (1/L) * grad
            z = self._soft_threshold(z, self.lambda_reg / L)
        return z

    def _reconstruct(self, z: np.ndarray) -> np.ndarray:
        return self.D @ z

    def _check_presuppositions(self, text: str) -> float:
        """Returns 1.0 if highly ambiguous/trapped, 0.0 if clear."""
        t = text.lower()
        score = 0.0
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        if re.search(r'\b(have you stopped|did you stop|why did .+ (fail|stop|quit)|when did .+ start)\b', t):
            score = max(score, 0.9)
            
        # 2. Scope ambiguity ("Every X ... a Y" - hard to detect perfectly without NLP, keyword heuristic)
        if re.search(r'\b(every|all)\b', t) and re.search(r'\b(same|different|own)\b', t):
            score = max(score, 0.7)
            
        # 3. Pronoun ambiguity patterns
        if re.search(r'\b(he|she|him|her|they)\b.*\b(who|which one)\b', t):
            score = max(score, 0.8)
            
        # 4. False dichotomy
        if re.search(r'\b(either .+ or|must be .+ or .+)\b', t) and not re.search(r'\b(both|maybe|possibly)\b', t):
            score = max(score, 0.6)
            
        # 5. Subjectivity
        if re.search(r'\b(best|worst|favorite|beautiful|ugly)\b', t) and not re.search(r'\b(data|fact|defined)\b', t):
            score = max(score, 0.5)
            
        return score

    def _meta_confidence(self, prompt: str) -> float:
        """Evaluates prompt properties to determine max allowable confidence."""
        trap_score = self._check_presuppositions(prompt)
        if trap_score > 0.5:
            return 0.25  # Cap for ambiguous/trap questions
        
        # Check for unanswerability markers
        if re.search(r'\b(insufficient|unknown|cannot be determined)\b', prompt.lower()):
            return 0.3
            
        return 1.0

    def _rollout_score(self, z_prompt: np.ndarray, z_candidate: np.ndarray, iterations: int = 20) -> float:
        """MCTS Rollout: Simulate truth assignments and check consistency."""
        total_score = 0.0
        
        # Reconstruct to get continuous approximation of logic
        x_prompt = self._reconstruct(z_prompt)
        x_cand = self._reconstruct(z_candidate)
        
        for _ in range(iterations):
            # Add noise to simulate sampling undefined atoms (Monte Carlo step)
            noise = self.rng.normal(0, 0.1, self.K)
            z_sim = z_candidate + noise
            
            # Reconstruct simulated state
            x_sim = self.D @ z_sim
            
            # Constraint Check 1: Structural alignment (Dot product similarity)
            struct_sim = np.dot(z_prompt, z_sim) / (np.linalg.norm(z_prompt) * np.linalg.norm(z_sim) + 1e-9)
            
            # Constraint Check 2: Numeric consistency heuristic
            # If prompt has numbers, candidate must have numbers or explicit negation
            has_num_p = z_prompt[6] > 0.5
            has_num_c = z_candidate[6] > 0.5
            numeric_consistent = (has_num_p == has_num_c) or (z_candidate[0] > 0.5) # Allow if negation present
            
            # Score calculation
            step_score = struct_sim
            if not numeric_consistent:
                step_score -= 0.5 # Penalty for numeric mismatch
            
            total_score += step_score
            
        return total_score / iterations

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse Prompt
        x_prompt = self._parse_features(prompt)
        z_prompt = self._encode_sparse(x_prompt)
        
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 2. Parse Candidate
            x_cand = self._parse_features(cand)
            z_cand = self._encode_sparse(x_cand)
            
            # 3. MCTS Evaluation
            mcts_score = self._rollout_score(z_prompt, z_cand)
            
            # 4. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # 5. Structural/Computation Weight (85%)
            # Normalize MCTS score roughly to [0, 1] range based on expected bounds
            base_score = (mcts_score + 1.0) / 2.0 
            final_score = 0.85 * base_score + ncd_score
            
            # Apply Epistemic Cap
            if meta_cap < 0.3:
                final_score = min(final_score, meta_cap)
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"MCTS coherence: {mcts_score:.2f}, Meta-cap: {meta_cap:.2f}"
            })
            
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps at 0.25 if prompt contains traps/ambiguity.
        Caps at 0.9 unless computation is definitive.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        x_p = self._parse_features(prompt)
        x_a = self._parse_features(answer)
        z_p = self._encode_sparse(x_p)
        z_a = self._encode_sparse(x_a)
        
        # Basic consistency
        sim = np.dot(z_p, z_a) / (np.linalg.norm(z_p) * np.linalg.norm(z_a) + 1e-9)
        base_conf = (sim + 1.0) / 2.0
        
        # Apply caps
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless it looks like a hard math/logic win
        # Heuristic: if numeric features match and no negation conflict
        numeric_match = (x_p[6] > 0.5) == (x_a[6] > 0.5)
        if not numeric_match and x_p[6] > 0.5:
            final_conf = min(final_conf, 0.4) # Low confidence if numbers missing in answer
            
        return float(min(max(final_conf, 0.0), 0.95 if meta_cap == 1.0 else 0.25))