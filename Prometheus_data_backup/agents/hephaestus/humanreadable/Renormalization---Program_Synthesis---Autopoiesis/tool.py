class ReasoningTool:
    """
    Renormalizing Autopoietic Program Synthesizer (RAPS) - Structural Implementation
    
    Mechanism:
    1. Program Synthesis (Structural Parser): Instead of generating code, we parse the prompt
       into a set of logical constraints (negations, comparatives, conditionals). This acts as
       the "fine-scale" program proposal.
    2. Renormalization: We integrate out low-level token noise by mapping candidates to a
       binary feature vector based on the parsed constraints. The "distance" is measured in
       this coarse-grained logical space, not raw string space.
    3. Autopoiesis: The system maintains an internal "organizational closure" state (self-rules)
       that evolves slightly based on the success of constraint detection. If no constraints
       are found, it regenerates its parsing rules (simulated by widening regex patterns).
       
    Scoring:
    - Primary: Structural adherence (constraint satisfaction).
    - Secondary: NCD (only if structural scores are tied).
    """

    def __init__(self):
        # Autopoietic state: Rules that define how we parse logic
        self._rules = {
            'negation': [r'\bnot\b', r'\bnever\b', r'\bfalse\b', r'\bno\b'],
            'comparative': [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\b', r'\bsmaller\b', r'>', r'<'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly\s+if\b'],
            'numeric': r'\d+\.?\d*'
        }
        self._closure_state = 0.5  # Internal metric for rule strictness

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Parse text into logical features (The Program Synthesis Step)."""
        text_lower = text.lower()
        features = {
            'has_negation': False,
            'negation_count': 0,
            'has_comparative': False,
            'has_conditional': False,
            'numbers': [],
            'raw_len': len(text)
        }
        
        # Check negations
        for pattern in self._rules['negation']:
            if re.search(pattern, text_lower):
                features['has_negation'] = True
                features['negation_count'] += len(re.findall(pattern, text_lower))
        
        # Check comparatives
        for pattern in self._rules['comparative']:
            if re.search(pattern, text_lower):
                features['has_comparative'] = True
                break
                
        # Check conditionals
        for pattern in self._rules['conditional']:
            if re.search(pattern, text_lower):
                features['has_conditional'] = True
                break
                
        # Extract numbers
        nums = re.findall(self._rules['numeric'], text)
        features['numbers'] = [float(n) for n in nums]
        
        return features

    def _renormalize_distance(self, prompt_feats: Dict, cand_feats