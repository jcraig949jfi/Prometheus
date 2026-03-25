class ReasoningTool:
    """
    Active Inference Model Predictive Controller (AI-MPC) for Reasoning.
    
    Mechanism:
    1. Generative Model (Perception): Parses the prompt to extract structural constraints
       (negations, comparatives, conditionals, numeric values). This forms the 'prior' belief.
    2. Variational Inference (Feedback): Evaluates candidates against these constraints.
       Mismatches generate 'prediction errors' (free energy).
    3. Optimal Control (Action): Selects the candidate minimizing expected free energy.
       - Structural adherence is the primary cost (extrinsic reward).
       - Precision weighting adjusts scores based on constraint confidence.
    4. Epistemic Drive: Candidates that resolve ambiguities or fit complex logical structures
       receive higher precision bonuses.
       
    Note: Per causal analysis, 'Optimal Control' math is restricted to the confidence wrapper
    and structural scoring logic, while 'Free Energy' drives the core evaluation loop.
    """

    def __init__(self):
        # Structural patterns for the generative model
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bwithout\b', r'\bexcept\b']
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', r'\bsmaller\s+than\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b']
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> dict:
        """Perceptual loop: Extracts hidden states (constraints) from observations (text)."""
        text_lower = text.lower()
        has_negation = any(re.search(p, text_lower) for p in self.negation_patterns)
        has_comparative = any(re.search(p, text_lower) for p in self.comparative_patterns)
        has_conditional = any(re.search(p, text_lower) for p in self.conditional_patterns)
        numbers = [float(n) for n in re.findall(self.number_pattern, text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text.split())
        }

    def _compute_prediction_error(self, prompt_struct: dict, candidate: str) -> float:
        """
        Calculates Free Energy (F) as prediction error.
        F = Sum of weighted mismatches between prompt constraints and candidate properties.
        Lower F = Better candidate.
        """
        error = 0.0
        cand_lower = candidate.lower()
        
        # 1. Negation Consistency Check
        # If prompt has negation, valid answers often contain specific negation markers or logical opposites
        # Here we penalize if the candidate blindly echoes the prompt without logical flip (simplified heuristic)
        if prompt_struct['negation']:
            # Heuristic: If prompt says "not", candidate shouldn't just be a substring match of the prompt
            if cand_lower in prompt_struct.get('raw_prompt', '').lower():
                error += 2.0 
        
        # 2. Numeric Consistency (The strongest signal)
        if prompt_struct['numbers']:
            cand_nums = [float(n) for n in re.findall(self.number_pattern, candidate)]
            if cand_nums:
                # Check if candidate numbers contradict prompt logic (simplified to presence/absence for robustness)
                # If prompt has numbers and candidate has none, high error
                if len(cand_nums) == 0 and len(prompt_struct['numbers']) > 0:
                     # Only penalize if the prompt actually requires a number (heuristic: prompt has > 1 number or comparative)
                    if prompt_struct['comparative'] or len(prompt_struct['numbers']) > 1:
                        error += 5.0
            else:
                # Candidate lacks numbers when prompt implies calculation/comparison
                if prompt_struct['comparative']:
                    error += 3.0

        # 3. Structural Complexity Match
        # If prompt is conditional, simple yes/no might be insufficient (epistemic penalty)
        if prompt_struct['conditional']:
            if cand_lower.strip() in ['yes', 'no', 'true', 'false']:
                error += 1.5 # Penalize oversimplification of conditional logic
        
        return error

    def