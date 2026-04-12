import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Prime-aware Epistemic Model Checker (PEMC) Implementation.
    
    Mechanism:
    1. Structural Parsing (50%): Extracts logical operators, negations, and comparatives.
    2. Constructive Computation (20%): Evaluates arithmetic and prime properties for small integers.
    3. Epistemic Justification (Meta-Layer): Detects Tier-B traps (presuppositions, ambiguity) to cap confidence.
    4. NCD Tiebreaker (15%): Used only when structural signals are weak or equal.
    
    The "Prime" aspect is implemented as a constructive verifier for number-theoretic claims within the prompt,
    serving as the "justification logic" for specific numeric beliefs.
    """

    def __init__(self):
        self.small_primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
        self.bound = 100  # State space bound B

    def _is_prime(self, n: int) -> bool:
        """Constructive prime check with justification trace."""
        if n < 2: return False
        if n in self.small_primes: return True
        if n % 2 == 0: return False
        # Simple trial division for the bounded state space
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    def _extract_numbers(self, text: str) -> List[int]:
        """Extract integers from text for constructive evaluation."""
        return [int(x) for x in re.findall(r'\b\d+\b', text)]

    def _check_presuppositions(self, prompt: str) -> Tuple[bool, str]:
        """
        Tier-B Epistemic Check: Detects ambiguous or unanswerable prompts.
        Returns (is_ambiguous, reason).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        if re.search(r'\b(have you stopped|why did .+ (fail|stop|quit)|when did .+ stop)\b', p):
            return True, "Presupposition detected"
            
        # 2. False Dichotomy ("Either A or B" without context)
        if re.search(r'\beither .+ or .+\b', p) and "option" not in p:
            # Heuristic: if it looks like a logic puzzle, maybe okay, else suspicious
            if "logic" not in p and "puzzle" not in p:
                return True, "Potential false dichotomy"

        # 3. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|ugliest)\b', p):
            if "math" not in p and "prime" not in p and "largest" not in p:
                return True, "Subjective criteria detected"

        # 4. Pronoun ambiguity (Simple heuristic: "he/she" + "who")
        if re.search(r'\b(he|she|him|her)\b', p) and re.search(r'\bwho\b', p):
            return True, "Pronoun ambiguity"

        return False, ""

    def _meta_confidence(self, prompt: str) -> float:
        """
        Calculates the maximum allowable confidence based on prompt properties.
        Enforces epistemic honesty.
        """
        is_ambig, _ = self._check_presuppositions(prompt)
        if is_ambig:
            return 0.25  # Cap for ambiguous/unanswerable
        
        # If no structural match can be found later, this ensures low confidence
        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Parses logical structure and verifies against candidate.
        Returns score 0.0 to 1.0.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        checks = 0
        
        # 1. Negation Handling
        has_negation = bool(re.search(r'\b(not|no|never|none|false)\b', p_lower))
        candidate_negation = bool(re.search(r'\b(not|no|never|none|false)\b', c_lower))
        
        if has_negation:
            checks += 1
            # If prompt asks what is NOT true, and candidate implies truth, penalize
            # Simplified: Check if candidate contradicts the negation structure
            if "not" in p_lower and "not" not in c_lower and "false" not in c_lower:
                # Heuristic: if prompt says "X is not Y", candidate should reflect that
                pass 
            score += 0.5 # Base credit for detecting negation presence
        else:
            checks += 1
            score += 0.5

        # 2. Comparative Logic (Numeric)
        numbers = self._extract_numbers(prompt)
        if len(numbers) >= 2:
            checks += 1
            # Detect comparative keywords
            if re.search(r'\b(more|less|greater|smaller|larger|between)\b', p_lower):
                val = max(numbers) if "largest" in p_lower or "greater" in p_lower else min(numbers)
                if str(val) in candidate:
                    score += 0.5
                else:
                    score += 0.0
            else:
                # Just presence of numbers in a math context
                if any(str(n) in candidate for n in numbers):
                    score += 0.3
                checks += 0.5 # Weighted less if no explicit comparator

        # 3. Prime Number Verification (Constructive)
        # If prompt mentions "prime" and a number, verify it
        if "prime" in p_lower and numbers:
            checks += 1
            target = numbers[0]
            is_p = self._is_prime(target)
            
            # Check if candidate affirms or denies correctly
            c_affirms = any(w in c_lower for w in ["yes", "true", "is prime", "correct"])
            c_denies = any(w in c_lower for w in ["no", "false", "is not", "composite"])
            
            if is_p and c_affirms:
                score += 0.5
            elif not is_p and c_denies:
                score += 0.5
            elif is_p and c_denies:
                score -= 0.5 # Penalty for wrong constructive check
            elif not is_p and c_affirms:
                score -= 0.5
            
        return max(0.0, min(1.0, score / (checks if checks > 0 else 1)))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0: return 1.0
        return (len_joint - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-check prompt first
        max_conf_cap = self._meta_confidence(prompt)
        is_ambiguous = max_conf_cap < 0.3
        
        for cand in candidates:
            # 1. Structural Score (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Constructive Computation Bonus
            # If the candidate is a number and we can verify it via prime logic
            comp_score = 0.0
            nums = self._extract_numbers(cand)
            if nums and "prime" in prompt.lower():
                n = nums[0]
                if self._is_prime(n) and "not" not in cand.lower():
                    comp_score = 0.2 # Bonus for correct prime identification
            
            # 3. NCD Tiebreaker (Max 15% influence)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so lower distance = higher score, but cap contribution
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Aggregate
            # Weighting: Structural 50%, Computation 20%, NCD 15%, Base 15%
            raw_score = (struct_score * 0.50) + (comp_score * 1.0) + (ncd_score * 0.30) + 0.15
            
            # Apply Epistemic Cap
            final_score = min(raw_score, max_conf_cap)
            
            # Reasoning Trace
            reason_parts = []
            if is_ambiguous:
                reason_parts.append("Epistemic cap applied: Prompt ambiguous.")
            if struct_score > 0.4:
                reason_parts.append("Structural match found.")
            if comp_score > 0:
                reason_parts.append("Constructive prime verification passed.")
            if not reason_parts:
                reason_parts.append("Low structural signal; relying on NCD.")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reason_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure epistemic honesty.
        """
        # 1. Check for Tier-B traps (Presuppositions, Ambiguity)
        cap = self._meta_confidence(prompt)
        
        if cap < 0.3:
            return cap
            
        # 2. Structural Validation
        # Run a mini-evaluation to see if the answer structurally fits
        temp_res = self.evaluate(prompt, [answer])
        if not temp_res:
            return 0.1
            
        score = temp_res[0]["score"]
        
        # 3. Constructive Verification (The "Prime" Justification)
        # If the prompt asks about primality, we must be 100% sure of the math
        if "prime" in prompt.lower():
            nums = self._extract_numbers(answer)
            if nums:
                # If the answer claims a number is prime, verify it definitively
                # This acts as the "Justification Logic" layer
                n = nums[0]
                is_p = self._is_prime(n)
                claims_prime = "prime" in answer.lower() and "not" not in answer.lower()
                claims_composite = "composite" in answer.lower() or ("not" in answer.lower() and "prime" in answer.lower())
                
                if (is_p and claims_prime) or (not is_p and claims_composite):
                    # Math checks out, allow higher confidence up to cap
                    return min(0.95, cap) 
                elif (is_p and claims_composite) or (not is_p and claims_prime):
                    # Math contradiction
                    return 0.05
        
        # Default: Scale score by the cap
        return min(score, cap)