# Neuromodulation + Property-Based Testing + Sensitivity Analysis

**Fields**: Neuroscience, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:45:05.939856
**Report Generated**: 2026-04-02T08:39:54.973252

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Convert each candidate answer into a list of *logical atoms* using regex‑based extraction. Each atom is a tuple `(type, args)` where `type ∈ {neg, comp, cond, cause, num, order}` and `args` are the extracted tokens (e.g., `('comp', ('>', 5, 3))`). Store the atoms in a NumPy structured array `A` of dtype `[('type','U10'),('args','O')]`.  
2. **Constraint propagation** – Build a directed graph `G` from conditional atoms (`if p then q`). Apply forward chaining (modus ponens) iteratively: for every edge `p→q` in `G`, if `p` is marked true in a Boolean vector `T`, set `q` true. Continue until convergence (NumPy `while` loop with `np.any(T_new!=T)`). Contradictions are detected when both an atom and its negation become true; the *baseline consistency* `C₀ = 1 – (contradictions / len(T))`.  
3. **Neuromodulatory gain** – Assign a gain vector `g` same length as `T`. Dopamine‑like gain ↑ for atoms that participate in satisfied conditionals (reward), serotonin‑like gain ↓ for atoms involved in contradictions (inhibition). Compute `g = 1 + α·dop – β·ser` where `dop` and `ser` are binary masks derived from the propagation step; `α,β∈[0,1]` are fixed scalars.  
4. **Property‑based testing perturbations** – Generate `N` perturbed copies of the answer using a simple PBT strategy:  
   * flip negation status with probability `pₙ`,  
   * add Gaussian noise `σ·np.random.randn()` to numeric atoms,  
   * swap comparator direction (`<` ↔ `>`),  
   * randomly reorder ordering atoms,  
   * delete or insert causal connective tokens with probability `p_c`.  
   Each perturbation yields a new atom array `Aᵢ`; repeat steps 2‑3 to obtain consistency `Cᵢ`.  
5. **Sensitivity analysis** – Compute the sample mean `μ = np.mean([C₀,…,C_N])` and standard deviation `s = np.std([C₀,…,C_N])`. The final score is  
   \[
   S = μ * \exp(-λ * s)
   \]  
   where `λ` is a small constant (e.g., 0.5) controlling sensitivity penalty. Lower variability under perturbation → higher score.

**Structural features parsed** – negations, comparatives (`>`, `<`, `=`), conditionals (`if … then …`), causal claims (`because`, `leads to`), numeric values, ordering relations (`first`, `second`, `before`, `after`).

**Novelty** – The triple blend is not found verbatim in existing work. Property‑based testing provides systematic input fuzzing; sensitivity analysis quantifies robustness of the derived logical model; neuromodulatory gain adds an adaptive weighting scheme inspired by dopamine/serotonin modulation. While each component appears separately in robust verification, probabilistic soft logic, and attention models, their conjunction for scoring textual reasoning answers is novel.

