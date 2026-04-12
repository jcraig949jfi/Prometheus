class ReasoningTool:
    """
    Ergodic-Nash-FreeEnergy reasoning evaluator with dynamics tracking.
    
    Combines:
    - Structural parsing (negations, comparatives, conditionals, causal, numeric, ordering)
    - Free Energy Principle belief updates with ergodic convergence
    - Nash equilibrium via replicator dynamics
    - Trajectory stability analysis for confidence estimation
    - Meta-confidence for epistemic honesty on ambiguous prompts
    """
    
    def __init__(self):
        self.epsilon = 1e-4
        self.max_iters = 50
        self.feature_patterns = {
            'negation': r'\b(not|no|never|neither|none|nothing|cannot|can\'t|won\'t|don\'t|doesn\'t|isn\'t)\b',
            'comparative': r'\b(more|less|greater|fewer|higher|lower|better|worse|larger|smaller|bigger|than)\b',
            'conditional': r'\bif\b.*\bthen\b|\bunless\b|\bwhen\b.*\bthen\b',
            'causal': r'\bbecause\b|\bleads? to\b|\bresults? in\b|\bcauses?\b|\bdue to\b',
            'numeric': r'\b\d+(\.\d+)?\b',
            'ordering': r'\bbefore\b|\bafter\b|\bfirst\b|\blast\b|\b>\b|\b<\b|\bearlier\b|\blater\b'
        }
    
    def _parse_propositions(self, text):
        """Extract propositions as (feature_type, predicate_string) tuples."""
        text_lower = text.lower()
        props = []
        sentences = re.split(r'[.!?;]', text)
        for sent in sentences:
            if len(sent.strip()) < 3:
                continue
            for feat_type, pattern in self.feature_patterns.items():
                if re.search(pattern, sent.lower()):
                    props.append((feat_type, sent.strip()))
        return props if props else [('null', text_lower[:50])]
    
    def _build_feature_matrix(self, propositions):
        """Build binary feature matrix F: P x K."""
        if not propositions:
            return np.zeros((1, len(self.feature_patterns)))
        P = len(propositions)
        K = len(self.feature_patterns)
        F = np.zeros((P, K))
        feat_names = list(self.feature_patterns.keys())
        for i, (feat_type, _) in enumerate(propositions):
            if feat_type in feat_names:
                F[i, feat_names.index(feat_type)] = 1
        return F
    
    def _free_energy_update(self, F, b0, weights):
        """Belief update via free energy minimization with ergodic averaging."""
        P = F.shape[0]
        b = b0.copy()
        trajectory = [b.copy()]
        
        for t in range(self.max_iters):
            likelihood = np.exp(F @ weights)
            likelihood = likelihood / (likelihood.sum() + 1e-10)
            log_b0 = np.log(b0 + 1e-10)
            log_L = np.log(likelihood + 1e-10)
            b_new = np.exp(log_b0 + log_L)
            b_new = b_new / (b_new.sum() + 1e-10)
            trajectory.append(b_new.copy())
            if np.linalg.norm(b_new - b, 1) < self.epsilon:
                break
            b = b_new
        
        # Ergodic average
        b_ergodic = np.mean(trajectory, axis=0)
        return b_ergodic, trajectory
    
    def _replicator_dynamics(self, belief, answer_vectors):
        """Nash equilibrium via replicator dynamics."""
        N = len(answer_vectors)
        p = np.ones(N) / N
        
        for t in range(self.max_iters):
            utilities = np.array([belief @ v for v in answer_vectors])
            mean_util = p @ utilities
            if mean_util < 1e-10:
                mean_util = 1e-10
            p_new = p * utilities / mean_util
            p_new = p_new / (p_new.sum() + 1e-10)
            if np.linalg.norm(p_new - p, 1) < self.epsilon:
                break
            p = p_new
        return p
    
    def _trajectory_stability(self, trajectory):
        """Compute stability metrics from belief trajectory."""
        if len(trajectory) < 2:
            return 0.5
        traj_array = np.array(trajectory)
        changes = np.diff(traj_array, axis=0)
        variance = np.mean(np.var(changes, axis=0))
        convergence_rate = 1.0 / (1.0 + len(trajectory))
        stability = np.exp(-variance * 10) * (1 - convergence_rate)
        return np.clip(stability, 0, 1)
    
    def _meta_confidence(self, prompt):
        """Check for epistemic traps that reduce confidence."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they|it)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', prompt_lower) and not re.search(r'\bother|else|also\b', prompt_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|favourite|prefer)\b', prompt_lower):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(impossible to|cannot determine|not enough|insufficient|ambiguous)\b', prompt_lower):
            return 0.2
        
        return 1.0
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by Ergodic-Nash-FreeEnergy scoring."""
        prompt_props = self._parse_propositions(prompt)
        F_prompt = self._build_feature_matrix(prompt_props)
        weights = np.ones(F_prompt.shape[1])
        b0 = np.ones(F_prompt.shape[0]) / F_prompt.shape[0]
        belief, trajectory = self._free_energy_update(F_prompt, b0, weights)
        
        answer_vectors = []
        for cand in candidates:
            cand_props = self._parse_propositions(cand)
            prop_indices = []
            for cp_type, cp_str in cand_props:
                for i, (pp_type, pp_str) in enumerate(prompt_props):
                    if cp_type == pp_type or cp_str.lower() in pp_str.lower():
                        prop_indices.append(i)
            vec = np.zeros(len(prompt_props))
            for idx in prop_indices:
                vec[idx] = 1
            answer_vectors.append(vec)
        
        nash_scores = self._replicator_dynamics(belief, answer_vectors)
        stability = self._trajectory_stability(trajectory)
        
        results = []
        for i, cand in enumerate(candidates):
            structural_score = nash_scores[i]
            ncd_score = 1 - self._ncd(prompt, cand)
            dynamics_score = stability * (answer_vectors[i] @ belief)
            
            final_score = 0.5 * dynamics_score + 0.35 * structural_score + 0.15 * ncd_score
            
            reasoning = f"Dynamics: {dynamics_score:.3f}, Structural: {structural_score:.3f}, NCD: {ncd_score:.3f}"
            results.append({"candidate": cand, "score": float(final_score), "reasoning": reasoning})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 with epistemic honesty."""
        meta_conf = self._meta_confidence(prompt)
        
        prompt_props = self._parse_propositions(prompt)
        answer_props = self._parse_propositions(answer)
        F_prompt = self._build_feature_matrix(prompt_props)
        weights = np.ones(F_prompt.shape[1])
        b0 = np.ones(F_prompt.shape[0]) / F_prompt.shape[0]
        belief, trajectory = self._free_energy_update(F_prompt, b0, weights)
        
        prop_indices = []
        for ap_type, ap_str in answer_props:
            for i, (pp_type, pp_str) in enumerate(prompt_props):
                if ap_type == pp_type or ap_str.lower() in pp_str.lower():
                    prop_indices.append(i)
        
        vec = np.zeros(len(prompt_props))
        for idx in prop_indices:
            vec[idx] = 1
        
        alignment = vec @ belief if len(prompt_props) > 0 else 0.5
        stability = self._trajectory_stability(trajectory)
        
        base_conf = 0.4 * alignment + 0.6 * stability
        final_conf = base_conf * meta_conf
        
        return float(np.clip(final_conf, 0, 0.95))