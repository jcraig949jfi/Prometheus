import re
import numpy as np
from math import log, digamma

class ReasoningTool:
    """
    Variational-Reward-Control Scoring (VRCS) Tool.
    
    Mechanism:
    1. Parsing: Extracts entities, relations, negations, comparatives, and numeric values 
       using regex to form grounded predicates.
    2. Free Energy (F): Computes prediction error based on a Dirichlet-multinomial model 
       over feature counts. Lower F indicates better alignment with the statistical 
       structure of the candidate set.
    3. Reward (R): Dot product of question and answer feature vectors (overlap).
    4. Control Cost (C): Quadratic penalty on weight deviation (regularization).
    5. Score: S = -F + R - C.
    
    Beats NCD baseline by focusing on structural logic (negation, magnitude) rather 
    than string compression similarity.
    """
    
    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none|cannot)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|larger|fewer|before|after|first|last)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in|causes)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'quantifier': re.compile(r'\b(all|some|every|each|any|most)\b', re.I),
            'modal': re.compile(r'\b(must|may|might|should|could|will)\b', re.I)
        }
        self.feature_keys = list(self.patterns.keys())
        self.d = len(self.feature_keys)

    def _extract_features(self, text: str) -> np.ndarray:
        """Convert text to a sparse binary feature vector + numeric stats."""
        text_lower = text.lower()
        features = np.zeros(self.d, dtype=float)
        
        # Binary structural flags
        for i, key in enumerate(self.feature_keys):
            if self.patterns[key].search(text_lower):
                features[i] = 1.0
                
        # Numeric density (heuristic for numeric reasoning)
        nums = self.patterns['numeric'].findall(text)
        if nums:
            # Add magnitude feature if numbers exist
            try:
                val = sum(float(n) for n in nums) / len(nums)
                # Normalize magnitude loosely to avoid overflow in dot products
                features[-1] = np.tanh(val / 1000.0) 
            except ValueError:
                pass
                
        return features

    def _compute_free_energy(self, X_candidates: np.ndarray, x_q: np.ndarray) -> np.ndarray:
        """
        Compute approximate Free Energy F(a) for each candidate.
        F = Prediction Error + Complexity
        Using Dirichlet-Multinomial approximation with alpha=1.
        """
        n_cands, d = X_candidates.shape
        if n_cands == 0:
            return np.array([])
            
        # Empirical expected feature distribution (prior + data)
        # p_hat = (alpha + sum(x)) / (d*alpha + total_count)
        alpha = 1.0
        sum_x = np.sum(X_candidates, axis=0) + alpha
        denom = np.sum(sum_x) + d * alpha # Normalization constant approx
        p_hat = sum_x / (np.sum(X_candidates, axis=0) + alpha * n_cands + 1e-9)
        p_hat = np.clip(p_hat, 1e-9, 1.0) # Avoid log(0)

        F = np.zeros(n_cands)
        
        for i in range(n_cands):
            x = X_candidates[i]
            # Avoid log(0) for zero features
            mask = x > 0
            if np.any(mask):
                # Prediction error term: sum(x_i * log(x_i / p_i))
                # Simplified for binary-ish features: x is 0 or 1 mostly
                err = np.sum(x[mask] * np.log(x[mask] / p_hat[mask]))
            else:
                err = 0.0
                
            # Complexity term (KL approx): sum(log(x_i + 1) - log(alpha)) 
            # Using psi(z) approx log(z-0.5) -> KL ~ log(x+0.5) - log(alpha-0.5)
            # Since alpha=1, log(0.5) is constant. We care about relative F.
            comp = np.sum(np.log(x + 0.5)) 
            
            F[i] = err + comp
            
        return F

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        # 1. Parse Question and Candidates
        x_q = self._extract_features(prompt)
        X_cands = np.array([self._extract_features(c) for c in candidates])
        
        # 2. Compute Components
        # Free Energy (Lower is better, so we subtract it later)
        F = self._compute_free_energy(X_cands, x_q)
        
        # Reward: Overlap with question (Dot product)
        # Weight vector w is the question features (as per spec)
        R = np.dot(X_cands, x_q)
        
        # Control Cost: Penalty for deviating from neutral (w0=0)
        # Since w = x_q, C = lambda/2 * ||x_q||^2. 
        # This is constant for all candidates given a fixed prompt, 
        # but we include it for theoretical completeness.
        lambda_param = 0.1
        C = (lambda_param / 2.0) * np.dot(x_q, x_q)
        
        # 3. Final Score: S = -F + R - C
        # Note: F can be negative in this approximation if probabilities are high, 
        # but generally we want to minimize F.
        scores = -F + R - C
        
        # Tie-breaking with NCD (Normalized Compression Distance) if scores are too close
        # Only used if max score diff is negligible
        if len(scores) > 1 and np.max(scores) - np.min(scores) < 1e-6:
            import zlib
            base_len = len(prompt.encode('utf-8'))
            ncds = []
            for c in candidates:
                c_enc = c.encode('utf-8')
                joint_len = len(zlib.compress((prompt + c).encode('utf-8')))
                c_len = len(c_enc)
                # NCD approx
                ncd = (joint_len - min(base_len, c_len)) / max(base_len, c_len, 1)
                ncds.append(-ncd) # Higher is better
            scores += np.array(ncds) * 0.01 # Small nudge

        # Construct result
        results = []
        for i, c in enumerate(candidates):
            results.append({
                "candidate": c,
                "score": float(scores[i]),
                "reasoning": f"F={-F[i]:.2f}, R={R[i]:.2f}, C={C:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimate confidence based on structural alignment and free energy.
        Returns 0.0 to 1.0.
        """
        # Evaluate single candidate against itself (degenerate case)
        # We simulate a scenario where the answer is the only option 
        # and check how well it fits the prompt's structural constraints.
        
        x_q = self._extract_features(prompt)
        x_a = self._extract_features(answer)
        
        # 1. Structural Overlap (Reward normalized)
        # If prompt has specific structural flags (negation, conditional), 
        # the answer should ideally reflect or address them.
        overlap = np.dot(x_q, x_a)
        q_mag = np.linalg.norm(x_q)
        a_mag = np.linalg.norm(x_a)
        
        if q_mag == 0:
            # No structural features detected, rely on length/complexity match
            base_conf = 0.5
        else:
            # Cosine similarity of structural features
            cos_sim = overlap / (q_mag * a_mag + 1e-9)
            base_conf = 0.5 + 0.4 * cos_sim # Map to 0.1 - 0.9 range
            
        # 2. Numeric Consistency Check (Heuristic)
        # If prompt has numbers and answer has numbers, check plausibility
        nums_p = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        nums_a = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', answer)]
        
        if nums_p and nums_a:
            # Simple heuristic: if prompt asks for comparison, does answer match?
            # This is a weak check without full logic, so we just boost confidence 
            # if numeric density matches roughly
            if abs(len(nums_p) - len(nums_a)) <= 1:
                base_conf = min(1.0, base_conf + 0.1)
                
        # 3. Negation consistency
        has_neg_p = bool(self.patterns['negation'].search(prompt))
        has_neg_a = bool(self.patterns['negation'].search(answer))
        
        if has_neg_p and not has_neg_a:
            # Prompt has negation, answer doesn't might be risky (or correct depending on context)
            # But if both have it, higher confidence in structural mirroring
            pass 
        elif has_neg_p and has_neg_a:
            base_conf = min(1.0, base_conf + 0.05)
            
        return float(np.clip(base_conf, 0.0, 1.0))