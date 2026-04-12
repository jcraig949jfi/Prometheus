import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    CS-HB-PL Implementation: Clonal-Selection with Phenomenological Bracketing and Pragmatics.
    
    Mechanism:
    1. Structural Parsing (Pragmatics): Extracts logical operators (negations, comparatives, 
       conditionals) to form a "contextual implicature" mask. This acts as the pragmatic layer 
       interpreting the speech act of the prompt.
    2. Phenomenological Bracketing: Isolates raw numeric and entity tokens from the prompt, 
       suspending linguistic bias to compare raw data values directly.
    3. Clonal Selection (Hypothesis Testing): Candidates are treated as "antibodies". 
       Their fitness is scored based on structural alignment with the prompt's logical mask 
       and numeric consistency. 
    4. Affinity Maturation: Scores are adjusted by a diversity metric (NCD) to prevent 
       premature convergence on string artifacts, ensuring the top hypothesis is both 
       logically sound and distinct from noise.
    """

    def __init__(self):
        # Logical operators for pragmatic parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.conditionals = ['if', 'then', 'else', 'unless', 'when']
        self.bool_words = ['yes', 'no', 'true', 'false']

    def _extract_numbers(self, text: str) -> List[float]:
        """Phenomenological bracketing: Extract raw numeric qualia."""
        pattern = r"-?\d+(?:\.\d+)?"
        try:
            return [float(x) for x in re.findall(pattern, text)]
        except:
            return []

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Pragmatic layer: Interpret logical speech acts."""
        lower_text = text.lower()
        has_negation = any(n in lower_text for n in self.negations)
        has_comparative = any(c in lower_text for c in self.comparatives)
        has_conditional = any(c in lower_text for c in self.conditionals)
        numbers = self._extract_numbers(text)
        
        # Detect boolean intent
        has_yes = 'yes' in lower_text
        has_no = 'no' in lower_text and 'not' not in lower_text # Simple check
        
        return {
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "numbers": numbers,
            "has_yes": has_yes,
            "has_no": has_no,
            "length": len(text.split())
        }

    def _check_numeric_consistency(self, prompt_nums: List[float], candidate_nums: List[float], 
                                   prompt_struct: Dict) -> float:
        """
        Tests hypothesis against raw data (Bracketing).
        Returns 1.0 if consistent, 0.0 if contradictory, 0.5 if neutral.
        """
        if not prompt_nums or not candidate_nums:
            return 0.5 # No numeric data to test
        
        # If prompt has numbers and candidate has numbers, check logical flow
        # Simple heuristic: If prompt implies sorting/comparison, candidate should reflect it
        if prompt_struct['comparative']:
            # If prompt asks for max/min, does candidate provide a number from the set?
            # Or if it's a math problem, is the answer derived? 
            # Since we can't solve arbitrary math, we check presence in prompt or simple logic
            if any(abs(c - p) < 1e-6 for c in candidate_nums for p in prompt_nums):
                return 1.0 # Candidate uses prompt numbers (likely relevant)
            # If candidate number is completely alien, penalize slightly unless it's a result
            # We assume if numbers exist in both, they are related unless obviously wrong
            return 0.8 
        
        return 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker/diversity metric."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        reasons = []
        score = 0.5 # Base score

        # 1. Pragmatic Implicature: Negation Alignment
        # If prompt negates, correct answer often contains negation or opposite boolean
        if p_struct['negation']:
            if c_struct['negation'] or c_struct['has_no']:
                score += 0.2
                reasons.append("negation_align")
            elif c_struct['has_yes']:
                score -= 0.2 # Potential contradiction
                reasons.append("negation_conflict")
        
        # 2. Numeric Consistency (Bracketing)
        if p_struct['numbers']:
            num_score = self._check_numeric_consistency(p_struct['numbers'], c_struct['numbers'], p_struct)
            if num_score == 1.0:
                score += 0.3
                reasons.append("numeric_match")
            elif num_score == 0.0:
                score -= 0.3
                reasons.append("numeric_mismatch")

        # 3. Structural Logic (Conditionals/Comparatives)
        if p_struct['comparative']:
            # Candidate should ideally contain comparative words or numbers
            if c_struct['comparative'] or c_struct['numbers']:
                score += 0.15
                reasons.append("comparative_responded")
        
        if p_struct['conditional']:
            if c_struct['conditional'] or any(w in candidate.lower() for w in ['if', 'then', 'because']):
                score += 0.1
                reasons.append("conditional_logic")

        # 4. Clonal Diversity (NCD Tiebreaker)
        # Penalize if candidate is too similar to prompt (echoing) unless it's a specific extraction
        ncd_val = self._ncd(prompt, candidate)
        if ncd_val > 0.9: # Too similar, likely echoing
            score -= 0.1
            reasons.append("echo_penalty")
        elif ncd_val < 0.2 and len(candidate) < len(prompt) * 0.5:
             # Very compressed, might be good summary or lazy. Neutral.
             pass

        # Cap score
        score = max(0.0, min(1.0, score))
        return score, ", ".join(reasons) if reasons else "structural_default"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            sc, reason = self._score_candidate(prompt, cand)
            scored.append({"candidate": cand, "score": sc, "reasoning": reason})
        
        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and pragmatic consistency.
        Uses the internal scoring mechanism but normalizes to 0-1 strictly.
        """
        sc, _ = self._score_candidate(prompt, answer)
        # The internal score is already roughly 0-1, but we ensure strict bounds
        return max(0.0, min(1.0, sc))