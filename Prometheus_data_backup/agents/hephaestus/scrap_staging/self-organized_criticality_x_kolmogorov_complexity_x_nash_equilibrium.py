import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Critical-Complexity Game Learner (CCGL) Implementation.
    
    Mechanism:
    1. SOC Dynamics: Hypothesis generation is modeled as an avalanche process. 
       We simulate this by perturbing candidate evaluation based on 'grain' accumulation 
       (structural complexity). If a candidate is too complex or the prompt is ambiguous, 
       an 'avalanche' occurs, triggering a low-confidence reset (epistemic honesty).
    2. Kolmogorov Complexity (KC): Approximated via zlib compression length. 
       Used as a penalty term (Occam's razor) and tie-breaker.
    3. Nash Equilibrium: The scoring function balances 'Survival' (matching structural 
       constraints of the prompt) vs. 'Simplicity' (low KC). The equilibrium is reached 
       when a candidate satisfies hard logical constraints (Survival) with minimal 
       description length (Simplicity).
       
    Epistemic Honesty (Tier B):
    Before scoring, the tool analyzes the prompt for presuppositions, scope ambiguities,
    and unanswerable conditions. If detected, confidence is capped < 0.3 regardless 
    of candidate content.
    """

    # Preset patterns for Tier B (Judgment) traps
    PRESUPPOSITION_TRIGGERS = [
        r"\b(stopped|quit|ceased)\s+(doing|eating|working)\b",
        r"\bwhy\s+did\s+\w+\s+(fail|stop|break)\b",
        r"\bwhen\s+did\s+\w+\s+(stop|fail)\b",
        r"\bhave\s+you\s+(stopped|quit)\b"
    ]
    
    FALSE_DICHOTOMY_TRIGGERS = [
        r"\beither\s+.*\s+or\s+.*\b",
        r"\bis\s+it\s+.*\s+or\s+.*\?"
    ]

    SCOPE_AMBIGUITY_TRIGGERS = [
        r"\bevery\s+\w+\s+.*\s+a\s+\w+\b", # Simplified heuristic for "Every X did a Y"
        r"\bsame\s+\w+\b"
    ]

    PRONOUN_AMBIGUITY_TRIGGERS = [
        r"\b(he|she|him|her|they)\s+was\s+(wrong|right|told)\b",
        r"\bwho\s+was\s+(it|he|she)\b"
    ]

    def __init__(self):
        self._state_seed = 42  # Deterministic seed for SOC simulation

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _get_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _approx_kc(self, s: str) -> float:
        """Approximate Kolmogorov Complexity via compression length."""
        if not s:
            return 0.0
        return len(zlib.compress(s.encode('utf-8')))

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, presupposition, and unanswerability.
        Returns a confidence cap (0.0 - 1.0).
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.PRESUPPOSITION_TRIGGERS:
            if re.search(pattern, p_lower):
                return 0.2
        
        # Check False Dichotomy
        for pattern in self.FALSE_DICHOTOMY_TRIGGERS:
            if re.search(pattern, p_lower):
                # Only flag if it looks like a forced choice without evidence
                if "prove" not in p_lower and "calculate" not in p_lower:
                    return 0.25

        # Check Scope/Pronoun Ambiguity (Heuristic)
        if re.search(r"\bevery\b", p_lower) and re.search(r"\bsame\b", p_lower):
            return 0.25
        
        if re.search(r"\btold\b", p_lower) and re.search(r"\bwho\b", p_lower):
            return 0.2

        # Check for missing info indicators (Subjectivity)
        subjective_words = ["best", "worst", "favorite", "opinion"]
        if any(w in p_lower for w in subjective_words):
            if "calculate" not in p_lower and "math" not in p_lower:
                return 0.2

        return 1.0  # No meta-issues detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        # Match integers and floats, handling negative signs
        matches = re.findall(r'-?\d+\.?\d*', text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural parsing and constructive computation.
        Returns a score 0.0 - 1.0 based on logical validity.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip()
        score = 0.0
        reasons = []

        # 1. Numeric Evaluation (Constructive Computation)
        # Detect simple comparisons or math problems
        if "greater" in p_lower or "larger" in p_lower or "smaller" in p_lower or "less" in p_lower:
            nums = self._extract_numbers(prompt)
            if len(nums) >= 2:
                # Expecting candidate to identify max/min or comparison result
                cand_nums = self._extract_numbers(candidate)
                if cand_nums:
                    val = cand_nums[0]
                    if "greater" in p_lower or "larger" in p_lower:
                        if val == max(nums):
                            score += 0.5
                            reasons.append("Correctly identified max value")
                    elif "smaller" in p_lower or "less" in p_lower:
                        if val == min(nums):
                            score += 0.5
                            reasons.append("Correctly identified min value")
        
        # 2. Boolean/Logic Traps (Yes/No)
        # If prompt asks a yes/no question but contains a false premise detected by meta,
        # structural score should be low unless candidate rejects premise.
        # Here we just check for direct contradiction if prompt implies a specific fact.
        
        # 3. Negation Handling
        if "not" in p_lower:
            # If prompt says "X is not Y", and candidate says "X is Y", penalize heavily
            # Simple heuristic: if prompt has "not A" and candidate has "A" without "not"
            # This is hard to do perfectly without NLP, so we rely on NCD for semantic match
            pass

        # 4. Direct String Match (Baseline)
        if c_lower in p_lower or p_lower in c_lower:
            score += 0.2
            reasons.append("Substring match")

        return min(score, 1.0), ", ".join(reasons) if reasons else "No structural match"

    def _soc_avalanche_check(self, prompt: str, candidate: str) -> bool:
        """
        Simulates SOC 'grain' addition. 
        If the candidate is overly complex (high KC) relative to the prompt, 
        or if the prompt is ambiguous, an 'avalanche' occurs, resetting the score.
        This enforces the 'Critical Point': only simple, robust hypotheses survive.
        """
        kc_prompt = self._approx_kc(prompt)
        kc_cand = self._approx_kc(candidate)
        
        # If candidate is significantly more complex than prompt without justification (heuristic)
        # Or if the description length explodes, trigger avalanche (reject)
        if kc_cand > (kc_prompt * 3.0): 
            return True # Avalanche triggered (Reset/Reject)
        return False

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Tier A - Primary Signal >= 50%)
            struct_score, struct_reason = self._structural_score(prompt, cand)
            
            # 2. Constructive Computation Check (Explicit Math)
            # Try to solve simple arithmetic if present
            computation_score = 0.0
            if "+" in prompt or "-" in prompt or "*" in prompt or "/" in prompt:
                # Very basic eval safety check
                try:
                    # Extract expression roughly
                    expr = re.sub(r'[^\d+\-*/().\s]', '', prompt)
                    if expr and any(c.isdigit() for c in expr):
                        # Safe eval context
                        allowed = set("0123456789+-*/(). ")
                        if all(c in allowed for c in expr):
                            true_val = eval(expr)
                            cand_nums = self._extract_numbers(cand)
                            if cand_nums and abs(cand_nums[-1] - true_val) < 1e-6:
                                computation_score = 0.4 # High weight for correct math
                except:
                    pass

            # 3. Kolmogorov Complexity / NCD (Tie breaker <= 15%)
            # We want Low KC (simple) and Low NCD to prompt (relevant)
            ncd_val = self._get_ncd(prompt, cand)
            kc_val = self._approx_kc(cand)
            
            # Normalize KC penalty (0 to 1 roughly)
            kc_penalty = min(kc_val / 100.0, 1.0) 
            
            # Combined Score Logic
            # Base score from structure and computation
            base_score = struct_score + computation_score
            
            # If base score is 0, rely on NCD similarity as a fallback (but capped)
            if base_score == 0:
                # Invert NCD so lower distance = higher score
                base_score = (1.0 - ncd_val) * 0.3 # Max 0.3 from pure similarity
            
            # Apply KC Penalty (Occam's Razor) - Small influence
            final_score = base_score - (kc_penalty * 0.05)
            
            # SOC Avalanche Check
            if self._soc_avalanche_check(prompt, cand):
                final_score *= 0.1 # Penalize heavily but don't zero out completely if it's the only option
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the question is ambiguous (meta_cap < 0.3), the score cannot exceed the cap
            if meta_cap < 0.3:
                final_score = min(final_score, meta_cap)
            
            # Ensure non-negative
            final_score = max(0.0, final_score)
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural: {struct_reason}; Meta-Cap: {meta_cap}; Comp-Score: {computation_score > 0}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly adheres to Epistemic Honesty:
        - Checks prompt for ambiguity (Tier B).
        - Checks if answer matches structural/computational truth (Tier A).
        """
        # 1. Meta-Check (Prompt Properties)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            # Ambiguous prompt -> Low confidence regardless of answer
            return round(meta_cap * 0.9, 2) # Slight reduction to ensure < cap

        # 2. Structural/Computational Verification
        # Re-run specific checks for this single candidate
        struct_score, _ = self._structural_score(prompt, answer)
        
        # Check Math explicitly
        comp_match = False
        if "+" in prompt or "-" in prompt or "*" in prompt or "/" in prompt:
            try:
                expr = re.sub(r'[^\d+\-*/().\s]', '', prompt)
                if expr and any(c.isdigit() for c in expr):
                    allowed = set("0123456789+-*/(). ")
                    if all(c in allowed for c in expr):
                        true_val = eval(expr)
                        cand_nums = self._extract_numbers(answer)
                        if cand_nums and abs(cand_nums[-1] - true_val) < 1e-6:
                            comp_match = True
            except:
                pass
        
        if comp_match:
            return 0.95 # High confidence on verified math
        
        if struct_score > 0.4:
            return 0.85 # High confidence on structural match
        
        # 3. Fallback to NCD similarity (Weak signal)
        ncd = self._get_ncd(prompt, answer)
        if ncd < 0.2:
            return 0.6
        elif ncd < 0.5:
            return 0.4
        
        # Default low confidence for unverified answers
        return 0.25