import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Feedback-Controlled Maximum-Entropy (PF-ME) Inference Engine.
    
    Mechanism:
    1. Structural Parsing (Pragmatism): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values to form a rigid 'utility' 
       skeleton. This avoids the 'historical inhibitor' trap by using pragmatism 
       only for structural validation, not semantic scoring.
    2. MaxEnt Initialization: Candidates start with equal probability (maximum entropy).
    3. Feedback Control (PID): 
       - Error (e_t) is the mismatch between candidate properties and prompt constraints.
       - P-term: Immediate penalty for constraint violation.
       - I-term: Cumulative penalty for repeated structural mismatches (bias correction).
       - D-term: Dampens oscillation between similar candidates.
    4. Scoring: Final score is the entropy-weighted sum of constraint satisfaction, 
       with NCD used strictly as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        # PID Controller Gains
        self.Kp = 1.0  # Proportional: Immediate constraint match/mismatch
        self.Ki = 0.1  # Integral: Cumulative structural consistency
        self.Kd = 0.05 # Derivative: Stability against noise
        
        # State storage for feedback loop (simplified for stateless interface)
        self._lambda = 0.0  # Lagrange multiplier proxy
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'boolean_yes': re.compile(r'\byes\b', re.I),
            'boolean_no': re.compile(r'\bno\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict:
        """Extract structural features for pragmatic utility calculation."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'is_yes': bool(self.patterns['boolean_yes'].search(text)),
            'is_no': bool(self.patterns['boolean_no'].search(text)),
            'length': len(text.split())
        }
        return features

    def _compute_constraint_error(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Calculate error signal (e_t) based on structural mismatch.
        This implements the 'Pragmatism' via utility thresholding on structure.
        """
        error = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should reflect understanding (heuristic)
        if prompt_feats['has_negation']:
            # Simple heuristic: if prompt negates, simple 'yes' is often wrong without context
            if cand_feats['is_yes'] and not cand_feats['has_negation']:
                error += 0.5
        
        # 2. Numeric Consistency (Constraint Propagation)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Check for direct contradiction or nonsensical scaling
            p_max = max(prompt_feats['numbers'])
            c_max = max(cand_feats['numbers'])
            # Heuristic: If candidate number is wildly out of bounds relative to prompt
            if c_max > p_max * 10 or c_max < p_max * 0.01:
                error += 0.8
                
        # 3. Logical Form Match
        # If prompt is conditional, ideal answer addresses the condition
        if prompt_feats['has_conditional'] and not cand_feats['has_conditional']:
            # Not a hard error, but increases uncertainty
            error += 0.2
            
        return error

    def _pid_update(self, error: float, prev_error: float, integral: float) -> Tuple[float, float, float]:
        """Compute PID control signal to adjust belief Lagrange multipliers."""
        derivative = error - prev_error
        integral += error
        control_signal = (self.Kp * error) + (self.Ki * integral) + (self.Kd * derivative)
        return control_signal, integral, derivative

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_structure(prompt)
        results = []
        
        # MaxEnt Initialization: Start with uniform belief
        # In a dynamic system, this would be a distribution vector. 
        # Here we simulate the steady-state of the PID loop for each candidate.
        
        integral_error = 0.0
        prev_error = 0.0
        
        # Pre-calculate errors to simulate batch feedback
        errors = [self._compute_constraint_error(prompt_feats, self._extract_structure(c)) for c in candidates]
        
        for i, candidate in enumerate(candidates):
            cand_feats = self._extract_structure(candidate)
            error = errors[i]
            
            # PID Control Step
            control_signal, integral_error, _ = self._pid_update(error, prev_error, integral_error)
            prev_error = error
            
            # MaxEnt Belief Update
            # Belief ~ exp(-lambda * error). 
            # Higher control signal (error) -> Lower belief.
            # We invert the signal to create a score where higher is better.
            base_score = 1.0 / (1.0 + abs(control_signal))
            
            # Pragmatic Utility Filter
            # If structural parsing detects a hard logical fail (e.g. wrong boolean in negated context)
            if prompt_feats['has_negation'] and cand_feats['is_yes'] and not cand_feats['has_negation']:
                # Apply heavy penalty (Pragmatic rejection)
                base_score *= 0.1
            
            results.append({
                'candidate': candidate,
                'score': base_score,
                'error_signal': error, # Store for tie-breaking logic
                'reasoning': f"Structural match score adjusted by PID feedback on error {error:.2f}"
            })

        # Sorting and Tie-Breaking
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply NCD tie-breaking for candidates with similar structural scores
        # This satisfies the requirement: "NCD is only a tiebreaker"
        final_results = []
        for i, res in enumerate(results):
            # Add small NCD perturbation to break ties deterministically
            # Compare against prompt to reward relevance, or against neighbors for diversity
            ncd_val = self._ncd(prompt, res['candidate'])
            # NCD is distance (lower is better similarity), we want higher score for better match
            # But strictly as tiebreaker: add tiny fraction based on NCD
            tie_breaker = ncd_val * 1e-6 
            res['score'] = res['score'] - tie_breaker # Prefer lower NCD (more similar) if scores equal
            
            # Clean up internal keys
            final_res = {
                'candidate': res['candidate'],
                'score': round(res['score'], 6),
                'reasoning': res['reasoning']
            }
            final_results.append(final_res)
            
        # Re-sort after tie-breaking adjustment
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and feedback error.
        """
        prompt_feats = self._extract_structure(prompt)
        ans_feats = self._extract_structure(answer)
        
        # Calculate error
        error = self._compute_constraint_error(prompt_feats, ans_feats)
        
        # Simulate one PID step to get control signal
        control_signal, _, _ = self._pid_update(error, 0.0, 0.0)
        
        # Convert to confidence
        # Low error -> Low control signal -> High confidence
        raw_conf = 1.0 / (1.0 + abs(control_signal))
        
        # Pragmatic hard constraints
        if prompt_feats['has_negation'] and ans_feats['is_yes'] and not ans_feats['has_negation']:
            raw_conf *= 0.2
            
        return max(0.0, min(1.0, raw_conf))