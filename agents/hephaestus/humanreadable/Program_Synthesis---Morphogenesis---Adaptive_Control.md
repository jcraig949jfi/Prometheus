# Program Synthesis + Morphogenesis + Adaptive Control

**Fields**: Computer Science, Biology, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T16:23:56.666508
**Report Generated**: 2026-03-31T18:39:47.430370

---

## Nous Analysis

**Algorithm – Constraint‑Driven Morphogenetic Program Synthesis (CD‑MPS)**  

1. **Parsing & Feature Extraction**  
   - Use a handful of regex patterns to pull atomic propositions from the prompt and each candidate answer:  
     *Negations* (`not`, `no`, `never`), *comparatives* (`>`, `<`, `>=`, `<=`, `more than`, `less than`), *conditionals* (`if … then`, `unless`), *numeric values* (`\d+(\.\d+)?`), *causal cues* (`because`, `leads to`, `results in`), *ordering* (`before`, `after`, `first`, `last`).  
   - Each proposition becomes a Boolean variable `v_i` with an associated type (e.g., `numeric`, `categorical`).  
   - Build a factor graph: variables are nodes; each extracted relation creates a constraint factor `C_j(v_a, v_b, …)` (e.g., `v_a > 5`, `¬v_c`, `v_d → v_e`).

2. **Data Structures**  
   - `V`: NumPy array of shape `(n_vars,)` holding current activation `a_i ∈ [0,1]`.  
   - `W`: NumPy matrix `(n_constraints, n_vars)` of constraint weights (initialized to 1.0).  
   - `C`: list of constraint objects storing the logical function (implemented with NumPy vectorized ops) and the indices of involved variables.

3. **Morphogenetic Activation Diffusion**  
   - For each iteration `t`:  
     *Reaction*: compute local satisfaction `s_j = C_j(V)` (0 or 1).  
     *Diffusion*: update activations with a Laplacian‑style step:  
       `a_i ← a_i + η * ( Σ_j W_{j,i} * (s_j - a_i) )`  
       where `η` is a small diffusion rate.  
     This spreads satisfaction information across linked variables, letting stable patterns (consistent assignments) emerge, analogous to Turing‑style reaction‑diffusion.

4. **Adaptive Control of Weights**  
   - After diffusion, compute global error `E = Σ_j (1 - s_j)`.  
   - Update each weight with a self‑tuning rule (gradient descent on error):  
       `W_{j,i} ← W_{j,i} - α * ∂E/∂W_{j,i}` where `∂E/∂W_{j,i} = -(s_j - a_i)`.  
   - `α` is a small learning rate. Over iterations, weights increase for constraints that are consistently satisfied and decrease for violated ones, letting the system self‑regulate to focus on salient logical structure.

5. **Program Synthesis & Scoring**  
   - When activations converge (ΔV < ε or max iterations), extract a deterministic program: a set of threshold rules `if a_i > τ then output 1 else 0` for each variable, derived from the final `a_i`.  
   - For a candidate answer, reconstruct its feature vector `V_ans` (same extraction pipeline).  
   - Run the synthesized program on `V_ans` to get a predicted label `ŷ`.  
   - Score = `1 - |ŷ - y_true|` (if a gold label is known) or simply the average activation of satisfied constraints: `score = mean(s_j)` evaluated on `V_ans`. Higher scores indicate answers that better satisfy the learned constraint pattern.

**Structural Features Parsed** – negations, comparatives, conditionals, numeric thresholds, causal cue phrases, ordering/temporal relations.

**Novelty** – While constraint satisfaction and program synthesis each appear in QA reranking, coupling them with a reaction‑diffusion dynamics layer and an online adaptive weight‑tuning controller is not present in existing literature; the morphogenetic diffusion of satisfaction scores is a novel mechanism for answer scoring.

**Rating**  
Reasoning: 8/10 — The algorithm captures logical structure, propagates consistency, and adapts weights, yielding nuanced reasoning beyond surface similarity.  
Metacognition: 6/10 — It monitors error and adjusts weights, but lacks explicit higher‑order reflection on its own uncertainty.  
Hypothesis generation: 7/10 — The synthesized threshold program functions as a compact hypothesis about answer correctness; generation is systematic but limited to linear‑threshold forms.  
Implementability: 9/10 — All components rely solely on NumPy vectorized ops and the Python standard library; no external models or APIs are required.

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
**Reason**: validation:runtime_error: NameError: name 'Dict' is not defined

