# Dynamical Systems + Genetic Algorithms + Cognitive Load Theory

**Fields**: Mathematics, Computer Science, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T21:58:51.024401
**Report Generated**: 2026-04-02T12:33:29.324021

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a chromosome encoding a set of propositional variables extracted from the prompt (e.g., `P: “X > Y”`, `Q: “¬Z”`). A chromosome is a binary numpy array `g ∈ {0,1}^k` where `k` is the number of extracted propositions; a `1` means the proposition is asserted true in the interpretation.  

1. **Parsing & constraint graph** – Using only `re` we extract atomic clauses and build a directed constraint graph `C`. Edges encode logical relations:  
   - *Negation* flips the target node.  
   - *Comparative* (`>`, `<`, `=`) creates an arithmetic constraint on any numeric tokens attached to the nodes.  
   - *Conditional* (`if A then B`) adds an implication edge `A → B`.  
   - *Causal* and *ordering* edges are treated similarly as deterministic update rules.  

2. **Dynamical‑system fitness** – Starting from a chromosome `g₀`, we iterate a deterministic update rule that propagates truth values through `C`:  
   ```
   g_{t+1} = f(g_t) = clamp( W @ g_t + b )
   ```  
   where `W` is the adjacency matrix of `C` (weights = 1 for positive influence, –1 for negation) and `b` encodes any fixed numeric thresholds from comparatives. The iteration stops when `g_{t+1}=g_t` (a fixed‑point attractor) or after a max‑step bound (modeling limited working memory). The fitness is the negative Hamming distance between the final attractor and the chromosome’s initial assertion of the answer’s target proposition (e.g., the truth value of the main claim). Lower distance → higher fitness.  

3. **Genetic‑algorithm search** – A population of `N` chromosomes is initialized randomly. Each generation:  
   - **Selection:** tournament pick based on fitness.  
   - **Crossover:** uniform crossover of parent bit‑strings.  
   - **Mutation:** bit‑flip with probability `μ = 1/k` (inverse chromosome length) to keep the expected number of active genes ≈ 1, embodying cognitive‑load constraints on working memory.  
   The process repeats for a fixed number of generations or until fitness converges. The best chromosome’s attractor state is taken as the reasoned answer; its fitness score is returned.

**Structural features parsed** – negations, comparatives (`>`, `<`, `=`), conditionals (`if…then`), causal verbs (`because`, `leads to`), ordering relations (`first`, `before`, `after`), and explicit numeric constants.

**Novelty** – Evolutionary search over logical interpretations has appeared in genetic programming for theorem proving, and dynamical‑systems‑style truth propagation is used in Boolean network models. The explicit coupling of a cognitive‑load‑bounded mutation rate with attractor‑based fitness is not common in existing neuro‑symbolic or GP literature, making the combination relatively novel.

