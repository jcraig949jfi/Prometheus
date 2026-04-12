import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Reservoir Hypothesis Tester with LDPC-inspired Self-Verification.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, numbers).
    2. Chaotic Amplification: Maps candidate semantics to initial states in a Logistic Map reservoir.
       Small semantic differences (hypothesis variations) diverge exponentially (Lyapunov expansion).
    3. Emergent Attractor Scoring: The trajectory's stability acts as the 'attractor basin'.
    4. Syndrome Decoding (Metacognition): Checks if the trajectory remains consistent with 
       extracted structural constraints. A 'syndrome' (error) is raised if the candidate 
       violates logical rules or diverges too wildly from the prompt's structural signature.
    5. Final Score: Weighted combination of structural match, chaotic stability, and NCD tiebreaker.
    """

    def __init__(self):
        self.reservoir_size = 100
        self.chaotic_param = 3.99  # High chaos for sensitive dependence
        self.iterations = 50
        np.random.seed(42)  # Determinism

    def _structural_parse(self, text: str) -> dict:
        """Extract logical primitives: negations, numbers, comparatives."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|>\|<)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums]
        return features

    def _hash_to_state(self, text: str, prompt_features: dict) -> np.ndarray:
        """Convert text to initial reservoir state using structural bias."""
        # Base hash
        h = zlib.crc32(text.encode())
        vec = np.zeros(self.reservoir_size)
        
        # Seed from hash
        for i in range(self.reservoir_size):
            h = (h * 1664525 + 1013904223) % (2**32)
            vec[i] = (h / (2**32)) * 0.1 # Small initial perturbation
            
        # Bias by structural features (The "Hypothesis Encoding")
        # If candidate has different negation count than prompt, shift state
        c_feats = self._structural_parse(text)
        neg_diff = abs(c_feats['negations'] - prompt_features['negations'])
        if neg_diff > 0:
            vec += neg_diff * 0.5  # Significant shift for logical mismatch
            
        # Numeric consistency check
        if prompt_features['numbers'] and c_feats['numbers']:
            # Simple proximity check for the first number found
            p_num = prompt_features['numbers'][0]
            c_num = c_feats['numbers'][0]
            if abs(p_num - c_num) > 1.0: # Allow small float errors
                vec += 0.3 # Shift state for numeric inconsistency
                
        return np.tanh(vec)

    def _run_chaotic_reservoir(self, initial_state: np.ndarray) -> Tuple[float, float]:
        """
        Run logistic map dynamics. 
        Returns: (mean_activity, lyapunov_estimate)
        Divergence indicates instability (potential falsehood/inconsistency).
        """
        state = initial_state.copy()
        history = []
        
        # Use a simple coupled map lattice approach for the reservoir
        for _ in range(self.iterations):
            # Logistic map: x_{n+1} = r * x_n * (1 - x_n)
            # Shift state to (0, 1) range for logistic map
            normalized_state = (state - state.min()) / (state.max() - state.min() + 1e-9)
            state = self.chaotic_param * normalized_state * (1 - normalized_state)
            
            # Add slight coupling (neighbor interaction) to simulate reservoir connectivity
            state = np.roll(state, 1) * 0.1 + state * 0.9
            
            history.append(np.mean(state))
            
        # Stability metric: variance of the mean activity over time
        # Low variance = stable attractor (consistent hypothesis)
        # High variance = chaotic divergence (inconsistent/false hypothesis)
        stability = 1.0 / (np.var(history) + 0.01)
        return np.mean(history), stability

    def _compute_syndrome(self, prompt: str, candidate: str) -> float:
        """
        Metacognitive check: Does the candidate violate explicit structural constraints?
        Returns 0.0 (valid) to 1.0 (invalid/high syndrome).
        """
        p_feats = self._structural_parse(prompt)
        c_feats = self._structural_parse(candidate)
        syndrome = 0.0
        
        # Check Negation Consistency (Modus Tollens approximation)
        # If prompt implies a negative context and candidate is positive (or vice versa)
        if p_feats['negations'] > 0 and c_feats['negations'] == 0:
            # Potential contradiction, but context matters. 
            # Heuristic: If prompt has 'not' and candidate lacks it, penalize slightly unless it's an answer.
            if 'no' in candidate.lower() or 'not' in candidate.lower():
                pass # Candidate acknowledges negation
            else:
                syndrome += 0.2

        # Check Numeric Logic
        if p_feats['numbers'] and c_feats['numbers']:
            p_val = p_feats['numbers'][0]
            c_val = c_feats['numbers'][0]
            # If prompt asks for comparison and candidate gets it wrong
            if 'less' in prompt.lower() and c_val > p_val:
                syndrome += 0.5
            if 'greater' in prompt.lower() and c_val < p_val:
                syndrome += 0.5
                
        return min(syndrome, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        return (z12 - min(z1, z2)) / max(z1, z2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        for cand in candidates:
            # 1. Encode hypothesis
            initial_state = self._hash_to_state(cand, prompt_feats)
            
            # 2. Chaotic Amplification & Attractor Analysis
            _, stability_score = self._run_chaotic_reservoir(initial_state)
            
            # 3. Syndrome Decoding (Metacognition)
            syndrome = self._compute_syndrome(prompt, cand)
            
            # 4. NCD Tiebreaker (Structural similarity)
            ncd_val = self._ncd(prompt, cand)
            
            # Combine scores
            # High stability + Low syndrome + Low NCD (similarity) = High Score
            # Normalize stability (inverse var) to 0-1 range roughly
            norm_stability = min(stability_score / 10.0, 1.0)
            
            final_score = (0.4 * norm_stability) + (0.4 * (1.0 - syndrome)) + (0.2 * (1.0 - ncd_val))
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Stability: {norm_stability:.2f}, Syndrome: {syndrome:.2f}, NCD: {ncd_val:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        
        # Adjust based on absolute syndrome check
        syndrome = self._compute_syndrome(prompt, answer)
        if syndrome > 0.4:
            return max(0.0, score - 0.3)
        
        return min(1.0, score)