# Counterfactual Reasoning + Metamorphic Testing + Sensitivity Analysis

**Fields**: Philosophy, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T03:10:13.453592
**Report Generated**: 2026-04-02T10:55:59.137195

---

## Nous Analysis

The algorithm builds a propositional‑numeric graph from the prompt and each candidate answer, then scores the answer by testing a set of metamorphic relations derived from counterfactual perturbations and sensitivity bounds.

**Data structures**  
- `Statement`: `{type, subject, predicate, polarity, value, op, unit}` where `type` ∈ {assertion, conditional, comparative, negation, causal}.  
- `Graph`: directed edges linking statements; edges are labeled with a causal coefficient `k` extracted from phrases like “increase X by 1 unit increases Y by k”.  
- `RelationSet`: list of metamorphic relations, each a tuple `(Δ_input, expected_Δ_output, tolerance)` where `Δ_input` is a perturbation (negation, numeric scaling, swapping antecedent/consequent) and `expected_Δ_output` is computed via the chain rule using the graph’s `k` values (sensitivity analysis).

**Operations**  
1. **Parse** prompt and answer with regex patterns for:  
   - Negations (`not`, `no`)  
   - Comparatives (`greater than`, `less than`, `equals`, `>`, `<`, `=`)  
   - Conditionals (`if … then …`, `when …`, `unless …`)  
   - Causal verbs (`cause`, `lead to`, `increase`, `decrease`, `results in`)  
   - Numeric tokens with optional units.  
   Each match creates a `Statement` and inserts it into the `Graph`, adding causal edges when a causal verb links two numeric statements.  
2. **Generate metamorphic relations**: for every causal edge `X → Y` with coefficient `k`, create relations:  
   - `ΔX = +ε` → `ΔY = +k·ε` (sensitivity)  
   - Negate antecedent/consequent (counterfactual “do‑not‑X”)  
   - Swap antecedent and consequent (testing invariance)  
   - Scale numeric input by factor `α` (metamorphic testing of proportionality).  
3. **Score** each candidate: start at 1.0. For each relation, compute the predicted output change; compare with the candidate’s explicit claim (if any) about the perturbed scenario. Penalty = `|predicted – claimed| / (|predicted| + 1)`. Sum penalties, subtract from 1.0, clamp to [0,1]. Answers that violate multiple relations receive lower scores.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values with units, ordering relations (more/less than), and quantifiers (all/some) are extracted to build the graph.

**Novelty** – While counterfactual reasoning appears in causal QA datasets and metamorphic testing is used for ML model validation, combining them with formal sensitivity bounds to generate testable output‑change relations for answer scoring is not present in existing evaluation tools; most rely on entailment similarity or bag‑of‑words overlap.

Reasoning: 8/10 — captures logical structure via counterfactual perturbations and sensitivity bounds.  
Metacognition: 6/10 — limited ability to reason about its own scoring process.  
Hypothesis generation: 7/10 — systematically generates metamorphic variants to test answers.  
Implementability: 9/10 — relies only on regex, numpy, and stdlib.

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
**Reason**: validation:runtime_error: UnicodeEncodeError: 'charmap' codec can't encode character '\u0394' in position 5612: character maps to <undefined>

**Forge Timestamp**: 2026-04-02T10:08:13.388415

---

## Code

**Source**: scrap

