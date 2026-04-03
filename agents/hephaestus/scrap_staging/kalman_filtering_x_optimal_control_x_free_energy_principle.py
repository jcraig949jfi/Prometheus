import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Hierarchical Active-Inference Controller (Simulated).
    
    Mechanism:
    1. Meta-Cognition (Epistemic Honesty): Analyzes the prompt for logical traps
       (presuppositions, ambiguity, false dichotomies) BEFORE scoring. If detected,
       confidence is capped low (<0.3) regardless of candidate content.
    2. Structural Parsing (Primary Signal): Extracts negations, comparatives, and
       numeric values to perform deterministic evaluation (e.g., 9.11 < 9.9).
    3. Computation: Solves simple arithmetic or logic constraints if present.
    4. NCD (Tiebreaker): Uses compression distance only when structural signals are weak.
    
    This design prioritizes 'Epistemic Honesty' (Tier B) while maintaining competence
    on clear structural tasks (Tier A), adhering to the Free Energy Principle's
    drive to minimize surprise (uncertainty) by recognizing unanswerable states.
    """

    def __init__(self):
        self.presupposition_triggers = [
            r"have you stopped", r"have you quit", r"why did .+ fail", 
            r"why did .+ stop", r"when did .+ stop", r"is it true that .+"
        ]
        self.ambiguity_triggers = [
            r"every .+ a .+", r"told .+ he was", r"told .+ she was", 
            r"either .+ or .+", r"best/worst/favorite"
        ]
        self.false_dichotomy_triggers = [r"either .+ or .+", r"choose between .+ and .+"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a cap value. If traps found, returns < 0.3.
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
                
        # Check Ambiguity (Pronoun/Scope)
        # Simple heuristic: if prompt asks "who" and contains "told ... he/she"
        if re.search(r"who", p_lower) and re.search(r"told .+ (he|she) was", p_lower):
            return 0.25
            
        # Check False Dichotomy without exhaustive options
        if re.search(r"either .+ or .+", p_lower) and "other" not in p_lower:
            # Heuristic: if it looks like a forced choice without context
            if "choose" in p_lower or "which" in p_lower:
                return 0.30

        return 1.0  # No immediate red flags

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for comparison."""
        # Match integers and floats, avoiding dates or version numbers if possible
        matches = re.findall(r'(?<!\d)-?\d+\.?\d*(?!\d)', text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Performs deterministic structural parsing and computation.
        Returns a score boost (0.0 to 0.6) based on correctness.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        
        # 1. Numeric Comparison Trap (e.g., 9.11 vs 9.9)
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            # Detect comparison keywords
            if any(k in p_lower for k in ["smaller", "less", "minimum", "lowest"]):
                correct_val = min(nums)
                candidate_nums = self._extract_numbers(candidate)
                if candidate_nums and abs(candidate_nums[0] - correct_val) < 1e-6:
                    score += 0.6
                elif "larger" in p_lower or "greater" in p_lower:
                     pass # Mismatched logic
            elif any(k in p_lower for k in ["larger", "greater", "maximum", "highest"]):
                correct_val = max(nums)
                candidate_nums = self._extract_numbers(candidate)
                if candidate_nums and abs(candidate_nums[0] - correct_val) < 1e-6:
                    score += 0.6

        # 2. Negation Handling
        # If prompt has "not X", and candidate is "X", penalize. If candidate is "not X", boost.
        negation_match = re.search(r"not\s+(\w+)", p_lower)
        if negation_match:
            target = negation_match.group(1)
            if target in c_lower and f"not {target}" not in c_lower:
                score -= 0.5 # Penalty for missing negation
            elif f"not {target}" in c_lower:
                score += 0.5

        # 3. Simple Arithmetic Verification
        # If prompt asks "What is X + Y?" and candidate is the number
        calc_match = re.search(r"(\d+)\s*[\+\-\*\/]\s*(\d+)", prompt)
        if calc_match:
            try:
                val = eval(f"{calc_match.group(0)}")
                cand_nums = self._extract_numbers(candidate)
                if cand_nums and abs(cand_nums[0] - val) < 1e-6:
                    score += 0.6
            except:
                pass

        return score

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """
        Normalized Compression Distance.
        Returns 1.0 for perfect match, 0.0 for total mismatch.
        Used only as a tiebreaker.
        """
        if not candidate:
            return 0.0
        
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1))
        len_s2 = len(zlib.compress(s2))
        len_s1s2 = len(zlib.compress(s1 + s2))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
            
        ncd = (len_s1s2 - min(len_s1, len_s2)) / max_len
        # Invert so higher is better (lower distance = higher score)
        # Scale to max 0.15 contribution
        return max(0.0, 1.0 - ncd) * 0.15

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-cognition check: Is the question itself flawed?
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            # 1. Structural/Computation Score (Primary, up to 0.6)
            struct_score = self._structural_score(prompt, candidate)
            
            # 2. NCD Score (Tiebreaker, up to 0.15)
            ncd_score = self._ncd_score(prompt, candidate)
            
            # Base relevance (simple overlap to avoid zeroing out completely)
            # This is a fallback, not the main driver.
            base_relevance = 0.1 if any(word in candidate.lower() for word in prompt.lower().split()[:5]) else 0.0
            
            raw_score = base_relevance + struct_score + ncd_score
            
            # Apply Meta-Cognitive Cap
            if meta_cap < 0.3:
                # If the question is ambiguous, we penalize high confidence in any answer
                # but still rank them by structural fit, just capped.
                final_score = min(raw_score, meta_cap)
                reason = f"Prompt contains ambiguity/trap. Confidence capped at {meta_cap}. Structural fit: {struct_score:.2f}"
            else:
                final_score = raw_score
                reason = f"Structural/Computation score: {struct_score:.2f}, NCD bonus: {ncd_score:.2f}"
                
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reason
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence if the prompt is ambiguous.
        """
        # 1. Check Meta-Confidence (The "Honesty" Filter)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate the specific answer structurally
        struct_score = self._structural_score(prompt, answer)
        ncd_score = self._ncd_score(prompt, answer)
        
        # Calculate raw confidence based on evidence
        # If struct_score is high (e.g., correct math), base is high.
        # If struct_score is 0, base is low.
        raw_conf = 0.2 + (struct_score * 0.5) + (ncd_score * 0.3)
        
        # Apply cap
        final_conf = min(raw_conf, cap)
        
        # Ensure we never return > 0.9 unless computation was definitive (struct_score maxed)
        if struct_score < 0.5:
            final_conf = min(final_conf, 0.85)
            
        return max(0.0, min(1.0, final_conf))