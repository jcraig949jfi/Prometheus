# Reinforcement Learning + Neural Plasticity + Abductive Reasoning

**Fields**: Computer Science, Biology, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T06:00:42.553043
**Report Generated**: 2026-04-02T08:39:55.159855

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a hypothesis \(h_i\) encoded as a sparse binary vector \(\mathbf{x}_i\in\{0,1\}^D\) where each dimension corresponds to a propositional atom extracted from the prompt (e.g., “X > Y”, “¬Causes(A,B)”, “temp = 23”). A weight vector \(\mathbf{w}\in\mathbb{R}^D\) stores the current strength of each atom, initialized to zero.  

1. **Parsing & constraint propagation** – Using regex we extract atoms and binary relations (comparatives, conditionals, causal links). We build a Boolean adjacency matrix \(\mathbf{R}\) where \(R_{jk}=1\) if atom \(j\) entails atom \(k\) (e.g., from “if P then Q”). We compute the transitive closure of \(\mathbf{R}\) with Floyd‑Warshall (numpy `np.maximum.accumulate`) to obtain the implied‑atom matrix \(\mathbf{C}\). For each hypothesis we compute the set of satisfied atoms \(\mathbf{s}_i = \mathbf{x}_i \lor (\mathbf{x}_i @ \mathbf{C})\) (logical OR after matrix multiplication).  

2. **Reward signal** – A scalar reward \(r_i\) is the number of satisfied atoms minus a penalty for any atom whose negation also appears in \(\mathbf{s}_i\). This captures explanatory fit (abductive reasoning).  

3. **Weight update (policy gradient + Hebbian plasticity)** – Let \(\bar{r}\) be a running baseline (exponential moving average). The policy‑gradient step updates weights as  
\[
\mathbf{w} \leftarrow \mathbf{w} + \alpha\,(r_i-\bar{r})\,(\mathbf{x}_i-\mathbf{w}),
\]  
where \(\alpha\) is a small step size. Simultaneously, a Hebbian term reinforces co‑active atoms when reward is positive:  
\[
\mathbf{w} \leftarrow \mathbf{w} + \beta\,r_i\,(\mathbf{x}_i \mathbf{x}_i^\top)\mathbf{1},
\]  
with \(\beta\) ≪ \(\alpha\) and \(\mathbf{1}\) a vector of ones. Negative reward triggers synaptic‑like decay: \(\mathbf{w} \leftarrow \mathbf{w} \cdot \lambda\) (\(\lambda<1\)).  

4. **Scoring** – After processing all candidates, the final score for hypothesis \(i\) is the dot product \(\text{score}_i = \mathbf{x}_i \cdot \mathbf{w}\). Higher scores indicate better explanatory power under the learned weighting.  

**Structural features parsed** – negations (“not”, “¬”), comparatives (“>”, “<”, “≥”, “≤”), conditionals (“if … then …”, “unless”), causal keywords (“because”, “leads to”, “results in”), numeric values and units, ordering relations (“before”, “after”, “first”, “last”), and quantifiers (“all”, “some”, “none”).  

