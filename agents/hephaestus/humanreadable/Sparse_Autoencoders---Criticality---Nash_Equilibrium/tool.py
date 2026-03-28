import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning evaluator based on Sparse Autoencoders (SAE), 
    Criticality scaling, and Game-Theoretic weighting.
    
    Mechanism:
    1. Structural Parsing: Extracts logical primitives (negations, comparatives, 
       conditionals, causals, ordering) into a binary feature vector x.
    2. Sparse Encoding: Uses a fixed over-complete dictionary D and soft-thresholding 
       to find sparse codes z.
    3. Criticality: Scales reconstruction error by susceptibility chi (inverse variance).
    4. Game-Theoretic Scoring: Simulates an evaluator vs. nature game to find robust 
       weights w, avoiding over-reliance on any single fragile feature.
    5. NCD Tiebreaker: Uses Normalized Compression Distance only when structural 
       signals are ambiguous.
    """

    def __init__(self):
        # Fixed random seed for determinism
        np.random.seed(42)
        
        # Define logical primitives (Features)
        self.primitives = [
            'not', 'never', 'no', 'none', 'cannot', # Negations
            'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'exceeds', # Comparatives
            'if', 'then', 'unless', 'provided', 'condition', # Conditionals
            'because', 'therefore', 'leads', 'causes', 'results', # Causal
            'first', 'last', 'between', 'before', 'after', 'next' # Ordering
        ]
        self.F = len(self.primitives)
        
        # Over-complete dictionary D (F x K, K > F). 
        # Initialized to identity + noise to simulate learned over-completeness.
        self.K = int(self.F * 1.5)
        self.D = np.zeros((self.F, self.K))
        self.D[:self.F, :self.F] = np.eye(self.F)
        if self.K > self.F:
            self.D[:self.F, self.F:] = np.random.randn(self.F, self.K - self.F) * 0.1
            
        # Regularization parameter for sparsity
        self.lambda_reg = 0.1

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector from text based on logical primitives."""
        text_lower = text.lower()
        x = np.zeros(self.F, dtype=float)
        for i, prim in enumerate(self.primitives):
            if prim in text_lower:
                x[i] = 1.0
        return x

    def _soft_threshold(self, v: np.ndarray, thresh: float) -> np.ndarray:
        """Element-wise soft thresholding (shrinkage)."""
        return np.sign(v) * np.maximum(np.abs(v) - thresh, 0.0)

    def _encode(self, x: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Encode x using sparse autoencoder logic.
        Returns sparse code z and reconstruction error.
        """
        # Encoder step: z = S(D^T x)
        z_raw = self.D.T @ x
        z = self._soft_threshold(z_raw, self.lambda_reg / 2.0)
        
        # Reconstruction
        x_hat = self.D @ z
        error = np.sum((x - x_hat) ** 2)
        
        return z, error

    def _compute_criticality(self, z: np.ndarray) -> float:
        """
        Compute susceptibility chi based on active code variance.
        Chi = 1 / Var(z_active). If no active codes, return 1.0.
        """
        active_mask = np.abs(z) > 1e-9
        if not np.any(active_mask):
            return 1.0
        
        active_z = z[active_mask]
        if len(active_z) < 2:
            return 1.0
            
        var_z = np.var(active_z)
        if var_z < 1e-9:
            return 1.0
            
        return 1.0 / var_z

    def _game_theoretic_score(self, errors: List[float], iterations: int = 10) -> float:
        """
        Simulate the evaluator vs nature game to find robust weights.
        Nature maximizes error on specific features; Evaluator minimizes weighted error.
        Returns the final score s = -w^T e.
        """
        if not errors:
            return 0.0
            
        n_features = len(errors)
        if n_features == 0:
            return 0.0

        # Initialize weights uniformly
        w = np.ones(n_features) / n_features
        
        # Convert errors to numpy array for manipulation
        e = np.array(errors)
        
        # Normalize errors to [0, 1] range for stability
        e_max = np.max(e) if np.max(e) > 0 else 1.0
        e_norm = e / e_max
        
        for _ in range(iterations):
            # Nature's move: Perturb the feature with maximal error contribution
            # In this simplified model, nature amplifies the max error dimension
            max_idx = np.argmax(e_norm)
            perturbation = np.zeros(n_features)
            perturbation[max_idx] = 0.1 # Adversarial nudge
            e_perturbed = e_norm + perturbation
            e_perturbed = np.clip(e_perturbed, 0, 1)
            
            # Evaluator's move: Update weights via projected gradient ascent on -w^T e
            # Gradient of -w^T e w.r.t w is -e. We want to minimize w^T e, so move against e.
            # However, the prompt says: "evaluator updates w via projected gradient ascent on -w^T e"
            # Ascent on negative loss = Descent on loss.
            # But nature wants to maximize, evaluator wants to minimize.
            # Payoff evaluator: -w^T e. Gradient w.r.t w is -e.
            # To maximize payoff (minimize error), we move in direction of -(-e) = e? 
            # No, if payoff is -w^T e, to maximize payoff we want w on smallest e.
            # Gradient of (-w^T e) is -e. Ascent step: w_new = w + lr * (-e) = w - lr * e.
            # Then project to simplex.
            
            lr = 0.1
            w_new = w - lr * e_perturbed
            
            # Project onto simplex (sum=1, w>=0) - simplified via clipping and normalization
            w_new = np.maximum(w_new, 0)
            if np.sum(w_new) > 0:
                w_new = w_new / np.sum(w_new)
            else:
                w_new = np.ones(n_features) / n_features
            
            w = w_new

        # Final score is negative weighted error (higher is better in our context if we invert,
        # but prompt says "Lower s indicates a better answer" for s = -w^T e.
        # Our interface requires Higher score = more likely correct.
        # So we return -s = w^T e? No, if s = -w^T e is lower=better, then w^T e is lower=better.
        # We need Higher score = better. So we return - (w^T e).
        
        final_weighted_error = np.dot(w, e_norm)
        return -final_weighted_error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2, c12 = len(zlib.compress(b1)), len(zlib.compress(b2)), len(zlib.compress(b1 + b2))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt features
        prompt_features = self._extract_features(prompt)
        
        candidate_scores = []
        
        for cand in candidates:
            # 1. Structural Feature Extraction
            cand_features = self._extract_features(cand)
            
            # Combine prompt and candidate logic (simple concatenation or interaction)
            # Here we treat the pair as a single logical state
            combined_x = np.concatenate([prompt_features, cand_features])
            
            # To fit our fixed D matrix which expects F dimensions, we sum or average logic
            # Since D is F x K, and we have 2F features now, let's average the logic vectors
            # to see if the candidate "matches" the prompt's logical density.
            # Actually, the prompt implies x is the feature vector of the *answer* in context.
            # Let's use the candidate features as x, but penalize if prompt has constraints candidate misses.
            
            # Refined approach: x = cand_features. 
            # But we must account for prompt constraints. 
            # If prompt has "not", candidate should reflect that.
            # We'll use the raw candidate features for the SAE pass.
            x = cand_features
            
            # 2. Sparse Encoding
            z, raw_error = self._encode(x)
            
            # 3. Criticality Scaling
            chi = self._compute_criticality(z)
            scaled_error = raw_error * chi
            
            # We need a list of errors for the game theoretic part. 
            # Since we have one candidate, we simulate "features" as the dimensions of error contribution?
            # No, the game is over the *candidates* or over the *features*?
            # Prompt: "two-player game between the evaluator (choosing a weight vector w) ... nature perturbs features"
            # This implies w weighs the FEATURES.
            # So 'errors' passed to the game should be the per-feature reconstruction errors.
            x_hat = self.D @ z
            feature_errors = (x - x_hat) ** 2
            
            # 4. Game Theoretic Scoring
            # Pass the per-feature errors to the game solver
            gt_score = self._game_theoretic_score(feature_errors.tolist())
            
            # 5. NCD Tiebreaker / Augmentation
            # If structural signal is weak (low variance in features), boost NCD influence
            if np.std(x) < 0.1:
                ncd_val = self._ncd(prompt, cand)
                # NCD is distance (lower is better), convert to score (higher is better)
                # Invert and scale to match magnitude of gt_score (~1.0)
                ncd_score = -ncd_val
                final_score = gt_score * 0.7 + ncd_score * 0.3
            else:
                final_score = gt_score

            # Reasoning string generation
            reason_parts = []
            if np.any(x > 0):
                detected = [self.primitives[i] for i in range(len(self.primitives)) if x[i] > 0]
                reason_parts.append(f"Detected logic: {', '.join(detected[:3])}")
            if chi > 2.0:
                reason_parts.append("High criticality (sensitive to perturbations)")
            if not reason_parts:
                reason_parts.append("Standard structural alignment")
                
            reasoning_str = "; ".join(reason_parts)
            
            candidate_scores.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning_str
            })

        # Sort by score descending (higher is better)
        candidate_scores.sort(key=lambda k: k['score'], reverse=True)
        return candidate_scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluation score mapped to probability via sigmoid-like scaling.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to [0, 1]. 
        # Typical scores are around -1 to 0 (from negative error) or small positives.
        # Shift and scale: assume score range [-2, 0] is common for bad, >0 good.
        # Sigmoid approximation: 1 / (1 + exp(-k(x - x0)))
        # Let's use a simple linear mapping clamped to [0,1] for robustness without torch.
        # If score > 0, high confidence. If score < -1, low.
        conf = 1.0 / (1.0 + np.exp(-2.0 * (score + 0.5)))
        return float(np.clip(conf, 0.0, 1.0))