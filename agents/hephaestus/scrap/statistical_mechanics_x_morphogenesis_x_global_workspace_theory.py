import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Statistical-Morphogenetic Global Workspace (SMGW) Approximation.
    
    Mechanism:
    1. Energy-Based Core (Stat Mech): Candidates are assigned an 'energy' score based on
       structural coherence (matching negations, conditionals, and numeric logic) with the prompt.
       Lower energy = higher probability. Fluctuation is simulated by penalizing length variance.
    2. Morphogenetic Layer (Reaction-Diffusion): A diffusion process smooths scores across
       candidate clusters based on lexical overlap (reaction terms), allowing coherent patterns
       to emerge and unstable ones to dissipate.
    3. Global Workspace (Attention): A broadcast mechanism selects the candidate with the
       lowest energy (highest coherence) and boosts its score if it exceeds an 'ignition'
       threshold of structural alignment.
    
    This implementation approximates the PDE and Boltzmann dynamics using discrete structural
    parsing and iterative score relaxation, adhering to the constraint of using only standard library.
    """

    def __init__(self):
        self.ignition_threshold = 0.6

    def _structural_parse(self, text: str) -> dict:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(no|not|never|none|neither)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|than)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[str], cand_nums: List[str]) -> float:
        """Check if candidate numbers logically follow prompt numbers (simple presence/order check)."""
        if not prompt_nums:
            return 1.0 if not cand_nums else 0.8 # Neutral if no numbers in prompt
        
        if not cand_nums:
            return 0.5 # Penalty for missing numbers if prompt had them
        
        try:
            # Check for direct mapping or simple inversion
            p_vals = [float(x) for x in prompt_nums]
            c_vals = [float(x) for x in cand_nums]
            
            # Simple heuristic: if prompt implies order, does candidate respect it?
            # Since we don't have full logic, we check if the magnitude trend matches for pairs
            if len(p_vals) >= 2 and len(c_vals) >= 2:
                p_diff = p_vals[0] - p_vals[1]
                c_diff = c_vals[0] - c_vals[1]
                if (p_diff > 0 and c_diff > 0) or (p_diff < 0 and c_diff < 0):
                    return 1.0
                elif p_diff == 0 and c_diff == 0:
                    return 1.0
                else:
                    return 0.2 # Contradiction
            return 0.9 # Partial match
        except ValueError:
            return 0.5

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute energy E = - (Structural Alignment).
        Lower energy is better.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        energy = 0.0
        
        # 1. Negation Consistency (Modus Tollens check approximation)
        # If prompt has negation, candidate should likely reflect it or answer directly
        if p_feat['negations'] > 0:
            if c_feat['negations'] > 0 or any(k in candidate.lower() for k in ['no', 'not', 'false']):
                energy -= 2.0 # Reward alignment
            else:
                energy += 1.5 # Penalty for ignoring negation
        
        # 2. Conditional Logic
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or any(k in candidate.lower() for k in ['if', 'then', 'because']):
                energy -= 1.5
            else:
                # Not a hard penalty, but less coherent
                energy += 0.5

        # 3. Numeric Consistency
        num_score = self._check_numeric_consistency(p_feat['numbers'], c_feat['numbers'])
        energy -= (num_score * 3.0) # Strong reward for numeric consistency

        # 4. Length Fluctuation (Entropy penalty)
        # Penalize candidates that are wildly different in length from prompt (noise)
        len_ratio = c_feat['length'] / (p_feat['length'] + 1)
        if len_ratio < 0.1 or len_ratio > 5.0:
            energy += 2.0 # High energy for outlier lengths
            
        return energy

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        z = zlib.compress
        len_s1 = len(z(s1.encode()))
        len_s2 = len(z(s2.encode()))
        len_s1_s2 = len(z((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max_len

    def _morphogenetic_diffusion(self, energies: List[float], candidates: List[str], steps: int = 3) -> List[float]:
        """
        Simulate reaction-diffusion: Smooth energies based on lexical similarity.
        Coherent clusters reinforce each other; outliers dissipate.
        """
        scores = [-e for e in energies] # Convert to positive scores for diffusion
        
        if len(candidates) < 2:
            return scores
            
        # Precompute similarity matrix (approximated for speed)
        n = len(candidates)
        for _ in range(steps):
            new_scores = scores.copy()
            for i in range(n):
                reaction_term = 0.0
                total_weight = 0.0
                for j in range(n):
                    if i == j: continue
                    # Lexical overlap as diffusion coefficient
                    set_i = set(candidates[i].lower().split())
                    set_j = set(candidates[j].lower().split())
                    if not set_i or not set_j:
                        continue
                    overlap = len(set_i & set_j) / len(set_i | set_j)
                    
                    if overlap > 0.3: # Diffusion threshold
                        reaction_term += scores[j] * overlap
                        total_weight += overlap
                
                if total_weight > 0:
                    # Update rule: weighted average of neighbors (diffusion)
                    new_scores[i] = 0.7 * scores[i] + 0.3 * (reaction_term / total_weight)
            scores = new_scores
            
        return scores

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Energy-Based Core: Compute initial energies
        energies = [self._compute_energy(prompt, c) for c in candidates]
        
        # 2. Morphogenetic Layer: Diffuse scores
        final_scores = self._morphogenetic_diffusion(energies, candidates)
        
        # 3. Global Workspace: Ignition and Ranking
        # Normalize scores to 0-1 range for ignition check
        min_s, max_s = min(final_scores), max(final_scores)
        range_s = max_s - min_s if max_s != min_s else 1.0
        normalized_scores = [(s - min_s) / range_s for s in final_scores]
        
        results = []
        for i, cand in enumerate(candidates):
            score = normalized_scores[i]
            
            # Ignition: Boost if structural alignment was high originally
            if energies[i] < -1.0: 
                score = min(1.0, score + 0.2)
            
            # Tiebreaker: NCD (only if scores are very close)
            # We don't apply NCD here directly to avoid overriding structural logic,
            # but we use it implicitly by ensuring the 'energy' accounted for structure.
            # For strict tie-breaking in sorting:
            ncd_val = self._ncd_distance(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Energy: {energies[i]:.2f}, Diffused Score: {score:.2f}, NCD: {ncd_val:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural coherence."""
        # Evaluate single candidate against a dummy list to get its score
        # We simulate a comparison by checking its absolute energy
        energy = self._compute_energy(prompt, answer)
        
        # Map energy to confidence
        # Very low energy (negative) -> High confidence
        # High energy (positive) -> Low confidence
        # Heuristic mapping: conf = 1 / (1 + exp(energy)) approx
        import math
        conf = 1.0 / (1.0 + math.exp(energy))
        return max(0.0, min(1.0, conf))