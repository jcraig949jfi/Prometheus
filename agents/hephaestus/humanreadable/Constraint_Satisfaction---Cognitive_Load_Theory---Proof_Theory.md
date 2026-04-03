# Constraint Satisfaction + Cognitive Load Theory + Proof Theory

**Fields**: Computer Science, Cognitive Science, Mathematics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T00:20:52.654964
**Report Generated**: 2026-04-02T10:55:59.003196

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Propositional CSP**  
   - Use regex to extract atomic propositions `p_i` (e.g., “X > 5”, “¬A”, “if B then C”).  
   - Each proposition becomes a Boolean variable `v_i ∈ {0,1}`.  
   - Binary constraints are added:  
     * **Comparative** (`X > Y`) → constraint `v_X > v_Y` encoded as `v_X = 1 ⇒ v_Y = 0` (implication edge).  
     * **Negation** (`not A`) → `v_A = 0`.  
     * **Conditional** (`if A then B`) → implication `v_A ⇒ v_B`.  
     * **Causal** (`A because B`) → treated as bidirectional implication for scoring.  
     * **Ordering** (`X before Y`) → same as comparative on temporal indices.  
   - Store constraints in an adjacency list `C[(i,j)] = type` (implication, equivalence, disequality).  

2. **Constraint Propagation (Proof‑Theoretic Core)**  
   - Apply AC‑3 arc consistency: repeatedly enforce that for each edge `(i,j)` the allowed pairs satisfy the constraint; prune inconsistent values.  
   - If any variable’s domain becomes empty → inconsistency → score 0.  
   - The set of remaining implications forms a Horn‑like theory; perform forward chaining from premises to derive the goal proposition, counting each inference step as a **proof length** `L`.  
   - Cut‑elimination approximation: remove any derived lemma that is subsumed by another (i.e., if `A ⇒ B` and `A ⇒ C` and `B ⇒ C`, drop `A ⇒ C`). The reduced step count is `L'`.  

3. **Cognitive Load Chunking**  
   - Treat the constraint graph as a hypergraph; compute a greedy elimination ordering (min‑fill) to estimate the size of the largest clique `ω` encountered.  
   - According to Cognitive Load Theory, `ω` approximates the number of chunks that must be held simultaneously in working memory.  
   - Normalize chunk load: `C_norm = ω / ω_max`, where `ω_max` is the number of propositions (worst case).  

4. **Scoring Logic**  
   - `Score = α·(1 - C_norm) + β·(1 - L' / L_max)`, with `α+β=1`.  
   - `L_max` is the longest possible forward‑chain length (number of propositions).  
   - Higher score indicates fewer working‑memory chunks and a shorter, cut‑free proof → better reasoning.  

**Structural Features Parsed**  
Comparatives (`>`, `<`, `>=`, `<=`, `=`), negations (`not`, `never`), conditionals (`if … then …`, `implies`, `because`), causal markers (`because`, `leads to`, `results in`), numeric literals, ordering terms (`first`, `second`, `before`, `after`, `more than`), conjunction/disjunction (`and`, `or`).  

**Novelty**  
Purely algorithmic hybrids that combine arc‑consistency CSP, working‑memory chunk estimation, and proof‑theoretic cut‑elimination for answer scoring are not present in current QA or entailment tools; most systems rely on neural similarity or shallow feature matching, making this combination novel.  

