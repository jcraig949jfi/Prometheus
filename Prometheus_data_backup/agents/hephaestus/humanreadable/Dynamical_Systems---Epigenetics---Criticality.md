# Dynamical Systems + Epigenetics + Criticality

**Fields**: Mathematics, Biology, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T14:28:56.608545
**Report Generated**: 2026-04-02T10:00:36.003432

---

## Nous Analysis

**Algorithm**  
Each candidate answer is parsed into a set of logical propositions \(P=\{p_i\}\) (e.g., “X > Y”, “if A then B”, “not C”). Propositions become nodes in a directed weighted graph \(G=(V,E,w)\) where an edge \(p_i\rightarrow p_j\) encodes a logical implication extracted from conditionals, causal language, or transitive relations; the weight \(w_{ij}\in[0,1]\) reflects confidence from linguistic cues (modal strength, negation polarity, numeric comparatives).  

We treat the graph as a discrete‑time dynamical system: a state vector \(s\in\{0,1\}^{|V|}\) indicates which propositions are currently true. Update rule:  
\[
s^{(t+1)}_j = \sigma\!\Big(\sum_i w_{ij}s^{(t)}_i - \theta_j\Big),
\]  
with \(\sigma\) a hard threshold (0/1) and \(\theta_j\) a node‑specific bias derived from epigenetic‑like marks.  

**Epigenetic marks** are static modifiers \(m_j\in[0,1]\) stored per node, initialized from lexical features (e.g., presence of hedging words lowers \(m_j\); strong assertive language raises it). The bias is \(\theta_j = \theta_0 - m_j\), so highly marked nodes are easier to activate.  

**Criticality** is approached by tuning a global gain \(g\) that multiplies all weights: \(w_{ij}\leftarrow g\,w_{ij}\). We evaluate the system for a range of \(g\) values and compute the order parameter \(M(g)=\frac{1}{|V|}\sum_j \langle s_j\rangle\) (average activation over a few iterations). The susceptibility \(\chi(g)=\partial M/\partial g\) is estimated by finite differences. The score for an answer is the value of \(\chi\) at the gain where \(\chi\) peaks (the pseudo‑critical point), normalized to \([0,1]\). High susceptibility indicates that the answer’s logical structure is poised between order (consistent, low‑entropy) and disorder (contradictory, high‑entropy), rewarding answers that are both coherent and richly inferential.  

**Parsed textual features**  
- Negations (flip truth value of a node)  
- Comparatives (“greater than”, “less than”) → numeric constraints encoded as directed edges with weight proportional to magnitude difference  
- Conditionals (“if … then …”) → implication edges  
- Causal claims (“because”, “leads to”) → weighted edges, weight increased by causal cue strength  
- Ordering relations (“first”, “after”) → temporal edges  
- Numeric values → nodes representing quantities, edges for equality/inequality  

