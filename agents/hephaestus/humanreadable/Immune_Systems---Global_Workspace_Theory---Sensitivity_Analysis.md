# Immune Systems + Global Workspace Theory + Sensitivity Analysis

**Fields**: Biology, Cognitive Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T17:18:46.126561
**Report Generated**: 2026-04-02T12:33:29.191023

---

## Nous Analysis

**Algorithm – Clonal‑Workspace Sensitivity Scorer (CWSS)**  

1. **Parsing & proposition extraction** – Using only `re` and `str.split`, the prompt and each candidate answer are scanned for:  
   * atomic predicates (`X is Y`),  
   * negations (`not …`),  
   * comparatives (`greater than`, `less than`),  
   * conditionals (`if … then …`),  
   * causal markers (`because`, `leads to`),  
   * numeric tokens (integers/floats).  
   Each match becomes a `Prop` object stored in a NumPy structured array with fields: `type` (enum), `arg1`, `arg2`, `polarity` (±1 for negation), `value` (float for numerics, else NaN).  

2. **Clonal expansion** – For a given set of propositions `P` (prompt or answer) we generate a clone library `C` by applying a fixed perturbation set:  
   * flip `polarity`,  
   * add/subtract ε=0.01 to numeric `value`,  
   * swap `arg1`/`arg2` for comparatives/causals,  
   * drop a random predicate (to model forgetting).  
   Clones are stored as rows in a NumPy array; affinity to the source set is computed as:  
   `aff = 0.5*Jaccard(predicate_set) + 0.5*(1 - normalized_L2_distance(numeric_vectors))`.  

3. **Global workspace ignition** – The top‑k clones (k=5 by affinity) are **broadcast**: their affinities are summed into a global activation `A = Σ w_i·aff_i` where weights `w_i` decay exponentially with rank. If `A` exceeds a threshold θ (set to the 75th percentile of affinities from a random baseline), the workspace is considered ignited and the clone set is accepted as a representation of the input’s logical core.  

4. **Memory & scoring** – Accepted clones are inserted into a long‑term memory matrix `M` (NumPy array) using a simple Hebbian update: `M ← M + η·clone·cloneᵀ`. For each candidate answer, we compute:  
   * **Core score** = affinity between its ignited clone set and the prompt’s ignited set.  
   * **Sensitivity score** = variance of core score under the same perturbation library applied to the answer (low variance → high robustness).  
   Final score = `core_score * (1 - sensitivity_score)`.  

**What is parsed?** Negations, comparatives, conditionals, causal markers, numeric values, and ordering relations (derived from comparatives).  

**Novelty?** The triplet maps loosely to existing ideas: clonal selection resembles genetic programming, global workspace resembles attention‑based broadcasting, and sensitivity analysis mirrors robustness checks in causal inference. However, binding them together in a deterministic, numpy‑only scorer that alternates mutation, affinity‑based selection, global ignition, and memory‑based Hebbian update is not described in the literature to my knowledge, making the combination novel for this evaluation setting.  

**Ratings**  
Reasoning: 8/10 — captures logical structure via propositional parsing and clonal competition, but lacks deeper higher‑order reasoning.  
Metacognition: 6/10 — sensitivity analysis offers a crude self‑check, yet no explicit monitoring of search dynamics.  
Hypothesis generation: 7/10 — clonal expansion yields diverse mutants; workspace ignition acts as a hypothesis filter.  
Implementability: 9/10 — relies solely on regex, NumPy arrays, and basic arithmetic; no external libraries or APIs needed.

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
**Reason**: validation:confidence_bad_return_type: float32

**Forge Timestamp**: 2026-04-02T11:55:14.468798

---

## Code

**Source**: scrap

