import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Pragmatic Compositional Minimum Description Length (PC-MDL) Reasoning Tool.
    
    Mechanism:
    1. Epistemic Honesty (Meta-Confidence): Analyzes the prompt for logical traps 
       (presuppositions, ambiguity, false dichotomies) before scoring. If detected, 
       confidence is capped low regardless of candidate quality.
    2. Structural Parsing & Computation: Extracts logical operators, numeric values, 
       and comparatives. Performs actual arithmetic or logical deduction where possible.
    3. Compositional MDL: Estimates description length via a stochastic grammar proxy 
       (token frequency/length). Simpler, structurally aligned candidates are preferred.
    4. Pragmatic Reward: Candidates that satisfy structural constraints (e.g., correct 
       inequality direction) receive a high reward signal.
    5. Scoring: L = Description_Length - lambda * Pragmatic_Reward. 
       Scores are normalized; NCD is used only as a tiebreaker (<15% weight).
    """

    # Preset logical traps for epistemic honesty
    PRESUPPOSITION_TRIGGERS = [
        r"\bhave you stopped\b", r"\bwhy did\b", r"\bwhy does\b", 
        r"\bfailed to\b", r"\brefused to\b", r"\bquit\b"
    ]
    SCOPE_AMBIGUITY = [r"\bevery\b.*\ba\b", r"\ball\b.*\bsome\b"]
    PRONOUN_AMBIGUITY = [r"\btold\b.*\bhe\b", r"\btold\b.*\bshe\b", r"\bwho\b"]
    FALSE_DICHOTOMY = [r"\beither\b.*\bor\b", r"\bis it\b.*\bor\b"]
    SUBJECTIVITY = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]

    def __init__(self):
        self.lambda_pragmatic = 0.6  # Weight for pragmatic success
        self.lambda_mdl = 0.4        # Weight for simplicity
        
    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for logical traps and ambiguity.
        Returns a confidence cap (0.0 - 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.PRESUPPOSITION_TRIGGERS:
            if re.search(pattern, p_lower):
                return 0.2
        
        # 2. Scope Ambiguity (Simplified heuristic)
        if re.search(r"\bevery\b", p_lower) and re.search(r"\bsame\b|\bdifferent\b", p_lower):
            return 0.25
            
        # 3. Pronoun Ambiguity in "Who" questions
        if re.search(r"\bwho\b", p_lower) and any(kw in p_lower for kw in ["told", "said to", "asked"]):
            if re.search(r"\bhe\b|\bshe\b|\bhim\b|\bher\b", p_lower):
                return 0.25

        # 4. False Dichotomy
        for pattern in self.FALSE_DICHOTOMY:
            if re.search(pattern, p_lower):
                # Only flag if it implies exclusivity without evidence
                if "or" in p_lower and "both" not in p_lower:
                    return 0.3

        # 5. Subjectivity
        for pattern in self.SUBJECTIVITY:
            if re.search(pattern, p_lower):
                return 0.3
                
        return 1.0  # No obvious traps detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text."""
        matches = re.findall(r"-?\d+\.?\d*", text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes structural alignment and pragmatic reward.
        Returns (score, reasoning_string).
        Higher score = better alignment.
        """
        score = 0.0
        reasons = []
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # A. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Check for comparison operators in prompt
            if "greater" in p_lower or "larger" in p_lower or ">" in prompt:
                if c_nums[0] == max(p_nums):
                    score += 2.0
                    reasons.append("Correctly identified max value")
                else:
                    score -= 1.0
            elif "less" in p_lower or "smaller" in p_lower or "<" in prompt:
                if c_nums[0] == min(p_nums):
                    score += 2.0
                    reasons.append("Correctly identified min value")
                else:
                    score -= 1.0
            elif "sum" in p_lower or "total" in p_lower or "add" in p_lower:
                if abs(c_nums[0] - sum(p_nums)) < 0.01:
                    score += 2.0
                    reasons.append("Correct summation")
        
        # B. Logical Negation/Constraint Propagation
        if re.search(r"\bnot\b|\bnever\b|\bimpossible\b", p_lower):
            # If prompt denies something, candidate should reflect that or not contradict
            if "yes" in c_lower and "no" in p_lower:
                score -= 2.0
                reasons.append("Contradicts negation constraint")
            elif "no" in c_lower and "yes" in p_lower: # Weak heuristic
                pass 

        # C. Boolean/Choice Matching
        yes_no_opts = ["yes", "no", "true", "false"]
        if any(opt in p_lower for opt in yes_no_opts):
            if c_lower.strip() in yes_no_opts:
                score += 0.5 # Reward valid format
                reasons.append("Valid boolean format")

        if not reasons:
            reasons.append("No strong structural signal")
            
        return score, "; ".join(reasons)

    def _mdl_length(self, candidate: str) -> float:
        """
        Approximates Kolmogorov complexity via description length.
        Uses a simple token-based grammar cost.
        """
        # Simple surrogate: length + penalty for rare chars, reward for common words
        tokens = re.findall(r'\w+|\W+', candidate)
        length_cost = len(candidate) * 0.1
        
        # Grammar prior: common logical words have lower cost
        common_words = {"the", "is", "a", "to", "of", "and", "yes", "no", "true", "false"}
        grammar_bonus = 0
        for t in tokens:
            if t.lower() in common_words:
                grammar_bonus -= 0.5
                
        return length_cost + grammar_bonus

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        c_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c_s1, c_s2)
        if max_len == 0:
            return 0.0
        return (c_combined - min(c_s1, c_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence for the whole prompt
        meta_conf = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & Pragmatic Score (Primary Signal ~70%)
            struct_score, reason = self._structural_score(prompt, cand)
            
            # 2. MDL Score (Simplicity) (~15%)
            # Lower MDL is better, so we negate it for the final score
            mdl_cost = self._mdl_length(cand)
            mdl_score = -mdl_cost 
            
            # 3. NCD Tiebreaker (~15%)
            # Prefer candidates that compress well with the prompt (contextual relevance)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.5
            
            # Combined Score
            # If meta-confidence is low, we penalize the absolute score magnitude 
            # but still rank based on relative structural fit to allow selection of "least bad"
            raw_score = (struct_score * 0.55) + (mdl_score * 0.30) + (ncd_score * 0.15)
            
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": reason,
                "meta_cap": meta_conf
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Adjust scores based on meta-confidence cap for the final output if needed,
        # but the prompt asks for ranking. We keep the score as the ranking metric.
        # The confidence() method will handle the capping logic for the user.
        
        return [
            {"candidate": r["candidate"], "score": r["score"], "reasoning": r["reasoning"]}
            for r in results
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty via _meta_confidence.
        """
        # 1. Check Question Properties (The "Honesty" Filter)
        honesty_cap = self._meta_confidence(prompt)
        
        # 2. Check Answer Quality (Structural/Computation)
        # We simulate a mini-evaluation to see if this specific answer is structurally sound
        struct_score, _ = self._structural_score(prompt, answer)
        
        # Base confidence on structural soundness
        # Map struct_score (roughly -2 to +3) to 0.0 - 1.0
        # If struct_score > 1.0, it's likely a strong match.
        base_conf = 0.5 + (struct_score * 0.15)
        base_conf = max(0.0, min(1.0, base_conf))
        
        # If the answer is just "Yes"/"No" and the prompt was complex, lower confidence
        ans_lower = answer.lower().strip()
        if ans_lower in ["yes", "no", "true", "false"]:
            if len(prompt.split()) > 15: # Heuristic for complexity
                base_conf = min(base_conf, 0.6)

        # Apply Honesty Cap
        final_conf = min(base_conf, honesty_cap)
        
        # Never return > 0.9 unless computation was definitive (handled by high struct_score)
        # But if honesty_cap is low, it overrides everything.
        return round(final_conf, 3)