import numpy as np
import zlib
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Chaotic Spectral Reservoir Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. Candidates are scored based on 
       logical consistency with these extracted features.
    2. Chaotic Reservoir Simulation (Secondary Signal): Implements a fixed-weight 
       recurrent network (Echo State Network style) with spectral radius > 1 to induce 
       chaotic dynamics. The prompt and candidate are mapped to input scalings.
    3. Spectral Hypothesis Testing: The reservoir's state trajectory is analyzed via 
       FFT. The power spectral density (PSD) energy in specific bands serves as a 
       "dynamic signature". 
    4. Fusion: Candidates that pass structural checks are ranked by how closely their 
       induced spectral signature matches a "coherent" template (simulated by stability 
       metrics in the chaotic regime). NCD is used only as a final tiebreaker.
    """

    def __init__(self):
        # Reservoir parameters (Chaotic regime: spectral_radius > 1)
        self.N = 64  # Reservoir size
        self.spectral_radius = 1.2
        self.input_scaling = 0.8
        self.leak_rate = 0.9
        
        # Initialize fixed random reservoir (deterministic seed for reproducibility)
        np.random.seed(42)
        W_in = np.random.randn(self.N, 1)
        W_res = np.random.randn(self.N, self.N)
        
        # Scale reservoir to have desired spectral radius
        eigenvalues = np.linalg.eigvals(W_res)
        max_eig = np.max(np.abs(eigenvalues))
        W_res = W_res * (self.spectral_radius / max_eig)
        
        self.W_in = W_in
        self.W_res = W_res
        self.state = np.zeros((self.N, 1))

    def _reset_state(self):
        self.state = np.zeros((self.N, 1))

    def _extract_structural_features(self, text: str) -> Dict[str, Any]:
        """Extract logical constraints and numeric values."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|impossible)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|larger|smaller)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'has_question': '?' in text
        }
        return features

    def _run_reservoir(self, input_signal: List[float]) -> np.ndarray:
        """Run the reservoir with the input signal and return state trajectory."""
        self._reset_state()
        trajectory = []
        
        for u_val in input_signal:
            u = np.array([[u_val]])
            # Update state: x(t) = (1-leak)x(t-1) + leak * tanh(W_in*u + W_res*x(t-1))
            pre_activation = self.input_scaling * self.W_in.T @ u + self.W_res @ self.state
            self.state = (1 - self.leak_rate) * self.state + self.leak_rate * np.tanh(pre_activation)
            trajectory.append(self.state.copy())
            
        return np.vstack(trajectory) if trajectory else np.zeros((1, self.N))

    def _compute_spectral_signature(self, trajectory: np.ndarray) -> float:
        """Compute a compact spectral signature (energy ratio) from trajectory."""
        if trajectory.shape[0] < 2:
            return 0.0
        
        # Compute FFT on the mean activity across neurons over time
        mean_activity = np.mean(trajectory, axis=1).flatten()
        fft_vals = np.fft.fft(mean_activity - np.mean(mean_activity))
        psd = np.abs(fft_vals) ** 2
        
        # Signature: Ratio of high-frequency energy to low-frequency energy
        # In chaotic systems, this ratio characterizes the "roughness" of the attractor
        mid = len(psd) // 2
        low_energy = np.sum(psd[1:mid]) + 1e-9
        high_energy = np.sum(psd[mid:]) + 1e-9
        
        return np.log10(high_energy / low_energy)

    def _text_to_input_sequence(self, text: str, base_scale: float = 1.0) -> List[float]:
        """Convert text to a numeric input sequence for the reservoir."""
        # Simple hash-based mapping to floats, scaled by base_scale
        vals = []
        for char in text:
            v = (ord(char) / 256.0) * self.input_scaling * base_scale
            vals.append(float(v))
        return vals if vals else [0.0]

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_features = self._extract_structural_features(prompt)
        results = []
        
        # Generate a "coherence" baseline from the prompt itself
        prompt_seq = self._text_to_input_sequence(prompt)
        prompt_traj = self._run_reservoir(prompt_seq)
        prompt_signature = self._compute_spectral_signature(prompt_traj)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            cand_features = self._extract_structural_features(cand)
            
            # 1. Structural Logic Scoring (Primary)
            # Check for contradiction in negation counts (heuristic)
            if prompt_features['negations'] > 0 and 'no' in cand.lower() and 'yes' in cand.lower():
                score -= 0.5
                reasoning_parts.append("Contradictory negation detected.")
            
            # Numeric consistency check (simplified)
            if prompt_features['numbers'] and cand_features['numbers']:
                try:
                    p_nums = [float(n) for n in prompt_features['numbers']]
                    c_nums = [float(n) for n in cand_features['numbers']]
                    if p_nums and c_nums:
                        # Heuristic: If prompt implies comparison, candidate should have numbers
                        if prompt_features['comparatives'] > 0:
                            score += 0.3
                            reasoning_parts.append("Numeric comparative consistency found.")
                except ValueError:
                    pass
            
            # Conditional presence
            if prompt_features['conditionals'] > 0:
                if any(k in cand.lower() for k in ['if', 'then', 'because', 'therefore']):
                    score += 0.2
                    reasoning_parts.append("Logical connector matches conditional prompt.")
                else:
                    score -= 0.1
                    reasoning_parts.append("Missing logical connector for conditional prompt.")

            # 2. Chaotic Spectral Hypothesis Testing (Secondary)
            # Scale input by a factor derived from candidate length to perturb dynamics
            scale_factor = 1.0 + (len(cand) / 100.0)
            cand_seq = self._text_to_input_sequence(cand, base_scale=scale_factor)
            cand_traj = self._run_reservoir(cand_seq)
            cand_signature = self._compute_spectral_signature(cand_traj)
            
            # Spectral Match Score: Closer to prompt's dynamic signature implies 
            # the candidate lies in the same attractor basin (hypothesis plausibility)
            spectral_diff = abs(cand_signature - prompt_signature)
            spectral_score = max(0, 1.0 - spectral_diff) * 0.3 # Max 0.3 contribution
            score += spectral_score
            reasoning_parts.append(f"Spectral coherence: {spectral_score:.2f}")

            # 3. NCD Tiebreaker (Only if scores are very close or zero)
            ncd_val = self._ncd_distance(prompt, cand)
            if abs(score) < 0.01:
                score -= ncd_val * 0.1 # Prefer lower NCD (higher similarity) if no logic found
                reasoning_parts.append("NCD tiebreaker applied.")

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural and spectral alignment."""
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
        
        raw_score = eval_results[0]['score']
        
        # Map raw score to 0-1 range
        # Assuming typical scores range from -0.5 to 1.0
        confidence = (raw_score + 0.5) / 1.5
        return max(0.0, min(1.0, confidence))