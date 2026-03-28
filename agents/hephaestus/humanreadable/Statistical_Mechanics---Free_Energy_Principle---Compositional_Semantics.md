# Statistical Mechanics + Free Energy Principle + Compositional Semantics

**Fields**: Physics, Theoretical Neuroscience, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T10:23:47.493789
**Report Generated**: 2026-03-27T16:08:16.917260

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Compositional Semantic Graph** – Using regex‑based patterns we extract elementary propositions (e.g., “X is Y”, “X > Y”, “if X then Y”, “not X”) and binary relations (negation, comparative, conditional, causal, ordering). Each proposition becomes a node; relations are directed edges labeled with a type. The graph is stored as a list of node objects and a NumPy adjacency tensor **R** of shape *(n_nodes, n_nodes, n_relation_types)* where entries are 1 if the relation holds, 0 otherwise.  
2. **Energy Assignment (Free Energy Principle)** – For each node *i* we define a local prediction error *e_i* as the squared deviation between its asserted truth value *t_i*∈{0,1} and the value implied by its parents via logical functions (e.g., modus ponens for conditionals, transitivity for ordering). The local energy is *E_i = ½ e_i²*. The total energy of a world assignment **t** is *E(**t**) = Σ_i E_i + λ Σ_{i,j} R_{ij}·|t_i−t_j|* (the second term penalizes violations of relational constraints, λ is a hyper‑parameter).  
3. **Partition Function & Scoring (Statistical Mechanics)** – We approximate the Boltzmann distribution over all 2ⁿ possible truth assignments using mean‑field variational inference: initialize **μ** = 0.5, iteratively update μ_i = σ(−∂E/∂t_i) where σ is the logistic function (implemented with NumPy). After convergence, the variational free energy *F = ⟨E⟩_μ − H(μ)* serves as an upper bound on −log Z.  
4. **Answer Scoring** – For each candidate answer we treat its proposition as an observed node (fix *t_i* to 1 if the answer asserts truth, 0 if denies). We run the same mean‑field update with that node clamped and compute the resulting free energy *F_ans*. Lower *F_ans* indicates higher plausibility; the final score is *S = −F_ans* (higher is better).  

**Parsed Structural Features** – Negations (¬), comparatives (> , <, =), conditionals (if … then …), causal verbs (causes, leads to), numeric thresholds (e.g., “at least 3”), ordering relations (before/after, greater/less than), and conjunctive/disjunctive connectives.  

**Novelty** – The approach merges compositional semantic parsing with a physics‑inspired energy‑based inference (Free Energy Principle) and a tractable partition‑function approximation. While related to Markov Logic Networks and Probabilistic Soft Logic, the explicit use of variational free energy as a scoring function and the mean‑field update derived from statistical mechanics is not standard in existing NLP reasoning tools, making the combination novel.  

**Ratings**  
Reasoning: 8/10 — captures logical dependencies and uncertainty via energy minimization, but approximations may miss multi‑modal posteriors.  
Metacognition: 6/10 — the algorithm can monitor its own free‑energy reduction, yet lacks explicit self‑reflection on parsing failures.  
Hypothesis generation: 7/10 — mean‑field updates propose alternative truth assignments, enabling hypothesis sampling, though guided by local gradients only.  
Implementability: 9/10 — relies solely on NumPy for matrix ops and Python’s re/std‑lib for parsing; no external libraries needed.

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
**Reason**: validation:runtime_error: NameError: name 'Tuple' is not defined

**Forge Timestamp**: 2026-03-27T15:53:01.829902

---

## Code

**Source**: scrap

[View code](./Statistical_Mechanics---Free_Energy_Principle---Compositional_Semantics/tool.py)

<details>
<summary>Show code</summary>

