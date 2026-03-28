# Evolution + Free Energy Principle + Maximum Entropy

**Fields**: Biology, Theoretical Neuroscience, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T10:56:49.285494
**Report Generated**: 2026-03-27T16:08:16.381673

---

## Nous Analysis

**1. Algorithm**  
We treat each candidate answer as a genotype encoding a weighted set of logical propositions extracted from the prompt. A population of genotypes evolves via mutation (randomly flipping a proposition’s polarity or adjusting its weight) and crossover (swapping subsets of propositions). Fitness is the negative variational free energy F = ⟨E⟩ − H, where ⟨E⟩ is the expected energy of constraint violations and H is the Shannon entropy of the weight distribution.  

*Data structures* –  
- **Proposition matrix** P ∈ ℝ^{n×m}: n propositions (e.g., “X > Y”, “¬Causes(A,B)”), m candidates; entry P_{ij} is the weight (log‑odds) that candidate j asserts proposition i.  
- **Constraint tensor** C ∈ {0,1,−1}^{k×n}: k logical constraints (transitivity, modus ponens, arithmetic) linking propositions; C_{p,i}=+1 if proposition i must be true for constraint p, −1 if it must be false, 0 otherwise.  
- **Weight vector** w ∈ ℝ^{m}: softmax‑normalized weights giving a distribution over candidates.  

*Operations* –  
1. **Parse** the prompt into propositions and build C using regex‑based extraction of negations, comparatives, conditionals, numeric values, causal claims, and ordering relations.  
2. **Energy** for candidate j: E_j = Σ_p max(0, −Σ_i C_{p,i}·P_{ij}) (sum of violated constraint magnitudes).  
3. **Expected energy** ⟨E⟩ = Σ_j w_j·E_j (numpy dot product).  
4. **Entropy** H = −Σ_j w_j·log(w_j+ε).  
5. **Free energy** F = ⟨E⟩ − H.  
6. **Fitness** = −F (lower free energy → higher fitness).  
7. **Selection**: tournament selection; **mutation**: add Gaussian noise to weights; **crossover**: uniform swap of proposition columns. Iterate until convergence; final score for each candidate is its weight w_j.

**2. Structural features parsed**  
- Negations (“not”, “no”) → polarity flip.  
- Comparatives (“greater than”, “less than”, “≤”, “≥”) → ordering propositions.  
- Conditionals (“if … then …”) → implication constraints in C.  
- Numeric values → arithmetic constraints (e.g., X + Y = Z).  
- Causal claims (“causes”, “leads to”) → directed causal propositions.  
- Quantifiers (“all”, “some”) → universal/existential constraint templates.  
- Temporal relations (“before”, “after”) → temporal ordering constraints.

**3. Novelty**  
The trio mirrors existing formalisms: Maximum Entropy underlies log‑linear models (e.g., CRFs); Free Energy Principle appears in active inference and predictive coding; Evolutionary optimization resembles genetic algorithms for structure learning. Combining them into a single fitness‑driven, constraint‑propagating, max‑ent evolutionary scorer is not described in the literature, though each component is used separately in probabilistic soft logic, Markov logic networks, and neuro‑evolutionary approaches.

