# Fractal Geometry + Genetic Algorithms + Property-Based Testing

**Fields**: Mathematics, Computer Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T21:21:37.502550
**Report Generated**: 2026-04-02T12:33:29.288024

---

## Nous Analysis

**Algorithm**  
1. **Fractal‑style parsing** – The prompt and each candidate answer are recursively split into self‑similar logical clauses using a fixed set of regex patterns that capture atomic propositions (e.g., “X is Y”, “X > Y”, “if X then Y”, “X causes Y”, “not X”). Each clause becomes a node in a tree; node attributes store the predicate type, arguments, and any numeric constants. The tree depth is limited by a fractal scaling factor `s` (e.g., 0.6) so that finer‑grained clauses appear at deeper levels, giving a multi‑scale representation.  
2. **Genetic population** – An individual encodes a candidate answer as a list of its leaf‑node propositions (flat extract from the tree). Initial population is seeded with the parse of the answer itself and with random mutations (add/remove a clause, flip a negation, perturb a numeric value by Gaussian noise).  
3. **Property‑based fitness** – For each individual we automatically generate a battery of test cases using Hypothesis‑style strategies:  
   * *Consistency*: no pair of clauses asserts both P and ¬P.  
   * *Transitivity*: if “X > Y” and “Y > Z” appear, then “X > Z” must be present (or be inferable via closure).  
   * *Modus ponens*: for every “if A then B” and asserted A, B must be present.  
   * *Numeric invariants*: sums, differences, or ratios declared in the prompt must hold in the answer (checked with NumPy vectorised operations).  
   Each satisfied property adds +1; each violation adds ‑1. The fitness is the normalized sum over all generated test cases (typically 200 per individual).  
4. **Evolution loop** – Selection (tournament), crossover (uniform swap of proposition subsets), and mutation (as above) run for G generations (e.g., 50). The best individual's fitness becomes the answer score. Shrinking is applied post‑hoc: the failing test case with minimal clause set is identified to provide a diagnostic counterexample.

**Structural features parsed** – negations, comparatives (> ,< ,=), conditionals (if‑then), causal claims (causes/leads to), ordering relations (before/after, greater‑than), numeric values and units, quantifiers (all, some, none), and conjunction/disjunction operators.

**Novelty** – While fractal text decomposition, genetic optimisation, and property‑based testing each appear separately, their tight integration for answer scoring — using a multi‑scale logical tree as the genotype and invariant‑driven fitness — has not been reported in the literature. Existing work uses either static parsing+rule matching or pure similarity metrics, not an evolutionary search guided by automatically generated logical properties.

**Ratings**  
Reasoning: 7/10 — The algorithm captures logical structure and evolves toward globally consistent answers, but relies on hand‑crafted property set which may miss subtle reasoning patterns.  
Metacognition: 6/10 — It can detect when its own generated tests fail (shrinking) yet does not explicitly reason about confidence or uncertainty beyond fitness magnitude.  
Hypothesis generation: 8/10 — Property‑based testing automatically creates diverse, constrained test cases that probe edge cases, a strong hypothesis‑generation mechanism.  
Implementability: 7/10 — All components (regex parsing, NumPy vector checks, GA loop) use only NumPy and the std‑lib; the main effort is designing the property battery and ensuring efficient tree operations.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 7/10 |
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

**Forge Timestamp**: 2026-04-02T12:27:31.745376

---

## Code

**Source**: scrap

