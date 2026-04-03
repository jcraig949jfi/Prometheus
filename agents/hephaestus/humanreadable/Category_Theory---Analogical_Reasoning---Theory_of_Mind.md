# Category Theory + Analogical Reasoning + Theory of Mind

**Fields**: Mathematics, Cognitive Science, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T08:04:45.061456
**Report Generated**: 2026-04-02T10:00:37.242412

---

## Nous Analysis

**Algorithm: Relational Functor Mapping with Intentional Attribution (RFMIA)**  

1. **Data structures**  
   - *Prompt graph* `Gp = (Vp, Ep)`: each vertex `v` is a typed entity (noun phrase, numeric literal, or propositional atom) extracted via regex patterns for negations, comparatives, conditionals, causal connectives, and ordering relations. Edges `e = (v_i, r, v_j)` carry a relation label `r ∈ {=, ≠, <, >, →, ∧, ¬, causes, enables}`.  
   - *Candidate graph* `Gc` built identically from each answer.  
   - *Intent model* `I = {b, d, intent}`: a triple of belief‑state flags (true/false) for each agent mentioned, derived from modal verbs (“think”, “believe”, “want”) and negation scope.  

2. **Operations**  
   - **Functor extraction**: Define a mapping `F: Vp → Vc` that preserves vertex types (entity → entity, number → number, proposition → proposition). Implemented as a bipartite matching solved with the Hungarian algorithm (numpy linear‑sum‑assignment) maximizing a similarity matrix `S_ij` where `S_ij = 1` if types match and relation‑label sets intersect, else `0`.  
   - **Natural‑transformation check**: For each edge `(v_i, r, v_j)` in `Gp`, verify that the image under `F` yields an edge `(F(v_i), r', F(v_j))` in `Gc` with `r'` entailed by `r` using a small rule table (e.g., `<` maps to `≤` or `=`, `→` maps to `¬∨`). Count satisfied edges → `struct_score`.  
   - **Theory‑of‑Mind adjustment**: For each agent `a` in `I`, propagate belief flags through the graph using modal‑logic rules (K axiom: if `a believes p` and `p → q` then `a believes q`). Compute belief‑consistency penalty `mind_penalty = Σ|belief_p(Gp) – belief_p(Gc)|`.  
   - **Final score**: `score = w1·struct_score / |Ep| – w2·mind_penalty`, with `w1=0.7, w2=0.3`. Scores are normalized to `[0,1]`.  

3. **Parsed structural features**  
   - Negations (`not`, `no`), comparatives (`more than`, `less than`), conditionals (`if … then`), causal claims (`because`, `leads to`), ordering relations (`first`, `before`, `after`), numeric values and units, and modal‑attributive verbs indicating beliefs/desires.  

4. **Novelty**  
   The combination mirrors functorial semantics (category theory) with structure‑mapping (analogy) and recursive mentalizing (ToM). While each component appears separately in AI‑symbiosis work (e.g., Discourse Representation Theory, Structure‑Mapping Engine, BDI agents), their exact integration—functor‑based vertex matching, natural‑transformation edge validation, and belief‑propagation penalty—has not been published as a unified scoring algorithm.  

**Ratings**  
Reasoning: 8/10 — captures relational and modal structure better than pure similarity methods.  
Metacognition: 7/10 — models belief states but limited to first‑order recursion.  
Hypothesis generation: 6/10 — can propose consistent mappings but does not generate novel hypotheses beyond graph completion.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and deterministic rule tables.

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
**Reason**: validation:forbidden_import: scipy

**Forge Timestamp**: 2026-04-02T09:41:09.519373

---

## Code

**Source**: scrap

