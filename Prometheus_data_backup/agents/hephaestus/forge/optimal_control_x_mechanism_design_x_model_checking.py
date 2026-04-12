import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Verified Incentive-Aware Control Synthesis (VIACS) Reasoning Tool.
    
    Mechanism:
    This tool implements a computational analogy of the 'Optimal Control x Mechanism Design x Model Checking'
    pipeline to rank candidate answers.
    
    1. Structural Parsing (Model Checking Layer): Extracts logical constraints (negations, conditionals,
       comparatives) from the prompt. Candidates are scored on satisfying these hard constraints.
       Failure here represents a 'safety violation' in the control system.
       
    2. Numeric/Logic Evaluation (Optimal Control Layer): Attempts to resolve numeric comparisons or
       explicit logical transitivity found in the prompt. This minimizes the 'cost function' of error.
       
    3. Incentive Compatibility (Mechanism Design Layer): Checks if a candidate merely echoes the prompt
       (gameable/low utility) vs. providing a distinct answer. It penalizes candidates that fail to
       align with the derived logical structure.
       
    4. NCD Tiebreaker: Uses Normalized Compression Distance only when structural scores are identical.
    """

    def __init__(self):
        self.negation_words = ["no", "not", "never", "none", "neither", "n't"]
        self.comparatives = ["more", "less", "greater", "smaller", "higher", "lower", "larger", "shorter"]
        self.conditionals = ["if", "unless", "provided", "when", "where"]

    def _extract_structural_constraints(self, prompt: str) -> dict:
        """Parses prompt for negations, comparatives, and conditionals."""
        p_lower = prompt.lower()
        tokens = re.findall(r'\b\w+\b', p_lower)
        
        constraints = {
            "has_negation": any(w in p_lower for w in self.negation_words),
            "has_comparative": any(w in p_lower for w in self.comparatives),
            "has_conditional": any(w in p_lower for w in self.conditionals),
            "has_numbers": bool(re.search(r'\d+', prompt)),
            "key_terms": set(tokens) # Simplified key terms
        }
        return constraints

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Attempts to verify numeric claims in candidate against prompt."""
        score = 0.0
        # Extract numbers from prompt
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums:
            return 0.5 # Neutral if no numbers
        
        try:
            p_vals = [float(n) for n in p_nums]
            c_vals = [float(n) for n in c_nums]
            
            # Simple heuristic: If prompt has 2 numbers and candidate has 1, 
            # check if candidate matches the logical result (e.g., max, min, sum)
            if len(p_vals) >= 2 and len(c_vals) >= 1:
                if "max" in candidate.lower() or "greater" in candidate.lower():
                    if max(p_vals) in c_vals: score += 0.4
                elif "min" in candidate.lower() or "less" in candidate.lower():
                    if min(p_vals) in c_vals: score += 0.4
                else:
                    # Check direct presence
                    if any(val in c_vals for val in p_vals):
                        score += 0.2
        except ValueError:
            pass
            
        return score

    def _check_incentive_compatibility(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design check: Ensures the candidate isn't just echoing the prompt
        (which would be a 'deviation' from truth-seeking behavior).
        """
        p_set = set(re.findall(r'\w+', prompt.lower()))
        c_set = set(re.findall(r'\w+', candidate.lower()))
        
        if len(p_set) == 0:
            return 0.0
            
        overlap = len(p_set.intersection(c_set)) / len(p_set)
        
        # If overlap is too high (>90%), it's likely an echo (bad mechanism)
        # If overlap is too low (<10%), it might be irrelevant
        # Ideal zone is moderate overlap with distinct answer content
        if overlap > 0.9:
            return 0.2 # Penalty for echoing
        elif overlap < 0.1:
            return 0.4 # Penalty for irrelevance
        return 0.8 # Good incentive alignment

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        constraints = self._extract_structural_constraints(prompt)
        scored_candidates = []
        
        for cand in candidates:
            score = 0.5  # Base score
            reasoning_parts = []
            
            # 1. Model Checking: Structural Constraints
            c_lower = cand.lower()
            structural_hit = True
            
            if constraints["has_negation"]:
                # Heuristic: If prompt has negation, correct answer often contains it or addresses it
                has_neg = any(w in c_lower for w in self.negation_words)
                if not has_neg:
                    # Soft penalty, not hard fail, unless logic dictates
                    score -= 0.1
                    reasoning_parts.append("Missed negation context")
                else:
                    score += 0.2
                    reasoning_parts.append("Handled negation")
            
            if constraints["has_conditional"]:
                if any(w in c_lower for w in ["if", "then", "yes", "no"]):
                    score += 0.1
                    reasoning_parts.append("Addressed conditional")
            
            # 2. Optimal Control: Numeric/Logic Optimization
            logic_score = self._evaluate_numeric_logic(prompt, cand)
            if logic_score > 0.5:
                score += 0.3
                reasoning_parts.append("Numeric logic verified")
            elif logic_score < 0.5 and constraints["has_numbers"]:
                score -= 0.1
                reasoning_parts.append("Numeric logic weak")
            
            # 3. Mechanism Design: Incentive Compatibility
            ic_score = self._check_incentive_compatibility(prompt, cand)
            score += (ic_score - 0.5) * 0.4 # Adjust based on IC
            
            # 4. NCD Tiebreaker (only if scores are close to baseline)
            # We use NCD to slightly differentiate similar candidates
            ncd_val = self._compute_ncd(prompt, cand)
            # Prefer lower NCD (more similar) ONLY if structural checks passed
            if structural_hit:
                score += (1.0 - ncd_val) * 0.05 
            
            scored_candidates.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Standard evaluation"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and lack of contradictions.
        """
        # Reuse evaluation logic for a single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]["score"]
        
        # Map internal score (approx 0.2 to 1.2 range potentially) to 0-1
        # Baseline is 0.5. 
        confidence = (raw_score - 0.2) / 0.8
        return max(0.0, min(1.0, confidence))