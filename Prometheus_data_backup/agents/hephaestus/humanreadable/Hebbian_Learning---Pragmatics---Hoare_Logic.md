# Hebbian Learning + Pragmatics + Hoare Logic

**Fields**: Neuroscience, Linguistics, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:44:03.040925
**Report Generated**: 2026-04-02T10:00:36.408427

---

## Nous Analysis

**Algorithm**  
We build a weighted implication graph \(G=(V,E,w)\) where each node \(v_i\) encodes a proposition extracted from the prompt (e.g., “X > Y”, “¬A”, “if P then Q”). Propositions are obtained via regex patterns that capture conditionals, negations, comparatives, causal connectives, and numeric constraints. Each directed edge \(e_{i\to j}\) represents a Hoare‑style triple \(\{P_i\}\,C\,\{Q_j\}\) meaning “if \(P_i\) holds before step \(C\), then \(Q_j\) holds after”. The edge weight \(w_{ij}\in[0,1]\) reflects the strength of the conditional belief.

1. **Initialization** – All edges start with a baseline weight \(w_0=0.1\).  
2. **Hebbian update** – Whenever two propositions \(p_i\) and \(p_j\) appear in the same sentence or within a sliding window of k tokens, we increase the weight of the edge that links them (if it exists) by \(\Delta w = \eta \cdot (act_i \cdot act_j)\), where \(act_i,act_j\in\{0,1\}\) indicate presence and \(\eta=0.05\) is a learning rate. This implements “neurons that fire together wire together”.  
3. **Constraint propagation** – Using the updated weights, we compute the transitive closure of implications with a max‑product variant of Floyd‑Warshall: for each \(i,j,k\), set \(w_{ij}\gets\max(w_{ij}, w_{ik}\cdot w_{kj})\). This yields the strongest inferred conditional belief between any two propositions, respecting modus ponens and transitivity.  
4. **Scoring a candidate answer** – The answer is parsed into a set of propositions \(A\). For each \(a\in A\) we check whether there exists a precondition \(p\) in the prompt such that a path \(p\leadsto a\) exists in \(G\). The contribution of \(a\) is the maximum path weight \(w_{p\to a}\). The final score is the normalized sum:  
\[
\text{score}(answer)=\frac{\sum_{a\in A}\max_{p\in P} w_{p\to a}}{|A|}
\]  
If a proposition contradicts an existing edge (e.g., \(a\) asserts ¬\(q\) while a high‑weight path derives \(q\)), its contribution is subtracted.

**Parsed structural features** – conditionals (if‑then), biconditionals, negations, comparatives (>,<,≥,≤), equality, causal verbs (“because”, “leads to”), temporal ordering (“before”, “after”), numeric thresholds, and quantifiers (“all”, “some”).

**Novelty** – Pure Hebbian weight learning over logical graphs is not common in existing NLP reasoning tools; related work uses static weighted logics (Markov Logic Networks, Probabilistic Soft Logic) or fixed rule weights, but the activity‑dependent update driven by co‑occurrence in the prompt is novel.

**Ratings**  
Reasoning: 7/10 — captures logical implication and uncertainty via learned weights, though deeper reasoning (e.g., nested quantifiers) needs extensions.  
Metacognition: 5/10 — the model can reflect on weight changes but lacks explicit self‑monitoring of its own inference process.  
Hypothesis generation: 6/10 — edge weights suggest plausible implicatures, enabling weak hypothesis ranking, but generation is limited to existing propositions.  
Implementability: 8/10 — relies only on regex, numpy matrix operations, and basic graph algorithms; no external libraries or APIs required.

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
**Reason**: validation:runtime_error: SyntaxError: (unicode error) 'utf-8' codec can't decode byte 0xac in position 28: invalid start byte (tmpccj0ixa3.py, line 33)

**Forge Timestamp**: 2026-04-02T09:53:07.891047

---

## Code

**Source**: scrap

