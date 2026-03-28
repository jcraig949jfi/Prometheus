# Neural Plasticity + Theory of Mind + Criticality

**Fields**: Biology, Cognitive Science, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T17:17:44.759977
**Report Generated**: 2026-03-27T05:13:35.125555

---

## Nous Analysis

**Algorithm**  
We build a weighted directed graph \(G=(V,E)\) where each node \(v_i\in V\) represents a proposition extracted from the prompt and a candidate answer (e.g., “X causes Y”, “¬Z”, “A > B”). Edge weights \(w_{ij}\) encode the strength of a Hebbian association between propositions \(i\) and \(j\).  

1. **Parsing** – Using regex we extract:  
   * literals (noun‑verb‑noun triples)  
   * negations (`not`, `no`) → flag node with polarity −1  
   * comparatives (`more than`, `less than`) → create ordered‑pair nodes with a comparative edge type  
   * conditionals (`if … then …`) → add a directed edge from antecedent to consequent labeled “cond”  
   * causal cues (`because`, `leads to`) → causal edge type  
   * numeric values → attach as attribute to the node.  

   The result is a set of node feature vectors \(x_i\in\{0,1\}^k\) (one‑hot for predicate type, polarity, comparatives, etc.) and an initial adjacency matrix \(W^{(0)}\) where \(w_{ij}^{(0)}=1\) if a syntactic relation connects \(i\)→\(j\), else 0.

2. **Hebbian plasticity with pruning** – For each candidate answer we run \(T\) iterations of:  
   \[
   \Delta w_{ij}= \eta \, (a_i a_j) - \lambda \, w_{ij}
   \]  
   where \(a_i = \sigma\!\left(\sum_j w_{ij} x_j\right)\) is the node activation (sigmoid), \(\eta\) is a learning rate, and \(\lambda\) implements synaptic pruning (weight decay). After each iteration we renormalize rows to keep \(\sum_j w_{ij}=1\).

3. **Theory of Mind recursion** – We maintain two belief states: the *self* belief vector \(b^{\text{self}}\) (derived from the prompt) and an *other* belief vector \(b^{\text{other}}\) initialized as a copy of \(b^{\text{self}}\). At each iteration we update the other’s belief by propagating the self’s activation through the graph, simulating a first‑order mental model:  
   \[
   b^{\text{other}} \leftarrow \sigma\!\left(W^\top b^{\text{self}}\right)
   \]  
   Recursive mentalizing (depth \(d\)) is achieved by repeating this step \(d\) times, each time swapping self/other roles.

4. **Criticality tuning** – After each Hebbian update we compute the spectral radius \(\rho(W)\). We adjust \(\eta\) via a simple homeostatic rule: if \(\rho(W)>1+\epsilon\) decrease \(\eta\); if \(\rho(W)<1-\epsilon\) increase \(\epsilon\). This drives the system to the edge of chaos where correlation length is maximal, giving the network high susceptibility to subtle structural mismatches.

5. **Scoring** – After \(T\) iterations we compute the energy  
   \[
   E = -\sum_{i,j} w_{ij} \, (b^{\text{self}}_i \, b^{\text{other}}_j)
   \]  
   Lower energy indicates better alignment of the candidate answer with the prompt under the plasticity‑ToM‑critical dynamics. The final score is \(-E\) (higher = better).

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations (before/after), numeric attributes, and polarity flags.

