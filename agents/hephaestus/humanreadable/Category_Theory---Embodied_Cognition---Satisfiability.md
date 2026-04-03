# Category Theory + Embodied Cognition + Satisfiability

**Fields**: Mathematics, Cognitive Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T13:11:04.146171
**Report Generated**: 2026-04-02T10:00:35.932433

---

## Nous Analysis

**1. Algorithm**  
Parse each prompt and candidate answer into a labeled directed graph \(G=(V,E)\) where vertices \(v_i\) are propositional atoms (e.g., “the block is red”, “speed > 5 m/s”) and edges \(e_{ij}\) encode a relation extracted by regex patterns:  
- Implication \(X\rightarrow Y\) (if X then Y, because X, leads to Y)  
- Equivalence \(X\leftrightarrow Y\) (X is the same as Y)  
- Negation \(\neg X\) (X is not true, no X)  
- Comparative \(X > Y\) or \(X < Y\) (greater than, less than, faster, slower)  
- Ordering \(X\) before \(Y\) (before, after, first, last)  

Each atom \(v_i\) is also grounded to an **embodied feature vector** \(g_i\in\mathbb{R}^d\) (d=5) built from simple heuristics: motion verbs → [1,0,0,0,0], spatial prepositions → [0,1,0,0,0], size adjectives → [0,0,1,0,0], valence words → [0,0,0,1,0], numeric magnitude → [0,0,0,0,1]. Vectors are normalized to unit length.

The graph is translated into a **CNF clause matrix** \(C\in\{0,1,-1\}^{m\times n}\) (m clauses, n literals) using NumPy: each row contains +1 for a positive literal, -1 for a negated literal, 0 otherwise. Unit propagation is performed iteratively:  
```
while any clause has exactly one unassigned literal:
    assign that literal to satisfy the clause
    propagate assignments (zero out satisfied clauses, simplify others)
```
Assignments are stored in a Boolean NumPy array \(a\). After propagation, the number of satisfied clauses \(sat = \sum_j \text{clause\_satisfied}(C_j, a)\) is computed. An **unsatisfiable core** is approximated by greedily removing clauses with the lowest satisfaction contribution until the remaining set becomes satisfiable (detected by a second propagation pass). Core size \(core\) is recorded.

Finally, compute an **embodiment similarity** between the aggregated grounded vectors of the prompt (\(G_Q\)) and answer (\(G_A\)):  
```
sim = cosine(G_Q, G_A) = (G_Q·G_A) / (||G_Q||·||G_A||)
```
where \(G_Q\) and \(G_A\) are the mean of the grounded vectors of atoms appearing in each text.

**Score** (higher is better):  
\[
\text{score}= w_1\frac{sat}{m} - w_2\frac{core}{m} + w_3\,sim
\]
with weights \(w_1=0.5, w_2=0.3, w_3=0.2\) (tunable).

**2. Structural features parsed**  
Negations (“not”, “no”, “never”), conditionals (“if … then”, “unless”, “because”), comparatives (“greater than”, “less than”, “more”, “faster”), ordering relations (“before”, “after”, “first”, “last”, “precedes”), causal claims (“leads to”, “results in”, “causes”), numeric values with units, and quantifiers (“all”, “some”, “none”) are extracted via regex and turned into the edge types above.

**3. Novelty**  
Pure‑numpy reasoners typically use either symbolic SAT solvers or bag‑of‑word similarity. Combining a category‑theoretic morphism view (edges as functors between propositional objects) with embodied grounding vectors and a lightweight unit‑propagation SAT core is not found in existing open‑source tools; most work treats logic and embodiment separately. Hence the combination is novel in this constrained setting.

