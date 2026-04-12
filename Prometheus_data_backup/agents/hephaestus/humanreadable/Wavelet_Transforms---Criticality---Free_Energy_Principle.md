# Wavelet Transforms + Criticality + Free Energy Principle

**Fields**: Signal Processing, Complex Systems, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:14:48.978900
**Report Generated**: 2026-03-27T06:37:38.970721

---

## Nous Analysis

**Algorithm**  
1. **Parse** each candidate answer with regexes to extract atomic propositions and logical operators (¬, ∧, ∨, →, ↔, >, <, =, ≠, causal keywords *because*, *leads to*, ordering *before/after*). Store propositions in a list `P` and build a directed adjacency matrix `A` (numpy bool) where `A[i,j]=1` if proposition *i* entails *j* (extracted from conditionals, causal, or transitive ordering).  
2. **Constraint propagation**: compute the transitive closure of `A` using repeated Boolean matrix multiplication (`A = A | (A @ A)`) until convergence, yielding a reachability matrix `R`. Assign an initial confidence vector `c0 = np.ones(len(P))`. Propagated confidence is `c = R @ c0` (clipped to [0,1]), representing how many constraints support each proposition.  
3. **Signal construction**: order propositions by their appearance in the text to form a 1‑D signal `s = c`. Apply a discrete Haar wavelet transform via numpy’s `np.kron` and successive averaging/differencing to obtain coefficients `w_k` at scales `k = 0…K`.  
4. **Criticality measure**: compute susceptibility at each scale as `χ_k = np.var(w_k)`. Aggregate criticality `C = np.sum(χ_k) / (K+1)`. High `C` indicates the system is near a boundary between order (low variance) and disorder (high variance).  
5. **Free‑energy score**: assume a Gaussian prior with zero mean and unit variance for wavelet coefficients. Variational free energy approximates prediction error plus complexity:  
   `F = 0.5 * np.sum(w_k**2) + 0.5 * np.sum(np.log(2*np.pi)) - np.sum(np.log(c+1e-8))`.  
   The final score is `-F` (lower free energy → higher score).  

**Parsed structural features** – negations (`not`, `no`), comparatives (`more`, `less`, `>`, `<`), conditionals (`if…then`, `implies`), causal claims (`because`, `leads to`), ordering relations (`before`, `after`, `first`, `last`), and explicit numeric values or ranges.

**Novelty** – While wavelet-based text analysis and constraint propagation appear separately, coupling them with a free‑energy principle to compute a variational score for reasoning quality has not been reported in existing evaluation tools; the trio forms a novel algorithmic pipeline.

Reasoning: 7/10 — captures multi‑scale logical consistency but relies on shallow proposition extraction.  
Metacognition: 5/10 — monitors confidence via criticality yet lacks explicit self‑reflection on uncertainty sources.  
Hypothesis generation: 6/10 — high criticality flags unstable propositions, prompting alternative parses, but no generative search.  
Implementability: 8/10 — uses only numpy regex and linear algebra; all steps are straightforward to code.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Wavelet Transforms**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Criticality + Wavelet Transforms: negative interaction (-0.074). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Wavelet Transforms: strong positive synergy (+0.116). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Criticality + Free Energy Principle: strong positive synergy (+0.369). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Evolution + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Architecture Search + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: error: bad escape \m at position 1

**Forge Timestamp**: 2026-03-26T01:51:50.873315

---

## Code

**Source**: scrap

