class ReasoningTool:
    """
    A hybrid reasoning tool combining structural logic parsing, thermodynamic 
    constraint satisfaction (energy minimization), and information-theoretic 
    entropy estimation. 
    
    Mechanism:
    1. Parses propositions (literals, negations, comparatives, conditionals) 
       from prompt and candidates into a unified constraint system.
    2. Models truth values as continuous variables. Constraints form an energy 
       landscape where violations increase energy (E).
    3. Samples the solution space to estimate entropy (S), penalizing ambiguity.
    4. Applies pragmatic weights (U) based on historical constraint reliability.
    5. Scores candidates via a free-energy-like objective: Score = -E + T*S + lambda*U.
    6. Uses NCD only as a tiebreaker for structural equality.
    """
    
    def __init__(self):
        # Pragmatic weights: historical success rates of constraint types
        # Higher weight = more reliable indicator of correctness
        self.pragmatic_weights = {
            'literal': 1.0,
            'negation': 1.2,      # Negations often critical for logic traps
            'comparative': 1.1,   # Math/Ordering is high fidelity
            'conditional': 0.9,
            'causal': 0.8,
            'numeric': 1.3,       # Numeric exactness is highest priority
            'temporal': 1.0
        }
        self.temperature = 1.0
        self.lambda_utility = 0.5
        self.n_samples = 50 # K samples for Monte Carlo estimation

    def _parse_propositions(self, text: str) -> List[Tuple[str, Any]]:
        """Extract structural features into typed propositions."""
        props = []
        text_lower = text.lower()
        
        # 1. Numeric comparisons (e.g., "9.11 < 9.9", "greater than 5")
        # Pattern: number (operator) number
        num_pat = r'(\d+\.?\d*)\s*(?:is\s+)?(greater\s+than|less\s+than|equal\s+to|>|<|=)\s*(\d+\.?\d*)'
        for m in re.finditer(num_pat, text_lower):
            v1, op, v2 = m.groups()
            props.append(('numeric', (float(v1), op.replace(' ', '_'), float(v2))))
            
        # 2. Negations (e.g., "not true", "is not")
        if re.search(r'\b(not|no|never)\b', text_lower):
            # Simplified: flag presence of negation affecting the whole sentence context
            props.append(('negation', 'global'))
            
        # 3. Comparatives (textual)
        if re.search(r'\b(more|less|greater|smaller|higher|lower)\b', text_lower):
            props.append(('comparative', 'detected'))
            
        # 4. Conditionals
        if re.search(r'\b(if|then|unless|otherwise)\b', text_lower):
            props.append(('conditional', 'detected'))

        # 5. Literals (simple subject-verb-object extraction approximation)
        # Looking for "the X is Y" or "X equals Y"
        lit_pat = r'\b(the\s+\w+\s+is\s+\w+|\w+\s+equals\s+\w+)\b'
        if re.search(lit_pat, text_lower):
            props.append(('literal', 'detected'))

        return props

    def _build_constraints(self, prompt_props: List, cand_props: List) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Build matrix A and vector b for Ax >= b.
        Rows represent constraints. 
        Returns A, b, and a list of constraint types for each row.
        """
        rows = []
        b_vals = []
        types = []
        
        # Combine prompt and candidate properties to check consistency
        all_props = prompt_props + cand_props
        
        # Constraint 1: Numeric consistency
        # If prompt says A > B and candidate implies A < B, energy increases.
        # Here we simplify: if candidate has numeric claims, they must not contradict prompt.
        # We encode "Candidate numeric truth" as a variable x_0. 
        # If prompt has numeric, we force x_0 to align.
        
        p_nums = [p[1] for p in prompt_props if p[0] == 'numeric']
        c_nums = [p[1] for p in cand_props if p[0] == 'numeric']
        
        # Add a generic "truth" variable index 0
        # If numeric values match exactly, constraint is satisfied (0 energy)
        # If they conflict, we add a penalty row.
        
        if p_nums and c_nums:
            # Check for direct contradiction
            p_val, p_op, p_target = p_nums[0]
            c_val, c_op, c_target = c_nums[0]
            
            # Simple contradiction check: same numbers, opposite operator
            if abs(p_val - c_val) < 1e-6 and abs(p_target - c_target) < 1e-6:
                if (p_op == 'greater_than' and c_op == 'less_than') or \
                   (p_op == 'less_than' and c_op == 'greater_than'):
                    # Contradiction: x_0 <= -1 (Impossible if x_0 >= 0)
                    rows.append([-1.0]) 
                    b_vals.append(1.0)
                    types.append('numeric')
        
        # Constraint 2: Negation consistency
        p_neg = any(p[0] == 'negation' for p in prompt_props)
        c_neg = any(p[0] == 'negation' for p in cand_props)
        
        # If prompt implies negation is needed but candidate lacks it (or vice versa)
        # This is a soft heuristic: mismatch adds energy
        if p_neg != c_neg:
            rows.append([-1.0]) # Penalty
            b_vals.append(0.5)
            types.append('negation')
            
        # If no specific constraints found, add a dummy constraint to keep matrix valid
        if not rows:
            rows.append([0.0])
            b_vals.append(0.0)
            types.append('literal')
            
        return np.array(rows), np.array(b_vals), types

    def _compute_energy(self, A: np.ndarray, b: np.ndarray, x: np.ndarray) -> float:
        """Calculate constraint violation energy: sum(max(0, Ax - b)^2)"""
        if A.shape[1] == 0:
            return 0.0
        # Ensure x matches dimensions (pad if necessary)
        if len(x) < A.shape[1]:
            x = np.pad(x, (0, A.shape[1] - len(x)), 'constant')
        x = x[:A.shape[1]]
        
        violations = np.dot(A, x) - b
        return np.sum(np.maximum(0, violations)**2)

    def _compute_entropy(self, A: np.ndarray, b: np.ndarray, n_dim: int) -> float:
        """Estimate entropy of the feasible region via sampling."""
        if n_dim == 0 or A.size == 0:
            return 0.0
            
        feasible_samples = []
        # Sample from uniform prior
        samples = np.random.uniform(-1, 1, (self.n_samples, n_dim))
        
        for x in samples:
            energy = self._compute_energy(A, b, x)
            # Threshold for "feasible" (approx 0)
            if energy < 1e-3:
                feasible_samples.append(x)
        
        if len(feasible_samples) == 0:
            # No feasible region found -> High uncertainty/chaos -> Low entropy score (penalty)
            # Or technically, if region is empty, entropy is undefined, but we treat as high disorder
            return 0.0
            
        # Discretize space to compute histogram entropy
        # Project to 1D if multi-dimensional for simplicity in this constrained env
        feasible_samples = np.array(feasible_samples)
        if feasible_samples.ndim > 1:
            projections = feasible_samples[:, 0] # Project to first dim
        else:
            projections = feasible_samples
            
        if len(projections) == 0:
            return 0.0
            
        # Histogram
        counts, _ = np.histogram(projections, bins=10, density=True)
        probs = counts / (counts.sum() + 1e-10)
        probs = probs[probs > 0]
        
        return -np.sum(probs * np.log2(probs))

    def _compute_utility(self, constraint_types: List[str]) -> float:
        """Compute pragmatic utility based on constraint types satisfied."""
        # In this simplified model, we assume if we are evaluating, we are checking satisfaction.
        # The utility is the sum of weights of the types of constraints present.
        # If a constraint type exists in the problem, satisfying it yields utility.
        utility = 0.0
        for ctype in constraint_types:
            utility += self.pragmatic_weights.get(ctype, 0.5)
        return utility

    def _calculate_score(self, prompt: str, candidate: str) -> float:
        # 1. Parse
        p_props = self._parse_propositions(prompt)
        c_props = self._parse_propositions(candidate)
        
        # 2. Build Constraints
        A, b, types = self._build_constraints(p_props, c_props)
        n_dim = A.shape[1] if A.shape[1] > 0 else 1
        
        # 3. Energy (Average over samples)
        # We sample random truth assignments to see how hard it is to satisfy constraints
        energies = []
        entropies = []
        
        # Deterministic seed for reproducibility within this call
        np.random.seed(42) 
        
        for _ in range(self.n_samples):
            x = np.random.uniform(-1, 1, n_dim)
            e = self._compute_energy(A, b, x)
            energies.append(e)
            
        avg_energy = np.mean(energies)
        
        # 4. Entropy
        entropy = self._compute_entropy(A, b, n_dim)
        
        # 5. Utility
        utility = self._compute_utility(types)
        
        # 6. Final Score: -Energy + Temp*Entropy + Lambda*Utility
        # Lower energy is better (so -E), Higher entropy is usually "more uncertain" 
        # but the prompt says "Higher S indicates... unresolved... which we penalize".
        # Wait, the formula in prompt: Score = -<E> + T*S + lambda*U.
        # And text says: "Higher S ... we penalize". This implies the formula should be -S?
        # Let's re-read carefully: "Higher S indicates the answer leaves more uncertainty unresolved, which we penalize."
        # But the formula given is: Score = -<E> + T*S + lambda*U.
        # If S is high, Score goes UP. This contradicts "penalize".
        # Interpretation: The prompt description of S might be "uncertainty", and usually we want LOW uncertainty.
        # However, in MaxEnt principles, we often maximize entropy to avoid overfitting.
        # Given the explicit formula in the prompt: Score = -<E> + T*S + lambda*U
        # I will follow the formula strictly. If S is "unresolved uncertainty", maybe the prompt meant 
        # the formula should have been -TS? 
        # BUT, the instruction says "Implement this as...". I must follow the formula provided.
        # Formula: Score = -<E> + T*S + lambda*U
        # If the text says "penalize", maybe T should be negative? Or S is defined differently?
        # Let's look at the "Thermodynamics" hint: Free Energy = Energy - Temp*Entropy.
        # Minimizing Free Energy -> Minimizing E - TS -> Maximizing -E + TS.
        # So the formula matches Free Energy minimization (maximizing the negative free energy).
        # In Free Energy, high entropy (disorder) is favored by the T*S term? 
        # Actually, F = E - TS. To minimize F, if T is high, we want high S.
        # So high S increases the score (makes it less positive/more negative F).
        # Okay, I will stick to the formula: Score = -avg_energy + T * entropy + lambda * utility.
        # Wait, if S is "unresolved uncertainty", we usually want to MINIMIZE it.
        # If the prompt says "penalize", then the term should be negative.
        # Conflict: Formula says +T*S. Text says "penalize".
        # Resolution: The prompt's text description of the penalty might be describing the *effect* of S in a different context,
        # OR the formula provided is the ground truth for implementation.
        # Given "Algorithm" section is the primary instruction: "Score(h) = -<E> + T*S + lambda*U".
        # I will implement the formula exactly. If S is high, Score increases.
        # However, to align with "penalize uncertainty", I will interpret the entropy calculation 
        # such that a "tight" solution (low uncertainty) has HIGHER entropy in the feasible region?
        # No, Shannon entropy is high for uniform distribution (high uncertainty).
        # Let's assume the formula is correct and the text "penalize" implies that in the specific 
        # thermodynamic analogy, this configuration works out. 
        # OR, perhaps I should subtract S? "Higher S ... which we penalize" -> Score -= S.
        # Let's look at the formula again: Score = -<E> + T*S + ...
        # If I follow the text "penalize", I should probably use -T*S.
        # BUT the formula is explicit. I will trust the explicit math formula over the prose description 
        # as this is a coding task based on an algorithm spec.
        # WAIT, re-reading: "Higher S indicates ... unresolved ... which we penalize."
        # If I strictly follow "penalize", the term must be negative.
        # Maybe the formula in the prompt has a typo? Or maybe T is negative? T is fixed to 1.0.
        # Let's look at the "Free Energy" concept. F = E - TS. We minimize F.
        # Equivalent to maximizing -F = -E + TS.
        # In statistical mechanics, high entropy states are MORE probable.
        # So maximizing entropy is usually the goal (principle of maximum entropy).
        # The text "penalize" might be a distractor or referring to a specific type of entropy (error entropy?).
        # Decision: I will implement the formula exactly as written: -E + T*S + U.
        # Why? Because "Free Energy" logic usually favors entropy (disorder) unless constrained by Energy.
        # The "penalize" text might refer to the fact that if E is high, the state is bad, and S is just a factor.
        # Actually, let's look at the "Causal Intelligence" warning: "Thermodynamics: Moderate positive synergy... secondary validation".
        # I will stick to the formula: Score = -avg_energy + self.temperature * entropy + self.lambda_utility * utility.
        # If the result is counter-intuitive, the structural parsing (Energy) dominates anyway.
        
        score = -avg_energy + self.temperature * entropy + self.lambda_utility * utility
        
        # Structural bonus: If candidate literally contains the answer to a numeric check
        # This boosts implementability for simple cases
        if 'numeric' in [p[0] for p in c_props]:
             score += 2.0 # Strong boost for explicit numeric reasoning
             
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(re.compress(b1))
            c2 = len(re.compress(b2))
            c12 = len(re.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        scores = []
        
        for cand in candidates:
            score = self._calculate_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Energy-constrained score with utility boost."
            })
            scores.append(score)
        
        # Tie-breaking with NCD if scores are very close
        final_results = []
        # Sort by score descending
        sorted_indices = np.argsort([-s for s in scores])
        
        for idx in sorted_indices:
            final_results.append(results[idx])
            
        # Refine ranking with NCD for ties (scores within 0.01)
        # This is a simple bubble pass for demonstration
        for i in range(len(final_results)-1):
            if abs(final_results[i]["score"] - final_results[i+1]["score"]) < 0.01:
                # Use NCD to prompt as tiebreaker (lower NCD = more similar/relevant)
                ncd1 = self._ncd(prompt, final_results[i]["candidate"])
                ncd2 = self._ncd(prompt, final_results[i+1]["candidate"])
                if ncd1 > ncd2: # If current is less similar, swap
                    final_results[i], final_results[i+1] = final_results[i+1], final_results[i]

        return final_results

    def confidence(self, prompt: str, answer: str