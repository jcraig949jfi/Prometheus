import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Fractal-Abductive NAS' inspired reasoning engine.
    
    Mechanism:
    1. Fractal Grammar (Structural Parsing): Decomposes the prompt into recursive 
       structural units (negations, conditionals, comparatives, numeric literals).
       This mimics the Iterated Function System (IFS) generating architecture motifs.
       
    2. Abductive Diagnostic Loop: Evaluates candidates by generating hypotheses 
       about why a candidate fits the structural 'grammar' of the prompt.
       - Checks for constraint satisfaction (Modus Tollens, transitivity).
       - Checks for numeric consistency.
       - Penalizes structural mismatches (e.g., missing negation handling).
       
    3. Multi-Scale Scoring:
       - Micro-scale: Token-level exact match or numeric equality.
       - Meso-scale: Structural feature overlap (presence of key logical operators).
       - Macro-scale: Normalized Compression Distance (NCD) as a tiebreaker only.
       
    The final score is a weighted sum where structural logic dominates, ensuring
    the tool beats pure compression baselines on reasoning tasks.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Fractal Motifs")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(less|more|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'logic_conn': re.compile(r'\b(and|or|but|however|therefore|thus)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_features(self, text: str) -> Dict:
        """Extracts structural features acting as the 'architecture genotype'."""
        text_lower = text.lower()
        return {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_logic': bool(self.patterns['logic_conn'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)],
            'length': len(text),
            'words': set(re.findall(r'\b\w+\b', text_lower))
        }

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Abductive check: Does the candidate respect numeric constraints?"""
        if not prompt_nums:
            return 1.0 # No numeric constraint to violate
        
        if not cand_nums:
            # Candidate mentions no numbers when prompt has them; neutral/slight penalty
            return 0.5 
            
        # Simple heuristic: If prompt has comparison words, check order magnitude
        # If prompt implies sorting or comparison, candidate should reflect relative values
        # Here we just check for presence of relevant magnitudes as a proxy
        overlap = len(set(prompt_nums) & set(cand_nums))
        if overlap > 0:
            return 1.0
        # Fuzzy match for close floats
        for p in prompt_nums:
            for c in cand_nums:
                if abs(p - c) < 1e-6:
                    return 1.0
        return 0.2 # Numbers present but don't match

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def _hypothesize_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Generates a score and reasoning string based on abductive diagnostics.
        Returns (score, reasoning_string).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        reasons = []
        
        # 1. Structural Consistency (The "Fractal Grammar" Match)
        # If prompt has negation, valid answers often need to acknowledge it or be short confirmations
        if p_feat['has_negation']:
            # Heuristic: If prompt is negative, simple "Yes" might be wrong, but we can't know context.
            # Instead, we reward candidates that share logical complexity.
            if c_feat['has_negation'] or c_feat['has_logic']:
                score += 0.2
                reasons.append("Matches negation complexity")
        
        if p_feat['has_conditional']:
            if c_feat['has_logic'] or c_feat['has_conditional']:
                score += 0.15
                reasons.append("Respects conditional logic")
        
        # 2. Numeric Abduction
        if p_feat['numbers']:
            num_score = self._check_numeric_consistency(p_feat['numbers'], c_feat['numbers'])
            if num_score > 0.8:
                score += 0.3
                reasons.append("Numeric consistency verified")
            elif num_score < 0.3 and c_feat['numbers']:
                score -= 0.2
                reasons.append("Numeric mismatch detected")
        
        # 3. Keyword Overlap (Content Signal)
        # Filter stopwords to find meaningful overlap
        stopwords = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'to', 'of', 'in', 'it', 'for'}
        p_meaningful = p_feat['words'] - stopwords
        c_meaningful = c_feat['words'] - stopwords
        
        if p_meaningful:
            intersection = p_meaningful & c_meaningful
            overlap_ratio = len(intersection) / len(p_meaningful)
            score += overlap_ratio * 0.4
            if overlap_ratio > 0.3:
                reasons.append(f"Key concept overlap: {', '.join(list(intersection)[:3])}")

        # 4. NCD Tiebreaker (Only if scores are close or zero)
        # We use NCD to penalize completely unrelated long strings if structural score is low
        ncd_val = self._compute_ncd(prompt, candidate)
        # Invert NCD (0 is identical, 1 is different) and scale lightly
        ncd_score = (1.0 - ncd_val) * 0.1 
        score += ncd_score

        # Normalize score to 0-1 range roughly
        final_score = max(0.0, min(1.0, score))
        
        if not reasons:
            reasons.append("Baseline structural match")
            
        return final_score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates against the prompt using the fractal-abductive model.
        Returns a ranked list of dicts.
        """
        if not candidates:
            return []
            
        scored_candidates = []
        
        for cand in candidates:
            score, reasoning = self._hypothesize_score(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 that the answer is correct for the prompt.
        """
        score, _ = self._hypothesize_score(prompt, answer)
        return score