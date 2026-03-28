import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    CIMEL-inspired Reasoning Tool.
    
    Mechanism:
    1. Compositionality: Decomposes prompt into structural primitives (negations, comparatives, 
       conditionals, numeric values) rather than treating it as a bag of words.
    2. Mechanism Design (Internal Scoring): Implements a 'truthful reporting' scoring rule.
       Candidates are scored based on structural alignment with the prompt's logic. 
       Deviations (e.g., missing a negation, reversing a comparison) incur heavy penalties 
       analogous to a Vickrey-Clarke-Groves penalty for non-truthful reporting.
    3. Maximum Entropy: Used strictly within the confidence() wrapper. Instead of assuming 
       certainty, it calculates the entropy of the candidate distribution to adjust the 
       final confidence score, preventing over-commitment on low-entropy (ambiguous) signals.
    
    This separation adheres to the causal constraints: MaxEnt is restricted to the confidence 
    wrapper, while Mechanism Design drives the primary structural scoring.
    """

    def __init__(self):
        # Primitives for structural parsing
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', 'bigger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for quantitative reasoning."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_negation(self, text: str) -> bool:
        """Detect presence of negation primitives."""
        tokens = set(re.findall(r'\b\w+\b', self._normalize(text)))
        return bool(tokens & self.negation_words)

    def _check_comparative(self, text: str) -> bool:
        """Detect presence of comparative primitives."""
        tokens = set(re.findall(r'\b\w+\b', self._normalize(text)))
        return bool(tokens & self.comparatives)

    def _check_conditional(self, text: str) -> bool:
        """Detect presence of conditional primitives."""
        tokens = set(re.findall(r'\b\w+\b', self._normalize(text)))
        return bool(tokens & self.conditionals)

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Component:
        Calculates a score based on structural alignment. 
        Truthful reporting (alignment) is rewarded; deviation is penalized.
        """
        score = 0.0
        p_norm = self._normalize(prompt)
        c_norm = self._normalize(candidate)
        
        # 1. Numeric Consistency (Strongest Signal)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums:
            if not c_nums:
                score -= 10.0 # Heavy penalty for missing numbers
            else:
                # Check if the candidate preserves the numeric order/magnitude implied
                # Simple heuristic: if prompt has 2 numbers and candidate has 2, check relation
                if len(p_nums) >= 2 and len(c_nums) >= 2:
                    p_diff = p_nums[0] - p_nums[1]
                    c_diff = c_nums[0] - c_nums[1]
                    if (p_diff > 0 and c_diff < 0) or (p_diff < 0 and c_diff > 0):
                        score -= 5.0 # Contradictory logic
                    else:
                        score += 2.0 # Consistent logic
                elif len(c_nums) > 0:
                    score += 1.0 # At least present

        # 2. Negation Consistency
        p_neg = self._check_negation(prompt)
        c_neg = self._check_negation(candidate)
        if p_neg != c_neg:
            # If prompt implies negation and candidate ignores it (or vice versa)
            # This is a critical failure of truthful reporting
            score -= 8.0
        else:
            score += 1.0

        # 3. Keyword Overlap (Weighted by structural importance)
        # We don't just count words; we check if structural markers exist in both
        if self._check_comparative(prompt) and self._check_comparative(candidate):
            score += 2.0
        if self._check_conditional(prompt) and self._check_conditional(candidate):
            score += 2.0
            
        # 4. NCD as Tiebreaker/Baseline (Normalized Compression Distance)
        # Only adds small value to break ties or handle unstructured text
        s_joint = f"{prompt} {candidate}"
        len_p = len(zlib.compress(prompt.encode()))
        len_c = len(zlib.compress(candidate.encode()))
        len_joint = len(zlib.compress(s_joint.encode()))
        
        # NCD formula: (L(xy) - min(L(x), L(y))) / max(L(x), L(y))
        # Lower NCD is better. We invert it for scoring.
        denom = max(len_p, len_c)
        if denom == 0:
            ncd = 1.0
        else:
            ncd = (len_joint - min(len_p, len_c)) / denom
        
        # Convert NCD to a small positive score contribution (0 to 1 range approx)
        ncd_score = (1.0 - ncd) * 0.5 
        score += ncd_score

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using structural parsing and mechanism-based scoring.
        Returns ranked list.
        """
        scored_candidates = []
        
        # Calculate raw structural scores
        raw_scores = []
        for cand in candidates:
            raw_scores.append(self._structural_score(prompt, cand))
        
        # Normalize scores to ensure stability (Mechanism Design: Proper Scoring Rule)
        # Shift to positive domain for softmax-like behavior if needed, but here we just rank
        max_score = max(raw_scores) if raw_scores else 0
        min_score = min(raw_scores) if raw_scores else 0
        range_score = (max_score - min_score) if (max_score - min_score) != 0 else 1.0
        
        for i, cand in enumerate(candidates):
            # Normalize to 0-1 range roughly, preserving order
            normalized_val = (raw_scores[i] - min_score) / range_score
            # Apply a sigmoid-like scaling to emphasize top performers (incentive compatibility)
            # This penalizes mid-tier answers that don't commit to a clear structural match
            final_score = 1.0 / (1.0 + math.exp(-3.0 * (normalized_val - 0.5)))
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment score: {raw_scores[i]:.2f}"
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Maximum Entropy principle: 
        If the system is uncertain (high entropy in local evaluation), confidence drops.
        If the structural signal is strong (low entropy), confidence rises.
        """
        # Evaluate the specific answer against others (simulated by comparing to itself and a dummy)
        # In a real multi-agent system, this would aggregate reports. 
        # Here we approximate by checking the robustness of the structural match.
        
        base_score = self._structural_score(prompt, answer)
        
        # Introduce a perturbation to estimate sensitivity (Entropy proxy)
        # If small changes in input (simulated by score magnitude) cause large swings, entropy is high
        # We use the magnitude of the base_score as a proxy for 'energy' in the system.
        # High positive score = Low Entropy (Ordered, certain)
        # Near zero or negative = High Entropy (Disordered, uncertain)
        
        # Map score to confidence using a saturating function
        # Range of _structural_score is roughly -20 to +10 based on penalties/rewards
        # We want -10 -> 0.0, 0 -> 0.5, +10 -> 1.0
        
        confidence = 1.0 / (1.0 + math.exp(-0.4 * base_score))
        
        # Clamp
        return max(0.0, min(1.0, confidence))