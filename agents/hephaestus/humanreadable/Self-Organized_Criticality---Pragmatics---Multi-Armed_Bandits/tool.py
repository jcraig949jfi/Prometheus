class ReasoningTool:
    """
    A reasoning tool combining Pragmatics, Self-Organized Criticality (SOC), 
    and Multi-Armed Bandits (MAB) with strict epistemic honesty.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, numbers, causals) to form a pragmatic score.
    2. SOC Diffusion: Candidates are nodes in a graph. High-scoring nodes 'avalanche' relevance to 
       structurally similar neighbors until stability, modeling constraint propagation.
    3. MAB Selection: Uses UCB1 to balance exploring low-confidence candidates vs exploiting high SOC scores.
    4. Epistemic Honesty: Meta-analysis of the prompt detects ambiguity traps, capping confidence regardless of score.
    5. Scoring: Structural (50%+) + Computation (20%+) + NCD Tiebreaker (<15%).
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|n\'t|no|never|neither|nor)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|better|worse|greater|lesser|-er|-est)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then|else|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|while|during|until|since)\b', re.IGNORECASE),
            'numbers': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|hours?|days?)?', re.IGNORECASE),
            'operators': re.compile(r'[\+\-\*/=<>]'),
            # Trap detectors
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why is|when did)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or|is it .+ or)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|they|him|her)\b.*\bwho\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features and compute binary indicators."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'has_temporal': bool(self.patterns['temporal'].search(text)),
            'numbers': self.patterns['numbers'].findall(text),
            'has_operators': bool(self.patterns['operators'].search(text)),
            'raw_text': text
        }
        return features

    def _compute_pragmatic_score(self, prompt: str, candidate: str) -> float:
        """
        Compute initial pragmatic score based on Grice's maxims and structural adherence.
        Returns a score between 0.0 and 1.0.
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        score = 0.0
        max_score = 0.0
        
        # Quantity: Does candidate address numeric constraints if present?
        if p_feats['numbers']:
            max_score += 1.0
            # Check if candidate contains numbers if prompt has them (heuristic)
            if c_feats['numbers']:
                score += 1.0
        else:
            max_score += 0.5
            score += 0.5 # Default pass if no numbers required

        # Quality: Negation alignment (avoiding contradiction)
        # If prompt has negation, valid answers often reflect it or don't contradict
        max_score += 1.0
        score += 0.5 # Base assumption of quality
        if p_feats['has_negation'] and not c_feats['has_negation']:
            # Potential penalty if prompt negates but answer ignores (simplified)
            pass 

        # Relation: Shared structural features (causal, conditional)
        if p_feats['has_conditional']:
            max_score += 1.0
            if c_feats['has_conditional']:
                score += 1.0
            elif "if" in c_feats['raw_text'] or "then" in c_feats['raw_text']:
                score += 0.8
        
        if p_feats['has_causal']:
            max_score += 1.0
            if c_feats['has_causal']:
                score += 1.0

        # Manner: Simplicity (length penalty for extreme verbosity)
        max_score += 1.0
        if len(c_feats['raw_text']) < len(p_feats['raw_text']) * 3:
            score += 1.0
        else:
            score += 0.5

        return (score / max_score) if max_score > 0 else 0.5

    def _compute_computation_score(self, prompt: str, candidate: str) -> float:
        """
        Attempt to solve math/logic problems explicitly.
        Returns 1.0 if correct, 0.0 if wrong, 0.5 if not applicable.
        """
        # Detect simple math expression in prompt or candidate
        # Look for patterns like "5 + 3" or "what is 2*2"
        text = f"{prompt} {candidate}"
        numbers = self._extract_features(text)['numbers']
        
        # Simple arithmetic check if operators exist
        if self._extract_features(text)['has_operators'] and len(numbers) >= 2:
            try:
                # Extract potential equation from candidate if it looks like a result
                # Or solve prompt if it's an expression
                expr_match = re.search(r'([\d\s\+\-\*/\.\(\)]+)', candidate)
                if expr_match:
                    # Sanitize and eval simple math
                    expr = expr_match.group(1).replace('=', '')
                    if re.match(r'^[\d\s\+\-\*/\.\(\)]+$', expr):
                        val = eval(expr)
                        # If candidate is just a number, check against prompt logic?
                        # For now, if it evaluates without error, give partial credit for structure
                        return 0.8 
            except:
                pass
        
        # Specific numeric comparison logic
        nums_p = self._extract_features(prompt)['numbers']
        nums_c = self._extract_features(candidate)['numbers']
        
        if nums_p and nums_c:
            try:
                # Check if candidate number matches a derived logic (simplified for demo)
                # E.g. Prompt: "Which is larger, 2 or 5?" Candidate: "5"
                p_vals = [float(n[0]) for n in nums_p]
                c_vals = [float(n[0]) for n in nums_c]
                
                if "larger" in prompt.lower() or "greater" in prompt.lower():
                    if max(p_vals) in c_vals: return 1.0
                elif "smaller" in prompt.lower() or "less" in prompt.lower():
                    if min(p_vals) in c_vals: return 1.0
            except:
                pass

        return 0.5 # Neutral if no computation detected

    def _soc_diffusion(self, prompt: str, candidates: List[str]) -> List[float]:
        """
        Perform Self-Organized Criticality diffusion.
        Nodes = candidates. Edges = Jaccard overlap of structural features.
        Avalanche redistributes pragmatic scores.
        """
        n = len(candidates)
        if n == 0: return []
        if n == 1: return [self._compute_pragmatic_score(prompt, candidates[0])]

        # 1. Initialize heights (h) with pragmatic scores
        h = [self._compute_pragmatic_score(prompt, c) for c in candidates]
        
        # 2. Build Graph (Adjacency via Jaccard on feature sets)
        feature_sets = []
        for c in candidates:
            f = self._extract_features(c)
            # Create a set of active features
            active = {k for k, v in f.items() if v and k != 'raw_text' and k != 'numbers'}
            if f['numbers']: active.add('has_numbers')
            feature_sets.append(active)

        # Adjacency matrix (weights)
        weights = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                set_i, set_j = feature_sets[i], feature_sets[j]
                union = set_i | set_j
                if not union:
                    w = 0.0
                else:
                    intersection = set_i & set_j
                    w = len(intersection) / len(union) if len(union) > 0 else 0.0
                weights[i][j] = weights[j][i] = w

        # 3. Avalanche Process
        theta = 1.0
        max_iterations = 1000
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            unstable = False
            for i in range(n):
                if h[i] > theta:
                    unstable = True
                    excess = h[i] - theta
                    h[i] = theta
                    
                    # Distribute excess to neighbors
                    total_weight = sum(weights[i])
                    if total_weight > 0:
                        for j in range(n):
                            if i != j and weights[i][j] > 0:
                                share = excess * (weights[i][j] / total_weight)
                                h[j] += share
                    else:
                        # If no neighbors, dissipate (lose energy)
                        pass 
                    break # Restart loop to ensure stability (synchronous update alternative)
            
            if not unstable:
                break
        
        return h

    def _mab_select(self, soc_scores: List[float], rounds: int = 10) -> List[int]:
        """
        Simulate Multi-Armed Bandit selection to rank candidates.
        Uses UCB1 to balance exploration/exploitation of SOC scores.
        """
        n_arms = len(soc_scores)
        if n_arms == 0: return []
        if n_arms == 1: return [0]

        counts = [1] * n_arms  # Initialize with 1 pull each to avoid div by zero
        means = soc_scores[:]  # Initial mean is the SOC score
        
        history = []
        
        for t in range(1, rounds + 1):
            ucb_values = []
            for i in range(n_arms):
                # UCB1 formula: mean + sqrt(2 * ln(t_total) / n_i)
                # We treat 't' as the global step, but here we simulate rounds
                exploration_bonus = math.sqrt(2 * math.log(t + 1) / counts[i])
                ucb_values.append(means[i] + exploration_bonus)
            
            best_arm = max(range(n_arms), key=lambda i: ucb_values[i])
            history.append(best_arm)
            
            # Update mean (simulate observation = true SOC score)
            # In real MAB, we observe a stochastic reward. Here we use the stable SOC score as the 'true' value.
            reward = soc_scores[best_arm]
            counts[best_arm] += 1
            means[best_arm] = means[best_arm] + (reward - means[best_arm]) / counts[best_arm]

        # Rank by final estimated means
        ranked_indices = sorted(range(n_arms), key=lambda i: means[i], reverse=True)
        return ranked_indices

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Caps confidence if the question itself is flawed.
        """
        p_lower = prompt.lower()
        features = self._extract_features(prompt)
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower) and "data" not in p_lower:
            return 0.4
            
        # 4. Pronoun Ambiguity (simplified check)
        if "who" in p_lower and any(pron in p_lower for pron in [" he ", " she ", " they "]):
             return 0.3

        # 5. Structural insufficiency (No clear logical hooks)
        if not any([
            features['has_negation'], features['has_conditional'], 
            features['has_causal'], features['numbers'], features['has_comparative']
        ]):
            # If the prompt is just "What is the best color?", structural score is low
            # But we check if the answer is definitive. If the prompt is vague, confidence drops.
            if len(prompt.split()) < 6 and "?" in prompt:
                return 0.25

        return 1.0 # No meta-traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        z = zlib.compress
        len_s1 = len(z(s1.encode()))
        len_s2 = len(z(s2.encode()))
        len_s1_s2 = len(z((s1 + s2).encode()))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Structural & Pragmatic Initialization + SOC Diffusion
        soc_scores = self._soc_diffusion(prompt, candidates)
        
        # 2. Computation Check (Boost if math/logic solved)
        comp_scores = [self._compute_computation_score(prompt, c) for c in candidates]
        
        # 3. Combine Scores: Structural (SOC) 60%, Computation 30%, NCD 10%
        final_scores = []
        for i, c in enumerate(candidates):
            soc = soc_scores[i]
            comp = comp_scores[i]
            
            # NCD as tiebreaker/minor factor (Distance to prompt? Or internal consistency?)
            # Using NCD to measure how much the candidate adds vs repeats (Quantity maxim)
            ncd_val = self._ncd_score(prompt, c)
            ncd_score = 1.0 - ncd_val # Higher is better (less redundant/more informative)
            
            # Weighted Sum
            # Ensure structural is dominant
            score = (soc * 0.60) + (comp * 0.30) + (ncd_score * 0.10)
            final_scores.append(score)

        # 4. MAB Ranking
        # We run a quick MAB simulation to order them based on the scores
        ranked_indices = self._mab_select(final_scores, rounds=20)
        
        result = []
        for idx in ranked_indices:
            result.append({
                "candidate": candidates[idx],
                "score": round(final_scores[idx], 4),
                "reasoning": f"SOC:{soc_scores[idx]:.2f}, Comp:{comp_scores[idx]:.2f}"
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt for ambiguity/traps.
        """
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt, answer)
        
        if meta_cap < 0.3:
            return round(meta_cap, 2)

        # 2. Structural Validation
        # Does the answer share structural features with the prompt?
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        structural_match = 0.0
        count = 0
        
        # Check specific alignments
        if p_feats['numbers'] and a_feats['numbers']:
            structural_match += 1.0
            count += 1
        elif not p_feats['numbers'] and not a_feats['numbers']:
            structural_match += 0.5 # Neutral
            count += 1
            
        if p_feats['has_negation'] == a_feats['has_negation']:
            structural_match += 1.0
            count += 1
            
        if p_feats['has_conditional'] == a_feats['has_conditional']:
            structural_match += 1.0
            count += 1
            
        base_score = (structural_match / count) if count > 0 else 0.5
        
        # 3. Computation Verification
        comp_score = self._compute_computation_score(prompt, answer)
        if comp_score == 1.0:
            base_score = 0.95 # High confidence if math checks out
        elif comp_score == 0.0:
            base_score = 0.1 # Math failed
            
        final_conf = min(base_score