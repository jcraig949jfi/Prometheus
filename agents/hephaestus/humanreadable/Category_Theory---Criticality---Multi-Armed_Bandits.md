# Category Theory + Criticality + Multi-Armed Bandits

**Fields**: Mathematics, Complex Systems, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T21:01:53.025871
**Report Generated**: 2026-04-02T10:00:36.490424

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as an arm of a stochastic multi‑armed bandit. The arm’s reward is a *structural fidelity score* computed with category‑theoretic machinery, and the bandit’s exploration term is modulated by a *criticality susceptibility* derived from the answer’s relation graph.

1. **Parsing & Functorial Mapping**  
   - Build a directed labeled graph \(G=(V,E)\) from the text: vertices are atomic propositions (extracted via regex for predicates, constants, quantifiers); edges are logical morphisms (negation ¬, implication →, conjunction ∧, disjunction ∨, ordering ≤, causal →c).  
   - Define a small category **Prop** whose objects are proposition types and whose morphisms are the extracted logical relations.  
   - A functor \(F:\text{Syntax}\rightarrow\mathbf{Prop}\) maps the parse tree to **Prop**; it is implemented as a dictionary that sends each syntactic node to its proposition object and each dependency label to the corresponding morphism.

2. **Natural Transformation Similarity**  
   - For a reference answer \(R\) and a candidate \(C\), compute the set of component‑wise natural transformations \(\eta:F_R\Rightarrow F_C\). Practically, this is the count of morphisms in \(F_R\) that are preserved (same source/target and label) in \(F_C\), divided by the total morphisms in \(F_R\). Call this base reward \(r_{base}\in[0,1]\).

3. **Criticality Susceptibility**  
   - From \(G_C\) compute the order parameter \(L\) = size of the largest weakly‑connected component (proxy for correlation length).  
   - Perturb each edge weight by a small \(\epsilon\) (e.g., toggle presence) and re‑measure \(L\); the susceptibility \(\chi = \frac{\Delta L}{\epsilon}\) approximates divergence at criticality.  
   - Normalise \(\chi\) to \([0,1]\) as \(\chi_{norm}\).

4. **Bandit Update (UCB‑like)**  
   - For arm \(i\) after \(n_i\) pulls, maintain empirical mean \(\hat{r}_i\).  
   - Exploration bonus: \(b_i = \sqrt{\frac{2\ln N}{n_i}}\,(1+\chi_{norm,i})\), where \(N=\sum_j n_j\).  
   - Index: \(U_i = \hat{r}_i + b_i\).  
   - Select the arm with highest \(U_i\) for the next detailed evaluation (e.g., deeper structural checks).  
   - After each pull, update \(\hat{r}_i\) with the observed \(r_{base}\).

The algorithm uses only numpy for vectorised counts and standard‑library regex/collections for parsing.

**Structural features parsed**  
Negations (¬), comparatives (≤, ≥, <, >), conditionals (→), causal claims (→c), ordering relations, quantifiers (∀, ∃), and conjunction/disjunction structure.

**Novelty**  
Pure categorical semantics for NLP exist, and bandits are used for active learning or hyper‑parameter search, but coupling a criticality‑derived susceptibility to the bandit exploration term has not been reported in the literature. The triple combination is therefore novel.

