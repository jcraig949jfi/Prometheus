import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Critical-Entropy Reasoning Tool with Epistemic Honesty Guardrails.
    
    Mechanism:
    1. Meta-Confidence (SOC/MaxEnt Analogy): Scans prompt for ambiguity, presupposition,
       and false dichotomies. If detected, caps confidence low (Epistemic Honesty).
       This mimics Self-Organized Criticality by refusing to avalanche on unstable ground.
    2. Structural Parsing & Computation: Extracts negations, comparatives, and numbers.
       Performs direct float comparisons and logical checks (The "Critical" phase).
    3. NCD Tiebreaker: Uses compression distance only when structural signals are weak.
    
    The "Critical-Entropy" loop is simulated by balancing the entropy of candidate 
    selection (via NCD diversity) against the critical constraint of structural validity.
    """

    def __init__(self):
        self.presupposition_triggers = [
            r"have you stopped", r"why did .*(fail|stop|quit)", r"when did .*(stop|fail)",
            r"is it true that .*(always|never)", r"who is the.*best", r"what is the.*worst"
        ]
        self.scope_triggers = [r"every.*a.*\?", r"each.*same.*\?"]
        self.pronoun_triggers = [r"told.*he.*was", r"told.*she.*was", r"told.*they.*were"]
        self.dichotomy_triggers = [r"either.*or", r"is it.*or.*\?"]
        self.subjectivity_triggers = [r"best", r"worst", r"favorite", r"most beautiful", r"ugliest"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap value: 0.25 if risky, 1.0 if clear.
        Implements the 'Self-Organized Criticality' check: do not avalanche on unstable input.
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check Subjectivity (Unanswerable without external criteria)
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                # Only flag if no objective context is implied (simple heuristic)
                if "objectively" not in p_lower and "math" not in p_lower:
                    return 0.25

        # Check False Dichotomy
        if re.search(r"either.*or", p_lower) and "option" not in p_lower:
             # Heuristic: if it asks to choose between two without listing options explicitly as exhaustive
             if "which of the following" not in p_lower:
                 return 0.25

        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for computation."""
        matches = re.findall(r"[-+]?\d*\.?\d+", text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Performs structural parsing and constructive computation.
        Returns a score 0.0 to 1.0 based on logical validity.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        reasons = []

        # 1. Numeric Evaluation (Constructive Computation)
        # Detect comparisons like "Is 9.11 > 9.9?" or "Which is larger: 5 or 10?"
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            # Simple heuristic: if prompt asks for larger/greater/max
            if any(k in p_lower for k in ["larger", "greater", "max", "more", "bigger"]):
                expected_val = max(nums)
                cand_nums = self._extract_numbers(candidate)
                if cand_nums and abs(cand_nums[0] - expected_val) < 1e-6:
                    score += 0.6
                    reasons.append("Numeric max match")
                elif cand_nums:
                    score -= 0.5 # Penalty for wrong number
            # Check for smaller/min
            elif any(k in p_lower for k in ["smaller", "less", "min", "fewer"]):
                expected_val = min(nums)
                cand_nums = self._extract_numbers(candidate)
                if cand_nums and abs(cand_nums[0] - expected_val) < 1e-6:
                    score += 0.6
                    reasons.append("Numeric min match")
        
        # 2. Negation Handling
        has_negation = any(k in p_lower for k in ["not ", "never ", "no ", "false "])
        cand_negation = any(k in c_lower for k in ["not ", "never ", "no ", "false "])
        
        if has_negation:
            # If prompt has negation, answer should likely reflect it or be 'no'/false
            if "yes" in c_lower and not cand_negation:
                score -= 0.4
                reasons.append("Negation mismatch")
            elif "no" in c_lower or cand_negation:
                score += 0.3
                reasons.append("Negation handled")

        # 3. Boolean/Yes-No Consistency
        if any(k in p_lower for k in ["is it true", "does it", "can it"]):
            if "yes" in c_lower or "true" in c_lower:
                score += 0.2
            elif "no" in c_lower or "false" in c_lower:
                score += 0.2 # Context needed, but presence of boolean word helps structure

        return max(0.0, min(1.0, 0.5 + score * 0.5)), "; ".join(reasons) if reasons else "Structural parse"

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            if c12 == 0: return 0.0
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return 1.0 - ncd # Invert so higher is better
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates based on structural parsing, computation, and NCD.
        Prioritizes epistemic honesty via meta-confidence capping.
        """
        # 1. Meta-Confidence Check (The SOC/MaxEnt Filter)
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        for cand in candidates:
            # 2. Structural & Computational Score (Primary Signal >= 50%)
            struct_score, reason = self._structural_score(prompt, cand)
            
            # 3. NCD Score (Tiebreaker <= 15%)
            ncd_score = self._ncd_score(prompt, cand)
            
            # Weighted Combination
            # Structural: 60%, NCD: 15%, Base Uncertainty: 25%
            raw_score = (struct_score * 0.60) + (ncd_score * 0.15) + 0.25
            
            # Apply Epistemic Cap
            final_score = min(raw_score, meta_cap)
            
            # If meta_cap is low, the reasoning should reflect the ambiguity
            final_reason = reason
            if meta_cap < 0.3:
                final_reason = "Low confidence: Prompt contains ambiguity, presupposition, or subjectivity."
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": final_reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if prompt is ambiguous (Tier B Honesty).
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Basic structural check for the specific answer
        score, _ = self._structural_score(prompt, answer)
        ncd = self._ncd_score(prompt, answer)
        raw_conf = (score * 0.6) + (ncd * 0.15) + 0.25
        
        # Apply cap
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless it's a clear computational win
        if meta_cap == 1.0 and score > 0.8:
            return min(final_conf, 0.95)
            
        return round(final_conf, 4)

    def _meta_confidence(self, prompt: str) -> float:
        """Wrapper to ensure method exists for internal calls if needed."""
        return self._meta_confidence_impl(prompt)

    def _meta_confidence_impl(self, prompt: str) -> float:
        """Internal implementation of meta confidence."""
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check Subjectivity
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                if "objectively" not in p_lower and "math" not in p_lower:
                    return 0.25

        # Check False Dichotomy
        if re.search(r"either.*or", p_lower) and "option" not in p_lower:
             if "which of the following" not in p_lower:
                 return 0.25

        return 1.0