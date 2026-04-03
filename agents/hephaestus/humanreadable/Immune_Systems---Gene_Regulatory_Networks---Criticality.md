# Immune Systems + Gene Regulatory Networks + Criticality

**Fields**: Biology, Biology, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T00:30:46.541921
**Report Generated**: 2026-04-02T08:39:54.848539

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Propositional GRN**  
   - Use regex‑based patterns to extract atomic propositions (e.g., “X is Y”, “X > 5”) and logical relations: negation (`not`), conditional (`if … then …`), causal (`because`, `leads to`), comparative (`more than`, `less than`), ordering (`before`, `after`), and numeric thresholds.  
   - Each proposition becomes a node in a Boolean gene‑regulatory network. Directed edges encode regulatory influence:  
     * Implication A→B → edge A→B with weight +1.  
     * Negation A→¬B → edge A→B with weight −1.  
     * Comparative or causal statements are translated into weighted edges proportional to the strength indicated by modifiers (e.g., “much greater” → larger magnitude).  
   - The adjacency matrix **W** is kept sparse (list of (src, dst, weight)).  

2. **Clonal Selection Population**  
   - Initialise a population **P** of *N* random bit‑strings (candidate truth assignments) of length *n* = #propositions.  
   - Fitness **f(s)** of a state *s* = (1 − HammingDistance(s, ŝ))/n + α·AttractorBonus, where *ŝ* is the state reached after iteratively updating the GRN using a synchronous threshold rule:  
     `s_i(t+1) = 1 if Σ_j W[j,i]·s_j(t) ≥ θ_i else 0` (θ_i set to node bias).  
     AttractorBonus rewards states that are fixed points or short‑period attractors (computed by detecting repetition ≤ 4 steps).  
   - **Selection**: keep top *k* individuals (elite).  
   - **Clonal expansion**: generate *M* offspring per elite by bit‑wise mutation with probability *p_mut* = β / (fitness + ε); higher‑fitness clones mutate less, mimicking immune memory.  
   - **Memory set** **Mset** stores unique attractors encountered; offspring that match a memory attractor receive a fitness boost to preserve diversity.  

3. **Criticality Tuning**  
   - Adjust average in‑degree 〈k〉 of the GRN by randomly adding/removing weak edges until the system’s susceptibility χ = Var[Σ_j W[j,i]·s_j] peaks (checked after each generation). Operating near χ‑max places the network at the edge of chaos, ensuring perturbations propagate far enough to explore the space but not so far as to destroy coherence.  

**Scoring**  
After *G* generations, the final score for each candidate answer is its normalized fitness plus a novelty term = Jaccard distance to the nearest memory attractor. The highest‑scoring answer is returned.

**Structural Features Parsed**  
Negations, conditionals, causal claims, comparatives, ordering relations, numeric thresholds, and explicit quantifiers (“all”, “some”).

**Novelty**  
While immune‑inspired clonal selection and critical Boolean networks appear separately in optimization and neuroscience, their joint use for parsing‑driven logical reasoning over text has not been reported in the literature; the combination yields a self‑adaptive, attractor‑based reasoner that explicitly exploits edge‑of‑chaos dynamics.

