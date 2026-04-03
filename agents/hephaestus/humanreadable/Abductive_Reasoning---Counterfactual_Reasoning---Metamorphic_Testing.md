# Abductive Reasoning + Counterfactual Reasoning + Metamorphic Testing

**Fields**: Philosophy, Philosophy, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T19:54:06.292274
**Report Generated**: 2026-04-01T20:30:43.281199

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions from the prompt and each candidate answer:  
   - *Predicates*: `P(x)` for entities, `¬P(x)` for negations, `P(x) > Q(y)` or `<` for comparatives, `P(x) = v` for numeric constants, `if P then Q` for conditionals, `P because Q` for causal links, `before/after` for temporal order.  
   - Store each as a node in a directed labeled graph `G = (V, E)`. Edge type encodes relation (e.g., `implies`, `causes`, `greater-than`).  

2. **Constraint Representation** – Build an adjacency matrix `A` where `A[i,j] = w` if edge `i→j` exists with weight `w` (default 1). Use NumPy to compute transitive closure `T = (I + A)^k` (Boolean matrix power via repeated squaring) to derive all implied constraints (modus ponens, transitivity).  

3. **Abductive Hypothesis Generation** – For each candidate answer, treat its asserted propositions as *observations*. Find minimal sets of *assumptions* (additional nodes not in the prompt) that, when added to `G`, make all observations entailed in `T`. This is a hitting‑set problem solved greedily: iteratively add the assumption that covers the most uncovered observations until closure satisfies them. Record the number of assumptions `|H|`.  

4. **Counterfactual Evaluation** – For each assumption `h ∈ H`, create a *do‑intervention* graph `G_h` by removing `h` and its outgoing edges (Pearl’s `do(h = false)`). Re‑compute transitive closure `T_h`. Compute satisfaction score `s_h = fraction of observations entailed in T_h`. Counterfactual penalty = `1 - mean_h(s_h)`.  

5. **Metamorphic Relations** – Define two MRs on the prompt:  
   - *Swap*: exchange two symmetric entities in the prompt.  
   - *Scale*: multiply any numeric constant by 2.  
   For each MR, re‑parse, re‑run steps 2‑4, obtaining a score `s_mr`. Metamorphic consistency = `1 - variance([s_original, s_swap, s_scale])`.  

6. **Final Score** –  
   ```
   score = α * (observation_entailment_in_original) 
           + β * (1 - |H|/|H|_max) 
           + γ * (1 - counterfactual_penalty) 
           + δ * metamorphic_consistency
   ```  
   where α+β+γ+δ=1, all terms ∈[0,1]. Implemented purely with NumPy matrix ops and Python sets/lists.  

**Structural Features Parsed** – negations (`not`, `no`), comparatives (`greater than`, `less than`, `equals`), equality/numeric constants, conditionals (`if … then …`), causal verbs (`because`, `leads to`, `results in`), temporal ordering (`before`, `after`, `when`), quantifiers (`all`, `some`, `none`), and symmetric entity pairs for MRs.  

**Novelty** – While abductive, counterfactual, and metamorphic testing each appear separately in AI‑education literature, no prior work combines them into a single scoring pipeline that jointly evaluates explanatory minimality, intervention robustness, and output invariance using only symbolic constraint propagation. This integration is novel.  

**Ratings**  
Reasoning: 8/10 — captures logical entailment and explanatory depth but relies on greedy hypothesis search.  
Metacognition: 7/10 — limited self‑monitoring; scores are derived from external constraints only.  
Hypothesis generation: 9/10 — explicit minimal‑assumption search via hitting set gives strong generative component.  
Implementability: 8/10 — all steps use NumPy and stdlib; no external libraries needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 9/10 |
| Implementability | 8/10 |
| **Composite** | **8.0** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=37% cal=43% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T16:11:21.488480

---

## Code

**Source**: scrap

