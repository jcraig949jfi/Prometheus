import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Categorical-Wavelet Error-Correcting Inference Engine (Approximated).
    
    Mechanism:
    1. Functorial Mapping (W): Treats text as a signal. Extracts structural features
       (negations, comparatives, conditionals, numbers) as the 'coefficients' of the hypothesis.
    2. Natural Transformation (eta): Applies error-correcting logic. Checks consistency between
       the prompt's constraints and the candidate's structural signature.
       - Detects contradictions (e.g., Prompt says "not X", Candidate implies "X").
       - Detects numeric inconsistencies.
    3. Syndrome Decoding: Computes a 'syndrome' score based on constraint violations.
       Low syndrome = high consistency.
    4. Reconstruction: Combines the structural consistency score with NCD (as a tiebreaker)
       to produce a final confidence metric.
       
    This implements the 'self-testing' capability by explicitly checking for logical 
    negations and numeric transitivity before measuring similarity.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Wavelet Basis")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|otherwise)\b', re.I),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'boolean_yes': re.compile(r'\b(yes|true|correct|affirmative)\b', re.I),
            'boolean_no': re.compile(r'\b(no|false|incorrect|negative)\b', re.I)
        }

    def _extract_features(self, text: str) -> Dict:
        """Extracts structural coefficients from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(n) for n in self.patterns['number'].findall(text)],
            'affirms': bool(self.patterns['boolean_yes'].search(text)),
            'denies': bool(self.patterns['boolean_no'].search(text))
        }
        return features

    def _compute_syndrome(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Computes the 'syndrome' (error signal) based on logical consistency.
        Returns 0.0 for perfect consistency, positive values for errors.
        """
        syndrome = 0.0
        
        # 1. Negation Consistency Check
        # If prompt strongly negates, candidate should not affirm (unless context implies correction)
        # Simple heuristic: If prompt has negation and candidate is a bare affirmation without nuance
        if prompt_feats['has_negation'] and cand_feats['affirms'] and not cand_feats['has_negation']:
            # Check if candidate is just "Yes" or similar short affirmation
            if len(candidate.strip().split()) <= 2:
                syndrome += 0.4
        
        # 2. Numeric Consistency Check (Transitivity/Magnitude)
        # If prompt contains numbers and candidate contains numbers, check rough alignment
        if prompt_feats['numbers'] and cand_feats['numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            
            # Heuristic: If prompt asks for "less than X" and candidate is > X
            # Detect "less" or "smaller" in prompt
            if 'less' in prompt.lower() or 'smaller' in prompt.lower() or 'under' in prompt.lower():
                threshold = min(p_nums) # Rough approximation of target bound
                if any(c > threshold for c in c_nums):
                    syndrome += 0.5
            
            # Detect "more" or "greater"
            if 'more' in prompt.lower() or 'greater' in prompt.lower() or 'over' in prompt.lower():
                threshold = max(p_nums)
                if any(c < threshold for c in c_nums):
                    syndrome += 0.5

        # 3. Conditional Logic Check
        # If prompt is conditional, candidate shouldn't be an absolute unconditional fact
        if prompt_feats['has_conditional'] and not cand_feats['has_conditional']:
            # Penalize absolute statements if prompt is hypothetical
            if cand_feats['affirms'] and not cand_feats['has_negation']:
                syndrome += 0.1

        return syndrome

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
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
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Baseline NCD for tie-breaking
        # We compare candidate to prompt + "correct" vs prompt + "incorrect" to gauge semantic drift
        # But per instructions, NCD is secondary.
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural/Syndrome Score (Primary Signal)
            syndrome = self._compute_syndrome(prompt_feats, cand_feats, prompt, cand)
            
            # Base score starts high, reduced by syndrome
            # Logic: If syndrome is high, the candidate violates structural constraints
            structural_score = max(0.0, 1.0 - syndrome)
            
            # 2. NCD Tiebreaker (Secondary Signal)
            # Calculate similarity to prompt. 
            # Note: Pure NCD is weak, so we weight it lightly (10%) unless structural is ambiguous
            ncd_val = self._ncd(prompt, cand)
            # Convert distance to similarity (1 - distance)
            ncd_similarity = 1.0 - min(1.0, ncd_val)
            
            # Final Score: Structural dominance (90%) + NCD (10%)
            final_score = (structural_score * 0.9) + (ncd_similarity * 0.1)
            
            # Reasoning string generation
            reasoning_parts = []
            if syndrome > 0.3:
                reasoning_parts.append("High syndrome: Logical inconsistency detected.")
            if prompt_feats['has_negation'] and cand_feats['affirms']:
                reasoning_parts.append("Potential negation mismatch.")
            if not reasoning_parts:
                reasoning_parts.append("Structurally consistent with prompt constraints.")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluate logic internally for a single candidate.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']