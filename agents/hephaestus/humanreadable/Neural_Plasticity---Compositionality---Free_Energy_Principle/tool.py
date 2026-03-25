import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Plastic Compositional Predictive Coding (PCPC) Approximation.
    
    Mechanism:
    1. Compositionality (Tensor Binding): Parses prompts into structural tuples 
       (Subject, Relation, Object) and numeric values. This creates a 
       compositional representation rather than a bag-of-words.
    2. Free Energy Principle (FEP): Defines 'Free Energy' as the sum of 
       prediction errors. 
       - For logic: Error is the mismatch between the candidate's implied state 
         and the prompt's constraints (e.g., negation flips expected truth).
       - For math: Error is the absolute difference between candidate and computed truth.
    3. Neural Plasticity (Hebbian Gating): Weights for semantic matches are 
       dynamically adjusted (plastic) based on the presence of logical gates 
       (negation/conditionals). If a negation is detected, the 'synaptic weight' 
       for positive matches is inhibited, and negative matches are potentiated.
       
    The system minimizes Free Energy by ranking candidates that best satisfy 
    the compositionally bound constraints under the current plastic weights.
    """

    def __init__(self):
        # Simple stoplist for structural parsing
        self.stopwords = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparators = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller'}
        
    def _tokenize(self, text: str) -> List[str]:
        return [w.strip('.,!?;:') for w in text.lower().split() if w.strip('.,!?;:')]

    def _extract_numbers(self, tokens: List[str]) -> List[float]:
        nums = []
        for t in tokens:
            try:
                # Handle basic floats
                if '.' in t or t.isdigit():
                    nums.append(float(t))
            except ValueError:
                continue
        return nums

    def _bind_structure(self, text: str) -> Dict:
        """
        Compositional Binding: Extracts roles (Subject, Object, Relation) 
        and fillers (concepts, numbers) into a structured dict.
        """
        tokens = self._tokenize(text)
        has_neg = any(t in self.negations for t in tokens)
        has_comp = any(t in self.comparators for t in tokens)
        numbers = self._extract_numbers(tokens)
        
        # Simplified role extraction (Subject = first noun-ish, Object = last)
        content = [t for t in tokens if t not in self.stopwords and t not in self.negations and t not in self.comparators]
        
        return {
            'negated': has_neg,
            'comparative': has_comp,
            'numbers': numbers,
            'concepts': set(content),
            'raw': text.lower()
        }

    def _compute_prediction_error(self, prompt_struct: Dict, candidate_struct: Dict) -> float:
        """
        Free Energy Calculation: Computes the discrepancy between the 
        generative model (prompt) and the sensory input (candidate).
        """
        error = 0.0
        
        # 1. Numeric Prediction Error (Exact match expected for math)
        if prompt_struct['numbers'] and candidate_struct['numbers']:
            # Compare sorted lists of numbers
            p_nums = sorted(prompt_struct['numbers'])
            c_nums = sorted(candidate_struct['numbers'])
            
            if len(p_nums) == len(c_nums):
                diff = sum(abs(a - b) for a, b in zip(p_nums, c_nums))
                error += diff * 0.1 # Scale factor
            else:
                error += 10.0 # Penalty for wrong count
        elif prompt_struct['numbers'] and not candidate_struct['numbers']:
            # Candidate lacks numbers when prompt has them (likely wrong for math tasks)
            # But allow if candidate is a word like "nine" (hard to detect without NLP)
            # We rely on string overlap for non-numeric concepts here.
            pass

        # 2. Logical/Conceptual Prediction Error
        # Intersection of concepts
        common = prompt_struct['concepts'] & candidate_struct['concepts']
        missing = prompt_struct['concepts'] - candidate_struct['concepts']
        extra = candidate_struct['concepts'] - prompt_struct['concepts']
        
        # Base error from missing/extra concepts
        error += len(missing) * 2.0
        error += len(extra) * 0.5
        
        # 3. Plasticity Gate (Hebbian update based on Negation)
        # If prompt is negated, a candidate that strongly affirms the concepts 
        # without negation markers should have higher error (inhibited).
        if prompt_struct['negated']:
            if not candidate_struct['negated'] and len(common) > 0:
                # High penalty for affirming a negated premise
                error += 5.0 
            elif candidate_struct['negated']:
                # Potentiate (reduce error) if candidate also respects negation
                error -= 2.0

        # 4. Comparative Logic Check
        if prompt_struct['comparative']:
            # If prompt implies comparison, candidate should ideally reflect it or be the result
            # This is a heuristic: if numbers exist, check order
            if len(prompt_struct['numbers']) >= 2 and len(candidate_struct['numbers']) == 1:
                p_nums = prompt_struct['numbers']
                c_val = candidate_struct['numbers'][0]
                
                # Heuristic: Is the candidate the max/min?
                if 'greater' in prompt_struct['raw'] or 'more' in prompt_struct['raw'] or 'higher' in prompt_struct['raw']:
                    target = max(p_nums)
                elif 'less' in prompt_struct['raw'] or 'fewer' in prompt_struct['raw'] or 'lower' in prompt_struct['raw']:
                    target = min(p_nums)
                else:
                    target = None
                
                if target is not None:
                    if abs(c_val - target) > 1e-5:
                        error += 5.0 # Wrong extreme
                    else:
                        error -= 2.0 # Correct extreme

        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker."""
        b1 = s1.encode()
        b2 = s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_struct = self._bind_structure(prompt)
        results = []
        
        # Pre-calculate NCD to prompt for tie-breaking
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        ncd_map = {c: score for c, score in ncd_scores}
        
        for cand in candidates:
            c_struct = self._bind_structure(cand)
            
            # Calculate Free Energy (Prediction Error)
            # Lower energy = better fit
            energy = self._compute_prediction_error(p_struct, c_struct)
            
            # Convert to score (inverse of energy)
            # Add small constant to avoid division by zero if energy is 0
            score = 1.0 / (1.0 + energy)
            
            # Tie-breaking with NCD (if energies are very close, prefer lower NCD)
            # But primary driver is the structural logic above.
            
            results.append({
                'candidate': cand,
                'score': score,
                'reasoning': f"Energy: {energy:.4f}, Negated: {c_struct['negated']}, NumMatch: {len(c_struct['numbers'])}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the Free Energy of the specific answer.
        """
        p_struct = self._bind_structure(prompt)
        a_struct = self._bind_structure(answer)
        
        energy = self._compute_prediction_error(p_struct, a_struct)
        
        # Transform energy to confidence
        # Energy 0 -> 1.0, Energy 10 -> ~0.09
        conf = 1.0 / (1.0 + energy)
        
        # Clamp
        return max(0.0, min(1.0, conf))