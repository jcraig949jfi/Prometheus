from typing import Dict, List, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Information Theory, Phase Transitions, and Dynamical Systems.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals, causals).
    2. Constraint Graph: Builds a directed adjacency matrix of implications.
    3. Noisy Worlds: Simulates truth assignments under varying noise temperatures (T).
    4. Criticality: Computes entropy and susceptibility to find the critical temperature (T*) where 
       the system undergoes a phase transition.
    5. Dynamics (Frame C): Tracks state evolution via Markov chain convergence to assess 
       trajectory stability (Lyapunov-like) under premise reordering.
    6. Scoring: Aligns candidate T* with reference T*, weighted by dynamic stability and 
       epistemic honesty checks.
    """

    def __init__(self):
        # Regex patterns for atomic proposition extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after|first|last)\b|[><=]', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'dichotomy': re.compile(r'\b(either|or|but not|must be)\b', re.IGNORECASE),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|quit|fail)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|it|they|him|her)\b.*\b(who|which one)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.IGNORECASE)
        }
        self.k_noise = 10.0  # Steepness of noise function
        self.M_samples = 200 # Number of noisy worlds per temperature
        self.T_bins = 20     # Resolution of temperature scan

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with type tags and polarity."""
        props = []
        text_lower = text.lower()
        
        # Simple sentence splitting (naive but effective for short logic puzzles)
        sentences = [s.strip() for s in re.split(r'[.!?;]', text) if s.strip()]
        if not sentences:
            sentences = [text]

        for i, sent in enumerate(sentences):
            if not sent: continue
            
            p_type = 'statement'
            polarity = True
            
            if self.patterns['negation'].search(sent):
                p_type = 'negation'
                polarity = False
            elif self.patterns['conditional'].search(sent):
                p_type = 'conditional'
            elif self.patterns['causal'].search(sent):
                p_type = 'causal'
            elif self.patterns['comparative'].search(sent):
                p_type = 'comparative'
            
            # Extract numeric literals if present
            nums = self.patterns['numeric'].findall(sent)
            
            props.append({
                'id': i,
                'text': sent,
                'type': p_type,
                'polarity': polarity,
                'has_numeric': len(nums) > 0,
                'nums': nums
            })
        return props

    def _build_constraint_graph(self, props: List[Dict]) -> np.ndarray:
        """Build adjacency matrix A where A[i,j]=1 if prop i implies prop j."""
        n = len(props)
        if n == 0:
            return np.zeros((0, 0), dtype=int)
            
        A = np.zeros((n, n), dtype=int)
        
        # Heuristic: Conditionals create edges. 
        # If a sentence contains "if", it likely links to the next or creates a self-constraint logic.
        # For this implementation, we assume sequential dependency for conditionals 
        # and explicit causal links.
        
        for i, p in enumerate(props):
            if p['type'] == 'conditional':
                # Connect to next proposition if exists, else self-loop (tautology check)
                if i + 1 < n:
                    A[i, i+1] = 1
                else:
                    A[i, i] = 1 
            elif p['type'] == 'causal':
                if i + 1 < n:
                    A[i, i+1] = 1
                else:
                    A[i, i] = 1
            else:
                # Default sequential flow for narrative logic
                if i + 1 < n:
                    A[i, i+1] = 1
        
        # Transitive closure C = A* using Boolean Warshall or matrix power
        # Since n is small, repeated squaring is fine.
        if n > 0:
            C = A.copy()
            for _ in range(n): # Approximate closure
                C = np.sign(C + C @ A) # Boolean addition and multiplication
            return C
        return A

    def _compute_critical_point(self, props: List[Dict], C: np.ndarray) -> float:
        """
        Simulate noisy worlds to find the temperature T* where susceptibility peaks.
        """
        n = len(props)
        if n == 0:
            return 0.5
            
        T_vals = np.linspace(0.01, 0.99, self.T_bins)
        H_vals = []
        
        # Pre-calculate constraint pairs from C
        # A constraint (i, j) is satisfied if (x_i is False) OR (x_j is True)
        # i.e., implication i -> j
        constraints = []
        rows, cols = np.where(C == 1)
        for r, c in zip(rows, cols):
            if r != c: # Ignore self-loops for constraint counting to avoid triviality
                constraints.append((r, c))
        
        if not constraints:
            return 0.5 # No constraints, flat landscape

        for T in T_vals:
            sigma = 1.0 / (1.0 + np.exp(-self.k_noise * (T - 0.5)))
            satisfied_counts = []
            
            for _ in range(self.M_samples):
                # Generate noisy truth assignment
                # Base truth: assume all propositions are initially True (default assumption)
                # Noise flips them with probability sigma
                x = np.random.rand(n) > sigma 
                x = x.astype(int) 
                
                # Check constraints
                sat_count = 0
                for i, j in constraints:
                    # Implication: if x[i] then x[j]
                    # False if x[i]=1 and x[j]=0
                    if x[i] == 0 or x[j] == 1:
                        sat_count += 1
                
                frac_sat = sat_count / len(constraints)
                satisfied_counts.append(frac_sat)
            
            # Compute Entropy of the distribution of satisfied fractions
            # Bin the results
            hist, _ = np.histogram(satisfied_counts, bins=10, range=(0, 1), density=True)
            hist = hist + 1e-9 # Avoid log(0)
            hist = hist / np.sum(hist)
            H = -np.sum(hist * np.log2(hist))
            H_vals.append(H)
        
        H_vals = np.array(H_vals)
        
        # Susceptibility chi = |dH/dT|
        if len(H_vals) < 2:
            return 0.5
            
        dH = np.abs(np.gradient(H_vals))
        peak_idx = np.argmax(dH)
        return T_vals[peak_idx]

    def _analyze_dynamics(self, prompt: str, answer: str) -> Tuple[float, float]:
        """
        Frame C: Dynamics Tracker.
        Models reasoning as a state evolution. 
        Returns (convergence_rate, stability_score).
        """
        # 1. Construct a synthetic state vector based on prompt features
        props = self._extract_propositions(prompt + " " + answer)
        n = len(props)
        if n == 0:
            return 0.0, 0.0
            
        # Initialize state vector (e.g., truth values or feature presence)
        # Let's use a simple binary feature vector per proposition
        state_dim = 4 # neg, comp, cond, causal
        S0 = np.zeros((n, state_dim))
        
        for i, p in enumerate(props):
            if p['type'] == 'negation': S0[i, 0] = 1
            elif p['type'] == 'comparative': S0[i, 1] = 1
            elif p['type'] == 'conditional': S0[i, 2] = 1
            elif p['type'] == 'causal': S0[i, 3] = 1
            
        # 2. Simulate Markov Chain / Reservoir Dynamics
        # Transition matrix based on constraint graph
        C = self._build_constraint_graph(props)
        if C.size == 0:
            return 0.0, 0.0
            
        # Normalize rows to make it stochastic (Markov)
        row_sums = C.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1 # Avoid division by zero
        P = C / row_sums
        
        # Evolve state: S_{t+1} = P * S_t
        # We look for convergence (steady state)
        S_curr = S0.copy()
        trajectory = []
        convergence_dist = []
        
        for t in range(10): # 10 steps
            S_next = P @ S_curr
            # Add small noise to test stability (Lyapunov exponent proxy)
            noise = np.random.normal(0, 0.01, S_next.shape)
            S_next += noise
            
            diff = np.linalg.norm(S_next - S_curr)
            convergence_dist.append(diff)
            trajectory.append(S_next.copy())
            S_curr = S_next
            
        # Convergence rate: How fast does diff drop?
        if len(convergence_dist) > 1:
            # Fit linear decay to log(diff) or just average drop
            avg_drop = np.mean(np.diff(convergence_dist))
            conv_rate = -avg_drop if avg_drop < 0 else 0.0
        else:
            conv_rate = 0.0
            
        # Stability: Variance of the final states across perturbations
        # (Simplified here as inverse of final difference)
        stability = 1.0 / (convergence_dist[-1] + 0.1) if convergence_dist else 0.0
        stability = min(1.0, stability) # Cap at 1
        
        return float(conv_rate), float(stability)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt pathology.
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            score = min(score, 0.2)
            
        # 2. Pronoun Ambiguity (heuristic: pronoun + who?)
        if self.patterns['pronoun_ambiguity'].search(p_lower):
            score = min(score, 0.2)
            
        # 3. False Dichotomy (Either/Or without context)
        if self.patterns['dichotomy'].search(p_lower) and "option" not in p_lower:
            score = min(score, 0.4)
            
        # 4. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            score = min(score, 0.3)
            
        # 5. Unanswerability (Very short prompts or missing info indicators)
        if len(prompt.split()) < 3:
            score = min(score, 0.1)
            
        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denom

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Core logic: Compare critical points of prompt+candidate vs prompt+reference.
        Since we don't have a gold reference, we treat the candidate's internal 
        consistency as the signal. We compare the candidate's T* to an idealized 
        stable T* (0.5) or use the prompt's inherent T* as a baseline.
        
        Better approach for single-candidate evaluation without gold:
        Measure the 'sharpness' of the phase transition. High sharpness = high logical structure.
        Low sharpness = random noise.
        """
        full_text = f"{prompt} {candidate}"
        props = self._extract_propositions(full_text)
        if not props:
            return 0.0
            
        C = self._build_constraint_graph(props)
        if C.size == 0:
            return 0.0
            
        # Re-run simulation to get the curve shape
        n = len(props)
        T_vals = np.linspace(0.01, 0.99, self.T_bins)
        s_vals = []
        
        constraints = []
        rows, cols = np.where(C == 1)
        for r, c in zip(rows, cols):
            if r != c:
                constraints.append((r, c))
        
        if not constraints:
            return 0.1 # Low score for no logic

        for T in T_vals:
            sigma = 1.0 / (1.0 + np.exp(-self.k_noise * (T - 0.5)))
            sat_list = []
            for _ in range(50): # Fewer samples for speed in scoring
                x = (np.random.rand(n) > sigma).astype(int)
                sat = sum(1 for i, j in constraints if x[i] == 0 or x[j] == 1) / len(constraints)
                sat_list.append(sat)
            s_vals.append(np.mean(sat_list))
            
        s_vals = np.array(s_vals)
        
        # Calculate susceptibility (derivative)
        chi = np.abs(np.gradient(s_vals))
        
        # A structured logical argument should have a distinct transition.
        # Random text often has a flat or monotonic curve.
        # We look for the peak magnitude.
        peak_chi = np.max(chi)
        
        # Normalize: Theoretical max derivative for step function is high.
        # Let's map peak_chi to [0, 1]. 
        # Empirical heuristic: peak_chi > 0.5 is good structure.
        struct_score = min(1.0, peak_chi / 0.8)
        
        return float(struct_score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Baseline: If no candidates, return empty
        if not candidates:
            return []
            
        # Calculate NCD distances to prompt for tie-breaking
        ncd_scores = [self._ncd_score(prompt, c) for c in candidates]
        min_ncd = min(ncd_scores) if ncd_scores else 1.0
        
        for i, cand in enumerate(candidates):
            # 1. Meta-Confidence (Epistemic Honesty)
            meta_cap = self._meta_confidence(prompt)
            
            # 2. Structural Score (Phase Transition)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 3. Dynamics Score (Stability)
            conv_rate, stability = self._analyze_dynamics(prompt, cand)
            dyn_score = stability * 0.7 + min(1.0, conv_rate * 10) * 0.3
            
            # 4. Numeric/Constructive Check (Simple heuristic)
            # If prompt has numbers and candidate has numbers, boost slightly
            has_nums_p = bool(self.patterns['numeric'].search(prompt))
            has_nums_c = bool(self.patterns['numeric'].search(cand))
            numeric_bonus = 0.1 if (has_nums_p and has_nums_c) else 0.0
            
            # Combine scores
            # Weighting: Structural 50%, Dynamics 30%, NCD 15%, Numeric 5%
            raw_score = (
                struct_score * 0.50 +
                dyn_score * 0.30 +
                (1.0 - min_ncd) * 0.05 + # NCD as minor factor
                numeric_bonus
            )
            
            # Apply NCD penalty if candidate is too dissimilar (gameable check)
            cand_ncd = self._ncd_score(prompt, cand)
            if cand_ncd > 0.9: # Too different?
                raw_score *= 0.8
                
            # Apply Epistemic Cap
            final_score = min(raw_score, meta_cap)
            final_score = max(0.0, min(1.0, final_score)) # Clamp [0,1]