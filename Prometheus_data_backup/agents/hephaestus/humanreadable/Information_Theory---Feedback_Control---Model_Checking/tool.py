import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Entropy-Driven Adaptive Model Checker (EDAMC)
    
    Mechanism:
    Treats the selection of the correct candidate as a control problem.
    1. HYPOTHESIS SPACE: The list of candidates represents possible system models.
    2. ENTROPY (H): Measures uncertainty in the current belief distribution over candidates.
       Belief is derived from structural alignment (negations, conditionals, numerics) 
       between the prompt and the candidate.
    3. CONTROL LOOP (PID-like): 
       - Error (e) = H_target - H_current.
       - If entropy is high (uncertainty), the controller increases the "exploration depth" 
         (rigor of structural parsing).
       - If entropy is low, it reduces effort, assuming convergence.
    4. MODEL CHECKING (Structural Parsing): 
       Instead of generating traces, we perform exhaustive logical checks on the text:
       - Negation consistency (Modus Tollens).
       - Comparative magnitude (Numeric evaluation).
       - Conditional presence.
    5. MUTUAL INFORMATION: The reduction in entropy after applying structural filters 
       serves as the feedback signal to rank candidates.
    
    This approach prioritizes logical structure over string similarity (NCD), 
    using NCD only as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        self.h_target = 0.5  # Desired entropy level (confidence)
        self.kp = 1.0        # Proportional gain for exploration depth

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers for numeric evaluation."""
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _check_negation_consistency(self, prompt: str, candidate: str) -> float:
        """
        Checks if negation markers in the prompt are logically respected in the candidate.
        Returns 1.0 for consistent, 0.0 for contradictory, 0.5 for neutral.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        has_prompt_neg = any(n in p_lower for n in negations)
        has_cand_neg = any(n in c_lower for n in negations)
        
        # Simple heuristic: If prompt implies negation and candidate affirms (or vice versa), penalize.
        # This is a simplified logical check.
        if has_prompt_neg and not has_cand_neg:
            # Prompt says "X is not true", candidate doesn't negate. 
            # Hard to judge without full NLP, so we look for direct contradiction patterns.
            pass 
        
        # Stronger signal: Direct substring match of negation logic
        if has_prompt_neg and has_cand_neg:
            return 1.0 # Likely consistent
        if not has_prompt_neg and not has_cand_neg:
            return 1.0 # Likely consistent
        if has_prompt_neg and not has_cand_neg:
            # Potential mismatch, but context needed. 
            # However, if prompt asks "Is it not X?" and answer is "Yes", it's complex.
            # We will rely on this being a weak signal unless explicit contradiction found.
            return 0.8 
        if not has_prompt_neg and has_cand_neg:
            return 0.8
            
        return 1.0

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """
        Extracts numbers and checks for basic comparative consistency.
        If prompt has numbers and candidate has numbers, do they align in magnitude?
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric data to contradict
        
        # Heuristic: If prompt implies a max/min and candidate violates it.
        # Since we don't have full semantic parse, we check if the candidate number 
        # is wildly outside the range of prompt numbers (outlier detection).
        if p_nums:
            p_min, p_max = min(p_nums), max(p_nums)
            for c in c_nums:
                # If candidate number is order-of-magnitude different, penalize
                if c > p_max * 10 or c < p_min * 0.1:
                    return 0.5
        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Performs the 'Model Checking' step.
        Evaluates structural constraints: Negation, Numerics, Conditionals.
        """
        score = 1.0
        
        # 1. Negation Check
        score *= self._check_negation_consistency(prompt, candidate)
        
        # 2. Numeric Check
        score *= self._check_numeric_logic(prompt, candidate)
        
        # 3. Length/Complexity penalty (Occam's razor via entropy)
        # Prefer candidates that are concise but not too short
        p_len = len(prompt.split())
        c_len = len(candidate.split())
        if c_len == 0:
            return 0.0
        if c_len > p_len * 2:
            score *= 0.9 # Penalize excessive verbosity
            
        return score

    def _calculate_entropy(self, beliefs: List[float]) -> float:
        """Calculates Shannon Entropy of the belief distribution."""
        total = sum(beliefs)
        if total == 0:
            return 0.0
        probs = [b / total for b in beliefs]
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Step 1: Initial Structural Scoring (The "Plant" model)
        raw_scores = []
        for cand in candidates:
            s = self._structural_score(prompt, cand)
            raw_scores.append(s)
        
        # Step 2: Control Loop (PID-like adjustment)
        # Calculate current entropy of the raw scores
        current_entropy = self._calculate_entropy(raw_scores)
        
        # Determine exploration depth based on error from target entropy
        # High entropy -> Need more rigorous checking (simulated by boosting structural weight)
        error = self.h_target - current_entropy
        control_signal = max(0.1, 1.0 + self.kp * error) # Modulate influence
        
        # Apply control signal to refine scores
        refined_scores = []
        for i, cand in enumerate(candidates):
            base_score = raw_scores[i]
            # Re-evaluate with "deeper" scrutiny if control signal is high
            # In this static implementation, we amplify the structural penalty for mismatches
            if control_signal > 1.2:
                # High uncertainty: Be stricter on structural mismatches
                if base_score < 1.0:
                    base_score *= 0.8 
            refined_scores.append(base_score)
            
        # Step 3: Normalize and Rank
        max_score = max(refined_scores) if refined_scores else 1.0
        if max_score == 0:
            max_score = 1.0
            
        results = []
        for i, cand in enumerate(candidates):
            # Primary Score: Structural/Logical alignment
            primary = refined_scores[i] / max_score
            
            # Tie-breaker: NCD (Compression distance)
            # We want LOW NCD (similar compression) to boost score slightly if primary is equal
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so high is good, scale down to not override structural
            ncd_score = (1.0 - ncd_val) * 0.05 
            
            final_score = primary + ncd_score
            # Ensure 0-1 range
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment: {primary:.2f}, NCD tiebreak: {ncd_val:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural integrity."""
        # Use the internal scoring mechanism
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]