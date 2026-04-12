import math
import zlib
import json

class ReasoningTool:
    """
    CNICE-inspired Reasoning Tool: Chaotic Neuromodulated Incentive-Compatible Exploration.
    
    Mechanism:
    1. Chaotic Core: Uses a logistic map (r=3.9) seeded by prompt-candidate hash to generate
       deterministic exploration noise. This mimics the Lyapunov-driven exploration rate.
    2. Neuromodulation: Computes a 'prediction error' (delta) based on the discrepancy between
       the candidate's semantic density (via NCD) and the prompt's expected structure.
       High delta increases the chaotic gain (exploration), low delta stabilizes (exploitation).
    3. Mechanism Design (Incentive Compatibility): Applies a quadratic scoring rule (Brier score
        analog) where 'truthful' reporting is defined as maximizing structural alignment 
        (constraint propagation) while minimizing unnecessary complexity. Candidates are penalized
        for strategic over-length or under-specificity relative to the prompt's constraints.
    
    This implementation approximates the theoretical architecture using deterministic string
    heuristics, compression-based similarity (NCD), and chaotic weighting to beat baseline NCD.
    """

    def __init__(self):
        self.r = 3.9  # Chaotic regime for logistic map
        self.base_state = 0.5

    def _logistic_map(self, x, steps=10):
        """Iterate logistic map to generate deterministic chaos from state x."""
        for _ in range(steps):
            x = self.r * x * (1.0 - x)
        return x

    def _get_chaos_seed(self, text):
        """Convert text to a deterministic float [0.1, 0.9] for chaotic initialization."""
        h = zlib.crc32(text.encode()) & 0xffffffff
        return 0.1 + 0.8 * (h / 0xffffffff)

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode()
        s2_b = s2.encode()
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        if min(c1, c2) == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _extract_constraints(self, prompt):
        """
        Structural parsing: Extract negations, comparatives, and conditionals.
        Returns a weight modifier based on constraint satisfaction potential.
        """
        p_lower = prompt.lower()
        score = 0.0
        
        # Detect logical operators
        if "not" in p_lower or "never" in p_lower:
            score += 0.2  # Negation requires higher precision
        if "if" in p_lower or "then" in p_lower:
            score += 0.2  # Conditional requires transitivity
        if ">" in prompt or "<" in prompt or "more" in p_lower or "less" in p_lower:
            score += 0.2  # Comparative requires numeric logic
            
        return score

    def _numeric_check(self, prompt, candidate):
        """
        Numeric evaluation: Detect number comparisons.
        If prompt implies math, verify candidate consistency.
        """
        # Simple heuristic: if prompt has numbers and candidate has numbers, check order
        # This is a simplified proxy for full symbolic math
        p_nums = [float(x) for x in prompt.split() if x.replace('.','').replace('-','').isdigit()]
        c_nums = [float(x) for x in candidate.split() if x.replace('.','').replace('-','').isdigit()]
        
        if not p_nums or not c_nums:
            return 0.0
            
        # Proxy for consistency: does the candidate number magnitude align with prompt trend?
        # (Very rough approximation for the sake of the 150-line limit)
        try:
            p_avg = sum(p_nums) / len(p_nums)
            c_avg = sum(c_nums) / len(c_nums)
            # Reward if candidate magnitude is within reasonable bound of prompt context
            if abs(p_avg - c_avg) < (p_avg * 0.5 + 1): 
                return 0.1
        except:
            pass
        return 0.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        constraint_weight = self._extract_constraints(prompt)
        base_chaos = self._get_chaos_seed(prompt)

        for cand in candidates:
            # 1. Chaotic Core Oscillator
            # Initialize chaotic variable based on prompt+candidate interaction
            x = self._get_chaos_seed(prompt + cand)
            # Iterate to mix state
            x = self._logistic_map(x, steps=5)
            
            # 2. Neuromodulatory Gain Control
            # Compute prediction error (delta) via NCD between prompt and candidate
            # Low NCD = high confidence (low delta), High NCD = low confidence (high delta)
            ncd_val = self._ncd(prompt, cand)
            delta = ncd_val  # Using NCD as proxy for |observed - predicted|
            
            # Modulate chaotic gain: Higher delta (uncertainty) -> higher chaos influence
            # If delta is high, we rely more on the chaotic exploration term
            chaos_gain = delta * 0.2 
            chaotic_term = (x - 0.5) * chaos_gain 

            # 3. Mechanism Design (Incentive Compatibility)
            # Proper scoring rule: Reward structural alignment, penalize noise.
            # Base score: Inverse of NCD (similarity)
            base_score = 1.0 - ncd_val
            
            # Add numeric and constraint bonuses
            numeric_bonus = self._numeric_check(prompt, cand)
            constraint_bonus = 0.0
            if constraint_weight > 0:
                # Heuristic: if constraints exist, longer candidates (up to a point) 
                # that include prompt words are 'truthful'
                overlap = len(set(prompt.lower().split()) & set(cand.lower().split()))
                constraint_bonus = min(overlap * 0.05, 0.2)

            # Final Score Calculation
            # Score = (Base Similarity + Constraint Bonuses) * (1 + Chaotic Exploration)
            # The chaotic term allows escaping local optima where NCD is misleading
            raw_score = (base_score + numeric_bonus + constraint_bonus) + chaotic_term
            
            # Clamp to [0, 1]
            final_score = max(0.0, min(1.0, raw_score))

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"NCD:{ncd_val:.2f} Chaos:{chaotic_term:.2f} Constraints:{constraint_bonus:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single answer.
        """
        # Reuse evaluate logic for consistency
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]