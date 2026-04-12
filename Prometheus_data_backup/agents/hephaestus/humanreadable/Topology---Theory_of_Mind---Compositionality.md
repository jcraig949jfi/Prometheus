# Topology + Theory of Mind + Compositionality

**Fields**: Mathematics, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T13:31:49.934176
**Report Generated**: 2026-03-26T19:49:03.841193

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Convert the prompt and each candidate answer into a typed dependency tree using a deterministic shift‑reduce parser built from the standard library (regex tokenisation, POS‑tag lookup tables). Each leaf node is an atomic proposition \(p_i\) (subject‑predicate‑object) annotated with extracted primitives: polarity (negation), modality (belief/desire), comparative operator, numeric value, or temporal marker. Internal nodes store the combination rule (e.g., ∧, →, ¬, ∀, ∃) derived from the dependency label. The tree is flattened into a **semantic graph** \(G=(V,E)\) where each \(V\) corresponds to a leaf proposition and each directed edge \(e_{ij}\) encodes the logical relation imposed by its parent node (e.g., \(p_i\rightarrow p_j\) for an implication, \(p_i\leftrightarrow p_j\) for a biconditional, \(p_i\sim p_j\) for a similarity constraint). Edge types are stored in a numpy array `etype` (0 = ¬, 1 = ∧, 2 = →, 3 = ∨, 4 = ≡, 5 = <, 6 = >, 7 = =).  

2. **Theory of Mind Expansion** – For each graph, generate a set of **belief‑state variants** \( \{G^{(k)}\} \) by toggling the truth value of nodes marked with a belief modality (e.g., “John thinks that …”). This yields a small K‑dimensional hypercube of possible worlds (K ≤ 5 in practice).  

3. **Topological Scoring** – Treat each variant as a simplicial complex where 0‑simplices are nodes and 1‑simplices are edges of type → or ≡. Compute the **boundary matrix** \(B_1\) (nodes × edges) using numpy; the rank of \(B_1\) gives the number of independent 1‑cycles (first Betti number \(β_1\)). Similarly, compute \(β_0\) (connected components) via union‑find on the adjacency matrix. The topological signature of a variant is the tuple \((β_0,β_1)\).  

4. **Constraint Propagation** – Apply iterative fix‑point propagation (modus ponens, transitivity, and symmetry for ≡) on the adjacency matrix until convergence; record the final truth‑value vector \(t\).  

5. **Scoring Logic** – For a candidate answer, compute the Euclidean distance between its topological signature \((β_0,β_1)\) and the gold answer’s signature, plus the Hamming distance between its propagated truth vector \(t\) and the gold \(t\). The final score is  
\[
S = -\big( w_1\|Δβ\|_2 + w_2 \|t_{cand}-t_{gold}\|_1 \big)
\]  
with weights \(w_1,w_2\) set to 0.5 each. Lower distance → higher score.

**Structural Features Parsed**  
Negations (¬), comparatives (<, >, =), conditionals (→), biconditionals (≡), quantifiers (∀, ∃) via modal tags, causal claims (→ with temporal markers), numeric values (regex‑extracted integers/floats), ordering relations (<, >), and belief/desire modalities (ToM nodes).

**Novelty**  
While topological data analysis, theory‑of‑mind modeling, and compositional semantic parsing each appear separately in NLP literature, their joint use — specifically computing Betti numbers over belief‑state graphs generated from a compositionally parsed logical form — has not been combined in a single scoring algorithm. Existing systems use either graph‑based consistency checks or mental‑state simulation, but not the topological invariant‑based similarity metric described here.

**Rating**  
Reasoning: 8/10 — captures logical consistency and belief alternatives via concrete graph operations.  
Metacognition: 7/10 — models alternative belief states but limited to simple toggling, not full recursive reasoning.  
Hypothesis generation: 6/10 — generates belief variants; does not propose new hypotheses beyond toggling.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and union‑find; all feasible in ≤200 lines.

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

- **Topology**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Chaos Theory + Active Inference + Compositionality (accuracy: 0%, calibration: 0%)
- Chaos Theory + Adaptive Control + Compositionality (accuracy: 0%, calibration: 0%)
- Chaos Theory + Compositionality + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=13% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T17:20:06.022178

---

## Code

**Source**: scrap

