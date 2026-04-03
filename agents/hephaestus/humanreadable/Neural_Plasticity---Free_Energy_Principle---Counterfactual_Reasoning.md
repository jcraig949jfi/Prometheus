# Neural Plasticity + Free Energy Principle + Counterfactual Reasoning

**Fields**: Biology, Theoretical Neuroscience, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T16:03:23.162549
**Report Generated**: 2026-04-02T10:55:58.328207

---

## Nous Analysis

**Algorithm**  
The scorer builds a lightweight causal‑belief graph from the prompt and each candidate answer, then iteratively refines edge weights using a Hebbian‑style plasticity rule while minimizing a variational free‑energy proxy (prediction‑error squared).  

1. **Parsing → graph**  
   - Use regex to extract triples ⟨subject, relation, object⟩ where relation can be a verb, comparative, conditional (“if … then …”), negation, or numeric comparison.  
   - Each unique entity becomes a node *i*; each extracted triple creates a directed edge *i → j* labeled with the relation type.  
   - Store adjacency in a NumPy boolean matrix **A** (shape *n×n*) and a weight matrix **W** (same shape, init = 0.1).  

2. **Initial belief propagation (free‑energy step)**  
   - Assign each node an activation **a** ∈ [0,1] initialized from lexical priors (e.g., 0.5 for unknown, 1.0 for asserted facts).  
   - Compute predicted activation **â** = σ(**W**·**a**) where σ is a logistic sigmoid (implemented with `np.exp`).  
   - Free‑energy ≈ ½‖**a** − **â**‖² (numpy L2 norm).  

3. **Hebbian plasticity update**  
   - For each edge *i→j* present in **A**, compute Δ**W**₍ᵢⱼ₎ = η · (aᵢ·aⱼ − λ · **W**₍ᵢⱼ₎) with learning rate η=0.01 and decay λ=0.001.  
   - Update **W** ← **W** + Δ**W**; repeat steps 2‑3 for *T*=3 iterations (enough for error to settle).  

4. **Counterfactual scoring**  
   - For a candidate answer, identify the antecedent clause *C* (e.g., “if X were Y”).  
   - Perform a *do*‑operation by clamping the node(s) representing *C* to the counterfactual value and re‑running steps 2‑3, yielding activation **a**ᶜᶠ.  
   - Counterfactual impact = ‖**a** − **a**ᶜᶠ‖₂.  
   - Final score = free‑energy after observation − α·counterfactual impact (α=0.5). Lower score ⇒ better answer.  

**Structural features parsed**  
- Negations (“not”, “no”) → edge label *¬*.  
- Comparatives (“greater than”, “less than”) → numeric relation edges with magnitude.  
- Conditionals (“if … then …”) → directed edges with a *do*‑flag.  
- Causal verbs (“cause”, “lead to”, “result in”) → causal edges.  
- Ordering/temporal markers (“before”, “after”) → temporal edges.  
- Numeric values and units → node attributes used in comparative checks.  

**Novelty**  
Purely algorithmic tools that combine Hebbian weight updates, variational free‑energy minimization, and explicit do‑calculus counterfactuals are uncommon. Predictive‑coding networks implement similar ideas but rely on neural layers; here the same principles are expressed with NumPy matrices and explicit graph operations, making the combination novel for a lightweight reasoning scorer.  

**Ratings**  
Reasoning: 7/10 — captures causal and counterfactual structure but limited depth of inference.  
Metacognition: 5/10 — no explicit self‑monitoring of uncertainty beyond free‑energy.  
Hypothesis generation: 6/10 — generates alternative activations via clamping, modestly exploratory.  
Implementability: 9/10 — relies only on regex, NumPy, and basic loops; easy to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=45% cal=5% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T10:17:18.297778

---

## Code

**Source**: scrap

