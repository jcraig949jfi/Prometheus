# Thermodynamics + Morphogenesis + Abductive Reasoning

**Fields**: Physics, Biology, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T14:47:47.018838
**Report Generated**: 2026-04-02T10:55:58.637204

---

## Nous Analysis

**Algorithm: Energy‑Diffusion Abduction Scorer (EDAS)**  

1. **Parsing & Graph Construction**  
   - Tokenize the prompt and each candidate answer with a rule‑based extractor (regex) that captures:  
     * atomic propositions (e.g., “X increases Y”),  
     * negations (`not`),  
     * comparatives (`greater than`, `less than`),  
     * conditionals (`if … then …`),  
     * causal verbs (`causes`, `leads to`),  
     * ordering relations (`before`, `after`),  
     * numeric values and units.  
   - Each proposition becomes a node in a directed hypergraph. Edges encode logical relations:  
     * **Implication edges** (if‑then) weight = 1.0,  
     * **Contradiction edges** (negation of same predicate) weight = –1.0,  
     * **Similarity edges** (shared entities, numeric proximity) weight = exp(−|Δ|/σ).  
   - Candidate answers are inserted as *hypothesis subgraphs* linked to the prompt graph via similarity edges.

2. **Energy Initialization (Thermodynamics)**  
   - Assign each node an initial “free energy” \(E_i = -\log P_i\) where \(P_i\) is a prior probability derived from term frequency in a small corpus (stdlib `collections.Counter`).  
   - For hypothesis nodes, add a penalty proportional to the number of unsupported literals (missing in prompt).

3. **Reaction‑Diffusion Update (Morphogenesis)**  
   - Treat energy as a concentration field. Iterate:  
     \[
     E_i^{(t+1)} = E_i^{(t)} + \alpha \sum_{j \in \mathcal{N}(i)} w_{ij}\,(E_j^{(t)} - E_i^{(t)}) - \beta \, \sigma\!\big(E_i^{(t)}\big)
     \]  
     where \(w_{ij}\) are edge weights, \(\alpha\) diffusion rate, \(\beta\) decay, and \(\sigma\) a sigmoid activator (local “reaction”).  
   - This is a discrete Turing‑style activator‑inhibitor system: high‑energy nodes (poor explanations) diffuse energy to neighbors, while low‑energy basins stabilize.

4. **Abductive Scoring**  
   - After convergence (ΔE < 1e‑4 or max 200 iterations), compute the hypothesis score as the average energy of its nodes:  
     \[
     S_{\text{hyp}} = \frac{1}{|H|}\sum_{i\in H} E_i^{(\infty)}
     \]  
   - Lower \(S_{\text{hyp}}\) indicates a better explanation (minimum free‑energy principle).  
   - Return normalized scores: \(\text{score}= \exp(-S_{\text{hyp}})\) for ranking.

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal claims, ordering relations, numeric values, and entity co‑occurrence. These are converted into weighted edges that drive diffusion.

**Novelty**  
Energy‑based scoring appears in Markov Logic Networks; reaction‑diffusion models Turing patterns; abduction is classic. Combining them into a single constraint‑propagation diffusion that directly optimizes explanatory free energy is not documented in mainstream NLP or AI‑reasoning surveys, making the approach novel.

---

