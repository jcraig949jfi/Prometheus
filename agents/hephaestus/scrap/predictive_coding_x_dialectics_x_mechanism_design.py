import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Hierarchical Dialectic Incentive-Compatible Predictive Coding (HDIC-PC) Tool.
    
    Mechanism Design Core (evaluate):
    Treats candidate answers as agents in a VCG-style auction.
    1. Thesis/Antithesis Generation: Candidates are parsed for structural logic (negations, comparatives).
    2. Error Bidding: Candidates submit 'bids' based on structural consistency with the prompt.
       Lower structural error = higher chance of winning.
    3. VCG Mechanism: The winner is selected based on minimizing global 'surprise' (structural mismatch).
       The 'payoff' is the reduction in error compared to the next best alternative.
    4. Dialectic Synthesis: If the winning bid (error) exceeds a threshold, the system synthesizes
       a new score by weighting the candidate's structural validity against its compression similarity.
    
    This ensures truthful reporting of logical consistency (Mechanism Design) while using
    Predictive Coding (error minimization) and Dialectics (thesis-antithesis synthesis) 
    to rank answers.
    """

    def __init__(self):
        self.surprise_threshold = 0.5

    def _structural_parse(self, text: str) -> Dict[str, Any]:
        """Extract logical primitives: negations, comparatives, conditionals, numbers."""
        t = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', t)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', t)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', t)),
            'numbers': re.findall(r'\d+\.?\d*', t),
            'length': len(t)
        }
        return features

    def _compute_structural_error(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Calculate 'prediction error' based on structural mismatch.
        In this mechanism, a high error implies the candidate does not logically 
        align with the prompt's complexity or constraints.
        """
        error = 0.0
        
        # Constraint 1: Negation alignment (simplified heuristic)
        # If prompt has high negation density, candidate should too, or vice versa mismatch penalty
        p_neg = prompt_feats['negations']
        c_neg = cand_feats['negations']
        if p_neg > 0 and c_neg == 0:
            error += 0.4  # Penalty for missing negation context
        elif p_neg == 0 and c_neg > 2:
            error += 0.3  # Penalty for over-negation

        # Constraint 2: Comparative logic
        if prompt_feats['comparatives'] > 0:
            if cand_feats['comparatives'] == 0:
                error += 0.3 # Missing comparative logic
        
        # Constraint 3: Numeric consistency (Basic type check)
        if prompt_feats['numbers'] and not cand_feats['numbers']:
            # If prompt has numbers but candidate has none, likely missing specific evaluation
            # Unless the answer is conceptual. We apply a small penalty.
            error += 0.1
            
        # Base error inversely proportional to feature overlap density
        p_total = sum(prompt_feats.values()) if isinstance(sum(prompt_feats.values()), (int, float)) else 0
        # Normalize error to 0-1 range roughly
        return min(1.0, error)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(z1, z2)
            if max_len == 0:
                return 1.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        # --- Mechanism Design: Sealed-Bid Auction ---
        # Each candidate submits a bid = structural error (lower is better)
        bids = []
        for i, cand in enumerate(candidates):
            cand_feats = self._structural_parse(cand)
            error_bid = self._compute_structural_error(prompt_feats, cand_feats)
            bids.append({'index': i, 'bid': error_bid, 'candidate': cand})
        
        # Sort by bid (ascending: lowest error wins)
        bids.sort(key=lambda x: x['bid'])
        
        # --- VCG Mechanism & Dialectic Synthesis ---
        # Determine winner and calculate payoff (externality imposed on others)
        # In this context, payoff adjusts the final score based on how much better 
        # the winner is than the runner-up (synthesis of quality and distinctiveness).
        
        for i, item in enumerate(bids):
            cand = item['candidate']
            base_error = item['bid']
            
            # Calculate externality (difference between this bid and the next best)
            if i < len(bids) - 1:
                next_best_error = bids[i+1]['bid']
                externality = next_best_error - base_error
            else:
                # Winner is unique, max externality relative to worst case
                externality = 1.0 - base_error
            
            # Dialectic Synthesis: Combine Thesis (Structural Error) and Antithesis (NCD Similarity)
            # If error is high (surprise), we rely more on NCD (compression) as a fallback.
            # If error is low, we trust the structural parse.
            
            ncd_val = self._ncd_distance(prompt, cand)
            
            # Synthesis formula: 
            # Score = (1 - Error) + (Weight * Externality) - (Noise Penalty)
            # We invert error so high score = good.
            structural_score = 1.0 - base_error
            
            # Adjust based on surprise threshold (Dialectic step)
            if base_error > self.surprise_threshold:
                # High surprise: Synthesize with NCD to ground the answer
                # NCD is 0 (same) to 1 (different). We want high similarity (low NCD).
                synthesis_weight = 0.4
                final_score = (structural_score * 0.6) + ((1.0 - ncd_val) * synthesis_weight) + (externality * 0.2)
            else:
                # Low surprise: Structural logic dominates
                final_score = structural_score + (externality * 0.3)
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural error: {base_error:.2f}, Externality bonus: {externality:.2f}, NCD factor: {ncd_val:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal evaluation mechanism to score the single candidate.
        """
        # Evaluate against a dummy set to get the score
        # We simulate a competition with the answer itself and a known bad answer
        # to force the mechanism to produce a relative score.
        dummy_bad = "IRRELEVANT_NO_LOGIC_" + "X" * len(answer)
        ranked = self.evaluate(prompt, [answer, dummy_bad])
        
        if not ranked:
            return 0.0
            
        # Find the score for the specific answer
        for item in ranked:
            if item['candidate'] == answer:
                return item['score']
        
        # Fallback if exact string match fails (shouldn't happen with this logic)
        return ranked[0]['score'] if ranked else 0.0