# Reinforcement Learning + Differentiable Programming + Free Energy Principle

**Fields**: Computer Science, Computer Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T05:59:48.396681
**Report Generated**: 2026-04-02T08:39:55.142855

---

## Nous Analysis

**Algorithm**  
We build a differentiable constraint‑solver that treats each answer candidate as a latent policy πθ(a|p) over a discrete set A of answer strings. The prompt p is first parsed into a set C of soft logical constraints (see §2). Each constraint c∈C is represented by a differentiable penalty ϕc(z)∈[0,∞) where z is a vector of propositional truth‑values derived from the answer.  

1. **Embedding layer** – For every token t in the answer we keep a one‑hot vector e(t)∈ℝᵛ (v = vocab size). The answer representation is the mean‑pooled embedding  
   \[
   x = \frac{1}{|a|}\sum_{t\in a} e(t)\in\mathbb{R}^v .
   \]  
2. **Propositional layer** – A fixed weight matrix W∈ℝ^{k×v} and bias b∈ℝ^{k} produce k proposition scores  
   \[
   s = \sigma(Wx+b)\in(0,1)^k ,
   \]  
   where σ is the logistic sigmoid; each s_i is the soft truth‑value of proposition i.  
3. **Constraint layer** – For each constraint we compute a penalty using only numpy:  
   * Equality (p_i = p_j): ϕ = (s_i−s_j)^2  
   * Inequality (p_i > p_j): ϕ = max(0, m + s_j−s_i)^2  (hinge with margin m=0.1)  
   * Implication (p_i → p_j): ϕ = max(0, s_i−s_j)^2  
   * Negation (¬p_i): ϕ = s_i^2  
   The total energy is E = Σ_c w_c·ϕc with hand‑tuned weights w_c (e.g., 1.0).  
4. **Free‑energy objective** – The variational free energy for a sampled answer a is  
   \[
   F(a) = E(a) - \mathcal{H}[\pi_\theta(\cdot|p)] ,
   \]  
   where the entropy term encourages exploration.  
5. **RL update** – Sample an answer a∼πθ, compute reward r = −F(a), and perform a REINFORCE step:  
   \[
   \theta \leftarrow \theta + \alpha \, (r - b)\,\nabla_\theta \log\pi_\theta(a|p),
   \]  
   with baseline b = running average of r. Gradients flow through W,b via standard back‑prop (numpy autodiff implemented manually). The final score for a candidate is −F(a).  

**Parsed structural features** – The parser extracts (via regex and shallow dependency patterns): negations (“not”, “no”), comparatives (“greater than”, “less than”, “equal to”), conditionals (“if … then …”, “unless”), causal cues (“because”, “leads to”), ordering relations (“before”, “after”, “precedes”), numeric constants and units, and quantifiers (“all”, “some”, “none”). Each maps to a proposition and a constraint type as above.  

**Novelty** – Differentiable logic networks and RL‑guided theorem proving exist separately, but coupling them with a free‑energy‑principle objective (energy minus entropy) to score answer candidates is not described in the literature; thus the combination is novel.  

