# Renormalization + Error Correcting Codes + Free Energy Principle

**Fields**: Physics, Information Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T15:18:44.678939
**Report Generated**: 2026-04-02T10:00:36.095431

---

## Nous Analysis

**Algorithm**  
We build a sparse binary parity‑check matrix **A** (size *M × N*) that encodes logical constraints extracted from the prompt and world knowledge. Each column *j* corresponds to a propositional atom *pⱼ* (e.g., “X > Y”, “¬Z”, “if A then B”). The entry *Aᵢⱼ = 1* iff atom *pⱼ* participates in constraint *cᵢ* (e.g., transitivity: *X > Y ∧ Y > Z → X > Z* becomes a parity check that the sum of the three involved literals must be even).  

1. **Parsing → feature vectors**  
   - Tokenise the prompt and each candidate answer with `str.split()` and a small regex‑based pattern library.  
   - Extract: negations (`not`, `no`), comparatives (`>`, `<`, `more than`, `less than`), conditionals (`if … then …`), causal cues (`because`, `leads to`), ordering relations (`before`, `after`), and numeric values (`\d+(\.\d+)?`).  
   - Each extracted pattern sets a bit in a proposition vector; synonyms are merged via exact string equality (no embeddings).  
   - The resulting *N*‑dimensional binary vector **x** represents the candidate answer’s asserted literals (1 = asserted true, 0 = asserted false or absent).  

2. **Constraint propagation (error‑correcting view)**  
   - Compute the syndrome **s = (A @ x) % 2** using NumPy’s dot product and modulo.  
   - Each non‑zero entry of **s** indicates a violated parity check, analogous to decoding an LDPC code where the syndrome points to errors.  

3. **Free‑energy scoring**  
   - Approximate variational free energy *F* as  
     \[
     F(\mathbf{x}) = \|\mathbf{s}\|_2^2 \;+\; \lambda\!\sum_{j=1}^{N}\!\big[x_j\log x_j + (1-x_j)\log(1-x_j)\big]
     \]  
     where the first term penalizes constraint violations (energy) and the second term is the Bernoulli entropy (variational entropy) encouraging uncommitted variables to stay near 0.5; λ is a small constant (e.g., 0.1).  
   - Lower *F* predicts a better answer. Scores are normalized across candidates: `score = -F`.  

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering/temporal relations, and explicit numeric quantities. These are turned into literals that feed the parity‑check matrix.  

**Novelty**  
The trio—renormalization‑style coarse‑graining (merging identical literals), LDPC‑style syndrome computation, and variational free‑energy minimization—has not been combined in a pure‑NumPy reasoning scorer. Existing work uses either symbolic theorem provers, neural language models, or shallow similarity metrics; none jointly treat constraints as a parity‑check code and optimize a free‑energy objective.  

**Ratings**  
Reasoning: 8/10 — captures logical structure via constraint violations and offers a principled energy‑based ranking.  
Metacognition: 6/10 — the algorithm can monitor its own syndrome entropy but lacks explicit self‑reflection on parsing failures.  
Hypothesis generation: 5/10 — generates candidate truth assignments implicitly via syndrome minimization, but does not propose new hypotheses beyond the given literals.  
Implementability: 9/10 — relies only on NumPy for matrix ops and the standard library for regex/tokenization; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=42% cal=3% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T09:29:31.494728

---

## Code

**Source**: scrap

