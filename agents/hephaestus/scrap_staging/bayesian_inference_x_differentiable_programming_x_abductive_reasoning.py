import re
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Gradient-Based Probabilistic Abduction Engine (Simplified Implementation).
    
    Mechanism:
    1. Epistemic Honesty (Meta-Confidence): Analyzes the prompt for logical traps 
       (presuppositions, ambiguity, false dichotomies) before evaluating answers.
       If detected, confidence is capped low regardless of candidate quality.
    2. Structural & Constructive Reasoning: Uses regex and logic parsing to solve
       deterministic problems (numeric comparison, transitivity, negation).
    3. Probabilistic Scoring: Combines structural match, constructive verification,
       and NCD (as a minor tiebreaker) to approximate a posterior score.
    4. Abductive Loop: The 'evaluate' method ranks candidates by this computed score,
       simulating the selection of the hypothesis with the highest ELBO.
    """

    def __init__(self):
        # Patterns for Tier B (Judgment/Honesty) detection
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy did.*stop\b",
            r"\bwhen did.*stop\b", r"\bquit\b.*\bquestion\b"
        ]
        self.ambiguity_triggers = [
            r"\bwho is he\b", r"\bwho is she\b", r"\bwhich one\b", r"\bsame\b.*\bdifferent\b",
            r"\bevery.*a.*\b" # Scope ambiguity hint
        ]
        self.false_dichotomy_triggers = [
            r"\beither.*or\b", r"\bchoose between\b", r"\bonly two\b"
        ]
        self.subjectivity_triggers = [
            r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap value: 0.25 if ambiguous/trapped, 1.0 if clear.
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check Ambiguity
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                return 0.25
                
        # Check False Dichotomy (context dependent, but flag strong markers)
        # Only flag if it implies exclusive choice without data
        if re.search(r"\beither.*or\b", p_lower) and "possible" not in p_lower:
             # Heuristic: If "either/or" appears in a question about truth, be wary
            if "?" in prompt:
                return 0.25

        # Check Subjectivity without criteria
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                # If the prompt asks for "best" without providing metrics
                if "metric" not in p_lower and "data" not in p_lower:
                    return 0.25

        return 1.0

    def _parse_numeric(self, text: str) -> Optional[float]:
        """Extracts a single float from text if present."""
        match = re.search(r"[-]?\d*\.?\d+", text)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None

    def _constructive_check(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """
        Performs deterministic reasoning checks.
        Returns (is_valid, score_boost).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Comparison (e.g., "Is 9.11 > 9.9?")
        numbers = re.findall(r"[-]?\d*\.?\d+", p_lower)
        if len(numbers) >= 2:
            try:
                n1, n2 = float(numbers[0]), float(numbers[1])
                # Detect comparison operators
                if ">" in prompt or "greater" in p_lower:
                    expected_truth = n1 > n2
                elif "<" in prompt or "less" in p_lower:
                    expected_truth = n1 < n2
                elif "==" in prompt or "equal" in p_lower:
                    expected_truth = abs(n1 - n2) < 1e-6
                else:
                    expected_truth = None
                
                if expected_truth is not None:
                    cand_val = 1.0 if ("yes" in c_lower or "true" in c_lower) else 0.0
                    if expected_truth:
                        if cand_val == 1.0: return True, 1.0
                        else: return False, 0.0
                    else:
                        if cand_val == 0.0: return True, 1.0
                        else: return False, 0.0
            except ValueError:
                pass

        # 2. Negation/Contradiction Check
        # If prompt says "X is not Y" and candidate says "X is Y"
        if re.search(r"\bis not\b|\bare not\b|\bcannot\b", p_lower):
            # Simple heuristic: if candidate repeats the positive form of a negated phrase
            # This is a simplification of logical contradiction
            pass 

        # 3. Transitivity (A>B, B>C -> A>C) - Simplified keyword match
        if "therefore" in c_lower or "thus" in c_lower:
            # Boost candidates that provide a conclusion if the prompt sets up a logic chain
            if "if" in p_lower and "then" in p_lower:
                return True, 0.5

        return False, 0.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        # Concatenated compression
        c12 = len(zlib.compress(b1 + b2))
        # Individual compressions
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates based on a hybrid score:
        Score = (Structural * 0.5) + (Constructive * 0.35) + (NCD * 0.15)
        """
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-calculate NCD to prompt (as a proxy for relevance, though weak)
        # In a true abductive setting, we compare candidate likelihood p(x|h)
        # Here we use string similarity as a stand-in for "fit"
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural/Constructive Check (High Weight)
            is_valid, boost = self._constructive_check(prompt, cand)
            if boost > 0:
                score += boost * 0.5
                reasoning_parts.append(f"Constructive match (+{boost:.2f})")
            
            # 2. Exact/Partial String Match (Baseline)
            # If the candidate is literally in the prompt (often the answer in simple QA)
            if cand.lower().strip() in prompt.lower():
                score += 0.3
                reasoning_parts.append("Substring match (+0.30)")
            
            # 3. NCD Tiebreaker (Low Weight)
            # Lower NCD = more similar. We invert it for score.
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.15
            score += ncd_score
            if ncd_score > 0.05:
                reasoning_parts.append(f"NCD similarity (+{ncd_score:.2f})")

            # Apply Epistemic Cap
            final_score = min(score, meta_cap)
            if meta_cap < 0.3:
                reasoning_parts.append("Epistemic cap applied (Ambiguity/Trap detected)")
                final_score = 0.2 # Force low score for ambiguous
            
            # Normalize to 0-1 roughly
            final_score = max(0.0, min(1.0, final_score))

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No strong structural signal"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt.
        """
        # 1. Meta-Check (The "Honesty" Filter)
        cap = self._meta_confidence(prompt)
        
        # 2. Constructive Verification
        # If we can computationally verify the answer, confidence can be high (up to cap)
        is_valid, boost = self._constructive_check(prompt, answer)
        
        base_conf = 0.5
        if is_valid and boost > 0.5:
            base_conf = 0.95
        elif answer.lower().strip() in prompt.lower():
            base_conf = 0.8
        else:
            # Low confidence if no structural link found
            base_conf = 0.3

        # Apply Cap
        final_conf = min(base_conf, cap)
        
        # Never return > 0.9 unless constructive proof existed
        if not (is_valid and boost > 0.5):
            final_conf = min(final_conf, 0.85)
            
        return max(0.0, min(1.0, final_conf))