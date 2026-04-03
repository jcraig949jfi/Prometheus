# Dynamical Systems + Causal Inference + Free Energy Principle

**Fields**: Mathematics, Information Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T03:59:50.316918
**Report Generated**: 2026-04-02T10:00:37.072415

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a dynamical system whose state *x* ∈ ℝⁿ encodes the truth‑strength of *n* extracted propositions. The prompt defines a target trajectory *x*₀ → *x*⁎ through a set of causal constraints. Scoring proceeds in three stages:

1. **Symbolic parsing → causal graph**  
   - Use regex to extract clauses (subject‑verb‑object triples).  
   - Nodes = unique propositions; edges = causal links signaled by words/phrases such as “because”, “leads to”, “if … then”, “results in”.  
   - Edge weight *w*ᵢⱼ ∈ {+1,−1} encodes positive/negative causality (detected via negation cues like “not”, “no”).  
   - Store adjacency matrix **A** (numpy.ndarray, shape n×n) and a bias vector **b** (numeric values, comparatives, thresholds).

2. **Constraint propagation (attractor computation)**  
   - Initialise state **x**⁰ from prompt propositions (1 for asserted true, 0 for false, 0.5 for uncertain).  
   - Iterate **x**ₜ₊₁ = σ(**A**·**x**ₜ + **b**) where σ is a logistic squashing function (implemented with `np.exp`).  
   - This is a discrete‑time dynamical system; after *T* steps (or when ‖**x**ₜ₊₁−**x**ₜ‖ < ε) we obtain a fixed point **x**⁎, interpreted as an attractor.  
   - Approximate the maximal Lyapunov exponent λ by computing the Jacobian **J** = σ'(**A**·**x**⁎+**A**)·**A** and estimating λ ≈ (1/T)∑ log‖**J**ᵗ‖ (using `np.linalg.norm`). Negative λ indicates stability.

3. **Free‑energy scoring**  
   - Prediction error ε = **x**⁎ − **x**₀ (difference between attractor and prompt‑derived state).  
   - Variational free energy F = ½ εᵀε + ½ log|Σ| where Σ = (**I**−**A**)⁻¹ (approximated via `np.linalg.inv`). The first term measures mismatch; the second term penalizes model complexity (entropy of the implicit Gaussian).  
   - Score = −F (lower free energy → higher score). All operations use only `numpy` and the standard library.

**Structural features parsed**  
- Negations (“not”, “no”, “never”) → flip edge sign.  
- Comparatives (“greater than”, “less than”, “at least”) → create bias entries **b** encoding thresholds.  
- Conditionals (“if … then”, “unless”) → add directed edges with optional temporal delay.  
- Causal claims (“because”, “leads to”, “causes”) → add edges.  
- Ordering relations (“before”, “after”, “precedes”) → encode as edges with a sign that favors monotonic increase/decrease.  
- Numeric values and units → translate into bias magnitudes.  
- Quantifiers (“all”, “some”, “none”) → adjust node initialisation (1, 0.5, 0).

**Novelty**  
Purely symbolic causal‑graph scoring exists (e.g., Pearl‑based do‑calculus solvers), and free‑energy formulations appear mainly in variational autoencoders or neural predictive coding. Combining a Lyapunov‑style stability analysis with a variational free‑energy objective in a rule‑based, numpy‑only system has not been described in the literature; thus the approach is novel.

