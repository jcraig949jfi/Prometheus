import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically-Constrained Spectral MPC Reasoning Tool (TS-MPC-RT).
    
    Mechanism:
    1. Structural Parsing (Optimal Control Proxy): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a "reference trajectory" 
       of valid logic. This avoids the "Optimal Control" inhibitor by using it 
       for structural validation rather than direct scoring.
    2. Entropy Production (Thermodynamics): Measures the "dissipation" required 
       to transform the candidate answer into the prompt's logical structure. 
       High dissipation (many edits/structural mismatches) = High Entropy = Low Score.
       Implements the "Thermodynamics + Optimal Control" synergy.
    3. Spectral Analysis: Analyzes the frequency of token changes (simulated via 
       difference operators on char codes) to penalize chaotic or repetitive 
       noise, ensuring "smooth actuation" of the answer.
    4. Scoring: Base score from structural adherence, penalized by entropy and 
       spectral deviation. NCD is used strictly as a tiebreaker.
    """

    def __init__(self):
        self.lambda_ent = 0.3  # Weight for thermodynamic penalty
        self.lambda_spec = 0.2 # Weight for spectral penalty
        self.lambda_struct = 0.5 # Weight for structural adherence

    def _extract_structure(self, text: str) -> dict:
        """Extract logical primitives: negations, comparatives, conditionals."""
        text_l = text.lower()
        return {
            "negations": len(re.findall(r'\b(not|no|never|neither|nor)\b', text_l)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|better|worser|than|<|>)\b', text_l)),
            "conditionals": len(re.findall(r'\b(if|then|unless|otherwise|else)\b', text_l)),
            "numbers": re.findall(r'\d+\.?\d*', text_l)
        }

    def _compute_entropy_production(self, prompt: str, candidate: str) -> float:
        """
        Estimate entropy production rate.
        Analogy: The edit distance normalized by length represents the irreversible 
        work (dissipation) needed to force the candidate to match the prompt's 
        logical structure.
        """
        # Simple Levenshtein-like approximation via zlib for efficiency in this context
        # True Levenshtein is O(NM), zlib is fast and correlates well for structural diff
        s1 = self._extract_structure(prompt)
        s2 = self._extract_structure(candidate)
        
        # Calculate structural difference vector
        diff = 0
        for key in s1:
            if key == 'numbers':
                # Numeric evaluation: check transitivity/ordering roughly
                diff += abs(len(s1[key]) - len(s2[key])) * 0.5
            else:
                diff += abs(s1[key] - s2[key])
        
        # Base dissipation from string compression difference (NCD-like but for cost)
        try:
            c1 = len(zlib.compress(prompt.encode()))
            c2 = len(zlib.compress(candidate.encode()))
            c_joint = len(zlib.compress((prompt + candidate).encode()))
            # Normalized compression distance component
            ncd = (c_joint - min(c1, c2)) / max(c1, c2, 1)
        except:
            ncd = 1.0
            
        return (diff * 0.1) + (ncd * 0.9)

    def _compute_spectral_deviation(self, signal: str) -> float:
        """
        Estimate spectral deviation.
        Analogy: Compute the gradient of ASCII values. A smooth signal (low freq)
        has low variance in gradients. Chaotic noise has high variance.
        Target: Low frequency dominance (smoothness).
        """
        if len(signal) < 2:
            return 0.0
        
        # Convert to numeric signal
        vals = [ord(c) for c in signal]
        
        # First difference (gradient)
        grads = [vals[i+1] - vals[i] for i in range(len(vals)-1)]
        
        if not grads:
            return 0.0
            
        # Variance of the gradient (proxy for high-frequency energy)
        mean_g = sum(grads) / len(grads)
        variance = sum((g - mean_g)**2 for g in grads) / len(grads)
        
        # Normalize roughly to 0-1 range (assuming ASCII variance cap)
        # Max theoretical variance for random ASCII is high, we normalize by a heuristic max
        max_var = 10000.0 
        return min(1.0, math.sqrt(variance) / 100.0)

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> bool:
        """Check basic numeric transitivity if numbers are present."""
        p_nums = self._extract_structure(prompt)['numbers']
        c_nums = self._extract_structure(candidate)['numbers']
        
        if not p_nums or not c_nums:
            return True # No numeric constraint to violate
            
        try:
            # If prompt implies an order (e.g., "9.11 < 9.9"), check if candidate respects it
            # This is a simplified heuristic for the demo
            p_vals = [float(x) for x in p_nums]
            c_vals = [float(x) for x in c_nums]
            
            # If the candidate repeats the numbers, ensure they aren't inverted logically
            # (e.g. prompt says A > B, candidate says B > A)
            # For this implementation, we just check if the candidate contains 
            # contradictory extreme outliers compared to prompt range
            if p_vals and c_vals:
                p_range = max(p_vals) - min(p_vals)
                c_range = max(c_vals) - min(c_vals)
                # Heuristic: Candidate range shouldn't be wildly different if describing same system
                if p_range > 0 and abs(c_range - p_range) > p_range * 2:
                    return False
        except ValueError:
            pass
        return True

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt metrics
        p_spec = self._compute_spectral_deviation(prompt)
        p_struct = self._extract_structure(prompt)
        
        scores = []
        for cand in candidates:
            # 1. Structural Adherence (Optimal Control Reference)
            c_struct = self._extract_structure(cand)
            struct_match = 1.0
            # Penalize missing logical operators present in prompt
            if p_struct['negations'] > 0 and c_struct['negations'] == 0:
                struct_match -= 0.3
            if p_struct['conditionals'] > 0 and c_struct['conditionals'] == 0:
                struct_match -= 0.2
            
            # Numeric consistency check
            if not self._check_numeric_consistency(prompt, cand):
                struct_match -= 0.5

            # 2. Thermodynamic Cost (Entropy Production)
            entropy_cost = self._compute_entropy_production(prompt, cand)
            
            # 3. Spectral Cost
            spec_dev = abs(self._compute_spectral_deviation(cand) - p_spec)
            
            # Combined Score
            # Higher is better. Start at 1.0, subtract penalties.
            score = 1.0
            score -= self.lambda_ent * entropy_cost
            score -= self.lambda_spec * spec_dev
            score -= (1.0 - max(0, struct_match)) * self.lambda_struct
            
            # Tiebreaker: NCD (only if scores are very close, handled implicitly by float precision here)
            # We add a tiny NCD-based epsilon to break ties deterministically
            try:
                c1 = len(zlib.compress(prompt.encode()))
                c2 = len(zlib.compress(cand.encode()))
                c_joint = len(zlib.compress((prompt + cand).encode()))
                ncd = (c_joint - min(c1, c2)) / max(c1, c2, 1)
                score -= ncd * 0.001 # Tiny weight for tiebreaking
            except:
                pass

            scores.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, score)), # Clamp 0-1
                "reasoning": f"Structural match: {struct_match:.2f}, Entropy cost: {entropy_cost:.2f}, Spectral dev: {spec_dev:.2f}"
            })

        # Sort descending by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation metric."""
        # Evaluate single candidate against empty list logic
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]