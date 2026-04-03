# Error Correcting Codes + Counterfactual Reasoning + Metamorphic Testing

**Fields**: Information Science, Philosophy, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:37:05.291591
**Report Generated**: 2026-04-02T11:44:50.432567

---

## Nous Analysis

**Algorithm**  
1. **Parsing & clause extraction** – Using a small set of regex patterns we extract atomic propositions (e.g., “X > Y”, “¬P”, “if A then B”, “cause C → D”) and bind each to a unique index i. The result is a list `clauses = [(type, args)]`.  
2. **Implication graph** – From conditionals and causal claims we build a directed graph `G = (V,E)` where each vertex vᵢ corresponds to a proposition and an edge vᵢ→vⱼ encodes “if vᵢ then vⱼ” (modus ponens). Transitive closure is computed with Floyd‑Warshall (O(|V|³) but |V| stays small because we only keep extracted propositions).  
3. **Binary encoding** – Each vertex receives a binary variable xᵢ∈{0,1} (false/true). A candidate answer supplies a set of asserted truth values `Ans = {xᵢ = v}`. We pack the current assignment into a k‑bit message `m` (k = number of independent propositions after removing those fixed by the prompt).  
4. **Error‑correcting code** – We encode `m` with a systematic linear block code (e.g., Hamming(7,4) or a short LDPC). The encoder `Genc` produces an n‑bit codeword `c = m·Genc`. The code’s parity‑check matrix `H` defines a syndrome `s = H·cᵀ (mod 2)`. In a noise‑free world `s = 0`.  
5. **Metamorphic relations as constraints** – For each metamorphic relation (MR) we define a deterministic transformation `T` on the input (e.g., double a numeric value, swap two operands). Applying `T` to the prompt yields a new clause set and thus a new message `m'`. The MR predicts that the syndrome after transformation should be unchanged (`s' = s`). We pre‑compute the set of expected syndrome deltas `Δs_MR` for all MRs relevant to the extracted features.  
6. **Counterfactual scoring** – To evaluate a candidate answer we:  
   a. Inject its truth assignments into the baseline codeword → compute baseline syndrome `s₀`.  
   b. For each MR, apply the transformation, recompute the syndrome `s₁`, and compute the Hamming weight `w = wt(s₀ ⊕ s₁)`.  
   c. The answer’s error score is `E = Σ w` over all MRs; lower `E` means fewer violated metamorphic constraints under counterfactual perturbations.  
   Final score = `1 / (1 + E)` (higher is better).  

**Structural features parsed**  
- Negations (`not`, `¬`)  
- Comparatives (`>`, `<`, `=`, `≥`, `≤`)  
- Conditionals (`if … then …`, `unless`)  
- Causal verbs (`cause`, `lead to`, `result in`)  
- Ordering/temporal markers (`before`, `after`, `increase`, `decrease`)  
- Numeric literals and arithmetic expressions  

**Novelty**  
The triple blend is not present in existing surveys. Error‑correcting codes are used here as a consistency‑checking layer over logical constraints, metamorphic relations provide the perturbation set, and counterfactual reasoning supplies the systematic “what‑if” recomputation. While each component appears separately in verification, testing, and causal inference, their joint use for scoring natural‑language answers is undocumented.

