# Sparse Coding + Compositional Semantics + Satisfiability

**Fields**: Neuroscience, Philosophy, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T21:04:17.804604
**Report Generated**: 2026-04-02T11:44:49.666921

---

## Nous Analysis

**Algorithm**  
1. **Parsing & grounding** – Using only regex and the Python `re` module we extract atomic propositions from the prompt and each candidate answer:  
   - Predicates (`is‑larger(X,Y)`, `equals(Z,5)`, `causes(A,B)`)  
   - Literals with polarity (¬ for negation)  
   - Numeric constraints (`value > 3`, `value ≤ ‑2`) are turned into propositional atoms via threshold encoding (e.g., `gt_3`).  
   The output is a list of literals `L = [l₁,…,lₙ]`.  

2. **Sparse coding layer** – Each literal is assigned a binary variable `xᵢ ∈ {0,1}` indicating whether it is asserted true in the candidate. We enforce sparsity by adding an L₀‑penalty term `λ‖x‖₀` (implemented as `λ * np.sum(x)`) to the energy; λ is set so that only a few literals may be active (typically ≤ 3).  

3. **Compositional semantics → clause matrix** – From the parsed structure we build a set of Horn‑style clauses that capture the meaning of the prompt:  
   - Modus ponens: `(p ∧ q) → r` becomes clause `¬p ∨ ¬q ∨ r`  
   - Transitivity of ordering: `a<b ∧ b<c → a<c`  
   - Causality: `causes(a,b)` → `a → b`  
   Each clause is stored as a row in a sparse boolean matrix `C ∈ {0,1}^{m×n}` where a `1` means the literal appears positively, a `-1` (encoded as separate matrix `Cneg`) means it appears negated.  

4. **Satisfiability scoring** – For a candidate answer vector `x`, clause violation is computed as:  
   ```
   violated = np.any(C @ x == 0, axis=0)   # clause unsatisfied if all literals false
   energy   = np.sum(violated) + λ * np.sum(x)
   ```  
   Lower energy = higher score. The SAT core idea is that a satisfying assignment yields zero violated clauses; sparsity pushes the solution toward the most compact explanation.  

**Structural features parsed**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `≥`, `≤`)  
- Conditionals (`if … then …`, `unless`)  
- Numeric values and thresholds  
- Causal claims (`causes`, `leads to`)  
- Ordering / transitive relations (`before`, `after`, `older than`)  

**Novelty**  
The trio mirrors neuro‑symbolic hybrids (e.g., Probabilistic Soft Logic, DeepSAT) but the concrete pipeline — regex grounding → binary sparse vector → explicit clause matrix → energy = violations + L₀ penalty — is not described in existing open‑source tools. It combines sparse coding’s energy‑based selection with compositional clause generation and pure SAT checking, a combination absent from current literature.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and sparsity, but limited to propositional Horn fragments.  
Metacognition: 6/10 — can detect over‑/under‑specification via energy, yet lacks self‑reflective revision loops.  
Hypothesis generation: 7/10 — sparse activation yields compact explanatory sets, useful for abductive guesses.  
Implementability: 9/10 — relies only on `numpy` and `re`; clause matrix and vector ops are straightforward.

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
**Reason**: validation:syntax_error: invalid syntax (line 200)

**Forge Timestamp**: 2026-04-02T11:20:19.383471

---

## Code

**Source**: scrap

