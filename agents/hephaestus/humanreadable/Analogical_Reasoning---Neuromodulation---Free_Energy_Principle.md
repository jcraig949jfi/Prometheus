# Analogical Reasoning + Neuromodulation + Free Energy Principle

**Fields**: Cognitive Science, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:08:45.156744
**Report Generated**: 2026-03-27T06:37:38.904295

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Graph construction** – Each sentence (question or candidate answer) is turned into a directed, labeled graph G = (V, E). Nodes V are noun phrases or predicates extracted via regex patterns (e.g., `(\b\w+\b)\s+is\s+greater\s+than\s+(\b\w+\b)` → edge type *comparative*). Edge types encoded as one‑hot vectors: {causal, conditional, comparative, negation, ordering, temporal}. The adjacency matrix A ∈ ℝ^{|V|×|V|×K} stores presence/strength for each K edge type.  
2. **Neuromodulatory gain** – From the same regex pass we detect modality cues:  
   * dopamine‑like gain g_D = 1 + α·[presence of “likely”, “possibly”, “may”]  
   * serotonin‑like gain g_S = 1 − β·[presence of “not”, “never”, “cannot”]  
   Edge weights are multiplied: A' = A ⊙ (g_D ⊕ g_S) (⊙ element‑wise, ⊕ broadcasts gains per edge type).  
3. **Analogical mapping (structure mapping)** – We seek a node permutation π that maximizes relational overlap between question graph Q and candidate graph C:  
   Score_map(π) = ∑_{i,j,k} Q'_{i,j,k} · C'_{π(i),π(j),k}  
   This is a quadratic assignment problem; for |V| ≤ 8 we solve it exactly via brute‑force enumeration using numpy permutations, otherwise we use a greedy hill‑climb that swaps nodes to increase Score_map.  
4. **Free‑energy principle scoring** – Treat the prior over mappings P(π) as uniform; the likelihood L(C|Q,π) ∝ exp(− E_pred) where prediction error E_pred = ‖Q' − π·C'·πᵀ‖_F² (Frobenius norm). Variational free energy F = E_pred − H[Q(π)] with entropy H ≈ log |Π| (number of permutations explored). Final answer score = −F (lower free energy → higher score). All operations use only numpy and itertools; no external libraries.

**Structural features parsed** – Negations (“not”, “never”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), causal claims (“causes”, “leads to”), ordering/temporal relations (“before”, “after”, “first”), modal adjectives (“possibly”, “likely”), and conjunctions that bind propositions.

**Novelty** – The combination is not found in existing reasoners. Analogical mapping (e.g., Structure Mapping Engine) is separate from Bayesian prediction‑error frameworks; neuromodulatory gain weighting of edges based on lexical cues has not been integrated into a free‑energy minimization loop for text scoring.

**Ratings**  
Reasoning: 8/10 — captures relational structure and aligns it via principled mapping, though limited to hand‑crafted regex patterns.  
Metacognition: 6/10 — provides a scalar free‑energy estimate but lacks explicit self‑monitoring or uncertainty calibration.  
Hypothesis generation: 7/10 — generates multiple node permutations as candidate mappings, enabling hypothesis exploration.  
Implementability: 9/10 — relies solely on numpy, itertools, and basic regex; easily portable and fast for small graphs.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Neuromodulation**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Analogical Reasoning + Free Energy Principle: strong positive synergy (+0.320). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Neuromodulation: negative interaction (-0.103). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: ValueError: Improper number of dimensions to norm.

**Forge Timestamp**: 2026-03-26T06:42:01.565469

---

## Code

**Source**: scrap

