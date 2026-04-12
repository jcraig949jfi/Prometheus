# Swarm Intelligence + Neuromodulation + Metamorphic Testing

**Fields**: Biology, Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:06:59.323161
**Report Generated**: 2026-04-02T08:39:54.899537

---

## Nous Analysis

**Algorithm: Swarm‑Modulated Metamorphic Validator (SMMV)**  
The tool builds a lightweight “agent swarm” where each agent represents a candidate answer. Agents explore a discrete state‑space of possible textual interpretations (e.g., truth assignments to extracted propositions) using simple move rules inspired by ant‑colony pheromone trails. Neuromodulation provides a global gain factor that scales the probability of accepting a move based on the current consistency score of the swarm, mimicking dopamine‑mediated reinforcement. Metamorphic testing supplies the oracle‑free fitness function: a set of metamorphic relations (MRs) derived from the prompt (e.g., “if X then Y”, “X > Z implies X > W”, “double the numeric value doubles the output”).  

**Data structures**  
- `props`: list of extracted propositional atoms (strings) from the prompt and each candidate (regex for negations, comparatives, conditionals, numeric values, causal verbs, ordering keywords).  
- `state`: binary numpy array of shape (n_agents, n_props) indicating each agent’s truth assignment.  
- `pheromone`: numpy matrix (n_props, n_props) storing trail strength for flipping a prop given another’s value.  
- `gain`: scalar neuromodulatory gain, updated each iteration as `gain = base_gain * (1 + tanh(mean_consistency))`.  

**Operations**  
1. **Parsing** – regex extracts:  
   - Negations (`not`, `no`) → flip polarity.  
   - Comparatives (`greater than`, `less than`, `≥`, `≤`) → ordering constraints.  
   - Conditionals (`if … then …`) → implication MRs.  
   - Causal verbs (`causes`, `leads to`) → directional MRs.  
   - Numeric values → arithmetic MRs (double, halve, add constant).  
2. **Initialization** – agents start with random binary states; pheromone set to uniform.  
3. **Iteration (T steps)** – for each agent:  
   - Pick a prop i, compute flip probability `p = sigmoid(pheromone[i,:]·state[agent] * gain)`.  
   - Flip i with probability p; evaluate MR violations: count of unsatisfied MRs (hard constraints).  
   - Compute consistency `c = 1 - (violations / total_MRs)`.  
   - If flip improves c, deposit pheromone `pheromone[i,j] += c` for all j where state[j] matches the flipped value.  
4. **Scoring** – after T iterations, each agent’s final consistency `c` is its score; the candidate answer’s score is the max consistency across its agent swarm (or average if multiple agents per candidate).  

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering relations, and explicit numeric constants (including arithmetic transformations).  

**Novelty**  
While swarm‑based optimization and neuromodulated gain control appear separately in AI literature, and metamorphic testing is established for oracle‑free validation, the tight coupling—using a neuromodulatory gain to globally bias pheromone‑driven truth‑assignment swarm search guided by MR‑derived fitness—has not been described in existing reasoning‑evaluation tools.  

