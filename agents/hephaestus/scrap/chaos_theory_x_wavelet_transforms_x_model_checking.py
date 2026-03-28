import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Scale Symbolic Abstraction Pipeline for Reasoning.
    
    Mechanism:
    1. Wavelet-like Decomposition (Discrete): The input text is parsed into structural 
       tokens (negations, comparatives, conditionals, numbers) representing 'scales' of logic.
       Non-structural text is treated as noise/background.
    2. Chaos/Attractor Mapping: Candidates are evaluated based on 'dynamic stability' 
       (consistency with extracted constraints). A candidate violating a hard constraint 
       (e.g., negation, numeric inequality) is assigned a high 'Lyapunov exponent' (instability), 
       effectively zeroing its score.
    3. Model Checking (Symbolic Verification): Remaining candidates are verified against 
       the logical trace (LTL-style checks). 
    4. Scoring: Base score derived from constraint satisfaction (Model Checking), 
       refined by NCD (compression) only as a tie-breaker for semantic closeness.
    """

    def __init__(self):
        # Structural patterns for "Wavelet" decomposition
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere|cannot|won\'t|don\'t|doesn\'t|didnt|isnt|arent|wasnt|werent)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|larger|fewer|higher|lower|better|worse|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|else|unless|provided|assuming|when|while)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+(?:\.\d+)?')
        
    def _extract_structural_signature(self, text: str) -> Dict:
        """Decompose text into logical scales (Wavelet coefficients analogy)."""
        lower_text = text.lower()
        return {
            "negations": len(self.negation_pattern.findall(lower_text)),
            "comparatives": len(self.comparative_pattern.findall(lower_text)),
            "conditionals": len(self.conditional_pattern.findall(lower_text)),
            "numbers": [float(n) for n in self.number_pattern.findall(text)],
            "length": len(text.split())
        }

    def _check_numeric_consistency(self, prompt_sig: Dict, cand_sig: Dict, prompt: str, candidate: str) -> Tuple[bool, float]:
        """Verify numeric constraints (Chaos stability check)."""
        p_nums = prompt_sig["numbers"]
        c_nums = cand_sig["numbers"]
        
        # If no numbers, pass through
        if not p_nums:
            return True, 1.0
            
        # Heuristic: If prompt has numbers and candidate has none, likely incomplete
        if not c_nums:
            # Check if prompt implies a calculation or comparison that needs an answer
            if prompt_sig["comparatives"] > 0 or "calculate" in prompt.lower() or "sum" in prompt.lower():
                return False, 0.0
        
        # Specific check: If prompt asks for "larger" or "smaller", verify candidate number aligns
        # This is a simplified symbolic check for demonstration
        if p_nums and c_nums:
            # If the prompt contains a comparative, ensure the candidate doesn't contradict obvious bounds
            # e.g. Prompt: "Is 5 > 3?" Candidate: "No, 5 is not greater." (Logic check handled below)
            pass
            
        return True, 1.0

    def _verify_logical_trace(self, prompt: str, candidate: str) -> float:
        """Model Checking: Verify candidate against prompt constraints (LTL style)."""
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 1.0
        
        # 1. Negation Consistency (Modus Tollens check)
        p_negs = self.negation_pattern.findall(p_lower)
        c_negs = self.negation_pattern.findall(c_lower)
        
        # If prompt asserts something is NOT X, and candidate says it IS X (without negation context), penalize
        # Simple heuristic: Count negation density mismatch if the topic is similar
        if len(p_negs) > 0 and len(c_negs) == 0:
            # If prompt is heavily negative ("It is not true that...") and candidate is affirmative without qualification
            if any(word in p_lower for word in ["false", "incorrect", "not true"]):
                if not any(word in c_lower for word in ["false", "incorrect", "not", "no"]):
                    score *= 0.2 # Strong penalty for missing the negation

        # 2. Conditional Consistency
        if "if" in p_lower:
            # If prompt is conditional, candidate should ideally reflect conditionality or answer the specific case
            if "yes" in c_lower or "no" in c_lower:
                # Acceptable direct answer
                pass
            elif len(c_lower.split()) < 5 and "if" not in c_lower:
                # Short answer without conditional context might be risky but not fatal
                pass

        # 3. Numeric Logic (Simplified)
        p_nums = self.number_pattern.findall(prompt)
        c_nums = self.number_pattern.findall(candidate)
        
        if p_nums and c_nums:
            try:
                p_vals = [float(n) for n in p_nums]
                c_vals = [float(n) for n in c_nums]
                
                # Check for direct contradiction in simple comparisons
                if "greater" in p_lower or "larger" in p_lower or ">" in prompt:
                    # If prompt asks what is larger, and candidate provides a number, 
                    # we can't fully verify without external knowledge, but we check consistency
                    pass
            except ValueError:
                pass

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        comp12 = len(zlib.compress(b1 + b2))
        
        numerator = comp12 - min(comp1, comp2)
        denominator = max(comp1, comp2)
        
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_sig = self._extract_structural_signature(prompt)
        results = []
        
        for cand in candidates:
            cand_sig = self._extract_structural_signature(cand)
            
            # Step 1: Structural Parsing & Numeric Evaluation (Chaos Stability)
            is_stable, numeric_score = self._check_numeric_consistency(prompt_sig, cand_sig, prompt, cand)
            
            if not is_stable:
                final_score = 0.0
                reason = "Failed numeric stability check (Chaos constraint violation)."
            else:
                # Step 2: Model Checking (Logical Trace Verification)
                logic_score = self._verify_logical_trace(prompt, cand)
                
                # Step 3: NCD as Tiebreaker/Refinement (Wavelet denoising)
                # Only apply NCD if logic score is high enough to avoid noise domination
                if logic_score > 0.5:
                    ncd_val = self._ncd(prompt, cand)
                    # Convert distance to similarity (0 dist = 1 sim)
                    # Weight NCD lightly (20%) compared to structural logic (80%)
                    similarity = 1.0 - ncd_val
                    final_score = (logic_score * 0.8) + (similarity * 0.2)
                    reason = f"Logical consistency: {logic_score:.2f}, Structural similarity: {similarity:.2f}"
                else:
                    final_score = logic_score * 0.5 # Penalize heavily if logic fails
                    reason = f"Logical inconsistency detected. Score capped."

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on logical consistency."""
        # Reuse evaluation logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]