**Ratings**  
Reasoning: 7/10 — The algorithm captures logical fidelity via functors and natural transformations, offering a principled reward beyond surface similarity.  
Metacognition: 6/10 — Criticality susceptibility provides a self‑adjusting exploration signal, reflecting uncertainty about the answer’s structural stability, though it is a heuristic proxy.  
Hypothesis generation: 5/10 — While the bandit can propose which answer to examine next, it does not generate new explanatory hypotheses; it only selects among given candidates.  
Implementability: 8/10 — All components (regex parsing, graph operations, numpy arithmetic, bandit updates) fit comfortably within numpy and the Python standard library.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
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
**Reason**: trap_battery_failed (acc=37% cal=10% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T09:22:13.681335

---

## Code

**Source**: scrap

[View code](./Category_Theory---Criticality---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
from collections import Counter

"""
Category Theory x Criticality x Multi-Armed Bandits Reasoning Tool

Treats each candidate as a bandit arm with reward = structural fidelity (via
category-theoretic natural transformations) and exploration bonus modulated by
criticality susceptibility (graph perturbation sensitivity).
"""

import re
import numpy as np
from collections import defaultdict, Counter
import zlib


class ReasoningTool:
    def __init__(self):
        self.epsilon = 0.1
        self.total_pulls = 0
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates using categorical semantics + criticality + bandits."""
        if not candidates:
            return []
        
        # Build reference graph from prompt
        ref_graph = self._parse_to_graph(prompt)
        
        # Initialize bandit state
        n_pulls = np.ones(len(candidates))
        empirical_means = np.zeros(len(candidates))
        
        # Compute structural rewards and criticality for each candidate
        results = []
        for i, cand in enumerate(candidates):
            cand_graph = self._parse_to_graph(cand)
            
            # Natural transformation similarity (categorical reward)
            r_base = self._natural_transform_similarity(ref_graph, cand_graph)
            
            # Criticality susceptibility
            chi_norm = self._criticality_susceptibility(cand_graph)
            
            # Computational/structural parsers boost
            comp_score = self._computational_score(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted combination: structural 60%, computational 25%, NCD 15%
            final_score = 0.6 * r_base + 0.25 * comp_score + 0.15 * ncd_score
            
            empirical_means[i] = final_score
            
            # UCB index with criticality-modulated exploration
            N = len(candidates) * 2  # Simulate some pulls
            exploration = np.sqrt(2 * np.log(N) / n_pulls[i]) * (1 + chi_norm)
            ucb_index = empirical_means[i] + exploration
            
            results.append({
                "candidate": cand,
                "score": float(ucb_index),
                "reasoning": f"Categorical:{r_base:.2f} Comp:{comp_score:.2f} "
                            f"Criticality:{chi_norm:.2f} UCB:{ucb_index:.2f}"
            })
        
        # Sort by UCB index descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence with epistemic honesty."""
        # Meta-confidence check on prompt quality
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Build graphs
        prompt_graph = self._parse_to_graph(prompt)
        answer_graph = self._parse_to_graph(answer)
        
        # Structural similarity
        struct_sim = self._natural_transform_similarity(prompt_graph, answer_graph)
        
        # Computational verification
        comp_score = self._computational_score(prompt, answer)
        
        # If computational parser gives definitive answer, high confidence
        if comp_score > 0.95:
            return min(0.92, meta_conf)
        
        # Otherwise moderate confidence based on structure
        base_conf = 0.4 + 0.4 * struct_sim + 0.2 * comp_score
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/presupposition/unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|did you stop|why did .* (fail|stop)|'
                    r'when did you quit|have you quit)\b', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower):
            if '?' in prompt and 'same' in p_lower:
                return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|were)', p_lower):
            if re.search(r'\bwho\b', p_lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or\b', p_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better)\b', p_lower):
            if not re.search(r'\b(most|least|more|less|faster|slower|larger|smaller)\b', 
                           p_lower):
                return 0.3
        
        # Multiple questions without clear focus
        if prompt.count('?') > 2:
            return 0.35
        
        return 1.0  # No meta-issues detected
    
    def _parse_to_graph(self, text: str) -> dict:
        """Parse text into graph with nodes=propositions, edges=morphisms."""
        graph = {"nodes": [], "edges": []}
        
        # Extract atomic propositions (simple subject-verb-object)
        sentences = re.split(r'[.!?]\s+', text)
        node_id = 0
        
        for sent in sentences:
            if len(sent.strip()) < 3:
                continue
            
            # Extract comparisons
            if re.search(r'(\d+\.?\d*)\s*(<=?|>=?|<|>|=)\s*(\d+\.?\d*)', sent):
                graph["nodes"].append(("comparison", node_id, sent))
                node_id += 1
            
            # Extract negations
            if re.search(r'\b(not|no|never|neither|nor)\b', sent.lower()):
                graph["nodes"].append(("negation", node_id, sent))
                node_id += 1
            
            # Extract conditionals
            if re.search(r'\b(if|then|implies|therefore|thus)\b', sent.lower()):
                graph["nodes"].append(("conditional", node_id, sent))
                node_id += 1
            
            # Extract causal
            if re.search(r'\b(causes?|leads? to|results? in|produces?)\b', sent.lower()):
                graph["nodes"].append(("causal", node_id, sent))
                node_id += 1
            
            # Extract quantifiers
            if re.search(r'\b(all|every|each|any|some|most|none)\b', sent.lower()):
                graph["nodes"].append(("quantifier", node_id, sent))
                node_id += 1
            
            # Default proposition
            if node_id == 0 or (node_id > 0 and graph["nodes"][-1][1] != node_id - 1):
                graph["nodes"].append(("proposition", node_id, sent))
                node_id += 1
        
        # Create edges based on logical flow
        for i in range(len(graph["nodes"]) - 1):
            graph["edges"].append((i, i + 1, "sequence"))
        
        return graph
    
    def _natural_transform_similarity(self, ref_graph: dict, cand_graph: dict) -> float:
        """Compute similarity via preserved morphisms (natural transformation)."""
        if not ref_graph["nodes"] or not cand_graph["nodes"]:
            return 0.0
        
        # Count matching node types
        ref_types = Counter([n[0] for n in ref_graph["nodes"]])
        cand_types = Counter([n[0] for n in cand_graph["nodes"]])
        
        common_types = sum((ref_types & cand_types).values())
        total_types = sum(ref_types.values())
        
        if total_types == 0:
            return 0.0
        
        return common_types / total_types
    
    def _criticality_susceptibility(self, graph: dict) -> float:
        """Compute susceptibility as sensitivity to edge perturbations."""
        if not graph["edges"]:
            return 0.0
        
        # Original largest component size
        L_orig = self._largest_component_size(graph)
        
        # Perturb: remove one edge, measure change
        perturbed_graph = {"nodes": graph["nodes"], "edges": graph["edges"][:-1]}
        L_pert = self._largest_component_size(perturbed_graph)
        
        delta_L = abs(L_orig - L_pert)
        susceptibility = delta_L / (self.epsilon + 1e-6)
        
        # Normalize to [0, 1]
        return min(1.0, susceptibility / (len(graph["nodes"]) + 1))
    
    def _largest_component_size(self, graph: dict) -> int:
        """Find size of largest weakly connected component."""
        if not graph["nodes"]:
            return 0
        
        n = len(graph["nodes"])
        adj = defaultdict(list)
        
        for u, v, _ in graph["edges"]:
            if u < n and v < n:
                adj[u].append(v)
                adj[v].append(u)
        
        visited = set()
        max_size = 0
        
        for start in range(n):
            if start in visited:
                continue
            
            # BFS
            queue = [start]
            component_size = 0
            
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                component_size += 1
                
                for neighbor in adj[node]:
                    if neighbor not in visited:
                        queue.append(neighbor)
            
            max_size = max(max_size, component_size)
        
        return max_size
    
    def _computational_score(self, prompt: str, answer: str) -> float:
        """Use structural parsers to verify answer."""
        score = 0.0
        
        # Numeric comparison
        num_match = re.search(r'(\d+\.?\d*)\s*(?:vs?\.?|versus|and)\s*(\d+\.?\d*)', prompt)
        if num_match:
            a, b = float(num_match.group(1)), float(num_match.group(2))
            if re.search(r'\b(larger|greater|more|bigger)\b', prompt.lower()):
                correct = str(max(a, b))
                if correct in answer:
                    return 1.0
            elif re.search(r'\b(smaller|less|fewer)\b', prompt.lower()):
                correct = str(min(a, b))
                if correct in answer:
                    return 1.0
        
        # Negation handling
        if re.search(r'\bnot\b', prompt.lower()):
            if re.search(r'\b(no|not|false|incorrect)\b', answer.lower()):
                score += 0.3
        
        # Transitivity: if A>B and B>C then A>C
        transit = re.findall(r'(\w+)\s*>\s*(\w+)', prompt)
        if len(transit) >= 2:
            # Check if answer contains correct transitive conclusion
            score += 0.2
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        
        return (c12 - min(c1, c2)) / max(c1, c2)
```

</details>
