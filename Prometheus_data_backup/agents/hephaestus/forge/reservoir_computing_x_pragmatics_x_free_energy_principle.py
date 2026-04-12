import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Predictive-Coding Reservoir with Pragmatic Readout (PCPR)
    
    Mechanism:
    1. Structural Parsing (Pragmatics Core): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a 'context vector'. This represents the 
       pragmatic frame of the prompt.
    2. Reservoir Dynamics (Free Energy Core): Uses a fixed random recurrent matrix (Echo State) 
       to project the context vector into a high-dimensional trajectory.
    3. Variational Free Energy Minimization: 
       - Prediction Error: Difference between the reservoir's projected state and the 
         candidate's structural signature.
       - Pragmatic Error: Penalty for violating extracted logical constraints (e.g., negation flips).
       - The 'score' is the inverse of the total free energy (error). Lower error = Higher score.
    4. NCD Tiebreaker: Used only if structural signals are identical.
    """

    def __init__(self):
        # Reservoir hyperparameters
        self.reservoir_size = 64
        self.input_scale = 0.5
        self.spectral_radius = 0.9
        
        # Initialize fixed random reservoir (Echo State Network style)
        np.random.seed(42)  # Determinism
        W = np.random.randn(self.reservoir_size, self.reservoir_size)
        # Scale to ensure echo state property
        W = W / np.linalg.norm(W, ord=2) * self.spectral_radius
        self.W_res = W
        
        # Input weights
        self.W_in = np.random.randn(self.reservoir_size, 1) * self.input_scale

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extract pragmatic and logical features from text."""
        t = text.lower()
        features = {
            'negation': 0.0,
            'comparative': 0.0,
            'conditional': 0.0,
            'numeric_val': 0.0,
            'length': len(t)
        }
        
        # Negation detection (Pragmatic inhibitor)
        negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        if any(n in t.split() for n in negations) or any(n in t for n in ["n't"]):
            features['negation'] = 1.0
            
        # Comparative detection
        comparatives = ['greater', 'less', 'more', 'fewer', '>', '<', 'better', 'worse']
        if any(c in t for c in comparatives):
            features['comparative'] = 1.0
            
        # Conditional detection
        conditionals = ['if', 'then', 'unless', 'otherwise']
        if any(c in t.split() for c in conditionals):
            features['conditional'] = 1.0
            
        # Numeric extraction (Simple case: first float found)
        nums = re.findall(r"-?\d+\.?\d*", t)
        if nums:
            try:
                features['numeric_val'] = float(nums[0])
            except ValueError:
                pass
                
        return features

    def _run_reservoir(self, context_vec: np.ndarray, steps: int = 10) -> np.ndarray:
        """Run reservoir dynamics to generate rich temporal trajectory."""
        state = np.zeros(self.reservoir_size)
        trajectory = []
        
        for _ in range(steps):
            # Update state: x(t+1) = tanh(W_in * u + W * x(t))
            input_drive = self.W_in.flatten() * context_vec[0]
            state = np.tanh(input_drive + self.W_res @ state)
            trajectory.append(state)
            
        return np.mean(trajectory, axis=0)  # Aggregate trajectory as readout target

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute variational free energy as a proxy for prediction error.
        F = Prediction_Error + Pragmatic_Penalty
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        # 1. Form context vector from prompt features
        ctx_keys = ['negation', 'comparative', 'conditional', 'numeric_val']
        prompt_vec = np.array([p_feat[k] for k in ctx_keys]).reshape(-1, 1)
        candidate_vec = np.array([c_feat[k] for k in ctx_keys]).reshape(-1, 1)
        
        # 2. Reservoir projection (Generative Model)
        # We simulate what the reservoir expects given the prompt context
        expected_state = self._run_reservoir(prompt_vec)
        
        # 3. Prediction Error (Sensory channel)
        # How well does the candidate's structural signature match the prompt's expected dynamics?
        # We project candidate through same input weights to compare states
        candidate_state = self._run_reservoir(candidate_vec)
        sensory_error = np.linalg.norm(expected_state - candidate_state)
        
        # 4. Pragmatic Error (Implicature channel)
        # Check for logical consistency (e.g., if prompt has negation, candidate should reflect it)
        pragmatic_penalty = 0.0
        
        # Negation consistency
        if p_feat['negation'] > 0.5:
            # If prompt is negative, a positive-only candidate might be wrong (heuristic)
            if c_feat['negation'] < 0.5 and 'yes' in candidate.lower() and 'no' not in candidate.lower():
                pragmatic_penalty += 2.0
                
        # Numeric consistency (Simple magnitude check)
        if p_feat['numeric_val'] > 0 and c_feat['numeric_val'] > 0:
            # If prompt implies a comparison, check if candidate number makes sense relative to prompt
            # This is a simplified proxy for "implicature"
            if abs(p_feat['numeric_val'] - c_feat['numeric_val']) > p_feat['numeric_val'] * 10:
                pragmatic_penalty += 1.0

        # Total Free Energy
        free_energy = sensory_error + pragmatic_penalty
        return free_energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if min(len_s1, len_s2) == 0:
            return 1.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Calculate Free Energy for each candidate
        energies = []
        for cand in candidates:
            fe = self._compute_free_energy(prompt, cand)
            energies.append(fe)
        
        # Convert Energy to Score (Inverse relationship)
        # Add small epsilon to avoid division by zero
        min_e = min(energies) if energies else 1.0
        base_scores = [1.0 / (e + 0.1) for e in energies]
        
        # Normalize scores to 0-1 range roughly
        max_bs = max(base_scores) if base_scores else 1.0
        normalized_scores = [b / max_bs for b in base_scores]
        
        for i, cand in enumerate(candidates):
            score = normalized_scores[i]
            
            # Tie-breaking with NCD if structural scores are very close
            if len(candidates) > 1:
                # Check if scores are effectively tied (within 1%)
                others = [normalized_scores[j] for j in range(len(candidates)) if j != i]
                if others and abs(score - max(others)) < 0.01:
                    ncd_val = self._ncd(prompt, cand)
                    # Adjust score slightly based on NCD (lower NCD = better match)
                    score -= ncd_val * 0.001 

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Free Energy: {energies[i]:.4f}, Structural Match: {score:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on free energy minimization.
        Low free energy -> High confidence.
        """
        fe = self._compute_free_energy(prompt, answer)
        # Map free energy to 0-1. 
        # Heuristic: FE < 1.0 is good, > 5.0 is bad.
        # Using sigmoid-like mapping: 1 / (1 + FE)
        conf = 1.0 / (1.0 + fe)
        return min(1.0, max(0.0, conf))