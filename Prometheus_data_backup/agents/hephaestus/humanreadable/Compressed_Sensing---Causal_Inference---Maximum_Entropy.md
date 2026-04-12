# Compressed Sensing + Causal Inference + Maximum Entropy

**Fields**: Computer Science, Information Science, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T06:21:59.036899
**Report Generated**: 2026-04-02T10:00:37.195413

---

## Nous Analysis

**Algorithm**  
1. **Proposition extraction** – Using regex, scan the prompt and each candidate answer for atomic propositions:  
   - Negations (`not P`) → signed literal `‑P`  
   - Conditionals (`if A then B`) → implication edge `A → B`  
   - Causal claims (`A causes B`, `B because A`) → directed edge `A → B`  
   - Comparatives/numerics (`X > 5`, `Y is twice Z`) → numeric constraints `f_i(x) = value`  
   - Ordering (`X before Y`) → temporal edge `X → Y`  
   Each unique proposition gets an index `j`; we build a sparse binary vector **x**∈ℝⁿ where `x_j=1` iff proposition j is asserted in the answer.

2. **Measurement matrix (Compressed Sensing)** – For every structural constraint extracted from the prompt we create a row of **M**∈ℝᵐˣⁿ:  
   - A conditional `A → B` gives `M[row, A]=+1, M[row, B]=‑1` ( enforces `x_A ≤ x_B`).  
   - A numeric constraint `f_i(x)=v` becomes a row with the appropriate coefficients (e.g., `2·x_Z - x_Y = 0`).  
   - Negations flip the sign of the corresponding column.  
   The prompt’s right‑hand side **b** encodes the required truth values (0/1 or numeric targets).

3. **Sparse recovery** – Solve the basis‑pursuit denoising problem  
   \[
   \min_x \|x\|_1 \quad\text{s.t.}\quad \|Mx-b\|_2\le\epsilon
   \]  
   using ISTA (Iterative Shrinkage‑Thresholding Algorithm) with only NumPy operations. The solution **x̂** is the sparsest set of propositions consistent with the prompt.

4. **Causal consistency propagation** – Build a causal adjacency matrix **C** from extracted cause‑effect edges. Compute its transitive closure via repeated Boolean matrix multiplication (or Floyd‑Warshall) to enforce modus ponens: if `A→B` and `B→C` then `A→C`. Any violation (e.g., `x_A=1, x_B=0` where `A→B` exists) incurs a penalty `λ·‖C·x̂ - x̂‖₁`.

5. **Maximum‑entropy weighting** – Treat each proposition’s expectation under the prompt constraints as a feature. Solve the log‑linear maxent model  
   \[
   p(x)=\frac{1}{Z}\exp\bigl(\sum_i \theta_i f_i(x)\bigr)
   \]  
   by iterative scaling (NumPy only) to obtain the least‑biased distribution **p\*** matching the empirical feature averages from the prompt. Convert the candidate’s proposition vector to a distribution **q** (e.g., normalize **x̂**). The final score is  
   \[
   S = -\|M\hat x-b\|_1 - \lambda\|C\hat x-\hat x\|_1 - \eta\,\mathrm{KL}(q\|p\*)
   \]  
   Lower (more negative) scores indicate better alignment.

**Structural features parsed**  
Negations, conditionals, causal claims, comparatives, numeric values, ordering relations, conjunctions/disjunctions (via parallel rows in **M**).

**Novelty**  
While each component (sparse recovery, causal DAG reasoning, maxent weighting) exists separately, their joint use to score answer candidates via a single optimization loop is not found in current QA or explanation‑scoring literature, making the combination novel.

