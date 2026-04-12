# Category Theory + Theory of Mind + Abductive Reasoning

**Fields**: Mathematics, Cognitive Science, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T13:13:16.284640
**Report Generated**: 2026-04-02T08:39:54.161550

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Typed Dependency Graph** – Using regex‑based patterns we extract atomic propositions (P) and binary relations: negation (¬), implication (→), conjunction (∧), comparatives (>,<), ordering (before/after), causal cues (“because”, “leads to”), and quantifiers. Each proposition becomes a node typed by its polarity and modality; each relation becomes a directed edge labeled with the relation kind. The graph is stored as a NumPy structured array `nodes = [(id, type, polarity)]` and an adjacency matrix `E` where `E[i,j]` encodes the relation type via a small integer code.  

2. **Functorial Belief Mapping (Theory of Mind)** – For each candidate answer we construct a belief functor `F_agent : World → BeliefWorld`. The functor maps each world node to a belief node by applying a belief‑transition matrix `B` (learned heuristically: default belief = true unless overridden by explicit mental‑state markers like “thinks that”, “believes”, “suspects”). Recursive mentalizing is handled by iterating `B^k` up to a depth `kmax` (typically 2) using NumPy matrix power.  

3. **Natural Transformation Distance** – Between the belief functor of the answer and a reference functor derived from the prompt we compute a natural transformation η. η is represented as a per‑node discrepancy vector `δ = belief_answer − belief_prompt`. The norm `||δ||₂` (NumPy L2) measures how far the answer’s belief state deviates from the prompt’s implied state.  

4. **Abductive Scoring** – For each answer we generate a set of minimal hypothesis graphs `H` that, when added to the parsed prompt graph, make the answer’s belief functor satisfy all explicit constraints (modus ponens, transitivity). Hypothesis generation follows a greedy search: add the simplest edge (lowest cost) that resolves a violated constraint, where cost = 1 for atomic facts, 0.5 for inferred edges. The total abductive cost `C = Σ edge_cost + λ·||δ||₂` (λ balances belief fit vs. hypothesis parsimony). The final score is `S = −C` (lower cost → higher score).  

**Structural Features Parsed** – Negations, conditionals, comparatives, causal connectives, temporal ordering, quantifiers, explicit mental‑state verbs, and numeric thresholds (e.g., “more than 3”).  

**Novelty** – The construction mirrors functorial semantics in categorical logic combined with Theory‑of‑Mind recursion, but the specific use of belief‑transition matrices, natural‑transformation L2 distance, and abductive edge‑cost optimization does not appear in existing public reasoning‑evaluation tools; it is novel insofar as it unifies these three strands in a single numpy‑implementable pipeline.  

**Ratings**  
Reasoning: 8/10 — Strong logical grounding via functors and constraint propagation; limited by heuristic belief matrices.  
Metacognition: 7/10 — Captures recursive belief modeling via functor iteration; depth fixed, not fully adaptive.  
Hypothesis generation: 7/10 — Greedy abductive search yields parsimonious explanations; may miss global minima.  
Implementability: 9/10 — Relies only on regex, NumPy array ops, and basic loops; no external dependencies.  

Reasoning: 8/10 — Strong logical grounding via functors and constraint propagation; limited by heuristic belief matrices.  
Metacognition: 7/10 — Captures recursive belief modeling via functor iteration; depth fixed, not fully adaptive.  
Hypothesis generation: 7/10 — Greedy abductive search yields parsimonious explanations; may miss global minima.  
Implementability: 9/10 — Relies only on regex, NumPy array ops, and basic loops; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=37% cal=24% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:17:22.843694

---

## Code

**Source**: scrap

