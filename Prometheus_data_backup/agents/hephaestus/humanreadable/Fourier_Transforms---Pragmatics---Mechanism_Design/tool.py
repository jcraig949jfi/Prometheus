import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool combining structural logical parsing, spectral analysis 
    (Fourier) for pattern detection, and mechanism design scoring.
    
    Mechanism:
    1. Structural Parsing: Extracts logical primitives (negation, conditionals, etc.) 
       to form a binary time-series matrix.
    2. Spectral Analysis: Applies FFT to detect periodic logical structures (e.g., 
       nested negations, alternating conditionals) which often indicate complex reasoning.
    3. Pragmatic Weighting: Weights spectral features based on Gricean maxims (relevance).
    4. Mechanism Design: Uses a proper scoring rule (logarithmic) to incentivize 
       truthful probability estimation, penalizing overconfidence in incorrect answers.
    5. NCD Fallback: Uses Normalized Compression Distance as a tiebreaker for low-signal cases.
    """

    def __init__(self):
        # Logical primitives regex patterns
        self.patterns = {
            'negation': re.compile(r'\b(not|no|none|never|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|than)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|next|previous)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|any|most)\b', re.IGNORECASE),
            'modal': re.compile(r'\b(may|must|should|could|would|will)\b', re.IGNORECASE)
        }
        self.primitives = list(self.patterns.keys())
        self.K = len(self.primitives)
        
        # Pragmatic weights (heuristic: mid-frequency relevance)
        # Higher weight for features that signal complex logical structure
        self.w_prag = np.array([1.2, 1.5, 1.4, 1.3, 1.1, 1.0, 1.2])

    def _parse_to_series(self, text: str) -> np.ndarray:
        """Convert text to binary time-series matrix X (K x T)."""
        tokens = re.findall(r'\b\w+\b', text.lower())
        T = len(tokens) if len(tokens) > 0 else 1
        X = np.zeros((self.K, T), dtype=float)
        
        if T == 0:
            return X

        # Map token index to presence of primitives
        # We scan the original text for positions, but align to token count for simplicity
        # A more rigorous approach maps char positions to token indices.
        # Here we approximate by checking if any primitive pattern matches near token boundaries.
        
        full_text_lower = text.lower()
        char_to_token_idx = []
        
        # Build mapping from char index to token index
        current_token = 0
        last_end = 0
        # Re-tokenize to get exact spans
        for match in re.finditer(r'\b\w+\b', text.lower()):
            start, end = match.span()
            # Fill gaps with previous token index or increment
            for i in range(last_end, start):
                pass # skip non-word chars
            if start >= last_end:
                current_token += 1
                last_end = end
            
        # Simpler approach: Create a high-res char array then downsample or just use char positions
        # Let's use char positions as time steps for FFT resolution, capped for performance
        max_len = 2048
        text_sample = full_text_lower[:max_len]
        T_char = len(text_sample)
        if T_char == 0: return np.zeros((self.K, 1))
        
        X_char = np.zeros((self.K, T_char), dtype=float)
        
        for k, key in enumerate(self.primitives):
            for match in self.patterns[key].finditer(text_sample):
                start, end = match.span()
                # Mark the center of the match
                center = (start + end) // 2
                if 0 <= center < T_char:
                    X_char[k, center] = 1.0
        
        # Downsample or pad to fixed size for consistent FFT if needed, 
        # but numpy.fft handles variable lengths. 
        # To make spectra comparable, we normalize by length or use fixed window.
        # Let's just use the sampled length.
        return X_char

    def _compute_spectral_features(self, X: np.ndarray) -> np.ndarray:
        """Compute log-power spectrum features."""
        if X.shape[1] == 0:
            return np.zeros(self.K)
        
        features = []
        for k in range(self.K):
            x_k = X[k, :]
            # Remove mean to focus on fluctuations
            x_k = x_k - np.mean(x_k)
            fft_val = np.fft.fft(x_k)
            power = np.abs(fft_val) ** 2
            # Take first half (symmetric) and log scale
            half_power = power[:len(power)//2]
            # Avoid log(0)
            half_power = np.log1p(half_power)
            # Aggregate: mean of mid-frequencies (ignoring DC and highest noise)
            if len(half_power) > 4:
                mid_freq = half_power[len(half_power)//4 : 3*len(half_power)//4]
                feat = np.mean(mid_freq) if len(mid_freq) > 0 else 0.0
            else:
                feat = np.mean(half_power) if len(half_power) > 0 else 0.0
            features.append(feat)
        
        return np.array(features)

    def _structural_score(self, text: str) -> float:
        """Calculate a direct structural score based on logical consistency hints."""
        score = 0.0
        text_lower = text.lower()
        
        # Count primitives
        counts = {k: len(self.patterns[k].findall(text_lower)) for k in self.primitives}
        
        # Heuristic: Presence of conditionals + causals implies higher reasoning depth
        if counts['conditional'] > 0 and counts['causal'] > 0:
            score += 0.2
        
        # Negation handling: odd number of negations might flip truth value (simplified)
        if counts['negation'] % 2 == 1:
            score -= 0.1 # Penalty for complexity unless resolved
            
        # Quantifiers add weight
        score += counts['quantifier'] * 0.05
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        if max(len1, len2) == 0: return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Internal scoring mechanism."""
        # 1. Structural Parsing & Fourier
        X = self._parse_to_series(prompt + " " + candidate)
        spectral_feats = self._compute_spectral_features(X)
        
        # 2. Pragmatic Weighting
        weighted_feats = self.w_prag * spectral_feats
        structural_signal = np.sum(weighted_feats) / 10.0 # Normalize roughly
        
        # 3. Direct Structural Heuristics
        struct_score = self._structural_score(prompt + " " + candidate)
        
        # Combine signals
        raw_score = structural_signal + struct_score
        
        # 4. Mechanism Design: Map to probability via sigmoid
        # w learned offline (simulated here as identity + bias)
        w = 1.0 
        bias = 0.5
        logit = w * raw_score + bias
        p_hat = 1.0 / (1.0 + np.exp(-logit))
        
        # Clamp to avoid log(0)
        p_hat = np.clip(p_hat, 1e-5, 1 - 1e-5)
        
        # 5. Proper Scoring Rule (Logarithmic)
        # We assume the "ground truth" p=1 for the purpose of ranking candidates 
        # by their likelihood of being the intended correct answer structure-wise.
        # Score = log(p_hat)
        final_score = np.log(p_hat)
        
        reasoning = f"Spectral:{spectral_feats[0]:.2f}, Struct:{struct_score:.2f}, Prob:{p_hat:.2f}"
        return final_score, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # First pass: Calculate structural/spectral scores
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reason})
            scores.append(score)
        
        # Check if scores are too close (tie situation) -> Use NCD
        if len(candidates) > 1:
            max_s = max(scores)
            min_s = min(scores)
            # If range is small, NCD might break ties based on prompt alignment
            if max_s - min_s < 0.1:
                for i, res in enumerate(results):
                    ncd_val = self._ncd(prompt, res['candidate'])
                    # Lower NCD is better (more similar/compressible together)
                    # Adjust score slightly
                    res['score'] -= ncd_val * 0.01 
                    res['reasoning'] += f", NCD:{ncd_val:.2f}"

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score, _ = self._score_candidate(prompt, answer)
        # Convert log-score back to probability approximation
        # Since score = log(p), p = exp(score). 
        # But our score includes penalties. Let's map via sigmoid of the raw logic.
        # Re-extract raw logic roughly:
        X = self._parse_to_series(prompt + " " + answer)
        spectral_feats = self._compute_spectral_features(X)
        struct_score = self._structural_score(prompt + " " + answer)
        raw = np.sum(self.w_prag * spectral_feats) / 10.0 + struct_score
        
        conf = 1.0 / (1.0 + np.exp(-(raw + 0.5)))
        return float(np.clip(conf, 0.0, 1.0))