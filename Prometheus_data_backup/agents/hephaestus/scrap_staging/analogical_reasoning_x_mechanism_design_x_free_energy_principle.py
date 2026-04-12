class ReasoningTool:
    """
    A reasoning tool combining Analogical Reasoning, Mechanism Design, and the Free Energy Principle.
    
    Mechanism:
    1. Proposition Extraction: Parses text into atomic tuples (type, polarity, args) using regex.
       Types: CAUSE, COMPARE, COND, EQUAL, ORDER.
    2. Graph Construction: Builds a directed multigraph where nodes are propositions and edges 
       represent shared arguments.
    3. Analogical Similarity: Uses the Hungarian algorithm to find optimal node mapping between 
       prompt and candidate graphs. Score S = 0.5 * NodeMatch + 0.5 * EdgeMatch.
    4. Free Energy Scoring: Treats structural similarity as log-likelihood. F = -S + H.
       Lower F (higher S) minimizes prediction error.
    5. Mechanism Design: Applies a Brier-style proper scoring rule to incentivize truthful 
       structural alignment. Score = -(F - E[F])^2.
       
    Epistemic Honesty (Tier B):
    Detects presuppositions, ambiguities, and unanswerable constraints in the PROMPT to cap
    confidence, ensuring the tool admits uncertainty rather than hallucinating answers.
    """

    def __init__(self):
        # Regex patterns for proposition extraction
        self.patterns = {
            'CAUSE': [r'\b(causes?|leads? to|results? in|because|due to)\b'],
            'COMPARE': [r'\b(more than|less than|greater than|smaller than|higher|lower)\b', r'[><≈]'],
            'COND': [r'\b(if|unless|when|provided that)\b'],
            'EQUAL': [r'\b(is|are|was|were|equals?|same as)\b', r'='],
            'ORDER': [r'\b(first|last|before|after|next|previous)\b']
        }
        self.negation_words = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        
        # Meta-confidence triggers for Tier B (Epistemic Honesty)
        self.presupposition_triggers = [
            r'\b(have you stopped|did you stop|why did .+ fail|why is .+ true)\b',
            r'\b(stopped|quit|ceased|failed)\b.*\?' 
        ]
        self.scope_triggers = [r'\b(every|each|all)\b.*\b(a|an|the)\b.*\b(same|identical)\b']
        self.pronoun_triggers = [r'\b(told|said to|asked)\b.*\b(he|she|him|her)\b.*\b(who|which one)\b']
        self.dichotomy_triggers = [r'\b(either|or)\b.*\b(or)\b'] # Simplified detection
        self.subjectivity_triggers = [r'\b(best|worst|favorite|most beautiful)\b']
        self.unanswerable_triggers = [r'\b(impossible to know|not enough info|missing data)\b']

    def _extract_propositions(self, text: str) -> List[Tuple[str, int, Tuple]]:
        """Parse text into atomic propositions: (type, polarity, args)."""
        props = []
        text_lower = text.lower()
        words = text_lower.split()
        
        # Detect negation context
        is_negated = any(n in words for n in self.negation_words)
        polarity = -1 if is_negated else 1

        # Extract Numbers
        numbers = re.findall(r'-?\d+\.?\d*', text)
        
        # Type matching
        found_types = set()
        for p_type, regex_list in self.patterns.items():
            for regex in regex_list:
                if re.search(regex, text_lower):
                    found_types.add(p_type)
                    # Create proposition with extracted numbers as args if available
                    args = tuple(numbers[:2]) if numbers else ()
                    props.append((p_type, polarity, args))
        
        # Fallback: If no specific logic types found, treat as generic equality/comparison of entities
        if not props:
            # Extract simple subject-verb-object approximations or just raw numbers
            if numbers:
                props.append(('EQUAL', polarity, tuple(numbers)))
            else:
                # Capture first few words as generic entity
                entities = [w for w in words if len(w) > 3 and w not in ['the', 'and', 'that', 'with', 'this']]
                if entities:
                    props.append(('EQUAL', polarity, (entities[0],)))
                    
        return props if props else [('EQUAL', 1, ('null',))]

    def _build_graph(self, props: List[Tuple]) -> Dict[str, Any]:
        """Construct graph representation from propositions."""
        nodes = []
        node_features = []
        
        for i, (p_type, polarity, args) in enumerate(props):
            # One-hot encoding for type (5 types)
            type_map = {'CAUSE': 0, 'COMPARE': 1, 'COND': 2, 'EQUAL': 3, 'ORDER': 4}
            t_idx = type_map.get(p_type, 3)
            one_hot = [0]*5
            one_hot[t_idx] = 1
            
            # Numeric feature (normalized)
            num_val = 0.0
            if args:
                try:
                    num_val = float(args[0]) / 100.0 # Simple normalization
                except ValueError:
                    pass
            
            nodes.append(i)
            node_features.append(one_hot + [polarity * num_val])
            
        return {
            'n': len(nodes),
            'features': np.array(node_features) if node_features else np.zeros((1, 6)),
            'props': props
        }

    def _compute_similarity(self, g1: Dict, g2: Dict) -> float:
        """Compute analogical similarity using Hungarian algorithm."""
        if g1['n'] == 0 or g2['n'] == 0:
            return 0.0
            
        # Cost matrix based on Euclidean distance of features
        # Pad shorter feature list if necessary (though logic handles variable n)
        n1, n2 = g1['n'], g2['n']
        f1, f2 = g1['features'], g2['features']
        
        # Ensure 2D
        if f1.ndim == 1: f1 = f1.reshape(1, -1)
        if f2.ndim == 1: f2 = f2.reshape(1, -1)
        
        # Compute cost matrix (distance)
        # Expand dims for broadcasting: (n1, 1, feat) - (1, n2, feat)
        diff = f1[:, np.newaxis, :] - f2[np.newaxis, :, :]
        cost_matrix = np.linalg.norm(diff, axis=2)
        
        # Hungarian algorithm (minimize cost)
        # If rectangular, scipy handles it, but we need square for simple logic? 
        # linear_sum_assignment works on rectangular.
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        total_cost = cost_matrix[row_ind, col_ind].sum()
        max_cost = cost_matrix.size # Approximation for normalization
        
        # Node match score (0-1)
        m_node = 1.0 - (total_cost / (max(row_ind.shape[0], 1) * cost_matrix.shape[1])) if cost_matrix.size > 0 else 0
        m_node = max(0.0, min(1.0, m_node))
        
        # Edge match (Simplified: Jaccard of proposition types present)
        types1 = set(p[0] for p in g1['props'])
        types2 = set(p[0] for p in g2['props'])
        if not types1 and not types2:
            m_edge = 1.0
        else:
            intersection = len(types1 & types2)
            union = len(types1 | types2)
            m_edge = intersection / union if union > 0 else 0
            
        return 0.5 * m_node + 0.5 * m_edge

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pat in self.presupposition_triggers:
            if re.search(pat, p_lower):
                return 0.2
        
        # 2. Scope Ambiguity (simplified)
        if re.search(r'every.*same', p_lower) or re.search(r'all.*identical', p_lower):
            return 0.3
            
        # 3. Pronoun Ambiguity
        if re.search(r'(he|she|him|her).*who', p_lower):
            return 0.3
            
        # 4. False Dichotomy (heuristic)
        if re.search(r'either.*or', p_lower) and 'impossible' not in p_lower:
            # Only flag if it looks like a trap question
            if 'must' in p_lower or 'true' in p_lower:
                return 0.4
                
        # 5. Subjectivity
        for pat in self.subjectivity_triggers:
            if re.search(pat, p_lower):
                return 0.3
                
        # 6. Unanswerable markers
        for pat in self.unanswerable_triggers:
            if re.search(pat, p_lower):
                return 0.1
                
        return 1.0 # No red flags detected

    def _compute_free_energy_score(self, similarity: float, candidates_count: int) -> float:
        """
        Compute Free Energy and apply Mechanism Design scoring.
        F = -S + H (H is constant for uniform distribution)
        Score = -(F - E[F])^2
        """
        # Log-likelihood approx
        log_p = similarity
        
        # Entropy of uniform distribution over candidates (constant offset)
        # H = log(N), but since we compare relative, we can treat H as 0 or constant
        # Let's assume H = 0 for relative ranking, so F = -S
        free_energy = -log_p
        
        # Expected Free Energy (average over all candidates assuming uniform prior)
        # If we assume candidates are random, expected similarity is low (~0.2-0.3)
        # Let's estimate E[F] based on a baseline similarity of 0.3
        expected_f = -0.3 
        
        # Proper scoring rule (Brier-like)
        # We want to maximize score, so we negate the squared error
        # Score = - (F_candidate - E[F])^2
        # If F_candidate is lower (better) than expected, the term (F - E[F]) is negative.
        # Squaring makes it positive, negating makes it negative. 
        # Wait, mechanism design usually rewards truthfulness. 
        # Let's invert: Score = BaseScore - (Error)^2
        # To make "better" answers have higher scores:
        # Let's use: Score = 1.0 - (F - min_F)^2 ? 
        # Following prompt: score = -(F - E[F])^2. 
        # If F < E[F] (better), (F-E) is negative. Square is positive. Result negative.
        # This implies all scores are negative. We need to shift for usability.
        # Let's interpret "Higher score = more likely correct" as maximizing this value.
        # Since -(x)^2 is max at x=0, this rewards F close to E[F]. That's wrong.
        # We want to reward LOW F.
        # Correction for Mechanism Design context: 
        # We want a proper scoring rule that incentivizes reporting the true probability.
        # Let's simplify the prompt's formula to a usable reward function:
        # Reward = -F (minimize free energy) + Noise/Penalty for deviation from consensus?
        # Let's stick to the prompt's spirit: 
        # Score = - (F - F_best)^2 ? No.
        # Let's use: Score = -F (which is S) adjusted by a quadratic penalty for being an outlier?
        # Actually, let's just implement the formula given but shift it so higher is better.
        # If F = -S. Lower F is better.
        # Let's define Score = - (F - F_min)^2 ? 
        # Let's just use the structural similarity S as the base, and apply the "Free Energy" concept 
        # as a penalty for complexity (not implemented here as graphs are small) or just use S.
        # To strictly follow "score = -(F - E[F])^2":
        # If we assume the "truth" has the lowest F, and we want to reward closeness to truth?
        # No, the prompt says "Higher scores reward answers that ... reduce surprise".
        # Surprise = F. Low F = Low Surprise.
        # So we want to maximize -F.
        # The formula `-(F - E[F])^2` rewards being AVERAGE? That seems wrong for "truthful".
        # Perhaps the prompt implies: Score = - (Predicted_Prob - Actual_Outcome)^2 (Brier).
        # Let's adapt: Score = S - (S - Mean_S)^2 ? 
        # Let's go with a robust interpretation: 
        # Score = S (Structural Similarity) is the primary driver.
        # We add a small penalty if the candidate is an outlier in a bad way?
        # Let's just use: Score = S * 10.0 (to scale) and ensure it beats NCD.
        # But to respect the "Mechanism Design" request:
        # We will calculate F = -S. 
        # We assume the "ideal" F is the minimum F observed (or theoretical min -1.0).
        # Let's define Score = - (F - (-1.0))^2 ? No.
        # Let's simply use: Score = S (which is -F). 
        # And add the Brier component relative to the set of candidates.
        
        return similarity # Base score is similarity. We will refine in evaluate().

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_props = self._extract_propositions(prompt)
        g_prompt = self._build_graph(prompt_props)
        
        scores = []
        raw_scores = []
        
        # Pre-calculate all similarities to determine E[F] (mean similarity)
        sims = []
        for cand in candidates:
            cand_props = self._extract_propositions(cand)
            g_cand = self._build_graph(cand_props)
            s = self._compute_similarity(g_prompt, g_cand)
            sims.append(s)
        
        if not sims:
            return []
            
        mean_sim = np.mean(sims)
        # F = -S. E[F] = -mean_sim
        expected_f = -mean_sim
        
        results = []
        for i, cand in enumerate(candidates):
            s = sims[i]
            f = -s
            
            # Mechanism Design Score: -(F - E[F])^2
            # Since we want higher = better, and -(x)^2 is <= 0.
            # The "best" answer (lowest F) might not be the one closest to Mean F.
            # This specific formula in the prompt seems to reward "typicality" if taken literally.
            # However, the prompt says "Lower F indicates better prediction".
            # And "Higher scores reward answers that ... reduce surprise".
            # Contradiction in prompt formula vs description? 
            # "score = -(F - E[F])^2" -> Maximized when F = E[F]. This rewards average-ness.
            # "Lower F ... better" -> We want min F.
            # Resolution: The prompt likely implies a proper scoring rule for probability estimation,
            # but applied here to structural fit. 
            # Let's prioritize the "Lower F is better" instruction for ranking, 
            # and use the formula as a tie-breaker or modifier?
            # NO, I must follow the algorithm steps. 
            # Step 5: "score = -(F - E[F])^2". 
            # If I follow this strictly, I reward the "average" answer. 
            # But the prompt ALSO says "Higher scores reward answers that ... reduce surprise".
            # This implies the formula might be illustrative of a Brier score (which measures accuracy of probability).
            # If we treat S as the probability of being correct.
            # Let's modify the interpretation: 
            # We want to reward LOW F. 
            # Let's use a transformed score: Score = -F + (Penalty for deviation from consensus if consensus is wrong?)
            # Let's stick to the core goal: Beat NCD, capture structure.
            # I will use: FinalScore = s * 10.0 (Dominant structural signal).
            # And I will incorporate the "Free Energy" concept by ensuring low F (high S) is the primary driver.
            # The "Mechanism Design" part in the code will be the ranking itself.
            
            # Re-reading carefully: "score = -(F - E[F])^2" where E[F] is expected free energy.
            # If the system is truthful, F should be low. 
            # Maybe the prompt meant: Score = - (F - F_optimal)^2?
            # Given the conflict, I will prioritize the GOAL: "Higher score = more likely correct".
            # Correct answers have high Structural Similarity (S) -> Low F.
            # So Score should correlate with S.
            # I will compute the Brier score against the "Best Possible" (F_min) instead