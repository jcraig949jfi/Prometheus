class ReasoningTool:
    """
    A reasoning tool combining Topological Data Analysis (Simplicial Complexes),
    Free Energy Principle (Error Minimization), and Property-Based Testing.
    
    Mechanism:
    1. Parsing: Extracts logical predicates and numeric constraints into a graph.
    2. Topology: Models truth assignments as a simplicial complex where holes represent
       logical inconsistencies.
    3. Free Energy: Defines an error function E(s) measuring clause violations.
    4. Dynamics (Frame C): Treats reasoning as a dynamical system. It simulates the 
       evolution of the state vector under premise perturbations to measure 
       Lyapunov-like stability (trajectory convergence).
    5. Epistemic Honesty (Tier B): Detects ambiguity/presuppositions to cap confidence.
    6. Scoring: Combines structural satisfaction, computational verification, 
       dynamic stability, and NCD (tiebreaker).
    """

    def __init__(self):
        self.tolerance = 1e-6

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity, presupposition, or unanswerability.
        """
        p = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        presupposition_patterns = [
            r"have you (stopped|quit|ceased)",
            r"why did .+ (fail|stop|end)",
            r"when did .+ (stop|fail)",
            r"how often do you",
            r"is it true that .+ (stopped|failed)"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p):
                return 0.2

        # 2. Scope/Pronoun Ambiguity
        ambiguity_triggers = [
            r"every .+ a .+", # "Every man loves a woman" (scope)
            r"told .+ he was", # Pronoun ambiguity
            r"told .+ she was",
            r"who is .+\?", # Often implies missing context in short prompts
            r"which one.*\?" # If options aren't clear
        ]
        for pat in ambiguity_triggers:
            if re.search(pat, p):
                # Only penalize if it looks like a trick question context
                if len(p.split()) < 50: # Heuristic for short ambiguous prompts
                    return 0.4

        # 3. False Dichotomy / Subjectivity
        if re.search(r"either .+ or .+", p) and not re.search(r"calculate|compute|math", p):
            return 0.5
        if re.search(r"(best|worst|favorite|most beautiful)", p) and not re.search(r"number|count", p):
            return 0.3

        # 4. Unanswerability (Missing info)
        if re.search(r"(unknown|missing|not given|insufficient)", p):
            return 0.1

        return 1.0

    def _parse_predicates(self, text: str) -> Tuple[List[str], np.ndarray, List[float]]:
        """
        Step 1: Parsing -> Propositional Graph.
        Extracts atomic predicates and builds adjacency matrix A and feature vector f.
        Returns nodes, adjacency matrix, and numeric features.
        """
        nodes = []
        edges = []
        features = []
        
        # Normalize
        text_clean = text.lower()
        
        # Extract numerics for constraints
        nums = re.findall(r"[-+]?\d*\.?\d+", text_clean)
        features = [float(n) for n in nums]
        
        # Simple tokenization for predicates (split by logic connectors)
        # We treat segments between logic words as nodes
        split_pattern = r"(if|then|else|and|or|not|implies|causes|leads to|before|after|>|<|=)"
        raw_segments = re.split(split_pattern, text)
        
        current_node_id = 0
        node_map = {} # text -> id
        
        def get_node_id(txt):
            txt = txt.strip()
            if not txt: return -1
            if txt not in node_map:
                node_map[txt] = current_node_id
                nodes.append(txt)
                return current_node_id - 1 # Will increment after
            return node_map[txt]

        # Re-scan to build graph structure
        # This is a simplified parser for the "Algorithm" description
        # It identifies relations and creates edges
        last_id = -1
        
        # Reset for structured pass
        nodes = []
        node_map = {}
        adj_list = []
        
        # Extract specific logical forms
        # Comparatives: "X > 5", "X is greater than Y"
        comp_pattern = r"(\w+)\s*(?:is\s+)?(greater|less|equal|more|fewer)\s+(?:than\s+)?(\w+|\d+\.?\d*)"
        for m in re.finditer(comp_pattern, text_clean):
            subj, comp_type, obj = m.groups()
            n1 = f"{subj}"
            n2 = f"{obj}"
            
            if n1 not in node_map:
                node_map[n1] = len(nodes)
                nodes.append(n1)
            if n2 not in node_map:
                node_map[n2] = len(nodes)
                nodes.append(n2)
            
            # Encode relation type in edge list (simplified to boolean adj for now)
            adj_list.append((node_map[n1], node_map[n2]))

        # Conditionals: "if A then B"
        cond_pattern = r"if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\s+(?:and|or|else|\.|$))"
        for m in re.finditer(cond_pattern, text_clean):
            antecedent = m.group(1).strip()
            consequent = m.group(2).strip()
            
            # Truncate long phrases for node identity
            a_node = antecedent[:20]
            c_node = consequent[:20]
            
            if a_node not in node_map:
                node_map[a_node] = len(nodes)
                nodes.append(a_node)
            if c_node not in node_map:
                node_map[c_node] = len(nodes)
                nodes.append(c_node)
            
            adj_list.append((node_map[a_node], node_map[c_node]))

        if len(nodes) == 0:
            # Fallback: treat whole text as one node if no structure found
            nodes = [text_clean[:50]]
            features = [0.0]
            return nodes, np.zeros((1,1), dtype=bool), features

        n_nodes = len(nodes)
        A = np.zeros((n_nodes, n_nodes), dtype=bool)
        for i, j in adj_list:
            if i < n_nodes and j < n_nodes:
                A[i, j] = True
                A[j, i] = True # Undirected for simplicial complex base

        return nodes, A, features

    def _compute_free_energy(self, candidate: str, nodes: List[str], A: np.ndarray, features: List[float]) -> float:
        """
        Step 3: Free-Energy-Like Error Function.
        E(s) = Sum of squared violations. 
        Here, we simulate 's' by checking if the candidate string satisfies the 
        logical implications encoded in the graph relative to the prompt.
        
        Since we don't have the full prompt state here, we approximate:
        - Check if candidate contradicts explicit numeric constraints in features.
        - Check semantic overlap (as a proxy for logical satisfaction).
        """
        if len(nodes) == 0:
            return 1.0

        cand_lower = candidate.lower()
        error = 0.0
        
        # 1. Numeric Constraint Check (Constructive Computation)
        # If prompt has numbers, candidate should ideally reflect them or not contradict
        cand_nums = re.findall(r"[-+]?\d*\.?\d+", cand_lower)
        cand_vals = [float(n) for n in cand_nums]
        
        # Penalty if candidate ignores specific numeric thresholds found in prompt features
        # This is a heuristic approximation of logical consistency
        if len(features) > 0 and len(cand_vals) == 0:
            # Candidate has no numbers but prompt does -> Potential error
            error += 0.5 * len(features)
        
        # 2. Logical Consistency (Simplicial violation approximation)
        # If A implies B (edge in A), and candidate asserts A but not B (heuristic)
        # Since we lack full truth values, we use string presence as a proxy for "True"
        present = [1 if n[:5] in cand_lower else 0 for n in nodes]
        present_vec = np.array(present)
        
        # Calculate "tension" in the graph: edges where one node is present and other isn't
        # High tension = high free energy (unlikely state)
        if A.shape[0] == len(present_vec):
            # Matrix mult to find neighbors
            # For each present node, check if neighbors are present
            for i in range(len(nodes)):
                if present_vec[i] == 1:
                    neighbors = A[i, :]
                    neighbor_presence = present_vec[neighbors]
                    # If I am true, my neighbors (implications) should ideally be true
                    # Violation = count of missing neighbors
                    error += np.sum(1 - neighbor_presence) * 0.1
        
        # 3. Direct Contradiction Check (Negation)
        if "not" in cand_lower and any(n.split()[0] in cand_lower for n in nodes if n):
             error += 1.0

        return float(error)

    def _property_based_shrink(self, prompt: str, candidate: str, nodes: List[str], A: np.ndarray, features: List[float]) -> int:
        """
        Step 4: Property-Based Testing Loop (Shrinking).
        Generate random perturbations of the candidate's logical representation.
        Return size of Minimal Failing Assignment (MFA).
        """
        # Simulate truth assignment vector based on candidate content
        if len(nodes) == 0:
            return 10 # Default high error size
            
        cand_lower = candidate.lower()
        initial_state = np.array([1 if n[:5] in cand_lower else 0 for n in nodes], dtype=float)
        
        # Base energy
        def get_energy(state):
            # Reconstruct pseudo-candidate from state? 
            # Instead, measure deviation from initial state logic
            # Simplified: Count active nodes vs edges
            active_indices = np.where(state > 0.5)[0]
            if len(active_indices) == 0: return 100.0
            
            energy = 0.0
            # Check connectivity of active nodes
            sub_A = A[np.ix_(active_indices, active_indices)]
            # If graph is disconnected, energy increases (hole in complex)
            # Simple connectivity check
            if len(active_indices) > 1:
                # Degree check
                degrees = sub_A.sum(axis=1)
                if np.any(degrees == 0):
                    energy += 1.0
            return energy

        base_energy = get_energy(initial_state)
        mfa_size = len(nodes) # Worst case
        
        # Sampling loop (Simulated)
        np.random.seed(42) # Deterministic
        attempts = 10
        current_state = initial_state.copy()
        
        for _ in range(attempts):
            # Flip a random bit
            idx = np.random.randint(0, len(nodes))
            current_state[idx] = 1.0 - current_state[idx]
            
            new_energy = get_energy(current_state)
            
            # If energy stays high (violation persists), keep the flip (shrinking)
            if new_energy >= base_energy * 0.9: # Threshold tau
                base_energy = new_energy
                # Count active
                mfa_size = int(np.sum(current_state > 0.5))
            else:
                # Revert
                current_state[idx] = 1.0 - current_state[idx]
                
        return max(1, mfa_size)

    def _dynamics_tracker(self, prompt: str, candidate: str, nodes: List[str], A: np.ndarray) -> float:
        """
        FRAME C: DYNAMICS TRACKER
        Models reasoning as a dynamical system.
        Uses Lyapunov-like stability analysis on the state trajectory.
        """
        if len(nodes) < 2:
            return 0.5 # Neutral stability
            
        N = len(nodes)
        # Initial state: presence of concepts in candidate
        s0 = np.array([1.0 if n[:5] in candidate.lower() else 0.0 for n in nodes])
        
        # Define dynamics: s(t+1) = A * s(t) (Propagation of truth)
        # Normalize A to be stochastic-ish for stability
        row_sums = A.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        W = A.astype(float) / row_sums
        
        # Simulate trajectory
        trajectory = [s0]
        s_curr = s0.copy()
        steps = 5
        for _ in range(steps):
            s_curr = W @ s_curr
            # Activation function (sigmoid-like clamp)
            s_curr = 1 / (1 + np.exp(-5 * (s_curr - 0.5)))
            trajectory.append(s_curr)
            
        # Calculate Convergence Rate (Lyapunov exponent approximation)
        # Distance between consecutive states
        diffs = []
        for i in range(1, len(trajectory)):
            dist = np.linalg.norm(trajectory[i] - trajectory[i-1])
            diffs.append(dist)
            
        if len(diffs) < 2:
            return 0.5
            
        # If diffs decrease rapidly, system is stable (high confidence)
        # If diffs oscillate or grow, unstable
        convergence_rate = np.mean(np.diff(diffs)) # Negative is good (converging)
        
        # Map to 0-1 score: Stable (negative diff) -> 1.0, Unstable -> 0.0
        # Heuristic mapping
        stability_score = 1.0 / (1.0 + np.exp(10 * convergence_rate))
        return float(stability_score)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Pre-parse prompt
        nodes, A, features = self._parse_predicates(prompt)
        
        # Check for meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Free Energy (Logical Consistency)
            energy = self._compute_free_energy(cand, nodes, A, features)
            
            # 2. Property Based Testing (Robustness)
            mfa_size = self._property_based_shrink(prompt, cand, nodes, A, features)
            
            # 3. Dynamics Stability (Frame C)
            stability = self._dynamics_tracker(prompt, cand, nodes, A)
            
            # 4. NCD (Tiebreaker, max 15% weight logic handled in scoring)
            ncd = self._ncd_score(prompt, cand)
            
            # Scoring Formula from Algorithm description + Dynamics integration
            # score = 1 / (1 + E) * exp(-|MFA|)
            # Modified to include Stability (Dynamics) and NCD cap
            base_score = (1.0 / (1.0 + energy)) * np.exp(-mfa_size * 0.5)
            
            # Combine: Structural/Computation (Energy/MFA) = 50%, Dynamics = 35%, NCD = 15%
            # Normalize NCD to be a positive contributor (1 - ncd)
            ncd_contrib = (1.0 - ncd) * 0.15
            
            # Weighted sum
            final_score = (base_score * 0.5) + (stability * 0.35) + ncd_contrib
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            if final_score > meta_cap:
                final_score = meta_cap
            
            # Generate reasoning string
            reason_parts = []
            if energy < 0.5: reason_parts.append("Low logical error")
            if stability > 0.7: reason_parts.append("Stable dynamics")
            if mfa_size < 3: reason_parts.append("Robust to perturbation")
            if meta_cap < 0.5: reason_parts.append("Ambiguous prompt detected")
            
            reasoning_str = "; ".join(reason_parts) if reason_parts else "Standard evaluation"

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning_str
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Meta Check (Crucial for Tier B)
        cap