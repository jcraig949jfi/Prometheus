import math
import hashlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a simplified ergodic epistemic reasoning engine.
    
    Mechanism:
    1. Ergodic Sampler: Uses a deterministic pseudo-random walk (seeded by content)
       to simulate Hamiltonian Monte-Carlo exploration of the hypothesis space.
    2. Global Workspace (MoE): Simulates expert selection by hashing candidates
       to specific 'expert' logic gates that evaluate different features (length,
       keyword density, semantic overlap). Only top-k experts contribute.
    3. Epistemic Justification: Computes three scores:
       - Foundational Prior: Based on prompt-candidate lexical overlap.
       - Coherence Penalty: Based on internal consistency (simulated via hash stability).
       - Reliability: Exponential moving average of prediction error (simulated).
    These scores reshape the sampling potential, biasing the final ranking.
    """

    def __init__(self):
        self._reliability_ema = 0.5  # Initial reliability estimate
        self._learning_rate = 0.1

    def _hash_to_float(self, s: str) -> float:
        """Deterministic mapping of string to [0, 1]."""
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        return int(h[:8], 16) / (16**8)

    def _compute_prior(self, prompt: str, candidate: str) -> float:
        """Foundational prior: Log-probability based on word overlap."""
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        if not c_words:
            return -10.0
        overlap = len(p_words & c_words)
        # Smoothed log probability
        return math.log(overlap + 1) - math.log(len(c_words) + 1)

    def _compute_coherence(self, prompt: str, candidate: str) -> float:
        """Coherence penalty: Negative KL-divergence approximation."""
        # Simulate distribution mismatch via hash difference
        h1 = self._hash_to_float(prompt + candidate)
        h2 = self._hash_to_float(candidate + prompt)
        # KL-like penalty: high if distributions (hashes) differ significantly
        diff = abs(h1 - h2)
        return -diff * 5.0  # Penalty scaled

    def _compute_expert_activation(self, candidate: str, expert_id: int) -> float:
        """Simulates sparse MoE expert activation."""
        # Expert 0: Length expert
        if expert_id == 0:
            val = 1.0 / (abs(len(candidate) - 50) + 1)
        # Expert 1: Complexity expert (unique chars)
        elif expert_id == 1:
            val = len(set(candidate)) / (len(candidate) + 1)
        # Expert 2: Pattern expert (hash based)
        else:
            val = self._hash_to_float(f"expert_{expert_id}_{candidate}")
        return val

    def _ergodic_sample(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """
        Simulates ergodic MCMC sampling over the candidate space.
        Returns weighted samples based on epistemic potential.
        """
        sampled_scores = []
        
        for cand in candidates:
            # 1. Calculate Epistemic Components
            prior = self._compute_prior(prompt, cand)
            coherence = self._compute_coherence(prompt, cand)
            
            # 2. Global Workspace: Select top 2 experts out of 3
            expert_scores = [self._compute_expert_activation(cand, i) for i in range(3)]
            expert_scores.sort(reverse=True)
            workspace_broadcast = sum(expert_scores[:2])  # Sum of top-k experts
            
            # 3. Epistemic Justification Score (Potential Function)
            # U = - (Prior + Coherence + Reliability * Workspace)
            reliability = self._reliability_ema
            potential = prior + coherence + (reliability * workspace_broadcast)
            
            # Add deterministic noise for ergodicity (simulated via hash)
            noise = (self._hash_to_float(cand + prompt) - 0.5) * 0.1
            final_score = potential + noise
            
            sampled_scores.append((cand, final_score))
            
            # Update reliability estimate (simplified error feedback)
            # If score is high, assume reliable; else less so.
            target_rel = 1.0 / (1.0 + math.exp(-final_score)) # Sigmoid
            self._reliability_ema = (1 - self._learning_rate) * self._reliability_ema + \
                                    self._learning_rate * target_rel

        return sampled_scores

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Run ergodic sampling to get scores
        scored_candidates = self._ergodic_sample(prompt, candidates)
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        max_score = scored_candidates[0][1] if scored_candidates else 0
        
        for cand, score in scored_candidates:
            # Normalize score for readability
            norm_score = score - max_score 
            reason = f"Epistemic score derived from prior coherence and MoE expert consensus."
            results.append({
                "candidate": cand,
                "score": norm_score,
                "reasoning": reason
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against itself to get raw score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]["score"]
        # Map raw score (usually negative or small positive) to [0, 1]
        # Using sigmoid approximation
        conf = 1.0 / (1.0 + math.exp(-raw_score))
        return max(0.0, min(1.0, conf))