**Novelty** – While Hebbian learning, recursive Theory‑of‑Mind graphs, and criticality‑tuned reservoirs appear separately in cognitive modeling and reservoir computing, their joint use as a scoring mechanism for answer evaluation has not been reported; the specific combination of synaptic pruning, belief‑state swapping, and spectral‑radius homeostasis is novel.

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical structure and propagates constraints, but relies on hand‑crafted regex and fixed depth.  
Metacognition: 7/10 — Modeling an “other” belief provides a rudimentary form of self‑reflection, yet lacks higher‑order uncertainty estimation.  
Hypothesis generation: 6/10 — Energy minimization yields a single best candidate; generating alternative hypotheses would require sampling mechanisms not included.  
Implementability: 9/10 — All operations are plain NumPy array manipulations and standard‑library regex; no external dependencies or neural nets are needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Neural Plasticity**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 29% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Criticality + Neural Plasticity: negative interaction (-0.103). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Neural Plasticity + Feedback Control (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Evolution + Criticality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: ValueError: shapes (2,2) and (5,2) not aligned: 2 (dim 1) != 5 (dim 0)

**Forge Timestamp**: 2026-03-26T01:19:32.599250

---

## Code

**Source**: scrap

[View code](./Neural_Plasticity---Theory_of_Mind---Criticality/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np

class ReasoningTool:
    """
    Implements a Neuro-Symbolic Reasoning Engine based on Hebbian Plasticity,
    Theory of Mind (ToM) recursion, and Criticality tuning.
    
    Mechanism:
    1. Parsing: Extracts propositions, negations, comparatives, and causals into a graph.
    2. Dynamics: Uses Hebbian learning with pruning to strengthen coherent logical paths.
    3. ToM: Simulates belief propagation between 'self' (prompt) and 'other' (candidate).
    4. Criticality: Adjusts learning rate to keep the system at the 'edge of chaos' 
       (spectral radius ~1) for maximum sensitivity to logical contradictions.
    5. Scoring: Computes energy based on the alignment of belief states.
    """

    def __init__(self):
        self.epsilon = 0.1
        self.t_iterations = 5
        self.tom_depth = 2

    def _parse_nodes(self, text):
        """Extracts literals, negations, comparatives, and numbers."""
        nodes = []
        features = []
        
        # Normalize
        text_lower = text.lower()
        
        # Detect global negation
        has_negation = bool(re.search(r'\b(not|no|never|none)\b', text_lower))
        
        # Detect comparatives
        has_comparative = bool(re.search(r'\b(more|less|greater|smaller|before|after)\b', text_lower))
        
        # Detect conditionals
        has_conditional = bool(re.search(r'\b(if|then|unless)\b', text_lower))
        
        # Detect causality
        has_causal = bool(re.search(r'\b(because|causes|leads to|due to)\b', text_lower))

        # Extract numbers
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        numeric_val = float(nums[0]) if nums else 0.0
        
        # Simple feature vector: [neg, comp, cond, causal, has_num]
        feat_vec = [
            1.0 if has_negation else 0.0,
            1.0 if has_comparative else 0.0,
            1.0 if has_conditional else 0.0,
            1.0 if has_causal else 0.0,
            1.0 if nums else 0.0
        ]
        
        # Create a node for the whole proposition context
        nodes.append("root_prop")
        features.append(feat_vec)
        
        # Add specific extracted entities as nodes to create graph density
        # Extract Noun-Verb-Noun approximations
        triples = re.findall(r'(\w+)\s+(is|causes|leads|precedes|follows|equals)\s+(\w+)', text_lower)
        for t in triples:
            nodes.append(f"rel_{t[0]}_{t[1]}_{t[2]}")
            features.append(feat_vec) # Inherit context features
            
        if not triples:
            # Fallback: split by sentences/clauses to ensure graph exists
            clauses = re.split(r'[.,;]', text)
            for i, c in enumerate(clauses):
                if c.strip():
                    nodes.append(f"clause_{i}")
                    features.append(feat_vec)

        return nodes, np.array(features, dtype=np.float32)

    def _build_graph(self, prompt, candidate):
        """Constructs initial adjacency matrix W and feature matrix X."""
        full_text = f"{prompt} {candidate}"
        nodes, X = self._parse_nodes(full_text)
        n = len(nodes)
        
        if n == 0:
            return np.zeros((1,1)), np.zeros((1,1))
            
        # Initialize W with syntactic relations (simplified to fully connected 
        # within the extracted context for robustness, weighted by feature similarity)
        W = np.zeros((n, n), dtype=np.float32)
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    W[i, j] = 0.5 # Self-loop stability
                else:
                    # Syntactic proximity heuristic: 
                    # If features match, strong connection. If mismatch (e.g. negation), weaker.
                    sim = np.dot(X[i], X[j]) / (np.linalg.norm(X[i]) * np.linalg.norm(X[j]) + 1e-9)
                    W[i, j] = sim
        
        # Normalize rows
        row_sums = W.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        W = W / row_sums
        
        return W, X

    def _run_dynamics(self, W, X, candidate):
        """Runs Hebbian plasticity, ToM recursion, and Criticality tuning."""
        n = W.shape[0]
        if n == 0: return 0.0
        
        # Initialize beliefs
        # Self: derived from prompt structure (uniform high activation initially)
        b_self = np.ones((n, 1), dtype=np.float32) * 0.5
        # Other: initialized to self, will evolve
        b_other = b_self.copy()
        
        eta = 0.1
        lambda_prune = 0.05
        sigmoid = lambda x: 1 / (1 + np.exp(-x))
        
        for t in range(self.t_iterations):
            # 1. Hebbian Update
            # a_i = sigma(W * x) - simplified activation based on features
            a = sigmoid(np.dot(W, X.T).T) # Shape (n, features) -> reduce to node activation
            a = np.mean(a, axis=1).reshape(-1, 1) # Average over features to get node activation
            
            # Delta W = eta * (a * a^T) - lambda * W
            delta_W = eta * np.dot(a, a.T) - lambda_prune * W
            W = W + delta_W
            
            # Renormalize rows
            row_sums = W.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            W = W / row_sums
            
            # 2. Criticality Tuning (Spectral Radius Homeostasis)
            # Approximate spectral radius via max row sum (infinity norm) for speed
            rho = np.max(np.sum(np.abs(W), axis=1))
            if rho > 1.0 + self.epsilon:
                eta *= 0.9 # Decrease learning rate to stabilize
            elif rho < 1.0 - self.epsilon:
                eta *= 1.1 # Increase to explore
            
            # 3. Theory of Mind Recursion
            # Propagate self belief to other
            for _ in range(self.tom_depth):
                b_other = sigmoid(np.dot(W.T, b_self))
                # Swap for next depth iteration (simulating recursive modeling)
                b_self, b_other = b_other, b_self
                
        # 4. Scoring: Energy minimization
        # E = - sum(w_ij * b_self_i * b_other_j)
        # We want low energy (high alignment), so score = -E
        energy = -np.sum(W * np.dot(b_self, b_other.T))
        
        # Normalize score to 0-1 range roughly
        score = -energy / (n * n) 
        return float(score)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            W, X = self._build_graph(prompt, cand)
            score = self._run_dynamics(W, X, cand)
            
            # Heuristic boost for structural matches if score is ambiguous
            # Check for direct string inclusion of key logical tokens
            common_tokens = set(re.findall(r'\b\w+\b', prompt.lower())) & set(re.findall(r'\b\w+\b', cand.lower()))
            overlap_ratio = len(common_tokens) / (len(set(re.findall(r'\b\w+\b', prompt.lower()))) + 1)
            
            # Blend physics-based score with basic overlap to ensure robustness
            final_score = 0.6 * score + 0.4 * overlap_ratio
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Hebbian-ToM energy: {score:.4f}, Overlap: {overlap_ratio:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        W, X = self._build_graph(prompt, answer)
        if W.size == 0:
            return 0.0
        score = self._run_dynamics(W, X, answer)
        # Map score to 0-1. The dynamics usually yield small numbers.
        # Sigmoid mapping for confidence
        conf = 1 / (1 + np.exp(-10 * (score + 0.5))) 
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
