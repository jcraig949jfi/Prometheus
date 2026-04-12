# Phase Transitions + Criticality + Free Energy Principle

**Fields**: Physics, Complex Systems, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T08:25:23.295447
**Report Generated**: 2026-03-27T16:08:10.638351

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex‑based patterns to extract atomic propositions from the prompt and each candidate answer. Atoms are typed (e.g., `Neg(p)`, `Comp(x>y)`, `Cond(A→B)`, `Causal(A→B)`, `Num(val,unit)`, `Order(A before B)`). Each atom becomes a node in a factor graph.  
2. **Factor construction** – For every logical relationship identified (transitivity of `Order`, modus ponens of `Cond`, contradiction of `Neg`, arithmetic consistency of `Num`, etc.) create a factor that connects the involved nodes. Assign each factor a weight `w` equal to the inverse of its estimated noise (derived from cue‑word confidence, e.g., “definitely” → high w).  
3. **Mean‑field variational free energy** – Treat the truth value of each atom as a binary variable `s_i∈{0,1}` with approximating posterior `q_i = P(s_i=1)`. Energy of a configuration:  
   `E(s) = Σ_f w_f·V_f(s)` where `V_f` is 0 if factor f is satisfied, 1 otherwise.  
   Free energy under mean‑field:  
   `F(q) = Σ_f w_f·⟨V_f⟩_q − Σ_i [q_i log q_i + (1−q_i) log(1−q_i)]`.  
   Update each `q_i` via the standard mean‑field fixed‑point equation until convergence.  
4. **Criticality detection** – Introduce a global temperature `T` that scales all weights (`w_f←w_f/T`). Compute susceptibility `χ = d⟨m⟩/dT` where order parameter `m = (1/N)Σ_i (2q_i−1)`. Sweep `T` across a log‑space grid; the peak of `χ` identifies the critical point.  
5. **Scoring** – For each candidate, record the free energy `F*` at the temperature where `χ` is maximal. Lower `F*` indicates better constraint satisfaction; higher `χ` indicates the answer sits near a phase transition, i.e., it captures subtle, high‑impact inferences. Final score = `−F* + λ·χ` (λ ≈ 0.1 to balance terms).  

**Structural features parsed**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `≥`, `≤`)  
- Conditionals (`if … then`, `unless`)  
- Causal cues (`because`, `leads to`, `results in`)  
- Numeric values with units and arithmetic relations  
- Ordering/temporal markers (`before`, `after`, `first`, `finally`)  
- Quantifiers (`all`, `some`, `none`)  
- Conjunction/disjunction (`and`, `or`)  

**Novelty**  
Energy‑based scoring of logical forms exists, but coupling it with a statistical‑physics criticality analysis—using susceptibility peaks to weight answers that are both low‑energy and highly sensitive—has not been applied to reasoning evaluation. Thus the combination is novel in this context.  

**Ratings**  
Reasoning: 8/10 — captures deep logical consistency and sensitivity to subtle constraints.  
Metacognition: 6/10 — provides implicit confidence via susceptibility but lacks explicit self‑reflection mechanisms.  
Hypothesis generation: 5/10 — focuses on scoring given hypotheses; generation would require additional proposal step.  
Implementability: 9/10 — relies only on regex, numpy operations, and simple iterative updates; feasible in pure Python.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Phase Transitions**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 33% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Criticality + Phase Transitions: strong positive synergy (+0.885). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Phase Transitions: strong positive synergy (+0.397). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Criticality + Free Energy Principle: strong positive synergy (+0.369). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Evolution + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Architecture Search + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T07:09:31.141838

---

## Code

**Source**: scrap

