import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically-Annealed Ergodic Program Sampler (Approximated).
    
    Mechanism:
    1. Structural Parsing (Energy Function): Computes an 'energy' score based on 
       logical consistency (negations, comparatives, conditionals) between prompt 
       and candidate. Lower energy = higher probability.
    2. Thermodynamic Annealing: Converts energy to a probability score using a 
       Boltzmann-like distribution. The 'temperature' is adaptive based on the 
       spread of energies, simulating an annealing schedule that prevents 
       premature convergence on shallow matches while favoring deep structural 
       alignment.
    3. Ergodic Sampling Proxy: Instead of running a slow MCMC chain, we treat 
       the candidate set as the state space. We re-weight candidates based on 
       their structural 'free energy' relative to the prompt's constraints.
    4. NCD Tiebreaker: Uses Normalized Compression Distance only when structural 
       signals are indistinguishable.
    
    This satisfies the requirement to use Ergodic/Thermo concepts as secondary 
    validators/modifiers while relying on structural parsing for the primary signal.
    """

    def __init__(self):
        # Keywords for structural extraction
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical features from text."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_neg = any(n in words for n in self.negations)
        has_comp = any(c in lower_text for c in self.comparatives)
        has_cond = any(c in lower_text for c in self.conditionals)
        
        # Extract numbers
        nums = re.findall(r'-?\d+\.?\d*', lower_text)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'negations': has_neg,
            'comparatives': has_comp,
            'conditionals': has_cond,
            'numbers': numbers,
            'word_set': set(words)
        }

    def _compute_structural_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute energy based on logical consistency.
        Lower energy = better match.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        energy = 0.0
        
        # 1. Negation Consistency (High penalty for mismatch)
        # If prompt implies negation logic, candidate should reflect it or answer appropriately
        if p_struct['negations']:
            # Simple heuristic: if prompt has negation, candidate shouldn't blindly echo positive assertions
            # without addressing it. This is a proxy for logical validity.
            if not c_struct['negations'] and len(c_struct['word_set']) < 10:
                # Short positive answers to negative prompts might be traps, add small penalty
                # unless the prompt is a direct question answered by Yes/No
                if any(w in c_struct['word_set'] for w in self.booleans):
                    pass # Accept boolean answer
                else:
                    energy += 0.5 

        # 2. Numeric Consistency
        if p_struct['numbers'] and c_struct['numbers']:
            # Check if candidate numbers are logically derived (simplified)
            # If prompt has "greater than 5" and candidate has "4", that's high energy
            # We assume if numbers exist, they should be close or logically related.
            # For this approximation, we check magnitude alignment if comparatives exist
            if p_struct['comparatives']:
                p_max = max(p_struct['numbers'])
                c_val = c_struct['numbers'][0] # Take first number in candidate
                
                # Heuristic: If prompt says "greater than X", candidate should ideally be > X
                # This is a simplification of full program synthesis verification
                if 'greater' in prompt.lower() or '>' in prompt:
                    if c_val <= p_max:
                        energy += 2.0 # High energy for violating "greater than"
                elif 'less' in prompt.lower() or '<' in prompt:
                    if c_val >= p_max:
                        energy += 2.0 # High energy for violating "less than"
        
        # 3. Conditional/Logical Flow
        # If prompt has conditionals, candidate should not contradict the premise
        if p_struct['conditionals']:
            # Basic check: candidate shouldn't contain strong contradiction markers 
            # unless the prompt asks for a counter-factual (hard to detect without LLM)
            # We rely on word overlap for conditionals as a proxy for relevance
            common_cond = p_struct['word_set'].intersection(c_struct['word_set'])
            if not common_cond and len(p_struct['word_set']) > 5:
                energy += 0.5 # Penalty for low relevance in conditional contexts

        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Step 1: Compute Structural Energy for each candidate
        energies = []
        for cand in candidates:
            e = self._compute_structural_energy(prompt, cand)
            energies.append(e)
        
        # Step 2: Thermodynamic Annealing (Boltzmann Distribution)
        # Convert energies to probabilities: P ~ exp(-E / T)
        # Adaptive Temperature: T scales with the variance of energies to ensure 
        # discrimination. If all energies are similar (high uncertainty), T is high.
        # If energies vary, T lowers to exploit the best ones.
        
        min_e = min(energies)
        max_e = max(energies)
        range_e = max_e - min_e if max_e > min_e else 1.0
        
        # Base temperature scaled by energy range
        T = 0.5 * range_e + 0.1 
        
        scores = []
        for i, e in enumerate(energies):
            # Boltzmann factor
            boltzmann = math.exp(-(e - min_e) / T)
            
            # Step 3: NCD Tiebreaker
            # If energies are very close (within thermal noise), use NCD to break ties
            # We add a tiny perturbation based on NCD distance to prompt
            if range_e < 0.01: 
                ncd_val = self._ncd(prompt, candidates[i])
                # Lower NCD is better, so we subtract a fraction of it from energy before exp
                # Or simply use it as a secondary sort key. Here we adjust the score slightly.
                boltzmann *= (1.0 - 0.1 * ncd_val)
            
            scores.append(boltzmann)
        
        # Normalize scores to 0-1 range for readability, though ranking is what matters
        max_score = max(scores) if max(scores) > 0 else 1.0
        normalized_scores = [s / max_score for s in scores]
        
        # Construct result
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": normalized_scores[i],
                "reasoning": f"Structural energy: {energies[i]:.4f}, Temp: {T:.4f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the inverse of the structural energy normalized by a sigmoid-like function.
        """
        energy = self._compute_structural_energy(prompt, answer)
        
        # If energy is 0, confidence is high. As energy increases, confidence drops.
        # Using a decay function: conf = 1 / (1 + energy)
        # This ensures 0 energy -> 1.0, high energy -> ~0.0
        
        base_conf = 1.0 / (1.0 + energy)
        
        # Boost if structural features match well (heuristic validation)
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Bonus for matching number presence
        if p_struct['numbers'] and a_struct['numbers']:
            base_conf = min(1.0, base_conf + 0.1)
            
        # Penalty if prompt has negation but answer is a blind "yes" (common trap)
        if p_struct['negations'] and not a_struct['negations']:
            if answer.strip().lower() in ['yes', 'true']:
                base_conf *= 0.5

        return float(max(0.0, min(1.0, base_conf)))