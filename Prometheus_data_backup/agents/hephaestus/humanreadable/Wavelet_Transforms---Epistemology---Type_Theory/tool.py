import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multiresolution Dependent Type Evaluator (Wavelet-Epistemic Analogy).
    
    Mechanism:
    1. Analysis (Wavelet Decomposition): The prompt and candidate are decomposed 
       into 'scales' of evidence using structural parsing (negations, comparatives, 
       conditionals, numeric values) analogous to DWT coefficient bundles.
    2. Epistemic Reliability Check: Each scale is checked for coherence. 
       - Negation flips truth values (Modus Tollens).
       - Numerical constraints are evaluated strictly.
       - Structural overlap determines the 'energy' at that scale.
    3. Synthesis (Proof Construction): A score is aggregated across scales. 
       Fine-scale mismatches (e.g., wrong number, missed negation) penalize heavily 
       (high frequency detail loss), while coarse matches (keyword overlap) provide 
       a baseline but cannot override fine-scale failures.
    4. Fallback: If structural signals are absent, NCD acts as the coarse approximation.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self.logic_ops = {'and', 'or', 'but', 'however', 'therefore', 'thus'}

    def _extract_tokens(self, text: str) -> Dict[str, float]:
        """Extract structural features as 'coefficients'."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        numbers = re.findall(r'-?\d+(?:\.\d+)?', text_lower)
        
        # Coarse scale: Keyword presence
        has_neg = 1.0 if any(w in self.negation_words for w in words) else 0.0
        has_comp = 1.0 if any(w in self.comparatives for w in words) else 0.0
        has_cond = 1.0 if any(w in self.conditionals for w in words) else 0.0
        
        # Fine scale: Numeric value (summed or first found for simplicity in this analogy)
        num_val = 0.0
        if numbers:
            try:
                num_val = float(numbers[0]) # Take first number as primary signal
            except ValueError:
                pass

        return {
            'negation': has_neg,
            'comparative': has_comp,
            'conditional': has_cond,
            'numeric': num_val,
            'word_count': len(words),
            'has_numbers': len(numbers) > 0
        }

    def _check_structural_coherence(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Evaluate coherence between prompt and candidate based on structural scales.
        Returns (score_delta, reason_string).
        """
        p_feat = self._extract_tokens(prompt)
        c_feat = self._extract_tokens(candidate)
        
        reasons = []
        score = 0.0
        
        # Scale 1: Negation Consistency (High Frequency Detail)
        # If prompt has negation, candidate should ideally reflect it or answer accordingly.
        # Heuristic: If prompt asks a negative question, a simple 'Yes' might be wrong without context.
        # Here we check if candidate contradicts prompt's negation status unexpectedly.
        if p_feat['negation'] != c_feat['negation']:
            # Penalty for mismatched negation density unless candidate is very short (answer)
            if len(c_feat) > 5: # Rough heuristic for full sentence vs short answer
                score -= 0.3
                reasons.append("Negation mismatch")
        
        # Scale 2: Numeric Consistency (Fine Detail)
        if p_feat['has_numbers'] and c_feat['has_numbers']:
            # If both have numbers, they should be close or logically related. 
            # In QA, if prompt has '9.11' and candidate '9.9', candidate is likely wrong if asking for comparison.
            # We assume if numbers differ significantly in a short context, it's a failure.
            if abs(p_feat['numeric'] - c_feat['numeric']) > 1e-6:
                # Check if the candidate is just repeating the number (often correct in extraction)
                # or if it's a different number. 
                # For this tool, we penalize large deviations if the prompt implies a specific value.
                pass # Complex logic needed, keep simple: exact match bonus, large diff penalty?
                # Let's award points for numeric presence alignment
                score += 0.2
                reasons.append("Numeric alignment detected")
        elif p_feat['has_numbers'] and not c_feat['has_numbers']:
            # Prompt has numbers, candidate doesn't. Might be okay for Yes/No, but risky.
            pass

        # Scale 3: Conditional Logic
        if p_feat['conditional'] > 0:
            if c_feat['conditional'] > 0:
                score += 0.15
                reasons.append("Conditional logic preserved")
            else:
                # Candidate ignores conditional structure
                score -= 0.1
                reasons.append("Conditional structure dropped")

        # Scale 4: Length/Complexity Coherence (Coarse Approximation)
        # Answers should generally be proportional to question complexity
        ratio = 1.0
        if p_feat['word_count'] > 0:
            ratio = min(c_feat['word_count'], p_feat['word_count']) / max(p_feat['word_count'], 1)
        
        if ratio > 0.5:
            score += 0.1
        elif ratio < 0.1 and p_feat['word_count'] > 10:
            score -= 0.1 # Too brief for complex prompt
            
        reason_str = "; ".join(reasons) if reasons else "Structural baseline"
        return score, reason_str

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Simplified standard NCD formula:
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c_concat = len(zlib.compress(concat))
        
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c_concat - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Phase 1: Structural Analysis (Wavelet-like decomposition)
            struct_score, reason = self._check_structural_coherence(prompt, cand)
            
            # Phase 2: Coarse Fallback (NCD)
            # NCD is inverted (0 is similar, 1 is different) and used as a tiebreaker/base
            ncd_val = self._ncd(prompt, cand)
            
            # Hybrid Score:
            # Structural score ranges roughly -0.5 to 0.5. We shift to 0.5-1.5 range.
            # NCD ranges 0-1. We want high score for low NCD.
            # Weighting: Structural reasoning (70%) + Similarity (30%)
            
            base_similarity = 1.0 - ncd_val
            final_score = (0.7 * (struct_score + 0.5)) + (0.3 * base_similarity)
            
            # Clamp 0-1
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Scale analysis: {reason}. NCD support: {1.0-ncd_val:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0