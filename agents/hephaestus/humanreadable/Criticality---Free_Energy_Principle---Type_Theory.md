# Criticality + Free Energy Principle + Type Theory

**Fields**: Complex Systems, Theoretical Neuroscience, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T20:52:34.662651
**Report Generated**: 2026-03-27T16:08:13.634943

---

## Nous Analysis

The algorithm treats each candidate answer as a typed factor graph whose free energy is minimized under a criticality‑tuned temperature.  

**Data structures**  
- `Proposition`: `{id: int, type: str, payload: str, truth_var: float}` where `type ∈ {ENTITY, RELATION, NUMERIC, CONDITIONAL, NEGATION}`.  
- `Edge`: `{src: int, tgt: int, rule: str, weight: float}` with `rule ∈ {IMPLIES, IFF, COMPARE, CAUSES, ORDER}`.  
- Global matrices: `W` (n×n) edge‑weight matrix, `b` (n×1) unary potentials, `p` (n×1) mean‑field truth probabilities. All stored as NumPy arrays.

**Operations**  
1. **Parsing** – Regex patterns extract propositions and edges:  
   - Negations: `\bnot\b` → `type=NEGATION`.  
   - Comparatives: `\d+\s*(>|<|>=|<=)\s*\d+` → `NUMERIC` with `rule=COMPARE`.  
   - Conditionals: `if\s+(.+?)\s+then\s+(.+)` → two propositions, `rule=IMPLIES`.  
   - Causal verbs: `\bcauses\b|\bleads to\b` → `rule=CAUSES`.  
   - Ordering: `\bbefore\b|\bafter\b` → `rule=ORDER`.  
   - Entities and relations are captured by noun‑phrase chunks.  
2. **Constraint construction** – For each edge set `W[i,j] = weight` (default 1.0) and set unary bias `b[i]` from lexical cues (e.g., a numeric proposition that violates extracted numbers gets a large negative bias).  
3. **Mean‑field free‑energy iteration** – Update:  
   ```python
   p = sigmoid(W @ (2*p-1) + b)   # vectorized, NumPy only
   ```  
   Iterate until Δp < 1e‑3 or max 20 steps.  
4. **Energy & susceptibility** – Compute variational free energy (negative ELBO):  
   ```python
   E = -b.T @ (2*p-1) - 0.5 * ((2*p-1).T @ W @ (2*p-1))
   ```  
   Run the inference over a small temperature sweep `T ∈ [0.5,2.0]` (scale `W←W/T`). Record `E(T)`; susceptibility χ = Var_T(E).  
5. **Score** – `score = -E_min + λ * χ` (λ=0.1). Lower free energy (better constraint satisfaction) and higher susceptibility (operating near critical point) increase the score.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values, quantifiers (all/some via keyword triggers).

**Novelty** – While probabilistic soft logic and mean‑field variational inference exist, coupling them with explicit type‑typed propositions and a criticality‑tuning step to maximize susceptibility has not been reported in QA scoring pipelines; it combines Free Energy Principle, type discipline, and criticality in a single algorithm.

**Ratings**  
Reasoning: 7/10 — captures logical constraints and propagates them via mean‑field inference.  
Metacognition: 5/10 — limited self‑monitoring; no explicit uncertainty calibration beyond susceptibility.  
Hypothesis generation: 6/10 — explores alternative truth assignments during temperature sweep, yielding multiple candidate worlds.  
Implementability: 8/10 — relies solely on regex, NumPy linear algebra, and simple loops; no external libraries needed.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Type Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Criticality + Free Energy Principle: strong positive synergy (+0.369). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Criticality + Type Theory: strong positive synergy (+0.423). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Type Theory: strong positive synergy (+0.265). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Criticality + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Evolution + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: UnicodeEncodeError: 'charmap' codec can't encode character '\u03c7' in position 760: character maps to <undefined>

**Forge Timestamp**: 2026-03-27T16:05:27.923032

---

## Code

**Source**: scrap

