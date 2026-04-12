import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    CAN-Reservoir: Chaotic Autopoietic Neuromodulator for Reasoning.
    
    Mechanism:
    1. Chaos Theory: Uses NCD (compression distance) as a baseline 'chaotic' metric 
       for semantic similarity, but keeps it bounded (Edge of Chaos).
    2. Autopoiesis: A self-monitoring loop (_meta_confidence) that inspects the 
       prompt's structural integrity. If the prompt contains logical traps 
       (presuppositions, ambiguity), the system 'prunes' its confidence to preserve 
       epistemic honesty (organizational closure).
    3. Neuromodulation: Dynamically adjusts the weighting between structural parsing 
       (exploitation) and semantic similarity (exploration) based on the presence 
       of numeric or logical operators. High gain on structure when detected.
    
    Score Decomposition:
    - Structural/Logical Parsing: 50%
    - Computational/Numeric: 20% 
    - NCD (Chaos/Similarity): 15%
    - Meta-Confidence Cap: Applied globally.
    """

    def __init__(self):
        # Autopoietic state: tracks internal stability (conceptual)
        self._integrity_threshold = 0.3 
        # Neuromodulatory gains
        self._structure_gain = 0.65
        self._chaos_gain = 0.20
        self._computation_gain = 0.15

    def _normalized_compression_distance(self, s1: str, s2: str) -> float:
        """Calculates NCD using zlib. 0.0 = identical, 1.0 = totally different."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0:
                return 0.0
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text."""
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text)]

    def _check_numeric_logic(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Constructive computation: Solves simple numeric comparisons or extractions.
        Returns a score (1.0 if correct, 0.0 if wrong) or None if not applicable.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # Case 1: Direct number match in candidate vs prompt extraction
        if p_nums and c_nums:
            # If prompt asks for a calculation result implicitly present
            # Simple heuristic: if candidate number matches the last number in prompt
            # This handles simple "What is 2+2?" -> "4" if parsed, but mostly 
            # handles "Which is larger? 5 or 3" -> "5"
            if "larger" in prompt.lower() or "max" in prompt.lower() or "greater" in prompt.lower():
                if c_nums[0] == max(p_nums):
                    return 1.0
                elif c_nums[0] == min(p_nums):
                    return 0.2 # Penalize wrong max
            elif "smaller" in prompt.lower() or "min" in prompt.lower() or "less" in prompt.lower():
                if c_nums[0] == min(p_nums):
                    return 1.0
            
            # Exact match of a specific number mentioned
            if len(c_nums) == 1 and len(p_nums) == 1:
                if abs(c_nums[0] - p_nums[0]) < 1e-6:
                    return 1.0

        # Case 2: Boolean/Logic keywords implying specific numbers
        lower_c = candidate.lower().strip()
        lower_p = prompt.lower()
        
        if "compare" in lower_p or "larger" in lower_p:
            nums = self._extract_numbers(prompt)
            if len(nums) >= 2:
                max_val = max(nums)
                # Check if candidate text contains the string of the max number
                if str(max_val) in candidate:
                    return 1.0
                if str(int(max_val)) in candidate: # Handle float/int mismatch
                    return 1.0

        return None

    def _check_structural_logic(self, prompt: str, candidate: str) -> float:
        """
        Structural parsing: Checks for negations, conditionals, and transitivity.
        Returns a score 0.0 to 1.0.
        """
        score = 0.0
        lower_p = prompt.lower()
        lower_c = candidate.lower().strip()
        
        # 1. Negation handling
        if re.search(r'\b(not|no|never|none)\b', lower_p):
            # If prompt has negation, candidate should reflect it or be specific
            if re.search(r'\b(not|no|never|none)\b', lower_c):
                score += 0.4
            else:
                # If candidate ignores negation, penalize heavily if it looks like a direct answer
                score -= 0.2
        
        # 2. Yes/No consistency with question type
        is_yes_no = any(x in lower_c for x in ['yes', 'no', 'true', 'false'])
        is_question = '?' in prompt
        
        if is_question and is_yes_no:
            # Basic heuristic: if prompt implies a contradiction, 'no' is often better
            if "impossible" in lower_p or "contradict" in lower_p:
                if "no" in lower_c or "false" in lower_c:
                    score += 0.5
                else:
                    score -= 0.5
            
            # If prompt asks "Is it true that...", candidate must be yes/no
            if "is it true" in lower_p or "does it" in lower_p:
                score += 0.3 # Reward structural alignment

        # 3. Option matching (A/B/C/D)
        options = re.findall(r'\b([A-D])\)[\s:]', prompt.upper())
        if options:
            # Candidate should ideally start with the option letter
            candidate_match = re.match(r'^\s*([A-D])', candidate.upper())
            if candidate_match:
                if candidate_match.group(1) in options:
                    score += 0.6
            # Also check if the text after the letter matches candidate content roughly
            # (Simplified for this constraint)
            
        return max(0.0, min(1.0, score))

    def _meta_confidence(self, prompt: str) -> float:
        """
        Epistemic Honesty Check (Autopoietic Boundary).
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0). If < 0.3, the system refuses to be confident.
        """
        lower_p = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_triggers = [
            "have you stopped", "have you quit", "why did", "when did", 
            "how often did", "regret", "fail to", "stopped x", "quit x"
        ]
        for trigger in presupposition_triggers:
            if trigger in lower_p:
                # Check if it's asking about a past event that might not have happened
                if "stop" in lower_p or "quit" in lower_p or "fail" in lower_p:
                    return 0.2 # Low confidence cap

        # 2. Scope Ambiguity
        if re.search(r'every.*a\s+\w+', lower_p) and ("same" in lower_p or "different" in lower_p):
            return 0.25

        # 3. Pronoun Ambiguity
        # "X told Y he..." patterns
        if re.search(r'\b(told|said|asked)\b.*\b(he|she|him|her)\b', lower_p):
            if "who" in lower_p and "?" in prompt:
                return 0.25

        # 4. False Dichotomy
        if re.search(r'\beither\b.*\bor\b', lower_p):
            if "only" in lower_p or "must" in lower_p:
                return 0.3

        # 5. Subjectivity without criteria
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(word in lower_p for word in subjective_words):
            if "according to" not in lower_p and "data" not in lower_p:
                return 0.3

        # 6. Unanswerability / Missing Info
        if "information not present" in lower_p or "cannot be determined" in lower_p:
            return 0.9 # Actually high confidence that it's unanswerable if stated
        if re.search(r'\b(if|suppose)\b.*\bthen\b', lower_p) and "missing" in lower_p:
             return 0.2

        return 1.0 # Default: No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-cognitive check on the prompt itself
        meta_cap = self._meta_confidence(prompt)
        
        # Check for computational/structural solvability
        comp_scores = []
        for cand in candidates:
            comp_score = self._check_numeric_logic(prompt, cand)
            comp_scores.append(comp_score)
        
        # If we have a clear computational winner, boost it
        has_computational_answer = any(s == 1.0 for s in comp_scores)
        
        for i, candidate in enumerate(candidates):
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural Parsing (High Weight)
            struct_score = self._check_structural_logic(prompt, candidate)
            
            # 2. Computational Check (Medium Weight)
            comp_score = comp_scores[i]
            if comp_score is not None:
                # If we found a computational match, it dominates
                final_comp = comp_score * self._computation_gain * 4.0 # Boost factor
                reasoning_parts.append(f"Computation: {comp_score:.2f}")
            else:
                final_comp = 0.0
            
            # 3. Chaos/NCD (Low Weight, Tiebreaker)
            # Compare candidate to prompt (similarity) and to other candidates (diversity)
            # Simplified: Similarity to prompt keywords
            ncd_score = 1.0 - self._normalized_compression_distance(prompt, candidate)
            # Normalize NCD contribution
            final_ncd = ncd_score * self._chaos_gain
            
            # Combine scores
            # Base score is a mix of structure and NCD
            raw_score = (struct_score * self._structure_gain) + final_ncd + final_comp
            
            # Apply Computational Override
            if comp_score == 1.0:
                raw_score = 0.95 # Strong signal for correct math
            elif comp_score == 0.0:
                raw_score = 0.1 # Strong penalty for wrong math
            
            # Apply Autopoietic Cap (Epistemic Honesty)
            if meta_cap < 0.3:
                # If the prompt is a trap, we cap the confidence regardless of candidate
                # But we still rank them by how well they handle the trap (e.g. saying "No")
                raw_score = min(raw_score, meta_cap + 0.1) 
                reasoning_parts.append("Meta-Cap: Ambiguous/Trap detected")
            
            # Normalize to 0-1
            final_score = max(0.0, min(1.0, raw_score))
            
            # Adjust reasoning string
            if struct_score > 0.3:
                reasoning_parts.append("Structural alignment detected")
            if not reasoning_parts:
                reasoning_parts.append("Baseline semantic match")
                
            results.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Heavily penalized by _meta_confidence if the prompt is a trap.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        struct_score = self._check_structural_logic(prompt, answer)
        comp_score = self._check_numeric_logic(prompt, answer)
        
        base_conf = 0.5
        if comp_score == 1.0:
            base_conf = 0.9
        elif comp_score == 0.0:
            base_conf = 0.1
        elif struct_score > 0.4:
            base_conf = 0.7
        elif struct_score < 0.1:
            base_conf = 0.3
            
        # Apply cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive
        if comp_score != 1.0 and final_conf > 0.85:
            final_conf = 0.85
            
        return round(max(0.0, min(1.0, final_conf)), 4)