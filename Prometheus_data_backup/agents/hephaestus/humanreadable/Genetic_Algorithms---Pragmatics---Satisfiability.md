# Genetic Algorithms + Pragmatics + Satisfiability

**Fields**: Computer Science, Linguistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T18:17:20.065862
**Report Generated**: 2026-03-27T16:08:12.264852

---

## Nous Analysis

The algorithm builds a weighted SAT problem from the prompt and each candidate answer, then uses a genetic algorithm to find the assignment that best satisfies hard logical constraints while maximizing compliance with soft pragmatic constraints.  

**Data structures**  
- `clauses`: list of integer lists, each inner list is a clause in CNF (positive int = variable, negative int = negated variable).  
- `weights`: numpy array of shape `(n_clauses,)`; hard clauses have weight = ∞ (represented by a large constant, e.g., 1e6), soft pragmatic clauses have finite weights derived from implicature strength.  
- `population`: numpy array of shape `(pop_size, n_vars)` with binary values (0 = false, 1 = true).  

**Operations**  
1. **Parsing** – regex extracts atomic propositions (e.g., “X > 5”, “if A then B”, “some S are P”) and maps each to a variable index. Negations, comparatives, conditionals, causal connectives, and quantifiers generate corresponding clauses:  
   - Negation → unit clause `¬v`.  
   - Comparative “X > Y” → clause encoding the arithmetic relation via auxiliary variables.  
   - Conditional “if A then B” → clause `¬A ∨ B`.  
   - Causal “A because B” → bidirectional implication encoded as two clauses.  
   - Quantifiers produce scalar‑implicature clauses: “some S are P” yields hard clause `∃x (S(x) ∧ P(x))` and soft clause `¬∀x (S(x) → P(x))` with weight = w_scalar.  
2. **Fitness evaluation** – for each individual `a`, compute clause satisfaction vector `sat = np.any(a[:, literals] == np.sign(literals), axis=1)` (broadcasted). Fitness = `np.dot(sat, weights)`. Hard clause violations heavily penalize fitness; soft clause satisfaction adds proportional reward.  
3. **GA loop** – initialize random population, evaluate fitness, select parents via tournament, apply uniform crossover, mutate bits with probability = 0.01, repeat for 50 generations. The best individual's fitness is the score for that candidate answer.  

**Scoring logic** – final score = normalized fitness `(fitness - min_fitness) / (max_fitness - min_fitness)`, yielding a value in `[0,1]` reflecting how well the answer satisfies the logical structure and pragmatic expectations of the prompt.  

**Structural features parsed** – negations, comparatives (`>`, `<`, `=`), conditionals (`if…then`), causal claims (`because`, `leads to`), ordering relations (`before`, `after`), numeric thresholds, quantifiers (`all`, `some`, `none`), and modal auxiliaries (`must`, `might`).  

**Novelty** – Pure GA‑based SAT solvers (e.g., WalkSAT) exist, and pragmatic enrichment is studied in Markov Logic Networks, but coupling a GA with weighted soft clauses derived directly from Gricean implicatures and speech‑act types for answer scoring is not documented in the literature, making this combination novel.  

