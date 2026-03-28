# Fractal Geometry + Criticality + Free Energy Principle

**Fields**: Mathematics, Complex Systems, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T13:57:58.820186
**Report Generated**: 2026-03-27T06:37:37.140295

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use a handful of regex patterns to extract atomic propositions and the logical links between them:  
   - Negation (`not`, `no`) → attach a ¬ flag to the target proposition.  
   - Comparatives (`greater than`, `less than`, `more`, `less`) → create a directed edge labelled *cmp* with weight proportional to the comparative magnitude (e.g., 1 for “more”, 0.5 for “somewhat more”).  
   - Conditionals (`if … then …`, `unless`) → edge labelled *cond*.  
   - Causal claims (`because`, `leads to`, `results in`) → edge labelled *cause*.  
   - Ordering (`before`, `after`, `first`, `last`) → edge labelled *ord*.  
   - Numeric values are captured as attributes on the source or target node.  
   Each proposition becomes a node; each link becomes a weighted directed edge. Store the graph as a NumPy adjacency matrix **W** (shape *n × n*) where *Wᵢⱼ*∈[0,1] is the cue‑derived confidence.

2. **Multi‑scale representation (Fractal Geometry)** – For a set of thresholds 𝜏 = {0.1,0.2,…,0.9} create binary graphs **Gₜ** = (W ≥ 𝜏). For each **Gₜ** compute a box‑counting covering:  
   - Choose a box size *r* (graph‑hop radius).  
   - Starting from each uncovered node, perform a BFS limited to *r* hops to form a box; mark all visited nodes as covered.  
   - Count *Nₜ(r)* boxes needed. Repeat for *r* = 1…⌈log₂ n⌉.  
   - Fit log Nₜ(r) vs. log (1/r) with NumPy’s `polyfit` (degree 1); the slope is the estimated fractal dimension *Dₜ*.  

3. **Criticality detection** – For each 𝜏 compute the size *Sₜ* of the largest weakly‑connected component. The susceptibility is χₜ = Var(S) over a sliding window of 𝜏 values (NumPy `var`). Identify 𝜏* where χₜ peaks; the distance |𝜏* − 0.5| measures how close the argument sits to the critical point (order‑disorder boundary).  

4. **Free‑Energy Principle scoring** – Assume a prior expectation **P** of uniform edge weight 0.5. Prediction error for each edge is εᵢⱼ = (Wᵢⱼ − 0.5)². Free energy *F* = Σ εᵢⱼ / (2σ²) − ½ log|Σ|, where σ² is the variance of **W** (NumPy) and Σ its covariance; the entropy term reduces to ½ log(σ²) for the scalar case. Lower *F* indicates better prediction‑error minimization.  

5. **Final score** – Normalize each metric to [0,1]:  
   - *Fractal* = (D̄ − D_min)/(D_max − D_min) where D̄ is the mean *Dₜ* over thresholds.  
   - *Critical* = 1 − (|𝜏* − 0.5| / 0.5).  
   - *FreeEnergy* = 1 − (F − F_min)/(F_max − F_min).  
   Score = w₁·Fractal + w₂·Critical + w₃·FreeEnergy (weights sum to 1, e.g., 0.4,0.3,0.3). Higher scores indicate answers whose internal logical structure is self‑similar across scales, poised near criticality, and minimally surprising under a uniform prior.

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering relations, explicit numeric values, quantifiers (“all”, “some”), and conjunction/disjunction cues. These are mapped directly to edge types and node attributes.

**Novelty**  
Purely syntactic similarity or bag‑of‑words methods ignore higher‑order graph dynamics. While fractal analysis of concept maps, criticality in neural avalanches, and free‑energy formulations of cognition exist separately, integrating all three to score argument structure has not been reported in the literature. The approach is therefore novel in its specific combination, though it builds on established network‑science and predictive‑coding tools.

**Rating**  
Reasoning: 7/10 — The algorithm captures multi‑scale logical coherence and prediction error, but relies on hand‑crafted regex and simple weighting, limiting deep semantic grasp.  
Metacognition: 5/10 — It provides internal diagnostics (fractal dimension, susceptibility, free energy) that can signal over‑ or under‑confidence, yet lacks explicit self‑monitoring loops.  
Hypothesis generation: 4/10 — The method scores existing candidates; proposing new hypotheses would require additional generative components not present here.  
Implementability: 8/10 — All steps use only NumPy and the Python standard library; regex, matrix operations, BFS, and linear fits are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Fractal Geometry**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Fractal Geometry + Free Energy Principle: strong positive synergy (+0.474). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Criticality + Free Energy Principle: strong positive synergy (+0.369). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Evolution + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Fractal Geometry + Cellular Automata + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T10:10:33.950289

---

## Code

**Source**: scrap

[View code](./Fractal_Geometry---Criticality---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
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
```

</details>
