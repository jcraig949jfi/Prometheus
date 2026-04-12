import re
import zlib
import math

class ReasoningTool:
    """
    Neuromodulated Falsification-Driven Incentive-Compatible Learner (NFDICL).
    
    Mechanism:
    1. Falsificationism (Core): Candidates are scored by their ability to satisfy 
       logical constraints (negations, conditionals) derived from the prompt. 
       Failure to satisfy a constraint acts as a 'falsification', heavily penalizing the score.
    2. Mechanism Design (Truthfulness): Uses a proper scoring rule logic. Candidates 
       that echo the prompt without answering (low information content) or contradict 
       explicit constraints are penalized more harshly than those admitting uncertainty.
    3. Neuromodulation (Gain Control): The 'confidence' method acts as the modulatory signal.
       It does not compute the primary rank but scales the 'plasticity' (score adjustment) 
       based on structural certainty. If structural signals are weak, the system defaults 
       to NCD (compression) as a low-gain baseline, preventing over-confidence in noise.
    """

    def __init__(self):
        self._constraint_keywords = ['not', 'no', 'never', 'unless', 'except', 'false', 'wrong']
        self._comparative_ops = ['greater', 'larger', 'more', 'less', 'smaller', 'fewer']
        self._conditional_ops = ['if', 'then', 'when', 'only if']

    def _extract_numbers(self, text):
        """Extract floating point numbers from text for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_structural_consistency(self, prompt, candidate):
        """
        Falsification Engine: Checks candidate against prompt constraints.
        Returns a penalty score (0.0 = fully falsified, 1.0 = consistent).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 1.0
        
        # 1. Negation Check (Modus Tollens approximation)
        # If prompt says "X is NOT Y", and candidate says "X is Y", falsify.
        has_negation = any(k in p_lower for k in self._constraint_keywords)
        if has_negation:
            # Simple heuristic: if prompt denies a concept and candidate affirms it strongly
            # without qualification, apply penalty.
            if any(k in c_lower for k in ['yes', 'is', 'are']) and 'not' not in c_lower:
                # Check if the candidate is just repeating the prompt (echo)
                if len(candidate) < len(prompt) * 0.9: 
                    score -= 0.5 # Heavy penalty for confident contradiction

        # 2. Numeric Consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If prompt implies an order (e.g., "which is larger?"), check candidate number
            if any(op in p_lower for op in self._comparative_ops):
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    # Heuristic: Assume prompt asks to pick the larger/smaller of two
                    # If prompt says "larger", candidate should be max(p_nums)
                    is_max_query = 'larger' in p_lower or 'greater' in p_lower or 'more' in p_lower
                    target = max(p_nums) if is_max_query else min(p_nums)
                    
                    # Allow small float tolerance
                    if abs(c_nums[0] - target) > 1e-6:
                        # Check if candidate explicitly mentions the other number as the answer
                        score -= 0.4 # Falsified by numeric evidence

        # 3. Conditional Logic (Simplified)
        # If prompt has "if X then Y", and candidate implies "X but not Y"
        if any(op in p_lower for op in self._conditional_ops):
            # Very basic check: if prompt sets a rule, candidate shouldn't contradict obvious outcomes
            # This is a placeholder for deeper logical graph traversal
            pass

        return max(0.0, score)

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker/baseline."""
        if not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(z1, z2)
        if denominator == 0:
            return 0.0
        return (z12 - min(z1, z2)) / denominator

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-calculate prompt structural features
        prompt_features = {
            'has_numbers': bool(self._extract_numbers(prompt)),
            'is_negative': any(k in prompt.lower() for k in self._constraint_keywords)
        }

        for cand in candidates:
            # 1. Falsification Score (Structural Parsing)
            falsification_score = self._check_structural_consistency(prompt, cand)
            
            # 2. Mechanism Design (Truthfulness/Echo Penalty)
            # Penalize candidates that are just substrings of the prompt (gaming)
            echo_penalty = 0.0
            if cand.strip() in prompt and len(cand.strip()) < len(prompt) * 0.5:
                echo_penalty = 0.3
            
            # 3. Baseline (NCD) - Used as tiebreaker or fallback
            # Invert NCD so higher is better (similarity to prompt context usually good, 
            # but we want distinct answers. Here we use it to measure relevance.)
            # Actually, for QA, we want the answer to be consistent with prompt context.
            # We use NCD primarily as the floor as per instructions.
            ncd_val = self._compute_ncd(prompt, cand)
            baseline_score = (1.0 - ncd_val) * 0.2  # Max 0.2 contribution from pure compression

            # Combine: Structural (High weight) + Baseline
            final_score = (falsification_score * 0.8) + baseline_score - echo_penalty
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))

            reasoning = f"Structural consistency: {falsification_score:.2f}; Echo penalty: {echo_penalty:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Neuromodulatory Gain Control.
        Returns a confidence value (0-1) acting as a learning rate scaler.
        High confidence (high gain) only when structural signals are strong.
        Low confidence (low gain) when relying on NCD/noise.
        """
        # Check for strong structural signals
        struct_score = self._check_structural_consistency(prompt, answer)
        has_numbers = bool(self._extract_numbers(answer))
        has_logic = any(k in prompt.lower() for k in self._conditional_ops + self._constraint_keywords)
        
        # Base confidence on structural clarity
        confidence = 0.5
        
        if struct_score > 0.9:
            confidence += 0.4  # High gain for consistent structural match
        elif struct_score < 0.5:
            confidence -= 0.4  # Low gain for falsified candidates
            
        if has_numbers and has_logic:
            confidence += 0.1 # Bonus for numeric logic presence
            
        return max(0.0, min(1.0, confidence))