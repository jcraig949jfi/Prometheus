import re
import numpy as np
from collections import deque
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning scorer based on Fractal Geometry, Criticality, and Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical links (negation, comparatives, conditionals, 
       causality, ordering) into a weighted adjacency matrix W.
    2. Fractal Analysis: Computes box-counting dimension across thresholds to measure self-similarity.
    3. Criticality: Identifies the threshold where susceptibility (variance of component size) peaks.
    4. Free Energy: Calculates prediction error relative to a uniform prior (0.5).
    5. Scoring: Combines normalized metrics into a final score.
    """
    
    def __init__(self):
        self.weights = (0.4, 0.3, 0.3)  # Fractal, Critical, FreeEnergy

    def _parse_text(self, text: str) -> Tuple[List[str], np.ndarray]:
        """Parse text into nodes and adjacency matrix W."""
        # Simple sentence splitter and tokenizer for demonstration
        # In a real engine, this would be a full NLP parser. 
        # Here we simulate atomic propositions based on delimiters.
        raw_sentences = re.split(r'[.;!?]', text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        if not sentences:
            return [], np.array([])
        
        nodes = sentences
        n = len(nodes)
        W = np.zeros((n, n))
        
        # Regex patterns
        pat_neg = re.compile(r'\b(not|no|never)\b', re.I)
        pat_comp = re.compile(r'\b(greater|less|more|less|before|after)\b', re.I)
        pat_cond = re.compile(r'\b(if|unless|then)\b', re.I)
        pat_cause = re.compile(r'\b(because|leads to|results in|causes)\b', re.I)
        pat_num = re.compile(r'\d+\.?\d*')
        
        for i, s in enumerate(nodes):
            # Base confidence from sentence length/complexity proxy
            base_conf = min(1.0, len(s) / 100.0 + 0.2)
            
            # Self-loop weight initialization
            W[i, i] = base_conf 
            
            # Check modifiers to adjust weight or create edges
            if pat_neg.search(s):
                # Negation reduces confidence slightly or flags node (simulated by weight mod)
                W[i, i] = max(0.1, W[i, i] - 0.2)
            
            if pat_comp.search(s):
                # Comparative implies strong relation
                val = 0.8 if "much" in s.lower() else 0.6
                # Create synthetic edge to next/prev if exists (simulated graph structure)
                if i > 0: W[i, i-1] = max(W[i, i-1], val)
                if i < n-1: W[i, i+1] = max(W[i, i+1], val)
                
            if pat_cond.search(s) or pat_cause.search(s):
                # Strong causal/conditional link
                val = 0.9
                if i > 0: W[i, i-1] = max(W[i, i-1], val)
                if i < n-1: W[i, i+1] = max(W[i, i+1], val)
                
            # Numeric extraction adds stability
            nums = pat_num.findall(s)
            if nums:
                W[i, i] = min(1.0, W[i, i] + 0.1)

        # Symmetrize for undirected component analysis (simplification)
        W = (W + W.T) / 2
        # Normalize to [0, 1]
        if W.max() > 0:
            W = W / W.max()
            
        return nodes, W

    def _compute_fractal_dim(self, W: np.ndarray) -> float:
        """Estimate fractal dimension via box-counting on thresholded graphs."""
        if W.size == 0: return 0.0
        n = W.shape[0]
        if n == 0: return 0.0
        
        thresholds = np.linspace(0.1, 0.9, 9)
        dims = []
        
        # Box size radii
        radii = list(range(1, max(2, int(np.ceil(np.log2(n + 1)) + 1))))
        
        for tau in thresholds:
            G_bin = (W >= tau).astype(int)
            # Simple box counting approximation: count components at different scales
            # Since true graph box-counting is complex, we approximate via component scaling
            counts = []
            for r in radii:
                # Simulate covering: greedy BFS with radius r
                visited = set()
                boxes = 0
                nodes = list(range(n))
                for start in nodes:
                    if start in visited: continue
                    boxes += 1
                    # BFS limited to r
                    q = deque([(start, 0)])
                    visited.add(start)
                    while q:
                        u, d = q.popleft()
                        if d >= r: continue
                        for v in range(n):
                            if G_bin[u, v] > 0 and v not in visited:
                                visited.add(v)
                                q.append((v, d+1))
                counts.append(boxes)
            
            # Fit log(N) vs log(1/r)
            if len(counts) > 1 and len(radii) > 1:
                x = np.log(1.0 / np.array(radii[:len(counts)]))
                y = np.log(counts)
                # Avoid division by zero or invalid logs
                valid = np.isfinite(x) & np.isfinite(y)
                if np.sum(valid) > 1:
                    slope, _ = np.polyfit(x[valid], y[valid], 1)
                    dims.append(abs(slope))
        
        return float(np.mean(dims)) if dims else 0.0

    def _compute_criticality(self, W: np.ndarray) -> Tuple[float, float]:
        """Find susceptibility peak and distance to critical point 0.5."""
        if W.size == 0: return 0.0, 0.5
        n = W.shape[0]
        thresholds = np.linspace(0.05, 0.95, 20)
        sizes = []
        
        for tau in thresholds:
            G_bin = (W >= tau).astype(int)
            # Find largest weakly connected component size
            visited = set()
            max_size = 0
            for i in range(n):
                if i in visited: continue
                comp_size = 0
                q = deque([i])
                visited.add(i)
                while q:
                    u = q.popleft()
                    comp_size += 1
                    for v in range(n):
                        if G_bin[u, v] > 0 and v not in visited:
                            visited.add(v)
                            q.append(v)
                max_size = max(max_size, comp_size)
            sizes.append(max_size)
        
        sizes = np.array(sizes)
        # Susceptibility approximated by variance over sliding window or global variance proxy
        # Here we use global variance of component sizes across thresholds as a proxy for susceptibility
        chi = np.var(sizes) if len(sizes) > 1 else 0.0
        
        # Find tau* where transition happens (steepest change in max component size)
        # Approximate derivative
        if len(sizes) > 1:
            diffs = np.abs(np.diff(sizes))
            peak_idx = np.argmax(diffs)
            tau_star = thresholds[peak_idx]
        else:
            tau_star = 0.5
            
        dist = abs(tau_star - 0.5)
        return float(chi), float(dist)

    def _compute_free_energy(self, W: np.ndarray) -> float:
        """Compute Free Energy score based on prediction error from uniform prior."""
        if W.size == 0: return 0.0
        
        prior = 0.5
        epsilon = (W - prior) ** 2
        sum_eps = np.sum(epsilon)
        
        # Variance of W
        sigma_sq = np.var(W) if W.size > 0 else 1e-6
        if sigma_sq < 1e-9: sigma_sq = 1e-9 # Prevent log(0)
        
        # F = Sum(eps) / (2*sigma^2) - 0.5 * log(sigma^2)
        # Note: Lower F is better. We will invert this later for scoring.
        F = (sum_eps / (2 * sigma_sq)) - 0.5 * np.log(sigma_sq)
        return float(F)

    def _normalize(self, val: float, min_v: float, max_v: float) -> float:
        if max_v - min_v == 0: return 0.5
        return (val - min_v) / (max_v - min_v)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        all_fractal = []
        all_crit = []
        all_fe = []
        
        # First pass to collect normalization stats
        raw_scores = []
        for cand in candidates:
            # Combine prompt and candidate for context
            full_text = f"{prompt} {cand}"
            nodes, W = self._parse_text(full_text)
            
            if len(nodes) == 0:
                raw_scores.append((cand, 0.0, "No structure detected"))
                continue
                
            D = self._compute_fractal_dim(W)
            chi, dist = self._compute_criticality(W)
            F = self._compute_free_energy(W)
            
            raw_scores.append((cand, D, chi, dist, F))
            all_fractal.append(D)
            all_crit.append((chi, dist))
            all_fe.append(F)
            
        if not raw_scores:
            return [{"candidate": c, "score": 0.0, "reasoning": "Empty"} for c in candidates]

        # Normalize metrics
        min_D, max_D = min(all_fractal), max(all_fractal)
        min_F, max_F = min(all_fe), max(all_fe)
        
        # Criticality metric: 1 - (dist / 0.5)
        crit_metrics = [1.0 - (min(d[1], 0.5) / 0.5) for d in all_crit]
        min_C, max_C = min(crit_metrics), max(crit_metrics)

        final_results = []
        for i, (cand, D, chi, dist, F) in enumerate(raw_scores):
            # Normalize
            norm_D = self._normalize(D, min_D, max_D)
            norm_C = self._normalize(crit_metrics[i], min_C, max_C)
            # Free Energy: Lower is better, so invert normalization logic or subtract from 1
            norm_F_raw = self._normalize(F, min_F, max_F)
            norm_F = 1.0 - norm_F_raw 
            
            score = self.weights[0]*norm_D + self.weights[1]*norm_C + self.weights[2]*norm_F
            score = max(0.0, min(1.0, score)) # Clamp
            
            reasoning = f"Fractal={norm_D:.2f}, Critical={norm_C:.2f}, FreeEnergy={norm_F:.2f}"
            final_results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
            
        # Sort descending by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']