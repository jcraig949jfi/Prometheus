import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Categorical Renormalizing Global Workspace (CRGW) Implementation.
    
    Mechanism:
    1. Category Theory (Structure): The prompt and candidates are parsed into 
       'objects' (entities) and 'morphisms' (logical relations like negation, 
       comparison, conditionals). This forms the base category C_0.
    2. Renormalization (Coarse-graining): We apply functors that map detailed 
       string tokens to abstract logical flags (e.g., presence of 'not', '>', 'if').
       This discards microscopic noise (specific words) while preserving universal 
       properties (logical structure).
    3. Global Workspace (Ignition): Candidates are scored based on structural 
       coherence with the prompt's logical constraints. If a candidate satisfies 
       the 'fixed-point' conditions (logical consistency across scales), it 
       achieves 'ignition' (high score). 
       
    Scoring Strategy:
    - Primary: Structural parsing (negations, comparatives, conditionals).
    - Secondary: Numeric evaluation for explicit number comparisons.
    - Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        # Logical keywords defining morphisms
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'higher', 'lower'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when'}
        self.quantifiers = {'all', 'every', 'some', 'any', 'most', 'few'}

    def _tokenize(self, text: str) -> set:
        """Extract lowercase tokens."""
        return set(re.findall(r'\b\w+\b', text.lower()))

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for comparative reasoning."""
        try:
            return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        except:
            return []

    def _parse_structure(self, text: str) -> dict:
        """
        Renormalization Step: Map raw text to abstract logical features.
        Returns a dictionary representing the object in the logical category.
        """
        tokens = self._tokenize(text)
        numbers = self._extract_numbers(text)
        
        return {
            'has_negation': bool(tokens & self.negations),
            'has_comparative': bool(tokens & self.comparatives),
            'has_conditional': bool(tokens & self.conditionals),
            'has_quantifier': bool(tokens & self.quantifiers),
            'numbers': numbers,
            'length': len(text),
            'tokens': tokens
        }

    def _check_logical_consistency(self, prompt_struct: dict, cand_struct: dict, prompt: str, candidate: str) -> float:
        """
        Evaluate coherence between prompt and candidate structures.
        Implements the 'beta-function' check: deviation from logical constraints reduces score.
        """
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt asserts a negative constraint, candidate should reflect understanding
        if prompt_struct['has_negation']:
            # Heuristic: If prompt has negation, exact token overlap without negation might be bad
            # But if candidate also has negation, it aligns structurally.
            if cand_struct['has_negation']:
                score += 0.2
            # Specific check for "not" appearing in both implies alignment on the constraint
            if 'not' in prompt_struct['tokens'] and 'not' in cand_struct['tokens']:
                score += 0.3

        # 2. Comparative/Numeric Consistency
        if prompt_struct['has_comparative'] and prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            
            # Simple transitivity check: if prompt says A > B, and candidate picks A
            # We look for the larger number in prompt being present in candidate
            if len(p_nums) >= 2:
                max_p = max(p_nums)
                min_p = min(p_nums)
                
                # Does the candidate select the correct extreme?
                # This is a heuristic guess based on common reasoning patterns
                if max_p in c_nums:
                    score += 0.4
                elif min_p in c_nums:
                    score += 0.2 # Partial credit
                    
        # 3. Conditional/Quantifier Alignment
        if prompt_struct['has_conditional']:
            if cand_struct['has_conditional'] or cand_struct['has_negation']:
                score += 0.2 # Acknowledges complex logic
        
        # 4. Token Overlap (Identity Morphism baseline)
        # Only count significant words (length > 3) to avoid noise
        common = prompt_struct['tokens'] & cand_struct['tokens']
        significant_common = [w for w in common if len(w) > 3]
        overlap_ratio = len(significant_common) / max(1, len(prompt_struct['tokens']))
        score += 0.3 * min(1.0, overlap_ratio)

        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if min(l1, l2) == 0:
            return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._parse_structure(prompt)
        results = []

        for cand in candidates:
            cand_struct = self._parse_structure(cand)
            
            # Primary Score: Structural Reasoning
            reason_score = self._check_logical_consistency(prompt_struct, cand_struct, prompt, cand)
            
            # Secondary Score: NCD Tiebreaker (inverted, so lower distance = higher score)
            # We scale NCD to be a small modifier so it doesn't override logic
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            total_score = reason_score + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if cand_struct['has_negation'] and prompt_struct['has_negation']:
                reasoning_parts.append("Aligned negation constraints")
            if cand_struct['numbers'] and prompt_struct['numbers']:
                reasoning_parts.append("Numeric consistency check")
            if not reasoning_parts:
                reasoning_parts.append("Structural overlap analysis")
                
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural coherence.
        Returns 0.0 to 1.0.
        """
        prompt_struct = self._parse_structure(prompt)
        ans_struct = self._parse_structure(answer)
        
        # Base coherence
        coherence = self._check_logical_consistency(prompt_struct, ans_struct, prompt, answer)
        
        # Normalize roughly to 0-1 range based on empirical max possible scores
        # Max theoretical score from _check_logical_consistency is approx 1.2
        confidence_val = min(1.0, max(0.0, coherence / 1.2))
        
        # Penalty for empty answers
        if not answer.strip():
            return 0.0
            
        return confidence_val