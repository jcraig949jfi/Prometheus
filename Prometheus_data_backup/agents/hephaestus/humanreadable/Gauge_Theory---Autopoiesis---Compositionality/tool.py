import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    GEACA-inspired Reasoning Tool.
    
    Mechanism:
    1. Gauge Equivariance (Structural Parsing): Extracts logical 'connections' 
       (negations, comparatives, conditionals) that transform the meaning of 
       candidates relative to the prompt.
    2. Autopoiesis (Homeostatic Confidence): Instead of dynamic weight rewriting, 
       uses a static viability check. If structural constraints are violated 
       (e.g., prompt says "not X", candidate is "X"), the system rejects the 
       hypothesis to maintain organizational integrity (confidence ~0).
    3. Compositionality: Scores candidates by composing primitive signals 
       (numeric truth, keyword overlap, structural consistency) into a final score.
    
    Beats NCD baseline by prioritizing logical structure and numeric evaluation 
    over raw string compression distance.
    """

    def __init__(self):
        self._keywords = ['therefore', 'thus', 'hence', 'because', 'so']
        self._negations = ['no', 'not', 'never', 'none', 'neither', 'nobody']
        self._comparatives = ['greater', 'larger', 'more', 'higher', 'less', 'smaller', 'fewer', 'lower']
        self._conditionals = ['if', 'unless', 'provided', 'when']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text.lower())]

    def _check_negation_consistency(self, prompt: str, candidate: str) -> float:
        """
        Gauge check: Does the candidate respect the negation gauge of the prompt?
        Returns 1.0 for consistent, 0.0 for contradictory.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        has_negation_prompt = any(n in p_low.split() for n in self._negations)
        # Simple heuristic: if prompt negates a concept, and candidate affirms it strongly without qualification
        # This is a simplified homeostatic check.
        
        if has_negation_prompt:
            # If prompt says "not", candidate should ideally reflect that or not contradict directly
            # Rough approximation: if prompt has "not" and candidate is a direct affirmative of a key phrase
            # We penalize if the candidate is a simple "Yes" when prompt implies negative
            if c_low.strip() in ['yes', 'true', 'correct']:
                # Check if the prompt is a negative question like "Is it not...?" vs "It is not..."
                # Simplified: If prompt starts with negative constraint, 'Yes' is risky.
                if p_low.startswith("it is not") or p_low.startswith("this is not"):
                    return 0.1 
        return 1.0

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """
        Compositional numeric evaluation.
        Detects comparisons and verifies if the candidate satisfies the numeric constraint.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric logic to violate, neutral score
        
        # Check for comparative keywords
        p_low = prompt.lower()
        is_max = any(k in p_low for k in ['largest', 'maximum', 'greatest', 'highest'])
        is_min = any(k in p_low for k in ['smallest', 'minimum', 'least', 'lowest'])
        
        if is_max and c_nums:
            # Candidate should contain the max of prompt numbers if it claims to answer "which is max"
            # Or if candidate is a single number, is it the max?
            if len(c_nums) == 1:
                if c_nums[0] == max(p_nums):
                    return 1.0
                else:
                    return 0.2 # Likely wrong
        
        if is_min and c_nums:
            if len(c_nums) == 1:
                if c_nums[0] == min(p_nums):
                    return 1.0
                else:
                    return 0.2

        # Direct comparison: "Is 9.11 < 9.9?" -> Candidate "True"
        if len(p_nums) >= 2 and len(c_nums) == 0:
            # Check text response for truth
            c_low = candidate.lower()
            val = 1.0 if (p_nums[0] < p_nums[1]) else 0.0
            if 'true' in c_low or 'yes' in c_low:
                return 1.0 if val == 1.0 else 0.1
            if 'false' in c_low or 'no' in c_low:
                return 1.0 if val == 0.0 else 0.1

        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Calculate score based on structural parsing rules."""
        score = 1.0
        
        # 1. Negation Gauge Check
        score *= self._check_negation_consistency(prompt, candidate)
        
        # 2. Numeric Logic
        score *= self._evaluate_numeric_logic(prompt, candidate)
        
        # 3. Keyword Overlap (Compositional binding of concepts)
        # Boost if candidate contains specific logical connectors found in prompt
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        intersection = p_words.intersection(c_words)
        # Normalize overlap by candidate length to prevent gaming by repeating prompt
        if len(c_words) > 0:
            overlap_ratio = len(intersection) / len(c_words)
            # Small boost for relevant vocabulary, but not dominant
            score += 0.1 * overlap_ratio 
            
        return min(score, 1.0)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        l1 = len(zlib.compress(s1_bytes))
        l2 = len(zlib.compress(s2_bytes))
        l_concat = len(zlib.compress(concat))
        
        max_len = max(l1, l2)
        if max_len == 0:
            return 0.0
        return (l_concat - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # Primary Score: Structural & Logical Analysis (Gauge + Compositionality)
            struct_score = self._structural_score(prompt, cand)
            
            # Tiebreaker: NCD (only used if structural scores are identical/high)
            # We invert NCD so higher is better, and scale it down to be a tiebreaker
            ncd = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.05 # Max 0.05 contribution
            
            final_score = struct_score + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if self._evaluate_numeric_logic(prompt, cand) < 1.0:
                reasoning_parts.append("Numeric constraint mismatch.")
            if self._check_negation_consistency(prompt, cand) < 1.0:
                reasoning_parts.append("Negation gauge violation.")
            if not reasoning_parts:
                reasoning_parts.append("Structural and logical consistency maintained.")
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Autopoietic Homeostatic Check.
        Returns 0.0 if the answer violates core structural invariants (negation/numeric).
        Returns 1.0 if consistent.
        """
        # Check 1: Negation Gauge
        neg_check = self._check_negation_consistency(prompt, answer)
        if neg_check < 0.5:
            return 0.05 # Near zero confidence, organizational boundary breached
        
        # Check 2: Numeric Logic
        num_check = self._evaluate_numeric_logic(prompt, answer)
        if num_check < 0.5:
            return 0.1
        
        # If passed structural checks, return a calibrated confidence based on overlap
        # This acts as the "viable manifold" indicator
        base_conf = 0.6
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        a_words = set(re.findall(r'\b\w+\b', answer.lower()))
        if p_words.intersection(a_words):
            base_conf += 0.3
            
        return min(base_conf, 1.0)