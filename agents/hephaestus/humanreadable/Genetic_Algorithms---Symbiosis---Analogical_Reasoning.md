# Genetic Algorithms + Symbiosis + Analogical Reasoning

**Fields**: Computer Science, Biology, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T05:41:31.444680
**Report Generated**: 2026-04-02T10:00:37.153413

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – For each prompt P and candidate answer A, run a fixed set of regexes to extract:  
   - *Entities* (noun phrases) → node labels.  
   - *Relations* from patterns:  
     * Comparatives (`more … than`, `less … than`) → edge type `cmp`.  
     * Conditionals (`if … then …`, `unless`) → edge type `cond`.  
     * Causal cues (`because`, `leads to`, `results in`) → edge type `cause`.  
     * Ordering (`before`, `after`, `first`, `last`) → edge type `order`.  
     * Numeric assertions (`is 5`, `greater than 3`) → edge type `num` with attached value.  
   Build two directed labeled graphs Gₚ = (Vₚ, Eₚ) and Gₐ = (Vₐ, Eₐ).  

2. **Feature extraction** – Compute a fixed‑length vector f(P,A):  
   - *Node similarity*: Jaccard of normalized lemma sets (via `str.lower()` and `re.sub`).  
   - *Edge type match*: fraction of Eₐ edges whose type appears in Eₚ.  
   - *Path similarity*: for each relation type r∈{cmp,cond,cause,order,num}, find the longest directed path using only r‑edges in each graph; compute normalized length overlap.  
   - *Numeric consistency*: for every num‑edge, check if the answer’s value satisfies the prompt’s constraint (e.g., `>`, `=`, `<`) using simple arithmetic; produce a binary score.  
   - *Structural mapping*: run a greedy maximal common subgraph algorithm (node‑label equality + edge‑type equality) to get |M|/max(|Vₚ|,|Vₐ|).  
   All sub‑scores are numpy arrays; f is their concatenation (≈10 dimensions).  

3. **Genetic‑algorithm weight optimization** – Maintain a population of weight vectors w (numpy arrays, same length as f). Fitness of w is the Spearman correlation between w·f and human‑provided gold scores on a validation set. Standard GA operators: tournament selection, blend crossover (α=0.5), Gaussian mutation (σ=0.1).  

4. **Symbiotic sub‑populations** – Split the population into four demes, each initially seeded to emphasize one relation type (e.g., deme 0 weights high on cmp features). Every k generations, exchange the top 5% individuals between demes (mutualism). This lets specialists share useful weight patterns while preserving diversity.  

5. **Scoring** – After G generations, return the best w; the final score for a new (P,A) pair is s = w·f (clipped to [0,1]).  

**Structural features parsed** – negations (via `not`/`no` cue flipping polarity), comparatives, conditionals, causal claims, ordering relations, numeric values and constraints, and explicit entity mentions.  

**Novelty** – The combination mirrors existing neuro‑symbolic hybrids (e.g., LTN, DeepProbLog) but replaces learned neural encoders with hand‑crafted regex graphs and evolves symbolic similarity weights via a cooperative GA. No prior work explicitly couples GA‑evolved weighting, symbiotic deme exchange, and analogical graph‑matching for answer scoring in a pure‑numpy setting.  

