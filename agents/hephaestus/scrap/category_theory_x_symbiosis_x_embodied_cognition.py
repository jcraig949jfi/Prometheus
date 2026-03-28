import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Symbiotic Functorial Embodied Reasoner (SFER) - Computational Approximation.
    
    Mechanism:
    1. Category-Theoretic Core (Structural Parsing): Treats the prompt as a category
       where objects are entities and morphisms are logical constraints (negations,
       comparatives, conditionals). We extract these 'natural transformations' to
       form a structural signature.
    2. Embodied Loop (Numeric/Constraint Evaluation): Simulates the active-inference
       loop by evaluating the 'free energy' (error) of each candidate against the
       extracted logical constraints. Candidates are scored on how well they preserve
       the logical structure (e.g., if prompt says "A < B", candidate must respect it).
    3. Symbiotic Transfer (Confidence Wrapper): Per the causal analysis, 'Symbiosis'
       is an inhibitor for direct scoring. Instead, this layer acts as a confidence
       calibrator. It checks if the candidate 'swaps' well with the prompt's structural
       constraints (high compatibility = high confidence). If structural signals are
       weak, it falls back to NCD (tiebreaker) but penalizes the score to avoid
       the 'inhibitor' trap.
       
    This approach prioritizes structural parsing and numeric evaluation (High Value)
    while restricting symbiotic mechanisms to confidence calibration (Risk Mitigation).
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Functor" definitions)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            'logic_ops': re.compile(r'\b(and|or|but|however|therefore)\b', re.IGNORECASE)
        }

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical morphisms (constraints) from text."""
        text_lower = text.lower()
        structure = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_numbers': bool(self.patterns['numeric'].search(text_lower)),
            'word_count': len(text.split()),
            'numbers': [float(n) for n in self.patterns['numeric']..findall(text_lower)]
        }
        return structure

    def _check_numeric_consistency(self, prompt_nums: List[float], candidate_nums: List[float], prompt: str) -> float:
        """Embodied check: Does the candidate respect numeric implications?"""
        if not prompt_nums or not candidate_nums:
            return 1.0 # No numeric constraint to violate
        
        # Simple heuristic: If prompt has numbers and candidate has numbers,
        # check for gross contradictions (e.g. prompt implies small, candidate is huge)
        # Since we don't have full semantic parsing, we check magnitude alignment if counts match
        if len(prompt_nums) == len(candidate_nums):
            # Check relative ordering if multiple numbers exist
            if len(prompt_nums) > 1:
                p_diff = prompt_nums[0] - prompt_nums[1]
                c_diff = candidate_nums[0] - candidate_nums[1]
                if (p_diff > 0) != (c_diff > 0): # Sign mismatch in comparison
                    return 0.2
        return 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        if min(len_s1, len_s2) == 0:
            return 1.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        prompt_nums = prompt_struct['numbers']
        scored_candidates = []

        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural Parsing Score (Category Theory Core)
            # Reward matching logical complexity (e.g., if prompt is conditional, candidate should be too)
            struct_match = 0.0
            if prompt_struct['has_negation'] and cand_struct['has_negation']:
                struct_match += 0.3
                reasoning_parts.append("Matches negation structure")
            elif prompt_struct['has_negation'] and not cand_struct['has_negation']:
                # Potential mismatch unless candidate is explicitly affirmative
                pass 
            
            if prompt_struct['has_comparative'] and cand_struct['has_comparative']:
                struct_match += 0.3
                reasoning_parts.append("Matches comparative structure")
                
            if prompt_struct['has_conditional'] and cand_struct['has_conditional']:
                struct_match += 0.2
                reasoning_parts.append("Matches conditional structure")
            
            # Baseline for answering the prompt length/complexity
            if cand_struct['word_count'] > 0:
                struct_match += 0.2 
                
            score += struct_match

            # 2. Embodied Numeric Evaluation
            cand_nums = cand_struct['numbers']
            numeric_score = self._check_numeric_consistency(prompt_nums, cand_nums, prompt)
            if numeric_score < 1.0:
                reasoning_parts.append("Numeric inconsistency detected")
            score *= numeric_score # Penalty multiplier

            # 3. Symbiotic/Confidence Adjustment (Applied here as final filter)
            # If structural signal is weak, rely on NCD but cap the score (Inhibitor logic)
            if struct_match < 0.3:
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD (lower distance = higher score) but cap at 0.5 to reflect inhibitor risk
                ncd_score = (1.0 - ncd_val) * 0.5 
                score = max(score, ncd_score) 
                if ncd_score > score:
                    reasoning_parts.append("Low structural signal; fallback to compression similarity")
            else:
                reasoning_parts.append("Strong structural alignment")

            scored_candidates.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Baseline evaluation"
            })

        # Rank by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Symbiotic Transfer Operator for Confidence.
        Evaluates compatibility between prompt constraints and answer.
        Returns 0-1.
        """
        # Re-use evaluation logic for a single pair
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        base_score = results[0]['score']
        
        # Symbiotic Compatibility Check:
        # Does the answer 'swap' cleanly with the prompt's logical operators?
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        compatibility_bonus = 0.0
        
        # Check for logical contradiction (Simple heuristic)
        # If prompt has "no" and answer has "yes" without qualification, lower confidence
        if p_struct['has_negation'] and not a_struct['has_negation']:
            # Check if answer is a simple affirmative that might contradict
            if re.search(r'\b(yes|true|correct)\b', answer, re.IGNORECASE):
                compatibility_bonus -= 0.2
        
        # Final confidence calculation
        # Base score is 0-1 roughly. Max out at 1.0.
        final_conf = min(1.0, max(0.0, base_score + compatibility_bonus))
        
        # Deterministic noise reduction: If structural match was high, boost confidence
        if p_struct['has_comparative'] and a_struct['has_comparative']:
            final_conf = min(1.0, final_conf + 0.1)
            
        return round(final_conf, 4)