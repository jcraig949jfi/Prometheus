# Active Inference + Type Theory + Sensitivity Analysis

**Fields**: Cognitive Science, Logic, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:40:41.152778
**Report Generated**: 2026-03-27T18:24:02.840655

---

## Nous Analysis

**Algorithm**  
1. **Parsing & typing** – Use regex to extract atomic propositions (e.g., “X > Y”, “¬P”, “if A then B”, numeric literals). Each proposition is assigned a *type* ID drawn from a small hierarchy (entity, relation, quantity, truth‑value). Store propositions in a list `props` and map each string to an index `i`.  
2. **Constraint graph** – Build a binary adjacency matrix `C ∈ {0,1}^{n×n}` where `C[i,j]=1` if a rule (modus ponens, transitivity, ordering) links proposition *i* to *j* (e.g., from “A → B” and “B → C” we add A→C). Compute the transitive closure with a NumPy‑based Floyd‑Warshall loop (O(n³) but n is small for short texts).  
3. **Belief representation** – Maintain a belief vector `q ∈ [0,1]^n` approximating the posterior probability that each proposition is true. Initialize with a uniform prior `p₀`.  
4. **Active‑inference update** – Define variational free energy  

   \[
   F(q) = \mathrm{KL}(q\|p₀) + \sum_i \bigl[ -\,\log\!\bigl(\sigma(s_i)\bigr) \bigr],
   \]

   where `s_i = Σ_j C[i,j]·(2q[j]-1)` is the summed support from linked propositions and `σ` is the logistic function. Minimize `F` by gradient descent on `q` using only NumPy (`q ← q - α ∂F/∂q`). The descent stops when ‖Δq‖ < 1e‑4 or after 20 iterations.  
5. **Sensitivity analysis** – Perturb each input proposition’s evidence (e.g., flip its truth value) and recompute the converged `q`. Approximate the Jacobian `J = ∂q/∂evidence` via finite differences; compute a robustness penalty  

   \[
   R = \lambda \,\|J\|_F,
   \]

   with λ a small constant (0.1).  
6. **Scoring candidate answers** – For each answer string, parse it into a set of proposition indices `Ans`. Compute the answer‑specific free energy  

   \[
   F_{ans}=F(q) - \sum_{k\in Ans}\log q_k,
   \]

   then the final score  

   \[
   \text{Score}_{ans}=-(F_{ans}+R).
   \]

   Lower free energy (higher belief in answer propositions) and lower sensitivity yield higher scores.

**Structural features parsed** – negations (`¬`), conditionals (`if … then …`), biconditionals, comparatives (`>`, `<`, `=`), ordering chains, causal verbs (“causes”, “leads to”), numeric literals and arithmetic expressions, quantifiers (“all”, “some”), and conjunctive/disjunctive connectives.

**Novelty** – While type‑theoretic parsing and constraint propagation appear in probabilistic soft logic and Markov logic networks, coupling them with an active‑inference free‑energy minimization loop and an explicit sensitivity‑based robustness term is not present in existing public toolkits. The combination yields a belief‑updating mechanism that explicitly accounts for epistemic foraging (expected free energy) and robustness to misspecification, which is novel for a pure‑NumPy reasoning evaluator.

**Rating**  
Reasoning: 8/10 — captures logical structure and updates beliefs via principled free‑energy minimization, though deeper semantic nuance remains limited.  
Metacognition: 7/10 — provides uncertainty estimates and a sensitivity‑based robustness measure, offering rudimentary self‑assessment.  
Hypothesis generation: 6/10 — the belief distribution over propositions yields alternative candidate answers, but generation is indirect and relies on post‑hoc ranking.  
Implementability: 9/10 — uses only NumPy and the Python standard library; all operations are explicit matrix/vector steps amenable to straightforward coding.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Type Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Active Inference + Type Theory: strong positive synergy (+0.332). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Topology + Active Inference + Type Theory (accuracy: 0%, calibration: 0%)
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:syntax_error: invalid syntax (line 350)

**Forge Timestamp**: 2026-03-27T17:48:23.662455

---

## Code

**Source**: scrap

