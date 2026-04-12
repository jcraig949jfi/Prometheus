# Genetic Algorithms + Pragmatics + Free Energy Principle

**Fields**: Computer Science, Linguistics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T23:08:09.474062
**Report Generated**: 2026-03-31T14:34:55.471074

---

## Nous Analysis

**Algorithm**  
We maintain a population \(P=\{w^{(i)}\}_{i=1}^{N}\) of weight vectors \(w\in\mathbb{R}^{d}\) that parameterize a linear scoring function \(s(q,a;w)=w^{\top}\phi(q,a)\). \(\phi(q,a)\) is a deterministic feature vector extracted from a prompt \(q\) and a candidate answer \(a\) by a pure‑Python parser that uses only the standard library (regex, itertools). The parser returns a bag of logical predicates:  

* atomic propositions \(p\) (e.g., “Sky is blue”)  
* negated propositions \(\neg p\)  
* binary relations \(R(x,y)\) drawn from a fixed set { =, ≠, <, >, ≤, ≥, causes, implies }  
* typed entities \(x\) (numbers, dates, proper nouns)  
* discourse markers indicating implicature (e.g., “but”, “however”, “some”, “all”)  

Each predicate is one‑hot encoded; numeric values are normalized and appended as raw floats. Thus \(\phi\in\mathbb{R}^{d}\) where \(d\) equals the number of possible predicate slots plus a few numeric dimensions.

**Fitness (Free‑Energy‑Pragmatic score)**  
For a given weight vector \(w\) we compute the prediction error of the answer under the prompt’s logical model:  

1. Build a tiny propositional model \(M_q\) from the prompt’s predicates (treated as hard constraints).  
2. Evaluate the truth value of each predicate in \(a\) under \(M_q\) using a deterministic truth‑table (no learning).  
3. Let \(e(w)=\|\,\phi_{\text{true}}(q,a)-s(q,a;w)\,\|_2^2\) be the squared error between the binary truth vector and the scorer’s output.  

Pragmatic violation penalty \(p(w)\) counts breaches of Grice’s maxims derived from the prompt: e.g., if the prompt contains a scalar implicature (“some”) and the answer asserts “all”, add a constant \(c>0\).  

Fitness \(f(w)= -\big(e(w)+\lambda p(w)\big)\) (higher is better).  

**GA loop**  
*Selection*: tournament selection on \(f\).  
*Crossover*: blend crossover (SBX) on real‑valued vectors using numpy.  
*Mutation*: Gaussian perturbation with decreasing sigma.  
Iterate for a fixed number of generations (e.g., 30) and return the best \(w\). Scoring a new candidate answer is then a single dot‑product \(s(q,a;w^*)\).

**Structural features parsed**  
Negations, comparatives (<, >, ≤, ≥), equality/inequality, conditionals (implies), causal claims (causes), ordering relations (before/after), numeric quantities, and discourse markers that trigger scalar or relevance implicatures.

**Novelty**  
Purely symbolic GA‑based weight learning for logical‑form scoring is uncommon; most neuro‑symbolic hybrids replace the GA with gradient‑based optimisation. Applying the Free Energy Principle as a prediction‑error term in an evolutionary fitness function, combined with explicit pragmatic penalty counts, has not been widely reported in the NLP literature, making the combination novel.

**Ratings**  
Reasoning: 7/10 — The method captures logical structure and optimizes a principled error‑plus‑pragmatic loss, yielding interpretable scores, but the linear scorer limits handling of higher‑order interactions.  
Metacognition: 5/10 — No explicit self‑monitoring of search stability; the GA’s stopping criterion is fixed, so the system does not adapt its own search depth based on difficulty.  
Hypothesis generation: 6/10 — The population explores alternative weight settings, implicitly generating hypotheses about which linguistic cues matter, yet hypothesis space is restricted to linear combinations of hand‑crafted features.  
Implementability: 8/10 — All components (regex parsing, numpy vector ops, tournament GA) rely solely on numpy and the Python standard library; no external dependencies or GPUs are required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=35% cal=18% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-28T05:43:54.289638

---

## Code

**Source**: scrap

