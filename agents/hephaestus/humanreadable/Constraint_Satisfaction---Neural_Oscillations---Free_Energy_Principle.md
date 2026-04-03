# Constraint Satisfaction + Neural Oscillations + Free Energy Principle

**Fields**: Computer Science, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T15:43:48.278819
**Report Generated**: 2026-04-02T04:20:09.971741

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a set of binary propositions \(p_i\) extracted with regex patterns for negations, comparatives, conditionals, causal links, ordering, and numeric thresholds (e.g., “X > Y”, “if A then B”, “not C”). These propositions become nodes in a factor graph.  

*Data structures*  
- **Variable matrix** \(V\in\{0,1\}^{n\times m}\): \(n\) propositions, \(m\) candidates; entry \(V_{ij}=1\) if proposition \(i\) holds in candidate \(j\).  
- **Constraint tensor** \(C\in\mathbb{R}^{k\times n\times n}\): each slice \(c_k\) encodes a logical constraint (e.g., modus ponens \(A\land(A\rightarrow B)\Rightarrow B\)) as a weight \(w_k\) and a pairwise interaction mask.  
- **Oscillator phase vector** \(\phi\in\mathbb{R}^{n}\): one phase per proposition, initialized uniformly.  

*Operations*  
1. **Constraint propagation (oscillatory message passing)** – For each iteration \(t\):  
   \[
   \phi^{(t+1)} = \phi^{(t)} + \alpha \sum_{k} w_k \, \sin\bigl(\phi^{(t)} \otimes M_k - \phi^{(t)}\bigr)
   \]  
   where \(M_k\) is the mask from \(C_k\) and \(\alpha\) a step size. This is a Kuramoto‑style coupling that drives phases of linked propositions toward consistency.  
2. **Free‑energy approximation** – Compute prediction error for each constraint:  
   \[
   E_k = w_k \bigl\| V_{\cdot j} \odot M_k - \text{target}_k \bigr\|_2^2
   \]  
   Sum over \(k\) gives variational free energy \(F_j = \sum_k E_k\) for candidate \(j\).  
3. **Score** – \(S_j = -F_j\) (lower energy → higher score). The iteration stops when \(\|\phi^{(t+1)}-\phi^{(t)}\|<\epsilon\) or after a fixed number of steps (typically 5‑10).  

*Structural features parsed*  
- Negations (“not”, “no”) → flip variable polarity.  
- Comparatives (“greater than”, “less than”) → numeric constraints on extracted quantities.  
- Conditionals (“if … then …”) → implication edges in \(C\).  
- Causal claims (“because”, “leads to”) → directed weighted edges.  
- Ordering relations (“before”, “after”) → temporal precedence constraints.  
- Quantifiers (“all”, “some”) → cardinality constraints encoded as additional slices in \(C\).  

*Novelty*  
Pure constraint solvers (SAT, CSP) lack a dynamical synchrony mechanism; variational free‑energy methods are usually applied to perceptual models, not discrete answer scoring. Combining Kuramoto‑style oscillatory message passing with a free‑energy objective yields a novel hybrid that enforces both logical consistency and global error minimization, which to our knowledge has not been used for answer ranking.  

