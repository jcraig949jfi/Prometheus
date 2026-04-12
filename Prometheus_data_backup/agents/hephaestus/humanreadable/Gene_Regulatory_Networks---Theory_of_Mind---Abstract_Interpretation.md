# Gene Regulatory Networks + Theory of Mind + Abstract Interpretation

**Fields**: Biology, Cognitive Science, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T16:04:34.317754
**Report Generated**: 2026-04-02T12:33:28.667896

---

## Nous Analysis

**Algorithm: Belief‑Propagation Abstract Regulator (BPAR)**  

*Data structures*  
- **Regulator graph** G = (V, E) where each node v ∈ V represents a propositional atom extracted from the prompt or a candidate answer (e.g., “X > Y”, “¬p”, “Agent A believes q”). Edges e = (u→v) encode regulatory influence: a transcription‑factor‑like rule IF u THEN v (activation) or IF u THEN ¬v (repression).  
- **Belief table** B[v] ∈ [0,1] stores the current degree of truth (abstract interpretation) for each atom, initialized from explicit facts in the prompt (1 for asserted true, 0 for asserted false, 0.5 for unknown).  
- **Intentional layer** I[a][p] ∈ [0,1] models Theory‑of‑Mind: for each agent a we keep a belief distribution over propositions p that the agent might hold, updated via recursive mentalizing (depth ≤ 2 to stay tractable).  

*Operations*  
1. **Parsing** – Use regex to extract atomic propositions and logical connectives (negation, conjunction, disjunction, implication, comparative, numeric inequality). Each yields a node; each connective yields directed edges with signs (+ for activation, – for repression).  
2. **Constraint propagation** – Iterate a synchronous update: for each edge u→v with sign s, compute Δ = s·B[u]; update B[v] = clip(B[v] + α·Δ, 0, 1) where α∈(0,1] is a damping factor (abstract interpretation’s widening/narrowing). Continue until ‖B⁽ᵗ⁺¹⁾−B⁽ᵗ⁾‖₁ < ε.  
3. **Theory‑of‑Mind update** – For each agent a, propagate beliefs through the same regulator graph but using the agent‑specific belief table Bᵃ; after convergence, set I[a][p] = Bᵃ[p]. Higher‑order beliefs are obtained by treating I[a][·] as new facts and repeating step 2 (bounded depth).  
4. **Scoring** – For a candidate answer C, extract its proposition set P_C. Compute answer‑fit = (1/|P_C|)∑_{p∈P_C} B[p] (how well the prompt’s inferred truth supports the answer). Compute consistency penalty = (1/|P_C|)∑_{p∈P_C} |B[p]−0.5| · (1−2·|B[p]−0.5|) to discourage vague mid‑range beliefs. Final score = answer‑fit − λ·consistency‑penalty (λ≈0.2).  

*Structural features parsed* – negations (“not”, “¬”), comparatives (“>”, “<”, “≥”, “≤”), conditionals (“if … then …”), causal verbs (“causes”, “leads to”), numeric values and units, ordering relations (“first”, “before”, “after”), and explicit belief predicates (“Agent X believes that …”).  

*Novelty* – The triple fusion is not present in existing NLP evaluation metrics. Gene‑regulatory‑style signed graphs with belief propagation appear in systems biology; Theory‑of‑Mind layers resemble recursive epistemic logics; abstract interpretation provides the sound over‑/under‑approximation semantics. No prior work combines all three to score answer correctness via constraint‑propagated belief tables.  

**Ratings**  
Reasoning: 8/10 — captures logical dependencies and uncertainty via propagation, yielding nuanced scores beyond exact match.  
Metacognition: 7/10 — models agents’ beliefs and higher‑order reasoning, though depth is limited to avoid explosion.  
Hypothesis generation: 6/10 — can propose missing propositions by inspecting low‑belief nodes, but lacks creative abductive leaps.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and simple loops; no external libraries or training needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
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
**Reason**: validation:forbidden_import: forge_primitives

**Forge Timestamp**: 2026-04-02T12:30:23.292285

---

## Code

**Source**: scrap

