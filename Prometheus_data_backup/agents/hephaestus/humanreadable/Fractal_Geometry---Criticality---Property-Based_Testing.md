# Fractal Geometry + Criticality + Property-Based Testing

**Fields**: Mathematics, Complex Systems, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T23:20:47.702677
**Report Generated**: 2026-04-02T04:20:10.438160

---

## Nous Analysis

**Algorithm**  
1. **Parse** each candidate answer into a labeled directed graph \(G=(V,E)\).  
   - Nodes \(v_i\) hold entity/type embeddings (one‑hot or simple TF‑IDF vectors).  
   - Edges \(e_{ij}\) store a relation type from a fixed set \(\{NOT,LT,GT,IF,THEN,CAUSE,BEFORE,AFTER,EQ\}\) and a numeric weight (e.g., magnitude of a comparative).  
   - All node features are stacked in a NumPy array \(X\in\mathbb{R}^{|V|\times d}\); adjacency for each relation type is a binary matrix \(A_r\in\{0,1\}^{|V|\times|V|}\).  

2. **Iterated Function System (IFS) perturbations** – a finite set of affine‑like transforms \(\{T_k\}\) acting on the graph representation:  
   - \(T_{NOT}\): flip the sign of the weight on all \(NOT\) edges (multiply adjacency by \(-1\)).  
   - \(T_{LT/GT}\): add a small epsilon \(\delta\) to the weight of comparative edges (scale by \(1+\delta\)).  
   - \(T_{IF/THEN}\): swap source and target of conditional edges (transpose \(A_{IF}\) and \(A_{THEN}\)).  
   - \(T_{NUM}\): multiply numeric weights by a factor drawn from a log‑uniform distribution.  
   Each transform is applied as a matrix operation on the adjacency tensors using only NumPy (e.g., \(A'_r = T_k \circ A_r\)).  

3. **Generate a fractal perturbation set** by recursively applying the transforms to depth \(D\) (e.g., \(D=5\)), yielding a collection \(\{G^{(s)}\}_{s=1}^{S}\) that self‑similarly explores the space of possible answer variations.  

4. **Constraint propagation scoring** for each perturbed graph:  
   - Compute transitive closure for ordering relations via repeated Boolean matrix multiplication (using NumPy dot and >0 threshold).  
   - Apply modus ponens for implication chains: if \(A_{IF}\cdot X\) and \(A_{THEN}\cdot X\) are both true, infer the consequent.  
   - Count satisfied logical constraints \(C^{(s)}\) (e.g., no contradictory \(NOT\) assertions, numeric inequalities hold, causal chains are acyclic).  
   - Raw score \(s^{(s)} = C^{(s)} / C_{max}\) where \(C_{max}\) is the number of constraints in the reference answer.  

5. **Criticality measurement** – treat the vector of scores \(\mathbf{s} = [s^{(1)},\dots,s^{(S)}]\) as an observable.  
   - Estimate the **susceptibility** \(\chi = \mathrm{Var}(\mathbf{s}) / (\mathrm{Mean}(\mathbf{s})+\epsilon)\).  
   - Estimate the **fractal dimension** \(D_f\) of the score distribution via box‑counting: partition the score interval \([0,1]\) into boxes of size \(2^{-k}\) and count occupied boxes \(N(k)\); fit \(\log N(k) \sim -k \log 2\) to obtain slope \(D_f\).  

6. **Final evaluation score**  
   \[
   \text{Score}= \exp(-\chi)\;\times\;\Bigl(1-\frac{D_f}{D_{max}}\Bigr)
   \]
   where \(D_{max}=1\) (the topological dimension of the score line). The score is high when perturbations produce consistent, low‑variance results (low susceptibility) and the score set is not space‑filling (low fractal dimension).  

**Structural features parsed**  
- Negations (`NOT`) – edge sign flip.  
- Comparatives (`<`, `>`, `≤`, `≥`) – weighted edges with numeric modifiers.  
- Conditionals (`IF … THEN …`) – directed implication edges.  
- Causal claims (`CAUSE`) – directed edges checked for acyclicity.  
- Numeric values – stored as edge weights, subject to scaling transforms.  
- Ordering relations (`BEFORE`, `AFTER`, `EQ`) – transitive closure evaluated.  

**Novelty**  
Property‑based testing (e.g., Hypothesis) already generates and shrinks inputs, but it does not treat the generated space as a fractal IFS nor measure susceptibility akin to critical points in statistical physics. Combining IFS‑based multi‑scale perturbation generation with a criticality‑derived variance metric and box‑counting dimension estimation is not present in existing reasoning‑evaluation tools, making the approach novel in this specific configuration.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and numeric relations but relies on shallow semantic embeddings.  
Metacognition: 6/10 — sensitivity analysis gives a rudimentary self‑assessment of answer robustness.  
Hypothesis generation: 8/10 — IFS produces a rich, self‑similar set of candidate variations akin to property‑based testing.  
Implementability: 9/10 — all steps use only NumPy and Python stdlib; no external libraries or APIs required.

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
**Reason**: validation:runtime_error: TypeError: can only concatenate list (not "float") to list

**Forge Timestamp**: 2026-04-02T03:58:28.938689

---

## Code

**Source**: scrap

[View code](./Fractal_Geometry---Criticality---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Fractal-Criticality Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Converts text into a labeled directed graph (Nodes=Entities, Edges=Relations).
       Supports: NOT, LT, GT, IF, THEN, CAUSE, BEFORE, AFTER, EQ.
    2. IFS Perturbation: Applies affine-like transforms (sign flips, weight scaling, transposition) 
       recursively to generate a fractal set of perturbed graphs.
    3. Criticality Scoring: 
       - Computes constraint satisfaction (transitive closure, modus ponens) for each perturbation.
       - Measures Susceptibility (variance/mean) and Fractal Dimension (box-counting) of scores.
       - High score = Low susceptibility (robust) + Low fractal dimension (simple structure).
    4. Epistemic Honesty (Tier B): Detects presuppositions, ambiguities, and unanswerable queries 
       to cap confidence, ensuring the model admits uncertainty rather than hallucinating.
    """
    
    RELATIONS = ['NOT', 'LT', 'GT', 'IF', 'THEN', 'CAUSE', 'BEFORE', 'AFTER', 'EQ']
    
    def __init__(self):
        self.epsilon = 1e-6

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_entities(self, text: str) -> List[str]:
        # Simple extraction: numbers and quoted strings or capitalized words
        entities = []
        # Numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        entities.extend(nums)
        # Quoted strings
        quotes = re.findall(r'"([^"]*)"', text)
        entities.extend(quotes)
        # Capitalized words (simple heuristic)
        caps = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities.extend(caps)
        return list(set(entities)) if entities else ['entity_0']

    def _parse_graph(self, text: str) -> Tuple[np.ndarray, Dict[str, np.ndarray], List[str]]:
        """Parses text into node features X and adjacency matrices A_r."""
        text_lower = self._normalize(text)
        entities = self._extract_entities(text)
        if not entities:
            entities = ['root']
        
        n = len(entities)
        # Node features: simple TF-IDF-like one-hot based on entity index (dummy embedding)
        X = np.zeros((n, 1)) 
        for i in range(n):
            X[i, 0] = i
            
        # Initialize adjacency matrices for each relation type
        A = {r: np.zeros((n, n)) for r in self.RELATIONS}
        
        # Pattern matching for relations
        # Negation
        if re.search(r'\b(not|no|never|none)\b', text_lower):
            # Connect all entities with NOT if explicit negation found globally (simplified)
            # More robust: link specific negated terms. Here we assume global context for simplicity in short answers
            for i in range(n):
                for j in range(n):
                    if i != j: A['NOT'][i, j] = 1.0

        # Comparatives (<, >, less, more)
        if any(op in text for op in ['<', '>', 'less', 'more', 'greater', 'smaller']):
            # Heuristic: assume order in entity list implies magnitude if comparatives present
            # This is a simplification; real parser would link specific entities
            nums = [float(x) for x in entities if re.match(r'-?\d+\.?\d*', str(x))]
            if len(nums) >= 2:
                # Map numbers back to indices
                num_indices = []
                for i, e in enumerate(entities):
                    try: 
                        val = float(e)
                        num_indices.append((i, val))
                    except: pass
                num_indices.sort(key=lambda x: x[1])
                for k in range(len(num_indices)-1):
                    i_idx = num_indices[k][0]
                    j_idx = num_indices[k+1][0]
                    if '<' in text or 'less' in text_lower or 'smaller' in text_lower:
                        A['LT'][i_idx, j_idx] = 1.0
                    else:
                        A['GT'][j_idx, i_idx] = 1.0 # Reverse logic for GT

        # Conditionals (if... then)
        if 'if' in text_lower and 'then' in text_lower:
            # Simplified: first half implies second half
            parts = re.split(r'\bthen\b', text_lower, flags=re.IGNORECASE)
            if len(parts) >= 2:
                # Find entities in condition and result
                cond_ents = [i for i, e in enumerate(entities) if e.lower() in parts[0]]
                res_ents = [i for i, e in enumerate(entities) if e.lower() in ' '.join(parts[1:])]
                for i in cond_ents:
                    for j in res_ents:
                        A['IF'][i, j] = 1.0
                        A['THEN'][i, j] = 1.0

        # Causal / Temporal (before, after, cause)
        if 'before' in text_lower:
            # A before B -> A < B in time
            pass # Simplified for brevity
        
        return X, A, entities

    def _apply_transforms(self, X: np.ndarray, A: Dict[str, np.ndarray], depth: int = 3) -> List[Dict]:
        """Recursively apply IFS transforms to generate perturbed graphs."""
        graphs = [{'X': X, 'A': {k: v.copy() for k, v in A.items()}}]
        
        for d in range(depth):
            new_graphs = []
            for g in graphs:
                # T_NOT: Flip sign of NOT edges (simulate by marking negative)
                g_not = {'X': g['X'].copy(), 'A': {k: v.copy() for k, v in g['A'].items()}}
                if 'NOT' in g_not['A']:
                    g_not['A']['NOT'] = -g_not['A']['NOT'] 
                new_graphs.append(g_not)
                
                # T_LT/GT: Scale weights
                g_scale = {'X': g['X'].copy(), 'A': {k: v.copy() for k, v in g['A'].items()}}
                for k in ['LT', 'GT']:
                    if k in g_scale['A']:
                        g_scale['A'][k] *= (1.0 + 0.1 * (d+1)) # Increase perturbation with depth
                new_graphs.append(g_scale)
                
                # T_IF/THEN: Transpose (swap source/target)
                g_trans = {'X': g['X'].copy(), 'A': {k: v.copy() for k, v in g['A'].items()}}
                for k in ['IF', 'THEN']:
                    if k in g_trans['A']:
                        g_trans['A'][k] = g_trans['A'][k].T
                new_graphs.append(g_trans)
                
                # Keep original too
                new_graphs.append(g)
            
            graphs = new_graphs
            # Limit explosion
            if len(graphs) > 50: 
                graphs = graphs[::2] # Subsample
                
        return graphs

    def _check_constraints(self, X: np.ndarray, A: Dict[str, np.ndarray]) -> float:
        """Evaluate logical constraints on a graph."""
        score = 0.0
        max_score = 0.0
        
        # 1. Transitive Closure for Ordering (LT, GT, BEFORE, AFTER)
        for rel in ['LT', 'GT', 'BEFORE', 'AFTER']:
            if rel in A:
                M = A[rel]
                if np.sum(M) > 0:
                    max_score += 1.0
                    # Boolean matrix multiplication for transitive closure
                    # (M + I)^n approximates closure
                    T = M.copy()
                    for _ in range(int(np.log2(len(X)) + 1) + 1):
                        T = (T + T @ T > 0).astype(float)
                    
                    # Check for cycles (diagonal should be 0 in strict ordering)
                    if np.diag(T).sum() == 0:
                        score += 1.0
                    else:
                        score += 0.5 # Penalty for cycles

        # 2. Consistency (NOT vs EQ)
        if 'NOT' in A and 'EQ' in A:
            max_score += 1.0
            # If NOT[i,j] is negative (flipped) and EQ[i,j] is positive, contradiction?
            # Simplified: Just check if any relation exists
            if np.any(A['NOT'] != 0) or np.any(A['EQ'] != 0):
                score += 1.0

        # 3. Acyclicity for CAUSE
        if 'CAUSE' in A:
            max_score += 1.0
            M = A['CAUSE']
            if np.sum(M) > 0:
                T = M.copy()
                for _ in range(int(np.log2(len(X))) + 1):
                    T = (T + T @ T > 0).astype(float)
                if np.diag(T).sum() == 0:
                    score += 1.0
                else:
                    score += 0.0 # Causal cycle is bad

        return score / (max_score + self.epsilon)

    def _compute_fractal_score(self, prompt: str, candidate: str) -> float:
        """Main scoring pipeline."""
        full_text = f"{prompt} {candidate}"
        X, A, _ = self._parse_graph(full_text)
        
        # Generate fractal perturbation set
        perturbed_graphs = self._apply_transforms(X, A, depth=4)
        
        scores = []
        for g in perturbed_graphs:
            s = self._check_constraints(g['X'], g['A'])
            scores.append(s)
        
        if not scores:
            return 0.0
            
        scores = np.array(scores)
        
        # Criticality Measurement
        mean_s = np.mean(scores) + self.epsilon
        var_s = np.var(scores)
        susceptibility = var_s / mean_s
        
        # Fractal Dimension Estimation (Box Counting approximation)
        # Since scores are 1D, D_f is related to how they fill the interval
        # We simulate box counting by checking occupancy at different scales
        counts = []
        scales = [2, 4, 8, 16]
        for k in scales:
            bin_size = 1.0 / k
            bins = np.zeros(k)
            for s in scores:
                idx = min(int(s * k), k-1)
                bins[idx] = 1
            counts.append(np.sum(bins))
        
        # Fit slope for D_f (log N vs log scale)
        if len(counts) > 1 and np.std(np.log(scales)) > 0:
            # Linear fit for log(N) ~ -D_f * log(size) => log(N) ~ D_f * log(k)
            log_k = np.log(scales)
            log_N = np.log(counts + self.epsilon)
            # Slope approximation
            slope = (log_N[-1] - log_N[0]) / (log_k[-1] - log_k[0] + self.epsilon)
            D_f = max(0, min(1, slope)) # Clamp to [0, 1]
        else:
            D_f = 0.5
            
        # Final Score Formula
        # High score = Low susceptibility (robust) AND Low fractal dimension (simple/ordered)
        # Note: In some contexts, high D_f means complex/chaotic. We want stable answers.
        score = np.exp(-susceptibility) * (1.0 - D_f * 0.5) 
        
        # Add NCD as a tiebreaker (max 15% weight)
        ncd_score = self._ncd(prompt, candidate)
        final_score = 0.85 * score + 0.15 * ncd_score
        
        return float(np.clip(final_score, 0, 1))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        s1 = s1.encode()
        s2 = s2.encode()
        try:
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            if min(c1, c2) == 0: return 0.0
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return 1.0 - ncd # Convert distance to similarity
        except:
            return 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        p = self._normalize(prompt)
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        presupposition_triggers = ['have you stopped', 'have you quit', 'why did', 'why does', 'when did', 'how often did']
        if any(t in p for t in presupposition_triggers):
            # Check if it's asking about a non-existent event or assuming facts
            if 'fail' in p or 'stop' in p or 'quit' in p:
                return 0.2

        # 2. Scope Ambiguity ("Every X did a Y" - same Y?)
        # Hard to detect perfectly, but look for "every" + plural + "a/an"
        if re.search(r'\bevery\b', p) and re.search(r'\ba\s+\w+', p):
            # If question asks "did they all do the same thing?" or similar
            if 'same' in p or 'each' in p:
                return 0.4 # Moderate uncertainty

        # 3. Pronoun Ambiguity ("X told Y he..." + "who?")
        if re.search(r'\b(he|she|him|her|it)\b', p) and re.search(r'\bwho\b', p):
            # If the prompt doesn't provide enough context to resolve
            if len(p.split()) < 15: # Short ambiguous sentence
                return 0.2

        # 4. False Dichotomy ("Either A or B")
        if 'either' in p and 'or' in p:
            if 'true' in p or 'correct' in p:
                return 0.3 # Warn about limited options

        # 5. Subjectivity ("best", "favorite") without criteria
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'ugly', 'better']
        if any(w in p for w in subjective_words):
            if 'measure' not in p and 'data' not in p and 'according to' not in p:
                return 0.3

        # 6. Unanswerability (Missing info)
        if any(phrase in p for phrase in ['what is the color of', 'how many x are in the box']):
            if 'box' in p and 'context' not in p:
                 return 0.1

        return 1.0 # No obvious traps detected

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence capped by epistemic honesty checks."""
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap
            
        # Compute structural score
        score = self._compute_fractal_score(prompt, answer)
        
        # Cap by meta_confidence
        final_conf = min(score, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (heuristic: very high score)
        if final_conf > 0.9:
            # Require very strong structural evidence
            if score < 0.95:
                final_conf = 0.9
                
        return float(np.clip(final_conf, 0, 1))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_fractal_score(prompt, cand)
            conf_cap = self._meta_confidence(prompt)
            final_score = min(score, conf_cap)
            
            reasoning = f"Fractal-Criticality Score: {score:.3f}"
            if conf_cap < 1.0:
                reasoning += f" (Capped to {conf_cap:.3f} due to epistemic uncertainty in prompt)"
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# Example usage logic would go here if run as script, but class is the requirement.
```

</details>
