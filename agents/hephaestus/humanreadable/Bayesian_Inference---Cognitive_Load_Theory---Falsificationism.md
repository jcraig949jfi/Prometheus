# Bayesian Inference + Cognitive Load Theory + Falsificationism

**Fields**: Mathematics, Cognitive Science, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T08:52:05.230209
**Report Generated**: 2026-04-02T10:00:37.355416

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex‑based patterns to extract atomic propositions from the prompt and each candidate answer. Patterns capture:  
   - Negations (`not`, `no`, `-n't`)  
   - Comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`)  
   - Conditionals (`if … then`, `unless`, `provided that`)  
   - Causal cues (`because`, `leads to`, `results in`)  
   - Ordering/temporal (`before`, `after`, `precedes`, `follows`)  
   - Numeric literals and units  
   - Quantifiers (`all`, `some`, `none`, `every`)  
   Each proposition is stored as a tuple `(predicate, args, polarity, weight)` where `polarity ∈ {+1,‑1}` indicates negation and `weight` encodes cognitive load (see step 3).  

2. **Constraint graph** – Build a directed graph where nodes are ground atoms (e.g., `Temperature > 30`) and edges represent logical relations extracted from conditionals, causals, and ordering. Apply simple forward‑chaining (modus ponens) and transitivity to infer implied atoms; store both asserted and inferred propositions in a set `E` (evidence from the prompt).  

3. **Cognitive‑load weighting** – For each proposition compute an intrinsic load score `L = 1 + (nesting depth of operators) + (number of arguments)`. Define weight `w = 1 / (1 + L)`. This down‑weights propositions that would heavily tax working memory, reflecting the idea that complex statements contribute less reliable evidence.  

4. **Bayesian scoring with falsification penalty** – Treat each proposition `e ∈ E` as an independent Bernoulli observation with unknown truth probability `θ`. Use a conjugate Beta(1,1) prior for each `θ`. For a candidate hypothesis `H`, compute the likelihood of the evidence:  

   ```
   L(H) = ∏_{e∈E} [ θ_e^{w·I(H⊨e)} · (1‑θ_e)^{w·(1‑I(H⊨e))} ]
   ```

   where `I(H⊨e)` is 1 if `H` entails `e` (checked via the constraint graph) else 0. After observing all evidence, the posterior for each `θ` is Beta(1 + Σ w·I, 1 + Σ w·(1‑I)). The marginal likelihood (evidence) simplifies to a product of Beta‑function ratios; we approximate the score by the log posterior odds:  

   ```
   score(H) = log P(H) + Σ_e w·[ log Beta(1+I,1+1‑I) – log Beta(1,1) ]
   ```

   with a uniform prior `log P(H)=0`.  

   **Falsificationism penalty** – Compute the proportion `f = |{e∈E : H ¬⊨ e}| / |E|`. If `f < τ` (e.g., τ = 0.1) meaning the hypothesis avoids risky predictions, multiply the score by `f/τ` (a penalty that approaches zero as `f→0`).  

5. **Final ranking** – Rank candidates by descending `score(H)`. All steps use only `numpy` for vectorized Beta/log operations and the Python standard library for regex and graph handling.

**Structural features parsed** – negations, comparatives, conditionals, causal verbs, ordering/temporal relations, numeric values, quantifiers, and conjunction/disjunction structure.

**Novelty** – While Bayesian model averaging, logic‑based constraint propagation, and cognitive‑load weighting each appear separately in educational‑AI literature, their conjunction—using load‑weighted Bayesian updating together with an explicit falsifiability penalty derived from Popperian criteria—has not been described in published work. The approach is novel in its tight coupling of these three mechanisms within a single scoring function.

**Rating**  
Reasoning: 8/10 — The algorithm blends probabilistic belief revision with logical constraint propagation, yielding nuanced scores that respect both evidence strength and logical coherence.  
Metacognition: 7/10 — Cognitive‑load weighting introduces a rudimentary model of resource limits, but it does not capture higher‑order self‑regulation strategies.  
Hypothesis generation: 6/10 — Falsifiability penalty discourages vacuous hypotheses, yet the system does not actively generate new conjectures; it only evaluates given candidates.  
Implementability: 9/10 — All components rely on regex, simple graph propagation, and NumPy vectorized math, fitting easily within the constraints of a pure‑Python, no‑external‑library tool.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
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
**Reason**: trap_battery_failed (acc=41% cal=14% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T09:11:30.708725

---

## Code

**Source**: scrap

[View code](./Bayesian_Inference---Cognitive_Load_Theory---Falsificationism/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Bayesian-Falsification Reasoning Tool with Dynamics Tracking

Combines:
- Structural parsing (negations, comparatives, conditionals, causals)
- Cognitive load weighting (complexity penalty)
- Bayesian belief updating with falsification penalty
- Dynamics tracking (state evolution, trajectory stability)
- Epistemic honesty (ambiguity detection)
"""

import re
import numpy as np
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple


class ReasoningTool:
    def __init__(self):
        self.tau = 0.1  # Falsification threshold
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by Bayesian-dynamics score."""
        propositions = self._parse_propositions(prompt)
        results = []
        
        for cand in candidates:
            # Bayesian score with falsification
            bayes_score = self._bayesian_score(propositions, prompt, cand)
            
            # Dynamics stability score
            dyn_score = self._dynamics_score(propositions, prompt, cand)
            
            # Structural/numeric computation
            struct_score = self._structural_score(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination: dynamics 40%, structural 30%, Bayesian 20%, NCD 10%
            total = 0.4 * dyn_score + 0.3 * struct_score + 0.2 * bayes_score + 0.1 * ncd_score
            
            reasoning = f"Dynamics={dyn_score:.2f} Struct={struct_score:.2f} Bayes={bayes_score:.2f}"
            results.append({"candidate": cand, "score": float(total), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        
        propositions = self._parse_propositions(prompt)
        if len(propositions) == 0:
            return min(0.2, meta_conf)
        
        # Dynamics stability
        dyn_score = self._dynamics_score(propositions, prompt, answer)
        
        # Structural match
        struct_score = self._structural_score(prompt, answer)
        
        # Combine and cap by meta-confidence
        raw_conf = 0.5 * dyn_score + 0.5 * struct_score
        return min(raw_conf, meta_conf)
    
    def _parse_propositions(self, text: str) -> List[Tuple]:
        """Extract propositions with cognitive load weights."""
        props = []
        text_lower = text.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|no|n\'t|never)\s+(\w+)', text_lower):
            props.append(("negation", m.group(2), -1, 0.9))
        
        # Comparatives with numbers
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|greater|less|more|fewer)\s*(\d+\.?\d*)', text_lower):
            props.append(("comparative", (m.group(1), m.group(2), m.group(3)), 1, 0.8))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.,;]', text_lower):
            nesting = m.group(1).count('if') + m.group(1).count('and') + m.group(1).count('or')
            weight = 1.0 / (1.0 + nesting)
            props.append(("conditional", (m.group(1), m.group(2)), 1, weight))
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(because|leads to|results in|causes)\s+(\w+)', text_lower):
            props.append(("causal", (m.group(1), m.group(3)), 1, 0.7))
        
        # Temporal ordering
        for m in re.finditer(r'(\w+)\s+(before|after|precedes|follows)\s+(\w+)', text_lower):
            props.append(("temporal", (m.group(1), m.group(2), m.group(3)), 1, 0.8))
        
        # Quantifiers
        for m in re.finditer(r'\b(all|every|some|none|each)\s+(\w+)', text_lower):
            props.append(("quantifier", (m.group(1), m.group(2)), 1, 0.85))
        
        return props
    
    def _bayesian_score(self, props: List[Tuple], prompt: str, cand: str) -> float:
        """Bayesian update with falsification penalty."""
        if not props:
            return 0.5
        
        log_score = 0.0
        entailments = 0
        total = 0
        
        cand_lower = cand.lower()
        
        for pred, args, polarity, weight in props:
            total += 1
            entails = self._check_entailment(pred, args, polarity, cand_lower)
            entailments += entails
            
            # Beta posterior odds
            if entails:
                log_score += weight * np.log(2.0)  # Evidence for
            else:
                log_score += weight * np.log(0.5)  # Evidence against
        
        # Falsification penalty
        f = (total - entailments) / max(total, 1)
        penalty = min(f / self.tau, 1.0) if f < self.tau else 1.0
        
        score = np.exp(log_score / max(total, 1)) * penalty
        return float(np.clip(score, 0, 1))
    
    def _check_entailment(self, pred: str, args, polarity: int, cand: str) -> bool:
        """Check if candidate entails proposition."""
        if pred == "negation":
            has_neg = any(w in cand for w in ["not", "no", "never", "n't"])
            has_term = args in cand
            return (has_neg and has_term) if polarity < 0 else (not has_neg and has_term)
        
        elif pred == "comparative":
            try:
                n1, op, n2 = args
                if op in ["greater", "more", ">"]:
                    return str(n1) in cand and float(n1) > float(n2)
                elif op in ["less", "fewer", "<"]:
                    return str(n1) in cand and float(n1) < float(n2)
            except:
                pass
        
        elif pred in ["conditional", "causal", "temporal"]:
            return all(str(a) in cand for a in args if isinstance(args, tuple))
        
        return False
    
    def _dynamics_score(self, props: List[Tuple], prompt: str, cand: str) -> float:
        """Track state evolution dynamics and measure stability."""
        if not props:
            return 0.5
        
        # Initialize state vector
        state = np.array([0.5])  # Neutral prior
        states = [state.copy()]
        
        # Update state for each proposition (simulating sequential processing)
        for pred, args, polarity, weight in props:
            entails = self._check_entailment(pred, args, polarity, cand.lower())
            
            # State update: move toward 1 if entails, toward 0 if not
            target = 1.0 if entails else 0.0
            state = state * 0.7 + target * weight * 0.3
            states.append(state.copy())
        
        # Measure trajectory stability (variance of state changes)
        states_arr = np.array([s[0] for s in states])
        deltas = np.diff(states_arr)
        
        # Lyapunov-inspired: stable if small changes
        stability = 1.0 / (1.0 + np.std(deltas))
        
        # Convergence: final state should be near 0 or 1
        convergence = abs(states_arr[-1] - 0.5) * 2  # 0 at 0.5, 1 at extremes
        
        # Basin stability: proportion of updates moving toward final state
        final = states_arr[-1]
        consistent = sum(1 for d in deltas if (d > 0 and final > 0.5) or (d < 0 and final < 0.5))
        basin = consistent / max(len(deltas), 1)
        
        # Combine dynamics metrics
        dyn_score = 0.4 * stability + 0.3 * convergence + 0.3 * basin
        return float(np.clip(dyn_score, 0, 1))
    
    def _structural_score(self, prompt: str, cand: str) -> float:
        """Structural and numeric computation."""
        score = 0.0
        
        # Numeric comparison
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', cand)
        if nums_p and nums_c:
            try:
                # Check if candidate contains correct numeric comparison
                for np_str in nums_p:
                    if np_str in cand:
                        score += 0.3
            except:
                pass
        
        # Boolean questions
        if re.search(r'\b(is|are|does|do|can|will)\b', prompt.lower()):
            if re.search(r'\b(yes|no|true|false)\b', cand.lower()):
                score += 0.2
        
        # Negation consistency
        has_neg_p = bool(re.search(r'\b(not|no|never|n\'t)\b', prompt.lower()))
        has_neg_c = bool(re.search(r'\b(not|no|never|n\'t)\b', cand.lower()))
        if has_neg_p == has_neg_c:
            score += 0.3
        
        # Subject-object role preservation
        subjects = re.findall(r'^(\w+)\s+(?:is|are|was|were)', prompt)
        if subjects and subjects[0].lower() in cand.lower():
            score += 0.2
        
        return float(np.clip(score, 0, 1))
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/unanswerability. Returns max confidence cap."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did .+ (fail|stop))\b', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .+ a \w+\b', prompt_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt_lower) and '?' in prompt:
            if re.search(r'\bwho\b', prompt_lower):
                return 0.3
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', prompt_lower):
            return 0.35
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', prompt_lower):
            if not re.search(r'\b(by|according to|measured by)\b', prompt_lower):
                return 0.4
        
        # Insufficient information
        if re.search(r'\b(what|which|who|when|where)\b', prompt_lower):
            if len(prompt.split()) < 8:
                return 0.45
        
        return 0.95  # High cap if no issues detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
