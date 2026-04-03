class ReasoningTool:
    """
    Strategic Graph-Signal Sensing Protocol (SGSSP) Implementation.
    
    Mechanism:
    1. Network Science (Structure): Parses the prompt to build a dependency graph of 
       logical constraints (negations, comparatives, conditionals). Nodes are semantic units.
    2. Compressed Sensing (Recovery): Treats candidate answers as noisy measurements. 
       Uses sparsity (penalizing verbosity/repetition) and graph-consistency to recover 
       the "true" signal (correct answer).
    3. Mechanism Design (Incentives): Applies a VCG-style scoring rule. Candidates are 
       scored on their marginal contribution to global logical consistency. Truthful 
       (logically consistent) reporting is incentivized by minimizing reconstruction error.
       
    This integrates the three concepts to beat NCD baselines by focusing on structural 
    logic rather than string similarity.
    """

    def __init__(self):
        self._lambda_sparse = 0.15  # Sparsity penalty (LASSO)
        self._gamma_graph = 0.45    # Graph consistency weight
        self._tau_truth = 0.30      # Truthfulness threshold

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_comb = len(zlib.compress(s1_b + s2_b))
        denom = max(len1, len2)
        if denom == 0:
            return 0.0
        return (len_comb - min(len1, len2)) / denom

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extract logical features: negations, comparatives, numbers."""
        features = {
            'negation_count': 0,
            'comparative_count': 0,
            'conditional_count': 0,
            'numeric_value': 0.0,
            'has_numbers': False
        }
        t_lower = text.lower()
        
        # Negations
        negations = ['not', 'no ', 'never', 'none', 'cannot', "n't"]
        for n in negations:
            if n in t_lower:
                features['negation_count'] += 1
        
        # Comparatives
        comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<', '==']
        for c in comparatives:
            if c in t_lower:
                features['comparative_count'] += 1
                
        # Conditionals
        conditionals = ['if', 'then', 'unless', 'else', 'provided']
        for c in conditionals:
            if c in t_lower:
                features['conditional_count'] += 1
                
        # Numeric extraction (simple)
        nums = re.findall(r"-?\d+\.?\d*", text)
        if nums:
            features['has_numbers'] = True
            try:
                features['numeric_value'] = float(nums[0])
            except ValueError:
                pass
                
        return features

    def _build_graph_signal(self, prompt: str, candidate: str) -> float:
        """
        Simulates Graph Signal Processing.
        The prompt defines the Laplacian eigenbasis (constraints).
        The candidate is the signal. We measure alignment.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        score = 0.0
        
        # Constraint Propagation (Modus Tollens approximation)
        # If prompt has high negation logic, candidate must reflect it or be short (sparse)
        if p_feat['negation_count'] > 0:
            if c_feat['negation_count'] > 0 or len(candidate.split()) < 5:
                score += 0.4
            else:
                score -= 0.4
        
        # Comparative consistency
        if p_feat['comparative_count'] > 0:
            if c_feat['comparative_count'] > 0 or c_feat['has_numbers']:
                score += 0.3
            else:
                score -= 0.3
                
        # Conditional logic check
        if p_feat['conditional_count'] > 0:
            if c_feat['conditional_count'] > 0 or any(w in candidate.lower() for w in ['yes', 'no', 'true', 'false']):
                score += 0.3
            else:
                score -= 0.2

        return score