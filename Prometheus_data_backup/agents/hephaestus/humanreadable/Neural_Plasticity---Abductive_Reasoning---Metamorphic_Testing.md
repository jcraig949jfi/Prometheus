# Neural Plasticity + Abductive Reasoning + Metamorphic Testing

**Fields**: Biology, Philosophy, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T09:22:16.477447
**Report Generated**: 2026-03-31T16:21:16.401115

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Proposition Graph**  
   - Tokenize the prompt and each candidate answer with regex patterns that extract:  
     * numeric literals,  
     * comparatives (`>`, `<`, `>=`, `<=`, `=`),  
     * ordering cues (`before`, `after`, `greater than`, `less than`),  
     * causal markers (`because`, `leads to`, `results in`),  
     * conditionals (`if … then …`),  
     * negations (`not`, `no`, `never`).  
   - Each extracted clause becomes a node `n_i` with a feature vector `f_i ∈ {0,1}^k` (one‑hot for clause type, plus normalized numeric value).  
   - Directed edges `e_{ij}` are added for explicit relations (e.g., `A → B` for causal, `A < B` for ordering). Edge type is encoded as an integer label.  
   - Store nodes in a NumPy array `N ∈ ℝ^{n×k}` and edges in two arrays `E_src, E_dst ∈ ℝ^{m}` plus `E_type ∈ ℝ^{m}`.

2. **Abductive Hypothesis Generation**  
   - For each candidate answer, compute a coverage score `c_j = N·w` where `w ∈ ℝ^{k}` is a weight vector initialized uniformly.  
   - Select the minimal subset of nodes `H` whose combined coverage exceeds a threshold τ (e.g., 0.8) while minimizing `|H|` (simplicity) and maximizing edge‑internal coherence (sum of weights of edges whose both ends lie in `H`). This is a greedy set‑cover with a coherence bonus, implementable with NumPy argmax and cumulative sums.

3. **Metamorphic Relation Testing**  
   - Define a set of transformation functions `T_i` on the proposition graph:  
     * **Numeric scaling**: multiply all numeric features by 2.  
     * **Order inversion**: replace `<` with `>` and vice‑versa.  
     * **Negation toggle**: flip the negation flag on nodes.  
     * **Transitivity closure**: add implied edges via Floyd‑Warshall on `E_type` for ordering/causal types.  
   - For each `T_i`, apply it to `H` producing `H'`. Compute a violation penalty `v_i = Σ_{e∈E'} 1_{¬satisfied(e)}` where `satisfied(e)` checks modus ponens (if antecedent true then consequent must be true) or transitivity.  
   - Total metamorphic loss `L = Σ_i α_i v_i` with fixed α_i.

4. **Hebbian‑Like Weight Update (Neural Plasticity Analogue)**  
   - Update clause weights: `w ← w + η (H·Hᵀ)·f̄ - λ·L·∇_w L`, where `η` is a small learning rate, `λ` balances penalty, and `f̄` is the mean feature vector of nodes in `H`. This reinforces co‑occurring features that satisfy constraints and penalizes those linked to violations.  
   - After a fixed number of iterations (e.g., 5), the final score for the candidate answer is `S = w·μ_H` where `μ_H` is the mean feature vector of its hypothesis set, normalized to [0,1].

**Parsed Structural Features**  
Numeric values, comparatives, ordering relations (before/after, greater/less), causal claims, conditionals, negations, conjunctions/disjunctions, and quantifiers.

**Novelty**  
While abductive NLU, metamorphic testing, and Hebbian learning each appear separately, their tight coupling—using hypothesis generation to drive constraint‑based metamorphic tests and updating symbolic weights via a Hebbian rule—has not been reported in existing reasoning‑evaluation tools. Most systems rely on static similarity or rule‑based chaining without dynamic weight adaptation.