[View code](./Sparse_Coding---Compositional_Semantics---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib

class ReasoningTool:
    """
    Sparse Coding x Compositional Semantics x Satisfiability
    
    Parses prompt/candidates into atomic propositions, builds Horn clauses,
    computes energy = SAT violations + L0 sparsity penalty.
    Lower energy = higher score.
    """
    
    def __init__(self):
        self.lambda_sparse = 0.3  # L0 penalty weight
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Parse prompt into literals and clauses
        prompt_literals, prompt_clauses = self._parse(prompt)
        
        for cand in candidates:
            cand_literals, _ = self._parse(cand)
            
            # Compute structural score via SAT + sparsity
            struct_score = self._sat_score(prompt_literals, prompt_clauses, cand_literals)
            
            # Compute numeric/arithmetic score
            comp_score = self._computation_score(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination: structural 55%, computation 30%, NCD 15%
            total_score = 0.55 * struct_score + 0.30 * comp_score + 0.15 * ncd_score
            
            reasoning = f"SAT:{struct_score:.2f} Comp:{comp_score:.2f} NCD:{ncd_score:.2f}"
            results.append({"candidate": cand, "score": total_score, "reasoning": reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        
        # Parse and score
        p_lits, p_clauses = self._parse(prompt)
        a_lits, _ = self._parse(answer)
        
        sat_score = self._sat_score(p_lits, p_clauses, a_lits)
        comp_score = self._computation_score(prompt, answer)
        
        # Combine scores but cap by meta-confidence
        base_conf = 0.6 * sat_score + 0.4 * comp_score
        
        # Never exceed 0.9 unless perfect computation match
        if comp_score < 1.0:
            base_conf = min(base_conf, 0.85)
        
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.25
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.28
        
        # Pronoun ambiguity followed by "who" question
        if re.search(r'\b(he|she)\b', p_lower) and 'who' in p_lower:
            return 0.27
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\b.*\bor\b', p_lower):
            return 0.30
        
        # Subjectivity without measurable criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and not re.search(r'\d', p_lower):
            return 0.35
        
        # Unanswerability markers
        if re.search(r'\b(impossible to know|not enough information|cannot determine)\b', p_lower):
            return 0.20
        
        return 1.0  # No meta issues detected
    
    def _parse(self, text: str):
        literals = set()
        clauses = []
        
        text_lower = text.lower()
        
        # Extract negations
        for match in re.finditer(r'\b(not|no)\s+(\w+)', text_lower):
            literals.add(f"NOT_{match.group(2)}")
        
        # Extract comparatives
        for match in re.finditer(r'(\w+)\s+(greater than|larger than|more than|>)\s+(\w+)', text_lower):
            lit = f"GT_{match.group(1)}_{match.group(3)}"
            literals.add(lit)
            
        for match in re.finditer(r'(\w+)\s+(less than|smaller than|fewer than|<)\s+(\w+)', text_lower):
            lit = f"LT_{match.group(1)}_{match.group(3)}"
            literals.add(lit)
        
        # Extract conditionals (if-then)
        for match in re.finditer(r'if\s+(\w+)\s+then\s+(\w+)', text_lower):
            antecedent = match.group(1)
            consequent = match.group(2)
            literals.add(antecedent)
            literals.add(consequent)
            # Clause: NOT antecedent OR consequent
            clauses.append((f"NOT_{antecedent}", consequent))
        
        # Extract causal relations
        for match in re.finditer(r'(\w+)\s+(causes|leads to)\s+(\w+)', text_lower):
            cause = match.group(1)
            effect = match.group(3)
            literals.add(cause)
            literals.add(effect)
            clauses.append((f"NOT_{cause}", effect))
        
        # Extract numeric values
        for match in re.finditer(r'(\d+\.?\d*)', text):
            literals.add(f"NUM_{match.group(1)}")
        
        # Extract simple predicates (words)
        words = re.findall(r'\b[a-z]+\b', text_lower)
        for w in words[:10]:  # Limit to avoid explosion
            if len(w) > 2:
                literals.add(w)
        
        return list(literals), clauses
    
    def _sat_score(self, prompt_lits, prompt_clauses, cand_lits):
        if not prompt_lits:
            return 0.5
        
        # Binary vector for candidate literals
        all_lits = list(set(prompt_lits + cand_lits))
        n = len(all_lits)
        x = np.zeros(n)
        
        for i, lit in enumerate(all_lits):
            if lit in cand_lits:
                x[i] = 1
        
        # Count clause violations
        violations = 0
        for clause in prompt_clauses:
            # Clause is (lit1, lit2) representing (NOT lit1 OR lit2)
            # Violated if lit1 is true AND lit2 is false
            lit1_idx = all_lits.index(clause[0]) if clause[0] in all_lits else -1
            lit2_idx = all_lits.index(clause[1]) if clause[1] in all_lits else -1
            
            if lit1_idx >= 0 and lit2_idx >= 0:
                if x[lit1_idx] == 1 and x[lit2_idx] == 0:
                    violations += 1
        
        # Sparsity penalty
        sparsity = np.sum(x)
        
        # Energy = violations + lambda * sparsity
        energy = violations + self.lambda_sparse * sparsity
        
        # Normalize to [0, 1], lower energy = higher score
        max_energy = len(prompt_clauses) + self.lambda_sparse * n
        if max_energy == 0:
            return 0.5
        
        score = 1.0 - min(energy / max_energy, 1.0)
        return max(score, 0.0)
    
    def _computation_score(self, prompt: str, candidate: str):
        score = 0.0
        
        # Numeric comparison
        num_match = re.search(r'(\d+\.?\d*)\s*(<?|>?)\s*(\d+\.?\d*)', prompt)
        if num_match:
            a, op, b = float(num_match.group(1)), num_match.group(2), float(num_match.group(3))
            cand_lower = candidate.lower()
            
            if '<' in op and a < b:
                if any(w in cand_lower for w in ['yes', 'true', 'correct', 'less', 'smaller']):
                    score += 0.5
            elif '>' in op and a > b:
                if any(w in cand_lower for w in ['yes', 'true', 'correct', 'greater', 'larger']):
                    score += 0.5
        
        # Arithmetic expression evaluation
        expr_match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)', prompt)
        if expr_match:
            a, op, b = int(expr_match.group(1)), expr_match.group(2), int(expr_match.group(3))
            result = {'+'|: a+b, '-': a-b, '*': a*b, '/': a//b if b != 0 else 0}.get(op, 0)
            
            if str(result) in candidate:
                score += 0.5
        
        # Boolean logic
        if re.search(r'\b(and|both)\b', prompt.lower()):
            if 'true' in candidate.lower() or 'yes' in candidate.lower():
                score += 0.2
        
        if re.search(r'\b(or|either)\b', prompt.lower()):
            if 'true' in candidate.lower() or 'yes' in candidate.lower():
                score += 0.2
        
        return min(score, 1.0)
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        
        numerator = len(c12) - min(len(c1), len(c2))
        denominator = max(len(c1), len(c2))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
```

</details>