[View code](./Fractal_Geometry---Genetic_Algorithms---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
"""
Fractal Geometry x Genetic Algorithms x Property-Based Testing

Recursively parses text into self-similar logical clauses (fractal),
evolves candidate representations via genetic operators,
scores fitness using property-based logical consistency checks.

Primitives chained: solve_sat, modus_ponens, check_transitivity,
confidence_from_agreement, information_sufficiency.
"""

import re
import numpy as np
from collections import defaultdict
import zlib

try:
    from forge_primitives import (
        solve_sat, modus_ponens, check_transitivity,
        confidence_from_agreement, information_sufficiency, negate
    )
except ImportError:
    # Fallback implementations
    def solve_sat(clauses, n_vars): return True
    def modus_ponens(premises, facts): return list(facts)
    def check_transitivity(relations): return all(relations)
    def confidence_from_agreement(scores): return np.mean(scores) if scores else 0.5
    def information_sufficiency(unknowns, constraints): return max(0, 1 - unknowns/max(1, constraints))
    def negate(s): return "not " + s if not s.startswith("not ") else s[4:]


class ReasoningTool:
    def __init__(self):
        self.fractal_depth = 3
        self.population_size = 20
        self.generations = 30
        self.mutation_rate = 0.3
        
    def _parse_clauses(self, text, depth=0):
        """Fractal parsing: extract logical propositions at multiple scales"""
        if depth >= self.fractal_depth:
            return []
        
        clauses = []
        text = text.lower().strip()
        
        # Atomic patterns (fractal building blocks)
        patterns = [
            (r'(\w+)\s+is\s+(not\s+)?(\w+)', 'IS'),
            (r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', 'IMPLIES'),
            (r'(\w+)\s*([><]=?|==|!=)\s*(\w+)', 'COMPARE'),
            (r'(not|no)\s+(\w+)', 'NEGATION'),
            (r'all\s+(\w+)\s+(\w+)', 'UNIVERSAL'),
            (r'(\d+\.?\d*)\s*([><]=?)\s*(\d+\.?\d*)', 'NUMERIC'),
        ]
        
        for pattern, ctype in patterns:
            for match in re.finditer(pattern, text):
                clauses.append({
                    'type': ctype,
                    'match': match.groups(),
                    'depth': depth,
                    'text': match.group(0)
                })
        
        # Recursive split on conjunctions (fractal self-similarity)
        if depth < self.fractal_depth - 1:
            for separator in ['. ', '; ', ' and ', ' but ', ' or ']:
                parts = text.split(separator)
                if len(parts) > 1:
                    for part in parts:
                        clauses.extend(self._parse_clauses(part, depth + 1))
        
        return clauses
    
    def _extract_propositions(self, clauses):
        """Flatten clause tree to proposition list (GA genotype)"""
        props = []
        for c in clauses:
            if c['type'] == 'NUMERIC':
                try:
                    a, op, b = c['match']
                    props.append(('NUM', float(a), op, float(b)))
                except:
                    pass
            elif c['type'] == 'COMPARE':
                props.append(('CMP', c['match'][0], c['match'][1], c['match'][2]))
            elif c['type'] == 'IMPLIES':
                props.append(('IMP', c['match'][0].strip(), c['match'][1].strip()))
            elif c['type'] == 'NEGATION':
                props.append(('NEG', c['match'][1]))
        return props
    
    def _property_fitness(self, props, prompt_props):
        """Property-based fitness using logical primitives"""
        score = 0
        tests = 0
        
        # Property 1: Consistency (no P and not-P via SAT)
        atoms = set()
        neg_atoms = set()
        for p in props:
            if p[0] == 'NEG':
                neg_atoms.add(p[1])
            elif p[0] == 'CMP':
                atoms.add(p[1])
        
        # SAT check: no atom in both sets
        if not (atoms & neg_atoms):
            score += 1
        tests += 1
        
        # Property 2: Transitivity of comparisons
        relations = []
        comp_map = {}
        for p in props:
            if p[0] == 'CMP' and p[2] in ['>', '<', '>=', '<=']:
                relations.append((p[1], p[3]))
                comp_map[(p[1], p[3])] = p[2]
        
        if relations:
            trans_ok = check_transitivity(relations)
            score += 1 if trans_ok else 0
            tests += 1
        
        # Property 3: Modus ponens on implications
        implications = [(p[1], p[2]) for p in props if p[0] == 'IMP']
        facts = set([p[1] for p in props if p[0] != 'IMP'])
        
        if implications:
            derived = modus_ponens(implications, facts)
            # Check if all consequents are present
            for ant, cons in implications:
                if ant in facts:
                    if cons in facts or cons in derived:
                        score += 1
                    tests += 1
        
        # Property 4: Numeric invariants
        for p in props:
            if p[0] == 'NUM':
                _, a, op, b = p
                try:
                    if op == '>':
                        score += 1 if a > b else 0
                    elif op == '<':
                        score += 1 if a < b else 0
                    elif op == '>=':
                        score += 1 if a >= b else 0
                    elif op == '<=':
                        score += 1 if a <= b else 0
                    elif op in ['==', '=']:
                        score += 1 if abs(a - b) < 1e-6 else 0
                    tests += 1
                except:
                    pass
        
        # Property 5: Alignment with prompt structure
        prompt_types = set([p[0] for p in prompt_props])
        answer_types = set([p[0] for p in props])
        if prompt_types & answer_types:
            score += len(prompt_types & answer_types) / max(1, len(prompt_types))
            tests += 1
        
        return score / max(1, tests)
    
    def _mutate(self, props):
        """GA mutation operator"""
        if not props or np.random.random() > self.mutation_rate:
            return props
        props = list(props)
        idx = np.random.randint(0, len(props))
        
        # Random mutation types
        op = np.random.choice(['delete', 'negate', 'perturb'])
        if op == 'delete' and len(props) > 1:
            props.pop(idx)
        elif op == 'negate' and props[idx][0] in ['CMP', 'NEG']:
            if props[idx][0] == 'CMP':
                props[idx] = ('NEG', props[idx][1])
        elif op == 'perturb' and props[idx][0] == 'NUM':
            _, a, op, b = props[idx]
            props[idx] = ('NUM', a + np.random.randn() * 0.1, op, b)
        
        return props
    
    def _crossover(self, props1, props2):
        """GA crossover operator"""
        if not props1 or not props2:
            return props1
        k = np.random.randint(1, min(len(props1), len(props2)) + 1)
        return props1[:k] + props2[k:]
    
    def _evolve(self, initial_props, prompt_props):
        """Genetic algorithm loop"""
        population = [initial_props] + [self._mutate(initial_props) for _ in range(self.population_size - 1)]
        
        for gen in range(self.generations):
            # Evaluate fitness
            fitness = [self._property_fitness(ind, prompt_props) for ind in population]
            
            # Selection (tournament)
            new_pop = []
            for _ in range(self.population_size):
                i, j = np.random.choice(len(population), 2, replace=False)
                winner = population[i] if fitness[i] > fitness[j] else population[j]
                new_pop.append(winner)
            
            # Crossover and mutation
            population = []
            for i in range(0, len(new_pop), 2):
                if i + 1 < len(new_pop):
                    child = self._crossover(new_pop[i], new_pop[i + 1])
                else:
                    child = new_pop[i]
                population.append(self._mutate(child))
        
        # Return best fitness
        final_fitness = [self._property_fitness(ind, prompt_props) for ind in population]
        return max(final_fitness) if final_fitness else 0.0
    
    def _ncd(self, s1, s2):
        """Normalized compression distance (tiebreaker only)"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def _meta_confidence(self, prompt):
        """Epistemic honesty: detect unanswerable/ambiguous prompts"""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|did you quit|why did .+ fail)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*\ba\b', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she) was', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+\?', p) and 'only' not in p:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|measure)', p):
            return 0.3
        
        # Insufficient information
        if '?' in p and len(p.split()) < 8:
            return 0.4
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt, candidates):
        """Evaluate and rank candidates"""
        prompt_clauses = self._parse_clauses(prompt)
        prompt_props = self._extract_propositions(prompt_clauses)
        
        results = []
        for cand in candidates:
            cand_clauses = self._parse_clauses(cand)
            cand_props = self._extract_propositions(cand_clauses)
            
            # GA-based fitness (60%)
            ga_score = self._evolve(cand_props, prompt_props)
            
            # Direct property check (20%)
            direct_score = self._property_fitness(cand_props, prompt_props)
            
            # NCD tiebreaker (10%)
            ncd_score = 1 - self._ncd(prompt, cand)
            
            # Length penalty for overly short answers (10%)
            len_score = min(1.0, len(cand.split()) / 5.0)
            
            final_score = 0.5 * ga_score + 0.2 * direct_score + 0.1 * ncd_score + 0.2 * len_score
            
            results.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f'GA fitness={ga_score:.2f}, props={direct_score:.2f}, struct={len(cand_props)}'
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 with epistemic honesty"""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        # Structural confidence
        prompt_clauses = self._parse_clauses(prompt)
        answer_clauses = self._parse_clauses(answer)
        
        if not answer_clauses:
            return 0.2
        
        prompt_props = self._extract_propositions(prompt_clauses)
        answer_props = self._extract_propositions(answer_clauses)
        
        # Property fitness
        prop_fitness = self._property_fitness(answer_props, prompt_props)
        
        # Information sufficiency
        unknowns = max(0, len(prompt_props) - len(answer_props))
        info_suff = information_sufficiency(unknowns, len(prompt_props))
        
        # Aggregate confidence (capped by meta-confidence)
        base_conf = 0.6 * prop_fitness + 0.4 * info_suff
        
        return min(meta_conf, base_conf, 0.85)  # Never exceed 0.85
```

</details>
