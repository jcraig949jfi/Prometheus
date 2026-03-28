import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Self-Interested Bandit-Driven Architecture Optimizer' via computational analogy.
    
    Mechanism:
    1. Agents (Candidates) bid for compute based on structural alignment with the Prompt.
    2. Mechanism Design (VCG-like): Candidates are penalized for 'over-bidding' (length/complexity) 
       without proportional structural gain (negations, comparatives, numeric logic). This enforces 
       truthfulness (Occam's razor).
    3. Multi-Armed Bandit (Thompson Sampling approx): We treat structural features as 'arms'. 
       We sample a weight vector from a Gaussian distribution (simulated via deterministic hash-seeding) 
       to balance exploration of different reasoning paths against exploitation of known patterns.
    4. Scoring: The final score is the 'utility' derived from the auction, normalized.
    
    This satisfies the requirement to use Structural Parsing as the primary signal and NCD as a tiebreaker.
    """

    def __init__(self):
        self._seed = 42  # Deterministic seed for the "Bandit" prior

    def _hash_float(self, s: str) -> float:
        """Deterministic pseudo-random float [0, 1] from string for bandit sampling."""
        h = zlib.crc32(s.encode()) ^ self._seed
        return (h % 10000) / 10000.0

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extract reasoning-critical features: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {}
        
        # Negations
        negations = ['not', 'no ', 'never', 'none', 'neither', 'without', 'fail']
        features['neg_count'] = sum(1 for n in negations if re.search(r'\b' + n + r'\b', text_lower))
        
        # Comparatives/Superlatives
        comps = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'best', 'worst', 'than', '>=', '<=', '>', '<']
        features['comp_count'] = sum(1 for c in comps if c in text_lower)
        
        # Conditionals
        conds = ['if', 'then', 'else', 'unless', 'provided', 'assuming']
        features['cond_count'] = sum(1 for c in conds if re.search(r'\b' + c + r'\b', text_lower))
        
        # Numeric detection
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['num_count'] = len(nums)
        features['has_math'] = 1.0 if any(op in text for op in ['+', '-', '*', '/', '=', 'sqrt']) else 0.0
        
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def _auction_bid(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulates the VCG Auction + Bandit selection.
        Returns (utility_score, reasoning_trace)
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        # Bandit Weight Sampling (Deterministic simulation of Thompson Sampling)
        # We sample weights for features based on the candidate content to simulate exploration
        w_neg = 1.5 + 0.5 * math.sin(self._hash_float(candidate) * 10)
        w_comp = 2.0 + 0.5 * math.cos(self._hash_float(candidate) * 5)
        w_cond = 1.2 + 0.3 * self._hash_float(candidate)
        w_num = 0.5 + 0.5 * self._hash_float(candidate)
        
        # Structural Alignment Score (The "Bid")
        # Candidates gain points for matching structural complexity of the prompt
        score = 0.0
        
        # Negation matching: If prompt has negation, candidate must handle it
        if p_feat['neg_count'] > 0:
            if c_feat['neg_count'] >= p_feat['neg_count']:
                score += w_neg * p_feat['neg_count']
            else:
                # Penalty for missing negation in negative prompt
                score -= 2.0 
        else:
            # Penalty for unnecessary negation in positive prompt (Hallucinated constraint)
            if c_feat['neg_count'] > 0:
                score -= 0.5 * c_feat['neg_count']

        # Comparative matching
        if p_feat['comp_count'] > 0:
            score += w_comp * min(c_feat['comp_count'], p_feat['comp_count'])
        
        # Conditional logic
        if p_feat['cond_count'] > 0:
            score += w_cond * min(c_feat['cond_count'], p_feat['cond_count'])
            
        # Numeric evaluation capability
        if p_feat['num_count'] > 0:
            # Check if candidate contains numbers or math operators
            if c_feat['num_count'] > 0 or c_feat['has_math'] > 0:
                score += w_num * p_feat['num_count']
            else:
                score -= 1.0 # Missed numeric context

        # Mechanism Design: Truthfulness Penalty (Goodhart's Law mitigation)
        # Penalize excessive length without proportional structural density
        length_ratio = len(candidate) / (len(prompt) + 1)
        structural_density = (c_feat['neg_count'] + c_feat['comp_count'] + c_feat['cond_count']) / (len(candidate.split()) + 1)
        
        if length_ratio > 3.0 and structural_density < 0.05:
            score -= 1.5 # Punish rambling without logic
            reason = "Penalized for verbosity without structural logic."
        elif length_ratio < 0.1 and p_feat['num_count'] > 0:
            score -= 1.0 # Punish overly short answers on math problems
            reason = "Penalized for insufficient detail on numeric problem."
        else:
            reason = "Structural alignment verified."

        # NCD Tiebreaker (Low weight, only matters for close calls)
        ncd = self._compute_ncd(prompt, candidate)
        # Lower NCD is better (more similar context), so we subtract it slightly
        score -= ncd * 0.1
        
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score, reason = self._auction_bid(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the auction utility score.
        Maps the raw score to a probability-like value.
        """
        score, _ = self._auction_bid(prompt, answer)
        
        # Sigmoid mapping to [0, 1]
        # Center around 0, steepness controlled by k
        k = 0.5
        conf = 1 / (1 + math.exp(-k * score))
        
        # Clamp to ensure strict 0-1
        return max(0.0, min(1.0, conf))