**Ratings**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency via attractor dynamics, capturing multi‑step inference better than shallow similarity metrics.  
Metacognition: 6/10 — Working‑memory limitation is modeled crudely through mutation rate; richer metacognitive monitoring (e.g., adaptive chunking) is absent.  
Hypothesis generation: 7/10 — The GA explores alternative interpretations, but hypothesis space is limited to propositional encodings extracted by regex.  
Implementability: 9/10 — Only `numpy` for matrix/vector ops and the standard library (`re`, `random`) are needed; no external APIs or neural components.

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
**Reason**: trap_battery_failed (acc=42% cal=21% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:59:20.721304

---

## Code

**Source**: scrap

[View code](./Dynamical_Systems---Genetic_Algorithms---Cognitive_Load_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Combines Dynamical Systems, Genetic Algorithms, and Cognitive Load Theory.
    
    Mechanism:
    1. Parse prompt into constraint graph (propositions + relations)
    2. Encode candidates as chromosomes (binary truth assignments)
    3. Propagate truth via dynamical system to find attractors
    4. Evolve population via GA with cognitive-load-bounded mutation
    5. Score by attractor stability and trajectory convergence
    """
    
    def __init__(self):
        self.max_iterations = 20
        self.population_size = 30
        self.generations = 15
        self.tournament_size = 3
        np.random.seed(42)
    
    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions from text."""
        text = text.lower()
        # Extract comparisons, relations, and simple statements
        patterns = [
            r'[a-z_]+\s*[<>=]+\s*[a-z0-9.]+',
            r'[a-z_]+\s+is\s+[a-z_]+',
            r'[a-z_]+\s+has\s+[a-z_]+',
            r'not\s+[a-z_]+',
            r'[a-z_]+\s+before\s+[a-z_]+',
            r'[a-z_]+\s+after\s+[a-z_]+',
        ]
        props = []
        for pat in patterns:
            props.extend(re.findall(pat, text))
        # Extract words as base propositions
        words = re.findall(r'\b[a-z]{3,}\b', text)
        props.extend(words[:10])  # Limit to prevent explosion
        return list(set(props))[:15]  # Cap at 15 for cognitive load
    
    def _build_constraint_graph(self, text: str, props: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Build adjacency matrix W and bias b from text constraints."""
        k = len(props)
        W = np.zeros((k, k))
        b = np.zeros(k)
        
        text_lower = text.lower()
        
        # Negations: flip sign
        for i, p in enumerate(props):
            if re.search(rf'\bnot\s+{re.escape(p)}', text_lower):
                b[i] -= 1
        
        # Conditionals: if A then B
        conditionals = re.findall(r'if\s+(\w+).*?then\s+(\w+)', text_lower)
        for a, c in conditionals:
            for i, p in enumerate(props):
                if a in p:
                    for j, q in enumerate(props):
                        if c in q:
                            W[j, i] = 1  # A implies B
        
        # Causal: A because B, A leads to B
        causal = re.findall(r'(\w+)\s+(?:because|leads to)\s+(\w+)', text_lower)
        for a, c in causal:
            for i, p in enumerate(props):
                if a in p:
                    for j, q in enumerate(props):
                        if c in q:
                            W[i, j] = 1
        
        # Comparatives: extract numeric relations
        comparisons = re.findall(r'(\d+\.?\d*)\s*([<>=]+)\s*(\d+\.?\d*)', text_lower)
        for left, op, right in comparisons:
            lv, rv = float(left), float(right)
            result = (lv > rv if '>' in op else lv < rv if '<' in op else lv == rv)
            if result:
                b[0] += 0.5  # Boost first prop if comparison holds
        
        return W, b
    
    def _propagate(self, g: np.ndarray, W: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Single step of dynamical system."""
        return np.clip(np.tanh(W @ g + b), 0, 1).round().astype(int)
    
    def _find_attractor(self, g0: np.ndarray, W: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, int]:
        """Iterate until fixed point or max steps. Returns (attractor, steps)."""
        g = g0.copy()
        trajectory = [g.copy()]
        for step in range(self.max_iterations):
            g_next = self._propagate(g, W, b)
            if np.array_equal(g_next, g):
                return g, step
            trajectory.append(g_next)
            g = g_next
        return g, self.max_iterations
    
    def _fitness(self, chromosome: np.ndarray, W: np.ndarray, b: np.ndarray, target_bit: int) -> float:
        """Fitness = convergence speed + attractor match to target."""
        attractor, steps = self._find_attractor(chromosome, W, b)
        # Reward fast convergence
        convergence_score = 1.0 - (steps / self.max_iterations)
        # Reward matching target bit
        target_score = float(attractor[0] == target_bit)
        return 0.7 * target_score + 0.3 * convergence_score
    
    def _genetic_search(self, k: int, W: np.ndarray, b: np.ndarray, target_bit: int) -> float:
        """Run GA to find best interpretation."""
        if k == 0:
            return 0.5
        
        population = [np.random.randint(0, 2, k) for _ in range(self.population_size)]
        mutation_rate = 1.0 / max(k, 1)
        
        for gen in range(self.generations):
            # Evaluate fitness
            fitness_scores = [self._fitness(ind, W, b, target_bit) for ind in population]
            
            # Selection + crossover + mutation
            new_pop = []
            for _ in range(self.population_size):
                # Tournament selection
                tournament = np.random.choice(self.population_size, self.tournament_size)
                parent1 = population[tournament[np.argmax([fitness_scores[i] for i in tournament])]]
                tournament = np.random.choice(self.population_size, self.tournament_size)
                parent2 = population[tournament[np.argmax([fitness_scores[i] for i in tournament])]]
                
                # Uniform crossover
                mask = np.random.rand(k) > 0.5
                child = np.where(mask, parent1, parent2)
                
                # Mutation with cognitive load constraint
                if np.random.rand() < mutation_rate * k:
                    flip_idx = np.random.randint(k)
                    child[flip_idx] = 1 - child[flip_idx]
                
                new_pop.append(child)
            
            population = new_pop
        
        # Return best fitness
        final_fitness = [self._fitness(ind, W, b, target_bit) for ind in population]
        return max(final_fitness)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity and epistemically problematic questions."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|quit|why did.*fail|when did.*stop)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*?\ba\s+\w+', p):
            return 0.25
        
        # Pronoun ambiguity with who question
        if re.search(r'\b(he|she)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+', p) and '?' in p:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|criterion|metric)\b', p):
            return 0.3
        
        return 1.0  # No obvious issues
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by dynamical-system fitness."""
        props = self._extract_propositions(prompt)
        W, b = self._build_constraint_graph(prompt, props)
        k = len(props)
        
        results = []
        for cand in candidates:
            # Determine target bit from candidate sentiment
            cand_lower = cand.lower()
            target_bit = 1 if any(w in cand_lower for w in ['yes', 'true', 'correct', 'more', 'greater']) else 0
            
            # Structural score via GA
            structural_score = self._genetic_search(k, W, b, target_bit) if k > 0 else 0.5
            
            # Computational score: check numeric comparisons
            comp_score = 0.0
            nums = re.findall(r'\d+\.?\d*', cand)
            if len(nums) >= 2:
                try:
                    vals = [float(n) for n in nums[:2]]
                    prompt_nums = re.findall(r'\d+\.?\d*', prompt)
                    if len(prompt_nums) >= 2:
                        pv = [float(n) for n in prompt_nums[:2]]
                        if (vals[0] > vals[1]) == (pv[0] > pv[1]):
                            comp_score = 1.0
                except:
                    pass
            
            # NCD tiebreaker
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Combine: 50% structural, 30% computational, 15% NCD
            final_score = 0.5 * structural_score + 0.3 * comp_score + 0.15 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural={structural_score:.2f}, Comp={comp_score:.2f}, NCD={ncd_score:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on prompt properties and answer fit."""
        meta_conf = self._meta_confidence(prompt)
        
        props = self._extract_propositions(prompt)
        W, b = self._build_constraint_graph(prompt, props)
        k = len(props)
        
        if k == 0:
            return min(0.3, meta_conf)  # No structure found
        
        # Determine target from answer
        ans_lower = answer.lower()
        target_bit = 1 if any(w in ans_lower for w in ['yes', 'true', 'correct']) else 0
        
        # Run GA
        fitness = self._genetic_search(k, W, b, target_bit)
        
        # Cap by meta-confidence
        raw_conf = min(0.95, fitness)  # Never fully certain
        return min(raw_conf, meta_conf)
```

</details>