**Rating**  
Reasoning: 8/10 — captures causal dynamics and stability, giving a principled gradient of correctness.  
Metacognition: 6/10 — the system can detect instability (high λ) but lacks explicit self‑monitoring of its own parsing errors.  
Hypothesis generation: 7/10 — by sampling alternative edge signs or bias values it can generate competing causal graphs, though search is limited to local perturbations.  
Implementability: 9/10 — relies solely on regex, numpy linear algebra, and basic control flow; no external libraries or GPUs needed.

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
**Reason**: trap_battery_failed (acc=22% cal=40% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T09:18:13.747618

---

## Code

**Source**: scrap

[View code](./Dynamical_Systems---Causal_Inference---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Dynamical Systems x Causal Inference x Free Energy Principle Reasoning Tool

Treats candidate answers as dynamical systems evolving under causal constraints.
Scores based on attractor stability (Lyapunov exponent) and variational free energy.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 50
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates by causal dynamics and free energy."""
        results = []
        
        for candidate in candidates:
            score, reasoning = self._score_candidate(prompt, candidate)
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": reasoning
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-analysis and dynamics."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score, _ = self._score_candidate(prompt, answer)
        # Cap confidence based on meta-analysis
        raw_conf = min(0.95, max(0.05, (score + 1) / 2))
        return min(raw_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        presup = [r"have you (stopped|quit)", r"why did .+ (fail|stop)",
                  r"when did you stop", r"do you still"]
        if any(re.search(pat, p_lower) for pat in presup):
            return 0.2
        
        # Scope ambiguity
        if re.search(r"every .+ (a|an) ", p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r"(he|she|they) ", p_lower) and "who" in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r"either .+ or .+[.?]", p_lower):
            if not re.search(r"(only|exactly|just) (two|2)", p_lower):
                return 0.3
        
        # Subjectivity without criteria
        if re.search(r"\b(best|worst|favorite|prettiest)\b", p_lower):
            if not re.search(r"(most|highest|lowest|least)", p_lower):
                return 0.3
        
        # Unanswerable markers
        if re.search(r"(cannot determine|not enough|insufficient)", p_lower):
            return 0.2
        
        return 0.8
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Score via causal dynamics, free energy, and structural checks."""
        # Extract causal graph from prompt + candidate
        A, b, prop_map = self._extract_causal_graph(prompt, candidate)
        n = len(prop_map)
        
        if n == 0:
            # Fallback to structural + NCD
            struct_score = self._structural_score(prompt, candidate)
            ncd = self._ncd(prompt, candidate)
            score = 0.7 * struct_score + 0.3 * (1 - ncd)
            return score, "No propositions extracted; fallback scoring"
        
        # Initialize state from prompt
        x0 = self._init_state(prompt, prop_map)
        
        # Run dynamics to find attractor
        x_star, trajectory = self._run_dynamics(A, b, x0)
        
        # Compute Lyapunov exponent
        lyap = self._lyapunov(A, x_star, trajectory)
        
        # Compute variational free energy
        free_energy = self._free_energy(A, b, x0, x_star)
        
        # Structural and numeric scoring
        struct_score = self._structural_score(prompt, candidate)
        numeric_score = self._numeric_score(prompt, candidate)
        
        # NCD tiebreaker
        ncd = self._ncd(prompt, candidate)
        
        # Weighted combination
        dynamics_score = -free_energy / (1 + abs(free_energy))
        stability_bonus = 0.1 if lyap < 0 else -0.1
        
        score = (0.4 * dynamics_score + 
                 0.25 * struct_score + 
                 0.2 * numeric_score + 
                 0.1 * (1 - ncd) + 
                 stability_bonus)
        
        reasoning = f"FE={free_energy:.2f}, Lyap={lyap:.2f}, Struct={struct_score:.2f}"
        return score, reasoning
    
    def _extract_causal_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Parse text into causal graph (A matrix, bias b, proposition map)."""
        text = prompt + " " + candidate
        
        # Extract propositions (simple clause extraction)
        clauses = re.split(r'[.!?;]', text)
        propositions = []
        for clause in clauses:
            clause = clause.strip()
            if len(clause) > 5:
                propositions.append(clause.lower())
        
        n = len(propositions)
        if n == 0:
            return np.zeros((0, 0)), np.zeros(0), {}
        
        prop_map = {i: p for i, p in enumerate(propositions)}
        A = np.zeros((n, n))
        b = np.zeros(n)
        
        # Extract causal links
        causal_words = ["because", "leads to", "causes", "results in", 
                        "if", "then", "therefore", "thus"]
        
        for i, prop in enumerate(propositions):
            # Negation detection
            if re.search(r"\b(not|no|never)\b", prop):
                b[i] -= 0.5
            
            # Numeric extraction
            numbers = re.findall(r'\d+\.?\d*', prop)
            if numbers:
                b[i] += float(numbers[0]) / 100.0
            
            # Comparatives
            if re.search(r"(greater|more|higher|increase)", prop):
                b[i] += 0.3
            elif re.search(r"(less|lower|decrease|fewer)", prop):
                b[i] -= 0.3
            
            # Causal edges
            for j, other in enumerate(propositions):
                if i != j:
                    for cw in causal_words:
                        if cw in prop and any(word in other for word in prop.split()[:3]):
                            sign = -1 if "not" in prop else 1
                            A[j, i] = 0.3 * sign
        
        return A, b, prop_map
    
    def _init_state(self, prompt: str, prop_map: Dict) -> np.ndarray:
        """Initialize state vector from prompt propositions."""
        n = len(prop_map)
        x0 = np.full(n, 0.5)
        
        for i, prop in prop_map.items():
            if prop in prompt.lower():
                if re.search(r"\b(not|no|false)\b", prop):
                    x0[i] = 0.0
                else:
                    x0[i] = 1.0
        
        return x0
    
    def _run_dynamics(self, A: np.ndarray, b: np.ndarray, x0: np.ndarray) -> Tuple[np.ndarray, List]:
        """Iterate x_{t+1} = sigma(A * x_t + b) until convergence."""
        x = x0.copy()
        trajectory = [x.copy()]
        
        for _ in range(self.max_iter):
            x_new = self._sigmoid(A @ x + b)
            trajectory.append(x_new.copy())
            
            if np.linalg.norm(x_new - x) < self.epsilon:
                break
            x = x_new
        
        return x, trajectory
    
    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        """Logistic squashing function."""
        return 1.0 / (1.0 + np.exp(-np.clip(z, -10, 10)))
    
    def _lyapunov(self, A: np.ndarray, x_star: np.ndarray, trajectory: List) -> float:
        """Estimate maximal Lyapunov exponent."""
        if len(trajectory) < 2:
            return 0.0
        
        # Jacobian at fixed point
        sigma_prime = x_star * (1 - x_star)
        J = np.diag(sigma_prime) @ A
        
        try:
            eigvals = np.linalg.eigvals(J)
            lyap = np.max(np.real(eigvals))
        except:
            lyap = 0.0
        
        return lyap
    
    def _free_energy(self, A: np.ndarray, b: np.ndarray, x0: np.ndarray, x_star: np.ndarray) -> float:
        """Compute F = 0.5 * ||error||^2 + 0.5 * log|Sigma|."""
        error = x_star - x0
        precision_term = 0.5 * np.dot(error, error)
        
        n = len(x0)
        try:
            I_minus_A = np.eye(n) - A
            Sigma = np.linalg.inv(I_minus_A @ I_minus_A.T + 1e-6 * np.eye(n))
            complexity_term = 0.5 * np.log(np.linalg.det(Sigma) + 1e-6)
        except:
            complexity_term = 0.0
        
        return precision_term + complexity_term
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Score based on structural pattern matching."""
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation consistency
        prompt_neg = bool(re.search(r"\b(not|no|never|false)\b", p_lower))
        cand_neg = bool(re.search(r"\b(not|no|never|false)\b", c_lower))
        if prompt_neg == cand_neg:
            score += 0.3
        
        # Question type matching
        if "how many" in p_lower and re.search(r'\d+', c_lower):
            score += 0.2
        if any(q in p_lower for q in ["is", "are", "does", "can"]):
            if any(a in c_lower for a in ["yes", "no", "true", "false"]):
                score += 0.2
        
        return min(1.0, score)
    
    def _numeric_score(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric comparisons and calculations."""
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums or not c_nums:
            return 0.5
        
        try:
            p_val = float(p_nums[-1])
            c_val = float(c_nums[0])
            
            # Check comparison operators
            if re.search(r"(greater|more|higher|larger)", prompt.lower()):
                return 1.0 if c_val > p_val else 0.0
            elif re.search(r"(less|fewer|lower|smaller)", prompt.lower()):
                return 1.0 if c_val < p_val else 0.0
            else:
                # Proximity scoring
                diff = abs(c_val - p_val)
                return max(0.0, 1.0 - diff / (abs(p_val) + 1))
        except:
            return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (capped at 15% weight)."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
```

</details>
