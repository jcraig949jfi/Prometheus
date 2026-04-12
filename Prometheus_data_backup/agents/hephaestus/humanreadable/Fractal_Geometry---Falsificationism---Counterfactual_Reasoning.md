# Fractal Geometry + Falsificationism + Counterfactual Reasoning

**Fields**: Mathematics, Philosophy, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T13:56:35.086637
**Report Generated**: 2026-03-27T06:37:37.130295

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions (e.g., “X > Y”, “because Z”, “not W”) and their logical connectors (negation, conditional, comparative, causal). Each proposition becomes a node in a directed hypergraph G = (V,E). Nodes store: a boolean truth value, a numeric feature vector f ∈ ℝᵏ (extracted numbers, units), and a scale label s ∈ ℕ (initially 0). Edges encode inference rules (modus ponens, transitivity, causal do‑calculus).  
2. **Fractal scaling** – Apply an iterated‑function‑system (IFS) transformation to generate self‑similar copies of G at scales s = 0,1,…,S. For each scale, copy V and E, incrementing the scale label and perturbing numeric features by a factor αˢ (α ∈ (0,1)). The collection of nodes across scales forms a multi‑scale adjacency tensor A ∈ {0,1}^{(|V|·(S+1))×(|V|·(S+1))}. Compute a box‑counting estimate of the Hausdorff dimension D by measuring how the number of nodes needed to cover G grows with scale (using numpy log‑log regression).  
3. **Falsificationist counterfactual testing** – For a candidate answer H (a distinguished node), generate counterfactual worlds by toggling the truth of randomly selected atomic propositions at each scale (the “do‑intervention”). After each toggle, propagate truth values through G using boolean matrix multiplication (A @ truth) until convergence (modus ponens & transitivity). If H evaluates to False in a world, record a falsification. Repeat for N worlds per scale.  
4. **Scoring** – Let F be the fraction of worlds where H is falsified. Compute robustness R = 1 − F. Final score = R · (D / D_max), where D_max is the maximum dimension observed across all candidates (normalized to [0,1]). Higher scores indicate answers that survive falsification attempts across self‑similar scales, reflecting strong logical structure.  

**Parsed structural features** – Negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), causal verbs (“because”, “leads to”, “results in”), numeric values with units, ordering relations (“first”, “second”, “more than”), quantifiers (“all”, “some”), and conjunctive/disjunctive connectives.  

**Novelty** – While argument graphs, causal do‑calculus, and fractal dimension analysis exist separately, combining iterative self‑similar perturbation generation with falsificationist robustness scoring is not present in current reasoning‑evaluation literature.  

**Ratings**  
Reasoning: 7/10 — captures logical depth and multi‑scale consistency but relies on heuristic perturbations.  
Metacognition: 5/10 — limited self‑monitoring; no explicit confidence calibration beyond robustness.  
Hypothesis generation: 8/10 — systematic counterfactual worlds via IFS provide rich alternative hypotheses.  
Implementability: 9/10 — uses only regex, numpy for matrix ops and regression, and stdlib data structures.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **6.67** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Fractal Geometry**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Falsificationism**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 34% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Counterfactual Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Falsificationism + Fractal Geometry: strong positive synergy (+0.923). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Counterfactual Reasoning + Fractal Geometry: strong positive synergy (+0.462). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Fractal Geometry + Falsificationism + Counterfactual Reasoning (accuracy: 0%, calibration: 0%)
- Fractal Geometry + Falsificationism + Feedback Control (accuracy: 0%, calibration: 0%)
- Apoptosis + Falsificationism + Self-Organized Criticality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Forged (passed trap battery)

| Metric | Score | vs NCD Baseline |
|--------|-------|-----------------|
| Accuracy | 27% | +7% |
| Calibration | 20% | +13% |

**Forge Timestamp**: 2026-03-26T17:15:07.790853

---

## Code

**Source**: forge

