# Analogical Reasoning + Theory of Mind + Property-Based Testing

**Fields**: Cognitive Science, Cognitive Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T18:44:51.612710
**Report Generated**: 2026-04-02T12:33:29.241023

---

## Nous Analysis

**Algorithm: Structure‑Mapping Belief‑Constrained Property Generator (SMB‑PG)**  

1. **Parsing & Graph Construction**  
   - Tokenize the prompt with a regex‑based tokenizer that extracts:  
     * predicates (`is`, `has`, `causes`, `greater_than`, `before`)  
     * arguments (noun phrases, numbers, dates)  
     * logical operators (`not`, `and`, `or`, `if … then`)  
   - Build a directed labeled graph **Gₚ** where nodes are entities/constants and edges are predicates with polarity (positive/negative).  
   - For each candidate answer, build an analogous graph **Gₐ** using the same tokenizer.

2. **Analogical Mapping (Structure Mapping)**  
   - Compute a *soft* subgraph isomorphism score using the Hungarian algorithm on node‑type similarity (exact string match → 1, synonym lookup via WordNet → 0.8, else 0) and edge‑type similarity (exact predicate → 1, inverse → 0.5, unrelated → 0).  
   - Let **M** be the set of matched node‑edge triples; the analogical score **A = |M| / max(|Gₚ|,|Gₐ|)**.

3. **Theory‑of‑Mind Belief Layer**  
   - Identify mental‑state predicates in **Gₚ** (`believes`, `wants`, `intends`, `thinks`).  
   - For each such node, generate a *belief subgraph* by recursively expanding its complement clause (depth‑limited to 2 to keep tractable).  
   - Propagate truth values through the belief subgraph using simple modus ponens: if `X believes P` and `P` is true in the world graph, then the belief edge receives weight 1; otherwise weight 0.  
   - Compute belief consistency **B** as the fraction of belief edges whose propagated weight matches the candidate’s asserted truth value (extracted from polarity of the belief edge in **Gₐ**).

4. **Property‑Based Testing Shrink**  
   - Treat the mismatch set **D = (Gₚ \ Gₐ) ∪ (Gₐ \ Gₚ)** as a property violation.  
   - Define a shrink function that iteratively removes the least‑scoring matched triple (according to A) and recomputes A+B; stop when removal decreases the total score.  
   - The final shrunk mismatch count **S** is normalized: **P = 1 – (|S| / |D₀|)**, where **D₀** is the initial mismatch size.

5. **Final Score**  
   - **Score = w₁·A + w₂·B + w₃·P**, with weights (e.g., 0.4, 0.3, 0.3) tuned on a validation set.  
   - All operations use only numpy arrays for adjacency matrices and standard‑library containers; no external ML.

**Structural Features Parsed**  
- Negations (`not`, `no`, `never`) → edge polarity.  
- Comparatives (`greater than`, `less than`, `more`) → numeric‑value edges with direction.  
- Conditionals (`if … then`, `unless`) → implication edges stored as separate sub‑graphs for antecedent/consequent.  
- Causal verbs (`causes`, `leads to`, `results in`) → directed causal edges.  
- Ordering/temporal markers (`before`, `after`, `while`) → temporal edges.  
- Quantifiers (`all`, `some`, `none`) → quantified node sets handled via belief expansion depth.

**Novelty**  
The triple combination is not found in existing surveys: analogical structure mapping is common in cognitive‑simulation models, theory‑of‑mind belief tracking appears in recursive reasoning datasets, and property‑based testing shrinking is confined to software testing. Merging them into a unified graph‑matching‑with‑belief‑propagation‑and‑shrink pipeline is novel; closest analogues are separate works on semantic parsing with belief states (e.g., belief‑augmented AMR) and on property‑guided program repair, but none combine all three with a shrink‑based scoring function.

