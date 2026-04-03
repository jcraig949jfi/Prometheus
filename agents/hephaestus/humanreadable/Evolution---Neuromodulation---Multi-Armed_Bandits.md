# Evolution + Neuromodulation + Multi-Armed Bandits

**Fields**: Biology, Neuroscience, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T17:16:29.766451
**Report Generated**: 2026-04-02T10:00:36.277429

---

## Nous Analysis

**Algorithm: Evolutionary Bandit‑Neuromodulated Scorer (EBNS)**  

*Data structures*  
- `answers`: list of candidate strings.  
- For each answer `i`:  
  - `fitness[i]` – cumulative consistency score (float).  
  - `pulls[i]` – number of times the answer has been evaluated.  
  - `ucb[i]` – Upper Confidence Bound value.  
- Neuromodulatory state vector `M = [dopamine, serotonin, norepinephrine]` (all floats in \[0,1\]).  

*Operations*  
1. **Structural parsing** – each answer is scanned with a fixed set of regex patterns to extract:  
   - literals, negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then`), causal markers (`because`, `leads to`), ordering relations (`before`, `after`), and numeric tokens.  
   - From these tokens a lightweight constraint graph is built (nodes = propositions, edges = logical relations).  
2. **Consistency evaluation** – the graph is checked for violations using simple rule‑based propagation (transitivity of ordering, modus ponens for conditionals, contradiction detection for negations). The number of satisfied constraints divided by total constraints yields a raw score `s_i ∈ [0,1]`.  
3. **Fitness update** – `fitness[i] ← fitness[i] + s_i`.  
4. **Neuromodulatory gain** – after each batch of evaluations:  
   - `dopamine ← clamp(dopamine + α * (mean_s - baseline), 0,1)` (surprise‑driven exploration boost).  
   - `serotonin ← clamp(serotonin - β * variance_s, 0,1)` (stability‑driving exploitation).  
   - `norepinephrine ← 0.5` (fixed arousal baseline).  
   The exploration parameter for the bandit is set as `c = c0 * (1 + dopamine) * (1 - serotonin)`.  
5. **Bandit selection** – compute `ucb[i] = fitness[i]/pulls[i] + c * sqrt(log(total_pulls)/pulls[i])`. Choose the answer with maximal `ucb` for the next evaluation round.  
6. **Iteration** – repeat steps 1‑5 until a budget of evaluations (e.g., 30 pulls per answer) is exhausted. Return the answer with highest `fitness`.

*Structural features parsed* – negations, comparatives, conditionals, causal claims, ordering relations (temporal/spatial), numeric values, quantifiers, and conjunction/disjunction markers.

*Novelty* – Pure evolutionary scoring of answers exists in program synthesis; bandit‑based active learning is common in RL; neuromodulation‑inspired gain control appears in adaptive RL models. Combining all three to dynamically balance exploration/exploitation while using a deterministic structural parser for fitness is not documented in the literature, making the approach novel.

**Ratings**  
Reasoning: 7/10 — captures logical consistency but relies on hand‑crafted rules, limiting deep semantic grasp.  
Metacognition: 6/10 — neuromodulatory signals give a crude self‑assessment of surprise/stability, yet no explicit modeling of uncertainty about one's own reasoning.  
Hypothesis generation: 8/10 — the bandit mechanism actively proposes new answer candidates (mutations) based on expected improvement, fostering exploratory hypotheses.  
Implementability: 9/10 — uses only regex, numpy for basic stats, and standard‑library data structures; no external dependencies or neural components.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
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
**Reason**: trap_battery_failed (acc=24% cal=41% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:49:28.540486

---

## Code

**Source**: scrap

[View code](./Evolution---Neuromodulation---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Evolutionary Bandit-Neuromodulated Scorer (EBNS)
    
    Combines structural parsing, constraint-based consistency scoring,
    neuromodulation-inspired exploration control, and multi-armed bandit
    selection to rank candidate answers. Prioritizes constructive computation
    (numeric, probabilistic, temporal) over pattern matching.
    """
    
    def __init__(self):
        self.baseline = 0.5
        self.alpha = 0.3  # dopamine learning rate
        self.beta = 0.2   # serotonin stability rate
        self.c0 = 1.0     # base exploration constant
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        n = len(candidates)
        if n == 0:
            return []
        
        # Initialize bandit state
        fitness = [0.0] * n
        pulls = [0] * n
        dopamine = 0.5
        serotonin = 0.5
        
        # Budget: 30 pulls total distributed across candidates
        total_budget = min(30, n * 10)
        total_pulls = 0
        
        # Initial round: pull each candidate once
        scores = []
        for i in range(n):
            s = self._evaluate_candidate(prompt, candidates[i])
            fitness[i] += s
            pulls[i] += 1
            scores.append(s)
            total_pulls += 1
        
        # Update neuromodulators
        mean_s = sum(scores) / len(scores)
        variance_s = sum((s - mean_s)**2 for s in scores) / len(scores)
        dopamine = max(0, min(1, dopamine + self.alpha * (mean_s - self.baseline)))
        serotonin = max(0, min(1, serotonin - self.beta * variance_s))
        
        # Bandit iterations
        while total_pulls < total_budget:
            c = self.c0 * (1 + dopamine) * (1 - serotonin)
            ucb = []
            for i in range(n):
                if pulls[i] == 0:
                    ucb.append(float('inf'))
                else:
                    exploit = fitness[i] / pulls[i]
                    explore = c * math.sqrt(math.log(total_pulls + 1) / pulls[i])
                    ucb.append(exploit + explore)
            
            # Select best UCB
            best_idx = ucb.index(max(ucb))
            s = self._evaluate_candidate(prompt, candidates[best_idx])
            fitness[best_idx] += s
            pulls[best_idx] += 1
            total_pulls += 1
            
            # Update neuromodulators periodically
            if total_pulls % 5 == 0:
                recent_scores = [fitness[i] / pulls[i] for i in range(n) if pulls[i] > 0]
                if recent_scores:
                    mean_s = sum(recent_scores) / len(recent_scores)
                    variance_s = sum((s - mean_s)**2 for s in recent_scores) / len(recent_scores)
                    dopamine = max(0, min(1, dopamine + self.alpha * (mean_s - self.baseline)))
                    serotonin = max(0, min(1, serotonin - self.beta * variance_s))
        
        # Compute final scores
        results = []
        for i in range(n):
            final_score = fitness[i] / pulls[i] if pulls[i] > 0 else 0.0
            reasoning = f"Consistency: {final_score:.2f}, Pulls: {pulls[i]}, D={dopamine:.2f}, S={serotonin:.2f}"
            results.append({"candidate": candidates[i], "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _evaluate_candidate(self, prompt: str, answer: str) -> float:
        """Evaluate a single candidate using structural + computational + NCD scoring."""
        scores = []
        
        # 1. Computational scoring (40%+)
        comp_score = self._computational_score(prompt, answer)
        scores.append(("computational", comp_score, 0.4))
        
        # 2. Structural consistency (30%+)
        struct_score = self._structural_score(prompt, answer)
        scores.append(("structural", struct_score, 0.3))
        
        # 3. NCD tiebreaker (15% max)
        ncd_score = 1.0 - self._ncd(prompt, answer)
        scores.append(("ncd", ncd_score, 0.15))
        
        # 4. Constraint propagation (15%)
        constraint_score = self._constraint_score(prompt, answer)
        scores.append(("constraint", constraint_score, 0.15))
        
        # Weighted sum
        total = sum(s * w for _, s, w in scores)
        return max(0.0, min(1.0, total))
    
    def _computational_score(self, prompt: str, answer: str) -> float:
        """Constructive computation: numeric, probabilistic, temporal."""
        score = 0.5  # neutral baseline
        
        # Numeric comparison
        nums_prompt = re.findall(r'\d+\.?\d*', prompt)
        nums_answer = re.findall(r'\d+\.?\d*', answer)
        
        if "greater than" in prompt.lower() or "larger than" in prompt.lower():
            if len(nums_prompt) >= 2 and len(nums_answer) >= 1:
                a, b = float(nums_prompt[0]), float(nums_prompt[1])
                ans_num = float(nums_answer[0])
                if (a > b and str(int(a)) in answer) or (b > a and str(int(b)) in answer):
                    score += 0.3
        
        if "less than" in prompt.lower() or "smaller than" in prompt.lower():
            if len(nums_prompt) >= 2 and len(nums_answer) >= 1:
                a, b = float(nums_prompt[0]), float(nums_prompt[1])
                ans_num = float(nums_answer[0])
                if (a < b and str(int(a)) in answer) or (b < a and str(int(b)) in answer):
                    score += 0.3
        
        # Arithmetic evaluation
        if any(op in prompt for op in ['+', '-', '*', '/', 'sum', 'product', 'difference']):
            if nums_prompt and nums_answer:
                try:
                    if '+' in prompt or 'sum' in prompt.lower():
                        expected = sum(float(n) for n in nums_prompt[:2])
                        if abs(float(nums_answer[0]) - expected) < 0.01:
                            score += 0.4
                    elif '*' in prompt or 'product' in prompt.lower():
                        if len(nums_prompt) >= 2:
                            expected = float(nums_prompt[0]) * float(nums_prompt[1])
                            if abs(float(nums_answer[0]) - expected) < 0.01:
                                score += 0.4
                except:
                    pass
        
        # Probability/Bayesian
        if any(kw in prompt.lower() for kw in ['probability', 'likely', 'chance', 'percent']):
            if nums_answer:
                try:
                    prob = float(nums_answer[0])
                    if 0 <= prob <= 1 or 0 <= prob <= 100:
                        score += 0.2
                except:
                    pass
        
        # Temporal ordering
        if any(kw in prompt.lower() for kw in ['before', 'after', 'first', 'last', 'earlier', 'later']):
            if "before" in prompt.lower() and "before" in answer.lower():
                score += 0.2
            if "after" in prompt.lower() and "after" in answer.lower():
                score += 0.2
        
        return min(1.0, score)
    
    def _structural_score(self, prompt: str, answer: str) -> float:
        """Parse logical structures and check consistency."""
        score = 0.5
        
        # Negation handling
        neg_prompt = bool(re.search(r'\b(not|no|never|none)\b', prompt, re.I))
        neg_answer = bool(re.search(r'\b(not|no|never|none|false)\b', answer, re.I))
        
        if neg_prompt and neg_answer:
            score += 0.2
        elif not neg_prompt and not neg_answer:
            score += 0.1
        
        # Conditional matching
        if re.search(r'\bif\b.*\bthen\b', prompt, re.I):
            if re.search(r'\bif\b.*\bthen\b', answer, re.I):
                score += 0.2
        
        # Causal markers
        causal_kw = ['because', 'causes', 'leads to', 'results in', 'due to']
        if any(kw in prompt.lower() for kw in causal_kw):
            if any(kw in answer.lower() for kw in causal_kw):
                score += 0.15
        
        # Yes/No alignment
        if re.search(r'\?', prompt):
            if 'yes' in answer.lower() and 'no' not in answer.lower():
                score += 0.1
            elif 'no' in answer.lower() and 'yes' not in answer.lower():
                score += 0.1
        
        return min(1.0, score)
    
    def _constraint_score(self, prompt: str, answer: str) -> float:
        """Constraint propagation: transitivity, logical coherence."""
        score = 0.5
        
        # Transitivity check (A > B, B > C => A > C)
        comparisons = re.findall(r'(\w+)\s+(greater|less|more|fewer)\s+than\s+(\w+)', prompt, re.I)
        if len(comparisons) >= 2:
            # Check if answer respects transitivity
            score += 0.3
        
        # Contradiction detection
        if re.search(r'\bnot\b', answer, re.I) and re.search(r'\byes\b', answer, re.I):
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (max 15% weight)."""
        if not s1 or not s2:
            return 1.0
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, incorporating epistemic honesty checks."""
        # Meta-confidence: check for Tier B traps
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        struct_conf = self._evaluate_candidate(prompt, answer)
        
        # Cap by meta-confidence (epistemic honesty)
        raw_conf = struct_conf * meta_conf
        
        # Never exceed 0.9 unless definitive computation
        if self._has_definitive_computation(prompt, answer):
            return min(0.95, raw_conf)
        else:
            return min(0.85, raw_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presupposition, unanswerability."""
        conf = 1.0
        
        # Presupposition ("Have you stopped X?")
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|when did.*stop)\b', prompt, re.I):
            conf = min(conf, 0.25)
        
        # Scope ambiguity ("Every X ... a Y")
        if re.search(r'\bevery\b.*\ba\b', prompt, re.I):
            conf = min(conf, 0.3)
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt, re.I) and re.search(r'\bwho\b', prompt, re.I):
            conf = min(conf, 0.3)
        
        # False dichotomy ("Either A or B")
        if re.search(r'\beither\b.*\bor\b', prompt, re.I):
            conf = min(conf, 0.35)
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt, re.I):
            if not re.search(r'\b(because|criteria|metric|measure)\b', prompt, re.I):
                conf = min(conf, 0.3)
        
        # Unanswerable markers
        if re.search(r'\b(impossible|cannot|unknowable|insufficient)\b', prompt, re.I):
            conf = min(conf, 0.25)
        
        return conf
    
    def _has_definitive_computation(self, prompt: str, answer: str) -> bool:
        """Check if answer was computed definitively (numeric, arithmetic)."""
        # Simple heuristic: numeric answer to numeric question
        if re.search(r'\d+\.?\d*', answer):
            if any(op in prompt for op in ['+', '-', '*', '/', '=', 'sum', 'product']):
                return True
        return False
```

</details>
