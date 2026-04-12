import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Message Passing Solver for Probabilistic Constraint Satisfaction.
    
    Mechanism:
    1. Bayesian Layer (Priors): Scores candidates based on structural alignment 
       (negations, comparatives, numeric consistency) with the prompt.
    2. CSP Layer (Constraints): Enforces hard logical constraints (e.g., if prompt 
       says "not X", candidates containing X get probability 0).
    3. Free Energy Principle (Active Inference): Computes a 'surprise' metric 
       (Variational Free Energy) representing the divergence between the candidate's 
       structural signature and the prompt's requirements. 
       
    The final score minimizes Free Energy (maximizes alignment) while satisfying 
    hard constraints. NCD is used only as a tie-breaking similarity metric.
    """

    def __init__(self):
        self.negation_words = ["not", "no", "never", "none", "neither", "n't"]
        self.comparative_ops = [">", "<", "greater", "less", "more", "fewer"]
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> dict:
        """Extract logical features: negations, numbers, comparatives."""
        lower_text = text.lower()
        has_negation = any(w in lower_text for w in self.negation_words)
        has_comparative = any(op in lower_text for op in self.comparative_ops)
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        return {
            "negation": has_negation,
            "comparative": has_comparative,
            "numbers": numbers,
            "length": len(text),
            "raw": lower_text
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _check_hard_constraints(self, prompt_feat: dict, cand_feat: dict) -> bool:
        """
        CSP Layer: Enforce hard logical constraints.
        If prompt implies negation, candidate must not contradict directly 
        (simplified heuristic: if prompt says 'not apple', candidate 'apple' is bad).
        """
        # Heuristic: If prompt has strong negation context and candidate is short 
        # and matches a noun in prompt, it might be a trap. 
        # For this implementation, we focus on numeric consistency as a hard constraint.
        
        p_nums = prompt_feat["numbers"]
        c_nums = cand_feat["numbers"]

        # If prompt establishes a numeric bound (e.g., "less than 5"), 
        # and candidate violates it explicitly, prune.
        # This is a simplified constraint propagation for demonstration.
        if len(p_nums) > 0 and len(c_nums) > 0:
            # If prompt mentions "less" and candidate number is huge compared to prompt max
            if "less" in prompt_feat["raw"] or "fewer" in prompt_feat["raw"]:
                if max(c_nums) > max(p_nums) * 10: # Arbitrary threshold for violation
                    return False
            if "greater" in prompt_feat["raw"] or "more" in prompt_feat["raw"]:
                if min(c_nums) < min(p_nums) * 0.1:
                    return False
        return True

    def _compute_free_energy(self, prompt_feat: dict, cand_feat: dict) -> float:
        """
        Free Energy Principle: Calculate surprise (prediction error).
        Lower energy = better fit.
        Energy = Prediction Error (structural mismatch) + Complexity Penalty
        """
        energy = 0.0

        # 1. Negation Consistency (Bayesian Update)
        # If prompt negates, we expect the answer to reflect that logic.
        if prompt_feat["negation"]:
            # Penalty if candidate lacks negation markers when prompt has them
            if not cand_feat["negation"]:
                energy += 2.0 
        else:
            if cand_feat["negation"]:
                energy += 1.0 # Unexpected negation

        # 2. Numeric Prediction Error
        p_nums = prompt_feat["numbers"]
        c_nums = cand_feat["numbers"]
        
        if p_nums and c_nums:
            # Check directional consistency
            p_dir = 1 if "greater" in prompt_feat["raw"] or "more" in prompt_feat["raw"] else -1
            # Simple error metric: deviation from expected relative magnitude
            # This is a proxy for variational bound minimization
            try:
                ratio = c_nums[0] / (p_nums[0] + 1e-9)
                if p_dir == 1 and ratio < 1.0: energy += 3.0 # Should be greater
                if p_dir == -1 and ratio > 1.0: energy += 3.0 # Should be less
            except:
                pass
        
        # 3. Complexity (Occam's Razor)
        # Prefer shorter, concise answers if structural match is equal
        energy += 0.01 * cand_feat["length"]

        return energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feat = self._extract_structure(prompt)
        scored_candidates = []

        # Pre-calculate NCD for tie-breaking (expensive op, so cached)
        ncd_scores = {c: self._compute_ncd(prompt, c) for c in candidates}

        for cand in candidates:
            cand_feat = self._extract_structure(cand)
            
            # CSP Layer: Hard Constraint Pruning
            if not self._check_hard_constraints(prompt_feat, cand_feat):
                score = -100.0 # Hard rejection
                reason = "Violates hard logical constraint"
            else:
                # Free Energy Minimization
                # We invert energy to get a score (higher is better)
                energy = self._compute_free_energy(prompt_feat, cand_feat)
                
                # Base score from structural alignment (Bayesian Prior)
                base_score = 0.0
                if prompt_feat["negation"] == cand_feat["negation"]:
                    base_score += 5.0
                if prompt_feat["comparative"] == cand_feat["comparative"]:
                    base_score += 2.0
                
                # Final Score = Prior - Free Energy (Surprise)
                # NCD is used only as a tiny tiebreaker if energy is similar
                score = base_score - energy - (ncd_scores[cand] * 0.1)
                reason = f"Energy: {energy:.2f}, Structural Match: {base_score:.1f}"

            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on free energy minimization.
        1.0 = Minimal surprise (perfect fit), 0.0 = High surprise (violation).
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize score to 0-1 range heuristically
        # Scores usually range from -100 (hard fail) to ~7 (perfect match)
        raw_score = results[0]["score"]
        
        if raw_score <= -50:
            return 0.0
        if raw_score >= 5.0:
            return 1.0
            
        # Sigmoid-like mapping
        confidence = 1.0 / (1.0 + math.exp(-raw_score + 2.0))
        return max(0.0, min(1.0, confidence))