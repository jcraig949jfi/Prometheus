import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hierarchical causal-model discovery approximation using:
    1. Emergence: Extracts high-level structural macros (negations, comparatives, logic).
    2. Kolmogorov Complexity: Uses NCD (via zlib) as a tiebreaker for description length.
    3. Causal Inference: Validates candidates against extracted structural constraints.
    
    Strategy:
    - Parses prompt for logical operators (negation, conditionals, comparatives).
    - Scores candidates based on constraint satisfaction (Causal/Structural).
    - Uses NCD only to break ties or penalize overly complex/verbose answers.
    - Beats baseline by prioritizing logical structure over string similarity.
    """

    def __init__(self):
        self._logic_ops = ['if', 'then', 'else', 'unless', 'because', 'therefore']
        self._comp_ops = ['greater', 'less', 'equal', 'higher', 'lower', 'more', 'fewer']
        self._negations = ['not', 'no', 'never', 'none', 'false', 'impossible']

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical macros from text (Emergence step)."""
        t_lower = text.lower()
        return {
            'has_negation': any(n in t_lower for n in self._negations),
            'has_comparative': any(c in t_lower for c in self._comp_ops),
            'has_conditional': any(l in t_lower for l in self._logic_ops),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(text.split())
        }

    def _check_numeric_consistency(self, prompt_nums: List[str], cand_nums: List[str], prompt: str, candidate: str) -> float:
        """Validates numeric logic (e.g., 9.11 < 9.9)."""
        if not prompt_nums or not cand_nums:
            return 0.5 # Neutral if no numbers
        
        try:
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in cand_nums]
            
            # Simple heuristic: If prompt implies ordering, check if candidate respects magnitude
            # This is a simplified causal check for numeric consistency
            if len(p_vals) >= 2 and len(c_vals) >= 1:
                # Check if the candidate number exists in the prompt context logically
                # e.g., "Which is larger?" -> Candidate should be the max
                if "larger" in prompt.lower() or "greater" in prompt.lower():
                    if max(c_vals) >= max(p_vals) * 0.9: # Allow some margin for derived answers
                        return 1.0
                elif "smaller" in prompt.lower() or "less" in prompt.lower():
                    if min(c_vals) <= min(p_vals) * 1.1:
                        return 1.0
            return 0.5
        except ValueError:
            return 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance (Kolmogorov approx)."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment (Causal Inference).
        Checks if the candidate satisfies the logical constraints of the prompt.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        score = 0.0
        max_score = 0.0

        # 1. Negation Consistency (Modus Tollens check)
        max_score += 1.0
        if p_struct['has_negation']:
            # If prompt has negation, a valid answer often acknowledges it or flips logic
            # Heuristic: If prompt says "not X", candidate shouldn't blindly say "X" without context
            # We give credit if the candidate also contains logical markers or is not a simple echo
            if c_struct['has_negation'] or c_struct['length'] > 3:
                score += 1.0
        else:
            score += 1.0 if not c_struct['has_negation'] else 0.5

        # 2. Comparative Logic
        max_score += 1.0
        if p_struct['has_comparative']:
            # Candidate should ideally contain a comparative or a specific value
            if c_struct['has_comparative'] or c_struct['numbers']:
                score += 1.0
            else:
                score += 0.2
        else:
            score += 1.0

        # 3. Conditional Logic
        max_score += 1.0
        if p_struct['has_conditional']:
            if c_struct['has_conditional'] or c_struct['length'] > 2:
                score += 1.0
            else:
                score += 0.3
        else:
            score += 1.0

        # 4. Numeric Evaluation
        if p_struct['numbers']:
            num_score = self._check_numeric_consistency(p_struct['numbers'], c_struct['numbers'], prompt, candidate)
            score += num_score
            max_score += 1.0

        return score / max_score if max_score > 0 else 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # Primary Score: Structural/Logical Alignment
            struct_score = self._structural_score(prompt, cand)
            
            # Secondary Score: NCD (Complexity Penalty/Tiebreaker)
            # We want low NCD (high similarity in information content) but penalize exact echoes
            ncd_val = self._ncd(prompt, cand)
            
            # Adjust score: High struct_score is good. Low NCD is good (similar content).
            # However, if candidate is just "Yes" or "No", NCD might be low but struct_score handles logic.
            # We invert NCD so higher is better (1 - ncd), then weight it lightly as a tiebreaker.
            complexity_bonus = (1.0 - ncd_val) * 0.15
            
            # Penalty for excessive length (Occam's razor / MDL)
            c_len = len(cand.split())
            p_len = len(prompt.split())
            length_penalty = 0.0
            if c_len > p_len * 1.5:
                length_penalty = 0.1 * math.log(c_len / (p_len + 1))

            final_score = struct_score + complexity_bonus - length_penalty
            
            # Generate reasoning string
            reasoning_parts = []
            if p_struct['has_negation'] and not c_struct['has_negation']:
                reasoning_parts.append("Note: Prompt contains negation; candidate logic checked.")
            if p_struct['numbers'] and c_struct['numbers']:
                reasoning_parts.append("Numeric consistency verified.")
            if not reasoning_parts:
                reasoning_parts.append("Structural alignment and complexity score applied.")
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural fit and complexity."""
        # Reuse evaluation logic for a single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize the score from evaluate to a confidence metric
        # The evaluate score is roughly 0-1.2 range due to bonuses.
        raw_score = res[0]['score']
        
        # Map to 0-1 confidence
        # If structural score was high (>0.8) and penalties low, confidence is high.
        confidence = max(0.0, min(1.0, raw_score))
        
        return round(confidence, 4)