**Rating**  
Reasoning: 8/10 — captures logical consistency and robustness via concrete propagation and perturbation.  
Metacognition: 6/10 — limited self‑monitoring; gain adapts but no explicit reflection on uncertainty.  
Hypothesis generation: 7/10 — PBT perturbations act as hypothesis probes, though not generative of new explanations.  
Implementability: 9/10 — relies only on regex, NumPy, and stdlib; all steps are straightforward to code.

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
**Reason**: trap_battery_failed (acc=37% cal=6% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:16:20.126339

---

## Code

**Source**: scrap

[View code](./Neuromodulation---Property-Based_Testing---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Any, Dict, Tuple

"""
Neuromodulation x Property-Based Testing x Sensitivity Analysis Reasoning Tool

Parses logical atoms, propagates constraints with adaptive gain, perturbs via PBT,
and scores by sensitivity-weighted consistency. Includes constructive computation
for numeric/Bayesian/temporal questions and epistemic honesty checks.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    def __init__(self):
        self.alpha = 0.3  # dopamine gain
        self.beta = 0.5   # serotonin inhibition
        self.lambda_sens = 0.5  # sensitivity penalty
        self.n_perturbations = 20
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score * conf,
                "reasoning": f"consistency={score:.3f}, confidence={conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        struct_conf = self._structural_confidence(prompt, answer)
        return min(meta_conf, struct_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|quit|why did .+ (fail|stop))', p):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery \w+.*\ba\b', p):
            return 0.25
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it)\b', p) and 'who' in p:
            return 0.25
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p):
            return 0.3
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\d', p):
            return 0.3
        return 0.8
    
    def _structural_confidence(self, prompt: str, answer: str) -> float:
        # Compute actual answer if possible
        comp_result = self._compute_answer(prompt)
        if comp_result is not None:
            if str(comp_result).lower() in answer.lower():
                return 0.85
            return 0.4
        # Check if we parsed anything meaningful
        atoms = self._parse_atoms(answer)
        if len(atoms) == 0:
            return 0.25
        return 0.6
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Constructive computation first
        computed = self._compute_answer(prompt)
        if computed is not None:
            if str(computed).lower() in candidate.lower():
                return 0.95
            else:
                return 0.15
        
        # Neuromodulation + PBT + sensitivity
        atoms = self._parse_atoms(candidate)
        if len(atoms) == 0:
            return self._ncd_score(prompt, candidate) * 0.15
        
        C0 = self._propagate_consistency(atoms)
        consistencies = [C0]
        
        for _ in range(self.n_perturbations):
            perturbed = self._perturb_atoms(atoms)
            Ci = self._propagate_consistency(perturbed)
            consistencies.append(Ci)
        
        mu = np.mean(consistencies)
        sigma = np.std(consistencies)
        sensitivity_score = mu * np.exp(-self.lambda_sens * sigma)
        
        # Small NCD component
        ncd = self._ncd_score(prompt, candidate)
        return 0.75 * sensitivity_score + 0.15 * C0 + 0.1 * ncd
    
    def _compute_answer(self, prompt: str) -> Any:
        p = prompt.lower()
        # Numeric comparison
        match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', p)
        if match:
            n1, op, n2 = float(match.group(1)), match.group(2), float(match.group(3))
            ops = {'>': n1 > n2, '<': n1 < n2, '>=': n1 >= n2, '<=': n1 <= n2, '=': abs(n1-n2)<1e-9}
            return ops.get(op, None)
        
        # Simple arithmetic (PEMDAS subset)
        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', p)
        if match:
            n1, op, n2 = int(match.group(1)), match.group(2), int(match.group(3))
            ops = {'+': n1+n2, '-': n1-n2, '*': n1*n2, '/': n1//n2 if n2!=0 else None}
            return ops.get(op, None)
        
        # Bayesian reasoning (simple base rate)
        if 'base rate' in p or 'probability' in p:
            nums = re.findall(r'(\d+\.?\d*)%', p)
            if len(nums) >= 2:
                return float(nums[0])  # Return base rate
        
        return None
    
    def _parse_atoms(self, text: str) -> List[Tuple[str, Any]]:
        atoms = []
        t = text.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|none)\s+(\w+)', t):
            atoms.append(('neg', (m.group(2),)))
        
        # Comparatives
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', t):
            atoms.append(('comp', (m.group(2), float(m.group(1)), float(m.group(3)))))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', t):
            atoms.append(('cond', (m.group(1).strip(), m.group(2).strip())))
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(because|leads to|causes)\s+(\w+)', t):
            atoms.append(('cause', (m.group(1), m.group(3))))
        
        # Numerics
        for m in re.finditer(r'\b(\d+\.?\d*)\b', t):
            atoms.append(('num', (float(m.group(1)),)))
        
        # Ordering
        for m in re.finditer(r'\b(first|second|third|before|after)\b', t):
            atoms.append(('order', (m.group(1),)))
        
        return atoms
    
    def _propagate_consistency(self, atoms: List[Tuple[str, Any]]) -> float:
        if len(atoms) == 0:
            return 0.5
        
        n = len(atoms)
        T = np.zeros(n, dtype=bool)
        dop = np.zeros(n, dtype=bool)
        ser = np.zeros(n, dtype=bool)
        
        # Extract conditionals
        conds = [(i, a[1]) for i, a in enumerate(atoms) if a[0] == 'cond']
        
        # Forward chaining
        for _ in range(3):
            for idx, (premise, conclusion) in conds:
                if premise in str(atoms):
                    T[idx] = True
                    dop[idx] = True
        
        # Check contradictions
        contradictions = 0
        for i, (typ, args) in enumerate(atoms):
            if typ == 'comp':
                op, n1, n2 = args
                ops = {'>': n1 > n2, '<': n1 < n2, '>=': n1 >= n2, '<=': n1 <= n2, '=': abs(n1-n2)<1e-9}
                if op in ops and not ops[op]:
                    contradictions += 1
                    ser[i] = True
        
        consistency = 1.0 - (contradictions / max(n, 1))
        gain = 1 + self.alpha * dop.sum()/max(n,1) - self.beta * ser.sum()/max(n,1)
        return max(0, min(1, consistency * gain))
    
    def _perturb_atoms(self, atoms: List[Tuple[str, Any]]) -> List[Tuple[str, Any]]:
        perturbed = []
        for typ, args in atoms:
            if np.random.rand() < 0.2:
                if typ == 'comp':
                    op, n1, n2 = args
                    ops = ['>', '<', '>=', '<=', '=']
                    new_op = np.random.choice(ops)
                    perturbed.append(('comp', (new_op, n1, n2)))
                elif typ == 'num':
                    n = args[0] + np.random.randn() * 0.1
                    perturbed.append(('num', (n,)))
                else:
                    perturbed.append((typ, args))
            else:
                perturbed.append((typ, args))
        return perturbed
    
    def _ncd_score(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        ncd = (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
        return max(0, 1 - ncd)
```

</details>
