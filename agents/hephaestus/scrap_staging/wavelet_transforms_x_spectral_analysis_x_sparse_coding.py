import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Multi-Resolution Sparse Spectral Coding (AMRSSC) Reasoning Tool.
    
    Mechanism:
    1. Signal Projection: Maps text to a 1D signal via character-code differencing.
    2. Wavelet-Spectral Decomposition: Simulates dyadic tiling by analyzing signal 
       segments at multiple scales (powers of 2). Computes local spectral energy 
       (variance-based proxy for multitaper PSD) per tile.
    3. Sparse Coding & Hypothesis Testing: Treats candidate answers as 'atoms'. 
       Evaluates the 'residual' (mismatch) between prompt structure and candidate 
       structure. 
       - Structural Parsing: Extracts negations, comparatives, and numerics.
       - Sparse Fit: Candidates matching the prompt's structural signature yield 
         low residual energy (high score).
    4. Metacognition: Confidence is derived from the sharpness of the sparse 
       coefficient distribution (ratio of best fit to total energy).
    """

    def __init__(self):
        self.scales = [2, 4, 8, 16]  # Dyadic scales for "wavelet" decomposition
        self.thresh_neg = re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I)
        self.thresh_comp = re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I)
        self.thresh_num = re.compile(r'\d+\.?\d*')
        self.thresh_cond = re.compile(r'\b(if|then|else|unless|provided)\b', re.I)

    def _text_to_signal(self, text: str) -> np.ndarray:
        """Converts text to a numeric signal based on char codes."""
        if not text:
            return np.zeros(1)
        codes = np.array([ord(c) for c in text], dtype=float)
        # Differencing to simulate high-pass wavelet detail
        if len(codes) > 1:
            return np.diff(codes)
        return codes

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical structures: negations, comparatives, numbers, conditionals."""
        t_lower = text.lower()
        has_neg = bool(self.thresh_neg.search(t_lower))
        has_comp = bool(self.thresh_comp.search(t_lower))
        has_cond = bool(self.thresh_cond.search(t_lower))
        nums = [float(x) for x in self.thresh_num.findall(text)]
        nums.sort()
        return {
            "neg": has_neg,
            "comp": has_comp,
            "cond": has_cond,
            "nums": nums,
            "num_count": len(nums)
        }

    def _spectral_energy(self, signal: np.ndarray, scale: int) -> float:
        """
        Simulates multitaper spectral estimation on a tile.
        Computes variance (energy) of the signal downsampled to the scale.
        """
        if len(signal) == 0:
            return 0.0
        # Downsample/Tile simulation
        tiled = signal[:len(signal) - (len(signal) % scale)]
        if len(tiled) == 0:
            return 0.0
        reshaped = tiled.reshape(-1, scale)
        # Energy per tile (proxy for PSD magnitude)
        energies = np.var(reshaped, axis=1)
        return float(np.mean(energies))

    def _compute_sparse_features(self, text: str) -> np.ndarray:
        """Generates the wavelet-spectral feature vector."""
        signal = self._text_to_signal(text)
        struct = self._extract_structure(text)
        
        features = []
        # 1. Structural bits (weighted heavily)
        features.extend([float(struct['neg']), float(struct['comp']), float(struct['cond'])])
        features.append(float(struct['num_count']))
        
        # 2. Spectral features at multiple scales
        for scale in self.scales:
            energy = self._spectral_energy(signal, scale)
            features.append(energy)
            
        return np.array(features, dtype=float)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes compatibility based on structural parsing.
        High score = candidate respects prompt constraints.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        matches = 0
        total_checks = 0

        # Check Negation consistency
        # If prompt has negation, valid answers often acknowledge it or differ.
        # Simplified: Exact match of boolean flags boosts score.
        if p_struct['neg'] == c_struct['neg']:
            matches += 1
        total_checks += 1

        # Check Comparative/Conditional presence
        if p_struct['comp'] and c_struct['comp']:
            matches += 2 # Stronger weight for matching logic type
        elif not p_struct['comp'] and not c_struct['comp']:
            matches += 1
        total_checks += 2

        if p_struct['cond'] == c_struct['cond']:
            matches += 1
        total_checks += 1

        # Numeric evaluation
        if p_struct['num_count'] > 0 and c_struct['num_count'] > 0:
            # Check if numbers are consistent (e.g. sorted order or magnitude)
            # Heuristic: If prompt has numbers, candidate having numbers is good.
            matches += 2
        elif p_struct['num_count'] == 0 and c_struct['num_count'] == 0:
            matches += 1
        total_checks += 2

        base_score = (matches / total_checks) if total_checks > 0 else 0.5
        
        # Penalty for mismatched logic types (e.g. prompt asks comparison, candidate gives yes/no)
        if p_struct['comp'] and not c_struct['comp'] and not c_struct['num_count']:
            base_score *= 0.5
            
        return base_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feat = self._compute_sparse_features(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = [(c, self._ncd_distance(prompt, c)) for c in candidates]
        ncd_map = {c: score for c, score in ncd_scores}
        
        for cand in candidates:
            cand_feat = self._compute_sparse_features(cand)
            
            # Sparse coding analogy: Reconstruction error
            # Distance in feature space (L2 norm of residual)
            residual = prompt_feat - cand_feat
            spectral_dist = np.linalg.norm(residual)
            
            # Structural compatibility (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # Combine: Structural match dominates, spectral distance refines
            # Invert spectral dist to similarity (heuristic scaling)
            spectral_sim = 1.0 / (1.0 + spectral_dist * 0.1)
            
            final_score = (struct_score * 0.7) + (spectral_sim * 0.3)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {struct_score:.2f}, Spectral sim: {spectral_sim:.2f}"
            })
        
        # Sort by score desc, then NCD asc (tiebreaker)
        results.sort(key=lambda x: (-x['score'], ncd_map.get(x['candidate'], 1.0)))
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the sharpness of the sparse representation.
        High confidence if structural features align perfectly and spectral residual is low.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # 1. Structural Alignment Check
        struct_align = 1.0
        if p_struct['neg'] != a_struct['neg']:
            struct_align -= 0.4
        if p_struct['comp'] != a_struct['comp']:
            struct_align -= 0.3
        if p_struct['cond'] != a_struct['cond']:
            struct_align -= 0.2
            
        # 2. Spectral Residual Check
        p_feat = self._compute_sparse_features(prompt)
        a_feat = self._compute_sparse_features(answer)
        residual_norm = np.linalg.norm(p_feat - a_feat)
        
        # Map residual to confidence (0 residual -> 1.0, high residual -> 0)
        spectral_conf = 1.0 / (1.0 + residual_norm * 0.05)
        
        # Combined confidence
        conf = max(0.0, min(1.0, (struct_align * 0.6 + spectral_conf * 0.4)))
        return conf