[View code](./Neural_Plasticity---Free_Energy_Principle---Counterfactual_Reasoning/tool.py)

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
    Neural Plasticity x Free Energy Principle x Counterfactual Reasoning
    
    Builds a causal belief graph from text, updates edge weights via Hebbian
    plasticity while minimizing variational free energy (prediction error).
    Tracks state evolution dynamics and performs counterfactual interventions.
    Scores based on trajectory stability, convergence, and counterfactual impact.
    """
    
    def __init__(self):
        self.eta = 0.01  # Hebbian learning rate
        self.lam = 0.001  # weight decay
        self.alpha = 0.5  # counterfactual weight
        self.T = 3  # iterations
        
    def _extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract (subject, relation, object) triples from text."""
        text = text.lower()
        triples = []
        
        # Conditionals: if X then Y
        for m in re.finditer(r'if\s+([^,\.]+?)\s+then\s+([^,\.]+)', text):
            triples.append((m.group(1).strip(), 'conditional', m.group(2).strip()))
        
        # Causals: X causes/leads to Y
        for m in re.finditer(r'([^,\.]+?)\s+(cause|lead to|result in|produce)\s+([^,\.]+)', text):
            triples.append((m.group(1).strip(), 'causal', m.group(3).strip()))
        
        # Comparatives: X > Y, X less than Y
        for m in re.finditer(r'([0-9\.]+)\s*(>|<|greater than|less than)\s*([0-9\.]+)', text):
            triples.append((m.group(1), m.group(2), m.group(3)))
        
        # Negations: X is not Y
        for m in re.finditer(r'([a-z]+)\s+(?:is|are)\s+not\s+([a-z]+)', text):
            triples.append((m.group(1), 'not', m.group(2)))
        
        # Simple assertions: X is Y
        for m in re.finditer(r'([a-z]+)\s+(?:is|are)\s+([a-z]+)', text):
            if m.group(0) not in text:  # avoid duplicates with negation
                triples.append((m.group(1), 'is', m.group(2)))
        
        return triples
    
    def _build_graph(self, text: str) -> Tuple[np.ndarray, np.ndarray, Dict[str, int], List[str]]:
        """Build adjacency and weight matrices from text."""
        triples = self._extract_triples(text)
        entities = set()
        for s, r, o in triples:
            entities.add(s)
            entities.add(o)
        
        if not entities:
            # Fallback: extract words
            words = re.findall(r'\b[a-z]{3,}\b', text.lower())
            entities = set(words[:10])  # limit size
        
        entity_list = sorted(entities)
        entity_to_idx = {e: i for i, e in enumerate(entity_list)}
        n = len(entity_list)
        
        A = np.zeros((n, n), dtype=bool)
        W = np.ones((n, n)) * 0.1
        
        for s, r, o in triples:
            if s in entity_to_idx and o in entity_to_idx:
                i, j = entity_to_idx[s], entity_to_idx[o]
                A[i, j] = True
                if r == 'not':
                    W[i, j] = -0.5
                elif r in ('causal', 'conditional'):
                    W[i, j] = 0.8
        
        return A, W, entity_to_idx, entity_list
    
    def _free_energy_step(self, W: np.ndarray, a: np.ndarray) -> Tuple[float, np.ndarray]:
        """Compute free energy and predicted activations."""
        a_pred = 1.0 / (1.0 + np.exp(-W @ a))  # sigmoid
        free_energy = 0.5 * np.sum((a - a_pred) ** 2)
        return free_energy, a_pred
    
    def _hebbian_update(self, W: np.ndarray, A: np.ndarray, a: np.ndarray) -> np.ndarray:
        """Update weights via Hebbian plasticity."""
        dW = np.zeros_like(W)
        for i in range(W.shape[0]):
            for j in range(W.shape[1]):
                if A[i, j]:
                    dW[i, j] = self.eta * (a[i] * a[j] - self.lam * W[i, j])
        return W + dW
    
    def _evolve_dynamics(self, W: np.ndarray, A: np.ndarray, a_init: np.ndarray) -> Tuple[List[np.ndarray], List[float]]:
        """Track state evolution over iterations."""
        trajectory = [a_init.copy()]
        energies = []
        a = a_init.copy()
        
        for _ in range(self.T):
            fe, a_pred = self._free_energy_step(W, a)
            energies.append(fe)
            a = 0.7 * a + 0.3 * a_pred  # blend for stability
            W = self._hebbian_update(W, A, a)
            trajectory.append(a.copy())
        
        return trajectory, energies
    
    def _trajectory_stability(self, trajectory: List[np.ndarray]) -> float:
        """Compute stability as inverse of trajectory variance."""
        if len(trajectory) < 2:
            return 0.5
        deltas = [np.linalg.norm(trajectory[i+1] - trajectory[i]) for i in range(len(trajectory)-1)]
        return 1.0 / (1.0 + np.mean(deltas))
    
    def _counterfactual_impact(self, W: np.ndarray, A: np.ndarray, a: np.ndarray, entity_to_idx: Dict[str, int], text: str) -> float:
        """Perform counterfactual intervention and measure impact."""
        # Find counterfactual clause
        cf_match = re.search(r'if\s+([^,\.]+)', text.lower())
        if not cf_match:
            return 0.0
        
        cf_entity = cf_match.group(1).strip().split()[0]
        if cf_entity not in entity_to_idx:
            return 0.0
        
        idx = entity_to_idx[cf_entity]
        a_cf = a.copy()
        a_cf[idx] = 1.0 - a[idx]  # flip activation
        
        _, energies_orig = self._evolve_dynamics(W.copy(), A, a)
        _, energies_cf = self._evolve_dynamics(W.copy(), A, a_cf)
        
        impact = abs(energies_orig[-1] - energies_cf[-1])
        return impact
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'have you (stopped|quit|ceased)', p):
            return 0.2
        if re.search(r'why did .+ (fail|stop)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every .+ (a|an) ', p):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+(who|which)', p):
            return 0.3
        
        # False dichotomy
        if re.search(r'either .+ or ', p) and 'only' not in p:
            return 0.35
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p):
            return 0.4
        
        return 1.0  # no issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by dynamics-based score."""
        A_p, W_p, ent_p, _ = self._build_graph(prompt)
        n = A_p.shape[0]
        a_init = np.ones(n) * 0.5
        
        traj_p, energies_p = self._evolve_dynamics(W_p.copy(), A_p, a_init)
        
        results = []
        for cand in candidates:
            A_c, W_c, ent_c, _ = self._build_graph(prompt + ' ' + cand)
            n_c = A_c.shape[0]
            a_c = np.ones(n_c) * 0.5
            
            traj_c, energies_c = self._evolve_dynamics(W_c.copy(), A_c, a_c)
            
            # Dynamics score: trajectory stability + convergence
            stability = self._trajectory_stability(traj_c)
            convergence = 1.0 / (1.0 + energies_c[-1]) if energies_c else 0.5
            dynamics_score = 0.6 * stability + 0.4 * convergence
            
            # Counterfactual impact
            cf_impact = self._counterfactual_impact(W_c.copy(), A_c, a_c, ent_c, cand)
            
            # NCD tiebreaker
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Combined score
            score = 0.5 * dynamics_score + 0.35 * (1.0 / (1.0 + cf_impact)) + 0.15 * ncd_score
            
            results.append({
                'candidate': cand,
                'score': float(score),
                'reasoning': f'stability={stability:.2f}, fe={energies_c[-1]:.2f}, cf_impact={cf_impact:.2f}'
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and dynamics."""
        meta_conf = self._meta_confidence(prompt)
        
        A, W, ent, _ = self._build_graph(prompt + ' ' + answer)
        n = A.shape[0]
        if n == 0:
            return 0.2 * meta_conf
        
        a_init = np.ones(n) * 0.5
        traj, energies = self._evolve_dynamics(W.copy(), A, a_init)
        
        stability = self._trajectory_stability(traj)
        convergence = 1.0 / (1.0 + energies[-1]) if energies else 0.5
        
        dynamics_conf = 0.7 * stability + 0.3 * convergence
        
        # Cap by meta-confidence
        return min(dynamics_conf * 0.85, meta_conf)
```

</details>
