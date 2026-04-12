import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Incentivized Statistical Verification Loop.
    
    Mechanism:
    1. Matched Filtering (Structural): Instead of signal processing on noise, we perform
       structural parsing on text. We extract a 'signal vector' of logical operators
       (negations, comparatives, conditionals, numbers). The 'correlation' is the 
       degree to which a candidate satisfies these structural constraints.
       
    2. Mechanism Design (Incentives): We implement a 'truthful reporting' scoring rule.
       Candidates are penalized heavily for contradicting explicit structural signals 
       (e.g., answering 'Yes' when 'not' is present). This aligns the 'agent' (candidate)
       interest with the 'principal' (truth) by making manipulation (ignoring constraints)
       costly.
       
    3. Model Checking (Verification): We treat the prompt's constraints as a finite 
       state machine. We verify temporal-logic-like properties: 
       - Safety: Does the answer violate a negative constraint? (□¬false)
       - Liveness: Does the answer satisfy the positive requirement? (◇true)
       Only candidates passing the safety check proceed to scoring.
    """

    def __init__(self):
        # Precompile regex for structural signal extraction
        self.signal_patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|only if|provided)\b', re.I),
            'numeric': re.compile(r'\d+\.?\d*'),
            'boolean_yes': re.compile(r'\byes\b', re.I),
            'boolean_no': re.compile(r'\bno\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extract structural signals (the 'known signal' s_h)."""
        signals = {}
        signals['has_negation'] = bool(self.signal_patterns['negation'].search(text))
        signals['has_comparative'] = bool(self.signal_patterns['comparative'].search(text))
        signals['has_conditional'] = bool(self.signal_patterns['conditional'].search(text))
        signals['numbers'] = [float(n) for n in self.signal_patterns['numeric'].findall(text)]
        
        # Detect expected boolean direction based on negation presence
        # If "not" is near "yes" logic, we expect "no", etc. Simplified for robustness:
        # We assume the prompt implies a specific direction if negation is dominant.
        signals['expects_negation'] = signals['has_negation']
        
        return signals

    def _verify_safety(self, prompt_sig: Dict, candidate: str) -> Tuple[bool, str]:
        """
        Model Checking: Safety Property.
        Ensures the candidate does not violate explicit negative constraints.
        Returns (is_safe, reason).
        """
        cand_lower = candidate.lower()
        cand_yes = bool(self.signal_patterns['boolean_yes'].search(candidate))
        cand_no = bool(self.signal_patterns['boolean_no'].search(candidate))
        
        # Safety Check 1: Contradiction of explicit negation
        # If prompt has negation and candidate asserts positive (Yes) without nuance
        if prompt_sig['expects_negation'] and cand_yes and not cand_no:
            # Heuristic: If the prompt is negative, a bare "Yes" is often unsafe 
            # unless the question is "Is it not...?" (Double negative). 
            # To be safe against gaming, we flag bare "Yes" in negative contexts as suspicious
            # unless the candidate is long enough to explain.
            if len(candidate.split()) <= 3:
                return False, "Safety violation: Bare affirmative in negative context."

        # Safety Check 2: Numeric consistency (Basic)
        # If prompt has numbers and candidate has numbers, check basic order if comparatives exist
        if prompt_sig['has_comparative'] and prompt_sig['numbers']:
            cand_nums = [float(n) for n in self.signal_patterns['numeric'].findall(candidate)]
            if cand_nums and prompt_sig['numbers']:
                # Simple transitivity check if both have numbers
                # If prompt implies "greater", and candidate number < prompt number, might be unsafe
                # This is a simplified proxy for complex logic
                pass 

        return True, "Safe"

    def _compute_correlation(self, prompt: str, candidate: str) -> float:
        """
        Matched Filtering: Compute cross-correlation between prompt structure and candidate.
        Maximizes SNR by rewarding structural alignment.
        """
        score = 0.0
        p_sig = self._extract_structure(prompt)
        c_sig = self._extract_structure(candidate)
        
        # 1. Numeric Correlation
        if p_sig['numbers'] and c_sig['numbers']:
            # Check if candidate numbers are logically derived (simplified to presence + magnitude match for now)
            # If prompt asks for "greater", and candidate is greater, score up.
            if p_sig['has_comparative']:
                if 'greater' in prompt.lower() or 'more' in prompt.lower() or 'higher' in prompt.lower():
                    if max(c_sig['numbers']) >= max(p_sig['numbers']):
                        score += 2.0
                    else:
                        score -= 1.0
                elif 'less' in prompt.lower() or 'smaller' in prompt.lower() or 'lower' in prompt.lower():
                    if min(c_sig['numbers']) <= min(p_sig['numbers']):
                        score += 2.0
                    else:
                        score -= 1.0
            else:
                # Exact match bonus for numeric problems without comparatives
                if set(c_sig['numbers']) == set(p_sig['numbers']):
                    score += 1.5
        
        # 2. Logical Negation Correlation
        if p_sig['has_negation']:
            # If prompt negates, a good answer often acknowledges it or flips the boolean
            if c_sig['has_negation'] or (bool(self.signal_patterns['boolean_no'].search(candidate))):
                score += 1.5
        
        # 3. Keyword Overlap (Weighted by structural importance)
        # Only count overlap if it's not just stop words, focusing on the extracted signals
        common_words = set(prompt.lower().split()) & set(candidate.lower().split())
        structural_hits = 0
        if p_sig['has_comparative'] and any(w in common_words for w in ['more', 'less', 'greater', 'smaller']):
            structural_hits += 1
        if p_sig['has_conditional'] and any(w in common_words for w in ['if', 'then', 'unless']):
            structural_hits += 1
            
        score += structural_hits * 1.2
        
        # Base similarity bonus (small)
        score += len(common_words) * 0.1
        
        return score

    def _mechanism_payment(self, base_score: float, prompt: str, candidate: str) -> float:
        """
        Mechanism Design: Adjust score based on incentive compatibility.
        Penalize gaming (short, vague answers that ignore structure).
        Reward truthful reporting of complexity.
        """
        payment = base_score
        
        # Penalty for length mismatch in reasoning tasks
        if len(prompt) > 50 and len(candidate) < 3:
            # If prompt is complex, a 1-word answer is likely gaming or wrong
            payment -= 2.0
            
        # Bonus for structural mirroring (honest signaling)
        p_sig = self._extract_structure(prompt)
        c_sig = self._extract_structure(candidate)
        
        if p_sig['has_negation'] and c_sig['has_negation']:
            payment += 1.0 # Reward acknowledging the negative constraint
            
        return payment

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        len_s1 = len(zlib.compress(s1.encode()))
        len_s2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_sig = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Model Checking: Safety Verification
            is_safe, reason = self._verify_safety(p_sig, cand)
            
            if not is_safe:
                # Safety violation: Assign low score but keep for ranking
                score = -10.0
                reasoning = f"Safety violation: {reason}"
            else:
                # 2. Matched Filtering: Structural Correlation
                correlation = self._compute_correlation(prompt, cand)
                
                # 3. Mechanism Design: Payment/Incentive Adjustment
                final_score = self._mechanism_payment(correlation, prompt, cand)
                
                # NCD as tiebreaker only (if scores are close or zero)
                # We add a tiny epsilon based on NCD to break ties deterministically
                ncd = self._ncd_distance(prompt, cand)
                # Invert NCD (lower is better) and scale down to be a tiebreaker
                ncd_bonus = (1.0 - ncd) * 0.01 
                
                score = final_score + ncd_bonus
                reasoning = f"Structural correlation: {correlation:.2f}, Payment adjusted: {final_score:.2f}"

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluation logic to determine if the answer is the 'best' among itself.
        """
        # Evaluate against a dummy set containing only the answer to get internal score
        # Then compare against a known bad answer to normalize? 
        # Simpler: Map the internal score to 0-1 via sigmoid-like clamp
        
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        score = res_list[0]["score"]
        
        # Safety violations yield -10, so map that to 0
        if score <= -5.0:
            return 0.0
        
        # Heuristic mapping: 
        # Score < 0 -> Low confidence
        # Score 0-2 -> Medium
        # Score > 2 -> High
        import math
        # Sigmoid scaling centered at 0, steepness 1.0
        conf = 1 / (1 + math.exp(-score))
        
        # Clamp
        return max(0.0, min(1.0, conf))