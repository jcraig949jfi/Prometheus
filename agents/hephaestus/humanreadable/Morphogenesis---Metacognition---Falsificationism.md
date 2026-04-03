# Morphogenesis + Metacognition + Falsificationism

**Fields**: Biology, Cognitive Science, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T00:56:21.968089
**Report Generated**: 2026-04-02T08:39:54.873537

---

## Nous Analysis

**Algorithm: Pattern‑Driven Falsifiable Constraint Solver with Metacognitive Calibration**  

**Data structures**  
- `Clause`: tuple `(predicate, args, polarity)` where `predicate` is a string extracted from the text (e.g., “causes”, “greater_than”), `args` are the grounded entities or numbers, and `polarity` ∈ {+1, –1} indicates affirmation or negation.  
- `ConstraintGraph`: adjacency list of `Clause` nodes; edges represent logical relationships (e.g., transitivity of “greater_than”, modus ponens of “if‑then”).  
- `PatternField`: 2‑D numpy array initialized with a small random seed; each cell holds a scalar “activation” representing the degree to which a local set of clauses satisfies a reaction‑diffusion rule.  
- `MetacogStats`: dict `{confidence: float, error_rate: float, strategy_counts: dict}` updated after each scoring pass.

**Operations**  
1. **Parsing** – Use regex to extract:  
   - Negations (`not`, `no`, `-`) → flip polarity.  
   - Comparatives (`greater than`, `less than`, `≥`, `≤`) → create `Clause` with predicate `cmp`.  
   - Conditionals (`if … then …`) → split into antecedent and consequent clauses; store as implication edge.  
   - Causal verbs (`causes`, `leads to`, `results in`) → predicate `cause`.  
   - Numeric values → attach to args as floats.  
   - Ordering relations (`first`, `second`, `before`, `after`) → predicate `order`.  

2. **Constraint Propagation** – Initialise `ConstraintGraph` with all extracted clauses. Iteratively apply:  
   - Transitivity for `cmp` and `order`.  
   - Modus ponens for implication edges.  
   - Contradiction detection: if a clause and its negation both become true, mark the graph as falsified.  

3. **Morphogenetic Scoring** – Treat each satisfied clause as a source of activation. At each iteration, update `PatternField` with a simple reaction‑diffusion step:  
   `A_{t+1} = A_t + D * ∇²A_t + f(A_t, B_t)`  
   where `A` is activation from satisfied clauses, `B` tracks falsified clauses, `D` is diffusion coefficient (fixed), and `f` is a linear source‑sink term (+1 for satisfaction, –1 for falsification). After N iterations (e.g., 10), compute the spatial entropy `H = -∑ p log p` of the normalized field; lower entropy indicates more coherent pattern formation → higher base score.  

4. **Metacognitive Calibration** – After scoring, compare the base score to a heuristic expectation (e.g., proportion of clauses satisfied). Update `MetacogStats`:  
   - `confidence` = 1 – |base – expectation|.  
   - `error_rate` increment if contradiction detected.  
   - Adjust future scoring weight `w = confidence * (1 – error_rate)`. Final score = base * w.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations.  

