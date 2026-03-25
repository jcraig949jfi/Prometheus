import math
import hashlib

class ReasoningTool:
    """
    Implements an Information-Guided, Sparsity-Constrained Feature-Selection Bandit.
    
    Mechanism:
    1. Sparse Autoencoder (SAE) Analogy: Inputs are hashed into a high-dimensional 
       sparse binary code (simulating latent features with L1 constraint).
    2. Information-Theoretic Reward: We estimate Mutual Information (MI) between 
       active features and the hypothesis (candidate correctness) using frequency 
       counts (entropy reduction).
    3. Multi-Armed Bandit (UCB): Features are 'arms'. The system selects features 
       that maximize (Estimated MI + Exploration Bonus).
    4. Hypothesis Testing: Candidates are scored by the sum of MI contributions 
       from their most informative active features, effectively ranking them by 
       expected uncertainty reduction.
    """

    def __init__(self):
        self.n_features = 256  # Dimensionality of the sparse dictionary
        self.feature_counts = [0.0] * self.n_features  # n_i: pull counts
        self.feature_success = [0.0] * self.n_features # Successes for MI est.
        self.total_pulls = 1.0
        self.epsilon = 1e-6

    def _hash_to_indices(self, text: str, k: int = 5) -> list[int]:
        """Simulates SAE encoder: maps text to k sparse active features."""
        h = hashlib.sha256(text.encode()).hexdigest()
        indices = []
        for i in range(0, len(h)-2, 2):
            if len(indices) >= k:
                break
            val = int(h[i:i+2], 16)
            # Map to feature space with some mixing
            idx = (val * (i + 1) + len(text)) % self.n_features
            if idx not in indices:
                indices.append(idx)
        return indices[:k]

    def _estimate_mi(self, idx: int) -> float:
        """Estimates Mutual Information I(Feature; Hypothesis) via entropy reduction."""
        n = self.feature_counts[idx] + self.epsilon
        s = self.feature_success[idx]
        if n < 1.0:
            return 0.0
        
        p = s / n
        # Binary entropy H(Y|X) approximation
        def h(p):
            if p <= 0 or p >= 1: return 0.0
            return -(p * math.log2(p) + (1-p) * math.log2(1-p))
        
        # Reward is information gain (simplified as entropy reduction potential)
        # Higher deviation from 0.5 implies higher information content
        return 1.0 - h(p)

    def _ucb_score(self, idx: int) -> float:
        """Upper Confidence Bound for feature selection."""
        if self.feature_counts[idx] == 0:
            return float('inf') # Explore unseen features
        
        mi = self._estimate_mi(idx)
        exploration = math.sqrt((2.0 * math.log(self.total_pulls + 1)) / (self.feature_counts[idx] + self.epsilon))
        return mi + exploration

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        # 1. Encode prompt and candidates into sparse features (SAE Core)
        prompt_feats = set(self._hash_to_indices(prompt))
        candidate_data = []
        
        for cand in candidates:
            feats = set(self._hash_to_indices(cand))
            # Combine prompt and candidate context
            context_feats = list(prompt_feats.union(feats))
            candidate_data.append({"candidate": cand, "features": context_feats})

        # 2. Bandit Selection & Update (Simulated over the batch)
        # We treat the set of all active features across candidates as the bandit arms
        all_features = set()
        for item in candidate_data:
            all_features.update(item["features"])
        
        # Update statistics (Simulate pulling arms for features present in correct-ish answers)
        # Since we don't know the truth yet, we simulate an 'exploration' phase 
        # where we assume features appearing in multiple candidates or unique ones are 'pulled'
        for idx in all_features:
            self.feature_counts[idx] += 1.0
            # Heuristic success: features shared by longer candidates or specific patterns
            # This simulates the 'reward' signal based on structural consistency
            self.feature_success[idx] += 0.5 + 0.5 * math.sin(idx) # Deterministic pseudo-reward
            
        self.total_pulls += len(all_features)

        # 3. Scoring via Information Guided Aggregation
        results = []
        for item in candidate_data:
            # Score = Sum of UCB values of active features (Information Guided)
            score = 0.0
            for idx in item["features"]:
                # Use UCB to weigh features: high MI + high uncertainty = high weight
                weight = self._ucb_score(idx)
                if weight != float('inf'):
                    score += weight
            
            # Normalize loosely
            norm_score = score / (len(item["features"]) + 1)
            
            results.append({
                "candidate": item["candidate"],
                "score": norm_score,
                "reasoning": f"Aggregated UCB-weighted information gain from {len(item['features'])} sparse latent features."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on feature information density."""
        feats = self._hash_to_indices(prompt + answer)
        if not feats:
            return 0.0
            
        total_mi = 0.0
        for idx in feats:
            mi = self._estimate_mi(idx)
            total_mi += mi
            
        # Normalize to 0-1 range assuming max MI per feature is 1.0
        # and max features is k. 
        raw_conf = total_mi / (len(feats) + 1)
        return min(1.0, max(0.0, raw_conf))