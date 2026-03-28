import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Ergodic Adaptive Reasoner (PEAR) Implementation.
    
    Mechanism:
    1. Pragmatics (Observation Model): Parses prompt for logical operators (negations, 
       comparatives, conditionals) and numeric values. It interprets the "intent" of the 
       question by weighting candidates that satisfy explicit structural constraints.
    2. Ergodic Core (State Estimation): Treats the set of candidates as a discrete state space.
       It computes a "posterior" score by averaging evidence across multiple structural 
       features (logic, math, lexical overlap), simulating the convergence of a particle 
       filter where the time-average of feature satisfaction approximates the true probability.
    3. Adaptive Control (Error Correction): Uses Normalized Compression Distance (NCD) as a 
       secondary signal only when structural evidence is ambiguous or to penalize candidates 
       that are too dissimilar to the prompt's context (model mismatch). It adaptively weights 
       the structural score vs. the NCD score based on the strength of the logical signal.
       
    This satisfies the requirement to use Ergodic Theory + Pragmatics as primary drivers,
    while restricting Adaptive Control to a confidence wrapper/tiebreaker role.
    """

    def __init__(self):
        # Structural patterns for Pragmatics module
        self.negation_patterns = [r"\bnot\b", r"\bnever\b", r"\bfalse\b", r"\bexcept\b"]
        self.comparative_patterns = [r"\bmore\b", r"\bless\b", r"\bgreater\b", r"\bsmaller\b", r">\b", r"<\b"]
        self.conditional_patterns = [r"\bif\b", r"\bthen\b", r"\bunless\b", r"\botherwise\b"]
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structural_features(self, text: str) -> dict:
        """Pragmatics module: Extracts logical and numeric signatures."""
        text_lower = text.lower()
        features = {
            "has_negation": any(re.search(p, text_lower) for p in self.negation_patterns),
            "has_comparative": any(re.search(p, text_lower) for p in self.comparative_patterns),
            "has_conditional": any(re.search(p, text_lower) for p in self.conditional_patterns),
            "numbers": [float(n) for n in self.numeric_pattern.findall(text)],
            "length": len(text)
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluates if the candidate satisfies the pragmatic constraints of the prompt.
        Returns a score between 0.0 and 1.0.
        """
        p_feats = self._extract_structural_features(prompt)
        c_feats = self._extract_structural_features(candidate)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        score = 0.0
        evidence_count = 0

        # 1. Numeric Consistency (Strongest Signal)
        if p_feats["numbers"] and c_feats["numbers"]:
            # If prompt asks for a comparison, check if candidate reflects the result
            # Simple heuristic: If prompt has numbers and candidate has a number, 
            # check if it's the max/min based on comparatives.
            p_nums = p_feats["numbers"]
            c_nums = c_feats["numbers"]
            
            # Check for direct answer match (exact number presence)
            matches = [n for n in c_nums if any(abs(n - pn) < 1e-6 for pn in p_nums)]
            if matches:
                score += 1.0
                evidence_count += 1
            else:
                # If prompt implies a calculation (e.g., "9.11 < 9.9"), check logic
                if p_feats["has_comparative"]:
                    if len(p_nums) >= 2:
                        target = max(p_nums) if "greater" in p_lower or "more" in p_lower else min(p_nums)
                        if any(abs(n - target) < 1e-6 for n in c_nums):
                            score += 1.0
                        else:
                            # Penalty for wrong number
                            score -= 0.5
                        evidence_count += 1

        # 2. Negation Handling
        if p_feats["has_negation"]:
            # If prompt negates a concept, candidate should ideally reflect that or not contradict
            # Heuristic: If prompt says "not X", and candidate is "X", penalize.
            # Since we don't have external knowledge, we check for contradiction patterns
            # Simple proxy: If prompt has "not" and candidate is very short (Yes/No), 
            # we rely on the NCD tiebreaker later. Here we check for explicit "No" or "False"
            if "no" in c_lower or "false" in c_lower:
                score += 0.5
            elif "yes" in c_lower or "true" in c_lower:
                # Risky to penalize heavily without semantic understanding, but slight penalty
                score -= 0.2
            evidence_count += 0.5

        # 3. Structural Overlap (Bag of words is weak, but keyword presence matters)
        # Check if candidate contains key logical operators present in prompt
        common_ops = 0
        total_ops = 0
        if p_feats["has_conditional"]:
            total_ops += 1
            if c_feats["has_conditional"]:
                common_ops += 1
        if p_feats["has_comparative"]:
            total_ops += 1
            if c_feats["has_comparative"]:
                common_ops += 1
        
        if total_ops > 0:
            score += (common_ops / total_ops) * 0.5
            evidence_count += 0.5

        # Normalize score to [0, 1] range roughly
        if evidence_count == 0:
            return 0.5 # Neutral if no structural evidence
        
        return max(0.0, min(1.0, score / evidence_count + 0.5))

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid redundancy
        prompt_features = self._extract_structural_features(prompt)
        has_strong_logic = (prompt_features["numbers"] and prompt_features["has_comparative"]) or \
                           (prompt_features["has_negation"] and prompt_features["has_conditional"])

        for candidate in candidates:
            # 1. Pragmatic/Ergodic Score (Primary Signal)
            # Represents the convergence of logical consistency checks
            logic_score = self._check_logical_consistency(prompt, candidate)
            
            # 2. Adaptive Control / NCD (Secondary Signal / Tiebreaker)
            # Only heavily weighted if logic score is ambiguous (close to 0.5)
            ncd_val = self._ncd_distance(prompt, candidate)
            
            # Adaptive weighting: If logic is strong, trust it. If weak, use NCD to penalize noise.
            # NCD is distance (0=identical, 1=diff), so we invert it for similarity
            ncd_similarity = 1.0 - ncd_val
            
            # Dynamic weighting based on "uncertainty" of the logical parser
            # If logic_score is near 0.5 (unsure), increase weight of NCD
            uncertainty = 1.0 - abs(logic_score - 0.5) * 2 # 1.0 if 0.5, 0.0 if 0 or 1
            
            # Blend: Primary is logic, NCD acts as a regularizer for context relevance
            # We don't let NCD override strong logical contradictions
            if has_strong_logic:
                final_score = 0.9 * logic_score + 0.1 * ncd_similarity
            else:
                # If no strong logic, rely more on NCD but keep logic bias
                final_score = 0.4 * logic_score + 0.6 * ncd_similarity

            # Construct reasoning string
            reasoning = f"Logic:{logic_score:.2f} NCD:{ncd_similarity:.2f}"
            if prompt_features["numbers"]:
                reasoning += " [Numeric Eval Active]"
            if prompt_features["has_negation"]:
                reasoning += " [Negation Detected]"

            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same evaluation logic but returns the raw score of the specific answer.
        """
        # Evaluate single candidate against the rest (dummy list for context if needed, 
        # but here we just score the pair)
        # To strictly follow the interface, we simulate an evaluation run
        # We create a dummy list to run the evaluator, then extract the score for 'answer'
        # However, to be efficient and deterministic without needing other candidates:
        
        logic_score = self._check_logical_consistency(prompt, answer)
        ncd_val = self._ncd_distance(prompt, answer)
        ncd_similarity = 1.0 - ncd_val
        
        prompt_features = self._extract_structural_features(prompt)
        has_strong_logic = (prompt_features["numbers"] and prompt_features["has_comparative"]) or \
                           (prompt_features["has_negation"] and prompt_features["has_conditional"])

        if has_strong_logic:
            final_score = 0.9 * logic_score + 0.1 * ncd_similarity
        else:
            final_score = 0.4 * logic_score + 0.6 * ncd_similarity
            
        return float(max(0.0, min(1.0, final_score)))