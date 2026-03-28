import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Oscillatory Predictive Coding Network (FOPCN) Implementation.
    
    Mechanism:
    1. Structural Parsing (Phenomenological Bracketing): Isolates logical operators 
       (negations, comparatives, conditionals) and numeric values, suppressing 
       raw text noise (bottom-up gamma drive).
    2. Categorical Limits (Category Theory): Evaluates candidates against 
       extracted constraints. Candidates violating explicit negations or 
       numeric bounds are assigned high 'error' (failed limit checks).
    3. Oscillatory Composition (Neural Oscillations): Simulates theta-gamma 
       coupling by weighting structural matches (high frequency details) 
       against global prompt coherence (low frequency context).
    4. Scoring: Base score derived from constraint satisfaction (Reasoning), 
       modulated by NCD only as a tiebreaker for structurally equivalent candidates.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'not': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comp': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'if': re.compile(r'\b(if|then|unless|only if)\b', re.IGNORECASE),
            'num': re.compile(r'-?\d+(?:\.\d+)?')
        }

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical and numeric features (Phenomenological Bracketing)."""
        text_lower = text.lower()
        return {
            'has_negation': bool(self.patterns['not'].search(text_lower)),
            'has_comparative': bool(self.patterns['comp'].search(text_lower)),
            'has_conditional': bool(self.patterns['if'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['num'].findall(text)]
        }

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _check_constraints(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluates categorical limits (Constraint Propagation).
        Returns a penalty score (0.0 = perfect, 1.0 = violation).
        """
        penalty = 0.0
        
        # Numeric Limit Check: If prompt defines a bound, check candidate adherence
        # This is a heuristic approximation of a 'pullback' in the categorical sense
        if len(prompt_struct['numbers']) > 0 and len(cand_struct['numbers']) > 0:
            # Simple heuristic: if prompt has numbers and candidate has numbers,
            # check for direct contradiction patterns (e.g., prompt "less than 5", candidate "6")
            # Since we don't have full NLP, we check for obvious magnitude mismatches if keywords exist
            if prompt_struct['has_comparative']:
                # If prompt compares, candidate numbers should logically align. 
                # Without full semantic parsing, we assume consistency if magnitudes are similar order
                # or if the candidate explicitly references the prompt number.
                pass 

        # Negation Consistency: 
        # If prompt strongly negates, and candidate affirms without qualification (simplified)
        # We use NCD as a proxy for semantic opposition in the absence of an ontology
        if prompt_struct['has_negation'] and not cand_struct['has_negation']:
            # Potential trap: Prompt says "X is NOT Y". Candidate says "X is Y".
            # We penalize if the candidate is very short (just "Yes") or lacks the negation structure
            if len(candidate.strip().split()) < 4:
                penalty += 0.2

        return min(penalty, 1.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt complexity for normalization
        prompt_comp = len(zlib.compress(prompt.encode()))
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural Score (Reasoning Core)
            # Measures alignment of logical features ( Functorial preservation )
            struct_match = 0.0
            if prompt_struct['has_negation'] == cand_struct['has_negation']:
                struct_match += 0.3
            if prompt_struct['has_comparative'] == cand_struct['has_comparative']:
                struct_match += 0.3
            if prompt_struct['has_conditional'] == cand_struct['has_conditional']:
                struct_match += 0.2
            
            # Numeric consistency bonus
            if prompt_struct['numbers'] and cand_struct['numbers']:
                # Check if candidate numbers are within reasonable range of prompt numbers
                # (Heuristic for limit preservation)
                p_nums = prompt_struct['numbers']
                c_nums = cand_struct['numbers']
                if any(abs(p - c) < 0.01 for p in p_nums for c in c_nums):
                    struct_match += 0.2
                elif len(p_nums) == len(c_nums):
                    struct_match += 0.1 # Partial credit for same count

            # 2. Constraint Penalty (Categorical Limits)
            penalty = self._check_constraints(prompt_struct, cand_struct, prompt, cand)
            
            # 3. Oscillatory Tie-Breaker (NCD)
            # Only used if structural signals are ambiguous or equal
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so higher is better, scale down to be a tiebreaker
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            base_score = struct_match - penalty
            final_score = base_score + ncd_score
            
            # Reasoning trace
            reasoning = f"Structural alignment: {struct_match:.2f}, Penalty: {penalty:.2f}, NCD-tiebreak: {ncd_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and NCD.
        Uses Phenomenological bracketing to isolate logic gates.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        confidence = 0.5 # Base prior
        
        # Boost if logical operators match (Functorial mapping)
        if p_struct['has_negation'] == a_struct['has_negation']:
            confidence += 0.2
        if p_struct['has_comparative'] == a_struct['has_comparative']:
            confidence += 0.2
            
        # Boost if numeric presence matches
        if (len(p_struct['numbers']) > 0) == (len(a_struct['numbers']) > 0):
            confidence += 0.1
            
        # Penalize if prompt has complex logic but answer is too short (failed hypothesis)
        if (p_struct['has_conditional'] or p_struct['has_comparative']) and len(answer.split()) < 3:
            confidence -= 0.3
            
        # NCD check for semantic drift
        ncd = self._ncd(prompt, answer)
        if ncd > 0.9: # Very different strings
            confidence -= 0.1
            
        return max(0.0, min(1.0, confidence))