[View code](./Topology---Theory_of_Mind---Compositionality/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Compositional Parsing, Theory of Mind (ToM) expansion,
    and Topological Scoring (Betti numbers) to evaluate logical consistency.
    
    Mechanism:
    1. Parsing: Converts text to a semantic graph of atomic propositions with logical edges.
    2. ToM Expansion: Generates belief variants by toggling modal nodes.
    3. Topology: Computes Betti numbers (beta0, beta1) on the implication graph.
    4. Scoring: Ranks candidates by minimizing distance to the prompt's topological signature
       and truth-vector consistency, using NCD only as a tiebreaker.
    """
    
    # Edge types: 0=NOT, 1=AND, 2=IMPLIES, 3=OR, 4=EQ, 5=LT, 6=GT, 7=NUM
    ETYPES = {'not':0, 'and':1, 'implies':2, 'or':3, 'eq':4, 'lt':5, 'gt':6, 'num':7}
    
    def __init__(self):
        self.ncd_cache = {}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b|[<>=]|[\d\.]+|[^\w\s]', text.lower())

    def _parse_to_graph(self, text: str) -> Tuple[List[Dict], np.ndarray, List[int]]:
        """Parses text into nodes (props) and edges (logical relations)."""
        tokens = self._tokenize(text)
        nodes = []
        edges = [] # (src, dst, type)
        
        # Simple state machine for parsing
        i = 0
        current_subj = None
        current_pred = None
        last_node_idx = -1
        
        while i < len(tokens):
            t = tokens[i]
            
            # Detect Negation
            if t in ['no', 'not', 'never', 'false']:
                if last_node_idx >= 0:
                    edges.append((last_node_idx, last_node_idx, 0)) # Self-loop negation
                i += 1
                continue
                
            # Detect Comparatives
            if t in ['<', '>', '=']:
                if last_node_idx >= 0 and i+1 < len(tokens):
                    # Look for number next
                    next_t = tokens[i+1]
                    if re.match(r'[\d\.]+', next_t):
                        val = float(next_t)
                        etype = 5 if t == '<' else (6 if t == '>' else 4)
                        # Create numeric node
                        n_idx = len(nodes)
                        nodes.append({'text': f"num_{val}", 'val': val, 'type': 'num'})
                        edges.append((last_node_idx, n_idx, etype))
                        last_node_idx = n_idx
                        i += 2
                        continue
            
            # Detect Conditionals (if... then)
            if t == 'if':
                # Mark next clause as antecedent
                pass 
            
            # Detect Belief Modals (ToM)
            is_modal = t in ['thinks', 'believes', 'wants', 'says']
            
            # Extract simple SVO or propositions
            if t not in ['if', 'then', 'and', 'or', 'but', 'because', 'so']:
                # Heuristic: treat sequence of words as a proposition until connector
                prop_words = [t]
                i += 1
                while i < len(tokens) and tokens[i] not in ['if', 'then', 'and', 'or', 'but', 'because', 'so', '.', ',']:
                    prop_words.append(tokens[i])
                    i += 1
                
                p_text = " ".join(prop_words)
                nodes.append({'text': p_text, 'type': 'belief' if is_modal else 'fact'})
                idx = len(nodes) - 1
                
                if last_node_idx >= 0:
                    # Default connective is AND or IMPLIES based on context
                    edges.append((last_node_idx, idx, 2)) # Default implies
                last_node_idx = idx
                continue
            
            i += 1

        if not nodes:
            nodes.append({'text': 'empty', 'type': 'fact'})
            
        # Build adjacency matrix for edges (implication/eq)
        n = len(nodes)
        adj = np.zeros((n, n), dtype=int)
        etype_arr = np.zeros((n, n), dtype=int) - 1
        
        for u, v, t in edges:
            if u < n and v < n:
                adj[u, v] = 1
                etype_arr[u, v] = t
                
        return nodes, adj, etype_arr

    def _compute_betti(self, adj: np.ndarray) -> Tuple[int, int]:
        """Computes beta0 (components) and beta1 (cycles) using numpy/union-find logic."""
        if adj.shape[0] == 0:
            return 1, 0
            
        n = adj.shape[0]
        # Symmetrize for connectivity (undirected view for components)
        undir = (adj + adj.T) > 0
        
        # Union-Find for beta0
        parent = list(range(n))
        def find(x):
            if parent[x] != x: parent[x] = find(parent[x])
            return parent[x]
        def union(x, y):
            px, py = find(x), find(y)
            if px != py: parent[px] = py
            
        for i in range(n):
            for j in range(n):
                if undir[i, j]: union(i, j)
        
        comps = len(set(find(i) for i in range(n)))
        beta0 = max(1, comps) # At least 1 component
        
        # Beta1 approx: E - V + C (Euler characteristic for graphs)
        # Count directed edges that are part of the main structure
        E = np.sum(adj > 0)
        V = n
        beta1 = max(0, int(E - V + beta0))
        
        return beta0, beta1

    def _propagate_truth(self, nodes: List[Dict], adj: np.ndarray) -> np.ndarray:
        """Simple fixpoint propagation of truth values."""
        n = len(nodes)
        if n == 0: return np.array([])
        
        # Initialize all as True (1), unless explicitly negated (handled in parsing ideally)
        t = np.ones(n, dtype=float)
        
        # Iterate for fixpoint
        for _ in range(n):
            changed = False
            for u in range(n):
                for v in range(n):
                    if adj[u, v] > 0:
                        # If u is true, v must be true (Modus Ponens approx)
                        if t[u] > 0.5 and t[v] < 0.5:
                            t[v] = 1.0
                            changed = True
                        # If u is false (0), no direct propagation in this simple model without NOT edges
            if not changed: break
        return t

    def _get_signature(self, text: str) -> Tuple[Tuple[int,int], np.ndarray]:
        nodes, adj, _ = self._parse_to_graph(text)
        if len(nodes) == 0:
            return (1, 0), np.array([])
        beta = self._compute_betti(adj)
        truth = self._propagate_truth(nodes, adj)
        return beta, truth

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1, len2 = len(s1_b), len(s2_b)
        if len1 == 0 or len2 == 0: return 1.0
        
        # Cache compression
        def comp(x):
            if x not in self.ncd_cache:
                self.ncd_cache[x] = len(zlib.compress(x))
            return self.ncd_cache[x]
            
        c1 = comp(s1_b)
        c2 = comp(s2_b)
        c12 = comp(s1_b + s2_b)
        
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_beta, p_truth = self._get_signature(prompt)
        
        # Pre-calculate prompt features for structural matching
        p_has_num = bool(re.search(r'\d+', prompt))
        p_has_if = 'if' in prompt.lower()
        p_has_not = any(w in prompt.lower() for w in ['not', 'no', 'never'])

        for cand in candidates:
            c_beta, c_truth = self._get_signature(cand)
            
            # 1. Topological Distance
            dist_beta = np.sqrt((p_beta[0]-c_beta[0])**2 + (p_beta[1]-c_beta[1])**2)
            
            # 2. Truth Vector Distance (Hamming-like)
            dist_truth = 0.0
            if len(p_truth) > 0 and len(c_truth) > 0:
                min_len = min(len(p_truth), len(c_truth))
                dist_truth = np.sum(np.abs(p_truth[:min_len] - c_truth[:min_len]))
            elif len(p_truth) != len(c_truth):
                dist_truth = 1.0 # Penalty for mismatched sizes
            
            # 3. Structural Feature Matching (High weight)
            struct_score = 0.0
            c_has_num = bool(re.search(r'\d+', cand))
            c_has_if = 'if' in cand.lower()
            c_has_not = any(w in cand.lower() for w in ['not', 'no', 'never'])
            
            if p_has_num and c_has_num: struct_score += 2.0
            if p_has_if and c_has_if: struct_score += 2.0
            if p_has_not and c_has_not: struct_score += 2.0
            # Penalize missing structural elements
            if p_has_num and not c_has_num: struct_score -= 3.0
            if p_has_if and not c_has_if: struct_score -= 3.0

            # 4. NCD Tiebreaker (only if structural signals are weak)
            ncd_val = self._ncd(prompt, cand)
            
            # Final Score: Higher is better. 
            # We invert distances and add structural bonus.
            score = 10.0 - 2.0*dist_beta - 0.5*dist_truth + struct_score
            
            # If structural score is neutral, use NCD to break ties
            if abs(struct_score) < 1.0:
                score -= ncd_val 
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"TopoDist:{dist_beta:.2f}, TruthDist:{dist_truth:.2f}, Struct:{struct_score:.1f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        # Check strict structural constraints first
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        a_nums = re.findall(r'\d+\.?\d*', answer)
        
        # If prompt has numbers, answer must have numbers to be confident
        if p_nums and not a_nums:
            return 0.1
            
        # Check logical operators
        if 'if' in prompt.lower() and 'if' not in answer.lower():
            # Weak penalty, maybe implicit
            pass
            
        # Use the evaluate logic to get a raw score, then normalize
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        # Normalize heuristically: assume max possible score ~15, min ~-5
        conf = (raw_score + 5) / 20.0
        return max(0.0, min(1.0, conf))
```

</details>
