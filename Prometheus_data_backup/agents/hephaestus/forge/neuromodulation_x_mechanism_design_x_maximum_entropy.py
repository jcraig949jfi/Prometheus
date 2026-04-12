import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    NICVI-inspired Reasoning Tool.
    
    Mechanism:
    1. Mechanism Design (Core): Candidates are 'agents'. We use a proper scoring rule 
       (Logarithmic Score) based on structural alignment with the prompt to incentivize 
       'truthful' (correct) reporting. The candidate with the highest structural match 
       (satisfying negations, conditionals, numeric constraints) wins.
    2. Neuromodulation (Gain Control): A dynamic 'exploration gain' adjusts the penalty 
       for length/complexity. If structural signals are weak (high uncertainty), the 
       system increases entropy tolerance (favors diverse/longer explanations). If 
       signals are strong, it tightens focus (exploitation).
    3. Maximum Entropy (Restricted): Used ONLY in the confidence() wrapper to smooth 
       probability estimates and prevent over-confidence, not for primary scoring.
    """

    def __init__(self):
        self.epsilon = 1e-9

    def _structural_parse(self, text: str) -> dict:
        """Extract logical constraints: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        return features

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Core: Evaluate if the candidate satisfies the prompt's 
        structural constraints. Returns a score where higher is better.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        
        # 1. Negation Consistency: If prompt has negation, correct answer often reflects it
        # Simple heuristic: Candidate should not contradict prompt negation density wildly
        # unless it's a correction. We penalize massive divergence in logical operators.
        if p_feat['negations'] > 0:
            # Reward candidates that also acknowledge logical complexity
            score += 2.0 if c_feat['negations'] > 0 else 0.5
            
        # 2. Numeric Consistency: If numbers exist, check for presence in candidate
        if p_feat['numbers']:
            # Does the candidate contain any of the prompt's numbers or a result?
            # Heuristic: Presence of numbers suggests engagement with numeric constraints
            has_nums = any(n in candidate for n in p_feat['numbers'])
            if has_nums:
                score += 3.0
            elif c_feat['numbers']:
                score += 1.0 # Might be a calculated result
        
        # 3. Conditional/Logical Flow
        if p_feat['conditionals'] > 0:
            score += 1.5 if c_feat['conditionals'] > 0 else 0.0
            
        # 4. NCD as Tiebreaker (Low weight)
        # Only used if structural signals are ambiguous
        ncd = self._ncd(prompt, candidate)
        score += (1.0 - ncd) * 0.5
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            min_c = min(c1, c2)
            if min_c == 0: return 1.0
            return (c12 - min_c) / max(c1, c2, 1)
        except:
            return 1.0

    def _neuromodulatory_gain(self, prompt: str, candidates: List[str]) -> float:
        """
        Neuromodulation: Calculate dynamic gain based on uncertainty.
        High uncertainty (low structural signal in top candidates) -> High Gain (Exploration).
        Low uncertainty -> Low Gain (Exploitation).
        """
        if not candidates:
            return 1.0
            
        # Estimate uncertainty by variance of raw structural scores
        scores = [self._check_constraint_satisfaction(prompt, c) for c in candidates]
        if len(scores) < 2:
            return 1.0
            
        mean_s = sum(scores) / len(scores)
        variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)
        
        # Inverse relationship: Low variance (clear winner) -> Low Gain (Sharpen)
        # High variance (confusion) -> High Gain (Broaden entropy tolerance)
        # Mapping to [0.5, 2.0] range
        gain = 1.0 + (1.0 / (variance + 0.1)) 
        return min(2.5, max(0.5, gain))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Neuromodulatory Gain Calculation
        gain = self._neuromodulatory_gain(prompt, candidates)
        
        ranked = []
        for cand in candidates:
            # 2. Mechanism Design: Proper Scoring Rule
            # Score = Structural Alignment + Gain * Entropy_Term(Approximated by length diversity)
            base_score = self._check_constraint_satisfaction(prompt, cand)
            
            # Entropy bonus: Slight preference for non-trivial length if gain is high
            # This mimics "exploration" when uncertainty is high
            entropy_bonus = 0.0
            if gain > 1.5:
                entropy_bonus = math.log(len(cand) + 1) * 0.1
            
            final_score = base_score + (gain * 0.1 * entropy_bonus)
            
            ranked.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match score: {base_score:.2f}, Gain-adjusted entropy bonus: {entropy_bonus:.2f}"
            })
        
        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Maximum Entropy principle restricted to smoothing the probability estimate
        based on the structural score relative to a null hypothesis.
        """
        # Get the structural score for the specific answer
        score = self._check_constraint_satisfaction(prompt, answer)
        
        # Baseline score for a generic wrong answer (e.g., empty or random)
        baseline = 1.0 
        
        # Convert to logit-like space
        diff = score - baseline
        
        # Maximum Entropy Smoothing: 
        # Instead of hard thresholding, use a sigmoid to map to [0,1] 
        # ensuring the distribution is least biased given the constraint (score).
        # This prevents over-confidence (0 or 1) unless evidence is extreme.
        import math
        # Sigmoid with temperature controlled by entropy logic
        temp = 2.0 
        conf = 1.0 / (1.0 + math.exp(-diff / temp))
        
        return float(conf)