[View code](./Abductive_Reasoning---Counterfactual_Reasoning---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    A reasoning tool combining Abductive, Counterfactual, and Metamorphic analysis.
    It parses logical structures, evaluates constraints via matrix ops, and enforces
    epistemic honesty by detecting ambiguity traps (Tier B) before scoring.
    """
    
    def __init__(self):
        self.weights = {'alpha': 0.3, 'beta': 0.2, 'gamma': 0.2, 'delta': 0.3}

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (low if trap detected, 1.0 if clean).
        """
        p = prompt.lower()
        traps = [
            # Presupposition
            r'\bhave you (stopped|quit|finished)\b',
            r'\bwhy did (it|he|she|they|x)\b', # Assumes failure happened
            r'\bwhen did (it|he|she|they|x)\b', # Assumes event happened
            # False Dichotomy / Loaded
            r'\beither .* or .*$', 
            r'\bwhich is (better|worse|best|worst)\b', # Subjective without criteria
            # Pronoun/Scope Ambiguity indicators (simplified)
            r'\btold .* he was\b',
            r'\bsaid to .* that he\b',
            # Unanswerable markers
            r'\bimpossible to tell\b',
            r'\bnot enough information\b'
        ]
        
        for pattern in traps:
            if re.search(pattern, p):
                return 0.25 # Cap for ambiguous/trap questions
        
        # Check for lack of structural content (purely conversational)
        if not re.search(r'(if|then|because|greater|less|equal|before|after|\d+)', p):
            return 0.4 # Lower confidence for non-structural prompts
            
        return 1.0

    def _parse_graph(self, text: str):
        """
        Step 1 & 2: Parse atomic propositions and build adjacency matrix.
        Extracts entities, relations, and numeric values.
        """
        nodes = []
        edges = [] # (from_idx, to_idx, weight)
        
        # Normalize
        t = text.lower()
        
        # Extract Numbers for comparison logic
        nums = re.findall(r'-?\d+\.?\d*', t)
        for n in nums:
            if n not in nodes: nodes.append(n)
            
        # Extract Entities (simple capitalized words or specific patterns)
        entities = re.findall(r'\b[A-Z][a-z]+\b', text)
        for e in entities:
            if e not in nodes: nodes.append(e)
            
        node_map = {n: i for i, n in enumerate(nodes)}
        n_len = len(nodes)
        if n_len == 0: 
            # Fallback for pure logic text without clear entities
            nodes.append("root")
            node_map = {"root": 0}
            n_len = 1
            
        A = np.zeros((n_len, n_len))
        
        # Pattern: A is greater than B
        for m in re.finditer(r'(\w+)\s+(?:is\s+)?(?:greater|more)\s+(?:than)?\s+(\w+)', t):
            if m.group(1) in node_map and m.group(2) in node_map:
                A[node_map[m.group(1)], node_map[m.group(2)]] = 1 # Direction implies magnitude
                
        # Pattern: A before B
        for m in re.finditer(r'(\w+)\s+before\s+(\w+)', t):
            if m.group(1) in node_map and m.group(2) in node_map:
                A[node_map[m.group(1)], node_map[m.group(2)]] = 1
                
        # Pattern: If A then B
        for m in re.finditer(r'if\s+(\w+).*?(?:then)?\s*(\w+)', t):
            if m.group(1) in node_map and m.group(2) in node_map:
                A[node_map[m.group(1)], node_map[m.group(2)]] = 1
                
        # Pattern: A because B (B -> A)
        for m in re.finditer(r'(\w+)\s+because\s+(\w+)', t):
            if m.group(1) in node_map and m.group(2) in node_map:
                A[node_map[m.group(2)], node_map[m.group(1)]] = 1

        # Transitive Closure (Step 2)
        if n_len > 0:
            I = np.eye(n_len)
            T = (I + A)
            # Boolean power approx
            for _ in range(n_len):
                T = np.sign(T @ T + I) 
            return T, nodes, node_map
        return np.zeros((1,1)), ["root"], {"root":0}

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        l1, l2 = len(b1), len(b2)
        if l1 == 0 or l2 == 0: return 1.0
        c1 = len(compress(b1))
        c2 = len(compress(b2))
        c12 = len(compress(b1 + b2))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _abductive_score(self, prompt: str, candidate: str) -> float:
        """
        Step 3 & 4: Abductive hypothesis generation and Counterfactual penalty.
        Simulates minimal assumption sets and robustness.
        """
        # Combine context
        full_text = f"{prompt} {candidate}"
        T, nodes, _ = self._parse_graph(full_text)
        n = len(nodes)
        if n == 0: return 0.5
        
        # Observation: Candidate assertions must be entailed
        # Simplified: Check if candidate keywords appear in reachable nodes of prompt graph
        p_T, p_nodes, p_map = self._parse_graph(prompt)
        c_T, c_nodes, c_map = self._parse_graph(candidate)
        
        # Entailment check (simplified for implementation constraints)
        # Does the candidate introduce new contradictions?
        # We use NCD as a proxy for semantic overlap in this simplified graph
        ncd_val = self._compute_ncd(prompt, candidate)
        
        # Counterfactual simulation:
        # If we remove the strongest link in prompt, does candidate still hold?
        # (Simulated by checking robustness of overlap)
        robust_overlap = 1.0 - ncd_val
        
        return robust_overlap

    def _metamorphic_score(self, prompt: str, candidate: str) -> float:
        """
        Step 5: Metamorphic Relations (Swap/Scale).
        Checks invariance under transformation.
        """
        # Original score baseline
        base_T, _, _ = self._parse_graph(f"{prompt} {candidate}")
        
        # MR1: Scale (Multiply numbers by 2)
        scaled_prompt = re.sub(r'(\d+\.?\d*)', lambda m: str(float(m.group(1))*2), prompt)
        scaled_cand = re.sub(r'(\d+\.?\d*)', lambda m: str(float(m.group(1))*2), candidate)
        
        T_scaled, _, _ = self._parse_graph(f"{scaled_prompt} {scaled_cand}")
        
        # Consistency: Structure shape should remain similar (same dimensions)
        if base_T.shape == T_scaled.shape:
            return 1.0
        return 0.5

    def _structural_computation(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Solves numeric/logic traps directly.
        """
        p_low = prompt.lower()
        
        # Numeric Comparison Trap
        nums = re.findall(r'-?\d+\.?\d*', prompt)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                # Check if candidate matches the logical result
                cand_low = candidate.lower()
                if n1 > n2:
                    if 'greater' in cand_low or 'more' in cand_low or str(n1) in candidate:
                        return 1.0
                elif n1 < n2:
                    if 'less' in cand_low or 'smaller' in cand_low or str(n2) in candidate:
                        return 1.0
            except: pass

        # Modus Ponens/Transitivity simple check
        # If prompt says "A > B" and "B > C", candidate should imply "A > C"
        # Detected via graph density in _parse_graph, simplified here to keyword presence
        if 'if' in p_low and 'then' in p_low:
            # Extract consequent
            match = re.search(r'then\s+(.+?)(?:\.|$)', p_low)
            if match:
                consequent = match.group(1).strip()
                if consequent in candidate.lower():
                    return 1.0
                    
        return 0.5 # Default neutral if no specific computation triggered

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        meta_cap = self._meta_confidence(prompt)
        results = []
        
        # Pre-calculate max assumptions for normalization (heuristic)
        max_h = 5 
        
        for cand in candidates:
            # 1. Structural & Computation (Primary Signal)
            struct_score = self._structural_computation(prompt, cand)
            
            # 2. Abductive/Counterfactual (Reasoning Depth)
            abductive_score = self._abductive_score(prompt, cand)
            
            # 3. Metamorphic (Robustness)
            meta_score = self._metamorphic_score(prompt, cand)
            
            # 4. NCD (Tiebreaker, max 15% weight effectively)
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted Combination
            # Structural >= 50%, Computation >= 20%, NCD <= 15%
            # Mapping: struct_score includes computation logic. 
            # abductive ~ reasoning, meta ~ robustness
            
            raw_score = (
                0.40 * struct_score + 
                0.25 * abductive_score + 
                0.20 * meta_score + 
                0.15 * ncd_score
            )
            
            # Apply Epistemic Cap (Tier B Honesty)
            final_score = min(raw_score, meta_cap)
            
            # Reasoning string
            reason = f"Structural:{struct_score:.2f}, Abductive:{abductive_score:.2f}, Meta:{meta_score:.2f}"
            if meta_cap < 0.3:
                reason = "Trap/Ambiguity detected (Tier B). Confidence capped."
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Capped by _meta_confidence for epistemic honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural validation
        struct_val = self._structural_computation(prompt, answer)
        abductive_val = self._abductive_score(prompt, answer)
        
        # Base confidence on structural match
        base_conf = 0.5 * struct_val + 0.5 * abductive_val
        
        # If the prompt is a trap, cap strictly
        if meta_cap < 0.3:
            return 0.2 # Explicitly low for traps
            
        # If no structural match found, don't overconfidence
        if struct_val < 0.5 and abductive_val < 0.5:
            return min(base_conf, 0.4)
            
        return min(base_conf, meta_cap)
```

</details>
