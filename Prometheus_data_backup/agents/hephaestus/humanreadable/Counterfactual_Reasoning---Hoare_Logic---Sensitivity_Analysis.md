# Counterfactual Reasoning + Hoare Logic + Sensitivity Analysis

**Fields**: Philosophy, Formal Methods, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T20:38:17.972708
**Report Generated**: 2026-04-02T10:55:58.883198

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Extract atomic propositions, numeric comparisons, and implication patterns with regex:  
   - `if <cond> then <cons>` → Horn clause `⟨cond⟩ ⟹ ⟨cons⟩`  
   - `because <cause> <effect>` → `⟨cause⟩ ⟹ ⟨effect⟩`  
   - Negations (`not`, `no`) toggle polarity.  
   - Comparatives (`>`, `<`, `=`) become numeric literals stored as `(var, op, const)`.  
   Each clause is a tuple `(pre: List[Literal], post: List[Literal])`.  
   All clauses are kept in a list `KB`.  

2. **Forward chaining (Hoare‑style)** – Starting from a set of asserted facts `F₀` (extracted from the prompt), repeatedly apply modus ponens: for any clause `(pre, post)` where `pre ⊆ F`, add `post` to `F`. This yields the closure `F*`, analogous to computing the strongest postcondition `{P}C{Q}`.  

3. **Counterfactual do‑operator** – For each candidate answer that contains a counterfactual clause (`would <X> if <Y>`), temporarily remove all incoming edges to the literal `<Y>` in the implication graph, set `<Y>` to the asserted value, and re‑run forward chaining. The resulting set `F*_{cf}` is the “possible world” under the intervention.  

4. **Sensitivity analysis** – For every numeric literal `(v, op, c)` in `KB`, perturb `c` by `±ε` (ε=1e‑3), recompute the closure, and record the change in each derived post‑literal as Δ. Stack Δs into a matrix `S`; the sensitivity score is `‖S‖₂` (Frobenius norm). Lower norm ⇒ more robust conclusions.  

5. **Scoring** – Let `R*` be the reference answer’s closure (obtained by the same pipeline on a gold answer). Compute:  
   - **Logical overlap** `J = |C* ∩ R*| / |C* ∪ R*|` (Jaccard).  
   - **Robustness penalty** `P = 1 / (1 + sensitivity(C*))`.  
   Final score = `J * P`.  

**Structural features parsed** – conditionals (`if…then`), causal connectives (`because`, leads to), negations, comparatives (`>`, `<`, `=`), numeric values and units, ordering phrases (`more than`, `less than`), invariant markers (`always`, `must`, `ensures`).  

**Novelty** – While Hoare logic, counterfactual do‑calculus, and sensitivity analysis each appear separately in verification or causal inference literature, their joint use as a pure‑algorithm scoring pipeline for natural‑language answers is not documented in existing work.  

**Ratings**  
Reasoning: 8/10 — captures deductive closure, counterfactual worlds, and robustness in a single numeric score.  
Metacognition: 6/10 — the method estimates fragility but does not actively monitor its own uncertainty or adjust search strategies.  
Hypothesis generation: 7/10 — the do‑operator generates explicit alternative worlds, serving as hypothesis generation.  
Implementability: 9/10 — relies only on regex, numpy arrays, and iterative forward chaining; straightforward to code and test.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=1% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T10:31:26.790923

---

## Code

**Source**: scrap

