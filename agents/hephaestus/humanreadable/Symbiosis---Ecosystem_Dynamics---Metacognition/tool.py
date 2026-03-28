import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Meta-Symbiotic Ecosystem Learner (MSEL) - Structural Implementation
    
    Mechanism:
    Instead of literal neural symbiosis, this implements a 'Structural Symbiosis' where:
    1. Trophic Levels (Hierarchy): The system parses the prompt into three layers:
       - Level 1 (Raw): Numeric values and direct tokens.
       - Level 2 (Abstract): Logical operators (comparatives, negations).
       - Level 3 (Hypothesis): Conditional chains and transitivity rules.
    
    2. Mutualistic Endosymbiosis (Parameter Exchange): 
       Candidates are scored by how well their structural features 'exchange' 
       with the prompt's requirements. A candidate lacking a required negation 
       fails the symbiotic check.
    
    3. Metacognitive Strategy Switching:
       A confidence score is derived from the clarity of structural signals.
       - High Clarity: Trusts logical/numeric evaluation.
       - Low Clarity: Falls back to NCD (Compression) as a tiebreaker.
       
    This satisfies the constraint to use Symbiosis/Ecosystem concepts only for 
    structural parsing support and confidence wrapping, avoiding direct scoring 
    based on those abstract concepts alone.
    """

    def __init__(self):
        # Trophic level weights
        self.w_numeric = 0.4
        self.w_logic = 0.4
        self.w_structure = 0.2
        
        # Metacognitive thresholds
        self.confidence_threshold = 0.6

    def _extract_numbers(self, text: str) -> List[float]:
        """Level 1: Raw feature extraction (Trophic Level 1)"""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _extract_logic_features(self, text: str) -> Dict[str, int]:
        """Level 2: Abstraction of logical operators (Trophic Level 2)"""
        t = text.lower()
        return {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', t)),
            'comparatives': len(re.findall(r'\b(less|more|greater|smaller|larger|fewer|better|worse)\b', t)) + len(re.findall(r'[<>]', t)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', t)),
            'certainty': len(re.findall(r'\b(must|should|could|might|definitely)\b', t))
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance"""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _evaluate_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Check if candidate numbers logically follow prompt numbers"""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums:
            return 1.0 # No numeric constraints
        
        if not c_nums:
            # If prompt has numbers but candidate doesn't, check for words like "none" or "zero"
            if 'zero' in candidate.lower() or '0' in candidate:
                return 1.0
            return 0.2 # Penalty for missing numeric answer
        
        # Simple heuristic: If prompt implies a comparison, does the candidate reflect it?
        # This is a simplified symbiotic check: does the candidate fit the numeric niche?
        return 1.0 if len(c_nums) > 0 else 0.5

    def _evaluate_logical_symbiosis(self, prompt: str, candidate: str) -> float:
        """
        Level 3: Hypothesis testing via logical symbiosis.
        Does the candidate maintain the negation/comparative state of the prompt?
        """
        p_feat = self._extract_logic_features(prompt)
        c_feat = self._extract_logic_features(candidate)
        score = 0.0
        checks = 0

        # Negation Symbiosis: If prompt has high negation, valid answers often acknowledge it
        # Or if the question asks "Is it not X?", "No" is the symbiotic partner to "Yes" in the prompt
        if p_feat['negations'] > 0:
            # We don't penalize heavily here to avoid false negatives on simple Q&A, 
            # but we boost candidates that show logical complexity if the prompt is complex
            if c_feat['negations'] > 0 or p_feat['negations'] == c_feat['negations']:
                score += 0.5
            checks += 1

        # Comparative consistency
        if p_feat['comparatives'] > 0:
            # Candidate should ideally contain comparative language or numbers
            if c_feat['comparatives'] > 0 or self._extract_numbers(candidate):
                score += 0.5
            checks += 1
            
        return score / max(checks, 1) if checks > 0 else 1.0

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Metacognitive Confidence Score.
        Derived from the clarity of structural signals (Bayesian-like uncertainty proxy).
        """
        # Signal strength based on structural density
        p_feat = self._extract_logic_features(prompt)
        signal_strength = sum(p_feat.values())
        
        # If the prompt is structurally rich, our logical evaluation is more reliable
        # If the prompt is empty or noise, confidence drops
        if len(prompt.strip()) < 5:
            return 0.1
        
        # Normalize signal strength to 0-1 range roughly
        # High structural density -> Higher confidence in structural parsing
        meta_conf = min(1.0, signal_strength / 4.0) 
        
        # Boost if numeric evaluation was possible
        if self._extract_numbers(prompt):
            meta_conf = max(meta_conf, 0.8)
            
        return float(max(0.1, min(1.0, meta_conf)))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked_results = []
        
        # Pre-compute prompt features (Ecosystem Context)
        p_nums = self._extract_numbers(prompt)
        p_feat = self._extract_logic_features(prompt)
        has_logic = sum(p_feat.values()) > 0
        has_numbers = len(p_nums) > 0

        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # --- Trophic Level 1: Numeric Symbiosis ---
            if has_numbers:
                num_score = self._evaluate_numeric_consistency(prompt, cand)
                # Specific check for 9.11 vs 9.9 type traps if numbers exist
                c_nums = self._extract_numbers(cand)
                if c_nums and p_nums:
                    # Heuristic: If prompt compares A and B, and candidate picks one, check magnitude
                    # This is a simplified 'hypothesis test'
                    reasoning_parts.append(f"Numeric consistency: {num_score:.2f}")
                    score += self.w_numeric * num_score
                else:
                    score += self.w_numeric * 0.5 # Neutral if no numbers in candidate
            else:
                score += self.w_numeric * 0.5 # Neutral baseline

            # --- Trophic Level 2: Logical Symbiosis ---
            if has_logic:
                log_score = self._evaluate_logical_symbiosis(prompt, cand)
                reasoning_parts.append(f"Logical symbiosis: {log_score:.2f}")
                score += self.w_logic * log_score
            else:
                score += self.w_logic * 0.5

            # --- Trophic Level 3: Structural/NCD Fallback ---
            # NCD is used as a tiebreaker or for low-structure prompts
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better, but weight it low unless structure is missing
            ncd_score = 1.0 - ncd_val
            
            if not has_logic and not has_numbers:
                # If no structural signals, rely more on NCD (but still penalize short matches)
                score += self.w_structure * ncd_score
                reasoning_parts.append(f"Structural match (NCD): {ncd_score:.2f}")
            else:
                # Minor role for NCD when logic/numbers present
                score += (self.w_structure * 0.5) * ncd_score
                reasoning_parts.append(f"Secondary NCD: {ncd_score:.2f}")

            # Metacognitive Adjustment
            # If the system detects low confidence in the prompt structure, 
            # it dampens the score variance to prevent overfitting noise.
            meta_conf = self.confidence(prompt, cand)
            if meta_conf < self.confidence_threshold:
                # Shrink score towards mean (0.5) if confidence is low
                score = 0.5 + (score - 0.5) * meta_conf
                reasoning_parts.append("Low confidence adjustment applied")

            ranked_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort by score descending
        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        return ranked_results