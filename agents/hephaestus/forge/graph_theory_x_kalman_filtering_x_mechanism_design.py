import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Truthful Graph-Structured Kalman Consensus Filter for Reasoning.
    
    Mechanism:
    1. Structural Parsing (Graph Topology): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a structural adjacency matrix.
    2. Local Estimation (Kalman): Computes a prior belief score based on constraint 
       satisfaction and numeric consistency.
    3. Incentive Layer (Mechanism Design): Applies a quadratic scoring rule penalty 
       to candidates that deviate significantly from the structural consensus, 
       making 'strategic' (gameable) answers costly.
    4. Fusion: Aggregates scores using Laplacian-weighted consensus to produce 
       final rankings.
    """

    def __init__(self):
        self.eps = 1e-6

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extracts logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negation': len(re.findall(r'\b(no|not|never|none|neither|without)\b', text_lower)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'conditional': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numeric': len(re.findall(r'\d+', text_lower))
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = zlib.compress(s1.encode())
        c2 = zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(c1), len(c2))
        if max_len == 0:
            return 0.0
        return (len(c12) - min(len(c1), len(c2))) / max_len

    def _evaluate_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Internal step: Computes local Kalman-like estimate and mechanism penalty.
        Returns (score, reasoning_string)
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # 1. Structural Consistency (The "Measurement")
        # Penalize if prompt has strong logic markers but candidate lacks them
        logic_gap = 0.0
        reasons = []
        
        if p_feat['negation'] > 0 and c_feat['negation'] == 0:
            logic_gap += 0.5
            reasons.append("Missing negation handling")
        if p_feat['comparative'] > 0 and c_feat['comparative'] == 0:
            logic_gap += 0.3
            reasons.append("Missing comparative logic")
        if p_feat['conditional'] > 0 and c_feat['conditional'] == 0:
            logic_gap += 0.4
            reasons.append("Missing conditional flow")
            
        # Numeric consistency check (simplified)
        if p_feat['numeric'] > 0 and c_feat['numeric'] == 0:
            logic_gap += 0.2
            reasons.append("Missing numeric evaluation")

        # Base score from structural fit (inverse of gap)
        base_score = max(0.0, 1.0 - logic_gap)
        
        # 2. Mechanism Design: Quadratic Scoring Rule Penalty
        # If the candidate is too short compared to prompt complexity, penalize heavily
        # This simulates the "cost of misreporting"
        len_ratio = len(candidate) / (len(prompt) + 1)
        if len_ratio < 0.05 and p_feat['numeric'] + p_feat['comparative'] > 0:
            penalty = 0.4 * ((0.1 - len_ratio) ** 2) * 100 # Heavy penalty for laziness on complex prompts
            reasons.append(f"Penalty for brevity on complex prompt: -{penalty:.2f}")
        else:
            penalty = 0.0
            
        final_score = base_score - penalty
        
        # 3. NCD as Tiebreaker/Refinement
        ncd_val = self._compute_ncd(prompt, candidate)
        # Adjust score slightly by similarity, but structural parse is dominant
        final_score = (final_score * 0.7) + ((1.0 - ncd_val) * 0.3)
        
        reason_str = "; ".join(reasons) if reasons else "Structural alignment confirmed"
        return final_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Runs the distributed estimation loop.
        1. Local prediction (structural parse).
        2. Neighbor exchange (simulated via global candidate set).
        3. Mechanism penalty application.
        4. Laplacian-weighted fusion (simulated via averaging with neighbors).
        """
        if not candidates:
            return []
            
        n = len(candidates)
        if n == 0:
            return []

        # Step 1 & 2: Local Estimates and Initial Scoring
        scores = np.zeros(n)
        reasons = []
        
        for i, cand in enumerate(candidates):
            score, reason = self._evaluate_candidate(prompt, cand)
            scores[i] = score
            reasons.append(reason)
            
        # Step 3: Graph Consensus (Simulated via Laplacian smoothing)
        # Construct adjacency based on NCD similarity (neighbors are similar candidates)
        # This creates the "Graph Structure" for the consensus filter
        adj = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = self._compute_ncd(candidates[i], candidates[j])
                    if dist < 0.8: # Threshold for connectivity
                        adj[i, j] = 1.0 - dist
        
        # Degree matrix and Laplacian
        D = np.diag(np.sum(adj, axis=1))
        L = D - adj
        
        # Consensus update: x_new = x_old - alpha * L * x_old
        # This smooths scores across the graph of similar candidates
        alpha = 0.1
        scores = scores - alpha * np.dot(L, scores)
        
        # Normalize to 0-1 range for stability
        min_s, max_s = scores.min(), scores.max()
        if max_s - min_s > self.eps:
            scores = (scores - min_s) / (max_s - min_s)
        else:
            scores = np.ones(n) * 0.5

        # Step 4: Output Ranking
        results = []
        sorted_idx = np.argsort(scores)[::-1] # Descending
        
        for idx in sorted_idx:
            results.append({
                "candidate": candidates[idx],
                "score": float(scores[idx]),
                "reasoning": reasons[idx]
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and mechanism penalty.
        """
        score, _ = self._evaluate_candidate(prompt, answer)
        # Clamp between 0 and 1
        return max(0.0, min(1.0, score))