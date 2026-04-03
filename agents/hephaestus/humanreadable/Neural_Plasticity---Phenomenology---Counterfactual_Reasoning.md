# Neural Plasticity + Phenomenology + Counterfactual Reasoning

**Fields**: Biology, Philosophy, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T04:59:39.895046
**Report Generated**: 2026-04-02T10:55:58.504204

---

## Nous Analysis

**Algorithm**  
1. **Parsing phase** – Tokenize the prompt and each candidate answer with `re.findall`. Extract:  
   - Predicate triples `(subject, relation, object)` where `relation` is a verb or copula.  
   - Negation flags (`not`, `no`, `never`).  
   - Comparative operators (`>`, `<`, `>=`, `<=`, `=`, `more than`, `less than`).  
   - Conditional antecedent‑consequent pairs signaled by `if…then`, `unless`, `provided that`.  
   - Causal markers (`because`, `leads to`, `results in`).  
   - Numeric constants.  
   Each extracted triple becomes a node `n_i` with attributes: polarity (`+1` for affirmative, `-1` for negated), type (`predicate`, `comparison`, `conditional`, `causal`).  

2. **Graph construction** – Build a directed adjacency matrix `A` (size `N×N`) where `A[i,j]=1` if there is a logical edge from `i` to `j`:  
   - `IMPLIES` for conditionals (`i` antecedent → `j` consequent).  
   - `EQUIV` for bidirectional definitions.  
   - `COMPARE` for comparative relations (directed according to order).  
   - `CAUSE` for causal markers.  
   Negation is stored as a separate polarity vector `p`.  

3. **Hebbian plasticity weighting** – Initialize weight matrix `W = np.ones_like(A, dtype=float)`. For each training example (prompt + known correct answer), compute an activation vector `a` where `a[i]=1` if node `i` appears in the answer (respecting polarity). Update weights with a simple Hebbian rule:  
   ```
   eta = 0.01
   W += eta * (np.outer(a, a) * A)
   ```  
   After processing all examples, prune weak connections: set `W[W < tau] = 0` (tau = 0.1). This implements synaptic pruning.  

4. **Counterfactual reasoning step** – For a candidate answer, generate its *counterfactual activation* `a_cf` by toggling the polarity of each node that appears under a conditional antecedent (i.e., apply Pearl’s do‑calculus: force antecedent to true/false and propagate). Propagate activation through the weighted graph using constrained linear dynamics:  
   ```
   a_next = np.clip(W.T @ a_cf, 0, 1)
   ```  
   Iterate until convergence (≤5 iterations) or change < 1e‑3.  

5. **Scoring logic** – The final score `s` is the sum of activated weights of nodes that match the candidate’s literals, minus a penalty for activated nodes whose polarity conflicts with the candidate:  
   ```
   match = np.sum(W * np.outer(a_final, a_final) * np.eye(N))
   conflict = np.sum(W * np.outer(a_final, np.abs(p - a_final)) * np.eye(N))
   s = match - 0.5 * conflict
   ```  
   Scores are normalized to `[0,1]` across all candidates.

**Structural features parsed** – Negations, comparatives (`>`, `<`, `=`), conditionals (`if…then`), causal claims (`because`, `leads to`), ordering relations (temporal or magnitude), numeric constants, and quantifier scope (`all`, `some`, `none`) via regex patterns.

**Novelty** – The combination of Hebbian‑style weight updating on a explicitly extracted logical graph, phenomenological bracketing (isolating predicate‑argument structure while discarding stylistic modifiers), and counterfactual world generation via do‑calculus is not present in existing neuro‑symbolic or probabilistic logic frameworks (e.g., Markov Logic Networks, Probabilistic Soft Logic, neural theorem provers), which either learn weighted formulas directly or use neural embeddings rather than pure Hebbian plasticity on a symbolic graph.

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical structure and propagates constraints, but relies on shallow regex parsing which can miss complex syntax.  
Metacognition: 6/10 — Bracketing provides a rudimentary form of reflecting on input form, yet the system does not monitor its own uncertainty or adjust learning rates adaptively.  
Hypothesis generation: 7/10 — Counterfactual toggling yields alternative worlds, enabling hypothesis scoring, though hypothesis space is limited to single‑node flips.  
Implementability: 9/10 — Uses only NumPy and the standard library; all steps are deterministic loops or matrix operations feasible in <200 lines.

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
**Reason**: validation:runtime_error: NameError: name 're' is not defined

**Forge Timestamp**: 2026-04-02T10:37:33.418488

---

## Code

**Source**: scrap

