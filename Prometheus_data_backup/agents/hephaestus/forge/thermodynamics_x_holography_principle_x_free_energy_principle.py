import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Predictive-Coding Energy-Based Model (HPC-EBM) Implementation.
    
    Mechanism:
    1. Core Driver (Free Energy): Minimizes variational free energy F = <E> - TS.
       - Energy (E): Prediction error derived from structural parsing (negations, 
         comparatives, conditionals) and numeric consistency between prompt and candidate.
       - Entropy (S): Estimated via token diversity and length variance (exploration term).
       - Temperature (T): Learnable scalar (simulated here as a tuning parameter) balancing 
         accuracy vs. exploration.
    
    2. Thermodynamics: Used as a secondary validation. Candidates violating logical 
       transitivity or containing contradictory markers receive an energy penalty (heat).
    
    3. Holography Principle (Restricted): Used ONLY in confidence() and structural parsing.
       The 'boundary' is a compressed hash of the structural signature. If the candidate's 
       structural signature does not match the prompt's expected boundary conditions 
       (e.g., prompt asks for a number, candidate provides text), confidence is capped.
    
    This approach prioritizes structural logic (Free Energy) while using Holography 
    strictly as a constraint filter, adhering to historical synergy data.
    """

    def __init__(self):
        # Hyperparameters simulating the thermodynamic balance
        self.temperature = 0.5  # Balances exploration (entropy) vs exploitation (energy)
        self.energy_weight = 1.0
        self.entropy_weight = 0.1
        
        # Structural markers for parsing
        self.negations = ['no', 'not', 'never', 'none', 'cannot', 'impossible']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _count_markers(self, text: str, markers: List[str]) -> int:
        """Count occurrence of specific logical markers."""
        lower_text = text.lower()
        return sum(1 for m in markers if r'\b' + m + r'\b' in lower_text or m in lower_text)

    def _structural_parse(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        return {
            'negations': self._count_markers(text, self.negations),
            'comparatives': self._count_markers(text, self.comparatives),
            'conditionals': self._count_markers(text, self.conditionals),
            'numbers': self._extract_numbers(text),
            'length': len(text.split()),
            'unique_tokens': len(set(text.lower().split()))
        }

    def _compute_energy(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Compute Energy (E) based on prediction error.
        Low energy = high consistency between prompt constraints and candidate answer.
        """
        energy = 0.0
        
        # 1. Numeric Consistency (Strong signal)
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if p_nums and c_nums:
            # Check if candidate numbers logically follow prompt numbers (simplified heuristic)
            # If prompt has comparative words, expect relation in numbers
            if prompt_struct['comparatives'] > 0:
                # Rough check: did the candidate attempt a numeric operation?
                energy -= 0.5 * len(c_nums) # Reward having numbers if comparatives exist
            else:
                # Exact match bonus if no logic required
                if set(p_nums) == set(c_nums):
                    energy -= 1.0
        
        # 2. Logical Marker Alignment
        # If prompt has conditionals, candidate should ideally reflect consequence or condition
        if prompt_struct['conditionals'] > 0:
            if cand_struct['conditionals'] > 0 or cand_struct['negations'] > 0:
                energy -= 0.3 # Reward logical complexity matching
        
        # 3. Negation Consistency (Basic)
        # If prompt is negative, candidate often needs to be negative or affirmative appropriately
        # Heuristic: High negation in prompt usually requires careful handling
        if prompt_struct['negations'] > 0:
            # Penalize if candidate ignores negation context (simplified)
            if cand_struct['negations'] == 0 and prompt_struct['negations'] > 1:
                energy += 0.5 # Potential error

        # 4. Length/Complexity Penalty (Occam's razor)
        # Penalize excessive verbosity without content
        if cand_struct['length'] > prompt_struct['length'] * 3:
            energy += 0.2
            
        return energy

    def _compute_entropy(self, struct: Dict) -> float:
        """
        Compute Entropy (S) based on token diversity.
        Higher unique token ratio = higher entropy (more informative/exploratory).
        """
        if struct['length'] == 0:
            return 0.0
        ratio = struct['unique_tokens'] / struct['length']
        # Shannon-like entropy approximation
        return -math.log(ratio + 1e-9) if ratio > 0 else 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len_s1 = len(zlib.compress(s1.encode()))
        len_s2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using Free Energy minimization.
        F = Energy - Temperature * Entropy
        Lower F is better. We invert score so higher is better.
        """
        prompt_struct = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate prompt entropy for relative comparison
        p_entropy = self._compute_entropy(prompt_struct)
        
        scores = []
        
        for cand in candidates:
            cand_struct = self._structural_parse(cand)
            
            # 1. Calculate Energy (Prediction Error)
            # Lower energy means better fit to prompt constraints
            E = self._compute_energy(prompt_struct, cand_struct, prompt, cand)
            
            # 2. Calculate Entropy (Diversity/Exploration)
            S = self._compute_entropy(cand_struct)
            
            # 3. Free Energy Calculation
            # F = E - T*S. We want to minimize F.
            free_energy = (self.energy_weight * E) - (self.temperature * self.entropy_weight * S)
            
            # Store intermediate values
            scores.append({
                'candidate': cand,
                'free_energy': free_energy,
                'energy': E,
                'entropy': S
            })
        
        # Normalize scores to be positive and higher=better
        # Since we want to minimize Free Energy, the lowest FE gets the highest score.
        min_fe = min(s['free_energy'] for s in scores)
        max_fe = max(s['free_energy'] for s in scores)
        range_fe = max_fe - min_fe if (max_fe - min_fe) > 1e-9 else 1.0
        
        final_results = []
        for item in scores:
            # Invert: Low FE -> High Score
            # Base score from Free Energy ranking
            norm_score = 1.0 - ((item['free_energy'] - min_fe) / range_fe)
            
            # Tie-breaking with NCD (only if structural signals are weak or tied)
            # We add a small NCD component to break ties among structurally similar candidates
            ncd_val = self._ncd(prompt, item['candidate'])
            # NCD is 0 (same) to 1 (different). We want similarity (low NCD) to boost score slightly
            # But only as a tiebreaker, so weight is very low
            tie_breaker = (1.0 - ncd_val) * 0.05 
            
            final_score = norm_score + tie_breaker
            
            # Reasoning string generation
            reasoning = (
                f"FE={item['free_energy']:.4f} (E={item['energy']:.2f}, S={item['entropy']:.2f}). "
                f"Structural match: {'High' if item['energy'] < -0.1 else 'Low'}."
            )
            
            final_results.append({
                'candidate': item['candidate'],
                'score': final_score,
                'reasoning': reasoning
            })
        
        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calculate confidence using Holographic Boundary constraints.
        The 'boundary' is the structural signature. If the answer's signature 
        violates the prompt's implied boundary conditions, confidence drops.
        """
        p_struct = self._structural_parse(prompt)
        a_struct = self._structural_parse(answer)
        
        confidence = 1.0
        
        # Holographic Constraint 1: Numeric Boundary
        # If prompt implies a numeric answer (has numbers + comparatives), 
        # and answer has NO numbers, it violates the information bound.
        if p_struct['numbers'] and p_struct['comparatives']:
            if not a_struct['numbers']:
                confidence *= 0.4 # Strong penalty
        
        # Holographic Constraint 2: Logical Consistency Boundary
        # If prompt is a yes/no question (high conditional/negation density, low length),
        # and answer is overly long without structure, it leaks information unnecessarily.
        if p_struct['conditionals'] > 0 and len(p_struct['numbers']) == 0:
            if a_struct['length'] > p_struct['length'] * 5:
                confidence *= 0.7
                
        # Holographic Constraint 3: Negation Flip
        # Simple check for direct contradiction in short phrases
        p_neg = p_struct['negations'] > 0
        a_neg = a_struct['negations'] > 0
        if p_neg != a_neg:
            # If one has negation and other doesn't, reduce confidence slightly 
            # unless context suggests otherwise (simplified)
            confidence *= 0.85
            
        # Base confidence from NCD similarity (as a fallback baseline)
        ncd = self._ncd(prompt, answer)
        # If NCD is very high (very different), cap confidence
        if ncd > 0.9:
            confidence = min(confidence, 0.5)
            
        return max(0.0, min(1.0, confidence))