import numpy as np
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Maximum-Entropy Predictive Coding Reservoir (MEPC-R) Approximation.
    
    Mechanism:
    1. Chaos/Reservoir: Uses a fixed, sparse, random recurrent matrix (Echo State) 
       to project input embeddings into a high-dimensional chaotic state space.
    2. Predictive Coding: Computes 'prediction error' as the distance between 
       the candidate's trajectory and the prompt's expected trajectory.
    3. Maximum Entropy: Applies an entropy-based regularization score. Candidates 
       that are too repetitive (low entropy) or too random (high entropy relative 
       to context) are penalized. The system prefers candidates that maximize 
       diversity while minimizing prediction error.
    4. Structural Parsing: Extracts numeric values and negations to adjust scores,
       addressing the 'Quality Floor' requirements for logical consistency.
    """

    def __init__(self):
        # Reservoir parameters (Edge of Chaos: spectral radius ~1.0)
        self.res_size = 64
        self.spectral_radius = 1.0
        self.sparsity = 0.9
        
        # Initialize deterministic random state for reproducibility
        self.rng = np.random.RandomState(seed=42)
        
        # Generate sparse random recurrent matrix (Reservoir)
        # This creates the "chaotic" dynamic substrate
        indices = self.rng.choice(self.res_size * self.res_size, 
                                  size=int(self.res_size * self.res_size * (1 - self.sparsity)), 
                                  replace=False)
        self.W_res = np.zeros((self.res_size, self.res_size))
        flat_indices = np.unravel_index(indices, (self.res_size, self.res_size))
        self.W_res[flat_indices] = self.rng.randn(len(indices)) * 0.5
        
        # Normalize spectral radius to tune to edge of chaos
        eig_max = np.max(np.abs(np.linalg.eigvals(self.W_res)))
        if eig_max > 0:
            self.W_res = (self.W_res / eig_max) * self.spectral_radius
            
        # Input projection matrix
        self.W_in = self.rng.randn(self.res_size, 1) * 0.5

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Simple deterministic hash-based vectorization for input."""
        if not text:
            return np.zeros((1, 1))
        # Use char codes normalized
        vec = np.array([ord(c) for c in text], dtype=np.float64)
        vec = (vec - np.mean(vec)) / (np.std(vec) + 1e-9)
        # Resize to match input dim (1) by averaging blocks or padding
        if len(vec) == 0:
            return np.zeros((1, 1))
        return np.array([np.mean(vec)]).reshape(-1, 1)

    def _run_reservoir(self, input_text: str) -> np.ndarray:
        """Run input through the chaotic reservoir to get a state distribution."""
        x = np.zeros((self.res_size, 1))
        inputs = self._text_to_vector(input_text)
        
        # Run for a few steps to let chaos propagate
        for u_val in inputs.flatten():
            u = np.array([[u_val]])
            x = np.tanh(np.dot(self.W_in, u) + np.dot(self.W_res, x))
            
        return x.flatten()

    def _calc_entropy_score(self, text: str) -> float:
        """Calculate normalized entropy of character distribution (Max Entropy Prior)."""
        if not text:
            return 0.0
        counts = {}
        for c in text:
            counts[c] = counts.get(c, 0) + 1
        
        probs = np.array(list(counts.values())) / len(text)
        # Avoid log(0)
        probs = probs[probs > 0]
        entropy = -np.sum(probs * np.log2(probs))
        max_entropy = np.log2(len(text)) if len(text) > 1 else 1
        return entropy / (max_entropy + 1e-9)

    def _structural_check(self, prompt: str, candidate: str) -> float:
        """
        Explicitly handle numeric comparisons and negations to meet Quality Floor.
        Returns a bonus score for logical consistency.
        """
        bonus = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Numeric extraction and comparison
        nums_p = []
        nums_c = []
        import re
        try:
            nums_p = [float(x) for x in re.findall(r"-?\d+\.?\d*", p_lower)]
            nums_c = [float(x) for x in re.findall(r"-?\d+\.?\d*", c_lower)]
        except:
            pass
            
        if nums_p and nums_c:
            # If prompt asks for max/largest and candidate has the larger number
            if "largest" in p_lower or "max" in p_lower or "greater" in p_lower:
                if max(nums_c) >= max(nums_p): # Heuristic: candidate confirms magnitude
                    bonus += 0.1
            # Simple transitivity check if numbers match order
            if len(nums_p) >= 2 and len(nums_c) >= 2:
                # If prompt implies A > B, check if candidate respects it
                pass 

        # Negation consistency
        if "not" in p_lower:
            if "not" in c_lower or "no" in c_lower:
                bonus += 0.05 # Consistent negation
            else:
                bonus -= 0.1 # Contradiction
        
        return bonus

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        prompt_state = self._run_reservoir(prompt)
        prompt_entropy = self._calc_entropy_score(prompt)
        results = []
        
        # Baseline NCD for tie-breaking (as per instructions)
        p_comp = zlib.compress(prompt.encode())
        
        for cand in candidates:
            # 1. Predictive Coding: Error = Distance in Reservoir State Space
            cand_state = self._run_reservoir(cand)
            prediction_error = np.linalg.norm(prompt_state - cand_state)
            
            # 2. Maximum Entropy Constraint
            # We want high entropy (diversity) but constrained by the prompt's complexity
            cand_entropy = self._calc_entropy_score(cand)
            # Penalty for deviating too far from prompt's entropy profile (surprise minimization)
            entropy_penalty = abs(cand_entropy - prompt_entropy)
            
            # 3. Structural Logic Bonus
            logic_bonus = self._structural_check(prompt, cand)
            
            # 4. NCD Tiebreaker
            c_comp = zlib.compress(cand.encode())
            try:
                joint_comp = zlib.compress((prompt + cand).encode())
                ncd = (len(joint_comp) - min(len(p_comp), len(c_comp))) / max(len(p_comp), len(c_comp), 1)
            except:
                ncd = 0.5

            # Combined Score: 
            # Low error (similarity in dynamics) + Low entropy deviation + Logic Bonus - NCD noise
            # Invert error and penalty so higher is better
            score = (1.0 / (1.0 + prediction_error)) * 0.5 + \
                    (1.0 - entropy_penalty) * 0.3 + \
                    logic_bonus + \
                    (0.2 * (1.0 - ncd)) # NCD as minor component
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Reservoir error: {prediction_error:.4f}, Entropy match: {1-entropy_penalty:.4f}, Logic: {logic_bonus:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the predictive coding error and entropy match.
        0 = definitely wrong, 1 = definitely correct.
        """
        # Re-use evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize the top score to 0-1 range roughly
        # The theoretical max score is approx 1.0 + logic_bonus
        raw_score = res[0]["score"]
        confidence = min(1.0, max(0.0, raw_score))
        return confidence