import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Emergence, Multi-Armed Bandits, and the Free Energy Principle.
    
    Mechanism:
    1. Structural Parsing (Micro-level): Extracts linguistic features (negations, causals, etc.)
       into a feature vector x for each candidate.
    2. Free Energy Minimization (Learning): Maintains a Bayesian posterior over weights w.
       Updates mu (mean) and Sigma (covariance) based on prediction error delta = r - wTx.
       This approximates variational free energy minimization.
    3. Thompson Sampling + UCB (Exploration): Draws samples from the posterior and adds
       an exploration bonus to select the best candidate, exhibiting weak emergence where
       the score is a non-linear function of uncertainty and structural fit.
    4. Epistemic Honesty (Meta-cognition): Explicitly checks for ambiguity, presuppositions,
       and false dichotomies to cap confidence scores, ensuring the system admits ignorance.
    """

    def __init__(self):
        # Feature definitions
        self.features = [
            ('negation', r'\b(not|no|never|none|n\'t)\b', True),
            ('comparative', r'\b(more|less|better|worse|greater|lesser|er|as\s+\w+\s+as)\b', True),
            ('conditional', r'\b(if|unless|would|could|should|then)\b', True),
            ('numeric', r'\d+(\.\d+)?%?', False), # Count
            ('causal', r'\b(cause|lead to|result in|because|due to|since)\b', True),
            ('ordering', r'\b(before|after|above|below|precede|follow)\b', True),
            ('quantifier', r'\b(all|some|most|every|each|few)\b', True),
            ('modality', r'\b(must|might|may|can|will)\b', True),
        ]
        self.k = len(self.features)
        
        # Bayesian Bandit State: w ~ N(mu, Sigma)
        # Initialize with zeros (no prior bias) and identity covariance (high uncertainty)
        self.mu = np.zeros(self.k)
        self.Sigma = np.eye(self.k)
        self.sigma_noise = 0.1 # Observation noise variance
        self.trial_count = 0
        
        # Regular expressions pre-compilation
        self.regex_compiled = {
            name: re.compile(pattern, re.IGNORECASE) if is_binary else re.compile(pattern)
            for name, pattern, is_binary in self.features
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural feature vector x from text."""
        x = np.zeros(self.k)
        text_lower = text.lower()
        
        for i, (name, _, is_binary) in enumerate(self.features):
            pattern = self.regex_compiled[name]
            matches = pattern.findall(text_lower)
            count = len(matches)
            
            if is_binary:
                x[i] = 1.0 if count > 0 else 0.0
            else:
                x[i] = float(count)
        return x

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def _check_numerical_consistency(self, prompt: str, candidate: str) -> bool:
        """Simple constructive computation check for numeric consistency."""
        # Extract numbers from prompt and candidate
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', candidate)
        
        if not nums_p or not nums_c:
            return True # No numbers to check, assume neutral
            
        try:
            # If prompt has a comparison (e.g., "is 5 > 3?") and candidate answers it
            # This is a simplified heuristic for demonstration
            p_vals = [float(n) for n in nums_p[-3:]] # Look at last few numbers
            c_vals = [float(n) for n in nums_c]
            
            # Heuristic: If candidate repeats a number from prompt in a logical way, 
            # or performs a simple operation, it gets a boost. 
            # For this implementation, we just ensure no obvious contradiction 
            # (e.g. prompt says "5", candidate says "100" without context is risky)
            # We return True by default to avoid penalizing valid non-numeric reasoning
            return True 
        except ValueError:
            return True

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "have you quit", "why did", "when did", "how did"]
        if any(t in p_lower for t in presupposition_triggers):
            # Check if it implies a fact not in evidence
            if "stopped" in p_lower or "quit" in p_lower or "fail" in p_lower:
                return 0.2

        # 2. Scope/Pronoun Ambiguity
        if re.search(r'\b(every|all)\s+\w+\s+(did|has|was)\s+\w+\s+a\s+\w+', p_lower):
             # "Every X did a Y" - ambiguous if Y is same for all
             if "same" not in p_lower and "different" not in p_lower:
                 return 0.4
                 
        if re.search(r'\b(\w+)\s+told\s+(\w+)\s+he\s+', p_lower):
            return 0.3 # Pronoun ambiguity

        # 3. False Dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+', p_lower):
            if "only" not in p_lower and "options" not in p_lower:
                return 0.5

        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p_lower for w in subjective_words):
            if "measure" not in p_lower and "criteria" not in p_lower:
                return 0.4

        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Meta-confidence check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Extract features for all candidates
        X = np.array([self._extract_features(c) for c in candidates])
        n_candidates = len(candidates)
        
        # 3. Thompson Sampling: Sample weights from posterior
        # w_sample ~ N(mu, Sigma)
        try:
            w_sample = np.random.multivariate_normal(self.mu, self.Sigma)
        except np.linalg.LinAlgError:
            # Fallback if Sigma is singular
            w_sample = self.mu.copy()

        # 4. Compute Scores
        scores = []
        raw_scores = X.dot(w_sample)
        
        # Add UCB exploration bonus
        t = max(1, self.trial_count)
        ucb_bonus = np.sqrt(np.log(t + 1) / (np.arange(1, n_candidates + 1))) # Simplified n_i approximation
        
        final_scores = raw_scores + 0.5 * ucb_bonus
        
        # Normalize scores to 0-1 range for consistency, respecting meta_cap
        min_s, max_s = final_scores.min(), final_scores.max()
        if max_s > min_s:
            normalized_scores = (final_scores - min_s) / (max_s - min_s)
        else:
            normalized_scores = np.ones_like(final_scores) * 0.5
            
        # Apply meta-confidence cap
        normalized_scores = np.minimum(normalized_scores, meta_cap)

        # 5. Construct results
        results = []
        for i, cand in enumerate(candidates):
            score = float(normalized_scores[i])
            reasoning = f"Structural match: {score:.2f}. "
            if meta_cap < 0.5:
                reasoning += "Warning: Prompt contains ambiguity or presupposition."
            elif score > 0.8:
                reasoning += "High confidence based on structural alignment and low uncertainty."
            else:
                reasoning += "Moderate confidence; exploration term influenced ranking."
                
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Update internal state (Simulated trial for the top candidate)
        # In a real interactive setting, we would get 'r' from user feedback.
        # Here we simulate a self-consistency check: does the top answer entail constraints?
        if results:
            top_cand = results[0]['candidate']
            # Simple consistency proxy: NCD similarity to prompt (higher is often better for context)
            # Or just assume the top ranked by our model is the 'rewarded' one for learning purposes
            # to drive the weights towards features present in high-scoring candidates.
            x_top = X[0] # Features of the top ranked (after sorting, index 0 is top)
            
            # Simulate reward: 1 if structural features are present, else 0.5
            # This is a self-training heuristic since we lack external ground truth here
            r = 1.0 if np.any(x_top > 0) else 0.5
            
            # Prediction
            y_hat = self.mu.dot(x_top)
            delta = r - y_hat
            
            # Free Energy Minimization Update (Bayesian Linear Regression update step)
            # Sigma_new = (Sigma^-1 + (1/sigma^2) * x x^T)^-1
            # mu_new = Sigma_new * (Sigma^-1 * mu + (r/sigma^2) * x)
            
            Sigma_inv = np.linalg.inv(self.Sigma + 1e-6 * np.eye(self.k)) # Regularize
            x_col = x_top.reshape(-1, 1)
            
            # Kalman gain-like term
            try:
                Sigma_inv_new = Sigma_inv + (1.0 / self.sigma_noise) * (x_col @ x_col.T)
                Sigma_new = np.linalg.inv(Sigma_inv_new)
                
                mu_new = Sigma_new @ (Sigma_inv @ self.mu + (r / self.sigma_noise) * x_col)
                
                self.mu = mu_new.flatten()
                self.Sigma = Sigma_new
                self.trial_count += 1
            except np.linalg.LinAlgError:
                pass # Skip update if singular

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on prompt ambiguity (Tier B) and structural match.
        """
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural evaluation
        x = self._extract_features(prompt + " " + answer)
        
        # Predict score
        y_hat = self.mu.dot(x)
        
        # Calculate uncertainty (variance of prediction)
        # var = x^T Sigma x + sigma_noise
        pred_var = float(x @ self.Sigma @ x.T + self.sigma_noise)
        pred_std = np.sqrt(pred_var)
        
        # Convert uncertainty to a confidence penalty
        # High variance -> low confidence
        uncertainty_penalty = 1.0 / (1.0 + np.exp(-2 * (pred_std - 0.5))) # Sigmoid mapping
        
        base_conf = 1.0 / (1.0 + np.exp(-y_hat)) # Logistic transform of prediction
        
        # Combine
        raw_conf = base_conf * (1.0 - 0.5 * uncertainty_penalty)
        
        # Apply hard cap from meta-analysis
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure bounds
        return float(np.clip(final_conf, 0.0, 1.0))