**Novelty** – The coupling of a reinforcement‑learning weight‑update rule with Hebbian‑style co‑activity modulation and abductive reward shaping does not appear verbatim in existing neuro‑symbolic or plasticity‑based RL works; it synthesizes three distinct mechanisms into a single scoring loop.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and explanatory fit via constraint propagation and reward‑driven weighting.  
Metacognition: 6/10 — includes a baseline and decay mechanism but lacks explicit self‑monitoring of uncertainty.  
Hypothesis generation: 7/10 — generates and updates hypothesis weights, though hypothesis space is limited to extracted atoms.  
Implementability: 9/10 — relies only on regex, NumPy matrix ops, and standard‑library containers; no external dependencies.

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
**Reason**: trap_battery_failed (acc=39% cal=3% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:11:48.113640

---

## Code

**Source**: scrap

[View code](./Reinforcement_Learning---Neural_Plasticity---Abductive_Reasoning/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Set, Tuple

"""
Reinforcement Learning x Neural Plasticity x Abductive Reasoning Tool

Combines RL weight updates, Hebbian co-activity modulation, and abductive scoring
to evaluate candidate answers against parsed propositional atoms and constraints.
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    def __init__(self):
        self.baseline_reward = 0.0
        self.alpha = 0.05  # policy gradient step size
        self.beta = 0.01   # Hebbian step size
        self.lambda_decay = 0.95
        self.ema_gamma = 0.7
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Extract atoms from prompt and candidates
        atoms, atom_to_idx = self._extract_atoms(prompt, candidates)
        D = len(atoms)
        
        if D == 0:
            return self._fallback_ncd(prompt, candidates)
        
        # Build implication matrix and transitive closure
        R = self._build_implications(atoms, atom_to_idx)
        C = self._transitive_closure(R)
        
        # Encode candidates as binary vectors
        hypothesis_vectors = []
        for cand in candidates:
            x = np.zeros(D, dtype=np.float32)
            for atom, idx in atom_to_idx.items():
                if self._atom_in_text(atom, cand):
                    x[idx] = 1.0
            hypothesis_vectors.append(x)
        
        # RL + Hebbian weight update
        w = np.zeros(D, dtype=np.float32)
        rewards = []
        
        for x_i in hypothesis_vectors:
            # Compute satisfied atoms via implication
            s_i = np.clip(x_i + (x_i @ C), 0, 1)
            r_i = self._compute_reward(s_i, atoms, prompt, candidates[len(rewards)])
            rewards.append(r_i)
            
            # Policy gradient update
            delta_r = r_i - self.baseline_reward
            w += self.alpha * delta_r * (x_i - w)
            
            # Hebbian reinforcement
            if r_i > 0:
                w += self.beta * r_i * (x_i * x_i @ np.ones(D))
            else:
                w *= self.lambda_decay
            
            # Update baseline
            self.baseline_reward = self.ema_gamma * self.baseline_reward + (1 - self.ema_gamma) * r_i
        
        # Score and rank
        results = []
        for i, cand in enumerate(candidates):
            rl_score = float(hypothesis_vectors[i] @ w)
            comp_score = self._computational_score(prompt, cand)
            ncd_score = self._ncd(prompt, cand)
            
            final_score = 0.55 * rl_score + 0.35 * comp_score + 0.10 * ncd_score
            
            reasoning = f"RL:{rl_score:.2f} Comp:{comp_score:.2f} NCD:{ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        comp_conf = self._computational_confidence(prompt, answer)
        return min(meta_conf, comp_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you|did you).*(stop|quit|cease)', p_lower):
            return 0.2
        if re.search(r'\bwhy (did|does|is).*(fail|stop|wrong)', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\b(every|each|all)\b.*\ba\b', p_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either|must be).*(or)\b', p_lower):
            return 0.35
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)', p_lower):
            return 0.3
        
        # Unanswerability markers
        if re.search(r'\b(cannot determine|not enough|insufficient)', p_lower):
            return 0.2
        
        return 0.8
    
    def _extract_atoms(self, prompt: str, candidates: List[str]) -> Tuple[List[str], Dict[str, int]]:
        atoms = set()
        text = prompt + " " + " ".join(candidates)
        
        # Numeric comparisons
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|=|==)\s*(\w+)', text):
            atoms.add(f"{m.group(1)}{m.group(2)}{m.group(3)}")
        
        # Negations
        for m in re.finditer(r'\b(not|no|never)\s+(\w+)', text):
            atoms.add(f"NOT_{m.group(2)}")
        
        # Causal links
        for m in re.finditer(r'(\w+)\s+(causes?|leads? to|results? in)\s+(\w+)', text):
            atoms.add(f"{m.group(1)}_CAUSES_{m.group(3)}")
        
        # Temporal ordering
        for m in re.finditer(r'(\w+)\s+(before|after)\s+(\w+)', text):
            atoms.add(f"{m.group(1)}_{m.group(2).upper()}_{m.group(3)}")
        
        # Extract key nouns and verbs
        words = re.findall(r'\b[A-Za-z]{4,}\b', text)
        atoms.update(words[:20])  # Limit to avoid explosion
        
        atom_list = sorted(list(atoms))
        atom_to_idx = {a: i for i, a in enumerate(atom_list)}
        return atom_list, atom_to_idx
    
    def _atom_in_text(self, atom: str, text: str) -> bool:
        return atom.lower() in text.lower()
    
    def _build_implications(self, atoms: List[str], atom_to_idx: Dict[str, int]) -> np.ndarray:
        D = len(atoms)
        R = np.eye(D, dtype=np.float32)
        
        # If-then implications
        for i, a1 in enumerate(atoms):
            for j, a2 in enumerate(atoms):
                if i != j:
                    # Simple heuristic: atoms with shared prefix imply each other
                    if len(a1) > 3 and len(a2) > 3 and a1[:3] == a2[:3]:
                        R[i, j] = 1.0
        
        return R
    
    def _transitive_closure(self, R: np.ndarray) -> np.ndarray:
        n = R.shape[0]
        C = R.copy()
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    C[i, j] = max(C[i, j], min(C[i, k], C[k, j]))
        return C
    
    def _compute_reward(self, s_i: np.ndarray, atoms: List[str], prompt: str, candidate: str) -> float:
        satisfied = np.sum(s_i)
        
        # Penalty for contradictions
        contradiction_penalty = 0
        for i, atom in enumerate(atoms):
            if s_i[i] > 0 and atom.startswith("NOT_"):
                base = atom[4:]
                for j, other in enumerate(atoms):
                    if other == base and s_i[j] > 0:
                        contradiction_penalty += 1
        
        return satisfied - contradiction_penalty
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        score = 0.0
        
        # Numeric comparison
        nc = self._parse_numeric_comparison(prompt, candidate)
        if nc is not None:
            score += 1.0 if nc else -0.5
        
        # Algebra (bat-and-ball)
        alg = self._parse_algebra(prompt, candidate)
        if alg is not None:
            score += 1.0 if alg else -0.5
        
        # Bayesian
        bay = self._parse_bayesian(prompt, candidate)
        if bay is not None:
            score += 1.0 if bay else -0.5
        
        # Logic
        log = self._parse_logic(prompt, candidate)
        if log is not None:
            score += 1.0 if log else -0.5
        
        return max(0, score)
    
    def _parse_numeric_comparison(self, prompt: str, candidate: str) -> bool:
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) >= 2:
            try:
                a, b = float(nums[0]), float(nums[1])
                if re.search(r'(which|what).*(larger|greater|more)', prompt.lower()):
                    expected = str(max(a, b))
                    return expected in candidate
                elif re.search(r'(which|what).*(smaller|less)', prompt.lower()):
                    expected = str(min(a, b))
                    return expected in candidate
            except:
                pass
        return None
    
    def _parse_algebra(self, prompt: str, candidate: str) -> bool:
        # Bat and ball: total $X, bat costs $Y more, ball costs?
        match = re.search(r'total.*\$?(\d+\.?\d*).*costs?\s*\$?(\d+\.?\d*)\s*more', prompt.lower())
        if match:
            try:
                total = float(match.group(1))
                diff = float(match.group(2))
                ball = (total - diff) / 2
                bat = ball + diff
                cand_nums = re.findall(r'\d+\.?\d*', candidate)
                if cand_nums:
                    cand_val = float(cand_nums[0])
                    return abs(cand_val - ball) < 0.01 or abs(cand_val - bat) < 0.01
            except:
                pass
        return None
    
    def _parse_bayesian(self, prompt: str, candidate: str) -> bool:
        # Simple base rate: P(disease)=X%, P(pos|disease)=Y%, P(pos|healthy)=Z%, prob disease given pos?
        match = re.search(r'(\d+)%.*?(\d+)%.*?(\d+)%', prompt)
        if match and re.search(r'probability|likely|chance', prompt.lower()):
            try:
                prior = float(match.group(1)) / 100
                sens = float(match.group(2)) / 100
                fpr = float(match.group(3)) / 100
                posterior = (prior * sens) / (prior * sens + (1 - prior) * fpr)
                cand_nums = re.findall(r'\d+\.?\d*', candidate)
                if cand_nums:
                    cand_val = float(cand_nums[0])
                    if cand_val > 1:
                        cand_val /= 100
                    return abs(cand_val - posterior) < 0.1
            except:
                pass
        return None
    
    def _parse_logic(self, prompt: str, candidate: str) -> bool:
        # Modus tollens: If P then Q, not Q, therefore not P
        if re.search(r'if\s+(\w+).*then\s+(\w+)', prompt.lower()):
            match = re.search(r'if\s+(\w+).*then\s+(\w+)', prompt.lower())
            if match and re.search(r'not\s+' + match.group(2), prompt.lower()):
                if re.search(r'not\s+' + match.group(1), candidate.lower()):
                    return True
        return None
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        comp_score = self._computational_score(prompt, answer)
        if comp_score > 0.5:
            return 0.85
        elif comp_score < -0.3:
            return 0.15
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        import zlib
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return 1.0 - (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _fallback_ncd(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._ncd(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": "NCD_fallback"})
        return sorted(results, key=lambda x: x["score"], reverse=True)
```

</details>
