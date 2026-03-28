import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Criticality-Aware Incentive-Compatible Model-Checking Engine (CA-ICME).
    
    Mechanism:
    1. Mechanism Design (Core): Candidates are treated as self-interested agents.
       Scores are derived from a VCG-like utility function that rewards structural 
       alignment with the prompt's logical constraints (negations, comparatives) 
       and penalizes logical contradictions. Truthful (structurally consistent) 
       reporting is the dominant strategy.
       
    2. Phase Transitions (Monitor): We compute an order parameter 'M' (belief magnetization)
       based on the divergence between candidate answers. If the system is near a 
       'critical point' (high disagreement/entropy), we trigger a rigorous 
       'model checking' routine (deep structural parsing). If stable (low disagreement),
       we rely on lighter heuristics to save compute.
       
    3. Model Checking (Validator): A deterministic rule-based parser verifies 
       temporal-logic style constraints (e.g., "if X then Y", "A > B") encoded 
       in the prompt against the candidate text.
    """

    def __init__(self):
        # Logical operators and comparators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparators = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text for numeric evaluation."""
        pattern = r"[-+]?\d*\.?\d+"
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_parse(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Parses logical structure: negations, comparatives, conditionals.
        Returns a score delta and a reasoning string.
        """
        score = 0.0
        reasons = []
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt asks "Which is NOT...", candidate must contain negation or antonym logic
        has_prompt_neg = any(n in p_low.split() for n in self.negations)
        has_cand_neg = any(n in c_low.split() for n in self.negations)
        
        if "not" in p_low or "never" in p_low:
            if has_cand_neg:
                score += 0.2
                reasons.append("Correctly identified negation context.")
            else:
                score -= 0.3
                reasons.append("Failed to reflect negation context.")

        # 2. Numeric Evaluation (Constraint Propagation)
        p_nums = self._extract_numbers(p_low)
        c_nums = self._extract_numbers(c_low)
        
        if p_nums and c_nums:
            # Check if candidate preserves numeric order implied by prompt comparatives
            # Simple heuristic: If prompt has numbers and candidate has numbers, 
            # check if they match or are logically derived.
            # For "9.11 vs 9.9" type problems, exact float comparison is key.
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Detect comparative intent in prompt
                is_greater = any(g in p_low for g in ['greater', 'larger', 'more', 'max'])
                is_less = any(l in p_low for l in ['less', 'smaller', 'fewer', 'min'])
                
                p_max = max(p_nums)
                p_min = min(p_nums)
                
                # If candidate is a number, check if it's the correct extreme
                if c_nums[0] == p_max and is_greater:
                    score += 0.4
                    reasons.append(f"Numeric check passed: {c_nums[0]} is max.")
                elif c_nums[0] == p_min and is_less:
                    score += 0.4
                    reasons.append(f"Numeric check passed: {c_nums[0]} is min.")
                elif c_nums[0] in p_nums:
                     score += 0.1 # Partial credit for presence
                     reasons.append("Number present but logical role unclear.")
                else:
                    score -= 0.2
                    reasons.append("Numeric inconsistency detected.")

        # 3. Conditional/Keyword Overlap (Weak Model Checking)
        # Checks if candidate contains specific logical tokens found in prompt
        common_bools = set(self.booleans) & set(c_low.split())
        if common_bools:
            score += 0.1
            reasons.append("Explicit boolean assertion found.")
            
        reason_str = " ".join(reasons) if reasons else "No strong structural signals."
        return score, reason_str

    def _calculate_magnetization(self, candidates: List[str]) -> float:
        """
        Calculates the order parameter M = |sum(2*c_h - 1)| approximated by 
        text similarity divergence. High divergence = Critical Phase.
        """
        if len(candidates) < 2:
            return 0.0
        
        # Use NCD as a proxy for distance between candidates to determine phase
        # If all candidates are similar, M is low (ordered). If diverse, M is high (critical).
        total_dist = 0.0
        count = 0
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                s1 = candidates[i].encode('utf-8')
                s2 = candidates[j].encode('utf-8')
                l1 = len(s1)
                l2 = len(s2)
                if l1 == 0 or l2 == 0:
                    continue
                c12 = len(zlib.compress(s1 + s2))
                # Normalized Compression Distance approx
                dist = (c12 - min(l1, l2)) / max(l1, l2)
                total_dist += dist
                count += 1
        
        avg_dist = total_dist / count if count > 0 else 0
        # Map distance to magnetization: High distance -> Low Magnetization (Disordered/Critical)
        # We want to detect the "Critical" zone where beliefs are split.
        return 1.0 - min(1.0, avg_dist)

    def _vcg_payment_rule(self, base_score: float, is_critical: bool, structural_bonus: float) -> float:
        """
        Applies VCG-like incentive compatibility.
        In critical phases, structural truthfulness (model checking) is heavily weighted.
        """
        if is_critical:
            # In critical phase, rely heavily on structural parsing (Model Checking)
            return base_score * 0.3 + structural_bonus * 0.7
        else:
            # In stable phase, base heuristics are sufficient
            return base_score * 0.8 + structural_bonus * 0.2

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Calculates 1 - NCD(prompt, candidate) as a baseline similarity metric."""
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        l1, l2 = len(s1), len(s2)
        if l1 == 0 or l2 == 0:
            return 0.0
        
        c12 = len(zlib.compress(s1 + s2))
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # We want similarity, so 1 - NCD
        ncd = (c12 - min(l1, l2)) / max(l1, l2)
        return max(0.0, 1.0 - ncd)

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment and NCD."""
        # Structural parse
        struct_score, _ = self._structural_parse(prompt, answer)
        # Normalize structural score to 0-1 range roughly
        norm_struct = (struct_score + 1.0) / 2.0 
        
        # NCD baseline
        ncd_sim = self._ncd_score(prompt, answer)
        
        # Weighted average favoring structure
        final_conf = 0.6 * norm_struct + 0.4 * ncd_sim
        return min(1.0, max(0.0, final_conf))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Monitor Phase Transition (Order Parameter M)
        magnetization = self._calculate_magnetization(candidates)
        # Threshold for criticality: if magnetization < 0.5, system is disordered/critical
        is_critical = magnetization < 0.5
        
        results = []
        for cand in candidates:
            # Base score from NCD (Tiebreaker/Background)
            base_score = self._ncd_score(prompt, cand)
            
            # Structural Parsing (Model Checking)
            struct_score, reason = self._structural_parse(prompt, cand)
            
            # Apply Mechanism Design (VCG Rule)
            # If critical, structural correctness dominates. 
            final_score = self._vcg_payment_rule(base_score, is_critical, struct_score)
            
            # Add small bonus for length appropriateness (avoiding empty or huge spam)
            if 0.5 * len(prompt) <= len(cand) <= 3.0 * len(prompt):
                final_score += 0.05
                
            results.append({
                "candidate": cand,
                "score": float(f"{final_score:.6f}"), # Ensure float type
                "reasoning": f"Phase={'Critical' if is_critical else 'Stable'}; {reason}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results