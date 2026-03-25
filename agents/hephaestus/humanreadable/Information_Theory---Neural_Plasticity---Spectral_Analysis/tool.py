import numpy as np
import math
from typing import List, Dict

class ReasoningTool:
    """
    Spectral Information-Theoretic Plasticity (SITP) Reasoning Tool.
    
    Mechanism Analogy:
    1. Signal Encoding: Input text (prompt + candidates) is mapped to a time-series
       signal using ASCII values normalized to [0, 1], acting as neural firing rates.
    2. Spectral Analysis (STFT): A sliding window Fourier transform extracts frequency
       components (features) of the semantic "activity".
    3. Information-Theoretic Plasticity: 
       - We estimate mutual information (MI) between the prompt's spectrum and the 
         candidate's spectrum. High MI implies the candidate preserves the information
         structure of the prompt (Hebbian potentiation).
       - Regularization: A KL-divergence-like penalty discourages candidates with 
         extreme spectral power distributions (deviating from a uniform prior).
    4. Scoring: The final score is the net result of information gain minus regularization.
    """

    def __init__(self):
        self.window_size = 8
        self.epsilon = 1e-9

    def _text_to_signal(self, text: str) -> np.ndarray:
        """Convert ASCII text to a normalized float signal."""
        if not text:
            return np.zeros(1)
        vals = [float(ord(c)) / 255.0 for c in text]
        # Pad to next multiple of window_size for STFT
        pad_len = (self.window_size - (len(vals) % self.window_size)) % self.window_size
        vals += [0.0] * pad_len
        return np.array(vals)

    def _stft(self, signal: np.ndarray) -> np.ndarray:
        """Compute simplified magnitude spectrum via sliding window FFT."""
        if len(signal) < self.window_size:
            return np.abs(np.fft.fft(signal, n=self.window_size))
        
        spectra = []
        step = self.window_size // 2
        for i in range(0, len(signal) - self.window_size + 1, step):
            window = signal[i:i+self.window_size]
            # Apply Hamming window implicitly by simple truncation for speed/simplicity
            fft_res = np.fft.fft(window)
            spectra.append(np.abs(fft_res))
        
        if not spectra:
            return np.zeros(self.window_size)
        return np.mean(np.array(spectra), axis=0)

    def _estimate_mi(self, spec1: np.ndarray, spec2: np.ndarray) -> float:
        """
        Estimate band-limited mutual information using discretized bins.
        I(X;Y) = sum p(x,y) log(p(x,y) / (p(x)p(y)))
        """
        # Normalize to probability distributions
        s1 = spec1 + self.epsilon
        s2 = spec2 + self.epsilon
        p1 = s1 / np.sum(s1)
        p2 = s2 / np.sum(s2)
        
        # Joint approximation: geometric mean of magnitudes normalized
        joint = np.sqrt(p1 * p2)
        joint = joint / np.sum(joint)
        
        mi = 0.0
        for i in range(len(p1)):
            if joint[i] > self.epsilon:
                mi += joint[i] * math.log(joint[i] / (p1[i] * p2[i] + self.epsilon) + self.epsilon)
        return max(0.0, mi)

    def _kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Compute KL divergence D_KL(p || q)."""
        p = p / (np.sum(p) + self.epsilon)
        q = q / (np.sum(q) + self.epsilon)
        p += self.epsilon
        q += self.epsilon
        
        kl = 0.0
        for i in range(len(p)):
            kl += p[i] * math.log(p[i] / q[i])
        return kl

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_sig = self._text_to_signal(prompt)
        prompt_spec = self._stft(prompt_sig)
        # Prior distribution is uniform (maximum entropy)
        prior = np.ones_like(prompt_spec) / len(prompt_spec)
        
        results = []
        for cand in candidates:
            cand_sig = self._text_to_signal(cand)
            cand_spec = self._stft(cand_sig)
            
            # Term 1: Information Potentiation (MI between prompt and candidate)
            info_gain = self._estimate_mi(prompt_spec, cand_spec)
            
            # Term 2: Regularization (Deviation from uniform prior)
            # We penalize candidates that are too "spiky" or structured differently 
            # from a neutral baseline, simulating the KL term in the prompt's equation.
            reg_penalty = self._kl_divergence(cand_spec, prior)
            
            # SITP Update Rule Analogue: Score = Info Gain - Lambda * Regularization
            # Lambda set to 0.5 to balance terms
            score = info_gain - 0.5 * reg_penalty
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Spectral MI: {info_gain:.4f}, Reg Penalty: {reg_penalty:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on normalized SITP score."""
        # Evaluate single candidate against prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        raw_score = res_list[0]["score"]
        
        # Map raw score to [0, 1] using a sigmoid-like mapping
        # Assuming typical MI ranges and penalty ranges, we normalize.
        # A score > 0 is good, < 0 is bad.
        confidence = 1.0 / (1.0 + math.exp(-raw_score * 2.0))
        return float(np.clip(confidence, 0.0, 1.0))