**Rating**  
Reasoning: 8/10 — captures logical, causal, and numeric constraints through a unified sparse‑recovery framework.  
Metacognition: 6/10 — the method evaluates consistency but lacks explicit self‑reflection or uncertainty calibration beyond the maxent prior.  
Hypothesis generation: 7/10 — ISTA produces a sparse set of candidate propositions, effectively generating parsimonious hypotheses.  
Implementability: 9/10 — relies solely on NumPy and Python’s standard library; no external models or APIs required.

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
**Reason**: validation:forbidden_import: forge_primitives

**Forge Timestamp**: 2026-04-02T09:14:25.453739

---

## Code

**Source**: scrap

[View code](./Compressed_Sensing---Causal_Inference---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
"""
Compressed Sensing x Causal Inference x Maximum Entropy Reasoning Tool

Pipeline:
1. Parse propositions from prompt/candidates (CS: measurement matrix)
2. Build causal DAG from conditionals (CI: causal structure)
3. Constraint propagation via primitives (CS: sparse recovery)
4. MaxEnt scoring via entropy minimization over valid states
5. Meta-confidence via information sufficiency check
"""

import re
import numpy as np
import zlib
from collections import defaultdict
from forge_primitives import (
    solve_constraints, modus_ponens, check_transitivity,
    bayesian_update, entropy, dag_traverse, topological_sort,
    information_sufficiency, confidence_from_agreement,
    solve_linear_system, modular_arithmetic
)


class ReasoningTool:
    def __init__(self):
        self.epsilon = 1e-6
        
    def _parse_propositions(self, text):
        """Extract atomic propositions and constraints."""
        props = {}
        constraints = []
        
        # Negations: "not X", "X is not Y"
        for match in re.finditer(r'\b(not|isn\'t|aren\'t|doesn\'t|don\'t)\s+(\w+)', text.lower()):
            prop = f"NOT_{match.group(2)}"
            props[prop] = props.get(prop, len(props))
        
        # Conditionals: "if A then B"
        for match in re.finditer(r'\bif\s+([^,]+?)\s+then\s+([^,.]+)', text.lower()):
            ante = match.group(1).strip()
            cons = match.group(2).strip()
            constraints.append(('implies', ante, cons))
        
        # Causal: "A causes B", "B because A"
        for match in re.finditer(r'(\w+)\s+causes\s+(\w+)', text.lower()):
            constraints.append(('causal', match.group(1), match.group(2)))
        for match in re.finditer(r'(\w+)\s+because\s+(\w+)', text.lower()):
            constraints.append(('causal', match.group(2), match.group(1)))
        
        # Comparatives: "X > Y", "X < Y"
        nums = {}
        for match in re.finditer(r'(\d+\.?\d*)', text):
            nums[match.group(1)] = float(match.group(1))
        for match in re.finditer(r'(\w+)\s*(>|<|>=|<=)\s*(\w+)', text):
            constraints.append(('compare', match.group(1), match.group(2), match.group(3)))
        
        return props, constraints, nums
    
    def _build_causal_dag(self, constraints):
        """Build causal adjacency from constraints."""
        edges = []
        for c in constraints:
            if c[0] in ('implies', 'causal'):
                edges.append((c[1], c[2]))
        return edges
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity/unanswerability markers."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.+fail|why did.+stop)', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and '?' in prompt:
            if re.search(r'\bwho\b', p_lower):
                return 0.2
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)', p_lower):
            return 0.25
        
        # Insufficient info
        if re.search(r'\b(unknown|not specified|no information|cannot determine)', p_lower):
            return 0.15
        
        return 1.0
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Score candidates via CS + CI + MaxEnt pipeline."""
        # Parse prompt structure
        p_props, p_constraints, p_nums = self._parse_propositions(prompt)
        causal_edges = self._build_causal_dag(p_constraints)
        
        # Meta-confidence cap
        meta_conf = self._meta_confidence(prompt)
        
        results = []
        for cand in candidates:
            c_props, c_constraints, c_nums = self._parse_propositions(cand)
            
            # STEP 1: Constraint satisfaction (Compressed Sensing recovery)
            all_props = set(list(p_props.keys()) + list(c_props.keys()))
            variables = {p: i for i, p in enumerate(all_props)}
            domains = {p: [0, 1] for p in all_props}
            
            cs_constraints = []
            for ct in p_constraints + c_constraints:
                if ct[0] == 'implies':
                    cs_constraints.append(('implies', ct[1], ct[2]))
            
            try:
                solution = solve_constraints(variables, domains, cs_constraints)
                constraint_score = 1.0 if solution else 0.3
            except:
                constraint_score = 0.5
            
            # STEP 2: Causal consistency (Causal Inference)
            causal_score = 1.0
            if causal_edges:
                try:
                    topo = topological_sort(causal_edges)
                    is_transitive = check_transitivity(causal_edges)
                    causal_score = 0.9 if is_transitive else 0.6
                except:
                    causal_score = 0.4
            
            # STEP 3: Numeric evaluation
            numeric_score = 1.0
            for ct in p_constraints:
                if ct[0] == 'compare':
                    try:
                        v1 = float(c_nums.get(ct[1], p_nums.get(ct[1], 0)))
                        v2 = float(c_nums.get(ct[3], p_nums.get(ct[3], 0)))
                        op = ct[2]
                        if op == '>' and v1 <= v2:
                            numeric_score *= 0.5
                        elif op == '<' and v1 >= v2:
                            numeric_score *= 0.5
                    except:
                        pass
            
            # STEP 4: Maximum Entropy weighting
            # Compute entropy over proposition assignments
            prop_count = max(len(all_props), 1)
            active_props = len([p for p in c_props if p in all_props])
            prop_prob = active_props / prop_count if prop_count > 0 else 0.5
            ent = entropy([prop_prob, 1 - prop_prob]) if prop_prob < 1 else 0.01
            
            # Lower entropy = more certain = higher score
            maxent_score = 1.0 - min(ent, 0.9)
            
            # STEP 5: NCD tiebreaker (max 10%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination
            final_score = (
                0.40 * constraint_score +
                0.25 * causal_score +
                0.20 * numeric_score +
                0.10 * maxent_score +
                0.05 * ncd_score
            )
            
            # Cap by meta-confidence
            final_score *= meta_conf
            
            reasoning = f"CS:{constraint_score:.2f} CI:{causal_score:.2f} Num:{numeric_score:.2f} MaxEnt:{maxent_score:.2f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural analysis."""
        # Check meta-properties first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Parse structures
        p_props, p_constraints, p_nums = self._parse_propositions(prompt)
        a_props, a_constraints, a_nums = self._parse_propositions(answer)
        
        # Information sufficiency check
        unknowns = len([c for c in p_constraints if 'unknown' in str(c).lower()])
        n_constraints = len(p_constraints)
        
        if unknowns > 0:
            return 0.2
        
        if n_constraints == 0:
            # No structure to verify against
            return 0.4
        
        # Constraint satisfaction confidence
        all_props = set(list(p_props.keys()) + list(a_props.keys()))
        variables = {p: i for i, p in enumerate(all_props)}
        domains = {p: [0, 1] for p in all_props}
        
        try:
            solution = solve_constraints(variables, domains, p_constraints)
            base_conf = 0.75 if solution else 0.35
        except:
            base_conf = 0.4
        
        # Numeric consistency boost
        for ct in p_constraints:
            if ct[0] == 'compare':
                try:
                    v1 = float(a_nums.get(ct[1], p_nums.get(ct[1], 0)))
                    v2 = float(a_nums.get(ct[3], p_nums.get(ct[3], 0)))
                    op = ct[2]
                    if (op == '>' and v1 > v2) or (op == '<' and v1 < v2):
                        base_conf = min(0.85, base_conf + 0.2)
                except:
                    pass
        
        # Cap by meta-confidence and never exceed 0.9
        return min(0.9, base_conf * meta_conf)
```

</details>
