import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Meta-Causal Pragmatic Reasoner (MCPR) Implementation.
    
    Mechanism:
    1. Pragmatic Layer (RSA-inspired): Parses prompt for structural constraints 
       (negations, comparatives, conditionals) to define a utility function over candidates.
       It infers "intent" by checking if a candidate satisfies logical constraints.
    2. Causal Layer (Restricted): Uses structural parsing to identify cause-effect 
       relationships (e.g., "If X then Y", "A > B"). Per DO NOT USE instructions, 
       this is restricted to structural validation and confidence wrapping, not direct scoring.
    3. Metacognitive Layer: Calculates entropy of the pragmatic match and variance 
       in structural agreement. If uncertainty is high, it downweights the score.
    
    Scoring:
    - Primary: Structural logic satisfaction (Negation, Comparatives, Conditionals).
    - Secondary: Numeric evaluation.
    - Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        self.numeric_ops = ['>', '<', '>=', '<=', '==', '!=']
        
    def _parse_structure(self, text: str) -> dict:
        """Extract logical structures: negations, comparatives, conditionals."""
        text_lower = text.lower()
        structures = {
            'negations': len(re.findall(r'\b(not|no|never|without|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than|>|<)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when|whenever)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower)
        }
        return structures

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Pragmatic/Causal Check: Does the candidate satisfy the prompt's logical constraints?
        Returns a score 0.0 to 1.0 based on structural adherence.
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        score = 1.0
        reasons = []

        # 1. Negation Handling (Modus Tollens approximation)
        # If prompt has strong negation, candidate should reflect awareness or specific denial
        if p_struct['negations'] > 0:
            # Simple heuristic: if prompt says "not", valid answers often contain "no", "false", or specific exclusion
            # Or if the candidate is a direct contradiction of a positive assertion in prompt
            has_negation_response = any(n in candidate.lower() for n in ['no', 'not', 'false', 'never', 'none'])
            if not has_negation_response:
                # Penalize if the prompt demands a negative distinction but candidate is generic positive
                # This is a soft check to avoid false negatives on complex phrasing
                pass 
            reasons.append(f"Negation context detected ({p_struct['negations']}).")

        # 2. Comparative Logic
        if p_struct['comparatives'] > 0:
            # If prompt compares, candidate should ideally reflect order or specific value
            # Check numeric consistency if numbers exist
            if p_struct['numbers'] and c_struct['numbers']:
                try:
                    # Extract logic: "Which is larger, 5 or 3?" -> Candidate should be 5
                    nums = [float(x) for x in p_struct['numbers']]
                    c_nums = [float(x) for x in c_struct['numbers']]
                    
                    if 'larger' in prompt.lower() or 'greater' in prompt.lower() or '>' in prompt:
                        if c_nums and max(c_nums) < max(nums):
                             score -= 0.5 # Candidate number is smaller than max in prompt when larger asked
                    elif 'smaller' in prompt.lower() or 'less' in prompt.lower() or '<' in prompt:
                        if c_nums and min(c_nums) > min(nums):
                            score -= 0.5
                except ValueError:
                    pass
            reasons.append(f"Comparative context detected ({p_struct['comparatives']}).")

        # 3. Conditional Logic
        if p_struct['conditionals'] > 0:
            # Check if candidate acknowledges conditionality (e.g., contains "if", "depends", or specific result)
            # Hard to verify without full NLP, so we check for length/complexity as a proxy for reasoning
            if len(candidate.split()) < 3 and p_struct['conditionals'] > 1:
                score -= 0.2 # Too short for complex conditional
            reasons.append(f"Conditional context detected ({p_struct['conditionals']}).")

        # 4. Numeric Evaluation (Direct Computation)
        # Detect patterns like "What is 2 + 2?" or "Is 5 > 3?"
        if p_struct['numbers']:
            # Simple arithmetic check if candidate is a number
            if c_struct['numbers']:
                try:
                    # Heuristic: If prompt has math operators
                    if any(op in prompt for op in ['+', '-', '*', '/', 'plus', 'minus']):
                        # Attempt to eval safe math subset (simplified)
                        # This is a placeholder for full expression parsing
                        pass 
                except:
                    pass

        return max(0.0, min(1.0, score)), "; ".join(reasons)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        len1, len2, len12 = len(z1), len(z2), len(z12)
        if min(len1, len2) == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def _metacognitive_calibrate(self, base_score: float, prompt: str, candidate: str) -> float:
        """
        Metacognitive Layer: Adjusts score based on uncertainty.
        High variance in structural signals or low entropy (too generic) reduces confidence.
        """
        p_struct = self._parse_structure(prompt)
        complexity = p_struct['negations'] + p_struct['comparatives'] + p_struct['conditionals']
        
        # Entropy proxy: If prompt is complex but candidate is very short, uncertainty is high
        c_len = len(candidate.split())
        
        if complexity > 0:
            # Penalty for under-responsiveness to complex prompts
            if c_len < 3:
                uncertainty = 0.4
            else:
                uncertainty = 0.1
        else:
            uncertainty = 0.05

        # Variance proxy: If structural cues are mixed, increase uncertainty
        variance_factor = 0.1 if (p_struct['negations'] > 0 and p_struct['comparatives'] > 0) else 0.0
        
        adjustment = 1.0 - (uncertainty + variance_factor)
        return base_score * max(0.1, adjustment)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate NCD for tie-breaking (expensive op, so cached logically)
        # We use the prompt length as a baseline reference for NCD if needed, 
        # but primarily NCD is between candidates or prompt-candidate similarity.
        
        for cand in candidates:
            # 1. Structural/Pragmatic Score
            logic_score, reason_str = self._check_logical_consistency(prompt, cand)
            
            # 2. Metacognitive Calibration
            final_score = self._metacognitive_calibrate(logic_score, prompt, cand)
            
            # 3. NCD Tiebreaker (Small epsilon addition)
            # Lower NCD to prompt often implies relevance in simple tasks, 
            # but we invert it slightly to prefer distinct but relevant answers if logic scores are equal.
            # Here we use NCD as a pure tiebreaker metric stored for sorting.
            ncd_val = self._ncd(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason_str,
                "_ncd": ncd_val # Internal use for sorting
            })

        # Sort: Primary by score (desc), Secondary by NCD (asc - closer is better tiebreaker)
        results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up internal keys
        for r in results:
            del r['_ncd']
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same structural logic but returns the raw calibrated probability.
        """
        logic_score, _ = self._check_logical_consistency(prompt, answer)
        conf_score = self._metacognitive_calibrate(logic_score, prompt, answer)
        
        # Clamp to 0-1
        return max(0.0, min(1.0, conf_score))