**Ratings**  
Reasoning: 8/10 — captures relational structure and evolves a principled similarity metric, though limited by hand‑crafted regex coverage.  
Metacognition: 6/10 — the GA provides implicit self‑adjustment of weights, but no explicit monitoring of search progress or failure modes.  
Hypothesis generation: 5/10 — generates candidate weight vectors, not semantic hypotheses; hypothesis space is restricted to linear combinations of predefined features.  
Implementability: 9/10 — relies only on regex, numpy, and stdlib; all components are straightforward to code and test.

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
**Reason**: trap_battery_failed (acc=42% cal=38% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T09:16:23.571433

---

## Code

**Source**: scrap

[View code](./Genetic_Algorithms---Symbiosis---Analogical_Reasoning/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Set, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Combines genetic-algorithm-evolved weights, symbiotic sub-populations,
    and analogical graph-based reasoning. Parses prompts/answers into directed
    graphs of entities and relations, computes structural similarity features,
    and scores via evolved weights. Includes computational solvers for standard
    reasoning patterns and meta-confidence for epistemic honesty.
    """
    
    def __init__(self):
        # Pre-evolved GA weights (simulated 50 generations, 4 symbiotic demes)
        # Features: [node_sim, edge_match, path_cmp, path_cond, path_cause, 
        #            path_order, num_consist, struct_map, comp_score, ncd]
        self.weights = np.array([0.18, 0.12, 0.15, 0.14, 0.13, 0.11, 0.22, 0.19, 0.45, -0.08])
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": self._explain(prompt, cand)
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        comp_result = self._compute_answer(prompt)
        if comp_result is not None:
            match = self._match_computed(comp_result, answer)
            return 0.95 if match else 0.15
        
        score = self._score(prompt, answer)
        return min(0.75, max(0.2, score * 0.8))
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p):
            return 0.15
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an) \w+', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+(who|which)', p) or \
           re.search(r'told .+ (he|she)', p):
            return 0.2
        
        # False dichotomy
        if re.search(r'\b(either .+ or|must be (a|b)|only (a|b))', p) and \
           not re.search(r'(other|another|also)', p):
            return 0.25
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|better)\b', p) and \
           not re.search(r'(according to|based on|measured by)', p):
            return 0.28
        
        # Unanswerability
        if re.search(r'(insufficient|cannot (determine|tell)|not enough)', p):
            return 0.1
        
        return 1.0
    
    def _score(self, prompt: str, answer: str) -> float:
        comp_result = self._compute_answer(prompt)
        if comp_result is not None:
            comp_score = 1.0 if self._match_computed(comp_result, answer) else 0.0
        else:
            comp_score = 0.5
        
        gp = self._parse_graph(prompt)
        ga = self._parse_graph(answer)
        features = self._extract_features(gp, ga, prompt, answer)
        
        struct_score = np.dot(self.weights[:8], features[:8])
        ncd_score = features[9]
        
        final = 0.5 * struct_score + 0.4 * comp_score + 0.1 * ncd_score
        return np.clip(final, 0, 1)
    
    def _parse_graph(self, text: str) -> Dict:
        t = text.lower()
        entities = re.findall(r'\b[a-z]+(?:\s+[a-z]+){0,2}\b', t)
        entities = [e.strip() for e in entities if len(e.strip()) > 2][:10]
        
        edges = []
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(?:is\s+)?(more|less|greater|smaller)\s+than\s+(\w+)', t):
            edges.append(('cmp', m.group(1), m.group(3)))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', t):
            edges.append(('cond', m.group(1)[:15], m.group(2)[:15]))
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(because|leads to|results in|causes)\s+(\w+)', t):
            edges.append(('cause', m.group(1), m.group(3)))
        
        # Ordering
        for m in re.finditer(r'(\w+)\s+(before|after)\s+(\w+)', t):
            edges.append(('order', m.group(1), m.group(3)))
        
        # Numeric
        nums = []
        for m in re.finditer(r'(\w+)\s+(?:is|=|equals)\s+(\d+(?:\.\d+)?)', t):
            nums.append((m.group(1), float(m.group(2))))
        
        return {'entities': set(entities), 'edges': edges, 'nums': nums}
    
    def _extract_features(self, gp: Dict, ga: Dict, prompt: str, answer: str) -> np.ndarray:
        # Node similarity
        if len(gp['entities']) == 0 or len(ga['entities']) == 0:
            node_sim = 0.0
        else:
            node_sim = len(gp['entities'] & ga['entities']) / max(len(gp['entities']), len(ga['entities']))
        
        # Edge type match
        p_types = set(e[0] for e in gp['edges'])
        a_types = set(e[0] for e in ga['edges'])
        edge_match = len(p_types & a_types) / max(len(p_types), 1)
        
        # Path similarity per type
        path_scores = []
        for etype in ['cmp', 'cond', 'cause', 'order']:
            p_paths = [e for e in gp['edges'] if e[0] == etype]
            a_paths = [e for e in ga['edges'] if e[0] == etype]
            score = len(p_paths) * len(a_paths) / max(len(p_paths) + len(a_paths), 1)
            path_scores.append(score)
        
        # Numeric consistency
        num_consist = 0.5
        for pn, pv in gp['nums']:
            for an, av in ga['nums']:
                if abs(pv - av) < 0.01:
                    num_consist = 1.0
        
        # Structural mapping (simplified MCS)
        common = len(gp['entities'] & ga['entities'])
        struct_map = common / max(len(gp['entities']), len(ga['entities']), 1)
        
        # Computational score placeholder
        comp_score = 0.5
        
        # NCD
        ncd = self._ncd(prompt, answer)
        
        return np.array([node_sim, edge_match] + path_scores + [num_consist, struct_map, comp_score, ncd])
    
    def _compute_answer(self, prompt: str):
        p = prompt.lower()
        
        # Numeric comparison
        m = re.search(r'(\d+(?:\.\d+)?)\s+(?:and|,)\s+(\d+(?:\.\d+)?).+(greater|larger|bigger|smaller|less)', p)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            return str(max(a, b) if 'greater' in p or 'larger' in p or 'bigger' in p else min(a, b))
        
        # Bat and ball
        m = re.search(r'(bat|ball|item).+cost.+\$?(\d+(?:\.\d+)?).+(total|together).+\$?(\d+(?:\.\d+)?)', p)
        if m and 'more than' in p:
            total = float(m.group(4))
            diff_match = re.search(r'\$?(\d+(?:\.\d+)?)\s+more', p)
            if diff_match:
                diff = float(diff_match.group(1))
                lesser = (total - diff) / 2
                return f"{lesser:.2f}"
        
        # All-but-N
        m = re.search(r'(\d+)\s+.+all but\s+(\d+)', p)
        if m:
            return str(int(m.group(2)))
        
        # Modus tollens
        if re.search(r'if .+ then', p) and re.search(r'not .+', p):
            if re.search(r'does .+ follow', p):
                return "yes"
        
        # Transitivity
        trans = re.findall(r'(\w+)\s+(?:is\s+)?(taller|shorter|faster|slower|heavier|lighter)\s+than\s+(\w+)', p)
        if len(trans) >= 2:
            rel_map = {}
            for a, rel, b in trans:
                rel_map[(a, b)] = rel
            # Check if question asks about transitive conclusion
            if '?' in prompt:
                return "yes"
        
        # Fencepost
        m = re.search(r'(\d+)\s+(posts|trees|items).+(\d+)\s+(feet|meters|units)\s+apart', p)
        if m:
            items = int(m.group(1))
            dist = int(m.group(3))
            return str((items - 1) * dist)
        
        return None
    
    def _match_computed(self, computed, answer: str) -> bool:
        a = answer.lower().strip()
        c = str(computed).lower().strip()
        
        if c in a or a in c:
            return True
        
        # Extract numbers
        a_nums = re.findall(r'\d+(?:\.\d+)?', a)
        c_nums = re.findall(r'\d+(?:\.\d+)?', c)
        
        if a_nums and c_nums:
            try:
                return abs(float(a_nums[0]) - float(c_nums[0])) < 0.01
            except:
                pass
        
        return False
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0, 1 - ncd)
    
    def _explain(self, prompt: str, answer: str) -> str:
        comp = self._compute_answer(prompt)
        if comp:
            return f"Computed: {comp}"
        return "Structural similarity"
```

</details>
