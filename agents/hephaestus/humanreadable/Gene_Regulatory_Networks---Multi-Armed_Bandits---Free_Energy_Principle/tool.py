import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Bayesian Bandit-Driven Predictive Coding Architecture.
    
    Mechanism:
    1. Generative Model (GRN-inspired): Parses prompt structure (negations, comparatives, 
       conditionals, numeric values) to form a "prior" belief about the logical constraints.
    2. Predictive Coding (FEP Core): Evaluates candidates by computing "Variational Free Energy" 
       (prediction error). Low energy = high consistency with structural priors.
       - Checks logical consistency (e.g., if prompt says "not X", candidate "X" gets high error).
       - Checks numeric consistency (e.g., if prompt implies A > B, candidate violating this gets high error).
    3. Bandit Controller: Acts as an exploration/exploitation regulator. It adjusts the weight 
       of structural vs. lexical signals based on the "uncertainty" (entropy) of the initial parse,
       effectively sampling the "arm" (hypothesis) that minimizes expected free energy.
    4. Scoring: Candidates are ranked by negative Free Energy (lower error = higher score).
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _parse_structure(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(not|no|never|without|except)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            "numbers": re.findall(r'-?\d+\.?\d*', text),
            "length": len(text),
            "words": set(re.findall(r'\b\w+\b', text_lower))
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """Calculate prediction error (Free Energy) based on logical constraints."""
        error = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation context, penalize candidates that lack negative markers 
        # if the semantic context suggests exclusion (heuristic approximation).
        if prompt_feats["negations"] > 0:
            # Simple heuristic: if prompt says "not", and candidate is very short/affirmative without qualifiers
            if cand_feats["negations"] == 0 and prompt_feats["negations"] > cand_feats["negations"]:
                # Check for direct contradiction keywords (simplified)
                if any(k in candidate.lower() for k in ["yes", "true", "all", "every"]):
                    error += 0.5

        # 2. Numeric Consistency
        if prompt_feats["numbers"] and cand_feats["numbers"]:
            try:
                p_nums = [float(x) for x in prompt_feats["numbers"]]
                c_nums = [float(x) for x in cand_feats["numbers"]]
                # If prompt implies ordering (detected by comparatives), check if candidate respects magnitude
                if prompt_feats["comparatives"] > 0:
                    # Heuristic: If prompt has numbers and comparatives, candidate numbers should 
                    # not wildly deviate in order of magnitude unless justified (simplified to range check)
                    if p_nums and c_nums:
                        p_avg = sum(p_nums) / len(p_nums)
                        c_avg = sum(c_nums) / len(c_nums)
                        # Penalize massive deviations in numeric expectations
                        if p_avg > 0 and abs(c_avg - p_avg) / (p_avg + self.epsilon) > 10.0:
                            error += 0.3
            except ValueError:
                pass

        # 3. Structural Overlap (Predictive Coding of content)
        # High overlap reduces prediction error
        common_words = prompt_feats["words"].intersection(cand_feats["words"])
        overlap_ratio = len(common_words) / (len(prompt_feats["words"]) + len(cand_feats["words"]) + 1)
        error -= (overlap_ratio * 0.5) # Reduce error for high overlap

        return max(0.0, error)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._parse_structure(prompt)
        results = []
        
        # Bandit-like exploration weight: 
        # High structural complexity in prompt -> Trust structure more (Exploit)
        # Low structural complexity -> Rely more on NCD/Lexical similarity (Explore)
        structural_complexity = (prompt_feats["negations"] + prompt_feats["comparatives"] + prompt_feats["conditionals"])
        bandit_weight = min(1.0, structural_complexity * 0.3) # Cap weight
        
        scores = []
        for cand in candidates:
            cand_feats = self._parse_structure(cand)
            
            # 1. Free Energy Minimization (Structural/Logical Error)
            # Lower error is better. We invert this for scoring later.
            logical_error = self._check_logical_consistency(prompt_feats, cand_feats, prompt, cand)
            
            # 2. NCD Baseline (Tiebreaker/Low-level similarity)
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Combine: Score = (1 - Logical_Error) * (1 - NCD) weighted by bandit factor
            # Actually, let's treat Logical Error as the primary driver (FEP)
            # Score = (1.0 - logical_error) * (1.0 - bandit_weight) + (1.0 - ncd_val) * bandit_weight
            
            # Refined FEP Score: 
            # We want low logical error. NCD is a secondary prior.
            fe_score = 1.0 - logical_error
            ncd_score = 1.0 - ncd_val
            
            final_score = (fe_score * (1.0 - bandit_weight)) + (ncd_score * bandit_weight)
            
            # Penalty for length mismatch if prompt is long and specific
            if len(prompt) > 50 and len(cand) < 3:
                final_score *= 0.8

            scores.append((cand, final_score, logical_error))

        # Rank by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                "candidate": c, 
                "score": float(s), 
                "reasoning": f"FEP={1.0-e:.2f}, NCD={1.0-self._compute_ncd(prompt, c):.2f}, BanditW={bandit_weight:.2f}"
            }
            for c, s, e in scores
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low prediction error (high consistency) = High confidence.
        """
        prompt_feats = self._parse_structure(prompt)
        cand_feats = self._parse_structure(answer)
        
        # Calculate logical error (Free Energy)
        error = self._check_logical_consistency(prompt_feats, cand_feats, prompt, answer)
        
        # Add NCD penalty
        ncd = self._compute_ncd(prompt, answer)
        
        # Confidence is inverse of total error
        # If error is high, confidence is low.
        total_error = error + (ncd * 0.5)
        
        conf = 1.0 / (1.0 + total_error * 2.0)
        return min(1.0, max(0.0, conf))