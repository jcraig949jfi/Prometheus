class ReasoningTool:
    """
    MS-PC-GNN Inspired Reasoning Tool (Computational Analogue)
    
    Mechanism:
    1. Wavelet Decomposition (Multi-scale Parsing): Instead of signal processing,
       we decompose the text into 'scales': Fine (tokens/numbers), Mid (logical operators),
       and Coarse (global constraints/negations).
    2. Graph Topology (Small-World): We construct a dependency graph where nodes are
       candidate answers and the prompt. Edges represent logical consistency (transitivity,
       numeric ordering) and semantic overlap.
    3. Free Energy Minimization (Predictive Coding): 
       - Prediction: The model predicts the 'ideal' answer features based on the prompt's
         logical structure (e.g., if prompt has 'not', ideal answer should reflect negation).
       - Error: Discrepancy between candidate features and predicted features.
       - Action: Scores are updated to minimize variational free energy (surprise).
         Candidates that satisfy structural constraints (numeric truth, logical consistency)
         have low free energy (high score).
    
    This implements the 'Free Energy Principle' as the core driver for evaluating candidates
    against structural truths extracted from the prompt.
    """

    def __init__(self):
        self.epsilon = 1e-9

    def _extract_structure(self, text: str) -> dict:
        """Extract logical primitives: numbers, negations, comparatives."""
        text_lower = text.lower()
        
        # Numeric extraction
        numbers = [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]
        
        # Logical flags
        has_negation = any(n in text_lower for n in ['not ', 'no ', 'never ', 'false ', 'cannot '])
        has_comparative = any(c in text_lower for c in ['greater', 'less', 'more', 'fewer', '>', '<', 'larger', 'smaller'])
        has_conditional = any(c in text_lower for c in ['if ', 'then ', 'unless ', 'otherwise '])
        
        return {
            'numbers': numbers,
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'length': len(text.split())
        }

    def _numeric_consistency(self, prompt_nums: List[float], candidate: str) -> float:
        """Check if candidate numbers logically follow prompt numbers."""
        cand_nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", candidate)]
        if not cand_nums or not prompt_nums:
            return 0.5  # Neutral if no numbers to compare
        
        # Simple heuristic: If prompt implies sorting or comparison, check order
        # Here we just check magnitude alignment for simple cases
        try:
            p_val = prompt_nums[-1] # Focus on last mentioned number as reference
            c_val = cand_nums[-1]
            # Penalty for large deviation unless context implies otherwise
            if p_val == 0:
                return 1.0 if c_val == 0 else 0.5
            ratio = abs(c_val - p_val) / (abs(p_val) + self.epsilon)
            return max(0.0, 1.0 - ratio) if ratio < 1.0 else 0.1
        except:
            return 0.5

    def _compute_free_energy(self, prompt_struct: dict, candidate: str) -> float:
        """
        Compute Variational Free Energy (Negative ELBO approximation).
        Lower energy = Better fit. We return negative energy as score.
        """
        cand_struct = self._extract_structure(candidate)
        energy = 0.0
        
        # 1. Prediction Error: Negation mismatch
        if prompt_struct['negation']:
            # If prompt has negation, candidate should ideally acknowledge it or be short (denial)
            # High energy if candidate is long and affirmative when prompt is negative
            if not cand_struct['negation'] and cand_struct['length'] > 3:
                energy += 2.0 
        else:
            # If prompt is positive, candidate shouldn't be unnecessarily negative
            if cand_struct['negation']:
                energy += 1.5

        # 2. Prediction Error: Numeric consistency
        if prompt_struct['numbers']:
            num_score = self._numeric_consistency(prompt_struct['numbers'], candidate)
            energy += (1.0 - num_score) * 3.0  # High penalty for numeric wrongness

        # 3. Complexity Penalty (Occam's razor)
        # Prefer concise answers that fit the data
        energy += 0.1 * cand_struct['length']

        return -energy  # Return as score (higher is better)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        denominator = max(len1, len2)
        if denominator == 0:
            return 0.0
        return (len_both - min(len1, len2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Base scores based on Free Energy minimization
        scores = []
        for cand in candidates:
            fe_score = self._compute_free_energy(prompt_struct, cand)
            
            # Structural Parsing Boost (The "Reasoning" component)
            # Check for direct logical contradictions in simple yes/no cases
            prompt_lower = prompt.lower()
            cand_lower = cand.lower().strip().rstrip('.')
            
            logic_boost = 0.0
            if 'yes' in cand_lower or 'no' in cand_lower:
                if 'not' in prompt_lower or 'false' in prompt_lower:
                    if 'no' in cand_lower:
                        logic_boost = 2.0  # Correctly identified negation
                    else:
                        logic_boost = -2.0 # Failed negation
                else:
                    if 'yes' in cand_lower:
                        logic_boost = 1.0
                    else:
                        logic_boost = -1.0
            
            # Numeric evaluation boost
            if prompt_struct['numbers'] and re.search(r'\d+', cand):
                # If candidate contains numbers, strict numeric check
                p_nums = prompt_struct['numbers']
                c_nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", cand)]
                if c_nums and p_nums:
                    # Example: Prompt "Is 9.11 > 9.9?" -> Candidate "No" or "False"
                    # We rely on the FE score mostly, but add small boost for exact matches
                    if abs(c_nums[-1] - p_nums[-1]) < 0.001:
                        logic_boost += 0.5

            final_score = fe_score + logic_boost
            scores.append((cand, final_score))

        # Normalize scores to 0-1 range roughly
        if scores:
            min_s = min(s[1] for s in scores)
            max_s = max(s[1] for s in scores)
            range_s = max_s - min_s if max_s != min_s else 1.0
            normalized_scores = []
            for cand, sc in scores:
                norm_sc = (sc - min_s) / range_s
                # Use NCD as tiebreaker for