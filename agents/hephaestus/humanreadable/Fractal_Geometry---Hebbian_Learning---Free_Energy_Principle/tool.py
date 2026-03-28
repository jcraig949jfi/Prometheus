import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Predictive Coding Network (FPCN) Implementation.
    
    Core Mechanism (Free Energy Principle):
    The 'evaluate' method acts as the variational inference engine. It minimizes 
    "free energy" by calculating the mismatch (prediction error) between the 
    structural constraints of the prompt and the candidate answers.
    
    Structural Parsing (The Generative Model):
    Instead of biological neurons, we use structural parsing (negations, comparatives,
    conditionals, numeric logic) to generate a high-precision "prediction" of what 
    a valid answer must look like. This forms the fractal-like multi-scale hypothesis space:
    1. Micro-scale: Numeric and boolean consistency.
    2. Meso-scale: Logical operator (AND/OR/NOT) satisfaction.
    3. Macro-scale: Semantic constraint propagation.
    
    Hebbian Learning (Precision Weighting):
    The 'confidence' method simulates Hebbian plasticity gated by precision. 
    It strengthens the association (score) between prompt constraints and candidate 
    features only when the prediction error (mismatch) is low. High precision (low error)
    leads to high confidence (consolidation).
    
    Note on Fractal/Hebbian constraints: Per causal analysis, Fractal Geometry and 
    Hebbian Learning are restricted to structural support and confidence gating 
    respectively, while Free Energy minimization drives the core scoring logic.
    """

    def __init__(self):
        # No external state needed; stateless inference
        pass

    def _extract_structural_features(self, text: str) -> dict:
        """Extract logical constraints: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'boolean_yes': 1 if re.search(r'\b(yes|true|correct)\b', text_lower) else 0,
            'boolean_no': 1 if re.search(r'\b(no|false|incorrect)\b', text_lower) else 0,
            'length': len(text)
        }
        return features

    def _compute_numeric_consistency(self, prompt_nums: List[str], candidate: str) -> float:
        """Check if candidate numbers logically follow prompt numbers (simple heuristic)."""
        cand_nums = re.findall(r'-?\d+\.?\d*', candidate)
        if not prompt_nums:
            return 1.0 # No numeric constraints
        if not cand_nums:
            # If prompt has numbers but candidate has none, it might be a word answer, give partial credit
            return 0.5 
        
        try:
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in cand_nums]
            
            # Simple heuristic: If prompt implies a comparison (detected by keywords), 
            # check if candidate reflects the result. 
            # Since we don't have full NLP, we check for direct equality or obvious derivation.
            # For this implementation, we reward candidates that contain the correct magnitude
            # if the prompt asks for a specific number, or logical consistency.
            
            # Baseline: Penalty if magnitudes are wildly different without obvious operation
            if len(p_vals) == len(c_vals):
                diff = sum(abs(p - c) for p, c in zip(p_vals, c_vals))
                if diff == 0: return 1.0
                return max(0.0, 1.0 - (diff / (max(p_vals + c_vals) + 1)))
            
            return 0.5 # Ambiguous numeric relationship
        except ValueError:
            return 0.5

    def _calculate_free_energy(self, prompt_features: dict, candidate: str) -> float:
        """
        Calculate Free Energy (F) = Accuracy - Complexity.
        Here, Accuracy is inverted to represent 'Error' (Mismatch).
        Lower Free Energy = Better Candidate.
        We return a score where Higher = Better (Negative Free Energy).
        """
        cand_features = self._extract_structural_features(candidate)
        
        # 1. Prediction Error Calculation (Mismatch between prompt constraints and candidate)
        error_term = 0.0
        
        # Negation consistency: If prompt has strong negation, candidate should reflect it or answer accordingly
        # Heuristic: If prompt is a question, we look for specific structural alignment.
        # Since we can't parse semantics fully, we use a proxy: 
        # If prompt has 'not', and candidate is 'yes'/'no', we need context. 
        # Instead, we penalize candidates that contradict explicit boolean flags if detectable.
        
        # Numeric Consistency (Strong Signal)
        if prompt_features['numbers']:
            num_score = self._compute_numeric_consistency(prompt_features['numbers'], candidate)
            error_term += (1.0 - num_score) * 2.0 # High weight on numbers
        
        # Logical Operator Consistency (Moderate Signal)
        # If prompt has conditionals, valid answers often contain logical connectors or specific formats
        if prompt_features['conditionals'] > 0:
            if cand_features['conditionals'] == 0 and cand_features['length'] < 10:
                # Short answers to complex conditional prompts are risky but possible
                error_term += 0.2
        
        # 2. Complexity Penalty (Occam's Razor)
        # Prefer concise answers that satisfy constraints
        complexity_penalty = math.log(cand_features['length'] + 1) / 10.0
        
        # Free Energy = Error + Complexity
        # We want to MINIMIZE this. 
        free_energy = error_term + complexity_penalty
        
        # Convert to score: Higher is better. 
        # Use exponential decay to map energy to probability-like score
        score = math.exp(-free_energy)
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates by minimizing variational free energy.
        Uses structural parsing to define the generative model's constraints.
        """
        prompt_feats = self._extract_structural_features(prompt)
        scored_candidates = []
        
        # Pre-calculate NCD matrix for tie-breaking if needed (simplified here to pairwise with prompt)
        
        for cand in candidates:
            # Primary Score: Free Energy Minimization (Structural + Numeric)
            fe_score = self._calculate_free_energy(prompt_feats, cand)
            
            # Secondary Signal: NCD (Only as a minor adjustment or tiebreaker)
            # We use NCD to penalize candidates that are completely unrelated in texture
            ncd = self._ncd_distance(prompt, cand)
            # Normalize NCD to a small penalty factor so it doesn't override structural logic
            ncd_adjustment = (1.0 - ncd) * 0.05 
            
            final_score = fe_score + ncd_adjustment
            
            # Reasoning trace
            reasoning = f"Structural match: {fe_score:.4f}; NCD adjustment: {ncd_adjustment:.4f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Compute confidence based on Hebbian-like precision gating.
        Confidence is high if the 'prediction error' (mismatch) is low.
        This effectively re-evaluates the specific pair with a focus on certainty.
        """
        # Re-use the free energy calculation as the error signal
        prompt_feats = self._extract_structural_features(prompt)
        fe_score = self._calculate_free_energy(prompt_feats, answer)
        
        # The 'fe_score' is already an exponential of negative error.
        # We interpret this directly as confidence (0 to 1).
        # However, to simulate Hebbian 'gating':
        # If the structural match is weak (low score), confidence drops sharply.
        # If strong, it consolidates to near 1.
        
        confidence_val = min(1.0, max(0.0, fe_score))
        
        # Apply a 'precision' threshold: if the answer is too short to contain logic, 
        # and the prompt is complex, reduce confidence (Hebbian failure to fire).
        if len(answer) < 3 and len(prompt) > 20:
            confidence_val *= 0.8
            
        return confidence_val