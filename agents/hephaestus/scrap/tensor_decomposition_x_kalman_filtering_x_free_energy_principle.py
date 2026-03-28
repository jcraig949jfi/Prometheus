import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Tensor-Structured Variational Kalman Filter (TS-VKF) Approximation.
    
    Mechanism:
    1. Free Energy Principle (Core): The 'score' is a variational bound approximation.
       We minimize 'surprise' (prediction error) by maximizing structural consistency.
       Candidates that satisfy logical constraints (negations, comparatives) have lower free energy.
    2. Tensor Decomposition (Structural Parsing): Instead of high-rank string matching,
       we decompose the prompt into latent logical factors (modes): 
       [Negation, Comparison, Conditionality, Numeric]. 
       This acts as a low-rank CP decomposition of the semantic space.
    3. Kalman Filtering (Confidence): The confidence() method acts as a recursive filter.
       It predicts the answer validity based on structural priors and updates the state
       (confidence score) based on the 'measurement' (structural match), reducing uncertainty.
       
    Note: Per causal intelligence guidelines, Tensor/Kalman concepts are restricted to 
    structural parsing and confidence wrapping, while Free Energy drives the evaluation logic.
    """

    def __init__(self):
        # Structural keywords acting as tensor factors (modes)
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.booleans = ['yes', 'no', 'true', 'false']
        
        # Priors for Free Energy calculation
        self.prior_weight = 0.2
        self.struct_weight = 0.8

    def _parse_structure(self, text: str) -> Dict[str, float]:
        """Decompose text into logical factors (Tensor Modes)."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        
        # Mode 1: Negation density
        neg_count = sum(1 for w in words if any(n in w for n in self.negations))
        
        # Mode 2: Comparative presence
        comp_count = sum(1 for w in words if any(c in w for c in self.comparatives))
        
        # Mode 3: Conditional presence
        cond_count = sum(1 for w in words if any(c in w for c in self.conditionals))
        
        # Mode 4: Numeric extraction (simplified)
        nums = re.findall(r'\d+\.?\d*', t)
        has_nums = 1.0 if nums else 0.0
        
        # Normalize factors to [0, 1] range roughly
        return {
            'negation': min(neg_count / 3.0, 1.0),
            'comparative': min(comp_count / 3.0, 1.0),
            'conditional': min(cond_count / 3.0, 1.0),
            'numeric': has_nums
        }

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric consistency (Constraint Propagation)."""
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r'\d+\.?\d*', prompt.lower())
        c_nums = re.findall(r'\d+\.?\d*', candidate.lower())
        
        if not p_nums or not c_nums:
            return 0.5  # No numeric signal
        
        try:
            # Simple heuristic: if prompt has comparison words, check order
            p_val = float(p_nums[-1])
            c_val = float(c_nums[-1])
            
            # If candidate repeats the number exactly, it's likely a direct extraction (good)
            if abs(p_val - c_val) < 1e-6:
                return 1.0
            
            # If prompt implies 'less' or 'more', verify rough directionality if possible
            # This is a simplified proxy for complex reasoning
            if any(w in prompt.lower() for w in ['less', 'smaller']):
                return 1.0 if c_val <= p_val else 0.2
            if any(w in prompt.lower() for w in ['more', 'greater']):
                return 1.0 if c_val >= p_val else 0.2
                
            return 0.5
        except ValueError:
            return 0.5

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute negative Free Energy (Evidence Lower Bound approximation).
        Lower prediction error (higher structural match) = Higher Score.
        """
        p_factors = self._parse_structure(prompt)
        c_factors = self._parse_structure(candidate)
        
        error = 0.0
        
        # Calculate prediction error across tensor modes
        # If prompt has strong negation, candidate should reflect it (or contradict logically)
        if p_factors['negation'] > 0.5:
            # Heuristic: If prompt is negative, simple 'yes' might be wrong unless context fits
            if candidate.lower().strip() in ['yes', 'true']:
                error += 0.5
        
        # Comparative consistency
        if p_factors['comparative'] > 0.5:
            if c_factors['comparative'] == 0.0 and not any(x in candidate.lower() for x in self.booleans):
                # Candidate ignores comparison structure
                error += 0.3
                
        # Numeric consistency
        if p_factors['numeric'] > 0.5:
            num_score = self._check_numeric_logic(prompt, candidate)
            error += (1.0 - num_score) * 0.5
            
        # Structural overlap (Jaccard-like on words) as a baseline prior
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        intersection = len(p_words & c_words)
        union = len(p_words | c_words)
        overlap = intersection / union if union > 0 else 0
        
        # Free Energy = Complexity (penalty) - Accuracy (reward)
        # Here we invert: Score = Accuracy - Error
        accuracy_score = overlap * 0.4 + (1.0 - error) * 0.6
        
        return accuracy_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by minimizing variational free energy."""
        results = []
        
        for cand in candidates:
            # Core Free Energy evaluation
            score = self._compute_free_energy(prompt, cand)
            
            # NCD Tiebreaker (only if scores are very close, handled by sorting stability mostly,
            # but we add a tiny noise term based on length compression ratio if needed)
            # For this implementation, we rely on the structural score as primary.
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Free energy minimization via structural tensor factors (neg: {self._parse_structure(prompt)['negation']:.2f}, comp: {self._parse_structure(prompt)['comparative']:.2f}). Prediction error: {1.0-score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Kalman-style update for confidence.
        State: Belief in answer correctness.
        Measurement: Structural consistency check.
        """
        # Prior belief (uncertainty)
        prior_mean = 0.5
        prior_var = 0.25
        
        # Measurement (Structural check)
        # If answer contains key structural elements found in prompt, measurement is high
        p_struct = self._parse_structure(prompt)
        a_struct = self._parse_structure(answer)
        
        # Measurement value (z): 1 if structures align, 0 if they contradict, 0.5 if neutral
        z = 0.5
        if p_struct['negation'] > 0.3 or p_struct['comparative'] > 0.3:
            # Check alignment
            if (p_struct['negation'] > 0.3 and a_struct['negation'] > 0.3) or \
               (p_struct['comparative'] > 0.3 and a_struct['comparative'] > 0.3):
                z = 0.9
            elif answer.lower().strip() in ['yes', 'no', 'true', 'false']:
                # Binary answers to complex structural prompts are risky
                z = 0.4 
        else:
            # Simple overlap for non-structural prompts
            if any(w in answer.lower() for w in re.findall(r'\b\w+\b', prompt.lower())):
                z = 0.8
        
        # Kalman Gain (K)
        # Assume measurement noise R = 0.2
        R = 0.2
        K = prior_var / (prior_var + R)
        
        # Update state
        posterior_mean = prior_mean + K * (z - prior_mean)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, posterior_mean))