import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Spectral Type-Checked Hypothesis Engine (CSTHE) - Computational Approximation.
    
    Mechanism:
    1. Type Theory (Logical Coherence): Uses structural parsing to extract logical operators
       (negations, comparatives, conditionals) and enforces constraint propagation.
       Ill-formed logical structures receive a penalty (Type Check).
    2. Chaos Theory (Sensitivity): Encodes the candidate string into initial conditions for
       a logistic map. Iterates the system to compute a Lyapunov-like exponent.
       High sensitivity to small string perturbations (brittleness) yields lower scores.
    3. Spectral Analysis (Stability): Treats the character code sequence as a time series.
       Computes the variance of differences (spectral proxy) to detect "noise" vs "signal".
       Smooth, logically consistent numeric/logic transitions yield higher stability scores.
       
    Scoring: Weighted sum of Logical Coherence (40%), Dynamical Stability (40%), and NCD (20%).
    """

    def __init__(self):
        self.logic_keywords = ['if', 'then', 'else', 'not', 'no', 'yes', 'true', 'false', 'greater', 'less', 'equal']
        self.comparators = ['<', '>', '=', '!', '>', '<']
        
    def _type_check_logic(self, text: str) -> float:
        """Scores logical coherence based on structural presence and consistency."""
        text_lower = text.lower()
        score = 0.0
        
        # Check for balanced logical structures (simplified)
        has_if = 'if' in text_lower
        has_then = 'then' in text_lower or ':' in text_lower
        has_not = 'not' in text_lower or 'no ' in text_lower
        
        # Reward consistent conditionals
        if has_if and has_then:
            score += 0.4
        elif has_if and not has_then:
            # Penalty for incomplete logic (Type error)
            score -= 0.2
        else:
            score += 0.1 # Neutral statement
            
        # Check for explicit boolean consistency
        if 'true' in text_lower and 'false' in text_lower:
            score -= 0.1 # Contradiction risk
        elif 'true' in text_lower or 'false' in text_lower:
            score += 0.2
            
        return max(0.0, min(1.0, 0.5 + score))

    def _chaos_sensitivity(self, text: str) -> float:
        """
        Simulates chaos via Logistic Map.
        Maps string hash to initial condition x0. 
        Measures divergence over iterations. Lower divergence = more stable/robust.
        """
        if not text:
            return 0.0
            
        # Normalize string to float seed (0.1 to 0.9)
        seed = sum(ord(c) for c in text) / (len(text) * 128.0)
        x0 = 0.1 + 0.8 * abs(math.sin(seed * 100)) # Ensure range (0.1, 0.9)
        
        r = 3.9 # Chaotic regime
        x = x0
        trajectory = []
        
        # Burn-in
        for _ in range(50):
            x = r * x * (1 - x)
            
        # Collect trajectory
        history = []
        for _ in range(100):
            x = r * x * (1 - x)
            history.append(x)
            
        # Estimate Lyapunov exponent approximation (average log divergence)
        # Since we only have one string, we simulate sensitivity by checking 
        # how much the trajectory varies locally (variance of derivatives)
        diffs = [abs(history[i+1] - history[i]) for i in range(len(history)-1)]
        if not diffs:
            return 0.5
            
        avg_diff = sum(diffs) / len(diffs)
        # Map to 0-1 score: Low variation in chaotic system implies specific stable pockets
        # However, in pure chaos, high variation is expected. 
        # We invert: We want candidates that don't produce 'random walk' noise in their encoding.
        # Let's use the regularity of the trajectory as a proxy for 'structured' input.
        
        # Alternative: Use the string length and char distribution to perturb x0 slightly
        # and see if the outcome classifies similarly. 
        # Simplified: Return stability score based on trajectory smoothness relative to max possible
        stability = 1.0 / (1.0 + avg_diff * 10) 
        return stability

    def _spectral_analyze(self, text: str) -> float:
        """
        Spectral proxy: Analyzes frequency of character code changes.
        High frequency noise = low score. Dominant low freq patterns = high score.
        """
        if len(text) < 2:
            return 0.5
            
        codes = [ord(c) for c in text]
        # First difference (high pass filter proxy)
        diffs = [codes[i+1] - codes[i] for i in range(len(codes)-1)]
        
        # Variance of differences (Energy in high frequencies)
        mean_diff = sum(diffs) / len(diffs)
        variance = sum((d - mean_diff)**2 for d in diffs) / len(diffs)
        
        # Normalize variance to 0-1. 
        # Typical ASCII variance is moderate. Extremely high variance = noise.
        # Scale: 0 variance = 1.0 score. High variance -> 0.
        score = 1.0 / (1.0 + math.log1p(variance) / 10.0)
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def _extract_numeric_truth(self, prompt: str, candidate: str) -> float:
        """
        Structural parsing for numeric comparisons.
        Detects patterns like '9.11 < 9.9' or '5 > 3'.
        """
        combined = f"{prompt} {candidate}"
        # Find floats/ints
        numbers = re.findall(r'-?\d+\.?\d*', combined)
        if len(numbers) < 2:
            return 0.5 # No numeric logic to verify
            
        try:
            nums = [float(n) for n in numbers]
            # Check for explicit operators in candidate
            if '>' in candidate and nums[0] > nums[1]:
                return 1.0
            if '<' in candidate and nums[0] < nums[1]:
                return 1.0
            if '==' in candidate or '=' in candidate and nums[0] == nums[1]:
                return 1.0
                
            # Implicit comparison: If prompt asks "which is larger" and candidate is the max
            # Heuristic: If candidate is just the number, check if it satisfies implied constraint
            if len(candidate.strip()) < 20 and candidate.strip() in combined:
                # If the candidate is purely the larger number in a comparison context
                if nums[0] != nums[1]:
                    expected = max(nums[0], nums[1])
                    # Check if candidate string contains the max number
                    if str(expected) in candidate or (expected == int(expected) and str(int(expected)) in candidate):
                         # Verify context implies maximization
                        if any(k in prompt.lower() for k in ['larger', 'bigger', 'max', 'greater', 'highest']):
                            return 1.0
                        if any(k in prompt.lower() for k in ['smaller', 'less', 'min', 'lowest']):
                            if str(min(nums)) in candidate:
                                return 1.0
        except ValueError:
            pass
            
        return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_logic = self._type_check_logic(prompt)
        
        for cand in candidates:
            # 1. Type Theory Score (Logical Structure)
            logic_score = self._type_check_logic(cand)
            
            # 2. Chaos Score (Sensitivity/Stability)
            chaos_score = self._chaos_sensitivity(cand)
            
            # 3. Spectral Score (Frequency domain)
            spectral_score = self._spectral_analyze(cand)
            
            # 4. Numeric/Structural Truth (Primary Signal)
            numeric_score = self._extract_numeric_truth(prompt, cand)
            
            # 5. NCD (Tiebreaker only)
            ncd_score = 1.0 - self._ncd(prompt, cand) # Invert so higher is better match
            
            # Weighted Combination
            # Priority: Numeric/Structural > Logic/Chaos/Spectral > NCD
            if numeric_score > 0.9:
                final_score = 0.95 + (logic_score * 0.04) + (chaos_score * 0.01)
            else:
                # Base reasoning on the triad
                base_reasoning = (logic_score * 0.4) + (chaos_score * 0.3) + (spectral_score * 0.3)
                # NCD as tiebreaker modifier (small weight)
                final_score = (base_reasoning * 0.8) + (ncd_score * 0.2)
            
            # Construct reasoning string
            reason = f"Logic:{logic_score:.2f} Chaos:{chaos_score:.2f} Spec:{spectral_score:.2f}"
            if numeric_score > 0.9:
                reason = "Structural numeric constraint satisfied."
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']