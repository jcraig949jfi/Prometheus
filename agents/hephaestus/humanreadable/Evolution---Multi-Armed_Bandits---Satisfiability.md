# Evolution + Multi-Armed Bandits + Satisfiability

**Fields**: Biology, Game Theory, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T04:40:24.313300
**Report Generated**: 2026-04-02T11:44:49.916917

---

## Nous Analysis

**Algorithm**  
Each candidate answer is represented as a binary string `x ∈ {0,1}^V` where `V` is the number of propositional variables extracted from the prompt (see §2). A population `P` of size `N` holds such strings. Fitness of an individual is the number of satisfied clauses in a CNF formula `F` built from the prompt:  

```
fitness(x) = Σ_{c∈F}  [  ∨_{l∈c}  (x[var(l)] == sign(l))  ]
```

where `sign(l)=1` for a positive literal and `0` for a negated literal; the bracket denotes 1 if the clause is true, 0 otherwise. This is a pure numpy operation: encode `F` as two integer arrays `pos` (shape `C×K_max`) and `neg` (same shape) giving variable indices for positive and negative literals; compute `sat = np.any((x[pos]==1) | (x[neg]==0), axis=1)` and sum.

To allocate evaluation budget we treat each individual as an arm of a multi‑armed bandit. After computing `fitness`, we update the arm’s empirical mean `μ_i` and count `n_i`. Selection for the next generation uses UCB1:  

```
i* = argmax_i ( μ_i + sqrt(2 * ln(t) / n_i) )
```

where `t` is the total number of evaluations so far. The chosen individual undergoes evolutionary variation: with probability `p_mut` each bit flips (mutation); with probability `p_cross` we pick two parents selected proportionally to `μ` and perform uniform crossover to create offspring. The offspring replace the lowest‑fitness individuals in `P`. The process repeats for a fixed number of generations; the final score for a candidate answer is its fitness normalized by `|F|`.

**Structural features parsed**  
The prompt is scanned with regex‑based patterns to extract:  
- Negations (`not`, `no`, `-`) → negative literals.  
- Comparatives (`greater than`, `<`, `≤`, `≥`, `>`) → arithmetic constraints turned into propositional variables via threshold encoding.  
- Conditionals (`if … then …`, `implies`) → implication clauses `(¬A ∨ B)`.  
- Causal claims (`because`, `due to`) → same as conditionals.  
- Ordering relations (`before`, `after`, `precedes`) → temporal variables with ordering encoded as a set of pairwise implication clauses.  
- Conjunctions (`and`, `&`) and disjunctions (`or`, `||`) → direct clause construction.

**Novelty**  
Evolutionary algorithms have been applied to SAT solving, and bandits have been used for hyper‑parameter or algorithm selection, but combining a bandit‑driven evaluation schedule with an evolutionary search whose fitness is a exact SAT clause‑satisfaction count — using only numpy/std‑lib — has not been reported in the literature for scoring reasoning answers.

**Ratings**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency and captures quantitative constraints via SAT, providing a principled reasoning score.  
Metacognition: 6/10 — Bandit allocation gives limited self‑monitoring of evaluation effort; no explicit modeling of uncertainty about one’s own knowledge.  
Hypothesis generation: 7/10 — Evolutionary mutation/crossover creates new answer variants, enabling exploratory hypothesis generation guided by UCB.  
Implementability: 9/10 — All components (regex parsing, numpy‑based SAT evaluation, UCB, mutation/crossover) rely solely on numpy and the Python standard library, making implementation straightforward.

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

**Forge Timestamp**: 2026-04-02T11:04:47.518406

---

## Code

**Source**: scrap

