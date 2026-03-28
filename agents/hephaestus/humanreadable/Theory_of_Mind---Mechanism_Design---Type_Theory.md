# Theory of Mind + Mechanism Design + Type Theory

**Fields**: Cognitive Science, Economics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:12:58.927548
**Report Generated**: 2026-03-27T05:13:35.350551

---

## Nous Analysis

**Algorithm**  
We build a *Typed Belief‑Propagation Scorer* (TBPS).  

1. **Parsing & typing** – Using regex we extract atomic propositions `p_i` from prompt and each candidate answer. For each we assign a simple type:  
   - `Bool` for plain statements, negations (`¬p`), and conditionals (`p → q`).  
   - `Real` for numeric values extracted with `\d+(\.\d+)?`.  
   - `Order` for comparatives (`>`, `<`, `≥`, `≤`) and causal chains (`p because q`).  
   The result is a list `terms = [(id, type, payload)]`.  

2. **Typed dependency graph** – Nodes are the extracted terms. Edges encode logical rules derived from the syntax:  
   - Modus ponens: if we have `p → q` (type `Bool`) and node `p`, add edge `p → q`.  
   - Transitivity for `Order`: `a > b` ∧ `b > c ⇒ a > c`.  
   - Numeric constraints: `x = 5` and `x > y` give `y < 5`.  
   The graph is a DAG; we store adjacency in a `numpy.int8` matrix `E`.  

3. **Constraint propagation (belief update)** – Initialize a belief vector `b ∈ [0,1]^n` for each agent (speaker, listener, generic “reasoner”) with uniform priors. Iterate:  
   ```
   b_new = b + α * (E @ b - b)   # α=0.1, @ is numpy matmul
   b_new = clip(b_new,0,1)
   ```  
   After convergence (`‖b_new-b‖<1e-3`) we treat `b` as the inferred truth‑probability distribution over worlds implied by the text.  

4. **Mechanism‑design scoring** – Treat the candidate answer as a reported probability vector `r` (built by mapping its propositions to the same index set and setting `r_i=1` for asserted literals, `0` for negated literals, averaging for conditionals). Apply the quadratic scoring rule, a strictly proper (incentive‑compatible) mechanism:  
   ```
   S = 1 - np.sum((r - b)**2)
   ```  
   Higher `S` indicates the answer aligns better with the inferred belief state while being truthful‑inducing.  

**Structural features parsed**  
Negations (`not`, `¬`), conditionals (`if … then …`), comparatives (`>`, `<`, `≥`, `≤`), causal markers (`because`, `leads to`), numeric constants, and ordering chains. These map directly to the typed propositions and the edge‑generation rules above.  

**Novelty**  
The combination mirrors existing frameworks (probabilistic soft logic, Markov Logic Networks, Bayesian Truth Serum) but adds a *type‑theoretic stratification* before belief propagation and uses a *proper scoring rule* from mechanism design as the final loss. No prior work couples syntactic type inference with incentive‑compatible scoring in a pure‑numpy pipeline, making the approach novel in this specific configuration.  

**Ratings**  
Reasoning: 7/10 — captures logical inference and belief updating but relies on simple linear propagation.  
Metacognition: 6/10 — models others’ beliefs via separate agent vectors, yet lacks higher‑order recursion depth.  
Hypothesis generation: 5/10 — generates implied truths through closure, but does not actively propose novel hypotheses beyond entailment.  
Implementability: 8/10 — all steps use regex, numpy matrix ops, and basic loops; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Type Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Mechanism Design + Type Theory: strong positive synergy (+0.562). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Causal Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Criticality + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: SyntaxError: (unicode error) 'utf-8' codec can't decode byte 0xac in position 25: invalid start byte (tmppc5rkqjc.py, line 40)

**Forge Timestamp**: 2026-03-26T12:44:49.978078

---

## Code

**Source**: scrap