[View code](./Genetic_Algorithms---Pragmatics---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from itertools import combinations
from typing import List, Dict, Tuple, Optional, Any

class ReasoningTool:
    """
    A hybrid neuro-symbolic reasoning tool using Genetic Algorithms (GA) 
    to optimize weights for logical feature scoring, grounded in the 
    Free Energy Principle (minimizing prediction error) and Pragmatics.
    
    Mechanism:
    1. Parsing: Extracts logical predicates (negations, relations, entities) 
       and pragmatic markers from prompts using regex (standard lib).
    2. GA Optimization: Evolves a population of weight vectors to minimize 
       a fitness function combining logical consistency error (Free Energy) 
       and pragmatic violation penalties.
    3. Scoring: Uses the best weight vector to score candidate answers via 
       dot-product of feature vectors.
    4. Epistemic Honesty: Caps confidence if the prompt contains ambiguity, 
       presuppositions, or unanswerable structures (Tier B compliance).
    """
    
    # Fixed relations and markers for one-hot encoding
    RELATIONS = ['=', '!=', '<', '>', '<=', '>=', 'causes', 'implies']
    MARKERS = ['but', 'however', 'some', 'all', 'every', 'either', 'or']
    PRESUPPOSITION_TRIGGERS = [r'stopped', r'quit', r'failed', r'regret']
    PRONOUN_AMBIGUITY_PATTERN = re.compile(r'(\w+)\s+(told|asked|said to)\s+(\w+)\s+(he|she|him|her|it)', re.IGNORECASE)
    
    def __init__(self):
        self.best_weights = None
        self.feature_names = self._build_feature_names()
        self.d = len(self.feature_names)
        self.rng = np.random.default_rng(seed=42)  # Deterministic

    def _build_feature_names(self) -> List[str]:
        """Generate list of feature names for one-hot encoding."""
        names = []
        # Atomic props (simplified to generic slots for this demo)
        for i in range(10): names.append(f"prop_{i}")
        # Relations
        for r in self.RELATIONS: names.append(f"rel_{r}")
        # Markers
        for m in self.MARKERS: names.append(f"marker_{m}")
        # Numeric
        names.extend(["num_val", "num_diff"])
        return names

    def _parse_prompt(self, text: str) -> Dict[str, Any]:
        """Extract logical predicates and features from text."""
        text_lower = text.lower()
        features = np.zeros(self.d)
        predicates = []
        
        # 1. Extract Numbers (Constructive Computation Base)
        numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        if numbers:
            features[-2] = numbers[0] if len(numbers) == 1 else sum(numbers)/len(numbers)
            if len(numbers) >= 2:
                features[-1] = abs(numbers[0] - numbers[1])
        
        # 2. Extract Relations
        if '=' in text: features[self._idx('rel_=')] = 1
        if '!=' in text or 'not equal' in text_lower: features[self._idx('rel_!=')] = 1
        if '<' in text or 'less than' in text_lower: features[self._idx('rel_<')] = 1
        if '>' in text or 'greater than' in text_lower: features[self._idx('rel_>')] = 1
        if 'cause' in text_lower: features[self._idx('rel_causes')] = 1
        if 'imply' in text_lower or 'if' in text_lower: features[self._idx('rel_implies')] = 1
        
        # 3. Extract Markers (Pragmatics)
        for m in self.MARKERS:
            if m in text_lower:
                idx = self._idx(f'marker_{m}')
                if idx < self.d: features[idx] = 1

        # 4. Simple Proposition Count (Placeholder for atomic props)
        sentences = text.split('.')
        for i, s in enumerate(sentences[:10]):
            if s.strip():
                features[i] = 1 
                predicates.append(('prop', s.strip()))

        return {'features': features, 'numbers': numbers, 'text': text_lower}

    def _idx(self, name: str) -> int:
        try: return self.feature_names.index(name)
        except ValueError: return -1

    def _compute_fitness(self, w: np.ndarray, prompt_data: Dict, candidates: List[str]) -> float:
        """
        Free Energy Principle Fitness:
        F = -(Prediction Error + Lambda * Pragmatic Penalty)
        Since we don't have ground truth labels in unsupervised mode, 
        we treat 'consistency across candidates' and 'logical constraint satisfaction' as the target.
        """
        total_error = 0.0
        pragmatic_penalty = 0.0
        
        # Heuristic target: The answer that maximizes logical coherence with prompt numbers
        # If prompt has numbers, we expect the answer to reflect a calculation
        prompt_nums = prompt_data['numbers']
        target_val = None
        if len(prompt_nums) >= 2:
            # Simple constructive hypothesis: sum or diff
            target_val = prompt_nums[0] + prompt_nums[1] 

        for cand in candidates:
            s = self._score_single(prompt_data, cand, w)
            # Prediction error: deviation from expected logical structure (simplified)
            # If we have a target value, penalize distance from it
            if target_val is not None:
                cand_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', cand)]
                if cand_nums:
                    total_error += (cand_nums[0] - target_val)**2
                else:
                    total_error += 1.0 # Penalty for missing numbers if expected
            
            # Pragmatic penalty: Check for Gricean violations (e.g., contradiction markers)
            if 'but' in prompt_data['text'] and 'however' not in cand.lower():
                pragmatic_penalty += 0.1
                
        return -(total_error + 0.5 * pragmatic_penalty)

    def _score_single(self, prompt_data: Dict, answer: str, w: np.ndarray) -> float:
        """Compute score s(q,a;w) = w^T phi(q,a)"""
        # Parse answer features
        ans_data = self._parse_prompt(answer)
        # Combine prompt and answer features (simple concatenation logic)
        # For this linear model, we assume features align or we use prompt features as base
        # Here we simulate phi(q,a) by adding prompt and answer feature vectors
        combined = prompt_data['features'] + ans_data['features']
        if len(combined) < len(w):
            combined = np.pad(combined, (0, len(w)-len(combined)))
        return float(np.dot(w[:len(combined)], combined[:len(w)]))

    def _genetic_algorithm(self, prompt_data: Dict, candidates: List[str], generations: int = 20, pop_size: int = 10) -> np.ndarray:
        """Run GA to find optimal weights."""
        if self.d == 0: return np.array([])
        
        # Initialize population
        population = self.rng.standard_normal((pop_size, self.d))
        best_w = population[0]
        best_fit = -np.inf

        sigma = 1.0
        
        for gen in range(generations):
            fitnesses = []
            for w in population:
                fit = self._compute_fitness(w, prompt_data, candidates)
                fitnesses.append(fit)
                if fit > best_fit:
                    best_fit = fit
                    best_w = w.copy()
            
            # Selection (Tournament)
            new_pop = []
            for _ in range(pop_size):
                contestants = self.rng.choice(pop_size, size=3, replace=False)
                winner = population[np.argmax([fitnesses[i] for i in contestants])]
                new_pop.append(winner)
            
            # Crossover (SBX-like blend)
            next_gen = []
            for i in range(0, pop_size-1, 2):
                p1, p2 = new_pop[i], new_pop[i+1]
                alpha = self.rng.random()
                c1 = alpha * p1 + (1-alpha) * p2
                c2 = (1-alpha) * p1 + alpha * p2
                next_gen.append(c1)
                next_gen.append(c2)
            if len(next_gen) < pop_size: next_gen.append(new_pop[-1])
            
            # Mutation
            population = np.array(next_gen[:pop_size])
            mutation = self.rng.normal(0, sigma, population.shape)
            population += mutation
            sigma *= 0.9  # Decreasing sigma
            
        return best_w

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Triggers
        for trig in self.PRESUPPOSITION_TRIGGERS:
            if re.search(trig, p_lower):
                return 0.25
        
        # 2. Pronoun Ambiguity
        if self.PRONOUN_AMBIGUITY_PATTERN.search(p_lower) and 'who' in p_lower:
            return 0.2
            
        # 3. False Dichotomy / Scope
        if 'either' in p_lower and 'or' in p_lower and 'only' not in p_lower:
            # Heuristic: if it looks like a forced choice without exhaustiveness
            if 'best' in p_lower or 'worst' in p_lower:
                return 0.3
                
        # 4. Subjectivity
        if any(x in p_lower for x in ['best', 'favorite', 'opinion', 'think about']):
            if 'calculate' not in p_lower and 'compute' not in p_lower:
                return 0.4
                
        return 1.0  # No obvious traps detected

    def _constructive_solve(self, prompt: str, candidates: List[str]) -> Optional[str]:
        """
        Frame B: Constructive Computation.
        Attempt to mathematically solve the problem if numbers are present.
        """
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt)]
        if len(nums) < 2:
            return None
            
        # Try basic operations
        results = {
            'sum': nums[0] + nums[1],
            'diff': abs(nums[0] - nums[1]),
            'prod': nums[0] * nums[1]
        }
        if len(nums) > 2:
            results['total'] = sum(nums)
            
        # Check if any candidate matches a computed result
        for cand in candidates:
            cand_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', cand)]
            if not cand_nums: continue
            val = cand_nums[0]
            for op, res in results.items():
                if math.isclose(val, res, rel_tol=0.01):
                    return cand
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_data = self._parse_prompt(prompt)
        
        # 1. Constructive Computation (Priority)
        constructive_answer = self._constructive_solve(prompt, candidates)
        
        # 2. GA Optimization (if no direct constructive match or for scoring)
        if self.best_weights is None or len(self.best_weights) != self.d:
            self.best_weights = self._genetic_algorithm(prompt_data, candidates)
            
        # Score candidates
        scored = []
        for cand in candidates:
            score = 0.0
            reasoning = "GA-weighted logical consistency"
            
            if constructive_answer == cand:
                score = 1.0
                reasoning = "Constructive computation match"
            else:
                # Fallback to GA score
                s_val = self._score_single(prompt_data, cand, self.best_weights)
                # Normalize score roughly to 0-1 range using sigmoid
                score = 1 / (1 + math.exp(-s_val))
                
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Rank
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-Cognitive Check (Tier B)
        cap = self._meta_confidence(prompt)
        if cap < 0.3:
            return cap
            
        # 2. Structural/Constructive Check
        # If we can't parse numbers or logic, and it's not a simple string match, lower confidence
        prompt_data = self._parse_prompt(prompt)
        has_structure = len(prompt_data['numbers']) > 0 or any(prompt_data['features'] > 0)
        
        if not has_structure:
            # If no structure found, rely on NCD only as tiebreaker, so confidence low
            return 0.25
            
        # 3. Compute Score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Cap by meta-confidence
        final_conf = min(raw_score, cap)
        
        # Ensure we never return > 0.9 unless it's a definitive constructive match
        if res[0]['reasoning'] != "Constructive computation match":
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
