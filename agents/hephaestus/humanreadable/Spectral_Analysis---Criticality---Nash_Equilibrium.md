# Spectral Analysis + Criticality + Nash Equilibrium

**Fields**: Signal Processing, Complex Systems, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:21:59.611027
**Report Generated**: 2026-03-27T06:37:39.061720

---

## Nous Analysis

**Algorithm – Spectral‑Critical‑Nash Scorer**

1. **Proposition extraction** – Using only the Python `re` module, scan each candidate answer for atomic clauses that contain:  
   - Negations (`not`, `no`, `never`)  
   - Comparatives (`more … than`, `less … than`, `greater`, `fewer`)  
   - Conditionals (`if … then`, `provided that`, `unless`)  
   - Causal cues (`because`, `leads to`, `results in`)  
   - Numeric tokens (`\d+(\.\d+)?`)  
   - Ordering relations (`before`, `after`, `earlier`, `later`)  
   Each clause becomes a proposition *pᵢ* and is stored in a list `props`. A dictionary maps each proposition to an integer index.

2. **Similarity graph** – For every pair (i,j) compute a lightweight similarity score:  
   - TF‑IDF vectors built from the clause’s tokens (using `collections.Counter` and numpy for dot‑products).  
   - Cosine similarity `sᵢⱼ = (v_i·v_j)/(‖v_i‖‖v_j‖)`.  
   - Apply a threshold τ (e.g., 0.3) to keep only meaningful links, yielding a weighted adjacency matrix **A** (numpy float64, shape n×n). Self‑loops are zero.

3. **Spectral analysis (coherence)** – Compute the combinatorial Laplacian **L** = **D** – **A**, where **D** is the degree matrix (row sums of **A**).  
   - Eigenvalues λ₀…λₙ₋₁ are obtained with `numpy.linalg.eigvalsh(L)` (real symmetric).  
   - The *spectral gap* γ = λ₁ (the second‑smallest eigenvalue, λ₀ = 0 for a connected component). Larger γ indicates stronger global coherence.

4. **Criticality proxy (susceptibility)** – Approximate the system’s susceptibility χ as the inverse of the gap: χ = 1/(γ + ε), with ε = 1e‑6 to avoid division by zero. A high χ signals proximity to a critical point (fragile coherence).

5. **Nash equilibrium (strategy stability)** – Treat each proposition as a pure strategy in a symmetric game. Define a payoff matrix **P** where  
   - Pᵢⱼ = similarity sᵢⱼ if the pair is logically compatible (no direct negation detected between the clauses),  
   - Pᵢⱼ = –sᵢⱼ if a negation relation is found (i.e., one clause denies the other).  
   - Compute a mixed‑strategy equilibrium by iteratively applying the best‑response dynamics: start with uniform distribution **x₀**, update **xₖ₊₁** = softmax(**P**·**xₖ**) until ‖xₖ₊₁ – xₖ‖₁ < 1e‑4 (numpy operations only). The equilibrium payoff **π** = **x**ᵀ**P****x** quantifies how stable the set of propositions is against unilateral deviation.

6. **Final score** – Combine the three terms (weights can be tuned, e.g., w₁=0.4, w₂=0.3, w₃=0.3):  
   ```
   score = w1 * (γ / γ_max)   # normalized spectral gap (order)
          - w2 * (χ / χ_max) # penalize closeness to criticality
          + w3 * ((π - π_min)/(π_max - π_min)) # reward Nash stability
   ```
   All normalisations use the observed min/max across the batch of candidates. The score is higher for answers that are internally coherent, not overly fragile, and form a stable mutual‑support set of propositions.

**Structural features parsed**  
- Negations (explicit “not”, “no”, “never”)  
- Comparatives (“more … than”, “less … than”, “greater”, “fewer”)  
- Conditionals (“if … then”, “provided that”, “unless”)  
- Causal claims (“because”, “leads to”, “results in”)  
- Numeric values (integers, decimals)  
- Ordering/temporal relations (“before”, “after”, “earlier”, “later”)  
- Logical connectives (“and”, “or”, “but”) are implicitly captured via co‑occurrence in the similarity vectors.

**Novelty**  
Spectral graph methods have been used for document coherence and community detection; criticality concepts appear in neuroscience and complex‑systems literature; Nash equilibria have been applied to dialogue and negotiation. The specific pipeline — extracting fine‑grained logical propositions, building a weighted similarity graph, measuring the Laplacian gap as an order metric, treating its inverse as susceptibility, and solving for a mixed‑strategy Nash equilibrium to assess propositional stability — does not, to my knowledge, appear in existing work. Hence the combination is novel.

**Rating**

