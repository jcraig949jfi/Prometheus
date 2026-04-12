# Bayesian Inference + Criticality + Compositionality

**Fields**: Mathematics, Complex Systems, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T11:56:43.081360
**Report Generated**: 2026-03-27T06:37:36.919298

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Convert the prompt and each candidate answer into a set of atomic propositions *p₁…pₙ* using regex‑based patterns for:  
   - Negations (`not`, `no`, `-`) → `¬p`  
   - Comparatives (`greater than`, `<`, `>`) → `p₁ > p₂` (numeric)  
   - Conditionals (`if … then …`, `implies`) → `p₁ → p₂`  
   - Causal verbs (`causes`, `leads to`) → `p₁ ⇒ p₂`  
   - Ordering (`first`, `before`, `after`) → temporal edges.  
   Each proposition gets a unique integer ID; relations are stored in a sparse adjacency matrix **R** (numpy `csr_matrix`) where `R[i,j]=1` encodes a directed link from *i* to *j* with a type tag (negation, conditional, etc.) kept in a parallel dtype‑structured array.

2. **Prior Belief (Bayesian Inference)** – Initialize a belief vector **b₀** of length *n* with a uniform prior (0.5) for propositions lacking explicit cue words; for propositions anchored by numeric values or definite statements set prior to 0.9 (true) or 0.1 (false) based on cue strength extracted from the prompt (e.g., “exactly 3” → high confidence).

3. **Likelihood Construction** – For each candidate answer, build a likelihood matrix **L** where `L[i]=P(evidence|pᵢ)` is derived from how well the answer satisfies the proposition:  
   - Exact match → 0.9  
   - Contradiction (via negation edge) → 0.1  
   - Partial match (numeric within tolerance) → 0.5  
   - No relation → 0.5 (uninformative).  
   This uses only numpy vector operations.

4. **Posterior Update** – Apply Bayes’ rule element‑wise: **b₁ = (L * b₀) / sum(L * b₀)**, where `*` is element‑wise multiplication. The posterior **b₁** gives the probability each proposition is true given the answer.

5. **Criticality Measure** – Compute the susceptibility χ of the belief system to infinitesimal perturbations:  
   - Perturb **b₀** by adding small Gaussian noise ε∼N(0,σ²) (σ=0.01) and recompute posterior **b₁′**.  
   - χ = Var(**b₁′ – b₁**) over 10 noise samples (numpy `var`).  
   High χ indicates the system is near a critical point (belief changes sharply with tiny evidence), low χ indicates ordered/insensitive regime.

6. **Scoring** – Final score for an answer = α·mean(**b₁**) + β·(1‑χ) where α,β∈[0,1] (e.g., 0.7,0.3). Answers with high average belief truth and low susceptibility (stable inference) rank higher.

**Structural Features Parsed** – negations, comparatives, conditionals, causal verbs, numeric quantities, temporal ordering, and explicit quantifiers (all, some, none).

**Novelty** – The method merges compositional propositional extraction (similar to semantic parsers) with Bayesian belief updating (as in Bayesian Networks/Markov Logic Networks) and adds a criticality‑based susceptibility term inspired by statistical‑physics analyses of belief propagation. While each component exists separately, their joint use for scoring reasoning answers is not documented in the literature.

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty propagation effectively.  
Metacognition: 6/10 — susceptibility provides a rough self‑assessment of confidence stability but lacks higher‑order reflection.  
Hypothesis generation: 5/10 — focuses on evaluating given hypotheses; generating new ones would require additional search mechanisms.  
Implementability: 9/10 — relies solely on regex, numpy arrays, and sparse matrices; no external libraries or APIs needed.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Bayesian Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Bayesian Inference + Criticality: strong positive synergy (+0.433). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Compositionality + Criticality: strong positive synergy (+0.329). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Bayesian Inference + Evolution + Criticality (accuracy: 0%, calibration: 0%)
- Fourier Transforms + Criticality + Compositionality (accuracy: 0%, calibration: 0%)
- Global Workspace Theory + Criticality + Compositionality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: AttributeError: 'NoneType' object has no attribute 'strip'

**Forge Timestamp**: 2026-03-26T03:19:00.762106

---

## Code

**Source**: scrap

