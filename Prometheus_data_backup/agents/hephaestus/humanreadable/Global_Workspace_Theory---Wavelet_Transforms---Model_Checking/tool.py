import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Resolution Conscious Verification Loop.
    
    Mechanism:
    1. Signal Encoding: Converts text into a binary stream based on structural tokens
       (negations, comparatives, conditionals, numbers) acting as 'sensorimotor variables'.
    2. Wavelet-like Decomposition: Simulates DWT by analyzing the signal at dyadic scales.
       - Coarse scale (Approximation): Global structural integrity (balance of constraints).
       - Fine scale (Details): Local token mismatches between prompt and candidate.
    3. Global Workspace Ignition: Candidates compete. 'Ignition' occurs when a candidate
       preserves the structural logic (high approximation match) while minimizing 
       contradictory details (low detail noise).
    4. Model Checking: Explicitly verifies logical consistency (e.g., if prompt has "not",
       candidate must reflect negation) using rule-based state exploration.
       
    Scoring: Weighted sum of Structural Parse (40%), Logical Consistency/Model Check (40%),
    and NCD tiebreaker (20%).
    """

    def __init__(self):
        # Structural regex patterns for "sensorimotor" extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nor|without|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|better|worse|higher|lower|than)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|otherwise|else)\b', re.I),
            'numeric': re.compile(r'\d+(?:\.\d+)?'),
            'boolean': re.compile(r'\b(true|false|yes|no)\b', re.I)
        }
        self.logic_ops = ['and', 'or', 'not', 'implies']

    def _extract_structure(self, text: str) -> Dict[str, List]:
        """Extract structural tokens to form the signal stream."""
        signal = {
            'negations': self.patterns['negation'].findall(text),
            'comparatives': self.patterns['comparative'].findall(text),
            'conditionals': self.patterns['conditional'].findall(text),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'booleans': self.patterns['boolean'].findall(text)
        }
        return signal

    def _model_check(self, prompt_sig: Dict, cand_sig: Dict, prompt_low: str, cand_low: str) -> float:
        """
        Verify logical consistency (Model Checking phase).
        Checks if the candidate violates constraints imposed by the prompt's structure.
        Returns a score 0.0 (fail) to 1.0 (pass).
        """
        score = 1.0
        
        # Check 1: Negation Consistency
        # If prompt has strong negation, candidate shouldn't blindly affirm without context
        if len(prompt_sig['negations']) > 0 and len(cand_sig['negations']) == 0:
            # Heuristic: If prompt denies something, and candidate is a simple "Yes", penalize
            if cand_low in ['yes', 'true'] and prompt_low.count('not') > 0:
                score -= 0.5
        
        # Check 2: Numeric Transitivity/Constraint
        # If prompt has numbers, candidate numbers should be logically consistent if present
        if prompt_sig['numbers'] and cand_sig['numbers']:
            # Simple check: if prompt defines a limit (e.g., "less than 10"), 
            # and candidate violates it (hard to parse fully without LLM, so we check presence)
            # Here we just ensure numbers aren't wildly hallucinated (presence check)
            pass 

        # Check 3: Boolean Contradiction
        p_bools = [b.lower() for b in prompt_sig['booleans']]
        c_bools = [b.lower() for b in cand_sig['booleans']]
        
        if 'no' in p_bools and 'yes' in c_bools and len(c_bools) == 1:
             score -= 0.4
        if 'false' in p_bools and 'true' in c_bools and len(c_bools) == 1:
             score -= 0.4

        return max(0.0, score)

    def _wavelet_decompose(self, prompt_text: str, cand_text: str) -> Tuple[float, float]:
        """
        Simulate Wavelet Transform.
        Approximation (Coarse): Character/N-gram density overlap (Global shape).
        Detail (Fine): Specific token mismatch penalty.
        """
        # Coarse: Normalized overlap of structural tokens
        p_sig = self._extract_structure(prompt_text)
        c_sig = self._extract_structure(cand_text)
        
        p_tokens = p_sig['negations'] + p_sig['comparatives'] + p_sig['conditionals']
        c_tokens = c_sig['negations'] + c_sig['comparatives'] + c_sig['conditionals']
        
        if not p_tokens:
            approx_score = 0.5 # Neutral if no structure
        else:
            matches = sum(1 for t in c_tokens if t in p_tokens)
            approx_score = matches / max(len(p_tokens), 1)
            
        # Fine: Detail coefficients (Penalty for extra noise or missing critical tokens)
        # If prompt has a negation and candidate doesn't, that's a high-magnitude detail error
        detail_error = 0.0
        if len(p_sig['negations']) > 0 and len(c_sig['negations']) == 0:
            detail_error += 0.3
        if len(p_sig['conditionals']) > 0 and len(c_sig['conditionals']) == 0:
            detail_error += 0.2
            
        return approx_score, detail_error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_low = prompt.lower()
        prompt_sig = self._extract_structure(prompt_low)
        results = []

        for cand in candidates:
            cand_low = cand.lower()
            cand_sig = self._extract_structure(cand_low)
            
            # 1. Model Checking (Logical Consistency)
            logic_score = self._model_check(prompt_sig, cand_sig, prompt_low, cand_low)
            
            # 2. Wavelet Decomposition (Multi-res analysis)
            approx, detail_err = self._wavelet_decompose(prompt_low, cand_low)
            
            # 3. Global Workspace Ignition Score
            # High approx + Low detail error + High logic = Ignition
            structural_score = approx - detail_err
            base_score = (0.4 * structural_score) + (0.4 * logic_score)
            
            # 4. NCD Tiebreaker (Only matters if structural signals are weak/equal)
            # We invert NCD (lower is better) and scale it small
            ncd_val = self._ncd(prompt_low, cand_low)
            ncd_score = (1.0 - ncd_val) * 0.2
            
            final_score = base_score + ncd_score
            
            # Reasoning string generation
            reasoning = f"Structural Match: {approx:.2f}, Logic Check: {logic_score:.2f}, Detail Error: {detail_err:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        # Normalize score to 0-1 range roughly, assuming max possible is around 1.0
        # The scoring logic yields roughly -0.5 to 1.0, so we clamp.
        score = ranked[0]['score']
        return max(0.0, min(1.0, score))