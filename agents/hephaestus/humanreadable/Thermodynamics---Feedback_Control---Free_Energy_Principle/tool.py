import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically Constrained Active Inference Controller.
    
    Mechanism:
    1. Generative Model (Structural Parsing): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a 'belief' about the prompt.
    2. Free Energy Principle (FEP): Calculates variational free energy (F) as the 
       divergence between the candidate's logical structure and the prompt's structure.
       Lower F = better fit.
    3. Thermodynamic Cost: Estimates 'entropy production' based on candidate complexity 
       (length/token variance). High complexity increases the cost term.
    4. PID Feedback Controller: Adjusts the final score. 
       - P: Instantaneous error (FEP gap).
       - I: Accumulated bias (penalizes candidates that ignore negation patterns).
       - D: Rate of change (rewards candidates that resolve ambiguity sharply).
       
    The final score minimizes Free Energy while penalizing excessive thermodynamic cost,
    effectively trading off accuracy against computational 'dissipation'.
    """

    def __init__(self):
        # State for PID controller (Integral term accumulator)
        self._integral_error = 0.0
        self._prev_error = 0.0
        # PID Gains
        self._kp = 1.5  # Proportional gain
        self._ki = 0.1  # Integral gain (bias correction)
        self._kd = 0.5  # Derivative gain (anticipation)
        
        # Logical patterns for structural parsing
        self._negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self._comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'fewer', '>', '<']
        self._conditionals = ['if', 'then', 'unless', 'otherwise', 'when']

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Structural parsing: Extracts logical signatures."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_neg = any(n in words for n in self._negations)
        has_comp = any(c in words for c in self._comparatives)
        has_cond = any(c in words for c in self._conditionals)
        
        # Numeric extraction
        numbers = re.findall(r'\d+\.?\d*', text)
        nums = [float(n) for n in numbers]
        
        return {
            'neg_count': sum(words.count(n) for n in self._negations),
            'comp_count': sum(words.count(c) for c in self._comparatives),
            'cond_count': sum(words.count(c) for c in self._conditionals),
            'numbers': nums,
            'length': len(text),
            'word_count': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _compute_free_energy(self, prompt_feat: Dict, cand_feat: Dict, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy (F).
        F = Accuracy (Surprise) + Complexity (Entropy Production cost)
        """
        # 1. Accuracy Term (Surprise): Structural mismatch
        # Penalize if prompt has logic features but candidate ignores them
        logic_mismatch = 0.0
        
        if prompt_feat['neg_count'] > 0:
            if cand_feat['neg_count'] == 0:
                logic_mismatch += 2.0  # High penalty for missing negation
            else:
                logic_mismatch += 0.5 * abs(prompt_feat['neg_count'] - cand_feat['neg_count'])
                
        if prompt_feat['comp_count'] > 0:
            if cand_feat['comp_count'] == 0:
                logic_mismatch += 1.5
                
        # Numeric consistency check (simplified)
        if prompt_feat['numbers'] and cand_feat['numbers']:
            # Check if candidate numbers are subset or close to prompt numbers
            p_nums = set(prompt_feat['numbers'])
            c_nums = set(cand_feat['numbers'])
            if not c_nums.intersection(p_nums) and len(c_nums) > 0:
                logic_mismatch += 1.0
        
        # 2. Thermodynamic Cost Term (Entropy Production)
        # Longer, more complex answers incur higher 'dissipation' cost
        # This prevents overfitting by penalizing unnecessarily verbose hypotheses
        complexity_cost = 0.001 * cand_feat['length']
        
        # NCD as a baseline similarity measure (tiebreaker/anchor)
        ncd_val = self._compute_ncd(prompt, candidate)
        
        # F = Logic Mismatch + Complexity Cost + (NCD * scaling)
        # We want to MINIMIZE F. 
        free_energy = logic_mismatch + complexity_cost + (ncd_val * 0.5)
        
        return free_energy

    def _pid_control(self, error: float) -> float:
        """
        PID Feedback Controller acting on the Free Energy gradient.
        Adjusts the 'learning rate' or confidence scaling based on error dynamics.
        """
        # Proportional
        p_term = self._kp * error
        
        # Integral (accumulates sustained bias)
        self._integral_error += error
        # Clamp integral to prevent windup
        self._integral_error = max(-10.0, min(10.0, self._integral_error))
        i_term = self._ki * self._integral_error
        
        # Derivative (anticipates rapid changes)
        d_term = self._kd * (error - self._prev_error)
        self._prev_error = error
        
        return p_term + i_term + d_term

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feat = self._extract_features(prompt)
        results = []
        
        # Calculate Free Energy for all candidates first to establish baseline
        fe_scores = []
        for cand in candidates:
            cand_feat = self._extract_features(cand)
            fe = self._compute_free_energy(prompt_feat, cand_feat, prompt, cand)
            fe_scores.append(fe)
            
        min_fe = min(fe_scores) if fe_scores else 0.0
        
        for i, cand in enumerate(candidates):
            cand_feat = self._extract_features(cand)
            fe = fe_scores[i]
            
            # Error signal: deviation from the best possible free energy found so far
            error = fe - min_fe
            
            # Apply PID controller to modulate the score based on error dynamics
            # The PID output here acts as a penalty adjustment
            pid_adjustment = self._pid_control(error)
            
            # Final Score: Inverse of Free Energy, adjusted by PID
            # We want high score for low FE. 
            # Base score: 1.0 / (1.0 + FE) ensures range (0, 1]
            base_score = 1.0 / (1.0 + fe)
            
            # Apply PID adjustment (subtract because PID returns penalty for error)
            # Ensure we don't go below 0
            final_score = max(0.0, base_score - (pid_adjustment * 0.1))
            
            # Reasoning string generation
            reasoning = f"FE={fe:.2f}, Cost={cand_feat['length']}, LogicMatch={'High' if error < 0.5 else 'Low'}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Reset integral term periodically to avoid state leakage between unrelated prompts
        # (In a real stream, this would be time-based; here we reset per batch if error is small)
        if abs(self._integral_error) > 5.0:
            self._integral_error *= 0.5
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on Free Energy minimization."""
        prompt_feat = self._extract_features(prompt)
        cand_feat = self._extract_features(answer)
        
        fe = self._compute_free_energy(prompt_feat, cand_feat, prompt, answer)
        
        # Convert Free Energy to Confidence (0-1)
        # Low FE -> High Confidence
        confidence = 1.0 / (1.0 + fe)
        
        # Apply a simple PID-like smoothing based on single instance (simulated)
        # Since we don't have history in single call, we use the error relative to 0
        error = fe 
        adjustment = self._kp * error * 0.1 # Dampened impact for single eval
        
        final_conf = max(0.0, min(1.0, confidence - adjustment))
        return final_conf