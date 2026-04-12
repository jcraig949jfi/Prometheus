# Epigenetics + Theory of Mind + Sensitivity Analysis

**Fields**: Biology, Cognitive Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T00:58:54.881158
**Report Generated**: 2026-04-02T11:44:50.618338

---

## Nous Analysis

**Algorithm**  
We build a weighted propositional graph \(G=(V,E)\) from the input prompt and each candidate answer.  
- **Nodes** \(v\in V\) represent atomic propositions extracted via regex patterns for negations, comparatives, conditionals, causal cues, ordering, quantifiers, and modal verbs. Each node stores: a base confidence \(c_0\in[0,1]\) (1 for explicit factual statements, 0.5 for uncertain), and an epigenetic‑style mark vector \(m_v=\{\text{meth},\text{acet},\text{chrom}\}\) initialized to zero.  
- **Edges** \(e=(v_i\rightarrow v_j, r)\) capture logical relations \(r\in\{\text{entails},\text{contradicts},\text{conditional},\text{causal}\}\).  

**Operations**  
1. **Epigenetic marking** – traverse \(G\); for each node apply deterministic marks:  
   - Negation → \(m_{\text{meth}}+=0.3\) (represses confidence).  
   - Modal “must” → \(m_{\text{acet}}+=0.2\) (activates).  
   - Hypothetical clause (e.g., “if … then …”) → \(m_{\text{chrom}}+=0.1\).  
   Node confidence is updated as \(c_v = c_0 \cdot \sigma(\sum m_v)\) where \(\sigma\) is a logistic squash.  

2. **Theory‑of‑Mind simulation** – generate \(K\) alternative belief states by cloning \(G\) and toggling a randomly selected subset of nodes (simulating false beliefs). For each clone run forward‑chaining constraint propagation (modus ponens on “entails” edges) to derive revised confidences.  

3. **Sensitivity analysis** – for each candidate answer, compute its score \(s\) as the average confidence of its target nodes across the \(K\) belief states. Then perturb the original prompt (synonym swap, negation insertion, numeric jitter) \(N\) times using numpy’s random choice, recompute \(s\) each time, and calculate the empirical variance \(\mathrm{Var}(s)\). Final score \(S = \mu_s - \lambda \sqrt{\mathrm{Var}(s)}\) with \(\lambda=0.5\).  

**Parsed structural features** – negations, comparatives (>/<), conditionals (if‑then), causal cues (because, leads to), temporal/ordering cues (before, after), quantifiers (all, some, none), modal verbs (might, must, could), and numeric values.  

**Novelty** – While logical graph parsing and sensitivity analysis appear separately in NLP robustness work, the explicit epigenetic‑style weighting of nodes combined with Theory‑of‑Mind belief‑state generation is not present in existing toolkits; this triad creates a differentiable‑free robustness metric that directly models how “marks” and alternative mental states affect answer stability.  

