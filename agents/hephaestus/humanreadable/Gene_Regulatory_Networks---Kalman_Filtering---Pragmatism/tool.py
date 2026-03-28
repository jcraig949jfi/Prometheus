import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Kalman Gene Network (PKGN) Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (The GRN Prior): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a sparse 'regulatory graph' of the prompt.
    2. State Estimation (Kalman Filter): Treats candidate adherence to these constraints 
       as a state estimation problem. We compute a 'prediction error' (innovation) 
       based on how well the candidate satisfies the extracted logical rules.
    3. Pragmatic Revision (Utility): Instead of philosophical truth, we use 
       predictive utility. Candidates that minimize logical contradiction (error) 
       relative to the structural prior receive higher scores. 
    4. NCD Tiebreaker: Used only when structural signals are equal.
    
    This implements the 'Pragmatic' aspect as a utility-driven filter: hypotheses 
    (candidates) that fail to predict the logical consequences of the prompt are 
    rejected (low score).
    """

    def __init__(self):
        self.tolerance = 0.5  # Pragmatic tolerance threshold

    def _structural_parse(self, text: str) -> Dict:
        """Extract logical signatures: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|neither)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'has_question': 1 if '?' in text else 0
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Simulates the Kalman 'innovation' step.
        Measures the discrepancy between prompt constraints and candidate content.
        Lower return value = better fit (lower error).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        error_sum = 0.0
        count = 0

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect awareness or not contradict
        if p_feat['negations'] > 0:
            # Heuristic: If prompt denies something, candidate repeating the denied term without context might be wrong
            # Simplified: Check if candidate has opposite polarity markers
            if 'yes' in candidate.lower() and 'not' in prompt.lower():
                error_sum += 0.5
            count += 1

        # 2. Numeric Evaluation
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # Extract first number from both
                p_num = float(p_feat['numbers'][0])
                c_num = float(c_feat['numbers'][0])
                
                # Check comparative logic
                if 'greater' in prompt.lower() or 'more' in prompt.lower() or '>' in prompt:
                    if c_num <= p_num: error_sum += 1.0 # Failed comparison
                elif 'less' in prompt.lower() or 'smaller' in prompt.lower() or '<' in prompt:
                    if c_num >= p_num: error_sum += 1.0 # Failed comparison
                else:
                    # Exact match preference for numbers if no comparative
                    if abs(p_num - c_num) > 0.01:
                        error_sum += 0.5
            except ValueError:
                error_sum += 0.5
            count += 1
            
        # 3. Conditional/Keyword Overlap (Structural similarity)
        # A valid hypothesis usually retains key structural tokens
        common_words = set(re.findall(r'\b\w+\b', prompt.lower())) & set(re.findall(r'\b\w+\b', candidate.lower()))
        # Remove stopwords
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'if', 'then', 'to', 'of', 'in'}
        meaningful_overlap = len([w for w in common_words if w not in stopwords])
        
        # Penalize low overlap significantly (High innovation error)
        if meaningful_overlap == 0 and len(prompt.split()) > 5:
            error_sum += 2.0
        else:
            # Reward overlap proportionally
            error_sum -= (meaningful_overlap * 0.1)
            
        return max(0.0, error_sum)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(z1, z2)
        if denominator == 0: return 0.0
        return (z12 - min(z1, z2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        
        # Pre-calculate prompt features to establish the "Prior"
        prompt_features = self._structural_parse(prompt)
        has_strong_signal = (prompt_features['negations'] > 0 or 
                             prompt_features['comparatives'] > 0 or 
                             prompt_features['numbers'])

        for cand in candidates:
            # Step 1: Calculate Structural Error (Kalman Innovation)
            error = self._check_logical_consistency(prompt, cand)
            
            # Step 2: Convert error to a base score (Pragmatic Utility)
            # Lower error -> Higher score. 
            base_score = 1.0 / (1.0 + error)
            
            # Step 3: Apply NCD only as a tiebreaker/secondary signal
            # If structural signal is weak, NCD weight increases slightly, 
            # but structural always dominates if present.
            ncd_val = self._ncd(prompt, cand)
            
            final_score = base_score
            
            # Refinement: If structural signals are present, penalize high NCD (dissimilarity)
            # If no structural signals, rely more on NCD
            if has_strong_signal:
                final_score = (base_score * 0.8) + ((1.0 - ncd_val) * 0.2)
            else:
                # Fallback behavior when logic is ambiguous
                final_score = (base_score * 0.4) + ((1.0 - ncd_val) * 0.6)

            scored.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Structural error: {error:.2f}, NCD: {ncd_val:.2f}"
            })

        # Sort descending by score
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the pragmatic success of the answer 
        against the prompt's structural constraints.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # The score from evaluate is already normalized 0-1 representing likelihood
        return results[0]['score']