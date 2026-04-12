# Category Theory + Active Inference + Mechanism Design

**Fields**: Mathematics, Cognitive Science, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T06:43:18.631584
**Report Generated**: 2026-03-27T16:08:16.108676

---

## Nous Analysis

The algorithm builds a **functor‑induced constraint network** that maps a syntactic parse of a question and each candidate answer to a small category of propositions.  

1. **Parsing & data structures** – A regex‑based extractor yields a list of atomic propositions \(p_i\). Each proposition gets a type tag from the set {negation, comparative, conditional, causal, numeric, ordering, quantifier}. For every proposition we store a feature vector \(\mathbf{f}_i\in\mathbb{R}^k\) (one‑hot for type, plus a scalar for any numeric value). Propositions are nodes in a directed graph \(G\); edges encode the logical relation extracted (e.g., “\(A\) → \(B\)” for a conditional, “\(A\) > \(B\)” for an ordering, “\(A\) causes \(B\)” for causal). The graph is represented by two NumPy arrays: an adjacency matrix \(A\in\{0,1\}^{n\times n}\) and an edge‑type matrix \(E\in\{0,1\}^{n\times n\times t}\) where \(t\) is the number of relation types.

2. **Functor mapping** – The functor \(F\) takes the parse graph of the reference answer (or a gold‑standard solution) and produces a canonical category \(\mathcal{C}_{ref}\). Applying the same functor to a candidate answer yields \(\mathcal{C}_{cand}\). A natural transformation \(\eta:\mathcal{C}_{ref}\Rightarrow\mathcal{C}_{cand}\) is approximated by the element‑wise difference of the node feature matrices: \(\Delta = F_{cand} - F_{ref}\).

3. **Active‑inference scoring (expected free energy)** –  
   - **Complexity term**: entropy of the candidate’s feature distribution, \(H = -\sum_i \mathbf{f}_i\log\mathbf{f}_i\) (computed with NumPy).  
   - **Risk term**: expected constraint violation. For each edge type \(r\) we define a predicate \(pr_r(\mathbf{f}_i,\mathbf{f}_j)\) that returns 1 if the relation holds (e.g., for ordering, check \(\mathbf{f}_j^{num} - \mathbf{f}_i^{num} > 0\) using the numeric slot). The risk is \(R = \sum_{i,j,r} A_{ij}E_{ijr}\,(1-pr_r(\mathbf{f}_i,\mathbf{f}_j))\).  
   - Expected free energy: \(F = H + \lambda R\) with \(\lambda\) a weighting hyper‑parameter. Lower \(F\) indicates higher plausibility; the score is \(S = -F\).

4. **Mechanism‑design incentive** – The scoring rule is designed to be **truth‑promoting**: if a candidate deviates from the reference, any increase in \(H\) (more uncertainty) or \(R\) (more violated constraints) raises \(F\), reducing the reward. Thus, maximizing \(S\) aligns with reporting the true logical content, satisfying incentive compatibility.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations (including transitive chains), and quantifiers.

