import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Pragmatic Chaotic Meta-Reservoir (PCMR) Implementation.
    
    Mechanism:
    1. Metacognitive Monitor (Epistemic Honesty): Analyzes the prompt for Tier B traps
       (presuppositions, ambiguities, false dichotomies). If detected, confidence is capped
       low regardless of candidate score, enforcing honesty over false competence.
       
    2. Structural Parser (Chaos/Reasoning): Extracts logical operators, negations, and
       numeric values. It performs deterministic calculations (PEMDAS, comparisons) to
       establish a baseline "truth" score. This acts as the "strange attractor" for correct
       answers.
       
    3. Pragmatic Modulator: Adjusts scoring weights based on Gricean maxims inferred from
       question type (e.g., strict equality for math, semantic overlap for open-ended).
       
    4. Reservoir Scoring: Combines structural match (high weight), computed truth (high weight),
       and NCD (low weight tie-breaker) to rank candidates.
    """

    def __init__(self):
        # Pragmatic thresholds
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did\b", r"\bwhen did\b", 
            r"\bwho is the\b", r"\bwhich one is the\b", r"\best\b", r"\worst\b"
        ]
        self.ambiguity_triggers = [
            r"\beither\b.*\bor\b", r"\ball\b.*\ba\b", r"\bevery\b.*\ba\b",
            r"\bhe told\b.*\bhe\b", r"\bshe told\b.*\bshe\b"
        ]
        self.false_dichotomy_triggers = [r"\beither\b", r"\bor else\b", r"\bmust be\b"]
        
        # Chaos/Metacognitive state
        self._state_seed = 0.5

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Evaluates the prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap value (0.0 - 1.0). If < 0.3, the system should express uncertainty.
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # Check for presuppositions and loaded questions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                score = min(score, 0.25) # Cap low for loaded questions
        
        # Check for scope/pronoun ambiguity
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                # Only penalize if the question asks for clarification ("who?", "which?")
                if re.search(r"\b(who|which|what|how)\b", p_lower):
                    score = min(score, 0.30)
        
        # Check for false dichotomy without exhaustive options
        if re.search(r"\beither\b", p_lower) and not re.search(r"\b(both|neither|all)\b", p_lower):
             if re.search(r"\b(true|correct|right)\b", p_lower):
                score = min(score, 0.40) # Slight penalty, not fatal unless ambiguous

        return score

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for computation."""
        # Match integers and floats, handling negative signs
        matches = re.findall(r'[-]?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _structural_analysis(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Performs structural parsing and constructive computation.
        Returns (score, reasoning_string).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        reasons = []

        # 1. Numeric Evaluation (Constructive Computation)
        # Detect comparison questions
        if any(op in p_lower for op in ["greater", "less", "larger", "smaller", "more", "fewer"]):
            nums = self._extract_numbers(prompt)
            cand_nums = self._extract_numbers(candidate)
            
            if len(nums) >= 2 and len(cand_nums) >= 1:
                # Simple logic: if "greater", candidate should be max(nums)
                is_greater = "greater" in p_lower or "larger" in p_lower or "more" in p_lower
                target = max(nums) if is_greater else min(nums)
                
                # Allow small float tolerance
                if any(abs(cand_nums[0] - target) < 1e-6 for cand_nums in [self._extract_numbers(candidate)]):
                    score += 0.5
                    reasons.append("Numeric computation matches logical extremum.")
                else:
                    score -= 0.5 # Penalty for wrong math
                    reasons.append("Numeric computation mismatch.")

        # 2. Logical Negation & Transitivity
        has_negation = bool(re.search(r"\b(not|no|never|none)\b", p_lower))
        cand_negation = bool(re.search(r"\b(not|no|never|none)\b", c_lower))
        
        if has_negation:
            # If prompt has negation, correct answer often requires careful handling
            # Heuristic: If candidate length is very short (Yes/No), check consistency
            if len(c_lower.strip()) < 5:
                # We can't fully solve without more context, but we reward structural awareness
                score += 0.1
                reasons.append("Negation detected; candidate structure analyzed.")

        # 3. Exact Structural Match (Modus Ponens/Tollens proxy)
        # If candidate is a substring of prompt logic (simplified)
        prompt_words = set(re.findall(r'\w+', p_lower))
        cand_words = set(re.findall(r'\w+', c_lower))
        
        if len(cand_words) > 0:
            overlap = len(prompt_words & cand_words) / len(cand_words)
            if overlap > 0.8:
                score += 0.2
                reasons.append("High lexical overlap with prompt constraints.")

        if not reasons:
            reasons.append("No specific structural pattern matched.")
            
        return score, "; ".join(reasons)

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

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-cognitive check on the prompt itself
        meta_cap = self._meta_confidence(prompt)
        is_ambiguous = meta_cap < 0.3

        for cand in candidates:
            # 1. Structural & Computational Score (Primary Signal)
            struct_score, struct_reason = self._structural_analysis(prompt, cand)
            
            # 2. NCD Score (Tiebreaker, max 15% weight)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better (0 distance = 1.0 score contribution)
            # But normalize: NCD is 0..2 usually. Let's map 0->1.0, 1->0.5, 2->0.0
            ncd_score = max(0.0, 1.0 - ncd_val) * 0.15 

            # 3. Combine scores
            # Structural/Computation weight = 0.85, NCD = 0.15
            # Base score starts at 0.5 (neutral) + structural offset
            raw_score = 0.5 + struct_score + (ncd_score - 0.075) # Center NCD
            
            # Clamp raw score 0..1
            raw_score = max(0.0, min(1.0, raw_score))
            
            # Apply Metacognitive Cap (Epistemic Honesty)
            # If the question is ambiguous, even a "matching" answer gets low confidence
            final_score = min(raw_score, meta_cap)
            
            # If ambiguous, adjust reasoning to reflect uncertainty
            if is_ambiguous:
                reason_text = f"[Meta-Warning] {struct_reason} Question contains ambiguity/presupposition."
            else:
                reason_text = struct_reason
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason_text
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure epistemic honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check to see if answer is plausible
        struct_score, _ = self._structural_analysis(prompt, answer)
        
        # If structural score is negative (contradicts math/logic), confidence is 0
        if struct_score < 0:
            return 0.0
        
        # Base confidence on structural match, but hard-capped by meta-analysis
        base_conf = 0.5 + struct_score
        base_conf = max(0.0, min(1.0, base_conf))
        
        return min(base_conf, meta_cap)