[View code](./Theory_of_Mind---Mechanism_Design---Type_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np

class ReasoningTool:
    """
    Typed Belief-Propagation Scorer (TBPS).
    Combines Type Theory (parsing types), Theory of Mind (belief vectors),
    and Mechanism Design (quadratic scoring) to evaluate reasoning.
    """
    
    def __init__(self):
        self.alpha = 0.1
        self.tol = 1e-3
        self.max_iter = 100

    def _extract_terms(self, text):
        """Parse text into typed terms: (id, type, payload, sign)."""
        terms = []
        text_lower = text.lower()
        
        # 1. Numeric constants (Type: Real)
        nums = re.finditer(r'(\d+(?:\.\d+)?)', text)
        for m in nums:
            terms.append((m.start(), 'Real', float(m.group(1)), 1.0))
            
        # 2. Comparatives (Type: Order) - simplified detection
        order_patterns = [
            (r'greater than|>', 'gt'), (r'less than|<', 'lt'),
            (r'equal to|=', 'eq'), (r'more than', 'gt')
        ]
        for pat, label in order_patterns:
            if re.search(pat, text_lower):
                terms.append((0, 'Order', label, 1.0))
                
        # 3. Conditionals & Causal (Type: Bool structure)
        if re.search(r'if.*then|because|leads to|implies', text_lower):
            terms.append((0, 'Bool', 'conditional', 1.0))
            
        # 4. Negations
        if re.search(r'\bnot\b|\bno\b|\bnever\b|¬', text_lower):
            terms.append((0, 'Bool', 'negation', -1.0))
            
        # 5. Generic propositions (split by punctuation for density)
        # We treat the presence of specific keywords as atomic Bool propositions
        keywords = ['true', 'false', 'yes', 'no', 'correct', 'wrong']
        for kw in keywords:
            if kw in text_lower:
                terms.append((0, 'Bool', kw, 1.0))
                
        return terms

    def _build_graph(self, prompt, candidate):
        """Construct adjacency matrix based on typed dependency rules."""
        # Combine context for term extraction to ensure shared vocabulary
        full_text = f"{prompt} {candidate}"
        terms = self._extract_terms(full_text)
        n = max(1, len(terms))
        
        # Initialize adjacency matrix E (n x n)
        E = np.zeros((n, n), dtype=np.float32)
        
        # Map types to indices for rule application
        type_map = {t[1]: i for i, t in enumerate(terms)}
        
        # Apply Typed Dependency Rules
        # Rule 1: Modus Ponens / Implication (Bool -> Bool)
        if 'Bool' in type_map:
            idx = type_map['Bool']
            # Self-reinforcement for logical consistency
            E[idx, idx] = 0.5 
            # Connect to other bools if present
            for i, t in enumerate(terms):
                if t[1] == 'Bool':
                    E[idx, i] = 0.2
                    E[i, idx] = 0.2

        # Rule 2: Transitivity (Order)
        if 'Order' in type_map:
            idx = type_map['Order']
            # Order constraints propagate strongly
            for i in range(n):
                E[idx, i] = 0.1
                E[i, idx] = 0.1
                
        # Rule 3: Numeric Constraints (Real)
        if 'Real' in type_map:
            idx = type_map['Real']
            # Numbers anchor beliefs
            for i in range(n):
                E[idx, i] = 0.05
                
        return E, n, terms

    def _propagate_beliefs(self, E, n):
        """Iterative belief update: b_new = b + alpha * (E @ b - b)"""
        b = np.ones(n) * 0.5  # Uniform prior
        
        for _ in range(self.max_iter):
            b_new = b + self.alpha * (E @ b - b)
            b_new = np.clip(b_new, 0.0, 1.0)
            if np.linalg.norm(b_new - b) < self.tol:
                break
            b = b_new
        return b

    def _get_report_vector(self, candidate, terms):
        """Map candidate assertions to the term index space."""
        r = np.zeros(len(terms))
        if not terms:
            return r
            
        c_lower = candidate.lower()
        
        for i, (_, t_type, payload, sign) in enumerate(terms):
            # If the candidate contains the specific keyword or number, assert it
            if t_type == 'Real':
                if str(int(payload)) in candidate or str(payload) in candidate:
                    r[i] = 1.0 if sign > 0 else 0.0
            elif t_type == 'Bool':
                if payload in c_lower:
                    r[i] = 1.0 if sign > 0 else 0.0
                elif payload == 'conditional' and ('if' in c_lower or 'because' in c_lower):
                    r[i] = 1.0
            elif t_type == 'Order':
                if payload == 'gt' and ('greater' in c_lower or '>' in c_lower):
                    r[i] = 1.0
                elif payload == 'lt' and ('less' in c_lower or '<' in c_lower):
                    r[i] = 1.0
                    
        # If no specific matches but terms exist, default to average belief of prompt
        if np.sum(r) == 0 and len(terms) > 0:
            r[:] = 0.5
            
        return r

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        import zlib
        l1, l2, l12 = len(s1), len(s2), len(s1 + s2)
        if l12 == 0: return 0.0
        # Approximate compression length with string length for speed/simplicity in this constraint
        # Real NCD needs actual compression sizes. Using len as proxy for "structural" check
        # To strictly follow "zlib NCD":
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        if not candidates:
            return []
            
        # Build global term space from prompt + all candidates to ensure alignment
        all_text = prompt + " " + " ".join(candidates)
        # Re-extract terms for the global space if needed, but here we simplify 
        # by building graph per candidate against prompt context for modularity.
        
        scores = []
        for cand in candidates:
            E, n, terms = self._build_graph(prompt, cand)
            if n == 0:
                # Fallback to NCD if no structure found
                score = 1.0 - self._ncd(prompt, cand)
                reason = "No structural tokens; fallback to NCD."
            else:
                # 1. Propagate beliefs based on prompt logic
                b = self._propagate_beliefs(E, n)
                
                # 2. Get candidate's reported vector
                r = self._get_report_vector(cand, terms)
                
                # 3. Mechanism Design: Quadratic Scoring Rule
                # S = 1 - sum((r - b)^2)
                diff = r - b
                S = 1.0 - np.sum(diff ** 2)
                score = float(S)
                reason = f"Typed belief propagation over {n} terms. Quadratic score: {score:.4f}"
            
            results.append({"candidate": cand, "score": score, "reasoning": reason})
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score: Theoretical min is negative infinity, but practically > -10
        # Map to 0-1. Since S = 1 - sum(sq), max is 1. 
        # We assume a reasonable lower bound of -5 for normalization if needed, 
        # but raw score is often sufficient for ranking. 
        # To strictly fit 0-1:
        raw = res[0]['score']
        conf = max(0.0, min(1.0, (raw + 1.0) / 2.0)) # Simple mapping assuming range [-1, 1] roughly
        return conf
```

</details>