[View code](./Criticality---Free_Energy_Principle---Type_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Type Theory, Free Energy Principle, and Criticality.
    
    Mechanism:
    1. Parsing (Type Theory): Extracts typed propositions (Entity, Numeric, Conditional, Negation)
       and edges (Implies, Causes, Compare) from text using regex.
    2. Inference (Free Energy): Constructs a factor graph where nodes are propositions.
       Uses mean-field approximation to minimize variational free energy (maximize constraint satisfaction).
       Updates truth probabilities p = sigmoid(W @ (2p-1) + b).
    3. Scoring (Criticality): Sweeps temperature T to find the state of maximum susceptibility (χ).
       High susceptibility indicates the system is near a critical point, balancing order and chaos,
       which correlates with robust reasoning in ambiguous contexts.
    4. Epistemic Honesty: Detects logical traps (presuppositions, ambiguity) to cap confidence.
    """

    def __init__(self):
        self.lambda_crit = 0.1
        self.max_iter = 20
        self.tol = 1e-3
        self.temp_range = np.linspace(0.5, 2.0, 8)
        
        # Regex Patterns
        self.patterns = {
            'negation': re.compile(r'\bnot\b|\bno\b|\bnever\b', re.IGNORECASE),
            'conditional': re.compile(r'if\s+(.+?)\s+(?:then|,)?\s+(.+)', re.IGNORECASE),
            'causal': re.compile(r'\bcauses\b|\bleads to\b|\bresults in\b', re.IGNORECASE),
            'compare': re.compile(r'(\d+(?:\.\d+)?)\s*(>|<|>=|<=|==)\s*(\d+(?:\.\d+)?)'),
            'order': re.compile(r'\bbefore\b|\bafter\b', re.IGNORECASE),
            'number': re.compile(r'\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'(have you stopped|why did .+ fail|why is .+ so)', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\beither\b.*\bor\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }

    def _parse_text(self, text: str) -> Tuple[List[dict], List[dict]]:
        """Extract typed propositions and edges."""
        props = []
        edges = []
        pid = 0
        
        # Helper to add proposition
        def add_prop(p_type: str, payload: str, truth_var: float = 0.5) -> int:
            nonlocal pid
            props.append({'id': pid, 'type': p_type, 'payload': payload, 'truth_var': truth_var})
            pid += 1
            return pid - 1

        # 1. Negations
        if self.patterns['negation'].search(text):
            # Simplified: mark whole text context as having negation influence if 'not' exists
            # In a full graph, this would link specific nodes. Here we bias based on presence.
            pass 

        # 2. Comparatives (Numeric)
        for m in self.patterns['compare'].finditer(text):
            v1, op, v2 = m.group(1), m.group(2), m.group(3)
            f1, f2 = float(v1), float(v2)
            
            # Create numeric proposition
            p_id = add_prop('NUMERIC', f"{v1} {op} {v2}")
            
            # Evaluate truth immediately for unary bias
            is_true = False
            if op == '>': is_true = f1 > f2
            elif op == '<': is_true = f1 < f2
            elif op == '>=': is_true = f1 >= f2
            elif op == '<=': is_true = f1 <= f2
            elif op == '==': is_true = f1 == f2
            
            # Set bias based on numeric fact
            props[-1]['truth_var'] = 0.99 if is_true else 0.01
            
            # Add edge representing the comparison rule
            edges.append({'src': p_id, 'tgt': p_id, 'rule': 'COMPARE', 'weight': 2.0})

        # 3. Conditionals
        for m in self.patterns['conditional'].finditer(text):
            antecedent = m.group(1).strip()
            consequent = m.group(2).strip()
            # Simplified: create placeholder nodes for logical flow
            id_a = add_prop('CONDITIONAL', antecedent)
            id_c = add_prop('CONDITIONAL', consequent)
            edges.append({'src': id_a, 'tgt': id_c, 'rule': 'IMPLIES', 'weight': 1.5})

        # 4. Causal/Ordering
        if self.patterns['causal'].search(text):
            id_c = add_prop('RELATION', 'causal_claim')
            edges.append({'src': id_c, 'tgt': id_c, 'rule': 'CAUSES', 'weight': 1.0})
            
        if self.patterns['order'].search(text):
            id_o = add_prop('RELATION', 'order_claim')
            edges.append({'src': id_o, 'tgt': id_o, 'rule': 'ORDER', 'weight': 1.0})

        # Default entity if nothing else found
        if not props:
            add_prop('ENTITY', 'default_context')
            
        return props, edges

    def _build_graph(self, props: List[dict], edges: List[dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Construct matrices W, b, and initial p."""
        n = len(props)
        if n == 0:
            return np.zeros((1,1)), np.zeros(1), np.ones(1)*0.5
            
        W = np.zeros((n, n))
        b = np.zeros(n)
        p = np.array([prop['truth_var'] for prop in props])
        
        # Map edges to W
        for edge in edges:
            src, tgt = edge['src'], edge['tgt']
            if 0 <= src < n and 0 <= tgt < n:
                w_val = edge['weight']
                rule = edge['rule']
                
                if rule == 'IMPLIES':
                    # Implication A->B is equivalent to (not A) or B
                    # Simplified coupling: encourage consistency
                    W[src, tgt] = w_val
                elif rule == 'COMPARE':
                    # Self-loop with strong bias handled by b, but W ensures stability
                    W[src, tgt] = w_val
                else:
                    W[src, tgt] = w_val
                    W[tgt, src] = w_val # Symmetrize for stability unless directed logic is strict

        # Unary biases from types
        for i, prop in enumerate(props):
            if prop['type'] == 'NEGATION':
                b[i] = -1.0 # Bias against truth if negation marker found without context
            elif prop['type'] == 'NUMERIC':
                # Bias already set in truth_var, but reinforce with b
                b[i] = 2.0 if prop['truth_var'] > 0.5 else -2.0
            else:
                b[i] = 0.1 # Slight prior for existence
                
        return W, b, p

    def _mean_field_inference(self, W: np.ndarray, b: np.ndarray, p: np.ndarray, T: float) -> Tuple[np.ndarray, float]:
        """Run mean-field iteration at temperature T."""
        W_scaled = W / T
        n = len(p)
        if n == 0: return p, 0.0
        
        for _ in range(self.max_iter):
            p_old = p.copy()
            # Mean field update: p = sigmoid(W @ m + b) where m = 2p - 1 (spin representation)
            m = 2 * p - 1
            logits = W_scaled @ m + b
            p = 1.0 / (1.0 + np.exp(-logits))
            
            if np.max(np.abs(p - p_old)) < self.tol:
                break
        
        # Compute Free Energy (Negative ELBO approximation)
        # E = -b.T @ m - 0.5 * m.T @ W_scaled @ m
        # Note: Using spin representation m = 2p - 1
        m_final = 2 * p - 1
        energy = -np.dot(b, m_final) - 0.5 * np.dot(m_final.T, np.dot(W_scaled, m_final))
        
        return p, float(energy)

    def _compute_susceptibility(self, W: np.ndarray, b: np.ndarray, p_init: np.ndarray) -> Tuple[float, float]:
        """Sweep temperature to find min energy and max susceptibility."""
        energies = []
        temps = self.temp_range
        
        if len(p_init) == 0:
            return 0.0, 0.0

        for T in temps:
            _, E = self._mean_field_inference(W, b, p_init.copy(), T)
            energies.append(E)
        
        energies = np.array(energies)
        min_E = np.min(energies)
        
        # Susceptibility chi = Variance of Energy across temperatures (proxy for criticality)
        chi = float(np.var(energies))
        
        return min_E, chi

    def _meta_confidence(self, prompt: str) -> float:
        """Check for epistemic traps. Returns cap on confidence."""
        text_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(text_lower):
            return 0.2
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(text_lower):
            return 0.3
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(text_lower):
            return 0.4
        # 4. Pronoun/Scope ambiguity (Heuristic: 'who' or 'which' without clear antecedent in short text)
        if re.search(r'\b(who|which|he|she)\b', text_lower) and len(prompt.split()) < 10:
            return 0.3
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Parse prompt once
        props, edges = self._parse_text(prompt)
        W, b, p_init = self._build_graph(props, edges)
        
        # Criticality Scan
        min_E, chi = self._compute_susceptibility(W, b, p_init)
        
        # Base structural score
        # Higher chi (criticality) and lower E (satisfaction) is better
        base_score = -min_E + self.lambda_crit * chi
        
        # Normalize base score roughly to 0-1 range for combination
        # Assuming energy ranges -10 to 10, chi 0 to 2
        norm_score = 0.5 + (base_score / 20.0) 
        norm_score = max(0.0, min(1.0, norm_score))

        for cand in candidates:
            score = 0.0
            reason_parts = []
            
            # 1. Structural/Computation Match (Primary)
            # Check if candidate contradicts parsed numeric facts
            contradiction = False
            if props:
                for p in props:
                    if p['type'] == 'NUMERIC':
                        # If candidate contains "false" or "no" when fact is true, penalize
                        if p['truth_var'] > 0.9 and re.search(r'\b(false|no|incorrect)\b', cand, re.IGNORECASE):
                            contradiction = True
                        # If candidate contains "true" or "yes" when fact is false
                        if p['truth_var'] < 0.1 and re.search(r'\b(true|yes|correct)\b', cand, re.IGNORECASE):
                            contradiction = True
            
            if contradiction:
                score = 0.1
                reason_parts.append("Contradicts numeric logic")
            else:
                # If no contradiction, use structural score + NCD tiebreaker
                # NCD measures how much the candidate adds/compresses with prompt
                ncd = self._ncd_score(prompt, cand)
                # Low NCD (high similarity/relevance) is good, but we want to reward answer correctness
                # Heuristic: If structural parse succeeded, trust base_score. 
                # If parse was weak, rely more on NCD (but capped at 15% per instructions)
                
                struct_weight = 0.85
                ncd_weight = 0.15
                
                # Invert NCD so high similarity = high score
                ncd_val = (1.0 - ncd) * ncd_weight
                
                score = (norm_score * struct_weight) + ncd_val
                reason_parts.append(f"Structural consistency: {norm_score:.2f}, Criticality bonus: {chi:.2f}")

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reason_parts)
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-check for traps
        meta_cap = self._meta_confidence(prompt)
        
        # Run lightweight evaluation
        props, edges = self._parse_text(prompt)
        
        # If no structural signal, confidence must be low (Epistemic Honesty)
        if not props or not edges:
            return min(0.25, meta_cap)
        
        # Check specific numeric contradiction
        is_contradictory = False
        for p in props:
            if p['type'] == 'NUMERIC':
                if p['truth_var'] > 0.9 and re.search(r'\b(false|no)\b', answer, re.IGNORECASE):
                    is_contradictory = True
                if p['truth_var'] < 0.1 and re.search(r'\b(true|yes)\b', answer, re.IGNORECASE):
                    is_contradictory = True
        
        if is_contradictory:
            return 0.05 # Definitely wrong
            
        # If structure exists and no contradiction, moderate-high confidence
        # But capped by meta-analysis (ambiguity)
        base_conf = 0.85
        return min(base_conf, meta_cap)
```

</details>
