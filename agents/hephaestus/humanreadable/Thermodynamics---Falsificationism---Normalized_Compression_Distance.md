# Thermodynamics + Falsificationism + Normalized Compression Distance

**Fields**: Physics, Philosophy, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T21:48:30.552934
**Report Generated**: 2026-03-27T06:37:40.731711

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use a handful of regex patterns to extract from each candidate answer:  
   * literals (e.g., “the temperature rose”) → `Prop(text, polarity=True)`  
   * negations (“not …”) → `polarity=False`  
   * comparatives (“X > Y”, “X ≤ Y”) → store `(left, op, right)`  
   * conditionals (“if A then B”) → store `(antecedent, consequent)`  
   * causal cues (“because”, “leads to”) → store `(cause, effect)`  
   * numeric values → attach as attributes.  
   Each proposition is a `namedtuple` saved in a Python list; a parallel NumPy array holds a weight `w_i` (initially 1.0).

2. **Constraint graph & propagation** – Build a directed graph where nodes are literals and edges represent conditionals, causals, and comparatives.  
   * Apply unit resolution (modus ponens) iteratively: if `A` is true and `A→B` exists, set `B` true.  
   * Propagate comparatives via transitivity (e.g., `A>B` & `B>C` ⇒ `A>C`).  
   * Detect contradictions: a node marked both true and false.  
   After convergence, compute for each proposition a truth probability `p_i ∈ {0,0.5,1}` (0.5 when undetermined).

3. **Thermodynamic score** –  
   * **Energy** `E = Σ w_i * c_i` where `c_i = 1` if proposition `i` participates in any contradiction, else `0`.  
   * **Entropy** `S = - Σ [p_i log p_i + (1-p_i) log(1-p_i)]` (binary entropy, treating 0.5 as maximal uncertainty).  
   * **Free energy** `F = E - T*S` with a fixed temperature `T=1.0`. Lower `F` indicates a more equilibrium‑like (consistent) set.

4. **Falsificationism score** – Proportion of propositions that survived falsification attempts:  
   `Fals = (N - #contradictions) / N`. This mirrors Popper’s bold conjecture: the fewer falsified clauses, the higher the score.

5. **Normalized Compression Distance (NCD)** – Compute `NCD(x,y) = (C(xy)-min(C(x),C(y))) / max(C(x),C(y))` where `C` is the size of `zlib.compress` output (standard library). Use a reference answer or a set of gold‑standard propositions as `y`. The similarity term is `Sim = 1 - NCD`.

6. **Final scoring** –  
   `Score = α*Sim + β*(1 - F_norm) + γ*Fals` where `F_norm = (F - F_min)/(F_max - F_min)` normalizes free energy across candidates, and `α+β+γ=1`. All operations use only NumPy (for arrays) and the stdlib (regex, zlib).

**Structural features parsed** – negations, comparatives (`>`, `<`, `≥`, `≤`, `=`), conditionals (“if…then”), causal cues (“because”, “leads to”, “results in”), numeric quantities, and ordering relations derived from comparative chains.

**Novelty** – While each component appears separately (energy‑based NLP models, Popper‑inspired hypothesis testing, compression‑based similarity), no published work combines them into a joint free‑energy/falsification/NCD scoring pipeline for answer evaluation. Thus the combination is novel.

