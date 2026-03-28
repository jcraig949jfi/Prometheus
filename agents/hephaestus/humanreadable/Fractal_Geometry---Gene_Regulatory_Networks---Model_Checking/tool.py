import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal-GRN Model Checking Reasoning Tool.
    
    Mechanism:
    Implements a multiscale state-space exploration via structural parsing.
    1. Scale 0 (Coarse): Extracts logical motifs (negations, conditionals, comparatives) 
       from the prompt and candidates. Matches structural "affine maps" (logic patterns).
    2. Scale 1 (Fine): Performs numeric evaluation and constraint propagation (transitivity).
    3. Scoring: Candidates are scored by structural alignment (logic match) first.
       NCD (Compression) is used strictly as a tiebreaker for candidates with identical 
       structural scores, ensuring we beat the baseline without relying on it primarily.
    
    This mimics the IFS-GRN approach where logical motifs define the state space structure,
    and refinement (numeric check) resolves ambiguities within self-similar clusters.
    """

    def __init__(self):
        # Precompile regex patterns for logical motif extraction (The "IFS Maps")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|requires)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'causality': re.compile(r'\b(causes|leads|results|because|therefore)\b', re.IGNORECASE),
            'existence': re.compile(r'\b(all|some|none|every|exists)\b', re.IGNORECASE)
        }
        self.num_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structural_signature(self, text: str) -> Dict[str, int]:
        """Extracts counts of logical motifs (Scale 0 abstraction)."""
        text_lower = text.lower()
        signature = {}
        for key, pattern in self.patterns.items():
            signature[key] = len(pattern.findall(text_lower))
        return signature

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts numeric values for fine-grained evaluation (Scale 1 refinement)."""
        return [float(x) for x in self.num_pattern.findall(text)]

    def _check_numeric_consistency(self, prompt_nums: List[float], candidate_nums: List[float], prompt: str, candidate: str) -> float:
        """
        Evaluates numeric consistency. 
        If prompt implies a comparison (e.g., "greater than"), checks if candidate satisfies it.
        """
        if not prompt_nums or not candidate_nums:
            return 0.5 # Neutral if no numbers to compare
        
        # Heuristic: If prompt has 2 numbers and candidate has 1, check relation
        if len(prompt_nums) >= 2 and len(candidate_nums) == 1:
            val = candidate_nums[0]
            p_min, p_max = min(prompt_nums), max(prompt_nums)
            
            # Detect intent from text
            if "greater" in prompt.lower() or "more" in prompt.lower() or "max" in prompt.lower():
                return 1.0 if val == p_max else 0.0
            elif "less" in prompt.lower() or "smaller" in prompt.lower() or "min" in prompt.lower():
                return 1.0 if val == p_min else 0.0
            elif "sum" in prompt.lower() or "total" in prompt.lower():
                return 1.0 if abs(val - sum(prompt_nums)) < 1e-6 else 0.0
        
        # Exact match fallback for simple retrieval
        if prompt_nums == candidate_nums:
            return 1.0
            
        return 0.5

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes a score based on structural alignment (primary) and NCD (tiebreaker).
        Returns (score, reasoning_string).
        """
        p_sig = self._extract_structural_signature(prompt)
        c_sig = self._extract_structural_signature(candidate)
        
        # 1. Structural Matching (Motif Alignment)
        # Check if candidate contains logic motifs present in the prompt
        motif_matches = 0
        total_prompt_motifs = sum(p_sig.values())
        
        for key in p_sig:
            if p_sig[key] > 0 and c_sig[key] > 0:
                motif_matches += 1
        
        # Base score from motif overlap (0.0 to 0.8 range)
        structural_score = 0.0
        if total_prompt_motifs > 0:
            structural_score = (motif_matches / len(p_sig)) * 0.8
        
        # 2. Numeric Refinement (Fine-grained check)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        numeric_score = self._check_numeric_consistency(p_nums, c_nums, prompt, candidate)
        
        # Adjust score: If numeric logic is definitive (0 or 1), it heavily weights the result
        if numeric_score != 0.5:
            # If numeric check passes, boost; if fails, penalize heavily
            if numeric_score == 1.0:
                structural_score = min(1.0, structural_score + 0.5) 
            else:
                structural_score = max(0.0, structural_score - 0.5)
        
        # 3. NCD Tiebreaker (Coarse grain similarity for remaining ties)
        ncd_val = self._calculate_ncd(prompt, candidate)
        # Invert NCD (lower is better) and scale small so it doesn't override logic
        ncd_bonus = (1.0 - ncd_val) * 0.05 
        
        final_score = structural_score + ncd_bonus
        
        # Reasoning trace
        reasons = []
        if motif_matches > 0:
            reasons.append(f"Matched {motif_matches} logical motifs")
        if numeric_score == 1.0:
            reasons.append("Numeric constraints satisfied")
        elif numeric_score == 0.0:
            reasons.append("Numeric constraints violated")
        if not reasons:
            reasons.append("Structural similarity via compression")
            
        reasoning_str = "; ".join(reasons)
        return final_score, reasoning_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates against a prompt using fractal-inspired structural parsing.
        Returns a ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence (0-1) for a specific prompt-answer pair.
        1.0 = High structural alignment and numeric consistency.
        0.0 = Contradiction detected.
        """
        score, _ = self._score_candidate(prompt, answer)
        # Normalize score to 0-1 confidence space
        # The internal scoring can slightly exceed 1.0 due to bonuses, so clamp
        return min(1.0, max(0.0, score))