[View code](./Evolution---Multi-Armed_Bandits---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
"""
Evolution x Multi-Armed Bandits x Satisfiability Reasoning Tool

Parses prompt into CNF clauses, evolves binary variable assignments (candidates),
uses SAT solver for fitness and UCB1 bandit to allocate evaluation budget.
Primitives: solve_sat, confidence_from_agreement, negate, bayesian_update.
"""
import re
import numpy as np
from forge_primitives import solve_sat, confidence_from_agreement, negate, bayesian_update
import zlib


class ReasoningTool:
    def __init__(self):
        self.n_generations = 15
        self.pop_size = 20
        self.p_mut = 0.15
        self.p_cross = 0.6
        
    def _parse_variables_and_clauses(self, prompt, candidate):
        """Extract propositional variables and CNF clauses from prompt+candidate."""
        text = prompt.lower() + " " + candidate.lower()
        variables = {}
        clauses = []
        var_count = 0
        
        # Extract variables from key phrases
        tokens = re.findall(r'\b\w+\b', text)
        for tok in set(tokens):
            if len(tok) > 2:
                variables[tok] = var_count
                var_count += 1
        
        # Conditionals: if A then B -> (-A OR B)
        for match in re.finditer(r'if\s+(\w+).*?then\s+(\w+)', prompt.lower()):
            a, b = match.groups()
            if a in variables and b in variables:
                clauses.append([(-variables[a]-1, variables[b])])
        
        # Negations: not A -> -A must be true
        for match in re.finditer(r'not\s+(\w+)', text):
            word = match.group(1)
            if word in variables:
                clauses.append([(-variables[word]-1,)])
        
        # Conjunctions: A and B -> both A, B
        for match in re.finditer(r'(\w+)\s+and\s+(\w+)', text):
            a, b = match.groups()
            if a in variables and b in variables:
                clauses.append([(variables[a],)])
                clauses.append([(variables[b],)])
        
        # Comparatives: extract numeric assertions
        nums = re.findall(r'\b(\d+\.?\d*)\s*([<>=]+)\s*(\d+\.?\d*)', text)
        for n1, op, n2 in nums:
            result = eval(f"{n1}{op}{n2}")
            var_name = f"cmp_{n1}_{op}_{n2}"
            if var_name not in variables:
                variables[var_name] = var_count
                var_count += 1
            if result:
                clauses.append([(variables[var_name],)])
            else:
                clauses.append([(-variables[var_name]-1,)])
        
        return variables, clauses, var_count
    
    def _fitness_sat(self, assignment, clauses):
        """Compute fitness = number of satisfied clauses."""
        if not clauses:
            return 0.0
        sat_count = 0
        for clause_list in clauses:
            for clause in clause_list:
                if isinstance(clause, tuple):
                    lit = clause[0]
                else:
                    lit = clause
                var_idx = abs(lit) - 1 if lit < 0 else lit
                is_neg = lit < 0
                if var_idx < len(assignment):
                    val = assignment[var_idx]
                    if (is_neg and val == 0) or (not is_neg and val == 1):
                        sat_count += 1
                        break
        return sat_count / max(len(clauses), 1)
    
    def _ucb1(self, means, counts, total):
        """UCB1 selection."""
        ucb = np.zeros(len(means))
        for i in range(len(means)):
            if counts[i] == 0:
                ucb[i] = float('inf')
            else:
                ucb[i] = means[i] + np.sqrt(2 * np.log(total + 1) / counts[i])
        return np.argmax(ucb)
    
    def _evolve_population(self, pop, clauses, n_vars):
        """Evolution with bandit-driven evaluation."""
        means = np.zeros(self.pop_size)
        counts = np.zeros(self.pop_size)
        total_evals = 0
        
        for gen in range(self.n_generations):
            # Bandit selection
            idx = self._ucb1(means, counts, total_evals)
            individual = pop[idx]
            
            # Evaluate fitness using SAT
            fit = self._fitness_sat(individual, clauses)
            counts[idx] += 1
            means[idx] = (means[idx] * (counts[idx] - 1) + fit) / counts[idx]
            total_evals += 1
            
            # Mutation
            if np.random.rand() < self.p_mut:
                offspring = individual.copy()
                for i in range(len(offspring)):
                    if np.random.rand() < 0.2:
                        offspring[i] = 1 - offspring[i]
            # Crossover
            elif np.random.rand() < self.p_cross:
                parent2_idx = np.random.choice(range(self.pop_size), p=means/means.sum() if means.sum() > 0 else None)
                parent1, parent2 = individual, pop[parent2_idx]
                offspring = np.array([p1 if np.random.rand() < 0.5 else p2 for p1, p2 in zip(parent1, parent2)])
            else:
                offspring = individual
            
            # Replace worst
            worst_idx = np.argmin(means)
            pop[worst_idx] = offspring
            means[worst_idx] = 0
            counts[worst_idx] = 0
        
        return means
    
    def _meta_confidence(self, prompt):
        """Check for reasoning traps that require epistemic honesty."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'why (did|does|is) \w+ (fail|stop|wrong)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*?\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*?(who|what|which)', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'either \w+ or \w+', p) and not re.search(r'(only|just|exactly)', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p) and not re.search(r'(according to|objectively|measured by)', p):
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt, candidates):
        """Evaluate candidates using evolutionary SAT search."""
        results = []
        
        for cand in candidates:
            variables, clauses, n_vars = self._parse_variables_and_clauses(prompt, cand)
            
            if n_vars == 0:
                # Fallback to NCD
                ncd = len(zlib.compress((prompt + cand).encode())) / (len(zlib.compress(prompt.encode())) + len(zlib.compress(cand.encode())) + 1e-9)
                score = 1.0 - ncd
                reasoning = "NCD fallback"
            else:
                # Initialize population
                pop = [np.random.randint(0, 2, n_vars) for _ in range(self.pop_size)]
                
                # Evolve with bandit allocation
                final_means = self._evolve_population(pop, clauses, n_vars)
                
                # Use primitives for final scoring
                sat_score = np.max(final_means)
                agreement = confidence_from_agreement([final_means])
                
                # Combine SAT fitness + agreement confidence
                score = 0.7 * sat_score + 0.3 * agreement
                
                # Small NCD tiebreaker
                ncd = len(zlib.compress((prompt + cand).encode())) / (len(zlib.compress(prompt.encode())) + len(zlib.compress(cand.encode())) + 1e-9)
                score = 0.9 * score + 0.1 * (1.0 - ncd)
                
                reasoning = f"SAT fitness={sat_score:.2f}, agreement={agreement:.2f}, {len(clauses)} clauses"
            
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence with epistemic honesty."""
        meta_cap = self._meta_confidence(prompt)
        
        variables, clauses, n_vars = self._parse_variables_and_clauses(prompt, answer)
        
        if n_vars == 0:
            return min(0.4, meta_cap)
        
        # Single evaluation
        pop = [np.random.randint(0, 2, n_vars) for _ in range(self.pop_size)]
        final_means = self._evolve_population(pop, clauses, n_vars)
        
        sat_score = np.max(final_means)
        
        # Bayesian update: prior 0.5, likelihood from SAT
        posterior = bayesian_update(0.5, sat_score, 0.1)
        
        # Cap by meta-confidence
        return min(posterior, meta_cap, 0.85)
```

</details>