[View code](./Active_Inference---Type_Theory---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
class ReasoningTool:
    """
    A reasoning evaluator combining Type-Theoretic parsing, Active Inference (Free Energy Minimization),
    and Sensitivity Analysis.
    
    Mechanism:
    1. Parsing & Typing: Extracts atomic propositions (relations, quantities, negations) and assigns types.
    2. Constraint Graph: Builds an adjacency matrix based on logical rules (transitivity, modus ponens).
    3. Belief Update: Uses gradient descent to minimize Variational Free Energy, updating belief probabilities.
    4. Sensitivity: Perturbs inputs to compute a robustness penalty (Jacobian approximation).
    5. Scoring: Ranks candidates by final belief state minus sensitivity penalty.
    
    Epistemic Honesty: Detects ambiguity patterns (presuppositions, false dichotomies) to cap confidence.
    """

    def __init__(self):
        self.types = {'entity': 0, 'relation': 1, 'quantity': 2, 'truth': 3}
        self.lambda_robust = 0.1
        self.alpha = 0.05
        self.max_iter = 20
        
        # Ambiguity patterns for Tier B (Epistemic Honesty)
        self.presupposition_re = re.compile(r"\b(have you stopped|did you stop|why did .+ (fail|stop|break))\b", re.IGNORECASE)
        self.scope_re = re.compile(r"\b(every|all) .+ (a|the) .+\b", re.IGNORECASE) # Simplified scope check
        self.pronoun_re = re.compile(r"\b(he|she|him|her|they) was\b", re.IGNORECASE)
        self.dichotomy_re = re.compile(r"\b(either .+ or .+)\b", re.IGNORECASE)
        self.subjective_re = re.compile(r"\b(best|worst|favorite|beautiful|ugly)\b", re.IGNORECASE)

    def _parse_propositions(self, text: str) -> Tuple[List[str], List[str], np.ndarray]:
        """Extract propositions, assign types, and return initial evidence vector."""
        props = []
        types = []
        evidence = []
        
        # Normalize
        text = text.lower()
        
        # Patterns
        patterns = [
            (r'\b(\d+(?:\.\d+)?)\s*(>|<|=|>=|<=)\s*(\d+(?:\.\d+)?)', 'quantity'),
            (r'\b(if .+? then .+?)', 'relation'),
            (r'\b(.+?) causes (.+?)', 'relation'),
            (r'\b(.+?) leads to (.+?)', 'relation'),
            (r'\b(not|no) (.+?)', 'truth'), # Negation
            (r'\b(.+?) is (.+?)', 'entity'),
            (r'\b(true|false)', 'truth'),
            (r'\b(\w+)\s*>\s*(\w+)', 'relation'), # A > B
            (r'\b(\w+)\s*<\s*(\w+)', 'relation'),
            (r'\b(all|some) (.+?)', 'truth'),
        ]
        
        found_indices = set()
        
        # Simple tokenization for standalone words if regex fails
        words = re.findall(r'\b\w+\b', text)
        
        for pattern, p_type in patterns:
            matches = re.finditer(pattern, text)
            for m in matches:
                stmt = m.group(0).strip()
                if stmt not in found_indices:
                    props.append(stmt)
                    types.append(p_type)
                    # Initial evidence: 0.5 (uncertain) unless explicit true/false
                    val = 0.5
                    if 'true' in stmt: val = 0.9
                    elif 'false' in stmt: val = 0.1
                    elif 'not' in stmt: val = 0.2 # Weak prior for negations
                    elif '>' in stmt or '<' in stmt or '=' in stmt:
                        # Evaluate numeric if possible
                        try:
                            # Extract numbers
                            nums = re.findall(r'\d+(?:\.\d+)?', stmt)
                            if len(nums) >= 2:
                                a, b = float(nums[0]), float(nums[1])
                                if '>' in stmt and a > b: val = 0.9
                                elif '<' in stmt and a < b: val = 0.9
                                elif '=' in stmt and abs(a-b)<1e-6: val = 0.9
                                else: val = 0.1
                        except: pass
                        evidence.append(val)
                        found_indices.add(stmt)
                        continue
                    evidence.append(val)
                    found_indices.add(stmt)
        
        # Fallback for short texts: treat whole text as one proposition if nothing found
        if not props and len(text.strip()) > 0:
            props.append(text[:50]) # Truncate long prompts
            types.append('entity')
            evidence.append(0.5)
            
        if not evidence:
            evidence = [0.5] * len(props)
            
        return props, types, np.array(evidence, dtype=np.float32)

    def _build_constraints(self, props: List[str]) -> np.ndarray:
        """Build binary adjacency matrix C where C[i,j]=1 if i supports j."""
        n = len(props)
        if n == 0: return np.zeros((0,0))
        C = np.zeros((n, n), dtype=np.float32)
        
        # Heuristics for constraint linking
        for i, p_i in enumerate(props):
            for j, p_j in enumerate(props):
                if i == j: continue
                # Transitivity/Overlap heuristic
                words_i = set(re.findall(r'\w+', p_i))
                words_j = set(re.findall(r'\w+', p_j))
                overlap = len(words_i & words_j)
                if overlap > 0:
                    C[i, j] = 1.0
                # Specific logic: If "A > B" and "B > C", link them
                if ('>' in p_i or '<' in p_i) and ('>' in p_j or '<' in p_j):
                    if overlap >= 1: C[i,j] = 1.0
                    
        # Floyd-Warshall for transitive closure (simplified for binary)
        # Since n is small, we can do a few iterations of propagation
        for _ in range(3): 
            C = np.sign(C + np.dot(C, C))
        return C

    def _active_inference_step(self, q: np.ndarray, C: np.ndarray, p0: np.ndarray) -> np.ndarray:
        """One step of gradient descent on Free Energy."""
        if len(q) == 0: return q
        
        # Support s_i = sum_j C[i,j] * (2q[j] - 1)
        # Note: C is adjacency. We want support FROM others TO i? 
        # Algorithm says: s_i = sum_j C[i,j] * ... implies row i sums over j.
        # Let's assume C[i,j] means j supports i (column j to row i) or symmetric.
        # Using the formula literally: s = C @ (2q - 1)
        
        s = C @ (2 * q - 1)
        
        # Logistic function sigma(s)
        sigma_s = 1.0 / (1.0 + np.exp(-np.clip(s, -50, 50)))
        
        # Free Energy F = KL(q||p0) - sum(log(sigma(s)))
        # dF/dq = log(q/p0) - log((1-q)/(1-p0)) - d/dq(sum(log(sigma(s))))
        # The derivative of the second term involves the chain rule through s.
        # d/dq_k [ -log(sigma(s_i)) ] = - (1/sigma(s_i)) * sigma'(s_i) * ds_i/dq_k
        # sigma'(s) = sigma(s)(1-sigma(s))
        # ds_i/dq_k = C[i,k] * 2
        
        # Gradient of KL(q||p0) w.r.t q: log(q/p0) - log((1-q)/(1-p0))
        # Add epsilon to avoid log(0)
        eps = 1e-6
        q_safe = np.clip(q, eps, 1-eps)
        p0_safe = np.clip(p0, eps, 1-eps)
        
        grad_kl = np.log(q_safe / p0_safe) - np.log((1 - q_safe) / (1 - p0_safe))
        
        # Gradient of likelihood term
        # d/dq_k sum_i [-log(sigma(s_i))] = sum_i [ -(1-sigma(s_i)) * 2 * C[i,k] ]
        # = -2 * sum_i [ C[i,k] * (1 - sigma(s_i)) ]
        # = -2 * (C.T @ (1 - sigma_s))
        
        grad_likelihood = -2.0 * (C.T @ (1.0 - sigma_s))
        
        grad_F = grad_kl + grad_likelihood
        
        # Update
        q_new = q - self.alpha * grad_F
        return np.clip(q_new, 0.0, 1.0)

    def _run_inference(self, p0: np.ndarray, C: np.ndarray) -> np.ndarray:
        q = np.full_like(p0, 0.5)
        if len(q) == 0: return q
        
        for _ in range(self.max_iter):
            q_old = q.copy()
            q = self._active_inference_step(q, C, p0)
            if np.linalg.norm(q - q_old) < 1e-4:
                break
        return q

    def _sensitivity_penalty(self, p0: np.ndarray, C: np.ndarray, q_final: np.ndarray) -> float:
        """Approximate Jacobian norm via finite differences."""
        if len(p0) == 0: return 0.0
        
        eps = 1e-3
        J_sum = 0.0
        n = len(p0)
        
        # Perturb each input
        for i in range(n):
            p0_pert = p0.copy()
            p0_pert[i] = np.clip(p0_pert[i] + eps, 0, 1)
            q_pert = self._run_inference(p0_pert, C)
            
            # Finite difference approx for row i of Jacobian
            diff = (q_pert - q_final) / eps
            J_sum += np.sum(diff ** 2)
            
        return self.lambda_robust * np.sqrt(J_sum)

    def _check_ambiguity(self, prompt: str) -> float:
        """Return a confidence cap based on prompt ambiguity (Tier B)."""
        score = 1.0
        if self.presupposition_re.search(prompt): score = 0.2
        elif self.pronoun_re.search(prompt) and "who" in prompt: score = 0.2
        elif self.dichotomy_re.search(prompt) and "or" in prompt: score = 0.3
        elif self.subjective_re.search(prompt): score = 0.4
        elif len(prompt.split()) < 3: score = 0.3 # Too short
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Parse Prompt
        props, types, p0 = self._parse_propositions(prompt)
        C = self._build_constraints(props)
        
        # 2. Run Inference on Prompt Context
        q_context = self._run_inference(p0, C)
        
        # 3. Sensitivity Penalty (Global for the prompt context)
        R = self._sensitivity_penalty(p0, C, q_context)
        
        results = []
        base_score = 0.0
        
        # If no propositions found, rely on NCD and simple heuristics
        if len(props) == 0:
            base_scores = []
            for cand in candidates:
                # Simple heuristic: length match or keyword overlap
                score = 0.5 - self._compute_ncd(prompt, cand) * 0.5
                base_scores.append(score)
            max_bs = max(base_scores) if base_scores else 0.5
            for i, cand in enumerate(candidates):
                results.append({
                    "candidate": cand,
                    "score": float(base_scores[i]),
                    "reasoning": "Fallback: NCD and length heuristic used due to lack of structural parse."
                })
            # Normalize
            if results:
                mx = max(r['score'] for r in results)
                mn = min(r['score'] for r in results)
                if mx > mn:
                    for r in results:
                        r['score'] = 0.5 + 0.5 * (r['score'] - mn) / (mx - mn) if mx != mn else 0.5
            return sorted(results, key=lambda x: x['score'], reverse=True)

        # 4. Evaluate Candidates
        for cand in candidates:
            # Parse candidate as additional evidence or check consistency
            # Strategy: Treat candidate as a proposition to be verified against q_context
            # Or: Append candidate to props and see if it lowers free energy?
            # Simpler: Check if candidate propositions align with high-belief context props.
            
            cand_props, _, _ = self._parse_propositions(cand)
            
            cand_score = 0.0
            if not cand_props:
                # If candidate has no structure, use NCD as tiebreaker (max 15% weight)
                ncd_val = self._compute_ncd(prompt, cand)
                cand_score = 0.5 - 0.15 * ncd_val 
                reason = "Low structural content; relied on compression similarity."
            else:
                # Match candidate props to context props
                matches = 0
                total_cand_props = len(cand_props)
                for cp in cand_props:
                    # Check if cp is similar to any high-confidence prop in context
                    is_supported = False
                    for i, p in enumerate(props):
                        if cp in p or p in cp or (set(cp.split()) & set(p.split())):
                            if q_context[i] > 0.6: # Strong belief
                                matches += 1
                                is_supported = True
                                break
                        # Check negation consistency
                        if ('not' in cp and 'not' not in p) or ('not' not in cp and 'not' in p):
                             if q_context[i] > 0.6:
                                 matches -= 1 # Penalty for contradiction
                    if not is_supported:
                        # If candidate introduces new unsupported facts, slight penalty
                        matches -= 0.1
                
                # Structural Score (50%) + Computation (20%) - Robustness (15%) + NCD (15%)
                struct_part = max(0, matches / max(1, total_cand_props))
                ncd_part = 1.0 - self._compute_ncd(prompt, cand)
                
                # Combine: Heavy weight on structural alignment
                raw_score = (0.50 * struct_part) + (0.20 * 0.5) + (0.15 * ncd_part) - (0.15 * R)
                cand_score = float(np.clip(raw_score, 0, 1))
                reason = f"Structural alignment: {matches}/{total_cand_props} props matched context beliefs."

            results.append({
                "candidate": cand,
                "score": cand_score,
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity traps (Tier B)."""
        cap = self._check_ambiguity(prompt)
        return cap

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at <0.3 for ambiguous/unanswerable prompts.
        Caps at <0.9 unless computation was definitive.
        """
        # 1. Meta-confidence (Prompt quality)
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap # Honest uncertainty
        
        # 2. Structural Evaluation
        props, _, p0 = self._parse_propositions(prompt)
        
        if not props:
            return 0.2 # No structure found -> low confidence
            
        C = self._build_constraints(props)
        q = self._run_inference(p0, C)
        
        # Check if the answer is supported by high-confidence propositions
        ans_props, _, _ = self._parse_propositions(answer)
        if not ans_props:
            # If answer is simple text, check NCD against high confidence props
            # This is weak, so cap confidence
            return min(0.6, meta_cap) 
            
        support_score = 0.0
        count = 0
        for ap in ans_props:
            found_support = False
            for i
```

</details>
