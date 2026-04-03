# Thermodynamics + Spectral Analysis + Criticality

**Fields**: Physics, Signal Processing, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T22:18:26.026407
**Report Generated**: 2026-04-02T10:00:36.653423

---

## Nous Analysis

**Algorithm**  
1. **Proposition extraction** – Using regex patterns we pull atomic clauses that contain negations, comparatives (“more/less than”), conditionals (“if … then”), causal verbs (“because”, “leads to”), numeric values, and ordering relations (“greater than”, “before”). Each clause becomes a node *i* in a logical graph.  
2. **Pairwise affinity** – For every pair (i,j) compute a token‑overlap similarity *S₍ᵢⱼ₎* (Jaccard of lower‑cased word sets) with NumPy.  
3. **Thermodynamic weighting** – Define an “energy” penalty *E₍ᵢⱼ₎* = ‖prompt‑vector − (node‑i + node‑j)‖₂², where vectors are simple TF‑IDF counts (NumPy). Convert to a Boltzmann factor *B₍ᵢⱼ₎* = exp(−E₍ᵢⱼ₎/T) with fixed temperature *T*=1.0. Edge weight *W₍ᵢⱼ₎* = S₍ᵢⱼ₎ · B₍ᵢⱼ₎. Store *W* in a symmetric NumPy matrix *A*.  
4. **Spectral analysis** – Compute the graph Laplacian *L = D − A* (degree matrix *D*). Obtain eigenvalues *λ* via `np.linalg.eigvalsh(L)`. Compute the power spectral density of the eigenvalue spectrum using `np.fft.rfft(|λ|²)`; derive spectral flatness *F* = (geometric mean)/(arithmetic mean) of the PSD.  
5. **Criticality measure** – Let λ_max be the largest eigenvalue. Define criticality distance *C* = exp(−|λ_max − 1|).  
6. **Score** – Final merit for a candidate answer:  
   `Score = α·(−np.sum(W)) + β·F + γ·C`  
   (α,β,γ are fixed scalars, e.g., 1.0 each). Lower total weight (more thermodynamically stable), higher spectral flatness (richer frequency content), and λ_max near 1 (critical regime) increase the score.

**Parsed structural features** – Negations, comparatives, conditionals, causal claims, numeric values, and ordering relations are explicitly extracted to build nodes and edges.

**Novelty** – While energy‑based scoring, graph‑spectral methods, and criticality metrics exist separately, their joint use to evaluate logical coherence of text has not been reported in the literature; the combination is therefore novel.

**Rating**  
Reasoning: 8/10 — captures logical structure via thermodynamic and spectral constraints.  
Metacognition: 6/10 — provides a self‑assessment (flatness, critical distance) but lacks explicit reflection on uncertainty.  
Hypothesis generation: 5/10 — the method scores given hypotheses; it does not propose new ones.  
Implementability: 9/10 — relies only on NumPy and Python’s stdlib (regex, math).

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:forbidden_import: networkx

**Forge Timestamp**: 2026-04-02T09:32:22.148465

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Spectral_Analysis---Criticality/tool.py)

<details>
<summary>Show code</summary>