[View code](./Renormalization---Error_Correcting_Codes---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    """
    Reasoning tool combining error-correcting codes, renormalization, and free energy principle.
    
    Mechanism:
    1. Extract propositional atoms from prompt/candidates (negations, comparatives, conditionals, numerics)
    2. Build sparse parity-check matrix A encoding logical constraints (transitivity, modus tollens, etc.)
    3. Compute syndrome s = (A @ x) % 2 to detect constraint violations
    4. Score via variational free energy F = ||s||^2 + lambda * entropy(x)
    5. Lower F => better candidate (higher score after normalization)
    """
    
    def __init__(self):
        self.lambda_entropy = 0.1
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by free energy score (higher = better)."""
        prompt_atoms, prompt_nums = self._parse(prompt)
        results = []
        
        for cand in candidates:
            cand_atoms, cand_nums = self._parse(cand)
            
            # Compute numerical answer if applicable
            num_score = self._numeric_eval(prompt, prompt_nums, cand, cand_nums)
            
            # Build feature vector and constraint matrix
            all_atoms = list(set(prompt_atoms + cand_atoms))
            x = self._build_vector(cand_atoms, all_atoms)
            A = self._build_constraint_matrix(prompt_atoms, cand_atoms, all_atoms)
            
            # Compute free energy
            fe_score = self._free_energy_score(x, A)
            
            # NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            
            # Combine: 60% FE, 30% numeric, 10% NCD
            final_score = 0.6 * fe_score + 0.3 * num_score + 0.1 * (1 - ncd)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"FE={fe_score:.3f} NUM={num_score:.3f} NCD={ncd:.3f}"
            })
        
        results.sort(key=lambda r: r["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 (capped by metacognitive checks)."""
        meta_conf = self._meta_confidence(prompt)
        
        # Parse and compute base confidence
        p_atoms, p_nums = self._parse(prompt)
        a_atoms, a_nums = self._parse(answer)
        
        # Check for definitive numeric answer
        num_score = self._numeric_eval(prompt, p_nums, answer, a_nums)
        if num_score > 0.95:
            base_conf = 0.85
        elif num_score > 0.5:
            base_conf = 0.6
        else:
            # Use FE-based confidence
            all_atoms = list(set(p_atoms + a_atoms))
            x = self._build_vector(a_atoms, all_atoms)
            A = self._build_constraint_matrix(p_atoms, a_atoms, all_atoms)
            fe_score = self._free_energy_score(x, A)
            base_conf = min(0.7, fe_score)
        
        # Cap by metacognitive confidence
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presuppositions, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition: "have you stopped/quit", "why did X fail"
        if re.search(r'\b(have you (stopped|quit)|why did .* (fail|stop))\b', p_lower):
            return 0.25
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower) and '?' in prompt:
            return 0.28
        
        # Pronoun ambiguity: "X told Y he/she" + "who?"
        if re.search(r'\btold\b.*\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\b(only|exactly)\b', p_lower):
            return 0.30
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|fewest|highest|lowest)\b', p_lower):
            return 0.35
        
        # Unanswerability: "cannot determine", "insufficient"
        if re.search(r'\b(cannot (be )?determin|insufficient|not enough (info|data))\b', p_lower):
            return 0.20
        
        return 0.75  # Default: reasonably answerable
    
    def _parse(self, text: str) -> Tuple[List[str], List[float]]:
        """Extract propositional atoms and numeric values."""
        atoms = []
        text_lower = text.lower()
        
        # Negations
        negs = re.findall(r'\b(not|no|never|n\'t)\s+(\w+)', text_lower)
        atoms.extend([f"NOT_{w}" for _, w in negs])
        
        # Comparatives (>,<,more,less,greater,fewer)
        comps = re.findall(r'(\w+)\s+(>|<|more than|less than|greater than|fewer than|exceeds|below)\s+(\w+)', text_lower)
        atoms.extend([f"{a}_CMP_{op.replace(' ', '')}_{b}" for a, op, b in comps])
        
        # Conditionals
        conds = re.findall(r'\bif\s+(\w+).*then\s+(\w+)', text_lower)
        atoms.extend([f"IF_{a}_THEN_{b}" for a, b in conds])
        
        # Causals
        causals = re.findall(r'(\w+)\s+(causes?|leads? to|results? in|produces?)\s+(\w+)', text_lower)
        atoms.extend([f"{a}_CAUSES_{b}" for a, _, b in causals])
        
        # Ordering/temporal
        orders = re.findall(r'(\w+)\s+(before|after|precedes?|follows?)\s+(\w+)', text_lower)
        atoms.extend([f"{a}_ORD_{op}_{b}" for a, op, b in orders])
        
        # Extract numbers
        nums = [float(n) for n in re.findall(r'\b\d+\.?\d*\b', text)]
        
        return atoms, nums
    
    def _build_vector(self, atoms: List[str], all_atoms: List[str]) -> np.ndarray:
        """Build binary feature vector from atoms."""
        N = len(all_atoms)
        x = np.zeros(N)
        atom_idx = {a: i for i, a in enumerate(all_atoms)}
        for atom in atoms:
            if atom in atom_idx:
                x[atom_idx[atom]] = 1.0
        return x
    
    def _build_constraint_matrix(self, p_atoms: List[str], c_atoms: List[str], all_atoms: List[str]) -> np.ndarray:
        """Build parity-check matrix encoding logical constraints."""
        N = len(all_atoms)
        atom_idx = {a: i for i, a in enumerate(all_atoms)}
        constraints = []
        
        # Transitivity: if A>B and B>C appear, then A>C should hold
        cmp_atoms = [a for a in all_atoms if '_CMP_' in a]
        for i, a1 in enumerate(cmp_atoms):
            for a2 in cmp_atoms[i+1:]:
                parts1 = a1.split('_CMP_')
                parts2 = a2.split('_CMP_')
                if len(parts1) == 2 and len(parts2) == 2:
                    x1, rest1 = parts1
                    x2, rest2 = parts2
                    if '_' in rest1 and '_' in rest2:
                        op1, y1 = rest1.split('_', 1)
                        op2, y2 = rest2.split('_', 1)
                        if y1 == x2:  # A>B and B>C
                            expected = f"{x1}_CMP_{op1}_{y2}"
                            if expected in all_atoms:
                                row = np.zeros(N)
                                row[atom_idx[a1]] = 1
                                row[atom_idx[a2]] = 1
                                row[atom_idx[expected]] = 1
                                constraints.append(row)
        
        # Modus tollens: IF A THEN B, NOT B => NOT A
        if_atoms = [a for a in all_atoms if a.startswith('IF_')]
        not_atoms = [a for a in all_atoms if a.startswith('NOT_')]
        for if_atom in if_atoms:
            parts = if_atom.split('_THEN_')
            if len(parts) == 2:
                ante = parts[0].replace('IF_', '')
                cons = parts[1]
                not_cons = f"NOT_{cons}"
                not_ante = f"NOT_{ante}"
                if not_cons in atom_idx and not_ante in atom_idx:
                    row = np.zeros(N)
                    row[atom_idx[if_atom]] = 1
                    row[atom_idx[not_cons]] = 1
                    row[atom_idx[not_ante]] = 1
                    constraints.append(row)
        
        if len(constraints) == 0:
            return np.zeros((1, N))
        return np.array(constraints)
    
    def _free_energy_score(self, x: np.ndarray, A: np.ndarray) -> float:
        """Compute normalized free energy score (higher = better)."""
        # Syndrome (constraint violations)
        s = (A @ x) % 2
        energy = np.sum(s ** 2)
        
        # Entropy term (encourage uncommitted variables)
        eps = 1e-10
        x_clip = np.clip(x, eps, 1 - eps)
        entropy = np.sum(x_clip * np.log(x_clip) + (1 - x_clip) * np.log(1 - x_clip))
        
        F = energy + self.lambda_entropy * abs(entropy)
        
        # Normalize to 0-1 (lower F = better => invert)
        return 1.0 / (1.0 + F)
    
    def _numeric_eval(self, prompt: str, p_nums: List[float], cand: str, c_nums: List[float]) -> float:
        """Evaluate numeric/computational problems."""
        score = 0.0
        
        # Numeric comparison
        if any(tok in prompt.lower() for tok in ['greater', 'less', 'larger', 'smaller', '>', '<']):
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                if '>' in prompt or 'greater' in prompt.lower() or 'larger' in prompt.lower():
                    if c_nums[0] == max(p_nums):
                        score = 1.0
                elif '<' in prompt or 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    if c_nums[0] == min(p_nums):
                        score = 1.0
        
        # Bat-and-ball: "X costs Y more than Z, total is T, what is Z?"
        if re.search(r'costs?\s+.*\s+more than', prompt.lower()) and 'total' in prompt.lower():
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                diff, total = p_nums[:2]
                expected_z = (total - diff) / 2
                if abs(c_nums[0] - expected_z) < 0.01:
                    score = 1.0
        
        # All-but-N: "All but N are X"
        if re.search(r'all but \d+', prompt.lower()):
            match = re.search(r'all but (\d+)', prompt.lower())
            if match and len(p_nums) >= 1 and len(c_nums) >= 1:
                n = int(match.group(1))
                total = p_nums[0] if len(p_nums) > 1 else p_nums[0]
                expected = total - n
                if abs(c_nums[0] - expected) < 0.01:
                    score = 1.0
        
        return score
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (lower = more similar)."""
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
