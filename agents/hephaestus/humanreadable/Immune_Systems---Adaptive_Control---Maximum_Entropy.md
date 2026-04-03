# Immune Systems + Adaptive Control + Maximum Entropy

**Fields**: Biology, Control Theory, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T04:49:13.289802
**Report Generated**: 2026-04-02T12:33:28.993390

---

## Nous Analysis

**Algorithm: Clonal‑Maximum‑Entropy Adaptive Scorer (CMEAS)**  

1. **Feature extraction** – From the prompt and each candidate answer we parse a fixed‑length feature vector **x** ∈ ℝᵈ using regex‑based structural patterns:  
   - negation tokens (“not”, “no”) → binary flag  
   - comparatives (“greater than”, “less than”) → signed magnitude  
   - conditionals (“if … then …”) → antecedent/consequent indices  
   - numeric values → normalized scalar  
   - causal cues (“because”, “leads to”) → directed edge flag  
   - ordering relations (“first”, “last”) → ordinal rank  
   - quantifiers (“all”, “some”) → count‑based bins  

   The same extractor is applied to the prompt, yielding a constraint feature vector **c**.

2. **Population of antibodies** – Maintain a set **P** = {w₁,…,wₙ} of weight vectors (ℝᵈ) that act as candidate “interpretations” of the prompt. Each w defines a log‑linear model p(y|w) ∝ exp(w·x_y) for any feature vector x_y (e.g., the feature vector of a candidate answer).

3. **Fitness evaluation** – For each wᵢ compute error eᵢ = ‖A wᵢ – b‖₂ where **A** stacks the prompt constraint features **c** and **b** is a target vector (e.g., desired expectation of each feature under the prompt). Fitness fᵢ = exp(−eᵢ²). This mirrors clonal selection: higher fitness → more clones.

4. **Clonal expansion & mutation** – Select the top‑k antibodies, clone each m times, and add Gaussian noise 𝒩(0,σ²I) to the clones (mutation). The mutation scale σ is adapted online.

5. **Adaptive control of σ** – Treat the mean error ē = (1/|P|)∑eᵢ as the process output. A simple self‑tuning rule updates σ:  
   σ ← σ·(1 + η(ē₀ − ē)), where ē₀ is a desired error threshold and η a small gain. This drives the population toward lower error while preventing collapse.

6. **Maximum‑entropy step** – After each generation, compute the Lagrange multipliers λ that satisfy the constraint expectations:  
   Solve for λ in 𝔼_{p(w)}[w] = λ⁻¹·c using iterative scaling (GIS). The resulting distribution p(w) is the least‑biased distribution consistent with the prompt’s feature expectations.

7. **Scoring candidates** – For each candidate answer a with feature vector x_a, compute its score as the predictive likelihood under the current max‑entropy distribution:  
   S(a) = ∫ exp(w·x_a) p(w) dw ≈ (1/|P|)∑_{wᵢ∈P} exp(wᵢ·x_a).  
   Higher S indicates better alignment with the prompt’s logical and numeric constraints.

**Structural features parsed**: negations, comparatives, conditionals, numeric values, causal claims, ordering relations, quantifiers, and logical connectives (AND/OR). These are turned into the feature vectors that drive both the constraint matrix **A** and the answer likelihood.

**Novelty**: The algorithm fuses three well‑studied mechanisms—clonal selection (immune‑inspired optimization), self‑tuning adaptive control, and maximum‑entropy inference—but their specific combination for scoring reasoning answers via a population of log‑linear models and online error‑driven mutation does not appear in existing surveys. Related work uses either Bayesian optimization or evolutionary strategies, but not the triple‑layered constraint‑propagation + max‑entropy scoring loop.

