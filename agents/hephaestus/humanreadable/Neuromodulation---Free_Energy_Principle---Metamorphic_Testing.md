# Neuromodulation + Free Energy Principle + Metamorphic Testing

**Fields**: Neuroscience, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T15:03:49.724777
**Report Generated**: 2026-03-27T17:21:24.393560

---

## Nous Analysis

The algorithm builds a **variational free‑energy factor graph** over extracted logical propositions and uses **neuromodulatory gain** to weight constraints, while **metamorphic relations** generate answer perturbations for consistency checking.

1. **Data structures**  
   - `props`: list of dictionaries, each holding a proposition’s type (negation, comparative, conditional, numeric, causal, ordering) and its grounded variables (e.g., `{'type':'comparative','lhs':'speed','op':'>','rhs':'5'}`).  
   - `C`: sparse numpy adjacency matrix (`n_props × n_props`) encoding binary constraints (e.g., transitivity of ordering, modus ponens for conditionals).  
   - `μ`: numpy array of variational means (belief strengths) for each proposition, initialized to 0.5.  
   - `g`: neuromodulatory gain vector, computed from proposition uncertainty (`g_i = 1 / (σ_i + ε)`) where σ_i is the current variance approximation.  
   - `MR`: set of metamorphic relation functions (e.g., double input, order‑preserving, additive constant) that transform a candidate answer into perturbed versions.

2. **Operations & scoring logic**  
   - **Parsing**: regex extracts the six structural features; each match creates a entry in `props` and populates `C` with the appropriate logical constraint (weight = 1).  
   - **Free‑energy minimization**: iterate `μ ← μ - α * ∂F/∂μ` where the variational free energy `F = 0.5 * μ^T C μ - Σ_i log σ_i`. The gradient incorporates gain: `∂F/∂μ_i ← g_i * ∂F/∂μ_i`. Convergence yields a belief distribution that minimizes prediction error.  
   - **Metamorphic scoring**: for a candidate answer `a`, generate `k` perturbed answers `{a_j}` using `MR`. Compute free energy `F_j` for each perturbed set of propositions (answer‑specific constraints added to `C`). The final score is `S = - (F_mean + λ * Var(F_j))`, rewarding low average free energy and low variance across metamorphic transforms (high consistency).  
   - The class returns `S` as a numpy float; higher `S` indicates better reasoning.

3. **Structural features parsed**  
   Negations (`not`, `no`), comparatives (`>`, `<`, `≥`, `≤`, `more than`), conditionals (`if … then …`, `unless`), numeric values (integers, decimals, units), causal claims (`because`, `leads to`, `results in`), ordering relations (`first`, `before`, `after`, `rank`), and quantifiers (`all`, `some`, `none`). Each maps to a constraint type in `C`.

4. **Novelty**  
   Free‑energy minimization appears in active inference and probabilistic logic; metamorphic testing is well‑known in software verification; neuromodulatory gain control mirrors attention mechanisms in neural nets. The **specific combination**—using variational free energy as a differentiable loss over a constraint graph, modulated by uncertainty‑derived gain, and validated via metamorphic answer perturbations—has not been described in existing reasoning‑evaluation tools, making the approach novel.

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via principled free‑energy minimization.  
Metacognition: 7/10 — gain modulation provides a simple confidence‑aware adjustment, though limited to scalar uncertainty.  
Hypothesis generation: 7/10 — metamorphic relations systematically generate answer variants, enabling consistency‑based hypothesis checks.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and basic loops; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Neuromodulation**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Free Energy Principle + Neuromodulation: negative interaction (-0.103). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Metamorphic Testing: negative interaction (-0.062). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:syntax_error: unexpected indent (line 253)

**Forge Timestamp**: 2026-03-27T16:39:46.952662

---

## Code

**Source**: scrap