[View code](./Counterfactual_Reasoning---Hoare_Logic---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Set, Tuple

import re
import zlib
from typing import List, Tuple, Set, Dict
import numpy as np

class ReasoningTool:
    """
    Counterfactual Reasoning x Hoare Logic x Sensitivity Analysis
    
    Mechanism:
    1. Parse text into Horn clauses (pre => post) and numeric constraints
    2. Forward chain to compute logical closure (Hoare postcondition)
    3. Apply counterfactual do-operator to test candidate claims
    4. Sensitivity analysis measures robustness to numeric perturbations
    5. Meta-confidence detects ambiguity and structural issues
    """
    
    def __init__(self):
        self.epsilon = 1e-3
    
    def _parse_clauses(self, text: str) -> Tuple[List[Tuple[Set[str], Set[str]]], Dict[str, Tuple[str, float]]]:
        """Parse text into (clauses, numeric_constraints)"""
        text = text.lower()
        clauses = []
        numerics = {}
        
        # Extract numeric comparisons: "x is 5", "x > 10", "x costs $5"
        num_patterns = [
            r'(\w+)\s+(?:is|are|was|were|costs?|equals?)\s+\$?(\d+\.?\d*)',
            r'(\w+)\s*([><]=?|=)\s*(\d+\.?\d*)',
        ]
        for pat in num_patterns:
            for m in re.finditer(pat, text):
                if len(m.groups()) == 2:
                    var, val = m.groups()
                    numerics[var] = ('=', float(val))
                else:
                    var, op, val = m.groups()
                    numerics[var] = (op, float(val))
        
        # Extract conditionals: "if X then Y", "X because Y", "X implies Y"
        cond_patterns = [
            r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$|,)',
            r'(.+?)\s+because\s+(.+?)(?:\.|$|,)',
            r'(.+?)\s+implies?\s+(.+?)(?:\.|$|,)',
            r'when\s+(.+?)\s*,\s*(.+?)(?:\.|$)',
        ]
        for pat in cond_patterns:
            for m in re.finditer(pat, text):
                pre_text, post_text = m.groups()
                pre = self._extract_literals(pre_text)
                post = self._extract_literals(post_text)
                if pre and post:
                    clauses.append((pre, post))
        
        # Extract simple assertions as facts (empty precondition)
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if sent and not any(kw in sent for kw in ['if', 'then', 'because', 'implies', 'when', 'would']):
                lits = self._extract_literals(sent)
                if lits:
                    clauses.append((set(), lits))
        
        return clauses, numerics
    
    def _extract_literals(self, text: str) -> Set[str]:
        """Extract atomic propositions, handling negations"""
        text = text.strip()
        literals = set()
        
        # Handle negations
        is_negated = bool(re.match(r'\s*not\s+|no\s+|n\'t\s+', text))
        text = re.sub(r'\s*not\s+|no\s+|n\'t\s+', '', text)
        
        # Clean and tokenize
        text = re.sub(r'[^\w\s]', '', text)
        tokens = text.split()
        
        if len(tokens) > 0:
            # Create a normalized literal
            lit = '_'.join(tokens[:5])  # Limit to 5 tokens
            if is_negated:
                lit = 'NOT_' + lit
            literals.add(lit)
        
        return literals
    
    def _forward_chain(self, clauses: List[Tuple[Set[str], Set[str]]], 
                       initial_facts: Set[str], max_iter: int = 10) -> Set[str]:
        """Hoare-style forward chaining: compute strongest postcondition"""
        facts = initial_facts.copy()
        
        for _ in range(max_iter):
            changed = False
            for pre, post in clauses:
                if pre.issubset(facts) and not post.issubset(facts):
                    facts.update(post)
                    changed = True
            if not changed:
                break
        
        return facts
    
    def _counterfactual_intervention(self, clauses: List[Tuple[Set[str], Set[str]]], 
                                     intervention: Set[str]) -> Set[str]:
        """Apply do-operator: set intervention facts, remove conflicting edges"""
        # Remove clauses that would derive negations of intervention
        filtered = []
        for pre, post in clauses:
            # Skip clauses that conflict with intervention
            conflict = False
            for lit in post:
                if lit.startswith('NOT_'):
                    pos = lit[4:]
                    if pos in intervention:
                        conflict = True
                else:
                    neg = 'NOT_' + lit
                    if neg in intervention:
                        conflict = True
            if not conflict:
                filtered.append((pre, post))
        
        return self._forward_chain(filtered, intervention)
    
    def _sensitivity_score(self, numerics: Dict[str, Tuple[str, float]], 
                          clauses: List[Tuple[Set[str], Set[str]]]) -> float:
        """Measure robustness to numeric perturbations"""
        if not numerics:
            return 1.0  # No numeric constraints = perfectly robust
        
        baseline = self._forward_chain(clauses, set())
        deltas = []
        
        for var, (op, val) in numerics.items():
            # Perturb up
            perturbed = numerics.copy()
            perturbed[var] = (op, val + self.epsilon)
            result_up = self._forward_chain(clauses, set())
            
            # Perturb down
            perturbed[var] = (op, val - self.epsilon)
            result_down = self._forward_chain(clauses, set())
            
            # Measure symmetric difference
            delta = len(result_up.symmetric_difference(baseline)) + \
                   len(result_down.symmetric_difference(baseline))
            deltas.append(delta)
        
        # Frobenius-like norm
        sensitivity = np.sqrt(np.sum(np.array(deltas) ** 2))
        return 1.0 / (1.0 + sensitivity)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity and structural issues in the prompt"""
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'have you (stopped|quit|ceased)', prompt_lower):
            return 0.2
        if re.search(r'why (did|does|is).+(fail|stop|wrong)', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+.+\ba\b', prompt_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+(who|which)\?', prompt_lower):
            return 0.3
        
        # False dichotomy
        if re.search(r'either .+ or .+\?', prompt_lower) and 'or neither' not in prompt_lower:
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower) and \
           not re.search(r'(most|least|criterion|measure)', prompt_lower):
            return 0.4
        
        return 1.0  # No meta-issues detected
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 that answer is correct"""
        meta_conf = self._meta_confidence(prompt)
        
        # Parse prompt
        clauses, numerics = self._parse_clauses(prompt)
        
        # If no structure parsed, return low confidence
        if not clauses and not numerics:
            return min(0.25, meta_conf)
        
        # Parse answer
        ans_clauses, ans_numerics = self._parse_clauses(answer)
        ans_facts = set()
        for pre, post in ans_clauses:
            ans_facts.update(post)
        
        # Compute prompt closure
        prompt_facts = self._forward_chain(clauses, set())
        
        # Apply counterfactual: inject answer and recompute
        cf_facts = self._counterfactual_intervention(clauses, ans_facts)
        
        # Logical overlap
        if len(prompt_facts | ans_facts) == 0:
            overlap = 0.5
        else:
            overlap = len(cf_facts & prompt_facts) / len(cf_facts | prompt_facts)
        
        # Robustness
        robustness = self._sensitivity_score(numerics, clauses)
        
        # Combined confidence (cap at meta_conf)
        base_conf = min(0.85, overlap * robustness)
        return min(base_conf, meta_conf)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by score (higher = better)"""
        clauses, numerics = self._parse_clauses(prompt)
        prompt_facts = self._forward_chain(clauses, set())
        robustness = self._sensitivity_score(numerics, clauses)
        
        results = []
        for cand in candidates:
            # Parse candidate
            cand_clauses, cand_numerics = self._parse_clauses(cand)
            cand_facts = set()
            for pre, post in cand_clauses:
                cand_facts.update(post)
            
            # Counterfactual intervention
            cf_facts = self._counterfactual_intervention(clauses, cand_facts)
            
            # Logical overlap (Jaccard)
            union = cf_facts | prompt_facts
            if len(union) == 0:
                jaccard = 0.5
            else:
                jaccard = len(cf_facts & prompt_facts) / len(union)
            
            # Structural score (70%)
            structural = jaccard * robustness * 0.7
            
            # NCD tiebreaker (10%)
            ncd_score = (1.0 - self._ncd(prompt, cand)) * 0.1
            
            # Computational: check numeric consistency (20%)
            comp_score = 0.2
            for var, (op, val) in cand_numerics.items():
                if var in numerics:
                    p_op, p_val = numerics[var]
                    if op == '=' and p_op == '=' and abs(val - p_val) < 1e-6:
                        comp_score += 0.1
            
            score = structural + ncd_score + min(comp_score, 0.2)
            
            reasoning = f"Jaccard={jaccard:.2f}, Robust={robustness:.2f}, NCD={ncd_score:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
```

</details>