[View code](./Immune_Systems---Global_Workspace_Theory---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Clonal-Workspace Sensitivity Scorer (CWSS)
    
    Combines immune system clonal selection, global workspace theory, and sensitivity
    analysis. Parses propositions, generates clonal expansions, uses affinity-based
    workspace ignition, tracks state dynamics, and scores via robustness + convergence.
    """
    
    def __init__(self):
        np.random.seed(42)
        self.memory = np.zeros((50, 50), dtype=np.float32)
        self.eta = 0.1
        self.theta_percentile = 75
        self.k_top = 5
        self.epsilon = 0.01
        
    def _parse_props(self, text: str) -> np.ndarray:
        """Extract propositions: negations, comparatives, conditionals, causals, numerics"""
        props = []
        text_lower = text.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|neither)\s+(\w+)', text_lower):
            props.append(('neg', m.group(2), '', -1, np.nan))
        
        # Comparatives with numbers
        for m in re.finditer(r'([\d.]+)\s*(>|<|>=|<=|greater|less)\s*(than\s*)?([\d.]+)', text_lower):
            v1, op, _, v2 = m.groups()
            props.append(('cmp', v1, v2, 1, float(v1) if v1 else np.nan))
        
        # Conditionals
        for m in re.finditer(r'if\s+(\w+).*?then\s+(\w+)', text_lower):
            props.append(('cond', m.group(1), m.group(2), 1, np.nan))
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(because|leads to|causes|implies)\s+(\w+)', text_lower):
            props.append(('cause', m.group(1), m.group(3), 1, np.nan))
        
        # Numeric tokens
        for m in re.finditer(r'\b(\d+\.?\d*)\b', text):
            props.append(('num', m.group(1), '', 1, float(m.group(1))))
        
        # Predicates
        for m in re.finditer(r'(\w+)\s+is\s+(\w+)', text_lower):
            props.append(('pred', m.group(1), m.group(2), 1, np.nan))
        
        return np.array(props, dtype=[('type', 'U10'), ('arg1', 'U50'), ('arg2', 'U50'), 
                                       ('pol', 'i4'), ('val', 'f4')]) if props else np.array([], dtype=[('type', 'U10'), ('arg1', 'U50'), ('arg2', 'U50'), ('pol', 'i4'), ('val', 'f4')])
    
    def _generate_clones(self, props: np.ndarray, n_clones: int = 20) -> List[np.ndarray]:
        """Generate clonal library via perturbations"""
        if len(props) == 0:
            return [props]
        
        clones = [props]
        for _ in range(n_clones - 1):
            clone = props.copy()
            if len(clone) > 0:
                idx = np.random.randint(len(clone))
                op = np.random.randint(4)
                
                if op == 0:  # Flip polarity
                    clone[idx]['pol'] *= -1
                elif op == 1 and not np.isnan(clone[idx]['val']):  # Perturb numeric
                    clone[idx]['val'] += np.random.choice([-self.epsilon, self.epsilon])
                elif op == 2:  # Swap args
                    clone[idx]['arg1'], clone[idx]['arg2'] = clone[idx]['arg2'], clone[idx]['arg1']
                elif op == 3 and len(clone) > 1:  # Drop predicate
                    clone = np.delete(clone, idx)
            
            clones.append(clone)
        return clones
    
    def _affinity(self, props1: np.ndarray, props2: np.ndarray) -> float:
        """Compute affinity between two proposition sets"""
        if len(props1) == 0 and len(props2) == 0:
            return 1.0
        if len(props1) == 0 or len(props2) == 0:
            return 0.0
        
        # Jaccard on predicates
        set1 = set(zip(props1['type'], props1['arg1'], props1['arg2']))
        set2 = set(zip(props2['type'], props2['arg1'], props2['arg2']))
        jaccard = len(set1 & set2) / max(len(set1 | set2), 1)
        
        # Numeric distance
        nums1 = props1['val'][~np.isnan(props1['val'])]
        nums2 = props2['val'][~np.isnan(props2['val'])]
        if len(nums1) > 0 and len(nums2) > 0:
            min_len = min(len(nums1), len(nums2))
            dist = np.linalg.norm(nums1[:min_len] - nums2[:min_len])
            num_sim = 1.0 / (1.0 + dist)
        else:
            num_sim = 0.5
        
        return 0.5 * jaccard + 0.5 * num_sim
    
    def _workspace_ignition(self, clones: List[np.ndarray], source: np.ndarray) -> Tuple[bool, float, List[np.ndarray]]:
        """Global workspace ignition via top-k affinity broadcast"""
        affinities = [self._affinity(c, source) for c in clones]
        sorted_idx = np.argsort(affinities)[::-1]
        
        top_k_idx = sorted_idx[:self.k_top]
        weights = np.exp(-0.5 * np.arange(self.k_top))
        activation = sum(weights[i] * affinities[top_k_idx[i]] for i in range(min(self.k_top, len(top_k_idx))))
        
        # Threshold from percentile
        theta = np.percentile(affinities, self.theta_percentile) if len(affinities) > 1 else 0.5
        ignited = activation > theta
        
        accepted = [clones[i] for i in top_k_idx] if ignited else []
        return ignited, activation, accepted
    
    def _state_dynamics(self, props: np.ndarray, prompt_props: np.ndarray) -> Dict[str, float]:
        """Track state evolution dynamics across premise processing"""
        if len(props) == 0:
            return {'convergence': 0.0, 'stability': 0.0, 'divergence': 1.0}
        
        # Build state trajectory by processing premises sequentially
        state = np.zeros(10)
        trajectory = [state.copy()]
        
        for i, prop in enumerate(props):
            # Update state based on proposition type
            if not np.isnan(prop['val']):
                state[i % 10] = prop['val'] * 0.1
            else:
                state[i % 10] = hash(prop['arg1'] + prop['arg2']) % 100 * 0.01
            
            state = 0.8 * state + 0.2 * np.random.randn(10) * 0.01  # Reservoir dynamics
            trajectory.append(state.copy())
        
        trajectory = np.array(trajectory)
        
        # Convergence: variance in later states
        if len(trajectory) > 2:
            late_var = np.var(trajectory[-3:])
            convergence = 1.0 / (1.0 + late_var)
        else:
            convergence = 0.5
        
        # Stability: max deviation from mean
        if len(trajectory) > 1:
            mean_state = np.mean(trajectory, axis=0)
            deviations = [np.linalg.norm(t - mean_state) for t in trajectory]
            stability = 1.0 / (1.0 + max(deviations))
        else:
            stability = 0.5
        
        # Divergence detection (Lyapunov-style)
        if len(trajectory) > 3:
            diffs = np.diff(trajectory, axis=0)
            growth = np.linalg.norm(diffs[-1]) / (np.linalg.norm(diffs[0]) + 1e-6)
            divergence = min(growth, 2.0) / 2.0
        else:
            divergence = 0.5
        
        return {'convergence': convergence, 'stability': stability, 'divergence': divergence}
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability"""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|have you quit|why did .* (fail|stop))', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*\ba\b', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'either .* or', p) and 'or' in p.split('either')[1]:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.3
        
        return 1.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using CWSS"""
        prompt_props = self._parse_props(prompt)
        prompt_clones = self._generate_clones(prompt_props)
        p_ignited, p_activation, p_accepted = self._workspace_ignition(prompt_clones, prompt_props)
        
        results = []
        for cand in candidates:
            cand_props = self._parse_props(cand)
            cand_clones = self._generate_clones(cand_props)
            c_ignited, c_activation, c_accepted = self._workspace_ignition(cand_clones, cand_props)
            
            # Core score: affinity
            core_score = self._affinity(cand_props, prompt_props)
            
            # Sensitivity: variance under perturbations
            perturb_scores = [self._affinity(c, prompt_props) for c in cand_clones]
            sensitivity = np.var(perturb_scores) if len(perturb_scores) > 1 else 0.5
            
            # Dynamics
            dynamics = self._state_dynamics(cand_props, prompt_props)
            
            # NCD tiebreaker
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Composite score: 40% dynamics, 30% core, 15% sensitivity, 15% NCD
            score = (0.4 * (dynamics['convergence'] + dynamics['stability']) / 2.0 +
                    0.3 * core_score +
                    0.15 * (1.0 - sensitivity) +
                    0.15 * ncd_score)
            
            results.append({
                'candidate': cand,
                'score': float(score),
                'reasoning': f"Dynamics conv={dynamics['convergence']:.2f} stab={dynamics['stability']:.2f}, Core={core_score:.2f}, Sens={sensitivity:.2f}"
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 for prompt-answer pair"""
        meta_cap = self._meta_confidence(prompt)
        
        prompt_props = self._parse_props(prompt)
        answer_props = self._parse_props(answer)
        
        if len(prompt_props) == 0 or len(answer_props) == 0:
            return min(0.25, meta_cap)
        
        affinity = self._affinity(answer_props, prompt_props)
        dynamics = self._state_dynamics(answer_props, prompt_props)
        
        base_conf = 0.5 * affinity + 0.5 * dynamics['convergence']
        
        return min(base_conf * 0.85, meta_cap)
```

</details>
