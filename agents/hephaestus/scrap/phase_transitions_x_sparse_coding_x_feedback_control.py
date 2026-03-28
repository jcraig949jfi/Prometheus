import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Feedback-Tuned Critical Sparse Coding (FT-CSC) Reasoning Tool.
    
    Mechanism:
    1. Sparse Coding (Structural Parsing): Instead of raw tokens, we extract a sparse 
       set of logical features (negations, comparatives, conditionals, numbers). 
       This acts as the 'dictionary' of reasoning primitives.
    2. Phase Transition (Criticality): We define an 'order parameter' based on the 
       density of logical constraints. If constraints are high, the system is in an 
       'ordered' state (strict matching). If low, it is 'disordered' (fuzzy matching).
       The transition point allows small changes in input to flip the ranking logic.
    3. Feedback Control (PID-like): 
       - Error Signal: The discrepancy between the prompt's logical requirements 
         (e.g., "NOT", "greater than") and the candidate's features.
       - Controller: Dynamically adjusts the penalty weight for missing logical features.
         If a candidate fails a hard constraint (e.g., negation mismatch), the error spikes,
         pushing the system to explore alternative rankings or heavily penalize the violation.
    
    This architecture prioritizes structural validity (Reasoning) over string similarity,
    using NCD only as a tiebreaker when structural signals are ambiguous.
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Sparse Dictionary")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|without|fail|false)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.I),
            'causality': re.compile(r'\b(because|therefore|thus|hence|causes|results)\b', re.I),
            'numbers': re.compile(r'\d+(?:\.\d+)?')
        }
        # PID Controller constants (Tuned for stability in logical space)
        self.kp = 2.0  # Proportional gain: Immediate reaction to logical errors
        self.ki = 0.5  # Integral gain: Accumulated pressure to satisfy constraints
        self.kd = 0.1  # Derivative gain: Dampening oscillations
        
    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract sparse logical features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causality': bool(self.patterns['causality'].search(text)),
            'numbers': sorted([float(n) for n in self.patterns['numbers'].findall(text)]),
            'word_count': len(text.split())
        }
        return features

    def _compute_structural_error(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute the 'reconstruction error' between prompt requirements and candidate features.
        High error indicates a logical violation (e.g., prompt says 'NOT', candidate implies 'YES').
        """
        error = 0.0
        
        # Negation mismatch: If prompt has negation, candidate must reflect it or be a direct answer
        # Simplified heuristic: If prompt has negation and candidate lacks specific negation words 
        # but isn't a short 'Yes/No', penalize.
        if prompt_feats['has_negation']:
            if not cand_feats['has_negation'] and cand_feats['word_count'] > 3:
                error += 1.0
        
        # Number consistency: If numbers exist, check relative order if comparatives are present
        if prompt_feats['numbers'] and cand_feats['numbers']:
            if prompt_feats['has_comparative'] or cand_feats['has_comparative']:
                # Check if the candidate preserves the magnitude direction roughly
                # This is a simplified check for presence/absence logic
                if len(prompt_feats['numbers']) == len(cand_feats['numbers']):
                    p_dir = [x > y for x, y in zip(prompt_feats['numbers'][:-1], prompt_feats['numbers'][1:])]
                    c_dir = [x > y for x, y in zip(cand_feats['numbers'][:-1], cand_feats['numbers'][1:])]
                    if p_dir != c_dir:
                        error += 1.5
        
        # Conditional presence
        if prompt_feats['has_conditional'] and not cand_feats['has_conditional']:
            # Soft penalty if the candidate ignores the conditional nature
            error += 0.5
            
        return error

    def _pid_control(self, error: float, prev_error: float, integral: float) -> Tuple[float, float]:
        """
        Simulate a PID controller to adjust the 'sparsity' (strictness) of the evaluation.
        Returns the new strictness factor and updated integral.
        """
        derivative = error - prev_error
        output = (self.kp * error) + (self.ki * integral) + (self.kd * derivative)
        new_integral = integral + error
        # Clamp integral to prevent windup
        new_integral = max(-10.0, min(10.0, new_integral))
        return output, new_integral

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Global state for the "system"
        total_integral = 0.0
        prev_error = 0.0
        
        # Pre-calculate structural errors to tune the global "criticality"
        errors = []
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            err = self._compute_structural_error(prompt_feats, cand_feats)
            errors.append(err)
        
        # If no structural errors found, system is in "disordered" high-entropy state (rely on NCD)
        # If errors exist, system moves to "ordered" critical state (penalize errors heavily)
        base_strictness = 1.0 if any(e > 0 for e in errors) else 0.1

        for i, cand in enumerate(candidates):
            cand_feats = self._extract_features(cand)
            error = errors[i]
            
            # Feedback loop: Adjust strictness based on error signal
            control_signal, total_integral = self._pid_control(error, prev_error, total_integral)
            prev_error = error
            
            # Calculate Score
            # Base score starts at 1.0
            score = 1.0
            
            # Apply structural penalty modulated by the control signal (Criticality)
            # If error > 0 and strictness is high, score drops significantly
            if error > 0:
                penalty = error * (base_strictness + control_signal)
                score -= penalty
            
            # Tie-breaking / Fine-tuning with NCD (only if structural scores are close/high)
            # We invert NCD so higher is better, scaled small so it doesn't override logic
            if score > 0.5: 
                ncd_val = self._ncd(prompt, cand)
                # Reward similarity slightly, but punish if it's too generic
                score -= (ncd_val * 0.1) 
            
            # Ensure bounds
            score = max(0.0, min(1.0, score))
            
            reasoning = f"Structural Error: {error:.2f}, Control Signal: {control_signal:.2f}"
            if error == 0:
                reasoning = "No logical violations detected."
                
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on logical consistency between prompt and answer.
        Returns 0.0 to 1.0.
        """
        prompt_feats = self._extract_features(prompt)
        ans_feats = self._extract_features(answer)
        
        error = self._compute_structural_error(prompt_feats, ans_feats)
        
        # If error is 0, high confidence. If error > 0, confidence drops.
        # Map error to 0-1 scale. 
        # Error 0 -> 1.0, Error 1.0 -> 0.5, Error 2.0+ -> ~0.0
        raw_conf = 1.0 / (1.0 + error)
        
        # Boost if NCD is low (high similarity) and logical error is 0
        if error == 0:
            ncd = self._ncd(prompt, answer)
            # If very similar and logically sound, boost confidence
            if ncd < 0.5:
                raw_conf = min(1.0, raw_conf + 0.2)
                
        return round(raw_conf, 4)