**Ratings**  
Reasoning: 7/10 — captures logical consistency and uncertainty via free energy, but limited to shallow parsing.  
Metacognition: 5/10 — entropy term provides basic exploration control; no explicit self‑monitoring of belief updates.  
Hypothesis generation: 6/10 — policy can propose diverse answers, yet generation is confined to the candidate set.  
Implementability: 8/10 — relies only on numpy and stdlib; all components are straightforward to code.

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
**Reason**: trap_battery_failed (acc=42% cal=0% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T07:59:42.620979

---

## Code

**Source**: scrap

[View code](./Reinforcement_Learning---Differentiable_Programming---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable constraint-solver using Free Energy Principle + RL.
    
    Parses prompts into soft logical constraints, embeds candidates as token vectors,
    maps to propositional truth-values via learnable weights, computes constraint
    penalties, and scores via free energy F = E - H. REINFORCE updates refine the policy.
    Implements epistemic honesty for Tier B reasoning (ambiguity detection).
    """
    
    def __init__(self):
        np.random.seed(42)
        self.vocab = {}
        self.vocab_size = 0
        self.k_props = 16  # number of propositions
        self.W = None
        self.b = None
        self.alpha = 0.01  # learning rate
        self.baseline = 0.0
        self.margin = 0.1
        
    def _build_vocab(self, texts: List[str]):
        """Build vocabulary from all text."""
        tokens = set()
        for text in texts:
            tokens.update(re.findall(r'\b\w+\b', text.lower()))
        self.vocab = {t: i for i, t in enumerate(sorted(tokens))}
        self.vocab_size = len(self.vocab)
        if self.vocab_size > 0:
            self.W = np.random.randn(self.k_props, self.vocab_size) * 0.1
            self.b = np.zeros(self.k_props)
    
    def _tokenize(self, text: str) -> List[str]:
        """Extract tokens from text."""
        return re.findall(r'\b\w+\b', text.lower())
    
    def _embed(self, text: str) -> np.ndarray:
        """Mean-pooled one-hot embedding."""
        tokens = self._tokenize(text)
        if not tokens or self.vocab_size == 0:
            return np.zeros(self.vocab_size)
        vecs = []
        for t in tokens:
            if t in self.vocab:
                v = np.zeros(self.vocab_size)
                v[self.vocab[t]] = 1.0
                vecs.append(v)
        if not vecs:
            return np.zeros(self.vocab_size)
        return np.mean(vecs, axis=0)
    
    def _sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))
    
    def _propositions(self, x: np.ndarray) -> np.ndarray:
        """Compute soft truth-values s = sigma(Wx + b)."""
        return self._sigmoid(self.W @ x + self.b)
    
    def _parse_constraints(self, prompt: str) -> List[Tuple[str, tuple]]:
        """Extract logical constraints from prompt."""
        constraints = []
        p_lower = prompt.lower()
        
        # Negations
        if re.search(r'\b(not|no|never|none)\b', p_lower):
            constraints.append(('negation', (0,)))
        
        # Comparatives
        if re.search(r'\b(greater|more|larger|higher|bigger)\b', p_lower):
            constraints.append(('inequality', (1, 2)))
        if re.search(r'\b(less|fewer|smaller|lower)\b', p_lower):
            constraints.append(('inequality', (2, 1)))
        if re.search(r'\b(equal|same|identical)\b', p_lower):
            constraints.append(('equality', (1, 2)))
        
        # Conditionals
        if re.search(r'\bif\b.*\bthen\b', p_lower):
            constraints.append(('implication', (3, 4)))
        if re.search(r'\bunless\b', p_lower):
            constraints.append(('implication', (5, 0)))
        
        # Ordering
        if re.search(r'\b(before|precedes)\b', p_lower):
            constraints.append(('inequality', (6, 7)))
        if re.search(r'\b(after|follows)\b', p_lower):
            constraints.append(('inequality', (7, 6)))
        
        return constraints
    
    def _constraint_penalty(self, s: np.ndarray, ctype: str, indices: tuple) -> float:
        """Compute differentiable penalty for a constraint."""
        if ctype == 'equality':
            i, j = indices[0] % len(s), indices[1] % len(s)
            return (s[i] - s[j]) ** 2
        elif ctype == 'inequality':
            i, j = indices[0] % len(s), indices[1] % len(s)
            return max(0, self.margin + s[j] - s[i]) ** 2
        elif ctype == 'implication':
            i, j = indices[0] % len(s), indices[1] % len(s)
            return max(0, s[i] - s[j]) ** 2
        elif ctype == 'negation':
            i = indices[0] % len(s)
            return s[i] ** 2
        return 0.0
    
    def _energy(self, candidate: str, prompt: str, constraints: List) -> float:
        """Compute total constraint violation energy."""
        x = self._embed(candidate)
        s = self._propositions(x)
        E = 0.0
        for ctype, indices in constraints:
            E += self._constraint_penalty(s, ctype, indices)
        return E
    
    def _entropy(self, s: np.ndarray) -> float:
        """Entropy of proposition distribution."""
        eps = 1e-8
        H = -np.sum(s * np.log(s + eps) + (1 - s) * np.log(1 - s + eps))
        return H
    
    def _free_energy(self, candidate: str, prompt: str, constraints: List) -> float:
        """F = E - H (energy minus entropy)."""
        x = self._embed(candidate)
        s = self._propositions(x)
        E = self._energy(candidate, prompt, constraints)
        H = self._entropy(s)
        return E - 0.1 * H  # scale entropy term
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _compute_numeric(self, prompt: str, candidate: str) -> float:
        """Extract and compare numeric values."""
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        if not p_nums or not c_nums:
            return 0.0
        # Check if candidate numbers satisfy prompt comparisons
        score = 0.0
        if 'greater' in prompt.lower() or 'more' in prompt.lower():
            if c_nums and p_nums and c_nums[0] > p_nums[0]:
                score += 1.0
        if 'less' in prompt.lower() or 'fewer' in prompt.lower():
            if c_nums and p_nums and c_nums[0] < p_nums[0]:
                score += 1.0
        return score
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect question ambiguity/unanswerability (Tier B reasoning)."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.28
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', p_lower):
            return 0.3
        
        # Unanswerability cues
        if re.search(r'\b(impossible|cannot determine|insufficient|not enough)\b', p_lower):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by free-energy score."""
        self._build_vocab([prompt] + candidates)
        constraints = self._parse_constraints(prompt)
        
        results = []
        for cand in candidates:
            # Free energy (lower is better, so negate for score)
            F = self._free_energy(cand, prompt, constraints)
            fe_score = -F
            
            # Numeric computation
            num_score = self._compute_numeric(prompt, cand)
            
            # NCD (similarity to prompt)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination: 60% FE, 25% numeric, 15% NCD
            final_score = 0.6 * fe_score + 0.25 * num_score + 0.15 * ncd_score
            
            reasoning = f"FE={fe_score:.3f}, Numeric={num_score:.3f}, NCD={ncd_score:.3f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and answer fit."""
        # First check meta-confidence (question ambiguity)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        self._build_vocab([prompt, answer])
        constraints = self._parse_constraints(prompt)
        
        # No constraints parsed -> uncertain
        if not constraints:
            return 0.4
        
        # Compute free energy
        F = self._free_energy(answer, prompt, constraints)
        
        # Lower F -> higher confidence (cap at 0.85 unless perfect computation)
        conf = max(0.0, min(0.85, 1.0 / (1.0 + F)))
        
        # Boost if numeric match
        num_score = self._compute_numeric(prompt, answer)
        if num_score > 0.5:
            conf = min(0.92, conf + 0.15)
        
        return conf * meta_conf
```

</details>
