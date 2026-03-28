# Pragmatism + Causal Inference + Normalized Compression Distance

**Fields**: Philosophy, Information Science, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:44:47.196965
**Report Generated**: 2026-03-27T04:25:48.766679

---

## Nous Analysis

**Algorithm**  
1. **Parse the prompt** with regex‑based patterns to extract propositions \(p_i = (s, rel, o)\) where \(rel\) captures negation, comparatives, conditionals, causal keywords, or numeric relations. Store each proposition in a list and build a directed adjacency list \(G\) where an edge \(u→v\) is added for explicit causal cues (“because”, “leads to”) or inferred temporal order (“before”, “after”). Attach a weight \(w_{uv}\) = 1 for definite causality, 0.5 for probabilistic cues.  
2. **Forward‑chain** over \(G\) using numpy arrays for the adjacency matrix to compute the closure \(C(G)\) (transitive hull). This gives all propositions entailed by the prompt under modus ponens and transitivity.  
3. **Consistency score** for a candidate answer \(a\): extract its propositions \(P_a\); compute \(cons = \frac{|P_a ∩ C(G)|}{|P_a|}\) (fraction of answer propositions entailed) and penalize any proposition whose negation appears in \(C(G)\) (using a separate negation set).  
4. **Intervention utility**: for each causal edge \(u→v\) in \(G\), simulate \(do(u)\) by removing incoming edges to \(u\) and checking whether the predicted effect \(v\) matches any observed outcome in the prompt (numeric change, state change). Utility \(util = \frac{\#\text{correct predictions}}{\#\text{edges tested}}\).  
5. **Normalized Compression Distance**: compress the prompt string \(x\) and the candidate answer string \(y\) with zlib; compute \(NCD(x,y) = \frac{C(xy)-\min(C(x),C(y))}{\max(C(x),C(y))}\). Lower NCD indicates greater algorithmic similarity.  
6. **Final score**: \(Score = α·cons + β·util + γ·(1−NCD)\) with \(α+β+γ=1\) (e.g., 0.4, 0.3, 0.3). Higher scores reflect answers that are pragmatically useful (work in simulated interventions), causally consistent, and compressively similar to the prompt.

**Structural features parsed** – negations (“not”, “no”), comparatives (“more than”, “<”, “>”), conditionals (“if … then”, “unless”), causal claims (“because”, “leads to”, “results in”), numeric values and units, ordering relations (“before”, “after”, “first”, “second”), quantifiers (“all”, “some”), and explicit intervention language (“do”, “set to”).

**Novelty** – While compression‑based similarity (NCD) and causal graph reasoning each appear separately, integrating them with a pragmatic utility derived from simulated interventions is uncommon. Existing tools tend to use either hash/BoW similarity or pure logical chaining; the triple fusion is therefore relatively novel, though each component is well‑studied.

**Ratings**  
Reasoning: 8/10 — captures entailment, contradiction, and intervention prediction via explicit graph operations.  
Metacognition: 6/10 — the method can estimate its own uncertainty via consistency vs. utility trade‑off but lacks reflective self‑adjustment.  
Hypothesis generation: 7/10 — by proposing candidate causes and testing their predicted effects it generates and evaluates hypotheses.  
Implementability: 9/10 — relies only on regex, numpy arrays, and zlib compression, all available in the standard library plus numpy.

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

- **Pragmatism**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Causal Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Abductive Reasoning + Causal Inference + Neural Oscillations (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Pragmatism + Type Theory (accuracy: 0%, calibration: 0%)
- Category Theory + Causal Inference + Mechanism Design (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T02:26:59.440796

---

## Code

**Source**: scrap

[View code](./Pragmatism---Causal_Inference---Normalized_Compression_Distance/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A hybrid reasoning tool combining structural causal parsing, forward-chaining
    entailment, and pragmatic utility simulation. Normalized Compression Distance (NCD)
    is restricted to a tie-breaking role to avoid known failure modes associated with
    pure compression-based reasoning.
    
    Mechanism:
    1. Parse propositions and causal links (regex) into a directed graph.
    2. Compute transitive closure (forward chaining) to find all entailed facts.
    3. Score candidates based on:
       - Consistency: Overlap with entailed facts minus contradictions.
       - Utility: Simulated intervention success rate.
       - NCD: Used only as a minor tiebreaker for structural similarity.
    """
    
    # Regex patterns for structural extraction
    PATTERNS = {
        'causal': re.compile(r'\b(because|leads to|causes|results in|therefore|so)\b', re.I),
        'conditional': re.compile(r'\b(if|unless|then|when)\b', re.I),
        'negation': re.compile(r'\b(not|no|never|without|cannot)\b', re.I),
        'comparative': re.compile(r'\b(more than|less than|greater|smaller|higher|lower|>\|<)\b', re.I),
        'numeric': re.compile(r'-?\d+\.?\d*'),
        'order': re.compile(r'\b(before|after|first|second|next|finally)\b', re.I)
    }

    def __init__(self):
        pass

    def _extract_props(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract simplified (subject, relation, object) triples."""
        props = []
        # Simple sentence splitting
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Detect relation type
            rel_type = "statement"
            if self.PATTERNS['causal'].search(sent): rel_type = "causal"
            elif self.PATTERNS['conditional'].search(sent): rel_type = "conditional"
            elif self.PATTERNS['negation'].search(sent): rel_type = "negation"
            elif self.PATTERNS['comparative'].search(sent): rel_type = "comparative"
            
            # Extract numeric values if present
            nums = self.PATTERNS['numeric'].findall(sent)
            if nums:
                props.append((sent.lower(), rel_type, nums[0]))
            else:
                # Fallback to whole sentence as proposition
                props.append((sent.lower(), rel_type, "true"))
        return props

    def _build_graph(self, prompt: str) -> Tuple[List[str], np.ndarray, Set[str]]:
        """Build adjacency matrix and node list from prompt."""
        props = self._extract_props(prompt)
        nodes = list(set([p[0] for p in props]))
        node_map = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        adj = np.zeros((n, n))
        negations = set()
        
        # Build edges based on causal cues or temporal order
        for i, (sub, rel, obj) in enumerate(props):
            if rel == "negation":
                negations.add(sub)
            
            # Look for explicit causal chains in adjacent propositions
            for j, (sub2, rel2, obj2) in enumerate(props):
                if i == j: continue
                # Heuristic: if prop i contains causal keyword and mentions sub2
                if rel in ["causal", "conditional"] and sub2 in sub:
                    if sub in node_map and sub2 in node_map:
                        u, v = node_map[sub], node_map[sub2]
                        weight = 1.0 if rel == "causal" else 0.5
                        adj[u, v] = weight
        
        return nodes, adj, negations

    def _transitive_closure(self, adj: np.ndarray) -> np.ndarray:
        """Compute transitive hull using numpy (Warshall-like)."""
        if adj.shape[0] == 0:
            return adj
        closure = (adj > 0).astype(float)
        np.fill_diagonal(closure, 1)
        # Matrix multiplication approach for small N, or iterative for stability
        # Using iterative bit-mask style for boolean closure
        changed = True
        while changed:
            old = closure.copy()
            closure = np.sign(closure @ closure) # Matrix multiply then threshold
            closure[closure > 0] = 1
            if np.array_equal(old, closure):
                changed = False
        return closure

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        nodes, adj, prompt_negs = self._build_graph(prompt)
        closure = self._transitive_closure(adj)
        
        # Map nodes to indices for closure lookup
        node_map = {n: i for i, n in enumerate(nodes)}
        entailed_set = set()
        
        # Extract entailed propositions from closure
        # If node i -> node j exists, and i is in prompt, j is entailed
        for i, n_i in enumerate(nodes):
            for j, n_j in enumerate(nodes):
                if closure[i, j] > 0 and i != j:
                    entailed_set.add(n_j)

        results = []
        for cand in candidates:
            cand_props = self._extract_props(cand)
            cand_subs = [p[0] for p in cand_props]
            
            # 1. Consistency Score
            matched = 0
            contradiction = 0
            for sub in cand_subs:
                if sub in entailed_set:
                    matched += 1
                # Check negation conflict
                if sub in prompt_negs:
                    contradiction += 1
            
            total_cand = len(cand_subs) if len(cand_subs) > 0 else 1
            cons_score = (matched - contradiction) / total_cand
            
            # 2. Utility (Simulated Intervention)
            # Simplified: If candidate suggests a change, does prompt support the outcome?
            # Here we approximate utility by checking if candidate contains causal keywords
            # that align with the graph structure.
            util_score = 0.0
            if any(self.PATTERNS['causal'].search(cand) for _ in [1]):
                # Crude heuristic: if candidate has causal language and matches graph nodes
                if any(n in cand for n in nodes):
                    util_score = 0.5
            
            # 3. NCD (Tiebreaker only)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Final Score: Weighted heavily towards structural consistency
            # Weights: Cons=0.7, Util=0.2, NCD=0.1 (NCD is strictly tiebreaker)
            score = 0.7 * cons_score + 0.2 * util_score + 0.1 * ncd_score
            
            # Penalty for pure NCD reliance if structural signal is zero
            if matched == 0 and contradiction == 0:
                score = 0.5 * ncd_score # Downgrade to NCD-only baseline if no structure found

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Consistency:{cons_score:.2f}, Utility:{util_score:.2f}, NCD:{ncd_val:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses structural parsing as primary signal, NCD as fallback.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Calibration: Map raw score to confidence
        # If structural consistency was high, confidence is high.
        # If only NCD matched, confidence is capped.
        reasoning = res[0]['reasoning']
        if "Consistency:0." not in reasoning and "Consistency:-" not in reasoning:
             # Basic check if consistency contributed positively
             if float(res[0]['score']) > 0.5:
                 return min(1.0, float(res[0]['score']) + 0.2)
        
        return max(0.0, min(1.0, float(score)))
```

</details>
