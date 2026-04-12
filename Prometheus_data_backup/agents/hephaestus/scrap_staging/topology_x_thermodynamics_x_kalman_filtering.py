import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topologically-Constrained, Entropy-Regularized Reasoning Tool (TCERKT).
    
    Mechanism:
    1. Topological Descriptor (Structural Parsing): Instead of computing persistent 
       homology on raw data (impossible for text), we compute the "persistence diagram" 
       of the logical structure. We extract features (negations, comparatives, conditionals)
       and treat their presence/absence as topological invariants (connected components).
       Candidates violating the prompt's structural invariants receive a high "topological penalty".
       
    2. Thermodynamic Potential (Entropy Regularization): We define a free energy function
       Phi = U - T*S.
       - U (Internal Energy): Distance metric based on structural alignment and NCD.
       - S (Entropy): Measures the "disorder" or ambiguity in the candidate's logical mapping.
       - T (Temperature): An annealing parameter that decreases as we verify more constraints.
       Minimizing Phi favors candidates that are structurally consistent (low U) and 
       logically precise (high S contribution to lowering free energy via regularization).
       
    3. Kalman Update (Recursive Estimation): We treat the score as a state estimate.
       We fuse the "measurement" (structural match) with the "prediction" (NCD baseline)
       using a gain factor derived from the thermodynamic confidence.
    """

    def __init__(self):
        # Structural keywords defining the "manifold" of valid logic
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'shorter']
        self.conditionals = ['if', 'unless', 'provided', 'when', 'then', 'else']
        self numerics = re.compile(r'-?\d+\.?\d*')
        
        # Thermodynamic constants
        self.base_temp = 1.0
        self.k_b = 1.0  # Boltzmann constant analog

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts topological features (logical structures) from text."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            'neg': has_negation,
            'comp': has_comparative,
            'cond': has_conditional,
            'nums': numbers,
            'len': len(words)
        }

    def _topological_distance(self, p_struct: Dict, c_struct: Dict) -> float:
        """
        Computes distance based on topological invariants.
        If the prompt has a feature (e.g., negation), the candidate must respect it.
        Violations create "holes" in the logical manifold, increasing distance.
        """
        dist = 0.0
        
        # Negation consistency (Critical invariant)
        if p_struct['neg']:
            # If prompt negates, candidate should ideally not contradict (simplified heuristic)
            # We penalize if the candidate lacks the complexity to handle negation
            if not c_struct['neg'] and c_struct['len'] < 5: 
                dist += 2.0 
        else:
            # If prompt is positive but candidate is strongly negative without cause
            if c_struct['neg'] and p_struct['len'] > 10:
                dist += 1.0

        # Comparative consistency
        if p_struct['comp'] and not c_struct['comp']:
            dist += 1.5
            
        # Conditional consistency
        if p_struct['cond'] and not c_struct['cond']:
            dist += 1.5
            
        # Numeric consistency (The strongest signal)
        if p_struct['nums'] and c_struct['nums']:
            # Check if order is preserved or logic holds (simplified: presence is key)
            pass 
        elif p_struct['nums'] and not c_struct['nums']:
            # Prompt has numbers, candidate doesn't -> High penalty
            dist += 3.0
            
        return dist

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _thermodynamic_potential(self, u_energy: float, candidate: str, prompt: str) -> float:
        """
        Calculates Free Energy Phi = U - T*S.
        U: Internal energy (structural + compression distance)
        S: Entropy (approximated by string variance/complexity relative to prompt)
        """
        # Approximate Entropy S via character distribution variance
        # Higher variance in char freq -> Higher entropy (more information rich)
        if len(candidate) == 0:
            return float('inf')
            
        freq = {}
        for char in candidate.lower():
            freq[char] = freq.get(char, 0) + 1
        probs = [count / len(candidate) for count in freq.values()]
        entropy = -sum(p * math.log(p + 1e-9) for p in probs if p > 0)
        
        # Temperature schedule: Lower temp for longer prompts (more rigorous check)
        temp = self.base_temp / (1.0 + 0.1 * len(prompt.split()))
        
        # Free Energy minimization
        # We want low U (good match) and high S (rich answer). 
        # So Phi = U - T*S. Lower Phi is better.
        phi = u_energy - (temp * self.k_b * entropy)
        return phi

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_struct = self._extract_structure(prompt)
        p_comp = zlib.compress(prompt.encode())
        results = []
        
        # Pre-calculate prompt stats for Kalman gain
        kalman_gain_base = 0.6 # Base trust in structural parser
        
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # 1. Topological Constraint (Structural Distance)
            topo_dist = self._topological_distance(p_struct, c_struct)
            
            # 2. NCD Baseline (Compression Distance)
            ncd_val = self._compute_ncd(prompt, cand)
            
            # 3. Internal Energy U (Weighted sum of distances)
            # Structural violations dominate energy
            u_energy = (topo_dist * 2.0) + (ncd_val * 0.5)
            
            # 4. Thermodynamic Potential (Free Energy)
            phi = self._thermodynamic_potential(u_energy, cand, prompt)
            
            # 5. Kalman-like Update for Score
            # State: Score. Measurement: Negative Free Energy (lower phi -> higher score)
            # Normalize phi to 0-1 range roughly (assuming phi > -10 usually)
            raw_score = max(0.0, 1.0 / (1.0 + phi))
            
            # Adjust with NCD as tiebreaker/refiner if structural signal is weak
            if topo_dist < 0.1: 
                final_score = raw_score * 0.7 + (1.0 - ncd_val) * 0.3
            else:
                final_score = raw_score
            
            # Reasoning string generation
            reason_parts = []
            if topo_dist > 0:
                reason_parts.append(f"Topological mismatch (dist={topo_dist:.2f})")
            if p_struct['nums'] and not c_struct['nums']:
                reason_parts.append("Missing numeric evaluation")
            if not reason_parts:
                reason_parts.append("Structurally consistent")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reason_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on thermodynamic stability of the answer.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        
        # Topological consistency check
        topo_dist = self._topological_distance(p_struct, c_struct)
        
        # If topological distance is high, confidence drops sharply
        if topo_dist > 2.0:
            return 0.1
            
        # NCD check
        ncd_val = self._compute_ncd(prompt, answer)
        
        # Simple heuristic mapping
        # Low distance + Low NCD = High confidence
        base_conf = 1.0 / (1.0 + topo_dist + ncd_val)
        
        # Boost if numeric structures match
        if p_struct['nums'] and c_struct['nums']:
            base_conf = min(1.0, base_conf + 0.2)
            
        return min(1.0, max(0.0, base_conf))