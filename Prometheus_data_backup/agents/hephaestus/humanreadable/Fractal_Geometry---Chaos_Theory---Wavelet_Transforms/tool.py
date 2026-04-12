import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning evaluator combining structural parsing (primary),
    wavelet-based fractal dimension estimation, and Lyapunov-like stability analysis.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals), numeric values, and causal cues. Scores based 
       on logical consistency with the prompt's constraints.
    2. Wavelet-Fractal Analysis: Converts text to binary token vectors, applies 
       Haar wavelet transform, estimates fractal dimension (D) of energy spectrum 
       to measure multi-scale coherence.
    3. Lyapunov Stability: Measures sensitivity to token-level noise; stable 
       answers (low lambda) indicate robust reasoning structures.
    4. Scoring: Weighted combination of structural score (alpha), normalized 
       fractal dimension (beta), and stability (gamma), with NCD as tiebreaker.
    """
    
    # Structural patterns for parsing
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|\w+er)\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided|when|while)\b', re.I),
        'causal': re.compile(r'\b(because|leads to|results in|causes|therefore|thus)\b', re.I),
        'ordering': re.compile(r'\b(before|after|preceding|following|first|last)\b', re.I),
        'numeric': re.compile(r'\d+(\.\d+)?')
    }

    def __init__(self):
        self.lambda_max = 2.0  # Calibration constant for Lyapunov normalization
        self.alpha = 0.6       # Weight for structural parsing
        self.beta = 0.25       # Weight for fractal dimension
        self.gamma = 0.15      # Weight for stability

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace tokenizer, lower-cased."""
        return text.lower().split()

    def _to_binary_vector(self, tokens: List[str], vocab: List[str]) -> np.ndarray:
        """Convert tokens to binary occurrence vector based on vocab."""
        vec = np.zeros(len(vocab), dtype=float)
        token_set = set(tokens)
        for i, word in enumerate(vocab):
            if word in token_set:
                vec[i] = 1.0
        return vec

    def _haar_wavelet(self, x: np.ndarray) -> List[np.ndarray]:
        """Compute discrete Haar wavelet decomposition levels."""
        coeffs = []
        signal = x.copy()
        n = len(signal)
        # Pad to power of 2
        size = 1
        while size < n:
            size *= 2
        signal = np.pad(signal, (0, size - n), mode='constant')
        
        current = signal
        while len(current) > 1:
            half = len(current) // 2
            # Approximation and Detail coefficients
            approx = (current[0::2] + current[1::2]) / 2.0
            detail = (current[0::2] - current[1::2]) / 2.0
            coeffs.append(detail)
            current = approx
        return coeffs

    def _estimate_fractal_dim(self, coeffs: List[np.ndarray]) -> float:
        """Estimate fractal dimension from wavelet energy spectrum."""
        scales = []
        energies = []
        for s, detail in enumerate(coeffs):
            if len(detail) == 0:
                continue
            energy = np.sum(detail ** 2)
            if energy > 0:
                scales.append(np.log2(s + 1))  # Scale index
                energies.append(np.log2(energy))
        
        if len(scales) < 2:
            return 0.0
            
        # Linear regression for slope
        A = np.vstack([scales, np.ones(len(scales))]).T
        try:
            slope, _ = np.linalg.lstsq(A, energies, rcond=None)[0]
            return -slope  # Fractal dimension D ≈ -slope
        except:
            return 0.0

    def _compute_lyapunov(self, tokens: List[str], vocab: List[str]) -> float:
        """Compute Lyapunov-like exponent via perturbation."""
        x = self._to_binary_vector(tokens, vocab)
        epsilon = 1e-3
        noise = np.random.uniform(-0.5, 0.5, len(x))
        x_pert = x + epsilon * noise
        x_pert = np.clip(x_pert, 0, 1)  # Keep in [0,1] range roughly
        
        # Wavelet decomposition
        w_orig = self._haar_wavelet(x)
        w_pert = self._haar_wavelet(x_pert)
        
        delta_es = []
        min_len = min(len(w_orig), len(w_pert))
        for i in range(min_len):
            e_orig = np.sum(w_orig[i] ** 2)
            e_pert = np.sum(w_pert[i] ** 2)
            diff = abs(e_orig - e_pert)
            if diff > 0:
                delta_es.append(np.log(diff / epsilon))
        
        if not delta_es:
            return 0.0
        return np.mean(delta_es)

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Extract logical and structural features from text."""
        features = {}
        for key, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            features[key] = matches
        return features

    def _score_structure(self, prompt: str, candidate: str) -> float:
        """Score based on structural alignment with prompt."""
        p_feats = self._extract_structural_features(prompt)
        c_feats = self._extract_structural_features(candidate)
        
        score = 0.0
        count = 0
        
        # Check for presence of similar logical structures
        for key in ['negation', 'conditional', 'causal', 'ordering']:
            if p_feats[key]:
                count += 1
                if c_feats[key]:
                    score += 1.0
        
        # Numeric consistency check
        p_nums = p_feats['numeric']
        c_nums = c_feats['numeric']
        if p_nums:
            count += 1
            # Simple heuristic: if prompt has numbers, answer should too or be logical
            if c_nums:
                score += 1.0
            elif any(k in c_feats for k in ['negation', 'conditional']):
                score += 0.5 # Logical operator compensates for lack of numbers
                
        if count == 0:
            return 0.5
        return min(1.0, score / max(1, count))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        return c12 / max(c1, c2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Build global vocab for wavelet consistency (optional, but good for relative comparison)
        all_tokens = set()
        for c in candidates:
            all_tokens.update(self._tokenize(c))
        vocab = sorted(list(all_tokens))
        
        # Pre-calculate reference if needed, here we just use max score for normalization
        scores = []
        
        for cand in candidates:
            # 1. Structural Score (Primary)
            struct_score = self._score_structure(prompt, cand)
            
            # 2. Wavelet/Fractal Analysis
            tokens = self._tokenize(cand)
            if not tokens:
                fractal_score = 0.0
                stability_score = 0.0
            else:
                vec = self._to_binary_vector(tokens, vocab)
                if np.sum(vec) == 0:
                    fractal_score = 0.0
                    stability_score = 0.0
                else:
                    coeffs = self._haar_wavelet(vec)
                    D = self._estimate_fractal_dim(coeffs)
                    # Normalize D: Theoretical max is log2(T), approximate normalization
                    T = len(vec)
                    D_norm = D / np.log2(T) if T > 1 else 0
                    # Target D around 0.5 (rich but not chaotic)
                    fractal_score = 1.0 - abs(D_norm - 0.5) * 2
                    fractal_score = max(0, min(1, fractal_score))
                    
                    # 3. Lyapunov Stability
                    lam = self._compute_lyapunov(tokens, vocab)
                    stability_score = max(0, 1.0 - abs(lam) / self.lambda_max)
            
            # 4. Combine Scores
            total_score = (self.alpha * struct_score + 
                           self.beta * fractal_score + 
                           self.gamma * stability_score)
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"Structural: {struct_score:.2f}, Fractal: {fractal_score:.2f}, Stability: {stability_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        if len(results) > 1:
            if abs(results[0]['score'] - results[1]['score']) < 0.01:
                # Re-sort based on NCD to prompt (lower NCD usually better for relevance in ties)
                # Note: In reasoning, sometimes diversity is good, but NCD measures similarity to prompt context
                # We assume the prompt contains necessary context, so similarity helps.
                results.sort(key=lambda x: self._ncd(prompt, x['candidate']))

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']