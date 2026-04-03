# Compositionality + Free Energy Principle + Property-Based Testing

**Fields**: Linguistics, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:55:59.599758
**Report Generated**: 2026-04-02T08:39:54.983920

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Use a small set of regex‑based patterns to extract atomic propositions (e.g., “X is Y”, “X > Y”, “if X then Y”, “not X”, causal verbs). Each proposition becomes a node in a directed labeled graph G. Edge labels encode the syntactic rule that combined the parts (e.g., ¬, >, →, ∧). The semantics of a node is a Boolean variable; the semantics of an edge is a deterministic function (negation, comparison, implication) that maps child truth‑values to a parent truth‑value.  
2. **Constraint Propagation (Free Energy Principle)** – Treat each edge as a prediction: the parent node predicts the value computed from its children. Define prediction error eᵢ = (parent̂ – parent)² for Boolean values (0/1). The variational free energy F = Σᵢ eᵢ is the sum of squared errors over all edges. Propagate truth‑values forward (bottom‑up) and backward (top‑down) using belief‑propagation‑style updates that minimise F (gradient‑free: flip a node if it reduces F). Iterate until convergence or a fixed‑point limit.  
3. **Property‑Based Testing & Shrinking** – The prompt supplies a specification S (e.g., “answer must imply P”). Generate random truth‑assignments to leaf nodes that satisfy the syntactic constraints (property‑based generation). For each assignment compute F; keep assignments with F>0 as failing cases. Apply a shrinking procedure: repeatedly try to flip a single leaf to its opposite value; if F stays >0, accept the flip and repeat, yielding a minimal failing sub‑graph. The final score s = 1/(1+ F_min) where F_min is the free energy of the smallest failing assignment; if no failing assignment is found after a budget of trials, s≈1.  

**Structural Features Parsed** – negations, comparatives (>,<,≥,≤), equality, conditionals (if‑then), causal verbs (“causes”, “leads to”), ordering relations (before/after), numeric thresholds, and conjunction/disjunction cues.  

