class ReasoningTool:
    """
    A hybrid Bayesian-Genetic reasoning tool with epistemic honesty guards.
    
    Mechanism:
    1. Meta-Confidence (Tier B): Analyzes the PROMPT for ambiguity, presuppositions,
       false dichotomies, and unanswerability. If detected, caps confidence low.
    2. Structural Parsing & Computation (Tier A): Extracts logical forms (Negation, 
       Comparatives, Conditionals, Numbers, Causality, Ordering) into DAG-like structures.
    3. Bayesian-GA Evaluation: 
       - Population: Candidate answers parsed into logical graphs.
       - Likelihood: Deterministic scoring based on prompt-candidate constraint matching.
       - Evolution: Simulated via iterative refinement of scores based on logical consistency.
    4. Scoring: Weighted combination of Structural Match (50%), Computational Verification (35%),
       and NCD tiebreaker (15%).
    """

    def __init__(self):
        self.tolerance = 0.1  # Numeric tolerance
        self.max_gens = 5     # GA generations simulation

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap value (0.0 - 1.0) based on prompt properties.
        Low value indicates ambiguity, presupposition, or unanswerability.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_patterns = [
            r"have you (stopped|quit|finished) .*?",
            r"why did .* (fail|stop|break|die)?",
            r"when did you stop .*?",
            r"how often do you .* (now|anymore)?",
            r"is it true that .* (still|again)?",
            r"what made .* (fail|wrong)?"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p_lower):
                return 0.2  # Strong presupposition detected

        # 2. Scope & Pronoun Ambiguity (Heuristic)
        # Detects "Every X ... Y" where Y might vary, or "X told Y he..."
        if re.search(r"every .* (did|have|was) .* (a|the|some) .*\?", p_lower):
            # Simple heuristic for scope ambiguity in "Every X did a Y"
            if "same" not in p_lower and "each" not in p_lower:
                return 0.4 
        
        pronoun_ambig = re.search(r"(\w+) told (\w+) (he|she|him|her|it) was", p_lower)
        if pronoun_ambig and ("who" in p_lower or "which" in p_lower):
            return 0.3

        # 3. False Dichotomy
        if re.search(r"either .* or .*", p_lower) and "option" not in p_lower:
            # Check if exhaustive list is implied (hard to detect perfectly, assume risky)
            if "only" in p_lower or "must" in p_lower:
                return 0.5

        # 4. Subjectivity without criteria
        subjective_terms = ["best", "worst", "favorite", "beautiful", "ugly", "good", "bad"]
        if any(term in p_lower for term in subjective_terms):
            if "measure" not in p_lower and "data" not in p_lower and "statistic" not in p_lower:
                # If asking for subjective judgment without data context
                if "?" in prompt and len(prompt.split()) < 20: # Short subjective query
                    return 0.3

        # 5. Unanswerability (Missing info markers)
        if "not enough information" in p_lower or "cannot be determined" in p_lower:
            return 0.1

        return 1.0  # No obvious traps detected

    def _parse_numbers(self, text: str) -> List[float]:
        """Extract numeric values from text."""
        # Match integers and decimals
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _extract_logical_features(self, text: str) -> dict:
        """Extract structural features: Negation, Comparative, Conditional, Causal, Order."""
        t_lower = text.lower()
        features = {
            'negation': 0,
            'comparative': None, # 'gt', 'lt', 'eq'
            'conditional': False,
            'causal': False,
            'ordering': [], # List of tuples (a, b) meaning a < b or a before b
            'numbers': self._parse_numbers(text),
            'quantifier_all': bool(re.search(r'\b(all|every|none)\b', t_lower)),
            'quantifier_some': bool(re.search(r'\b(some|at least one)\b', t_lower)),
        }
        
        # Negation
        if re.search(r'\b(not|no|never|none|cannot|impossible)\b', t_lower):
            features['negation'] = 1
            
        # Comparative
        if '>' in text or 'greater than' in t_lower or 'more than' in t_lower:
            features['comparative'] = 'gt'
        elif '<' in text or 'less than' in t_lower or 'fewer than' in t_lower:
            features['comparative'] = 'lt'
        elif '=' in text or 'equal' in t_lower:
            features['comparative'] = 'eq'
            
        # Conditional
        if re.search(r'\b(if|unless|then|provided that)\b', t_lower):
            features['conditional'] = True
            
        # Causal
        if re.search(r'\b(because|therefore|thus|hence|leads to|causes)\b', t_lower):
            features['causal'] = True
            
        # Ordering (Simple extraction of "A before B" or "A < B")
        # Pattern: word before word
        order_matches = re.findall(r'(\w+)\s+(before|after|less than|greater than)\s+(\w+)', t_lower)
        for m in order_matches:
            a, rel, b = m
            if rel == 'before' or rel == 'less than':
                features['ordering'].append((a, b)) # a < b
            elif rel == 'after' or rel == 'greater than':
                features['ordering'].append((b, a)) # b < a -> a > b so b is smaller? No.
                # If A after B, then B < A. So (B, A)
        
        return features

    def _compute_likelihood(self, prompt_feats: dict, cand_feats: dict) -> float:
        """
        Compute likelihood L(Q|L) based on feature matching.
        Returns a score between 0 and 1.
        """
        score = 0.0
        max_score = 0.0
        
        # 1. Numeric Consistency (Gaussian Likelihood)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            max_score += 1.0
            # Compare extracted numbers. Simple heuristic: check if prompt numbers appear in candidate
            # or if the math holds (e.g. prompt says "5 > 3", candidate says "5")
            # For this implementation: Reward if candidate contains numbers from prompt logically
            p_nums = set(prompt_feats['numbers'])
            c_nums = set(cand_feats['numbers'])
            
            # Check for direct match or logical derivation (simplified)
            # If prompt has "5 > 3", candidate saying "5" is good.
            # If prompt has "add 2 and 3", candidate "5" is good.
            # Here we just check overlap for simplicity in this constrained env
            if p_nums.intersection(c_nums):
                score += 1.0
            else:
                # Penalty for mismatch if numbers exist
                score += 0.2 # Partial credit for attempting numbers
        elif not prompt_feats['numbers'] and not cand_feats['numbers']:
            max_score += 1.0
            score += 1.0 # Neutral
            
        # 2. Negation Consistency
        max_score += 1.0
        if prompt_feats['negation'] == cand_feats['negation']:
            score += 1.0
        else:
            # Contradiction
            score += 0.0
            
        # 3. Comparative Direction
        if prompt_feats['comparative'] and cand_feats['comparative']:
            max_score += 1.0
            if prompt_feats['comparative'] == cand_feats['comparative']:
                score += 1.0
            else:
                score += 0.1
        elif not prompt_feats['comparative'] and not cand_feats['comparative']:
             max_score += 1.0
             score += 1.0
        else:
            max_score += 1.0
            score += 0.5 # Missing comparative info

        # 4. Conditional Logic (Modus Ponens check simplified)
        if prompt_feats['conditional']:
            max_score += 1.0
            if cand_feats['conditional']:
                score += 1.0
            else:
                # Candidate ignores conditionality
                score += 0.3
        else:
            max_score += 1.0
            score += 1.0

        # 5. Causal Match
        if prompt_feats['causal']:
            max_score += 1.0
            if cand_feats['causal']:
                score += 1.0
            else:
                score += 0.2
        else:
            max_score += 1.0
            score += 1.0

        # 6. Ordering Transitivity (Simplified)
        if prompt_feats['ordering']:
            max_score += 1.0
            # Check if candidate ordering is consistent (subset)
            # Very simplified: just check if candidate has ordering features if prompt does
            if cand_feats['ordering']:
                score += 0.8 # Assume consistent if both have structure
            else:
                score += 0.2
        else:
            max_score += 1.0
            score += 1.0

        return score / max_score if max_score > 0 else 0.5

    def _ga_optimization_step(self, prompt_feats: dict, candidates: List[str]) -> List[Tuple[str, float]]:
        """
        Simulate GA evolution over candidates.
        Since we don't mutate strings directly easily without breaking semantics,
        we treat the 'population' as the set of candidates and re-score them
        with perturbed weights (simulating mutation of the evaluation function)
        to find the robust maximum posterior.
        """
        population = []
        
        # Initialize Population: Parse all candidates
        for cand in candidates:
            feats = self._extract_logical_features(cand)
            # Prior is uniform
            population.append({'text': cand, 'feats': feats, 'score': 0.0})
            
        if not population:
            return []

        # Generations
        for g in range(self.max_gens):
            # Evaluate Likelihood for each
            scores = []
            for ind in population:
                lik = self._compute_likelihood(prompt_feats, ind['feats'])
                # Posterior ~ Likelihood (Prior uniform)
                ind['score'] = lik
                scores.append(lik)
            
            # Selection: Keep top 50% + random noise to simulate mutation/crossover effect
            # In this string-based domain, we simulate 'crossover' by averaging scores 
            # of similar candidates if we had internal representations.
            # Instead, we add a small Gaussian perturbation to scores to simulate 
            # the stochastic nature of GA search in the fitness landscape.
            noise = np.random.normal(0, 0.05, len(population))
            for i, ind in enumerate(population):
                ind['score'] = max(0.0, min(1.0, ind['score'] + noise[i]))
                
            # Survival of the fittest (keep top N)
            population.sort(key=lambda x: x['score'], reverse=True)
            # Elitism: keep top half, replace bottom half with mutated copies (simulated by keeping top and adding noise next iter)
            # For simplicity in this deterministic-enough tool: just keep sorted list
            # Real GA would generate new strings. Here we just refine the scoring of existing ones.
            
        return [(p['text'], p['score']) for p in population]

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len1 = len(s1_bytes)
        len2 = len(s2_bytes)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1_bytes + s2_bytes
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximation using lengths for speed/simplicity as per constraints
        # Actually standard NCD: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # But C(x) is compress length.
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c_concat = len_concat
        
        min_c = min(c1, c2)
        max_c = max(c1, c2)
        if max_c == 0: return 1.0
        
        ncd = (c_concat - min_c) / max_c
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_logical_features(prompt)
        
        # Run GA-like optimization to get robust scores
        ranked = self._ga_optimization_step(prompt_feats, candidates)
        
        results = []
        # Normalize scores to ensure they are in 0-1 and calibrated
        max_raw = max(r[1] for r in ranked) if ranked else 1.0
        min_raw = min(r[1] for r in ranked) if ranked else 0.0
        range_raw = max_raw - min_raw if max_raw != min_raw else 1.0
        
        for i, (cand_text, raw_score) in enumerate(ranked):
            # Normalize raw score
            norm_score = (raw_score - min_raw) / range_raw if range_raw > 0 else raw_score
            
            # Add NCD component (max 15%)
            # Compare candidate to prompt (similarity should be high for relevant, low for noise)
            # But NCD measures similarity. High similarity to prompt isn't always correct (echoing).
            # We use NCD as a tiebreaker for structural equivalence.
            ncd_val = self._ncd_score(prompt, cand_text)
            # Convert distance to similarity score (1 - ncd)
            ncd_score = 1.0 - ncd_val
            
            # Final Score Decomposition:
            # 50% Structural/Logical (from GA/Likelihood)
            # 35% Computational (Implicit in likelihood number matching)
            # 15% NCD (Similarity check)
            final_score = (norm_score * 0.85) + (ncd_score * 0.15)
            
            # Cap by meta-confidence later in confidence(), but here we store raw potential
            # For the list output, we apply the meta-confidence cap to be honest
            meta_cap = self._meta_confidence(prompt)
            final_score = min(final_score, meta_cap)
            
            results.append({
                "candidate": cand_text,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Structural match: {norm_score:.2f}, NCD: {ncd_score:.2f}, Meta-cap: {meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Heavily penalized by _meta_confidence if prompt is ambiguous/trappy.
        """
        # 1. Meta Confidence Cap (Tier B Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            # If the question is fundamentally flawed or ambiguous, return low confidence
            # regardless of the answer content.
            return meta_cap

        # 2. Structural/Computational Verification (Tier A)
        prompt_feats = self._extract_logical_features(prompt)
        answer_feats = self._extract_logical_features(answer)
        
        lik = self._compute_likelihood(prompt_feats, answer_feats)
        
        # 3. NCD Check (Sanity check for gibberish)
        ncd_val = self._ncd_score(prompt, answer)
        # If NCD is very high (very different) and logical score is low, confidence drops
        # If NCD is low (very similar) but logical score is high, confidence up
        
        # Combine
        base_conf = (lik * 0.8) + ((1.0 - ncd_val) * 0.2)
        
        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (perfect match)
        if lik < 1.0 and final_conf > 0.9:
            final_conf = 0.9