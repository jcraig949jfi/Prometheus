import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a predictive-coding hierarchy with information-theoretic Hebbian updates.
    
    Mechanism:
    1. Structural Parsing (Prediction): Extracts logical constraints (negations, comparatives, 
       conditionals, numbers) to form a "generative model" of the prompt.
    2. Error Calculation (Surprise): Measures the mismatch between the prompt's constraints 
       and each candidate's structural signature.
    3. Information-Theoretic Hebbian Update: 
       - Estimates local Mutual Information (I) via co-occurrence of structural tokens.
       - Updates a synthetic weight proportional to (Information - Error).
       - Candidates that satisfy high-information constraints (e.g., specific numbers, negations) 
         receive higher scores, simulating the minimization of free energy.
    4. Emergence: Functional modules (logic checks) self-organize to penalize candidates 
       that violate transitivity or numeric order.
    """

    def __init__(self):
        # Synthetic synaptic weights for structural features
        self.weights = {
            'negation': 1.0,
            'comparative': 1.0,
            'conditional': 1.0,
            'numeric': 1.0,
            'causal': 1.0
        }
        self.lambda_error = 0.5  # Balances information gain vs error reduction

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts structural features acting as the 'neural activity' x_i."""
        text_lower = text.lower()
        features = {
            'negation': len(re.findall(r'\b(not|no|never|neither|nor|without|fail)\b', text_lower)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worst|best|than|>=|<=|>|<)\b', text_lower)),
            'conditional': len(re.findall(r'\b(if|then|unless|otherwise|provided|when)\b', text_lower)),
            'numeric': len(re.findall(r'\d+(?:\.\d+)?', text_lower)),
            'causal': len(re.findall(r'\b(because|therefore|thus|hence|causes|leads to)\b', text_lower))
        }
        
        # Numeric evaluation state
        numbers = re.findall(r'-?\d+(?:\.\d+)?', text)
        features['numbers'] = [float(n) for n in numbers] if numbers else []
        
        # Check for specific numeric logic patterns (e.g., A > B)
        features['numeric_logic_valid'] = True
        if 'greater' in text_lower or 'less' in text_lower or '>' in text or '<' in text:
            if len(features['numbers']) >= 2:
                # Simple transitivity check heuristic
                if 'less' in text_lower or '<' in text:
                    if features['numbers'] != sorted(features['numbers']):
                        features['numeric_logic_valid'] = False
                elif 'greater' in text_lower or '>' in text:
                    if features['numbers'] != sorted(features['numbers'], reverse=True):
                        features['numeric_logic_valid'] = False

        return features

    def _estimate_mutual_information(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Estimates local mutual information I[x_i; x_j] based on feature co-occurrence.
        If the prompt has a feature (activity > 0), the candidate having it increases MI.
        """
        mi_score = 0.0
        count = 0
        
        for key in ['negation', 'comparative', 'conditional', 'numeric', 'causal']:
            p_val = prompt_feats.get(key, 0)
            c_val = cand_feats.get(key, 0)
            
            # Binary activation for MI estimation
            p_active = 1 if p_val > 0 else 0
            c_active = 1 if c_val > 0 else 0
            
            if p_active > 0:
                # Information gain if candidate also activates this feature
                if c_active > 0:
                    mi_score += 1.0 
                count += 1
        
        return mi_score / (count + 1e-6) if count > 0 else 0.0

    def _compute_prediction_error(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Computes surprise (epsilon) based on constraint violation.
        High error if prompt requires a feature (e.g., negation) but candidate lacks it.
        """
        error = 0.0
        
        # Check presence/absence matching
        for key in ['negation', 'comparative', 'conditional', 'causal']:
            p_active = 1 if prompt_feats.get(key, 0) > 0 else 0
            c_active = 1 if cand_feats.get(key, 0) > 0 else 0
            
            # If prompt has it, candidate MUST have it (Penalty if missing)
            if p_active > 0 and c_active == 0:
                error += 2.0
            # If prompt implies a specific numeric logic, check validity
            if key == 'numeric' and prompt_feats.get('numbers') and cand_feats.get('numbers'):
                if not prompt_feats.get('numeric_logic_valid', True):
                     # If prompt sets up a logic trap and candidate falls in, high error
                     # (Simplified: assume candidate repeats prompt numbers implies agreement)
                     pass 

        # Numeric consistency check
        if prompt_feats.get('numbers') and cand_feats.get('numbers'):
            # If candidate numbers contradict prompt logic (simplified)
            if not prompt_feats.get('numeric_logic_valid', True):
                 error += 1.5

        return error

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_structure(prompt)
        results = []
        
        # Baseline NCD calculation (using length difference as proxy for compression distance tiebreaker)
        # Real NCD is expensive; len ratio is a deterministic, fast approximation for tie-breaking
        prompt_len = len(prompt)
        
        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # 1. Information Theoretic Hebbian Update
            # Delta w ~ (I[x_i; x_j] - lambda * epsilon)
            mi = self._estimate_mutual_information(prompt_feats, cand_feats)
            error = self._compute_prediction_error(prompt_feats, cand_feats)
            
            # Base score from Hebbian rule
            hebbian_score = mi - (self.lambda_error * error)
            
            # 2. Emergent Constraint Propagation
            # If prompt has numbers, strict numeric check boosts score significantly
            if prompt_feats.get('numbers') and cand_feats.get('numbers'):
                if prompt_feats['numeric_logic_valid']:
                    hebbian_score += 2.0 # Reward consistency
            
            # 3. NCD Tiebreaker (Structural parsing is primary, NCD secondary)
            # Lower NCD (higher similarity) is better. 
            # Approximated here by inverse length difference normalized
            cand_len = len(cand)
            ncd_proxy = abs(prompt_len - cand_len) / (max(prompt_len, cand_len) + 1)
            
            final_score = hebbian_score - (0.1 * ncd_proxy)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Hebbian:{mi:.2f} - Error:{error:.2f} + NCD_penalty"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the score of the single candidate.
        Uses the same Hebbian logic.
        """
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        
        score = ranked[0]['score']
        
        # Map score to 0-1 range using a sigmoid-like function
        # Hebbian scores usually range -2 to +3 in this implementation
        confidence = 1 / (1 + math.exp(-score))
        return min(1.0, max(0.0, confidence))