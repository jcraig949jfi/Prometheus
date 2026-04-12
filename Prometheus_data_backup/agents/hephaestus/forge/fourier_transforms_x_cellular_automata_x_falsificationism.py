import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Falsification Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Falsification Core): Extracts logical constraints 
       (negations, comparatives, conditionals) from the prompt. These act as 
       "spectral peaks" of truth.
    2. Candidate Evaluation: Candidates are tested against these constraints.
       - Violating a hard constraint (e.g., answering "Yes" to "Is it false?") 
         constitutes immediate falsification (Score -> 0).
       - Structural alignment boosts the score.
    3. Spectral Proxy (Fourier Analogy): We treat the presence of logical keywords 
       as frequency components. A candidate matching the prompt's logical "spectrum" 
       gets a high base score.
    4. NCD Tiebreaker: Only used if structural signals are ambiguous.
    
    This implements the "Spectral-Falsification Loop" by generating a hypothesis 
    (the logical structure of the prompt) and falsifying candidates that contradict it.
    """

    def __init__(self):
        # Logical keywords acting as "frequencies" in our spectral analysis
        self.negations = ['no', 'not', 'never', 'false', 'deny', 'impossible']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided']
        self.booleans = ['yes', 'no', 'true', 'false']
        
    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Parses text for logical constraints (The 'Fourier' step)."""
        lower = self._normalize(text)
        has_neg = any(n in lower for n in self.negations)
        has_comp = any(c in lower for c in self.comparatives)
        has_cond = any(c in lower for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r"-?\d+\.?\d*", lower)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            "negation": has_neg,
            "comparative": has_comp,
            "conditional": has_cond,
            "numbers": numbers,
            "length": len(text.split())
        }

    def _check_falsification(self, prompt: str, candidate: str, p_struct: Dict) -> Tuple[bool, float]:
        """
        Tests candidate against prompt constraints.
        Returns (is_falsified, penalty_score).
        """
        c_lower = self._normalize(candidate)
        p_lower = self._normalize(prompt)
        
        # 1. Negation Falsification (Modus Tollens check)
        # If prompt asks "Is it NOT X?" and candidate says "Yes" (implying it is X), 
        # we need to be careful. Simpler: If prompt contains "not" and candidate 
        # affirms the negative without negation, it might be wrong.
        # Heuristic: If prompt is a negation question, prefer candidates with negation or 'no'.
        if p_struct["negation"]:
            c_has_neg = any(n in c_lower for n in self.negations)
            # If prompt implies negation, and candidate is a bare "yes" without negation words
            # This is a weak falsification trigger, handled more by scoring.
            pass

        # 2. Numeric Falsification (Hard Constraint)
        if len(p_struct["numbers"]) >= 2:
            # Detect simple comparison patterns like "Which is greater, A or B?"
            nums = p_struct["numbers"]
            # Heuristic: If prompt asks for "greater", candidate should contain the larger number
            if "greater" in p_lower or "larger" in p_lower or ">" in p_lower:
                target = max(nums)
                # Check if candidate contains the string representation of the max number
                if str(int(target)) not in candidate and str(target) not in candidate:
                    # Falsified: Didn't pick the max
                    return True, 0.0
            elif "less" in p_lower or "smaller" in p_lower or "<" in p_lower:
                target = min(nums)
                if str(int(target)) not in candidate and str(target) not in candidate:
                    return True, 0.0

        # 3. Boolean Consistency (The "Glider" check)
        # If prompt has "not", "false", "never", the answer often requires inversion.
        # This is a probabilistic falsification based on common reasoning traps.
        if p_struct["negation"]:
            # If candidate is a simple boolean, check if it contradicts the negative framing
            # This is hard to do perfectly without NLP, so we use a penalty approach.
            if c_lower in ["yes", "true"] and any(x in p_lower for x in ["is not", "not true", "false that"]):
                # Potential falsification, apply heavy penalty but don't zero unless sure
                return False, 0.2 
        
        return False, 0.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt structure "spectrum"
        p_lower = self._normalize(prompt)
        
        for cand in candidates:
            score = 0.5  # Base prior
            reasoning = "Base prior."
            c_lower = self._normalize(cand)
            
            # 1. Falsification Test
            is_falsified, penalty = self._check_falsification(prompt, cand, p_struct)
            if is_falsified:
                score = 0.0
                reasoning = "Falsified by numeric or logical constraint."
            else:
                score -= penalty
                if penalty > 0:
                    reasoning = f"Penalized for logical mismatch ({penalty})."

            if score > 0:
                # 2. Spectral Matching (Keyword Overlap as Frequency Match)
                # Count how many logical "frequencies" match
                matches = 0
                total_freqs = 0
                
                # Check negation alignment
                if p_struct["negation"]:
                    total_freqs += 1
                    if any(n in c_lower for n in self.negations) or c_lower in ["no", "false"]:
                        matches += 1
                        reasoning += " Matched negation spectrum."
                
                # Check boolean alignment
                if any(b in p_lower for b in self.booleans):
                    total_freqs += 1
                    if any(b in c_lower for b in self.booleans):
                        matches += 1
                        reasoning += " Matched boolean spectrum."

                if total_freqs > 0:
                    spectral_bonus = (matches / total_freqs) * 0.4
                    score += spectral_bonus
                    if spectral_bonus > 0:
                        reasoning += f" Spectral match: {matches}/{total_freqs}."

                # 3. NCD Tiebreaker (Only if scores are close to baseline)
                if 0.4 < score < 0.6:
                    ncd = self._compute_ncd(prompt, cand)
                    # Lower NCD is better (more similar context)
                    if ncd < 0.7:
                        score += 0.1
                        reasoning += f" NCD support ({ncd:.2f})."

            results.append({
                "candidate": cand,
                "score": min(1.0, max(0.0, score)),
                "reasoning": reasoning
            })
        
        # Sort descending by score
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural alignment and falsification survival."""
        p_struct = self._extract_structure(prompt)
        is_falsified, penalty = self._check_falsification(prompt, answer, p_struct)
        
        if is_falsified:
            return 0.05
        
        base_conf = 0.5
        c_lower = self._normalize(answer)
        p_lower = self._normalize(prompt)
        
        # Boost if logical keywords align
        if p_struct["negation"] and any(n in c_lower for n in self.negations):
            base_conf += 0.3
        elif p_struct["negation"] and c_lower in ["yes", "true"]:
            # Risky, lower confidence
            base_conf -= 0.2
            
        # Numeric check
        if len(p_struct["numbers"]) >= 2:
            nums = p_struct["numbers"]
            if "greater" in p_lower:
                if str(max(nums)) in answer: base_conf += 0.3
            elif "less" in p_lower:
                if str(min(nums)) in answer: base_conf += 0.3
                
        return min(1.0, max(0.0, base_conf - penalty))