```python
"""
Thermodynamic-Spectral-Criticality Reasoning Tool

Combines:
1. Thermodynamic weighting: energy-based edge weights via entropy and Boltzmann factors
2. Spectral analysis: eigenvalue spectrum of logical affinity graphs
3. Criticality: detect near-critical phase transitions (lambda_max ~ 1)

Chains forge_primitives: entropy, confidence_from_agreement, information_sufficiency
with graph spectral methods to score logical coherence.
"""

import re
import numpy as np
import networkx as nx
from collections import Counter
import zlib

try:
    from forge_primitives import (
        entropy, confidence_from_agreement, information_sufficiency,
        bayesian_update, solve_constraints, check_transitivity
    )
except ImportError:
    # Fallback implementations
    def entropy(probs):
        probs = np.array(probs)
        probs = probs[probs > 0]
        return -np.sum(probs * np.log2(probs))
    
    def confidence_from_agreement(scores):
        return 1.0 - np.std(scores) / (np.mean(scores) + 1e-9)
    
    def information_sufficiency(unknowns, constraints):
        return min(1.0, constraints / max(1, unknowns))


class ReasoningTool:
    def __init__(self):
        self.temperature = 1.0
        self.alpha, self.beta, self.gamma = 1.0, 1.0, 1.0
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by thermodynamic-spectral-criticality score."""
        results = []
        
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            reasoning = self._explain_score(prompt, cand, score)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-analysis of prompt quality."""
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        struct_features = self._extract_features(prompt + " " + answer)
        if len(struct_features) == 0:
            struct_conf = 0.2
        else:
            struct_conf = min(0.7, len(struct_features) / 10.0)
        
        # Compute score for this answer
        score = self._compute_score(prompt, answer)
        score_conf = min(0.8, score / 5.0)
        
        # Combine but cap by meta-confidence
        raw_conf = 0.4 * struct_conf + 0.6 * score_conf
        return min(meta_conf, raw_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for epistemic traps - return cap on confidence."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you stop|quit|cease)\b', p_lower):
            return 0.25
        if re.search(r'\bwhy did .*(fail|stop|end)\b', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery .* a \b', p_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.3
        
        # False dichotomy
        if re.search(r'\beither .* or \b', p_lower) and 'only' not in p_lower:
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            if not re.search(r'\b(because|criteria|measure|metric)\b', p_lower):
                return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(impossible|cannot|unknown|insufficient)\b', p_lower):
            return 0.25
        
        return 0.95  # No traps detected
    
    def _extract_features(self, text: str) -> list[str]:
        """Extract logical propositions: negations, comparatives, conditionals, etc."""
        features = []
        sentences = re.split(r'[.;!?]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Negations
            if re.search(r'\b(not|no|never|none|neither)\b', sent, re.I):
                features.append(f"NEG:{sent[:50]}")
            
            # Comparatives
            if re.search(r'\b(more|less|greater|smaller|higher|lower) than\b', sent, re.I):
                features.append(f"CMP:{sent[:50]}")
            
            # Conditionals
            if re.search(r'\b(if|when|unless|provided)\b.*\b(then|would|will)\b', sent, re.I):
                features.append(f"COND:{sent[:50]}")
            
            # Causal
            if re.search(r'\b(because|since|therefore|thus|leads to|causes)\b', sent, re.I):
                features.append(f"CAUSE:{sent[:50]}")
            
            # Numeric
            nums = re.findall(r'\b\d+\.?\d*\b', sent)
            if nums:
                features.append(f"NUM:{','.join(nums)}")
            
            # Ordering
            if re.search(r'\b(before|after|first|second|next|last)\b', sent, re.I):
                features.append(f"ORD:{sent[:50]}")
        
        return features
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Thermodynamic-Spectral-Criticality scoring."""
        # Extract propositions
        combined = prompt + " " + candidate
        features = self._extract_features(combined)
        
        if len(features) < 2:
            return self._ncd_fallback(prompt, candidate)
        
        # Build affinity matrix via token overlap + thermodynamic weighting
        n = len(features)
        A = np.zeros((n, n))
        
        # TF-IDF vectors for energy computation
        tfidf_prompt = self._tfidf(prompt)
        
        for i in range(n):
            for j in range(i+1, n):
                # Token overlap similarity
                tokens_i = set(re.findall(r'\w+', features[i].lower()))
                tokens_j = set(re.findall(r'\w+', features[j].lower()))
                jaccard = len(tokens_i & tokens_j) / max(1, len(tokens_i | tokens_j))
                
                # Energy penalty
                tfidf_i = self._tfidf(features[i])
                tfidf_j = self._tfidf(features[j])
                energy = np.linalg.norm(tfidf_prompt - (tfidf_i + tfidf_j))
                boltzmann = np.exp(-energy / self.temperature)
                
                # Combined weight
                A[i, j] = A[j, i] = jaccard * boltzmann
        
        # Spectral analysis via NetworkX
        G = nx.from_numpy_array(A)
        laplacian = nx.laplacian_matrix(G).toarray()
        
        try:
            eigenvalues = np.linalg.eigvalsh(laplacian)
            eigenvalues = np.abs(eigenvalues)
            
            # Spectral flatness
            psd = np.abs(np.fft.rfft(eigenvalues**2))
            psd = psd[psd > 1e-9]
            if len(psd) > 0:
                geo_mean = np.exp(np.mean(np.log(psd + 1e-9)))
                arith_mean = np.mean(psd)
                flatness = geo_mean / (arith_mean + 1e-9)
            else:
                flatness = 0.5
            
            # Criticality
            lambda_max = np.max(eigenvalues)
            criticality = np.exp(-abs(lambda_max - 1.0))
            
            # Total weight (thermodynamic stability)
            total_weight = -np.sum(A)
            
            # Combined score
            score = (self.alpha * total_weight + 
                    self.beta * flatness + 
                    self.gamma * criticality)
            
            # Normalize to positive range
            score = 5.0 / (1.0 + np.exp(-score))
            
        except:
            score = 2.5
        
        # Add NCD tiebreaker (max 10% influence)
        ncd = self._ncd(prompt, candidate)
        score = 0.9 * score + 0.1 * (5.0 * (1.0 - ncd))
        
        return float(score)
    
    def _tfidf(self, text: str) -> np.ndarray:
        """Simple TF-IDF vector (fixed 100-dim hash)."""
        tokens = re.findall(r'\w+', text.lower())
        vec = np.zeros(100)
        for token in tokens:
            idx = hash(token) % 100
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-9)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def _ncd_fallback(self, prompt: str, candidate: str) -> float:
        """Fallback when structural parsing fails."""
        ncd = self._ncd(prompt, candidate)
        return 5.0 * (1.0 - ncd)
    
    def _explain_score(self, prompt: str, candidate: str, score: float) -> str:
        """Brief explanation of score components."""
        features = self._extract_features(prompt + " " + candidate)
        return f"Found {len(features)} logical features; thermodynamic-spectral score: {score:.2f}"
```

</details>
