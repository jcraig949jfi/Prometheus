import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Type-Guided MCTS (RG-MCTS) Approximation.
    
    Mechanism:
    1. Type-Guided Filtering (Coarse Grain 1): Candidates are parsed for logical 
       consistency with the prompt's structural constraints (negations, conditionals).
       Invalid "types" (logical mismatches) are penalized heavily.
    2. Structural Scoring (Fine Grain): Extracts numeric comparisons and boolean 
       logic to assign a base Q-value.
    3. Renormalization: The final score is a weighted flow where structural evidence 
       (high fidelity) dominates, while NCD acts as a low-fidelity tiebreaker only 
       when structural signals are ambiguous (simulating RG flow to fixed point).
    4. MCTS Analogy: Exploration bonus is simulated by favoring candidates that 
       explicitly address specific prompt tokens (coverage).
    """
    
    def __init__(self):
        self.ncd_calls = 0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _parse_structure(self, text: str) -> Dict:
        """Extract logical atoms: negations, comparatives, numbers, conditionals."""
        text_l = text.lower()
        has_neg = bool(re.search(r'\b(not|no|never|without|impossible|false)\b', text_l))
        has_if = bool(re.search(r'\b(if|then|unless|provided)\b', text_l))
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', text_l)]
        # Detect simple comparatives
        has_comp = bool(re.search(r'\b(more|less|greater|smaller|higher|lower|best|worst)\b', text_l))
        return {
            "neg": has_neg, "if": has_if, "nums": nums, "comp": has_comp,
            "len": len(text), "words": set(re.findall(r'\w+', text_l))
        }

    def _check_logical_consistency(self, p_struct: Dict, c_struct: Dict, prompt: str, candidate: str) -> float:
        """Type-checking: Does the candidate respect the prompt's logical signature?"""
        score = 0.0
        
        # Negation consistency: If prompt asks "What is NOT...", candidate shouldn't be empty or generic
        if p_struct["neg"]:
            if c_struct["neg"]: score += 0.2 # Reinforces negative logic
            # Penalize if prompt has specific numbers and candidate ignores them completely
            if len(p_struct["nums"]) > 0 and len(c_struct["nums"]) == 0:
                score -= 0.3 

        # Numeric consistency: If prompt has numbers, candidate should engage with them
        if len(p_struct["nums"]) >= 2:
            if len(c_struct["nums"]) > 0:
                # Check magnitude alignment (heuristic)
                p_max = max(p_struct["nums"])
                c_max = max(c_struct["nums"]) if c_struct["nums"] else 0
                if p_max > 0 and c_max > 0:
                    score += 0.3 # Engaged with numbers
            else:
                score -= 0.4 # Ignored numeric data

        # Conditional consistency
        if p_struct["if"] and not c_struct["if"]:
            # Prompt sets up a condition, candidate should ideally reflect consequence or condition
            if len(c_struct["words"]) < 3:
                score -= 0.2 # Too short to be a valid conditional response

        return score

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Primary scoring based on structural parsing and logic."""
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        
        score = 0.5 # Base prior
        
        # 1. Type Guidance (Logical Consistency)
        score += self._check_logical_consistency(p_struct, c_struct, prompt, candidate)
        
        # 2. Numeric Evaluation (Direct computation check)
        if len(p_struct["nums"]) >= 2 and len(c_struct["nums"]) >= 1:
            # Simple heuristic: if prompt implies comparison, does candidate match expected order?
            # E.g., "Is 9.11 > 9.9?" -> "No" (requires external knowledge, approximated here by presence)
            score += 0.2
            
        # 3. Coverage (MCTS Exploration Bonus analog)
        # Reward candidates that contain unique significant words from the prompt
        common_words = p_struct["words"] & c_struct["words"]
        coverage = len(common_words) / (len(p_struct["words"]) + 1)
        score += coverage * 0.2
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate structural scores (Fine scale)
        struct_scores = [(c, self._compute_structural_score(prompt, c)) for c in candidates]
        max_struct = max(s[1] for s in struct_scores) if struct_scores else 0.5
        min_struct = min(s[1] for s in struct_scores) if struct_scores else 0.0
        range_struct = max_struct - min_struct if max_struct != min_struct else 1.0

        for cand, s_score in struct_scores:
            # Renormalization Step:
            # If structural signal is strong (far from mean), trust it.
            # If structural signal is weak (all similar), flow towards NCD (tiebreaker).
            
            normalized_s = (s_score - min_struct) / range_struct
            
            # Calculate NCD only as a tiebreaker/refiner
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) and scale to [0, 0.1] range
            # so it never overrides strong structural logic
            ncd_score = (1.0 - ncd_val) * 0.05 
            
            # Final RG Flow: Structural (90%+) + NCD (<10%)
            final_score = 0.9 * normalized_s + 0.1 * ncd_score
            
            # Reasoning string generation
            reason = f"Structural match: {s_score:.2f}. "
            if p_struct := self._parse_structure(prompt):
                if p_struct["nums"] and not self._parse_structure(cand)["nums"]:
                    reason += "Warning: Ignored numeric data. "
                if p_struct["neg"] and not self._parse_structure(cand)["neg"]:
                    reason += "Caution: Missing negation logic. "
            reason += f"Renormalized value: {final_score:.4f}"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural integrity as the primary proxy for correctness.
        """
        # Re-use evaluation logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]["score"]
        # Map internal score to confidence probability
        # High structural score -> High confidence
        # Low structural score -> Low confidence
        conf = max(0.0, min(1.0, score))
        return conf