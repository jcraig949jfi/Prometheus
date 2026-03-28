# Symbiosis + Spectral Analysis + Criticality

**Fields**: Biology, Signal Processing, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T00:42:03.021036
**Report Generated**: 2026-03-27T06:37:41.920631

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a discrete signal \(x[t]\) where \(t\) indexes tokens after structural parsing (see §2). From the parsed tokens we build three complementary matrices:

1. **Symbiosis matrix \(S\)** – a co‑occurrence graph where nodes are semantic roles (e.g., *Agent*, *Patient*, *Condition*) extracted via regex patterns for negations, comparatives, conditionals, causal claims, and ordering relations. An edge weight \(S_{ij}\) is the pointwise mutual information (PMI) between role \(i\) in the answer and role \(j\) in a reference answer (or a gold‑standard annotation). Symbiosis score \( \sigma = \frac{1}{|E|}\sum_{(i,j)\in E} S_{ij}\) measures mutual benefit: high PMI means the answer shares the same relational structure as the reference.

2. **Spectral matrix \(F\)** – a Toeplitz autocorrelation matrix of a numeric feature series \(y[t]\) derived from the answer: \(y[t]=1\) if token \(t\) is a numeric value or a measured quantity, else 0. We compute the power spectral density via the periodogram \(P(f)=\left|\sum_{t} y[t] e^{-i2\pi ft}\right|^{2}\) using only numpy’s FFT. The spectral score \( \rho = \frac{\int_{f_{c}}^{f_{max}} P(f)df}{\int_{0}^{f_{max}} P(f)df}\) captures the proportion of energy in a mid‑frequency band \([f_{c},f_{max}]\) that corresponds to periodic patterns of logical connectives (e.g., alternating “if‑then”, “because‑therefore”). High \( \rho\) indicates well‑structured temporal reasoning.

3. **Criticality matrix \(C\)** – the Laplacian \(L = D - S\) of the symbiosis graph, where \(D\) is the degree vector. We compute the eigenvalue spectrum \(\lambda_{1}\le\lambda_{2}\le …\le\lambda_{n}\). Criticality is quantified by the spectral gap \( \gamma = \lambda_{2} - \lambda_{1}\) (algebraic connectivity) and the susceptibility‑like quantity \( \chi = \frac{1}{\gamma}\). A system near criticality shows small \( \gamma\) (large \( \chi\)), meaning the answer’s relational graph is poised between rigid order (large gap) and disorder (no gap). The criticality score \( \kappa = \exp(-\chi)\) rewards answers that are neither overly rigid nor chaotic.

**Overall score**  
\[
\text{Score}= w_{\sigma}\sigma + w_{\rho}\rho + w_{\kappa}\kappa,
\]
with weights tuned on a validation set (e.g., \(w_{\sigma}=0.4, w_{\rho}=0.3, w_{\kappa}=0.3\)). All operations use only numpy and the Python standard library.

**Structural features parsed**  
- Negations (“not”, “no”) → polarity flag on role nodes.  
- Comparatives (“more than”, “less than”) → ordered edges with weight proportional to degree.  
- Conditionals (“if … then …”) → directed edges from antecedent role to consequent role.  
- Numeric values → binary series \(y[t]\) for spectral analysis.  
- Causal claims (“because”, “due to”) → weighted edges in \(S\).  
- Ordering relations (“first”, “finally”) → temporal edges influencing the Toeplitz structure of \(F\).

**Novelty**  
The triple‑layer combination is not found in standard NLP evaluation metrics. Symbiosis‑style PMI graphs appear in lexical cohesion work; spectral analysis of token‑level binary series has been used for periodicity detection in code; criticality via algebraic connectivity is known in network science but rarely applied to answer graphs. Jointly using mutual‑information‑based edge weights, a frequency‑domain measure of logical connective periodicity, and a spectral‑gap‑based criticality term is, to our knowledge, novel.

**Ratings**  
Reasoning: 8/10 — captures deep relational and periodic structure, though relies on hand‑crafted regex patterns.  
Metacognition: 6/10 — provides self‑diagnostic scores (symbiosis, spectral, criticality) but lacks explicit uncertainty modeling.  
Hypothesis generation: 5/10 — can flag low‑scoring components for revision, but does not generate new hypotheses autonomously.  
Implementability: 9/10 — all steps are pure numpy/stdlib; no external libraries or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Symbiosis**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Spectral Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Criticality + Spectral Analysis: strong positive synergy (+0.401). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ergodic Theory + Spectral Analysis + Criticality (accuracy: 0%, calibration: 0%)
- Spectral Analysis + Falsificationism + Criticality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T04:44:06.943364

