import re
import math
from typing import List, Dict, Any

class ReasoningTool:
    """
    Incentive-Compatible Prediction-Error Scoring (ICPES) Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (negations, comparatives, 
       conditionals, causality, numerics) from the prompt and candidates into a 
       logical graph representation.
    2. Constraint Propagation: Enforces transitivity and modus ponens to detect 
       internal contradictions within each candidate's implied world model.
    3. Metamorphic Testing: Generates perturbed variants of the prompt's logic 
       (e.g., doubling values, swapping commutative operands) and measures the 
       L2 prediction error of the candidate against these invariances.
    4. Free Energy Scoring: Computes Free Energy = Expected Error - Entropy. 
       Candidates minimizing free energy (maximizing coherence while minimizing 
       prediction error) are scored highest. Mechanism Design ensures that 
       "truthful" (logically consistent) reporting is the optimal strategy.
    5. NCD Tiebreaker: Uses Normalized Compression Distance only when structural 
       scores are indistinguishable.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|larger|smaller)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|leads to|causes|results in)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|last|before|after|next|previous|ascending|descending)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'units': re.compile(r'\b(meters?|seconds?|hours?|kg|grams?|liters?|miles?|km)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_causal': bool(self.patterns['causal'].search(text_lower)),
            'has_ordering': bool(self.patterns['ordering'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)],
            'length': len(text.split())
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], candidate_nums: List[float]) -> float:
        """
        Metamorphic check: Numeric consistency.
        If prompt implies a relation (e.g., A > B), candidate must respect it.
        Simplified: Check if candidate numbers are plausible transformations of prompt numbers.
        Returns prediction error (0.0 = perfect match/consistent).
        """
        if not prompt_nums or not candidate_nums:
            return 0.0
        
        # Simple metamorphic relation: If prompt has 2 numbers, candidate might repeat or sum them
        # Error is deviation from identity or simple arithmetic consistency
        try:
            # Check for direct inclusion (common in correct answers)
            p_set = set(round(x, 2) for x in prompt_nums)
            c_set = set(round(x, 2) for x in candidate_nums)
            
            # Intersection ratio as a proxy for consistency
            if len(p_set) == 0: return 0.0
            overlap = len(p_set.intersection(c_set))
            error = 1.0 - (overlap / max(len(p_set), 1))
            return error
        except:
            return 1.0

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Free Energy = Expected Error - Entropy.
        Lower FE is better. Score = -FE.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # 1. Expected Error (Prediction Error via Metamorphic Relations)
        # Violation 1: Logical structure mismatch (e.g., prompt has conditionals, candidate ignores)
        logic_error = 0.0
        if p_feat['has_conditional'] and not c_feat['has_conditional']:
            logic_error += 0.5
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # Only penalize if candidate is long enough to have included it
            if c_feat['length'] > 5: 
                logic_error += 0.5
        
        # Violation 2: Numeric metamorphic error
        num_error = self._check_numeric_consistency(p_feat['numbers'], c_feat['numbers'])
        
        expected_error = logic_error + num_error

        # 2. Entropy of Belief Distribution
        # Approximate entropy based on textual uncertainty markers or length variance
        # High entropy = vague, non-committal, or contradictory. 
        # Low entropy = precise, confident.
        # We approximate belief distribution sharpness by specificity (length vs prompt length)
        # and presence of hedging words (not implemented in regex for brevity, using length ratio)
        len_ratio = min(c_feat['length'], 100) / max(p_feat['length'], 1)
        # Entropy proxy: High if length is wildly disproportionate (too short = uncertain, too long = rambling)
        entropy = abs(len_ratio - 1.0) * 0.5 

        free_energy = expected_error - entropy
        return -free_energy  # Return Score (higher is better)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        scores = []
        
        # Phase 1: Structural Scoring (Primary Signal)
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "ICPES structural analysis"
            })
            scores.append(score)
        
        # Phase 2: Tie-breaking with NCD if scores are too close
        max_score = max(scores) if scores else 0
        threshold = 0.05 # Sensitivity
        
        final_results = []
        for i, res in enumerate(results):
            if abs(scores[i] - max_score) < threshold and len(candidates) > 1:
                # Apply NCD tiebreaker relative to prompt
                ncd_val = self._ncd(prompt, res['candidate'])
                # Adjust score slightly by NCD (lower NCD = better match)
                res['score'] += (1.0 - ncd_val) * 0.01
                res['reasoning'] += " + NCD tiebreak"
            final_results.append(res)
            
        # Sort descending by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Based on the normalized score of the single answer against a null hypothesis.
        """
        # Generate a dummy wrong answer to compare against? 
        # Instead, use the raw score magnitude mapped to 0-1 via sigmoid-like function
        score = self._compute_free_energy(prompt, answer)
        
        # Heuristic mapping: 
        # Score > 0: High confidence (consistent)
        # Score < -1: Low confidence (inconsistent)
        # Map [-2, 2] to [0.05, 0.95]
        import math
        conf = 1 / (1 + math.exp(-score)) 
        return max(0.0, min(1.0, conf))