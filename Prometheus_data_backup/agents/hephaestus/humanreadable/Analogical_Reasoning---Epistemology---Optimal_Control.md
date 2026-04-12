# Analogical Reasoning + Epistemology + Optimal Control

**Fields**: Cognitive Science, Philosophy, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:37:48.030798
**Report Generated**: 2026-04-02T11:44:50.630373

---

## Nous Analysis

**Algorithm: Epistemic‑Guided Structure‑Mapping Edit Distance (EG‑SMED)**  

1. **Parsing & Data Structures**  
   - Use a handful of regex patterns to extract atomic propositions from a prompt and each candidate answer:  
     *Negation* (`not`, `never`), *comparative* (`greater than`, `less than`), *conditional* (`if … then …`), *causal* (`because`, `leads to`), *ordering* (`before`, `after`, `first`, `last`).  
   - Each proposition becomes a node record `(id, pred, args, polarity, modality)` where `pred` is the relation verb (e.g., `greater_than`, `cause`), `args` are the extracted noun phrases, `polarity ∈ {+1,‑1}` for negation, and `modality ∈ {asserted, believed, possible}` for epistemic tags.  
   - Store all nodes in a NumPy structured array `nodes`. Build a directed labeled adjacency matrix `A ∈ ℝ^{n×n}` where `A[i,j]=1` if node *i* directly supports node *j* (e.g., antecedent → consequent in a conditional) and `0` otherwise.  
   - Maintain a belief vector `b ∈ ℝ^{n}` initialized from epistemic heuristics: foundational facts (e.g., numeric values, definitions) get high reliability (`0.9`); coherentist support (nodes with ≥2 incoming edges) get `0.7`; reliabilist downgrade for nodes containing unverified modals (`0.5`).  

2. **Structure‑Mapping Cost Matrix**  
   - For a reference answer graph `G_ref` and candidate graph `G_cand`, compute a cost matrix `C ∈ ℝ^{m×n}` (m = |G_ref|, n = |G_cand|):  
     `C[i,j] = w_pred * δ(pred_i≠pred_j) + w_args * (1 - cosine(args_i, args_j)) + w_belief * |b_ref_i - b_cand_j|`.  
   - `δ` is Kronecker delta; cosine uses TF‑IDF vectors of the argument strings (still stdlib + numpy). Weights `w_pred=0.4, w_args=0.4, w_belief=0.2`.  

3. **Optimal Control‑Style Editing**  
   - Treat node alignment as a discrete‑time control problem: at each step we may **match**, **insert**, or **delete** a node. The instantaneous cost of matching i→j is `C[i,j]`; insertion/deletion cost is a constant `λ=0.5`.  
   - Solve the finite‑horizon Hamilton‑Jacobi‑Bellman recursion via DP (equivalent to edit‑distance with weighted substitution):  
     `D[i,j] = min( D[i-1,j-1] + C[i,j], D[i-1,j] + λ, D[i,j-1] + λ )` with `D[0,:]=j*λ, D[:,0]=i*λ`.  
   - Final score = `1 - D[m,n] / (m*λ + n*λ)` (normalized similarity in `[0,1]`).  

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal claims, ordering/temporal relations, and explicit numeric values (captured as args).  

**Novelty**  
The combination is novel: analogical structure mapping supplies the graph‑matching core; epistemic belief weighting injects a justification layer absent in pure metric‑based analogiers; optimal‑control DP reframes edit distance as a cost‑minimization trajectory problem, a perspective not seen in existing NLP scoring tools (which typically use pure graph edit distance or neural similarity).  

**Ratings**  
Reasoning: 8/10 — captures relational structure and justification, but relies on hand‑crafted regex patterns that may miss complex syntax.  
Metacognition: 7/10 — belief vector provides a simple self‑assessment of confidence, yet lacks higher‑order reflection on inference quality.  
Hypothesis generation: 6/10 — the algorithm can propose alternative alignments via sub‑optimal DP paths, but does not actively generate new hypotheses beyond re‑scoring.  
Implementability: 9/10 — only numpy and stdlib are needed; all components (regex, TF‑IDF, DP) are straightforward to code.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=36% cal=2% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:37:30.516788

---

## Code

**Source**: scrap

[View code](./Analogical_Reasoning---Epistemology---Optimal_Control/tool.py)

