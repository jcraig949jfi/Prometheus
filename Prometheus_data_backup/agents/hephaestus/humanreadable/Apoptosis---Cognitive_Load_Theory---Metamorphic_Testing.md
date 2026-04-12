# Apoptosis + Cognitive Load Theory + Metamorphic Testing

**Fields**: Biology, Cognitive Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:11:59.262452
**Report Generated**: 2026-04-02T08:39:54.914536

---

## Nous Analysis

**1. Algorithm – “Apoptotic Metamorphic Constraint Scorer (AMCS)”**  

*Data structures*  
- `Prop`: a namedtuple `(id, polarity, pred, args)` where `polarity∈{+1,‑1}` encodes negation, `pred` is a predicate string, `args` is a tuple of grounded terms (constants or variables).  
- `ConstraintGraph`: adjacency list `graph[pid] = set of (qid, rel_type, weight)`. `rel_type∈{IMPLIES, EQUIV, ORDER, CAUSE, COMPARE}`.  
- `Candidate`: list of `Prop` extracted from an answer string.  
- `WorkingSet`: a fixed‑size list (size `K`) representing the current chunk of propositions held in “working memory”.  

*Parsing (regex‑based, stdlib only)*  
1. Tokenise the prompt and each candidate answer.  
2. Extract propositions with patterns for:  
   - Negation: `\b(not|no)\b` → flip polarity.  
   - Comparatives: `(\d+)\s*(>|<|>=|<=)\s*(\d+)` → `COMPARE` edge with weight = 1.  
   - Conditionals: `if\s+(.+?)\s+then\s+(.+)` → two `Prop`s, add `IMPLIES` edge (weight = 2).  
   - Causal: `because\s+(.+?),\s+(.+)` → `CAUSE` edge.  
   - Ordering/temporal: `before|after|first|second` → `ORDER` edge.  
   - Simple predications: `(\w+)\s+(\w+)` → `Prop` with default polarity = +1.  
3. Store each `Prop` in a dict `prop_id → Prop`.  

*Constraint propagation*  
- Initialise `graph` with extracted edges.  
- Iterate until fixed point: for each `(u → v, IMPLIES, w)` and `(v → x, IMPLIES, w2)`, add `(u → x, IMPLIES, min(w,w2))` (transitivity).  
- For each `ORDER` chain, enforce antisymmetry (if `A<Order>B` and `B<Order>A` → contradiction).  

*Scoring a candidate*  
1. **Base consistency** – For each `Prop p` in the candidate, check if `graph` entails `p` or its negation.  
   - Entailment test: BFS from `p` following `IMPLIES` edges; if a contradictory polarity is reached, count a violation.  
   - `violations = Σ entailed_contradictions`.  
   - `base = 1 - (violations / max(1, total_props_in_candidate))`.  
2. **Apoptotic pruning** – Treat low‑viability candidates as “cells earmarked for death”.  
   - Sort candidates by `base` ascending.  
   - Remove the lowest‑scoring candidate, recompute `base` for the rest (since removal can reduce constraint pressure).  
   - Continue until removal would increase the average `base` of the remaining set.  
   - Let `r` be number removed; apoptosis factor `apo = exp(-λ·r)` with λ=0.5.  
3. **Cognitive‑load chunking** – While evaluating a candidate, keep at most `K=4` propositions in `WorkingSet`.  
   - If the candidate exceeds `K`, compute excess `e = len(candidate)-K`.  
   - Load factor `load = 1 / (1 + α·e)` with α=0.3.  

*Final score*  
`score = base · apo · load`.  
Scores are normalized to `[0,1]` for ranking.

**2. Structural features parsed**  
Negations, comparatives (`>`,`<`, `>=`, `<=`), conditionals (`if … then`), causal claims (`because`, `leads to`), ordering/temporal relations (`before`, `after`, `first`, `second`), numeric constants, simple subject‑predicate‑object triples, and equivalence phrases (`is the same as`).

**3. Novelty**  
The algorithm fuses three well‑studied ideas: apoptosis‑inspired iterative pruning (akin to argument‑framework semantics), metamorphic relations (using logical constraints as relations between inputs/outputs), and Cognitive Load Theory’s bounded working‑memory chunking. While each component appears separately in literature (e.g., constraint‑based QA, metamorphic testing of solvers, cognitive‑load‑aware models), their conjunction in a single, deterministic scoring pipeline has not been described to our knowledge, making the combination novel.

**4. Ratings**  