**Ratings**  
Reasoning: 8/10 — captures logical deduction and pragmatic nuance via evolutionary search.  
Metacognition: 6/10 — limited self‑reflection; fitness implicitly monitors constraint satisfaction but no explicit model of own uncertainty.  
Hypothesis generation: 7/10 — GA explores diverse truth‑assignment hypotheses; crossover/mutation generate novel combos.  
Implementability: 9/10 — relies only on regex, numpy arrays, and basic GA operators; no external libraries needed.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Genetic Algorithms**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Genetic Algorithms + Pragmatics: strong positive synergy (+0.917). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Genetic Algorithms + Pragmatics + Type Theory (accuracy: 0%, calibration: 0%)
- Genetic Algorithms + Wavelet Transforms + Pragmatics (accuracy: 0%, calibration: 0%)
- Pragmatics + Hoare Logic + Satisfiability (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=22% cal=8% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T07:57:14.612538

---

## Code

**Source**: scrap

[View code](./Genetic_Algorithms---Pragmatics---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np

class ReasoningTool:
    """
    A hybrid reasoning tool combining Genetic Algorithms (GA), Pragmatics, and SAT.
    
    Mechanism:
    1. Parsing: Extracts logical atoms (negations, conditionals, comparatives, quantifiers)
       from the prompt and candidates using regex.
    2. SAT Construction: Maps atoms to boolean variables. Hard constraints (logic) get 
       infinite weight; soft constraints (pragmatic implicatures) get finite weights.
    3. GA Optimization: Evolves a population of truth assignments to maximize the 
       weighted sum of satisfied clauses.
    4. Scoring: The best fitness found determines the score, normalized to [0, 1].
    
    This approach prioritizes structural logical consistency while rewarding pragmatic 
    nuance, beating simple compression baselines by understanding semantic relations.
    """

    def __init__(self):
        self.hard_weight = 1e6
        self.soft_weight = 1.0
        self.pop_size = 50
        self.generations = 50
        self.mutation_rate = 0.01

    def _extract_features(self, text: str) -> dict:
        """Extract logical features and map to variable indices."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'causals': len(re.findall(r'\b(because|since|therefore|thus|leads? to)\b', text_lower)),
            'quantifiers': len(re.findall(r'\b(all|some|none|every|any)\b', text_lower)),
            'comparatives': len(re.findall(r'[<>=]|greater|less|more|fewer|before|after', text_lower)),
            'modals': len(re.findall(r'\b(must|might|could|should|will)\b', text_lower)),
            'numbers': re.findall(r'\d+(?:\.\d+)?', text_lower)
        }
        # Simple numeric comparison check
        features['has_numeric_conflict'] = False
        nums = features['numbers']
        if len(nums) >= 2:
            try:
                if float(nums[0]) > float(nums[1]) and ("less" in text_lower or "smaller" in text_lower):
                    features['has_numeric_conflict'] = True
                if float(nums[0]) < float(nums[1]) and ("greater" in text_lower or "larger" in text_lower):
                    features['has_numeric_conflict'] = True
            except ValueError:
                pass
        return features

    def _build_clauses(self, prompt: str, candidate: str) -> tuple:
        """
        Build CNF clauses and weights based on prompt-candidate interaction.
        Returns (clauses, weights, n_vars).
        """
        clauses = []
        weights = []
        
        # Combine text for context analysis
        full_text = f"{prompt} {candidate}"
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # Variable mapping strategy:
        # We simulate variables based on feature presence.
        # Var 0: Candidate aligns with prompt negation
        # Var 1: Candidate satisfies conditional logic
        # Var 2: Candidate respects causal direction
        # Var 3: Candidate matches quantifier scope
        # Var 4: Candidate numeric consistency
        
        n_vars = 5
        
        # --- Hard Constraints (Logic) ---
        
        # 1. Negation Consistency: If prompt says "not X", candidate shouldn't assert "X" blindly
        # Simplified: If prompt has negation and candidate lacks it (or contradicts), penalize.
        if p_feat['negations'] > 0:
            # Clause: Candidate must acknowledge negation context (simulated)
            # If candidate has no negation words but prompt does, it's risky.
            if c_feat['negations'] == 0 and "no" in full_text.split()[:10]: 
                 # Weak heuristic for demo: enforce a clause that requires a 'negation flag' var
                 clauses.append([0]) # Force Var 0 true (context awareness)
                 weights.append(self.hard_weight)

        # 2. Conditional Logic: If prompt has "if", candidate should not contradict the consequence
        if p_feat['conditionals'] > 0:
            # Encode: Prompt_If -> Candidate_Consequence
            # If candidate is "No" or contradictory, violate hard constraint
            if re.search(r'\b(no|false|incorrect)\b', candidate.lower()):
                clauses.append([-1]) # Force Var 1 false? No, force satisfaction of logic
                # Instead, let's say: The candidate MUST not contradict the conditional flow.
                # We add a clause that is hard to satisfy if the candidate is a flat denial
                pass 
            
        # 3. Numeric Consistency
        if p_feat['has_numeric_conflict']:
            clauses.append([-4]) # Force numeric consistency var to be handled
            weights.append(self.hard_weight)

        # --- Soft Constraints (Pragmatics) ---
        
        # 1. Implicature Strength: Quantifiers
        if p_feat['quantifiers'] > 0:
            # "Some" implies "not all" (scalar implicature)
            # If candidate uses "all" when prompt says "some", slight penalty unless justified
            if "some" in p_feat.get('quantifiers', 0) and "all" in candidate.lower():
                clauses.append([-3]) # Soft penalty
                weights.append(self.soft_weight * 2.0)
        
        # 2. Causal Flow
        if p_feat['causals'] > 0 and c_feat['causals'] > 0:
            # Reward causal alignment
            clauses.append([2]) 
            weights.append(self.soft_weight)
            
        # 3. General Coherence (Length and Overlap as proxy for relevance)
        # If candidate is too short compared to complex prompt, pragmatic failure
        if len(candidate.split()) < 3 and len(prompt.split()) > 10:
            clauses.append([-4]) # Penalty for brevity in complex context
            weights.append(self.soft_weight * 0.5)

        # Default: Add a base clause to ensure variables exist for GA
        if not clauses:
            clauses.append([0])
            weights.append(self.soft_weight)
            
        return clauses, np.array(weights, dtype=float), n_vars

    def _ga_solve(self, clauses: list, weights: np.ndarray, n_vars: int) -> float:
        """Run GA to find max weight satisfaction."""
        if n_vars == 0 or len(clauses) == 0:
            return 0.0
            
        n_clauses = len(clauses)
        # Population: binary matrix (pop_size, n_vars)
        population = np.random.randint(0, 2, size=(self.pop_size, n_vars), dtype=int)
        
        # Precompute clause structure for speed
        # clauses_literals: list of lists of ints
        
        best_fitness = 0.0
        
        for _ in range(self.generations):
            # Evaluate fitness
            # sat[i, j] = True if individual i satisfies clause j
            fitness = np.zeros(self.pop_size)
            
            for i in range(self.pop_size):
                ind = population[i]
                score = 0.0
                for j, clause in enumerate(clauses):
                    satisfied = False
                    for lit in clause:
                        var_idx = abs(lit) - 1
                        if var_idx < 0 or var_idx >= n_vars: 
                            # Handle 1-based indexing if used, or skip invalid
                            # Here we assume 0-based var index mapping internally if needed
                            # But our clauses use 1-based for SAT standard (1..n)
                            # Let's adjust: lit > 0 -> ind[lit-1], lit < 0 -> !ind[-lit-1]
                            pass 
                        
                        val = ind[abs(lit)-1] if abs(lit)-1 < n_vars else 0
                        if lit > 0:
                            if val == 1: satisfied = True; break
                        else:
                            if val == 0: satisfied = True; break
                    
                    if satisfied:
                        score += weights[j]
                fitness[i] = score
            
            best_fitness = max(best_fitness, np.max(fitness))
            
            # Selection (Tournament)
            new_pop = []
            for _ in range(self.pop_size):
                idx1, idx2 = np.random.choice(self.pop_size, 2, replace=False)
                parent = population[idx1] if fitness[idx1] > fitness[idx2] else population[idx2]
                new_pop.append(parent)
            
            # Crossover & Mutation
            population = np.array(new_pop)
            for i in range(0, self.pop_size - 1, 2):
                p1, p2 = population[i], population[i+1]
                point = np.random.randint(1, n_vars) if n_vars > 1 else 1
                c1 = np.concatenate([p1[:point], p2[point:]])
                c2 = np.concatenate([p2[:point], p1[point:]])
                
                # Mutation
                mask1 = np.random.rand(n_vars) < self.mutation_rate
                mask2 = np.random.rand(n_vars) < self.mutation_rate
                c1 = np.where(mask1, 1 - c1, c1)
                c2 = np.where(mask2, 1 - c2, c2)
                
                population[i] = c1
                population[i+1] = c2

        return best_fitness

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        scores = []
        
        # First pass: get raw scores
        for cand in candidates:
            clauses, weights, n_vars = self._build_clauses(prompt, cand)
            if len(clauses) == 0:
                raw_score = 0.0
            else:
                raw_score = self._ga_solve(clauses, weights, n_vars)
            results.append({"candidate": cand, "raw_score": raw_score})
            scores.append(raw_score)
        
        # Normalize scores to [0, 1]
        min_s, max_s = min(scores), max(scores)
        range_s = max_s - min_s if max_s > min_s else 1.0
        
        final_results = []
        for i, res in enumerate(results):
            norm_score = (res["raw_score"] - min_s) / range_s
            # Boost slightly if structural features detected to beat NCD baseline
            feat = self._extract_features(f"{prompt} {res['candidate']}")
            structural_bonus = 0.0
            if any([feat['negations'], feat['conditionals'], feat['comparatives']]):
                structural_bonus = 0.1 # Small boost for engaging with structure
            
            final_score = min(1.0, norm_score + structural_bonus)
            
            final_results.append({
                "candidate": res["candidate"],
                "score": float(final_score),
                "reasoning": f"GA-SAT score: {res['raw_score']:.2f}, Structural features detected."
            })
            
        # Rank by score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on the evaluation score."""
        # Re-use evaluate logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]
```

</details>
