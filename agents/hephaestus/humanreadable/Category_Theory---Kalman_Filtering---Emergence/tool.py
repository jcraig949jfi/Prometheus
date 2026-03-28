import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Multi-scale Kalman Filter (FMKF) Reasoning Tool.
    
    Mechanism:
    1. Micro-Level (Kalman): Parses prompt for structural constraints (negations, comparatives, 
       conditionals) and numeric values. Treats these as noisy observations of the 'true' logic.
    2. Macro-Level (Functor): Lifts micro-observations to a coherence score. Candidates are 
       evaluated by how well they satisfy the structural constraints (process noise minimization).
    3. Emergence (Natural Transformation): Computes the discrepancy between the candidate's 
       logical implication and the prompt's constraints. This 'mismatch' acts as the innovation 
       term in a Kalman update, adjusting the final score.
    4. Scoring: Combines structural satisfaction (logic) with NCD (compression) as a tiebreaker.
    """

    def __init__(self):
        # Process noise covariance (uncertainty in logical rules)
        self.Q = 0.1 
        # Measurement noise covariance (uncertainty in text interpretation)
        self.R = 0.2
        
    def _extract_structure(self, text: str) -> dict:
        """Extract logical primitives: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        structure = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': []
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        structure['numbers'] = [float(n) for n in nums]
        return structure

    def _check_constraint_satisfaction(self, prompt_struct: dict, candidate: str) -> float:
        """
        Evaluate how well a candidate satisfies the structural constraints of the prompt.
        Returns a score between 0 (violation) and 1 (satisfaction).
        """
        score = 1.0
        cand_lower = candidate.lower()
        
        # 1. Negation Check: If prompt has negation, candidate should reflect exclusion or specific logic
        # Simple heuristic: if prompt has 'not', candidate shouldn't be a blind affirmative without nuance
        if prompt_struct['negations'] > 0:
            if cand_lower in ['yes', 'true', 'it is']:
                score -= 0.4 # Penalty for blind affirmation in negative context
            if 'not' in cand_lower or 'no' in cand_lower:
                score += 0.2 # Reward for acknowledging negation

        # 2. Comparative Check: If prompt compares, candidate should ideally reflect order
        if prompt_struct['comparatives'] > 0:
            # If candidate contains numbers, check if they align with simple comparative logic
            cand_nums = re.findall(r'-?\d+\.?\d*', candidate)
            if len(cand_nums) > 0 and len(prompt_struct['numbers']) >= 2:
                # Basic transitivity check if numbers are present
                try:
                    c_val = float(cand_nums[0])
                    p_vals = sorted(prompt_struct['numbers'])
                    # Heuristic: Does the candidate number fit the range or order?
                    # This is a simplified proxy for complex logical inference
                    if p_vals[0] < p_vals[-1] and c_val == p_vals[-1]:
                        score += 0.3
                except:
                    pass

        # 3. Conditional Check
        if prompt_struct['conditionals'] > 0:
            if 'if' in cand_lower or 'then' in cand_lower or 'because' in cand_lower:
                score += 0.2
        
        return max(0.0, min(1.0, score))

    def _kalman_update_score(self, prior_score: float, observation: float) -> float:
        """Simple 1D Kalman update to fuse structural prior with observation."""
        # Predict step (identity model)
        pred_est = prior_score
        pred_err = prior_score * (1 - prior_score) + self.Q # Approximate error covariance
        
        # Update step
        kalman_gain = pred_err / (pred_err + self.R)
        updated_est = pred_est + kalman_gain * (observation - pred_est)
        
        return max(0.0, min(1.0, updated_est))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Global prior based on prompt complexity (Emergence macro-state)
        # Complex prompts (high structure count) require higher logical rigor
        macro_complexity = min(1.0, (prompt_struct['negations'] + prompt_struct['comparatives'] + prompt_struct['conditionals']) / 3.0)
        global_prior = 0.5 + (macro_complexity - 0.5) * 0.2 

        for cand in candidates:
            # Micro-level: Structural parsing
            struct_score = self._check_constraint_satisfaction(prompt_struct, cand)
            
            # Macro-level: Functorial lift to coherence
            # The functor F maps structural satisfaction to a probability space
            macro_coherence = self._kalman_update_score(global_prior, struct_score)
            
            # Natural Transformation: Discrepancy between expected logic and candidate content
            # If the candidate is short and the prompt is complex, penalty applies unless logic holds
            length_ratio = len(cand) / (len(prompt) + 1)
            emergence_penalty = 0.0
            if macro_complexity > 0.5 and length_ratio < 0.1 and struct_score < 0.8:
                emergence_penalty = 0.2
            
            final_score = max(0.0, macro_coherence - emergence_penalty)
            
            # NCD Tiebreaker (only if scores are very close, handled by sorting stability mostly, 
            # but we add a tiny epsilon based on NCD to break ties deterministically)
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so lower distance (higher similarity/relevance) adds slightly to score
            # Note: NCD is 0 (identical) to 1 (disjoint). We want low NCD to help.
            ncd_bonus = (1.0 - ncd_val) * 0.01 

            results.append({
                "candidate": cand,
                "score": round(final_score + ncd_bonus, 6),
                "reasoning": f"Structural fit: {struct_score:.2f}, Macro coherence: {macro_coherence:.2f}, NCD bonus: {ncd_bonus:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        prompt_struct = self._extract_structure(prompt)
        struct_score = self._check_constraint_satisfaction(prompt_struct, answer)
        
        # Use the same Kalman logic as evaluate for consistency
        macro_complexity = min(1.0, (prompt_struct['negations'] + prompt_struct['comparatives'] + prompt_struct['conditionals']) / 3.0)
        global_prior = 0.5 + (macro_complexity - 0.5) * 0.2 
        final_score = self._kalman_update_score(global_prior, struct_score)
        
        return max(0.0, min(1.0, final_score))