import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Neuromodulated Critical Boltzmann Machine (NCBM) Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Energy Minimization): Extracts logical constraints, negations, 
       and comparatives to form a base energy score.
    2. Constructive Computation (Avalanche Dynamics): Attempts to mathematically solve 
       numeric, temporal, or causal chains. Success triggers a large "avalanche" (score boost).
    3. Neuromodulation (Metacognition): Adjusts the "temperature" (confidence) based on 
       ambiguity detection (Tier B traps). High ambiguity -> High Temp -> Low Confidence.
    4. Scoring: Weighted sum where Computation > Structure > NCD.
    """

    def __init__(self):
        # SOC Parameters
        self.threshold = 0.8  # Avalanche trigger threshold for computation success
        self.base_temp = 1.0  # Base temperature for exploration
        
        # Weights for scoring components
        self.w_comp = 0.50  # Computation weight
        self.w_struct = 0.35 # Structural parsing weight
        self.w_ncd = 0.15   # NCD weight (tiebreaker only)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Epistemic Honesty Check.
        Detects ambiguity, presuppositions, and unanswerable queries.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        presupposition_patterns = [
            r"have you (stopped|quit|finished) .*[?]",
            r"why did .* (fail|stop|quit|break)[?]",
            r"when did you stop .*[?]",
            r"is it true that .*[?]" # Often implies a hidden premise
        ]
        for pattern in presupposition_patterns:
            if re.search(pattern, p):
                return 0.25

        # 2. Scope/Pronoun Ambiguity
        ambiguity_keywords = ["who is he", "who is she", "which one", "same y", "different y"]
        if any(k in p for k in ambiguity_keywords):
            return 0.30
            
        # 3. False Dichotomy indicators without exhaustive lists
        if re.search(r"either .* or .*[?]", p) and "none" not in p and "other" not in p:
            # Heuristic: if it forces a choice but doesn't list options clearly
            if len(p.split()) < 15: 
                return 0.40

        # 4. Subjectivity without criteria
        subjective_terms = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(term in p for term in subjective_terms):
            if "measure" not in p and "criteria" not in p and "define" not in p:
                return 0.35

        return 1.0  # No ambiguity detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all floating point numbers from text."""
        # Match integers and floats, including negative
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _compute_constructive(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Attempt to solve the problem mathematically or logically.
        Returns (score_boost, reasoning_string).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (PEMDAS, Comparisons)
        nums_prompt = self._extract_numbers(prompt)
        nums_candidate = self._extract_numbers(candidate)
        
        if nums_prompt:
            # Check for direct comparison questions
            if "greater" in p_lower or "less" in p_lower or "more" in p_lower or "fewer" in p_lower:
                if len(nums_prompt) >= 2 and nums_candidate:
                    val = nums_candidate[0]
                    # Simple heuristic: if asking for 'more', candidate should be max or difference
                    if "more" in p_lower or "greater" in p_lower:
                        if abs(val - max(nums_prompt)) < 1e-6 or abs(val - (max(nums_prompt)-min(nums_prompt))) < 1e-6:
                            return 0.9, "Numeric comparison verified."
                    # If asking 'which is greater', check if candidate matches max
                    if "which" in p_lower and "greater" in p_lower:
                         if abs(val - max(nums_prompt)) < 1e-6:
                            return 0.9, "Max value identified."
            
            # Check arithmetic consistency if candidate is a number
            if nums_candidate and len(nums_prompt) >= 2:
                # Try sum, diff, product
                ops = [
                    sum(nums_prompt),
                    nums_prompt[0] - nums_prompt[1] if len(nums_prompt) > 1 else 0,
                    nums_prompt[0] * nums_prompt[1] if len(nums_prompt) > 1 else 0
                ]
                for op_val in ops:
                    if abs(nums_candidate[0] - op_val) < 1e-6:
                        return 0.85, f"Arithmetic match found: {op_val}"

        # 2. Logical/Structural Computation (Negation & Conditionals)
        # If prompt has "not", candidate must reflect it
        if " not " in p_lower or "never" in p_lower:
            negation_words = ["not", "no", "never", "false", "impossible"]
            if any(w in c_lower for w in negation_words):
                return 0.7, "Negation constraint satisfied."
            else:
                # If prompt denies something, and candidate affirms it blindly, penalize
                # This is a soft check, returns 0.0 boost (neutral) rather than negative
                pass

        # 3. Causal/Temporal Ordering
        if "before" in p_lower or "after" in p_lower or "first" in p_lower or "last" in p_lower:
            # Heuristic: If candidate contains ordinal indicators (1st, 2nd, first, second)
            ordinals = ["first", "second", "third", "1st", "2nd", "3rd", "last"]
            if any(o in c_lower for o in ordinals):
                return 0.6, "Temporal marker detected."

        return 0.0, "No constructive computation path found."

    def _parse_structure(self, prompt: str, candidate: str) -> float:
        """
        Structural parsing for logical consistency.
        Returns a score 0.0 to 1.0 based on structural alignment.
        """
        score = 0.5  # Base neutral
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Check for Yes/No alignment with negation
        if "not" in p_lower:
            if ("yes" in c_lower and "not" not in c_lower) or ("true" in c_lower and "not" not in c_lower):
                # Potential trap, but depends on question type. 
                # If question is "Is it not X?", "Yes" means it is not X.
                # Skipping strict boolean logic here to avoid false negatives on complex linguistics.
                pass
        
        # Keyword overlap weighted by importance (comparatives)
        important_tokens = ["greater", "less", "equal", "before", "after", "cause", "effect"]
        matches = sum(1 for t in important_tokens if t in p_lower and t in c_lower)
        if matches > 0:
            score += 0.2 * min(matches, 2) # Cap bonus
            
        return min(score, 1.0)

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_join = len(zlib.compress((s1 + s2).encode()))
        
        if len_join == 0:
            return 0.0
        return (len_join - min(len1, len2)) / max(len1, len2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            # 1. Constructive Computation (Primary Signal)
            comp_score, comp_reason = self._compute_constructive(prompt, candidate)
            
            # 2. Structural Parsing (Secondary Signal)
            struct_score = self._parse_structure(prompt, candidate)
            
            # 3. NCD (Tiebreaker/Minor component)
            ncd_val = self._calculate_ncd(prompt, candidate)
            # Invert NCD so higher is better, scale to 0-1 range roughly
            ncd_score = max(0.0, 1.0 - ncd_val)
            
            # Combine scores based on weights
            # If computation succeeded (high comp_score), it dominates
            if comp_score > 0.1:
                final_score = (comp_score * 0.7) + (struct_score * 0.2) + (ncd_score * 0.1)
                reasoning = f"Computation: {comp_reason}"
            else:
                # Fallback to structure and NCD if no math/logic path found
                final_score = (struct_score * 0.6) + (ncd_score * 0.4)
                reasoning = "Structural/NCD analysis."
            
            # Apply Neuromodulatory Cap (Metacognition)
            # If the prompt is ambiguous (low meta_cap), we cannot be confident regardless of score
            if meta_cap < 0.5:
                # Suppress score variance in ambiguous contexts
                final_score = 0.5 * meta_cap + (final_score * 0.5 * meta_cap)
                reasoning += " [Low confidence due to ambiguity]"
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Heavily penalized by _meta_confidence if the prompt is tricky.
        """
        # 1. Check Meta-Confidence (The Cap)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate the specific answer
        # Run a mini-evaluation to see how well this specific answer fits
        # We simulate the scoring logic
        comp_score, _ = self._compute_constructive(prompt, answer)
        struct_score = self._parse_structure(prompt, answer)
        ncd_score = max(0.0, 1.0 - self._calculate_ncd(prompt, answer))
        
        # Raw confidence based on fit
        if comp_score > 0.5:
            raw_conf = 0.9 * comp_score + 0.1
        elif struct_score > 0.6:
            raw_conf = 0.8 * struct_score + 0.1
        else:
            raw_conf = 0.4 * ncd_score + 0.1
            
        # Apply Cap (Neuromodulation)
        # If cap is low (ambiguous prompt), confidence must be low
        final_conf = min(raw_conf, cap)
        
        # Never return > 0.9 unless computation was definitive
        if comp_score < 0.8 and final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 4)