Reasoning: 7/10 — The method captures logical structure and propagates constraints, but relies on hand‑crafted edge weights that may miss nuanced semantics.  
Metacognition: 6/10 — No explicit self‑monitoring of convergence quality; performance depends on fixed hyperparameters.  
Hypothesis generation: 8/10 — Energy minimization naturally yields competing explanations; the diffusion process surfaces low‑energy basins as candidate hypotheses.  
Implementability: 9/10 — Uses only numpy for matrix operations and stdlib for parsing; the core loop is straightforward to code and debug.

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
**Reason**: trap_battery_failed (acc=37% cal=0% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T10:07:24.759447

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Morphogenesis---Abductive_Reasoning/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import Counter
import zlib

class ReasoningTool:
    """Energy-Diffusion Abduction Scorer (EDAS)
    
    Combines thermodynamics (free energy), morphogenesis (reaction-diffusion),
    and abductive reasoning to score candidate answers. Parses logical structure
    into a hypergraph, assigns energy based on priors, runs diffusion dynamics,
    and scores by minimum free-energy principle.
    """
    
    def __init__(self):
        self.alpha = 0.3  # diffusion rate
        self.beta = 0.1   # decay rate
        self.max_iter = 200
        self.eps = 1e-4
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by abductive energy minimization."""
        results = []
        prompt_props = self._parse(prompt)
        
        for cand in candidates:
            cand_props = self._parse(cand)
            
            # Constructive computation score (primary)
            comp_score = self._compute_answer(prompt, cand, prompt_props, cand_props)
            
            # Structural score via energy diffusion
            struct_score = self._diffusion_score(prompt_props, cand_props)
            
            # NCD as minor tiebreaker
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted combination: 45% computation, 40% structure, 15% NCD
            final_score = 0.45 * comp_score + 0.40 * struct_score + 0.15 * ncd_score
            
            reasoning = f"comp={comp_score:.2f} struct={struct_score:.2f} ncd={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        props_p = self._parse(prompt)
        props_a = self._parse(answer)
        
        comp_score = self._compute_answer(prompt, answer, props_p, props_a)
        struct_score = self._diffusion_score(props_p, props_a)
        
        base_conf = 0.5 * comp_score + 0.5 * struct_score
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\b(every|each|all) .{1,30}\b(a|an)\b', p):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they|it)\b', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .* or|must be (a|b))\b', p) and '?' in p:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p) and not re.search(r'\b(by|according to|measured)\b', p):
            return 0.3
        
        # Insufficient information
        if re.search(r'\b(not enough|insufficient|cannot determine|missing)\b', p):
            return 0.2
        
        return 0.95
    
    def _parse(self, text: str):
        """Extract propositions: negations, conditionals, causals, comparatives, numerics."""
        props = {
            'negations': re.findall(r'\b(not|never|no|none|neither)\s+(\w+)', text.lower()),
            'conditionals': re.findall(r'\b(if|when|whenever)\s+(.{5,40}?)\s+(then|,)', text.lower()),
            'causals': re.findall(r'(\w+)\s+(causes?|leads? to|results? in|produces?)\s+(\w+)', text.lower()),
            'comparatives': re.findall(r'(\w+)\s+(greater|less|more|fewer|higher|lower)\s+than\s+(\w+)', text.lower()),
            'numbers': [(m.group(), float(m.group())) for m in re.finditer(r'\b\d+\.?\d*\b', text)],
            'entities': re.findall(r'\b[A-Z][a-z]+\b', text),
            'tokens': text.lower().split()
        }
        return props
    
    def _compute_answer(self, prompt: str, candidate: str, props_p, props_c):
        """Constructive computation: numeric, probabilistic, temporal, causal."""
        score = 0.0
        count = 0
        
        # Numeric comparison
        if props_p['numbers'] and props_c['numbers']:
            p_nums = [n[1] for n in props_p['numbers']]
            c_nums = [n[1] for n in props_c['numbers']]
            
            # Check if candidate numbers satisfy prompt comparatives
            for comp in props_p['comparatives']:
                for pn in p_nums:
                    for cn in c_nums:
                        if 'greater' in comp[1] or 'more' in comp[1] or 'higher' in comp[1]:
                            score += 1.0 if cn > pn else 0.0
                        elif 'less' in comp[1] or 'fewer' in comp[1] or 'lower' in comp[1]:
                            score += 1.0 if cn < pn else 0.0
                        count += 1
        
        # Bayesian probability (base rate)
        if re.search(r'\b(probability|percent|rate|base rate)\b', prompt.lower()):
            # Extract percentages
            p_pct = re.findall(r'(\d+\.?\d*)%', prompt)
            c_pct = re.findall(r'(\d+\.?\d*)%', candidate)
            if p_pct and c_pct:
                score += 1.0 / (1.0 + abs(float(p_pct[0]) - float(c_pct[0])) / 100.0)
                count += 1
        
        # Temporal ordering
        before = re.findall(r'(\w+)\s+before\s+(\w+)', prompt.lower())
        after = re.findall(r'(\w+)\s+after\s+(\w+)', prompt.lower())
        if before or after:
            c_before = re.findall(r'(\w+)\s+before\s+(\w+)', candidate.lower())
            c_after = re.findall(r'(\w+)\s+after\s+(\w+)', candidate.lower())
            if before and c_before:
                score += 1.0 if before[0] == c_before[0] else 0.0
                count += 1
            if after and c_after:
                score += 1.0 if after[0] == c_after[0] else 0.0
                count += 1
        
        # Causal consistency
        for p_cause in props_p['causals']:
            for c_cause in props_c['causals']:
                if p_cause[0] == c_cause[0] or p_cause[2] == c_cause[2]:
                    score += 0.5
                    count += 1
        
        # Conditional matching
        if props_p['conditionals'] and props_c['conditionals']:
            score += 0.5
            count += 1
        
        # Negation consistency
        p_neg_set = set([n[1] for n in props_p['negations']])
        c_neg_set = set([n[1] for n in props_c['negations']])
        if p_neg_set and c_neg_set:
            overlap = len(p_neg_set & c_neg_set)
            score += overlap / max(len(p_neg_set), 1)
            count += 1
        
        return score / max(count, 1) if count > 0 else 0.5
    
    def _diffusion_score(self, props_p, props_c):
        """Energy-based scoring via reaction-diffusion on proposition graph."""
        # Build unified token set
        tokens_p = set(props_p['tokens'])
        tokens_c = set(props_c['tokens'])
        all_tokens = list(tokens_p | tokens_c)
        n = len(all_tokens)
        
        if n == 0:
            return 0.5
        
        token_idx = {t: i for i, t in enumerate(all_tokens)}
        
        # Initialize energy: -log(prior)
        corpus = tokens_p | tokens_c
        freq = Counter(corpus)
        energy = np.zeros(n)
        for i, t in enumerate(all_tokens):
            p_i = (freq[t] + 1) / (len(corpus) + n)
            energy[i] = -np.log(p_i)
        
        # Build adjacency with edges
        W = np.zeros((n, n))
        
        # Similarity edges (shared tokens)
        for i in range(n):
            for j in range(i+1, n):
                t_i, t_j = all_tokens[i], all_tokens[j]
                if t_i in tokens_p and t_j in tokens_p:
                    W[i, j] = W[j, i] = 0.5
                if t_i in tokens_c and t_j in tokens_c:
                    W[i, j] = W[j, i] = 0.5
        
        # Contradiction edges (negations)
        for neg in props_p['negations']:
            if neg[1] in token_idx:
                i = token_idx[neg[1]]
                for j in range(n):
                    if all_tokens[j] == neg[1]:
                        W[i, j] = -1.0
        
        # Reaction-diffusion
        for _ in range(self.max_iter):
            energy_old = energy.copy()
            for i in range(n):
                diffusion = sum(W[i, j] * (energy_old[j] - energy_old[i]) for j in range(n))
                reaction = 1.0 / (1.0 + np.exp(-energy_old[i]))  # sigmoid
                energy[i] = energy_old[i] + self.alpha * diffusion - self.beta * reaction
            
            if np.linalg.norm(energy - energy_old) < self.eps:
                break
        
        # Score: lower energy = better
        hyp_energy = np.mean([energy[token_idx[t]] for t in tokens_c if t in token_idx]) if tokens_c else 1.0
        score = np.exp(-hyp_energy)
        return np.clip(score, 0.0, 1.0)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
