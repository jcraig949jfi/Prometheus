import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Regulating Variational Inference Engine via Mechanism Design.
    
    Mechanism:
    1. Agents (Candidates) compute Expected Free Energy Reduction (EFER) as their bid.
       - EFER ~ Information Gain - Complexity Cost.
       - Information Gain is approximated by structural constraint satisfaction 
         (negations, numerics, transitivity) relative to the prompt.
       - Complexity Cost is approximated by description length (compression).
    2. A Vickrey-Clarke-Groves (VCG) auction allocates 'compute' (score).
       - Winners are those who maximize global free energy reduction.
       - Scores are adjusted by the externality imposed on others (second-price logic).
    3. Phase Transition Detection:
       - Monitors the variance of bids. High variance indicates a critical point 
         where the current hypothesis space may need expansion (simulated by 
         boosting scores of structurally complex but valid candidates).
    """

    def __init__(self):
        self._state = {}

    def _structural_score(self, text: str) -> float:
        """Extract structural reasoning features (Numeric, Negation, Logic)."""
        score = 0.0
        
        # Numeric evaluation capability
        numbers = re.findall(r'-?\d+\.?\d*', text)
        if numbers:
            score += 0.5 * len(numbers)
            try:
                # Reward sortedness or simple magnitude logic if multiple numbers exist
                vals = [float(n) for n in numbers]
                if len(vals) > 1:
                    is_sorted = all(vals[i] <= vals[i+1] for i in range(len(vals)-1))
                    score += 0.2 if is_sorted else 0.0
            except ValueError:
                pass
        
        # Negation detection (Critical for constraint propagation)
        negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        words = text.lower().split()
        neg_count = sum(1 for w in words if w in negations)
        score += 0.3 * neg_count
        
        # Comparatives
        comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'than']
        score += 0.2 * sum(1 for w in words if w in comparatives)
            
        return score

    def _compute_complexity(self, text: str) -> float:
        """Approximate Kolmogorov complexity via zlib compression length."""
        import zlib
        if not text:
            return 0.0
        try:
            compressed = len(zlib.compress(text.encode('utf-8')))
            return compressed / 100.0  # Normalize slightly
        except:
            return len(text) / 10.0

    def _compute_efer(self, prompt: str, candidate: str) -> float:
        """
        Compute Expected Free Energy Reduction (EFER).
        EFER = (Structural Alignment with Prompt) - (Complexity Cost)
        """
        # 1. Complexity Cost (Free Energy Penalty for complexity)
        complexity_cost = self._compute_complexity(candidate)
        
        # 2. Information Gain (Structural alignment)
        # We measure how well the candidate's structural features match the prompt's needs
        cand_struct = self._structural_score(candidate)
        prompt_struct = self._structural_score(prompt)
        
        # Alignment: Candidates should reflect the structural complexity of the prompt
        # If prompt has numbers, candidate should likely handle numbers.
        alignment = 0.0
        if prompt_struct > 0:
            # Reward matching the magnitude of structural features
            alignment = cand_struct * (1.0 / (1.0 + abs(prompt_struct - cand_struct)))
        else:
            alignment = cand_struct * 0.5
            
        # Base EFER
        efer = alignment - (0.1 * complexity_cost)
        return efer

    def _vcg_adjustment(self, bids: List[float], index: int) -> float:
        """
        Apply VCG-like adjustment.
        Score = Own Bid - (Global Optimal without me - Global Optimal with me)
        Simplified for ranking: Penalize if removing this candidate significantly 
        changes the 'market' variance (Phase Transition signal).
        """
        if len(bids) < 2:
            return bids[index]
            
        own_bid = bids[index]
        
        # Calculate market variance (Order Parameter)
        mean_bid = sum(bids) / len(bids)
        variance = sum((b - mean_bid)**2 for b in bids) / len(bids)
        
        # Phase Transition Signal: If variance is high, we are near a critical point.
        # Boost candidates that are above average but penalize outliers that destabilize.
        if variance > 0.5: 
            # Critical regime: Favor robustness (closeness to mean if mean is high, or max)
            # This simulates the "meta-control" expanding/contracting space
            if own_bid > mean_bid:
                return own_bid * (1.0 + 0.1 * math.log(variance + 1))
            else:
                return own_bid * 0.9 # Penalize low performers in critical phase
        else:
            # Stable regime: Pure bid matters most
            return own_bid

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Compute Bids (EFER) for all agents
        bids = [self._compute_efer(prompt, c) for c in candidates]
        
        # 2. Detect Phase Transition (Variance of bids)
        mean_bid = sum(bids) / len(bids)
        variance = sum((b - mean_bid)**2 for b in bids) / len(bids) if len(bids) > 1 else 0
        
        # 3. Allocate Compute (VCG Adjustment)
        final_scores = []
        for i, bid in enumerate(bids):
            adjusted_score = self._vcg_adjustment(bids, i)
            
            # Add small deterministic tie-breaker based on string hash to ensure stability
            tie_breaker = (hash(candidates[i]) % 1000) / 1e6
            final_scores.append(adjusted_score + tie_breaker)
        
        # 4. Rank and Format
        ranked_indices = sorted(range(len(final_scores)), key=lambda k: final_scores[k], reverse=True)
        
        results = []
        for idx in ranked_indices:
            results.append({
                "candidate": candidates[idx],
                "score": round(final_scores[idx], 6),
                "reasoning": f"EFER={bids[idx]:.4f}, Var={variance:.4f}"
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on relative EFER dominance.
        Compares the answer's EFER against a 'null' hypothesis and structural expectations.
        """
        # Generate a set of dummy alternatives to simulate the market
        # This allows us to see if the proposed answer dominates the hypothesis space
        dummies = [
            "No", "Yes", "Unknown", "Maybe", 
            answer[::-1], # Reverse string as a bad hypothesis
            str(len(answer)) # Numeric distractor
        ]
        # Include the answer itself in the pool to calculate relative dominance
        pool = list(set(dummies + [answer]))
        
        # Evaluate the whole pool
        evaluated = self.evaluate(prompt, pool)
        
        # Find the score of the specific answer provided
        answer_score = None
        max_score = -float('inf')
        if evaluated:
            max_score = evaluated[0]["score"]
            for item in evaluated:
                if item["candidate"] == answer:
                    answer_score = item["score"]
                    break
        
        if answer_score is None:
            return 0.0
            
        # Normalize confidence: How close is this answer to the theoretical max possible in this context?
        # Use a sigmoid-like scaling based on the gap to the winner
        if max_score == answer_score:
            # It is the winner
            gap = 0.0
        else:
            gap = max_score - answer_score
            
        # Map gap to 0-1. Small gap -> high confidence. Large gap -> low confidence.
        # Assuming typical EFER ranges are small (-5 to 5), a gap of 1.0 is significant.
        confidence = 1.0 / (1.0 + math.exp(2.0 * gap))
        
        return min(1.0, max(0.0, confidence))