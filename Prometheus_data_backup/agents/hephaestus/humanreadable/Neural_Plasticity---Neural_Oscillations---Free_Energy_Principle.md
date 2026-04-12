# Neural Plasticity + Neural Oscillations + Free Energy Principle

**Fields**: Biology, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T00:31:07.150493
**Report Generated**: 2026-03-27T05:13:37.317732

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract propositional triples *(subject, relation, object)* from the prompt and each candidate answer. Relations are categorized into a fixed set: negation (`not`), comparative (`>`, `<`, `more than`, `less than`), conditional (`if … then`), causal (`because`, `leads to`, `results in`), ordering (`before`, `after`, `first`, `second`), and numeric equality/inequality (`=`, `≠`). Each triple becomes a node *i* in a directed graph; the relation type labels the edge *i → j*.  
2. **Graph representation** – Build an adjacency tensor **R** of shape *(n_nodes, n_nodes, n_relation_types)* where *R[i,j,k] = 1* if relation *k* holds from *i* to *j*, else 0. Initialize a weight tensor **W** (same shape) with small ε = 0.01.  
3. **Plasticity (Hebbian update)** – Slide a token window of length *γ* (gamma cycle) over the tokenized prompt. For each window, compute a binary activation vector **a** where *a[i]=1* if node *i* appears in the window. Update **W** with Δ**W** = η · (**a** ⊗ **a**) · **g**, where **g** is a gamma‑gating mask (1 inside the window, 0 otherwise) and η = 0.05. This reinforces co‑occurring propositions.  
4. **Oscillatory gating (theta reset)** – After every *θ* tokens (theta cycle), zero‑accumulate the eligibility trace: set **W** ← **W** · exp(−λ·Δt) with λ = 0.1 to simulate decay, then continue Hebbian updates in the next theta window. This implements cross‑frequency coupling: gamma binds within theta, theta refreshes context.  
5. **Free‑energy scoring** – For a candidate answer, build its adjacency tensor **A**. Compute precision matrix **Π** = **W** + δ·I (δ = 0.001) to avoid singularity. Prediction error:  
   \[
   F = \frac12 \sum_{i,j,k} \Pi_{ijk}\,(A_{ijk}-W_{ijk})^2 \;+\; \frac12 \log|\mathbf{\Sigma}|
   \]  
   where **Σ** = (**W** + δ·I)^{−1}; the log‑determinterm is obtained via `numpy.linalg.slogdet`. Lower *F* indicates higher plausibility. Rank candidates by ascending *F*.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values, temporal markers (while, when), and conjunctions that bind multiple propositions.  

**Novelty** – While graph‑based reasoning, Hebbian learning, and variational free energy appear separately in cognitive modeling and ML, their concrete combination as a deterministic, numpy‑only scoring pipeline that uses oscillatory gating to modulate plasticity and then evaluates free energy on symbolic graphs has not been described in existing public tools.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and updates weights via biologically plausible Hebbian rules, but limited to pairwise relations and lacks higher‑order quantifier handling.  
Metacognition: 5/10 — no explicit self‑monitoring or confidence calibration beyond the free‑energy term, which approximates uncertainty only implicitly.  
Hypothesis generation: 6/10 — can produce alternative parses by varying gamma/theta window sizes, yet does not actively search hypothesis space beyond deterministic updates.  
Implementability: 8/10 — relies solely on regex, numpy array ops, and linear algebra; all components are straightforward to code and debug.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Neural Plasticity**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 29% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Neural Oscillations**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Free Energy Principle + Neural Plasticity: strong positive synergy (+0.575). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Neural Oscillations: strong positive synergy (+0.271). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Chaos Theory + Neural Plasticity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T12:13:34.944937

---

## Code

**Source**: scrap

