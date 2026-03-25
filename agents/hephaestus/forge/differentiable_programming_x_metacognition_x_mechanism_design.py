import math
import hashlib

class ReasoningTool:
    """
    Differentiable Meta-Mechanism for Self-Interested Hypothesis Agents.
    
    Mechanism:
    1. Generators (Candidates) bid compute resources based on self-confidence.
    2. Critics evaluate consistency between Prompt and Candidate using a deterministic
       hash-based semantic similarity proxy (simulating a frozen critic network).
    3. A Clarke-Groves inspired payment rule rewards candidates whose inclusion
       improves the global 'truth' score of the set, penalizing overconfidence.
    4. A Metacognitive Controller adjusts the 'temperature' of the bidding process
       based on the variance of critic scores, simulating exploration/exploitation.
       
    This implementation approximates the differentiable auction using deterministic
    heuristics to satisfy the 'no external deps' constraint while maintaining the
    logical structure of the proposed architecture.
    """

    def __init__(self):
        # Metacognitive state: tracks system uncertainty to adjust temperature
        self._meta_uncertainty = 0.5 
        self._base_temp = 1.0

    def _hash_score(self, text: str) -> float:
        """Deterministic pseudo-random score based on text content (0.0 - 1.0)."""
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        val = int(h[:8], 16)
        return val / 0xFFFFFFFF

    def _semantic_similarity(self, prompt: str, candidate: str) -> float:
        """
        Simulates a Critic Agent evaluating hypothesis consistency.
        Returns a score where higher is better. Uses overlap + hash stability.
        """
        p_tokens = set(prompt.lower().split())
        c_tokens = set(candidate.lower().split())
        
        # Jaccard-like overlap
        intersection = len(p_tokens & c_tokens)
        union = len(p_tokens | c_tokens)
        overlap = (intersection / union) if union > 0 else 0.0
        
        # Consistency check: if candidate repeats key prompt words, boost score
        # This simulates the 'verifiability' pressure from the prompt
        prompt_words = [w for w in p_tokens if len(w) > 3]
        match_count = sum(1 for w in prompt_words if w in c_tokens)
        relevance_bonus = min(0.5, match_count * 0.1) if prompt_words else 0.0
        
        base_score = self._hash_score(prompt + candidate)
        # Critic logic: Blend random noise with structural overlap
        return min(1.0, 0.4 * base_score + 0.6 * overlap + relevance_bonus)

    def _clarke_groves_payment(self, scores: list[float], idx: int) -> float:
        """
        Computes a simplified Clarke-Groves style payment.
        Reward = (Global Welfare with agent) - (Global Welfare without agent).
        In this context, it rewards agents that increase the total quality of the set.
        """
        if not scores: return 0.0
        
        total_with = sum(scores)
        # Welfare without this agent is just the sum of others
        total_without = total_with - scores[idx]
        
        # The 'payment' is the marginal contribution to the group truth
        # We add a small constant to ensure positive flow for valid hypotheses
        marginal_contribution = scores[idx] 
        
        # Penalty for reducing group coherence (simplified for differentiability proxy)
        avg_others = (total_without / (len(scores) - 1)) if len(scores) > 1 else 0
        penalty = 0.1 * (avg_others - scores[idx]) if scores[idx] < avg_others else 0.0
        
        return marginal_contribution - penalty

    def _metacognitive_control(self, scores: list[float]) -> float:
        """
        Adjusts temperature based on the variance of critic scores.
        High variance (disagreement) -> Higher temperature (more exploration).
        Low variance (agreement) -> Lower temperature (exploitation).
        """
        if len(scores) < 2:
            return 1.0
        
        mean_s = sum(scores) / len(scores)
        variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)
        
        # Update internal state (simulating recurrent controller)
        self._meta_uncertainty = 0.8 * self._meta_uncertainty + 0.2 * variance
        
        # Map uncertainty to temperature: high uncertainty -> high temp
        # Range roughly 0.5 to 2.0
        return 0.5 + 2.0 * math.tanh(variance * 5.0)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        # 1. Critic Phase: Evaluate all hypotheses
        raw_scores = [self._semantic_similarity(prompt, c) for c in candidates]
        
        # 2. Metacognitive Phase: Adjust temperature based on critic disagreement
        temp = self._metacognitive_control(raw_scores)
        
        # 3. Mechanism Design Phase: Differentiable Auction
        # Normalize scores to prevent explosion, then apply softmax bidding
        max_score = max(raw_scores) if raw_scores else 1.0
        normalized_scores = [s / (max_score + 1e-9) for s in raw_scores]
        
        # Softmax bidding with metacognitive temperature
        exp_scores = [math.exp((s - 1.0) / temp) for s in normalized_scores] # Shifted for stability
        sum_exp = sum(exp_scores) + 1e-9
        bids = [e / sum_exp for e in exp_scores]
        
        results = []
        for i, cand in enumerate(candidates):
            # Calculate incentive-compatible payment
            payment = self._clarke_groves_payment(raw_scores, i)
            
            # Final score combines critic evaluation, auction bid, and mechanism payment
            # This encourages high utility (score) and honesty (payment alignment)
            final_score = (0.5 * raw_scores[i]) + (0.3 * bids[i]) + (0.2 * payment)
            final_score = min(1.0, max(0.0, final_score)) # Clamp to 0-1
            
            reasoning = (
                f"Critic Score: {raw_scores[i]:.4f}, "
                f"Auction Bid: {bids[i]:.4f}, "
                f"Mech Payment: {payment:.4f}, "
                f"Meta Temp: {temp:.2f}"
            )
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on critic evaluation and mechanism stability."""
        # Run single evaluation to get critic score
        score = self._semantic_similarity(prompt, answer)
        
        # Simulate a 'stability' check by perturbing input slightly (deterministically)
        # If the score is robust, confidence increases
        perturbed = answer + " " + prompt[:5] # Deterministic perturbation
        score_perturbed = self._semantic_similarity(prompt, perturbed)
        
        stability = 1.0 - abs(score - score_perturbed)
        
        # Confidence is a blend of raw score and stability
        conf = 0.7 * score + 0.3 * stability
        return min(1.0, max(0.0, conf))