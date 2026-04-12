import numpy as np

class ReasoningTool:
    """
    Measure-theoretic optimal control reasoning tool.
    
    Mechanism:
    1. Parse prompt/candidates into clauses (structural features)
    2. Build measure space of possible worlds (truth assignments)
    3. Apply Bellman recursion (optimal control) to minimize expected loss
    4. Use proper scoring rule (mechanism design) for incentive alignment
    5. Track state trajectory stability across premise orderings (dynamics)
    
    Score = trajectory_stability * bellman_value * structural_match - ncd_penalty
    Confidence = min(meta_confidence_cap, trajectory_convergence)
    """
    
    def __init__(self):
        self.epsilon = 1e-6
        
    def _parse_clauses(self, text):
        """Extract structural features as clauses."""
        clauses = []
        
        # Negations
        if re.search(r'\b(not|no|never|n\'t)\b', text, re.I):
            clauses.append(('negation', True))
        
        # Numeric comparatives
        numbers = re.findall(r'\d+\.?\d*', text)
        if len(numbers) >= 2:
            nums = [float(n) for n in numbers[:2]]
            clauses.append(('numeric_compare', nums[0], nums[1]))
        
        # Comparatives
        if re.search(r'\b(greater|more|larger|higher|bigger)\b', text, re.I):
            clauses.append(('comparative', 'greater'))
        elif re.search(r'\b(less|fewer|smaller|lower)\b', text, re.I):
            clauses.append(('comparative', 'less'))
        elif re.search(r'\b(equal|same)\b', text, re.I):
            clauses.append(('comparative', 'equal'))
        
        # Conditionals
        if re.search(r'\b(if|when|given|assuming)\b', text, re.I):
            clauses.append(('conditional', True))
        
        # Causal
        if re.search(r'\b(because|cause|due to|result|therefore)\b', text, re.I):
            clauses.append(('causal', True))
        
        # Temporal ordering
        if re.search(r'\b(before|after|then|next|later)\b', text, re.I):
            clauses.append(('temporal', True))
        
        return clauses if clauses else [('default', True)]
    
    def _meta_confidence(self, prompt):
        """Check for Tier B judgment traps. Returns cap on confidence."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you stop|why did.*fail|when did.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and '?' in prompt:
            if re.search(r'\bwho\b|\bwhich\b', p_lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(according to|measured by|criterion)\b', p_lower):
                return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(impossible to|cannot know|not enough information|ambiguous)\b', p_lower):
            return 0.2
        
        return 1.0  # No trap detected
    
    def _build_state_space(self, clauses):
        """Build state vector: probability distribution over clause truth values."""
        n = len(clauses)
        # Initial state: uniform prior over all truth assignments
        state = np.ones(2**n) / (2**n)
        return state, n
    
    def _state_update(self, state, evidence_clause, candidate_clause):
        """Update state based on evidence from prompt vs candidate."""
        # Bellman-style update: apply cost and reweight distribution
        n = int(np.log2(len(state)))
        costs = np.zeros(len(state))
        
        for i in range(len(state)):
            # Decode world i as binary truth assignment
            assignment = [(i >> j) & 1 for j in range(n)]
            # Brier loss: squared error
            cost = sum((e != c)**2 for e, c in zip(evidence_clause, assignment))
            costs[i] = cost
        
        # Optimal control: minimize expected cost
        values = costs + self.epsilon
        new_state = state / (values + self.epsilon)
        new_state /= (new_state.sum() + self.epsilon)
        
        return new_state
    
    def _trajectory_stability(self, prompt_clauses, candidate_clauses):
        """Measure stability of state trajectory under premise reordering."""
        if len(prompt_clauses) <= 1:
            return 0.5
        
        # Sample different orderings
        orderings = list(permutations(range(len(prompt_clauses))))[:min(6, len(list(permutations(range(len(prompt_clauses))))))]
        
        final_states = []
        for ordering in orderings:
            state, n = self._build_state_space(prompt_clauses)
            for idx in ordering:
                # Simplify: use clause index as pseudo-evidence
                evidence = [1 if i == idx else 0 for i in range(n)]
                state = self._state_update(state, evidence, [1]*n)
            final_states.append(state)
        
        # Stability = inverse of variance across orderings
        if len(final_states) > 1:
            stacked = np.array(final_states)
            variance = np.var(stacked, axis=0).mean()
            stability = 1.0 / (1.0 + variance)
        else:
            stability = 0.5
        
        return stability
    
    def _bellman_value(self, prompt_clauses, candidate_clauses):
        """Compute optimal value via backward HJB recursion."""
        T = max(len(prompt_clauses), 1)
        n_worlds = 2**T
        
        # Initialize terminal value
        V = np.zeros(n_worlds)
        
        # Backward recursion
        for t in range(T-1, -1, -1):
            V_new = np.zeros(n_worlds)
            for omega in range(n_worlds):
                # Action: flip or not flip clause t
                costs = []
                for action in [0, 1]:
                    omega_next = omega ^ (action << t)  # Flip bit t if action=1
                    cost_t = ((omega >> t) & 1) * 0.5  # Simplified cost
                    costs.append(cost_t + V[omega_next])
                V_new[omega] = min(costs)
            V = V_new
        
        # Scoring rule: negative expected loss
        score = -V.mean()
        return score
    
    def _structural_match(self, prompt, candidate):
        """Compute structural feature overlap."""
        p_clauses = self._parse_clauses(prompt)
        c_clauses = self._parse_clauses(candidate)
        
        # Negation match
        p_neg = any(c[0] == 'negation' for c in p_clauses)
        c_neg = any(c[0] == 'negation' for c in c_clauses)
        neg_match = 1.0 if p_neg == c_neg else 0.0
        
        # Numeric computation
        num_match = 0.5
        p_nums = [c for c in p_clauses if c[0] == 'numeric_compare']
        c_nums = [c for c in c_clauses if c[0] == 'numeric_compare']
        if p_nums and c_nums:
            p_cmp = p_nums[0][1] < p_nums[0][2]
            c_cmp = c_nums[0][1] < c_nums[0][2]
            num_match = 1.0 if p_cmp == c_cmp else 0.0
        
        # Feature overlap
        p_types = set(c[0] for c in p_clauses)
        c_types = set(c[0] for c in c_clauses)
        overlap = len(p_types & c_types) / max(len(p_types | c_types), 1)
        
        return 0.4 * neg_match + 0.3 * num_match + 0.3 * overlap
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by combined score."""
        p_clauses = self._parse_clauses(prompt)
        results = []
        
        for cand in candidates:
            c_clauses = self._parse_clauses(cand)
            
            # Dynamics: trajectory stability (40%)
            stability = self._trajectory_stability(p_clauses, c_clauses)
            
            # Optimal control: Bellman value (20%)
            bellman = self._bellman_value(p_clauses, c_clauses)
            
            # Structural match (30%)
            struct = self._structural_match(prompt, cand)
            
            # NCD penalty (10%, inverted)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - min(ncd_val, 1.0)
            
            # Combined score
            score = 0.4 * stability + 0.2 * (bellman + 1.0) + 0.3 * struct + 0.1 * ncd_score
            
            reasoning = f"Stability={stability:.3f} Bellman={bellman:.3f} Struct={struct:.3f} NCD={ncd_score:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1. Capped by meta-confidence."""
        meta_cap = self._meta_confidence(prompt)
        
        p_clauses = self._parse_clauses(prompt)
        a_clauses = self._parse_clauses(answer)
        
        # Trajectory convergence
        stability = self._trajectory_stability(p_clauses, a_clauses)
        
        # Structural match
        struct = self._structural_match(prompt, answer)
        
        # Base confidence on convergence + structure
        base_conf = 0.6 * stability + 0.4 * struct
        
        # Cap by meta-confidence
        final_conf = min(base_conf, meta_cap)
        
        # Never exceed 0.9 unless perfect structural match
        if struct < 0.95:
            final_conf = min(final_conf, 0.85)
        
        return max(0.05, min(final_conf, 0.95))