[View code](./Analogical_Reasoning---Neuromodulation---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from itertools import permutations
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements Analogical Reasoning via Free Energy Minimization with Neuromodulatory Gain.
    
    Mechanism:
    1. Parsing: Converts text to directed graphs (nodes=concepts, edges=relations).
       Supports: causal, conditional, comparative, negation, ordering, temporal.
    2. Neuromodulation: Adjusts edge weights based on modality cues.
       - Dopamine (g_D): Boosts 'likely', 'possibly'.
       - Serotonin (g_S): Suppresses 'not', 'never'.
    3. Analogical Mapping: Finds node permutation pi maximizing relational overlap between 
       Question graph and Candidate graph (Structure Mapping).
    4. Free Energy Scoring: Scores candidates by minimizing prediction error (Frobenius norm)
       between mapped candidate graph and question graph, penalized by mapping entropy.
    """
    
    # Edge types for one-hot encoding
    EDGE_TYPES = ['causal', 'conditional', 'comparative', 'negation', 'ordering', 'temporal']
    TYPE_MAP = {t: i for i, t in enumerate(EDGE_TYPES)}
    
    # Regex patterns for extraction
    PATTERNS = {
        'causal': [r'\b(causes|leads to|results in|creates)\b'],
        'conditional': [r'\b(if|unless|then|otherwise)\b'],
        'comparative': [r'\b(greater than|less than|more than|bigger than|smaller than)\b', r'\b(\w+)\s+is\s+(greater|less)\s+than\s+(\w+)'],
        'negation': [r'\b(not|never|cannot|no)\b'],
        'ordering': [r'\b(before|after|first|last|next)\b'],
        'temporal': [r'\b(when|while|during|until)\b']
    }
    
    MODALITY_POSITIVE = ['likely', 'possibly', 'may', 'might', 'could']
    MODALITY_NEGATIVE = ['not', 'never', 'cannot', 'impossible']

    def __init__(self):
        pass

    def _extract_nodes(self, text: str) -> List[str]:
        """Extract noun phrases or key tokens as nodes."""
        # Simple extraction: capitalized words, quoted strings, or specific nouns
        # Fallback to splitting by common delimiters if no complex NLP
        clean_text = re.sub(r'[^\w\s]', ' ', text)
        words = [w for w in clean_text.split() if len(w) > 2]
        # Deduplicate while preserving order
        seen = set()
        nodes = []
        for w in words:
            if w.lower() not in seen:
                seen.add(w.lower())
                nodes.append(w)
        return nodes if nodes else ['entity']

    def _build_graph(self, text: str) -> Tuple[List[str], np.ndarray]:
        """Parse text into nodes and adjacency tensor A [N, N, K]."""
        nodes = self._extract_nodes(text)
        n = len(nodes)
        if n == 0:
            return [], np.zeros((0, 0, len(self.EDGE_TYPES)))
            
        A = np.zeros((n, n, len(self.EDGE_TYPES)))
        text_lower = text.lower()
        
        # Detect global modality gains
        g_d = 1.0 + 0.5 * any(m in text_lower for m in self.MODALITY_POSITIVE)
        g_s = 1.0 - 0.5 * any(m in text_lower for m in self.MODALITY_NEGATIVE)
        
        # Apply gains per edge type logic (simplified broadcast)
        # We apply gains during edge weight assignment
        
        for rel_type, patterns in self.PATTERNS.items():
            idx = self.TYPE_MAP[rel_type]
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # If relation exists, connect relevant nodes heuristically
                    # Since we don't have full dependency parse, we assume dense connectivity 
                    # for detected relations in small graphs, weighted by presence
                    for i, n1 in enumerate(nodes):
                        for j, n2 in enumerate(nodes):
                            if i != j:
                                # Heuristic: if words appear near the pattern, strengthen link
                                # For robustness in this constrained env, we mark existence
                                weight = 1.0
                                if rel_type == 'negation':
                                    weight *= g_s
                                else:
                                    weight *= g_d
                                A[i, j, idx] = weight
                                
        return nodes, A

    def _compute_free_energy(self, Q_nodes: List[str], Q_adj: np.ndarray, 
                             C_nodes: List[str], C_adj: np.ndarray) -> float:
        """
        Compute Free Energy F = E_pred - H.
        E_pred: Prediction error (Frobenius norm of difference after mapping).
        H: Entropy approximation (log of permutations explored).
        """
        if Q_adj.size == 0 or C_adj.size == 0:
            return 100.0 # High energy for empty graphs
            
        n_q, n_c = len(Q_nodes), len(C_nodes)
        if n_q == 0 or n_c == 0:
            return 100.0

        # Pad smaller graph to match size for permutation (dummy nodes)
        size = max(n_q, n_c)
        
        def pad_graph(adj, target_size):
            n = adj.shape[0]
            if n >= target_size:
                return adj[:target_size, :target_size, :]
            new_adj = np.zeros((target_size, target_size, adj.shape[2]))
            new_adj[:n, :n, :] = adj
            return new_adj

        Q_pad = pad_graph(Q_adj, size)
        C_pad = pad_graph(C_adj, size)
        
        best_score = -np.inf
        perms_explored = 0
        
        # Limit permutations for complexity (brute force up to 8, else sample)
        limit = 8
        indices = list(range(size))
        
        if size <= limit:
            perm_iter = permutations(indices)
        else:
            # Greish hill climb or random sample for large graphs
            # Using a fixed set of shifts for determinism and speed
            perm_iter = []
            base = list(range(size))
            for k in range(20): # 20 random restarts
                shift = (k * 3) % size
                p = base[shift:] + base[:shift]
                perm_iter.append(tuple(p))

        for p in perm_iter:
            perms_explored += 1
            # Permute C_adj according to p
            # new_C[i, j] = old_C[p[i], p[j]]
            permuted_C = C_pad[np.ix_(p, p, range(C_pad.shape[2]))]
            
            # Prediction Error: Frobenius norm of difference
            diff = Q_pad - permuted_C
            E_pred = np.linalg.norm(diff, 'fro')
            
            # We want to maximize overlap (minimize error). 
            # Score = -Error (since we want max score)
            if E_pred < 1e-9: # Exact match bonus
                current_score = 1000.0 - E_pred
            else:
                current_score = -E_pred
                
            if current_score > best_score:
                best_score = current_score

        # Entropy term: log(|Pi|) - approximated by log(perms_explored)
        # Since we want to minimize F = E - H, and we return -F as score:
        # Score = H - E_pred
        H = np.log(max(1, perms_explored))
        free_energy = E_pred - H 
        return -free_energy # Higher is better

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Direct structural parsing score to ensure we beat NCD baseline.
        Checks for constraint satisfaction (negations, comparatives).
        """
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation consistency
        negations = ['not', 'never', 'no', 'cannot']
        p_neg = any(n in p_low for n in negations)
        c_neg = any(n in c_low for n in negations)
        if p_neg == c_neg:
            score += 2.0
        else:
            score -= 2.0 # Penalty for flipping negation
            
        # 2. Comparative consistency (heuristic)
        comps = ['greater', 'less', 'more', 'bigger', 'smaller']
        p_has_comp = any(c in p_low for c in comps)
        c_has_comp = any(c in c_low for c in comps)
        if p_has_comp and c_has_comp:
            score += 1.5
        elif p_has_comp and not c_has_comp:
            score -= 1.0
            
        # 3. Numeric evaluation (if present)
        nums_p = re.findall(r'\d+\.?\d*', p_low)
        nums_c = re.findall(r'\d+\.?\d*', c_low)
        if nums_p and nums_c:
            # Simple presence check, deeper logic requires context
            score += 1.0
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        q_nodes, q_adj = self._build_graph(prompt)
        
        for cand in candidates:
            c_nodes, c_adj = self._build_graph(cand)
            
            # 1. Structural Score (Primary signal for robustness)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Analogical/Free Energy Score
            fe_score = self._compute_free_energy(q_nodes, q_adj, c_nodes, c_adj)
            
            # Combine: Weight structural heavily to beat baseline, FE for nuance
            # Normalization: FE can be large negative, struct is small positive
            total_score = (struct_score * 10.0) + (fe_score * 0.5)
            
            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": f"Structural:{struct_score:.2f} FE:{fe_score:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on relative ranking."""
        # Evaluate against a dummy wrong answer to gauge separation
        # Or simply use the structural score mapped to 0-1
        struct = self._structural_score(prompt, answer)
        # Map structural score (approx -4 to +4) to 0-1
        conf = 1.0 / (1.0 + np.exp(-struct)) # Sigmoid
        return float(np.clip(conf, 0.01, 0.99))
```

</details>
