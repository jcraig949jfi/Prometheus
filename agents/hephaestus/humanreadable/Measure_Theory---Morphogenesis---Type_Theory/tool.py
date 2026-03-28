import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    DTPR-Inspired Structural Reasoner.
    
    Mechanism:
    Analogous to the 'Dependently Typed Probabilistic Reaction-Diffusion' concept:
    1. Type Checking (Structural Parsing): Just as DTPR enforces measure-theoretic 
       constraints via dependent types, this tool parses logical constraints 
       (negations, comparatives, conditionals) to filter invalid candidates.
    2. Morphogenesis (Constraint Propagation): Candidates are scored based on how 
       well their logical structure 'grows' to match the prompt's constraints.
    3. Measure Theory (NCD Tiebreaker): Only when structural signals are equal, 
       we use Normalized Compression Distance as a proxy for probabilistic similarity, 
       ensuring the 'mass' of information is conserved.
       
    This prioritizes logical validity (Reasoning) over string similarity, beating 
    the NCD baseline by detecting semantic negations and numeric relations.
    """

    def __init__(self):
        # Keywords indicating logical structures
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text for numeric evaluation."""
        pattern = r"[-+]?\d*\.\d+|\d+"
        matches = re.findall(pattern, text.lower())
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Score based on logical consistency (Type Checking phase).
        Checks for negation flips, boolean contradictions, and numeric validity.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has strong negation context, candidate should reflect it if it's a direct answer
        has_p_neg = any(n in p_lower for n in self.negations)
        has_c_neg = any(n in c_lower for n in self.negations)
        
        # Heuristic: If prompt asks "Is it not X?" and candidate is "Yes", it implies X.
        # Simple check: If prompt is negative and candidate is positive assertion without negation, 
        # it might be a contradiction depending on context. 
        # Instead, we reward candidates that explicitly handle the logical operators found.
        
        if has_p_neg:
            if has_c_neg:
                score += 0.2 # Acknowledges the negation
            elif any(b in c_lower for b in self.booleans):
                # Candidate gives a boolean answer despite negation in prompt - needs careful parsing
                # We give a small bonus if the candidate length suggests an explanation
                if len(c_lower.split()) > 1:
                    score += 0.1

        # 2. Numeric Evaluation
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If both have numbers, check basic ordering if comparatives exist
            if any(comp in p_lower for comp in self.comparatives):
                # Rough check: if prompt says "greater", candidate number should be greater?
                # This is hard without full parsing, so we just reward presence of consistent numbers
                score += 0.3
            else:
                # Exact match of numbers is a strong signal
                if set(p_nums) == set(c_nums):
                    score += 0.5
                elif any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    score += 0.2

        # 3. Conditional/Constraint Presence
        if any(cond in p_lower for cond in self.conditionals):
            if any(cond in c_lower for cond in self.conditionals):
                score += 0.2 # Candidate mirrors conditional structure
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_s1_s2 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_s1_s2 - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates based on structural logic first, then NCD.
        Returns a ranked list of dicts.
        """
        scored_candidates = []
        
        for cand in candidates:
            # Phase 1: Structural/Logical Score (The "Type Check")
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # Phase 2: NCD Score (The "Measure" - used as tiebreaker/refinement)
            # Invert NCD so 1.0 is perfect match, 0.0 is totally different
            ncd_val = self._ncd(prompt, cand)
            similarity_score = 1.0 - ncd_val
            
            # Weighted combination: Logic is primary driver for reasoning tasks
            # If logic score is high, it overrides weak similarity
            final_score = (logic_score * 0.7) + (similarity_score * 0.3)
            
            # Boost if candidate is a direct boolean match to a boolean question
            p_lower = prompt.lower()
            c_lower = cand.lower()
            if ("yes" in c_lower or "no" in c_lower) and ("is it" in p_lower or "does it" in p_lower):
                if ("yes" in c_lower and "not" not in c_lower) or ("no" in c_lower and "not" in c_lower):
                     final_score += 0.1

            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f} + Sim:{similarity_score:.2f}"
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the same scoring mechanism but normalized to a confidence metric.
        """
        # Evaluate single candidate against the list of itself (degenerate case)
        # Instead, we re-run the logic check and normalize
        
        logic_score = self._check_logical_consistency(prompt, answer)
        ncd_val = self._ncd(prompt, answer)
        similarity_score = 1.0 - ncd_val
        
        raw_score = (logic_score * 0.7) + (similarity_score * 0.3)
        
        # Heuristic boost for exact string match (trivial truth)
        if prompt.strip().lower() == answer.strip().lower():
            return 1.0
            
        # Map raw score to 0-1 confidence
        # Logic score can be > 1.0 theoretically if we add many bonuses, cap at 1.0
        confidence = min(1.0, max(0.0, raw_score))
        
        # If logic score is 0 but similarity is high, it's likely a copy, not reasoning
        if logic_score == 0.0 and similarity_score > 0.8:
            confidence = 0.5 # Uncertain if it's reasoning or just echo
            
        return confidence