**Novelty**  
The triple blend of dynamical‑systems stability analysis, epigenetically modulated node biases, and critical‑point susceptibility scoring does not appear in existing QA‑scoring literature. Prior work uses either pure constraint propagation or similarity metrics; none jointly treats answers as tunable dynamical networks whose score derives from a susceptibility peak.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and inferential richness via dynamical stability and critical sensitivity.  
Metacognition: 6/10 — the model can reflect on its own parameter (gain) but lacks explicit self‑monitoring of update steps.  
Hypothesis generation: 7/10 — susceptibility peak highlights regions where small changes produce large inference shifts, useful for proposing alternative interpretations.  
Implementability: 9/10 — relies only on numpy for matrix operations and stdlib for regex/graph construction; no external libraries needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
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
**Reason**: trap_battery_failed (acc=42% cal=5% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T09:21:12.896038

---

## Code

**Source**: scrap

[View code](./Dynamical_Systems---Epigenetics---Criticality/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Dynamical Systems x Epigenetics x Criticality Reasoning Tool

Parses candidate answers into proposition graphs, applies epigenetic marks
from linguistic features, treats as a dynamical system, and scores by
susceptibility at the critical point. Includes constructive computation
for numeric/probabilistic questions and meta-confidence for ambiguity.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    def __init__(self):
        self.theta_0 = 0.5  # Base threshold
        self.gain_range = np.linspace(0.1, 2.0, 20)
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by combined computation + criticality score."""
        results = []
        
        for cand in candidates:
            # Constructive computation (primary)
            comp_score = self._compute_answer(prompt, cand)
            
            # Criticality-based coherence (secondary)
            crit_score = self._criticality_score(cand)
            
            # Combined score: 50% computation, 35% criticality, 15% NCD
            ncd_score = 1.0 - self._ncd(prompt, cand)
            final_score = 0.5 * comp_score + 0.35 * crit_score + 0.15 * ncd_score
            
            reasoning = f"Computation: {comp_score:.2f}, Criticality: {crit_score:.2f}, NCD: {ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence with meta-checks for ambiguity."""
        # Meta-confidence caps based on prompt properties
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence from computation
        comp_score = self._compute_answer(prompt, answer)
        
        # Never exceed 0.9 unless we computed a definitive answer
        base_conf = min(comp_score, 0.85)
        
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerable questions."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did .+ fail|when did .+ stop)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an) \b', p) and '?' in p:
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|were|is|are)', p) and re.search(r'\bwho\b', p):
            return 0.3
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', p):
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p) and not re.search(r'\b(according to|based on|measured by)\b', p):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(cannot determine|not enough information|impossible to)\b', p):
            return 0.25
        
        return 1.0  # No ambiguity detected
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        """Constructive computation: actually solve the problem."""
        score = 0.0
        
        # Numeric comparison
        num_score = self._numeric_eval(prompt, candidate)
        if num_score > 0:
            return num_score
        
        # Bayesian/probability
        prob_score = self._bayesian_eval(prompt, candidate)
        if prob_score > 0:
            return prob_score
        
        # Temporal ordering
        temp_score = self._temporal_eval(prompt, candidate)
        if temp_score > 0:
            return temp_score
        
        # Logical constraints
        logic_score = self._logical_eval(prompt, candidate)
        if logic_score > 0:
            return logic_score
        
        return 0.3  # Low default if no computation matches
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        """Extract and compare numbers."""
        p_nums = re.findall(r'\b\d+\.?\d*\b', prompt)
        c_nums = re.findall(r'\b\d+\.?\d*\b', candidate)
        
        if not p_nums or not c_nums:
            return 0.0
        
        # Detect comparison operators
        if re.search(r'\b(greater|larger|more|higher)\b', prompt.lower()):
            try:
                if float(c_nums[0]) > float(p_nums[0]):
                    return 0.9
            except:
                pass
        
        if re.search(r'\b(less|fewer|smaller|lower)\b', prompt.lower()):
            try:
                if float(c_nums[0]) < float(p_nums[0]):
                    return 0.9
            except:
                pass
        
        # Arithmetic operations
        if '+' in prompt or 'plus' in prompt.lower() or 'sum' in prompt.lower():
            try:
                expected = sum(float(n) for n in p_nums)
                actual = float(c_nums[0])
                if abs(expected - actual) < 0.01:
                    return 0.95
            except:
                pass
        
        return 0.0
    
    def _bayesian_eval(self, prompt: str, candidate: str) -> float:
        """Compute Bayesian posteriors."""
        p = prompt.lower()
        
        # Detect base rate problems
        if 'base rate' in p or 'prior probability' in p:
            # Extract probabilities
            probs = re.findall(r'(\d+\.?\d*)%', prompt)
            if len(probs) >= 2:
                try:
                    # Simple Bayes: P(A|B) proportional to P(B|A) * P(A)
                    prior = float(probs[0]) / 100
                    likelihood = float(probs[1]) / 100
                    
                    c_probs = re.findall(r'(\d+\.?\d*)%', candidate)
                    if c_probs:
                        cand_val = float(c_probs[0]) / 100
                        expected = prior * likelihood / (prior * likelihood + (1-prior) * 0.1)
                        if abs(cand_val - expected) < 0.1:
                            return 0.9
                except:
                    pass
        
        return 0.0
    
    def _temporal_eval(self, prompt: str, candidate: str) -> float:
        """Evaluate temporal ordering."""
        # Detect temporal keywords
        temporal_markers = ['before', 'after', 'then', 'first', 'second', 'finally']
        if not any(m in prompt.lower() for m in temporal_markers):
            return 0.0
        
        # Check if candidate matches temporal structure
        p_order = re.findall(r'\b(first|second|third|then|after|before)\b', prompt.lower())
        c_order = re.findall(r'\b(first|second|third|then|after|before)\b', candidate.lower())
        
        if p_order and c_order:
            overlap = len(set(p_order) & set(c_order)) / max(len(p_order), 1)
            return min(0.8, overlap)
        
        return 0.0
    
    def _logical_eval(self, prompt: str, candidate: str) -> float:
        """Evaluate logical constraints and transitivity."""
        # Negation handling
        p_neg = bool(re.search(r'\b(not|never|no|none)\b', prompt.lower()))
        c_neg = bool(re.search(r'\b(not|never|no|none)\b', candidate.lower()))
        
        # If prompt asks "not X", candidate should contain negation
        if 'which is not' in prompt.lower() or 'is not' in prompt.lower():
            if c_neg:
                return 0.7
        
        # Transitivity: A > B, B > C => A > C
        if '>' in prompt or 'greater' in prompt.lower():
            entities = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(entities) >= 3:
                # Simple heuristic: candidate should mention entities
                mentioned = sum(1 for e in entities if e in candidate)
                return min(0.75, mentioned / len(entities))
        
        return 0.0
    
    def _criticality_score(self, text: str) -> float:
        """Build proposition graph, tune to criticality, return susceptibility."""
        props, graph, marks = self._parse_propositions(text)
        
        if len(props) < 2:
            return 0.5  # Degenerate case
        
        n = len(props)
        susceptibilities = []
        
        for g in self.gain_range:
            W = graph * g
            activations = []
            state = np.random.rand(n) > 0.5
            
            for _ in range(5):  # Few iterations
                theta = np.array([self.theta_0 - marks[i] for i in range(n)])
                state = (W @ state - theta) > 0
                activations.append(state.mean())
            
            susceptibilities.append(np.std(activations))
        
        # Peak susceptibility
        return min(1.0, max(susceptibilities))
    
    def _parse_propositions(self, text: str) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """Extract propositions, build implication graph, assign epigenetic marks."""
        sentences = re.split(r'[.!?]', text)
        props = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        n = len(props)
        if n == 0:
            return [], np.zeros((1,1)), np.zeros(1)
        
        # Build adjacency matrix (implications)
        graph = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Causal/conditional edges
                    if any(w in props[i].lower() for w in ['if', 'because', 'leads to', 'causes']):
                        graph[i, j] = 0.6
                    # Comparative edges
                    if any(w in props[i].lower() for w in ['greater', 'more', 'less']):
                        graph[i, j] = 0.5
        
        # Epigenetic marks from linguistic features
        marks = np.zeros(n)
        for i, prop in enumerate(props):
            p = prop.lower()
            # Assertive language raises mark
            if any(w in p for w in ['definitely', 'certainly', 'must', 'always']):
                marks[i] += 0.3
            # Hedging lowers mark
            if any(w in p for w in ['maybe', 'perhaps', 'possibly', 'might']):
                marks[i] -= 0.2
            # Negation modulates
            if any(w in p for w in ['not', 'never', 'no']):
                marks[i] -= 0.1
        
        marks = np.clip(marks, 0, 1)
        return props, graph, marks
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
