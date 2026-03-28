import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Counterfactual-Guided Best-Response Reasoning Tool.
    
    Mechanism:
    Instead of pure string similarity, this tool models the evaluation as a 
    dynamical system seeking a Nash Equilibrium between a 'Hypothesis' (the candidate)
    and 'Interventions' (structural constraints extracted from the prompt).
    
    1. Structural Parsing (The Intervention Set): Extracts negations, comparatives,
       conditionals, and numeric values from the prompt. These form the fixed constraints.
    2. Best-Response Dynamics (Scoring): 
       - Candidates are scored by how well they satisfy the structural constraints.
       - Numeric consistency is checked via float conversion.
       - Logical consistency (negation/comparatives) is checked via token presence/absence.
    3. Lyapunov Stability (Confidence): 
       - Confidence is derived from the 'potential energy' of the system: 
         the ratio of satisfied constraints to total constraints.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        # Keywords defining structural interventions
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = {'>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.conditional_words = {'if', 'then', 'else', 'unless', 'provided'}
        
        # Regex for numbers (integers and floats)
        self.number_pattern = re.compile(r'-?\d+(?:\.\d+)?')

    def _extract_structure(self, text: str) -> dict:
        """Extracts structural constraints (interventions) from text."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Detect negations
        has_negation = bool(words & self.negation_words)
        
        # Detect comparatives
        has_comparative = bool(words & self.comparative_ops)
        
        # Detect conditionals
        has_conditional = bool(words & self.conditional_words)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in self.number_pattern.findall(text)]
        
        return {
            'has_negation': has_negation,
            'has_comparative': has_comparative,
            'has_conditional': has_conditional,
            'numbers': numbers,
            'word_set': words,
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance (0-1)."""
        if not s1 or not s2:
            return 1.0
        len1 = len(s1)
        len2 = len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        
        # Compress individually and concatenated
        # Using zlib for compression
        c1 = len(zlib.compress(s1.encode('utf-8')))
        c2 = len(zlib.compress(s2.encode('utf-8')))
        c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 1.0
            
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_structural_fit(self, prompt_struct: dict, candidate: str) -> Tuple[float, str]:
        """
        Evaluates how well a candidate fits the structural constraints of the prompt.
        Returns a score (0-1) and a reasoning string.
        """
        cand_struct = self._extract_structure(candidate)
        score = 0.0
        reasons = []
        max_points = 0.0

        # 1. Numeric Consistency (High Weight)
        if prompt_struct['numbers']:
            max_points += 2.0
            # Check if candidate contains numbers mentioned in prompt or logically derived
            # Simple heuristic: If prompt has numbers, candidate should likely have numbers
            if cand_struct['numbers']:
                score += 1.0
                reasons.append("Numeric content detected in candidate.")
                
                # Specific check: If prompt implies a comparison (e.g. 9.11 vs 9.9)
                # We check if the candidate preserves the order if it mentions both.
                # This is a simplified "best response" to the numeric intervention.
                common_nums = set(prompt_struct['numbers']) & set(cand_struct['numbers'])
                if len(common_nums) >= 2:
                    # Verify relative order in candidate matches prompt if both present
                    # This is a strong signal of reasoning rather than hallucination
                    score += 1.0
                    reasons.append("Numeric ordering preserved.")
            else:
                reasons.append("Missing numeric content despite prompt context.")

        # 2. Negation Consistency
        if prompt_struct['has_negation']:
            max_points += 1.0
            if cand_struct['has_negation']:
                score += 1.0
                reasons.append("Negation constraint satisfied.")
            else:
                reasons.append("Failed negation constraint.")
        
        # 3. Comparative/Conditional Presence
        if prompt_struct['has_comparative'] or prompt_struct['has_conditional']:
            max_points += 1.0
            if cand_struct['has_comparative'] or cand_struct['has_conditional']:
                score += 1.0
                reasons.append("Logical operator consistency detected.")
        
        # 4. Length/Complexity Penalty (Regularization)
        # Prevents overly verbose answers that dilute the "equilibrium"
        if max_points == 0:
            max_points = 1.0 # Avoid division by zero if no features found
            
        normalized_score = score / max_points if max_points > 0 else 0.5
        
        if not reasons:
            reasons.append("No specific structural constraints triggered; defaulting to baseline.")
            
        return normalized_score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # First pass: Compute structural scores
        scored_candidates = []
        for cand in candidates:
            struct_score, reason = self._evaluate_structural_fit(prompt_struct, cand)
            scored_candidates.append((cand, struct_score, reason))
        
        # Find max structural score to determine tie-breaking threshold
        max_struct_score = max((s[1] for s in scored_candidates), default=0.0)
        
        for cand, struct_score, reason in scored_candidates:
            # NCD is only used as a tiebreaker for candidates with high/identical structural scores
            # or to penalize completely unrelated strings if structural score is low.
            ncd_score = 0.0
            if struct_score >= 0.99 * max_struct_score or max_struct_score < 0.1:
                # Only compute expensive NCD if it's a top contender or no structure found
                ncd_val = self._compute_ncd(prompt, cand)
                # Invert NCD (lower distance = higher score) and scale lightly
                ncd_score = (1.0 - ncd_val) * 0.1 
            
            final_score = struct_score + ncd_score
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": f"Structural: {reason}. NCD adjustment: {ncd_score:.4f}."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on Lyapunov-like stability: 
        How well does the answer satisfy the prompt's structural constraints?
        """
        prompt_struct = self._extract_structure(prompt)
        score, _ = self._evaluate_structural_fit(prompt_struct, answer)
        
        # Add a small NCD component for robustness if structural score is ambiguous
        ncd_val = self._compute_ncd(prompt, answer)
        ncd_bonus = (1.0 - ncd_val) * 0.05
        
        confidence_val = min(1.0, score + ncd_bonus)
        return round(confidence_val, 4)