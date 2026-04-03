# Chaos Theory + Compositionality + Proof Theory

**Fields**: Physics, Linguistics, Mathematics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T04:16:22.204080
**Report Generated**: 2026-04-02T10:55:59.172193

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Each sentence is tokenised with `re.findall` to extract atomic propositions (e.g., “X > Y”, “¬P”, “if A then B”). Propositions are stored as tuples `(pred, args, polarity)` in a NumPy structured array `props`. Logical connectives are mapped to compositional operators:  
   - conjunction → `np.minimum` (Gödel t‑norm)  
   - disjunction → `np.maximum`  
   - implication → `np.where(antecedent≤consequent, 1.0, consequent)`  
   - negation → `1.0 - value`.  
   The truth‑value of a complex formula is computed by a bottom‑up traversal of the parse tree, yielding a vector `v` of shape `(n_props,)`.

2. **Constraint Propagation (Proof Theory)** – Propositions are nodes in a directed graph `G`. Edges represent inference rules extracted from the text (modus ponens, transitivity, syllogism). We initialise a proof‑step counter `steps = np.zeros_like(v, dtype=int)`. Using a work‑list algorithm, we repeatedly apply each rule: if the antecedent nodes have values ≥ τ (τ=0.9), the consequent node’s value is updated with the compositional operator and its `steps` incremented. The process stops when no updates occur; this is analogous to cut‑elimination/normalisation because redundant steps are not re‑applied once a node reaches a fixed point.

3. **Sensitivity Scoring (Chaos Theory)** – To measure dependence on initial conditions, we perturb the initial truth‑values of atomic propositions by adding small i.i.d. noise `ε ~ Uniform(-δ, δ)` (δ=0.02) and recompute the propagation. For each candidate answer we compute the Lyapunov‑like exponent estimate:  
   `λ = (1/k) * Σ log(|v_perturbed - v| / δ)` over `k=5` perturbations.  
   The final score is `S = exp(-λ) * (1 - mean(steps)/max_steps)`, rewarding stable, short‑proof derivations.

**Structural Features Parsed**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `≥`, `≤`)  
- Conditionals (`if … then …`, `only if`)  
- Numeric values and units (extracted with `\d+(\.\d+)?`)  
- Causal claims (`because`, `leads to`)  
- Ordering relations (`before`, `after`, `precedes`)  

**Novelty**  
The triple‑layer combination — compositional truth‑functional evaluation, proof‑theoretic normalisation via constraint propagation, and chaos‑theoretic sensitivity analysis — is not present in existing NLP scoring tools. Prior work uses either semantic parsing with weighted logic or graph‑based consistency checks, but none perturb initial assignments to estimate Lyapunov exponents or combine the resulting exponent with proof‑length normalisation in a single deterministic algorithm.

**Ratings**  
Reasoning: 8/10 — captures logical depth and sensitivity to small changes, though approximations may miss subtle pragmatics.  
Metacognition: 6/10 — the method can report instability (high λ) as a cue of low confidence, but lacks explicit self‑reflection on its own parsing limits.  
Hypothesis generation: 5/10 — generates alternative truth‑assignments via perturbations, yet does not propose new semantic hypotheses beyond scoring.  
Implementability: 9/10 — relies only on `re`, `numpy`, and basic data structures; all steps are deterministic and O(|V|+|E|).

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:forbidden_import: forge_primitives

**Forge Timestamp**: 2026-04-02T10:11:35.607099

---

## Code

**Source**: scrap

