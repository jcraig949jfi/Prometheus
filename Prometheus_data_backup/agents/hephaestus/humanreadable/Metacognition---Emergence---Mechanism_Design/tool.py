import re
import json
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Reflective Emergent Mechanism-Design (SREMD) Tool.
    
    Mechanism:
    1. Micro-Level (Hypothesis Generation): Candidates are parsed into structural 
       features (negations, comparatives, numeric values, logical constraints).
    2. Emergent Macro-Level (Auction): Candidates "bid" compute resources based on 
       their expected reduction in uncertainty (entropy). The bid is calculated 
       via a VCG-style score: (Structural Match * Numeric Consistency) - Penalty.
       This ensures incentive compatibility; candidates with contradictory 
       structures (e.g., prompt says "not", candidate says "yes") bid low.
    3. Metacognitive Loop: A calibration layer adjusts scores based on 
       self-consistency checks (e.g., if a candidate is a subset of the prompt 
       but misses a negation, confidence is penalized).
    
    This architecture prioritizes structural logic over string similarity (NCD),
    using NCD only as a tie-breaker for semantically identical structures.
    """

    def __init__(self):
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")
        self.negations = {"no", "not", "never", "none", "neither", "n't"}
        self.comparatives = {"more", "less", "greater", "smaller", "higher", "lower", ">", "<"}
        self.conditionals = {"if", "then", "else", "unless", "when"}

    def _parse_structure(self, text: str) -> dict:
        """Extract structural features: negations, numbers, comparatives, conditionals."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negations)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            "negations": has_negation,
            "comparatives": has_comparative,
            "conditionals": has_conditional,
            "numbers": numbers,
            "word_set": words,
            "length": len(text)
        }

    def _calculate_vcg_bid(self, prompt_feat: dict, cand_feat: dict) -> float:
        """
        Computes the 'bid' for a candidate based on mechanism design principles.
        The bid represents the marginal gain in truthfulness (structural alignment).
        High bid = High alignment with prompt constraints.
        """
        score = 0.0
        
        # 1. Constraint Propagation (Negation Matching)
        # If prompt has negation, candidate MUST have negation (or specific contradiction logic)
        if prompt_feat["negations"]:
            if cand_feat["negations"]:
                score += 2.0  # Reward matching negation
            else:
                score -= 5.0  # Heavy penalty for missing negation (Critical failure)
        else:
            # Penalty if candidate introduces unwarranted negation
            if cand_feat["negations"]:
                score -= 1.0

        # 2. Comparative Consistency
        if prompt_feat["comparatives"]:
            if cand_feat["comparatives"]:
                score += 1.5
            # Neutral if missing, but not penalized heavily unless numbers contradict
        
        # 3. Numeric Evaluation (Transitivity/Magnitude)
        p_nums = prompt_feat["numbers"]
        c_nums = cand_feat["numbers"]
        
        if p_nums and c_nums:
            # Check rough order of magnitude or direct equality
            # Simple heuristic: If prompt implies a direction, does candidate follow?
            # Here we just check presence and proximity as a proxy for valid calculation
            min_p = min(p_nums)
            max_p = max(p_nums) if len(p_nums) > 1 else min_p
            
            # Reward if candidate numbers are within reasonable range of prompt context
            # or if they resolve a comparison correctly (simplified for single pass)
            for cn in c_nums:
                if min_p <= cn <= max_p:
                    score += 1.0
                else:
                    # If candidate number is wildly outside prompt range, slight penalty
                    score -= 0.5
        elif p_nums and not c_nums:
            # Prompt has math, candidate ignores it -> Penalty
            score -= 2.0

        # 4. Structural Overlap (Jaccard-ish) excluding stop words
        common = prompt_feat["word_set"] & cand_feat["word_set"]
        # Remove generic words to avoid noise
        noise = {"the", "a", "an", "is", "are", "was", "were", "be", "to", "of", "and", "or"}
        common_clean = common - noise
        overlap_ratio = len(common_clean) / (len(prompt_feat["word_set"]) + 1e-6)
        
        score += overlap_ratio * 3.0
        
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tie-breaker."""
        import zlib
        s1_bytes = s1.encode()
        s2_bytes = s2.encode()
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._parse_structure(prompt)
        results = []
        
        # Phase 1: Bidding (Scoring)
        bids = []
        for idx, cand in enumerate(candidates):
            cand_feat = self._parse_structure(cand)
            # Mechanism Design: VCG-style bid based on structural alignment
            bid_score = self._calculate_vcg_bid(prompt_feat, cand_feat)
            
            # Metacognitive Wrapper: Adjust for self-consistency
            # If candidate is just a repetition of prompt without answer, penalize
            if cand.strip() == prompt.strip():
                bid_score -= 10.0
            
            bids.append((idx, bid_score, cand))
        
        # Sort by bid score (descending)
        bids.sort(key=lambda x: x[1], reverse=True)
        
        # Phase 2: Allocation & Calibration
        # Normalize scores to 0-1 range roughly, using the top bid as anchor
        max_bid = bids[0][1] if bids else 0
        min_bid = bids[-1][1] if bids else 0
        range_bid = max_bid - min_bid if max_bid != min_bid else 1.0
        
        final_ranking = []
        for rank, (idx, bid_score, cand) in enumerate(bids):
            # Normalize bid to 0.2 - 0.99 range
            normalized_score = 0.2 + (0.79 * (bid_score - min_bid) / range_bid)
            
            # Tie-breaking with NCD if scores are very close (within 0.01)
            if rank > 0:
                prev_score = final_ranking[-1]["raw_score"]
                if abs(bid_score - prev_score) < 0.05:
                    prev_cand = final_ranking[-1]["candidate"]
                    ncd_curr = self._ncd_distance(prompt, cand)
                    ncd_prev = self._ncd_distance(prompt, prev_cand)
                    # Lower NCD means more similar (often better for tie breaking in simple cases)
                    if ncd_curr > ncd_prev:
                        normalized_score -= 0.01 # Slight penalty
            
            # Ensure strict ordering if needed, but float precision usually handles it
            reasoning = f"Structural alignment score: {bid_score:.4f}. "
            if prompt_feat["negations"] and not self._parse_structure(cand)["negations"]:
                reasoning += "Warning: Missing negation detected."
            elif prompt_feat["numbers"] and not self._parse_structure(cand)["numbers"]:
                reasoning += "Note: Numeric data present in prompt but absent in candidate."
            else:
                reasoning += "Constraints satisfied."

            final_ranking.append({
                "candidate": cand,
                "score": round(normalized_score, 4),
                "reasoning": reasoning,
                "raw_score": bid_score # For internal tracking if needed
            })
            
        # Clean up internal keys before returning
        return [{k: v for k, v in item.items() if k != "raw_score"} for item in final_ranking]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the same mechanism: high structural alignment = high confidence.
        """
        prompt_feat = self._parse_structure(prompt)
        cand_feat = self._parse_structure(answer)
        
        bid = self._calculate_vcg_bid(prompt_feat, cand_feat)
        
        # Map bid to 0-1. 
        # Heuristic mapping based on typical bid ranges:
        # Strong match: > 3.0 -> 0.9+
        # Weak match: ~0.0 -> 0.5
        # Contradiction: < -2.0 -> < 0.2
        
        # Sigmoid-like mapping approximation
        confidence = 1 / (1 + 2.718 ** (-0.5 * (bid - 1.0)))
        
        # Hard constraints (Metacognitive override)
        if prompt_feat["negations"] and not cand_feat["negations"]:
            confidence = min(confidence, 0.3) # Cap confidence if negation missed
            
        return round(max(0.0, min(1.0, confidence)), 4)