from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Combines Theory of Mind, Causal Inference, and Free Energy Principle.
    Builds a two-layer DBN (world + ToM) with causal structure, computes variational
    free energy to score candidates. Includes constructive computation for numeric/
    probabilistic reasoning and epistemic honesty via meta-confidence checks.
    """
    
    def __init__(self):
        self.causal_cues = r'\b(because|causes?|leads? to|prevents?|if|then|unless|due to|results? in)\b'
        self.negation_cues = r'\b(not|no|never|neither|nor|without)\b'
        self.comparative_cues = r'\b(more|less|greater|fewer|higher|lower|twice|half|double)\s+than\b'
        self.temporal_cues = r'\b(before|after|while|during|until|since|when)\b'
        
    def _extract_propositions(self, text: str) -> List[str]:
        """Extract simple propositions from text."""
        sentences = re.split(r'[.!?;]', text.lower())
        props = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 5 and len(sent.split()) >= 2:
                props.append(sent)
        return props[:10]  # Limit for efficiency
    
    def _extract_causal_edges(self, props: List[str]) -> List[Tuple[int, int]]:
        """Extract causal edges between propositions."""
        edges = []
        for i, p1 in enumerate(props):
            if re.search(self.causal_cues, p1):
                for j, p2 in enumerate(props):
                    if i != j and any(w in p1 for w in p2.split()[:3]):
                        edges.append((i, j))
        return edges
    
    def _build_dbn(self, props: List[str], edges: List[Tuple[int, int]]) -> Tuple[np.ndarray, np.ndarray]:
        """Build DBN with world and ToM layers. Returns prior and CPT structure."""
        n = len(props)
        if n == 0:
            return np.array([0.5]), np.zeros((1, 1))
        
        priors = np.full(n * 2, 0.5)  # n world nodes + n ToM nodes
        adj = np.zeros((n * 2, n * 2))
        
        for i, j in edges:
            if i < n and j < n:
                adj[i, j] = 0.7
                adj[i + n, j + n] = 0.7  # Mirror in ToM layer
                adj[i, j + n] = 0.3  # Cross-layer influence
        
        return priors, adj
    
    def _compute_free_energy(self, priors: np.ndarray, posteriors: np.ndarray) -> float:
        """Compute variational free energy F = KL divergence."""
        eps = 1e-10
        priors = np.clip(priors, eps, 1 - eps)
        posteriors = np.clip(posteriors, eps, 1 - eps)
        
        kl = posteriors * np.log(posteriors / priors) + (1 - posteriors) * np.log((1 - posteriors) / (1 - priors))
        return np.sum(kl)
    
    def _update_beliefs(self, priors: np.ndarray, adj: np.ndarray, evidence: Dict[int, bool]) -> np.ndarray:
        """Simple belief propagation with evidence clamping."""
        beliefs = priors.copy()
        
        for idx, val in evidence.items():
            if idx < len(beliefs):
                beliefs[idx] = 0.95 if val else 0.05
        
        for _ in range(3):  # Belief propagation iterations
            new_beliefs = beliefs.copy()
            for i in range(len(beliefs)):
                if i not in evidence:
                    parents = np.where(adj[:, i] > 0)[0]
                    if len(parents) > 0:
                        influence = np.mean([beliefs[p] * adj[p, i] for p in parents])
                        new_beliefs[i] = 0.5 * beliefs[i] + 0.5 * influence
            beliefs = new_beliefs
        
        return beliefs
    
    def _compute_numeric(self, prompt: str, candidate: str) -> Tuple[float, bool]:
        """Constructive computation for numeric questions."""
        numbers_p = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        numbers_c = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if not numbers_c:
            return 0.0, False
        
        if re.search(r'\bgreater|more|higher|larger\b', prompt.lower()):
            if numbers_p and numbers_c[0] > max(numbers_p):
                return 0.8, True
        elif re.search(r'\bless|fewer|lower|smaller\b', prompt.lower()):
            if numbers_p and numbers_c[0] < min(numbers_p):
                return 0.8, True
        
        if len(numbers_p) >= 2 and len(numbers_c) >= 1:
            computed = numbers_p[0] + numbers_p[1] if '+' in prompt else numbers_p[0] * numbers_p[1]
            if abs(computed - numbers_c[0]) < 0.01:
                return 0.9, True
        
        return 0.0, False
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, and unanswerable questions."""
        p_lower = prompt.lower()
        
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop)|when did .* stop)\b', p_lower):
            return 0.2  # Presupposition
        
        if re.search(r'\bevery .* a \b', p_lower) and '?' in prompt:
            return 0.25  # Scope ambiguity
        
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25  # Pronoun ambiguity
        
        if re.search(r'\beither .* or\b', p_lower) and not re.search(r'\bonly|just\b', p_lower):
            return 0.3  # Possible false dichotomy
        
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p_lower) and not re.search(r'\bmeasured|according to\b', p_lower):
            return 0.3  # Subjectivity
        
        return 1.0  # No ambiguity detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker only."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using DBN + free energy + constructive computation."""
        props_p = self._extract_propositions(prompt)
        edges_p = self._extract_causal_edges(props_p)
        priors, adj = self._build_dbn(props_p, edges_p)
        
        results = []
        for cand in candidates:
            score = 0.0
            
            num_score, num_valid = self._compute_numeric(prompt, cand)
            if num_valid:
                score += num_score * 0.5
            
            props_c = self._extract_propositions(cand)
            evidence = {}
            for i, prop in enumerate(props_p[:len(priors) // 2]):
                for c_prop in props_c:
                    if len(set(prop.split()) & set(c_prop.split())) >= 2:
                        has_neg = bool(re.search(self.negation_cues, c_prop))
                        evidence[i] = not has_neg
            
            if len(priors) > 0:
                posteriors = self._update_beliefs(priors, adj, evidence)
                fe = self._compute_free_energy(priors, posteriors)
                fe_score = 1.0 / (1.0 + fe)
                score += fe_score * 0.35
            
            ncd_score = 1.0 - self._ncd(prompt, cand)
            score += ncd_score * 0.15
            
            reasoning = f"FE: {fe_score:.3f}, Num: {num_score:.3f}, NCD: {ncd_score:.3f}" if len(priors) > 0 else "Minimal structure"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence for ambiguous prompts."""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        num_score, num_valid = self._compute_numeric(prompt, answer)
        if num_valid:
            return min(0.85, num_score * meta_conf)
        
        props_p = self._extract_propositions(prompt)
        props_a = self._extract_propositions(answer)
        
        if len(props_p) == 0 or len(props_a) == 0:
            return 0.25 * meta_conf
        
        edges_p = self._extract_causal_edges(props_p)
        priors, adj = self._build_dbn(props_p, edges_p)
        
        evidence = {}
        for i, prop in enumerate(props_p[:len(priors) // 2]):
            for a_prop in props_a:
                if len(set(prop.split()) & set(a_prop.split())) >= 2:
                    has_neg = bool(re.search(self.negation_cues, a_prop))
                    evidence[i] = not has_neg
        
        posteriors = self._update_beliefs(priors, adj, evidence)
        fe = self._compute_free_energy(priors, posteriors)
        
        base_conf = 1.0 / (1.0 + fe) if len(priors) > 0 else 0.3
        return min(0.85, base_conf * meta_conf)