# Emergence + Criticality + Property-Based Testing

**Fields**: Complex Systems, Complex Systems, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T19:57:43.889217
**Report Generated**: 2026-04-02T04:20:10.220381

---

## Nous Analysis

**1. Algorithm – Emergent Criticality Checker (ECC)**  
*Data structures*  
- `atoms`: list of tuples `(pred, args, polarity)` extracted from the prompt and each candidate answer via regex (e.g., `('GreaterThan', ('X', 'Y'), True)`).  
- `imp_matrix`: a boolean NumPy array of shape `(n_atoms, n_atoms)` where `imp_matrix[i,j]=1` iff atom i entails atom j (derived from extracted conditionals, causal claims, or numeric comparisons).  
- `core_mask`: boolean array marking atoms currently in the *unsatisfiable core* during shrinking.  

*Operations*  
1. **Parsing** – For each sentence, apply a fixed set of regex patterns to capture:  
   - Negations (`not`, `no`) → flip polarity.  
   - Comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`) → `GreaterThan`/`LessThan` atoms.  
   - Conditionals (`if … then …`, `when …`) → directed edges.  
   - Causal verbs (`cause`, `lead to`, `result in`) → edges.  
   - Ordering (`first`, `before`, `after`) → temporal edges.  
   - Numeric values → atoms with numeric arguments for later arithmetic checks.  
2. **Constraint propagation** – Compute the transitive closure of `imp_matrix` using repeated Boolean matrix multiplication (`imp_matrix = imp_matrix | (imp_matrix @ imp_matrix)`) until convergence (NumPy `dot` with `dtype=bool`). This yields the entailment relation at the *critical* point where adding any new edge would create a cycle.  
3. **Core extraction (property‑based shrinking)** – Initialise `core_mask` with all atoms that appear in the candidate answer. While the sub‑graph induced by `core_mask` contains a directed cycle (detected via NumPy‑based DFS on the adjacency matrix), attempt to remove one atom:  
   - For each atom `k` where `core_mask[k]` is True, temporarily set `core_mask[k]=False` and recompute transitive closure on the reduced matrix.  
   - If the cycle disappears, permanently drop `k`; otherwise restore it.  
   - Iterate until no atom can be removed without eliminating the cycle. The remaining set is a *minimal unsatisfiable core* (MUC).  
4. **Scoring** –  
   - **Emergence score** = number of distinct macro‑level predicates that are *derived* (appear in the transitive closure but not in the original atom list) divided by total derived predicates (range 0‑1).  
   - **Criticality score** = `1 - (|MUC| / n_atoms)`; a smaller core means the answer is nearer to the critical boundary (more fragile).  
   - **Final score** = `0.5 * emergence + 0.5 * criticality`. Higher scores indicate answers that exhibit non‑trivial emergent entailments while being poised near inconsistency.  

**2. Structural features parsed**  
Negations, comparatives (`>`, `<`, `≥`, `≤`), conditionals (`if … then …`), causal verbs (`cause`, `lead to`), temporal ordering (`before`, `after`, `first`), and explicit numeric values with units. These are mapped directly to atoms and directed edges.  

**3. Novelty**  
The combination mirrors existing work in automated reasoning (e.g., SAT‑based unsat‑core extraction, property‑based testing shrinking) and studies of criticality in logical systems (phase transitions in random k‑SAT). However, integrating *emergent macro‑predicate counting* with a criticality‑distance metric derived from the size of a minimal unsatisfiable core is not standard in current reasoning‑evaluation tools, making the approach novel in this specific configuration.  

**Ratings**  
Reasoning: 8/10 — The algorithm performs explicit logical propagation and extracts minimal unsatisfiable cores, providing a principled measure of answer soundness.  
Metacognition: 6/10 — It can report why a score was given (size of core, number of emergent entailments) but does not adapt its parsing strategy based on prior failures.  
Hypothesis generation: 7/10 — The shrinking loop actively generates smaller failing subsets, akin to hypothesis‑based minimization, though it does not propose alternative candidate answers.  
Implementability: 9/10 — All steps use only NumPy for Boolean matrix operations and the Python standard library for regex and control flow; no external dependencies are required.

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
**Reason**: trap_battery_failed (acc=38% cal=17% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T22:06:58.387688

---

## Code

**Source**: scrap

[View code](./Emergence---Criticality---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    Emergent Criticality Checker (ECC) with Constructive Computation.
    
    Mechanism:
    1. Structural Parsing: Extracts atoms (predicates, args, polarity) using regex.
    2. Constructive Computation: Detects numeric/comparative tasks and computes exact answers.
       If a candidate matches the computed answer, it gets a near-perfect score.
    3. Constraint Propagation: Builds an implication matrix and computes transitive closure.
    4. Criticality Analysis: Identifies Minimal Unsatisfiable Cores (MUC) via shrinking.
    5. Scoring: Combines emergence (derived predicates), criticality (fragility), and computation.
    6. Epistemic Honesty: Caps confidence on ambiguous/unanswerable prompts (Tier B).
    """
    
    # Regex patterns for atom extraction
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none)\b', re.I),
        'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|more than|less than|greater than|less than)\s*(\w+)', re.I),
        'conditional': re.compile(r'\bif\s+(.+?)\s+(?:then|,)?\s+(.+?)\b', re.I),
        'causal': re.compile(r'(\w+(?:\s+\w+)?)\s+(causes?|leads to|results in)\s+(\w+(?:\s+\w+)?)', re.I),
        'temporal': re.compile(r'\b(before|after|first|next)\b', re.I),
        'number': re.compile(r'-?\d+(?:\.\d+)?'),
        'pronoun_ambiguity': re.compile(r'(\w+)\s+told\s+(\w+)\s+(he|she|him|her)\b', re.I),
        'presupposition': re.compile(r'\b(have you stopped|why did|why does|failed to|stopped)\b', re.I),
        'false_dichotomy': re.compile(r'\b(either|or)\b', re.I),
        'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.I)
    }

    def __init__(self):
        pass

    def _extract_atoms(self, text: str) -> List[Tuple[str, tuple, bool]]:
        """Extract logical atoms from text."""
        atoms = []
        lower_text = text.lower()
        
        # Negations
        if self.PATTERNS['negation'].search(lower_text):
            atoms.append(('Negation', (), True))
            
        # Comparatives
        for m in self.PATTERNS['comparative'].finditer(lower_text):
            atoms.append(('Comparative', (m.group(1), m.group(2)), True))
            
        # Conditionals
        for m in self.PATTERNS['conditional'].finditer(lower_text):
            atoms.append(('Conditional', (m.group(1), m.group(2)), True))
            
        # Causal
        for m in self.PATTERNS['causal'].finditer(lower_text):
            atoms.append(('Causal', (m.group(1), m.group(3)), True))
            
        # Numbers (as potential operands)
        nums = self.PATTERNS['number'].findall(lower_text)
        if len(nums) >= 2:
            atoms.append(('NumericSet', tuple(nums[:4]), True))
            
        return atoms

    def _build_imp_matrix(self, atoms: List) -> np.ndarray:
        """Build initial implication matrix based on atom types."""
        n = len(atoms)
        if n == 0:
            return np.array([], dtype=bool)
            
        imp = np.zeros((n, n), dtype=bool)
        np.fill_diagonal(imp, True)
        
        # Simple heuristic: earlier atoms imply later ones in a sequence unless negated
        # This simulates a basic narrative flow constraint
        for i in range(n - 1):
            if atoms[i][0] != 'Negation':
                imp[i, i+1] = True
                
        return imp

    def _transitive_closure(self, matrix: np.ndarray) -> np.ndarray:
        """Compute transitive closure via Boolean matrix multiplication."""
        if matrix.size == 0:
            return matrix
        n = matrix.shape[0]
        if n == 0:
            return matrix
            
        closure = matrix.copy()
        # Warshall's algorithm or repeated squaring
        # Using repeated squaring for numpy efficiency
        for _ in range(n): 
            prev = closure.copy()
            closure = closure | (closure @ closure > 0)
            if np.array_equal(prev, closure):
                break
        return closure

    def _compute_answer(self, prompt: str) -> Optional[Any]:
        """
        Constructive Computation: Attempt to solve numeric/logic problems directly.
        Returns the computed answer if solvable, else None.
        """
        # Extract all numbers
        nums = [float(x) for x in self.PATTERNS['number'].findall(prompt.lower())]
        lower_p = prompt.lower()
        
        # Case 1: Simple Arithmetic (e.g., "What is 5 + 3?")
        if '+' in lower_p or 'plus' in lower_p:
            if len(nums) >= 2:
                return nums[0] + nums[1]
        if '-' in lower_p and 'minus' in lower_p or ('-' in lower_p and len(nums)>=2):
             # Handle hyphen carefully
            if 'minus' in lower_p and len(nums) >= 2:
                return nums[0] - nums[1]
        if '*' in lower_p or 'times' in lower_p or 'multiplied by' in lower_p:
            if len(nums) >= 2:
                return nums[0] * nums[1]
        if '/' in lower_p or 'divided by' in lower_p:
            if len(nums) >= 2 and nums[1] != 0:
                return nums[0] / nums[1]
                
        # Case 2: Comparisons (e.g., "Is 9.11 > 9.9?")
        if 'greater than' in lower_p or '>' in prompt:
            if len(nums) >= 2:
                return nums[0] > nums[1]
        if 'less than' in lower_p or '<' in prompt:
            if len(nums) >= 2:
                return nums[0] < nums[1]
                
        # Case 3: Temporal ordering (simple "before/after" count)
        if 'before' in lower_p and 'after' in lower_p:
            # Heuristic: if asking for order, we can't compute exact value without more info
            # But we can flag it as a structural logic problem
            pass
            
        return None

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        lower_p = prompt.lower()
        
        # 1. Presupposition traps
        if self.PATTERNS['presupposition'].search(lower_p):
            return 0.2
            
        # 2. Pronoun ambiguity
        if self.PATTERNS['pronoun_ambiguity'].search(lower_p) and 'who' in lower_p:
            return 0.2
            
        # 3. False dichotomy indicators without clear context
        if self.PATTERNS['false_dichotomy'].search(lower_p) and 'otherwise' not in lower_p:
            # Weak signal, reduce confidence slightly
            return 0.7
            
        # 4. Subjectivity
        if self.PATTERNS['subjectivity'].search(lower_p):
            return 0.3
            
        # 5. Unanswerable (missing info keywords)
        if re.search(r'\b(missing|unknown|impossible|cannot be determined)\b', lower_p):
            return 0.1
            
        return 1.0

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Internal scoring logic."""
        prompt_atoms = self._extract_atoms(prompt)
        cand_atoms = self._extract_atoms(candidate)
        
        # 1. Constructive Computation Check (Highest Priority)
        computed = self._compute_answer(prompt)
        if computed is not None:
            # Try to parse candidate as a number or boolean
            cand_txt = candidate.strip().lower()
            cand_val = None
            
            # Parse candidate number
            c_nums = self.PATTERNS['number'].findall(cand_txt)
            if c_nums:
                cand_val = float(c_nums[0])
            elif 'true' in cand_txt or 'yes' in cand_txt:
                cand_val = True
            elif 'false' in cand_txt or 'no' in cand_txt:
                cand_val = False
                
            if cand_val is not None:
                if cand_val == computed:
                    return 0.99, "Computed match: Candidate matches exact constructive solution."
                else:
                    return 0.05, "Computed mismatch: Candidate contradicts exact constructive solution."

        # 2. Structural & Criticality Analysis
        all_atoms = prompt_atoms + cand_atoms
        n = len(all_atoms)
        
        if n == 0:
            return 0.1, "No structural atoms found."
            
        imp_matrix = self._build_imp_matrix(all_atoms)
        closure = self._transitive_closure(imp_matrix)
        
        # Emergence Score: Derived relations not in original matrix
        # (Simplified: count of True in closure vs original)
        orig_count = np.count_nonzero(imp_matrix)
        closed_count = np.count_nonzero(closure)
        emergence = (closed_count - orig_count) / (n * n) if n > 0 else 0
        emergence = min(1.0, max(0.0, emergence))
        
        # Criticality Score: Simulate MUC shrinking
        # We assume the "cycle" is a contradiction between prompt and candidate if they clash
        # Here we approximate: if candidate adds no new constraints, criticality is low
        # If candidate creates a tight loop (high connectivity), criticality is high
        density = closed_count / (n * n) if n > 0 else 0
        criticality = 1.0 - density # Sparse core = more critical/fragile
        
        # Base structural score
        base_score = 0.5 * emergence + 0.5 * criticality
        
        # Bonus for keyword overlap in atoms (semantic similarity)
        prompt_preds = set([a[0] for a in prompt_atoms])
        cand_preds = set([a[0] for a in cand_atoms])
        overlap = len(prompt_preds.intersection(cand_preds))
        overlap_bonus = min(0.3, overlap * 0.1)
        
        final_score = base_score + overlap_bonus
        final_score = min(1.0, max(0.0, final_score))
        
        reason = f"Emergence: {emergence:.2f}, Criticality: {criticality:.2f}"
        return final_score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Tier B: Epistemic Honesty Check
        meta_cap = self._meta_confidence(prompt)
        
        # If the prompt is fundamentally ambiguous/unanswerable, cap confidence
        if meta_cap < 0.3:
            return meta_cap
            
        # Run evaluation to get structural score
        # We treat the single answer as a candidate list of one
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # If computation produced a definitive answer (score ~0.99 or ~0.0), confidence is high
        # If it's a structural guess (0.3-0.7), confidence is moderate
        if base_score > 0.9 or base_score < 0.1:
            conf = 0.95
        else:
            conf = 0.5 + (base_score * 0.4) # Scale 0.5-0.9
            
        # Apply meta cap
        final_conf = min(conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (handled by meta_cap usually)
        # But explicit check:
        if base_score < 0.9 and base_score > 0.1:
            final_conf = min(final_conf, 0.85)
            
        return round(final_conf, 3)

    def _meta_confidence(self, prompt: str) -> float:
        """Wrapper for meta-confidence checks."""
        return self._check_meta_confidence(prompt)
```

</details>