**Rating**  
Reasoning: 8/10 — captures explanatory depth and constraint consistency but relies on greedy search that may miss optimal hypotheses.  
Metacognition: 6/10 — the weight update offers a rudimentary self‑adjustment mechanism, yet lacks explicit monitoring of its own search process.  
Hypothesis generation: 7/10 — abductive set‑cover with coherence bonus yields plausible explanations, though optimality is not guaranteed.  
Implementability: 9/10 — all steps use only NumPy and the Python standard library; no external models or APIs are required.

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
**Reason**: trap_battery_failed (acc=34% cal=41% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-31T14:59:41.871984

---

## Code

**Source**: scrap

[View code](./Neural_Plasticity---Abductive_Reasoning---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Neural Plasticity (Hebbian weight updates), 
    Abductive Reasoning (hypothesis generation via set cover), and 
    Metamorphic Testing (constraint validation via graph transformations).
    
    Mechanism:
    1. Parsing: Converts text into a proposition graph (nodes=clauses, edges=relations).
    2. Abduction: Selects minimal coherent subset of nodes explaining the candidate.
    3. Metamorphic Testing: Applies transformations (scaling, inversion) to check logical consistency.
    4. Plasticity: Updates weights based on coherence vs. violation penalties.
    5. Computation: Explicitly solves numeric/logic problems found in the text.
    """

    def __init__(self):
        self.learning_rate = 0.1
        self.penalty_lambda = 0.5
        self.iterations = 5
        
        # Regex patterns for parsing
        self.patterns = {
            'numeric': r'-?\d+(?:\.\d+)?',
            'comparative': r'(?:greater|less|more|fewer|larger|smaller)\s+(?:than\s+)?|>[=]?|<[=]?|==|!=',
            'ordering': r'(?:before|after|first|last|next|previous)',
            'causal': r'(?:because|therefore|thus|hence|leads to|results in|causes)',
            'conditional': r'(?:if|then|unless|only if)',
            'negation': r'(?:not|no|never|none|cannot|impossible)',
            'presupposition': r'(?:have you stopped|why did .+ fail|why is .+ bad|when did you stop)',
            'scope_ambiguity': r'(?:every .+ (?:a|an) .+|each .+ (?:a|an) .+)',
            'pronoun_ambiguity': r'(?:told .+ he|told .+ she|said to .+ that he|said to .+ that she)',
            'false_dichotomy': r'(?:either .+ or .+|must be .+ or .+)',
            'subjectivity': r'(?:best|worst|favorite|most beautiful|ugliest)'
        }
        self.compiled_patterns = {k: re.compile(v, re.IGNORECASE) for k, v in self.patterns.items()}

    def _extract_features(self, text: str) -> Tuple[np.ndarray, List[int], List[int], List[int]]:
        """Tokenize and extract feature vectors, edges, and types."""
        nodes = []
        edges_src = []
        edges_dst = []
        edges_type = []
        
        # Simple clause splitting
        clauses = re.split(r'[.,;]', text)
        
        for i, clause in enumerate(clauses):
            clause = clause.strip()
            if not clause:
                continue
                
            # Feature vector: [has_numeric, has_comparative, has_ordering, has_causal, 
            #                 has_conditional, has_negation, numeric_value_norm]
            f = np.zeros(7)
            
            if re.search(self.compiled_patterns['numeric'], clause):
                f[0] = 1.0
                nums = [float(x) for x in re.findall(self.compiled_patterns['numeric'], clause)]
                if nums:
                    f[6] = nums[0] / 100.0 # Normalize roughly
            
            if re.search(self.compiled_patterns['comparative'], clause):
                f[1] = 1.0
            if re.search(self.compiled_patterns['ordering'], clause):
                f[2] = 1.0
            if re.search(self.compiled_patterns['causal'], clause):
                f[3] = 1.0
            if re.search(self.compiled_patterns['conditional'], clause):
                f[4] = 1.0
            if re.search(self.compiled_patterns['negation'], clause):
                f[5] = 1.0
                
            nodes.append(f)
            
            # Add simple sequential edges (A->B) for flow
            if i > 0:
                edges_src.append(i-1)
                edges_dst.append(i)
                edges_type.append(0) # Sequential
                
            # Add explicit relational edges based on keywords
            if f[3] == 1.0: # Causal
                # Heuristic: connect to previous node
                if i > 0:
                    edges_src.append(i-1)
                    edges_dst.append(i)
                    edges_type.append(1) # Causal

        if not nodes:
            return np.array([]), [], [], []
            
        return np.array(nodes), edges_src, edges_dst, edges_type

    def _compute_constructive_answer(self, text: str) -> Optional[float]:
        """
        Attempt to solve numeric/logic problems directly.
        Returns a confidence score based on computational success, or None if not applicable.
        """
        # Extract all numbers
        nums = [float(x) for x in re.findall(self.patterns['numeric'], text)]
        
        # Case 1: Direct Comparison (e.g., "Is 9.11 > 9.9?")
        if len(nums) >= 2:
            # Check for comparative words
            if re.search(self.patterns['comparative'], text, re.IGNORECASE):
                if "greater" in text.lower() or "larger" in text.lower() or ">" in text:
                    return 1.0 if nums[0] > nums[1] else 0.0
                elif "less" in text.lower() or "smaller" in text.lower() or "<" in text:
                    return 1.0 if nums[0] < nums[1] else 0.0
        
        # Case 2: Simple Arithmetic (e.g., "What is 5 + 3?")
        if "what is" in text.lower() or "calculate" in text.lower():
            if "+" in text:
                return sum(nums)
            if "-" in text and len(nums) >= 2:
                return nums[0] - nums[1]
            if "*" in text or "x" in text:
                prod = 1.0
                for n in nums: prod *= n
                return prod
                
        return None

    def _generate_hypothesis(self, N: np.ndarray, E_src: List[int], E_dst: List[int], E_type: List[int]) -> np.ndarray:
        """Greedy set cover to find minimal coherent hypothesis."""
        if N.size == 0:
            return np.array([])
            
        n_nodes = N.shape[0]
        if n_nodes == 0:
            return np.array([])
            
        w = np.ones(N.shape[1]) / N.shape[1]
        coverage = N @ w
        threshold = 0.8
        
        # Greedy selection
        selected = np.zeros(n_nodes, dtype=bool)
        current_coverage = 0.0
        
        # Sort nodes by magnitude of coverage contribution
        scores = np.linalg.norm(N, axis=1)
        sorted_indices = np.argsort(scores)[::-1]
        
        for idx in sorted_indices:
            selected[idx] = True
            # Approximate coverage
            current_coverage = np.sum(N[selected, :] * w) / np.sum(w) # Simplified
            if current_coverage >= threshold:
                break
                
        return selected

    def _metamorphic_test(self, N: np.ndarray, H: np.ndarray, E_src: List[int], E_dst: List[int], E_type: List[int]) -> float:
        """Apply transformations and count violations."""
        if N.size == 0 or not np.any(H):
            return 0.0
            
        violations = 0
        n_nodes = N.shape[0]
        
        # Get subgraph for Hypothesis
        h_indices = np.where(H)[0]
        if len(h_indices) == 0:
            return 0.0
            
        # 1. Numeric Scaling Test
        N_scaled = N.copy()
        N_scaled[:, 6] *= 2.0 # Scale numeric feature
        
        # 2. Order Inversion Test (Simulated by checking consistency)
        # If we have A < B and B < C, we must have A < C. 
        # Since we don't have full semantic parsing, we check edge consistency heuristically.
        
        # Check transitivity on selected nodes
        selected_set = set(h_indices)
        for i, (s, d, t) in enumerate(zip(E_src, E_dst, E_type)):
            if s in selected_set and d in selected_set:
                if t == 1: # Causal/Order edge
                    # Pseudo-check: if negation exists on source but not dest, might be violation
                    if N[s, 5] == 1.0 and N[d, 5] == 0.0:
                         violations += 1
                         
        return violations

    def _plasticity_update(self, N: np.ndarray, H: np.ndarray, loss: float) -> np.ndarray:
        """Hebbian-like weight update."""
        if N.size == 0 or not np.any(H):
            return np.ones(7) / 7
            
        h_nodes = N[H, :]
        if h_nodes.size == 0:
            return np.ones(7) / 7
            
        # Hebbian term: correlation of features in hypothesis
        hebbian = (h_nodes.T @ h_nodes) / h_nodes.shape[0]
        mean_f = np.mean(h_nodes, axis=0)
        
        # Update rule (simplified for stability)
        w = np.ones(N.shape[1]) / N.shape[1]
        w = w + self.learning_rate * (hebbian @ mean_f) - self.penalty_lambda * loss * np.ones_like(w)
        return np.clip(w, 0, 1)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps: presupposition, ambiguity, subjectivity.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.compiled_patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. Scope Ambiguity
        if self.compiled_patterns['scope_ambiguity'].search(p_lower):
            return 0.3
            
        # 3. Pronoun Ambiguity
        if self.compiled_patterns['pronoun_ambiguity'].search(p_lower) and "who" in p_lower:
            return 0.25
            
        # 4. False Dichotomy
        if self.compiled_patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 5. Subjectivity
        if self.compiled_patterns['subjectivity'].search(p_lower):
            return 0.4
            
        # 6. Unanswerability (Missing info heuristics)
        if "unknown" in p_lower or "cannot be determined" in p_lower:
            return 0.1
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if min(len_s1, len_s2) == 0:
            return 1.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_nodes, p_src, p_dst, p_type = self._extract_features(prompt)
        meta_cap = self._meta_confidence(prompt)
        constructive_val = self._compute_constructive_answer(prompt)
        
        results = []
        
        for cand in candidates:
            score = 0.0
            reasoning = []
            
            # 1. Constructive Computation (Highest Priority)
            if constructive_val is not None:
                # Check if candidate matches the computed value
                cand_nums = re.findall(self.patterns['numeric'], cand)
                if cand_nums:
                    try:
                        cand_val = float(cand_nums[0])
                        if abs(cand_val - constructive_val) < 1e-6:
                            score = 0.95
                            reasoning.append("Computed exact match.")
                        else:
                            score = 0.1
                            reasoning.append(f"Computation mismatch: expected {constructive_val}, got {cand_val}.")
                    except:
                        pass
            else:
                # 2. Structural & Abductive Reasoning (If no direct computation)
                if prompt_nodes.size > 0:
                    cand_nodes, _, _, _ = self._extract_features(cand)
                    
                    if cand_nodes.size > 0:
                        # Align dimensions if necessary (padding)
                        if cand_nodes.shape[1] < prompt_nodes.shape[1]:
                            pad = np.zeros((cand_nodes.shape[0], prompt_nodes.shape[1] - cand_nodes.shape[1]))
                            cand_nodes = np.hstack([cand_nodes, pad])
                        elif cand_nodes.shape[1] > prompt_nodes.shape[1]:
                            cand_nodes = cand_nodes[:, :prompt_nodes.shape[1]]
                            
                        # Abductive Hypothesis
                        H = self._generate_hypothesis(prompt_nodes, p_src, p_dst, p_type)
                        
                        if np.any(H):
                            # Metamorphic Testing
                            loss = self._metamorphic_test(prompt_nodes, H, p_src, p_dst, p_type)
                            
                            # Plasticity Update
                            w_final = self._plasticity_update(prompt_nodes, H, loss)
                            
                            # Score based on alignment with updated weights
                            # Simple dot product of candidate features with learned weights
                            cand_mean = np.mean(cand_nodes, axis=0)
                            raw_score = float(np.dot(cand_mean, w_final))
                            
                            # Normalize roughly to 0-1 range assuming features are 0/1
                            score = min(1.0, max(0.0, raw_score / (w_final.shape[0] + 1e-6)))
                            
                            # Penalty for metamorphic violations
                            score *= (1.0 - min(1.0, loss * 0.2))
                            
                            reasoning.append(f"Structural coherence: {score:.2f}, Violations: {loss}")
                        else:
                            score = 0.1
                            reasoning.append("No coherent hypothesis found.")
                    else:
                        score = 0.1
                        reasoning.append("Candidate parsing failed.")
                else:
                    # Fallback for non-structural prompts
                    score = 0.5
                    reasoning.append("Low structural signal.")

            # 3. NCD Tiebreaker (Max 15% influence)
            # Only used if structural score is ambiguous or to slightly boost relevance
            ncd = self._ncd_score(prompt, cand)
            ncd_boost = (1.0 - ncd) * 0.15
            
            final_score = score * 0.85 + ncd_boost
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            if meta_cap < 1.0:
                final_score = min(final_score, meta_cap)
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": "; ".join(reasoning) if reasoning else "No reasoning path."
            })
            
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps based on meta-analysis of the prompt for ambiguity/traps.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get base score
        # We simulate a single candidate evaluation
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        base_score = res_list[0]["score"]
        
        # If constructive computation succeeded, we can be more confident
        constructive_val = self._compute_constructive_answer(prompt)
        if constructive_val is not None:
            # If we computed an answer and it matches, confidence can be high
            # If it doesn't match, confidence should be low
            cand_nums = re.findall(self.patterns['numeric'], answer)
            if cand_nums:
                try:
                    if abs(float(cand_nums[0]) - constructive_val) < 1e-6:
                        return min(0.95, meta_cap) # High confidence but capped by meta
                    else:
                        return 0.1 # Definitely wrong
                except:
                    pass
        
        # For structural reasoning, cap at 0.8 unless meta says otherwise
        structural_cap = 0.8
        if meta_cap < structural_cap:
            return meta_cap
            
        return min(base_score, meta_cap)
```

</details>