[View code](./Phase_Transitions---Criticality---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np

class ReasoningTool:
    """
    Implements a Mean-Field Variational Free Energy solver with Criticality detection.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (Negation, Comparison, Conditionals, Causal, Numeric, Order).
    2. Factor Graph: Constructs logical constraints between atoms based on prompt logic.
    3. Inference: Uses mean-field updates to minimize Free Energy (satisfy constraints).
    4. Criticality: Sweeps a global temperature parameter to find the susceptibility peak.
       - Answers with low Free Energy (consistent) AND high Susceptibility (sensitive to constraints)
       are ranked highest.
    5. Scoring: Final score = -F* + lambda * chi_peak.
    """

    def __init__(self):
        # Regex patterns for atomic extraction
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comp': re.compile(r'\b(greater|less|more|fewer|higher|lower|bigger|smaller)\b', re.IGNORECASE),
            'cond': re.compile(r'\b(if|unless|then|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'order': re.compile(r'\b(before|after|first|last|finally|precede|follow)\b', re.IGNORECASE),
            'num': re.compile(r'-?\d+(?:\.\d+)?'),
            'quant': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE)
        }

    def _extract_atoms(self, text: str) -> list:
        """Extract typed atomic propositions from text."""
        atoms = []
        text_lower = text.lower()
        
        # Extract numeric values
        nums = self.patterns['num'].findall(text)
        for n in nums:
            atoms.append(('Num', float(n)))
            
        # Extract logical markers (simplified to presence counts for atomic nodes)
        if self.patterns['neg'].search(text_lower): atoms.append(('Neg', 1.0))
        if self.patterns['comp'].search(text_lower): atoms.append(('Comp', 1.0))
        if self.patterns['cond'].search(text_lower): atoms.append(('Cond', 1.0))
        if self.patterns['causal'].search(text_lower): atoms.append(('Causal', 1.0))
        if self.patterns['order'].search(text_lower): atoms.append(('Order', 1.0))
        if self.patterns['quant'].search(text_lower): atoms.append(('Quant', 1.0))
        
        # Fallback if no atoms found (prevents empty graph)
        if not atoms:
            atoms.append(('Raw', 1.0))
            
        return atoms

    def _build_factors(self, prompt_atoms: list, answer_atoms: list) -> list:
        """
        Construct factors connecting prompt and answer atoms.
        Returns list of (indices, weight, type)
        """
        factors = []
        all_atoms = prompt_atoms + answer_atoms
        n = len(all_atoms)
        if n == 0: return factors
        
        p_len = len(prompt_atoms)
        
        # 1. Consistency factors (Prompt Negation should match Answer Negation if present)
        # We create factors between similar types in prompt and answer
        for i, (p_type, p_val) in enumerate(prompt_atoms):
            for j, (a_type, a_val) in enumerate(answer_atoms):
                idx_a = p_len + j
                if p_type == a_type:
                    # Strong weight for matching logical types
                    w = 2.0 
                    factors.append(([i, idx_a], w, 'match'))
                elif p_type == 'Num' and a_type == 'Num':
                    # Numeric consistency: if prompt has numbers, answer having numbers is a weak positive constraint
                    # (In a real solver, we'd check magnitude logic)
                    factors.append(([i, idx_a], 0.5, 'num_match'))
        
        # 2. Structural integrity factors (internal to answer)
        # If answer has 'Neg' and 'Comp', they likely form a valid comparative negation structure
        a_types = [x[0] for x in answer_atoms]
        if 'Neg' in a_types and 'Comp' in a_types:
            idx_neg = p_len + a_types.index('Neg')
            idx_comp = p_len + a_types.index('Comp')
            factors.append(([idx_neg, idx_comp], 1.5, 'struct_neg_comp'))
            
        # 3. Prompt-Answer implication (Simplified Modus Ponens)
        # If prompt has 'Cond' and answer has 'Causal' or 'Order', boost connection
        if any(x[0] == 'Cond' for x in prompt_atoms):
            for j, (a_type, _) in enumerate(answer_atoms):
                if a_type in ['Causal', 'Order', 'Comp']:
                    idx_a = p_len + j
                    # Connect to a dummy 'conclusion' node or just boost internal answer coherence
                    factors.append(([idx_a, idx_a], 1.0, 'implication_support'))

        return factors

    def _mean_field_solve(self, n_nodes: int, factors: list, T: float) -> tuple:
        """
        Perform mean-field updates to find q (probabilities).
        Returns (free_energy, q_vector)
        """
        if n_nodes == 0: return 0.0, np.array([])
        
        # Initialize q uniformly
        q = np.full(n_nodes, 0.5)
        
        # Precompute factor data for speed
        # factors format: (indices, weight, type)
        # V_f(s) = 0 if satisfied. 
        # For 'match': satisfied if s_i == s_j. Energy = w * (s_i != s_j)
        # Mean field approximation for pairwise: <V> = q_i(1-q_j) + (1-q_i)q_j
        
        max_iter = 50
        for _ in range(max_iter):
            q_old = q.copy()
            for idxs, w_raw, f_type in factors:
                w = w_raw / T
                i = idxs[0]
                j = idxs[1] if len(idxs) > 1 else i
                
                if i >= n_nodes or j >= n_nodes: continue

                if f_type == 'match' or f_type == 'num_match':
                    # Interaction term: encourage same state
                    # dE/dq_i approx w * (1 - 2*q_j) ? 
                    # Actually, for Ising-like: E = -J s_i s_j. Here we want match.
                    # Let's use simple heuristic: q_i <- sigmoid( sum_j w_ij * (2q_j - 1) )
                    pass 
                elif f_type == 'struct_neg_comp':
                    # Encourage co-activation
                    pass
                elif f_type == 'implication_support':
                    # Self-loop boost
                    q[i] = min(0.99, max(0.01, q[i] + w * 0.1))

            # Simplified Mean Field Update Rule for this specific graph structure
            # We approximate the gradient of Free Energy w.r.t q_i
            new_q = q.copy()
            for i in range(n_nodes):
                field = 0.0
                for idxs, w_raw, f_type in factors:
                    if i not in idxs: continue
                    w = w_raw / T
                    j = idxs[1] if idxs[0] == i and len(idxs)>1 else (idxs[0] if idxs[1]==i else idxs[0])
                    if j >= n_nodes: j=i
                    
                    if f_type in ['match', 'num_match', 'struct_neg_comp']:
                        # Ferromagnetic coupling: align with neighbor
                        field += w * (2 * q[j] - 1)
                    elif f_type == 'implication_support':
                        field += w * 0.5
                
                # Logistic update
                logit = math.log(q[i] / (1 - q[i] + 1e-9)) + field
                new_q[i] = 1.0 / (1.0 + math.exp(-logit))
                new_q[i] = min(0.999, max(0.001, new_q[i]))
            
            q = new_q
            if np.max(np.abs(q - q_old)) < 1e-4:
                break
        
        # Calculate Free Energy F = <E> - S
        energy = 0.0
        for idxs, w_raw, f_type in factors:
            w = w_raw / T
            i, j = idxs[0], idxs[1] if len(idxs)>1 else idxs[0]
            if i>=n_nodes or j>=n_nodes: continue
            
            if f_type in ['match', 'num_match', 'struct_neg_comp']:
                # Prob of mismatch: q_i(1-q_j) + (1-q_i)q_j
                prob_violate = q[i]*(1-q[j]) + (1-q[i])*q[j]
                energy += w * prob_violate
            elif f_type == 'implication_support':
                 # Self penalty if low confidence? No, just boost.
                 pass

        entropy = 0.0
        for qi in q:
            if qi > 1e-9 and qi < 1-1e-9:
                entropy -= (qi * math.log(qi) + (1-qi) * math.log(1-qi))
                
        F = energy - entropy
        return F, q

    def _compute_susceptibility(self, prompt: str, candidate: str) -> tuple:
        """Sweep T to find critical point and compute susceptibility."""
        p_atoms = self._extract_atoms(prompt)
        a_atoms = self._extract_atoms(candidate)
        factors = self._build_factors(p_atoms, a_atoms)
        n_nodes = len(p_atoms) + len(a_atoms)
        
        if n_nodes == 0: return 0.0, 0.0
        
        # Temperature sweep
        temps = np.logspace(-2, 1, 20) # T from 0.01 to 10
        m_vals = []
        f_vals = []
        
        for T in temps:
            F, q = self._mean_field_solve(n_nodes, factors, T)
            m = np.mean(2 * q - 1) # Order parameter
            m_vals.append(m)
            f_vals.append(F)
            
        # Compute susceptibility chi = d<m>/dT approximated by finite difference
        chi_vals = []
        for i in range(1, len(m_vals)):
            dm = m_vals[i] - m_vals[i-1]
            dT = temps[i] - temps[i-1]
            chi = abs(dm / (dT + 1e-9))
            chi_vals.append(chi)
            
        if not chi_vals: return 0.0, 0.0
        
        # Find critical point (max chi)
        max_chi_idx = np.argmax(chi_vals)
        max_chi = chi_vals[max_chi_idx]
        
        # Get Free Energy at critical temperature
        # Note: chi_vals is one shorter than temps. max_chi_idx corresponds to interval i->i+1
        # We take the F at the higher T of the interval for safety, or average. 
        # Let's pick the F at the index corresponding to the peak.
        critical_F = f_vals[min(max_chi_idx + 1, len(f_vals)-1)]
        
        return critical_F, max_chi

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            F_star, chi = self._compute_susceptibility(prompt, cand)
            
            # Score: Lower F is better (negative F_star), Higher Chi is better
            # Normalize slightly to prevent overflow if chi is huge
            score = -F_star + 0.1 * math.log1p(chi)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free Energy: {F_star:.4f}, Susceptibility: {chi:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the scoring mechanism."""
        # Evaluate single candidate against a dummy set to get relative score?
        # Or just use the internal metrics mapped to 0-1.
        # Let's use the score components directly.
        F_star, chi = self._compute_susceptibility(prompt, answer)
        
        # Heuristic mapping: 
        # Low F (good) -> high base confidence. 
        # High Chi (critical) -> boost.
        # F is usually small negative/positive. Let's assume F < 0 is good.
        # Sigmoid mapping of (-F + 0.1*chi)
        raw_score = -F_star + 0.1 * math.log1p(chi)
        
        # Map to 0-1. Assume raw_score ranges roughly -5 to 5.
        conf = 1.0 / (1.0 + math.exp(-raw_score))
        return conf
```

</details>