[View code](./Neural_Plasticity---Phenomenology---Counterfactual_Reasoning/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Neural Plasticity x Phenomenology x Counterfactual Reasoning
    
    Extracts logical structure (predicates, negations, conditionals, comparatives),
    builds a weighted graph with Hebbian plasticity, performs counterfactual
    propagation via do-calculus, and evaluates epistemic validity before scoring.
    """
    
    def __init__(self):
        self.eta = 0.01  # Hebbian learning rate
        self.tau = 0.1   # Pruning threshold
        self.max_iter = 5
        
    def _tokenize_and_extract(self, text: str) -> List[Dict]:
        """Extract structural features: predicates, negations, comparatives, conditionals"""
        text = text.lower()
        nodes = []
        
        # Negation patterns
        neg_pattern = r'\b(not|no|never|neither|nor|n\'t)\s+(\w+(?:\s+\w+){0,3})'
        for match in re.finditer(neg_pattern, text):
            nodes.append({'type': 'predicate', 'text': match.group(2), 'polarity': -1})
        
        # Comparatives
        comp_pattern = r'([\d.]+)\s*(>|<|>=|<=|=|equals?|more than|less than|greater|smaller)\s*([\d.]+)'
        for match in re.finditer(comp_pattern, text):
            nodes.append({'type': 'comparison', 'text': match.group(0), 'polarity': 1, 
                         'left': match.group(1), 'op': match.group(2), 'right': match.group(3)})
        
        # Conditionals
        cond_pattern = r'(if|when|unless|provided that)\s+([^,]+),?\s+(then\s+)?([^.;]+)'
        for match in re.finditer(cond_pattern, text):
            nodes.append({'type': 'conditional', 'text': match.group(0), 'polarity': 1,
                         'antecedent': match.group(2), 'consequent': match.group(4)})
        
        # Causal relations
        causal_pattern = r'([^.;]+)\s+(because|leads to|results in|causes|due to)\s+([^.;]+)'
        for match in re.finditer(causal_pattern, text):
            nodes.append({'type': 'causal', 'text': match.group(0), 'polarity': 1,
                         'cause': match.group(3), 'effect': match.group(1)})
        
        # General predicates (subject-verb-object)
        pred_pattern = r'\b(\w+)\s+(is|are|was|were|has|have|can|will)\s+(\w+(?:\s+\w+){0,2})'
        for match in re.finditer(pred_pattern, text):
            if not any(match.group(0) in n['text'] for n in nodes):
                nodes.append({'type': 'predicate', 'text': match.group(0), 'polarity': 1})
        
        return nodes if nodes else [{'type': 'predicate', 'text': text[:50], 'polarity': 1}]
    
    def _meta_confidence(self, prompt: str) -> float:
        """Evaluate prompt for ambiguity, presupposition, unanswerability"""
        prompt_lower = prompt.lower()
        
        # Presupposition traps
        presup_patterns = [
            r'have you (stopped|quit|ceased)',
            r'why did \w+ (fail|stop|end)',
            r'when did you (start|begin|stop)',
        ]
        for pattern in presup_patterns:
            if re.search(pattern, prompt_lower):
                return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*\ba\b', prompt_lower) or re.search(r'all \w+.*\ba\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\s+(was|is|did)', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .* or .*[?.!]', prompt_lower) and 'only' not in prompt_lower:
            return 0.28
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful|ideal)\b', prompt_lower):
            if not re.search(r'(metric|measure|criterion|defined as|according to)', prompt_lower):
                return 0.25
        
        # Unanswerable patterns
        if re.search(r'what will happen|predict the future|cannot be determined', prompt_lower):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def _build_graph(self, nodes: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Build adjacency matrix and polarity vector"""
        n = len(nodes)
        A = np.zeros((n, n))
        p = np.array([node['polarity'] for node in nodes])
        
        # Connect conditionals, causals
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if i == j:
                    continue
                if node_i['type'] == 'conditional':
                    if node_i.get('consequent', '') in node_j['text']:
                        A[i, j] = 1
                elif node_i['type'] == 'causal':
                    if node_i.get('effect', '') in node_j['text']:
                        A[i, j] = 1
        
        return A, p
    
    def _hebbian_update(self, W: np.ndarray, A: np.ndarray, a: np.ndarray) -> np.ndarray:
        """Hebbian plasticity: strengthen co-activated connections"""
        W += self.eta * (np.outer(a, a) * A)
        W[W < self.tau] = 0
        return W
    
    def _counterfactual_propagate(self, W: np.ndarray, a_init: np.ndarray) -> np.ndarray:
        """Propagate activation through weighted graph"""
        a = a_init.copy()
        for _ in range(self.max_iter):
            a_next = np.clip(W.T @ a, 0, 1)
            if np.sum(np.abs(a_next - a)) < 1e-3:
                break
            a = a_next
        return a
    
    def _score_candidate(self, prompt_nodes: List[Dict], cand_nodes: List[Dict], 
                        A: np.ndarray, W: np.ndarray, p: np.ndarray) -> Tuple[float, str]:
        """Score a candidate using Hebbian-weighted graph + counterfactual reasoning"""
        n = len(prompt_nodes)
        
        # Activation vector for candidate
        a_cand = np.zeros(n)
        for i, pnode in enumerate(prompt_nodes):
            for cnode in cand_nodes:
                if pnode['text'] in cnode['text'] or cnode['text'] in pnode['text']:
                    a_cand[i] = 1 if cnode['polarity'] == pnode['polarity'] else 0.5
        
        # Counterfactual: toggle conditional antecedents
        a_cf = a_cand.copy()
        for i, node in enumerate(prompt_nodes):
            if node['type'] == 'conditional':
                a_cf[i] = 1 - a_cf[i]  # Do-calculus intervention
        
        # Propagate
        a_final = self._counterfactual_propagate(W, a_cf)
        
        # Scoring: match vs conflict
        match = np.sum(W * np.outer(a_final, a_final)) / (np.sum(W) + 1e-6)
        conflict = 0
        for i in range(n):
            for j in range(n):
                if W[i, j] > 0 and p[i] * p[j] < 0 and a_final[i] * a_final[j] > 0.5:
                    conflict += W[i, j]
        
        structural_score = match - 0.5 * conflict / (np.sum(W) + 1e-6)
        
        # Numeric computation
        numeric_score = self._evaluate_numeric(prompt_nodes, cand_nodes)
        
        # NCD tiebreaker
        prompt_text = ' '.join([n['text'] for n in prompt_nodes])
        cand_text = ' '.join([n['text'] for n in cand_nodes])
        ncd = self._ncd(prompt_text, cand_text)
        
        # Combine: 50% structural, 30% numeric, 15% NCD, 5% activation
        final_score = 0.5 * structural_score + 0.3 * numeric_score + 0.15 * (1 - ncd) + 0.05 * np.mean(a_final)
        
        reasoning = f"struct={structural_score:.2f} num={numeric_score:.2f} ncd={ncd:.2f}"
        return final_score, reasoning
    
    def _evaluate_numeric(self, prompt_nodes: List[Dict], cand_nodes: List[Dict]) -> float:
        """Evaluate numeric comparisons"""
        for pnode in prompt_nodes:
            if pnode['type'] == 'comparison':
                try:
                    left = float(pnode['left'])
                    right = float(pnode['right'])
                    op = pnode['op']
                    
                    truth = False
                    if '>' in op or 'greater' in op or 'more' in op:
                        truth = left > right
                    elif '<' in op or 'less' in op or 'smaller' in op:
                        truth = left < right
                    elif '=' in op or 'equal' in op:
                        truth = abs(left - right) < 1e-6
                    
                    # Check if candidate agrees
                    cand_text = ' '.join([n['text'] for n in cand_nodes]).lower()
                    if truth and ('yes' in cand_text or 'true' in cand_text or 'correct' in cand_text):
                        return 1.0
                    elif not truth and ('no' in cand_text or 'false' in cand_text or 'incorrect' in cand_text):
                        return 1.0
                except:
                    pass
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        import zlib
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by score"""
        # Extract prompt structure
        prompt_nodes = self._tokenize_and_extract(prompt)
        A, p = self._build_graph(prompt_nodes)
        W = np.ones_like(A, dtype=float)
        
        # Train on prompt (self-supervision)
        a_prompt = np.ones(len(prompt_nodes))
        W = self._hebbian_update(W, A, a_prompt)
        
        # Score each candidate
        results = []
        for cand in candidates:
            cand_nodes = self._tokenize_and_extract(cand)
            score, reasoning = self._score_candidate(prompt_nodes, cand_nodes, A, W, p)
            results.append({'candidate': cand, 'score': score, 'reasoning': reasoning})
        
        # Normalize scores
        scores = [r['score'] for r in results]
        if max(scores) > min(scores):
            for r in results:
                r['score'] = (r['score'] - min(scores)) / (max(scores) - min(scores))
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, with epistemic honesty"""
        # Meta-confidence: evaluate prompt quality
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Structural confidence
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.2
        
        base_score = results[0]['score']
        
        # Check for structural parsers matching
        prompt_nodes = self._tokenize_and_extract(prompt)
        has_structure = any(n['type'] in ['comparison', 'conditional', 'causal'] for n in prompt_nodes)
        
        if not has_structure:
            # No structural match -> honest uncertainty
            return min(0.25, base_score * meta_conf)
        
        # Cap confidence unless we have definitive computation
        answer_nodes = self._tokenize_and_extract(answer)
        has_numeric = any(n['type'] == 'comparison' for n in prompt_nodes)
        
        if has_numeric and base_score > 0.8:
            return min(0.85 * meta_conf, base_score * meta_conf)
        
        # Default: moderate confidence, scaled by meta
        return min(0.7, base_score * 0.8) * meta_conf
```

</details>
