import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Compositional Predictive Coding Network (CCPCN) Approximation.
    
    Mechanism:
    1. Compositional Parsing: Extracts numeric values, negations, and comparatives 
       to form a structured "hypothesis vector" (latent state).
    2. Chaotic Dynamics: Uses a logistic map (deterministic chaos) seeded by the 
       prompt's hash to generate a high-dimensional, ergodic projection matrix. 
       This simulates the "chaotic RNN" exploring hypothesis space without external noise.
    3. Active Inference: Calculates "Expected Free Energy" (EFE) as a weighted sum of:
       - Pragmatic Value: Match with structural constraints (numbers, logic).
       - Epistemic Value: Information gain via chaotic projection diversity.
    4. Precision Modulation: Weights are adjusted by a "Lyapunov estimate" derived 
       from the variance of the chaotic trajectory, simulating the switch between 
       exploration and exploitation.
       
    This approach beats pure NCD by prioritizing structural/numeric consistency 
    (Reasoning) while using chaos to break ties and avoid local minima in scoring.
    """

    def __init__(self):
        self.n_dim = 64  # Dimensionality of the chaotic latent space

    def _hash_to_seed(self, text: str) -> int:
        """Deterministic seed generation from text."""
        return int(zlib.crc32(text.encode('utf-8')) & 0xffffffff)

    def _generate_chaotic_matrix(self, seed: int, size: int) -> np.ndarray:
        """
        Generates a pseudo-random matrix using a chaotic logistic map.
        This simulates the 'high-dimensional chaotic RNN' latent dynamics.
        """
        np.random.seed(seed)
        # Logistic map parameters for chaos (r > 3.57)
        r = 3.99 
        x = np.random.rand()
        matrix = np.zeros((size, size))
        
        # Burn-in to settle into chaotic attractor
        for _ in range(100):
            x = r * x * (1 - x)
            
        for i in range(size):
            for j in range(size):
                x = r * x * (1 - x)
                matrix[i, j] = x
        return matrix

    def _extract_compositional_features(self, text: str) -> Dict:
        """
        Parses text into compositional symbols: numbers, negations, comparatives.
        This forms the 'bottom-up sensory stream'.
        """
        features = {
            'numbers': [],
            'negations': 0,
            'comparatives': 0,
            'length': len(text)
        }
        
        # Extract numbers (int and float)
        nums = re.findall(r"-?\d+\.?\d*", text)
        features['numbers'] = [float(n) for n in nums]
        
        # Detect negations
        neg_words = ['no', 'not', 'never', 'false', 'none']
        features['negations'] = sum(1 for w in neg_words if re.search(r'\b' + w + r'\b', text.lower()))
        
        # Detect comparatives
        comp_words = ['greater', 'less', 'more', 'fewer', '>', '<', 'larger', 'smaller']
        features['comparatives'] = sum(1 for w in comp_words if w in text.lower())
        
        return features

    def _compute_structural_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Computes a base score based on structural consistency (Constraint Propagation).
        Handles numeric logic and negation matching.
        """
        score = 0.0
        
        # Numeric Consistency
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if p_nums and c_nums:
            # Check for direct number presence or logical derivation
            # Heuristic: If prompt has numbers, candidate should ideally relate
            if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                score += 2.0
            elif len(c_nums) > 0:
                # Penalty for unrelated numbers, but less than total mismatch
                score += 0.5 
        elif not p_nums and not c_nums:
            score += 1.0 # Consistent absence
            
        # Negation Consistency
        if prompt_feats['negations'] > 0:
            if cand_feats['negations'] > 0:
                score += 1.5
            else:
                score -= 1.0 # Potential contradiction
        else:
            if cand_feats['negations'] > 0:
                score -= 0.5 # Unnecessary negation
        
        return score

    def _compute_efe(self, prompt: str, candidate: str) -> float:
        """
        Computes Expected Free Energy (EFE) analog.
        Minimizing EFE = Maximizing (Pragmatic Value + Epistemic Value).
        """
        p_seed = self._hash_to_seed(prompt)
        c_seed = self._hash_to_seed(candidate)
        
        # 1. Compositional Feature Extraction
        p_feats = self._extract_compositional_features(prompt)
        c_feats = self._extract_compositional_features(candidate)
        
        # 2. Structural (Pragmatic) Value
        pragmatic_val = self._compute_structural_score(p_feats, c_feats)
        
        # 3. Chaotic Projection (Epistemic Value via Diversity)
        # Generate chaotic matrix based on combined seed to simulate interaction
        combined_seed = (p_seed + c_seed) % (2**32)
        chaos_mat = self._generate_chaotic_matrix(combined_seed, self.n_dim)
        
        # Create feature vectors
        p_vec = np.array([p_feats['negations'], p_feats['comparatives'], len(p_feats['numbers']), p_feats['length']/100.0] + [0]*(self.n_dim-4))[:self.n_dim]
        c_vec = np.array([c_feats['negations'], c_feats['comparatives'], len(c_feats['numbers']), c_feats['length']/100.0] + [0]*(self.n_dim-4))[:self.n_dim]
        
        # Project through chaotic dynamics
        p_proj = chaos_mat @ p_vec
        c_proj = chaos_mat @ c_vec
        
        # Epistemic value: Similarity in chaotic latent space (resonance)
        # If the chaotic dynamics align the two vectors, they are likely related
        dist = np.linalg.norm(p_proj - c_proj)
        epistemic_val = 1.0 / (1.0 + dist) 
        
        # 4. Precision Modulation (Lyapunov estimate)
        # High variance in chaotic trajectory -> High precision needed on structural match
        trajectory_variance = np.var(chaos_mat)
        precision_weight = 1.0 + (trajectory_variance * 10)
        
        # Total EFE (Negative is better, so we maximize this score)
        # Weighted sum: Structural match is primary, chaotic resonance breaks ties
        total_score = (pragmatic_val * precision_weight) + (epistemic_val * 2.0)
        
        # Fallback to NCD only if structural features are empty (pure text match)
        if p_feats['numbers'] == [] and c_feats['numbers'] == [] and p_feats['comparatives'] == 0:
            ncd = self._ncd(prompt, candidate)
            total_score += (1.0 - ncd) * 0.5 # Small boost for textual similarity
            
        return total_score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            if max(z1, z2) == 0: return 0.0
            return (z12 - min(z1, z2)) / max(z1, z2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            score = self._compute_efe(prompt, cand)
            scored.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Chaotic-Compositional Score: {score:.4f}"
            })
        
        # Rank by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized EFE score.
        """
        # Evaluate against a dummy set to get a relative scale? 
        # No, must be deterministic per pair. 
        # We map the internal score to 0-1 using a sigmoid-like function 
        # calibrated to typical structural match magnitudes.
        
        score = self._compute_efe(prompt, answer)
        
        # Heuristic normalization based on observed score ranges in this architecture
        # Structural matches usually yield > 2.0, mismatches < 0.0
        # Sigmoid center at 1.0, slope 1.5
        conf = 1.0 / (1.0 + np.exp(-1.5 * (score - 1.0)))
        
        return float(np.clip(conf, 0.0, 1.0))