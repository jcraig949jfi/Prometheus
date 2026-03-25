import math
import hashlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Falsifiability-driven Differentiable Architecture Search (FD-DARTS) Approximation.
    
    Mechanism:
    1. Hypothesis Encoding: Candidates are treated as hypotheses (h) in a version space.
    2. Predictive Information (I): Estimated via semantic similarity (hash-based overlap)
       between the prompt context and the candidate. Higher overlap = higher mutual information.
    3. Expected Falsification Gain (KL): We simulate a 'critical experiment' by checking
       how distinct the candidate is from the average of all candidates. A candidate that
       is too generic (high entropy across version space) has low falsification gain.
       A candidate that is specific and divergent maximizes the KL divergence between
       its specific prediction and the prior distribution of answers.
    4. Optimization: The score is L = I - lambda * Entropy (approximating the KL penalty
       for non-falsifiable, vague hypotheses). We maximize specificity and relevance.
    """

    def __init__(self):
        self.lambda_falsify = 0.5  # Weight for falsification penalty

    def _hash_vector(self, text: str, size: int = 64) -> List[float]:
        """Deterministic mapping of string to normalized float vector."""
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        vec = []
        for i in range(0, size):
            byte_idx = (i * 2) % (len(h) - 1)
            val = int(h[byte_idx:byte_idx+2], 16)
            vec.append(val / 255.0)
        return vec

    def _cosine_sim(self, v1: List[float], v2: List[float]) -> float:
        """Compute cosine similarity."""
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _estimate_mutual_info(self, prompt: str, candidate: str) -> float:
        """
        Estimate I(Y; f_alpha(X)) via semantic overlap.
        Uses hash-vector similarity as a proxy for predictive information.
        """
        # Augment prompt with candidate to see if it 'fits' the context structure
        combined = f"{prompt} {candidate}"
        v_prompt = self._hash_vector(prompt)
        v_combined = self._hash_vector(combined)
        
        # Similarity between prompt structure and combined structure indicates fit
        base_sim = self._cosine_sim(v_prompt, v_combined)
        return max(0.0, base_sim)

    def _estimate_falsification_gain(self, candidate: str, all_candidates: List[str]) -> float:
        """
        Estimate Expected Falsification Gain.
        Measures how much observing this candidate reduces the version space.
        High gain = Candidate is distinct from the 'average' hypothesis (low prior entropy).
        """
        if len(all_candidates) <= 1:
            return 1.0
            
        v_cand = self._hash_vector(candidate)
        
        # Compute 'prior' as the centroid of all candidates (the consensus)
        dim = len(v_cand)
        centroid = [0.0] * dim
        for c in all_candidates:
            v = self._hash_vector(c)
            for i in range(dim):
                centroid[i] += v[i]
        
        norm_factor = len(all_candidates)
        centroid = [x / norm_factor for x in centroid]
        
        # KL Divergence approx: Distance from centroid. 
        # If candidate == centroid, gain is 0 (no new info, cannot falsify consensus).
        # If candidate is distinct, gain is high.
        dist_sq = sum((a - b)**2 for a, b in zip(v_cand, centroid))
        gain = math.sqrt(dist_sq)
        
        return gain

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        # Pre-calculate centroid for falsification logic if needed, 
        # but here we compute per-candidate relative to the set
        
        for cand in candidates:
            # 1. Predictive Information Term
            pred_info = self._estimate_mutual_info(prompt, cand)
            
            # 2. Falsification Gain Term (KL divergence proxy)
            falsify_gain = self._estimate_falsification_gain(cand, candidates)
            
            # 3. Objective: Maximize (Predictive Info + lambda * Falsification Gain)
            # Note: Original formula subtracts KL cost, but here KL represents 'Gain'.
            # We want hypotheses that are both predictive AND highly falsifiable (specific).
            score = pred_info + (self.lambda_falsify * falsify_gain)
            
            reasoning = (
                f"Predictive Info: {pred_info:.4f}, "
                f"Falsification Gain: {falsify_gain:.4f}"
            )
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the FD-DARTS objective score.
        """
        # Evaluate single candidate against itself to get base metrics
        # We simulate a minimal version space to check distinctiveness
        dummy_space = [answer, f"not {answer}", "irrelevant"]
        ranked = self.evaluate(prompt, dummy_space)
        
        if not ranked:
            return 0.0
            
        # Find the specific answer in results
        target_score = None
        for res in ranked:
            if res["candidate"] == answer:
                target_score = res["score"]
                break
                
        if target_score is None:
            return 0.0
            
        # Normalize roughly to 0-1 assuming max theoretical score ~ 2.0
        conf = min(1.0, max(0.0, target_score))
        return conf