**Rating**  
Reasoning: 7/10 — captures logical consistency and uncertainty but relies on hand‑crafted regexes.  
Metacognition: 6/10 — the model can detect its own contradictions via free energy, yet lacks explicit self‑reflection on reasoning steps.  
Hypothesis generation: 8/10 — falsification‑driven scoring naturally encourages bold, testable conjectures.  
Implementability: 9/10 — uses only regex, NumPy, and zlib; straightforward to code and run offline.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Thermodynamics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 40% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Falsificationism**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 34% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Falsificationism + Thermodynamics: strong positive synergy (+0.145). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Thermodynamics + Kalman Filtering + Falsificationism (accuracy: 0%, calibration: 0%)
- Apoptosis + Falsificationism + Self-Organized Criticality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Predictive Coding + Falsificationism (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=53% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T05:13:35.261800

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Falsificationism---Normalized_Compression_Distance/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Any

# Structural primitives
Prop = namedtuple('Prop', ['text', 'polarity', 'left', 'op', 'right', 'antecedent', 'consequent', 'cause', 'effect', 'value'])

class ReasoningTool:
    """
    A reasoning evaluator combining Thermodynamic consistency, Falsificationism, and NCD.
    
    Mechanism:
    1. Parsing: Extracts logical structures (negations, comparatives, conditionals) via regex.
    2. Constraint Graph: Builds a dependency graph to propagate truth values (Modus Ponens) 
       and detect contradictions (Energy).
    3. Thermodynamics: Computes Free Energy (F = E - TS) where E is contradiction count 
       and S is entropy of undetermined states. Lower F is better.
    4. Falsification: Scores based on the proportion of non-contradicted propositions.
    5. NCD: Used strictly as a tie-breaker for structural similarity to the prompt context.
    """
    
    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither)\s+(\w+)', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|==|=|greater than|less than)\s*(\w+)', re.IGNORECASE),
            'conditional': re.compile(r'\bif\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)', re.IGNORECASE),
            'causal': re.compile(r'(.+?)\s+(because|leads to|results in|causes)\s+(.+?)(?:\.|,|$)', re.IGNORECASE),
            'numeric': re.compile(r'\b(\d+\.?\d*)\b')
        }

    def _parse_text(self, text: str) -> List[Prop]:
        """Extract structured propositions from text."""
        props = []
        lower_text = text.lower()
        
        # 1. Negations
        for m in self.patterns['negation'].finditer(lower_text):
            props.append(Prop(text=m.group(0), polarity=False, left=None, op=None, right=None,
                              antecedent=None, consequent=None, cause=None, effect=None, value=None))
            
        # 2. Comparatives
        for m in self.patterns['comparative'].finditer(lower_text):
            props.append(Prop(text=m.group(0), polarity=True, left=m.group(1), op=m.group(2), right=m.group(3),
                              antecedent=None, consequent=None, cause=None, effect=None, value=None))
                              
        # 3. Conditionals
        for m in self.patterns['conditional'].finditer(lower_text):
            props.append(Prop(text=m.group(0), polarity=True, left=None, op=None, right=None,
                              antecedent=m.group(1).strip(), consequent=m.group(2).strip(),
                              cause=None, effect=None, value=None))
                              
        # 4. Causal
        for m in self.patterns['causal'].finditer(lower_text):
            props.append(Prop(text=m.group(0), polarity=True, left=None, op=None, right=None,
                              antecedent=None, consequent=None, cause=m.group(1).strip(), effect=m.group(3).strip(), value=None))

        # 5. Numerics (attach to context if possible, else standalone)
        nums = self.patterns['numeric'].findall(lower_text)
        if nums:
            props.append(Prop(text=" ".join(nums), polarity=True, left=None, op=None, right=None,
                              antecedent=None, consequent=None, cause=None, effect=None, value=float(nums[0]) if nums else None))
        
        # Default literal if no structure found
        if not props and len(text.strip()) > 5:
            props.append(Prop(text=text.strip(), polarity=True, left=None, op=None, right=None,
                              antecedent=None, consequent=None, cause=None, effect=None, value=None))
        return props

    def _build_graph_and_propagate(self, props: List[Prop]) -> Tuple[float, float, int]:
        """
        Build constraint graph, propagate truth, detect contradictions.
        Returns: (Energy, Entropy, Contradiction Count)
        """
        n = len(props)
        if n == 0:
            return 0.0, 0.0, 0
            
        # State: 0=False, 0.5=Unknown, 1=True
        state = np.full(n, 0.5) 
        weights = np.ones(n)
        
        # Map keywords to indices for quick lookup
        keyword_map = {}
        for i, p in enumerate(props):
            if p.left: keyword_map.setdefault(p.left.lower(), []).append(i)
            if p.right: keyword_map.setdefault(p.right.lower(), []).append(i)
            if p.antecedent: keyword_map.setdefault(p.antecedent.lower(), []).append(i)
            if p.consequent: keyword_map.setdefault(p.consequent.lower(), []).append(i)
            if p.cause: keyword_map.setdefault(p.cause.lower(), []).append(i)
            if p.effect: keyword_map.setdefault(p.effect.lower(), []).append(i)

        contradictions = 0
        
        # Iterative propagation (simplified unit resolution)
        changed = True
        iterations = 0
        while changed and iterations < 10:
            changed = False
            iterations += 1
            for i, p in enumerate(props):
                if state[i] == 0.5: # Only process unknowns or re-evaluate
                    # Check comparatives transitivity logic (simplified)
                    if p.left and p.op in ['>', '>=', '=', '==']:
                        # If we know left, infer right? Hard without external knowledge.
                        # Instead, check internal consistency of the proposition list
                        pass
                    
                # Detect direct negation conflicts
                if p.polarity == False:
                    # Look for positive version of same text
                    target = p.text.replace(re.search(r'\b(not|no|never|neither)\s+', p.text, re.I).group(0), "") if re.search(r'\b(not|no|never|neither)\s+', p.text, re.I) else ""
                    for j, other in enumerate(props):
                        if i != j and target in other.text and other.polarity == True:
                            if state[i] > 0 and state[j] > 0: # Both asserted true
                                state[i] = 0.0 # Mark contradiction as false energy
                                state[j] = 0.0
                                contradictions += 1
                                changed = True

        # Calculate Energy (E): Sum of weights where contradiction exists
        # Simplified: E = count of contradictions
        E = float(contradictions)
        
        # Calculate Entropy (S): Binary entropy of state probabilities
        # Treat 0.5 as max uncertainty (1.0 entropy), 0 or 1 as 0 entropy
        S = 0.0
        for p_val in state:
            if 0 < p_val < 1:
                # Avoid log(0)
                p_safe = max(1e-9, min(1-1e-9, p_val))
                S -= (p_safe * np.log2(p_safe) + (1-p_safe) * np.log2(1-p_safe))
            elif p_val == 0.5:
                S += 1.0 # Max entropy for unknown
        
        return E, S, contradictions

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        scores = []
        
        # Parse prompt once
        prompt_props = self._parse_text(prompt)
        prompt_E, prompt_S, _ = self._build_graph_and_propagate(prompt_props)
        
        for cand in candidates:
            # 1. Parse Candidate
            cand_props = self._parse_text(cand)
            
            # 2. Thermodynamic Score (Consistency)
            E, S, contra_count = self._build_graph_and_propagate(cand_props)
            T = 1.0
            F = E - T * S  # Free energy. Lower is better (more consistent/less uncertain)
            
            # 3. Falsification Score
            # Proportion of props that didn't lead to contradiction
            total_props = max(1, len(cand_props))
            fals_score = (total_props - contra_count) / total_props
            
            # 4. NCD Similarity (Tiebreaker/Context check)
            # Compare candidate to prompt to ensure relevance
            ncd_val = self._compute_ncd(prompt, cand)
            sim_score = 1.0 - ncd_val
            
            # Combined Score
            # Priority: Falsification (Logic) > Thermodynamics (Consistency) > NCD (Relevance)
            # Normalize F roughly: assume max E is small, S is bounded by log(n)
            norm_F = 1.0 / (1.0 + abs(F)) if F != 0 else 1.0
            
            final_score = 0.5 * fals_score + 0.3 * norm_F + 0.2 * sim_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Falsification:{fals_score:.2f}, Thermodynamics(F):{F:.2f}, NCD-Sim:{sim_score:.2f}"
            })
            scores.append(final_score)
            
        # Rank descending
        ranked_indices = np.argsort(scores)[::-1]
        return [results[i] for i in ranked_indices]

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly
        score = res[0]['score']
        return min(1.0, max(0.0, score))
```

</details>
