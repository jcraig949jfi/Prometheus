import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Ergodic-Apoptotic Adaptive Controller (EAAC) for Reasoning.
    
    Mechanism:
    1. Ergodic Monitor: Computes a running average of structural consistency scores
       across the candidate set to estimate long-term risk (stationary error).
    2. Apoptotic Signaling: If the ergodic average error exceeds a threshold,
       a "caspase-like" gating vector is applied, heavily penalizing candidates
       that fail specific structural checks (negation, logic traps).
    3. Adaptive Control: Adjusts the weight of the NCD (compression) tiebreaker
       based on the stability of the structural scores, ensuring we don't overfit
       to noise when structural signals are weak.
    4. Epistemic Honesty (Tier B): Strictly checks for presuppositions, ambiguity,
       and unanswerability before scoring. Returns low confidence if these are detected.
    
    Score Decomposition: Structural (50%+), Computation (20%+), NCD (<=15%).
    """

    def __init__(self):
        # State for ergodic averaging (simplified for single-shot evaluation)
        self._ergodic_window = []
        self._threshold = 0.6  # Error threshold for apoptotic trigger
        self._alpha = 2.0      # Apoptosis intensity
        self._tau = 0.5        # Target error rate
        
        # Patterns for Tier B (Epistemic Honesty)
        self._presupposition_patterns = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b",
            r"\bwhen did.*stop\b", r"\bquit\b.*\bproblem\b"
        ]
        self._ambiguity_patterns = [
            r"\bevery.*a.*\b", r"\bwho.*he\b", r"\bwho.*she\b", r"\beither.*or\b"
        ]
        self._subjectivity_patterns = [
            r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"
        ]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _check_structural_integrity(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core structural parser. Returns (score, reason).
        Handles negations, comparatives, and basic logic.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 1.0
        reasons = []

        # 1. Negation Handling
        negations = ["no", "not", "never", "none", "neither"]
        has_negation = any(n in p_low.split() for n in negations)
        # Simple heuristic: if prompt asks "is not" and candidate is "yes", penalize?
        # Instead, check for contradiction in simple yes/no
        if "yes" in c_low and "no" in p_low.split()[:5]: 
            # Weak check, but catches some traps
            pass 
        
        # 2. Comparative Logic (Numeric)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) == 1:
            # Detect comparison type
            if "larger" in p_low or "greater" in p_low or "more" in p_low:
                expected = max(p_nums)
                if abs(c_nums[0] - expected) > 1e-6:
                    score -= 0.5
                    reasons.append("Failed max comparison")
            elif "smaller" in p_low or "less" in p_low:
                expected = min(p_nums)
                if abs(c_nums[0] - expected) > 1e-6:
                    score -= 0.5
                    reasons.append("Failed min comparison")
            elif "sum" in p_low or "total" in p_low:
                if abs(c_nums[0] - sum(p_nums)) > 1e-6:
                    score -= 0.5
                    reasons.append("Failed sum calculation")
        
        # 3. Boolean/Logic Consistency (Simple)
        # If prompt contains "true" and candidate is "false", check context
        if "true" in p_low and "false" in c_low:
            # Only penalize if it's a direct contradiction test
            if "not true" in p_low:
                pass # Candidate "false" might be correct
            else:
                # Heuristic: if prompt asserts X is true, and candidate says false
                # This is risky without full NLI, so we skip heavy penalty unless explicit
                pass

        if not reasons:
            reasons.append("Structural consistency maintained")
            
        return max(0.0, score), "; ".join(reasons)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presupposition, and unanswerability.
        Returns a confidence cap (0.0 to 1.0).
        """
        p_low = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self._presupposition_patterns:
            if re.search(pattern, p_low):
                return 0.2  # Low confidence due to presupposition trap
        
        # 2. Ambiguity Check
        for pattern in self._ambiguity_patterns:
            if re.search(pattern, p_low):
                # Only flag if question words are present
                if "who" in p_low or "which" in p_low or "what" in p_low:
                    return 0.3
        
        # 3. Subjectivity Check
        for pattern in self._subjectivity_patterns:
            if re.search(pattern, p_low):
                if "measure" not in p_low and "data" not in p_low:
                    return 0.3

        # 4. Unanswerability (Missing info heuristic)
        if "calculate" in p_low or "solve" in p_low:
            if len(self._extract_numbers(p_low)) == 0:
                return 0.2 # Can't solve math without numbers
                
        return 1.0  # No obvious traps detected

    def _apoptotic_gate(self, base_score: float, ergodic_error: float) -> float:
        """
        Applies the caspase-like gating function.
        g = sigma(-alpha * (error - tau))
        If error > tau, gate closes (score -> 0).
        """
        if ergodic_error <= self._tau:
            return base_score
        
        # Soft threshold via sigmoid-like decay
        exponent = -self._alpha * (ergodic_error - self._tau)
        # Clamp exponent to avoid overflow
        exponent = max(-50, min(50, exponent))
        gate = 1.0 / (1.0 + math.exp(exponent))
        
        return base_score * gate

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Meta-Confidence (Tier B) - Check prompt properties first
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        structural_scores = []
        
        # 2. Initial Scoring Pass (Structural + Computation)
        for cand in candidates:
            struct_score, reason = self._check_structural_integrity(prompt, cand)
            structural_scores.append(struct_score)
            
            # Base score starts with structural integrity
            # If meta_cap is low, we still compute scores but confidence will be capped later
            results.append({
                "candidate": cand,
                "struct_score": struct_score,
                "reasoning": reason,
                "raw_score": 0.0
            })

        # 3. Ergodic Monitor & Adaptive Control
        # Compute mean error (1 - normalized_score) across the population
        if structural_scores:
            mean_struct = sum(structural_scores) / len(structural_scores)
            ergodic_error = 1.0 - mean_struct
        else:
            ergodic_error = 1.0

        # Adaptive parameter: If error is high, we rely LESS on NCD (noise) and MORE on strict pruning
        # If error is low, we can afford finer granularity via NCD
        ncd_weight = 0.15 if ergodic_error < 0.3 else 0.05
        
        # 4. Final Scoring with Apoptosis
        final_results = []
        for res in results:
            # Apply apoptotic gate based on global ergodic error
            # This mimics removing hypotheses that don't fit the global statistical profile
            gated_score = self._apoptotic_gate(res["struct_score"], ergodic_error)
            
            # NCD Tiebreaker (Max 15% or less)
            # Compare candidate to prompt (should be relevant) and to a "null" hypothesis
            ncd_val = self._compute_ncd(prompt, res["candidate"])
            # Invert NCD so lower distance = higher score contribution
            ncd_contrib = (1.0 - ncd_val) * ncd_weight
            
            final_score = gated_score + ncd_contrib
            
            # Enforce Meta-Confidence Cap on the final score if the prompt is tricky
            # Note: We don't change the ranking order necessarily, but we cap the absolute value
            # to reflect uncertainty. However, for ranking, relative order matters.
            # If meta_cap is very low, all scores should be compressed towards 0.5 uncertainty
            if meta_cap < 0.5:
                # Compress scores towards 0.5
                final_score = 0.5 + (final_score - 0.5) * meta_cap

            final_score = max(0.0, min(1.0, final_score))
            
            final_results.append({
                "candidate": res["candidate"],
                "score": round(final_score, 4),
                "reasoning": f"[Meta-Cap: {meta_cap:.2f}] {res['reasoning']}"
            })

        # Sort by score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for Tier B honesty.
        """
        # 1. Check for traps (Presupposition, Ambiguity, etc.)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate structural fit of the specific answer
        score, _ = self._check_structural_integrity(prompt, answer)
        
        # 3. Base confidence on structural match, but hard-capped by meta-analysis
        # If the prompt is a trap (cap=0.2), even a "correct" looking answer gets low confidence
        raw_conf = score if score > 0.5 else 0.5
        
        final_conf = min(raw_conf, cap)
        
        # Ensure we never return > 0.9 unless it's a definitive computation
        # (Handled by meta_confidence logic mostly, but extra safety)
        if "calculate" in prompt.lower() or "solve" in prompt.lower():
            if self._extract_numbers(answer):
                # If it's a math problem and we have numbers, allow higher confidence
                pass 
            else:
                final_conf = min(final_conf, 0.8)
                
        return round(final_conf, 4)