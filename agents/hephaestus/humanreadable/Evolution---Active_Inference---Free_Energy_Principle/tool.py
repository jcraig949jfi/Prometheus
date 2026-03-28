import re
import numpy as np

class ReasoningTool:
    """
    Evolutionary Active Inference Reasoning Tool.
    
    Mechanism:
    1. Parses prompt into logical propositions (negations, comparatives, conditionals, numerics).
    2. Encodes each candidate answer as a binary hypothesis vector matching these propositions.
    3. Computes Variational Free Energy (F) = Prediction Error + Complexity Penalty.
    4. Runs a micro-evolutionary loop (selection/mutation) to minimize Expected Free Energy (G).
    5. Scores candidates based on the inverse of the minimum G found.
    """
    
    def __init__(self):
        self.lambda_complexity = 0.5
        self.generations = 5
        self.population_size = 10
        self.mutation_rate = 0.1

    def _parse_propositions(self, text):
        """Extract logical constraints as regex patterns and numeric values."""
        props = []
        text_lower = text.lower()
        
        # Negations
        if re.search(r'\b(not|no|none|never)\b', text_lower):
            props.append(('negation', 1 if re.search(r'\b(not|no|none|never)\b', text_lower) else 0))
        
        # Comparatives
        comps = re.findall(r'(\w+)\s*(>|<|>=|<=|greater|less)\s*(\w+)', text_lower)
        for c in comps:
            props.append(('comparative', c[0], c[1], c[2]))
            
        # Conditionals
        if re.search(r'\b(if|then|unless)\b', text_lower):
            props.append(('conditional', 1))
            
        # Numerics extraction for evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                props.append(('numeric_check', n1 < n2)) # Example constraint: is first < second?
            except: pass
            
        return props

    def _encode_candidate(self, candidate, props):
        """Encode candidate truth values against parsed propositions."""
        vec = []
        c_lower = candidate.lower()
        
        for p in props:
            if p[0] == 'negation':
                # Check if candidate acknowledges negation
                has_neg = any(w in c_lower for w in ['not', 'no', 'false', 'never'])
                vec.append(1 if has_neg else 0)
            elif p[0] == 'comparative':
                # Simplified: check if candidate contains comparative words
                has_comp = any(w in c_lower for w in ['greater', 'less', 'more', 'fewer', '>', '<'])
                vec.append(1 if has_comp else 0)
            elif p[0] == 'conditional':
                has_if = any(w in c_lower for w in ['if', 'then', 'because', 'so'])
                vec.append(1 if has_if else 0)
            elif p[0] == 'numeric_check':
                # If prompt has numbers, does candidate reflect the relation? 
                # Heuristic: presence of numbers implies engagement
                has_num = bool(re.search(r'\d', c_lower))
                vec.append(1 if has_num else 0)
            else:
                vec.append(0)
        return np.array(vec, dtype=float)

    def _compute_free_energy(self, hypothesis_vec, target_vec, lambda_reg=0.5):
        """F = Prediction Error + Lambda * Complexity"""
        if len(hypothesis_vec) == 0:
            return 1.0
        # Pad/truncate to match
        min_len = min(len(hypothesis_vec), len(target_vec))
        h = hypothesis_vec[:min_len]
        t = target_vec[:min_len]
        
        # Prediction Error (Squared Euclidean)
        error = np.sum((h - t) ** 2)
        
        # Complexity (Sparsity penalty: penalize too many 'true' assertions)
        complexity = lambda_reg * np.sum(h)
        
        return error + complexity

    def _evolve(self, initial_vec, target_vec):
        """Micro-evolution to minimize Free Energy."""
        if len(initial_vec) == 0:
            return 1.0
            
        dim = len(initial_vec)
        # Initialize population around the candidate's encoding
        pop = np.tile(initial_vec, (self.population_size, 1))
        
        # Add noise (mutation) to create diversity
        noise = np.random.randint(0, 2, size=pop.shape).astype(float)
        # Randomly flip bits based on mutation rate
        mask = np.random.random(pop.shape) < self.mutation_rate
        pop = np.where(mask, 1 - pop, pop)
        
        best_G = float('inf')
        
        for _ in range(self.generations):
            scores = []
            for i in range(self.population_size):
                h = pop[i]
                F = self._compute_free_energy(h, target_vec, self.lambda_complexity)
                
                # Expected Free Energy approximation:
                # G = F + Information Gain (variance reduction heuristic)
                # Here approximated by penalizing uncertainty (values near 0.5) and rewarding fit
                info_gain_term = 0.1 * np.var(h) 
                G = F + info_gain_term
                scores.append(G)
            
            # Selection: keep top half
            idx = np.argsort(scores)[:self.population_size//2 + 1]
            survivors = pop[idx]
            
            # Crossover and Mutation
            new_pop = []
            while len(new_pop) < self.population_size:
                p1, p2 = survivors[np.random.randint(len(survivors))], survivors[np.random.randint(len(survivors))]
                # Uniform crossover
                child = np.where(np.random.random(dim) > 0.5, p1, p2)
                # Mutation
                mut_mask = np.random.random(dim) < self.mutation_rate
                child = np.where(mut_mask, 1 - child, child)
                new_pop.append(child)
            pop = np.array(new_pop)
            best_G = min(best_G, min(scores))
            
        return best_G

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        props = self._parse_propositions(prompt)
        
        # Create target vector based on prompt structure (Ideal logical consistency)
        # For this model, we assume the prompt's implicit logic is the "truth" target
        target_vec = []
        for p in props:
            if p[0] == 'negation': target_vec.append(p[1])
            elif p[0] == 'comparative': target_vec.append(1) # Expect comparative awareness
            elif p[0] == 'conditional': target_vec.append(1)
            elif p[0] == 'numeric_check': target_vec.append(1 if p[1] else 0)
        target_vec = np.array(target_vec) if target_vec else np.array([0.5])

        results = []
        for cand in candidates:
            if not cand.strip():
                score = -100.0
            else:
                init_vec = self._encode_candidate(cand, props)
                # If no props found, use NCD tiebreaker logic implicitly via length penalty
                if len(props) == 0:
                    # Fallback to simple length/overlap heuristic if parsing fails
                    score = -abs(len(cand) - len(prompt))/100.0 
                else:
                    # Minimize Free Energy -> Higher score
                    G = self._evolve(init_vec, target_vec)
                    score = -G 
            
            results.append({"candidate": cand, "score": score, "reasoning": f"Free Energy: {-score:.4f}"})
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score: assume worst case G is high, best is near 0
        # Map [-10, 0] to [0, 1] roughly
        raw_score = res[0]["score"]
        conf = 1.0 / (1.0 + np.exp(raw_score + 2)) # Sigmoid shift
        return float(np.clip(conf, 0.0, 1.0))