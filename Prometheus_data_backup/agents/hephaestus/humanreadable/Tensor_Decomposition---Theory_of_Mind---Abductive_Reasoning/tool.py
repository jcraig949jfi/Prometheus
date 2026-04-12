class ReasoningTool:
    """
    Belief-Tensor Abduction Scorer (BTAS) Implementation.
    
    Mechanism:
    1. Meta-Confidence (Epistemic Honesty): Analyzes prompt for presuppositions, 
       ambiguities, and false dichotomies. Caps confidence if detected.
    2. Structural Parsing: Extracts entities, relations, negations, and numbers 
       into a 5D tensor space (Entity, Relation, Polarity, Modality, Numeric).
    3. Abductive Scoring: Constructs a Ground Truth tensor (G) from the prompt 
       and Observation tensors (O) from candidates. Uses low-rank CP decomposition 
       logic (approximated via residual minimization for stability) to measure 
       how well the candidate explains the prompt's constraints.
    4. Hybrid Score: Combines structural residual error (50%), computational 
       verification (35%), and NCD tie-breaking (15%).
    """

    def __init__(self):
        self.alpha = 0.5  # Weight for residual error
        self.beta = 0.3   # Weight for belief consistency
        self.vocab_size = 50 # Simplified vocab hashing
        
        # Presupposition triggers
        self.presup_triggers = [
            r"\b(stopped|quit|ceased)\s+(doing\s+)?", 
            r"\bwhy\s+(did|does|is)\s+\w+\s+(fail|stop|wrong)",
            r"\bwhen\s+did\s+\w+\s+(stop|fail)"
        ]
        # Ambiguity triggers
        self.ambig_triggers = [r"\b(every|all)\s+\w+\s+.*\s+a\s+\w+", r"\bwho\s+is\s+(he|she|it)\b"]
        # False dichotomy
        self.dichotomy_triggers = [r"\beither\s+.*\s+or\s+", r"\bis\s+it\s+.*\s+or\s+.*\?"]

    def _hash_word(self, word: str) -> int:
        """Simple hash to map words to tensor indices."""
        return hash(word.lower()) % self.vocab_size

    def _parse_structural(self, text: str) -> Dict:
        """Extract structural features: negations, numbers, comparatives."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'entities': list(set(re.findall(r'\b[A-Z][a-z]+\b', text))) # Simple proper noun heuristic
        }
        return features

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value. If 1.0, no issues detected.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.presup_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # 2. Scope/Pronoun Ambiguity
        for pattern in self.ambig_triggers:
            if re.search(pattern, p_lower):
                # Only flag if question asks "who" or implies ambiguity resolution
                if "who" in p_lower or "which one" in p_lower:
                    return 0.25

        # 3. False Dichotomy
        for pattern in self.dichotomy_triggers:
            if re.search(pattern, p_lower):
                # Check if options are exhaustive (hard to detect, so be conservative)
                if "only" not in p_lower:
                    return 0.4 # Slightly higher than presupposition but still low

        # 4. Subjectivity
        if re.search(r'\b(best|worst|favorite|beautiful)\b', p_lower) and "calculate" not in p_lower:
            return 0.3

        return 1.0

    def _compute_numeric_truth(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Solves simple math/comparisons explicitly.
        Returns 1.0 if correct, 0.0 if wrong, 0.5 if not applicable.
        """
        # Extract numbers from prompt
        nums_prompt = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt)]
        nums_cand = [float(x) for x in re.findall(r'-?\d+\.?\d*', candidate)]
        
        # Case 1: Direct Comparison (e.g., "Is 9.11 > 9.9?")
        if len(nums_prompt) >= 2 and len(nums_cand) == 0:
            # Check for Yes/No in candidate
            cand_lower = candidate.lower()
            is_yes = 'yes' in cand_lower
            is_no = 'no' in cand_lower
            
            if '>' in prompt or 'greater' in prompt:
                expected = nums_prompt[0] > nums_prompt[1]
            elif '<' in prompt or 'less' in prompt:
                expected = nums_prompt[0] < nums_prompt[1]
            else:
                return 0.5 # Cannot determine operation
            
            if is_yes and expected: return 1.0
            if is_no and not expected: return 1.0
            if is_yes and not expected: return 0.0
            if is_no and expected: return 0.0
            
        # Case 2: Arithmetic verification (Simple sum check)
        if len(nums_prompt) >= 2 and len(nums_cand) == 1:
            # Heuristic: if prompt has two numbers and candidate has one, 
            # check if candidate is sum/diff/prod
            a, b = nums_prompt[0], nums_prompt[1]
            c = nums_cand[0]
            ops = [a+b, a-b, b-a, a*b]