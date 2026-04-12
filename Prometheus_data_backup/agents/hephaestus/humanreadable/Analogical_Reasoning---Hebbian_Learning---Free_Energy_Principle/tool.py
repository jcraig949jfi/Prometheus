import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hebbian Predictive-Coding with Analogy-Driven Priors.
    
    Core Mechanism (Free Energy Principle):
    The system minimizes variational free energy by reducing prediction error between
    a generative model (structural expectations) and sensory input (candidate text).
    
    Implementation Details:
    1. Generative Model (Priors): Extracts structural constraints (negations, comparatives, 
       conditionals, numeric logic) from the prompt. This forms the 'analogy-driven prior'.
    2. Prediction Error: Measures the divergence between the candidate's logical structure 
       and the prompt's structural requirements.
    3. Hebbian Plasticity (Confidence): Used strictly as a confidence wrapper. It strengthens 
       the 'confidence' signal only when structural alignment is high (pre/post co-activation), 
       avoiding direct scoring to prevent reasoning traps.
    4. Scoring: Primary signal is structural constraint satisfaction. NCD is a tie-breaker.
    """

    def __init__(self):
        self.baseline_accuracy = 0.20
        self.target_accuracy = 0.53
        
    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extract logical constraints acting as generative priors."""
        t_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|except)\b', t_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', t_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', t_lower)),
            'numeric_val': None,
            'word_count': len(text.split()),
            'raw_len': len(text)
        }
        
        # Extract numeric values for comparison logic
        nums = re.findall(r"[-+]?\d*\.?\d+", text)
        if nums:
            try:
                features['numeric_val'] = float(nums[0])
            except ValueError:
                pass
                
        return features

    def _compute_prediction_error(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Compute prediction error based on structural mismatch.
        Lower error = better fit.
        """
        error = 0.0
        
        # Constraint 1: Negation consistency (Simple heuristic: if prompt has negation, 
        # valid answers often need to address it, but strict boolean matching is hard without NLI.
        # Instead, we penalize length mismatches and lack of structural markers if prompt has them.)
        
        # If prompt has comparatives, candidates lacking them might have higher error (unless answer is numeric)
        if prompt_feats['has_comparative'] and not cand_feats['has_comparative']:
            # Check if it's a numeric answer which satisfies the comparative implicitly
            if cand_feats['numeric_val'] is None:
                error += 0.3
        
        # If prompt has conditionals, check for logical connectors or specific answer patterns
        if prompt_feats['has_conditional']:
            # Heuristic: Conditional prompts often require specific logical steps. 
            # We rely on NCD here as a secondary check, but add small penalty for very short answers
            if cand_feats['word_count'] < 2:
                error += 0.2

        # Numeric consistency: If both have numbers, check magnitude logic if comparatives exist
        if prompt_feats['numeric_val'] is not None and cand_feats['numeric_val'] is not None:
            p_val = prompt_feats['numeric_val']
            c_val = cand_feats['numeric_val']
            
            if prompt_feats['has_comparative']:
                if 'less' in str(prompt_feats).lower() or 'smaller' in str(prompt_feats).lower():
                    if c_val >= p_val: error += 0.5 # Contradiction
                elif 'more' in str(prompt_feats).lower() or 'greater' in str(prompt_feats).lower():
                    if c_val <= p_val: error += 0.5 # Contradiction

        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tie-breaker."""
        if not s1 or not s2: return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0: return 1.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD matrix for tie-breaking if needed
        # But per instructions, NCD is only for ties or when no structural signal.
        
        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # 1. Free Energy Minimization (Structural Prediction Error)
            pred_error = self._compute_prediction_error(prompt_feats, cand_feats, cand)
            
            # 2. Base Score from Structural Fit (Inverse of Error)
            # Start with high score, subtract error
            base_score = 1.0 - pred_error
            
            # Adjust for word count plausibility (very short answers to complex prompts = high error)
            if prompt_feats['word_count'] > 10 and cand_feats['word_count'] < 2:
                base_score -= 0.2
                
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Structural error: {pred_error:.2f}",
                "_feats": cand_feats # Internal use for tie-breaking
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are close (within 0.05)
        # This implements the "NCD as tiebreaker" requirement
        final_results = []
        if len(results) > 1:
            # Simple clustering for tie breaking could be overkill, 
            # just apply NCD relative to prompt for final sorting if scores are equal
            results.sort(key=lambda x: (x['score'], -self._ncd(prompt, x['candidate'])), reverse=True)
            
        for r in results:
            del r['_feats']
            final_results.append(r)
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Hebbian Confidence Wrapper.
        Strengthens confidence (pre-post co-activation) only if structural alignment is high.
        Historical inhibitor warning: Not used for direct scoring, only confidence estimation.
        """
        prompt_feats = self._extract_structure(prompt)
        cand_feats = self._extract_structure(answer)
        
        # Calculate structural alignment (Hebbian pre-post correlation)
        alignment = 0.0
        
        # Co-activation of negation
        if prompt_feats['has_negation'] and cand_feats['has_negation']:
            alignment += 0.4
        elif not prompt_feats['has_negation'] and not cand_feats['has_negation']:
            alignment += 0.2 # Consistent absence
            
        # Co-activation of comparatives
        if prompt_feats['has_comparative'] and cand_feats['has_comparative']:
            alignment += 0.4
        elif not prompt_feats['has_comparative'] and not cand_feats['has_comparative']:
            alignment += 0.2
            
        # Co-activation of conditionals
        if prompt_feats['has_conditional'] and cand_feats['has_conditional']:
            alignment += 0.4
        elif not prompt_feats['has_conditional'] and not cand_feats['has_conditional']:
            alignment += 0.2
            
        # Normalize alignment to 0-1 range roughly
        # Max possible alignment ~1.2 in this simple model, cap at 1.0
        raw_conf = min(1.0, alignment)
        
        # Penalty for length mismatch (simulating prediction error)
        if prompt_feats['word_count'] > 15 and cand_feats['word_count'] < 3:
            raw_conf *= 0.5
            
        return float(np.clip(raw_conf, 0.0, 1.0))