[View code](./Fractal_Geometry---Falsificationism---Counterfactual_Reasoning/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning evaluator combining structural parsing, 
    fractal-scale perturbation (simulated), and falsificationist testing.
    
    Mechanism:
    1. Parses atomic propositions (negations, comparatives, conditionals, numbers).
    2. Constructs a logical graph where nodes are propositions and edges are inference rules.
    3. Simulates 'Fractal Scaling' by generating perturbed versions of the logical state 
       at decreasing scales (alpha^s) to test stability.
    4. Applies 'Falsificationism' by toggling truth values in these scaled worlds.
    5. Scores candidates based on robustness (survival rate) and structural complexity (Hausdorff dimension estimate).
    6. Uses NCD only as a tiebreaker for low-structure cases.
    """

    def __init__(self):
        self.alpha = 0.5  # Scaling factor for fractal perturbation
        self.scales = 3   # Number of fractal iterations
        self.iterations = 20 # Counterfactual worlds per scale

    def _parse_structure(self, text: str) -> Dict:
        """Extracts logical features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower)),
            'causal': len(re.findall(r'\b(because|leads|results|causes|due to)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums]
        return features

    def _build_graph(self, features: Dict) -> Tuple[np.ndarray, int]:
        """
        Creates a simplified adjacency representation based on feature density.
        Returns adjacency matrix and node count.
        """
        # Node types: [negation, comparative, conditional, causal, numeric_cluster]
        # We approximate the graph density based on feature counts
        node_types = 5
        base_nodes = max(1, sum([
            features['negations'], 
            features['comparatives'], 
            features['conditionals'], 
            features['causal'],
            int(len(features['numbers']) > 0)
        ]))
        
        if base_nodes == 0:
            return np.zeros((1, 1)), 1
            
        # Construct a dense enough graph to allow propagation
        size = min(base_nodes, 10) # Cap size for efficiency
        A = np.zeros((size, size))
        
        # Fill with heuristic connectivity (transitivity simulation)
        for i in range(size):
            for j in range(size):
                if i != j:
                    # Higher connectivity if conditionals/causals exist
                    if features['conditionals'] > 0 or features['causal'] > 0:
                        A[i, j] = 1.0 / (abs(i - j) + 1) 
                    else:
                        A[i, j] = 0.5 # Weak connectivity for simple statements
        return A, size

    def _estimate_dimension(self, sizes: List[int]) -> float:
        """Estimates Hausdorff dimension via log-log regression of node coverage."""
        if len(sizes) < 2:
            return 1.0
        x = np.log(np.arange(1, len(sizes) + 1))
        y = np.log(np.array(sizes) + 1e-9) # Avoid log(0)
        # Linear regression slope approximates dimension
        try:
            slope, _ = np.polyfit(x, y, 1)
            return max(0.1, slope) # Ensure positive dimension
        except:
            return 1.0

    def _falsification_test(self, A: np.ndarray, base_truth: np.ndarray, scale: int) -> float:
        """
        Simulates counterfactual worlds by perturbing truth vectors and propagating.
        Returns fraction of worlds where the logical structure collapses (falsified).
        """
        if A.size == 0:
            return 0.0
            
        n = A.shape[0]
        falsifications = 0
        
        for _ in range(self.iterations):
            # Perturb: Flip random bits based on scale (alpha^scale)
            perturbation_prob = (self.alpha ** scale)
            noise = (np.random.rand(n) < perturbation_prob).astype(float)
            
            # Intervention: XOR logic simulation
            current_truth = (base_truth + noise) % 2 
            if np.sum(current_truth) == 0:
                current_truth = np.ones(n) # Ensure at least one true premise
                
            # Propagate (simplified boolean matrix multiplication)
            # Truth spreads if connected
            for _ in range(3): # Convergence steps
                next_truth = (A.T @ current_truth) > 0.5
                current_truth = np.logical_or(current_truth, next_truth).astype(float)
            
            # Check for contradiction (simplified: if all become true or all false unexpectedly)
            # In a robust system, specific patterns hold. Here we check stability.
            if np.sum(current_truth) == 0 or np.sum(current_truth) == n:
                falsifications += 1
                
        return falsifications / self.iterations

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        l1 = len(zlib.compress(s1.encode()))
        l2 = len(zlib.compress(s2.encode()))
        l12 = len(zlib.compress((s1 + s2).encode()))
        if max(l1, l2) == 0:
            return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feats = self._parse_structure(prompt)
        prompt_A, prompt_size = self._build_graph(prompt_feats)
        
        # Baseline dimension of prompt
        base_dims = []
        for s in range(self.scales):
            base_dims.append(prompt_size * (self.alpha ** s))
        D_prompt = self._estimate_dimension(base_dims)
        D_max = D_prompt if D_prompt > 0 else 1.0

        for cand in candidates:
            cand_feats = self._parse_structure(cand)
            cand_A, cand_size = self._build_graph(cand_feats)
            
            # 1. Structural Matching & Numeric Evaluation
            score = 0.0
            
            # Numeric consistency check
            num_match = 1.0
            if prompt_feats['numbers'] and cand_feats['numbers']:
                # Simple check: does the candidate contain numbers present in prompt?
                # Or logical consistency (e.g. 9.11 < 9.9)
                p_nums = sorted(prompt_feats['numbers'])
                c_nums = sorted(cand_feats['numbers'])
                # Heuristic: overlap or logical ordering
                if len(p_nums) > 0 and len(c_nums) > 0:
                    # Check if candidate numbers are a subset or logically derived
                    # For this implementation, we reward presence of prompt numbers
                    overlap = len(set(p_nums) & set(c_nums))
                    num_match = min(1.0, (overlap + 1) / (len(p_nums) + 1))
            
            # Logical feature alignment
            logic_overlap = 0
            total_features = 0
            for key in ['negations', 'comparatives', 'conditionals', 'causal']:
                if prompt_feats[key] > 0:
                    total_features += 1
                    if cand_feats[key] > 0:
                        logic_overlap += 1
            logic_score = logic_overlap / max(1, total_features)
            
            # 2. Fractal-Falsification Robustness
            # Create initial truth vector (all true initially)
            if cand_size > 0:
                base_truth = np.ones(cand_size)
                falsification_rate = 0.0
                dims_at_scale = []
                
                for s in range(self.scales):
                    # Perturb and test
                    f_rate = self._falsification_test(cand_A, base_truth, s)
                    falsification_rate += f_rate
                    dims_at_scale.append(cand_size * (self.alpha ** s))
                
                falsification_rate /= self.scales
                robustness = 1.0 - falsification_rate
                
                # Dimension estimate for candidate
                D_cand = self._estimate_dimension(dims_at_scale)
                dim_factor = min(1.0, D_cand / max(0.1, D_max))
                
                # Final Score Composition
                # Primary: Logic match and Robustness
                # Secondary: Dimensional complexity
                raw_score = (0.4 * logic_score) + (0.4 * robustness) + (0.2 * dim_factor * num_match)
                
                # Boost if numeric logic is explicitly satisfied (heuristic boost)
                if prompt_feats['numbers'] and cand_feats['numbers']:
                     # Simple numeric sanity: if prompt has 2 numbers, candidate should too
                     if len(cand_feats['numbers']) >= len(prompt_feats['numbers']) * 0.5:
                         raw_score *= 1.1
            else:
                # Fallback for empty structure
                raw_score = logic_score * 0.5

            # 3. NCD Tiebreaker (only if structural signal is weak)
            if raw_score < 0.3:
                ncd_val = self._ncd(prompt, cand)
                # Lower NCD is better (more similar), invert for score
                raw_score += (1.0 - ncd_val) * 0.2

            results.append({
                "candidate": cand,
                "score": float(np.clip(raw_score, 0, 1)),
                "reasoning": f"Logic:{logic_score:.2f}, Robust:{1.0-falsification_rate:.2f}, Dim:{D_max:.2f}" if cand_size>0 else "Low structure"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and falsification robustness.
        Restricted usage of counterfactuals as per guidelines.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to confidence
        # High structural match + high robustness = high confidence
        base_conf = res[0]['score']
        
        # Penalty for very short answers that lack structure (unless prompt is simple)
        if len(answer.split()) < 3 and len(prompt.split()) > 10:
            base_conf *= 0.8
            
        return float(np.clip(base_conf, 0.0, 1.0))
```

</details>