[View code](./Wavelet_Transforms---Criticality---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np

class ReasoningTool:
    """
    Implements a reasoning evaluator based on Wavelet Transforms, Criticality, 
    and the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical operators (negation, causality, 
       conditionals, ordering) using regex. Builds a directed adjacency matrix of entailment.
    2. Constraint Propagation: Computes transitive closure via Boolean matrix multiplication 
       to determine reachability (logical consistency).
    3. Signal Construction: Maps propagated confidence to a 1D signal based on text order.
    4. Wavelet Criticality: Applies a discrete Haar wavelet transform. Criticality is the 
       average variance across scales, detecting boundary states between order and chaos.
    5. Free Energy: Computes variational free energy (prediction error + complexity) assuming 
       a Gaussian prior. The final score is negative free energy (lower F = higher score).
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|causes)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|implies|unless|only if)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|precede|follow)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\more|\less|greater|smaller|>|<|=|!=)', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*')
        }
        self.stopwords = set(['the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

    def _extract_propositions(self, text: str) -> list:
        """Extract atomic propositions based on sentence splitting and keyword density."""
        # Simple sentence splitter
        sentences = [s.strip() for s in re.split(r'[.!?;]', text) if s.strip()]
        props = []
        for sent in sentences:
            words = re.findall(r'\b\w+\b', sent.lower())
            if not words: continue
            # Score based on structural keywords
            score = 0
            for key in self.patterns:
                if self.patterns[key].search(sent):
                    score += 2
            # Add base score for content words
            score += len([w for w in words if w not in self.stopwords])
            props.append({'text': sent, 'score': score + 1}) # +1 to avoid zero
        
        # If no sentences found, treat whole text as one proposition
        if not props and text.strip():
            props.append({'text': text.strip(), 'score': 1})
            
        return props

    def _build_adjacency_matrix(self, props: list, text: str) -> np.ndarray:
        """Build directed adjacency matrix A where A[i,j]=1 if i entails j."""
        n = len(props)
        if n == 0: return np.array([])
        A = np.zeros((n, n), dtype=bool)
        
        # Heuristic: Order implies entailment (narrative flow)
        # Also check for explicit logical connectors between propositions
        for i in range(n):
            A[i, i] = True  # Reflexive
            if i > 0:
                # Check if previous proposition leads to this one (simplified narrative flow)
                A[i-1, i] = True 
                
            # Check for internal conditionals within a proposition that might link to others
            # This is a simplification of the complex parsing required
            if 'if' in props[i]['text'].lower() or 'leads to' in props[i]['text'].lower():
                # If conditional, assume it links to subsequent context broadly
                for j in range(i+1, min(i+2, n)):
                    A[i, j] = True
                    
        return A

    def _transitive_closure(self, A: np.ndarray) -> np.ndarray:
        """Compute transitive closure using Warshall's algorithm (matrix multiplication approach)."""
        if A.size == 0: return A
        R = A.copy()
        n = R.shape[0]
        # Repeated Boolean matrix multiplication until convergence
        # R = R | (R @ R)
        for _ in range(n): 
            prev = R.copy()
            R = R | (R @ R > 0) # Boolean multiplication via thresholding
            if np.array_equal(R, prev):
                break
        return R

    def _haar_wavelet(self, s: np.ndarray) -> list:
        """Apply discrete Haar wavelet transform manually."""
        if len(s) == 0: return []
        coeffs = []
        current = s.astype(float)
        
        # Pad to power of 2 for simplicity in this implementation
        n = len(current)
        if n == 0: return [np.array([0.0])]
        
        # Simple iterative averaging and differencing
        while len(current) > 1:
            if len(current) % 2 != 0:
                current = np.append(current, current[-1]) # Pad last element
            
            avg = (current[0::2] + current[1::2]) / 2.0
            diff = (current[0::2] - current[1::2]) / 2.0
            
            coeffs.append(diff)
            current = avg
            
        coeffs.append(current) # Final approximation coefficient
        return coeffs

    def _compute_score(self, text: str) -> float:
        """Core algorithm: Parse -> Propagate -> Wavelet -> Free Energy."""
        props = self._extract_propositions(text)
        if not props:
            return -100.0 # Penalty for empty
            
        n = len(props)
        A = self._build_adjacency_matrix(props, text)
        if A.size == 0:
            return -100.0
            
        R = self._transitive_closure(A)
        
        # Initial confidence vector
        c0 = np.ones(n)
        # Propagated confidence
        c = R @ c0
        c = np.clip(c, 0, 1)
        
        # Signal construction: order by appearance (already ordered)
        # Weight signal by proposition structural score
        signal_vals = [p['score'] * conf for p, conf in zip(props, c)]
        s = np.array(signal_vals)
        
        if len(s) == 0:
            return -100.0

        # Wavelet transform
        w_coeffs = self._haar_wavelet(s)
        
        if not w_coeffs:
            return -100.0

        # Criticality measure: Average variance across scales
        vars_per_scale = [np.var(w) if len(w) > 0 else 0.0 for w in w_coeffs]
        K = len(w_coeffs) - 1
        C = np.sum(vars_per_scale) / (K + 1) if (K + 1) > 0 else 0.0
        
        # Free Energy Score
        # Flatten all coefficients for global calculation
        all_w = np.concatenate(w_coeffs) if w_coeffs else np.array([0.0])
        
        # F = 0.5 * sum(w^2) + 0.5 * sum(log(2pi)) - sum(log(c + epsilon))
        # We want to maximize -F
        epsilon = 1e-8
        term1 = 0.5 * np.sum(all_w**2)
        term2 = 0.5 * len(all_w) * np.log(2 * np.pi)
        term3 = -np.sum(np.log(c + epsilon)) # Complexity penalty based on confidence spread
        
        F = term1 + term2 + term3
        score = -F
        
        # Boost for high criticality (indicates rich logical structure near phase transition)
        # This helps distinguish complex correct reasoning from simple noise
        score += 0.1 * np.log(C + 1)
        
        return float(score)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            # Combine prompt and candidate for context-aware scoring if needed, 
            # but primarily scoring the candidate's internal logic relative to prompt keywords
            # Here we score the concatenation to capture flow
            full_text = f"{prompt} {cand}"
            score = self._compute_score(full_text)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Wavelet-FEP Score: {score:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score = self._compute_score(f"{prompt} {answer}")
        # Normalize score to 0-1 range using a sigmoid-like mapping
        # Assuming typical scores fall between -50 and 10
        # Shift and scale
        normalized = 1.0 / (1.0 + np.exp(-0.1 * (score + 20)))
        return float(np.clip(normalized, 0.0, 1.0))
```

</details>