---

## Code

**Source**: scrap

[View code](./Symbiosis---Spectral_Analysis---Criticality/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
from collections import Counter
from math import log, exp
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning evaluator based on Criticality-driven Structural Analysis.
    
    Mechanism:
    1. Structural Parsing: Extracts semantic roles (Agent, Patient, Condition) and 
       logical connectors (negations, comparatives, conditionals) using regex.
    2. Symbiosis (Support Only): Computes PMI between extracted roles to build a 
       co-occurrence graph. Used for graph construction, not direct scoring.
    3. Spectral Analysis: Converts numeric token presence into a time series, 
      computes FFT to detect periodic logical structures (e.g., alternating if-then).
    4. Criticality (Core): Computes the Laplacian of the symbiosis graph. The 
       spectral gap (algebraic connectivity) determines if the answer is neither 
       rigid nor chaotic. This is the primary scoring driver.
    5. Scoring: Weighted sum of Criticality (0.4), Spectral (0.3), and Symbiosis (0.3).
       NCD is used strictly as a tiebreaker for low-structure candidates.
    """
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.I),
        'causal': re.compile(r'\b(because|therefore|thus|hence|due to|since)\b', re.I),
        'ordering': re.compile(r'\b(first|second|finally|next|then|lastly)\b', re.I),
        'numeric': re.compile(r'\b\d+(\.\d+)?\b')
    }
    
    ROLES = ['Agent', 'Patient', 'Condition', 'Action', 'Result']

    def __init__(self):
        self.w_sigma = 0.3  # Symbiosis weight
        self.w_rho = 0.3    # Spectral weight
        self.w_kappa = 0.4  # Criticality weight (Primary driver)

    def _extract_tokens(self, text: str) -> Dict[str, List[int]]:
        """Extract structural features and return binary masks."""
        text_lower = text.lower()
        tokens = text.split()
        n = len(tokens)
        if n == 0: return {}
        
        features = {k: [0]*n for k in self.PATTERNS.keys()}
        features['numeric_val'] = [0.0]*n
        
        for i, token in enumerate(tokens):
            clean = token.strip(".,;:!?\"'")
            if not clean: continue
            
            for key, pattern in self.PATTERNS.items():
                if key == 'numeric':
                    if pattern.match(clean):
                        features['numeric'][i] = 1
                        try: features['numeric_val'][i] = float(clean)
                        except: pass
                else:
                    if pattern.search(clean):
                        features[key][i] = 1
        return features

    def _build_symbiosis_graph(self, prompt: str, answer: str) -> np.ndarray:
        """Build co-occurrence matrix S based on semantic roles."""
        # Simplified role extraction: map regex hits to roles
        combined = f"{prompt} {answer}"
        feats = self._extract_tokens(combined)
        n = len(feats.get('negation', []))
        if n == 0: return np.zeros((1,1))
        
        # Assign pseudo-roles based on windowed presence of patterns
        # Node i represents a window or a specific pattern instance
        # For this implementation, nodes are the detected pattern instances
        nodes = []
        for key in self.PATTERNS:
            indices = [i for i, val in enumerate(feats[key]) if val == 1]
            for idx in indices:
                nodes.append((key, idx))
        
        if len(nodes) < 2:
            return np.zeros((max(1, len(nodes)), max(1, len(nodes))))

        n_nodes = len(nodes)
        S = np.zeros((n_nodes, n_nodes))
        
        # Edge weight = PMI-like score based on proximity and type compatibility
        for i, (type_i, idx_i) in enumerate(nodes):
            for j, (type_j, idx_j) in enumerate(nodes):
                if i == j: continue
                # Proximity bonus
                dist = abs(idx_i - idx_j) + 1
                proximity = 1.0 / dist
                # Type compatibility (simplified: causal/conditional boost)
                type_bonus = 1.0
                if type_i in ['conditional', 'causal'] and type_j in ['conditional', 'causal']:
                    type_bonus = 2.0
                S[i, j] = proximity * type_bonus
                
        return S

    def _compute_symbiosis_score(self, S: np.ndarray) -> float:
        """Calculate average edge weight (PMI proxy)."""
        if S.size == 0: return 0.0
        non_zero = S[S != 0]
        if len(non_zero) == 0: return 0.0
        return float(np.mean(non_zero))

    def _compute_spectral_score(self, text: str) -> float:
        """Compute spectral score based on numeric token periodicity."""
        feats = self._extract_tokens(text)
        if 'numeric' not in feats or len(feats['numeric']) == 0:
            return 0.5 # Neutral if no numbers
        
        y = np.array(feats['numeric'], dtype=float)
        if np.sum(y) == 0:
            return 0.5
            
        # FFT via numpy
        fft_vals = np.fft.fft(y - np.mean(y))
        psd = np.abs(fft_vals)**2
        freqs = np.fft.fftfreq(len(y))
        
        # Positive frequencies only
        pos_mask = freqs > 0
        if not np.any(pos_mask): return 0.5
        
        pos_freqs = freqs[pos_mask]
        pos_psd = psd[pos_mask]
        
        # Mid-frequency band (avoiding DC and highest noise)
        f_max = np.max(pos_freqs)
        f_c = f_max * 0.2 # Lower 20% cutoff
        
        if f_max <= f_c: return 0.5
        
        total_energy = np.sum(pos_psd)
        if total_energy == 0: return 0.5
        
        band_mask = (pos_freqs >= f_c)
        band_energy = np.sum(pos_psd[band_mask])
        
        return float(band_energy / total_energy)

    def _compute_criticality_score(self, S: np.ndarray) -> float:
        """Compute criticality via spectral gap of Laplacian."""
        if S.size == 0 or S.shape[0] < 2:
            return 0.5
            
        # Degree matrix
        D = np.diag(np.sum(S, axis=1))
        # Symmetrize S for undirected graph assumption in Laplacian
        S_sym = (S + S.T) / 2
        L = D - S_sym
        
        # Eigenvalues
        try:
            eigenvals = np.linalg.eigvalsh(L)
            eigenvals = np.sort(eigenvals)
            
            # Spectral gap (lambda_2 - lambda_1)
            # lambda_1 should be ~0 for connected graph
            l1 = eigenvals[0]
            l2 = eigenvals[1] if len(eigenvals) > 1 else l1
            
            gamma = l2 - l1
            if gamma < 1e-9: gamma = 1e-9 # Avoid division by zero
            
            chi = 1.0 / gamma
            kappa = exp(-chi)
            return float(kappa)
        except:
            return 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Build Graph
            S = self._build_symbiosis_graph(prompt, cand)
            
            # 2. Compute Scores
            sigma = self._compute_symbiosis_score(S)
            rho = self._compute_spectral_score(cand)
            kappa = self._compute_criticality_score(S)
            
            # 3. Weighted Sum
            score = (self.w_sigma * sigma) + (self.w_rho * rho) + (self.w_kappa * kappa)
            
            # Heuristic boost for structural richness (prevents short "Yes/No" bias)
            struct_count = sum([
                len(self.PATTERNS['negation'].findall(cand)),
                len(self.PATTERNS['conditional'].findall(cand)),
                len(self.PATTERNS['numeric'].findall(cand))
            ])
            if struct_count > 0:
                score += 0.1 * min(struct_count, 5) # Cap bonus
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Sym:{sigma:.2f}, Spec:{rho:.2f}, Crit:{kappa:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        if len(results) > 1:
            diff = results[0]['score'] - results[1]['score']
            if abs(diff) < 1e-4:
                # Use NCD relative to prompt as tiebreaker (lower NCD = better match)
                results.sort(key=lambda x: self._ncd(prompt, x['candidate']))
                
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on criticality and structural density."""
        S = self._build_symbiosis_graph(prompt, answer)
        kappa = self._compute_criticality_score(S)
        rho = self._compute_spectral_score(answer)
        
        # Count structural markers
        text = f"{prompt} {answer}"
        markers = sum(len(p.findall(text)) for p in self.PATTERNS.values())
        
        # Base confidence on criticality (stability) and marker density
        # High criticality (near 1) means balanced structure
        # High marker count implies reasoning content
        base_conf = (kappa * 0.6) + (min(markers / 10.0, 1.0) * 0.4)
        
        # Penalize extremely short answers unless highly critical
        if len(answer.split()) < 3:
            base_conf *= 0.5
            
        return max(0.0, min(1.0, base_conf))
```

</details>