*Ratings*  
Reasoning: 8/10 — captures logical structure and propagates constraints via a principled dynamical system.  
Metacognition: 6/10 — the algorithm can monitor free‑energy reduction but lacks explicit self‑reflection on its own certainty.  
Hypothesis generation: 5/10 — generates implicit hypotheses (phase alignments) but does not produce symbolic alternative answers.  
Implementability: 9/10 — relies only on numpy for matrix ops and stdlib regex; all steps are straightforward to code.

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
**Reason**: trap_battery_failed (acc=35% cal=23% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T20:56:09.938499

---

## Code

**Source**: scrap

[View code](./Constraint_Satisfaction---Neural_Oscillations---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining Constraint Satisfaction, Neural Oscillations (Kuramoto),
    and Free Energy Principle with Dynamical Systems stability analysis.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, negations, comparatives, and conditionals.
    2. Oscillatory Consensus: Uses Kuramoto-style phase coupling to enforce logical consistency
       among extracted propositions within each candidate.
    3. Free Energy Scoring: Calculates prediction error (energy) based on constraint satisfaction.
    4. Dynamical Stability (Frame C): Perturbs the system state and measures trajectory convergence
       to determine epistemic confidence. Unstable trajectories indicate ambiguity or insufficient info.
    5. Epistemic Honesty: Explicitly checks for Tier B traps (presuppositions, ambiguity) to cap confidence.
    """

    def __init__(self):
        self.epsilon = 1e-4
        self.max_steps = 10
        self.alpha = 0.5  # Coupling strength
        self.perturbation_scale = 0.1

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extracts logical atoms, negations, comparatives, and conditionals."""
        props = []
        text_lower = text.lower()
        
        # 1. Negations
        if re.search(r'\b(not|no|never|none)\b', text_lower):
            props.append({'type': 'negation_flag', 'val': 1.0})
            
        # 2. Comparatives (Numeric)
        nums = re.findall(r'-?\d+\.?\d*', text)
        if len(nums) >= 2:
            vals = [float(n) for n in nums]
            # Simple comparative check: is the sequence sorted?
            is_sorted = all(vals[i] <= vals[i+1] for i in range(len(vals)-1))
            props.append({'type': 'numeric_order', 'val': 1.0 if is_sorted else 0.0})
            
        # 3. Conditionals
        if re.search(r'\b(if|then|unless|provided)\b', text_lower):
            props.append({'type': 'conditional_flag', 'val': 1.0})
            
        # 4. Causal/Temporal
        if re.search(r'\b(because|therefore|before|after|leads to)\b', text_lower):
            props.append({'type': 'causal_flag', 'val': 1.0})

        # 5. Quantifiers
        if re.search(r'\b(all|every|some|none)\b', text_lower):
            props.append({'type': 'quantifier_flag', 'val': 1.0})

        # Default proposition if nothing specific found (baseline)
        if not props:
            props.append({'type': 'default', 'val': 0.5})
            
        return props

    def _build_constraint_matrix(self, props: List[Dict]) -> np.ndarray:
        """Builds a symmetric constraint matrix based on logical compatibility."""
        n = len(props)
        if n == 0:
            return np.array([[0.0]])
        
        C = np.zeros((n, n))
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i == j:
                    C[i, j] = 1.0
                    continue
                
                # Logical consistency rules (simplified for demonstration)
                # Negation conflicts with positive assertions if types clash
                if p1['type'] == 'negation_flag' and p2['type'] != 'negation_flag':
                    C[i, j] = -0.5 # Tension
                elif p1['type'] == 'conditional_flag' and p2['type'] == 'causal_flag':
                    C[i, j] = 0.8 # Reinforcement
                else:
                    C[i, j] = 0.1 # Weak coupling
                    
        return C

    def _kuramoto_step(self, phases: np.ndarray, C: np.ndarray) -> np.ndarray:
        """Single step of Kuramoto oscillatory message passing."""
        n = len(phases)
        update = np.zeros(n)
        for i in range(n):
            sum_sin = 0.0
            for j in range(n):
                if i != j:
                    # Coupling term: sin(phase_j - phase_i) weighted by constraint C_ij
                    sum_sin += C[i, j] * np.sin(phases[j] - phases[i])
            update[i] = self.alpha * sum_sin
        return phases + update

    def _compute_free_energy(self, phases: np.ndarray, C: np.ndarray) -> float:
        """Computes variational free energy (prediction error)."""
        energy = 0.0
        n = len(phases)
        for i in range(n):
            for j in range(i+1, n):
                # Error is deviation from expected phase relationship (synchronized = 0 diff)
                # Target is 0 (mod 2pi) for positive constraints, pi for negative
                target = 0.0 if C[i,j] > 0 else np.pi
                weight = abs(C[i,j])
                diff = phases[i] - phases[j]
                # Normalize diff to [-pi, pi]
                diff = np.arctan2(np.sin(diff), np.cos(diff))
                energy += weight * (diff - target)**2
        return energy

    def _simulate_dynamics(self, props: List[Dict], n_perturb: int = 3) -> Tuple[float, float]:
        """
        Runs the oscillatory dynamics and measures stability.
        Returns: (final_energy, stability_score)
        Stability is inverse variance of final states under small perturbations.
        """
        n = max(1, len(props))
        C = self._build_constraint_matrix(props)
        
        # Base run
        phases = np.random.uniform(0, 2*np.pi, n)
        for _ in range(self.max_steps):
            phases = self._kuramoto_step(phases, C)
        base_energy = self._compute_free_energy(phases, C)
        
        # Perturbation runs for stability analysis (Lyapunov-like)
        final_states = []
        for _ in range(n_perturb):
            p_perturbed = phases + np.random.normal(0, self.perturbation_scale, n)
            for _ in range(self.max_steps):
                p_perturbed = self._kuramoto_step(p_perturbed, C)
            final_states.append(p_perturbed)
            
        if n_perturb == 0:
            return base_energy, 1.0
            
        final_states = np.array(final_states)
        # Stability: low variance in final states indicates a strong attractor (high confidence)
        variance = np.mean(np.var(final_states, axis=0))
        stability = 1.0 / (1.0 + variance) # Map variance to 0-1 scale
        
        return base_energy, stability

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presuppositions, and unanswerable structures.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if re.search(r'\b(have you stopped|did you stop|why did .+ fail|why is .+ wrong)\b', p_lower):
            score = min(score, 0.2)
            
        # 2. Scope/Pronoun ambiguity markers
        if re.search(r'\b(every .+ a .+|he was|she was|they said|who is)\b', p_lower):
            if 'ambigu' in p_lower or 'refer' in p_lower:
                score = min(score, 0.3)
                
        # 3. False dichotomy
        if re.search(r'\b(either .+ or .+)\b', p_lower) and not re.search(r'\b(both|neither)\b', p_lower):
            score = min(score, 0.4)
            
        # 4. Subjectivity
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_lower):
            score = min(score, 0.5)
            
        # 5. Unanswerable / Missing info
        if re.search(r'\b(without|missing|unknown|cannot be determined)\b', p_lower):
            score = min(score, 0.1)

        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        props = self._extract_propositions(prompt)
        
        # Pre-calculate prompt NCD for normalization if needed
        prompt_len = len(prompt)
        
        for cand in candidates:
            # 1. Structural & Dynamical Analysis
            # Combine prompt props with candidate content for context-sensitive parsing
            full_text = f"{prompt} {cand}"
            cand_props = self._extract_propositions(full_text)
            
            # Run dynamics
            energy, stability = self._simulate_dynamics(cand_props)
            
            # 2. Constructive Computation (Numeric/Logic check)
            # If numbers exist, try to verify logic directly
            logic_bonus = 0.0
            nums = re.findall(r'-?\d+\.?\d*', full_text)
            if len(nums) >= 2:
                # Simple heuristic: if candidate contains a calculation result implied by prompt
                # This is a placeholder for specific domain solvers (PEMDAS, etc)
                logic_bonus = 0.1 
            
            # 3. NCD Tiebreaker (Max 15% influence)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Combine scores: Higher stability = lower energy = better
            # Normalize energy roughly to 0-10 range for scaling
            norm_energy = min(10.0, energy) 
            base_score = (10.0 - norm_energy) * stability + logic_bonus + ncd_score
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Stability:{stability:.2f}, Energy:{norm_energy:.2f}, NCD:{ncd_val:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _meta_confidence(self, prompt: str) -> float:
        return self._check_meta_confidence(prompt)

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Check for Tier B traps (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # If meta-analysis detects a trap, return low confidence immediately
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Evaluate the specific answer dynamics
        props = self._extract_propositions(f"{prompt} {answer}")
        energy, stability = self._simulate_dynamics(props)
        
        # 3. Compute raw confidence from stability and energy
        # High stability + Low energy = High confidence
        raw_conf = stability * np.exp(-energy / 5.0)
        
        # 4. Apply structural penalty if no clear structure found
        if len(props) <= 1:
            raw_conf = min(raw_conf, 0.4) # Cap confidence if parsing yields little structure
            
        # 5. Enforce cap
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure bounds [0, 1]
        return max(0.0, min(1.0, final_conf))
```

</details>