[View code](./Hebbian_Learning---Pragmatics---Hoare_Logic/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Set, Tuple

"""
Hebbian-Hoare Reasoning Tool with Dynamics Tracking

Builds a weighted implication graph where propositions are nodes and edges
represent Hoare-style conditionals {P}C{Q}. Edge weights are learned via
Hebbian co-occurrence updates. Tracks state evolution as a dynamical system
to measure trajectory stability and convergence for confidence scoring.
"""

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    def __init__(self):
        self.eta = 0.05  # Hebbian learning rate
        self.w0 = 0.1    # Baseline edge weight
        
    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions from text using structural patterns."""
        text = text.lower()
        props = []
        
        # Conditionals: if X then Y
        for m in re.finditer(r'if\s+([^,\.]+?)\s+then\s+([^,\.]+)', text):
            props.append(f"if_{m.group(1).strip()}")
            props.append(f"then_{m.group(2).strip()}")
        
        # Negations
        for m in re.finditer(r'not\s+(\w+)|n[o\']t\s+(\w+)|¬(\w+)', text):
            word = m.group(1) or m.group(2) or m.group(3)
            props.append(f"not_{word}")
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|=|equals?)\s*(\w+)', text):
            props.append(f"{m.group(1)}_{m.group(2)}_{m.group(3)}")
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(because|leads to|causes)\s+(\w+)', text):
            props.append(f"{m.group(1)}_causes_{m.group(3)}")
        
        # Temporal
        for m in re.finditer(r'(\w+)\s+(before|after)\s+(\w+)', text):
            props.append(f"{m.group(1)}_{m.group(2)}_{m.group(3)}")
        
        # Simple assertions (words)
        words = re.findall(r'\b[a-z]{3,}\b', text)
        props.extend(words[:20])  # Limit to avoid explosion
        
        return list(set(props))
    
    def _build_graph(self, props: List[str], text: str) -> np.ndarray:
        """Build weighted adjacency matrix with Hebbian learning."""
        n = len(props)
        if n == 0:
            return np.zeros((1, 1))
        
        W = np.full((n, n), self.w0)
        
        # Tokenize for co-occurrence window
        tokens = text.lower().split()
        window = 5
        
        # Hebbian update: co-occurrence in sliding window
        for i, pi in enumerate(props):
            for j, pj in enumerate(props):
                if i == j:
                    continue
                # Check if both appear in same window
                act_i = act_j = 0
                for k in range(len(tokens) - window):
                    window_text = ' '.join(tokens[k:k+window])
                    if any(word in window_text for word in pi.split('_')):
                        act_i = 1
                    if any(word in window_text for word in pj.split('_')):
                        act_j = 1
                    if act_i and act_j:
                        W[i, j] += self.eta
                        break
        
        return np.clip(W, 0, 1)
    
    def _transitive_closure(self, W: np.ndarray) -> np.ndarray:
        """Compute max-product transitive closure (Floyd-Warshall variant)."""
        n = W.shape[0]
        W_close = W.copy()
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    W_close[i, j] = max(W_close[i, j], W_close[i, k] * W_close[k, j])
        return W_close
    
    def _track_dynamics(self, props_prompt: List[str], props_answer: List[str], 
                        W: np.ndarray) -> Tuple[float, float]:
        """Track state evolution as dynamical system, return convergence & stability."""
        n = len(props_prompt)
        if n == 0:
            return 0.0, 0.0
        
        # Initialize belief state vector
        state = np.ones(n) * 0.5
        
        # Simulate state updates: each proposition activates its node
        trajectory = [state.copy()]
        for _ in range(5):  # 5 iterations
            # Update: state[j] += sum_i W[i,j] * state[i]
            new_state = state + 0.1 * (W.T @ state)
            new_state = np.clip(new_state, 0, 1)
            trajectory.append(new_state.copy())
            state = new_state
        
        # Convergence: measure state change in final steps
        conv = 1.0 - np.linalg.norm(trajectory[-1] - trajectory[-2])
        
        # Stability: variance of trajectory
        traj_matrix = np.array(trajectory)
        stability = 1.0 - np.mean(np.std(traj_matrix, axis=0))
        
        return max(0, conv), max(0, stability)
    
    def _score_answer(self, props_prompt: List[str], props_answer: List[str], 
                      W_close: np.ndarray) -> float:
        """Score answer based on path weights from prompt to answer propositions."""
        if len(props_prompt) == 0 or len(props_answer) == 0:
            return 0.0
        
        scores = []
        for pa in props_answer:
            max_weight = 0.0
            for i, pp in enumerate(props_prompt):
                # Check if answer prop matches any prompt prop
                for j, pq in enumerate(props_prompt):
                    if any(word in pa for word in pq.split('_')):
                        max_weight = max(max_weight, W_close[i, j] if i < W_close.shape[0] and j < W_close.shape[1] else 0)
            scores.append(max_weight)
        
        return np.mean(scores) if scores else 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerability."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ a \b', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+(who|which)', p) or re.search(r'(who|which).+(he|she|it)', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.3
        
        # Question without info
        if '?' in p and len(p.split()) < 8:
            return 0.4
        
        return 1.0  # No red flags
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by Hebbian-Hoare logic and dynamics."""
        props_prompt = self._extract_propositions(prompt)
        W = self._build_graph(props_prompt, prompt)
        W_close = self._transitive_closure(W)
        
        results = []
        for cand in candidates:
            props_cand = self._extract_propositions(cand)
            
            # Structural score from graph
            struct_score = self._score_answer(props_prompt, props_cand, W_close)
            
            # Dynamics: convergence and stability
            conv, stab = self._track_dynamics(props_prompt, props_cand, W)
            dyn_score = 0.5 * conv + 0.5 * stab
            
            # NCD (tiebreaker only)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination: dynamics 40%, structural 45%, NCD 15%
            final_score = 0.45 * struct_score + 0.40 * dyn_score + 0.15 * ncd_score
            
            reasoning = f"Struct={struct_score:.2f}, Dyn(conv={conv:.2f},stab={stab:.2f})={dyn_score:.2f}, NCD={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence in answer, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        props_prompt = self._extract_propositions(prompt)
        props_answer = self._extract_propositions(answer)
        
        if len(props_prompt) == 0:
            return 0.3
        
        W = self._build_graph(props_prompt, prompt)
        W_close = self._transitive_closure(W)
        
        struct_score = self._score_answer(props_prompt, props_answer, W_close)
        conv, stab = self._track_dynamics(props_prompt, props_answer, W)
        dyn_score = 0.5 * conv + 0.5 * stab
        
        # Confidence based on dynamics stability and structural match
        raw_conf = 0.6 * dyn_score + 0.4 * struct_score
        
        # Cap by meta-confidence (epistemic honesty)
        return min(raw_conf, meta_conf, 0.85)
```

</details>
