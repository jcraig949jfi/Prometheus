import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A self-tuning hierarchical generative model approximation using predictive coding
    and neuromodulatory gain control for reasoning tasks.
    
    Mechanism:
    1. Generative Model (Differentiable Programming): Uses structural parsing rules
       to predict the logical validity of candidates based on the prompt.
    2. Predictive Coding: Computes prediction errors between prompt constraints
       and candidate properties (negations, numbers, conditionals).
    3. Neuromodulation: Dynamically adjusts the 'precision' (gain) of specific
       reasoning pathways (numeric, logical, lexical) based on the variance of
       prediction errors in the current context, mimicking dopaminergic modulation.
    
    This creates a feedback loop where high-surprise features (e.g., detected numbers)
    receive higher gain, forcing the system to prioritize numeric consistency over
    simple string similarity (NCD).
    """

    def __init__(self):
        # State variables for neuromodulatory gains (initialized to neutral)
        # Represents the 'precision' weighting for different reasoning modalities
        self.gain_numeric = 1.0
        self.gain_logical = 1.0
        self.gain_lexical = 0.5  # Lower base priority for pure string match
        
        # Running statistics for meta-learning (simulated via simple moving average)
        self.error_mean = 0.0
        self.error_var = 0.0

    def _extract_features(self, text: str) -> dict:
        """Extract structural features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        
        # Numeric detection
        numbers = re.findall(r"-?\d+\.?\d*", text_lower)
        nums = [float(n) for n in numbers] if numbers else []
        
        # Logical operators
        has_negation = any(w in text_lower for w in ['not', 'no ', 'never', 'false', 'impossible'])
        has_conditional = any(w in text_lower for w in ['if', 'then', 'unless', 'otherwise'])
        has_comparative = any(w in text_lower for w in ['greater', 'less', 'more', 'fewer', '>', '<', 'higher', 'lower'])
        
        # Subject/Object heuristic (simple word count proxy for complexity)
        word_count = len(text.split())
        
        return {
            'numbers': nums,
            'has_negation': has_negation,
            'has_conditional': has_conditional,
            'has_comparative': has_comparative,
            'word_count': word_count,
            'raw': text_lower
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a baseline tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Normalized to 0-1 where 0 is identical
        numerator = len_combined - min(len_s1, len_s2)
        denominator = max(len_s1, len_s2)
        
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def _update_gains(self, errors: List[float]):
        """
        Neuromodulatory update rule.
        Adjusts gains based on the variance of recent prediction errors.
        High variance -> High surprise -> Increase gain on specific pathways to focus learning.
        """
        if not errors:
            return
            
        # Calculate statistics
        mean_err = sum(errors) / len(errors)
        variance = sum((e - mean_err) ** 2 for e in errors) / len(errors) if len(errors) > 1 else 0.0
        
        # Meta-learning update (simplified gradient step on gain)
        # If variance is high, we need to trust our specialized modules more (increase gain)
        # If variance is low, we can rely more on defaults
        sensitivity = 0.1
        self.gain_numeric = max(0.1, self.gain_numeric + sensitivity * (variance - self.error_var))
        self.gain_logical = max(0.1, self.gain_logical + sensitivity * (variance - self.error_var))
        
        # Update running stats for next iteration
        self.error_mean = mean_err
        self.error_var = variance

    def _compute_prediction_error(self, prompt_feat: dict, cand_feat: dict) -> float:
        """
        Compute the 'prediction error' between prompt expectations and candidate reality.
        Lower error = higher consistency.
        """
        error = 0.0
        
        # 1. Numeric Consistency Check (High Precision required)
        if prompt_feat['numbers'] and cand_feat['numbers']:
            # Check if candidate numbers logically follow prompt numbers (simplified)
            # E.g., if prompt has "2" and "3", candidate having "5" might be expected in sum tasks
            # Here we just check magnitude consistency for comparatives
            if prompt_feat['has_comparative']:
                p_max = max(prompt_feat['numbers'])
                c_max = max(cand_feat['numbers']) if cand_feat['numbers'] else 0
                # If prompt implies comparison, large deviation in candidate numbers is an error
                if abs(p_max - c_max) > 10: 
                    error += 2.0 * self.gain_numeric
            else:
                # Exact match preference for non-comparative numeric contexts
                if set(prompt_feat['numbers']) != set(cand_feat['numbers']):
                    error += 1.5 * self.gain_numeric

        # 2. Logical Consistency (Negation/Conditional)
        if prompt_feat['has_negation']:
            # If prompt has negation, candidate should ideally reflect it or be short (Yes/No)
            if not cand_feat['has_negation'] and cand_feat['word_count'] > 10:
                error += 1.0 * self.gain_logical
                
        if prompt_feat['has_conditional']:
            if not cand_feat['has_conditional'] and cand_feat['word_count'] > 5:
                # Conditional prompts often require conditional answers or specific logic
                error += 0.5 * self.gain_logical

        # 3. Lexical Overlap (Baseline)
        # Simple Jaccard-like penalty for low overlap
        p_words = set(prompt_feat['raw'].split())
        c_words = set(cand_feat['raw'].split())
        if p_words:
            overlap = len(p_words.intersection(c_words)) / len(p_words)
            error += (1.0 - overlap) * 0.2 # Low weight baseline
            
        return error

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_features(prompt)
        results = []
        errors = []

        # First pass: Compute raw errors to update neuromodulatory gains
        for cand in candidates:
            cand_feat = self._extract_features(cand)
            err = self._compute_prediction_error(prompt_feat, cand_feat)
            errors.append(err)
        
        # Update internal state (Meta-learning step)
        self._update_gains(errors)

        # Second pass: Generate scores using updated gains
        for i, cand in enumerate(candidates):
            cand_feat = self._extract_features(cand)
            err = self._compute_prediction_error(prompt_feat, cand_feat)
            
            # Convert error to score (inverse relationship)
            # Base score from error
            score = 1.0 / (1.0 + err)
            
            # Tiebreaker: NCD (only if structural signals are weak)
            if err < 0.5: # If structural error is low, use NCD to refine
                ncd = self._compute_ncd(prompt, cand)
                # NCD is distance (0=identical), we want similarity
                # But for reasoning, identical is bad (tautology), so we balance
                # We use NCD primarily to distinguish between similar logical structures
                score += (1.0 - ncd) * 0.05 

            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"Structural consistency error: {err:.2f}, Adjusted by gain (Num:{self.gain_numeric:.2f}, Log:{self.gain_logical:.2f})"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the prediction error of the single answer.
        """
        prompt_feat = self._extract_features(prompt)
        cand_feat = self._extract_features(answer)
        
        err = self._compute_prediction_error(prompt_feat, cand_feat)
        
        # Map error to confidence: Low error -> High confidence
        # Using a steeper decay for confidence to be conservative
        conf = 1.0 / (1.0 + (err * 1.5))
        
        # Boost if structural features align perfectly
        if prompt_feat['has_negation'] == cand_feat['has_negation']:
            conf = min(1.0, conf + 0.1)
        if prompt_feat['has_conditional'] == cand_feat['has_conditional']:
            conf = min(1.0, conf + 0.1)
            
        return round(min(1.0, max(0.0, conf)), 4)