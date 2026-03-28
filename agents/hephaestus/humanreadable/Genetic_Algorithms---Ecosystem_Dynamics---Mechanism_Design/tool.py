import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Genetic Algorithm with Ecosystem Dynamics and Mechanism Design.
    
    Mechanism:
    1. Feature Extraction: Parses binary vectors for logic features (negation, conditionals, etc.).
    2. Ecosystem Fitness: Computes energy flow from raw features (producers) to constraint 
       satisfaction (consumers). Higher trophic levels represent complex logical consistency.
    3. Mechanism Design: Applies a VCG-style penalty to discourage feature misrepresentation 
       relative to the population best, enforcing truthful structural alignment.
    4. Evolution: Runs a micro-GA (selection, crossover, mutation) to optimize the feature 
       encoding of each candidate answer against the prompt's logical constraints.
    
    Scoring: Normalized final energy + mechanism incentive. NCD used only as tiebreaker.
    """
    
    # Feature patterns
    PATTERNS = {
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
        'comparative': [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\blesser\b', r'>', r'<'],
        'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\belse\b'],
        'numeric': [r'\d+(\.\d+)?%?', r'\bone\b', r'\btwo\b', r'\bthree\b'],
        'causal': [r'\bbecause\b', r'\bleads to\b', r'\bresults in\b', r'\bcauses\b'],
        'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b'],
        'equality': [r'\bequal\b', r'\bsame\b', r'\bidential\b', r'='],
        'quantifier': [r'\ball\b', r'\bsome\b', r'\bany\b', r'\bevery\b', r'\bnone\b']
    }

    def __init__(self):
        self.feat_keys = list(self.PATTERNS.keys())
        self.num_features = len(self.feat_keys)
        self.mu = 1.0 / max(1, self.num_features)
        self.generations = 10
        self.pop_size = 8

    def _extract_features(self, text: str) -> np.ndarray:
        """Parse text into a binary feature vector."""
        text_lower = text.lower()
        vector = np.zeros(self.num_features, dtype=np.float32)
        for i, key in enumerate(self.feat_keys):
            for pattern in self.PATTERNS[key]:
                if re.search(pattern, text_lower):
                    vector[i] = 1.0
                    break
        return vector

    def _get_constraints(self, prompt: str) -> List[Tuple[int, int, int]]:
        """
        Generate logical constraints based on prompt features.
        Returns list of (input_idx, output_idx, type) representing logical flow.
        Type 0: Direct implication, Type 1: Negation check, Type 2: Numeric consistency
        """
        constraints = []
        p_feats = self._extract_features(prompt)
        
        # If prompt has conditionals, enforce dependency between conditional and causal/quantifier
        if p_feats[self.feat_keys.index('conditional')] > 0:
            c_idx = self.feat_keys.index('conditional')
            # Expect causal or quantifier in answer if prompt is conditional
            if 'causal' in self.feat_keys:
                constraints.append((c_idx, self.feat_keys.index('causal'), 0))
            if 'quantifier' in self.feat_keys:
                constraints.append((c_idx, self.feat_keys.index('quantifier'), 0))
        
        # If prompt has negation, expect negation or specific handling
        if p_feats[self.feat_keys.index('negation')] > 0:
            n_idx = self.feat_keys.index('negation')
            # Constraint: Negation in prompt should reflect in answer structure
            constraints.append((n_idx, n_idx, 1)) # Self-consistency on negation
            
        # Numeric consistency
        if p_feats[self.feat_keys.index('numeric')] > 0:
            n_idx = self.feat_keys.index('numeric')
            constraints.append((n_idx, n_idx, 2))
            
        # Default transitivity: If features exist, they should propagate
        for i, feat in enumerate(self.feat_keys):
            if p_feats[i] > 0:
                constraints.append((i, i, 0))
                
        return constraints

    def _compute_energy(self, features: np.ndarray, constraints: List, level: int = 0) -> float:
        """Compute ecosystem energy flow."""
        # Level 0: Raw feature weight
        weights = np.linspace(0.5, 1.0, self.num_features)
        e0 = np.sum(features * weights)
        
        if level == 0:
            return e0
            
        # Level 1+: Constraint satisfaction
        energy = e0
        for inp_idx, out_idx, ctype in constraints:
            if inp_idx < len(features) and out_idx < len(features):
                # Simple logical gate simulation
                if ctype == 0: # Implication
                    if features[inp_idx] > 0.5:
                        energy += features[out_idx] * 0.5
                elif ctype == 1: # Negation consistency
                    if features[inp_idx] > 0.5 and features[out_idx] < 0.5:
                        energy -= 0.5 # Penalty for missing expected negation
                elif ctype == 2: # Numeric
                    energy += features[out_idx] * 0.3
        return energy

    def _vcg_payment(self, x: np.ndarray, x_best: np.ndarray, constraints: List) -> float:
        """VCG-style payment to incentivize truthful feature reporting."""
        if np.all(x_best == 0):
            return 0.0
        
        # Calculate social welfare difference
        # Simplified: Penalty proportional to distance from the 'best' truthful representation
        diff = np.sum(np.abs(x - x_best))
        penalty = 0.1 * diff
        
        # Bonus for matching specific constraint satisfactions of the best
        match_bonus = 0.0
        for inp, out, _ in constraints:
            if inp < len(x) and out < len(x):
                if x[inp] == x_best[inp] and x[out] == x_best[out]:
                    match_bonus += 0.05
                    
        return match_bonus - penalty

    def _evolve_candidate(self, prompt: str, candidate: str) -> float:
        """Run micro-GA to find optimal feature encoding for the candidate."""
        constraints = self._get_constraints(prompt)
        base_features = self._extract_features(candidate)
        
        # Initialize population with variations of the candidate's features
        population = []
        for _ in range(self.pop_size):
            individual = base_features.copy()
            # Mutate slightly to explore logical space
            if np.random.random() < 0.5:
                mask = np.random.random(self.num_features) < self.mu
                individual = np.where(mask, 1 - individual, individual)
            population.append(individual)
            
        best_fitness = -np.inf
        best_individual = base_features
        
        for gen in range(self.generations):
            fitnesses = []
            # Evaluate
            for ind in population:
                energy = self._compute_energy(ind, constraints, level=2)
                # Mechanism design term relative to current best found in this generation
                current_best = max(population, key=lambda x: self._compute_energy(x, constraints, level=2))
                payment = self._vcg_payment(ind, current_best, constraints)
                fit = energy + payment
                fitnesses.append(fit)
            
            # Track global best for this candidate
            max_idx = np.argmax(fitnesses)
            if fitnesses[max_idx] > best_fitness:
                best_fitness = fitnesses[max_idx]
                best_individual = population[max_idx].copy()
            
            # Selection (Tournament size 3)
            new_pop = []
            for _ in range(self.pop_size):
                contestants = np.random.choice(len(population), 3, replace=False)
                winner_idx = contestants[np.argmax([fitnesses[i] for i in contestants])]
                winner = population[winner_idx].copy()
                
                # Crossover & Mutation
                if np.random.random() < 0.7: # Crossover rate
                    partner_idx = np.random.choice(len(population))
                    partner = population[partner_idx]
                    mask = np.random.random(self.num_features) < 0.5
                    winner = np.where(mask, winner, partner)
                
                if np.random.random() < self.mu: # Mutation
                    flip_idx = np.random.randint(0, self.num_features)
                    winner[flip_idx] = 1 - winner[flip_idx]
                    
                new_pop.append(winner)
            
            population = new_pop

        # Final score calculation
        final_energy = self._compute_energy(best_individual, constraints, level=2)
        # Normalize roughly to 0-1 range based on max possible energy approx
        max_possible = self.num_features * 1.5 + 2.0 
        score = max(0.0, min(1.0, final_energy / max_possible))
        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        try:
            z1 = len(repr(zip(*[iter(s1)]*1))) # Dummy compress proxy
            # Use actual zlib for NCD
            import zlib
            l1 = len(zlib.compress(s1.encode()))
            l2 = len(zlib.compress(s2.encode()))
            l12 = len(zlib.compress((s1+s2).encode()))
            ncd = (l12 - min(l1, l2)) / max(l1, l2)
            return max(0.0, min(1.0, ncd))
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        scores = []
        
        # Phase 1: Structural Scoring
        for cand in candidates:
            score = self._evolve_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": "Structural GA"})
            scores.append(score)
        
        # Phase 2: Tie-breaking with NCD if scores are too close
        max_score = max(scores) if scores else 0
        final_results = []
        
        for res in results:
            # Add small NCD component only if structural score is high (tie-breaker logic)
            # Or if structural signal is weak
            base_score = res["score"]
            
            # Heuristic: If score is near max, use NCD to differentiate
            if max_score > 0.1 and abs(base_score - max_score) < 0.05:
                ncd = self._ncd_score(prompt, res["candidate"])
                # Invert NCD (lower distance = higher score) and add tiny epsilon
                res["score"] = base_score + (1.0 - ncd) * 0.001
            
            res["score"] = float(round(res["score"], 6))
            final_results.append(res)
            
        # Sort descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        # Reuse the evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]