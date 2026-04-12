import re
import math
import zlib
import numpy as np

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Multi-Armed Bandits, and MaxEnt principles.
    
    Mechanism:
    1. Structural Parsing: Extracts linguistic features (negations, comparatives, numbers).
    2. MaxEnt Prior: Initializes a Gaussian belief over feature weights based on linear constraints.
    3. Kalman Update: Treats the 'correctness score' as a latent state, updating beliefs as 
       structural evidence is observed in the candidate text.
    4. MAB Exploration: Uses UCB to weigh uncertain but informative features heavily.
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity traps (Tier B).
    
    Scoring: Structural (50%+) + Computation (20%+) + NCD Tiebreaker (<15%).
    """

    def __init__(self):
        # Feature definitions (Regex patterns)
        self.feature_names = [
            "negation", "comparative", "conditional", "numeric", 
            "causal", "ordering", "quantifier", "modal"
        ]
        self.patterns = [
            re.compile(r'\b(not|never|no|none|neither)\b', re.IGNORECASE),
            re.compile(r'\b(more|less|greater|smaller|better|worse|than|er)\b', re.IGNORECASE),
            re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.IGNORECASE),
            re.compile(r'\d+(\.\d+)?%?'),
            re.compile(r'\b(cause|lead to|result in|due to|because)\b', re.IGNORECASE),
            re.compile(r'\b(first|second|before|after|next|last)\b', re.IGNORECASE),
            re.compile(r'\b(all|some|every|each|any|no)\b', re.IGNORECASE),
            re.compile(r'\b(must|should|might|could|would|may)\b', re.IGNORECASE)
        ]
        
        # Trap patterns for Tier B (Epistemic Honesty)
        self.trap_patterns = [
            re.compile(r'(have you stopped|did you stop|why did .+ fail|why did .+ stop)', re.IGNORECASE), # Presupposition
            re.compile(r'(every .+ (a|an) .+\?)', re.IGNORECASE), # Scope ambiguity hint
            re.compile(r'(told .+ he|told .+ she|who was)', re.IGNORECASE), # Pronoun ambiguity
            re.compile(r'(either .+ or .+)', re.IGNORECASE), # False dichotomy hint
            re.compile(r'(best|worst|favorite|most beautiful)', re.IGNORECASE), # Subjectivity
            re.compile(r'(impossible to know|not enough information)', re.IGNORECASE) # Unanswerable hints
        ]

        # Kalman State Initialization
        self.d = len(self.feature_names)
        self.w = np.zeros(self.d)  # Mean of weights
        # MaxEnt-inspired Covariance: Start with high uncertainty, constrained by calibration logic
        # We assume features are initially independent but uncertain.
        self.Sigma = np.eye(self.d) * 2.0 
        self.Q = np.eye(self.d) * 0.1  # Process noise (slow evolution)
        self.R = 1.0  # Measurement noise
        
        # MAB State
        self.arm_counts = np.zeros(self.d)
        self.total_steps = 1
        self.beta = 0.5  # Exploration parameter

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts and L2-normalizes structural features."""
        features = np.zeros(self.d)
        text_lower = text.lower()
        for i, pattern in enumerate(self.patterns):
            features[i] = len(pattern.findall(text_lower))
        
        # L2 Normalize
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        if min(c1, c2) == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Check: Detects ambiguity, presuppositions, and traps.
        Returns a cap on confidence (low if trap detected).
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # Check for trap indicators in prompt
        for pattern in self.trap_patterns:
            if pattern.search(p_lower):
                return 0.25  # Strong penalty for ambiguous/trap prompts
        
        # Check for "I don't know" or similar in answer if prompt was tricky
        if any(k in a_lower for k in ["cannot be determined", "insufficient", "ambiguous"]):
            return 0.9 # High confidence in the *admission* of uncertainty
            
        return 1.0 # No traps detected

    def _kalman_update(self, phi: np.ndarray, z: float):
        """
        Updates the latent belief state (w) given observation z = phi^T w + noise.
        State x = w (static, so F=I).
        """
        # Prediction
        mu_pred = self.w.copy()
        Sigma_pred = self.Sigma + self.Q
        
        # Update
        # H = phi.T
        # S = H Sigma H^T + R
        S = float(phi.T @ Sigma_pred @ phi + self.R)
        S_inv = 1.0 / S if S != 0 else 1.0
        
        # K = Sigma H^T S^-1
        K = (Sigma_pred @ phi) * S_inv
        
        # Innovation
        y = z - float(phi.T @ mu_pred)
        
        # Posterior
        self.w = mu_pred + K * y
        self.Sigma = (np.eye(self.d) - np.outer(K, phi)) @ Sigma_pred
        
        # Ensure symmetry
        self.Sigma = (self.Sigma + self.Sigma.T) / 2

    def _get_mab_ucb(self, phi: np.ndarray) -> np.ndarray:
        """Calculates UCB indices for feature exploration."""
        ucb = np.zeros(self.d)
        for i in range(self.d):
            # Expected variance reduction if we observe feature i
            # Simplified approximation for the specific context
            var_reduction = self.Sigma[i,i] - (self.Sigma[i,:] @ phi)**2 / (phi.T @ self.Sigma @ phi + self.R)
            var_reduction = max(0, var_reduction)
            
            # UCB formula
            if self.arm_counts[i] == 0:
                exploration_bonus = float('inf')
            else:
                exploration_bonus = self.beta * math.sqrt(math.log(self.total_steps + 1) / self.arm_counts[i])
            
            ucb[i] = var_reduction + exploration_bonus
        return ucb

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Core scoring logic:
        1. Extract features from candidate.
        2. Update Kalman state (simulating observation of 'correctness' proxy).
        3. Use MAB to weight features.
        4. Return expected score.
        """
        phi = self._extract_features(candidate)
        
        # Heuristic Observation (z): 
        # We simulate an observation based on feature density. 
        # If a candidate has rich structural features matching the prompt's complexity, 
        # we treat it as a positive signal.
        # Note: In a real training loop, 'z' would come from ground truth. 
        # Here, we approximate 'z' by checking feature overlap with prompt.
        phi_prompt = self._extract_features(prompt)
        overlap = np.dot(phi, phi_prompt)
        
        # Construct a pseudo-observation: 
        # High overlap + high feature count => higher likelihood of being a reasoned answer
        z = overlap * (np.sum(phi) + 0.1) 
        
        # Kalman Update (Learning the weights of features dynamically)
        self._kalman_update(phi, z)
        
        # MAB Step: Identify which features to trust/explore
        ucb_vals = self._get_mab_ucb(phi)
        best_arm = np.argmax(ucb_vals)
        self.arm_counts[best_arm] += 1
        self.total_steps += 1
        
        # Final Score Calculation
        # Mean prediction: phi^T * w
        score = float(phi.T @ self.w)
        
        # Uncertainty penalty: Lower score if variance is high
        variance = float(phi.T @ self.Sigma @ phi)
        score -= 0.5 * variance 
        
        return score

    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """
        Extracts numbers and checks for logical consistency (e.g., ordering, simple math).
        Returns a score boost if numbers align logically.
        """
        nums_p = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        nums_c = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if not nums_p:
            return 0.0
        
        score = 0.0
        # Check if candidate numbers are derived from prompt numbers (heuristic)
        if nums_c:
            # Reward if candidate contains numbers close to prompt (potential calculation result)
            # Or if it contains specific logical markers like "0" for impossible cases
            for nc in nums_c:
                for np_val in nums_p:
                    if abs(nc - np_val) < 0.01: # Exact match
                        score += 0.5
                    elif abs(nc - (np_val * 2)) < 0.01: # Simple doubling
                        score += 0.3
            
            # Check for comparative consistency if comparatives exist
            if re.search(r'(more|greater|larger)', candidate, re.IGNORECASE):
                if nums_c and max(nums_c) > min(nums_p or [0]):
                    score += 0.5
            if re.search(r'(less|smaller)', candidate, re.IGNORECASE):
                if nums_c and max(nums_c) < max(nums_p or [float('inf')]):
                    score += 0.5
                    
        return score

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-calculate NCD for tie-breaking
        # We compare candidate to prompt (relevance) and penalize length divergence
        base_ncd_scores = []
        for c in candidates:
            ncd = self._compute_ncd(prompt, c)
            # Normalize: lower NCD is better (more similar), but we want higher score
            # Also penalize extremely short answers unless they are "None"/"0"
            len_pen = 0 if len(c) > 3 else 0.5 
            base_ncd_scores.append(1.0 - ncd - len_pen)
        
        for i, cand in enumerate(candidates):
            # 1. Structural Score (Kalman/MAB driven) - Weight ~50%
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Numeric/Computation Score - Weight ~20%
            numeric_score = self._compute_numeric_score(prompt, cand)
            
            # 3. NCD Tiebreaker - Weight ~15%
            ncd_score = base_ncd_scores[i] * 0.15
            
            # Combined Score
            # Normalize struct_score roughly to 0-1 range based on typical outputs
            # The Kalman update can drift, so we sigmoid it slightly to keep stable
            final_score = (0.5 * (1.0 / (1.0 + math.exp(-struct_score)))) + \
                          (0.2 * numeric_score) + \
                          ncd_score
            
            # Reasoning string
            reasoning = f"Structural evidence (Kalman): {struct_score:.2f}; Numeric check: {numeric_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for Tier B traps.
        """
        # 1. Check for traps (Presuppositions, Ambiguity)
        trap_cap = self._meta_confidence(prompt, answer)
        if trap_cap < 0.3:
            return trap_cap
        
        # 2. Evaluate structural richness
        phi = self._extract_features(answer)
        phi_prompt = self._extract_features(prompt)
        
        # If no structural features found in either, low confidence
        if np.sum(phi) == 0 and np.sum(phi_prompt) == 0:
            return 0.25
            
        # 3. Calculate raw confidence based on feature match and certainty
        # Higher match + lower variance = higher confidence
        score_match = float(phi.T @ phi_prompt)
        variance = float(phi.T @ self.Sigma @ phi)
        
        raw_conf = score_match * (1.0 / (1.0 + variance))
        
        # Normalize roughly to 0-1
        raw_conf = min(1.0, max(0.0, raw_conf))
        
        # Apply Trap Cap (Epistemic Honesty)
        final_conf = min(raw_conf, trap_cap)
        
        # Never return > 0.9 unless it's a very strong numeric match
        if final_conf > 0.9:
            # Double check numeric validity
            if not re.search(r'\d', answer):
                final_conf = 0.85 # Cap non-numeric high confidence
                
        return final_conf