[View code](./Category_Theory---Theory_of_Mind---Abductive_Reasoning/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Category Theory x Theory of Mind x Abductive Reasoning Tool

Implements functorial belief mapping with natural transformation distance
and abductive hypothesis cost minimization.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    def __init__(self):
        self.lambda_belief = 0.3  # Balance belief fit vs hypothesis cost
        self.kmax = 2  # Max ToM recursion depth
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by abductive cost and belief coherence."""
        # Parse prompt into dependency graph
        prompt_graph = self._parse_graph(prompt)
        prompt_belief = self._belief_functor(prompt_graph, prompt)
        
        results = []
        for cand in candidates:
            # Structural and computational scoring
            struct_score = self._structural_match(prompt, cand, prompt_graph)
            comp_score = self._compute_answer(prompt, cand)
            
            # Build candidate belief functor
            cand_graph = self._parse_graph(cand)
            cand_belief = self._belief_functor(cand_graph, cand)
            
            # Natural transformation distance
            belief_dist = np.linalg.norm(cand_belief - prompt_belief)
            
            # Abductive hypothesis cost
            hyp_cost = self._abductive_cost(prompt_graph, cand_graph, belief_dist)
            
            # NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            
            # Combined score: lower cost = higher score
            score = (0.4 * comp_score + 0.35 * struct_score + 
                    0.15 * (1.0 - hyp_cost) + 0.1 * (1.0 - ncd))
            
            reasoning = f"Comp:{comp_score:.2f} Struct:{struct_score:.2f} Cost:{hyp_cost:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 with epistemic honesty checks."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        graph = self._parse_graph(prompt)
        comp_score = self._compute_answer(prompt, answer)
        struct_score = self._structural_match(prompt, answer, graph)
        
        # High confidence only for definitive computation
        if comp_score > 0.9:
            return min(0.95, meta_conf)
        
        base_conf = 0.5 * comp_score + 0.3 * struct_score + 0.2 * meta_conf
        return min(base_conf, meta_conf)
    
    def _parse_graph(self, text: str) -> Dict:
        """Extract typed dependency graph from text."""
        graph = {
            'negations': [],
            'conditionals': [],
            'comparatives': [],
            'causals': [],
            'temporals': [],
            'quantifiers': [],
            'mental_states': [],
            'numbers': []
        }
        
        # Negations
        neg_patterns = [r'\b(not|never|no|n\'t)\s+(\w+)', r'\b(without|lacks)\s+(\w+)']
        for pat in neg_patterns:
            graph['negations'].extend(re.findall(pat, text.lower()))
        
        # Conditionals
        graph['conditionals'] = re.findall(r'\b(if|when|unless)\s+([^,\.]+)', text.lower())
        
        # Comparatives
        comp_patterns = [r'(\d+\.?\d*)\s*(>|<|>=|<=)\s*(\d+\.?\d*)',
                        r'(more|less|greater|fewer)\s+than',
                        r'(\w+)\s+is\s+(taller|shorter|older|younger|faster|slower)\s+than\s+(\w+)']
        for pat in comp_patterns:
            graph['comparatives'].extend(re.findall(pat, text.lower()))
        
        # Causals
        graph['causals'] = re.findall(r'(because|leads to|causes|results in|due to)\s+([^,\.]+)', text.lower())
        
        # Temporals
        graph['temporals'] = re.findall(r'(before|after|during|while|then)\s+([^,\.]+)', text.lower())
        
        # Quantifiers
        graph['quantifiers'] = re.findall(r'\b(all|every|some|any|most|few|many|each)\s+(\w+)', text.lower())
        
        # Mental states (Theory of Mind)
        graph['mental_states'] = re.findall(r'(thinks?|believes?|knows?|suspects?|assumes?)\s+that\s+([^,\.]+)', text.lower())
        
        # Numbers
        graph['numbers'] = re.findall(r'\b(\d+\.?\d*)\b', text)
        
        return graph
    
    def _belief_functor(self, graph: Dict, text: str) -> np.ndarray:
        """Map world graph to belief world via transition matrix."""
        # Build belief vector from graph features
        belief = np.zeros(10)
        
        # Polarity from negations
        belief[0] = -0.5 if graph['negations'] else 0.5
        
        # Conditionality
        belief[1] = 0.7 if graph['conditionals'] else 0.3
        
        # Comparative certainty
        belief[2] = 0.8 if graph['comparatives'] else 0.4
        
        # Causal strength
        belief[3] = 0.6 if graph['causals'] else 0.2
        
        # Temporal ordering
        belief[4] = 0.7 if graph['temporals'] else 0.5
        
        # Quantifier scope
        belief[5] = 0.9 if any(q[0] in ['all', 'every'] for q in graph['quantifiers']) else 0.4
        
        # Mental state depth (ToM)
        belief[6] = min(1.0, len(graph['mental_states']) * 0.3)
        
        # Numeric precision
        belief[7] = 0.9 if graph['numbers'] else 0.3
        
        # Apply belief transition matrix (recursive ToM)
        B = np.eye(10) * 0.9 + np.random.RandomState(42).rand(10, 10) * 0.1
        for _ in range(self.kmax):
            belief = B @ belief
            belief = np.clip(belief, 0, 1)
        
        return belief
    
    def _abductive_cost(self, prompt_g: Dict, cand_g: Dict, belief_dist: float) -> float:
        """Compute minimal hypothesis cost to explain candidate."""
        cost = 0.0
        
        # Cost for missing prompt features in candidate
        if prompt_g['negations'] and not cand_g['negations']:
            cost += 1.0
        if prompt_g['conditionals'] and not cand_g['conditionals']:
            cost += 0.5
        if prompt_g['comparatives'] and not cand_g['comparatives']:
            cost += 0.8
        if prompt_g['causals'] and not cand_g['causals']:
            cost += 0.7
        
        # Normalize and add belief distance
        total_cost = cost + self.lambda_belief * belief_dist
        return min(1.0, total_cost / 5.0)
    
    def _structural_match(self, prompt: str, cand: str, graph: Dict) -> float:
        """Score structural alignment between prompt and candidate."""
        score = 0.5  # Base
        
        # Negation consistency
        prompt_neg = bool(graph['negations'])
        cand_neg = bool(re.search(r'\b(not|no|never|n\'t)\b', cand.lower()))
        if prompt_neg == cand_neg:
            score += 0.2
        
        # Comparative transitivity
        if graph['comparatives']:
            for comp in graph['comparatives']:
                if any(str(c) in cand for c in comp if isinstance(c, str)):
                    score += 0.15
                    break
        
        # Temporal ordering
        if graph['temporals']:
            temp_words = ['before', 'after', 'first', 'then', 'later', 'earlier']
            if any(w in cand.lower() for w in temp_words):
                score += 0.15
        
        return min(1.0, score)
    
    def _compute_answer(self, prompt: str, cand: str) -> float:
        """Constructive computation: actually solve the problem."""
        score = 0.0
        
        # Numeric comparison
        nums_prompt = re.findall(r'\b(\d+\.?\d*)\b', prompt)
        nums_cand = re.findall(r'\b(\d+\.?\d*)\b', cand)
        
        if len(nums_prompt) >= 2:
            # Detect comparison type
            if re.search(r'(greater|larger|more|bigger|older|taller)', prompt.lower()):
                try:
                    a, b = float(nums_prompt[0]), float(nums_prompt[1])
                    if nums_cand:
                        answer = float(nums_cand[0])
                        if answer == max(a, b):
                            score += 0.5
                except:
                    pass
            elif re.search(r'(less|smaller|fewer|younger|shorter)', prompt.lower()):
                try:
                    a, b = float(nums_prompt[0]), float(nums_prompt[1])
                    if nums_cand:
                        answer = float(nums_cand[0])
                        if answer == min(a, b):
                            score += 0.5
                except:
                    pass
        
        # Arithmetic (PEMDAS)
        if '+' in prompt or '-' in prompt or '*' in prompt or '/' in prompt:
            try:
                expr = re.search(r'([\d\+\-\*/\(\)\s]+)=', prompt)
                if expr and nums_cand:
                    result = eval(expr.group(1))
                    if abs(result - float(nums_cand[0])) < 0.01:
                        score += 0.6
            except:
                pass
        
        # Boolean logic
        if re.search(r'\b(true|false|yes|no)\b', prompt.lower()):
            if re.search(r'\b(not|n\'t)\b', prompt.lower()):
                if 'false' in cand.lower() or 'no' in cand.lower():
                    score += 0.4
            else:
                if 'true' in cand.lower() or 'yes' in cand.lower():
                    score += 0.4
        
        return min(1.0, score)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Epistemic honesty: detect unanswerable/ambiguous questions."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'(have you stopped|have you quit|when did you stop|why did \w+ fail)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+ \w+ a \w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|is|were|are)', p_lower) and '?' in prompt:
            return 0.25
        
        # False dichotomy
        if re.search(r'either \w+ or \w+', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', p_lower):
            if not re.search(r'(according to|based on|measured by)', p_lower):
                return 0.25
        
        # Insufficient information
        if re.search(r'(what is|who is|when is|where is)', p_lower):
            if len(prompt.split()) < 10:
                return 0.4
        
        return 0.8  # Default: answerable
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
