import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Measure-Theoretic Information-Directed Bandit (MIB) Reasoning Tool.
    
    Mechanism:
    1. Hypothesis Space (Theta): Treats candidates as hypotheses.
    2. Measure (Mu): Constructs a discrete probability measure over candidates based on 
       structural alignment with the prompt (negations, comparatives, numeric consistency).
    3. Information Gain (I): Estimates mutual information by measuring how well a candidate 
       reduces the "uncertainty" (entropy) of the prompt's constraints.
    4. Bandit Selection: Ranks candidates by maximizing the ratio of Information Gain to 
       Variance (complexity penalty), simulating the Information-Directed Sampling rule.
    5. NCD Tiebreaker: Uses Normalized Compression Distance only when structural scores are identical.
    """

    def __init__(self):
        self._struct_keywords = {
            'negations': ['not', 'no', 'never', 'none', 'cannot', "n't"],
            'comparatives': ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'],
            'conditionals': ['if', 'then', 'unless', 'otherwise', 'provided'],
            'logic_ops': ['and', 'or', 'but', 'however', 'therefore']
        }

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text for numeric evaluation."""
        pattern = r'-?\d+(?:\.\d+)?'
        try:
            return [float(x) for x in re.findall(pattern, text)]
        except ValueError:
            return []

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a structural alignment score based on logic patterns.
        Higher score = better structural fit.
        """
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect it or not contradict
        p_neg = any(k in p_low for k in self._struct_keywords['negations'])
        c_neg = any(k in c_low for k in self._struct_keywords['negations'])
        if p_neg == c_neg:
            score += 2.0
        elif p_neg and not c_neg:
            score -= 5.0 # Penalty for ignoring negation
        
        # 2. Comparative Presence
        has_comp = any(k in p_low for k in self._struct_keywords['comparatives'])
        if has_comp:
            if any(k in c_low for k in self._struct_keywords['comparatives']):
                score += 1.5
            # Check if numbers exist in both (proxy for comparative reasoning)
            p_nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(candidate)
            if p_nums and c_nums:
                score += 1.0

        # 3. Conditional/Logic Overlap
        logic_overlap = 0
        for k in self._struct_keywords['logic_ops'] + self._struct_keywords['conditionals']:
            if k in p_low and k in c_low:
                logic_overlap += 1
        score += logic_overlap * 0.5

        # 4. Numeric Consistency (Simple transitivity check)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        if p_nums and c_nums:
            # If prompt implies an order (e.g., 5 > 3) and candidate respects it
            # Here we just check if candidate numbers are a subset or derived, 
            # simplistic approach: reward if candidate numbers appear in prompt
            if any(abs(n - c_nums[0]) < 1e-6 for n in p_nums) if c_nums else False:
                score += 2.0
        
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            numerator = z12 - min(z1, z2)
            denominator = max(z1, z2)
            if denominator == 0:
                return 0.0
            return numerator / denominator
        except Exception:
            return 1.0

    def _estimate_information_gain(self, prompt: str, candidate: str) -> float:
        """
        Estimate I(H; O_a | mu).
        Analogy: Information gain is high if the candidate specifically addresses 
        the structural constraints (logic/numbers) of the prompt.
        """
        struct_score = self._structural_score(prompt, candidate)
        
        # Entropy reduction proxy: 
        # If structural score is high, the "uncertainty" about whether this candidate 
        # is the correct hypothesis decreases significantly.
        # We map structural score to an information gain metric.
        # Base gain + bonus for structural alignment
        base_gain = 0.1
        if struct_score > 0:
            return base_gain + (struct_score * 0.5)
        return base_gain - 0.2

    def _estimate_variance(self, candidate: str) -> float:
        """
        Estimate Var[Delta mu_a].
        Analogy: Variance is proportional to the complexity/length of the candidate.
        Longer, more complex answers have higher variance in their posterior update 
        (more ways to be wrong). We penalize excessive length/complexity.
        """
        length = len(candidate)
        # Simple variance proxy: log-length normalized
        return math.log(length + 2) * 0.1

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Pre-calculate prompt structural features to ensure consistency
        prompt_nums = self._extract_numbers(prompt)
        
        for cand in candidates:
            # 1. Calculate Information Gain (Reward)
            info_gain = self._estimate_information_gain(prompt, cand)
            
            # 2. Calculate Variance (Cost/Risk)
            variance = self._estimate_variance(cand)
            
            # 3. MIB Ratio: I^2 / Var (from Russo & Van Roy adaptation)
            # Avoid division by zero
            safe_var = max(variance, 1e-6)
            mib_score = (info_gain ** 2) / safe_var
            
            # Add small NCD component only as a tiny tiebreaker influence initially,
            # but primarily rely on the structural score for the main ranking logic
            struct_score = self._structural_score(prompt, cand)
            
            # Final score combines MIB ratio with direct structural penalty/reward
            final_score = mib_score + (struct_score * 0.5)
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"MIB Score: {mib_score:.4f}, Structural: {struct_score:.2f}, InfoGain: {info_gain:.4f}"
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Refine scores using NCD as a strict tiebreaker for top candidates if needed
        # In this implementation, we adjust the score slightly if NCD indicates 
        # the candidate is just a copy-paste (low NCD) vs reasoned.
        # However, per instructions, NCD is a tiebreaker. 
        # We apply a final pass: if scores are within 1% threshold, use NCD.
        
        if len(scored_candidates) > 1:
            threshold = 0.01 * max(1.0, scored_candidates[0]["score"])
            i = 0
            while i < len(scored_candidates) - 1:
                j = i + 1
                # Check cluster of similar scores
                while j < len(scored_candidates) and abs(scored_candidates[j]["score"] - scored_candidates[i]["score"]) < threshold:
                    j += 1
                
                if j > i + 1:
                    # Tie detected in this range [i, j), use NCD to sort
                    cluster = scored_candidates[i:j]
                    # Sort cluster by NCD distance to prompt (prefer distinct but relevant? 
                    # Actually, for reasoning, we often prefer the one that compresses well WITH the prompt
                    # implying shared structure, but NCD low means similar. 
                    # Let's use NCD to break ties by preferring lower NCD (higher similarity) 
                    # as a heuristic for "answering the prompt directly".
                    cluster.sort(key=lambda x: self._compute_ncd(prompt, x["candidate"]))
                    scored_candidates[i:j] = cluster
                i = j

        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Based on the normalized MIB score of the specific answer against the prompt.
        """
        # Evaluate single candidate against itself to get its raw score
        # We need a baseline to normalize. Let's create a dummy set.
        # Since we can't generate alternatives, we assess the absolute quality 
        # of the structural match.
        
        struct_score = self._structural_score(prompt, answer)
        info_gain = self._estimate_information_gain(prompt, answer)
        variance = self._estimate_variance(answer)
        
        if variance == 0:
            variance = 1e-6
            
        raw_score = (info_gain ** 2) / variance + (struct_score * 0.5)
        
        # Map raw score to 0-1 using a sigmoid-like function
        # Assuming typical scores range from -2 to 10
        # Center around 2.0, scale by 2.0
        normalized = 1 / (1 + math.exp(-(raw_score - 2.0) / 2.0))
        
        return max(0.0, min(1.0, normalized))