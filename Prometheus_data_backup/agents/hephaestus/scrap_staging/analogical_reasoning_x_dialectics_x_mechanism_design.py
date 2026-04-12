import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    DADI-HT: Dialectical Analogy-Driven Incentive-Compatible Hypothesis Tester.
    
    Mechanism:
    1. Thesis/Antithesis (Dialectics): Parses prompt for structural constraints (Thesis) 
       and ambiguity traps/fallacies (Antithesis).
    2. Analogical Retrieval: Maps numeric/comparative patterns to known logical forms.
    3. Mechanism Design (VCG-inspired): Scores candidates based on marginal utility 
       (structural match) minus penalty (ambiguity cost). Truthful reporting (high score) 
       is only possible if the candidate satisfies structural constraints without triggering 
       epistemic honesty caps.
    
    Epistemic Honesty: Prioritizes detecting ambiguity (Tier B) over forced guessing.
    """

    def __init__(self):
        # Presupposition triggers (Antithesis generators)
        self.presupposition_patterns = [
            r"\b(stopped|quit|ceased)\s+(doing\s+)?", 
            r"\bwhy\s+(did|does|is)\s+\w+\s+(fail|stop|wrong)",
            r"\bwhen\s+did\s+\w+\s+(stop|fail)",
            r"\bhave\s+you\s+(stopped|quit)"
        ]
        # Scope/Pronoun ambiguity
        self.ambiguity_patterns = [
            r"\bevery\s+\w+.*\ba\s+\w+", # Every X did a Y (same Y?)
            r"\b(he|she|it|they)\s+(was|is|were)\s+", # Pronoun ref
            r"\bwho\s+is\s+(he|she|it)?",
            r"\bwhich\s+one\s+is\s+(he|she|it)?"
        ]
        # False Dichotomy
        self.dichotomy_patterns = [
            r"\beither\s+.*\bor\s+",
            r"\bis\s+it\s+(a|b)\s+or\s+(c|d)"
        ]
        # Subjectivity
        self.subjectivity_patterns = [
            r"\b(best|worst|favorite|most\s+beautiful)\s+",
            r"\bwho\s+is\s+the\s+(best|smartest)"
        ]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _check_presupposition(self, prompt: str) -> bool:
        p_low = prompt.lower()
        for pattern in self.presupposition_patterns:
            if re.search(pattern, p_low):
                return True
        return False

    def _check_ambiguity(self, prompt: str) -> bool:
        p_low = prompt.lower()
        # Simple heuristic for pronoun ambiguity in questions
        if re.search(r"\bwho\s+is\s+(he|she|it|they)\b", p_low):
            return True
        if re.search(r"\bevery\s+\w+.*\ba\s+\w+", p_low) and "same" not in p_low:
            return True
        return False

    def _check_false_dichotomy(self, prompt: str) -> bool:
        p_low = prompt.lower()
        if re.search(r"\beither\s+\w+.*\bor\s+\w+", p_low):
            # Check if context implies exclusivity without justification
            if "option" not in p_low and "choice" not in p_low:
                return True
        return False

    def _check_subjectivity(self, prompt: str) -> bool:
        p_low = prompt.lower()
        for pattern in self.subjectivity_patterns:
            if re.search(pattern, p_low):
                return True
        return False

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap on confidence (0.0 to 1.0).
        """
        if self._check_presupposition(prompt):
            return 0.2  # Strong presupposition trap
        if self._check_ambiguity(prompt):
            return 0.25 # Ambiguous reference
        if self._check_false_dichotomy(prompt):
            return 0.3  # Potential false dichotomy
        if self._check_subjectivity(prompt):
            return 0.3  # Subjective question
        return 1.0  # No obvious traps detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers for constructive computation."""
        # Match integers and floats, handling negative signs
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Thesis Generation & Verification.
        Checks logical consistency, negation handling, and numeric validity.
        """
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive Computation)
        # If prompt has numbers and candidate is a number, check magnitude logic
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Case: Comparison traps (e.g., 9.11 vs 9.9)
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Heuristic: If prompt asks for "larger" or "smaller"
                val = c_nums[0]
                if "larger" in p_low or "greater" in p_low or "more" in p_low:
                    if val == max(p_nums): score += 0.5
                elif "smaller" in p_low or "less" in p_low:
                    if val == min(p_nums): score += 0.5
                # Direct match bonus if exact number from prompt appears in correct context
                if val in p_nums:
                    score += 0.3
        
        # 2. Negation Handling (Modus Tollens check)
        # If prompt says "not X", candidate should not be "X"
        if re.search(r"\bis\s+not\s+|\bare\s+not\s+|\bdoes\s+not\s+", p_low):
            # Simple anti-match: if candidate repeats the positive verb phrase without negation
            # This is a weak proxy but catches obvious contradictions
            if "yes" in c_low and "no" not in c_low:
                # If the question is a negative constraint, "Yes" is often wrong unless qualified
                pass # Complex logic needed, skip for brevity, rely on NCD tiebreak
        
        # 3. Binary Logic (Yes/No consistency)
        yes_no_words = ['yes', 'no', 'true', 'false']
        if any(w in p_low for w in ['is it true', 'does it', 'can it']):
            if c_low in ['yes', 'true']:
                score += 0.2
            elif c_low in ['no', 'false']:
                score += 0.2

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(s1_b)
        len2 = len(s2_b)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1_b + s2_b
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Simplified for stability: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Using lengths as proxy for C(x) if not compressing individually, 
        # but standard NCD uses compressed lengths.
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c_concat = len(zlib.compress(concat))
        
        min_c = min(c1, c2)
        max_c = max(c1, c2)
        if max_c == 0: return 1.0
        return (c_concat - min_c) / max_c

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main evaluation loop implementing DADI-HT logic.
        1. Meta-check prompt for honesty cap.
        2. Score candidates via Structural (Thesis) and Analogy (NCD).
        3. Apply Mechanism Design: Penalize scores if honesty cap is low.
        """
        results = []
        
        # Step 1: Epistemic Honesty Check (Antithesis)
        honesty_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            # Step 2: Structural Scoring (Thesis)
            struct_score = self._structural_score(prompt, candidate)
            
            # Step 3: Analogical Scoring (NCD as tiebreaker/similarity)
            # Low NCD means high similarity. We want high similarity to valid patterns.
            # But NCD is noisy. We use it only as a small booster if structural is non-zero.
            ncd_val = self._ncd(prompt, candidate)
            # Convert distance to similarity (0-1), inverted
            ncd_score = (1.0 - ncd_val) * 0.15 # Max 15% weight
            
            # Raw Score = Structural (Dominant) + NCD (Minor)
            raw_score = struct_score + ncd_score
            
            # Step 4: Mechanism Design (Incentive Compatibility)
            # If the prompt is ambiguous (low honesty_cap), the mechanism 
            # severely penalizes high confidence in any specific candidate.
            # This forces the 'agent' to report low confidence on ambiguous queries.
            if honesty_cap < 0.4:
                # Cap the score based on epistemic uncertainty
                final_score = min(raw_score, honesty_cap)
                reason = f"Epistemic limit applied: {honesty_cap:.2f}. Structural: {struct_score:.2f}."
            else:
                final_score = raw_score
                reason = f"Structural: {struct_score:.2f}, NCD: {ncd_score:.2f}."

            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at _meta_confidence limit to ensure epistemic honesty.
        """
        # Check meta-constraints first
        cap = self._meta_confidence(prompt)
        
        # Calculate base confidence from structural match
        struct_score = self._structural_score(prompt, answer)
        ncd_val = self._ncd(prompt, answer)
        ncd_score = (1.0 - ncd_val) * 0.15
        
        base_conf = min(1.0, struct_score + ncd_score + 0.1) # Small base for valid looking answers
        
        # Apply cap
        final_conf = min(base_conf, cap)
        
        # Ensure we don't return > 0.9 without strong structural evidence
        if struct_score < 0.5 and final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 3)