Reasoning: 7/10 — The algorithm captures logical consistency via spectral gap and game‑theoretic stability, but relies on shallow similarity heuristics rather than deep semantic reasoning.  
Metacognition: 6/10 — It estimates uncertainty (susceptibility) yet does not explicitly model the system’s own reasoning process or confidence calibration.  
Implementability: 8/10 — All steps use only numpy and the Python standard library; no external libraries or APIs are required, making it straightforward to deploy.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | N/A |
| Implementability | 8/10 |
| **Composite** | **6.5** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Spectral Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Nash Equilibrium**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Criticality + Spectral Analysis: strong positive synergy (+0.401). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Epistemology + Criticality + Nash Equilibrium (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Spectral Analysis + Criticality (accuracy: 0%, calibration: 0%)
- Measure Theory + Spectral Analysis + Nash Equilibrium (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T01:53:52.296577

---

## Code

**Source**: scrap

[View code](./Spectral_Analysis---Criticality---Nash_Equilibrium/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Critical-Nash Scorer.
    Mechanism:
    1. Proposition Extraction: Parses atomic clauses containing logical markers (negations, comparatives, conditionals, causals, numbers, ordering).
    2. Similarity Graph: Builds a weighted adjacency matrix based on TF-IDF cosine similarity between propositions.
    3. Spectral Analysis: Computes the Laplacian spectral gap (gamma) as a measure of global coherence.
    4. Criticality: Uses inverse gap (susceptibility) to penalize fragile coherence.
    5. Nash Equilibrium: Simulates best-response dynamics on a payoff matrix derived from logical compatibility to find strategy stability.
    6. Scoring: Combines coherence, criticality, and stability into a final rank score.
    """

    # Logical markers for proposition extraction
    MARKERS = [
        r'\bnot\b', r'\bno\b', r'\bnever\b',  # Negations
        r'\bmore\s+\w+\s+than\b', r'\bless\s+\w+\s+than\b', r'\bgreater\b', r'\bfewer\b',  # Comparatives
        r'\bif\b.*\bthen\b', r'\bprovided\s+that\b', r'\bunless\b',  # Conditionals
        r'\bbecause\b', r'\bleads\s+to\b', r'\bresults\s+in\b',  # Causal
        r'\d+(\.\d+)?',  # Numbers
        r'\bbefore\b', r'\bafter\b', r'\bearlier\b', r'\blater\b'  # Ordering
    ]
    PATTERN = re.compile(r'|'.join(MARKERS), re.IGNORECASE)
    
    # Splitter for atomic clauses (simplified)
    SPLITTER = re.compile(r'[.;!?]')

    def __init__(self):
        self.epsilon = 1e-6

    def _extract_props(self, text: str) -> List[str]:
        """Extract atomic clauses containing logical markers."""
        props = []
        # Split by sentence delimiters
        segments = self.SPLITTER.split(text)
        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue
            # Check if segment contains any marker
            if self.PATTERN.search(seg):
                props.append(seg.lower())
        return props if props else [text.lower()] # Fallback if no markers found

    def _tfidf_vector(self, prop: str, vocab: Dict[str, int], doc_freq: np.ndarray, total_docs: int) -> np.ndarray:
        """Compute TF-IDF vector for a proposition."""
        tokens = re.findall(r'\b\w+\b', prop)
        if not tokens:
            return np.zeros(len(vocab))
        
        tf = Counter(tokens)
        vec = np.zeros(len(vocab))
        
        for word, count in tf.items():
            if word in vocab:
                idx = vocab[word]
                # TF: raw count (simplified)
                # IDF: log(total_docs / doc_freq)
                idf = math.log((total_docs + 1) / (doc_freq[idx] + 1))
                vec[idx] = count * idf
        
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def _build_graph(self, props: List[str]) -> Tuple[np.ndarray, List[str]]:
        """Build similarity matrix A and return props list."""
        n = len(props)
        if n == 0:
            return np.array([[0.0]]), []
        
        # Build vocabulary
        all_tokens = []
        prop_tokens = []
        for p in props:
            toks = re.findall(r'\b\w+\b', p)
            prop_tokens.append(toks)
            all_tokens.extend(toks)
        
        vocab = {w: i for i, w in enumerate(set(all_tokens))}
        if not vocab:
            return np.zeros((n, n)), props

        # Document frequency
        doc_freq = np.zeros(len(vocab))
        for toks in prop_tokens:
            unique = set(toks)
            for w in unique:
                if w in vocab:
                    doc_freq[vocab[w]] += 1
        
        # Compute vectors
        vectors = []
        for p in props:
            vec = self._tfidf_vector(p, vocab, doc_freq, n)
            vectors.append(vec)
        
        # Similarity Matrix (Cosine)
        A = np.zeros((n, n), dtype=np.float64)
        for i in range(n):
            for j in range(i + 1, n):
                dot_prod = np.dot(vectors[i], vectors[j])
                # Vectors are normalized, so dot_prod is cosine similarity
                if dot_prod > 0.3: # Threshold tau
                    A[i, j] = dot_prod
                    A[j, i] = dot_prod
        
        return A, props

    def _compute_spectral_gap(self, A: np.ndarray) -> float:
        """Compute Laplacian spectral gap."""
        n = A.shape[0]
        if n <= 1:
            return 0.0
        
        D = np.diag(A.sum(axis=1))
        L = D - A
        
        # Eigenvalues (sorted)
        try:
            eigvals = np.linalg.eigvalsh(L)
        except np.linalg.LinAlgError:
            return 0.0
            
        # Gamma = lambda_1 (second smallest)
        gamma = eigvals[1] if len(eigvals) > 1 else 0.0
        return float(gamma)

    def _compute_nash_stability(self, A: np.ndarray, props: List[str]) -> float:
        """Compute Nash equilibrium payoff via best-response dynamics."""
        n = A.shape[0]
        if n == 0:
            return 0.0
        if n == 1:
            return 1.0

        # Payoff matrix P: similarity if compatible, -similarity if negation conflict
        P = A.copy()
        
        # Detect negation conflicts (simplified: if one has 'not' and other doesn't, but similar topic)
        # For this implementation, we assume high similarity implies compatibility unless explicit negation tokens clash
        has_neg = [bool(re.search(r'\b(not|no|never)\b', p)) for p in props]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    P[i, j] = 0
                    continue
                # If both have negation or neither, they are compatible (positive)
                # If one has and other doesn't, and they are similar, potential conflict -> negative payoff
                if has_neg[i] != has_neg[j]:
                    P[i, j] = -A[i, j]
        
        # Best-response dynamics
        x = np.ones(n) / n  # Uniform start
        for _ in range(50):  # Iterations
            px = P @ x
            # Softmax
            exp_px = np.exp(px - np.max(px)) # Stability for softmax
            x_new = exp_px / np.sum(exp_px)
            
            if np.linalg.norm(x_new - x, 1) < 1e-4:
                break
            x = x_new
        
        # Equilibrium payoff pi = x^T P x
        pi = float(x.T @ P @ x)
        return pi

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        gammas = []
        chis = []
        pis = []
        
        # Pre-calculate metrics for normalization
        raw_data = []
        for cand in candidates:
            props = self._extract_props(cand)
            if not props:
                raw_data.append((cand, 0.0, 0.0, 0.0))
                continue
                
            A, valid_props = self._build_graph(props)
            gamma = self._compute_spectral_gap(A)
            chi = 1.0 / (gamma + self.epsilon)
            pi = self._compute_nash_stability(A, valid_props)
            
            raw_data.append((cand, gamma, chi, pi))
        
        if not raw_data:
            return [{"candidate": c, "score": 0.0, "reasoning": "No logical structure found."} for c in candidates]

        # Normalize
        gammas = [d[1] for d in raw_data]
        chis = [d[2] for d in raw_data]
        pis = [d[3] for d in raw_data]
        
        max_g = max(gammas) if max(gammas) > 0 else 1.0
        max_c = max(chis) if max(chis) > 0 else 1.0
        min_p = min(pis)
        max_p = max(pis)
        range_p = (max_p - min_p) if (max_p - min_p) > 0 else 1.0
        
        final_scores = []
        for i, (cand, g, c, p) in enumerate(raw_data):
            # Score = w1*norm(gamma) - w2*norm(chi) + w3*norm(pi)
            # Note: High chi (fragility) is bad, so subtract.
            norm_g = g / max_g
            norm_c = c / max_c
            norm_p = (p - min_p) / range_p
            
            score = 0.4 * norm_g - 0.3 * norm_c + 0.3 * norm_p
            final_scores.append((cand, score))
        
        # Sort descending
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        output = []
        for cand, sc in final_scores:
            output.append({
                "candidate": cand,
                "score": float(sc),
                "reasoning": f"Spectral gap: {sc:.4f} (Coherence-Stability metric)"
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on internal scoring logic."""
        # Evaluate single candidate against a dummy set to get relative score
        # Since we need absolute confidence, we check internal consistency metrics directly
        props = self._extract_props(answer)
        if not props:
            return 0.1 # Low confidence if no logical structure
        
        A, valid_props = self._build_graph(props)
        gamma = self._compute_spectral_gap(A)
        pi = self._compute_nash_stability(A, valid_props)
        
        # Heuristic mapping to 0-1
        # High gamma (coherence) and high pi (stability) -> high confidence
        # Normalize roughly: gamma usually 0-2 for small graphs, pi can be negative
        conf_g = min(gamma / 2.0, 1.0)
        conf_p = (pi + 1.0) / 2.0 # Assume pi range roughly -1 to 1
        conf_p = max(0.0, min(1.0, conf_p))
        
        return float(0.6 * conf_g + 0.4 * conf_p)
```

</details>
