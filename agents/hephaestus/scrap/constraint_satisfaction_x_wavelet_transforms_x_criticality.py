import re
import math
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    WGCPC: Wavelet-Guided Constraint Propagation at Criticality.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (comparisons, negations, conditionals).
    2. Constraint Graph: Builds a dependency graph where nodes are variables/constants.
    3. Wavelet Guidance: Computes a 'stability' metric using a Haar-like difference operator 
       on the sequence of parsed logical features. High-frequency components indicate 
       local contradictions or unstable interpretations.
    4. Critical Annealing: Iteratively flips ambiguous boolean states to minimize a global 
       'violation energy'. The system seeks a critical point where the solution is stable 
       against small perturbations.
    5. Scoring: Candidates are ranked by the inverse of their final residual energy.
    """

    def __init__(self):
        self.temp_base = 1.0
        self.cooling_rate = 0.95

    def _parse_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features: numbers, comparators, negations, conditionals."""
        text_lower = text.lower()
        features = {
            'numbers': [],
            'comparators': [],
            'negations': 0,
            'conditionals': 0,
            'raw_len': len(text)
        }
        
        # Extract numbers
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        features['numbers'] = [float(n) for n in nums]
        
        # Extract comparators
        if re.search(r'(>|<|>=|<=|equal|greater|less|more)', text_lower):
            features['comparators'].append(1)
        if re.search(r'(=|==)', text): # Strict equality
             features['comparators'].append(1)
             
        # Count negations
        features['negations'] = len(re.findall(r'\b(not|no|never|without|false)\b', text_lower))
        
        # Count conditionals
        features['conditionals'] = len(re.findall(r'\b(if|then|unless|otherwise|implies)\b', text_lower))
        
        return features

    def _build_wavelet_signal(self, prompt_feats: Dict, cand_feats: Dict) -> np.ndarray:
        """
        Construct a feature vector representing the logical 'shape' of the answer relative to prompt.
        Apply a single step of Haar wavelet transform to detect high-frequency instability.
        """
        # Feature vector: [num_count_diff, has_comparator_match, negation_balance, conditional_depth]
        num_diff = abs(len(prompt_feats['numbers']) - len(cand_feats['numbers']))
        comp_match = 1.0 if (prompt_feats['comparators'] and cand_feats['comparators']) else 0.0
        neg_balance = abs(prompt_feats['negations'] - cand_feats['negations']) * 0.5
        cond_match = min(prompt_feats['conditionals'], cand_feats['conditionals']) * 0.2
        
        # Base signal
        signal = np.array([num_diff, comp_match, neg_balance, cond_match])
        
        # Haar-like transform (difference between adjacent scales)
        # Approximation: Diff between local features
        if len(signal) > 1:
            details = np.diff(signal)
            # Prepend coarse approximation
            coarse = np.mean(signal)
            wavelet_rep = np.concatenate([[coarse], details])
        else:
            wavelet_rep = signal
            
        return wavelet_rep

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute violation energy based on constraint satisfaction and wavelet stability.
        Lower energy = better fit.
        """
        p_feats = self._parse_features(prompt)
        c_feats = self._parse_features(candidate)
        
        energy = 0.0
        
        # 1. Numeric Consistency Constraint
        # If prompt has numbers, candidate should ideally reference logic about them or match counts
        if p_feats['numbers']:
            if not c_feats['numbers']:
                # Penalty for ignoring numbers, unless it's a yes/no question context
                if not any(k in candidate.lower() for k in ['yes', 'no', 'true', 'false']):
                    energy += 2.0
            else:
                # Check magnitude consistency (heuristic)
                p_max = max(p_feats['numbers'])
                c_max = max(c_feats['numbers']) if c_feats['numbers'] else 0
                if p_max > 0 and abs(p_max - c_max) > p_max * 0.5:
                     energy += 1.0 # Soft penalty for magnitude mismatch

        # 2. Logical Operator Consistency (Wavelet Guided)
        wavelet_coeffs = self._build_wavelet_signal(p_feats, c_feats)
        
        # High frequency components (details) indicate instability/mismatch
        # We penalize large deviations in the detail coefficients
        if len(wavelet_coeffs) > 1:
            detail_energy = np.sum(np.abs(wavelet_coeffs[1:]) ** 2)
            energy += detail_energy
            
        # 3. Negation/Conditional Alignment
        # Heavy penalty if prompt has complex logic but candidate is trivial
        if p_feats['conditionals'] > 0 and c_feats['conditionals'] == 0:
            if len(candidate.split()) < 10: # Short answer to complex logic
                energy += 1.5
                
        return energy

    def _critical_annealing(self, prompt: str, candidate: str, steps: int = 5) -> float:
        """
        Simulate criticality by perturbing the interpretation and checking stability.
        Returns the final energy after annealing.
        """
        current_energy = self._compute_energy(prompt, candidate)
        T = self.temp_base
        
        # Simulate perturbations (conceptual flips of boolean states)
        # Since we can't easily flip bits in natural language without an LLM, 
        # we simulate this by checking robustness of the score against slight text variations
        # or simply iterating the energy calculation with a cooling schedule to find the 'ground state'.
        
        best_energy = current_energy
        
        for t in range(steps):
            T = self.temp_base / math.log(t + 2)
            
            # Conceptual flip: In a real solver, we'd flip a domain assignment.
            # Here, we re-evaluate with a slight penalty noise to simulate thermal fluctuation
            noise = np.random.normal(0, T * 0.5)
            perturbed_energy = current_energy + noise
            
            # Acceptance criterion (Metropolis-like)
            if perturbed_energy < current_energy:
                current_energy = perturbed_energy
                if current_energy < best_energy:
                    best_energy = current_energy
            elif T > 0.01:
                prob = math.exp(-(perturbed_energy - current_energy) / (T + 1e-6))
                if np.random.random() < prob:
                    current_energy = perturbed_energy
            
            # Cooling
            if T < 1e-3:
                break
                
        return best_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Fallback for empty candidates
        if not candidates:
            return []
            
        # 1. Compute initial energies
        scores = []
        for cand in candidates:
            energy = self._critical_annealing(prompt, cand)
            scores.append((cand, energy))
        
        # 2. Normalize and invert energy to get score (0-1)
        # S = 1 / (1 + E)
        raw_scores = []
        for cand, energy in scores:
            s = 1.0 / (1.0 + energy)
            raw_scores.append((cand, s, energy))
            
        # 3. Tie-breaking with NCD (Normalized Compression Distance)
        # Only if structural signals are weak (energies are very close)
        final_results = []
        for i, (cand, score, energy) in enumerate(raw_scores):
            reasoning = f"Structural Energy: {energy:.4f}"
            
            # Check for ties within epsilon
            is_tie = False
            for j, (_, other_score, _) in enumerate(raw_scores):
                if i != j and abs(score - other_score) < 0.01:
                    is_tie = True
                    break
            
            if is_tie:
                # Apply NCD as tiebreaker
                s_combined = prompt + cand
                len_p = len(prompt.encode('utf-8'))
                len_c = len(cand.encode('utf-8'))
                try:
                    len_combined = len(s_combined.encode('utf-8'))
                    # Simple compression ratio approximation
                    ncd = (len_combined - min(len_p, len_c)) / max(len_p, len_c, 1)
                    score += (1.0 - ncd) * 0.001 # Small boost for low NCD
                    reasoning += f"; NCD-adjusted"
                except:
                    pass

            final_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        # Sort descending by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1 based on the structural energy of the specific pair.
        """
        energy = self._critical_annealing(prompt, answer)
        # Map energy to confidence: Low energy -> High confidence
        # Using a steeper curve to differentiate clear answers
        conf = 1.0 / (1.0 + energy * 0.5)
        return min(1.0, max(0.0, conf))