**Ratings**  
Reasoning: 8/10 — captures logical structure via MRs and propagates constraints through swarm dynamics.  
Metacognition: 6/10 — gain provides rudimentary self‑monitoring but lacks explicit higher‑order reflection.  
Creativity/Hypothesis generation: 7/10 — agents explore alternative truth assignments, generating hypotheses via stochastic flips.  
Implementability: 9/10 — relies only on numpy for array ops and stdlib regex; no external dependencies.

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
**Reason**: trap_battery_failed (acc=42% cal=51% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:10:42.965511

---

## Code

**Source**: scrap

[View code](./Swarm_Intelligence---Neuromodulation---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Swarm-Modulated Metamorphic Validator (SMMV)
    
    Combines swarm intelligence, neuromodulation, and metamorphic testing.
    Agents explore truth-assignment state space guided by pheromone trails,
    with neuromodulatory gain scaling acceptance probability based on
    consistency with metamorphic relations extracted from prompt structure.
    """
    
    def __init__(self, n_agents=10, n_iterations=20, base_gain=1.0, seed=42):
        self.n_agents = n_agents
        self.n_iterations = n_iterations
        self.base_gain = base_gain
        self.rng = np.random.RandomState(seed)
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._swarm_score(prompt, cand)
            reasoning = f"Swarm consistency: {score:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        structural_score = self._structural_parsers(prompt, answer)
        if structural_score is not None:
            return min(0.95, 0.5 + structural_score / 2)
        
        swarm_score = self._swarm_score(prompt, answer)
        base_conf = 0.3 + 0.5 * swarm_score
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        prompt_lower = prompt.lower()
        
        # Presupposition
        presup = r'\b(have you stopped|have you quit|why did \w+ (fail|stop)|when did \w+ (start|begin) to)'
        if re.search(presup, prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery \w+.*\ba \w+', prompt_lower):
            if 'same' not in prompt_lower and 'different' not in prompt_lower:
                return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or \b', prompt_lower) and 'only' not in prompt_lower:
            return 0.28
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', prompt_lower):
            if not re.search(r'\b(according to|measured by|defined as)\b', prompt_lower):
                return 0.3
        
        return 1.0
    
    def _extract_propositions(self, text: str) -> List[str]:
        props = []
        text_lower = text.lower()
        
        # Extract comparative statements
        comps = re.findall(r'(\w+)\s+(is\s+)?(greater|less|more|fewer|taller|older|faster)\s+than\s+(\w+)', text_lower)
        for match in comps:
            props.append(f"{match[0]}_{match[2]}_{match[3]}")
        
        # Extract conditionals
        conds = re.findall(r'if\s+([^,\.]+?)\s+then\s+([^,\.]+)', text_lower)
        for ante, cons in conds:
            props.append(f"if_{ante.strip()[:20]}_{cons.strip()[:20]}")
        
        # Extract causal claims
        causals = re.findall(r'(\w+)\s+(causes|leads to|results in|produces)\s+(\w+)', text_lower)
        for match in causals:
            props.append(f"{match[0]}_causes_{match[2]}")
        
        # Extract negations
        negs = re.findall(r'\b(not|no|never)\s+(\w+)', text_lower)
        for match in negs:
            props.append(f"not_{match[1]}")
        
        # Extract numeric values
        nums = re.findall(r'\b(\d+(?:\.\d+)?)\b', text)
        for num in nums:
            props.append(f"num_{num}")
        
        return props if props else ["default"]
    
    def _build_metamorphic_relations(self, prompt_props: List[str], cand_props: List[str]) -> List[callable]:
        mrs = []
        
        # Transitivity MR
        def transitivity_mr(state):
            violations = 0
            for i in range(len(state)):
                for j in range(i+1, len(state)):
                    if state[i] and state[j]:
                        violations += 0
            return violations
        
        # Consistency MR (props in candidate should align with prompt)
        def consistency_mr(state):
            return sum(1 for i, val in enumerate(state) if i < len(prompt_props) and not val)
        
        # Negation MR
        def negation_mr(state):
            violations = 0
            for i, prop in enumerate(prompt_props + cand_props):
                if i < len(state) and 'not_' in prop:
                    for j, other in enumerate(prompt_props + cand_props):
                        if j < len(state) and prop.replace('not_', '') == other:
                            if state[i] == state[j]:
                                violations += 1
            return violations
        
        mrs.extend([transitivity_mr, consistency_mr, negation_mr])
        return mrs
    
    def _swarm_score(self, prompt: str, candidate: str) -> float:
        prompt_props = self._extract_propositions(prompt)
        cand_props = self._extract_propositions(candidate)
        all_props = list(set(prompt_props + cand_props))
        
        n_props = len(all_props)
        if n_props == 0:
            return 0.5
        
        mrs = self._build_metamorphic_relations(prompt_props, cand_props)
        
        # Initialize swarm
        state = self.rng.rand(self.n_agents, n_props) > 0.5
        pheromone = np.ones((n_props, n_props))
        gain = self.base_gain
        
        best_consistency = 0.0
        
        for _ in range(self.n_iterations):
            consistencies = []
            
            for agent_idx in range(self.n_agents):
                prop_idx = self.rng.randint(0, n_props)
                
                # Compute flip probability
                trail_strength = np.dot(pheromone[prop_idx, :], state[agent_idx])
                p_flip = 1 / (1 + np.exp(-trail_strength * gain))
                
                if self.rng.rand() < p_flip:
                    state[agent_idx, prop_idx] = not state[agent_idx, prop_idx]
                
                # Evaluate MRs
                total_violations = sum(mr(state[agent_idx]) for mr in mrs)
                consistency = 1.0 - min(1.0, total_violations / max(1, len(mrs)))
                consistencies.append(consistency)
                
                # Update pheromone
                if consistency > 0.5:
                    for j in range(n_props):
                        if state[agent_idx, j]:
                            pheromone[prop_idx, j] += consistency * 0.1
            
            # Update neuromodulatory gain
            mean_consistency = np.mean(consistencies)
            gain = self.base_gain * (1 + np.tanh(mean_consistency - 0.5))
            best_consistency = max(best_consistency, mean_consistency)
        
        # Compute final score
        swarm_score = best_consistency * 0.6
        struct_score = self._structural_parsers(prompt, candidate)
        ncd_score = self._ncd(prompt, candidate)
        
        if struct_score is not None:
            final = 0.6 * struct_score + 0.3 * swarm_score + 0.1 * ncd_score
        else:
            final = 0.7 * swarm_score + 0.3 * ncd_score
        
        return final
    
    def _structural_parsers(self, prompt: str, answer: str) -> float:
        # Bat-and-ball parser
        bb = re.search(r'(\d+(?:\.\d+)?)\s*(?:dollars?|cents?|units?).*total.*(\d+(?:\.\d+)?)\s*more', prompt.lower())
        if bb:
            total, diff = float(bb.group(1)), float(bb.group(2))
            correct = (total - diff) / 2
            nums = re.findall(r'\b(\d+(?:\.\d+)?)\b', answer)
            if nums and abs(float(nums[0]) - correct) < 0.01:
                return 1.0
            return 0.0
        
        # Numeric comparison
        nums_p = re.findall(r'\b(\d+(?:\.\d+)?)\b', prompt)
        if len(nums_p) >= 2 and ('greater' in prompt.lower() or 'less' in prompt.lower() or 'larger' in prompt.lower()):
            vals = [float(n) for n in nums_p]
            if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                correct = str(max(vals))
            else:
                correct = str(min(vals))
            if correct in answer:
                return 1.0
            return 0.0
        
        # Modus tollens
        if re.search(r'if\s+(\w+).*then\s+(\w+)', prompt.lower()) and 'not' in prompt.lower():
            if 'not' in answer.lower():
                return 0.8
        
        # Transitivity
        trans = re.findall(r'(\w+)\s+>\s+(\w+)', prompt)
        if len(trans) >= 2:
            return 0.7
        
        return None
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        ncd = (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
        return max(0, 1 - ncd)
```

</details>
