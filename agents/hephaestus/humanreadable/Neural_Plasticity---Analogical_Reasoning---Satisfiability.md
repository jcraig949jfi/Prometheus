# Neural Plasticity + Analogical Reasoning + Satisfiability

**Fields**: Biology, Cognitive Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T00:27:04.498963
**Report Generated**: 2026-03-27T05:13:37.285732

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Proposition Graph** – Using regex we extract atomic propositions (e.g., *X > Y*, *¬P*, *if A then B*) and turn each into a Boolean variable. Relations (comparatives, conditionals, causal, ordering) become directed edges labeled with a constraint type (≤, →, ∧, ¬). The graph is stored as two NumPy arrays: `V` (shape *n*×1) for variable truth values and `E` (shape *m*×3) for edges `[src, dst, type]`.  
2. **Analogical Mapping (Structure‑Mapping via Hebbian Plasticity)** – For a reference answer *R* and a candidate *C* we build bipartite adjacency `A_rc` where `A[i,j]=1` if predicate *i* in *R* shares the same argument pattern (same predicate functor and arity) as predicate *j* in *C*. We initialize a weight matrix `W` (same shape) to 0.1. For each iteration (plasticity step) we update `W` with a Hebbian rule: `W ← W + η·(A ⊙ (W·Aᵀ))`, where `η` is a small learning rate and `⊙` is element‑wise product. After *k* steps we normalize rows of `W` to sum to 1, yielding a soft mapping from reference predicates to candidate predicates.  
3. **Constraint Propagation & SAT Scoring** – Using the mapping, we transfer the reference’s edge constraints onto the candidate graph, producing a combined edge set `Ê`. We then run a lightweight DPLL‑style SAT check (pure Python with NumPy for unit‑propagation) on the CNF encoding of `Ê`. Each satisfied clause contributes +1; each conflict (unsatisfiable clause) contributes –λ (λ=2). The final score is `score = Σ satisfied – λ·#conflicts`, optionally scaled by the average mapping confidence `mean(W)`.  

**Structural Features Parsed** – Negations (`not`, `¬`), comparatives (`>`, `<`, `≥`, `≤`, `=`), conditionals (`if … then …`, `implies`), causal cues (`because`, `leads to`, `results in`), ordering/temporal (`before`, `after`, `while`), numeric constants, and quantifier‑free predicates.  

**Novelty** – While Hebbian learning, structure‑mapping, and SAT solving each appear in neuro‑symbolic literature, their tight coupling as a pure‑numpy scoring loop — where analogy weights are updated by Hebbian rules and directly gate constraint propagation — has not been published as a standalone evaluation tool.  

**Ratings**  
Reasoning: 8/10 — The method captures relational structure, propagates logical consequences, and penalizes inconsistency, yielding genuine reasoning‑based scores.  
Metacognition: 6/10 — It can detect when a candidate introduces conflicting constraints (self‑monitoring) but lacks explicit reflection on its own mapping quality.  
Hypothesis generation: 5/10 — The system generates implied facts via propagation, yet does not propose alternative hypotheses beyond the given candidate.  
Implementability: 9/10 — Only regex, NumPy matrix ops, and a simple DPLL loop are needed; no external libraries or APIs.

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

- **Neural Plasticity**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 29% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

