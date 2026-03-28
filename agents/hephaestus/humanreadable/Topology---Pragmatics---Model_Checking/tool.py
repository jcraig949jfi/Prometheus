import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Topological Model Checker (PTMC) Approximation.
    
    Mechanism:
    1. Structural Parsing (Topology Proxy): Instead of computing persistent homology on a 
       state graph (which is infeasible without a formal model), we treat the text's 
       logical structure as a simplicial complex. We detect "holes" (missing logical links) 
       by analyzing negations, conditionals, and comparatives. A candidate that fills these 
       structural holes (e.g., provides the missing consequent or respects a negation) 
       receives a topological boost.
       
    2. Pragmatic Refinement: We apply Gricean maxims (Relevance, Quantity) by checking 
       if a candidate directly addresses the specific constraints extracted from the prompt. 
       Candidates that ignore specific numeric or logical constraints are penalized as 
       "pragmatically infelicitous."
       
    3. Model Checking Simulation: We simulate a verification step by treating the prompt's 
       constraints as assertions. Candidates are "checked" against these assertions. 
       Failure to satisfy a hard constraint (e.g., numeric inequality) results in a 
       counter-example, lowering the score.
       
    4. Scoring: Primary signal is structural/constraint satisfaction (Logic). 
       Tie-breaking uses Normalized Compression Distance (NCD) to favor candidates 
       lexically similar to the context (Relevance).
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(less|more|greater|smaller|larger|fewer|higher|lower)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+(?:\.\d+)?')
        self.bool_pattern = re.compile(r'\b(true|false|yes|no)\b', re.IGNORECASE)

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for constraint checking."""
        return [float(n) for n in self.number_pattern.findall(text)]

    def _analyze_structure(self, text: str) -> Dict:
        """
        Analyze text for logical 'holes' and structural markers.
        Returns a signature used for topological comparison.
        """
        has_neg = bool(self.negation_pattern.search(text))
        has_cond = bool(self.conditional_pattern.search(text))
        has_comp = bool(self.comparative_pattern.search(text))
        nums = self._extract_numbers(text)
        has_bool = bool(self.bool_pattern.search(text))
        
        return {
            "neg_count": int(has_neg),
            "cond_count": int(has_cond),
            "comp_count": int(has_comp),
            "num_count": len(nums),
            "has_bool": int(has_bool),
            "nums": nums
        }

    def _check_constraints(self, prompt_struct: Dict, cand_struct: Dict, prompt_lower: str, cand_lower: str) -> float:
        """
        Simulate model checking: Verify if candidate satisfies prompt constraints.
        Returns a score modifier based on constraint satisfaction.
        """
        score = 1.0
        
        # 1. Numeric Consistency Check
        # If prompt has numbers and candidate has numbers, check logical consistency
        if prompt_struct["num_count"] > 0 and cand_struct["num_count"] > 0:
            p_nums = prompt_struct["nums"]
            c_nums = cand_struct["nums"]
            
            # Heuristic: If prompt implies "less", candidate numbers should ideally be smaller
            # or the candidate should explicitly mention the relation.
            if "less" in prompt_lower or "smaller" in prompt_lower or "fewer" in prompt_lower:
                # If candidate repeats the larger number without qualification, it might be wrong
                # This is a weak proxy, but captures the 'comparative' topology
                if max(c_nums) > max(p_nums) and "less" not in cand_lower and "smaller" not in cand_lower:
                    score -= 0.4
            
            elif "more" in prompt_lower or "greater" in prompt_lower or "larger" in prompt_lower:
                if min(c_nums) < min(p_nums) and "more" not in cand_lower and "greater" not in cand_lower:
                    score -= 0.4

        # 2. Negation Preservation (Modus Tollens proxy)
        # If prompt strongly negates, candidate shouldn't affirm blindly unless structured carefully
        if prompt_struct["neg_count"] > 0:
            # If candidate has NO negation words but the prompt is a negative constraint,
            # it might be failing to address the 'hole' (the exception).
            # However, if the answer is simply "No", that's valid.
            if cand_struct["neg_count"] == 0 and cand_struct["has_bool"] == 0:
                # Potential false positive risk, slight penalty if structure mismatches
                score -= 0.1

        # 3. Conditional Logic
        if prompt_struct["cond_count"] > 0:
            # If prompt is conditional, candidate should ideally reflect uncertainty or conditionality
            # unless it's a direct deduction. 
            # We reward candidates that contain logical connectors if the prompt has them.
            if cand_struct["cond_count"] == 0 and cand_struct["has_bool"] == 0:
                score -= 0.05 # Weak penalty

        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        denominator = max(len1, len2)
        if denominator == 0:
            return 1.0
        return (len12 - min(len1, len2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_lower = prompt.lower()
        p_struct = self._analyze_structure(prompt)
        p_len = len(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_lower = cand.lower()
            c_struct = self._analyze_structure(cand)
            
            # 1. Structural/Logical Score (Primary Signal)
            # Check if candidate fills the logical 'holes' identified in prompt
            logic_score = self._check_constraints(p_struct, c_struct, prompt_lower, cand_lower)
            
            # Bonus for structural alignment (e.g., if prompt asks a question, answer should be concise)
            # If prompt is long and complex, candidate should have some substance (not too short)
            if p_struct["cond_count"] > 0 and c_struct["cond_count"] == 0 and c_struct["has_bool"] == 0:
                # Prompt has logic, candidate is simple text -> maybe less relevant
                logic_score *= 0.9
                
            # 2. Pragmatic Relevance (NCD as tiebreaker/refiner)
            # NCD measures how much information in the candidate is 'new' vs shared with prompt
            ncd_val = self._ncd(prompt_lower, cand_lower)
            
            # Convert NCD to a relevance score (lower NCD = higher relevance usually, but too low = echo)
            # We want a balance. 
            # If NCD is very high (>0.9), candidate is unrelated -> penalty.
            relevance_score = 1.0 if ncd_val < 0.8 else 0.5
            
            # Combine scores: Logic is dominant, NCD refines
            final_score = (logic_score * 0.7) + (relevance_score * 0.3)
            
            # Heuristic boost for exact keyword matches in numeric/comparative contexts
            if p_struct["comp_count"] > 0:
                if any(k in cand_lower for k in ["less", "more", "greater", "smaller", "larger"]):
                    final_score += 0.1
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f}, NCD:{ncd_val:.2f}"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence that 'answer' is correct for 'prompt'.
        Uses the same structural and pragmatic analysis.
        """
        # Run single evaluation
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize the score to 0-1 range based on internal thresholds
        raw_score = results[0]["score"]
        
        # Calibration: 
        # Raw score can exceed 1.0 due to bonuses. 
        # Map typical range [0.5, 1.2] to [0.1, 0.95] to avoid overconfidence
        confidence = (raw_score - 0.5) * 1.2 
        return max(0.0, min(1.0, confidence))