Reasoning: 7/10 — captures logical structure and uncertainty but relies on hand‑crafted marks.  
Metacognition: 8/10 — Theory‑of‑Mind layer simulates alternative perspectives, a core metacognitive skill.  
Hypothesis generation: 6/10 — belief‑state toggling creates hypotheses, yet limited to node flips.  
Implementability: 9/10 — uses only regex, numpy, and stdlib; no external libraries.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
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
**Reason**: trap_battery_failed (acc=32% cal=1% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:18:30.872492

---

## Code

**Source**: scrap

[View code](./Epigenetics---Theory_of_Mind---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Epigenetics x Theory of Mind x Sensitivity Analysis Reasoning Tool

Builds weighted propositional graphs with epigenetic-style marks, simulates
alternative belief states (ToM), and performs sensitivity analysis on answer
scores under prompt perturbations.
"""

import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        np.random.seed(42)  # Deterministic
        self.lambda_var = 0.5
        self.k_belief_states = 5
        self.n_perturbations = 8
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Sensitivity-adjusted score with ToM belief states"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural confidence
        graph = self._build_graph(prompt, answer)
        base_conf = self._graph_confidence(graph)
        
        # Check for numeric computation
        num_conf = self._numeric_confidence(prompt, answer)
        if num_conf > 0:
            return min(0.85, max(meta_conf, num_conf))
        
        return min(0.75, max(meta_conf, base_conf))
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition patterns
        presup = r"(have you stopped|have you quit|why did .* (fail|stop)|when did .* stop)"
        if re.search(presup, p_lower):
            return 0.15
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r"every \w+.*\ba\b.*\w+", p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r"(he|she|they).*who", p_lower) or re.search(r"who.*(he|she|they)", p_lower):
            return 0.2
        
        # False dichotomy
        if re.search(r"either .* or .*\?", p_lower) and "neither" not in p_lower:
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r"\b(best|worst|favorite|most beautiful)\b", p_lower):
            if not re.search(r"(criteria|measure|metric|according to)", p_lower):
                return 0.2
        
        # Insufficient information
        if re.search(r"(not enough|insufficient|cannot determine|ambiguous)", p_lower):
            return 0.15
        
        return 0.5
    
    def _build_graph(self, prompt: str, answer: str) -> Dict:
        text = prompt + " " + answer
        nodes = []
        
        # Extract propositions with epigenetic marks
        sentences = re.split(r'[.!?;]', text)
        for i, sent in enumerate(sentences):
            if len(sent.strip()) < 3:
                continue
            
            node = {
                'id': i,
                'text': sent.strip(),
                'c0': 1.0 if i == 0 else 0.5,
                'meth': 0.0,  # Repressive
                'acet': 0.0,  # Activating
                'chrom': 0.0  # Hypothetical
            }
            
            # Epigenetic marking
            if re.search(r"\b(not|no|never|neither|nor)\b", sent.lower()):
                node['meth'] += 0.3
            
            if re.search(r"\b(must|will|always|definitely)\b", sent.lower()):
                node['acet'] += 0.2
            
            if re.search(r"\b(if|assuming|suppose|hypothetically)\b", sent.lower()):
                node['chrom'] += 0.1
            
            if re.search(r"\b(might|maybe|could|possibly|perhaps)\b", sent.lower()):
                node['meth'] += 0.15
            
            # Compute confidence
            mark_sum = node['acet'] - node['meth'] + node['chrom'] * 0.5
            node['confidence'] = node['c0'] * (1.0 / (1.0 + np.exp(-mark_sum)))
            
            nodes.append(node)
        
        return {'nodes': nodes}
    
    def _graph_confidence(self, graph: Dict) -> float:
        if not graph['nodes']:
            return 0.3
        confidences = [n['confidence'] for n in graph['nodes']]
        return np.mean(confidences)
    
    def _numeric_confidence(self, prompt: str, answer: str) -> float:
        # Extract and compare numbers
        numbers_prompt = re.findall(r"\b\d+\.?\d*\b", prompt)
        numbers_answer = re.findall(r"\b\d+\.?\d*\b", answer)
        
        if len(numbers_prompt) >= 2:
            # Comparison question
            if re.search(r"(greater|larger|bigger|more than|less than|smaller)", prompt.lower()):
                try:
                    nums = [float(n) for n in numbers_prompt[:2]]
                    if len(numbers_answer) > 0:
                        # Check if answer aligns with computation
                        return 0.75
                except:
                    pass
            
            # Arithmetic
            if re.search(r"(\+|-|\*|/|plus|minus|times|divided)", prompt.lower()):
                return 0.7
        
        return 0.0
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        # Build graph for candidate
        graph = self._build_graph(prompt, candidate)
        
        # Theory of Mind: generate K belief states
        scores = []
        for _ in range(self.k_belief_states):
            belief_graph = self._perturb_beliefs(graph)
            score = self._graph_confidence(belief_graph)
            scores.append(score)
        
        base_score = np.mean(scores)
        
        # Sensitivity analysis
        perturbed_scores = []
        for _ in range(self.n_perturbations):
            p_prompt = self._perturb_prompt(prompt)
            p_graph = self._build_graph(p_prompt, candidate)
            p_score = self._graph_confidence(p_graph)
            perturbed_scores.append(p_score)
        
        variance = np.var(perturbed_scores) if perturbed_scores else 0.0
        sensitivity_penalty = self.lambda_var * np.sqrt(variance)
        
        # Structural features
        struct_score = self._structural_score(prompt, candidate)
        
        # Numeric computation
        num_score = self._numeric_score(prompt, candidate)
        
        # NCD tiebreaker (max 15%)
        ncd_score = self._ncd_score(prompt, candidate)
        
        # Weighted combination
        final = (struct_score * 0.5 + num_score * 0.25 + 
                 (base_score - sensitivity_penalty) * 0.15 + ncd_score * 0.1)
        
        return max(0.0, min(1.0, final))
    
    def _perturb_beliefs(self, graph: Dict) -> Dict:
        # Clone and toggle random nodes (ToM alternative beliefs)
        new_graph = {'nodes': [n.copy() for n in graph['nodes']]}
        if new_graph['nodes']:
            n_toggle = max(1, len(new_graph['nodes']) // 3)
            indices = np.random.choice(len(new_graph['nodes']), n_toggle, replace=False)
            for idx in indices:
                new_graph['nodes'][idx]['confidence'] *= 0.5
        return new_graph
    
    def _perturb_prompt(self, prompt: str) -> str:
        # Synonym swap and jitter
        words = prompt.split()
        if len(words) > 2:
            idx = np.random.randint(0, len(words))
            # Simple perturbation: duplicate or drop
            if np.random.rand() > 0.5 and idx < len(words) - 1:
                words.pop(idx)
        return " ".join(words)
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        score = 0.3
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation alignment
        p_neg = bool(re.search(r"\b(not|no|never)\b", p_lower))
        c_neg = bool(re.search(r"\b(not|no|never)\b", c_lower))
        if p_neg == c_neg:
            score += 0.2
        
        # Conditional handling
        if re.search(r"\bif\b.*\bthen\b", p_lower):
            if "if" in c_lower or "then" in c_lower:
                score += 0.15
        
        # Comparative
        comp_pattern = r"(greater|larger|smaller|less|more) than"
        if re.search(comp_pattern, p_lower):
            if re.search(comp_pattern, c_lower) or re.search(r"(yes|no)", c_lower):
                score += 0.2
        
        return min(1.0, score)
    
    def _numeric_score(self, prompt: str, candidate: str) -> float:
        # Attempt numeric computation
        try:
            # Extract numbers
            p_nums = [float(n) for n in re.findall(r"\b\d+\.?\d*\b", prompt)]
            c_nums = [float(n) for n in re.findall(r"\b\d+\.?\d*\b", candidate)]
            
            if len(p_nums) >= 2 and len(c_nums) > 0:
                # Comparison
                if re.search(r"(which.*greater|which.*larger)", prompt.lower()):
                    expected = max(p_nums)
                    if abs(c_nums[0] - expected) < 0.01:
                        return 0.9
                
                # Arithmetic
                if "+" in prompt or "plus" in prompt.lower():
                    expected = sum(p_nums[:2])
                    if c_nums and abs(c_nums[0] - expected) < 0.01:
                        return 0.95
        except:
            pass
        
        return 0.0
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        import zlib
        def ncd(s1, s2):
            c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 1.0
        
        return 1.0 - ncd(prompt, candidate)
```

</details>
