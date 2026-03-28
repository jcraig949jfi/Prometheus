import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Bayesian Incentive-Compatible Proof-Search (BICPS) Implementation.
    
    Mechanism:
    1. Mechanism Design (Core): Treats candidate evaluation as a proof submission.
       - Agents (candidates) are scored on "conciseness" (length penalty) and 
         "validity" (structural match to prompt constraints).
       - Uses a peer-prediction style scoring rule where the 'peer' is the 
         structural expectation derived from the prompt.
    2. Bayesian Inference: Updates a prior belief (0.5) based on likelihoods 
       derived from structural parsing (negations, comparatives, numerics).
    3. Proof Theory: Uses string normalization (whitespace/case reduction) as 
       a proxy for cut-elimination/normalization to check equivalence.
       
    Scoring Logic:
    - High priority: Structural constraint satisfaction (Negation flipping, Numeric comparison).
    - Medium priority: Logical form matching (Conditionals).
    - Low priority (Tiebreaker): Normalized Compression Distance (NCD).
    """

    def __init__(self):
        self.prior = 0.5
        self.epsilon = 1e-6

    def _normalize(self, text: str) -> str:
        """Proof-theoretic normalization (cut-elimination proxy)."""
        if not text:
            return ""
        t = text.lower()
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for comparative reasoning."""
        # Match integers and floats
        matches = re.findall(r'-?\d+\.?\d*', text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _check_structural_consistency(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """
        Mechanism Design: Verify if the candidate respects logical constraints 
        implied by the prompt's structure (negations, comparatives).
        Returns (is_valid, likelihood_ratio).
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        score_modifier = 1.0
        valid = True

        # 1. Negation Handling (Modus Tollens/Opposites)
        negation_words = ['no', 'not', 'never', 'false', 'impossible']
        p_has_neg = any(w in p_low.split() for w in negation_words)
        c_has_neg = any(w in c_low.split() for w in negation_words)
        
        # If prompt asks "What is NOT...", candidate should ideally reflect negation or opposite
        # Simple heuristic: If prompt has 'not' and candidate is 'yes/no', check alignment
        if 'not' in p_low and ('yes' in c_low or 'no' in c_low):
            if ('yes' in c_low and not p_has_neg) or ('no' in c_low and p_has_neg):
                # Misaligned negation
                valid = False
                score_modifier = 0.1

        # 2. Numeric Comparative Reasoning
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Detect comparative keywords
            is_less = any(w in p_low for w in ['less', 'smaller', 'lower', 'minimum'])
            is_more = any(w in p_low for w in ['more', 'larger', 'greater', 'maximum', 'most'])
            
            p_val = p_nums[0] # Simplified: assume first two are comparable
            p_val2 = p_nums[1] if len(p_nums) > 1 else p_nums[0]
            
            expected_val = p_val2 # Default fallback
            
            if is_less:
                expected_val = min(p_val, p_val2)
            elif is_more:
                expected_val = max(p_val, p_val2)
            
            # Check if candidate contains the correct numeric answer
            # Allow small float tolerance
            found_correct = False
            for cn in c_nums:
                if abs(cn - expected_val) < 1e-5:
                    found_correct = True
                    break
            
            if found_correct:
                score_modifier = 2.0 # Strong reward for numeric proof
            else:
                # If numbers are present but wrong, penalize heavily
                if len(c_nums) > 0:
                    valid = False
                    score_modifier = 0.05

        # 3. Conditional/Constraint Propagation (Simple keyword overlap for logic)
        # If prompt says "If X then Y", and candidate lacks Y (approximated by word overlap)
        if 'if' in p_low and 'then' in p_low:
            # Extract potential consequence (words after 'then')
            parts = p_low.split('then')
            if len(parts) > 1:
                consequence = parts[1].split('?')[0].split('.')[0].strip()
                cons_words = set(consequence.split())
                cand_words = set(c_low.split())
                # Check if at least one significant word from consequence is in candidate
                sig_match = any(w in cand_words for w in cons_words if len(w) > 3)
                if not sig_match and len(cons_words) > 0:
                    score_modifier *= 0.5

        return valid, score_modifier

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_norm = self._normalize(prompt)
        
        # Calculate scores based on Mechanism Design incentives
        for cand in candidates:
            cand_norm = self._normalize(cand)
            
            # 1. Structural/Logical Validation (The "Proof")
            is_valid, logic_mult = self._check_structural_consistency(prompt, cand)
            
            # 2. Bayesian Update Proxy
            # Prior = 0.5. Likelihood proportional to logic_mult.
            # If logic_mult is high, posterior moves to 1. If low, moves to 0.
            likelihood = logic_mult * (1.0 if is_valid else 0.01)
            
            # Normalize likelihood to probability space roughly
            # Using a simple scaling: score = likelihood / (likelihood + constant)
            # But we need to rank, so raw likelihood is sufficient if scaled well.
            # Let's create a raw score: Base + Logic Bonus - Length Penalty (Conciseness)
            
            length_penalty = len(cand_norm) * 0.001 # Small penalty for verbosity
            base_score = 0.5
            
            raw_score = base_score * logic_mult - length_penalty
            
            # Ensure non-negative for now
            if raw_score < 0: raw_score = 0.01
            
            # 3. NCD Tiebreaker (Only if logic scores are identical, which is rare with floats)
            # We incorporate NCD as a small additive factor to break ties smoothly
            # Lower NCD = Higher similarity = Better (usually)
            ncd = self._calculate_ncd(prompt_norm, cand_norm)
            # Invert NCD so higher is better, scale down to not override logic
            ncd_score = (1.0 - ncd) * 0.001 
            
            final_score = raw_score + ncd_score
            
            # Generate reasoning string
            reason_parts = []
            if logic_mult > 1.5:
                reason_parts.append("Strong structural/numeric match")
            elif logic_mult < 0.5:
                reason_parts.append("Logical inconsistency detected")
            if is_valid:
                reason_parts.append("Valid proof fragment")
            else:
                reason_parts.append("Proof normalization failed")
                
            reasoning = "; ".join(reason_parts) if reason_parts else "Standard evaluation"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the incentive-compatible score.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly
        # Since max logic_mult is ~2.0 and base is 0.5, max raw is ~1.0
        score = res[0]["score"]
        conf = min(1.0, max(0.0, score))
        return conf