[View code](./Gene_Regulatory_Networks---Theory_of_Mind---Abstract_Interpretation/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Set

"""
Belief-Propagation Abstract Regulator (BPAR)

Fuses Gene Regulatory Networks + Theory of Mind + Abstract Interpretation.
Models reasoning as belief propagation through a signed regulatory graph where
nodes are propositions and edges encode activation/repression rules. Tracks
agent-specific beliefs for recursive mentalizing.
"""

import re
import numpy as np
from collections import defaultdict
from forge_primitives import (
    track_beliefs, topological_sort, confidence_from_agreement,
    information_sufficiency, bayesian_update, entropy
)


class ReasoningTool:
    def __init__(self):
        self.alpha = 0.3  # damping factor for belief propagation
        self.epsilon = 0.01  # convergence threshold
        self.max_iter = 50
        self.lambda_penalty = 0.2
        
    def _extract_propositions(self, text):
        """Parse text into atomic propositions and regulatory edges."""
        text = text.lower()
        nodes = {}
        edges = []
        node_id = 0
        
        # Extract comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|==)\s*(\w+)', text):
            prop = f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
            if prop not in nodes:
                nodes[prop] = node_id
                node_id += 1
        
        # Extract numeric inequalities
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|==)\s*(\d+\.?\d*)', text):
            try:
                left, op, right = float(m.group(1)), m.group(2), float(m.group(3))
                result = eval(f"{left}{op}{right}")
                prop = f"num_{m.group(1)}_{op}_{m.group(3)}"
                if prop not in nodes:
                    nodes[prop] = node_id
                    node_id += 1
            except:
                pass
        
        # Extract conditionals (if-then creates activation edge)
        for m in re.finditer(r'if\s+([^,\.]+?)\s+then\s+([^,\.]+?)(?:\.|,|$)', text):
            ante = m.group(1).strip()
            cons = m.group(2).strip()
            if ante not in nodes:
                nodes[ante] = node_id
                node_id += 1
            if cons not in nodes:
                nodes[cons] = node_id
                node_id += 1
            edges.append((nodes[ante], nodes[cons], 1))  # activation
        
        # Extract negations (creates repression edge)
        for m in re.finditer(r'not\s+(\w+)', text):
            prop = m.group(1)
            neg_prop = f"not_{prop}"
            if prop not in nodes:
                nodes[prop] = node_id
                node_id += 1
            if neg_prop not in nodes:
                nodes[neg_prop] = node_id
                node_id += 1
            edges.append((nodes[prop], nodes[neg_prop], -1))  # repression
        
        # Extract belief predicates for Theory of Mind
        agents = {}
        for m in re.finditer(r'(\w+)\s+(?:believes?|thinks?)\s+(?:that\s+)?([^,\.]+)', text):
            agent = m.group(1)
            belief = m.group(2).strip()
            if agent not in agents:
                agents[agent] = []
            if belief not in nodes:
                nodes[belief] = node_id
                node_id += 1
            agents[agent].append(nodes[belief])
        
        return nodes, edges, agents
    
    def _propagate_beliefs(self, n_nodes, edges, initial_beliefs):
        """Run belief propagation on regulatory graph."""
        beliefs = np.array(initial_beliefs)
        
        for _ in range(self.max_iter):
            new_beliefs = beliefs.copy()
            for src, dst, sign in edges:
                if src < len(beliefs) and dst < len(beliefs):
                    delta = sign * beliefs[src]
                    new_beliefs[dst] = np.clip(new_beliefs[dst] + self.alpha * delta, 0, 1)
            
            if np.sum(np.abs(new_beliefs - beliefs)) < self.epsilon:
                break
            beliefs = new_beliefs
        
        return beliefs
    
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/unanswerability markers."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|have you quit|why did \w+ (fail|stop))', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*\ba\b \w+', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\w+ told \w+ (he|she)', p) and 'who' in p:
            return 0.2
        
        # False dichotomy
        if re.search(r'either \w+ or \w+', p) and not re.search(r'(only|exactly)', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.3
        
        # Insufficient information
        if re.search(r'(not enough|cannot determine|insufficient|ambiguous)', p):
            return 0.25
        
        return 1.0
    
    def evaluate(self, prompt, candidates):
        """Score candidates via belief propagation through regulatory graph."""
        nodes, edges, agents = self._extract_propositions(prompt)
        
        if not nodes:
            # Fallback: use NCD
            return self._ncd_fallback(prompt, candidates)
        
        # Initialize beliefs (0.5 = unknown)
        initial = np.full(len(nodes), 0.5)
        
        # Set known facts from prompt to 1.0
        for m in re.finditer(r'(\w+)\s+is\s+(true|correct|yes)', prompt.lower()):
            prop = m.group(1)
            if prop in nodes:
                initial[nodes[prop]] = 1.0
        
        # Propagate beliefs
        prompt_beliefs = self._propagate_beliefs(len(nodes), edges, initial)
        
        # Theory of Mind: track agent-specific beliefs
        agent_beliefs = {}
        for agent, belief_nodes in agents.items():
            agent_initial = initial.copy()
            for bn in belief_nodes:
                if bn < len(agent_initial):
                    agent_initial[bn] = 0.8  # agent holds this belief
            agent_beliefs[agent] = self._propagate_beliefs(len(nodes), edges, agent_initial)
        
        # Score each candidate
        results = []
        for cand in candidates:
            cand_nodes, cand_edges, _ = self._extract_propositions(cand)
            
            # Map candidate propositions to main graph
            scores = []
            for prop, cid in cand_nodes.items():
                if prop in nodes:
                    scores.append(prompt_beliefs[nodes[prop]])
            
            if scores:
                answer_fit = np.mean(scores)
                consistency_penalty = np.mean([abs(s - 0.5) * (1 - 2*abs(s - 0.5)) for s in scores])
                score = answer_fit - self.lambda_penalty * consistency_penalty
            else:
                # Use NCD as tiebreaker
                score = 0.1 * self._ncd(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Belief fit: {answer_fit:.3f}, Consistency: {consistency_penalty:.3f}" if scores else "NCD fallback"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 based on meta-cognitive assessment."""
        meta_conf = self._meta_confidence(prompt)
        
        nodes, edges, _ = self._extract_propositions(prompt)
        if not nodes:
            return min(0.4, meta_conf)
        
        initial = np.full(len(nodes), 0.5)
        beliefs = self._propagate_beliefs(len(nodes), edges, initial)
        
        # Extract answer propositions
        ans_nodes, _, _ = self._extract_propositions(answer)
        ans_scores = []
        for prop in ans_nodes:
            if prop in nodes:
                ans_scores.append(beliefs[nodes[prop]])
        
        if ans_scores:
            # High confidence if beliefs are definitive (near 0 or 1)
            avg_belief = np.mean(ans_scores)
            definitiveness = 2 * abs(avg_belief - 0.5)
            base_conf = min(0.9, definitiveness)
        else:
            base_conf = 0.4
        
        return min(base_conf, meta_conf)
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance (max 15% of score)."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return 1 - (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _ncd_fallback(self, prompt, candidates):
        """Pure NCD ranking when structural parsing fails."""
        results = []
        for cand in candidates:
            score = self._ncd(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "NCD similarity (no structure found)"
            })
        return sorted(results, key=lambda x: x["score"], reverse=True)
```

</details>
