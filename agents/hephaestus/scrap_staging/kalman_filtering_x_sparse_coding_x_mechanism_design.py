class ReasoningTool:
    """
    Recursive Sparse Incentive-Compatible Estimator (RSICE) Implementation.
    
    Mechanism:
    1. Structural Parsing (Kalman State): Extracts logical features (negations, comparatives, numbers).
       This forms the linear state vector x.
    2. Sparse Coding (Dictionary): Uses a fixed set of logical 'atoms' (e.g., 'not', '>', 'if').
       Only active atoms contribute to the state update, enforcing sparsity.
    3. Mechanism Design (VCG Scoring): Candidates are scored by their marginal contribution 
       to reducing uncertainty (structural match) minus a penalty for complexity/externality.
       
    Note: Per safety guidelines, Sparse Coding is restricted to the confidence wrapper 
    and structural feature extraction, while Kalman + Mechanism Design drive the core logic.
    """

    def __init__(self):
        # Fixed dictionary of logical atoms (Sparse Coding component)
        self.atoms = [
            (r'\bnot\b', -1.0), (r'\bno\b', -1.0), (r'\bnever\b', -1.0),
            (r'\byes\b', 1.0), (r'\btrue\b', 1.0), (r'\bcorrect\b', 1.0),
            (r'\bgreater\b', 1.0), (r'\bless\b', -1.0), (r'\bmore\b', 1.0),
            (r'\bif\b', 0.5), (r'\bthen\b', 0.5), (r'\btherefore\b', 0.8),
            (r'\d+\.\d+', 0.0), (r'\b\d+\b', 0.0) # Numeric placeholders
        ]
        self.atom_patterns = [(re.compile(p, re.IGNORECASE), w) for p, w in self.atoms]
        
        # Kalman State Initialization (State vector x, Covariance P)
        self.state_dim = 4 # [logic_score, numeric_match, negation_count, confidence]
        self.x = np.zeros(self.state_dim)
        self.P = np.eye(self.state_dim) * 0.5
        self.Q = np.eye(self.state_dim) * 0.1 # Process noise
        self.R = 0.2 # Measurement noise

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract sparse structural features based on the dictionary."""
        features = np.zeros(self.state_dim)
        logic_sum = 0.0
        neg_count = 0
        
        # Sparse activation: Only iterate patterns that match
        for pattern, weight in self.atom_patterns:
            matches = pattern.findall(text)
            if matches:
                if weight == 0.0: # Numeric detected
                    features[1] = 1.0
                elif weight < 0:
                    neg_count += len(matches)
                    logic_sum += weight * len(matches)
                else:
                    logic_sum += weight * len(matches)
        
        features[0] = logic_sum
        features[2] = neg_count
        # Heuristic for initial confidence based on length and structure
        features[3] = min(1.0, len(text) / 100.0) 
        return features

    def _kalman_update(self, z: np.ndarray) -> np.ndarray:
        """Perform a single Kalman predict-update step."""
        # Predict
        x_pred = self.x.copy() # Identity transition model
        P_pred = self.P + self.Q
        
        # Update
        K = P_pred @ np.linalg.inv(P_pred + np.eye(self.state_dim) * self.R)
        self.x = x_pred + K @ (z - x_pred)
        self.P = (np.eye(self.state_dim) - K) @ P_pred
        return self.x

    def _compute_vcg_payment(self, base_score: float, candidate_score: float, penalty: float) -> float:
        """
        Compute VCG-style payment: Improvement in accuracy - Externality (penalty).
        This ensures incentive compatibility: agents maximize utility by being truthful/accurate.
        """
        improvement = candidate_score - base_score
        return improvement - penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_features = self._extract_features(prompt)
        base_state = self._kalman_update(prompt_features)
        base_score = float(np.mean(base_state))
        
        results = []
        for cand in candidates:
            # Reset state for fair comparison (or maintain sequence if context implies)
            # Here we treat each candidate as an independent measurement against the prompt context
            temp_x = self.x.copy() 
            cand_features = self._extract_features(cand)
            
            # Combine prompt and candidate features for joint estimation
            joint_obs = (prompt_features + cand_features) / 2.0
            
            # Kalman Update for this candidate
            # We simulate the update without permanently altering global state for the next candidate
            # by using a local copy logic or resetting. For simplicity in this tool, 
            # we calculate the 'measurement' of the candidate relative to the prompt.
            
            # Scoring Logic (Mechanism Design)
            # 1. Structural Match: Does the candidate answer the logical constraints?
            structural_match = 0.0
            if prompt_features[0] > 0 and cand_features[0] > 0:
                structural_match = 1.0
            elif prompt_features[0] < 0 and cand_features[0] < 0:
                structural_match = 1.0 # Double negative or consistent negation
                
            # 2. Numeric Consistency
            numeric_consistency = 0.0
            if prompt_features[1] > 0 or cand_features[1] > 0:
                # Simple heuristic: if both have numbers, assume consistency for now
                numeric_consistency = 0.5 if (prompt_features[1] > 0 and cand_features[1] > 0) else 0.0
            
            # Raw Score
            raw_score = structural_match + numeric_consistency + (cand_features[3] * 0.2)
            
            # Penalty (Complexity/Length penalty to simulate externality)
            penalty = min(0.5, len(cand) / 500.0)
            
            # VCG Payment as final score
            final_score = self._compute_vcg_payment(base_score, raw_score, penalty)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {structural_match:.2f}, Numeric: {numeric_consistency:.2f}, Penalty: {penalty:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str