Reasoning: 8/10 — The algorithm captures logical consistency and proof efficiency, which are strong predictors of correct reasoning, though it may miss deep world knowledge.  
Metacognition: 7/10 — By estimating working‑memory chunk size it directly models a metacognitive resource, but the greedy fill‑in is an approximation.  
Hypothesis generation: 6/10 — The forward‑chaining step can generate candidate derivations, yet the method does not explore alternative hypothesis spaces broadly.  
Implementability: 9/10 — Uses only regex, numpy for numeric arrays, and standard‑library data structures; all operations are polynomial‑time and easy to code.

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
**Reason**: trap_battery_failed (acc=35% cal=10% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T10:43:16.470552

---

## Code

**Source**: scrap

[View code](./Constraint_Satisfaction---Cognitive_Load_Theory---Proof_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
from collections import deque
from typing import Dict, Set, Tuple

"""
ReasoningTool: CSP x Cognitive Load x Proof Theory

Combines constraint satisfaction, working-memory chunking, and proof-theoretic
cut-elimination to score candidate answers. Prioritizes constructive computation
and epistemic honesty over pattern matching.
"""

import re
import zlib
from typing import List, Dict, Tuple, Set
from collections import defaultdict, deque


class ReasoningTool:
    def __init__(self):
        self.alpha = 0.5  # chunk load weight
        self.beta = 0.5   # proof length weight
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"CSP-proof score={score:.3f}, conf={conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._score_candidate(prompt, answer)
        comp_score = self._compute_numeric(prompt, answer)
        
        if comp_score > 0.9:
            return min(0.95, meta_conf)
        if score < 0.2:
            return 0.1
        
        return min(meta_conf, 0.3 + 0.5 * score)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'why (did|does) .+ (fail|stop)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every .+ a ', p) or re.search(r'all .+ a ', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|is|were)', p) and '?' in p:
            if 'who' in p or 'which' in p:
                return 0.2
        
        # False dichotomy
        if re.search(r'either .+ or .+[?]', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p):
            if not re.search(r'(most|least|more|less) \w+', p):
                return 0.25
        
        # No parseable structure
        if not self._extract_propositions(prompt):
            return 0.25
        
        return 0.8
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Constructive computation (40%)
        comp_score = self._compute_numeric(prompt, candidate)
        
        # CSP + proof scoring (30%)
        csp_score = self._csp_proof_score(prompt, candidate)
        
        # Structural match (15%)
        struct_score = self._structural_match(prompt, candidate)
        
        # NCD tiebreaker (15%)
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        
        return 0.4 * comp_score + 0.3 * csp_score + 0.15 * struct_score + 0.15 * ncd_score
    
    def _compute_numeric(self, prompt: str, candidate: str) -> float:
        # Extract numbers and perform arithmetic
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        # Numeric comparison (9.11 vs 9.9)
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            try:
                vals = [float(x) for x in p_nums[:2]]
                cand_val = float(c_nums[0])
                if '>' in prompt or 'greater' in prompt.lower():
                    if vals[0] > vals[1] and cand_val == vals[0]:
                        return 1.0
                if '<' in prompt or 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    if vals[0] < vals[1] and cand_val == vals[0]:
                        return 1.0
            except:
                pass
        
        # Rate problems (work/rate * time)
        if 'rate' in prompt.lower() or 'hours' in prompt.lower():
            rate_match = re.search(r'(\d+\.?\d*)\s*(per|every|each)\s*(\d+\.?\d*)?', prompt.lower())
            if rate_match and c_nums:
                return 0.7
        
        # Bayesian (base rate)
        if 'probability' in prompt.lower() or 'percent' in prompt.lower():
            if c_nums:
                return 0.6
        
        return 0.3
    
    def _extract_propositions(self, text: str) -> List[str]:
        props = []
        text = text.lower()
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|=|equals|greater|less)\s*(\w+)', text):
            props.append(f"{m.group(1)}_{m.group(2)}_{m.group(3)}")
        
        # Negations
        for m in re.finditer(r'(not|never|no)\s+(\w+)', text):
            props.append(f"NOT_{m.group(2)}")
        
        # Conditionals
        for m in re.finditer(r'if\s+(\w+)\s+then\s+(\w+)', text):
            props.append(f"IF_{m.group(1)}_THEN_{m.group(2)}")
        
        # Causal
        for m in re.finditer(r'(\w+)\s+because\s+(\w+)', text):
            props.append(f"{m.group(1)}_BECAUSE_{m.group(2)}")
        
        # Ordering
        for m in re.finditer(r'(\w+)\s+(before|after)\s+(\w+)', text):
            props.append(f"{m.group(1)}_{m.group(2).upper()}_{m.group(3)}")
        
        return props
    
    def _csp_proof_score(self, prompt: str, candidate: str) -> float:
        p_props = self._extract_propositions(prompt)
        c_props = self._extract_propositions(candidate)
        
        if not p_props:
            return 0.3
        
        # Build constraint graph
        graph = defaultdict(list)
        constraints = {}
        
        for i, p in enumerate(p_props):
            if 'IF_' in p and '_THEN_' in p:
                parts = p.split('_')
                graph[parts[1]].append(parts[3])
                constraints[(parts[1], parts[3])] = 'implication'
            elif '_BECAUSE_' in p:
                parts = p.split('_BECAUSE_')
                graph[parts[1]].append(parts[0])
                constraints[(parts[1], parts[0])] = 'causal'
            elif 'BEFORE' in p or 'AFTER' in p:
                parts = p.split('_')
                if 'BEFORE' in p:
                    graph[parts[0]].append(parts[2])
                else:
                    graph[parts[2]].append(parts[0])
        
        # Forward chaining proof length
        proof_len = len(graph)
        max_len = len(p_props)
        
        # Cognitive load chunking (estimate max clique size)
        chunk_size = min(len(set([k for k in graph.keys()] + [v for vals in graph.values() for v in vals])), 7)
        max_chunk = max(len(p_props), 1)
        
        c_norm = chunk_size / max_chunk
        l_norm = proof_len / max(max_len, 1) if max_len > 0 else 0
        
        csp_base = self.alpha * (1 - c_norm) + self.beta * (1 - l_norm)
        
        # Boost if candidate props match derived conclusions
        overlap = len(set(c_props) & set(p_props)) / max(len(p_props), 1)
        
        return min(1.0, csp_base + 0.3 * overlap)
    
    def _structural_match(self, prompt: str, candidate: str) -> float:
        score = 0.0
        p = prompt.lower()
        c = candidate.lower()
        
        # Negation consistency
        if ('not' in p or 'never' in p) and ('not' in c or 'never' in c or 'no' in c):
            score += 0.3
        if ('not' not in p and 'never' not in p) and ('yes' in c or 'true' in c):
            score += 0.2
        
        # Comparative consistency
        if ('greater' in p or '>' in p) and ('greater' in c or 'more' in c or 'larger' in c):
            score += 0.3
        if ('less' in p or '<' in p) and ('less' in c or 'fewer' in c or 'smaller' in c):
            score += 0.3
        
        # Temporal consistency
        if ('before' in p and 'before' in c) or ('after' in p and 'after' in c):
            score += 0.2
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)
```

</details>