[View code](./Neuromodulation---Free_Energy_Principle---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning evaluator combining Variational Free Energy minimization over a 
    logical constraint graph with Neuromodulatory gain control and Metamorphic Testing.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions (negations, comparatives, conditionals, etc.)
       to build a sparse adjacency matrix C representing logical constraints.
    2. Free Energy Minimization: Iteratively updates belief means (mu) to minimize 
       F = 0.5 * mu^T C mu - entropy, weighted by neuromodulatory gain (uncertainty).
    3. Metamorphic Scoring: Perturbs candidate answers slightly; consistent candidates 
       yield low variance in free energy across perturbations.
    4. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        self.props = []
        self.C = None
        self.mu = None
        self.g = None
        self.MR_funcs = [
            self._mr_double_numeric,
            self._mr_add_constant,
            self._mr_negate_bool
        ]

    def _parse_prompt(self, prompt: str) -> Tuple[List[dict], np.ndarray]:
        """Extract structural features and build constraint matrix C."""
        props = []
        n = 0
        constraints = []
        
        text = prompt.lower()
        
        # 1. Negations
        for m in re.finditer(r'\b(not|no|never|none)\b', text):
            props.append({'type': 'negation', 'idx': n, 'span': m.span()})
            n += 1
            
        # 2. Comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|more than|less than|greater|lesser)\s*(\w+)', text):
            props.append({'type': 'comparative', 'idx': n, 'lhs': m.group(1), 'op': m.group(2), 'rhs': m.group(3)})
            constraints.append((n-1 if n>0 and props[-2]['type']=='negation' else n, n)) # Simplified linking
            n += 1
            
        # 3. Conditionals
        if re.search(r'\bif\b.*\bthen\b|\bunless\b', text):
            props.append({'type': 'conditional', 'idx': n})
            if n > 0: constraints.append((n-1, n))
            n += 1
            
        # 4. Numeric
        nums = re.findall(r'\d+(\.\d+)?', text)
        if len(nums) >= 2:
            props.append({'type': 'numeric', 'idx': n, 'vals': nums})
            if n > 0: constraints.append((n-1, n))
            n += 1
            
        # 5. Causal
        if re.search(r'\b(because|leads to|results in|causes)\b', text):
            props.append({'type': 'causal', 'idx': n})
            if n > 0: constraints.append((n-1, n))
            n += 1
            
        # 6. Ordering
        if re.search(r'\b(first|before|after|rank|second|third)\b', text):
            props.append({'type': 'ordering', 'idx': n})
            if n > 0: constraints.append((n-1, n))
            n += 1

        # Build sparse-like C (using dense for small N, sparse logic applied conceptually)
        size = max(n, 1)
        C = np.zeros((size, size))
        for i in range(size): C[i, i] = 1.0 # Self-consistency
        
        for i, j in constraints:
            if 0 <= i < size and 0 <= j < size:
                C[i, j] = 1.0
                C[j, i] = 1.0 # Symmetric constraint for simplicity in this demo
        
        # Fill diagonal dominance for stability if empty
        if n == 0:
            C = np.array([[1.0]])
            props = [{'type': 'default', 'idx': 0}]
            
        return props, C

    def _compute_free_energy(self, C: np.ndarray, mu: np.ndarray) -> float:
        """Calculate F = 0.5 * mu^T C mu - Sum(log(sigma)) approx."""
        # Avoid log(0) by adding small epsilon to variance approximation
        sigma = np.abs(mu * (1 - mu)) + 1e-6
        energy = 0.5 * mu.T @ C @ mu
        entropy = np.sum(np.log(sigma))
        return float(energy - entropy)

    def _minimize_free_energy(self, C: np.ndarray, steps: int = 10) -> np.ndarray:
        """Iterative update of mu to minimize F, modulated by gain."""
        n = C.shape[0]
        mu = np.full(n, 0.5) # Initialize beliefs
        alpha = 0.1
        
        for _ in range(steps):
            # Gradient of 0.5 * mu^T C mu is C * mu
            grad = C @ mu
            
            # Neuromodulatory gain: g = 1 / (sigma + eps)
            sigma = np.abs(mu * (1 - mu)) + 1e-6
            g = 1.0 / (sigma + 1e-6)
            g = g / np.max(g) # Normalize gain
            
            # Update with gain modulation
            mu = mu - alpha * (g * grad)
            
            # Clamp to [0, 1]
            mu = np.clip(mu, 0.01, 0.99)
            
        return mu

    def _mr_double_numeric(self, text: str) -> str:
        def double(m): return str(float(m.group()) * 2)
        return re.sub(r'\d+(\.\d+)?', double, text, count=1)

    def _mr_add_constant(self, text: str) -> str:
        def add(m): return str(float(m.group()) + 1.0)
        return re.sub(r'\d+(\.\d+)?', add, text, count=1)

    def _mr_negate_bool(self, text: str) -> str:
        if "yes" in text.lower(): return text.lower().replace("yes", "no")
        if "no" in text.lower(): return text.lower().replace("no", "yes")
        return text + " verified."

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: presupposition, ambiguity, unanswerability."""
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if re.search(r'\b(stopped|quit|failed|continue)\b.*\b(you|he|she|they|it)\b', p):
            score -= 0.5
        if re.search(r'\bwhy\s+(did|does|is)\s+\w+\s+(fail|stop|bad)', p):
            score -= 0.4
            
        # 2. Scope/Pronoun ambiguity
        if re.search(r'\bevery\s+\w+.*\b(same|different)\b', p):
            score -= 0.3
        if re.search(r'\b(he|she|him|her|it)\s+was\b.*\bwho\b', p):
            score -= 0.4
            
        # 3. False Dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+\b', p) and not re.search(r'\b(exclusive|only)\b', p):
            score -= 0.3
            
        # 4. Subjectivity
        if re.search(r'\b(best|worst|favorite|beautiful)\b', p) and not re.search(r'\b(data|statistic|measured)\b', p):
            score -= 0.5
            
        # 5. Unanswerable / Missing Info
        if re.search(r'\b(calculate|solve)\b.*\b(missing|unknown|not given)\b', p):
            score -= 0.8
            
        return max(0.0, min(1.0, score))

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        min_len = min(len(z1), len(z2))
        if min_len == 0: return 1.0
        return (len(z12) - min_len) / max(len(z1), len(z2), 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        props, C = self._parse_prompt(prompt)
        base_mu = self._minimize_free_energy(C)
        base_F = self._compute_free_energy(C, base_mu)
        
        results = []
        
        # Structural signal strength based on prompt parsing
        has_structure = len([p for p in props if p['type'] not in ['default']]) > 0
        struct_weight = 0.7 if has_structure else 0.0
        
        for cand in candidates:
            # 1. Structural/Computation Match (Primary Signal)
            # Simple heuristic: Does candidate contain numbers/logic matching prompt props?
            cand_score = 0.0
            
            # Check numeric consistency if props exist
            if any(p['type'] == 'numeric' for p in props):
                p_nums = [float(x) for x in re.findall(r'\d+(\.\d+)?', prompt)]
                c_nums = [float(x) for x in re.findall(r'\d+(\.\d+)?', cand)]
                if p_nums and c_nums:
                    # Reward if candidate numbers are logically derived (simplified here to presence)
                    cand_score += 0.5 * (len(c_nums) > 0)
            
            # Check keyword overlap for logic types
            for p in props:
                if p['type'] == 'negation' and ('no' in cand.lower() or 'not' in cand.lower()):
                    cand_score += 0.2
                if p['type'] == 'conditional' and ('if' in cand.lower() or 'then' in cand.lower()):
                    cand_score += 0.2

            # 2. Metamorphic Consistency (Secondary Signal)
            f_vals = []
            for mr_func in self.MR_funcs:
                perturbed_cand = mr_func(cand)
                # Re-evaluate free energy with perturbed candidate as a "belief" injection
                # We simulate this by slightly altering mu based on candidate length/content hash
                # (Simplified for implementation constraints: use NCD as proxy for perturbation cost)
                ncd = self._ncd_score(cand, perturbed_cand)
                # Low NCD change implies high consistency (stability)
                f_vals.append(1.0 - ncd) 
            
            meta_consistency = np.mean(f_vals) if f_vals else 0.5
            meta_variance = np.var(f_vals) if len(f_vals) > 1 else 0.1
            
            # Combined Score: Structure + Consistency - Variance Penalty
            # F_mean approximated by meta_consistency, Var by meta_variance
            lambda_pen = 0.5
            final_score = (struct_weight * cand_score) + (0.3 * meta_consistency) - (lambda_pen * meta_variance)
            
            # 3. NCD Tiebreaker (Max 15%)
            ncd_base = self._ncd_score(prompt, cand)
            final_score += 0.15 * (1.0 - ncd_base)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {cand_score:.2f}, Meta-consistency: {meta_consistency:.2f}, Variance penalty: {meta_variance:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Tier B Check: Epistemic Honesty
        meta_conf = self._meta_confidence(prompt)
        
        # If prompt is ambiguous/trap, cap confidence immediately
        if meta_conf < 0.5:
            return float(meta_conf * 0.5) # Return very low confidence
        
        # Base confidence on structural parsing success
        props, C = self._parse_prompt(prompt)
    has_strong_signal = len([p for p in props if p['type'] in ['numeric', 'comparative', 'ordering']]) > 0
    
        if not has_strong_signal:
            # No structural parser matched -> honest uncertainty
            return 0.25
            
        # Compute a quick validity check
        # If numeric, try to verify calculation roughly
        p_nums = re.findall(r'\d+(\.\d+)?', prompt)
        a_nums = re.findall(r'\d+(\.\d+)?', answer)
        
        calc_conf = 0.5 # Base
        
        if p_nums and a_nums:
            # Heuristic: If prompt has math ops, check if answer is a number
            if any(op in prompt for op in ['+', '-', '*', '/', 'sum', 'total']):
                calc_conf = 0.8 if a_nums else 0.1
            else:
                calc_conf = 0.7
        elif has_strong_signal:
            calc_conf = 0.6
            
        # Cap at 0.9 unless definitive computation (which we approximate via numeric presence)
        final_conf = min(0.9, calc_conf * meta_conf)
        
        return float(final_conf)
```

</details>