[View code](./Category_Theory---Analogical_Reasoning---Theory_of_Mind/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import scipy
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Relational Functor Mapping with Intentional Attribution (RFMIA).
    
    Combines Category Theory (functors preserving structure), Analogical Reasoning
    (structure-mapping), and Theory of Mind (belief tracking). Parses text into
    relational graphs, finds functor mappings via Hungarian algorithm, validates
    natural transformations, and adjusts scores by belief consistency.
    """
    
    def __init__(self):
        self.relations = {'=', '!=', '<', '>', '->', '&', '~', 'causes', 'enables'}
        self.entailment_rules = {
            '<': {'<', '<=', '!='},
            '>': {'>', '>=', '!='},
            '=': {'=', '<=', '>='},
            '->': {'->', '~|'},
            'causes': {'causes', 'enables'},
            'enables': {'enables'}
        }
    
    def _extract_graph(self, text: str) -> Tuple[List[Tuple[str, str]], List[Tuple[int, str, int]], Dict]:
        """Parse text into graph: vertices (entities, numbers, propositions), edges (relations)."""
        text = text.lower()
        vertices = []
        edges = []
        intent = {'beliefs': {}, 'desires': {}}
        
        # Extract numeric literals
        for match in re.finditer(r'\b(\d+\.?\d*)\b', text):
            vertices.append((match.group(1), 'number'))
        
        # Extract entities (noun phrases - simple heuristic)
        words = re.findall(r'\b[a-z]+\b', text)
        entities = [w for w in words if len(w) > 2 and w not in {'the', 'and', 'but', 'for', 'with', 'not', 'more', 'less', 'than'}]
        for ent in entities[:10]:  # Limit vertices
            vertices.append((ent, 'entity'))
        
        # Extract propositions from conditionals
        if_then = re.finditer(r'if\s+([^,]+?)\s+then\s+([^,\.]+)', text)
        for match in if_then:
            ant, cons = match.group(1).strip(), match.group(2).strip()
            vertices.append((ant, 'proposition'))
            vertices.append((cons, 'proposition'))
        
        # Build edges from relational patterns
        v_list = [(v[0], i) for i, v in enumerate(vertices)]
        
        # Comparatives
        for match in re.finditer(r'(\w+)\s+(?:is\s+)?(?:more|less|greater|smaller)\s+than\s+(\w+)', text):
            a, b = match.group(1), match.group(2)
            idx_a = next((i for v, i in v_list if v == a), None)
            idx_b = next((i for v, i in v_list if v == b), None)
            if idx_a is not None and idx_b is not None:
                edges.append((idx_a, '<' if 'less' in match.group(0) or 'smaller' in match.group(0) else '>', idx_b))
        
        # Negations
        for match in re.finditer(r'not\s+(\w+)', text):
            term = match.group(1)
            idx = next((i for v, i in v_list if v == term), None)
            if idx is not None:
                edges.append((idx, '~', idx))
        
        # Causals
        for match in re.finditer(r'(\w+)\s+(?:causes|leads to|enables)\s+(\w+)', text):
            a, b = match.group(1), match.group(2)
            idx_a = next((i for v, i in v_list if v == a), None)
            idx_b = next((i for v, i in v_list if v == b), None)
            if idx_a is not None and idx_b is not None:
                rel = 'causes' if 'cause' in match.group(0) else 'enables'
                edges.append((idx_a, rel, idx_b))
        
        # Theory of Mind: extract beliefs
        for match in re.finditer(r'(\w+)\s+(?:thinks|believes|wants)\s+([^,\.]+)', text):
            agent, belief = match.group(1), match.group(2).strip()
            intent['beliefs'][agent] = belief
        
        return vertices, edges, intent
    
    def _hungarian_match(self, vp: List, vc: List) -> Dict[int, int]:
        """Find functor mapping F: Vp -> Vc preserving types via Hungarian algorithm."""
        if not vp or not vc:
            return {}
        
        n_p, n_c = len(vp), len(vc)
        cost = np.zeros((n_p, n_c))
        
        for i, (val_p, type_p) in enumerate(vp):
            for j, (val_c, type_c) in enumerate(vc):
                if type_p == type_c:
                    cost[i, j] = 1.0
                    if val_p == val_c:
                        cost[i, j] = 2.0  # Bonus for exact match
        
        # Maximize similarity -> minimize negative cost
        from scipy.optimize import linear_sum_assignment
        row_ind, col_ind = linear_sum_assignment(-cost)
        
        mapping = {}
        for i, j in zip(row_ind, col_ind):
            if cost[i, j] > 0:  # Only valid matches
                mapping[i] = j
        
        return mapping
    
    def _natural_transformation_score(self, ep: List, ec: List, mapping: Dict) -> float:
        """Check edge preservation under functor mapping (natural transformation)."""
        if not ep:
            return 0.0
        
        satisfied = 0
        for i, r, j in ep:
            if i in mapping and j in mapping:
                fi, fj = mapping[i], mapping[j]
                # Check if image edge exists with entailed relation
                for ic, rc, jc in ec:
                    if ic == fi and jc == fj:
                        if rc in self.entailment_rules.get(r, {r}):
                            satisfied += 1
                            break
        
        return satisfied / len(ep) if ep else 0.0
    
    def _belief_consistency(self, intent_p: Dict, intent_c: Dict) -> float:
        """Compute Theory of Mind belief consistency penalty."""
        beliefs_p = intent_p.get('beliefs', {})
        beliefs_c = intent_c.get('beliefs', {})
        
        if not beliefs_p and not beliefs_c:
            return 0.0
        
        # Use track_beliefs primitive for structured belief tracking
        all_agents = set(beliefs_p.keys()) | set(beliefs_c.keys())
        if not all_agents:
            return 0.0
        
        penalty = 0.0
        for agent in all_agents:
            bp = beliefs_p.get(agent, '')
            bc = beliefs_c.get(agent, '')
            if bp != bc:
                penalty += 1.0
        
        return penalty / len(all_agents) if all_agents else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Epistemic honesty: detect ambiguity, presupposition, unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'have you stopped|have you quit|why did \w+ (fail|stop|quit)', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*\ba\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with explicit question
        if re.search(r'(he|she|it|they).*who\?', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either \w+ or \w+', prompt_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower) and not re.search(r'(most|least|measure|criteria)', prompt_lower):
            return 0.3
        
        # Information insufficiency check
        unknowns = len(re.findall(r'\?', prompt))
        constraints = len(re.findall(r'(if|then|because|therefore|given)', prompt_lower))
        info_score = information_sufficiency(unknowns, constraints)
        
        return max(0.4, info_score)  # Base confidence if no traps detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates by functorial structure mapping + belief consistency."""
        vp, ep, intent_p = self._extract_graph(prompt)
        results = []
        
        for cand in candidates:
            vc, ec, intent_c = self._extract_graph(cand)
            
            # Functor mapping
            mapping = self._hungarian_match(vp, vc)
            
            # Natural transformation score (structural)
            struct_score = self._natural_transformation_score(ep, ec, mapping)
            
            # Theory of Mind penalty
            mind_penalty = self._belief_consistency(intent_p, intent_c)
            
            # Compute NCD tiebreaker
            combined = prompt + cand
            ncd = (len(combined.encode()) - min(len(prompt.encode()), len(cand.encode()))) / max(len(prompt.encode()), len(cand.encode()), 1)
            
            # Final score: 70% structure, 20% belief, 10% NCD
            score = 0.7 * struct_score + 0.2 * (1.0 - mind_penalty) + 0.1 * (1.0 - ncd)
            
            reasoning = f"Struct={struct_score:.2f}, Belief={1-mind_penalty:.2f}, NCD={1-ncd:.2f}"
            results.append({'candidate': cand, 'score': score, 'reasoning': reasoning})
        
        # Use confidence_from_agreement primitive for meta-scoring
        scores = [r['score'] for r in results]
        if scores:
            agreement = confidence_from_agreement(scores)
            for r in results:
                r['score'] = 0.8 * r['score'] + 0.2 * agreement
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence in answer, capped by meta-confidence on prompt quality."""
        meta_conf = self._meta_confidence(prompt)
        
        # Evaluate just this answer
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        base_score = results[0]['score']
        
        # Cap by meta-confidence (epistemic honesty)
        final_conf = min(base_score, meta_conf)
        
        # Never exceed 0.9 unless perfect structural match
        vp, ep, _ = self._extract_graph(prompt)
        va, ea, _ = self._extract_graph(answer)
        mapping = self._hungarian_match(vp, va)
        struct = self._natural_transformation_score(ep, ea, mapping)
        
        if struct < 0.95:
            final_conf = min(final_conf, 0.85)
        
        return final_conf
```

</details>
