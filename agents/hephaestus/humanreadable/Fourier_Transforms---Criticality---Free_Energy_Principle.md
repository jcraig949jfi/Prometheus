# Fourier Transforms + Criticality + Free Energy Principle

**Fields**: Mathematics, Complex Systems, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T05:39:18.098408
**Report Generated**: 2026-04-02T11:44:50.130925

---

## Nous Analysis

**Algorithm**  
1. **Parse** each candidate answer into a list of *propositions* P₁…Pₙ using regex patterns that extract:  
   - Negations (`\bnot\b|\bno\b|\bn’t\b`)  
   - Comparatives (`\bmore\b|\bless\b|\bgreater\b|\blesser\b`)  
   - Conditionals (`\bif\b.*\bthen\b|\bunless\b`)  
   - Causal cues (`\bbecause\b|\bdue\ to\b|\bleads\ to\b`)  
   - Numbers (`\d+(\.\d+)?`)  
   - Ordering (`\bfirst\b|\bsecond\b|\bbefore\b|\bafter\b|\b>\b|\b<\b`)  
   Each proposition yields a binary feature vector **f**ᵢ∈{0,1}ᵏ (k = number of feature types).  

2. **Build a relation matrix** R∈{0,1}ⁿˣⁿ where R[i,j]=1 if a regex‑detected link (e.g., causal, comparative) connects proposition i to j.  

3. **Form a multivariate signal** X(t)∈ℝⁿ by ordering propositions as they appear in the text and setting X[t]=∑ᵢ R[t,i]·**f**ᵢ (i.e., a weighted sum of feature counts at position t).  

4. **Fourier Transform**: compute the discrete FFT of each dimension of X using `np.fft.fft`. Aggregate power spectrum P(f)=|FFT|² averaged over dimensions.  

5. **Criticality score**: fit a line to log₁₀(P) vs log₁₀(f) (excluding f=0) via `np.linalg.lstsq`. Let β be the slope. Ideal critical 1/f noise has β≈−1. Define C = −|β+1| (higher when slope close to −1).  