**Forge Timestamp**: 2026-03-31T18:30:02.459405

---

## Code

**Source**: scrap

[View code](./Program_Synthesis---Morphogenesis---Adaptive_Control/tool.py)

<details>
<summary>Show code</summary>

```python
class ReasoningTool:
    """
    Constraint-Driven Morphogenetic Program Synthesis (CD-MPS) Tool.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals, numbers).
    2. Representation: Builds a factor graph where variables are nodes and logical relations are constraints.
    3. Morphogenesis: Uses reaction-diffusion dynamics to propagate satisfaction scores across the graph.
       - Reaction: Local constraint satisfaction.
       - Diffusion: Spreads consistency information via Laplacian-style updates.
    4. Adaptive Control: Adjusts constraint weights based on global error (gradient descent).
    5. Scoring: Evaluates candidates against the converged logical state.
    
    Epistemic Honesty: Detects ambiguity, presupposition, and insufficiency to cap confidence.
    """

    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 50
        self.eta = 0.1  # Diffusion rate
        self.alpha = 0.05  # Learning rate
        
        # Regex patterns for feature extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.I),
            'causal': re.compile(r'\b(because|leads to|results in|causes)\b', re.I),
            'numeric': re.compile(r'-?\d+(\.\d+)?'),
            'ordering': re.compile(r'\b(first|last|next|previous|between)\b', re.I),
            # Ambiguity detectors
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|regret)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|must be .+ or .+)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|think about)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|it)\b.*\bwho\b', re.I),
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features and numeric values."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'has_ordering': bool(self.patterns['ordering'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'length': len(text),
            'text_lower': text.lower()
        }
        return features

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Check if options are exhaustive (hard to know, but flag if vague)
            if "only two" not in p_lower:
                return 0.3
                
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.3
            
        # 4. Pronoun Ambiguity with "who" question
        if self.patterns['pronoun_ambiguity'].search(p_lower) and "who" in p_lower:
            return 0.25

        # 5. Unanswerability / Insufficiency heuristics
        if "impossible" in p_lower or "cannot be determined" in p_lower:
            return 0.9 # Actually high confidence that it's unanswerable if stated
            
        return 1.0

    def _compute_deterministic_answer(self, prompt: str) -> Optional[Any]:
        """
        Frame E: Computational Execution.
        Attempts to solve the problem logically/mathematically before pattern matching.
        Returns the computed result or None if not solvable computationally.
        """
        p_lower = prompt.lower()
        
        # 1. Numeric Comparison (Direct Calculation)
        nums = [float(n) for n in self.patterns['numeric'].findall(prompt)]
        if len(nums) == 2:
            if "greater" in p_lower or ">" in prompt:
                return max(nums)
            if "less" in p_lower or "<" in prompt:
                return min(nums)
            if "sum" in p_lower or "total" in p_lower:
                return sum(nums)
            if "difference" in p_lower:
                return abs(nums[0] - nums[1])
                
        # 2. Bat-and-Ball Algebra (x + y = T, x = y + D => 2y + D = T)
        # Pattern: "A and B cost $T. A costs $D more than B."
        if "cost" in p_lower and "more than" in p_lower and len(nums) >= 2:
            # Heuristic: Assume last two numbers are Total and Diff if structure fits
            # Strict parsing is hard, but let's try standard bat-and-ball form
            # "A ball and a bat cost $1.10. The bat costs $1.00 more than the ball."
            if len(nums) == 2:
                total, diff = nums
                if total > diff:
                    ball = (total - diff) / 2.0
                    return round(ball, 2)

        # 3. Modular Arithmetic
        # "What is X mod Y?" or "remainder of X divided by Y"
        if ("mod" in p_lower or "remainder" in p_lower) and len(nums) >= 2:
            return int(nums[0]) % int(nums[1])
            
        # 4. Parity
        if ("odd" in p_lower or "even" in p_lower) and len(nums) >= 1:
            n = int(nums[0])
            if "odd" in p_lower:
                return (n % 2 != 0)
            return (n % 2 == 0)

        # 5. Temporal Ordering (Simple Before/After)
        # "If A is before B, and B is before C, what is first?"
        if "before" in p_lower and "after" in p_lower:
            # Very basic extraction of entities around keywords
            # This is a simplification; full SVO parsing is complex without NLP libs
            pass 

        return None

    def _build_constraint_system(self, prompt: str, candidates: List[str]) -> Tuple[np.ndarray, List[Any], np.ndarray]:
        """
        Build the factor graph components: Variables (V), Constraints (C), Weights (W).
        """
        p_feat = self._extract_features(prompt)
        c_feats = [self._extract_features(c) for c in candidates]
        
        # Variables: [Prompt_Neg, Prompt_Num, Cand_Neg, Cand_Num, Match_Neg, Match_Num]
        # Simplified to 4 core variables for the morphogenetic field
        # 0: Prompt has Negation
        # 1: Candidate has Negation
        # 2: Prompt has Number
        # 3: Candidate has Number
        
        n_vars = 4
        n_constraints = 0
        constraints = []
        
        # Helper to add constraint
        def add_constraint(func, indices):
            nonlocal n_constraints
            constraints.append({'func': func, 'indices': indices})
            n_constraints += 1

        # Constraint 1: Negation Consistency (Modus Tollens-ish)
        # If prompt has negation, candidate should ideally reflect it (or contradict logically)
        # Simplified: If prompt has 'not', candidate having 'not' gets a boost (double negation or emphasis)
        # Or if prompt implies negation, candidate without it is penalized.
        # Let's use a simple consistency check: Prompt Neg == Candidate Neg (for simple traps)
        def c_neg_consistency(V):
            # V[0] = prompt_neg, V[1] = cand_neg
            # Satisfaction is high if both have it or both don't (context dependent)
            # For now, assume structural symmetry in simple logic puzzles
            return 1.0 if (V[0] == V[1]) else 0.0
        add_constraint(c_neg_consistency, [0, 1])

        # Constraint 2: Numeric Presence
        # If prompt has numbers, valid answer often involves numbers
        def c_numeric_presence(V):
            return 1.0 if (V[2] > 0.5 and V[3] > 0.5) or (V[2] < 0.5 and V[3] < 0.5) else 0.0
        add_constraint(c_numeric_presence, [2, 3])

        # Constraint 3: Logical Implication (Prompt -> Candidate)
        # If prompt is conditional, candidate should be categorical or boolean
        if p_feat['has_conditional']:
            def c_conditional(V):
                # If prompt conditional, candidate must have some logical marker
                return 1.0 if V[1] > 0.2 else 0.5 # Weak constraint
            add_constraint(c_conditional, [1]) # Check cand neg as proxy for logic

        # Initialize Variables (Activations)
        # Order: [p_neg, c_neg, p_num, c_num]
        V = np.array([
            1.0 if p_feat['has_negation'] else 0.0,
            0.0, # Will be set per candidate
            1.0 if len(p_feat['numbers']) > 0 else 0.0,
            0.0  # Will be set per candidate
        ], dtype=float)

        W = np.ones((n_constraints, n_vars), dtype=float)
        
        return V, constraints, W, p_feat, c_feats

    def _morphogenetic_solve(self, V_init: np.ndarray, constraints: List, W: np.ndarray) -> np.ndarray:
        """Run the reaction-diffusion and adaptive control loop."""
        V = V_init.copy()
        n_constraints = len(constraints)
        n_vars = len(V)
        
        for t in range(self.max_iter):
            V_old = V.copy()
            s = np.zeros(n_constraints)
            
            # Reaction: Compute satisfaction for each constraint
            for j, cons in enumerate(constraints):
                indices = cons['indices']
                # Gather relevant variables
                v_sub = V[indices]
                # Evaluate constraint function
                s[j] = cons['func'](v_sub)
            
            # Diffusion: Update activations
            # a_i <- a_i + eta * sum_j ( W_ji * (s_j - a_i) )
            # Note: W is (n_constraints, n_vars). 
            # We need to aggregate influence of all constraints on var i
            for i in range(n_vars):
                diffusion_term = 0.0
                for j in range(n_constraints):
                    if i in constraints[j]['indices']:
                        # Simple weighting: if var is involved, it feels the constraint
                        diffusion_term += W[j, i] * (s[j] - V[i])
                V[i] += self.eta * diffusion_term
                
                # Clamp to [0, 1]
                V[i] = max(0.0, min(1.0, V[i]))

            # Adaptive Control: Update Weights
            # E = sum(1 - s_j)
            # dE/dW = -(s_j - a_i) approx
            E = np.sum(1.0 - s)
            if E < self.epsilon:
                break
                
            for j in range(n_constraints):
                for i in constraints[j]['indices']:
                    # Gradient step to reduce error by increasing weight if satisfied, decreasing if not?
                    # Actually, we want to weight constraints that are HARD to satisfy but satisfied?
                    # Or simply: if s_j is low, reduce weight (it's a bad constraint for this context)
                    # If s_j is high, increase weight.
                    grad = -(s[j] - V[i]) 
                    W[j, i] -= self.alpha * grad
                    W[j, i] = max(0.1, W[j, i]) # Prevent zeroing out completely

            if np.max(np.abs(V - V_old)) < self.epsilon:
                break
                
        return V, s

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Meta-confidence check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # Try deterministic computation first (Frame E)
        computed_result = self._compute_deterministic_answer(prompt)
        
        results = []
        
        # Build shared constraint system
        V_init, constraints, W_init, p_feat, c_feats = self._build_constraint_system(prompt, candidates)
        
        for i, cand in enumerate(candidates):
            score = 0.0
            reasoning = []
            
            # 1. Deterministic Match (High Priority)
            if computed_result is not None:
                cand_text = str(cand).lower().strip()
                cand_str = str(computed_result).lower().strip()
                
                # Check if candidate contains the computed result
                if cand_str in cand_text or cand_text in cand_str:
                    score = 1.0
                    reasoning.append(f"Computed value {computed_result} matches candidate.")
                elif len(c_feats[i]['numbers']) > 0:
                    # Check numeric proximity if exact string match fails
                    if abs(c_feats[i]['numbers'][0] - computed_result) < 0.01:
                        score = 0.95
                        reasoning.append(f"Numeric match to computed {computed_result}.")
                    else:
                        score = 0.1 # Computed answer exists but doesn't match
                        reasoning.append(f"Computed {computed_result}, candidate differs.")
                else:
                    score = 0.1
                    reasoning.append(f"Expected numeric/logic result {computed_result}, candidate is textual.")
            else:
                # 2. Morphogenetic Scoring (When no direct computation possible)
                # Initialize V for this candidate
                V_curr = V_init.copy()
                V_curr[1] = 1.0 if c_feats[i]['has_negation'] else 0.0
                V_curr[3] = 1.0 if len(c_feats[i]['numbers']) > 0 else 0.0
                
                # Run dynamics
                V_final, s_final = self._morphogenetic_solve(V_curr, constraints, W_init.copy())
                
                # Score based on average constraint satisfaction and activation stability
                base_score = np.mean(s_final)
                
                # Bonus for structural alignment (e.g., if prompt has numbers, cand should)
                struct_bonus = 0.0
                if p_feat['has_negation'] and c_feats[i]['has_negation']:
                    struct_bonus += 0.2
                if len(p_feat['numbers']) > 0 and len(c_feats[i]['numbers']) > 0:
                    struct_bonus += 0.2
                    
                score = min(1.0, base_score * 0.6 + struct_bonus)
                reasoning.append(f"Morphogenetic consistency: {base_score:.2f}, Structural bonus: {struct_bonus:.2f}")

            # Apply Epistemic Cap
            if meta_cap < 0.5:
                score = min(score, meta_cap + 0.2) # Allow slight rise if candidate resolves ambiguity, but keep low
                
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasoning) if reasoning else "Structural evaluation."
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity/traps.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run a quick evaluation to see if the answer is structurally sound
        # We simulate a binary choice scenario implicitly
        dummy_candidates = [answer, "INVALID_PLACEHOLDER"]
        # We don't need full eval, just check if the answer triggers computational flags
        computed = self._compute_deterministic_answer(prompt)
        
        conf = 0.5 # Base uncertainty
        
        if computed is not None:
            # If we can compute, check match
            if str(computed).lower() in str(answer).lower():
                conf = 0.95
            else:
                conf = 0.1
        else:
            # If no computation, rely on structural parse quality
            # If prompt is complex but answer is short, confidence drops
            if len(answer.split()) < 2 and len(prompt.split()) > 20:
                conf = 0.4
            else:
                conf = 0.6 # Moderate confidence for structural matches

        return float(min(conf, meta_cap))

    def _meta_confidence(self, prompt: str) -> float:
        """Wrapper for epistemic checks."""
        return self._check_meta_conf
```

</details>
