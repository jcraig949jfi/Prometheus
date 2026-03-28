import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Graph-Structured Active Inference Engine (Simplified for Standard Lib).
    
    Mechanism:
    1. Structural Parsing (Graph Nodes): Extracts logical operators (negations, comparatives,
       conditionals) and numeric literals as latent variables in a probabilistic graph.
    2. Free Energy Minimization (Evaluation): Computes a 'surprise' score (Free Energy) for
       each candidate. Lower Free Energy = Better Fit.
       F = Prediction_Error (Logical/Numeric mismatch) + Complexity (Length penalty).
    3. Active Inference (Ranking): Candidates are ranked by their ability to minimize F.
       The system 'prunes' candidates that violate structural constraints (high error)
       or introduce unnecessary complexity.
    4. NCD Tiebreaker: Used only when structural signals are identical.
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Graph Topology")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none|cannot|won\'t|don\'t|isn\'t|aren\'t)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|while)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'boolean_true': re.compile(r'\b(true|yes|correct|valid)\b', re.I),
            'boolean_false': re.compile(r'\b(false|no|incorrect|invalid)\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict:
        """Parses text into structural features (latent variables)."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'asserts_true': bool(self.patterns['boolean_true'].search(text)),
            'asserts_false': bool(self.patterns['boolean_false'].search(text)),
            'length': len(text.split())
        }
        return features

    def _compute_prediction_error(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Computes expected prediction error based on structural consistency.
        High error = High Free Energy contribution.
        """
        error = 0.0
        
        # 1. Logical Consistency (Negation Flip Check)
        # If prompt has negation, candidate should ideally reflect it or not contradict directly
        if prompt_feat['has_negation'] != cand_feat['has_negation']:
            # Soft penalty for mismatched negation structure
            error += 2.5
            
        # 2. Numeric Consistency (Transitivity/Comparison)
        # If both have numbers, check magnitude alignment with comparatives
        if prompt_feat['numbers'] and cand_feat['numbers']:
            p_nums = prompt_feat['numbers']
            c_nums = cand_feat['numbers']
            
            # Simple heuristic: Do they agree on order of magnitude or specific values?
            # If prompt implies a value and candidate contradicts it directly
            if len(p_nums) == len(c_nums):
                for p, c in zip(p_nums, c_nums):
                    if p != 0 and abs(p - c) / (abs(p) + 1e-9) > 0.5: # >50% deviation
                        error += 3.0
            elif prompt_feat['has_comparative']:
                # If prompt compares, candidate numbers should reflect that relation
                # Simplified: Check if max/min align
                if (max(p_nums) > min(p_nums)) and (max(c_nums) < min(c_nums)):
                    error += 4.0 # Direct contradiction of order

        # 3. Boolean Contradiction
        if prompt_feat['asserts_true'] and cand_feat['asserts_false']:
            error += 5.0
        if prompt_feat['asserts_false'] and cand_feat['asserts_true']:
            error += 5.0
            
        return error

    def _compute_complexity(self, cand_feat: Dict) -> float:
        """Complexity term (KL divergence approximation): Penalize unnecessary length."""
        # Occam's razor: Prefer shorter explanations if error is low
        return 0.1 * cand_feat['length']

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        F = Expected Prediction Error + Complexity - Entropy (approximated)
        We minimize F. Lower F = Better Candidate.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        prediction_error = self._compute_prediction_error(p_feat, c_feat)
        complexity = self._compute_complexity(c_feat)
        
        # Entropy term is hard to estimate without a distribution, 
        # so we rely on the error+complexity trade-off typical in variational bounds.
        free_energy = prediction_error + complexity
        
        return free_energy

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / (max(c1, c2) - min_len + 1e-9)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Step 1: Compute Free Energy for all candidates
        results = []
        for cand in candidates:
            fe = self._calculate_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "free_energy": fe,
                "structural_score": -fe # Invert because lower FE is better
            })
        
        # Step 2: Check for ties in structural score to apply NCD tiebreaker
        # Group by rounded structural score to handle float precision
        tolerance = 0.5
        for i, res in enumerate(results):
            score = res['structural_score']
            # Find if there are neighbors with similar scores
            is_tie = False
            for j, other in enumerate(results):
                if i != j and abs(other['structural_score'] - score) < tolerance:
                    is_tie = True
                    break
            
            if is_tie:
                # Apply NCD as tiebreaker: Lower NCD to prompt is better
                ncd = self._ncd_distance(prompt, res['candidate'])
                # Adjust score slightly by NCD (negative because lower NCD is better)
                # We subtract a small fraction of NCD so it acts as a tiebreaker, not primary driver
                res['final_score'] = score - (ncd * 0.1)
            else:
                res['final_score'] = score

        # Sort by final score descending (higher is better)
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Normalize scores to 0-1 range for output consistency
        min_fe = results[-1]['free_energy'] if results else 0
        max_fe = results[0]['free_energy'] if results else 0
        range_fe = max_fe - min_fe if (max_fe - min_fe) > 1e-9 else 1.0
        
        output = []
        for res in results:
            # Convert Free Energy to a probability-like score (0-1)
            # Since we minimized FE, low FE -> High Score
            norm_score = 1.0 - ((res['free_energy'] - min_fe) / range_fe)
            norm_score = max(0.0, min(1.0, norm_score)) # Clamp
            
            output.append({
                "candidate": res['candidate'],
                "score": round(norm_score, 4),
                "reasoning": f"Free Energy: {res['free_energy']:.2f} (Error+Complexity). Lower is better."
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low Free Energy -> High Confidence.
        """
        fe = self._calculate_free_energy(prompt, answer)
        
        # Map Free Energy to Confidence
        # Heuristic: FE < 1.0 is very confident, FE > 5.0 is very low confidence
        # Using an exponential decay similar to Boltzmann distribution
        confidence = math.exp(-fe)
        
        return round(min(1.0, max(0.0, confidence)), 4)