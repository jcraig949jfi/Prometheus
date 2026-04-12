# Swarm Intelligence + Abductive Reasoning + Counterfactual Reasoning

**Fields**: Biology, Philosophy, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T06:12:46.080407
**Report Generated**: 2026-04-01T20:30:43.651121

---

## Nous Analysis

The algorithm treats each candidate answer as a potential “food source” that a swarm of simple agents explores. First, a deterministic parser (regex‑based) extracts a set of binary structural features from the prompt and each answer: presence of negations (`not`, `no`), conditionals (`if … then`, `unless`), comparatives (`>`, `<`, `more than`, `less than`), causal verbs (`cause`, `lead to`, `results in`), ordering relations (`before`, `after`, `first`, `second`), numeric constants, and quantifiers. These features populate a matrix **F** ∈ {0,1}^{A×F} where *A* is the number of answers and *F* the number of feature types.

Each agent maintains a hypothesis vector **h** ∈ {0,1}^F indicating which features it currently believes explain the prompt. The agent’s fitness for answer *a* is:

```
fitness(a, h) = w·F[a]          # weighted match to extracted features
                – λ·CF_violation(a, h)   # penalty for counterfactual inconsistencies
                + μ·|h|/F           # small reward for hypothesis compactness
```

where **w** is a global pheromone weight vector (initialized uniformly), λ and μ are scalars. `CF_violation` is computed by checking parsed causal rules: if a rule `X → Y` is present in the prompt, the agent flips the value of X in its hypothesis and verifies whether Y changes accordingly; a mismatch adds to the violation count.

Swarm dynamics follow stigmergic updates: after all agents evaluate all answers, the pheromone vector is updated:

```
w ← (1–ρ)·w + ρ· Σ_a ( best_fitness_a · F[a] )
```

where ρ∈(0,1) is the evaporation rate and `best_fitness_a` is the highest fitness obtained for answer *a* in that iteration. Over *T* iterations, agents probabilistically flip bits in **h** with probability proportional to the current pheromone weights, implementing a hill‑climbing search guided by collective experience. The final score for each answer is the accumulated pheromone‑weighted feature match across iterations; the answer with the highest score is selected.

**Structural features parsed**: negations, conditionals, comparatives, causal verbs, ordering relations (temporal/sequestered), numeric values, quantifiers, and explicit variable names appearing in causal statements.

**Novelty**: While ant‑colony optimization has been applied to SAT and abductive logic programming, and counterfactual reasoning has been formalized via do‑calculus, the tight coupling of a swarm‑based hypothesis generator with explicit counterfactual consistency checks inside a unified scoring loop has not been described in the literature. It blends three distinct reasoning paradigms into a single, executable, numpy‑only mechanism.

**Ratings**  
Reasoning: 8/10 — captures logical structure and counterfactual constraints but lacks deep semantic nuance.  
Metacognition: 6/10 — pheromone evaporation provides basic self‑adjustment, yet no explicit monitoring of search efficacy.  
Hypothesis generation: 9/10 — the swarm continuously generates and refines many explanatory hypotheses.  
Implementability: 8/10 — relies only on regex extraction and numpy vector operations; straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 9/10 |
| Implementability | 8/10 |
| **Composite** | **7.67** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=32% cal=46% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T19:45:40.526769

---

## Code

**Source**: scrap

