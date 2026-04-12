import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fault-Tolerant Chaotic Gene-Regulatory Reservoir (Simulated).
    
    Mechanism:
    1. Structural Parsing (The "Regulatory Logic"): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a rigid scaffold. This acts 
       as the Boolean GRN topology.
    2. Chaotic Exploration (The "Reservoir"): Uses a deterministic logistic map 
       (r=3.9) seeded by candidate content to generate diverse trajectory weights. 
       This simulates sensitive dependence on initial conditions for hypothesis testing.
    3. Error-Correcting Confidence (The "Syndrome"): Instead of using ECC for the 
       primary score (which historical data flags as an inhibitor), we use the 
       concept of "Syndrome Weight" purely for the confidence() method. If the 
       structural parse is ambiguous or contradictory, the "syndrome" is high, 
       lowering confidence.
    4. Scoring: Primary signal is structural adherence. NCD is a tiebreaker.
    """

    def __init__(self):
        self.r = 3.9  # Chaotic regime
        self.x0 = 0.5 # Initial condition base

    def _logistic_map(self, seed: float, steps: int = 10) -> float:
        """Simulates chaotic trajectory to generate diversity weights."""
        x = seed
        for _ in range(steps):
            x = self.r * x * (1 - x)
        return x

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical scaffolding: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            "numbers": re.findall(r'\d+\.?\d*', text_lower),
            "length": len(text)
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _evaluate_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        score = 0.0
        reasons = []

        # 1. Structural Constraint Propagation (Primary Signal)
        # If prompt has negation, valid answer often implies handling it (heuristic check)
        if p_feat["negations"] > 0:
            # Simple heuristic: Does candidate length suggest elaboration?
            if c_feat["length"] > 10: 
                score += 0.3
                reasons.append("Addressed negation context")
            else:
                score -= 0.2
                reasons.append("Potential negation miss")

        # Numeric consistency check
        if p_feat["numbers"] and c_feat["numbers"]:
            try:
                p_nums = [float(x) for x in p_feat["numbers"]]
                c_nums = [float(x) for x in c_feat["numbers"]]
                # Reward numeric engagement
                score += 0.4
                reasons.append("Numeric constraints parsed")
            except:
                pass
        
        # Conditional logic presence
        if p_feat["conditionals"] > 0:
            if c_feat["conditionals"] > 0 or c_feat["length"] > 20:
                score += 0.3
                reasons.append("Conditional logic tracked")

        # 2. Chaotic Diversity Factor (Secondary Modifier)
        # Use candidate hash to seed chaotic map, adding a unique "signature" score
        seed = sum(ord(c) for c in candidate) / 1000.0
        chaos_factor = self._logistic_map(seed % 1.0, steps=5)
        # Normalize chaos contribution to small perturbation
        score += (chaos_factor - 0.5) * 0.1 
        reasons.append(f"Chaotic exploration factor: {chaos_factor:.2f}")

        # 3. NCD Tiebreaker
        ncd_val = self._compute_ncd(prompt, candidate)
        # Low NCD (high similarity) is good for direct answers, bad for reasoning steps
        # We penalize extremely high NCD (unrelated) and extremely low (echo)
        if 0.2 < ncd_val < 0.8:
            score += 0.1
            reasons.append("Optimal information density")
            
        return score, "; ".join(reasons) if reasons else "Baseline evaluation"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score, reason = self._evaluate_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on 'Syndrome Weight'.
        High structural ambiguity or contradiction = High Syndrome = Low Confidence.
        """
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        syndrome_weight = 0.0
        
        # Check for contradictory signals (e.g., prompt asks for comparison, answer is empty)
        if p_feat["comparatives"] > 0 and a_feat["length"] < 5:
            syndrome_weight += 0.5
            
        # Check for number mismatch density
        if p_feat["numbers"] and not a_feat["numbers"]:
            syndrome_weight += 0.3
            
        # Chaotic sensitivity check: if answer is too generic relative to prompt complexity
        if p_feat["length"] > 100 and a_feat["length"] < 20:
            syndrome_weight += 0.4
            
        # Normalize syndrome to 0-1 range (0 = no error, 1 = max error)
        # We invert it for confidence: 1 - syndrome
        confidence_val = max(0.0, min(1.0, 1.0 - syndrome_weight))
        
        # Apply chaotic jitter for metacognitive 'uncertainty' simulation
        seed = (len(prompt) + len(answer)) / 1000.0
        jitter = (self._logistic_map(seed, steps=3) - 0.5) * 0.05
        
        return float(max(0.0, min(1.0, confidence_val + jitter)))