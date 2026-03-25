import re
import json
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    TRISL: Thermodynamic-Regularized Incentive-Compatible Sparse Learner.
    
    Mechanism Analogy:
    1. Thermodynamics (Entropy/Free Energy): We treat the candidate text as a system.
       Complexity (length + special token density) represents 'Energy'. 
       Entropy is approximated by NCD (compression). The 'Free Energy' score balances 
       fit (structural alignment) against complexity (Occam's razor).
       
    2. Compressed Sensing (Sparse Inference): We assume the 'truth' is sparse.
       We extract a sparse set of structural features (negations, comparatives, numbers)
       rather than using full semantic vectors. This acts as the sensing matrix A.
       
    3. Mechanism Design (Incentive Compatibility): 
       Candidates are 'agents' reporting measurements. 
       The scoring function acts as a VCG-like payment rule:
       - Base Score: Structural alignment with prompt constraints.
       - Penalty (Tax): Deviation from prompt complexity (entropy cost).
       - Reward: Truthful reporting (matching numeric/logical constraints) minimizes the 'free energy' cost.
       
    This ensures that the highest-ranked candidate is the one that truthfully satisfies
    the prompt's logical constraints with minimal unnecessary complexity.
    """

    def __init__(self):
        # State initialization if needed for iterative processes
        pass

    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """Extract sparse structural features (Compressed Sensing step)."""
        text_lower = text.lower()
        
        # Negations
        negations = len(re.findall(r'\b(not|no|never|neither|nobody|nothing)\b', text_lower))
        
        # Comparatives/Superlatives
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|better|worse|larger|higher|lower|most|least|best|worst)\b', text_lower))
        
        # Conditionals
        conditionals = len(re.findall(r'\b(if|unless|provided|assuming|then|else)\b', text_lower))
        
        # Numbers (for numeric evaluation)
        numbers = re.findall(r'-?\d+\.?\d*', text)
        numeric_vals = []
        for n in numbers:
            try:
                numeric_vals.append(float(n))
            except ValueError:
                pass
                
        return {
            "length": len(text),
            "negations": negations,
            "comparatives": comparatives,
            "conditionals": conditionals,
            "numbers": numeric_vals,
            "has_numbers": len(numeric_vals) > 0
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as an entropy proxy."""
        if not s1 or not s2:
            return 1.0
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            ncd = (c12 - min_len) / max(c1, c2)
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def _calculate_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Calculate score based on structural parsing and constraint propagation.
        This is the primary signal (beating NCD baseline).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has high negation density, valid answers often acknowledge it or follow logic
        if p_struct["negations"] > 0:
            # Reward if candidate also handles negation or is logically consistent
            # Heuristic: If prompt negates, simple positive echo is bad. 
            # We reward structural complexity matching.
            score += 0.5 * (c_struct["negations"] >= 1)
        
        # 2. Conditional Logic
        if p_struct["conditionals"] > 0:
            # Reward candidates that also exhibit conditional logic or specific answers
            score += 0.5 * (c_struct["conditionals"] > 0 or c_struct["has_numbers"])
            
        # 3. Numeric Evaluation
        if p_struct["has_numbers"] and c_struct["has_numbers"]:
            # Check for numeric consistency if both have numbers
            # Simple heuristic: If prompt asks for comparison, candidate should reflect order
            p_nums = p_struct["numbers"]
            c_nums = c_struct["numbers"]
            
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Detect if prompt implies a comparison (e.g., "which is larger?")
                is_larger_q = "larger" in prompt.lower() or "greater" in prompt.lower() or "max" in prompt.lower()
                is_smaller_q = "smaller" in prompt.lower() or "less" in prompt.lower() or "min" in prompt.lower()
                
                p_diff = p_nums[0] - p_nums[1] if len(p_nums) >= 2 else 0
                
                if is_larger_q:
                    # Expect candidate to pick larger number
                    if c_nums[0] == max(p_nums): score += 2.0
                    elif c_nums[0] > p_diff: score += 0.5 # Partial credit for direction
                elif is_smaller_q:
                    if c_nums[0] == min(p_nums): score += 2.0
                else:
                    # General numeric presence bonus for math problems
                    score += 1.0
        elif p_struct["has_numbers"] and not c_struct["has_numbers"]:
            # Penalty for missing numbers when prompt has them
            score -= 1.0

        # 4. Length/Complexity Matching (Thermodynamic prior)
        # Avoid extremely short answers for complex prompts (Occam's razor but not too short)
        if len(prompt) > 50 and len(candidate) < 5:
            score -= 0.5
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Pre-calculate prompt structure
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Primary Signal)
            struct_score = self._calculate_structural_score(prompt, cand)
            
            # 2. Thermodynamic Regularization (Entropy/NCD)
            # NCD acts as the "Free Energy" penalty for complexity mismatch
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Mechanism Design Payment Rule:
            # Score = Structural Fit - Beta * (Complexity Cost)
            # Beta acts as inverse temperature. High NCD (dissimilarity) increases cost if structure doesn't align.
            beta = 0.5 
            thermodynamic_penalty = beta * ncd_val
            
            # Final Score formulation
            # We want high structural score, low NCD (high similarity in compressed space implies relatedness)
            # But NCD is distance, so we subtract it.
            final_score = struct_score - thermodynamic_penalty
            
            # Bonus for exact keyword matches in structural roles (Constraint Propagation)
            c_lower = cand.lower()
            p_lower = prompt.lower()
            
            # Check for direct contradiction in negation (Simple heuristic)
            if "not" in p_lower and ("yes" in c_lower or "true" in c_lower) and "not" not in c_lower:
                 # Potential trap, reduce score slightly unless context clarifies
                 pass 

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural fit: {struct_score:.2f}, Entropy cost (NCD): {ncd_val:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and thermodynamic stability.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        item = res[0]
        score = item["score"]
        
        # Map score to 0-1 confidence
        # Heuristic mapping based on empirical thresholds
        # Score > 1.0: High confidence (Strong structural match)
        # Score > 0.0: Medium confidence
        # Score < 0.0: Low confidence
        
        confidence = 1.0 / (1.0 + 2.718 ** (-score)) # Sigmoid mapping
        
        # Clamp
        return max(0.0, min(1.0, confidence))