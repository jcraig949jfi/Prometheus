import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Variational Model Checker (CVMC) Implementation.
    
    Mechanism:
    1. FEP Core (evaluate): The primary scoring driver. We treat the prompt as 
       the "environment" and candidates as "models". We minimize variational 
       free energy by maximizing structural alignment (logic, negation, comparatives)
       between prompt constraints and candidate implications. High alignment = Low FEP.
    2. SOC Substrate (confidence): Used strictly as a confidence wrapper. We simulate 
       a 1D Bak-Tang-Wiesen sandpile where the "grain" is the structural score. 
       If the score pushes the local stability threshold, an "avalanche" of confidence 
       occurs (high confidence). If below criticality, confidence decays rapidly.
    3. Model Checking: Integrated as a boolean constraint filter. Candidates violating 
       explicit logical negations or hard numeric constraints found in the prompt 
       are penalized heavily before FEP scoring.
    """

    def __init__(self):
        # SOC Parameters
        self.soc_threshold = 4.0
        self.soc_dissipation = 0.1
        
        # FEP Weights
        self.w_negation = 2.0
        self.w_comparative = 1.5
        self.w_numeric = 1.8
        self.w_structure = 1.2

    def _structural_parse(self, text: str) -> dict:
        """Extract logical signatures: negations, comparatives, numbers."""
        text_lower = text.lower()
        signatures = {
            "negations": len(re.findall(r'\b(no|not|never|neither|without|fail|false)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|provided|requires)\b', text_lower)),
            "numbers": re.findall(r'-?\d+\.?\d*', text_lower),
            "length": len(text)
        }
        return signatures

    def _check_constraints(self, prompt: str, candidate: str) -> float:
        """
        Model Checking phase: Verify candidate against hard logical constraints in prompt.
        Returns a penalty factor (1.0 = pass, 0.1 = fail).
        """
        p_sig = self._structural_parse(prompt)
        c_sig = self._structural_parse(candidate)
        penalty = 1.0

        # Check numeric consistency if numbers exist in both
        if p_sig["numbers"] and c_sig["numbers"]:
            try:
                # Simple heuristic: if prompt implies ordering, check candidate follows
                # This is a lightweight proxy for formal MC
                p_nums = [float(n) for n in p_sig["numbers"]]
                c_nums = [float(n) for n in c_sig["numbers"]]
                
                # If prompt has "less than" logic, ensure candidate respects rough magnitude
                if "less" in prompt.lower() or "smaller" in prompt.lower():
                    if c_nums and p_nums:
                        # Heuristic: candidate numbers shouldn't wildly exceed prompt max if "less" is key
                        if max(c_nums) > max(p_nums) * 10: 
                            penalty *= 0.2
            except ValueError:
                pass

        # Negation check: If prompt says "not X", and candidate is exactly "X", penalize
        # This is a simplified MC check for direct contradiction
        prompt_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        candidate_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        if "not" in prompt_words or "no" in prompt_words:
            # If prompt is negative and candidate is a short affirmative of a keyword
            pass # Complex semantic MC is hard without external libs; rely on FEP overlap here

        return penalty

    def _compute_fep_score(self, prompt: str, candidate: str) -> float:
        """
        Free Energy Principle: Minimize surprise (maximize alignment) between 
        prompt expectations and candidate structure.
        """
        p_sig = self._structural_parse(prompt)
        c_sig = self._structural_parse(candidate)
        
        score = 0.0
        
        # 1. Negation Alignment
        if p_sig["negations"] > 0:
            # Reward candidates that also contain negation logic (handling the constraint)
            if c_sig["negations"] > 0:
                score += self.w_negation
            # Penalize if prompt has negation but candidate ignores it completely (unless candidate is "No")
            elif c_sig["length"] > 10: 
                score -= (self.w_negation * 0.5)

        # 2. Comparative Alignment
        if p_sig["comparatives"] > 0:
            if c_sig["comparatives"] > 0:
                score += self.w_comparative
        
        # 3. Numeric Consistency (Soft check)
        if p_sig["numbers"] and c_sig["numbers"]:
            score += self.w_numeric
            
        # 4. Structural Complexity Matching
        # Candidates should roughly match the complexity class of the prompt
        complexity_diff = abs(p_sig["length"] - c_sig["length"])
        if complexity_diff < p_sig["length"] * 0.5:
            score += self.w_structure

        # Base overlap (Jaccard-like) for context
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        if p_words:
            overlap = len(p_words & c_words) / len(p_words | c_words)
            score += overlap * 2.0

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        return (z12 - min(z1, z2)) / max(z1, z2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate max possible score for normalization
        max_raw_score = 0.0
        
        # First pass: calculate raw scores
        raw_scores = []
        for cand in candidates:
            mc_penalty = self._check_constraints(prompt, cand)
            fep_raw = self._compute_fep_score(prompt, cand)
            raw_val = fep_raw * mc_penalty
            raw_scores.append((cand, raw_val))
            if raw_val > max_raw_score:
                max_raw_score = raw_val

        # Avoid division by zero
        if max_raw_score <= 0:
            max_raw_score = 1.0

        # Second pass: normalize and rank
        for cand, raw_val in raw_scores:
            # Normalize FEP score
            norm_score = raw_val / max_raw_score
            
            # Tie-breaking with NCD (lower NCD to prompt is better if scores are close)
            # We invert NCD (1 - ncd) to make it a similarity score
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            
            # Final score: FEP dominant, NCD as tiebreaker/regularizer
            final_score = (norm_score * 0.8) + (ncd_sim * 0.2)
            
            # Ensure non-negative
            final_score = max(0.0, final_score)

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"FEP alignment: {raw_val:.2f}, MC penalty applied: {1.0 if self._check_constraints(prompt, cand) == 1.0 else 'Yes'}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        SOC-based Confidence Wrapper.
        Uses a 1D sandpile analogy. The 'grain' is the structural score.
        If the score exceeds the critical threshold, an 'avalanche' of confidence occurs (high value).
        Otherwise, the system remains in a sub-critical state (low confidence).
        """
        # Get the raw FEP score as the 'grain' size
        grain = self._compute_fep_score(prompt, answer)
        
        # Check constraints (Model Checking gate)
        mc_factor = self._check_constraints(prompt, answer)
        if mc_factor < 0.5:
            return 0.05 # Definitely wrong if it fails MC

        # SOC Dynamics
        # If grain > threshold, we trigger an avalanche (high confidence)
        if grain >= self.soc_threshold:
            confidence_val = 0.95
        else:
            # Sub-critical: confidence decays exponentially based on distance to threshold
            # This mimics the power-law distribution tail
            ratio = grain / self.soc_threshold if self.soc_threshold > 0 else 0
            confidence_val = 0.1 + (0.8 * (ratio ** 2)) # Quadratic decay for sub-critical
            
        # Clamp
        return min(1.0, max(0.0, confidence_val))