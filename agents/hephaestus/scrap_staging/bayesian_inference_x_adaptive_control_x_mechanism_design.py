class ReasoningTool:
    """
    A reasoning tool combining Bayesian Inference, Adaptive Control, and Mechanism Design.
    
    Mechanism:
    1. Feature Extraction: Parses prompt/candidates for negations, comparatives, conditionals,
       numerics, causal cues, and ordering.
    2. Bayesian Update: Treats candidates as hypotheses. Updates belief based on feature likelihoods.
    3. Adaptive Control: Adjusts feature weights online to minimize prediction error (simulated).
    4. Mechanism Design: Scores features based on proper scoring rules to incentivize 'truthful'
       evidence reporting (simulated via consistency checks).
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity, presuppositions,
       or unanswerable structures (Tier B reasoning).
    """

    def __init__(self):
        # Feature names corresponding to regex patterns
        self.feature_names = [
            "negation", "comparative", "conditional", "numeric", 
            "causal", "ordering", "conjunctive"
        ]
        self.n_features = len(self.feature_names)
        
        # Weights w (initialized to small random-ish values via hash of name to be deterministic)
        # Using a simple deterministic init: 0.1 * index - 0.1
        self.w = [0.1 * (i - 1) for i in range(self.n_features)]
        self.alpha = 0.05  # Learning rate
        
        # Regex patterns
        self.patterns = {
            "negation": re.compile(r'\b(not|no|never|neither|nobody|nothing|none|cannot|won\'t|don\'t|doesn\'t|didn\'t)\b', re.IGNORECASE),
            "comparative": re.compile(r'\b(more|less|greater|smaller|better|worse|higher|lower|than|<|>|<=|>=)\b', re.IGNORECASE),
            "conditional": re.compile(r'\b(if|then|unless|otherwise|provided|except)\b', re.IGNORECASE),
            "numeric": re.compile(r'\b(\d+(\.\d+)?|\$[\d,]+)\b'),
            "causal": re.compile(r'\b(because|therefore|thus|hence|leads to|results in|causes|due to)\b', re.IGNORECASE),
            "ordering": re.compile(r'\b(first|last|before|after|earliest|latest|previous|next|sequence)\b', re.IGNORECASE),
            "conjunctive": re.compile(r'\b(and|or|both|either|nor|but|yet)\b', re.IGNORECASE)
        }
        
        # Tier B Ambiguity Patterns
        self.presupposition_re = re.compile(r'\b(have you stopped|have you quit|why did .*(fail|stop|break)|when did .*(stop|fail))\b', re.IGNORECASE