# Renormalization + Abductive Reasoning + Sensitivity Analysis

**Fields**: Physics, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T04:55:16.642335
**Report Generated**: 2026-04-02T08:39:55.110856

---

## Nous Analysis

**Algorithm**  
1. **Proposition extraction** – Using a handful of regex patterns we pull from each answer (and the question) atomic propositions Pᵢ = ⟨polarity, predicate, args⟩ where polarity ∈ {+,-} (negation), predicate is a verb or relation, and args are noun phrases or numeric literals. Captured structures include comparatives (“more than”, “<”), conditionals (“if … then …”, “unless”), causal cues (“because”, “leads to”), ordering (“before”, “after”), and quantifiers (“all”, “some”, “none”). Each proposition is stored as a dict and assigned a unique integer ID.  

2. **Premise graph construction** – From the question we build a weighted directed graph G₀ = (V,E,W). V = premise propositions. For every pair (u,v) we set an edge weight wᵤᵥ = exp(−d(u,v)) where d is a normalized argument‑overlap distance (Jaccard on arg sets, 0 for identical, 1 for disjoint). This weight expresses abductive plausibility: how well v explains u.  

3. **Renormalization‑group coarse‑graining** – Iteratively we merge nodes whose similarity exceeds a threshold τ (e.g., d < 0.2). When merging u and v into a new node m, we set its incoming weight as the sum of the predecessors’ weights and recompute outgoing weights to remaining nodes using the same exp(−d) rule. The process repeats until no further merges occur; the resulting graph G* is a fixed point of the RG flow, capturing hierarchical explanatory chunks.  

4. **Abductive score** – For each candidate answer we compute Sₐ = Σ_{p∈answer} w*_{q→p} where q runs over premise nodes and w* are the final edge weights in G*. This aggregates the best‑explanation weights supplied by the RG‑refined graph.  

5. **Sensitivity analysis** – We perturb premise weights by adding i.i.d. Gaussian noise 𝒩(0,σ²) (σ small, e.g., 0.05) and recompute Sₐ′ over N=20 samples. The sensitivity penalty is 𝜆·std(Sₐ′)/mean(Sₐ′) with 𝜆=0.5. Final score = Sₐ / (1 + penalty).  

All steps use only NumPy for matrix operations and Python’s re module for parsing; no external models are invoked.  

**Structural features parsed** – negations (“not”, “no”), comparatives (“more than”, “less than”, “>”, “<”), conditionals (“if … then …”, “unless”), causal cues (“because”, “leads to”, “causes”), numeric values, ordering relations (“before”, “after”, “first”, “second”), quantifiers (“all”, “some”, “none”), and conjunctive/disjunctive connectives.  

**Novelty** – While abductive scoring and sensitivity checks appear separately in QA literature, coupling them with an explicit renormalization‑group coarse‑graining loop that seeks a fixed point of explanatory weights is not present in current open‑source reasoning evaluators. The approach is therefore a novel combination, though each component has precedents.  

Reasoning: 7/10 — captures explanatory strength via weighted graph but relies on heuristic similarity.  
Metacognition: 6/10 — sensitivity penalty offers a rudimentary self‑check of robustness.  
Hypothesis generation: 8/10 — abductive weighting directly ranks candidate explanations.  
Implementability: 9/10 — uses only regex, NumPy, and basic loops; easy to code and test.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=39% cal=8% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:31:40.697472

---

## Code

**Source**: scrap