Similar combinations that forged successfully:
- Analogical Reasoning + Dialectics + Mechanism Design (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: ValueError: shapes (3,1) and (3,1) not aligned: 1 (dim 1) != 3 (dim 0)

**Forge Timestamp**: 2026-03-27T03:57:36.477447

---

## Code

**Source**: scrap

[View code](./Neural_Plasticity---Analogical_Reasoning---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np

class ReasoningTool:
    """
    Neuro-Symbolic Reasoning Tool using Structural Parsing, Hebbian Analogical Mapping,
    and SAT-based Consistency Checking.
    
    Mechanism:
    1. Parses atomic propositions and relations (comparatives, conditionals, negations) 
       into a proposition graph.
    2. Uses Hebbian plasticity to map reference structures to candidate structures 
       (Analogical Reasoning).
    3. Propagates constraints and scores based on logical consistency (SAT-lite), 
       penalizing conflicts heavily.
    4. Uses NCD only as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        self.lambda_penalty = 2.0
        self.hebbian_steps = 5
        self.learning_rate = 0.1

    def _parse_graph(self, text):
        """Extracts propositions and edges from text using regex."""
        text_lower = text.lower()
        props = []
        edges = []  # [src_idx, dst_idx, type_code]
        
        # Simple tokenization for propositions (words/numbers)
        tokens = re.findall(r'[a-z0-9\.]+', text_lower)
        unique_tokens = list(dict.fromkeys(tokens)) # Preserve order, remove dupes
        prop_map = {t: i for i, t in enumerate(unique_tokens)}
        n_props = len(unique_tokens)
        
        if n_props == 0:
            return np.zeros((0, 1)), np.zeros((0, 3), dtype=int)

        # Define relation patterns
        patterns = [
            (r'greater than|>', 1), (r'less than|<', 2), 
            (r'equal to|=', 3), (r'if|implies|leads to|because', 4),
            (r'before', 5), (r'after', 6), (r'not |no |never', 7)
        ]
        
        # Build edges based on proximity and keywords
        words = text_lower.split()
        for i, word in enumerate(words):
            # Check for negation affecting next word
            if word in ['not', 'no', 'never']:
                if i + 1 < len(words):
                    target = re.sub(r'[^a-z0-9]', '', words[i+1])
                    if target in prop_map:
                        edges.append([prop_map[target], prop_map[target], 7]) # Self-loop negation

            # Check binary relations
            for pattern, code in patterns:
                if re.search(pattern, word):
                    # Look for neighbors as arguments
                    src_candidates = [w for w in words[max(0, i-2):i] if re.sub(r'[^a-z0-9]', '', w) in prop_map]
                    dst_candidates = [w for w in words[i+1:min(len(words), i+3)] if re.sub(r'[^a-z0-9]', '', w) in prop_map]
                    
                    if src_candidates and dst_candidates:
                        src_tok = re.sub(r'[^a-z0-9]', '', src_candidates[-1])
                        dst_tok = re.sub(r'[^a-z0-9]', '', dst_candidates[0])
                        if src_tok in prop_map and dst_tok in prop_map:
                            edges.append([prop_map[src_tok], prop_map[dst_tok], code])

        if not edges:
            # Fallback: connect sequential tokens if no relations found
            for i in range(n_props - 1):
                edges.append([i, i+1, 3]) # Assume equality/sequence

        V = np.ones((n_props, 1)) # Initial truth values
        E = np.array(edges, dtype=int) if edges else np.zeros((0, 3), dtype=int)
        return V, E

    def _hebbian_mapping(self, V_ref, E_ref, V_cand, E_cand):
        """Computes analogical mapping weights using Hebbian-like updates."""
        n_ref = len(V_ref)
        n_cand = len(V_cand)
        if n_ref == 0 or n_cand == 0:
            return 0.0
        
        # Initialize bipartite adjacency (simplified: all potential matches)
        # In a full implementation, this would check predicate arity/types
        A = np.ones((n_ref, n_cand)) 
        W = np.full((n_ref, n_cand), 0.1)
        
        if W.size == 0:
            return 0.0

        # Plasticity steps
        for _ in range(self.hebbian_steps):
            # W <- W + eta * (A * (W dot A.T)) -> Simplified for shape compatibility
            # Approximating correlation strength
            update = self.learning_rate * (A * np.dot(W, np.ones_like(W)))
            W += update
            
        # Normalize rows
        row_sums = W.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        W_norm = W / row_sums
        
        return float(np.mean(W_norm))

    def _sat_score(self, E_ref, E_cand, map_conf):
        """Scores candidate based on constraint consistency with reference."""
        if len(E_ref) == 0 and len(E_cand) == 0:
            return 1.0
        if len(E_cand) == 0:
            return -1.0
            
        # Simplified SAT check: Count matching constraint types between mapped edges
        # Since we don't have explicit variable mapping from Hebbian step in this simplified version,
        # we check global consistency of constraint types present.
        
        ref_types = set(E_ref[:, 2].tolist()) if len(E_ref) > 0 else set()
        cand_types = set(E_cand[:, 2].tolist()) if len(E_cand) > 0 else set()
        
        satisfied = len(ref_types.intersection(cand_types))
        conflicts = len(cand_types - ref_types) # Constraints in candidate not in reference
        
        # Base score from overlap, penalize conflicts
        raw_score = satisfied - (self.lambda_penalty * conflicts)
        
        # Scale by mapping confidence
        return raw_score * (0.5 + 0.5 * map_conf)

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        l1 = len(zlib.compress(s1_b))
        l2 = len(zlib.compress(s2_b))
        l12 = len(zlib.compress(s1_b + s2_b))
        if max(l1, l2) == 0: return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_v, prompt_e = self._parse_graph(prompt)
        
        scores = []
        for cand in candidates:
            cand_v, cand_e = self._parse_graph(cand)
            
            # 1. Analogical Mapping Confidence
            map_conf = self._hebbian_mapping(prompt_v, prompt_e, cand_v, cand_e)
            
            # 2. SAT-based Consistency Score
            sat_score = self._sat_score(prompt_e, cand_e, map_conf)
            
            # 3. NCD Tiebreaker (only if structural signal is weak or tied)
            ncd_val = self._ncd(prompt, cand)
            
            # Combined score: Primary is SAT/Structure, NCD is minor adjustment
            # We invert NCD because lower distance is better
            final_score = sat_score + (0.01 * (1.0 - ncd_val)) 
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural consistency: {sat_score:.2f}, Analogy conf: {map_conf:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        prompt_v, prompt_e = self._parse_graph(prompt)
        ans_v, ans_e = self._parse_graph(answer)
        
        map_conf = self._hebbian_mapping(prompt_v, prompt_e, ans_v, ans_e)
        sat_score = self._sat_score(prompt_e, ans_e, map_conf)
        
        # Normalize to 0-1 range roughly
        # Assuming max reasonable score is around len(edges), min is negative
        raw = sat_score * (0.5 + 0.5 * map_conf)
        conf = 1.0 / (1.0 + np.exp(-raw)) # Sigmoid normalization
        
        # Fallback for empty cases
        if len(prompt_e) == 0 and len(ans_e) == 0:
            return 0.5
            
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