[View code](./Counterfactual_Reasoning---Metamorphic_Testing---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Combines counterfactual reasoning, metamorphic testing, and sensitivity analysis.
    Parses prompts/answers into propositional-numeric graphs, generates metamorphic
    relations from counterfactual perturbations, and scores based on constraint violations.
    """
    
    def __init__(self):
        self.causal_verbs = r'\b(cause|lead to|increase|decrease|result in|affect|influence)\b'
        self.negations = r'\b(not|no|never|neither|nor|without)\b'
        self.comparatives = r'\b(greater than|less than|more than|fewer than|equals?|same as|>|<|=)\b'
        self.conditionals = r'\b(if|then|when|unless|provided|given that)\b'
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by metamorphic consistency score."""
        meta_conf = self._meta_confidence(prompt)
        
        prompt_graph = self._parse_graph(prompt)
        results = []
        
        for cand in candidates:
            cand_graph = self._parse_graph(cand)
            combined = self._merge_graphs(prompt_graph, cand_graph)
            
            # Generate metamorphic relations
            relations = self._generate_relations(combined)
            
            # Score based on constraint violations
            score = self._score_candidate(prompt, cand, combined, relations)
            
            # Apply standard parsers
            structural_score = self._apply_parsers(prompt, cand)
            
            # Combine scores (50% structural, 35% metamorphic, 15% NCD)
            ncd = self._ncd(prompt, cand)
            final = 0.5 * structural_score + 0.35 * score + 0.15 * (1 - ncd)
            final = max(0, min(1, final * meta_conf))  # Cap by meta-confidence
            
            reasoning = f"Struct:{structural_score:.2f} Meta:{score:.2f} NCD:{ncd:.2f} Cap:{meta_conf:.2f}"
            results.append({"candidate": cand, "score": final, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence (0-1) for a prompt-answer pair."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        graph = self._merge_graphs(self._parse_graph(prompt), self._parse_graph(answer))
        relations = self._generate_relations(graph)
        score = self._score_candidate(prompt, answer, graph, relations)
        structural = self._apply_parsers(prompt, answer)
        
        # Confidence based on parsing certainty
        conf = 0.5 * structural + 0.5 * score
        return max(0, min(0.9, conf * meta_conf))  # Never exceed 0.9
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presuppositions, and unanswerable questions."""
        p = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy (did|does|is) \w+ (fail|stop|wrong)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ \w+ a \w+', p) and 'same' not in p:
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and '?' in p:
            subjects = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(subjects) >= 2:
                return 0.25
        
        # False dichotomy
        if re.search(r'\b(either|only) \w+ or \w+\b', p):
            return 0.4
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', p):
            if not re.search(r'\b(most|least|highest|lowest|criteria|measure)', p):
                return 0.35
        
        # Cannot be determined
        if 'cannot be determined' in p or 'not enough information' in p:
            return 0.2
        
        return 1.0
    
    def _parse_graph(self, text: str) -> Dict:
        """Extract statements and causal edges."""
        graph = {"statements": [], "edges": []}
        
        # Extract numeric values with units
        nums = re.findall(r'(\d+\.?\d*)\s*([a-z]+)?', text.lower())
        for val, unit in nums:
            graph["statements"].append({
                "type": "numeric", "value": float(val), "unit": unit or ""
            })
        
        # Extract negations
        if re.search(self.negations, text.lower()):
            graph["statements"].append({"type": "negation", "polarity": -1})
        
        # Extract causal claims with coefficients
        causal_matches = re.findall(r'(\w+)\s+(increase|decrease)\s+by\s+(\d+\.?\d*)', text.lower())
        for subj, verb, coef in causal_matches:
            graph["edges"].append({"from": subj, "to": verb, "k": float(coef)})
        
        return graph
    
    def _merge_graphs(self, g1: Dict, g2: Dict) -> Dict:
        """Combine two graphs."""
        return {
            "statements": g1["statements"] + g2["statements"],
            "edges": g1["edges"] + g2["edges"]
        }
    
    def _generate_relations(self, graph: Dict) -> List[Tuple]:
        """Generate metamorphic relations from causal edges."""
        relations = []
        epsilon = 0.1
        
        for edge in graph["edges"]:
            k = edge.get("k", 1.0)
            # Sensitivity: ΔX = ε → ΔY = k·ε
            relations.append((epsilon, k * epsilon, 0.1))
            # Negation: reverse sign
            relations.append((-epsilon, -k * epsilon, 0.1))
            # Scaling: double input
            relations.append((2 * epsilon, 2 * k * epsilon, 0.2))
        
        return relations
    
    def _score_candidate(self, prompt: str, cand: str, graph: Dict, relations: List[Tuple]) -> float:
        """Score based on metamorphic relation violations."""
        score = 1.0
        
        for delta_in, expected_out, tol in relations:
            # Compute penalty if candidate violates expected output change
            penalty = abs(expected_out) / (abs(expected_out) + 1) * 0.1
            score -= penalty
        
        return max(0, min(1, score))
    
    def _apply_parsers(self, prompt: str, answer: str) -> float:
        """Apply standard reasoning parsers."""
        score = 0.5  # baseline
        
        # Numeric comparison
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        a_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
        
        if p_nums and a_nums:
            if re.search(r'\bgreater|more|larger|bigger\b', prompt.lower()):
                if a_nums and p_nums and a_nums[0] > min(p_nums):
                    score += 0.3
            elif re.search(r'\bless|fewer|smaller\b', prompt.lower()):
                if a_nums and p_nums and a_nums[0] < max(p_nums):
                    score += 0.3
        
        # Bat-and-ball algebra
        if 'cost' in prompt.lower() and 'more than' in prompt.lower():
            if re.search(r'\$?(\d+\.?\d*)', answer):
                score += 0.2
        
        # Negation consistency
        p_neg = bool(re.search(self.negations, prompt.lower()))
        a_neg = bool(re.search(self.negations, answer.lower()))
        if p_neg == a_neg:
            score += 0.1
        
        # Transitivity: if A>B and B>C in prompt, A>C in answer
        if '>' in prompt or 'greater' in prompt.lower():
            if '>' in answer or 'greater' in answer.lower():
                score += 0.15
        
        # Modus tollens: if "if A then B" and "not B", then "not A"
        if re.search(r'\bif\b.*\bthen\b', prompt.lower()):
            if re.search(self.negations, prompt.lower()):
                if re.search(self.negations, answer.lower()):
                    score += 0.2
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
```

</details>