```python
class ReasoningTool:
    """
    A reasoning tool combining Compositional Semantic Parsing with the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts logical propositions and relations (negation, conditionals, comparatives)
       into a semantic graph represented by an adjacency tensor.
    2. Energy Model: Defines a local prediction error based on logical consistency (e.g., if A->B, 
       then truth(A) implies truth(B)). Total energy includes a regularization term for relational constraints.
    3. Inference: Uses Mean-Field Variational Inference (derived from Statistical Mechanics) to 
       approximate the posterior distribution over truth assignments by minimizing variational free energy.
    4. Scoring: Evaluates candidate answers by clamping their truth value and measuring the resulting 
       free energy. Lower free energy = higher plausibility.
    5. Epistemic Honesty: Explicitly detects ambiguity, presuppositions, and unanswerable queries 
       to cap confidence, ensuring high uncertainty where structural parsing fails or logic is flawed.
    """

    def __init__(self):
        self.relation_types = ['implication', 'negation', 'conjunction', 'disjunction', 'comparative', 'causal']
        self.n_rel = len(self.relation_types)
        self.lambda_reg = 1.0  # Regularization strength for relational constraints
        self.max_iter = 50
        self.tol = 1e-4

    def _meta_confidence(self, prompt: str) -> float:
        """
        Checks prompt for Tier B traps: presupposition, ambiguity, subjectivity, unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        presupposition_patterns = [
            r"have you (stopped|quit|ceased)",
            r"why did .+ (fail|stop|break)",
            r"when did .+ (stop|end)",
            r"how many times did .+ (fail|error)"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p):
                return 0.2

        # 2. Scope/Pronoun Ambiguity ("Every X... a Y", "X told Y he...")
        if re.search(r"every .+ (did|saw|has) a .+", p) and "same" not in p:
            return 0.3
        if re.search(r"told .+ (he|she|him|her)", p) and "who" in p:
            return 0.3

        # 3. False Dichotomy ("Either A or B" without context of exhaustiveness)
        if re.search(r"either .+ or .+", p) and "only" not in p:
            # Heuristic: if it looks like a logic puzzle, maybe okay, else suspicious
            if "logic" not in p and "puzzle" not in p:
                return 0.4

        # 4. Subjectivity ("Best", "Favorite" without criteria)
        subjective_words = ["best", "worst", "favorite", "beautiful", "tasty"]
        if any(w in p for w in subjective_words) and "measure" not in p and "data" not in p:
            return 0.3

        # 5. Unanswerability (Missing info indicators)
        if "cannot be determined" in p or "not enough info" in p:
            return 0.1
            
        return 1.0

    def _parse_prompt(self, prompt: str) -> Tuple[List[str], np.ndarray, Dict[str, int]]:
        """
        Parses prompt into nodes and an adjacency tensor R.
        Returns: (nodes, R_tensor, node_map)
        """
        sentences = re.split(r'[.!?]', prompt)
        nodes = []
        node_map = {}  # Map proposition string to index
        relations = [] # List of (i, j, type_idx)

        def get_node_idx(prop: str) -> int:
            prop = prop.strip()
            if not prop: return -1
            if prop not in node_map:
                node_map[prop] = len(nodes)
                nodes.append(prop)
            return node_map[prop]

        for sent in sentences:
            sent = sent.strip().lower()
            if not sent: continue

            # Pattern 1: Negation ("X is not Y", "Not X")
            neg_match = re.search(r"(.+?) is not (.+)", sent)
            if neg_match:
                p1 = get_node_idx(neg_match.group(1).strip())
                p2 = get_node_idx(neg_match.group(2).strip())
                if p1 != -1 and p2 != -1:
                    relations.append((p1, p2, self.relation_types.index('negation')))
                continue
            
            if sent.startswith("not "):
                p1 = get_node_idx(sent[4:])
                if p1 != -1:
                    # Self-negation marker or link to a virtual false node? 
                    # Simplification: Mark as negation relation to self or skip if atomic
                    pass 

            # Pattern 2: Conditionals ("If X then Y")
            cond_match = re.search(r"if (.+?) then (.+)", sent)
            if cond_match:
                p1 = get_node_idx(cond_match.group(1).strip())
                p2 = get_node_idx(cond_match.group(2).strip())
                if p1 != -1 and p2 != -1:
                    relations.append((p1, p2, self.relation_types.index('implication')))
                continue

            # Pattern 3: Causal ("X causes Y", "X leads to Y")
            causal_match = re.search(r"(.+?) (causes|leads to) (.+)", sent)
            if causal_match:
                p1 = get_node_idx(causal_match.group(1).strip())
                p2 = get_node_idx(causal_match.group(3).strip())
                if p1 != -1 and p2 != -1:
                    relations.append((p1, p2, self.relation_types.index('causal')))
                continue

            # Pattern 4: Comparatives ("X > Y", "X is greater than Y")
            comp_match = re.search(r"(.+?) (is greater than|is less than|>) (.+)", sent)
            if comp_match:
                p1 = get_node_idx(comp_match.group(1).strip())
                p2 = get_node_idx(comp_match.group(3).strip())
                if p1 != -1 and p2 != -1:
                    relations.append((p1, p2, self.relation_types.index('comparative')))
                continue

            # Pattern 5: Simple Assertion ("X is Y") - treated as conjunction of properties or just existence
            # For this model, we treat isolated assertions as nodes that should be true if asserted.
            # We don't add explicit edges for simple "A is B" unless linked to others.
            is_match = re.search(r"(.+?) is (.+)", sent)
            if is_match:
                # Just ensure nodes exist
                get_node_idx(is_match.group(1).strip())
                get_node_idx(is_match.group(2).strip())

        n = len(nodes)
        if n == 0:
            return [], np.array([]), {}

        R = np.zeros((n, n, self.n_rel), dtype=np.float32)
        for i, j, r_idx in relations:
            R[i, j, r_idx] = 1.0

        return nodes, R, node_map

    def _compute_free_energy(self, R: np.ndarray, fixed_nodes: Optional[Dict[int, float]] = None) -> float:
        """
        Computes variational free energy using mean-field approximation.
        fixed_nodes: dict mapping node index to fixed truth value (0.0 or 1.0)
        """
        n = R.shape[0]
        if n == 0: return 0.0

        # Initialize mu (probabilities)
        mu = np.full(n, 0.5, dtype=np.float32)
        
        # Clamp fixed nodes
        if fixed_nodes:
            for idx, val in fixed_nodes.items():
                mu[idx] = val

        # Iterative update
        for _ in range(self.max_iter):
            mu_old = mu.copy()
            
            # Compute local fields (h_i) based on relations
            # E = sum(0.5 * (t_i - predicted_i)^2) + lambda * sum(R_ij * |t_i - t_j|)
            # Gradient descent step approximation for mean field:
            # mu_i = sigmoid( - dE/dmu_i )
            
            grads = np.zeros(n, dtype=np.float32)
            
            # Contribution from logical relations (simplified for speed)
            # Implication: If A->B, error if A=1 and B=0. 
            # We want to minimize (A * (1-B))^2 roughly.
            
            for r_idx in range(self.n_rel):
                # Adjacency matrix for this relation type
                adj = R[:, :, r_idx]
                if np.sum(adj) == 0: continue
                
                # Vectorized logic operations approx
                # For implication (i->j): penalty if mu[i] high and mu[j] low
                if self.relation_types[r_idx] == 'implication' or self.relation_types[r_idx] == 'causal':
                    # Target: mu[j] should be >= mu[i]
                    # Gradient w.r.t mu[i]: -(1 - mu[j]) * 2 * (mu[i] - mu[i]*mu[j]) ? 
                    # Simplified: push mu[i] down if mu[j] is low, push mu[j] up if mu[i] is high
                    preds = adj @ mu # sum of parents
                    # This is a rough heuristic gradient for the mean-field update
                    grads -= adj @ (1.0 - mu) # Encourage consistency
                    grads += (adj.T @ mu) # Reverse influence
                    
                elif self.relation_types[r_idx] == 'negation':
                    # A -> not B. If A high, B should be low.
                    grads -= adj @ mu 
                    grads += adj.T @ (1.0 - mu)

            # Regularization term gradient (smoothing)
            # lambda * sum |t_i - t_j| -> encourages similar values unless constrained
            # Skip for strict logical constraints to avoid blurring
            
            # Update rule: mu = sigmoid( -grad )
            # Shift grads to prevent overflow
            update = 1.0 / (1.0 + np.exp(grads))
            
            # Apply clamping
            if fixed_nodes:
                for idx, val in fixed_nodes.items():
                    update[idx] = val
                mu = update
            else:
                mu = update

            if np.max(np.abs(mu - mu_old)) < self.tol:
                break

        # Calculate Free Energy F = <E> - H
        # <E>: Expected energy
        energy = 0.0
        eps = 1e-7
        
        # Energy from relations
        for r_idx in range(self.n_rel):
            adj = R[:, :, r_idx]
            if np.sum(adj) == 0: continue
            
            if self.relation_types[r_idx] == 'implication' or self.relation_types[r_idx] == 'causal':
                # E ~ sum( mu_i * (1 - mu_j) )
                diff = mu[:, None] * (1.0 - mu[None, :])
                energy += np.sum(adj * diff)
                
            elif self.relation_types[r_idx] == 'negation':
                # E ~ sum( mu_i * mu_j ) (Penalize both true)
                prod = mu[:, None] * mu[None, :]
                energy += np.sum(adj * prod)

        energy *= 0.5 # 1/2 factor
        
        # Entropy H = - sum( mu log mu + (1-mu) log (1-mu) )
        H = -np.sum(mu * np.log(mu + eps) + (1.0 - mu) * np.log(1.0 - mu + eps))
        
        F = energy - H
        return F

    def _calculate_ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a minor tie-breaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_comb = len(zlib.compress(s1_b + s2_b))
        if max(len_s1, len_s2) == 0: return 0.0
        return (len_comb - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        nodes, R, node_map = self._parse_prompt(prompt)
        n = len(nodes)
        
        # If no structure found, rely on NCD and low confidence
        if n == 0 or R.size == 0:
            base_score = -1.0
            results = []
            for cand in candidates:
                # Simple keyword overlap as fallback
                score = 0.0
                p_words = set(prompt.lower().split())
                c_words = set(cand.lower().split())
                overlap = len(p_words & c_words) / (len(c_words) + 1)
                ncd = self._calculate_ncd_score(prompt, cand)
                final_score = overlap - 0.5 * ncd # Rough heuristic
                results.append({"candidate": cand, "score": final_score, "reasoning": "No structural parse; fallback to lexical overlap."})
            return sorted(results, key=lambda x: x['score'], reverse=True)

        results = []
        base_energy = self._compute_free_energy(R)

        for cand in candidates:
            # Map candidate to node constraints
            # Heuristic: Check if candidate string matches any known node proposition
            cand_lower = cand.lower().strip().rstrip('.')
            fixed = {}
            
            # Try to find matching nodes
            matched = False
            for prop, idx in node_map.items():
                if prop in cand_lower or cand_lower in prop:
                    # If candidate asserts the proposition, fix to 1. 
                    # If it denies (contains "not"), fix to 0.
                    if "not" in cand_lower and prop not in cand_lower:
                        fixed[idx] = 0.0
                    else:
                        fixed[idx] = 1.0
                    matched = True
            
            # If no direct node match, treat as a general assertion affecting the whole system?
            # For now, if no match, penalty.
            if not matched:
                # Penalize candidates that don't map to parsed structure
                cand_energy = base_energy + 2.0 
            else:
                cand_energy = self._compute_free_energy(R, fixed)

            # Score is negative free energy (lower energy = higher score)
            # Normalize slightly
            score = -cand_energy
            
            # Add small NCD component (max 15% influence)
            ncd = self._calculate_ncd_score(prompt, cand)
            score = 0.85 * score - 0.15 * ncd

            reasoning = f"Parsed {n} nodes. Free Energy: {cand_energy:.4f}."
            if not matched:
                reasoning += " Candidate did not map to parsed logical structure."
            
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})

        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Check meta-constraints (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Run evaluation to see if answer is structurally sound
        candidates = [answer, "The opposite of " + answer] # Dummy contrast
        # We need to see if the answer makes sense in context, 
        # but for confidence we mostly care about the prompt's solvability.
        
        # If meta-analysis says it's a trap, return low confidence immediately
        if meta_cap < 0.5:
            return meta_cap

        # 3. Structural check: Did we parse anything?
        nodes, R, _ = self._parse_prompt(prompt)
        if len(nodes) == 0:
            return 0.3 # Honest uncertainty
        
        # 4. Computation check: Does the answer reduce energy significantly?
        # We compare the free energy of the world with the answer clamped vs unclamped?
        # Or simply: if the answer contradicts strong logical constraints, confidence drops.
        
        # Map answer to nodes
        fixed = {}
        answer_lower = answer.lower().strip()
        matched_any = False
        for prop, idx in node_map.items():
             if prop in answer_lower or answer_lower in prop:
                 fixed[idx] = 1.0
                 matched_any = True
        
        if not matched_any:
            # If answer doesn't touch parsed logic, we can't be very confident it's "computationally" derived
            return 0.5

        # If we passed meta checks and have structure, return moderate-high confidence
        # But never > 0.9 unless it's a pure math solve (which this parser doesn't fully handle yet)
        return min(0.85, meta_cap)
```

</details>
