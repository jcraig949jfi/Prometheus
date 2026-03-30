import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Counterexample-Guided Causal Program Synthesizer (CG-CPS) with Epistemic Honesty.
    
    Mechanism:
    1. Synthesis Phase: Parses the prompt to construct a structural hypothesis (logic tree).
    2. Falsification Phase: Checks the hypothesis against "Meta-Constraints" (ambiguity, presupposition).
       If a meta-constraint is violated (e.g., ambiguous pronoun), the hypothesis is falsified immediately.
    3. Counterexample Generation: If falsified, generates a low-confidence score (counterexample to certainty).
    4. Revision: If not falsified, proceeds to structural parsing and numeric evaluation.
    
    This implements Popperian falsification by prioritizing the rejection of uncertain/ambiguous 
    hypotheses before attempting to validate correct ones.
    """

    def __init__(self):
        # Patterns for Tier B (Epistemic Honesty) detection
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bquit\b", r"\bassum.*that\b", r"\bgiven that\b"
        ]
        self.false_dichotomy_triggers = [r"\beither.*or\b", r"\bmust.*or\b"]
        self.pronoun_ambiguity_triggers = [r"\btold.*\bhe\b", r"\btold.*\bshe\b", r"\bsaid.*\bhe\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]
        
        # Patterns for Tier A (Structural/Logic)
        self.negation_pattern = r"\b(not|no|never|neither)\b"
        self.comparative_pattern = r"\b(more|less|greater|smaller|higher|lower)\b"
        self.conditional_pattern = r"\b(if|then|unless|only if)\b"

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Evaluates the prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap value. If issues found, returns < 0.3.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.15  # Strong presupposition detected
        
        # 2. False Dichotomy Check
        for pattern in self.false_dichotomy_triggers:
            if re.search(pattern, p_lower):
                # Only flag if it looks like a forced choice without data
                if "option" in p_lower or "choice" in p_lower:
                    return 0.25

        # 3. Pronoun Ambiguity (Simple heuristic)
        if re.search(r"\bwho\b", p_lower) and any(re.search(p, p_lower) for p in self.pronoun_ambiguity_triggers):
            return 0.20

        # 4. Subjectivity without criteria
        if any(re.search(p, p_lower) for p in self.subjectivity_triggers):
            if "data" not in p_lower and "table" not in p_lower and "list" not in p_lower:
                return 0.10

        return 1.0  # No meta-issues detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for numeric evaluation."""
        matches = re.findall(r"-?\d+\.?\d*", text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural parsing and constructive computation.
        Returns a score based on logic consistency and numeric correctness.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive Computation)
        # Detect simple comparisons in prompt like "Is 9.11 < 9.9?"
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            # Heuristic: If prompt has numbers and candidate has "yes"/"no" or true/false
            if re.search(r"\b(yes|true|correct)\b", c_lower):
                # Verify logic if comparative words exist
                if re.search(r"greater|larger|more", p_lower):
                    if nums[0] > nums[1]: score += 0.5
                    else: score -= 0.5
                elif re.search(r"less|smaller", p_lower):
                    if nums[0] < nums[1]: score += 0.5
                    else: score -= 0.5
                else:
                    # Default numeric presence bonus if logic isn't explicit
                    score += 0.2
            elif re.search(r"\b(no|false|incorrect)\b", c_lower):
                if re.search(r"greater|larger|more", p_lower):
                    if nums[0] <= nums[1]: score += 0.5
                elif re.search(r"less|smaller", p_lower):
                    if nums[0] >= nums[1]: score += 0.5

        # 2. Negation Handling
        has_negation = bool(re.search(self.negation_pattern, p_lower))
        candidate_negates = bool(re.search(self.negation_pattern, c_lower))
        
        if has_negation:
            # If prompt has negation, correct answer often requires careful handling.
            # Simple heuristic: If prompt asks "Is it not X?" and candidate says "No", 
            # it implies agreement with the negative premise.
            if candidate_negates:
                score += 0.3
        else:
            if not candidate_negates:
                score += 0.2

        # 3. Conditional Logic Check
        if re.search(self.conditional_pattern, p_lower):
            if re.search(r"\b(therefore|thus|hence|so)\b", c_lower):
                score += 0.2
        
        # 4. String Overlap (NCD Tiebreaker component - limited weight)
        # Only used if structural signals are weak
        ncd_score = self._ncd_similarity(prompt, candidate)
        score += (ncd_score * 0.15) 

        return score

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            s1_bytes = s1.encode('utf-8')
            s2_bytes = s2.encode('utf-8')
            concat = s1_bytes + b" " + s2_bytes
            
            len_s1 = len(zlib.compress(s1_bytes))
            len_s2 = len(zlib.compress(s2_bytes))
            len_concat = len(zlib.compress(concat))
            
            max_len = max(len_s1, len_s2)
            if max_len == 0: return 0.0
            ncd = (len_concat - max_len) / max_len
            return 1.0 - ncd  # Convert distance to similarity
        except:
            return 0.0

    def _generate_reasoning(self, prompt: str, candidate: str, meta_cap: float) -> str:
        """Generates a brief reasoning string based on the synthesis phase."""
        if meta_cap < 0.3:
            return "Falsified: Prompt contains ambiguity, presupposition, or unanswerable constraints."
        
        reasons = []
        if re.search(self.negation_pattern, prompt.lower()):
            reasons.append("Negation detected")
        if self._extract_numbers(prompt):
            reasons.append("Numeric evaluation performed")
        if re.search(self.conditional_pattern, prompt.lower()):
            reasons.append("Conditional logic analyzed")
            
        if not reasons:
            reasons.append("Structural pattern matched")
            
        return f"Synthesis valid: {', '.join(reasons)}."

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main loop: Synthesis -> Falsification -> Scoring.
        """
        results = []
        
        # Step 1: Meta-Analysis (Falsification of the question itself)
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            base_score = 0.0
            
            if meta_cap < 0.3:
                # If the question is flawed, high confidence in any answer is wrong.
                # We penalize candidates that look overly confident or specific if the prompt is trash,
                # but primarily we cap the final confidence.
                base_score = 0.1 # Low base score for flawed prompts
            else:
                # Step 2: Structural Synthesis & Scoring
                base_score = self._structural_score(prompt, candidate)
                # Normalize score to 0-1 range roughly
                base_score = max(0.0, min(1.0, base_score))

            results.append({
                "candidate": candidate,
                "score": base_score,
                "reasoning": self._generate_reasoning(prompt, candidate, meta_cap)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence capped by epistemic honesty checks.
        """
        # 1. Meta-Check (The Falsification Step)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Verification
        struct_score = self._structural_score(prompt, answer)
        
        # 3. Combine
        # If meta_cap is low, confidence is capped regardless of structural match
        raw_conf = min(meta_cap, struct_score)
        
        # Ensure we don't return > 0.9 unless it's a very strong structural match
        if struct_score < 0.4:
            raw_conf = min(raw_conf, 0.4)
            
        return float(max(0.0, min(1.0, raw_conf)))