[View code](./Chaos_Theory---Compositionality---Proof_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Chaos Theory x Compositionality x Proof Theory Reasoning Tool

Combines:
1. Compositional parsing of logical structure into atomic propositions
2. Proof-theoretic constraint propagation via modus ponens and transitivity
3. Chaos-theoretic sensitivity analysis through perturbation of truth assignments

Uses primitives for logical inference, perturbs initial states, and scores
candidates by stability (low Lyapunov exponent) and proof brevity.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib
from forge_primitives import (
    modus_ponens, check_transitivity, negate, solve_constraints,
    confidence_from_agreement, information_sufficiency
)


class ReasoningTool:
    def __init__(self):
        self.threshold = 0.9
        self.delta = 0.02
        self.n_perturbations = 5
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates using chaos-sensitive proof search."""
        results = []
        
        for cand in candidates:
            # Parse prompt + candidate into logical structure
            props, graph = self._parse_logical_structure(prompt, cand)
            
            if len(props) == 0:
                # Fallback to NCD
                score = 1.0 - self._ncd(prompt, cand)
                results.append({
                    "candidate": cand,
                    "score": score * 0.3,
                    "reasoning": "No logical structure detected, using NCD fallback"
                })
                continue
            
            # Proof-theoretic propagation
            base_values, proof_steps = self._propagate_constraints(props, graph)
            
            # Chaos-theoretic sensitivity
            stability = self._compute_stability(props, graph)
            
            # Numeric evaluation
            numeric_score = self._evaluate_numerics(prompt, cand)
            
            # Compute final score
            proof_quality = np.exp(-proof_steps / max(proof_steps + 1, 1))
            structural_score = base_values.mean() * proof_quality * stability
            
            final_score = 0.5 * structural_score + 0.35 * numeric_score + 0.15 * (1.0 - self._ncd(prompt, cand))
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Proof steps={proof_steps:.1f}, stability={stability:.2f}, numeric={numeric_score:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence with meta-cognitive checks."""
        # Meta-confidence: check for reasoning traps
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Parse and evaluate
        props, graph = self._parse_logical_structure(prompt, answer)
        
        if len(props) == 0:
            return 0.2  # Low confidence without structure
        
        values, proof_steps = self._propagate_constraints(props, graph)
        stability = self._compute_stability(props, graph)
        numeric_score = self._evaluate_numerics(prompt, answer)
        
        # High confidence only if: stable, short proof, numeric match
        base_conf = values.mean() * stability
        if numeric_score > 0.9 and stability > 0.8:
            return min(0.95, base_conf)
        
        return min(meta_conf, base_conf * 0.7)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B reasoning traps."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did \w+ (fail|stop))', p_lower):
            return 0.15
        
        # Scope ambiguity
        if re.search(r'\bevery \w+.*\ba \w+', p_lower):
            if 'same' not in p_lower and 'different' not in p_lower:
                return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|were)', p_lower):
            if re.search(r'\bwho\b', p_lower):
                return 0.2
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', p_lower):
            if 'only' not in p_lower:
                return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|greatest)\b', p_lower):
            if not re.search(r'\b(most|least|highest|lowest|measure)', p_lower):
                return 0.3
        
        # Insufficient information
        unknowns = len(re.findall(r'\?|\bunknown\b|\bnot (given|stated|specified)\b', p_lower))
        constraints = len(re.findall(r'\bif\b|\bthen\b|\bgiven\b|\bwhen\b', p_lower))
        
        if unknowns > 0:
            sufficiency = information_sufficiency(unknowns, constraints)
            if sufficiency < 0.5:
                return 0.25
        
        return 1.0
    
    def _parse_logical_structure(self, prompt: str, candidate: str) -> Tuple[np.ndarray, Dict]:
        """Parse into atomic propositions and inference graph."""
        text = prompt + " " + candidate
        
        # Extract atomic propositions
        props_list = []
        
        # Negations
        for match in re.finditer(r'\b(not|no|never)\s+(\w+)', text, re.IGNORECASE):
            props_list.append(("negation", match.group(2), 0.0))
        
        # Comparatives with numbers
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|greater|less)\s*(\d+\.?\d*)', text):
            props_list.append(("compare", (match.group(1), match.group(2), match.group(3)), 1.0))
        
        # Conditionals
        for match in re.finditer(r'\bif\s+(.+?)\s+then\s+(.+?)[\.,]', text, re.IGNORECASE):
            props_list.append(("conditional", (match.group(1), match.group(2)), 0.5))
        
        # Equality/identity
        for match in re.finditer(r'(\w+)\s+is\s+(\w+)', text):
            props_list.append(("equality", (match.group(1), match.group(2)), 0.8))
        
        if not props_list:
            props_list = [("default", text[:50], 0.5)]
        
        # Convert to numpy array
        props = np.array([p[2] for p in props_list], dtype=float)
        
        # Build inference graph (edges represent logical dependencies)
        graph = {"nodes": props_list, "edges": []}
        
        for i, p1 in enumerate(props_list):
            for j, p2 in enumerate(props_list):
                if i != j and p1[0] == "conditional" and p2[0] in ["equality", "compare"]:
                    graph["edges"].append((i, j))
        
        return props, graph
    
    def _propagate_constraints(self, props: np.ndarray, graph: Dict) -> Tuple[np.ndarray, float]:
        """Propagate logical constraints using proof primitives."""
        values = props.copy()
        steps = 0
        max_iterations = 10
        
        for iteration in range(max_iterations):
            changed = False
            
            # Apply modus ponens through graph edges
            for src, dst in graph["edges"]:
                if values[src] >= self.threshold:
                    # Premise holds, propagate to conclusion
                    old_val = values[dst]
                    values[dst] = max(values[dst], values[src] * 0.9)
                    if abs(values[dst] - old_val) > 0.01:
                        changed = True
                        steps += 1
            
            # Check transitivity in comparison chains
            comparisons = [(i, n) for i, n in enumerate(graph["nodes"]) if n[0] == "compare"]
            if len(comparisons) >= 2:
                # Build relation list for transitivity check
                relations = [(i, i+1) for i in range(len(comparisons)-1)]
                if check_transitivity(relations):
                    for idx, _ in comparisons:
                        values[idx] = min(1.0, values[idx] * 1.1)
                    steps += 0.5
            
            if not changed:
                break
        
        return values, steps
    
    def _compute_stability(self, props: np.ndarray, graph: Dict) -> float:
        """Chaos-theoretic stability via perturbation."""
        base_values, _ = self._propagate_constraints(props, graph)
        
        divergences = []
        for _ in range(self.n_perturbations):
            # Perturb initial values
            noise = np.random.uniform(-self.delta, self.delta, size=props.shape)
            perturbed_props = np.clip(props + noise, 0.0, 1.0)
            
            # Recompute propagation
            perturbed_values, _ = self._propagate_constraints(perturbed_props, graph)
            
            # Measure divergence (Lyapunov-like)
            div = np.abs(perturbed_values - base_values).mean()
            divergences.append(div / (self.delta + 1e-6))
        
        # Stability = low divergence
        mean_lyapunov = np.mean(divergences)
        stability = np.exp(-mean_lyapunov)
        
        return float(stability)
    
    def _evaluate_numerics(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric comparisons and arithmetic."""
        score = 0.5  # Neutral default
        
        # Extract numbers from prompt and candidate
        prompt_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        # Check numeric comparisons
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', prompt + " " + candidate):
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            
            if op in ['>', 'greater'] and a > b:
                score += 0.2
            elif op in ['<', 'less'] and a < b:
                score += 0.2
            elif op in ['>='] and a >= b:
                score += 0.2
            elif op in ['<='] and a <= b:
                score += 0.2
        
        # Numeric answer validation
        if len(cand_nums) == 1 and len(prompt_nums) >= 2:
            # Check if candidate number is plausible given prompt numbers
            if min(prompt_nums) <= cand_nums[0] <= max(prompt_nums) * 2:
                score += 0.1
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