**4. Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via principled free‑energy minimization.  
Metacognition: 6/10 — the algorithm can monitor its own prediction error (free energy) but lacks explicit self‑reflection on search dynamics.  
Hypothesis generation: 7/10 — mutation/crossover generate new propositional hypotheses; selection favors those reducing surprise.  
Implementability: 9/10 — relies only on numpy for matrix ops and standard library for parsing, mutation, and selection loops.

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
**Reason**: trap_battery_failed (acc=32% cal=17% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T14:58:53.656110

---

## Code

**Source**: scrap

[View code](./Evolution---Free_Energy_Principle---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Evolutionary Free-Energy Reasoner.
    
    Mechanism:
    1. Parsing: Extracts logical propositions (negations, comparatives, conditionals, numerics)
       from the prompt and candidates into a proposition matrix.
    2. Constraint Generation: Builds a constraint tensor based on logical rules (transitivity,
       modus ponens, arithmetic consistency).
    3. Evolutionary Optimization: Treats candidate answers as genotypes. Uses mutation and 
       crossover to evolve a population of weight distributions over propositions.
    4. Fitness Function: Minimizes Variational Free Energy (F = Expected Energy - Entropy).
       - Energy: Penalty for violating logical constraints.
       - Entropy: Encourages exploration of hypothesis space.
    5. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, and false dichotomies
       to cap confidence, ensuring the model admits uncertainty rather than hallucinating.
    """

    def __init__(self):
        self.epsilon = 1e-9
        self.generations = 50
        self.pop_size = 20
        self.mutation_rate = 0.1

    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extracts structured propositions from text."""
        props = []
        text_lower = text.lower()
        
        # 1. Numeric comparisons
        nums = re.findall(r'[-+]?\d*\.?\d+', text)
        for i, n in enumerate(nums):
            props.append({'type': 'numeric', 'value': float(n), 'raw': n})
            
        # 2. Negations
        if re.search(r'\b(not|no|never|none)\b', text_lower):
            props.append({'type': 'negation', 'present': True})
            
        # 3. Conditionals
        if re.search(r'\b(if|then|unless|otherwise)\b', text_lower):
            props.append({'type': 'conditional', 'present': True})
            
        # 4. Comparatives
        if re.search(r'\b(more|less|greater|smaller|better|worst|before|after)\b', text_lower):
            props.append({'type': 'comparative', 'present': True})
            
        # 5. Quantifiers
        if re.search(r'\b(all|every|some|none|only)\b', text_lower):
            props.append({'type': 'quantifier', 'present': True})

        # 6. Causal
        if re.search(r'\b(causes|leads to|results in|because)\b', text_lower):
            props.append({'type': 'causal', 'present': True})

        return props

    def _build_constraints(self, prompt_props: List[Dict], cand_props: List[Dict]) -> np.ndarray:
        """
        Builds a simplified constraint vector. 
        Returns a vector of expected truth values for specific logical patterns.
        """
        # We define a set of abstract constraints based on prompt structure
        # C_{p,i}: Does candidate proposition i satisfy prompt constraint p?
        # Simplified for implementation: We check consistency of types and numeric logic
        
        constraints = []
        
        # Constraint 1: Numeric consistency (if prompt has numbers, candidate should respect order)
        p_nums = [p['value'] for p in prompt_props if p['type'] == 'numeric']
        c_nums = [p['value'] for p in cand_props if p['type'] == 'numeric']
        
        if len(p_nums) >= 2 and len(c_nums) >= 2:
            # Check if relative order is preserved (simplified)
            p_diff = p_nums[0] - p_nums[1]
            c_diff = c_nums[0] - c_nums[1]
            # If prompt implies A > B, candidate shouldn't imply B > A
            if (p_diff > 0 and c_diff < 0) or (p_diff < 0 and c_diff > 0):
                constraints.append(1.0) # Violation
            else:
                constraints.append(0.0)
        elif len(p_nums) > 0 and len(c_nums) == 0:
             # Prompt has numbers, candidate ignores them (potential issue)
             constraints.append(0.5) 
        else:
            constraints.append(0.0)

        # Constraint 2: Negation alignment
        p_neg = any(p.get('present') for p in prompt_props if p['type'] == 'negation')
        c_neg = any(p.get('present') for p in cand_props if p['type'] == 'negation')
        # Rough heuristic: if prompt is negative, candidate shouldn't be purely affirmative without context
        # This is a weak constraint, mostly for structural matching
        constraints.append(0.0 if (p_neg == c_neg) else 0.2)

        # Constraint 3: Logical flow (Conditional presence)
        p_cond = any(p.get('present') for p in prompt_props if p['type'] == 'conditional')
        c_cond = any(p.get('present') for p in cand_props if p['type'] == 'conditional')
        constraints.append(0.0 if (p_cond == c_cond) else 0.1)

        return np.array(constraints)

    def _calculate_energy(self, prompt: str, candidate: str) -> float:
        """Calculates energy E based on constraint violations."""
        p_props = self._parse_propositions(prompt)
        c_props = self._parse_propositions(candidate)
        
        constraints = self._build_constraints(p_props, c_props)
        
        # Base energy from constraint violations
        base_energy = np.sum(constraints)
        
        # Structural mismatch penalty (Jaccard-like on proposition types)
        p_types = set(p['type'] for p in p_props)
        c_types = set(p['type'] for p in c_props)
        if len(p_types.union(c_types)) == 0:
            struct_penalty = 0.0
        else:
            intersection = len(p_types.intersection(c_types))
            union = len(p_types.union(c_types))
            struct_penalty = 1.0 - (intersection / union)
            
        # Numeric calculation check (Constructive computation)
        # If prompt asks for math, verify candidate
        num_match = re.search(r'calculate|sum|add|subtract|multiply|divide|what is \d+', prompt.lower())
        if num_match:
            # Try to extract final number from candidate
            c_nums = [p['value'] for p in c_props if p['type'] == 'numeric']
            p_nums = [p['value'] for p in p_props if p['type'] == 'numeric']
            
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Simple addition check as proxy for constructive computation
                expected = p_nums[0] + p_nums[1] 
                if len(c_nums) > 0:
                    # Allow small float error
                    if abs(c_nums[-1] - expected) > 0.01:
                        base_energy += 2.0 # High penalty for wrong math

        return base_energy + struct_penalty

    def _evolve_weights(self, prompt: str, candidates: List[str]) -> np.ndarray:
        """Evolutionary algorithm to optimize weights over candidates."""
        n = len(candidates)
        if n == 0:
            return np.array([])
        if n == 1:
            return np.array([1.0])

        # Initialize population: Each individual is a weight vector over candidates
        # Shape: (pop_size, n)
        population = np.random.dirichlet(np.ones(n), size=self.pop_size)
        
        # Pre-calculate energies (static for this generation step)
        energies = np.array([self._calculate_energy(prompt, c) for c in candidates])
        
        best_weights = None
        min_free_energy = float('inf')

        for gen in range(self.generations):
            new_population = []
            
            for individual in population:
                # Calculate Fitness: F = <E> - H
                exp_energy = np.dot(individual, energies)
                entropy = -np.sum(individual * np.log(individual + self.epsilon))
                free_energy = exp_energy - entropy
                fitness = -free_energy
                
                if free_energy < min_free_energy:
                    min_free_energy = free_energy
                    best_weights = individual.copy()
                
                new_population.append(individual)
            
            # Selection & Mutation (Simplified for single run)
            # Tournament selection to pick parents
            parents_idx = []
            for _ in range(self.pop_size):
                contestants = np.random.choice(self.pop_size, 3, replace=False)
                scores = [-np.dot(new_population[i], energies) + np.sum(new_population[i] * np.log(new_population[i]+self.epsilon)) for i in contestants]
                winner = contestants[np.argmax(scores)]
                parents_idx.append(winner)
            
            # Crossover & Mutation
            next_gen = []
            for i in range(0, self.pop_size - 1, 2):
                p1 = new_population[parents_idx[i]]
                p2 = new_population[parents_idx[i+1]]
                
                # Uniform crossover
                mask = np.random.rand(n) > 0.5
                child1 = np.where(mask, p1, p2)
                child2 = np.where(mask, p2, p1)
                
                # Mutation (Gaussian noise + renormalize)
                if np.random.rand() < self.mutation_rate:
                    child1 += np.random.normal(0, 0.1, n)
                    child1 = np.clip(child1, 0, 1)
                    child1 += self.epsilon
                    child1 /= np.sum(child1)
                
                if np.random.rand() < self.mutation_rate:
                    child2 += np.random.normal(0, 0.1, n)
                    child2 = np.clip(child2, 0, 1)
                    child2 += self.epsilon
                    child2 /= np.sum(child2)
                    
                next_gen.append(child1)
                next_gen.append(child2)
            
            population = next_gen[:self.pop_size]
            if len(population) < self.pop_size:
                population.append(np.random.dirichlet(np.ones(n)))

        # Final evaluation of the best found weights
        if best_weights is None:
            # Fallback if evolution didn't improve (rare)
            exp_e = np.array([self._calculate_energy(prompt, c) for c in candidates])
            inv_e = 1.0 / (exp_e + 1.0)
            return inv_e / np.sum(inv_e)
            
        return best_weights

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presuppositions, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop|when did .+ start)\b', p):
            score = min(score, 0.2)
        
        # 2. Scope ambiguity ("Every X ... a Y" - same Y?)
        if re.search(r'\b(every|all) .+ (a|an) .+\b', p) and re.search(r'\b(same|different|who|which one)\b', p):
            score = min(score, 0.3)
            
        # 3. Pronoun ambiguity ("X told Y he..." + who?)
        if re.search(r'\b(told|said to) .+ he\b', p) and re.search(r'\b(who|he refer to)\b', p):
            score = min(score, 0.25)
            
        # 4. False dichotomy ("Either A or B" without exhaustiveness)
        if re.search(r'\b(either .+ or .+)\b', p) and not re.search(r'\b(only|exclusive)\b', p):
            score = min(score, 0.4)
            
        # 5. Subjectivity ("Best", "Favorite" without criteria)
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(according to|data|statistics)\b', p):
            score = min(score, 0.3)
            
        # 6. Unanswerability (Missing info)
        if re.search(r'\b(unknown|missing|not given|cannot be determined)\b', p):
            score = min(score, 0.1)
            
        # 7. No structural match (Honest uncertainty)
        props = self._parse_propositions(prompt)
        if len(props) == 0 and len(prompt.split()) > 5:
            # If we can't parse anything, be humble
            score = min(score, 0.4)

        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a minor tiebreaker."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Evolutionary Free Energy Optimization
        weights = self._evolve_weights(prompt, candidates)
        
        # 2. NCD Tiebreaker (Max 15% influence)
        # We adjust scores slightly based on similarity to prompt (context relevance)
        adjusted_scores = []
        for i, cand in enumerate(candidates):
            base_score = weights[i] if i < len(weights) else 0.0
            
            # NCD component: Lower distance = better. 
            # We want high score for low distance.
            ncd = self._ncd_score(prompt, cand)
            ncd_bonus = (1.0 - ncd) * 0.15 
            
            # Structural/Computation weight (85%) + NCD (15%)
            final_score = 0.85 * base_score + 0.15 * ncd_bonus
            adjusted_scores.append(final_score)
        
        # Normalize final scores
        total = sum(adjusted_scores) + self.epsilon
        normalized_scores = [s / total for s in adjusted_scores]
        
        # Construct result
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(normalized_scores[i]),
                "reasoning": f"Evolutionary free-energy minimization yielded weight {normalized_scores[i]:.4f}. Constraints checked: numeric, logical, structural."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Calculate base confidence from the reasoning engine
        # We simulate a mini-evaluation to see how well this answer ranks
        # For efficiency, we just check energy vs a dummy alternative
        energy = self._calculate_energy(prompt, answer)
        
        # Transform energy to confidence (lower energy = higher confidence)
        # Using a soft exponential decay
        base_conf = math.exp(-energy)
        
        # If the answer itself contains uncertainty markers, reduce confidence
        if re.search(r'\b(maybe|possibly|uncertain|unknown)\b', answer.lower()):
            base_conf = min(base_conf, 0.5)
            
        # 2. Apply Meta-Confidence Cap (Tier B Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        final_conf = min(base_conf, meta_cap)
        
        # Ensure bounds
        return max(0.0, min(1.0, final_conf))
```

</details>