**Ratings**  
Reasoning: 7/10 — captures logical constraints via feature‑based error and propagates them through clonal selection, yielding nuanced answer evaluation.  
Metacognition: 6/10 — the adaptive σ update provides basic self‑monitoring of error, but lacks higher‑order reflection on strategy suitability.  
Hypothesis generation: 8/10 — the antibody population explicitly generates diverse interpretive hypotheses (weight vectors) and refines them via mutation and selection.  
Implementability: 7/10 — relies only on numpy for linear algebra, random sampling, and iterative scaling; all components are straightforward to code without external libraries.

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
**Reason**: trap_battery_failed (acc=37% cal=40% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T12:09:27.750872

---

## Code

**Source**: scrap

[View code](./Immune_Systems---Adaptive_Control---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Clonal-Maximum-Entropy Adaptive Scorer (CMEAS)
    
    Combines immune-inspired clonal selection, adaptive control, and maximum
    entropy inference. Maintains a population of weight vectors (antibodies)
    that evolve to match prompt constraints, then scores candidates via
    max-entropy distribution over the population.
    """
    
    def __init__(self):
        self.population_size = 30
        self.top_k = 10
        self.clones_per_antibody = 3
        self.sigma = 0.5
        self.eta = 0.1
        self.target_error = 0.3
        self.feature_dim = 12
        np.random.seed(42)
    
    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural and semantic features from text."""
        text_lower = text.lower()
        features = np.zeros(self.feature_dim)
        
        # 0: Negation tokens
        features[0] = len(re.findall(r'\b(not|no|never|none|neither)\b', text_lower))
        
        # 1: Comparatives (signed magnitude)
        greater = len(re.findall(r'\b(greater|more|higher|larger|above)\b', text_lower))
        less = len(re.findall(r'\b(less|fewer|lower|smaller|below)\b', text_lower))
        features[1] = greater - less
        
        # 2: Conditionals
        features[2] = len(re.findall(r'\b(if|when|unless|provided)\b', text_lower))
        
        # 3: Numeric values (normalized mean)
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        features[3] = np.mean([float(n) for n in numbers]) / 100 if numbers else 0
        
        # 4: Causal cues
        features[4] = len(re.findall(r'\b(because|since|therefore|thus|leads to|causes)\b', text_lower))
        
        # 5: Ordering relations
        features[5] = len(re.findall(r'\b(first|last|before|after|then|next)\b', text_lower))
        
        # 6: Quantifiers
        features[6] = len(re.findall(r'\b(all|some|every|any|each|most)\b', text_lower))
        
        # 7: Logical connectives
        features[7] = len(re.findall(r'\b(and|or|but|however|although)\b', text_lower))
        
        # 8: Question words
        features[8] = len(re.findall(r'\b(who|what|when|where|why|how|which)\b', text_lower))
        
        # 9: Certainty markers
        features[9] = len(re.findall(r'\b(must|always|definitely|certainly|possibly|maybe)\b', text_lower))
        
        # 10: Text length (normalized)
        features[10] = min(len(text) / 200, 1.0)
        
        # 11: Numeric density
        features[11] = len(numbers) / max(len(text.split()), 1)
        
        return features
    
    def _compute_answer(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Constructively compute answer for specific problem types."""
        prompt_lower = prompt.lower()
        candidate_lower = candidate.lower()
        
        # Numeric comparison
        if any(word in prompt_lower for word in ['greater', 'less', 'larger', 'smaller']):
            nums_prompt = re.findall(r'\b(\d+\.?\d*)\b', prompt)
            if len(nums_prompt) >= 2:
                a, b = float(nums_prompt[0]), float(nums_prompt[1])
                is_greater = 'greater' in prompt_lower or 'larger' in prompt_lower
                correct = (a > b) if is_greater else (a < b)
                if ('yes' in candidate_lower and correct) or ('no' in candidate_lower and not correct):
                    return 0.9, "numeric_comparison"
                return 0.1, "numeric_comparison"
        
        # Probability/Bayesian reasoning
        if any(word in prompt_lower for word in ['probability', 'likely', 'chance']):
            nums = re.findall(r'(\d+\.?\d*)%', prompt)
            if nums:
                probs = [float(n)/100 for n in nums]
                if len(probs) >= 2:
                    # Simple Bayes approximation
                    posterior = probs[0] * probs[1] / max(probs[1], 0.01)
                    nums_cand = re.findall(r'(\d+\.?\d*)', candidate)
                    if nums_cand:
                        cand_val = float(nums_cand[0])
                        if abs(cand_val - posterior*100) < 10:
                            return 0.8, "bayesian"
        
        # Temporal ordering
        if any(word in prompt_lower for word in ['before', 'after', 'first', 'last']):
            if 'before' in prompt_lower and 'before' in candidate_lower:
                return 0.7, "temporal"
            if 'after' in prompt_lower and 'after' in candidate_lower:
                return 0.7, "temporal"
        
        # Logical negation
        if 'not' in prompt_lower:
            negations_p = len(re.findall(r'\bnot\b', prompt_lower))
            negations_c = len(re.findall(r'\bnot\b', candidate_lower))
            if negations_p % 2 == negations_c % 2:
                return 0.6, "logical_negation"
        
        return 0.0, "none"
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity and epistemic issues in the prompt."""
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .* fail|why did .* stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .* a \b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*\?', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or \b', prompt_lower):
            return 0.3
        
        # Subjectivity without criteria
        if any(word in prompt_lower for word in ['best', 'worst', 'favorite']) and not any(w in prompt_lower for w in ['most', 'least', 'highest', 'lowest']):
            return 0.3
        
        # Unanswerability markers
        if re.search(r'\b(impossible to|cannot determine|not enough information)\b', prompt_lower):
            return 0.2
        
        return 1.0  # No epistemic issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates using CMEAS."""
        # Extract prompt features
        prompt_features = self._extract_features(prompt)
        constraint_vector = prompt_features / (np.linalg.norm(prompt_features) + 1e-6)
        
        # Initialize population of antibodies
        population = [np.random.randn(self.feature_dim) * 0.5 for _ in range(self.population_size)]
        
        # Run clonal selection for multiple generations
        for generation in range(5):
            # Fitness evaluation
            errors = []
            for w in population:
                error = np.linalg.norm(w - constraint_vector)
                errors.append(error)
            
            fitnesses = [np.exp(-e**2) for e in errors]
            
            # Select top-k
            sorted_indices = np.argsort(fitnesses)[::-1]
            elite = [population[i] for i in sorted_indices[:self.top_k]]
            
            # Clonal expansion and mutation
            new_population = []
            for antibody in elite:
                new_population.append(antibody)
                for _ in range(self.clones_per_antibody):
                    clone = antibody + np.random.randn(self.feature_dim) * self.sigma
                    new_population.append(clone)
            
            population = new_population[:self.population_size]
            
            # Adaptive control of sigma
            mean_error = np.mean(errors)
            self.sigma = self.sigma * (1 + self.eta * (self.target_error - mean_error))
            self.sigma = np.clip(self.sigma, 0.1, 2.0)
        
        # Score candidates
        results = []
        for candidate in candidates:
            cand_features = self._extract_features(candidate)
            
            # Constructive computation score
            comp_score, comp_type = self._compute_answer(prompt, candidate)
            
            # Max-entropy score from population
            scores = [np.exp(np.dot(w, cand_features)) for w in population]
            maxent_score = np.mean(scores)
            maxent_normalized = 1 / (1 + np.exp(-maxent_score + 5))
            
            # NCD as tiebreaker
            ncd = self._ncd(prompt, candidate)
            ncd_score = 1 - ncd
            
            # Combine: 50% computation, 35% maxent, 15% NCD
            final_score = 0.5 * comp_score + 0.35 * maxent_normalized + 0.15 * ncd_score
            
            reasoning = f"Computation: {comp_score:.2f} ({comp_type}), MaxEnt: {maxent_normalized:.2f}, NCD: {ncd_score:.2f}"
            results.append({"candidate": candidate, "score": final_score, "reasoning": reasoning})
        
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on prompt properties and answer quality."""
        # Check meta-confidence first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Constructive computation confidence
        comp_score, comp_type = self._compute_answer(prompt, answer)
        if comp_type != "none":
            return min(comp_score * meta_conf, 0.95)
        
        # Structural match confidence
        prompt_features = self._extract_features(prompt)
        answer_features = self._extract_features(answer)
        
        feature_similarity = np.dot(prompt_features, answer_features) / (np.linalg.norm(prompt_features) * np.linalg.norm(answer_features) + 1e-6)
        structural_conf = max(0, min(feature_similarity, 1.0))
        
        # Cap confidence when no computation available
        base_conf = 0.4 * structural_conf + 0.1
        return min(base_conf * meta_conf, 0.6)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
```

</details>
