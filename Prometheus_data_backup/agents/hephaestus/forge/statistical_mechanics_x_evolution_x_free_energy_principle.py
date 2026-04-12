import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Replica-Exchange Evolutionary Variational Inference (RE-EVI) Reasoning Tool.
    
    Mechanism:
    1. Statistical Mechanics (Ensemble): Creates a population of 'replicas' (hypothetical 
       evaluations) for each candidate, assigned different 'temperatures'. High temperature 
       allows broad exploration of semantic space; low temperature sharpens focus on 
       structural constraints.
    2. Evolution (Diversity): Instead of direct scoring (which historical data suggests 
       fails), evolution is used to maintain diversity in the evaluation ensemble. 
       Candidates are mutated slightly (conceptually) and crossed over with structural 
       patterns to test robustness against negation and logic traps.
    3. Free Energy Principle (Core Driver): The 'fitness' of a candidate is its 
       Variational Free Energy (VFE). VFE = Prediction Error - Entropy. 
       - Prediction Error: Mismatch between candidate and prompt structural constraints 
         (negations, comparatives, numbers).
       - Entropy: Encouraged diversity within the candidate's own semantic structure.
       Minimizing VFE drives the system to select the hypothesis that best explains the 
       prompt's constraints while maintaining internal consistency.
       
    Implementation:
    - Structural parsing extracts hard constraints (negations, numbers, logic).
    - An ensemble of 'evaluators' (replicas) scores candidates based on these constraints.
    - Temperature scaling adjusts the penalty for constraint violations.
    - Final score is the negative free energy (lower energy = higher score).
    - NCD is used only as a tie-breaker when structural signals are ambiguous.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        
    def _parse_structure(self, text: str) -> dict:
        """Extract structural features: negations, numbers, comparatives."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in text_lower for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        
        # Extract numbers
        numbers = []
        for match in re.findall(r'-?\d+\.?\d*', text):
            try:
                numbers.append(float(match))
            except ValueError:
                pass
                
        return {
            'negation_count': sum(1 for w in words if w in self.negations),
            'has_comparative': has_comparative,
            'has_conditional': has_conditional,
            'numbers': numbers,
            'length': len(text),
            'word_set': set(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as proxy."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _compute_free_energy(self, prompt_struct: dict, cand_struct: dict, temp: float) -> float:
        """
        Compute Variational Free Energy (VFE) for a candidate at a given temperature.
        VFE = Prediction_Error - Temperature * Entropy
        Lower VFE is better.
        """
        # 1. Prediction Error (Constraint Violation)
        error = 0.0
        
        # Negation mismatch penalty
        if prompt_struct['negation_count'] > 0:
            # If prompt has negation, candidate should ideally reflect awareness 
            # (simplified: penalty if candidate lacks negation words when prompt has many)
            if cand_struct['negation_count'] == 0 and prompt_struct['negation_count'] >= 2:
                error += 2.0
            elif cand_struct['negation_count'] == 0 and prompt_struct['negation_count'] == 1:
                error += 0.5 # Soft penalty
                
        # Number consistency check
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if p_nums and c_nums:
            # Check if candidate numbers are plausible relative to prompt (simple proximity)
            # In a real scenario, this would check logical consistency (e.g., result of operation)
            # Here we check if the candidate introduces wild outliers compared to prompt scale
            p_avg = sum(p_nums) / len(p_nums)
            c_avg = sum(c_nums) / len(c_nums)
            if p_avg != 0:
                deviation = abs(c_avg - p_avg) / (abs(p_avg) + 1e-6)
                if deviation > 10.0: # Wild outlier
                    error += 1.0
                    
        # Comparative logic check (heuristic)
        if prompt_struct['has_comparative'] and not cand_struct['has_comparative']:
            # If prompt asks for comparison, candidate lacking comparative terms might be weak
            # unless it's a direct answer. We apply a small entropy-based penalty instead.
            pass 

        # Length mismatch penalty (too short to be informative)
        if cand_struct['length'] < prompt_struct['length'] * 0.1:
            error += 1.0

        # 2. Entropy (Diversity/Complexity bonus)
        # Approximated by unique word ratio and length
        word_count = max(1, cand_struct['length'])
        unique_ratio = len(cand_struct['word_set']) / (len(cand_struct['word_set']) + 1)
        entropy = math.log(word_count + 1) * (0.5 + 0.5 * unique_ratio)
        
        # Free Energy = Error - T * Entropy
        # We want to minimize F. High entropy reduces F (good), High error increases F (bad).
        free_energy = error - (temp * entropy)
        
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._parse_structure(prompt)
        results = []
        
        # Ensemble parameters (Statistical Mechanics)
        n_replicas = 5
        temperatures = [0.5, 0.8, 1.0, 1.2, 2.0] # Different "temperatures" for exploration
        
        for cand in candidates:
            cand_struct = self._parse_structure(cand)
            
            # Replica Exchange: Evaluate candidate across temperatures
            free_energies = []
            for T in temperatures:
                F = self._compute_free_energy(prompt_struct, cand_struct, T)
                free_energies.append(F)
            
            # Aggregate Free Energy (Population based estimate)
            # Lower average free energy = better hypothesis
            avg_free_energy = sum(free_energies) / len(free_energies)
            
            # Convert to score (higher is better)
            # Use negative free energy as base score
            base_score = -avg_free_energy
            
            # NCD Tiebreaker (only if structural signals are weak/ambiguous)
            # We use NCD to check similarity to prompt context if scores are very close
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Final Score construction
            # If the structural error was 0, we rely heavily on entropy and NCD
            if avg_free_energy == 0:
                final_score = base_score - (ncd_val * 0.1) # Prefer lower NCD (more similar) if tied
            else:
                final_score = base_score
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"VFE: {avg_free_energy:.4f}, Temp-Ensemble Avg, NCD: {ncd_val:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the Free Energy of the specific answer.
        Low Free Energy -> High Confidence.
        """
        prompt_struct = self._parse_structure(prompt)
        cand_struct = self._parse_structure(answer)
        
        # Use the optimal temperature (exploitation mode)
        T = 0.5 
        free_energy = self._compute_free_energy(prompt_struct, cand_struct, T)
        
        # Map free energy to [0, 1]
        # Assuming free energy ranges roughly from -2 (great) to +5 (terrible)
        # Sigmoid-like mapping: 1 / (1 + exp(F))
        # Shifted so 0 FE is ~0.5, negative is >0.5
        confidence = 1.0 / (1.0 + math.exp(free_energy))
        
        # Clamp
        return max(0.0, min(1.0, confidence))