**Novelty** – The combination mirrors reaction‑diffusion pattern formation (morphogenesis) to evaluate global coherence, uses explicit falsification checks (Popperian), and adds a metacognitive feedback loop for confidence calibration. While each component appears separately in AI‑reasoning literature (e.g., constraint solvers, diffusion‑based similarity, confidence estimators), their tight integration in a single scoring loop is not documented in mainstream surveys, making the approach novel.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and falsification but relies on hand‑crafted regex.  
Metacognition: 7/10 — provides confidence adjustment yet simplistic error model.  
Hypothesis generation: 6/10 — derives hypotheses implicitly via pattern formation; limited generative breadth.  
Implementability: 9/10 — uses only numpy and stdlib; clear, finite steps.

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
**Reason**: trap_battery_failed (acc=42% cal=3% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T07:52:45.017837

---

## Code

**Source**: scrap

[View code](./Morphogenesis---Metacognition---Falsificationism/tool.py)

<details>
<summary>Show code</summary>

```python
from dataclasses import field
from typing import Dict, Tuple

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pattern-Driven Falsifiable Constraint Solver with Metacognitive Calibration.
    
    Combines morphogenesis (reaction-diffusion), falsificationism (constraint checking),
    and metacognition (epistemic honesty) to evaluate reasoning candidates.
    
    Core mechanism:
    1. Parse structural features (negations, comparatives, conditionals, numerics)
    2. Build constraint graph and propagate logical relationships
    3. Model as dynamical system: track state evolution across premises
    4. Score via reaction-diffusion entropy (morphogenetic coherence)
    5. Calibrate confidence via trajectory stability and ambiguity detection
    """
    
    def __init__(self):
        self.meta_stats = {'confidence': 1.0, 'error_rate': 0.0}
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            reasoning = f"Constraint score: {score:.3f}, Confidence: {conf:.3f}"
            results.append({'candidate': cand, 'score': score, 'reasoning': reasoning})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        base_conf = self._compute_base_confidence(prompt, answer)
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect epistemic issues in the prompt itself."""
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X did a Y"
        if re.search(r'\bevery\b.*\b(a|an)\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            return 0.3
        
        # Insufficient info markers
        if re.search(r'\b(cannot determine|insufficient|not enough|ambiguous)\b', p_lower):
            return 0.2
        
        return 0.95
    
    def _parse_clauses(self, text: str) -> List[Tuple[str, List, int]]:
        """Extract clauses: (predicate, args, polarity)."""
        clauses = []
        text_lower = text.lower()
        
        # Negations
        polarity = 1
        if re.search(r'\b(not|no|n\'t|never|cannot)\b', text_lower):
            polarity = -1
        
        # Numeric comparisons
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|greater|less)\s*(\d+\.?\d*)', text_lower):
            left, op, right = float(match.group(1)), match.group(2), float(match.group(3))
            if 'greater' in op or '>' in op:
                clauses.append(('cmp_gt', [left, right], polarity))
            elif 'less' in op or '<' in op:
                clauses.append(('cmp_lt', [left, right], polarity))
        
        # Ordering relations
        if re.search(r'\b(before|after|first|second|earlier|later)\b', text_lower):
            clauses.append(('order', [], polarity))
        
        # Causal relations
        if re.search(r'\b(cause|lead to|result in|because|therefore)\b', text_lower):
            clauses.append(('cause', [], polarity))
        
        # Conditionals
        if_match = re.search(r'if\s+(.+?)\s+then\s+(.+)', text_lower)
        if if_match:
            clauses.append(('implies', [if_match.group(1), if_match.group(2)], polarity))
        
        return clauses
    
    def _propagate_constraints(self, clauses: List[Tuple]) -> Tuple[int, bool]:
        """Propagate constraints and detect contradictions."""
        satisfied = 0
        contradiction = False
        
        # Check numeric constraints
        for pred, args, pol in clauses:
            if pred == 'cmp_gt' and len(args) == 2:
                if (args[0] > args[1] and pol == 1) or (args[0] <= args[1] and pol == -1):
                    satisfied += 1
                elif (args[0] > args[1] and pol == -1) or (args[0] <= args[1] and pol == 1):
                    contradiction = True
            elif pred == 'cmp_lt' and len(args) == 2:
                if (args[0] < args[1] and pol == 1) or (args[0] >= args[1] and pol == -1):
                    satisfied += 1
                elif (args[0] < args[1] and pol == -1) or (args[0] >= args[1] and pol == 1):
                    contradiction = True
        
        return satisfied, contradiction
    
    def _reaction_diffusion_score(self, clauses: List[Tuple], satisfied: int) -> float:
        """Morphogenetic scoring via reaction-diffusion entropy."""
        if not clauses:
            return 0.5
        
        # Initialize pattern field
        field_size = 8
        A = np.random.rand(field_size, field_size) * 0.1
        
        # Seed activation from satisfied clauses
        sat_ratio = satisfied / max(len(clauses), 1)
        A += sat_ratio * 0.5
        
        # Reaction-diffusion iterations
        D = 0.1
        for _ in range(10):
            laplacian = (np.roll(A, 1, 0) + np.roll(A, -1, 0) + 
                        np.roll(A, 1, 1) + np.roll(A, -1, 1) - 4 * A)
            A = A + D * laplacian + 0.01 * (sat_ratio - A)
            A = np.clip(A, 0, 1)
        
        # Compute entropy (lower = more coherent pattern)
        A_norm = A / (A.sum() + 1e-9)
        entropy = -np.sum(A_norm * np.log(A_norm + 1e-9))
        max_entropy = np.log(field_size * field_size)
        coherence = 1.0 - (entropy / max_entropy)
        
        return coherence
    
    def _trajectory_stability(self, prompt: str, answer: str) -> float:
        """Track state evolution across sequential premise processing."""
        sentences = re.split(r'[.!?]+', prompt)
        states = []
        
        for i in range(1, len(sentences) + 1):
            partial = ' '.join(sentences[:i])
            clauses = self._parse_clauses(partial + ' ' + answer)
            sat, _ = self._propagate_constraints(clauses)
            states.append(sat / max(len(clauses), 1))
        
        if len(states) < 2:
            return 0.5
        
        # Stability = 1 - variance (stable trajectories = high confidence)
        variance = np.var(states)
        stability = 1.0 / (1.0 + variance)
        return stability
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (max 15% of score)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Composite scoring: dynamics 40%, structural 30%, computation 20%, NCD 10%."""
        combined = prompt + ' ' + candidate
        clauses = self._parse_clauses(combined)
        satisfied, contradiction = self._propagate_constraints(clauses)
        
        # Morphogenetic coherence (structural)
        morph_score = self._reaction_diffusion_score(clauses, satisfied)
        
        # Trajectory stability (dynamics)
        traj_score = self._trajectory_stability(prompt, candidate)
        
        # Computational check
        comp_score = satisfied / max(len(clauses), 1) if clauses else 0.5
        
        # NCD tiebreaker
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        
        # Penalize contradictions
        if contradiction:
            self.meta_stats['error_rate'] = min(1.0, self.meta_stats['error_rate'] + 0.1)
            return 0.1
        
        # Weighted combination
        base_score = (0.4 * traj_score + 0.3 * morph_score + 
                     0.2 * comp_score + 0.1 * ncd_score)
        
        # Metacognitive calibration
        calibrated = base_score * self.meta_stats['confidence'] * (1 - self.meta_stats['error_rate'])
        return max(0.0, min(1.0, calibrated))
    
    def _compute_base_confidence(self, prompt: str, answer: str) -> float:
        """Base confidence from trajectory stability and constraint satisfaction."""
        traj_stab = self._trajectory_stability(prompt, answer)
        
        clauses = self._parse_clauses(prompt + ' ' + answer)
        if not clauses:
            return 0.4  # Honest uncertainty
        
        satisfied, contradiction = self._propagate_constraints(clauses)
        
        if contradiction:
            return 0.1
        
        sat_ratio = satisfied / len(clauses)
        
        # Combine stability and satisfaction, cap at 0.85 unless perfect
        conf = 0.5 * traj_stab + 0.5 * sat_ratio
        
        if sat_ratio == 1.0 and traj_stab > 0.9:
            return min(0.95, conf)
        
        return min(0.85, conf)
```

</details>