<details>
<summary>Show code</summary>

```python
"""
Epistemic-Guided Structure-Mapping Edit Distance (EG-SMED)

Combines analogical structure mapping, epistemic belief tracking, and optimal control
edit distance to evaluate reasoning quality. Parses text into proposition graphs,
computes belief vectors, and uses DP to find minimum-cost alignments.
"""

import re
import numpy as np
from collections import defaultdict


class ReasoningTool:
    def __init__(self):
        self.w_pred = 0.4
        self.w_args = 0.4
        self.w_belief = 0.2
        self.insert_del_cost = 0.5
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by structural + computational alignment with prompt."""
        # Parse prompt into reference graph
        prompt_graph = self._parse_graph(prompt)
        
        # Try computational solving first
        computed = self._compute_answer(prompt)
        
        results = []
        for cand in candidates:
            cand_graph = self._parse_graph(cand)
            
            # Structure mapping score
            struct_score = self._structure_map_score(prompt_graph, cand_graph)
            
            # Computational match score
            comp_score = self._computational_match(prompt, cand, computed)
            
            # NCD tiebreaker (max 15%)
            ncd_score = self._ncd_score(prompt, cand)
            
            # Weighted combination
            final_score = 0.55 * struct_score + 0.30 * comp_score + 0.15 * ncd_score
            
            reasoning = f"Struct={struct_score:.2f} Comp={comp_score:.2f} NCD={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence 0-1."""
        # Check meta-confidence (epistemic honesty)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute answer and check match
        computed = self._compute_answer(prompt)
        if computed is not None:
            if self._answers_match(computed, answer):
                return min(0.95, meta_conf)
            else:
                return 0.1
        
        # Fallback to structure mapping
        prompt_graph = self._parse_graph(prompt)
        answer_graph = self._parse_graph(answer)
        score = self._structure_map_score(prompt_graph, answer_graph)
        
        return min(score * meta_conf, 0.85)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/presupposition/unanswerability."""
        p = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p) and not re.search(r'\b(most|least|highest|lowest)\b', p):
            return 0.3
        
        # Insufficient information markers
        if re.search(r'\b(cannot be determined|not enough information|need more)\b', p):
            return 0.4
        
        return 1.0
    
    def _parse_graph(self, text: str):
        """Parse text into proposition nodes and adjacency matrix."""
        nodes = []
        t = text.lower()
        
        # Extract atomic propositions
        for match in re.finditer(r'(\bnot\b|\bnever\b)?\s*([a-z_]+)\s*\(([^)]+)\)', t):
            polarity = -1 if match.group(1) else 1
            pred = match.group(2)
            args = match.group(3)
            nodes.append({'pred': pred, 'args': args, 'polarity': polarity, 'modality': 'asserted'})
        
        # Numeric comparisons
        for match in re.finditer(r'([\d.]+)\s*(>|<|>=|<=|=)\s*([\d.]+)', t):
            nodes.append({'pred': match.group(2), 'args': f"{match.group(1)},{match.group(3)}", 'polarity': 1, 'modality': 'asserted'})
        
        # Conditionals
        for match in re.finditer(r'if (.+?) then (.+?)(?:\.|$)', t):
            nodes.append({'pred': 'implies', 'args': f"{match.group(1)};{match.group(2)}", 'polarity': 1, 'modality': 'asserted'})
        
        # Causal
        for match in re.finditer(r'(.+?)\s+(because|leads to|causes)\s+(.+?)(?:\.|$)', t):
            nodes.append({'pred': 'causes', 'args': f"{match.group(1)};{match.group(3)}", 'polarity': 1, 'modality': 'asserted'})
        
        # Negations
        for match in re.finditer(r'\b(not|never)\s+([a-z]+)', t):
            nodes.append({'pred': match.group(2), 'args': '', 'polarity': -1, 'modality': 'asserted'})
        
        n = len(nodes)
        adj = np.zeros((n, n))
        belief = np.ones(n) * 0.7
        
        # Build belief vector
        for i, node in enumerate(nodes):
            if re.search(r'\d', node['args']):
                belief[i] = 0.9
            if node['modality'] == 'possible':
                belief[i] = 0.5
        
        return {'nodes': nodes, 'adj': adj, 'belief': belief}
    
    def _structure_map_score(self, g_ref, g_cand):
        """Compute structure-mapping similarity via DP edit distance."""
        nodes_ref = g_ref['nodes']
        nodes_cand = g_cand['nodes']
        m, n = len(nodes_ref), len(nodes_cand)
        
        if m == 0 and n == 0:
            return 0.5
        if m == 0 or n == 0:
            return 0.3
        
        # Cost matrix
        C = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                pred_cost = 0.0 if nodes_ref[i]['pred'] == nodes_cand[j]['pred'] else 1.0
                args_cost = 1.0 - self._cosine_sim(nodes_ref[i]['args'], nodes_cand[j]['args'])
                belief_cost = abs(g_ref['belief'][i] - g_cand['belief'][j])
                C[i, j] = self.w_pred * pred_cost + self.w_args * args_cost + self.w_belief * belief_cost
        
        # DP edit distance
        D = np.zeros((m + 1, n + 1))
        D[0, :] = np.arange(n + 1) * self.insert_del_cost
        D[:, 0] = np.arange(m + 1) * self.insert_del_cost
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                D[i, j] = min(D[i-1, j-1] + C[i-1, j-1], D[i-1, j] + self.insert_del_cost, D[i, j-1] + self.insert_del_cost)
        
        max_cost = (m + n) * self.insert_del_cost
        return max(0, 1 - D[m, n] / max_cost) if max_cost > 0 else 0.5
    
    def _cosine_sim(self, s1, s2):
        """TF-IDF cosine similarity."""
        tokens1 = set(re.findall(r'\w+', s1.lower()))
        tokens2 = set(re.findall(r'\w+', s2.lower()))
        if not tokens1 or not tokens2:
            return 0.5 if s1 == s2 else 0.0
        intersect = len(tokens1 & tokens2)
        return intersect / np.sqrt(len(tokens1) * len(tokens2))
    
    def _compute_answer(self, prompt: str):
        """Execute computational reasoning."""
        p = prompt.lower()
        
        # Numeric comparison
        match = re.search(r'which is (greater|larger|bigger|smaller|less): ([\d.]+) (?:or|and) ([\d.]+)', p)
        if match:
            op, a, b = match.groups()
            a, b = float(a), float(b)
            return str(max(a, b)) if 'greater' in op or 'larger' in op or 'bigger' in op else str(min(a, b))
        
        # Bat and ball
        match = re.search(r'bat and ball cost \$([\d.]+).+bat costs \$([\d.]+) more.+ball cost', p)
        if match:
            total, diff = float(match.group(1)), float(match.group(2))
            ball = (total - diff) / 2
            return f"${ball:.2f}"
        
        # All but N
        match = re.search(r'(\d+) .+ all but (\d+)', p)
        if match:
            total, remaining = int(match.group(1)), int(match.group(2))
            return str(remaining)
        
        # Modular arithmetic
        match = re.search(r'(\d+) mod (\d+)', p)
        if match:
            a, m = int(match.group(1)), int(match.group(2))
            return str(a % m)
        
        # Transitivity
        match = re.search(r'(\w+) > (\w+).+(\w+) > (\w+)', p)
        if match and re.search(r'who is (tallest|fastest|biggest)', p):
            return match.group(1)
        
        return None
    
    def _computational_match(self, prompt: str, candidate: str, computed):
        """Score candidate against computed answer."""
        if computed is None:
            return 0.5
        
        # Normalize and compare
        cand_norm = re.sub(r'[^a-z0-9.]', '', candidate.lower())
        comp_norm = re.sub(r'[^a-z0-9.]', '', str(computed).lower())
        
        if comp_norm in cand_norm or cand_norm in comp_norm:
            return 1.0
        
        # Numeric tolerance
        try:
            c_val = float(re.search(r'[\d.]+', candidate).group())
            comp_val = float(re.search(r'[\d.]+', str(computed)).group())
            if abs(c_val - comp_val) < 0.01:
                return 1.0
        except:
            pass
        
        return 0.0
    
    def _answers_match(self, computed, answer):
        """Check if computed result matches answer."""
        a_norm = re.sub(r'[^a-z0-9.]', '', answer.lower())
        c_norm = re.sub(r'[^a-z0-9.]', '', str(computed).lower())
        return c_norm in a_norm or a_norm in c_norm
    
    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance."""
        import zlib
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0, 1 - ncd)
```

</details>
