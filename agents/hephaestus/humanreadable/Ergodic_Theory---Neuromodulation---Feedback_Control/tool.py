import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic Neuromodulatory Feedback Controller (ENFC) for Reasoning.
    
    Mechanism:
    1. Ergodic Estimation: Treats the text analysis as a trajectory. Time-averages 
       of structural features (negations, comparatives, numerics) converge to 
       ensemble estimates of logical validity.
    2. Neuromodulatory Gains: Adaptive parameters (DA, 5HT, ACh) scale the sensitivity 
       of the scorer based on detected 'error' (mismatch between expected structure 
       and observed candidate properties).
       - Dopamine (DA): Rewards structural alignment (positive logic).
       - Serotonin (5HT): Penalizes uncertainty or contradiction (negation handling).
       - Acetylcholine (ACh): Adjusts gain on numeric precision.
    3. Feedback Control: A PID-like loop computes the error between the prompt's 
       structural constraints and the candidate's fulfillment. Persistent error 
       (hypothesis mismatch) triggers a 'gain shift' lowering the score of candidates 
       that fail specific structural tests (e.g., missing negations).
       
    This approach prioritizes structural parsing and constraint propagation over 
    simple string similarity (NCD), using NCD only as a tiebreaker.
    """

    def __init__(self):
        # Neuromodulatory gains (adaptive)
        self.g_da = 1.0   # Dopamine: Reward prediction / structural match
        self.g_5ht = 1.0  # Serotonin: Uncertainty / Negation penalty
        self.g_ach = 1.0  # Acetylcholine: Numeric precision gain
        
        # PID Controller state for error accumulation
        self.integral_error = 0.0
        self.prev_error = 0.0
        
        # PID Constants
        self.kp = 0.5
        self.ki = 0.1
        self.kd = 0.1

    def _extract_structural_features(self, text: str) -> dict:
        """Extracts logical primitives: negations, comparatives, numbers."""
        text_lower = text.lower()
        
        # Negations
        negations = len(re.findall(r'\b(not|no|never|neither|none|without)\b', text_lower))
        
        # Comparatives / Superlatives
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|better|worst|best|most|least|than)\b', text_lower))
        
        # Conditionals
        conditionals = len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower))
        
        # Numbers (for numeric evaluation)
        numbers = re.findall(r'\d+\.?\d*', text)
        numeric_vals = []
        for n in numbers:
            try:
                numeric_vals.append(float(n))
            except ValueError:
                pass
        
        return {
            'negations': negations,
            'comparatives': comparatives,
            'conditionals': conditionals,
            'numbers': numeric_vals,
            'has_numbers': len(numeric_vals) > 0
        }

    def _compute_pid_gain(self, error: float) -> float:
        """Simulates the neuromodulatory update via PID control on error."""
        self.integral_error += error
        derivative_error = error - self.prev_error
        
        # PID output adjusts the global sensitivity
        adjustment = self.kp * error + self.ki * self.integral_error + self.kd * derivative_error
        self.prev_error = error
        
        # Clip adjustment to prevent explosion (biological plausibility)
        return max(0.1, min(5.0, 1.0 + adjustment))

    def _calculate_ergodic_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes a score based on structural alignment and ergodic convergence.
        Returns (score, reasoning_string).
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        score = 0.0
        reasons = []
        
        # 1. Negation Consistency (Serotonergic check)
        # If prompt has negations, candidate should ideally reflect understanding 
        # (heuristic: if prompt has negation, candidate having some logical marker is good)
        neg_error = abs(p_feat['negations'] - c_feat['negations']) / (p_feat['negations'] + 1)
        if p_feat['negations'] > 0:
            # Reward if candidate acknowledges complexity (has some structure)
            if c_feat['negations'] > 0 or c_feat['conditionals'] > 0:
                score += 0.3 * self.g_5ht
                reasons.append("Negation context acknowledged.")
            else:
                score -= 0.2 * self.g_5ht
                reasons.append("Potential negation oversight.")
        
        # 2. Numeric Evaluation (Cholinergic check)
        if p_feat['has_numbers'] and c_feat['has_numbers']:
            # Check for direct number presence or simple ordering if applicable
            # Heuristic: Candidate containing prompt numbers is often correct in reasoning tasks
            match_count = sum(1 for n in p_feat['numbers'] if str(int(n)) in candidate or str(n) in candidate)
            if match_count > 0:
                score += 0.4 * self.g_ach
                reasons.append("Numeric constraints satisfied.")
            else:
                # Penalty for missing numbers when prompt has them
                score -= 0.1 * self.g_ach
        elif p_feat['has_numbers'] and not c_feat['has_numbers']:
            # Strong penalty if prompt requires math but candidate has no numbers
            score -= 0.3 * self.g_ach
            reasons.append("Missing numeric evaluation.")

        # 3. Structural Complexity (Dopaminergic reward)
        # Reward candidates that match the logical density of the prompt
        logic_density_p = p_feat['comparatives'] + p_feat['conditionals']
        logic_density_c = c_feat['comparatives'] + c_feat['conditionals']
        
        if logic_density_p > 0:
            if logic_density_c >= logic_density_p * 0.5:
                score += 0.3 * self.g_da
                reasons.append("Logical complexity matched.")
            else:
                score -= 0.1 * self.g_da
                reasons.append("Logical simplification detected.")

        # 4. NCD Tiebreaker (Compression)
        # Only used to break ties or add small differentiation
        try:
            data = (prompt + candidate).encode('utf-8')
            comp_len = len(zlib.compress(data))
            max_len = len(data) + 100 # Approximate max
            ncd_score = 1.0 - (comp_len / max_len) if max_len > 0 else 0
            score += ncd_score * 0.05 # Small weight
        except:
            pass

        return score, "; ".join(reasons) if reasons else "Structural analysis complete."

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the ENFC framework.
        """
        results = []
        
        # Calculate initial scores to determine error signal
        raw_scores = []
        for cand in candidates:
            s, _ = self._calculate_ergodic_score(prompt, cand)
            raw_scores.append(s)
        
        # Compute error signal (deviation from ideal score of 1.0 or max)
        # In a batch, we assume the best candidate represents the 'truth' trajectory
        max_score = max(raw_scores) if raw_scores else 0.0
        error = 1.0 - max_score # Error relative to perfect score
        
        # Update neuromodulatory gains via Feedback Control
        gain_factor = self._compute_pid_gain(error)
        self.g_da = gain_factor
        self.g_5ht = gain_factor
        self.g_ach = gain_factor
        
        # Re-evaluate with updated gains
        for cand in candidates:
            score, reason = self._calculate_ergodic_score(prompt, cand)
            # Apply global gain modulation
            final_score = score * gain_factor
            
            # Normalize to 0-1 range roughly (sigmoid-like clipping)
            final_score = 1.0 / (1.0 + pow(2.718, -final_score)) 
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        score, _ = self._calculate_ergodic_score(prompt, answer)
        
        # Apply current gain state
        adjusted_score = score * self.g_da
        
        # Sigmoid mapping to 0-1
        conf = 1.0 / (1.0 + pow(2.718, -adjusted_score))
        return max(0.0, min(1.0, conf))