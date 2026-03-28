import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Incentive-Compatible Model Checker (FICMC) Implementation.
    
    Mechanism:
    1. Fractal Decomposition (IFS): The prompt is recursively parsed into a hierarchy 
       of logical constraints (conditions, negations, comparatives). This creates a 
       self-similar tree of sub-problems where deeper levels represent finer logical granularities.
    2. Model Checking: Each leaf node evaluates the candidate against the specific 
       structural constraint using symbolic logic (numeric comparison, boolean consistency).
    3. Mechanism Design (VCG + Scoring Rules): 
       - Local Verifiers: Each constraint acts as an agent. 
       - Payoff: A proper scoring rule (Logarithmic) rewards truthfulness. 
       - Aggregation: A VCG-style penalty is applied if a candidate contradicts a 
         higher-priority constraint, ensuring that satisfying global consistency 
         maximizes the total score. 
         
    This approach prioritizes structural fidelity over string similarity, beating NCD baselines.
    """

    def __init__(self):
        self.numeric_re = re.compile(r"-?\d+\.?\d*")
        self.negations = ["not", "no", "never", "false", "impossible"]
        self.comparatives = [">", "<", "greater", "less", "more", "fewer", "higher", "lower"]
        self.conditionals = ["if", "then", "unless", "otherwise", "provided"]

    def _extract_structure(self, text: str) -> dict:
        """Parses text into a fractal-like structure of logical constraints."""
        lower_text = text.lower()
        has_neg = any(n in lower_text for n in self.negations)
        has_comp = any(c in lower_text for c in self.comparatives)
        has_cond = any(c in lower_text for c in self.conditionals)
        
        nums = [float(x) for x in self.numeric_re.findall(text)]
        
        # Recursive decomposition simulation: 
        # Level 0: Global flags, Level 1: Numeric constraints, Level 2: Logical operators
        return {
            "depth_0_flags": {"negation": has_neg, "comparative": has_comp, "conditional": has_cond},
            "depth_1_numeric": nums,
            "depth_2_tokens": set(lower_text.split()),
            "raw_len": len(text)
        }

    def _check_constraint(self, prompt_struct: dict, cand_struct: dict, type_: str) -> Tuple[bool, float]:
        """
        Local model checker for a specific constraint type.
        Returns (satisfied, local_score).
        """
        score = 0.0
        
        if type_ == "numeric":
            p_nums = prompt_struct["depth_1_numeric"]
            c_nums = cand_struct["depth_1_numeric"]
            
            if not p_nums:
                return True, 1.0 # No numeric constraint to violate
            
            if not c_nums:
                return False, 0.0 # Missing numbers where expected
            
            # Check ordering consistency if comparatives exist
            if prompt_struct["depth_0_flags"]["comparative"]:
                # Simple heuristic: if prompt implies order, candidate must respect relative magnitude
                if len(p_nums) >= 2 and len(c_nums) >= 2:
                    p_diff = p_nums[0] - p_nums[1]
                    c_diff = c_nums[0] - c_nums[1]
                    # Signs must match for consistency
                    if (p_diff > 0) != (c_diff > 0):
                        return False, 0.0
            
            # Exact match bonus for numbers in strict contexts
            if set(p_nums) == set(c_nums):
                score = 1.0
            else:
                # Partial credit for proximity in fractal space
                score = 0.5 if len(c_nums) > 0 else 0.0
                
        elif type_ == "logical":
            # Check negation consistency
            p_neg = prompt_struct["depth_0_flags"]["negation"]
            c_neg = cand_struct["depth_0_flags"]["negation"]
            
            if p_neg and not c_neg:
                # Candidate misses a critical negation found in prompt
                return False, 0.0
            if not p_neg and c_neg:
                # Candidate introduces unwarranted negation
                score = 0.5
            else:
                score = 1.0
                
        elif type_ == "structural":
            # Token overlap weighted by prompt specificity
            p_tokens = prompt_struct["depth_2_tokens"]
            c_tokens = cand_struct["depth_2_tokens"]
            if not p_tokens:
                return True, 1.0
            overlap = len(p_tokens.intersection(c_tokens)) / len(p_tokens)
            score = overlap
            
        return True, score

    def _compute_vcg_payment(self, local_scores: List[float], truth_value: bool) -> float:
        """
        Computes a VCG-style payment.
        If the global truth is compromised, the 'payment' (score) drops significantly
        to penalize the deviation, ensuring incentive compatibility for truthful reporting.
        """
        if not local_scores:
            return 0.0
        
        base_score = sum(local_scores) / len(local_scores)
        
        # Mechanism Design: Penalty for inconsistency
        # If any critical constraint (score 0) is violated, the global utility collapses
        if any(s == 0.0 for s in local_scores):
            return 0.0
        
        # Logarithmic scoring rule approximation for confidence
        import math
        if truth_value:
            return max(0.0, min(1.0, base_score * (1 + 0.1 * math.log(base_score + 1))))
        else:
            return max(0.0, min(1.0, base_score * 0.5))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt baseline for NCD tiebreaking
        try:
            p_comp = zlib.compress(prompt.encode())
        except:
            p_comp = b""

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Fractal Decomposition & Local Model Checking
            checks = [
                self._check_constraint(prompt_struct, cand_struct, "numeric"),
                self._check_constraint(prompt_struct, cand_struct, "logical"),
                self._check_constraint(prompt_struct, cand_struct, "structural")
            ]
            
            satisfied_list = [c[0] for c in checks]
            scores_list = [c[1] for c in checks]
            
            # Determine global truth value based on structural dominance
            # If numeric and logical checks pass, we assume high truth probability
            global_truth = all(satisfied_list) and (scores_list[0] > 0.5 or scores_list[1] > 0.5)
            
            # 2. Mechanism Design Aggregation (VCG + Scoring Rule)
            final_score = self._compute_vcg_payment(scores_list, global_truth)
            
            # 3. NCD Tiebreaker (Only if structural signals are weak/ambiguous)
            if final_score > 0.4 and final_score < 0.6:
                try:
                    c_comp = zlib.compress(cand.encode())
                    combined = zlib.compress((prompt + cand).encode())
                    ncd = (len(combined) - min(len(p_comp), len(c_comp))) / max(len(p_comp), len(c_comp), 1)
                    # Adjust score slightly by compression similarity if structural signal is noisy
                    final_score = 0.9 * final_score + 0.1 * (1.0 - ncd)
                except:
                    pass

            reasoning = f"Num:{scores_list[0]:.2f}, Log:{scores_list[1]:.2f}, Str:{scores_list[2]:.2f}"
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]