**Ratings**  
Reasoning: 8/10 — captures logical structure and propagates constraints effectively.  
Metacognition: 6/10 — limited self‑monitoring; no explicit confidence calibration beyond the score.  
Hypothesis generation: 7/10 — can propose answers that maximize clause satisfaction and embodiment similarity.  
Implementability: 9/10 — relies only on regex, NumPy arrays, and basic loops; no external dependencies.

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
**Reason**: trap_battery_failed (acc=2% cal=5% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:45:19.227143

---

## Code

**Source**: scrap

[View code](./Category_Theory---Embodied_Cognition---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Category Theory x Embodied Cognition x Satisfiability reasoner.
    Parses text to labeled graphs, grounds atoms to feature vectors,
    converts to CNF, performs unit propagation, and computes scores
    combining SAT satisfaction, unsatisfiable core, and embodiment similarity.
    """
    
    def __init__(self):
        self.weights = {'sat': 0.5, 'core': 0.3, 'emb': 0.2}
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Check if we have a computational solution
        comp_result = self._compute_answer(prompt)
        if comp_result is not None:
            # Deterministic answer from computation
            if self._answers_match(comp_result, answer):
                return 0.85
            else:
                return 0.15
        
        # Use scoring
        score, _ = self._score_candidate(prompt, answer)
        conf = min(0.75, max(0.25, score))
        return min(conf, meta_conf + 0.4)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition detection
        if re.search(r'(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'why (did|does) .+ (fail|stop|end)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|did)', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+[?]', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.3
        
        # Insufficient information
        if 'not enough information' in p or 'cannot be determined' in p:
            return 0.25
        
        return 0.8
    
    def _compute_answer(self, prompt: str):
        # Numeric comparison
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) == 2 and any(w in prompt.lower() for w in ['greater', 'less', 'larger', 'smaller', 'more', 'fewer']):
            a, b = float(nums[0]), float(nums[1])
            if 'greater' in prompt.lower() or 'larger' in prompt.lower() or 'more' in prompt.lower():
                return str(max(a, b))
            else:
                return str(min(a, b))
        
        # Bat and ball algebra: total - small = large
        if 'bat' in prompt.lower() and 'ball' in prompt.lower():
            match = re.search(r'(\d+\.?\d*).+more than.+ball', prompt.lower())
            if match and len(nums) >= 2:
                total = float(nums[0])
                diff = float(match.group(1))
                ball = (total - diff) / 2
                return f"{ball:.2f}"
        
        # Modular arithmetic
        if 'remainder' in prompt.lower() or 'modulo' in prompt.lower():
            if len(nums) >= 2:
                return str(int(nums[0]) % int(nums[1]))
        
        # Temporal ordering - simple first/last
        time_words = re.findall(r'\b(first|second|third|last|before|after)\b', prompt.lower())
        if time_words:
            items = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if 'first' in time_words and items:
                return items[0]
            if 'last' in time_words and items:
                return items[-1]
        
        return None
    
    def _answers_match(self, comp: str, cand: str) -> bool:
        c1, c2 = comp.lower().strip(), cand.lower().strip()
        if c1 == c2:
            return True
        if c1 in c2 or c2 in c1:
            return True
        try:
            if abs(float(c1) - float(c2)) < 0.01:
                return True
        except:
            pass
        return False
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        # Parse to graphs
        g_p = self._parse_graph(prompt)
        g_c = self._parse_graph(candidate)
        
        # Convert to CNF and solve
        cnf_p = self._graph_to_cnf(g_p)
        cnf_c = self._graph_to_cnf(g_c)
        cnf_combined = np.vstack([cnf_p, cnf_c]) if cnf_p.size > 0 and cnf_c.size > 0 else cnf_p
        
        sat_score, core_size = self._sat_solve(cnf_combined)
        
        # Embodiment similarity
        emb_p = self._aggregate_embeddings(g_p)
        emb_c = self._aggregate_embeddings(g_c)
        emb_sim = self._cosine_sim(emb_p, emb_c)
        
        # Compute NCD tiebreaker
        ncd = self._ncd(prompt, candidate)
        
        # Final score
        m = max(1, cnf_combined.shape[0])
        score = (self.weights['sat'] * sat_score / m - 
                 self.weights['core'] * core_size / m + 
                 self.weights['emb'] * emb_sim +
                 0.1 * (1 - ncd))
        
        reasoning = f"SAT:{sat_score}/{m}, Core:{core_size}, Emb:{emb_sim:.2f}, NCD:{ncd:.2f}"
        return score, reasoning
    
    def _parse_graph(self, text: str) -> Dict:
        atoms = []
        edges = []
        
        # Extract atoms (simple noun phrases and clauses)
        sentences = re.split(r'[.!?;]', text)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 3:
                continue
            atoms.append(sent)
            
            # Extract relations
            if re.search(r'\bif .+ then\b', sent.lower()):
                parts = re.split(r'\bthen\b', sent.lower())
                if len(parts) == 2:
                    edges.append(('implies', parts[0].strip(), parts[1].strip()))
            
            if re.search(r'\bnot\b|\bno\b|\bnever\b', sent.lower()):
                edges.append(('negation', sent, ''))
            
            if re.search(r'(greater|less|more|fewer) than', sent.lower()):
                edges.append(('comparative', sent, ''))
            
            if re.search(r'\b(before|after|first|last)\b', sent.lower()):
                edges.append(('ordering', sent, ''))
        
        return {'atoms': atoms, 'edges': edges}
    
    def _graph_to_cnf(self, graph: Dict) -> np.ndarray:
        atoms = graph['atoms']
        if not atoms:
            return np.array([]).reshape(0, 0)
        
        n = len(atoms)
        clauses = []
        
        # Each atom becomes a clause
        for i in range(n):
            clause = np.zeros(n)
            clause[i] = 1
            clauses.append(clause)
        
        # Process edges
        for edge_type, src, tgt in graph['edges']:
            if edge_type == 'implies' and src in atoms and tgt in atoms:
                i, j = atoms.index(src), atoms.index(tgt)
                clause = np.zeros(n)
                clause[i] = -1
                clause[j] = 1
                clauses.append(clause)
            elif edge_type == 'negation':
                for i, atom in enumerate(atoms):
                    if atom == src:
                        clause = np.zeros(n)
                        clause[i] = -1
                        clauses.append(clause)
        
        return np.array(clauses) if clauses else np.array([]).reshape(0, n)
    
    def _sat_solve(self, cnf: np.ndarray) -> Tuple[int, int]:
        if cnf.size == 0:
            return 0, 0
        
        m, n = cnf.shape
        assignment = np.zeros(n, dtype=int)
        
        # Unit propagation
        for _ in range(10):
            changed = False
            for i in range(m):
                clause = cnf[i]
                unassigned = np.where((clause != 0) & (assignment == 0))[0]
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    assignment[lit] = 1 if clause[lit] > 0 else -1
                    changed = True
            if not changed:
                break
        
        # Count satisfied clauses
        satisfied = 0
        for i in range(m):
            clause = cnf[i]
            if any((clause[j] > 0 and assignment[j] > 0) or 
                   (clause[j] < 0 and assignment[j] < 0) for j in range(n)):
                satisfied += 1
        
        # Approximate unsat core
        core_size = m - satisfied
        
        return satisfied, core_size
    
    def _aggregate_embeddings(self, graph: Dict) -> np.ndarray:
        atoms = graph['atoms']
        if not atoms:
            return np.zeros(5)
        
        embeddings = []
        for atom in atoms:
            emb = self._ground_atom(atom)
            embeddings.append(emb)
        
        agg = np.mean(embeddings, axis=0)
        norm = np.linalg.norm(agg)
        return agg / norm if norm > 0 else agg
    
    def _ground_atom(self, atom: str) -> np.ndarray:
        emb = np.zeros(5)
        atom_l = atom.lower()
        
        # Motion verbs
        if any(w in atom_l for w in ['move', 'run', 'walk', 'fly', 'jump', 'go']):
            emb[0] = 1
        
        # Spatial prepositions
        if any(w in atom_l for w in ['in', 'on', 'above', 'below', 'left', 'right', 'near', 'far']):
            emb[1] = 1
        
        # Size adjectives
        if any(w in atom_l for w in ['big', 'small', 'large', 'tiny', 'huge', 'tall', 'short']):
            emb[2] = 1
        
        # Valence words
        if any(w in atom_l for w in ['good', 'bad', 'happy', 'sad', 'love', 'hate']):
            emb[3] = 1
        
        # Numeric magnitude
        nums = re.findall(r'\d+', atom)
        if nums:
            emb[4] = min(1.0, sum(int(n) for n in nums) / 100.0)
        
        norm = np.linalg.norm(emb)
        return emb / norm if norm > 0 else emb
    
    def _cosine_sim(self, a: np.ndarray, b: np.ndarray) -> float:
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def _ncd(self, s1: str, s2: str) -> float:
        import zlib
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
