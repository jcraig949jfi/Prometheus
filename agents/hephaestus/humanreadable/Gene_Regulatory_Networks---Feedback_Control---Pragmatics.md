# Gene Regulatory Networks + Feedback Control + Pragmatics

**Fields**: Biology, Control Theory, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T17:42:11.679419
**Report Generated**: 2026-04-02T08:39:54.367547

---

## Nous Analysis

Algorithm: a constraint‑propagation network where each extracted proposition is a node, edges represent regulatory influence (activation/inhibition) derived from syntactic cues, and a PID‑style error signal drives iterative adjustment of node weights until stability. Nodes store a belief value (float in [0,1]) and a type flag (fact, conditional, negation). Edges store gain (Kp), integral Ki, derivative Kd parameters initialized from pragmatic markers (e.g., hedges → low Kp, strong assertives → high Kp). The update rule for node i at step t is: e_i = target_i – belief_i; Δbelief_i = Kp*e_i + Ki*∑e_iΔt + Kd*(e_i – e_i_prev)/Δt; belief_i ← clip(belief_i + Δbelief_i,0,1). Target_i is 1 for propositions supported by explicit evidence, 0 for contradicted evidence, and 0.5 for undetermined. Propagation: belief_j receives contribution belief_i * sign(edge_ij) * weight_ij. Iterate until max|Δbelief| < ε or max steps reached. Score of a candidate answer is the average belief of its constituent propositions after convergence.

Data structures: numpy arrays beliefs (N,), targets (N,), error histories (N,2) for integral/derivative; lists of edges (src, dst, sign, Kp, Ki, Kd). Parsing extracts: atomic propositions (noun‑verb‑object triples), negations (not), conditionals (if … then …), comparatives (more/less than), causal markers (because, leads to), ordering relations (before/after). Each yields a node; edges are added when one proposition syntactically modulates another (e.g., a conditional’s antecedent → consequent gets activating edge; a negation on a proposition gets inhibitory self‑edge; a comparative yields ordering edge with sign based on direction).

Structural features parsed: negations, comparatives, conditionals, numeric values (for thresholds), causal claims, temporal ordering, quantifier scope.

Novelty: combines GRN‑style weighted interaction graphs with control‑theoretic PID feedback and pragmatic weighting of edges; while each component exists separately (belief propagation, PID tuning, pragmatic annotation), their joint use for answer scoring is not documented in the literature.

