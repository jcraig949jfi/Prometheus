import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A resource-constrained active-inference planner using Mechanism Design.
    
    Mechanism:
    1. Structural Parsing (FEP Priors): Extracts logical constraints (negations, comparatives, 
       conditionals) to form a 'generative model' of the prompt's requirements.
    2. Hypothesis Generation: Treats candidates as hypotheses proposing to explain the prompt.
    3. VCG Auction (Mechanism Design): 
       - Candidates 'bid' for limited working memory slots.
       - Bid Value = (Structural Match Score) - (Complexity Cost).
       - Complexity Cost penalizes verbosity and lack of precision (intrinsic load).
       - The 'auction' selects candidates that maximize germane load (useful signal) while 
         respecting the cognitive budget.
    4. Scoring: Final score is the normalized auction value, ensuring only structurally 
       sound and concise answers rise to the top.
    """

    def __init__(self):
        # Working memory budget (Cognitive Load Theory limit)
        self.wm_capacity = 4.0 
        # Keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical signatures: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in lower_text for n in self.negations)
        has_comparative = any(c in lower_text for c in self.comparatives)
        has_conditional = any(c in lower_text for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r"-?\d+\.?\d*", lower_text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'word_count': len(words),
            'char_count': len(text)
        }

    def _compute_structural_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Computes the 'Germane Load' (useful learning) by matching structural features.
        High score = Candidate respects the logical constraints of the prompt.
        """
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect it or not contradict it.
        # Simplified: Presence match boosts score, absence is neutral.
        if prompt_struct['negation']:
            score += 2.0 if cand_struct['negation'] else 0.5
        else:
            # Penalty if candidate introduces unnecessary negation when prompt didn't have it
            score += 1.0 if not cand_struct['negation'] else -1.0

        # 2. Comparative Consistency
        if prompt_struct['comparative']:
            score += 2.0 if cand_struct['comparative'] else 0.0
        else:
            score += 1.0 if not cand_struct['comparative'] else -0.5

        # 3. Conditional Consistency
        if prompt_struct['conditional']:
            score += 2.0 if cand_struct['conditional'] else 0.0
        else:
            score += 1.0 if not cand_struct['conditional'] else -0.5

        # 4. Numeric Evaluation (Simple transitivity check)
        # If both have numbers, check if candidate numbers are 'reasonable' relative to prompt
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if p_nums and c_nums:
            # Heuristic: If prompt implies an order (e.g., 9.11 vs 9.9), 
            # candidate should ideally reflect the correct magnitude if it's a direct answer.
            # Since we don't know the question type, we reward numeric presence in numeric contexts.
            score += 1.5
            # Specific check: If prompt has 2 numbers and candidate has 1, check magnitude?
            # Too risky without semantic understanding. Stick to structural presence.
        elif p_nums and not c_nums:
            # Prompt asks for math/numbers, candidate gives text -> Penalty
            score -= 2.0

        return score

    def _calculate_complexity_cost(self, cand_struct: Dict) -> float:
        """
        Calculates intrinsic cognitive load.
        Longer, more complex answers cost more 'tokens'.
        """
        # Base cost proportional to length
        length_cost = cand_struct['char_count'] / 50.0 
        return length_cost

    def _vcg_auction(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float, str]]:
        """
        Runs a VCG-style auction where hypotheses bid for memory slots.
        Bid = (Structural Match) - (Complexity Cost).
        Incentive compatible: Truthful representation of structural fit maximizes utility.
        """
        p_struct = self._parse_structure(prompt)
        results = []
        
        for cand in candidates:
            c_struct = self._parse_structure(cand)
            
            # Calculate Value (Germane Load)
            structural_value = self._compute_structural_score(p_struct, c_struct)
            
            # Calculate Cost (Intrinsic Load)
            complexity_cost = self._calculate_complexity_cost(c_struct)
            
            # Bid = Value - Cost
            bid = structural_value - complexity_cost
            
            reasoning = (
                f"Structural Match: {structural_value:.2f}, "
                f"Complexity Cost: {complexity_cost:.2f}, "
                f"Net Bid: {bid:.2f}"
            )
            results.append((cand, bid, reasoning))
            
        # Sort by bid (descending) - The 'winners' of the auction
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_both = len(zlib.compress((s1 + s2).encode()))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_both - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Run the Mechanism Design / Active Inference Loop
        auction_results = self._vcg_auction(prompt, candidates)
        
        # Normalize scores to 0-1 range for the final output
        # We use a soft-max like normalization or simple min-max scaling on the bids
        bids = [r[1] for r in auction_results]
        min_bid = min(bids)
        max_bid = max(bids)
        range_bid = max_bid - min_bid if max_bid != min_bid else 1.0
        
        final_results = []
        
        # Group by score to apply NCD tie-breaking
        # Since auction results are sorted, we can process sequentially
        for i, (cand, bid, reason) in enumerate(auction_results):
            # Normalize bid to 0.2 - 0.9 range to leave room for NCD adjustments
            norm_score = 0.2 + (0.7 * (bid - min_bid) / range_bid)
            
            # Apply NCD as a subtle tie-breaker or booster for high similarity
            # Only if the structural score is very close to another candidate
            is_tie = False
            if i < len(auction_results) - 1:
                next_bid = auction_results[i+1][1]
                if abs(bid - next_bid) < 0.1: # Threshold for 'tie' in auction
                    is_tie = True
            
            if is_tie:
                # Boost score slightly if NCD to prompt is low (similar content)
                # But be careful: sometimes the answer is short ("No") and prompt is long.
                # Instead, use NCD between candidate and the "ideal" structural features?
                # Simpler: Use NCD between candidate and prompt as a relevance proxy for ties.
                ncd_val = self._ncd(prompt, cand)
                # Lower NCD is better. Convert to boost.
                boost = (1.0 - ncd_val) * 0.05 
                norm_score += boost
                reason += f" [NCD Tiebreak: {ncd_val:.2f}]"

            # Clamp score
            norm_score = max(0.0, min(1.0, norm_score))
            
            final_results.append({
                "candidate": cand,
                "score": round(norm_score, 4),
                "reasoning": reason
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the auction bid of the single candidate.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']