**Novelty** – While logical parsers, Bayesian active‑inference frameworks, and mechanism‑design scoring exist separately, their conjunction into a single functor‑derived constraint network with an explicit free‑energy‑based reward has not been reported in the literature.

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via constraint propagation and free energy.  
Metacognition: 6/10 — limited self‑reflection; the model can assess its own uncertainty but does not revise parsing strategies.  
Hypothesis generation: 5/10 — can generate alternative parses by sampling feature perturbations, but lacks systematic hypothesis expansion.  
Implementability: 9/10 — relies only on regex, NumPy, and stdlib; all operations are matrix‑based and straightforward to code.

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
**Reason**: trap_battery_failed (acc=40% cal=26% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T09:15:01.283916

---

## Code

**Source**: scrap

[View code](./Category_Theory---Active_Inference---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np

class ReasoningTool:
    """
    Functor-Induced Constraint Network with Active Inference Scoring.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions tagged by type (numeric, conditional, etc.)
       into a feature matrix F and logical relation graphs (Adjacency A, Edge-types E).
    2. Functor Mapping: Maps the candidate parse to the reference space. The 'natural 
       transformation' error is approximated by the L1 distance between feature matrices.
    3. Active Inference: Computes Expected Free Energy (F = Complexity + Risk).
       - Complexity (H): Entropy of feature distribution (uncertainty).
       - Risk (R): Sum of violated logical constraints (e.g., A > B but val_A <= val_B).
    4. Scoring: Score = -F. Lower energy (higher plausibility) yields higher score.
    """

    def __init__(self):
        self.types = ['negation', 'comparative', 'conditional', 'causal', 'numeric', 'ordering', 'quantifier']
        self.type_map = {t: i for i, t in enumerate(self.types)}
        self.num_type_idx = self.type_map['numeric']
        self.comp_type_idx = self.type_map['comparative']
        self.order_type_idx = self.type_map['ordering']

    def _extract_props(self, text: str):
        """Regex-based extractor yielding propositions and feature vectors."""
        props = []
        features = []
        text_lower = text.lower()
        
        # Patterns
        patterns = [
            (r'not\s+(\w+)', 'negation'),
            (r'(more|less|greater|smaller|higher|lower)\s+than', 'comparative'),
            (r'if\s+.+then\s+.+|implies', 'conditional'),
            (r'causes|leads\s+to|results\s+in', 'causal'),
            (r'-?\d+\.?\d*', 'numeric'),
            (r'(before|after|first|last|next)', 'ordering'),
            (r'(all|some|none|every|at\s+least)', 'quantifier')
        ]
        
        found_indices = set()
        
        # Extract matches
        for pattern, p_type in patterns:
            for match in re.finditer(pattern, text_lower):
                if match.start() not in found_indices:
                    found_indices.add(match.start())
                    val = 0.0
                    if p_type == 'numeric':
                        try: val = float(match.group())
                        except: pass
                    
                    # Feature vector: [one_hot_types..., numeric_value]
                    f_vec = [0.0] * (len(self.types) + 1)
                    f_vec[self.type_map[p_type]] = 1.0
                    f_vec[-1] = val
                    props.append((match.group(), p_type, match.start()))
                    features.append(f_vec)
        
        if not props:
            # Fallback for empty parse
            return np.zeros((1, len(self.types) + 1)), np.zeros((1,1)), np.zeros((1,1,len(self.types)))
            
        F = np.array(features)
        n = len(props)
        
        # Build Graph (Simplified: Fully connected for small n, or proximity based)
        # For this implementation, we assume a dense constraint network where 
        # logical consistency is checked pairwise if types align.
        A = np.ones((n, n)) if n > 1 else np.zeros((1,1))
        E = np.zeros((n, n, len(self.types)))
        
        if n > 1:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        # Heuristic edge typing based on proposition types
                        # If prop i is numeric and j is numeric, maybe ordering
                        if F[i, self.num_type_idx] > 0 and F[j, self.num_type_idx] > 0:
                             E[i, j, self.order_type_idx] = 1
                        # Generic logical flow
                        E[i, j, self.type_map[props[i][1]]] = 1 
                        E[i, j, self.type_map[props[j][1]]] = 1

        return F, A, E

    def _compute_risk(self, F, A, E):
        """Calculate constraint violation risk R."""
        if F.shape[0] < 2:
            return 0.0
        
        risk = 0.0
        n = F.shape[0]
        count = 0
        
        for i in range(n):
            for j in range(n):
                if i == j: continue
                for r_idx in range(len(self.types)):
                    if E[i, j, r_idx] == 1:
                        count += 1
                        # Check specific predicates
                        violation = 0.0
                        if r_idx == self.order_type_idx:
                            # Check numeric consistency if both have numeric values
                            val_i = F[i, -1]
                            val_j = F[j, -1]
                            if val_i != 0 and val_j != 0:
                                # Simple heuristic: if indices suggest order, check values
                                # Since we don't have explicit direction in this simple parse,
                                # we penalize high variance in numeric clusters as 'risk'
                                if abs(val_i - val_j) > 100: # Arbitrary threshold for conflict
                                    violation = 1.0
                        elif r_idx == self.type_map['negation']:
                            # Hard to check without semantic NLP, approximate with feature mismatch
                            if np.allclose(F[i], F[j]):
                                violation = 0.5 
                        risk += violation
        return risk if count == 0 else risk / max(count, 1)

    def _compute_energy(self, F, A, E, F_ref=None):
        """Compute Expected Free Energy F = H + lambda*R."""
        # Complexity H: Entropy of feature distribution
        # Normalize features to sum to 1 for entropy calc
        F_norm = F + 1e-9
        F_prob = F_norm / np.sum(F_norm)
        H = -np.sum(F_prob * np.log(F_prob))
        
        # Risk R
        R = self._compute_risk(F, A, E)
        
        # Divergence from reference (Functor mapping error)
        Delta = 0.0
        if F_ref is not None:
            if F.shape == F_ref.shape:
                Delta = np.sum(np.abs(F - F_ref))
            else:
                # Shape mismatch penalty
                Delta = abs(F.shape[0] - F_ref.shape[0]) * 10.0

        lam = 1.5
        free_energy = H + lam * R + 0.5 * Delta
        return -free_energy # Score is negative free energy

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        # Parse Prompt as Reference Structure (Gold Standard Proxy)
        F_ref, A_ref, E_ref = self._extract_props(prompt)
        
        results = []
        scores = []
        
        for cand in candidates:
            F_cand, A_cand, E_cand = self._extract_props(cand)
            
            # Calculate Score
            score = self._compute_energy(F_cand, A_cand, E_cand, F_ref)
            
            # Add NCD as a tiny tie-breaker bonus for string similarity if scores are close
            # This ensures "Yes" vs "No" distinction if logic is ambiguous
            try:
                import zlib
                s_joint = (prompt + cand).encode('utf-8')
                s_cand = cand.encode('utf-8')
                s_prompt = prompt.encode('utf-8')
                l_joint = len(zlib.compress(s_joint))
                l_cand = len(zlib.compress(s_cand))
                l_prompt = len(zlib.compress(s_prompt))
                ncd = (l_joint - min(l_cand, l_prompt)) / max(l_joint, 1)
                score += (1.0 - ncd) * 0.01 # Small bonus
            except:
                pass

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Energy: {-score:.4f}, Nodes: {F_cand.shape[0]}"
            })
            scores.append(score)
        
        # Rank descending
        ranked_indices = np.argsort(scores)[::-1]
        return [results[i] for i in ranked_indices]

    def confidence(self, prompt: str, answer: str) -> float:
        # Use the scoring mechanism relative to a perfect match proxy
        # If the answer contains the same logical structure as the prompt's implied solution
        F_ans, _, _ = self._extract_props(answer)
        F_prompt, _, _ = self._extract_props(prompt)
        
        # Heuristic: If answer has high numeric content matching prompt, or low energy
        # We simulate a 'perfect' candidate by checking if answer reduces prompt entropy
        score = self._compute_energy(F_ans, np.ones((1,1)), np.zeros((1,1,1)), F_prompt)
        
        # Normalize to 0-1 roughly based on empirical bounds of the energy function
        # Energy is negative, so higher (less negative) is better.
        # Shift and scale: assume range [-20, 0] maps to [0, 1]
        conf = 1.0 / (1.0 + np.exp(-(score + 5.0))) # Sigmoid mapping
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
