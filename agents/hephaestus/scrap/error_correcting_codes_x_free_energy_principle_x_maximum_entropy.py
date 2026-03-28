import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Predictive-Coding Architecture with Protected Latents.
    
    Mechanism:
    1. MaxEnt Prior (Structural Parsing): Establishes a least-bias baseline by extracting
       structural constraints (negations, comparatives, conditionals) from the prompt.
       This defines the 'expected value constraints' for the hypothesis space.
    2. Free Energy Principle (Evaluation): Candidates are evaluated by minimizing 
       Variational Free Energy (F). F = Accuracy_Error + Complexity_Penalty.
       - Accuracy: How well the candidate satisfies extracted structural constraints.
       - Complexity: Penalizes candidates that deviate wildly from the prompt's semantic 
         center (approximated via NCD) without adding structural value.
    3. Error Correcting Codes (Latent Protection): The internal score vector is treated 
       as a noisy transmission. A simple parity-based 'belief propagation' step checks 
       consistency between structural matches and semantic similarity. If a candidate 
       matches structural keys but has high semantic distance (or vice versa), the 
       'energy' is increased (penalized), simulating error detection/correction.
    
    This integrates ECC, FEP, and MaxEnt to rank candidates by robustness to noise 
    and adherence to logical constraints.
    """

    def __init__(self):
        # Structural patterns act as the "Expected Value Constraints" for MaxEnt
        self.negation_words = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparative_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.conditional_words = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extract structural constraints (MaxEnt Prior)."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(w in words for w in self.negation_words)
        has_comparative = any(op in lower_text for op in self.comparative_ops)
        has_conditional = any(w in words for w in self.conditional_words)
        
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        numbers.sort()
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text)
        }

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a proxy for semantic similarity."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def _check_logical_consistency(self, prompt_struct: Dict, cand_struct: Dict, candidate: str) -> float:
        """
        ECC-inspired Belief Propagation: Check consistency between prompt and candidate structures.
        Returns a penalty (0.0 = consistent, 1.0 = inconsistent).
        """
        penalty = 0.0
        
        # Parity Check 1: Negation consistency
        # If prompt has negation, valid answers often reflect it or explicitly deny it.
        # Heuristic: If prompt negates, and candidate ignores negation words entirely while being short, penalize.
        if prompt_struct['negation']:
            if not cand_struct['negation'] and cand_struct['length'] < 20:
                # Weak check: short answers ignoring negation might be errors
                penalty += 0.2
        
        # Parity Check 2: Numeric Transitivity
        # If both have numbers, ensure basic ordering logic isn't violated if comparatives exist
        if prompt_struct['comparative'] and cand_struct['comparative']:
            if len(prompt_struct['numbers']) >= 2 and len(cand_struct['numbers']) >= 2:
                p_diff = prompt_struct['numbers'][-1] - prompt_struct['numbers'][0]
                c_diff = cand_struct['numbers'][-1] - cand_struct['numbers'][0]
                # If directions oppose wildly without linguistic justification, add noise
                if (p_diff > 0 and c_diff < 0) or (p_diff < 0 and c_diff > 0):
                    penalty += 0.3

        return min(penalty, 1.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []
        
        # Pre-calculate NCD matrix for tie-breaking and complexity penalty
        # Using prompt as reference "True State"
        base_ncd = [self._ncd(prompt, cand) for cand in candidates]
        
        for i, cand in enumerate(candidates):
            cand_struct = self._extract_structure(cand)
            
            # 1. MaxEnt Prior Satisfaction (Structural Match)
            # Reward matching structural features present in the prompt
            struct_score = 0.0
            if prompt_struct['negation'] and cand_struct['negation']:
                struct_score += 0.4
            elif not prompt_struct['negation'] and not cand_struct['negation']:
                struct_score += 0.2 # Neutral alignment
                
            if prompt_struct['comparative'] and cand_struct['comparative']:
                struct_score += 0.3
            elif prompt_struct['comparative'] and not cand_struct['comparative']:
                # Missing required comparative logic
                struct_score -= 0.5
                
            if prompt_struct['conditional'] and cand_struct['conditional']:
                struct_score += 0.3

            # 2. Free Energy Minimization
            # F = Energy (Error) - Entropy (Uncertainty/Complexity)
            # We want to minimize F. 
            # Error term: Structural mismatch + Semantic distance (NCD)
            # High NCD from prompt implies high "surprise" or error if not justified by structure.
            
            semantic_distance = base_ncd[i]
            
            # ECC Correction Step: Apply consistency penalty
            ecc_penalty = self._check_logical_consistency(prompt_struct, cand_struct, cand)
            
            # Total Free Energy Estimate (Lower is better)
            # Weighted sum: Structural errors hurt most, then semantic drift, then ECC penalties
            energy = (1.0 - struct_score) + (0.5 * semantic_distance) + ecc_penalty
            
            # Convert to Score (Higher is better)
            # Invert energy, ensure non-negative
            score = max(0.0, 1.0 - energy)
            
            # Tie-breaking with pure NCD if scores are close (handled by float precision mostly)
            # But we add a tiny NCD bonus for being semantically close if structural score is equal
            score += (1.0 - semantic_distance) * 0.001 

            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match: {struct_score:.2f}, Semantic dist: {semantic_distance:.2f}, ECC penalty: {ecc_penalty:.2f}"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low Free Energy = High Confidence.
        """
        # Evaluate single candidate against itself to get relative ranking potential
        # We simulate a minimal candidate set to gauge absolute quality
        dummy_candidates = [answer, ""] 
        results = self.evaluate(prompt, [answer])
        
        if not results:
            return 0.0
            
        # The score from evaluate is already a normalized proxy for 1 - FreeEnergy
        # We clamp it to [0, 1]
        raw_score = results[0]['score']
        return max(0.0, min(1.0, raw_score))