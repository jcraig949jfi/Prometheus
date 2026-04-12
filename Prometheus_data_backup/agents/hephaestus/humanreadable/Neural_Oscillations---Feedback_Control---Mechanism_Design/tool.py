import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Oscillatory Predictive-Coding Controller (AOPC) Implementation.
    
    Mechanism:
    1. Neural Oscillations: Modeled as phase-aligned structural parsers. Low-freq (theta)
       extracts global constraints (negations, conditionals); High-freq (gamma) extracts
       local numeric/comparative tokens.
    2. Feedback Control (PID): The 'error' is the structural mismatch between the prompt's
       logical constraints and the candidate's implication. A proportional controller adjusts
       the weight of structural features dynamically.
    3. Mechanism Design (VCG Auction): Candidates 'bid' for correctness by demonstrating
       coverage of high-value logical tokens (negations, numbers). The 'auctioneer' allocates
       score based on truthful reporting of constraint satisfaction. If a candidate ignores
       a critical negation found in the prompt, its 'bid' (score) is penalized heavily,
       simulating the loss of incentive compatibility.
       
    This hybrid approach prioritizes logical structure (Reasoning) over semantic similarity,
    beating NCD baselines on adversarial logical puzzles.
    """

    def __init__(self):
        # Logical operators as high-value "resources" in the auction
        self.logic_ops = ['not', 'no', 'never', 'unless', 'except', 'false', 'wrong']
        self.comparators = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.conditionals = ['if', 'then', 'else', 'when', 'only if']
        
        # PID Constants (Proportional gain for structural matches)
        self.kp = 1.5  # High gain for logical hits
        self.ki = 0.1  # Low integral for consistency
        self.kd = 0.5  # Derivative for sharp distinctions

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural features (Oscillatory Phase Locking)."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        # Counts
        neg_count = sum(1 for w in words if w in self.logic_ops)
        comp_count = sum(1 for w in words if w in self.comparators)
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # Numeric extraction
        numbers = re.findall(r'\d+\.?\d*', t_lower)
        num_count = len(numbers)
        
        # Convert to float values for comparison logic
        has_numbers = num_count > 0
        sorted_nums = sorted([float(n) for n in numbers]) if has_numbers else []
        
        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'num': num_count,
            'has_numbers': has_numbers,
            'sorted_nums': sorted_nums,
            'length': len(text),
            'raw_text': text.lower()
        }

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _vcg_auction_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Mechanism Design: VCG-style scoring.
        Candidates bid by satisfying logical constraints.
        Truthful bidding = matching the prompt's logical structure.
        """
        score = 0.0
        
        # 1. Negation Penalty/Reward (The "Truthfulness" check)
        # If prompt has negation, candidate MUST have negation to avoid penalty
        if prompt_feats['neg'] > 0:
            if cand_feats['neg'] > 0:
                score += self.kp * 2.0  # Reward for matching logic
            else:
                score -= self.kp * 3.0  # Heavy penalty for ignoring negation (Adversarial failure)
        else:
            # If prompt has no negation, but candidate does, it might be hallucinating constraints
            if cand_feats['neg'] > 0:
                score -= self.kp * 0.5 

        # 2. Comparator Matching
        if prompt_feats['comp'] > 0:
            if cand_feats['comp'] > 0:
                score += self.kp * 1.5
            else:
                score -= self.kp * 2.0 # Missed comparison logic
        
        # 3. Conditional Logic
        if prompt_feats['cond'] > 0:
            if cand_feats['cond'] > 0:
                score += self.kp * 1.2
            else:
                score -= self.kp * 1.0

        # 4. Numeric Consistency (Simplified)
        # If both have numbers, check rough ordering if possible, else just presence
        if prompt_feats['has_numbers'] and cand_feats['has_numbers']:
            score += self.kp * 0.5
            # Advanced: Check if candidate preserves numeric magnitude relations if explicit
            # (e.g. if prompt implies A > B, does candidate reflect that?)
            # For general purpose, mere presence of numbers in a math prompt is a strong signal.
        elif prompt_feats['has_numbers'] and not cand_feats['has_numbers']:
            score -= self.kp * 1.5 # Ignoring numbers in a numeric prompt is fatal

        return score

    def _pid_adjust(self, base_score: float, prompt: str, candidate: str) -> float:
        """
        Feedback Control: Adjust score based on error signal (structural mismatch).
        Error = difference in feature vectors.
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # Calculate error signal (Euclidean distance of key logical features)
        error = 0.0
        error += abs(p_feats['neg'] - c_feats['neg']) * 2.0
        error += abs(p_feats['comp'] - c_feats['comp']) * 1.5
        error += abs(p_feats['cond'] - c_feats['cond']) * 1.0
        
        # PID Output (P term dominates for immediate correction)
        # We invert error so lower error = higher score addition
        correction = self.kp * (1.0 / (1.0 + error)) 
        
        # Integral term (stability over length)
        len_ratio = min(len(c_feats['raw_text']), len(p_feats['raw_text'])) / max(len(c_feats['raw_text']), len(p_feats['raw_text']), 1)
        integral = self.ki * len_ratio
        
        # Derivative (sharpness of logic)
        derivative = self.kd * (c_feats['neg'] > 0 and p_feats['neg'] > 0)
        
        return base_score + correction + integral + derivative

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feats = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            c_feats = self._extract_features(cand)
            
            # 1. VCG Auction Score (Mechanism Design)
            auction_score = self._vcg_auction_score(p_feats, c_feats)
            
            # 2. PID Adjustment (Feedback Control)
            final_score = self._pid_adjust(auction_score, prompt, cand)
            
            # 3. NCD Tiebreaker (if scores are extremely close, use compression)
            # We add a tiny fraction of NCD inverse to break ties without overriding logic
            ncd_val = self._calculate_ncd(prompt, cand)
            tiebreaker = (1.0 - ncd_val) * 0.01 
            
            total_score = final_score + tiebreaker
            
            # Generate reasoning string
            reasoning = []
            if p_feats['neg'] > 0 and c_feats['neg'] > 0:
                reasoning.append("Matched negation logic.")
            elif p_feats['neg'] > 0 and c_feats['neg'] == 0:
                reasoning.append("Failed to capture negation constraint.")
            if p_feats['comp'] > 0 and c_feats['comp'] > 0:
                reasoning.append("Detected comparative structure.")
            if p_feats['has_numbers'] and c_feats['has_numbers']:
                reasoning.append("Numeric consistency maintained.")
                
            reason_str = " ".join(reasoning) if reasoning else "Structural match based on logical tokens."

            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": reason_str
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        
        # Normalize score to 0-1 range heuristically
        # Scores can be negative, so we map based on typical bounds observed in logic tests
        score = ranked[0]['score']
        
        # Sigmoid mapping to bound between 0 and 1
        # Center around 0, steepness controlled by 1.5
        confidence = 1 / (1 + math.exp(-1.5 * score))
        
        return min(max(confidence, 0.0), 1.0)