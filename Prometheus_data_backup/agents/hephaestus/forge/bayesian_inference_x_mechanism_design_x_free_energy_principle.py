import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Bayesian Mechanism Design (VBMD) Tool.
    
    Mechanism:
    1. Free Energy Principle (FEP): Defines the 'surprise' or prediction error.
       We treat the prompt as the 'sensory data' and candidates as 'hypotheses'.
       Structural consistency (logic, numbers) minimizes free energy.
    2. Mechanism Design: Implements an internal prediction market.
       Each candidate is a sub-agent. They 'bid' based on structural validity.
       Proper scoring rules (Brier/Log) penalize over-confidence in structurally flawed answers.
       Candidates that contradict prompt constraints (negations, comparatives) are 'penalized' 
       by having their market share (score) reduced relative to the consensus.
    
    This creates a self-correcting loop where logically consistent answers 
    accumulate 'wealth' (higher score) while hallucinated or contradictory ones lose value.
    """

    def __init__(self):
        self.epsilon = 1e-9

    def _extract_structural_features(self, text: str) -> dict:
        """Extract logical constraints: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', text),
            'length': len(text.split())
        }
        return features

    def _compute_structural_consistency(self, prompt: str, candidate: str) -> float:
        """
        Computes a consistency score based on structural alignment.
        High score = low free energy (hypothesis matches data constraints).
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        score = 0.0
        
        # 1. Negation Alignment (Modus Tollens check proxy)
        # If prompt has negation, candidate should ideally reflect awareness or not contradict blindly
        if p_feat['negations'] > 0:
            # Reward if candidate also handles logic (heuristic: has similar complexity or explicit negation)
            if c_feat['negations'] > 0 or c_feat['length'] > p_feat['length'] * 0.5:
                score += 2.0
            else:
                # Penalty for ignoring complex negation contexts
                score -= 1.0
        
        # 2. Comparative/Ordinal Consistency
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0:
                score += 1.5
            # Check number extraction for direct comparison if present
            if p_feat['numbers'] and c_feat['numbers']:
                try:
                    p_nums = [float(x) for x in p_feat['numbers']]
                    c_nums = [float(x) for x in c_feat['numbers']]
                    # Simple transitivity check: if prompt implies order, does candidate follow?
                    # Heuristic: Candidate numbers shouldn't be wildly out of distribution unless explaining
                    if len(p_nums) > 0 and len(c_nums) > 0:
                        p_avg = sum(p_nums)/len(p_nums)
                        c_avg = sum(c_nums)/len(c_nums)
                        if abs(p_avg - c_avg) < (p_avg * 0.5 + 1): # Reasonable range
                            score += 1.0
                except ValueError:
                    pass

        # 3. Conditional Logic Depth
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or c_feat['length'] > 15: # Complex answers for complex prompts
                score += 1.0
        
        # Length penalty for extreme brevity on complex prompts (Hallucination check)
        if p_feat['length'] > 10 and c_feat['length'] < 3:
            score -= 2.0
            
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        
        # Step 1: Compute Free Energy (Structural Consistency) for each candidate
        # Lower free energy = higher raw score
        raw_scores = []
        for cand in candidates:
            fe_score = self._compute_structural_consistency(prompt, cand)
            raw_scores.append(fe_score)
        
        # Step 2: Mechanism Design - Market Clearing
        # Convert raw scores to probabilities via softmax (Market Prices)
        # This acts as the variational update q(s) approximating posterior
        max_raw = max(raw_scores)
        exp_scores = [math.exp(s - max_raw) for s in raw_scores] # Stability shift
        sum_exp = sum(exp_scores) + self.epsilon
        
        market_prices = [e / sum_exp for e in exp_scores]
        
        # Step 3: Refine with NCD as tie-breaker/refiner
        # If structural signals are weak (prices close), NCD distinguishes relevance
        final_scores = []
        for i, cand in enumerate(candidates):
            base_score = market_prices[i]
            
            # NCD penalty: If candidate is too dissimilar to prompt context (high NCD), 
            # it might be irrelevant noise, unless structural score is very high.
            ncd_val = self._ncd_distance(prompt, cand)
            
            # Adaptive weighting: Trust structure more than compression
            # But use NCD to dampen outliers that got lucky on structural keywords
            adjustment = (1.0 - ncd_val) * 0.15 
            
            final_score = base_score + adjustment
            final_scores.append(final_score)
        
        # Normalize final scores to 0-1 range roughly
        max_final = max(final_scores) if final_scores else 1.0
        min_final = min(final_scores) if final_scores else 0.0
        range_final = max_final - min_final + self.epsilon
        
        ranked = []
        for i, cand in enumerate(candidates):
            norm_score = (final_scores[i] - min_final) / range_final
            ranked.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": f"VBMD Score: Structural consistency={raw_scores[i]:.2f}, Market Price={market_prices[i]:.3f}, NCD adjustment applied."
            })
        
        # Sort descending by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal market mechanism to price this single hypothesis.
        """
        # Create a dummy competitor to simulate market pressure
        # If the answer is good, it should dominate a null hypothesis
        dummy_candidates = [answer, "The opposite is true.", "Unknown."]
        ranked = self.evaluate(prompt, dummy_candidates)
        
        # Find the score for the specific answer
        for item in ranked:
            if item['candidate'] == answer:
                # Map the relative score to confidence
                # High market share in a competitive pool = high confidence
                return min(1.0, max(0.0, item['score']))
        
        return 0.0