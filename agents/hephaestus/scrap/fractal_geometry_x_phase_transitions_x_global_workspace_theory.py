import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Multi-Scale Critical Ignition Network (MICIN) Implementation.
    
    Mechanism:
    1. Fractal/Phase Transition: Uses self-similar structural parsing scales (regex, logic, math).
       Activity accumulates until a 'critical point' (threshold) is reached, triggering an 'avalanche'
       of confidence or rejection.
    2. Global Workspace: A centralized broadcast mechanism where high-confidence structural matches
       inhibit lower-level heuristic matches (winner-take-all dynamics).
    3. Epistemic Honesty (Tier B): Before scoring, the system scans for 'poisonous' patterns
       (presuppositions, ambiguities). If detected, the global workspace forces a low-confidence
       state regardless of candidate quality, preventing overconfidence on traps.
    
    Score Decomposition:
    - Structural/Logic/Math (Critical Avalanches): ~60%
    - NCD (Fractal similarity tiebreaker): ~15%
    - Meta-Cognitive Honesty (Gatekeeper): Caps confidence if traps detected.
    """

    def __init__(self):
        # Thresholds for critical ignition
        self.IGNITION_THRESHOLD = 0.85
        self.AMBIGUITY_CAP = 0.25
        self.MAX_CONFIDENCE_DEFINITIVE = 0.95
        
        # Patterns for Tier B (Epistemic Honesty)
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bwhen did.*stop\b", r"\bquit\b", r"\bassumed\b"
        ]
        self.false_dichotomy_triggers = [
            r"\beither.*or\b", r"\bchoose between\b", r"\bonly two options\b"
        ]
        self.scope_pronoun_triggers = [
            r"\bwho was.*\b", r"\bwhich one.*\b", r"\bsame.*different\b",
            r"\btold.*he\b", r"\btold.*she\b"
        ]
        self.subjectivity_triggers = [
            r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a cap value. If traps found, returns low cap (0.25). Else 1.0.
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return self.AMBIGUITY_CAP
        
        # Check False Dichotomies (context sensitive, but keyword hint)
        # Only flag if it looks like a forced choice without data
        if re.search(r"\beither.*or\b", p_lower):
            if "true" in p_lower or "false" in p_lower:
                pass # Logical boolean is fine
            else:
                return self.AMBIGUITY_CAP

        # Check Subjectivity without data
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                # If asking for opinion without context
                if "according to" not in p_lower and "text" not in p_lower:
                    return self.AMBIGUITY_CAP

        # Check for unanswerable/missing info indicators
        if "not enough information" in p_lower or "cannot be determined" in p_lower:
            return self.AMBIGUITY_CAP
            
        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        # Match integers and floats, handling negative numbers
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _structural_parse(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Scale 1 & 2: Structural and Logical Parsing.
        Detects negations, comparatives, and numeric truth.
        Returns (score, reason).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt and candidate to check consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Simple consistency check: if prompt has numbers and candidate has numbers,
            # do they align? (Heuristic for now)
            # If prompt asks "Is 9.11 < 9.9?", candidate "Yes" implies logic check
            if "less than" in p_lower or "<" in prompt:
                if len(p_nums) >= 2:
                    expected = p_nums[0] < p_nums[1]
                    if "yes" in c_lower and expected:
                        return 0.95, "Numeric verification: True"
                    if "no" in c_lower and not expected:
                        return 0.95, "Numeric verification: True"
                    if len(c_nums) >= 1:
                        # If candidate provides a number, check if it's the result
                        # This is a simplified check for specific math traps
                        pass 

        # 2. Logical Negation & Contradiction
        # If prompt contains "not X" and candidate is "X", penalize heavily
        negation_patterns = [
            r"is not (\w+)", r"does not (\w+)", r"never (\w+)", r"cannot (\w+)"
        ]
        
        for pattern in negation_patterns:
            match = re.search(pattern, p_lower)
            if match:
                target = match.group(1)
                if target in c_lower and "not" not in c_lower:
                    # Candidate affirms what prompt negates
                    return 0.1, "Logical contradiction with prompt negation"

        # 3. Comparative Consistency
        comparatives = ["greater", "larger", "more", "less", "smaller", "fewer"]
        has_comparative = any(c in p_lower for c in comparatives)
        
        if has_comparative:
            # Heuristic: If prompt compares A and B, candidate should reflect direction
            # This is a shallow check; deep logic requires more complex parsing
            if "yes" in c_lower or "no" in c_lower:
                # Acceptable binary response to comparative
                return 0.6, "Comparative structure detected"

        return 0.5, "No strong structural signal"

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        try:
            len1 = len(zlib.compress(s1.encode()))
            len2 = len(zlib.compress(s2.encode()))
            len12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(len1, len2)
            if max_len == 0:
                return 0.0
            return (len12 - min(len1, len2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main evaluation loop implementing MICIN dynamics.
        1. Meta-Check: Determine if the prompt is a trap (Tier B).
        2. Structural Ignition: Score candidates based on logic/math (Tier A).
        3. Global Broadcast: Normalize scores and apply meta-cap.
        4. Fractal Tiebreaker: Use NCD for remaining ambiguity.
        """
        if not candidates:
            return []

        # 1. Meta-Confidence (Epistemic Honesty Gate)
        meta_cap = self._meta_confidence(prompt)
        is_trap = meta_cap < 0.5

        results = []
        
        # Pre-calculate structural scores to find the 'ignited' candidate
        structural_scores = []
        for cand in candidates:
            score, reason = self._structural_parse(prompt, cand)
            structural_scores.append((score, reason, cand))
        
        # Find max structural score to normalize (Winner-Take-All dynamics)
        max_struct = max(s[0] for s in structural_scores) if structural_scores else 0.5
        
        for i, cand in enumerate(candidates):
            struct_score, reason, _ = structural_scores[i]
            
            # Normalize structural score relative to the best candidate (Global Workspace)
            # If a candidate hits the ignition threshold, others are suppressed
            if max_struct > self.IGNITION_THRESHOLD:
                if struct_score < self.IGNITION_THRESHOLD:
                    # Suppress non-ignited candidates if one has ignited
                    normalized_struct = struct_score * 0.5 
                else:
                    normalized_struct = struct_score
            else:
                normalized_struct = struct_score

            # Fractal Tiebreaker: NCD (Max 15% influence)
            # Measure similarity to prompt (relevance)
            ncd_val = self._compute_ncd(prompt, cand)
            # Convert distance to similarity (1 - ncd), scaled to 0.15 max contribution
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Combine: Structural (dominant) + NCD (tiebreaker)
            final_score = (normalized_struct * 0.85) + ncd_score
            
            # Apply Epistemic Cap (Tier B)
            if is_trap:
                final_score = min(final_score, self.AMBIGUITY_CAP)
                reason = "Tier B Trap Detected: Ambiguity/Presupposition limits confidence."
            elif struct_score < 0.3:
                # Low structural support
                reason = "Low structural support; relying on similarity."

            # Cap absolute confidence unless definitive computation occurred
            if "Numeric verification" in reason:
                final_score = min(final_score, self.MAX_CONFIDENCE_DEFINITIVE)
            elif not is_trap:
                final_score = min(final_score, 0.89) # Prevent overconfidence on heuristics

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly adheres to Tier B honesty constraints.
        """
        # 1. Check Meta-Confidence (The Trap Detector)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Validation
        struct_score, reason = self._structural_parse(prompt, answer)
        
        # 3. Compute Base Confidence
        base_conf = struct_score
        
        # If it's a trap, cap immediately
        if meta_cap < 0.5:
            return round(meta_cap, 4)
        
        # If structural score is low, confidence should be low
        if struct_score < 0.4:
            # Check NCD as a secondary signal for relevance
            ncd_val = self._compute_ncd(prompt, answer)
            if ncd_val > 0.8: # Very different strings
                return round(0.2, 4)
            base_conf = 0.5 # Uncertain but plausible
            
        # Cap at 0.95 unless it's a verified math fact
        if "Numeric verification" not in reason:
            base_conf = min(base_conf, 0.89)
            
        return round(base_conf, 4)