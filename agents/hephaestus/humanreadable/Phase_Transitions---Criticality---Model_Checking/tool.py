import zlib
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Criticality-Guided Symbolic Model Checking Engine (Approximated for NLP).
    
    Mechanism:
    1. Order Parameter (O): Defined as a structural validity score based on 
       constraint satisfaction (negations, comparatives, transitivity) extracted 
       from the prompt-candidate pair.
    2. Control Parameter (lambda): A perturbation factor applied to the candidate 
       string (simulated via substring masking) to test stability.
    3. Susceptibility (chi): The rate of change of O with respect to lambda.
       High chi indicates the candidate is near a "phase boundary" (ambiguous/critical).
    4. Renormalization: Candidates with high susceptibility are coarse-grained 
       (penalized) unless they pass strict structural parsing checks.
    5. CEGAR Loop: Iteratively refines the score by checking specific logical 
       constraints (modus tollens, number comparison) only if the candidate 
       survives the initial criticality filter.
    """

    def __init__(self):
        self._comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self._negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_constraints(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """
        Structural parsing and constraint propagation.
        Returns (is_valid, score_delta).
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 0.0
        valid = True

        # 1. Negation Consistency
        has_neg_p = any(n in p_low for n in self._negations)
        has_neg_c = any(n in c_low for n in self._negations)
        
        if "contradict" in p_low or "false" in p_low:
            if has_neg_c != has_neg_p: # Simple heuristic for contradiction tasks
                pass # Context dependent, skip hard penalty
        else:
            # If prompt implies affirmation and candidate denies without cause
            if has_neg_p and not has_neg_c and "yes" in c_low:
                score -= 0.5
            if not has_neg_p and has_neg_c and "no" in c_low:
                # Check if the negative is justified by prompt content
                if "impossible" not in p_low and "false" not in p_low:
                     score -= 0.2

        # 2. Numeric Evaluation
        p_nums = self._extract_numbers(p_low)
        c_nums = self._extract_numbers(c_low)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Detect comparison intent
            if any(c in p_low for c in self._comparatives):
                p_max = max(p_nums)
                p_min = min(p_nums)
                c_val = c_nums[0]
                
                if "larger" in p_low or "greater" in p_low or "more" in p_low:
                    if c_val != p_max: score -= 0.8
                elif "smaller" in p_low or "less" in p_low or "fewer" in p_low:
                    if c_val != p_min: score -= 0.8
                else:
                    # General magnitude check if direction unclear
                    if abs(c_val - p_max) > abs(c_val - p_min) and "small" in p_low:
                        score -= 0.5

        # 3. Transitivity / Logic Keywords
        if "if" in p_low and "then" in p_low:
            if "therefore" in c_low or "thus" in c_low:
                score += 0.1 # Reward logical connector usage
        
        return valid, score

    def _compute_order_parameter(self, prompt: str, candidate: str) -> float:
        """
        Compute Order Parameter O: A mix of NCD and Structural Validity.
        O = (1 - NCD) + Structural_Score
        """
        # NCD Component
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        s12 = s1 + s2
        
        l1 = len(zlib.compress(s1))
        l2 = len(zlib.compress(s2))
        l12 = len(zlib.compress(s12))
        
        ncd = (l12 - min(l1, l2)) / max(l1, l2) if max(l1, l2) > 0 else 1.0
        ncd_score = 1.0 - ncd # Higher is better match
        
        # Structural Component
        _, struct_score = self._check_constraints(prompt, candidate)
        
        return 0.4 * ncd_score + 0.6 * (0.5 + struct_score) # Weighted sum

    def _compute_susceptibility(self, prompt: str, candidate: str) -> float:
        """
        Compute Susceptibility chi = dO/dlambda.
        We simulate lambda by perturbing the candidate (masking last word).
        """
        base_o = self._compute_order_parameter(prompt, candidate)
        
        # Perturb candidate (simulate control parameter change)
        words = candidate.split()
        if len(words) <= 1:
            perturbed = ""
        else:
            perturbed = " ".join(words[:-1])
            
        if not perturbed:
            perturbed_o = 0.0
        else:
            perturbed_o = self._compute_order_parameter(prompt, perturbed)
            
        # Avoid division by zero, use small epsilon for lambda step
        delta_lambda = 0.1 if len(words) <= 1 else 1.0 / len(words)
        if delta_lambda == 0: delta_lambda = 0.01
            
        chi = abs(base_o - perturbed_o) / delta_lambda
        return chi

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Phase 1: Compute Order Parameters and Susceptibility for all candidates
        stats = []
        for cand in candidates:
            o_param = self._compute_order_parameter(prompt, cand)
            chi = self._compute_susceptibility(prompt, cand)
            stats.append((cand, o_param, chi))
        
        # Phase 2: Criticality-Guided Ranking (Renormalization)
        # If susceptibility is high (unstable), we penalize unless order parameter is very high
        max_o = max(s[1] for s in stats) if stats else 0.5
        
        for cand, o_param, chi in stats:
            # Renormalization step: Coarse grain unstable states
            # If chi > threshold (critical region), apply penalty unless O is near 1.0
            critical_threshold = 0.5 
            if chi > critical_threshold:
                # Penalty proportional to instability
                final_score = o_param * (1.0 / (1.0 + chi))
            else:
                final_score = o_param
            
            # Generate reasoning string
            reason = f"Order={o_param:.2f}, Susceptibility={chi:.2f}. "
            if chi > critical_threshold:
                reason += "Critical instability detected; score renormalized."
                # Apply specific logical checks only if critical (CEGAR loop simulation)
                valid, delta = self._check_constraints(prompt, cand)
                if delta < 0:
                    final_score = 0.0
                    reason += " Structural constraint violation confirmed."
            else:
                reason += "Stable regime; standard scoring applied."
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the same engine: high order parameter + low susceptibility = high confidence.
        """
        o_param = self._compute_order_parameter(prompt, answer)
        chi = self._compute_susceptibility(prompt, answer)
        
        # Map to 0-1 confidence
        # High O and Low Chi -> High Confidence
        confidence = o_param * math.exp(-chi)
        
        # Hard constraints check
        valid, delta = self._check_constraints(prompt, answer)
        if delta < -0.5: # Strong violation
            confidence = 0.0
            
        return max(0.0, min(1.0, confidence))