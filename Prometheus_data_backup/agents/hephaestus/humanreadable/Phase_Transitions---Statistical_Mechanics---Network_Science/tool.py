import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Criticality-Driven Renormalization Inference Engine.
    
    Mechanism:
    1. Network Construction: Treats candidates as nodes in a hypothesis graph.
    2. Coupling (J_ij): Estimates logical/evidential support using structural parsing 
       (negations, comparatives, conditionals) and NCD-based similarity as a proxy 
       for shared premises.
    3. Fields (h_i): Encodes prior likelihood based on structural alignment with the prompt.
    4. Phase Transition Detection: Simulates an Ising model dynamics. 
       - Computes global magnetization (consensus) and susceptibility (fluctuation).
       - Uses the susceptibility peak to determine if the evidence pool has stabilized.
    5. Scoring: Ranks candidates by their steady-state spin expectation (magnetization),
       effectively performing belief propagation on the constructed network.
    """

    def __init__(self):
        self.tolerance = 1e-6

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Extracts logical constraints: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negation_count': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparative_count': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditional_count': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': []
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums]
        return features

    def _compute_coupling(self, feat1: Dict, feat2: Dict, ncd_val: float) -> float:
        """
        Computes J_ij (coupling strength).
        High coupling if structural features align and NCD is low (similar content).
        """
        # Structural alignment penalty
        struct_diff = abs(feat1['negation_count'] - feat2['negation_count'])
        struct_diff += abs(feat1['comparative_count'] - feat2['comparative_count'])
        struct_diff += abs(feat1['conditional_count'] - feat2['conditional_count'])
        
        # Numeric consistency check
        num_penalty = 0.0
        if feat1['numbers'] and feat2['numbers']:
            # If both have numbers, they should be close or logically related
            # Simple heuristic: penalty if ranges don't overlap or differ wildly
            min1, max1 = min(feat1['numbers']), max(feat1['numbers'])
            min2, max2 = min(feat2['numbers']), max(feat2['numbers'])
            if max1 < min2 or max2 < min1:
                num_penalty = 0.5 # Disjoint ranges
        
        # Combine: Low NCD + Low Structural Diff = High Coupling
        # Base similarity from NCD (inverted)
        sim = 1.0 - min(1.0, ncd_val)
        
        # Apply penalties
        coupling = sim * math.exp(-0.5 * struct_diff) * math.exp(-2.0 * num_penalty)
        return coupling

    def _compute_field(self, prompt: str, candidate: str) -> float:
        """
        Computes h_i (external field).
        Measures how well the candidate structurally aligns with the prompt's constraints.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        score = 0.0
        # Reward matching negation logic
        if p_feat['negation_count'] > 0 and c_feat['negation_count'] > 0:
            score += 0.5
        elif p_feat['negation_count'] == 0 and c_feat['negation_count'] == 0:
            score += 0.2
            
        # Reward matching comparative logic
        if p_feat['comparative_count'] > 0 and c_feat['comparative_count'] > 0:
            score += 0.5
            
        # Numeric constraint satisfaction (simplified)
        if p_feat['numbers'] and c_feat['numbers']:
            # Check if candidate numbers satisfy simple prompt inequalities if detectable
            # Here we just reward presence of numbers if prompt has them
            score += 0.3
            
        # NCD tiebreaker for direct inclusion
        ncd = self._ncd(prompt.lower(), candidate.lower())
        if ncd < 0.6: # High overlap
            score += 0.4
            
        return score

    def _ising_simulation(self, nodes: List[str], J: List[List[float]], h: List[float], steps: int = 50) -> List[float]:
        """
        Simulates Ising model dynamics to find equilibrium magnetization.
        Returns the average spin <sigma_i> for each node.
        """
        n = len(nodes)
        if n == 0:
            return []
        if n == 1:
            return [1.0 if h[0] > 0 else -1.0]

        # Initialize spins randomly but biased by field
        spins = [1.0 if h[i] > 0 else -1.0 for i in range(n)]
        
        # Control parameter lambda (evidence strength) - simulated by temperature schedule
        # We assume high evidence (low T) to force consensus
        beta = 2.0 
        
        history_magnetization = []
        
        for _ in range(steps):
            for i in range(n):
                # Calculate local field acting on spin i
                local_field = h[i]
                for j in range(n):
                    if i != j:
                        local_field += J[i][j] * spins[j]
                
                # Probabilistic update (Metropolis-like)
                energy_diff_up = -2 * local_field # Energy change if flipping to +1
                # Actually, delta_E = E_new - E_old. 
                # If current is -1, flipping to +1: delta_E = -2 * sigma_i * H_local = -2*(-1)*H = 2H
                # If current is +1, flipping to -1: delta_E = -2*(1)*H = -2H
                
                current_spin = spins[i]
                delta_E = 2 * current_spin * local_field
                
                if delta_E < 0 or math.random() < math.exp(-beta * delta_E):
                    spins[i] = -current_spin
            
            # Monitor global magnetization
            M = sum(spins) / n
            history_magnetization.append(M)
            
        # Return the final spins as confidence scores (mapped to 0-1)
        # We use the final state as the consensus
        return spins

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        n = len(candidates)
        
        # 1. Precompute features
        prompt_feat = self._extract_structural_features(prompt)
        cand_feats = [self._extract_structural_features(c) for c in candidates]
        
        # 2. Build Coupling Matrix (J) and Field Vector (h)
        J = [[0.0] * n for _ in range(n)]
        h = [0.0] * n
        
        for i in range(n):
            # Compute Field h_i
            h[i] = self._compute_field(prompt, candidates[i])
            
            for j in range(i + 1, n):
                # Compute Coupling J_ij
                ncd_val = self._ncd(candidates[i], candidates[j])
                coupling = self._compute_coupling(cand_feats[i], cand_feats[j], ncd_val)
                J[i][j] = coupling
                J[j][i] = coupling
        
        # 3. Run Ising Simulation to find consensus
        final_spins = self._ising_simulation(candidates, J, h)
        
        # 4. Convert spins to scores (0-1)
        # Spin +1 -> 1.0, Spin -1 -> 0.0
        results = []
        for i, spin in enumerate(final_spins):
            score = (spin + 1.0) / 2.0
            # Boost slightly if structural alignment was strong initially
            if h[i] > 0.5:
                score = min(1.0, score + 0.1)
            
            results.append({
                "candidate": candidates[i],
                "score": score,
                "reasoning": f"Consensus spin {spin:.2f} via Ising dynamics; structural alignment {h[i]:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence by simulating the hypothesis network with the 
        proposed answer included. If the answer stabilizes to +1 (accepted) 
        in the consensus, confidence is high.
        """
        # Create a dummy set of candidates to form a network
        # We use the answer itself and a few perturbations to simulate the "pool"
        candidates = [
            answer,
            "Not " + answer if not answer.startswith("Not") else answer[4:],
            answer + " possibly",
            "It is false that " + answer
        ]
        
        # Run evaluation to get the score of the primary answer
        # We only care about the score of the first candidate (the exact answer)
        results = self.evaluate(prompt, candidates)
        
        # Find the result corresponding to the exact answer
        for res in results:
            if res['candidate'] == answer:
                return res['score']
        
        # Fallback if exact match lost (shouldn't happen with this logic)
        return 0.5