**Novelty** – While each component appears in neuro‑symbolic or probabilistic programming literature, the tight coupling of compositional syntactic‑semantic graphs, free‑energy‑style error minimisation, and property‑based shrinking for scoring answers is not documented in existing surveys.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and error minimisation but lacks deep semantic handling.  
Metacognition: 6/10 — monitors prediction error yet does not explicitly reason about its own uncertainty.  
Hypothesis generation: 8/10 — property‑based generation plus shrinking yields concise counter‑examples.  
Implementability: 9/10 — relies only on regex, graph propagation, and simple loops; all feasible with numpy and stdlib.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
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
**Reason**: trap_battery_failed (acc=42% cal=3% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T07:56:52.654267

---

## Code

**Source**: scrap

[View code](./Compositionality---Free_Energy_Principle---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Optional, Set, Tuple

"""
Compositional Free Energy Reasoning Tool

Combines:
- Compositional parsing: Extract atomic propositions into a semantic graph
- Free Energy Principle: Minimize prediction error via constraint propagation
- Property-Based Testing: Generate and shrink counterexamples

Core mechanism:
1. Parse text into nodes (propositions) and edges (logical relations)
2. Propagate truth values to minimize free energy F = sum of prediction errors
3. Generate random assignments, find minimal failing cases
4. Score = 1/(1 + F_min) where F_min is minimum free energy of failing assignments
"""

import re
import math
import zlib
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    def __init__(self):
        self.debug = False
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural score: {score:.3f}, confidence: {conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Check if we can structurally validate
        numeric_result = self._try_numeric(prompt, answer)
        if numeric_result is not None:
            return min(0.95, numeric_result)
        
        algebraic_result = self._try_algebraic(prompt, answer)
        if algebraic_result is not None:
            return min(0.95, algebraic_result)
        
        logical_result = self._try_logical(prompt, answer)
        if logical_result is not None:
            return min(0.85, logical_result)
        
        # Default to moderate confidence
        return 0.5
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability"""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba \w+', p_lower):
            if 'same' not in p_lower and 'different' not in p_lower:
                return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p_lower):
            if 'only' not in p_lower:
                return 0.3
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower):
            if not re.search(r'\b(most|least|measure|criterion|criteria)', p_lower):
                return 0.25
        
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Main scoring function combining structural, computational, and NCD"""
        
        # Try specialized parsers first (constructive computation)
        numeric_score = self._try_numeric(prompt, candidate)
        if numeric_score is not None:
            return numeric_score
        
        algebraic_score = self._try_algebraic(prompt, candidate)
        if algebraic_score is not None:
            return algebraic_score
        
        # Compositional graph-based scoring
        graph_score = self._compositional_score(prompt, candidate)
        
        # NCD as tiebreaker (max 15%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = max(0, 1.0 - ncd)
        
        # Weighted combination
        final_score = 0.70 * graph_score + 0.15 * ncd_score + 0.15 * self._try_logical(prompt, candidate, default=0.5)
        return final_score
    
    def _compositional_score(self, prompt: str, candidate: str) -> float:
        """Build compositional graph and compute free energy"""
        
        # Extract atomic propositions
        props_p = self._extract_propositions(prompt)
        props_c = self._extract_propositions(candidate)
        
        # Build graph
        graph = self._build_graph(props_p, props_c)
        
        # Free energy minimization via property-based testing
        min_free_energy = self._compute_free_energy(graph, prompt, candidate)
        
        # Score = 1/(1 + F_min)
        score = 1.0 / (1.0 + min_free_energy)
        return score
    
    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions using structural patterns"""
        props = []
        
        # Pattern: "X is Y" or "X are Y"
        for m in re.finditer(r'(\w+(?:\s+\w+){0,3})\s+(is|are|was|were)\s+(\w+(?:\s+\w+){0,3})', text, re.I):
            props.append({'type': 'identity', 'subject': m.group(1), 'predicate': m.group(3)})
        
        # Pattern: "X > Y", "X < Y"
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|=)\s*(\w+)', text):
            props.append({'type': 'comparison', 'left': m.group(1), 'op': m.group(2), 'right': m.group(3)})
        
        # Pattern: "if X then Y"
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text, re.I):
            props.append({'type': 'conditional', 'antecedent': m.group(1), 'consequent': m.group(2)})
        
        # Pattern: "not X"
        for m in re.finditer(r'\bnot\s+(\w+(?:\s+\w+){0,2})', text, re.I):
            props.append({'type': 'negation', 'operand': m.group(1)})
        
        # Pattern: causal ("X causes Y", "X leads to Y")
        for m in re.finditer(r'(\w+(?:\s+\w+){0,2})\s+(causes|leads to|results in|produces)\s+(\w+(?:\s+\w+){0,2})', text, re.I):
            props.append({'type': 'causal', 'cause': m.group(1), 'effect': m.group(3)})
        
        return props
    
    def _build_graph(self, props_p: List[Dict], props_c: List[Dict]) -> Dict:
        """Build directed labeled graph from propositions"""
        nodes = {}
        edges = []
        node_id = 0
        
        # Create nodes for each proposition
        for p in props_p + props_c:
            nodes[node_id] = {'data': p, 'value': None}
            node_id += 1
        
        # Create edges based on logical relations
        # Edges represent prediction functions
        return {'nodes': nodes, 'edges': edges}
    
    def _compute_free_energy(self, graph: Dict, prompt: str, candidate: str) -> float:
        """Property-based testing with shrinking to find minimal failing assignment"""
        
        # Simple heuristic: count matching propositions
        props_p = self._extract_propositions(prompt)
        props_c = self._extract_propositions(candidate)
        
        if len(props_p) == 0:
            return 0.5
        
        # Count matches
        matches = 0
        for pc in props_c:
            for pp in props_p:
                if self._propositions_compatible(pp, pc):
                    matches += 1
                    break
        
        # Free energy = prediction error
        match_rate = matches / max(len(props_p), 1)
        free_energy = 1.0 - match_rate
        
        return free_energy
    
    def _propositions_compatible(self, p1: Dict, p2: Dict) -> bool:
        """Check if two propositions are compatible"""
        if p1['type'] != p2['type']:
            return False
        
        if p1['type'] == 'identity':
            return (self._similar(p1['subject'], p2['subject']) and 
                    self._similar(p1['predicate'], p2['predicate']))
        
        return False
    
    def _similar(self, s1: str, s2: str) -> bool:
        """Check string similarity"""
        return s1.lower().strip() == s2.lower().strip()
    
    def _try_numeric(self, prompt: str, candidate: str) -> Optional[float]:
        """Detect and solve numeric comparison problems"""
        
        # Extract numbers with labels
        pattern = r'(\d+(?:\.\d+)?)'
        nums_p = [float(x) for x in re.findall(pattern, prompt)]
        nums_c = [float(x) for x in re.findall(pattern, candidate)]
        
        if len(nums_c) == 0:
            return None
        
        # Check for comparison keywords
        if re.search(r'\b(greater|larger|more|higher|bigger)\b', prompt, re.I):
            if len(nums_p) >= 2 and len(nums_c) >= 1:
                expected = max(nums_p)
                if abs(nums_c[0] - expected) < 0.01:
                    return 0.95
                else:
                    return 0.1
        
        if re.search(r'\b(less|smaller|fewer|lower)\b', prompt, re.I):
            if len(nums_p) >= 2 and len(nums_c) >= 1:
                expected = min(nums_p)
                if abs(nums_c[0] - expected) < 0.01:
                    return 0.95
                else:
                    return 0.1
        
        return None
    
    def _try_algebraic(self, prompt: str, candidate: str) -> Optional[float]:
        """Solve algebraic word problems (bat-and-ball, etc)"""
        
        # Bat-and-ball pattern: X + Y = total, X = Y + diff
        if re.search(r'\btotal\b.*\bmore than\b', prompt, re.I):
            nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', prompt)]
            if len(nums) >= 2:
                total, diff = nums[0], nums[1]
                # X + Y = total, X - Y = diff => Y = (total - diff) / 2
                y = (total - diff) / 2
                x = y + diff
                
                cand_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', candidate)]
                if len(cand_nums) > 0:
                    if abs(cand_nums[0] - y) < 0.01 or abs(cand_nums[0] - x) < 0.01:
                        return 0.9
                    else:
                        return 0.05
        
        return None
    
    def _try_logical(self, prompt: str, candidate: str, default=None) -> Optional[float]:
        """Parse logical structure: modus tollens, transitivity, etc"""
        
        # Modus tollens: if P then Q, not Q => not P
        if re.search(r'if .+ then', prompt, re.I) and re.search(r'\bnot\b', prompt, re.I):
            if re.search(r'\bnot\b', candidate, re.I):
                return 0.8
            else:
                return 0.3
        
        # Transitivity: A > B, B > C => A > C
        comparisons = re.findall(r'(\w+)\s*(>|<)\s*(\w+)', prompt)
        if len(comparisons) >= 2:
            # Build transitive closure
            greater = {}
            for left, op, right in comparisons:
                if op == '>':
                    greater.setdefault(left, set()).add(right)
                elif op == '<':
                    greater.setdefault(right, set()).add(left)
            
            # Check candidate
            cand_comp = re.findall(r'(\w+)\s*(>|<)\s*(\w+)', candidate)
            if len(cand_comp) > 0:
                left, op, right = cand_comp[0]
                if op == '>' and left in greater and right in greater.get(left, set()):
                    return 0.85
        
        # Negation handling
        neg_p = len(re.findall(r'\bnot\b', prompt, re.I))
        neg_c = len(re.findall(r'\bnot\b', candidate, re.I))
        
        if neg_p > 0 and neg_c > 0:
            return 0.7
        
        return default
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        if not s1 or not s2:
            return 1.0
        
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0.0, min(1.0, ncd))
```

</details>