[View code](./Renormalization---Abductive_Reasoning---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib

class ReasoningTool:
    """
    Renormalization x Abductive Reasoning x Sensitivity Analysis
    
    Extracts propositions from text, builds weighted graphs of explanatory
    relationships, applies RG coarse-graining to find hierarchical structure,
    scores candidates by abductive strength, and penalizes sensitivity.
    Implements epistemic honesty via meta-confidence checks.
    """
    
    def __init__(self):
        self.prop_id = 0
        np.random.seed(42)
    
    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with polarity, predicate, args."""
        props = []
        text_lower = text.lower()
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(more|less|greater|smaller)\s+than\s+(\w+)', text_lower):
            props.append({'id': self.prop_id, 'polarity': '+', 'pred': m.group(2), 'args': {m.group(1), m.group(3)}})
            self.prop_id += 1
        for m in re.finditer(r'(\d+\.?\d*)\s*([<>]=?)\s*(\d+\.?\d*)', text):
            props.append({'id': self.prop_id, 'polarity': '+', 'pred': m.group(2), 'args': {m.group(1), m.group(3)}})
            self.prop_id += 1
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:[.,;]|$)', text_lower):
            props.append({'id': self.prop_id, 'polarity': '+', 'pred': 'implies', 'args': {m.group(1).strip(), m.group(2).strip()}})
            self.prop_id += 1
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(because|causes?|leads?\s+to)\s+(\w+)', text_lower):
            props.append({'id': self.prop_id, 'polarity': '+', 'pred': m.group(2), 'args': {m.group(1), m.group(3)}})
            self.prop_id += 1
        
        # Negations
        for m in re.finditer(r'(not|no|never)\s+(\w+)', text_lower):
            props.append({'id': self.prop_id, 'polarity': '-', 'pred': 'negate', 'args': {m.group(2)}})
            self.prop_id += 1
        
        # Extract key noun phrases as props
        words = re.findall(r'\b\w+\b', text_lower)
        for i, w in enumerate(words):
            if len(w) > 3 and w not in {'that', 'this', 'with', 'from', 'have', 'been'}:
                props.append({'id': self.prop_id, 'polarity': '+', 'pred': 'contains', 'args': {w}})
                self.prop_id += 1
        
        return props if props else [{'id': self.prop_id, 'polarity': '+', 'pred': 'text', 'args': set(words[:5])}]
    
    def _jaccard(self, s1: set, s2: set) -> float:
        """Jaccard distance between two sets."""
        if not s1 and not s2:
            return 0.0
        union = s1 | s2
        if not union:
            return 1.0
        return 1.0 - len(s1 & s2) / len(union)
    
    def _build_graph(self, props: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """Build weighted graph with exp(-distance) weights."""
        n = len(props)
        W = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = self._jaccard(props[i]['args'], props[j]['args'])
                    W[i, j] = np.exp(-d)
        return W, props
    
    def _renormalize(self, W: np.ndarray, props: List[Dict], tau: float = 0.2) -> Tuple[np.ndarray, List[Dict]]:
        """RG coarse-graining: merge similar nodes until fixed point."""
        max_iter = 5
        for _ in range(max_iter):
            n = len(props)
            merged = False
            for i in range(n):
                for j in range(i+1, n):
                    d = self._jaccard(props[i]['args'], props[j]['args'])
                    if d < tau:
                        # Merge j into i
                        props[i]['args'] = props[i]['args'] | props[j]['args']
                        W[i, :] += W[j, :]
                        W[:, i] += W[:, j]
                        W[i, i] = 0
                        # Remove j
                        props = [p for k, p in enumerate(props) if k != j]
                        W = np.delete(W, j, axis=0)
                        W = np.delete(W, j, axis=1)
                        merged = True
                        break
                if merged:
                    break
            if not merged:
                break
        return W, props
    
    def _abductive_score(self, W_premise: np.ndarray, props_premise: List[Dict], props_answer: List[Dict]) -> float:
        """Sum of explanation weights from premise to answer propositions."""
        score = 0.0
        for p_ans in props_answer:
            for i, p_prem in enumerate(props_premise):
                d = self._jaccard(p_prem['args'], p_ans['args'])
                weight = np.exp(-d)
                score += weight * W_premise[i, :].sum() / (len(props_premise) + 1e-6)
        return score / (len(props_answer) + 1e-6)
    
    def _sensitivity_penalty(self, W: np.ndarray, props_premise: List[Dict], props_answer: List[Dict], sigma: float = 0.05, N: int = 20) -> float:
        """Perturb weights and measure score variance."""
        scores = []
        for _ in range(N):
            W_pert = W + np.random.normal(0, sigma, W.shape)
            W_pert = np.maximum(W_pert, 0)
            s = self._abductive_score(W_pert, props_premise, props_answer)
            scores.append(s)
        mean_s = np.mean(scores)
        std_s = np.std(scores)
        return 0.5 * std_s / (mean_s + 1e-6)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerable questions."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.+\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she)\b', p_lower) and '?' in prompt:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.+\bor\b', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and 'most' not in p_lower:
            return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(cannot be determined|insufficient|ambiguous|unclear)\b', p_lower):
            return 0.2
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by RG-abductive score with sensitivity penalty."""
        self.prop_id = 0
        props_prompt = self._extract_propositions(prompt)
        W_prompt, props_prompt = self._build_graph(props_prompt)
        W_rg, props_rg = self._renormalize(W_prompt, props_prompt)
        
        results = []
        for cand in candidates:
            props_cand = self._extract_propositions(cand)
            abd_score = self._abductive_score(W_rg, props_rg, props_cand)
            sens_pen = self._sensitivity_penalty(W_rg, props_rg, props_cand)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            final_score = 0.6 * abd_score / (1 + sens_pen) + 0.1 * ncd_score
            
            reasoning = f"Abductive={abd_score:.3f}, Sensitivity={sens_pen:.3f}, NCD={ncd_score:.3f}"
            results.append({'candidate': cand, 'score': final_score, 'reasoning': reasoning})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        
        self.prop_id = 0
        props_prompt = self._extract_propositions(prompt)
        props_answer = self._extract_propositions(answer)
        
        W_prompt, props_prompt = self._build_graph(props_prompt)
        W_rg, props_rg = self._renormalize(W_prompt, props_prompt)
        
        abd_score = self._abductive_score(W_rg, props_rg, props_answer)
        sens_pen = self._sensitivity_penalty(W_rg, props_rg, props_answer)
        
        raw_conf = abd_score / (1 + sens_pen)
        raw_conf = min(raw_conf, 0.85)  # Never exceed 0.85 without computation
        
        return min(raw_conf, meta_conf)
```

</details>
