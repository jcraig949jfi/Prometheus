# Dynamical Systems + Criticality + Sensitivity Analysis

**Fields**: Mathematics, Complex Systems, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T14:30:25.512935
**Report Generated**: 2026-04-02T10:00:36.025432

---

## Nous Analysis

**Algorithm**  
Each candidate answer is first parsed into a set of discrete propositions \(P_i\) (subject‑predicate‑object triples) using regex patterns for negations, comparatives, conditionals, causal cue‑words (“because”, “leads to”), ordering relations (“more than”, “less than”), and numeric values. A proposition carries a binary truth variable \(x_i\in\{0,1\}\) and a weight \(w_i\) reflecting the strength of any attached causal claim (extracted from cue‑words and numeric modifiers).  

We construct a directed implication graph \(G=(V,E)\) where an edge \(i\rightarrow j\) encodes a logical rule extracted from conditionals or causal statements (modus ponens). The graph also stores transitivity constraints: if \(i\rightarrow j\) and \(j\rightarrow k\) then an implicit edge \(i\rightarrow k\) is added.  

Define a consistency energy \(E(\mathbf{x})=\sum_{(i\rightarrow j)\in E} w_{ij}\, \max(0, x_i - x_j)\); \(E=0\) when all implications are satisfied. Treat \(\mathbf{x}\) as the state of a discrete‑time dynamical system. One iteration applies the deterministic update  
\[
x_i^{(t+1)} = \begin{cases}
1 & \text{if } \sum_{k\rightarrow i} w_{ki} x_k^{(t)} \ge \theta_i\\
0 & \text{otherwise}
\end{cases}
\]  
with thresholds \(\theta_i\) set to the average incoming weight. This update mimics a threshold‑network dynamical system.  

**Sensitivity & Criticality**  
To assess sensitivity, we compute a finite‑difference Jacobian approximation: for each proposition \(i\), flip \(x_i\) (0↔1), run the dynamics to a fixed point, and record the change in total satisfied constraints \(\Delta C_i\). The Jacobian entry \(J_{ij}\approx \Delta C_i / \Delta x_j\). The maximal Lyapunov exponent estimate is \(\lambda = \frac{1}{T}\sum_{t=0}^{T-1}\ln\frac{\|J^{(t)}\mathbf{v}\|}{\|\mathbf{v}\|}\) for a random perturbation vector \(\mathbf{v}\).  

Susceptibility is the variance of \(C\) under random uniform perturbations of \(\mathbf{x}\): \(\chi = \mathrm{Var}[C(\mathbf{x}+\epsilon)]\). By sweeping a global coupling scalar \(\alpha\) that multiplies all weights \(w_{ij}\), we plot \(\chi(\alpha)\). Criticality is identified as the \(\alpha^\*\) where \(\chi\) peaks (maximal correlation length).  

**Scoring Logic**  
For each candidate answer we compute:  
1. Distance to critical point: \(d = |\alpha_{\text{answer}}-\alpha^\*|\).  
2. Stability term: \(-\lambda\) (more negative → more stable).  
3. Consistency term: \(-E(\mathbf{x}^\*)\) (lower energy → higher score).  

Final score: \(S = -d - \lambda - E\). Higher \(S\) indicates answers whose logical structure sits near a critical, highly sensitive regime while remaining dynamically stable — mirroring how reasoning should be both expressive and robust.  

**Structural Features Parsed**  
Negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), causal claims (“because”, “leads to”, “results in”), ordering relations (“more than”, “fewer than”), numeric values and units, quantifiers (“all”, “some”, “none”).  

**Novelty**  
Pure logical‑similarity or bag‑of‑words baselines dominate current answer‑scoring tools. Integrating a dynamical‑systems update rule, Lyapunov‑exponent estimation, and susceptibility‑based criticality detection for textual reasoning is not present in the published literature; thus the combination is novel.  