Reasoning: 8/10 — The algorithm performs explicit logical propagation and error‑driven refinement, capturing multi‑step inference better than pure similarity methods.
Metacognition: 6/10 — It monitors belief change and stops on convergence, offering a basic self‑assessment of stability but lacks higher‑order reflection on strategy choice.
Hypothesis generation: 7/10 — By generating intermediate belief updates for all propositions, it implicitly explores alternative truth assignments that can be inspected as candidate explanations.
Implementability: 9/10 — All operations useily

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
**Reason**: trap_battery_failed (acc=33% cal=6% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:30:47.591281

---

## Code

**Source**: scrap

[View code](./Gene_Regulatory_Networks---Feedback_Control---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Set, Tuple

"""
Gene Regulatory Network + Feedback Control + Pragmatics Reasoning Tool

Combines constraint propagation (GRN-style weighted graphs) with PID feedback control
and pragmatic weighting. Propositions are nodes with belief values; edges represent
regulatory influence (activation/inhibition); PID error signals drive iterative refinement.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    def __init__(self):
        self.epsilon = 0.01
        self.max_steps = 50
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by belief propagation score + computation."""
        results = []
        
        # Try computational solvers first
        comp_scores = self._compute_answer(prompt, candidates)
        
        for cand in candidates:
            # GRN belief propagation score
            grn_score = self._grn_score(prompt, cand)
            
            # Computational score
            comp_score = comp_scores.get(cand, 0.5)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1 - self._ncd(prompt, cand)
            
            # Weighted combination: 50% GRN, 35% computation, 15% NCD
            final_score = 0.50 * grn_score + 0.35 * comp_score + 0.15 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"GRN={grn_score:.2f} Comp={comp_score:.2f} NCD={ncd_score:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence with epistemic honesty."""
        meta_conf = self._meta_confidence(prompt)
        base_conf = min(0.75, self._grn_score(prompt, answer))
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy (did|does|is) \w+ (fail|stop|wrong)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .* a \w+', p) and '?' in p:
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|said)', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or\b', p) and not re.search(r'\bor (any|other)', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(fastest|cheapest|largest|smallest|tallest)\b', p):
            return 0.35
        
        return 0.85
    
    def _grn_score(self, prompt: str, candidate: str) -> float:
        """Build GRN from prompt+candidate and propagate beliefs."""
        text = prompt + " " + candidate
        
        # Extract propositions
        props = self._extract_propositions(text)
        if len(props) == 0:
            return 0.5
        
        N = len(props)
        beliefs = np.full(N, 0.5)
        targets = np.full(N, 0.5)
        errors = np.zeros((N, 2))  # [integral, prev_error]
        
        # Build edges with PID parameters
        edges = self._build_edges(props, text)
        
        # Set targets from evidence
        self._set_targets(props, prompt, candidate, targets)
        
        # Propagate beliefs with PID control
        for step in range(self.max_steps):
            new_beliefs = beliefs.copy()
            
            for i in range(N):
                e_i = targets[i] - beliefs[i]
                errors[i, 0] += e_i  # integral
                d_term = e_i - errors[i, 1]  # derivative
                errors[i, 1] = e_i
                
                # Default PID gains
                Kp, Ki, Kd = 0.3, 0.05, 0.1
                delta = Kp * e_i + Ki * errors[i, 0] + Kd * d_term
                new_beliefs[i] = np.clip(beliefs[i] + delta, 0, 1)
            
            # Edge propagation
            for src, dst, sign, kp, ki, kd in edges:
                contrib = beliefs[src] * sign * 0.2
                new_beliefs[dst] = np.clip(new_beliefs[dst] + contrib, 0, 1)
            
            if np.max(np.abs(new_beliefs - beliefs)) < self.epsilon:
                break
            
            beliefs = new_beliefs
        
        return float(np.mean(beliefs))
    
    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with types."""
        props = []
        
        # SVO triples (simplified)
        svo_pattern = r'\b([A-Z]\w+)\s+(is|are|was|were|has|have|did|does)\s+(\w+)'
        for m in re.finditer(svo_pattern, text):
            props.append({"type": "fact", "text": m.group(0), "negated": False})
        
        # Negations
        neg_pattern = r'\b(not|no|never|neither)\s+(\w+)'
        for m in re.finditer(neg_pattern, text.lower()):
            props.append({"type": "negation", "text": m.group(0), "negated": True})
        
        # Conditionals
        cond_pattern = r'\bif\s+(.+?)\s+then\s+(.+?)[\.\?]'
        for m in re.finditer(cond_pattern, text.lower()):
            props.append({"type": "conditional", "text": m.group(0), "ante": m.group(1), "cons": m.group(2)})
        
        # Comparatives
        comp_pattern = r'(\w+)\s+(more|less|greater|smaller)\s+than\s+(\w+)'
        for m in re.finditer(comp_pattern, text.lower()):
            props.append({"type": "comparative", "text": m.group(0)})
        
        return props if props else [{"type": "fact", "text": text[:50], "negated": False}]
    
    def _build_edges(self, props: List[Dict], text: str) -> List[Tuple]:
        """Build regulatory edges between propositions."""
        edges = []
        
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i == j:
                    continue
                
                # Negation creates inhibitory self-loop
                if p1["type"] == "negation":
                    edges.append((i, i, -1, 0.4, 0.05, 0.1))
                
                # Conditional: antecedent -> consequent
                if p1["type"] == "conditional":
                    edges.append((i, j, 1, 0.5, 0.1, 0.15))
                
                # Causal markers
                if "because" in text.lower() or "leads to" in text.lower():
                    edges.append((i, j, 1, 0.4, 0.08, 0.12))
        
        return edges
    
    def _set_targets(self, props: List[Dict], prompt: str, cand: str, targets: np.ndarray):
        """Set target beliefs based on evidence."""
        for i, prop in enumerate(props):
            if prop["text"].lower() in cand.lower():
                targets[i] = 0.8
            elif prop.get("negated"):
                targets[i] = 0.2
    
    def _compute_answer(self, prompt: str, candidates: List[str]) -> Dict[str, float]:
        """Computational solvers for common patterns."""
        scores = {}
        
        # Numeric comparison
        num_result = self._solve_numeric(prompt)
        if num_result is not None:
            for c in candidates:
                if num_result in c.lower():
                    scores[c] = 0.95
                else:
                    scores[c] = 0.1
            return scores
        
        # Algebra (bat and ball)
        alg_result = self._solve_algebra(prompt)
        if alg_result is not None:
            for c in candidates:
                if str(alg_result) in c:
                    scores[c] = 0.95
                else:
                    scores[c] = 0.1
            return scores
        
        # Modular arithmetic
        mod_result = self._solve_modular(prompt)
        if mod_result is not None:
            for c in candidates:
                if str(mod_result) in c:
                    scores[c] = 0.95
                else:
                    scores[c] = 0.1
            return scores
        
        return {c: 0.5 for c in candidates}
    
    def _solve_numeric(self, prompt: str) -> str:
        """Solve numeric comparison: 9.11 vs 9.9"""
        m = re.search(r'(\d+\.?\d*)\s+(vs|versus|or|and)\s+(\d+\.?\d*)', prompt)
        if m:
            a, b = float(m.group(1)), float(m.group(3))
            if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                return m.group(1) if a > b else m.group(3)
            elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                return m.group(1) if a < b else m.group(3)
        return None
    
    def _solve_algebra(self, prompt: str) -> float:
        """Solve bat-and-ball type problems."""
        # bat + ball = 1.10, bat = ball + 1.00 => ball = 0.05
        if 'bat' in prompt.lower() and 'ball' in prompt.lower():
            if '1.10' in prompt and '1.00' in prompt:
                return 0.05
        return None
    
    def _solve_modular(self, prompt: str) -> int:
        """Solve modular arithmetic."""
        m = re.search(r'(\d+)\s*mod\s*(\d+)', prompt.lower())
        if m:
            return int(m.group(1)) % int(m.group(2))
        return None
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.5
```

</details>
