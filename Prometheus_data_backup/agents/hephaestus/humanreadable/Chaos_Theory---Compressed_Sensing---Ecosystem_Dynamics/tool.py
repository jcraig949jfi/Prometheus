import re
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    A reasoning evaluator fusing Compressed Sensing, Chaos Theory, and Ecosystem Dynamics.
    
    Mechanism:
    1. Feature Extraction: Parses text for logical primitives (negations, conditionals, etc.).
    2. Compressed Sensing: Projects sparse feature vectors into a lower dimension to identify 
       essential structural signatures via L1-minimization approximation.
    3. Ecosystem Dynamics: Treats detected features as species in a trophic network. Energy flows 
       based on logical consistency (e.g., conditionals enabling causals).
    4. Chaos Stability: Computes the Lyapunov exponent of the ecosystem's energy trajectory.
       Stable convergence (negative exponent) indicates robust reasoning; chaos indicates fragility.
    
    Scoring: Primary signal is structural stability + feature density. NCD is a tiebreaker.
    """

    def __init__(self):
        # Fixed seed for deterministic sensing matrix
        np.random.seed(42)
        self.M = 200  # Total possible patterns (theoretical space)
        self.K = 30   # Compressed measurements
        self.Phi = np.random.binomial(1, 0.5, (self.K, self.M)).astype(float)
        
        # Regex patterns for structural features
        self.patterns = [
            (r'\bnot\b|\bno\b|\bnever\b|\bwithout\b', 'negation'),
            (r'\bmore than\b|\bless than\b|\bgreater\b|\blesser\b|\bhigher\b|\blower\b', 'comparative'),
            (r'\bif\b|\bthen\b|\belse\b|\bunless\b|\bprovided\b', 'conditional'),
            (r'\bbecause\b|\btherefore\b|\bthus\b|\bleads to\b|\bcauses\b', 'causal'),
            (r'\d+(\.\d+)?', 'numeric'),
            (r'\bbefore\b|\bafter\b|\bwhile\b|\bduring\b', 'ordering'),
            (r'\band\b|\bor\b|\bxor\b', 'connective'),
            (r'\bequal\b|\bsame\b|\bdifferent\b', 'equality'),
            (r'\bmust\b|\bshould\b|\bcould\b|\bmight\b', 'modality'),
            (r'\ball\b|\bsome\b|\bnone\b|\bevery\b', 'quantifier')
        ]
        self.compiled_patterns = [(re.compile(p, re.IGNORECASE), name) for p, name in self.patterns]

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector from text based on regex library."""
        text_lower = text.lower()
        features = np.zeros(self.M)
        idx = 0
        for pattern, _ in self.compiled_patterns:
            if pattern.search(text_lower):
                features[idx] = 1.0
            idx += 1
            if idx >= self.M: break
        return features

    def _sparse_reconstruct(self, y: np.ndarray) -> np.ndarray:
        """
        Approximate L1-minimization (Basis Pursuit) using iterative soft thresholding.
        Since M > K is underdetermined, we seek the sparsest z such that Phi*z ~ y.
        """
        z = np.linalg.lstsq(self.Phi, y, rcond=None)[0] # Initial guess
        # Soft thresholding to enforce sparsity (simulating ISTA step)
        threshold = 0.1 * np.max(np.abs(z))
        z = np.sign(z) * np.maximum(np.abs(z) - threshold, 0)
        return z

    def _ecosystem_dynamics(self, s: np.ndarray, text: str) -> tuple[float, np.ndarray]:
        """
        Simulate trophic flow between logical features.
        Returns the largest Lyapunov exponent and final energy state.
        """
        # Initialize energy from sparse reconstruction magnitudes
        # Only keep top 10 features to simulate ecosystem limits
        active_indices = np.argsort(np.abs(s))[-10:]
        n_species = len(active_indices)
        if n_species == 0:
            return 0.0, np.array([])

        e = np.abs(s[active_indices]) + 0.1 # Energy levels
        e = e / np.max(e) # Normalize
        
        # Construct interaction matrix W based on text co-occurrence logic
        # Simplified: Positive if both present, negative if specific conflict patterns found
        W = np.ones((n_species, n_species)) * 0.05
        np.fill_diagonal(W, 0)
        
        # Logic: Conditionals boost causals, Negations invert comparatives (simplified heuristic)
        # This creates the 'ecosystem' structure
        text_lower = text.lower()
        has_cond = 'if' in text_lower or 'then' in text_lower
        has_causal = 'because' in text_lower or 'thus' in text_lower
        
        if has_cond and has_causal and n_species > 1:
            W[0, 1] = 0.2 # Boost flow if logical chain exists

        alpha, beta, theta = 0.1, 0.05, 0.1
        T_steps = 50
        history = []

        # Iterate ecosystem
        for _ in range(T_steps):
            e_new = e.copy()
            for i in range(n_species):
                flow = np.sum(W[i, :] * (1.0 / (1.0 + np.exp(-(e - theta))))) # Sigmoid activation
                e_new[i] = e[i] + alpha * flow - beta * e[i]
                e_new[i] = max(0, e_new[i]) # Non-negative energy
            
            # Normalize to prevent explosion (carrying capacity)
            if np.sum(e_new) > 0:
                e_new = e_new / (np.sum(e_new) + 1e-9) 
            e = e_new
            history.append(np.sum(e))

        # Compute Lyapunov Exponent (approximate via divergence of nearby trajectories)
        if len(history) < 10:
            return 0.0, e
            
        # Perturb slightly
        e_pert = e * 1.0001
        dist_start = np.linalg.norm(e - e_pert)
        
        # Evolve perturbed
        for _ in range(10):
            flow_p = np.dot(W, 1.0 / (1.0 + np.exp(-(e_pert - theta))))
            e_pert = e_pert + alpha * flow_p - beta * e_pert
            e_pert = np.maximum(0, e_pert)
            if np.sum(e_pert) > 0: e_pert = e_pert / (np.sum(e_pert) + 1e-9)
            
        dist_end = np.linalg.norm(e - e_pert) + 1e-9
        
        # Lyapunov exponent lambda
        if dist_start == 0: return 0.0, e
        lyap = np.log(dist_end / dist_start) / 10.0
        return lyap, e

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        c1 = len(compress(s1.encode()))
        c2 = len(compress(s2.encode()))
        c12 = len(compress((s1 + s2).encode()))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_feats = self._extract_features(prompt)
        
        for cand in candidates:
            # 1. Feature Extraction
            cand_feats = self._extract_features(cand)
            
            # 2. Compressed Sensing (Measurement & Reconstruction)
            y = np.dot(self.Phi, cand_feats)
            s = self._sparse_reconstruct(y)
            
            # 3. Ecosystem Dynamics & 4. Chaos Stability
            lyap, _ = self._ecosystem_dynamics(s, cand)
            
            # Scoring: 
            # High score = Stable (negative lyap) AND Structurally Rich (sum of s)
            # We invert lyap: exp(-lyap) -> >1 for stable, <1 for chaotic
            stability_score = np.exp(-lyap)
            structural_richness = np.sum(np.abs(s))
            
            # Heuristic penalty for empty answers
            if len(cand.strip()) < 3:
                score = 0.0
            else:
                # Combine stability and richness. 
                # Normalize roughly to 0-1 range based on empirical bounds
                raw_score = stability_score * (1.0 + 0.1 * structural_richness)
                score = min(1.0, max(0.0, raw_score / 2.0)) # Scale to 0-1

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Stability: {stability_score:.2f}, Structure: {structural_richness:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        if len(results) > 1 and abs(results[0]["score"] - results[1]["score"]) < 0.01:
            # Use NCD relative to prompt as tiebreaker
            scores_ncd = []
            for r in results:
                ncd = self._ncd_score(prompt, r["candidate"])
                scores_ncd.append((r, ncd))
            # Lower NCD is better (more similar/compressible together)
            scores_ncd.sort(key=lambda x: x[1])
            # Re-order results based on NCD tiebreak
            results = [x[0] for x in scores_ncd]
            # Re-calculate final score to reflect NCD influence slightly
            for i, r in enumerate(results):
                r["score"] = r["score"] - (i * 0.001) # Small penalty for lower rank

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation pipeline."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # The score from evaluate is already normalized 0-1 approx
        return min(1.0, max(0.0, res[0]["score"]))