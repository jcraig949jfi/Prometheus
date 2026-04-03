import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Critical-Adaptive Program Synthesizer (CAPS) Implementation.
    
    Mechanism:
    1. Epistemic Honesty (Meta-Control): Before scoring, analyzes the prompt for 
       logical traps (presuppositions, ambiguity, false dichotomies). If detected,
       confidence is capped low (<0.3) regardless of candidate content.
    2. Structural Parsing & Computation (The Engine): Extracts negations, comparatives,
       and numeric values. Performs actual float comparisons and logic checks.
       This constitutes >50% of the score.
    3. SOC-Inspired Adaptation: Uses a simplified avalanche metric based on 
       candidate length variance and structural complexity to adjust scoring bias,
       simulating the "critical point" between small tweaks and large rewrites.
    4. NCD Tiebreaker: Used only when structural signals are weak (<15% weight).
    """

    def __init__(self):
        # Patterns for structural parsing
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = ['>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer']
        self.presupposition_triggers = [
            r"have you stopped", r"did you stop", r"why did.*fail", r"why.*stop",
            r"when did.*stop", r"how often.*fail"
        ]
        self.ambiguity_triggers = [
            r"every.*a.*\?", r"told.*he.*\?", r"told.*she.*\?", r"either.*or",
            r"best.*without", r"favorite.*without"
        ]
        self.false_dichotomy_triggers = [r"either.*or", r"is it.*or.*\?"]
        
        # SOC State: Tracks "avalanche" sizes (changes in score delta) to tune sensitivity
        self._avalanche_history = [] 
        self._sensitivity = 0.5 # Adaptive control parameter

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_negations(self, text: str) -> int:
        words = re.findall(r'\b\w+\b', self._normalize(text))
        return sum(1 for w in words if w in self.negation_words)

    def _extract_numbers(self, text: str) -> List[float]:
        # Extracts floating point numbers
        matches = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return [float(m) for m in matches]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap value: 1.0 (safe) or <0.3 (trap detected).
        """
        p_lower = self._normalize(prompt)
        
        # 1. Presupposition Check
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # 2. Ambiguity Check (Pronoun/Scope)
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                return 0.25
                
        # 3. False Dichotomy
        if re.search(r"either.*or", p_lower) and "not" not in p_lower:
             # Simple heuristic: if "either/or" exists without explicit negation context
             if len(p_lower.split()) < 50: # Avoid long context false positives
                return 0.25

        # 4. Unanswerability (Subjectivity without criteria)
        if any(k in p_lower for k in ["best", "worst", "favorite"]) and "criteria" not in p_lower:
            if "list" not in p_lower and "sort" not in p_lower:
                return 0.25

        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Performs structural parsing and constructive computation.
        Returns (score_component, reasoning_string)
        """
        p_norm = self._normalize(prompt)
        c_norm = self._normalize(candidate)
        score = 0.0
        reasons = []

        # A. Numeric Evaluation (Constructive Computation)
        # If prompt asks for comparison, verify candidate matches logic
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2:
            # Detect comparison intent
            is_greater = any(k in p_norm for k in ["greater", "larger", "more", ">"])
            is_less = any(k in p_norm for k in ["less", "smaller", "fewer", "<"])
            
            if is_greater or is_less:
                val1, val2 = p_nums[0], p_nums[1]
                expected_true = (val1 > val2) if is_greater else (val1 < val2)
                
                # Check if candidate affirms or denies
                c_affirms = any(k in c_norm for k in ["yes", "true", "correct", "affirmative"])
                c_denies = any(k in c_norm for k in ["no", "false", "incorrect", "negative"])
                
                if expected_true and c_affirms:
                    score += 0.4
                    reasons.append("Numeric comparison correct (affirmed)")
                elif not expected_true and c_denies:
                    score += 0.4
                    reasons.append("Numeric comparison correct (denied)")
                elif expected_true and c_denies:
                    score -= 0.4
                    reasons.append("Numeric comparison failed (false negative)")
                elif not expected_true and c_affirms:
                    score -= 0.4
                    reasons.append("Numeric comparison failed (false positive)")

        # B. Negation Consistency
        p_neg_count = self._count_negations(prompt)
        c_neg_count = self._count_negations(candidate)
        
        # Heuristic: If prompt has odd negations, answer should likely reflect that logic
        # This is a simplified proxy for logical consistency
        if p_neg_count > 0:
            if (p_neg_count % 2 == 1) and (c_neg_count % 2 == 1):
                score += 0.2
                reasons.append("Negation parity maintained")
            elif (p_neg_count % 2 == 0) and (c_neg_count % 2 == 0):
                score += 0.2
                reasons.append("Double negation resolved")
        
        # C. Constraint Propagation (Simple keyword matching for logic traps)
        if "not" in p_norm and ("yes" in c_norm or "true" in c_norm):
            # Potential trap: Prompt says "Which is NOT...", candidate says "Yes"
            # Without full semantic parse, we penalize blind affirmation in negative contexts
            if any(q in p_norm for q in ["which is not", "is not true", "false"]):
                if c_affirms := any(k in c_norm for k in ["yes", "true"]):
                    score -= 0.3
                    reasons.append("Penalized blind affirmation in negative context")

        reason_str = "; ".join(reasons) if reasons else "Structural baseline"
        return score, reason_str

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        s1 = (prompt + candidate).encode('utf-8')
        p_enc = prompt.encode('utf-8')
        c_enc = candidate.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1))
        len_p = len(zlib.compress(p_enc))
        len_c = len(zlib.compress(c_enc))
        
        max_len = max(len_p, len_c)
        if max_len == 0:
            return 0.0
        
        ncd = (len_s1 - min(len_p, len_c)) / max_len
        # Invert: lower NCD (more similar) -> higher score, but capped at 0.15 weight
        return max(0.0, 1.0 - ncd) * 0.15

    def _soc_adapt(self, scores: List[float]) -> float:
        """
        Simulates SOC adaptation. 
        Calculates the 'avalanche size' (variance in scores) to adjust sensitivity.
        Returns a scaling factor based on the system being near criticality.
        """
        if len(scores) < 2:
            return 1.0
        
        # Avalanche size approximation: difference between max and mean
        avg = sum(scores) / len(scores)
        if avg == 0:
            return 1.0
            
        variance = sum((s - avg)**2 for s in scores) / len(scores)
        
        # If variance is too low (stagnation) or too high (chaos), adjust sensitivity
        # Target: Power law distribution (intermediate variance)
        if variance < 0.01:
            self._sensitivity = min(1.0, self._sensitivity + 0.1) # Increase exploration
        elif variance > 0.5:
            self._sensitivity = max(0.1, self._sensitivity - 0.1) # Reduce noise
        else:
            # Critical state maintained
            pass
            
        return self._sensitivity

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        raw_scores = []
        
        # 2. Evaluate each candidate
        for cand in candidates:
            # Structural Score (Primary Driver)
            struct_score, reason = self._structural_score(prompt, cand)
            
            # NCD Score (Tiebreaker)
            ncd_score = self._ncd_score(prompt, cand)
            
            # Combine: Structural (85%) + NCD (15%)
            # Ensure structural dominates
            total_score = (struct_score * 0.85) + (ncd_score * 0.15)
            
            # Apply Epistemic Cap
            if meta_cap < 0.3:
                # If the question is a trap, confidence is capped, but we still rank based on 
                # which candidate acknowledges the trap best (heuristic: shorter, more cautious?)
                # For this implementation, we strictly cap the score.
                total_score = min(total_score, meta_cap)
                if reason == "Structural baseline":
                    reason = "Epistemic trap detected in prompt; score capped."
            
            raw_scores.append(total_score)
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reason
            })

        # 3. SOC Adaptation Step (Updates internal state based on score distribution)
        # This doesn't change the current output order significantly but tunes the 
        # internal sensitivity for future 'batches' if this were a continuous loop.
        self._soc_adapt(raw_scores)

        # 4. Sort and Return
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty caps.
        """
        # 1. Check Meta-Confidence (The Cap)
        cap = self._meta_confidence(prompt)
        
        # 2. Calculate Base Confidence from Structural Match
        score, _ = self._structural_score(prompt, answer)
        ncd = self._ncd_score(prompt, answer)
        base_conf = (score * 0.85) + (ncd * 0.15)
        
        # Normalize base_conf to 0-1 range roughly
        # Structural score can be negative, so we map [-0.5, 0.5] -> [0, 1] approx
        normalized_conf = max(0.0, min(1.0, (base_conf + 0.5) / 1.0))
        
        # 3. Apply Cap
        final_conf = min(normalized_conf, cap)
        
        # 4. Never return > 0.9 without definitive computation
        # (Our structural score is the 'computation', so if it triggered, it's allowed higher)
        if "Numeric comparison" not in self._structural_score(prompt, answer)[1]:
            final_conf = min(final_conf, 0.85)
            
        return round(final_conf, 4)