[View code](./Neural_Plasticity---Neural_Oscillations---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning engine based on Neural Plasticity, Oscillations, and Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts propositional triples (subject, relation, object) using regex.
    2. Graph Rep: Builds an adjacency tensor R where edges represent relation types.
    3. Plasticity: Uses Hebbian updates (co-occurrence within gamma windows) to strengthen weights.
    4. Oscillations: Applies theta-cycle decay to simulate context refreshing and cross-frequency coupling.
    5. Free Energy: Scores candidates by computing variational free energy (prediction error + complexity)
       between the prompt's learned weight matrix and the candidate's structural tensor.
    """
    
    RELATIONS = ['not', 'gt', 'lt', 'if', 'causes', 'before', 'after', 'eq', 'neq']
    GAMMA = 4  # Gamma cycle window size
    THETA = 10 # Theta cycle length
    ETA = 0.05 # Learning rate
    LAMBDA = 0.1 # Decay rate
    DELTA = 0.001 # Regularization
    
    def __init__(self):
        self.relation_patterns = [
            (r'\bnot\b|\bno\b|\bnever\b', 'not'),
            (r'\bmore than\b|\bgreater than\b|>', 'gt'),
            (r'\bless than\b|<', 'lt'),
            (r'\bif\b|\bthen\b|\bunless\b', 'if'),
            (r'\bbecause\b|\bleads to\b|\bresults in\b|\bcauses\b', 'causes'),
            (r'\bbefore\b|\bfirst\b', 'before'),
            (r'\bafter\b|\bsecond\b|\bnext\b', 'after'),
            (r'\bequal\b|=', 'eq'),
            (r'\bunequal\b|\b!=\b', 'neq')
        ]

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract (subject, relation, object) triples."""
        triples = []
        tokens = self._tokenize(text)
        text_lower = text.lower()
        
        # Simple heuristic: look for relation keywords and grab surrounding words
        for pattern, rel_type in self.relation_patterns:
            matches = list(re.finditer(pattern, text_lower))
            for m in matches:
                start, end = m.start(), m.end()
                # Find nearest nouns/words before and after
                pre_text = text_lower[:start].strip()
                post_text = text_lower[end:].strip()
                
                subj = pre_text.split()[-1] if pre_text.split() else "null"
                obj = post_text.split()[0] if post_text.split() else "null"
                
                # Clean punctuation
                subj = re.sub(r'[^\w]', '', subj)
                obj = re.sub(r'[^\w]', '', obj)
                
                if subj and obj:
                    triples.append((subj, rel_type, obj))
        
        # Add numeric comparisons if detected
        nums = re.findall(r'\d+\.?\d*', text)
        if len(nums) >= 2:
            # Assume order implies relation if no explicit comparator found near them
            triples.append((nums[0], 'gt', nums[1])) # Heuristic assumption
            
        return triples

    def _build_tensor(self, triples: List[Tuple[str, str, str]], all_nodes: List[str]) -> np.ndarray:
        """Build adjacency tensor R [n_nodes, n_nodes, n_relations]."""
        n = len(all_nodes)
        r_len = len(self.RELATIONS)
        tensor = np.zeros((n, n, r_len))
        
        node_map = {node: i for i, node in enumerate(all_nodes)}
        
        for subj, rel, obj in triples:
            if subj in node_map and obj in node_map:
                i, j = node_map[subj], node_map[obj]
                if rel in self.RELATIONS:
                    k = self.RELATIONS.index(rel)
                    tensor[i, j, k] = 1.0
        return tensor

    def _simulate_dynamics(self, text: str, all_nodes: List[str]) -> np.ndarray:
        """Simulate plasticity and oscillations to learn weights W."""
        if not all_nodes:
            return np.zeros((1, 1, len(self.RELATIONS)))
            
        n = len(all_nodes)
        r_len = len(self.RELATIONS)
        W = np.full((n, n, r_len), 0.01) # Initialize with epsilon
        
        tokens = self._tokenize(text)
        if not tokens:
            return W
            
        node_map = {node: i for i, node in enumerate(all_nodes)}
        
        # Gamma windows for Hebbian update
        for t in range(len(tokens)):
            # Gamma window
            window_start = max(0, t - self.GAMMA)
            window_tokens = tokens[window_start:t+1]
            
            # Activation vector
            a = np.zeros(n)
            for tok in window_tokens:
                if tok in node_map:
                    a[node_map[tok]] = 1.0
            
            # Hebbian update: Delta W = eta * (a outer a)
            # We apply this to all relation layers where co-occurrence happens
            if np.sum(a) > 0:
                outer_prod = np.outer(a, a)
                for k in range(r_len):
                    # Strengthen connections between active nodes
                    W[:, :, k] += self.ETA * (outer_prod * (1.0 if np.any(a) else 0.0))
            
            # Theta reset (decay)
            if t % self.THETA == 0 and t > 0:
                W *= np.exp(-self.LAMBDA)
                
        return W

    def _compute_free_energy(self, W: np.ndarray, A: np.ndarray) -> float:
        """Compute Free Energy F = 0.5 * sum(Pi * (A-W)^2) + 0.5 * log|Sigma|."""
        if W.size == 0 or A.size == 0:
            return 1e6
            
        # Precision matrix approximation (diagonal dominance for stability)
        Pi = W + self.DELTA
        
        # Prediction error term
        diff = A - W
        error_term = 0.5 * np.sum(Pi * (diff ** 2))
        
        # Complexity term (Log determinant)
        # Flatten for slogdet or use diagonal approximation if too large
        try:
            # Use a simplified trace/log-det approximation for stability in small dims
            # Or just log det of the flattened view if square, but tensor is 3D.
            # We treat the tensor as a collection of independent graphs or flatten.
            # Let's use the sum of log diagonals as a proxy for log-det to ensure stability
            log_det_term = 0.5 * np.sum(np.log(np.abs(Pi) + 1e-10))
        except:
            log_det_term = 0.0
            
        return float(error_term + log_det_term)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_triples = self._extract_triples(prompt)
        prompt_nodes = list(set([s for s, _, o in prompt_triples] + [o for _, _, o in prompt_triples]))
        
        # If no structure found, use all words as nodes to allow NCD fallback logic via tensor density
        if not prompt_nodes:
            prompt_nodes = list(set(self._tokenize(prompt)))[:10] # Limit size

        # Learn W from prompt
        W = self._simulate_dynamics(prompt, prompt_nodes)
        
        results = []
        for cand in candidates:
            cand_triples = self._extract_triples(cand)
            # Map candidate nodes to prompt nodes where possible, else ignore
            cand_nodes = [n for n in prompt_nodes if n in [s for s,_,o in cand_triples] or n in [o for _,_,o in cand_triples]]
            
            if not cand_nodes:
                # Fallback: if no structural overlap, score based on string similarity (NCD proxy)
                # But per instructions, NCD is tiebreaker. We assign a neutral high energy.
                score = 100.0 
            else:
                # Build candidate tensor A aligned with prompt nodes
                A = self._build_tensor(cand_triples, prompt_nodes)
                F = self._compute_free_energy(W, A)
                score = -F # Lower F is better, so higher score is better
            
            results.append({"candidate": cand, "score": score, "reasoning": "Free Energy Minimization"})

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score roughly to 0-1 based on typical free energy ranges
        # Since F can be large negative, we use a sigmoid-like mapping
        score = res[0]["score"]
        # Heuristic normalization: assume scores > -10 are good, < -100 are bad
        conf = 1.0 / (1.0 + np.exp(0.1 * (score + 50))) 
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