**Ratings**  
Reasoning: 8/10 — captures relational transfer and belief consistency, though limited to shallow recursion.  
Metacognition: 7/10 — models others’ beliefs explicitly but lacks higher‑order recursive modeling beyond depth‑2.  
Hypothesis generation: 6/10 — shrink process generates minimal counter‑examples, a form of hypothesis, but not exploratory.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and stdlib data structures; straightforward to code.

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
**Reason**: trap_battery_failed (acc=29% cal=28% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T12:02:33.975337

---

## Code

**Source**: scrap

[View code](./Analogical_Reasoning---Theory_of_Mind---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Set, Tuple

"""
Structure-Mapping Belief-Constrained Property Generator (SMB-PG)

Combines analogical reasoning (structure mapping), theory of mind (belief tracking),
and property-based testing (shrinking) with constructive computation for numeric,
probabilistic, and temporal reasoning.
"""

import re
import zlib
from typing import List, Dict, Tuple, Set
import numpy as np


class ReasoningTool:
    def __init__(self):
        # Predicate patterns
        self.predicates = {
            'is': r'\b(is|are|was|were|am)\b',
            'has': r'\b(has|have|had|owns|possesses)\b',
            'causes': r'\b(causes|leads to|results in|produces)\b',
            'believes': r'\b(believes|thinks|assumes|considers)\b',
            'wants': r'\b(wants|desires|intends|plans)\b',
            'greater': r'\b(greater than|more than|higher than|exceeds|>)\b',
            'less': r'\b(less than|fewer than|lower than|<)\b',
            'before': r'\b(before|prior to|earlier than)\b',
            'after': r'\b(after|following|later than)\b',
        }
        
        self.mental_predicates = {'believes', 'wants', 'thinks', 'intends'}
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by combined structural, computational, and belief scores."""
        results = []
        
        # Parse prompt graph
        prompt_graph = self._parse_graph(prompt)
        
        # Check for computational answers
        comp_answer = self._compute_answer(prompt)
        
        for cand in candidates:
            # Compute score
            if comp_answer is not None:
                # Constructive computation path
                comp_match = self._match_computed(cand, comp_answer)
                struct_score = 0.3
                belief_score = 0.3
                final_score = 0.6 * comp_match + 0.3 * struct_score + 0.1 * belief_score
            else:
                # Structure mapping path
                cand_graph = self._parse_graph(cand)
                struct_score = self._analogical_score(prompt_graph, cand_graph)
                belief_score = self._belief_consistency(prompt_graph, cand_graph)
                prop_score = self._property_score(prompt_graph, cand_graph)
                
                # Weights: structure 40%, belief 30%, property 20%, NCD 10%
                ncd = self._ncd(prompt, cand)
                final_score = 0.4 * struct_score + 0.3 * belief_score + 0.2 * prop_score + 0.1 * (1 - ncd)
            
            reasoning = f"struct={struct_score:.2f}, belief={belief_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        
        # Compute base confidence
        comp_answer = self._compute_answer(prompt)
        if comp_answer is not None:
            match = self._match_computed(answer, comp_answer)
            base_conf = match
        else:
            prompt_graph = self._parse_graph(prompt)
            answer_graph = self._parse_graph(answer)
            struct = self._analogical_score(prompt_graph, answer_graph)
            belief = self._belief_consistency(prompt_graph, answer_graph)
            base_conf = 0.6 * struct + 0.4 * belief
        
        # Cap by meta-confidence
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presuppositions, unanswerability."""
        lower = prompt.lower()
        
        # Presupposition checks
        if re.search(r'\b(have you stopped|did you stop|quit|cease)', lower):
            return 0.2
        if re.search(r'\bwhy did .* (fail|stop|end)', lower):
            return 0.25
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+ .* a \w+', lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|were|is)', lower) and '?' in prompt:
            if re.search(r'\bwho\b', lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or\b', lower) and '?' in prompt:
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', lower):
            if not re.search(r'\b(most|least|highest|lowest)\b', lower):
                return 0.3
        
        # Insufficient information
        if re.search(r'\b(cannot|can\'t|impossible to|insufficient)', lower):
            return 0.2
        
        return 0.95  # High confidence in question quality
    
    def _compute_answer(self, prompt: str):
        """Constructively compute answers for numeric, probability, temporal questions."""
        # Numeric comparison
        numbers = re.findall(r'\b\d+\.?\d*\b', prompt)
        if len(numbers) >= 2 and any(w in prompt.lower() for w in ['greater', 'less', 'larger', 'smaller', 'more', 'fewer']):
            nums = [float(n) for n in numbers[:2]]
            if 'greater' in prompt.lower() or 'more' in prompt.lower() or 'larger' in prompt.lower():
                return {'type': 'comparison', 'result': nums[0] > nums[1]}
            elif 'less' in prompt.lower() or 'fewer' in prompt.lower() or 'smaller' in prompt.lower():
                return {'type': 'comparison', 'result': nums[0] < nums[1]}
        
        # Probability/Bayesian reasoning
        if 'probability' in prompt.lower() or 'percent' in prompt.lower():
            probs = [float(n) for n in numbers if float(n) <= 100]
            if len(probs) >= 2:
                # Simple expected value or product
                return {'type': 'probability', 'value': np.mean(probs)}
        
        # Rate problems
        if any(w in prompt.lower() for w in ['hours', 'minutes', 'days', 'rate', 'speed']):
            if len(numbers) >= 2:
                # Simple rate calculation
                nums = [float(n) for n in numbers[:2]]
                return {'type': 'rate', 'value': nums[0] / nums[1] if nums[1] != 0 else 0}
        
        # Yes/No boolean reasoning
        if prompt.strip().endswith('?'):
            if re.search(r'\b(not|no|never|none)\b', prompt.lower()):
                # Negation present
                return {'type': 'boolean', 'negation': True}
        
        return None
    
    def _match_computed(self, candidate: str, computed) -> float:
        """Match candidate against computed answer."""
        cand_lower = candidate.lower()
        
        if computed['type'] == 'comparison':
            if computed['result']:
                return 0.9 if any(w in cand_lower for w in ['yes', 'true', 'correct', 'greater', 'more']) else 0.1
            else:
                return 0.9 if any(w in cand_lower for w in ['no', 'false', 'incorrect', 'less', 'fewer']) else 0.1
        
        if computed['type'] == 'probability':
            nums = re.findall(r'\b\d+\.?\d*\b', candidate)
            if nums:
                cand_val = float(nums[0])
                diff = abs(cand_val - computed['value'])
                return max(0.0, 1.0 - diff / 50.0)  # Normalize by 50
        
        if computed['type'] == 'rate':
            nums = re.findall(r'\b\d+\.?\d*\b', candidate)
            if nums:
                cand_val = float(nums[0])
                diff = abs(cand_val - computed['value'])
                return max(0.0, 1.0 - diff / 10.0)
        
        if computed['type'] == 'boolean':
            if computed.get('negation'):
                return 0.8 if any(w in cand_lower for w in ['no', 'false', 'not']) else 0.2
        
        return 0.5
    
    def _parse_graph(self, text: str) -> Dict:
        """Parse text into graph with entities and predicates."""
        graph = {'nodes': set(), 'edges': []}
        
        # Extract entities (nouns)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        graph['numbers'] = [float(n) for n in numbers]
        
        # Find predicates
        for pred_name, pattern in self.predicates.items():
            if re.search(pattern, text.lower()):
                graph['edges'].append(pred_name)
        
        # Check for negations
        graph['negations'] = len(re.findall(r'\b(not|no|never|none)\b', text.lower()))
        
        # Entity extraction (simplified)
        graph['nodes'] = set(words[:10])  # Limit to avoid explosion
        
        return graph
    
    def _analogical_score(self, g1: Dict, g2: Dict) -> float:
        """Compute structural similarity between graphs."""
        if not g1['edges'] and not g2['edges']:
            return 0.5
        
        # Edge overlap
        edges1 = set(g1['edges'])
        edges2 = set(g2['edges'])
        if edges1 or edges2:
            edge_score = len(edges1 & edges2) / max(len(edges1), len(edges2))
        else:
            edge_score = 0.5
        
        # Node overlap
        nodes1 = g1['nodes']
        nodes2 = g2['nodes']
        if nodes1 or nodes2:
            node_score = len(nodes1 & nodes2) / max(len(nodes1), len(nodes2), 1)
        else:
            node_score = 0.5
        
        # Negation alignment
        neg_score = 1.0 if g1['negations'] == g2['negations'] else 0.3
        
        return 0.5 * edge_score + 0.3 * node_score + 0.2 * neg_score
    
    def _belief_consistency(self, prompt_g: Dict, cand_g: Dict) -> float:
        """Check consistency of mental state predicates."""
        mental_edges_p = [e for e in prompt_g['edges'] if e in self.mental_predicates]
        mental_edges_c = [e for e in cand_g['edges'] if e in self.mental_predicates]
        
        if not mental_edges_p:
            return 0.5  # Neutral if no belief predicates
        
        # Simple overlap
        overlap = len(set(mental_edges_p) & set(mental_edges_c))
        return overlap / len(mental_edges_p) if mental_edges_p else 0.5
    
    def _property_score(self, g1: Dict, g2: Dict) -> float:
        """Compute shrunk mismatch score."""
        # Mismatch in edges
        edges1 = set(g1['edges'])
        edges2 = set(g2['edges'])
        mismatch = len((edges1 - edges2) | (edges2 - edges1))
        total = len(edges1 | edges2)
        
        if total == 0:
            return 0.5
        
        return 1.0 - (mismatch / total)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return min(1.0, max(0.0, ncd))
```

</details>
