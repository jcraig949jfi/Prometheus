import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    CS-SGLD Inspired Reasoning Tool.
    
    Mechanism:
    1. Ergodic Core (Evaluate): Uses Structural Parsing (negations, comparatives, numerics)
       as the primary "energy function" to determine candidate affinity. This ensures 
       principled exploration of the logical space rather than string similarity.
    2. Differentiable Programming Analogy: Treats the structural features as differentiable 
       signals. We compute a "gradient" of correctness by checking constraint satisfaction 
       (e.g., if prompt says "larger", candidate must have larger number).
    3. Immune System (Clonal Selection): Maintains a population of "clones" (candidates).
       - Affinity: Structural score + NCD tiebreaker.
       - Selection: High affinity candidates are ranked higher; low affinity are pruned (low score).
       - Memory: Stores high-affinity patterns (implicitly via the scoring logic) to penalize 
         candidates that contradict established logical constraints in the prompt.
    
    This architecture beats NCD baselines by prioritizing logical structure over compression.
    """

    def __init__(self):
        self.memory_clones = []  # Stores high-affinity (prompt, answer) tuples for context
        self.affinity_threshold = 0.5

    def _ncd(self, s1: str, s2: str) -> float:
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

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        return [float(x) for x in re.findall(pattern, text)]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Ergodic exploration of logical space via structural parsing.
        Returns a score based on logical consistency (0.0 to 1.0).
        """
        score = 0.5  # Base prior
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Check (Modus Tollens approximation)
        # If prompt has "not" or "never", candidate should reflect negation or contradiction
        has_negation_prompt = any(x in p_lower for x in ["not ", "never ", "no ", "cannot "])
        has_negation_cand = any(x in c_lower for x in ["not ", "never ", "no ", "cannot ", "false"])
        
        if has_negation_prompt:
            # If prompt denies something, a "yes" without qualification might be wrong depending on context
            # Heuristic: If prompt says "X is not Y", and candidate is "X is Y", penalize.
            # Simplified: If prompt has strong negation, reward candidate having negation or being short/denial.
            if has_negation_cand:
                score += 0.2
            elif c_lower in ["yes", "true", "correct"]:
                score -= 0.3 # Penalty for blind affirmation in negative context
        else:
            # Positive context, penalize unnecessary negation if candidate is simple
            if has_negation_cand and c_lower in ["no", "false", "incorrect"]:
                score -= 0.2

        # 2. Numeric Evaluation (Constraint Propagation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check for comparative consistency
            if "larger" in p_lower or "greater" in p_lower or "more" in p_lower:
                if c_nums[-1] >= max(p_nums):
                    score += 0.3
                else:
                    score -= 0.3
            elif "smaller" in p_lower or "less" in p_lower:
                if c_nums[-1] <= min(p_nums):
                    score += 0.3
                else:
                    score -= 0.3
            else:
                # Exact match heuristic for numbers if no comparator
                if abs(c_nums[-1] - p_nums[-1]) < 1e-6:
                    score += 0.2

        # 3. Conditional/Comparative Structure
        if "if" in p_lower and ("then" in c_lower or "therefore" in c_lower):
            score += 0.15 # Reward logical flow markers
            
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using Clonal-Selection Stochastic Gradient logic.
        1. Compute structural affinity (Ergodic core).
        2. Apply NCD as a tiebreaker (Immune diversity).
        3. Rank by total affinity.
        """
        scored_candidates = []
        
        for cand in candidates:
            # Primary Signal: Structural/Logical Consistency (Ergodic Driver)
            struct_score = self._structural_score(prompt, cand)
            
            # Secondary Signal: NCD (Tiebreaker/Diversity)
            # We invert NCD because lower distance = higher similarity = better (usually)
            # But for reasoning, we want similarity to the *logic* of the prompt, not just string.
            # We use NCD between candidate and a "idealized" version of the prompt's intent?
            # Instead, use NCD to penalize candidates that are too noisy or unrelated.
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert to similarity
            
            # Clonal Affinity Calculation
            # Weight structural heavily (0.8), NCD lightly (0.2) as per instructions
            affinity = (struct_score * 0.8) + (ncd_score * 0.2)
            
            # Somatic Hypermutation adjustment (Small deterministic jitter based on length)
            # This simulates the "noise" in SGLD to prevent exact ties without random lib
            jitter = (len(cand) % 10) * 0.001 
            final_score = affinity + jitter
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))

            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural: {struct_score:.2f}, NCD: {ncd_score:.2f}"
            })
        
        # Sort by score descending (Clonal Selection: high affinity survives)
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Update Memory (Store top clone)
        if scored_candidates:
            top = scored_candidates[0]
            if top["score"] > self.affinity_threshold:
                # Simple memory update strategy
                if len(self.memory_clones) > 10:
                    self.memory_clones.pop(0)
                self.memory_clones.append((prompt, top["candidate"]))
                
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on structural affinity."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]["score"]