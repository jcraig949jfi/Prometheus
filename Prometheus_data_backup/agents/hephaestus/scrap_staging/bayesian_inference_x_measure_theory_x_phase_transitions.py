class ReasoningTool:
    """
    Measure-Theoretic Bayesian RG Inference Engine (Computational Analogue).
    
    Mechanism:
    1. Structural Parsing (The Measure Space): Extracts logical operators (negations,
       comparatives, conditionals) and numeric values to define the observable space.
    2. RG Flow (Coarse-Graining): Treats the prompt as a high-resolution configuration.
       Candidates are evaluated by how well they preserve the "mass" of logical constraints
       when projected onto the answer space.
    3. Phase Transition Detection (Susceptibility): Computes a 'susceptibility' score based
       on the variance between structural adherence and semantic overlap. A high variance
       (critical slowing down analogue) indicates the candidate is unstable/incompatible
       with the prompt's logical structure (model mismatch).
    4. Scoring: Candidates are ranked by structural consistency (primary) and NCD (tiebreaker).
    """

    def __init__(self):
        self._logic_ops = ['if', 'then', 'else', 'unless', 'but', 'however', 'therefore']
        self._comparators = ['>', '<', '>=', '<=', '==', '!=', 'greater', 'less', 'equal']
        self._negations = ['not', 'no', 'never', 'none', 'false', 'impossible']

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical skeleton: negations, comparators, numbers, and logic flow."""
        lower_text = text.lower()
        tokens = re.findall(r'\b\w+\b', lower_text)
        
        # Count logical operators
        neg_count = sum(1 for t in tokens if t in self._negations)
        logic_count = sum(1 for t in tokens if t in self._logic_ops)
        comp_count = sum(len(re.findall(r'|'.join(re.escape(c) for c in self._comparators), lower_text)))
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = [float(n) for n in numbers]
        
        # Simple numeric constraint check (e.g., "is 5 greater than 3?")
        numeric_valid = True
        if len(nums) >= 2:
            # Heuristic: if prompt asks comparison, check if answer implies correct order
            # Since we don't know the question type, we just flag presence for now
            pass
            
        return {
            "negations": neg_count,
            "logic_ops": logic_count,
            "comparators": comp_count,
            "numbers": nums,
            "length": len(text),
            "word_set": set(tokens)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        b1 = zlib.compress(s1.encode('utf-8'))
        b2 = zlib.compress(s2.encode('utf-8'))
        b12 = zlib.compress((s1 + s2).encode('utf-8'))
        
        len1 = len(b1)
        len2 = len(b2)
        len12 = len(b12)
        
        if min(len1, len2) == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def _calculate_susceptibility(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Calculate 'susceptibility' (variance) between prompt and candidate structures.
        High susceptibility = Phase transition detected (Model mismatch).
        Low susceptibility = Stable inference.
        """
        # 1. Logical Consistency Check (Coarse-grained Hamiltonian)
        # If prompt has negation, candidate should ideally reflect it (simplified heuristic)
        logic_diff = abs(prompt_struct['logic_ops'] - cand_struct['logic_ops'])
        neg_diff = abs(prompt_struct['negations'] - cand_struct['negations'])
        
        # 2. Numeric Consistency
        num_diff = 0
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # Check if relative order is preserved (very basic)
            p_nums = sorted(prompt_struct['numbers'])
            c_nums = sorted(cand_struct['numbers'])
            # Just checking magnitude similarity for now as proxy
            if len(p_nums) > 0 and len(c_nums) > 0:
                num_diff = abs(p_nums[0] - c_nums[0]) / (abs(p_nums[0]) + 1e-6)
        
        # 3. Variance (Susceptibility)
        # We treat the difference in logical density as the 'energy' fluctuation
        variance = (logic_diff ** 2) + (2 * neg_diff ** 2) + (0.5 * num_diff ** 2)
        
        # Normalize roughly
        susceptibility = math.sqrt(variance) / (len(prompt_struct['word_set']) + 1e-6)
        
        return susceptibility

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt complexity for normalization
        prompt_complexity = prompt_struct['logic_ops'] + prompt_struct['negations'] + 1
        
        scores = []
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # Primary Signal: Structural Parsing & Constraint Propagation
            # Does the candidate respect the logical density and negation of the prompt?
            susceptibility = self._calculate_susceptibility(prompt_struct, cand_struct, prompt, cand)
            
            # Invert susceptibility: Lower susceptibility (stable flow) = Higher score
            # Add small epsilon to avoid division by zero
            structural_score = 1.0 / (1.0 + susceptibility * 10)
            
            # Boost if logical operators match presence (e.g. if prompt has 'if', answer might need logic)
            logic_bonus = 0.0
            if prompt_struct['logic_ops'] > 0 and cand_struct['logic_ops'] > 0:
                logic_bonus = 0.1
            if prompt_struct['negations'] > 0 and cand_struct['negations'] > 0:
                logic_bonus += 0.1
                
            final_score = min(1.0, structural_score + logic_bonus)
            
            scores.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Susceptibility: {susceptibility:.4f}, Logic Match: {logic_bonus:.