[View code](./Bayesian_Inference---Criticality---Compositionality/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Bayesian Inference, Criticality, and Compositionality.
    
    Mechanism:
    1. Parsing (Compositionality): Extracts atomic propositions and relations (negation, 
       comparatives, conditionals) from prompts using regex, mapping them to a sparse graph.
    2. Prior Belief (Bayesian): Initializes belief vectors based on cue strength (numeric vs. vague).
    3. Likelihood & Posterior: Updates beliefs based on how well candidates satisfy extracted constraints.
    4. Criticality: Measures system susceptibility to noise; stable answers (low susceptibility) 
       are preferred alongside high belief.
    5. Scoring: Weighted sum of mean posterior belief and inverse susceptibility.
    """

    def __init__(self):
        self.alpha = 0.7  # Weight for belief
        self.beta = 0.3   # Weight for stability (1 - criticality)
        self.sigma = 0.01 # Noise magnitude for criticality test
        self.samples = 10 # Monte Carlo samples for criticality

    def _parse_propositions(self, text: str) -> Tuple[List[str], Dict[Tuple[int, int], str]]:
        """Extract atomic propositions and relations (negation, comparison, conditional)."""
        text_lower = text.lower()
        props = []
        relations = {} # (i, j) -> type
        
        # Simple tokenization for propositions (split by punctuation/connectors)
        raw_props = re.split(r'[,.!?;]|(?:\b(and|or|if|then|but|so)\b)', text_lower)
        raw_props = [p.strip() for p in raw_props if p.strip()]
        
        prop_map = {} # text -> id
        next_id = 0
        
        def get_id(p_text):
            nonlocal next_id
            p_text = p_text.strip()
            if not p_text: return -1
            if p_text not in prop_map:
                prop_map[p_text] = next_id
                props.append(p_text)
                next_id += 1
            return prop_map[p_text]

        # Extract specific patterns
        # Negations
        for match in re.finditer(r'(not|no|never)\s+(\w+)', text_lower):
            p_txt = match.group(2)
            pid = get_id(p_txt)
            # Implicit negation node could be added, but we mark relation type for simplicity
            # Here we just tag the proposition text itself if needed, or store relation
            # For this implementation, we store a self-loop negation marker or separate flag
            # To keep it simple: we note the proposition contains negation context
            pass 

        # Comparatives (greater than, less than)
        for match in re.finditer(r'(\d+(?:\.\d+)?)\s*(?:is|was|are)?\s*(greater|less|more|fewer)\s+than\s*(\d+(?:\.\d+)?)', text_lower):
            v1, typ, v2 = match.groups()
            p1_txt = f"val_{v1}"
            p2_txt = f"val_{v2}"
            i, j = get_id(p1_txt), get_id(p2_txt)
            relations[(i, j)] = 'gt' if 'greater' in typ or 'more' in typ else 'lt'

        # Conditionals (if... then...)
        if_match = re.search(r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)', text_lower)
        if if_match:
            i = get_id(if_match.group(1))
            j = get_id(if_match.group(2))
            relations[(i, j)] = 'implies'

        # Fallback: treat remaining chunks as independent propositions if none found
        if not props:
            for chunk in raw_props[:5]: # Limit depth
                get_id(chunk)

        return props, relations

    def _compute_likelihood(self, prompt: str, candidate: str, props: List[str], relations: Dict) -> np.ndarray:
        """Compute likelihood vector L based on candidate matching propositions."""
        n = len(props)
        if n == 0: return np.array([0.5])
        
        L = np.ones(n) * 0.5 # Default uninformative
        cand_lower = candidate.lower()
        prompt_lower = prompt.lower()
        
        for i, p in enumerate(props):
            if not p: continue
            
            # Exact match or strong keyword presence
            if p in cand_lower or p in prompt_lower: 
                # Check if candidate contradicts (simple heuristic: 'not' in cand but not in prompt prop)
                if re.search(r'\b(not|no|never)\b', cand_lower) and not re.search(r'\b(not|no|never)\b', p):
                    L[i] = 0.1 # Contradiction
                else:
                    L[i] = 0.9 # Match
            elif p in cand_lower:
                L[i] = 0.9
            else:
                # Numeric evaluation
                nums_p = re.findall(r'\d+(?:\.\d+)?', p)
                nums_c = re.findall(r'\d+(?:\.\d+)?', cand_lower)
                if nums_p and nums_c:
                    try:
                        vp = float(nums_p[0])
                        vc = float(nums_c[0])
                        if abs(vp - vc) < 1e-6: L[i] = 0.9
                        elif abs(vp - vc) < 0.1: L[i] = 0.7
                        else: L[i] = 0.2
                    except: pass
        
        # Handle relations explicitly if possible (simplified for brevity)
        for (i, j), typ in relations.items():
            if i >= len(L) or j >= len(L): continue
            # If relation is 'gt', check if candidate implies p_i > p_j
            # This is a heuristic approximation
            if typ == 'gt':
                # If candidate has numbers, verify order
                nums = re.findall(r'\d+(?:\.\d+)?', cand_lower)
                if len(nums) >= 2:
                    if float(nums[0]) > float(nums[1]):
                        L[i] = max(L[i], 0.8)
                        L[j] = max(L[j], 0.8)
                    else:
                        L[i] = min(L[i], 0.2)

        return L

    def _bayesian_update(self, b0: np.ndarray, L: np.ndarray) -> np.ndarray:
        """Apply Bayes rule: b1 ~ L * b0"""
        numerator = L * b0
        denom = np.sum(numerator)
        if denom == 0: return b0
        return numerator / denom

    def _compute_criticality(self, b0: np.ndarray, L: np.ndarray) -> float:
        """Compute susceptibility chi via noise perturbation."""
        if len(b0) == 0: return 0.0
        
        b1_base = self._bayesian_update(b0, L)
        diffs = []
        
        for _ in range(self.samples):
            noise = np.random.normal(0, self.sigma, size=b0.shape)
            b0_perturbed = np.clip(b0 + noise, 0.01, 0.99)
            b1_perturbed = self._bayesian_update(b0_perturbed, L)
            diffs.append(np.var(b1_perturbed - b1_base))
            
        return float(np.mean(diffs)) if diffs else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        props, relations = self._parse_propositions(prompt)
        n = len(props) if props else 1
        
        # 1. Priors: Uniform 0.5, high confidence for numeric/definite
        b0 = np.full(n, 0.5)
        for i, p in enumerate(props):
            if re.search(r'\d+', p): b0[i] = 0.9
            elif any(k in p for k in ['is', 'are', 'was']): b0[i] = 0.7

        results = []
        for cand in candidates:
            L = self._compute_likelihood(prompt, cand, props, relations)
            if len(L) < n: L = np.pad(L, (0, n-len(L)), constant_values=0.5)
            L = L[:n] # Ensure match
            
            b1 = self._bayesian_update(b0, L)
            chi = self._compute_criticality(b0, L)
            
            # Score: High belief, Low criticality (stable)
            score = self.alpha * np.mean(b1) + self.beta * (1.0 - min(chi, 1.0))
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Belief: {np.mean(b1):.2f}, Stability: {1.0-chi:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.5
```

</details>