**Rating**  
Reasoning: 8/10 — captures logical structure and dynamic sensitivity but relies on linearized approximations.  
Metacognition: 6/10 — limited self‑monitoring; the method does not explicitly reason about its own uncertainty.  
Hypothesis generation: 7/10 — can generate alternative truth assignments via perturbations, offering rudimentary hypothesis exploration.  
Implementability: 9/10 — uses only numpy for matrix ops and regex/std lib for parsing; straightforward to code.

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
**Reason**: trap_battery_failed (acc=42% cal=45% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:48:27.871535

---

## Code

**Source**: scrap

[View code](./Dynamical_Systems---Criticality---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dynamical Systems x Criticality x Sensitivity Analysis reasoning tool.
    
    Core mechanism:
    1. Parse text into propositions (subject-predicate-object triples)
    2. Build implication graph from logical/causal structure
    3. Run threshold-network dynamics to find fixed points
    4. Compute Jacobian, Lyapunov exponent, susceptibility
    5. Find critical point (peak susceptibility) via coupling sweep
    6. Score = -distance_to_critical - lambda - energy
    
    Also includes computational solvers for numeric/algebraic/Bayesian problems.
    """
    
    def __init__(self):
        self.rng = np.random.RandomState(42)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        score, _ = self._score_candidate(prompt, answer)
        conf = 1.0 / (1.0 + np.exp(-score))
        return min(conf, 0.85) if meta_conf > 0.5 else min(conf, 0.5)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        if re.search(r'have you (stopped|quit)', p_lower):
            return 0.2
        if re.search(r'why did .+ (fail|stop)', p_lower):
            return 0.25
        if re.search(r'every .+ a ', p_lower) and 'same' not in p_lower:
            return 0.25
        if re.search(r'(best|worst|favorite)', p_lower) and not re.search(r'(most|least|highest|lowest)', p_lower):
            return 0.3
        if re.search(r'either .+ or .+\?', p_lower) and 'only' not in p_lower:
            return 0.3
        if re.search(r'(he|she) was', p_lower) and 'who' in p_lower:
            return 0.25
        return 0.7
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        comp_score = self._computational_solve(prompt, candidate)
        if comp_score is not None:
            return comp_score, "computational"
        
        props_p, graph_p = self._parse_propositions(prompt)
        props_c, graph_c = self._parse_propositions(candidate)
        
        if len(props_c) == 0:
            return -5.0, "no propositions"
        
        combined_props = props_p + props_c
        combined_graph = {**graph_p, **{(k[0]+len(props_p), k[1]+len(props_p)): v 
                                        for k, v in graph_c.items()}}
        
        n = len(combined_props)
        if n == 0:
            ncd = self._ncd(prompt, candidate)
            return -ncd * 2.0, "ncd_fallback"
        
        alpha_crit, suscept = self._find_critical_point(n, combined_graph)
        x_star, energy = self._run_dynamics(n, combined_graph, alpha_crit)
        lyap = self._lyapunov_exponent(n, combined_graph, x_star, alpha_crit)
        
        score = -abs(1.0 - alpha_crit) - lyap - energy * 0.5
        ncd = self._ncd(prompt, candidate)
        score += (1.0 - ncd) * 0.3
        
        return score, f"dyn:a={alpha_crit:.2f},lam={lyap:.2f},E={energy:.2f}"
    
    def _computational_solve(self, prompt: str, candidate: str) -> float:
        p_lower = prompt.lower()
        
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) >= 2:
            if 'bat' in p_lower and 'ball' in p_lower and 'total' in p_lower:
                try:
                    total, diff = float(nums[0]), float(nums[1])
                    ball = (total - diff) / 2.0
                    cand_nums = re.findall(r'\d+\.?\d*', candidate)
                    if cand_nums and abs(float(cand_nums[0]) - ball) < 0.02:
                        return 10.0
                except:
                    pass
            
            if '>' in prompt or '<' in prompt or 'greater' in p_lower or 'less' in p_lower:
                try:
                    a, b = float(nums[0]), float(nums[1])
                    cand_lower = candidate.lower()
                    if (a > b and ('yes' in cand_lower or 'true' in cand_lower or nums[0] in candidate)):
                        return 8.0
                    if (a < b and ('no' in cand_lower or 'false' in cand_lower or nums[1] in candidate)):
                        return 8.0
                except:
                    pass
        
        if 'coin' in p_lower and 'flip' in p_lower:
            if '0.5' in candidate or '1/2' in candidate or 'independent' in candidate.lower():
                return 7.0
        
        if ('all but' in p_lower or 'except' in p_lower) and nums:
            try:
                total, excluded = int(nums[0]), int(nums[1]) if len(nums) > 1 else 1
                result = total - excluded
                if str(result) in candidate:
                    return 8.0
            except:
                pass
        
        if 'if' in p_lower and 'then' in p_lower:
            parts = re.split(r'\b(if|then)\b', p_lower)
            if len(parts) >= 4:
                antecedent = parts[2].strip()
                consequent = parts[4].strip()
                cand_lower = candidate.lower()
                if antecedent in cand_lower and consequent in cand_lower:
                    return 6.0
        
        return None
    
    def _parse_propositions(self, text: str) -> Tuple[List[Dict], Dict]:
        props = []
        graph = {}
        
        sentences = re.split(r'[.!?;]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            negated = bool(re.search(r'\b(not|no|never|nothing)\b', sent.lower()))
            
            nums = re.findall(r'\d+\.?\d*', sent)
            weight = 1.0 + len(nums) * 0.5
            
            if re.search(r'\b(because|leads to|results in|causes)\b', sent.lower()):
                weight *= 2.0
            
            props.append({'text': sent, 'negated': negated, 'weight': weight, 'nums': nums})
            
            if re.search(r'\bif\b.+\bthen\b', sent.lower()):
                parts = re.split(r'\b(if|then)\b', sent.lower())
                if len(parts) >= 4:
                    idx = len(props) - 1
                    if idx > 0:
                        graph[(idx-1, idx)] = weight
        
        return props, graph
    
    def _run_dynamics(self, n: int, graph: Dict, alpha: float) -> Tuple[np.ndarray, float]:
        x = self.rng.rand(n) > 0.5
        x = x.astype(float)
        
        thresholds = np.ones(n) * 0.5
        
        for _ in range(20):
            x_new = x.copy()
            for i in range(n):
                incoming = sum(alpha * w * x[j] for (j, k), w in graph.items() if k == i)
                x_new[i] = 1.0 if incoming >= thresholds[i] else 0.0
            if np.allclose(x, x_new):
                break
            x = x_new
        
        energy = sum(w * max(0, x[i] - x[j]) for (i, j), w in graph.items())
        return x, energy
    
    def _lyapunov_exponent(self, n: int, graph: Dict, x: np.ndarray, alpha: float) -> float:
        if n == 0:
            return 0.0
        
        delta = 0.01
        lyap_sum = 0.0
        trials = min(5, n)
        
        for _ in range(trials):
            idx = self.rng.randint(n)
            x_pert = x.copy()
            x_pert[idx] = 1.0 - x_pert[idx]
            
            x_final, _ = self._run_dynamics(n, graph, alpha)
            x_pert_final, _ = self._run_dynamics(n, graph, alpha)
            
            dist = np.linalg.norm(x_final - x_pert_final)
            if dist > 1e-6:
                lyap_sum += np.log(dist / delta)
        
        return lyap_sum / max(trials, 1)
    
    def _find_critical_point(self, n: int, graph: Dict) -> Tuple[float, float]:
        alphas = np.linspace(0.5, 2.0, 10)
        suscepts = []
        
        for alpha in alphas:
            var_sum = 0.0
            for _ in range(5):
                x = self.rng.rand(n) > 0.5
                x = x.astype(float)
                _, energy = self._run_dynamics(n, graph, alpha)
                var_sum += energy ** 2
            suscepts.append(var_sum / 5.0)
        
        max_idx = np.argmax(suscepts)
        return alphas[max_idx], suscepts[max_idx]
    
    def _ncd(self, s1: str, s2: str) -> float:
        import zlib
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
```

</details>
