class ReasoningTool:
    """
    A reasoning evaluator combining Sparse Autoencoders, Falsificationism, and Kolmogorov Complexity.
    
    Mechanism:
    1. Feature Extraction: Parses sentences into binary vectors representing logical primitives 
       (negation, comparatives, conditionals, causality, ordering, numbers, quantifiers, connectives).
    2. Sparse Coding (SAE): Uses a fixed, over-complete dictionary of logical 'atoms'. Candidates 
       are encoded via Orthogonal Matching Pursuit (OMP) to find sparse representations.
    3. Kolmogorov Approximation: Scores candidates by Description Length (L). Lower L implies 
       the candidate fits the prompt's logical structure more naturally (higher probability).
    4. Falsification: Explicitly checks if the difference between Prompt and Candidate involves 
       minimal 'polarity flips' (negations). Easy-to-falsify statements get a bonus.
    5. Scoring: Final Score = -(Description Length + alpha * Falsifiability). 
       NCD is used only as a tiebreaker when structural signals are weak.
    """

    def __init__(self):
        # Define regex patterns for structural primitives (Order matters for index mapping)
        self.patterns = [
            r'\b(not|no|never|neither|nobody|nothing)\b',          # 0: Negation
            r'(>|<|=|!=|<=|>=|greater|less|equal)',                # 1: Comparatives
            r'\b(if|then|unless|otherwise)\b',                     # 2: Conditional
            r'\b(because|therefore|thus|hence|leads to)\b',        # 3: Causal
            r'\b(before|after|while|during|prior)\b',              # 4: Ordering/Temporal
            r'\b\d+(\.\d+)?\b',                                    # 5: Numeric
            r'\b(all|some|none|every|any|most)\b',                 # 6: Quantifiers
            r'\b(and|or|but|yet|so)\b',                            # 7: Connectives
            r'[,.:;?!]',                                           # 8: Punctuation/Clauses
        ]
        self.m = len(self.patterns)
        self.k = self.m * 2  # Over-complete dictionary size
        
        # Initialize a deterministic pseudo-dictionary D (k x m)
        # In a real training scenario, this would be learned via OMP on a corpus.
        # Here, we synthesize atoms that represent single features and simple combinations.
        np.random.seed(42)
        self.D = np.zeros((self.k, self.m))
        
        # Atoms 0..m-1: Unit vectors (single features)
        for i in range(self.m):
            self.D[i, i] = 1.0
            
        # Atoms m..2m-1: Negative unit vectors (representing absence or inverse logic)
        for i in range(self.m):
            self.D[self.m + i, i] = -1.0
            
        self.lambda_reg = 0.1
        self.alpha = 0.5  # Weight for falsification
        self.sigma_sq = 0.1  # Noise variance for MDL

    def _extract_features(self, text: str) -> np.ndarray:
        """Convert text to binary feature vector x."""
        text_lower = text.lower()
        x = np.zeros(self.m)
        for i, pattern in enumerate(self.patterns):
            if re.search(pattern, text_lower):
                x[i] = 1.0
        return x

    def _omp(self, x: np.ndarray, max_iter: int = 5) -> np.ndarray:
        """
        Orthogonal Matching Pursuit to solve min ||x - Da||^2 + lambda||a||_1.
        Returns sparse code 'a'.
        """
        residual = x.copy()
        indices = []
        a = np.zeros(self.k)
        
        for _ in range(max_iter):
            # Correlation
            corr = np.abs(np.dot(self.D, residual))
            # Mask already selected
            for idx in indices:
                corr[idx] = -1
            
            if np.max(corr) <= 1e-9:
                break
                
            idx = int(np.argmax(corr))
            indices.append(idx)
            
            # Least squares solution for selected atoms
            D_sub = self.D[:, indices]
            # Solve (D_sub^T D_sub) a_sub = D_sub^T x
            try:
                a_sub, _, _, _ = np.linalg.lstsq(D_sub, x, rcond=None)
            except np.linalg.LinAlgError:
                break
                
            # Update residual
            approx = np.dot(D_sub, a_sub)
            residual = x - approx
            
            # Early stop if residual is small
            if np.linalg.norm(residual) < 1e-6:
                break

        # Populate full sparse vector
        if len(indices) > 0:
            D_sub = self.D[:, indices]
            try:
                a_sub, _, _, _ = np.linalg.lstsq(D_sub, x, rcond=None)
                for i, idx in enumerate