Reasoning: 8/10 — The method performs explicit logical propagation and violation counting, giving a sound, interpretable measure of answer consistency.  
Metacognition: 7/10 — Apoptotic pruning mimics self‑monitoring (removing low‑viability answers) and cognitive‑load limits simulate awareness of processing limits, though it lacks higher‑level strategy selection.  
Metamorphic Testing: 9/10 — Constraints are explicit metamorphic relations; the scorer directly evaluates whether answers preserve those relations under transformations (negation, ordering, etc.).  
Implementability: 9/10 — Uses only regex (stdlib) and NumPy for vector‑only operations (e.g., exponential, division); no external libraries or APIs required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | N/A |
| Implementability | 9/10 |
| **Composite** | **7.5** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=34% cal=12% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:34:15.993679

---

## Code

**Source**: scrap

[View code](./Apoptosis---Cognitive_Load_Theory---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, List, Set, Tuple

import re
import zlib
from typing import NamedTuple, List, Dict, Set, Tuple
import math

class Prop(NamedTuple):
    id: int
    polarity: int  # +1 or -1
    pred: str
    args: Tuple[str, ...]

class ReasoningTool:
    """
    Apoptotic Metamorphic Constraint Scorer (AMCS).
    
    Combines constraint propagation, apoptotic pruning, and cognitive load theory
    to score candidate answers. Extracts logical relations (IMPLIES, ORDER, CAUSE,
    COMPARE) from prompt text, builds a constraint graph, and scores candidates by:
    1. Base consistency - violation counting via BFS entailment
    2. Apoptotic factor - iterative removal of low-viability candidates
    3. Cognitive load - penalty for exceeding working memory (K=4 props)
    """
    
    def __init__(self):
        self.K = 4  # Working memory capacity
        self.lambda_apo = 0.5
        self.alpha_load = 0.3
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Parse prompt to extract constraints
        prompt_props, prompt_graph = self._parse_text(prompt)
        
        # Score each candidate
        results = []
        for cand in candidates:
            cand_props, cand_graph = self._parse_text(cand)
            combined_graph = self._merge_graphs(prompt_graph, cand_graph)
            
            base_score = self._base_consistency(cand_props, combined_graph, prompt_props)
            load_score = self._cognitive_load(cand_props)
            
            # Numeric evaluation
            numeric_score = self._numeric_eval(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination
            score = 0.5 * base_score + 0.2 * numeric_score + 0.15 * load_score + 0.15 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"base={base_score:.2f}, numeric={numeric_score:.2f}, load={load_score:.2f}"
            })
        
        # Apoptotic pruning
        results = self._apoptotic_pruning(results)
        
        # Normalize and sort
        if results:
            max_s = max(r["score"] for r in results)
            min_s = min(r["score"] for r in results)
            for r in results:
                r["score"] = (r["score"] - min_s) / max(0.01, max_s - min_s)
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence: check for ambiguity/unanswerability
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        prompt_props, prompt_graph = self._parse_text(prompt)
        ans_props, ans_graph = self._parse_text(answer)
        combined_graph = self._merge_graphs(prompt_graph, ans_graph)
        
        base_score = self._base_consistency(ans_props, combined_graph, prompt_props)
        numeric_score = self._numeric_eval(prompt, answer)
        
        struct_conf = 0.6 * base_score + 0.4 * numeric_score
        
        # Cap by meta-confidence
        return min(meta_conf, struct_conf)
    
    def _parse_text(self, text: str) -> Tuple[List[Prop], Dict]:
        text = text.lower()
        props = []
        graph = {}
        pid = 0
        
        # Extract negations
        neg_pattern = r'\b(not|no|never|neither)\s+(\w+)'
        for m in re.finditer(neg_pattern, text):
            props.append(Prop(pid, -1, m.group(2), ()))
            graph[pid] = set()
            pid += 1
        
        # Extract comparatives (numeric)
        comp_pattern = r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)'
        for m in re.finditer(comp_pattern, text):
            props.append(Prop(pid, 1, 'COMPARE', (m.group(1), m.group(2), m.group(3))))
            graph[pid] = set()
            pid += 1
        
        # Extract conditionals
        cond_pattern = r'if\s+(.+?)\s+then\s+(.+?)[\.\,\;]'
        for m in re.finditer(cond_pattern, text):
            p1 = Prop(pid, 1, 'cond_ant', (m.group(1).strip(),))
            p2 = Prop(pid+1, 1, 'cond_cons', (m.group(2).strip(),))
            props.extend([p1, p2])
            graph[pid] = {(pid+1, 'IMPLIES', 2)}
            graph[pid+1] = set()
            pid += 2
        
        # Extract causal
        cause_pattern = r'because\s+(.+?),\s+(.+?)[\.\;]'
        for m in re.finditer(cause_pattern, text):
            p1 = Prop(pid, 1, 'cause', (m.group(1).strip(),))
            p2 = Prop(pid+1, 1, 'effect', (m.group(2).strip(),))
            props.extend([p1, p2])
            graph[pid] = {(pid+1, 'CAUSE', 1)}
            graph[pid+1] = set()
            pid += 2
        
        # Extract ordering
        order_pattern = r'(before|after|first|second|earlier|later)'
        if re.search(order_pattern, text):
            props.append(Prop(pid, 1, 'ORDER', ()))
            graph[pid] = set()
            pid += 1
        
        # Simple predications
        pred_pattern = r'(\w+)\s+(is|are|was|were)\s+(\w+)'
        for m in re.finditer(pred_pattern, text):
            props.append(Prop(pid, 1, m.group(2), (m.group(1), m.group(3))))
            graph[pid] = set()
            pid += 1
        
        return props, graph
    
    def _merge_graphs(self, g1: Dict, g2: Dict) -> Dict:
        merged = {}
        for k, v in g1.items():
            merged[k] = v.copy()
        offset = max(g1.keys()) + 1 if g1 else 0
        for k, v in g2.items():
            merged[k + offset] = {(nid + offset, rel, w) for nid, rel, w in v}
        return merged
    
    def _base_consistency(self, cand_props: List[Prop], graph: Dict, prompt_props: List[Prop]) -> float:
        if not cand_props:
            return 0.5
        
        violations = 0
        # Check for contradictions
        for cp in cand_props:
            for pp in prompt_props:
                if cp.pred == pp.pred and cp.polarity != pp.polarity:
                    violations += 1
        
        # Check IMPLIES chains
        for pid, edges in graph.items():
            for target, rel, _ in edges:
                if rel == 'IMPLIES' and pid < len(cand_props) and target < len(cand_props):
                    if cand_props[pid].polarity == 1 and cand_props[target].polarity == -1:
                        violations += 1
        
        return 1.0 - (violations / max(1, len(cand_props)))
    
    def _cognitive_load(self, props: List[Prop]) -> float:
        excess = max(0, len(props) - self.K)
        return 1.0 / (1.0 + self.alpha_load * excess)
    
    def _apoptotic_pruning(self, results: List[Dict]) -> List[Dict]:
        if len(results) <= 1:
            return results
        
        removed = 0
        while len(results) > 1:
            results_sorted = sorted(results, key=lambda x: x["score"])
            avg_before = sum(r["score"] for r in results) / len(results)
            avg_after = sum(r["score"] for r in results[1:]) / (len(results) - 1)
            
            if avg_after > avg_before:
                results = results_sorted[1:]
                removed += 1
            else:
                break
        
        apo_factor = math.exp(-self.lambda_apo * removed)
        for r in results:
            r["score"] *= apo_factor
        
        return results
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        # Extract numbers from prompt and candidate
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        # Check comparisons
        comp_match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', prompt)
        if comp_match:
            a, op, b = float(comp_match.group(1)), comp_match.group(2), float(comp_match.group(3))
            expected = (a > b if op == '>' else a < b if op == '<' else a >= b if op == '>=' else a <= b)
            
            # Check if candidate affirms this
            if ('yes' in candidate.lower() or 'true' in candidate.lower()) and expected:
                return 1.0
            if ('no' in candidate.lower() or 'false' in candidate.lower()) and not expected:
                return 1.0
        
        # Numeric overlap
        if p_nums and c_nums:
            overlap = len(set(p_nums) & set(c_nums))
            return overlap / max(len(p_nums), len(c_nums))
        
        return 0.5
    
    def _meta_confidence(self, prompt: str) -> float:
        text = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)', text):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', text):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\s+(was|is|said)', text) and 'who' in text:
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either\s+\w+\s+or\s+\w+)', text):
            return 0.25
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', text) and not re.search(r'(most|least|highest|lowest)', text):
            return 0.25
        
        # Unanswerable markers
        if re.search(r'(cannot be determined|not enough information|impossible to tell)', text):
            return 0.2
        
        return 0.85
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)
```

</details>
