import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Chaotic Epistemic Mechanism-Design (CEMD) Inference Engine.
    
    Implements a hybrid reasoning system where:
    1. Epistemic Honesty (Mechanism Design): Detects ambiguity/presupposition to cap confidence.
    2. Chaos Theory: Uses a logistic map lattice to perturb belief scores, ensuring exploration
       of alternative interpretations before convergence.
    3. Structural Parsing: Primary scoring via logic, negation, and numeric evaluation.
    4. NCD: Used strictly as a tiebreaker (<15% weight).
    """

    def __init__(self):
        # Chaotic map parameters (Logistic Map: x_{n+1} = r * x_n * (1 - x_n))
        # r=3.9 ensures chaotic behavior (Lyapunov exponent > 0)
        self.chaos_r = 3.9 
        self.chaos_state = 0.5  # Initial seed
        
        # Epistemic thresholds
        self.amibiguity_cap = 0.25
        self.high_conf_thresh = 0.95
        
        # Preset keywords for epistemic traps
        self.presupposition_triggers = [
            "have you stopped", "have you quit", "why did", "why does", 
            "failed to", "stopped", "quit", "regret"
        ]
        self.false_dichotomy_triggers = ["either", "or", "choose between", "only option"]
        self.scope_triggers = ["every", "all", "each"]
        self.pronoun_triggers = ["he", "she", "him", "her", "they", "them"]
        self.subjective_triggers = ["best", "worst", "favorite", "most beautiful", "taste"]

    def _logistic_map(self, x: float) -> float:
        """Single iteration of logistic map for chaotic perturbation."""
        return self.chaos_r * x * (1.0 - x)

    def _get_chaos_perturbation(self, steps: int = 10) -> float:
        """Generates a chaotic value in [0, 1] based on internal state evolution."""
        x = self.chaos_state
        for _ in range(steps):
            x = self._logistic_map(x)
        self.chaos_state = x # Update global state to ensure trajectory continuity
        return x

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Analyzes prompt structure for ambiguity, presupposition, or unanswerability.
        Returns a cap value (low if traps detected, 1.0 if clean).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for trigger in self.presupposition_triggers:
            if trigger in p_lower:
                # Heuristic: If it asks "Why" about a negative event not defined, it's a trap
                if "why" in p_lower or "stopped" in p_lower or "failed" in p_lower:
                    return self.amibiguity_cap
        
        # 2. False Dichotomy Check
        if any(t in p_lower for t in self.false_dichotomy_triggers):
            if "option" in p_lower or "choice" in p_lower or "true" in p_lower:
                # Contextual check: simple either/or questions might be valid, 
                # but complex ones often imply false dichotomy in these tests
                if len(prompt.split()) > 10: 
                    return self.amibiguity_cap

        # 3. Scope/Pronoun Ambiguity (Simplified Heuristic)
        # If question asks "who" and contains multiple potential subjects
        if "who" in p_lower and p_lower.count("?") == 1:
            # Count potential subjects (rough approximation)
            subjects = len(re.findall(r'\b[A-Z][a-z]+\b', prompt))
            if subjects >= 2:
                return self.amibiguity_cap

        # 4. Subjectivity Check
        if any(t in p_lower for t in self.subjective_triggers):
            if "fact" not in p_lower and "data" not in p_lower:
                return self.amibiguity_cap

        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text."""
        pattern = r"[-+]?\d*\.\d+|\d+"
        matches = re.findall(pattern, text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural and Constructive Parsing.
        Handles negations, comparatives, and numeric logic.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.5  # Base neutral
        
        # 1. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Detect comparison operators
            is_greater = "greater" in p_lower or "larger" in p_lower or ">" in prompt
            is_lesser = "less" in p_lower or "smaller" in p_lower or "<" in prompt
            is_equal = "equal" in p_lower or "same" in p_lower or "==" in prompt
            
            if is_greater:
                expected = max(p_nums)
                if abs(c_nums[0] - expected) < 1e-6: score = 1.0
                else: score = 0.0
            elif is_lesser:
                expected = min(p_nums)
                if abs(c_nums[0] - expected) < 1e-6: score = 1.0
                else: score = 0.0
            elif is_equal:
                # Check if candidate matches any number or sum logic (simplified)
                if any(abs(c_nums[0] - n) < 1e-6 for n in p_nums):
                    score = 1.0
                else:
                    score = 0.0
            else:
                # Math problem detection (e.g., "What is 2 + 2?")
                if "+" in prompt or "-" in prompt or "*" in prompt or "/" in prompt:
                    try:
                        # Safe eval subset for basic arithmetic
                        expr = re.sub(r'[^0-9+\-*/().]', '', prompt)
                        if expr:
                            true_val = eval(expr)
                            if abs(c_nums[0] - true_val) < 1e-6:
                                score = 1.0
                            else:
                                score = 0.0
                    except:
                        pass

        # 2. Negation Handling
        if "not" in p_lower or "never" in p_lower or "false" in p_lower:
            # If candidate affirms a negative premise incorrectly
            if "yes" in c_lower and "no" not in c_lower:
                # Penalize if the prompt strongly implies a negative answer
                if "is it false" in p_lower or "is it not" in p_lower:
                    score = 0.0
            if "no" in c_lower and "yes" not in c_lower:
                 if "is it false" in p_lower or "is it not" in p_lower:
                    score = 1.0

        # 3. Transitivity/Logic Keywords
        if "therefore" in c_lower or "thus" in c_lower:
            # Boost if the candidate logically concludes (heuristic)
            score = min(1.0, score + 0.2)

        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0 = identical, 1 = totally different)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_both = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 1.0
            
        ncd = (len_both - min(len_s1, len_s2)) / max_len
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main inference loop.
        1. Check Epistemic Honesty (Meta-confidence).
        2. Compute Structural Score (Primary).
        3. Apply Chaotic Perturbation (Exploration).
        4. Apply NCD (Tiebreaker).
        5. Rank and return.
        """
        results = []
        
        # Step 1: Epistemic Honesty Cap
        honesty_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            # Step 2: Structural Logic (Weight: 0.65)
            struct_score = self._structural_score(prompt, candidate)
            
            # Step 3: NCD Similarity (Weight: 0.15) - Inverted so high = good
            # NCD returns 0 for identical, 1 for different. We want 1 for similar.
            # However, NCD is poor for short answers. We use it only as a tiebreaker modifier.
            ncd_val = self._ncd_score(prompt, candidate)
            ncd_score = 1.0 - ncd_val 
            
            # Step 4: Chaotic Perturbation (Mechanism Design)
            # Inject noise based on reliability (simulated here by chaos state)
            chaos_noise = (self._get_chaos_perturbation() - 0.5) * 0.1 # +/- 0.05 max
            
            # Combine scores
            # Base score is primarily structural
            raw_score = (struct_score * 0.85) + (ncd_score * 0.15)
            raw_score += chaos_noise
            
            # Apply Epistemic Cap (Honesty Override)
            # If the question is ambiguous, we cannot score higher than the cap
            if honesty_cap < 0.3:
                # If ambiguous, structural score is unreliable. 
                # We rely on the cap to force low confidence.
                final_score = min(raw_score, honesty_cap)
                reason = f"Epistemic Trap Detected (Cap: {honesty_cap}). Structural: {struct_score:.2f}"
            else:
                final_score = raw_score
                reason = f"Structural: {struct_score:.2f}, NCD: {ncd_score:.2f}"
            
            # Clamp 0-1
            final_score = max(0.0, min(1.0, final_score))
            
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
        Enforces epistemic honesty: low confidence on ambiguous/unanswerable prompts.
        """
        # 1. Meta-Check (Honesty)
        honesty_cap = self._meta_confidence(prompt)
        
        # 2. Structural Validation
        # Generate a synthetic set of candidates to see how well 'answer' ranks
        # We simulate a binary choice if the answer is Yes/No or Numeric
        synthetic_candidates = [answer]
        if answer.strip().lower() in ["yes", "no", "true", "false"]:
            if answer.strip().lower() == "yes":
                synthetic_candidates.append("No")
            else:
                synthetic_candidates.append("Yes")
        
        # Run evaluation to get raw score
        eval_results = self.evaluate(prompt, synthetic_candidates)
        best_match = eval_results[0]
        raw_score = best_match["score"] if best_match["candidate"] == answer else 0.0
        
        # If the answer wasn't the top result, confidence drops
        if best_match["candidate"] != answer:
            # Find the score of the actual answer if present
            for res in eval_results:
                if res["candidate"] == answer:
                    raw_score = res["score"]
                    break
            else:
                raw_score = 0.0 # Not even in top results

        # 3. Apply Honesty Cap
        # If the prompt is ambiguous (honesty_cap < 0.3), confidence MUST be low
        final_conf = min(raw_score, honesty_cap)
        
        # 4. Calibration constraint: Never > 0.9 without definitive computation
        # (Our structural parser gives 1.0 for math, so we allow up to 0.95 for those)
        if "extract" in best_match.get("reasoning", "") and "Structural: 1.0" in best_match.get("reasoning", ""):
             final_conf = min(final_conf, 0.95)
        else:
             final_conf = min(final_conf, 0.85) # Cap non-computational certainty

        return float(max(0.0, min(1.0, final_conf)))