6. **Free‑energy (prediction error)**: fit a first‑order autoregressive model X̂[t+1]=A·X[t] (least‑squares solution A = X[1:]·X[:-1]ᵀ·(X[:-1]·X[:-1]ᵀ)⁻¹). Compute MSE = mean‖X[t+1]−X̂[t+1]‖². Add a complexity term ½·log‖cov(X‖ (determinant of covariance). Free energy F = MSE + 0.5·log‖cov‖. Lower F is better.  

7. **Score** candidate answer: S = w₁·C − w₂·F (weights w₁,w₂ set to 1.0 for simplicity). Higher S indicates answer whose propositional signal exhibits critical spectral dynamics and low prediction error, i.e., aligns with the combined principles.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations (first/second, before/after, >/<).  

**Novelty** – While predictive coding and critical brain hypotheses exist, applying FFT‑based spectral analysis to a discrete logical‑relation time series and scoring answers via proximity to 1/f criticality plus free‑energy minimization is not present in current NLP evaluation tools; it bridges signal processing, statistical physics, and Bayesian cognition in a concrete algorithm.  

**Ratings**  
Reasoning: 7/10 — captures logical structure via spectral criticality and prediction error.  
Metacognition: 5/10 — limited self‑monitoring; no explicit uncertainty calibration beyond FE.  
Hypothesis generation: 6/10 — AR model generates forward predictions, but generative scope is narrow.  
Implementability: 8/10 — relies only on numpy, regex, and linear algebra; straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=37% cal=17% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:10:48.292700

---

## Code

**Source**: scrap

[View code](./Fourier_Transforms---Criticality---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Fourier-Criticality-FreeEnergy Reasoning Tool

Evaluates candidate answers by modeling their propositional structure as a
dynamical system, measuring:
1. Criticality: How close the power spectrum is to 1/f noise (critical dynamics)
2. Free Energy: Prediction error + complexity of autoregressive model
3. Dynamics: Trajectory stability under premise reordering

Epistemic honesty: Returns low confidence on ambiguous/presupposed questions.
"""

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple


class ReasoningTool:
    def __init__(self):
        self.w1 = 1.0  # criticality weight
        self.w2 = 1.0  # free energy weight
        self.w_dynamics = 0.8  # dynamics weight
        self.w_ncd = 0.15  # NCD weight (max 15%)
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by combined criticality, free energy, and dynamics."""
        results = []
        
        for cand in candidates:
            # Core spectral-FE score
            props = self._parse_propositions(cand)
            if len(props) < 2:
                # Fallback for very short answers
                score = self._fallback_score(prompt, cand)
                reasoning = "Short answer - fallback scoring"
            else:
                X = self._build_signal(props)
                C = self._criticality_score(X)
                F = self._free_energy(X)
                D = self._dynamics_score(props)
                
                # NCD tiebreaker
                ncd = self._ncd(prompt, cand)
                
                # Combined score
                score = self.w1 * C - self.w2 * F + self.w_dynamics * D - self.w_ncd * ncd
                reasoning = f"C={C:.3f} F={F:.3f} D={D:.3f} NCD={ncd:.3f}"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        # First check prompt quality
        meta_conf = self._meta_confidence(prompt)
        
        # Compute answer quality
        props = self._parse_propositions(answer)
        if len(props) < 1:
            answer_conf = 0.2
        else:
            X = self._build_signal(props)
            C = self._criticality_score(X)
            F = self._free_energy(X)
            D = self._dynamics_score(props)
            
            # Normalize to 0-1
            raw_score = self.w1 * C - self.w2 * F + self.w_dynamics * D
            answer_conf = 1.0 / (1.0 + np.exp(-raw_score))  # sigmoid
        
        # Cap by meta-confidence
        return min(meta_conf, answer_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerable questions."""
        p = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', p):
            return 0.25
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in p:
            return 0.28
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.27
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.29
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', p):
            if not re.search(r'\b(most|least|highest|lowest|measure|metric)\b', p):
                return 0.30
        
        # Insufficient information
        if re.search(r'\b(not enough|insufficient|cannot determine|ambiguous)\b', p):
            return 0.26
        
        return 0.85  # Default: assume answerable
    
    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract propositions with feature vectors."""
        sentences = re.split(r'[.!?;]', text)
        props = []
        
        for sent in sentences:
            if len(sent.strip()) < 3:
                continue
            
            features = {
                'negation': 1 if re.search(r'\bnot\b|\bno\b|\bn\'t\b', sent, re.I) else 0,
                'comparative': 1 if re.search(r'\b(more|less|greater|lesser|higher|lower)\b', sent, re.I) else 0,
                'conditional': 1 if re.search(r'\bif\b.*\bthen\b|\bunless\b', sent, re.I) else 0,
                'causal': 1 if re.search(r'\b(because|due to|leads to|causes|results in)\b', sent, re.I) else 0,
                'numeric': len(re.findall(r'\d+\.?\d*', sent)),
                'ordering': 1 if re.search(r'\b(first|second|before|after|then)\b|>|<', sent, re.I) else 0,
            }
            
            props.append({'text': sent.strip(), 'features': features})
        
        return props
    
    def _build_signal(self, props: List[Dict]) -> np.ndarray:
        """Build multivariate signal from propositions."""
        n = len(props)
        if n < 2:
            return np.array([[1.0]])
        
        # Feature matrix
        feat_keys = ['negation', 'comparative', 'conditional', 'causal', 'numeric', 'ordering']
        F = np.array([[p['features'][k] for k in feat_keys] for p in props], dtype=float)
        
        # Relation matrix: connect consecutive and causal/conditional props
        R = np.zeros((n, n))
        for i in range(n - 1):
            R[i, i + 1] = 1  # sequential
        for i in range(n):
            if props[i]['features']['causal'] or props[i]['features']['conditional']:
                for j in range(i + 1, min(i + 3, n)):
                    R[i, j] = 0.5
        
        # Build signal: X[t] = sum of connected features
        X = np.zeros((n, len(feat_keys)))
        for t in range(n):
            for i in range(n):
                X[t] += R[t, i] * F[i]
        
        return X + 1e-6  # avoid zeros
    
    def _criticality_score(self, X: np.ndarray) -> float:
        """Measure proximity to 1/f noise (critical dynamics)."""
        if X.shape[0] < 3:
            return 0.0
        
        # FFT on each dimension, aggregate power
        power_total = np.zeros(X.shape[0] // 2)
        for dim in range(X.shape[1]):
            fft = np.fft.fft(X[:, dim])
            power = np.abs(fft[:len(fft)//2]) ** 2
            power_total += power
        
        power_total /= X.shape[1]
        
        # Fit log-log slope (skip f=0)
        freqs = np.arange(1, len(power_total))
        if len(freqs) < 2:
            return 0.0
        
        log_f = np.log10(freqs + 1e-9)
        log_p = np.log10(power_total[1:] + 1e-9)
        
        # Linear fit
        A = np.vstack([log_f, np.ones(len(log_f))]).T
        beta, _ = np.linalg.lstsq(A, log_p, rcond=None)[0]
        
        # Criticality: how close to -1
        C = -np.abs(beta + 1.0)
        return C
    
    def _free_energy(self, X: np.ndarray) -> float:
        """Compute prediction error + complexity."""
        if X.shape[0] < 3:
            return 1.0
        
        # AR(1) model: X[t+1] = A * X[t]
        X_curr = X[:-1].T
        X_next = X[1:].T
        
        # Least squares: A = X_next * X_curr^T * (X_curr * X_curr^T)^-1
        try:
            gram = X_curr @ X_curr.T
            A = X_next @ X_curr.T @ np.linalg.pinv(gram)
        except:
            return 1.0
        
        # Prediction error
        X_pred = A @ X_curr
        mse = np.mean((X_next - X_pred) ** 2)
        
        # Complexity term
        cov = np.cov(X.T)
        sign, logdet = np.linalg.slogdet(cov + np.eye(cov.shape[0]) * 1e-6)
        complexity = 0.5 * logdet if sign > 0 else 1.0
        
        F = mse + complexity
        return F
    
    def _dynamics_score(self, props: List[Dict]) -> float:
        """Score based on trajectory stability under reordering."""
        if len(props) < 2:
            return 0.0
        
        # Build state trajectory
        states = []
        state = np.zeros(6)  # feature vector
        feat_keys = ['negation', 'comparative', 'conditional', 'causal', 'numeric', 'ordering']
        
        for p in props:
            for i, k in enumerate(feat_keys):
                state[i] += p['features'][k] * 0.7  # decay
            states.append(state.copy())
        
        states = np.array(states)
        
        # Convergence: measure variance reduction
        if len(states) > 1:
            early_var = np.var(states[:len(states)//2], axis=0).mean()
            late_var = np.var(states[len(states)//2:], axis=0).mean()
            convergence = max(0, early_var - late_var)
        else:
            convergence = 0.0
        
        # Stability: trajectory smoothness
        if len(states) > 2:
            diffs = np.diff(states, axis=0)
            smoothness = 1.0 / (1.0 + np.mean(np.abs(diffs)))
        else:
            smoothness = 0.5
        
        return convergence + smoothness
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _fallback_score(self, prompt: str, answer: str) -> float:
        """Fallback for very short answers."""
        # Check numeric match
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        a_nums = re.findall(r'\d+\.?\d*', answer)
        
        if p_nums and a_nums:
            return -self._ncd(prompt, answer)
        
        # Check negation consistency
        p_neg = bool(re.search(r'\bnot\b|\bno\b', prompt, re.I))
        a_neg = bool(re.search(r'\bnot\b|\bno\b', answer, re.I))
        
        if p_neg == a_neg:
            return 0.5
        
        return -self._ncd(prompt, answer)
```

</details>