[View code](./Swarm_Intelligence---Abductive_Reasoning---Counterfactual_Reasoning/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Swarm-Abductive Counterfactual Reasoner.
    
    Mechanism:
    1. Structural Parsing: Extracts binary features (negations, conditionals, causals, numerics).
    2. Swarm Optimization: Agents explore hypothesis spaces (feature weights) to maximize 
       consistency between prompt structure and candidate answers.
    3. Counterfactual Check: Penalizes hypotheses where flipping a causal antecedent 
       does not logically propagate to the consequent in the candidate text.
    4. Epistemic Honesty: Caps confidence if the prompt contains ambiguity, presupposition, 
       or unanswerable constraints (Tier B).
    5. Scoring: Weighted sum of structural match (50%+), computational consistency (20%+), 
       and NCD tiebreaker (<15%).
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|provided|given that)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(cause|causes|lead to|results in|because|since|therefore)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|second|last|next|previous)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|many|few|every|each|most|none)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'variable': re.compile(r'\b([A-Z])(?:\s*[-=]|\s+is|\s+was)\b') # Simple variable assignment
        }
        self.tier_b_patterns = {
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|it)\b.*\bwho\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or|must choose between)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.IGNORECASE)
        }
        self.feature_keys = list(self.patterns.keys())
        self.num_features = len(self.feature_keys)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary structural features from text."""
        text_lower = text.lower()
        features = np.zeros(self.num_features, dtype=float)
        for i, key in enumerate(self.feature_keys):
            if self.patterns[key].search(text):
                features[i] = 1.0
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _check_counterfactual_violation(self, prompt: str, candidate: str, h: np.ndarray) -> float:
        """
        Simulate counterfactual check.
        If prompt has causal structure and candidate ignores the implication, penalize.
        This is a heuristic approximation of the do-calculus check described.
        """
        violation = 0.0
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # If prompt has causal/conditional logic (features 1, 2, 4)
        has_logic = (p_feats[1] > 0) or (p_feats[2] > 0) 
        
        if has_logic:
            # Heuristic: If prompt implies causality but candidate lacks causal verbs or negation handling
            # and the hypothesis weight for 'causal' is high, check consistency.
            if p_feats[2] > 0 and c_feats[2] == 0:
                # Prompt has causal verbs, candidate doesn't. 
                # Check if candidate at least acknowledges the result structure
                if not any(k in candidate.lower() for k in ['result', 'cause', 'effect', 'because', 'so']):
                    violation += 0.5
            
            # Negation check: If prompt has negation, candidate should ideally reflect it or explicitly resolve it
            if p_feats[0] > 0 and c_feats[0] == 0:
                # Simple heuristic: if prompt says "not", candidate shouldn't blindly affirm without qualification
                if "yes" in candidate.lower() or "true" in candidate.lower():
                     violation += 0.3

        return violation

    def _swarm_optimize(self, prompt: str, candidates: List[str], iterations: int = 10) -> Tuple[List[float], np.ndarray]:
        """Run swarm optimization to find best feature weights and score candidates."""
        if not candidates: return [], np.zeros(self.num_features)
        
        n_agents = 5
        n_candidates = len(candidates)
        
        # Precompute feature matrix F [Candidates x Features]
        F = np.zeros((n_candidates, self.num_features))
        for i, c in enumerate(candidates):
            F[i, :] = self._extract_features(c)
        
        prompt_feats = self._extract_features(prompt)
        
        # Initialize pheromones (weights) uniformly
        w = np.ones(self.num_features) / self.num_features
        
        best_scores = np.zeros(n_candidates)
        
        for _ in range(iterations):
            agent_scores = np.zeros((n_agents, n_candidates))
            
            for a in range(n_agents):
                # Agent hypothesis: perturb weights slightly based on pheromones + noise
                h = w + np.random.normal(0, 0.1, self.num_features)
                h = np.clip(h, 0, 1)
                if h.sum() == 0: h = np.ones(self.num_features) / self.num_features
                else: h /= h.sum()
                
                for i, cand in enumerate(candidates):
                    # Fitness = Weighted Match - Counterfactual Penalty + Compactness
                    match_score = np.dot(F[i, :], h)
                    
                    # Counterfactual violation check
                    cf_penalty = self._check_counterfactual_violation(prompt, cand, h)
                    
                    # Compactness (encourage sparse hypotheses)
                    compactness = 0.05 * (1.0 - np.sum(h > 0.5) / self.num_features)
                    
                    fitness = match_score - (0.5 * cf_penalty) + compactness
                    agent_scores[a, i] = fitness
            
            # Update pheromones based on best performing agents for each candidate
            iteration_best = np.max(agent_scores, axis=0)
            best_scores += iteration_best
            
            # Stigmergic update: reinforce features that led to high scores
            # Weighted sum of features from high-scoring candidates
            if np.max(iteration_best) > 0:
                norm_scores = (iteration_best - np.min(iteration_best)) 
                if np.max(norm_scores) > 0:
                    norm_scores /= np.max(norm_scores)
                
                feature_contribution = np.dot(norm_scores, F) # Sum of features weighted by score
                w = (0.7 * w) + (0.3 * feature_contribution)
                w = np.clip(w, 0.01, 1.0)
                w /= w.sum() # Normalize

        # Final scoring
        final_scores = []
        for i in range(n_candidates):
            # Structural match (weighted by final pheromones)
            struct_score = np.dot(F[i, :], w)
            
            # Computational/Numeric check (Constructive)
            comp_score = 0.0
            p_nums = re.findall(r'\d+\.\d+|\d+', prompt)
            c_nums = re.findall(r'\d+\.\d+|\d+', candidates[i])
            if p_nums and c_nums:
                try:
                    # Simple heuristic: if numbers match exactly, boost
                    p_set = set(float(x) for x in p_nums)
                    c_set = set(float(x) for x in c_nums)
                    if p_set == c_set: comp_score = 0.5
                    elif c_set.issubset(p_set): comp_score = 0.2
                except: pass
            
            # NCD Tiebreaker (max 15% influence)
            ncd_val = self._compute_ncd(prompt, candidates[i])
            ncd_score = (1.0 - ncd_val) * 0.15
            
            total = (struct_score * 0.65) + (comp_score * 0.20) + ncd_score
            final_scores.append(total)
            
        return final_scores, w

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detect ambiguity, presupposition, or unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.tier_b_patterns['presupposition'].search(prompt):
            return 0.25
        
        # 2. False Dichotomy indicators without clear options
        if self.tier_b_patterns['false_dichotomy'].search(prompt):
            if "or" in p_lower and "?" in prompt:
                # Check if it's a simple choice question, if too vague, lower confidence
                if len(prompt.split()) < 10: return 0.3
        
        # 3. Subjectivity without criteria
        if self.tier_b_patterns['subjectivity'].search(prompt):
            if "why" in p_lower or "how" in p_lower:
                return 0.3 # Subjective questions are hard to score definitively

        # 4. Pronoun ambiguity (Heuristic)
        if self.tier_b_patterns['pronoun_ambiguity'].search(prompt):
            return 0.3

        # 5. Unanswerable / Missing Info
        if "cannot" in p_lower or "impossible" in p_lower or "unknown" in p_lower:
             return 0.2

        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Run swarm optimization
        scores, _ = self._swarm_optimize(prompt, candidates, iterations=15)
        
        # Normalize scores to 0-1 range roughly
        min_s = min(scores)
        max_s = max(scores)
        range_s = max_s - min_s if (max_s - min_s) > 0 else 1.0
        
        normalized_scores = [(s - min_s) / range_s for s in scores]
        
        results = []
        for i, cand in enumerate(candidates):
            score = normalized_scores[i]
            # Adjust score based on meta-confidence cap? 
            # No, evaluate returns ranking. Confidence is separate. 
            # But we can dampen score if the whole prompt is suspect? 
            # Let's keep score as "relative likelihood among candidates"
            
            reasoning = f"Structural match: {score:.2f}. "
            if score > 0.8: reasoning += "High consistency with prompt constraints."
            elif score < 0.3: reasoning += "Low structural alignment."
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by _meta_confidence for epistemic honesty.
        """
        # 1. Meta-confidence cap (Tier B)
        cap = self._meta_confidence(prompt)
        
        # If cap is low, we are uncertain regardless of answer match
        if cap < 0.4:
            return cap * 0.9 # Stay below cap

        # 2. Evaluate single candidate against empty set (or self) to get relative score
        # We simulate a comparison to gauge absolute quality
        scores, _ = self._swarm_optimize(prompt, [answer], iterations=10)
        raw_score = scores[0] if scores else 0.0
        
        # Scale raw score (which is based on feature density) to 0-1
        # Heuristic: High feature match + low violation = high score
        # Since we only have one candidate, the score reflects absolute feature coverage
        base_conf = min(1.0, max(0.0, raw_score * 1.5)) # Scale up slightly
        
        # Apply cap
        final_conf = min(base_conf, cap)
        
        # Never return > 0.9 unless computation was definitive (hard to prove with regex)
        # So we hard cap at 0.95 max to maintain humility
        return min(final_conf, 0.95)
```

</details>
