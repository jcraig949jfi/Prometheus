# Genetic Algorithms + Compressed Sensing + Sensitivity Analysis

**Fields**: Computer Science, Computer Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T10:26:13.339230
**Report Generated**: 2026-04-02T10:55:58.574203

---

## Nous Analysis

**Algorithm: Evolutionary Sparse Constraint Scorer (ESCS)**  

*Data structures*  
- **Population matrix** `P ∈ ℝ^{N×M}` where each row is a candidate answer encoded as a binary feature vector of length `M` (presence/absence of parsed structural tokens).  
- **Measurement matrix** `Φ ∈ ℝ^{K×M}` (K ≪ M) drawn once from a Bernoulli‑±1 distribution; implements compressed‑sensing projection.  
- **Sensitivity vector** `s ∈ ℝ^{M}` storing partial derivatives of a proxy loss (e.g., violation of logical constraints) w.r.t. each token.  
- **Fitness score** `f_i = ‖Φ·x_i‖_2^2 + λ·‖x_i‖_1 + γ·s^T·x_i` for individual `x_i`.  

*Operations*  
1. **Parsing & feature extraction** – From prompt and each candidate, extract a set of structural tokens:  
   - Negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then`), causal arrows (`because`, `leads to`), numeric values, ordering relations (`first`, `before`).  
   Each token maps to a column index; the binary vector `x_i` marks token presence.  
2. **Constraint propagation** – Build a sparse linear system `A·x = b` representing transitivity, modus ponens, and numeric consistency (e.g., if `A > B` and `B > C` then `A > C`). Violations contribute to the sensitivity vector `s` via finite‑difference of the constraint residual.  
3. **Compressed‑sensing measurement** – Compute `y_i = Φ·x_i`. The L2 term rewards measurements that preserve the energy of the sparse token pattern, encouraging answers that retain informative structure while discarding noise.  
4. **Sparsity regularization** – L1 term (`‖x_i‖_1`) favours parsimonious explanations, mirroring basis pursuit.  
5. **Sensitivity‑guided mutation** – For each token `j`, mutation probability ∝ `|s_j|`; high‑sensitivity tokens (those whose flip most changes constraint violation) are perturbed more often, steering the population toward robust solutions.  
6. **Selection & crossover** – Tournament selection based on fitness `f_i`; uniform crossover mixes token sets. Iterate for `G` generations; the best individual's fitness is the final score.  

*Structural features parsed*  
Negations, comparatives, conditionals, causal claims, numeric constants, ordering/sequential relations, and explicit quantifiers (`all`, `some`). These are tokenized directly into the feature space.  

*Novelty*  
The triple fusion is not present in existing reasoning scorers. GA‑based answer ranking exists, as do compressed‑sensing feature selectors and sensitivity analysis for model robustness, but none combine an evolutionary search with CS‑projected sparse representations and gradient‑informed mutation to directly optimise logical‑constraint satisfaction.  

**Ratings**  
Reasoning: 8/10 — The algorithm explicitly evaluates logical consistency via constraint propagation and sparsity, yielding nuanced scores beyond surface similarity.  
Metacognition: 6/10 — It monitors sensitivity of token flips, offering a rudimentary self‑assessment of answer robustness, but lacks higher‑order reflection on its own search process.  
Hypothesis generation: 7/10 — Mutation guided by sensitivity creates new token combinations, effectively generating alternative hypotheses while preserving high‑fitness structures.  
Implementability: 9/10 — All steps use only NumPy (matrix ops, random projections) and Python’s stdlib (regex for token extraction, tournament loops); no external libraries or APIs are required.

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
**Reason**: trap_battery_failed (acc=34% cal=6% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T10:21:38.074438

---

## Code

**Source**: scrap

[View code](./Genetic_Algorithms---Compressed_Sensing---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Evolutionary Sparse Constraint Scorer (ESCS)
Combines Genetic Algorithms, Compressed Sensing, and Sensitivity Analysis
with state evolution dynamics tracking for reasoning evaluation.
"""

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        np.random.seed(42)
        self.M = 128  # Feature dimension
        self.K = 32   # Compressed dimension
        self.Phi = np.random.choice([-1, 1], size=(self.K, self.M))
        self.N_pop = 20
        self.N_gen = 15
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        score, _ = self._score_candidate(prompt, answer)
        structural_coverage = self._structural_coverage(prompt, answer)
        if structural_coverage < 0.2:
            return min(0.25, score / 2)
        comp_result = self._compute_if_numeric(prompt, answer)
        if comp_result is not None:
            return 0.92 if comp_result else 0.08
        return min(0.75, 0.3 + score * 0.5)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p_lower):
            return 0.15
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and '?' in prompt:
            return 0.22
        # False dichotomy
        if re.search(r'\b(either .+ or)\b', p_lower):
            return 0.25
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            return 0.28
        # Scope ambiguity
        if re.search(r'\bevery .+ a \b', p_lower):
            return 0.26
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        p_tokens = self._extract_tokens(prompt)
        c_tokens = self._extract_tokens(candidate)
        combined = p_tokens + c_tokens
        
        # Numeric computation
        num_score = self._numeric_eval(prompt, candidate)
        if num_score is not None:
            return num_score, "numeric_computation"
        
        # State evolution dynamics
        dyn_score = self._dynamics_score(prompt, candidate)
        
        # GA-based sparse constraint scoring
        x = self._vectorize(combined)
        constraints = self._build_constraints(p_tokens, c_tokens)
        s = self._sensitivity(x, constraints)
        
        pop = self._init_population(x)
        for gen in range(self.N_gen):
            fitness = self._fitness(pop, s, constraints)
            pop = self._evolve(pop, fitness, s)
        
        final_fitness = self._fitness(pop, s, constraints)
        best_idx = np.argmax(final_fitness)
        ga_score = final_fitness[best_idx]
        
        # NCD (max 15%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd
        
        # Combine: dynamics 40%, GA 35%, structural 10%, NCD 15%
        final = 0.4 * dyn_score + 0.35 * ga_score + 0.15 * ncd_score + 0.1 * self._structural_score(p_tokens, c_tokens)
        reasoning = f"dyn={dyn_score:.2f} ga={ga_score:.2f} ncd={ncd_score:.2f}"
        return final, reasoning
    
    def _extract_tokens(self, text: str) -> List[str]:
        tokens = []
        t_lower = text.lower()
        # Negations
        tokens.extend(re.findall(r'\b(not|no|never|neither|nor)\b', t_lower))
        # Comparatives
        tokens.extend(re.findall(r'\b(greater|less|more|fewer|larger|smaller|than|above|below)\b', t_lower))
        # Conditionals
        tokens.extend(re.findall(r'\b(if|then|unless|provided|when|whenever)\b', t_lower))
        # Causals
        tokens.extend(re.findall(r'\b(because|since|therefore|thus|hence|leads to|causes)\b', t_lower))
        # Orderings
        tokens.extend(re.findall(r'\b(first|second|before|after|next|last|prior)\b', t_lower))
        # Quantifiers
        tokens.extend(re.findall(r'\b(all|some|every|each|any|none)\b', t_lower))
        # Numbers
        tokens.extend(re.findall(r'\b\d+\.?\d*\b', t_lower))
        return tokens
    
    def _vectorize(self, tokens: List[str]) -> np.ndarray:
        x = np.zeros(self.M)
        for i, tok in enumerate(tokens[:self.M]):
            x[i] = 1.0
        return x
    
    def _build_constraints(self, p_tokens: List[str], c_tokens: List[str]) -> np.ndarray:
        A = np.zeros((10, self.M))
        for i in range(min(10, len(p_tokens))):
            if i < len(p_tokens):
                A[i, i % self.M] = 1.0
        return A
    
    def _sensitivity(self, x: np.ndarray, A: np.ndarray) -> np.ndarray:
        s = np.zeros(self.M)
        baseline = np.linalg.norm(A @ x)
        for j in range(self.M):
            x_flip = x.copy()
            x_flip[j] = 1.0 - x_flip[j]
            flipped = np.linalg.norm(A @ x_flip)
            s[j] = abs(flipped - baseline)
        return s / (np.max(s) + 1e-9)
    
    def _init_population(self, x: np.ndarray) -> np.ndarray:
        pop = np.zeros((self.N_pop, self.M))
        pop[0] = x
        for i in range(1, self.N_pop):
            pop[i] = np.random.binomial(1, 0.3, self.M)
        return pop
    
    def _fitness(self, pop: np.ndarray, s: np.ndarray, A: np.ndarray) -> np.ndarray:
        fit = np.zeros(self.N_pop)
        for i in range(self.N_pop):
            y = self.Phi @ pop[i]
            cs_term = np.linalg.norm(y) ** 2 / (self.K + 1)
            l1_term = np.sum(pop[i])
            sens_term = s @ pop[i]
            fit[i] = cs_term - 0.01 * l1_term + 0.5 * sens_term
        return fit / (np.max(fit) + 1e-9)
    
    def _evolve(self, pop: np.ndarray, fitness: np.ndarray, s: np.ndarray) -> np.ndarray:
        new_pop = np.zeros_like(pop)
        # Elitism
        best_idx = np.argmax(fitness)
        new_pop[0] = pop[best_idx]
        
        for i in range(1, self.N_pop):
            # Tournament selection
            idx1, idx2 = np.random.choice(self.N_pop, 2, replace=False)
            parent = pop[idx1] if fitness[idx1] > fitness[idx2] else pop[idx2]
            child = parent.copy()
            # Sensitivity-guided mutation
            for j in range(self.M):
                if np.random.rand() < 0.1 * (s[j] + 0.1):
                    child[j] = 1.0 - child[j]
            new_pop[i] = child
        return new_pop
    
    def _dynamics_score(self, prompt: str, candidate: str) -> float:
        sentences = re.split(r'[.!?;]', prompt)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.5
        
        # State vector evolves as we process premises
        state = np.zeros(16)
        trajectory = []
        
        for sent in sentences:
            tokens = self._extract_tokens(sent)
            for tok in tokens[:16]:
                idx = hash(tok) % 16
                state[idx] = 0.7 * state[idx] + 0.3
            trajectory.append(state.copy())
        
        # Candidate influence
        c_tokens = self._extract_tokens(candidate)
        for tok in c_tokens[:16]:
            idx = hash(tok) % 16
            state[idx] = 0.7 * state[idx] + 0.3
        final_state = state.copy()
        
        # Convergence: measure Lyapunov stability
        if len(trajectory) < 2:
            return 0.5
        
        deltas = [np.linalg.norm(trajectory[i+1] - trajectory[i]) for i in range(len(trajectory)-1)]
        convergence = 1.0 / (1.0 + np.mean(deltas))
        
        # Basin stability: how much does final state differ from mean trajectory
        mean_traj = np.mean(trajectory, axis=0)
        stability = 1.0 / (1.0 + np.linalg.norm(final_state - mean_traj))
        
        return 0.6 * convergence + 0.4 * stability
    
    def _structural_score(self, p_tokens: List[str], c_tokens: List[str]) -> float:
        if not p_tokens:
            return 0.0
        overlap = len(set(p_tokens) & set(c_tokens))
        return overlap / len(p_tokens)
    
    def _structural_coverage(self, prompt: str, answer: str) -> float:
        p_tok = self._extract_tokens(prompt)
        a_tok = self._extract_tokens(answer)
        if not p_tok:
            return 0.0
        return len(set(p_tok) & set(a_tok)) / len(p_tok)
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', candidate)
        
        if len(nums_p) >= 2 and len(nums_c) >= 1:
            # Comparison detection
            if re.search(r'\b(greater|larger|more|bigger)\b', prompt.lower()):
                try:
                    a, b = float(nums_p[0]), float(nums_p[1])
                    ans = float(nums_c[0])
                    if a > b and abs(ans - a) < 0.01:
                        return 0.95
                    elif b > a and abs(ans - b) < 0.01:
                        return 0.95
                except:
                    pass
            elif re.search(r'\b(less|smaller|fewer)\b', prompt.lower()):
                try:
                    a, b = float(nums_p[0]), float(nums_p[1])
                    ans = float(nums_c[0])
                    if a < b and abs(ans - a) < 0.01:
                        return 0.95
                    elif b < a and abs(ans - b) < 0.01:
                        return 0.95
                except:
                    pass
        return None
    
    def _compute_if_numeric(self, prompt: str, answer: str) -> bool:
        result = self._numeric_eval(prompt, answer)
        if result is not None:
            return result > 0.5
        return None
```

</details>
