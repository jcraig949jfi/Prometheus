import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Oscillatory Adaptive Sparse Predictive Coding (OASPC) Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Sparse Coding Analogue): Extracts high-value logical tokens
       (negations, comparatives, conditionals, numbers) as the "sparse representation"
       of the prompt. Per constraints, this drives the primary scoring signal.
    2. Oscillatory Gating: Simulates theta-gamma cycles to alternate between 
       "Hypothesis Stability" (checking constraint satisfaction) and "Error Exploration" 
       (checking NCD similarity).
    3. Feedback Control: A discrete PID-like controller adjusts the 'precision' (weight)
       of the structural score vs. the compression score based on the magnitude of
       logical errors (reconstruction error).
       
    This satisfies the requirement to use Structural Parsing as primary, NCD as tiebreaker,
    and implements the OASPC theoretical framework as a computational analogy.
    """

    def __init__(self):
        # Logical operators for sparse extraction
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'before', 'after']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided', 'assuming']
        self.quantifiers = ['all', 'some', 'many', 'few', 'every', 'each', 'any']
        
        # Feedback Controller State
        self.integral_error = 0.0
        self.prev_error = 0.0
        
        # Tuning parameters (PID-like)
        self.kp = 0.6  # Proportional gain
        self.ki = 0.1  # Integral gain
        self.kd = 0.2  # Derivative gain

    def _extract_sparse_features(self, text: str) -> Dict[str, any]:
        """Extracts logical structures (Sparse Coding layer)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        features = {
            'has_negation': any(n in words for n in self.negations),
            'has_comparative': any(c in words for c in self.comparatives) or any(c in lower_text for c in ['>', '<']),
            'has_conditional': any(c in words for c in self.conditionals),
            'has_quantifier': any(q in words for q in self.quantifiers),
            'numbers': re.findall(r'\d+\.?\d*', lower_text),
            'word_count': len(words)
        }
        return features

    def _evaluate_logic_consistency(self, prompt: str, candidate: str) -> float:
        """
        Computes a logic consistency score based on structural overlap.
        Returns 1.0 for perfect structural match, 0.0 for contradiction, ~0.5 for neutral.
        """
        p_feat = self._extract_sparse_features(prompt)
        c_feat = self._extract_sparse_features(candidate)
        
        score = 0.5  # Base prior
        
        # Constraint Propagation: Negation matching
        if p_feat['has_negation']:
            if c_feat['has_negation']: score += 0.2
            else: score -= 0.2
        else:
            if c_feat['has_negation']: score -= 0.1 # Unexpected negation
            
        # Comparative matching
        if p_feat['has_comparative']:
            if c_feat['has_comparative']: score += 0.2
            else: score -= 0.2
            
        # Conditional matching
        if p_feat['has_conditional']:
            if c_feat['has_conditional']: score += 0.15
            # Lack of conditional in answer isn't always fatal, but presence helps
            
        # Numeric evaluation heuristic
        if p_feat['numbers'] and c_feat['numbers']:
            # If both have numbers, check if candidate numbers are subset or close
            p_nums = set(p_feat['numbers'])
            c_nums = set(c_feat['numbers'])
            if c_nums.issubset(p_nums) or p_nums.issubset(c_nums):
                score += 0.2
            else:
                score -= 0.1 # Conflicting numbers
        elif p_feat['numbers'] and not c_feat['numbers']:
            score -= 0.15 # Missing required numeric reasoning

        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        concat = s1_bytes + s2_bytes
        len_concat = len(zlib.compress(concat))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed/stability in this context if needed, 
        # but strict NCD uses compressed lengths. Let's use compressed lengths for rigor.
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        c_concat = len_concat # Already compressed
        
        min_c = min(c_s1, c_s2)
        max_c = max(c_s1, c_s2)
        
        if max_c == 0:
            return 1.0
            
        ncd = (c_concat - min_c) / max_c
        return max(0.0, min(1.0, ncd))

    def _feedback_controller(self, error: float) -> float:
        """
        Discrete PID controller to adjust precision gain.
        Error is the discrepancy between expected logic and observed structure.
        """
        self.integral_error += error
        derivative_error = error - self.prev_error
        
        # Output is the adjustment factor (gain)
        gain_adjustment = (self.kp * error) + \
                          (self.ki * self.integral_error) + \
                          (self.kd * derivative_error)
        
        self.prev_error = error
        return gain_adjustment

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Oscillatory Cycle Simulation
        # Phase 1: Structural Analysis (Theta phase - gating)
        prompt_features = self._extract_sparse_features(prompt)
        has_complex_logic = any([
            prompt_features['has_negation'],
            prompt_features['has_comparative'],
            prompt_features['has_conditional'],
            len(prompt_features['numbers']) > 0
        ])
        
        # Reset controller state for each evaluation batch
        self.integral_error = 0.0
        self.prev_error = 0.0
        
        # Pre-calculate NCD tiebreakers (expensive op, done once per candidate)
        # We use a dummy 'ideal' suffix to compare against, or pairwise.
        # For ranking, we can just use NCD against the prompt as a baseline similarity.
        
        scored_candidates = []
        
        for cand in candidates:
            # Phase 2: Sparse Coding Evaluation (Gamma phase - processing)
            logic_score = self._evaluate_logic_consistency(prompt, cand)
            
            # Calculate Reconstruction Error (1.0 - logic_score)
            # High logic score = low error
            error = 1.0 - logic_score
            
            # Phase 3: Feedback Control
            # Adjust precision based on error magnitude
            gain_mod = self._feedback_controller(error)
            
            # Base precision weight (higher if prompt has complex logic)
            base_precision = 0.8 if has_complex_logic else 0.5
            
            # Apply gain modulation
            final_precision = max(0.1, base_precision + gain_mod)
            
            # Phase 4: NCD Tiebreaker (Only if logic is ambiguous or equal)
            # We invert NCD so higher is better (1.0 - ncd)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Final Score: Dominated by Logic, refined by NCD
            # If logic_score is high (>0.6), NCD is minor. 
            # If logic_score is neutral (~0.5), NCD breaks ties.
            if has_complex_logic:
                score = (logic_score * final_precision) + (ncd_score * (1.0 - final_precision) * 0.3)
            else:
                # For simple prompts, NCD carries more weight as structural cues are scarce
                score = (logic_score * 0.4) + (ncd_score * 0.6)
                
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Logic:{logic_score:.2f} NCD:{ncd_score:.2f} Gain:{gain_mod:.2f}"
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        Uses the same sparse coding logic as evaluate.
        """
        logic_score = self._evaluate_logic_consistency(prompt, answer)
        
        # If logic score is very low, confidence is low.
        # If logic score is high, confidence is high.
        # Map [0.3, 0.9] range to [0.0, 1.0] roughly
        conf = (logic_score - 0.3) / 0.6
        return max(0.0, min(1.0, conf))