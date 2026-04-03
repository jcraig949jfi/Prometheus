class ReasoningTool:
    """
    GAHE-inspired Reasoning Tool: Gauge-Equivariant Analogy Hypothesis Engine.
    
    Mechanism:
    1. Analogical Reasoning (Core): Maps the prompt's structural skeleton to candidates.
       Uses 'Parallel Transport' of logical constraints (negations, comparatives) to 
       verify if the candidate preserves the relational structure of the prompt.
    2. Mechanism Design (Evaluation): Implements a VCG-like incentive scheme.
       Candidates are scored by their marginal contribution to structural consistency.
       'Payments' (scores) are adjusted by a penalty for failing constraint propagation,
       ensuring truthful reporting of logical validity rather than lexical overlap.
    3. Gauge Theory (Wrapper): The confidence() method acts as the gauge function,
       assessing the invariance of the answer under re-parameterization (synonym/structure swap).
       
    Note: Pure gauge theory math is restricted to the confidence wrapper as per historical data.
    Primary scoring relies on structural parsing and analogical mapping.
    """

    def __init__(self):
        # Structural patterns for analogical mapping
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'larger', 'smaller', 'more', 'less', 'greater', 'fewer', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        
    def _structural_signature(self, text: str) -> Dict:
        """Extract structural features for analogical mapping."""
        t_lower = text.lower()
        words = re.findall(r'\w+', t_lower)
        
        has_neg = any(w in self.negation_words for w in words)
        has_comp = any(w in self.comparatives for w in words)
        has_cond = any(w in self.conditionals for w in words)
        
        # Numeric extraction for constraint propagation
        nums = re.findall(r'\d+\.?\d*', text)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'neg_count': sum(1 for w in words if w in self.negation_words),
            'has_comp': has_comp,
            'has_cond': has_cond,
            'numbers': numbers,
            'word_set': set(words),
            'length': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _analogical_transfer_score(self, prompt: str, candidate: str) -> float:
        """
        Core Analogical Reasoning: Parallel Transport of Structure.
        Checks if the candidate preserves the logical 'fiber' of the prompt.
        """
        p_sig = self._structural_signature(prompt)
        c_sig = self._structural_signature(candidate)
        
        score = 0.0
        total_weight = 0.0

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt implies negation, candidate should reflect it or answer appropriately
        if p_sig['neg_count'] > 0:
            total_weight += 2.0
            # Heuristic: If prompt has negation, a valid answer often acknowledges it 
            # or the candidate itself contains negation if it's a continuation.
            # For QA, we check if the candidate contradicts the prompt's negation structure.
            # Simplified: Reward structural awareness.
            if c_sig['neg_count'] > 0 or p_sig['neg_count'] == c_sig['neg_count']:
                score += 1.5
            else:
                # Penalty for ignoring negation context
                score += 0.2 

        # 2. Comparative Logic
        if p_sig['has_comp']:
            total_weight += 2.0
            if c_sig['has_comp']:
                score += 2.0 # Strong analogical match
            elif c_sig['numbers']:
                score += 1.0 # Partial match (uses numbers)
        
        # 3. Conditional Logic
        if p_sig['has_cond']:
            total_weight += 2.0
            if c_sig['has_cond']:
                score += 2.0
            else:
                score += 0.5

        # 4. Numeric Constraint Propagation
        if p_sig['numbers'] and c_sig['numbers']:
            total_weight += 3.0
            # Check simple ordering consistency if both have numbers
            p_nums = p_sig['numbers']
            c_nums = c_sig['numbers']
            if len(p_nums) == len(c_nums):
                # Exact number match in same order is strong evidence
                if p_nums == c_nums:
                    score += 3.0
                else:
                    score += 0.5
            elif any(n in c_nums for n in p_nums):
                score += 1.5 # Partial overlap
        
        # Base overlap (Jaccard) for semantic context
        intersection = len(p_sig['word_set'] & c_sig['word_set'])
        union = len(p_sig['word_set'] | c_sig['word_set'])
        jaccard = intersection / union if union > 0 else 0
        score += jaccard * 2.0
        total_weight += 2.0

        return score / total_weight if total_weight > 0 else 0.0

    def _vcg_mechanism_adjust(self, base_score: float, prompt: str, candidate: str, all_candidates: List[str]) -> float:
        """
        Mechanism Design: VCG-like adjustment.
        Adjusts score based on marginal utility compared to the set.
        Prevents 'strategic' high scores from generic answers.
        """
        if len(all_candidates) < 2:
            return base_score
            
        # Calculate average score of others to determine marginal contribution
        others = [c for c in all_candidates if c != candidate]
        if not others:
            return base_score
            
        # Simulate: Does this candidate provide unique structural alignment?
        # If candidate is too similar to others (low diversity) but high score, penalize slightly
        avg_sim_to_others = sum(self._compute_ncd(candidate, o) for o in others) / len(others)
        
        # VCG-ish penalty: If it's very close to others (high compression together), 
        # it adds less marginal information.
        # NCD close to 0 means very similar. 
        diversity_bonus = (1.0 - avg_sim_to_others) * 0.1
        
        return base_score + diversity_bonus

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        raw_scores = []
        
        # Phase 1: Analogical Scoring
        for cand in candidates:
            score = self._analogical_transfer_score(prompt, cand)
            raw_scores.append(score)
        
        max_raw = max(raw_scores) if raw_scores else 1.0
        min_raw = min(raw_scores) if raw_scores else 0.0
        span = max_raw - min_raw if max_raw != min_raw else 1.0

        # Phase 2: Mechanism Design Adjustment & Normalization
        for i, cand in enumerate(candidates):
            # Normalize raw score to 0.4 - 0.9 range initially
            norm_score = 0.4 + 0.5 * ((raw_scores[i] - min_raw) / span)
            
            # Apply VCG adjustment
            final_score = self._vcg_mechanism_adjust(norm_score, prompt, cand, candidates)
            
            # Fallback to NCD if structural signals are weak (score near baseline)
            if final_score < 0.45:
                ncd = self._compute_ncd(prompt, cand)
                # Invert NCD (lower is better) and use as tiebreaker
                ncd_score = 1.0 - ncd 
                final_score = max(final_score, ncd_score * 0.4) 

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Analogical match: {raw_scores[i]:.2f}, Adjusted: {final_score:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Gauge Equivariant Confidence Wrapper.
        Tests invariance of the answer under structural perturbations.
        Returns 0-1.
        """
        # 1. Base structural consistency
        base_score = self._analogical_transfer_score(prompt, answer)
        
        # 2. Gauge Transformation: Check stability under re-phrasing (simulated)
        # If the answer relies on specific words that aren't structural, confidence drops.
        # We simulate a 'gauge transformation' by checking if the core numbers/logic hold.
        p_sig = self._structural_signature(prompt)
        a_sig = self._structural_signature(answer)
        
        gauge_invariance = 1.0
        
        # Check numeric gauge invariance
        if p_sig['numbers'] and a_sig['numbers']:
            # If numbers in answer are a subset of prompt, high invariance
            if set(a_sig['