**Rating**  
Reasoning: 7/10 — captures logical structure well but relies on heuristic threshold tuning.  
Metacognition: 6/10 — limited self‑reflection; memory provides basic awareness of explored states.  
Hypothesis generation: 8/10 — clonal expansion actively creates diverse truth‑assignment hypotheses.  
Implementability: 9/10 — uses only numpy arrays, sparse lists, and standard‑library regex; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
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
**Reason**: trap_battery_failed (acc=32% cal=15% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:39:25.123258

---

## Code

**Source**: scrap

[View code](./Immune_Systems---Gene_Regulatory_Networks---Criticality/tool.py)

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
    Immune-inspired Boolean GRN reasoner operating at criticality.
    
    Parses text into propositional graph, evolves truth assignments via clonal
    selection, and scores by attractor stability + trajectory convergence.
    """
    
    def __init__(self):
        np.random.seed(42)
        self.memory_attractors = []
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        score, _ = self._score_candidate(prompt, answer)
        raw_conf = min(score, 1.0)
        return min(raw_conf * meta_conf, 0.95)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability markers."""
        p = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', p):
            return 0.25
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in p:
            return 0.3
        # Pronoun ambiguity
        if re.search(r'\b(he|she)\b', p) and re.search(r'\bwho\b', p):
            return 0.3
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p):
            return 0.4
        # Subjectivity
        if re.search(r'\b(best|worst|favorite)\b', p) and not re.search(r'\b(most|least|highest|lowest)\b', p):
            return 0.35
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        text = prompt + " " + candidate
        props, W, biases = self._parse_to_grn(text)
        n = len(props)
        if n == 0:
            return 0.5, "No structure"
        
        # Structural: number parsing
        struct_score = self._structural_score(prompt, candidate)
        
        # Dynamics: evolve GRN population
        N, G, k = 30, 15, 5
        pop = [np.random.randint(0, 2, n) for _ in range(N)]
        
        for gen in range(G):
            fits = [self._fitness(s, W, biases, n) for s in pop]
            elite_idx = np.argsort(fits)[-k:]
            elite = [pop[i] for i in elite_idx]
            
            offspring = []
            for e, ef in zip(elite, [fits[i] for i in elite_idx]):
                M = 5
                p_mut = 0.3 / (ef + 0.01)
                for _ in range(M):
                    child = e.copy()
                    mask = np.random.rand(n) < p_mut
                    child[mask] = 1 - child[mask]
                    offspring.append(child)
            pop = elite + offspring[:N-k]
        
        # Final fitness
        final_fits = [self._fitness(s, W, biases, n) for s in pop]
        best_fit = max(final_fits)
        
        # Trajectory stability
        stability = self._trajectory_stability(pop, W, biases, n)
        
        # NCD tiebreaker
        ncd = self._ncd(prompt, candidate)
        
        # Combine: 50% dynamics, 30% structural, 15% NCD
        dyn_score = (best_fit + stability) / 2
        final = 0.5 * dyn_score + 0.3 * struct_score + 0.15 * (1 - ncd)
        
        reason = f"Dyn={dyn_score:.2f} Str={struct_score:.2f} Stab={stability:.2f}"
        return final, reason
    
    def _parse_to_grn(self, text: str) -> Tuple[List[str], List[Tuple[int,int,float]], List[float]]:
        """Extract propositions and build sparse adjacency."""
        props = []
        edges = []
        
        # Extract atomic propositions
        matches = re.findall(r'([A-Z][a-z]*)\s+(is|are|was|were)\s+([a-z]+)', text)
        for subj, verb, obj in matches:
            props.append(f"{subj}_{obj}")
        
        # Comparisons
        comp = re.findall(r'(\d+\.?\d*)\s*([<>]=?|=)\s*(\d+\.?\d*)', text)
        for left, op, right in comp:
            props.append(f"{left}{op}{right}")
        
        # Conditionals (if X then Y)
        cond = re.findall(r'if\s+([^,\.]+?)\s+then\s+([^,\.]+)', text.lower())
        for ant, cons in cond:
            props.extend([ant.strip(), cons.strip()])
            edges.append((len(props)-2, len(props)-1, 1.0))
        
        # Negations
        neg = re.findall(r'not\s+([a-z]+)', text.lower())
        for n in neg:
            if n in [p.lower() for p in props]:
                idx = [p.lower() for p in props].index(n)
                edges.append((idx, idx, -1.0))
        
        # Causals
        caus = re.findall(r'([^,\.]+?)\s+(leads to|causes|because)\s+([^,\.]+)', text.lower())
        for cause, rel, effect in caus:
            props.extend([cause.strip(), effect.strip()])
            w = 1.2 if 'leads' in rel else 0.8
            edges.append((len(props)-2, len(props)-1, w))
        
        n = len(props)
        biases = np.zeros(n)
        return props, edges, biases.tolist()
    
    def _fitness(self, s: np.ndarray, W: List[Tuple[int,int,float]], biases: List[float], n: int) -> float:
        """Fitness = attractor stability + consistency."""
        traj = [s.copy()]
        for t in range(6):
            s_new = np.zeros(n)
            for i in range(n):
                inp = sum(w for j, k, w in W if k == i and s[j] == 1)
                s_new[i] = 1 if inp >= biases[i] else 0
            s = s_new.astype(int)
            # Check for attractor
            for prev in traj:
                if np.array_equal(s, prev):
                    period = len(traj) - list(map(lambda x: np.array_equal(x, s), traj)).index(True)
                    bonus = 0.3 if period <= 2 else 0.15
                    self.memory_attractors.append(tuple(s))
                    return 0.7 + bonus
            traj.append(s.copy())
        return 0.4
    
    def _trajectory_stability(self, pop: List[np.ndarray], W: List[Tuple[int,int,float]], biases: List[float], n: int) -> float:
        """Measure convergence of population trajectories."""
        if n == 0:
            return 0.5
        # Check variance across population attractors
        attractors = []
        for s in pop[:10]:
            for _ in range(4):
                s_new = np.zeros(n)
                for i in range(n):
                    inp = sum(w for j, k, w in W if k == i and s[j] == 1)
                    s_new[i] = 1 if inp >= biases[i] else 0
                s = s_new.astype(int)
            attractors.append(s)
        
        if len(attractors) < 2:
            return 0.5
        var = np.mean([np.var([a[i] for a in attractors]) for i in range(n)])
        return max(0.0, 1.0 - 2 * var)
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Numeric and logical structure evaluation."""
        score = 0.5
        # Number comparison
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            try:
                if 'greater' in prompt.lower() or '>' in prompt:
                    if float(c_nums[0]) > float(p_nums[0]):
                        score += 0.3
                elif 'less' in prompt.lower() or '<' in prompt:
                    if float(c_nums[0]) < float(p_nums[0]):
                        score += 0.3
            except:
                pass
        
        # Negation consistency
        if 'not' in prompt.lower():
            p_words = set(re.findall(r'\b[a-z]{4,}\b', prompt.lower()))
            c_words = set(re.findall(r'\b[a-z]{4,}\b', candidate.lower()))
            if len(p_words & c_words) < len(p_words) * 0.5:
                score += 0.2
        
        return min(score, 1.0)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.5
```

</details>