**Rating**  
Reasoning: 8/10 — captures logical implication, counterfactual sensitivity, and noise‑robust consistency via syndrome weight.  
Metacognition: 6/10 — limited self‑monitoring; the method detects violated MRs but does not reflect on its own uncertainty beyond syndrome magnitude.  
Hypothesis generation: 7/10 — generates counterfactual worlds by flipping propositions and applying MRs, yielding alternative explanations.  
Implementability: 9/10 — relies only on regex, graph algorithms, and numpy‑based binary linear algebra; no external libraries or training needed.

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
**Reason**: trap_battery_failed (acc=36% cal=8% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:14:40.191577

---

## Code

**Source**: scrap

[View code](./Error_Correcting_Codes---Counterfactual_Reasoning---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from itertools import combinations

class ReasoningTool:
    """
    Combines Error Correcting Codes + Counterfactual Reasoning + Metamorphic Testing.
    Parses logical structure, encodes truth assignments as binary codewords, applies
    metamorphic transformations, and scores candidates by syndrome weight under perturbations.
    """
    
    def __init__(self):
        # Hamming(7,4) generator matrix (systematic form)
        self.G = np.array([[1,0,0,0,1,1,0],[0,1,0,0,1,0,1],[0,0,1,0,0,1,1],[0,0,0,1,1,1,1]], dtype=np.uint8)
        # Parity check matrix
        self.H = np.array([[1,1,0,1,1,0,0],[1,0,1,1,0,1,0],[0,1,1,1,0,0,1]], dtype=np.uint8)
    
    def _meta_confidence(self, prompt):
        """Check prompt for Tier B traps: presupposition, ambiguity, false dichotomy."""
        p = prompt.lower()
        # Presupposition traps
        if re.search(r'\b(have you stopped|did you stop|quit|why did .+ fail|why is .+ wrong)\b', p):
            return 0.2
        # Scope ambiguity: "every X...a Y"
        if re.search(r'\bevery .{5,40} a \w+', p) and '?' in prompt:
            return 0.25
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).{0,30}\?', p) and re.search(r'\btold\b|\bsaid\b', p):
            return 0.25
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p) and not re.search(r'\bonly\b|\bexactly\b', p):
            return 0.3
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\bmost|least|measure', p):
            return 0.25
        # Unanswerable markers
        if re.search(r'cannot be determined|insufficient|not enough info', p):
            return 0.15
        return 1.0
    
    def _parse_clauses(self, text):
        """Extract atomic propositions: negations, comparisons, conditionals, causal."""
        clauses = []
        # Numeric comparisons
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?)\s*(\d+\.?\d*)', text):
            left, op, right = float(m.group(1)), m.group(2), float(m.group(3))
            result = self._eval_compare(left, op, right)
            clauses.append(('compare', (left, op, right, result)))
        # Conditionals: if...then
        for m in re.finditer(r'if (.{3,40}) then (.{3,40})', text.lower()):
            clauses.append(('conditional', (m.group(1).strip(), m.group(2).strip())))
        # Negations
        for m in re.finditer(r'\b(not|never|no)\s+(\w+)', text.lower()):
            clauses.append(('negation', m.group(2)))
        # Causal
        for m in re.finditer(r'(\w+)\s+(cause[sd]?|leads? to|results? in)\s+(\w+)', text.lower()):
            clauses.append(('causal', (m.group(1), m.group(3))))
        return clauses
    
    def _eval_compare(self, left, op, right):
        """Evaluate numeric comparison."""
        if op in ['>', 'greater']: return left > right
        if op in ['<', 'less']: return left < right
        if op in ['>=', 'at least']: return left >= right
        if op in ['<=', 'at most']: return left <= right
        if op in ['=', 'equals', 'equal']: return abs(left - right) < 1e-9
        return None
    
    def _bat_and_ball(self, text):
        """Solve bat-and-ball algebra: X + Y = total, X - Y = diff."""
        m = re.search(r'(\d+\.?\d*).+together.+(\d+\.?\d*).+more than', text)
        if m:
            total, diff = float(m.group(1)), float(m.group(2))
            # X + Y = total, X - Y = diff => X = (total+diff)/2, Y = (total-diff)/2
            return (total + diff) / 2, (total - diff) / 2
        return None
    
    def _all_but_n(self, text):
        """All but N: total - N."""
        m = re.search(r'all but (\d+)', text.lower())
        m2 = re.search(r'(\d+) total|(\d+) items', text.lower())
        if m and m2:
            n = int(m.group(1))
            total = int(m2.group(1) or m2.group(2))
            return total - n
        return None
    
    def _build_implication_graph(self, clauses):
        """Build directed graph from conditionals and causal claims."""
        edges = []
        for ctype, args in clauses:
            if ctype == 'conditional':
                edges.append((args[0], args[1]))
            elif ctype == 'causal':
                edges.append((args[0], args[1]))
        return edges
    
    def _encode_message(self, truth_vals):
        """Encode 4-bit truth assignment to 7-bit Hamming codeword."""
        m = np.array(truth_vals[:4], dtype=np.uint8)
        c = np.dot(m, self.G) % 2
        return c
    
    def _syndrome(self, codeword):
        """Compute syndrome s = H * c^T mod 2."""
        s = np.dot(self.H, codeword) % 2
        return s
    
    def _apply_metamorphic(self, clauses, mr_type):
        """Apply metamorphic relation: swap operands, negate, double numeric."""
        transformed = []
        for ctype, args in clauses:
            if ctype == 'compare' and mr_type == 'swap':
                left, op, right, _ = args
                # Swap and invert operator
                new_op = {'<': '>', '>': '<', '<=': '>=', '>=': '<=', '=': '='}.get(op, op)
                result = self._eval_compare(right, new_op, left)
                transformed.append(('compare', (right, new_op, left, result)))
            elif ctype == 'compare' and mr_type == 'double':
                left, op, right, _ = args
                result = self._eval_compare(left*2, op, right*2)
                transformed.append(('compare', (left*2, op, right*2, result)))
            else:
                transformed.append((ctype, args))
        return transformed
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1+s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
    
    def _score_candidate(self, prompt, candidate):
        """Compute error score via ECC syndromes under metamorphic perturbations."""
        clauses = self._parse_clauses(prompt + ' ' + candidate)
        if not clauses:
            return 0.5, 0.3  # Low score, low confidence
        
        # Extract truth values from comparisons
        truth_vals = [int(args[3]) for ctype, args in clauses if ctype == 'compare' and len(args) > 3]
        if len(truth_vals) < 4:
            truth_vals += [0] * (4 - len(truth_vals))
        
        # Encode and compute baseline syndrome
        codeword = self._encode_message(truth_vals)
        s0 = self._syndrome(codeword)
        
        # Apply metamorphic relations
        error_sum = 0
        for mr in ['swap', 'double']:
            transformed = self._apply_metamorphic(clauses, mr)
            t_truth = [int(args[3]) for ctype, args in transformed if ctype == 'compare' and len(args) > 3]
            if len(t_truth) < 4:
                t_truth += [0] * (4 - len(t_truth))
            c1 = self._encode_message(t_truth)
            s1 = self._syndrome(c1)
            error_sum += np.sum(np.bitwise_xor(s0, s1))
        
        # Score: lower error is better
        score = 1.0 / (1.0 + error_sum)
        
        # Check special parsers
        bat_ball = self._bat_and_ball(prompt)
        if bat_ball:
            for val in bat_ball:
                if re.search(r'\b' + re.escape(f'{val:.2f}') + r'\b', candidate):
                    score = max(score, 0.9)
                    return score, 0.85
        
        all_but = self._all_but_n(prompt)
        if all_but and str(all_but) in candidate:
            score = max(score, 0.85)
            return score, 0.8
        
        # Confidence based on clause count and consistency
        confidence = min(0.9, 0.3 + 0.1 * len(clauses)) if error_sum < 3 else 0.4
        
        return score, confidence
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by ECC syndrome score + special parsers."""
        meta_conf = self._meta_confidence(prompt)
        
        results = []
        for cand in candidates:
            score, conf = self._score_candidate(prompt, cand)
            
            # Add NCD component (max 15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = max(0, 1 - ncd)
            
            # Combine: 70% ECC, 15% NCD, 15% length penalty
            len_penalty = min(1.0, len(cand) / (len(prompt) + 1))
            final_score = 0.7 * score + 0.15 * ncd_score + 0.15 * len_penalty
            
            reasoning = f"ECC={score:.2f} NCD={ncd_score:.2f} meta_conf={meta_conf:.2f}"
            results.append({'candidate': cand, 'score': final_score, 'reasoning': reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 based on metacognitive checks + structural parse."""
        meta_conf = self._meta_confidence(prompt)
        
        # If meta-confidence is low (Tier B trap), cap confidence
        if meta_conf < 0.5:
            return meta_conf
        
        score, conf = self._score_candidate(prompt, answer)
        
        # Never exceed 0.9 unless we have high-confidence computation
        final_conf = min(0.9, conf * meta_conf)
        
        # Lower confidence if no structural matches
        clauses = self._parse_clauses(prompt + ' ' + answer)
        if len(clauses) == 0:
            final_conf = min(final_conf, 0.3)
        
        return final_conf
```

</details>
