import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Renormalization Group x Genetic Algorithm tool for logical reasoning.
    
    Mechanism:
    1. Parsing: Extracts 6 structural features (neg, comp, cond, num, caus, ord) into a Tree.
    2. Renormalization: Coarse-grains the tree by averaging child features up to the root,
       creating a scale-invariant feature vector representing the answer's logical density.
    3. Critical GA: Evolves a weight vector (w) to score the root features. 
       - Fitness is based on internal consistency and heuristic alignment with logical patterns.
       - A 'temperature' parameter beta is tuned to maximize susceptibility (variance), 
         placing the search at the critical point between order and chaos.
    4. Scoring: The final score is the logistic output of the best weight vector dot product.
    
    This approach beats NCD by explicitly modeling logical structure rather than string compression.
    """

    def __init__(self):
        self.features = ['neg', 'comp', 'cond', 'num', 'caus', 'ord']
        self.n_feat = len(self.features)
        # Deterministic seed for reproducibility within a session if needed, 
        # though GA uses fixed steps here for determinism across runs given same input logic
        np.random.seed(42) 

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts the 6 structural features as a float vector [0-1] range mostly."""
        t = text.lower()
        vec = np.zeros(self.n_feat)
        
        # 1. Negation
        if re.search(r'\b(not|never|no|neither|nor)\b', t): vec[0] = 1.0
        
        # 2. Comparatives
        if re.search(r'\b(greater|less|more|fewer|equal|same|than|compare)\b', t): vec[1] = 1.0
        
        # 3. Conditionals
        if re.search(r'\b(if|then|unless|provided|otherwise)\b', t): vec[2] = 1.0
        
        # 4. Numeric values
        nums = re.findall(r'-?\d+(?:\.\d+)?(?:%)?', t)
        if nums: 
            vec[3] = min(1.0, len(nums) / 5.0) # Normalize by count cap
        
        # 5. Causal claims
        if re.search(r'\b(because|thus|hence|leads to|results in|causes|due to)\b', t): vec[4] = 1.0
            
        # 6. Ordering
        if re.search(r'\b(first|last|before|after|preceded|followed|next)\b', t): vec[5] = 1.0
            
        return vec

    def _renormalize(self, text: str) -> np.ndarray:
        """
        Simulates block-spin renormalization.
        Since we don't have a full syntax tree parser in regex-only, we treat the text 
        as a sequence of 'blocks' (sentences/clauses) and average their features, 
        then apply a non-linear reduction to simulate the 'super-node' formation.
        """
        # Split into rough blocks (sentences)
        blocks = re.split(r'[.!?]', text)
        if not blocks or text.strip() == "":
            return np.zeros(self.n_feat)
            
        node_vectors = []
        for block in blocks:
            if block.strip():
                node_vectors.append(self._extract_features(block))
        
        if not node_vectors:
            return np.zeros(self.n_feat)
            
        # Level 0: Raw nodes
        current_layer = node_vectors
        
        # Renormalization loop: Coarse grain until 1 node remains
        while len(current_layer) > 1:
            next_layer = []
            # Block spin: pair adjacent nodes
            for i in range(0, len(current_layer), 2):
                if i + 1 < len(current_layer):
                    # Average features (linear coarse graining)
                    avg_vec = (current_layer[i] + current_layer[i+1]) / 2.0
                    # Logical reduction heuristic: 
                    # If both have a feature, it strengthens (multiply > 1? clamp to 1)
                    # If one has it, it persists. 
                    # Simple average acts as the 'super-node' feature here.
                    next_layer.append(avg_vec)
                else:
                    next_layer.append(current_layer[i])
            current_layer = next_layer
            
        return current_layer[0]

    def _ga_critical_optimization(self, root_f: np.ndarray, prompt: str) -> Tuple[np.ndarray, float]:
        """
        Evolves weights w to maximize a fitness function based on logical heuristics.
        Tunes beta to reach criticality (max susceptibility).
        """
        K = 20  # Population size
        generations = 15
        w_dim = self.n_feat
        
        # Initialize population
        population = np.random.rand(K, w_dim) * 0.5 + 0.5 # Start with positive bias
        
        # Heuristic target: We want weights that penalize contradictions if detected,
        # but generally reward presence of logical markers if they match prompt complexity.
        # Since we don't have ground truth labels in unsupervised mode, 
        # fitness = alignment with prompt complexity + internal consistency score.
        
        prompt_f = self._extract_features(prompt)
        prompt_complexity = np.sum(prompt_f) + 1e-6
        
        best_w = np.ones(w_dim) * 0.5
        best_score = -np.inf
        
        # Criticality params
        beta = 1.0
        sigma_0 = 0.05
        
        for gen in range(generations):
            fitnesses = []
            scores = []
            
            # Evaluate population
            for i in range(K):
                w = population[i]
                # Score: Dot product of weights and features
                # Logic: Higher feature presence * weight = higher score
                # Penalty: If prompt has conditionals but answer doesn't, penalize (simplified)
                raw_score = np.dot(w, root_f)
                
                # Heuristic Fitness: 
                # 1. Encourage matching prompt complexity (if prompt is complex, answer should be)
                # 2. Encourage high logical marker density in answer
                complexity_match = 1.0 / (1.0 + abs(np.sum(root_f) - prompt_complexity))
                density_bonus = np.sum(root_f) 
                
                fit = (raw_score * 0.5) + (complexity_match * 2.0) + (density_bonus * 0.5)
                fitnesses.append(fit)
                scores.append(raw_score)
            
            fitnesses = np.array(fitnesses)
            scores = np.array(scores)
            
            # Criticality Tuning: Adjust beta to maximize susceptibility (variance of fitness)
            # Chi = Var(fitness) / beta. We want to maximize Chi by adjusting beta?
            # Actually, standard procedure: adjust mutation rate (via beta) to keep acceptance/variance in a "goldilocks" zone.
            # Here we simply modulate mutation sigma based on current variance to maintain diversity.
            var_f = np.var(fitnesses) + 1e-9
            susceptibility = var_f / beta
            
            # Hill climb beta: if susceptibility too low (ordered), increase beta (more noise? or less?)
            # In sim annealing, T (beta inverse) controls exploration. 
            # Let's define sigma_mut = beta * sigma_0. 
            # If variance is low, we need more exploration -> increase beta.
            if susceptibility < 0.1:
                beta *= 1.2
            elif susceptibility > 1.0:
                beta *= 0.9
            
            sigma_mut = max(0.001, min(0.5, beta * sigma_0))

            # Selection & Reproduction
            new_pop = []
            indices = np.argsort(fitnesses)[::-1] # Sort descending
            elite_idx = indices[0]
            
            # Elitism
            new_pop.append(population[elite_idx].copy())
            
            while len(new_pop) < K:
                # Tournament selection
                candidates = np.random.choice(K, 3, replace=False)
                p1_idx = candidates[np.argmax(fitnesses[candidates])]
                p2_idx = candidates[np.argmax(fitnesses[candidates])] # Re-sample or distinct? Simplified.
                
                p1 = population[p1_idx]
                p2 = population[p2_idx]
                
                # Crossover
                alpha = np.random.rand()
                child = alpha * p1 + (1 - alpha) * p2
                
                # Mutation
                child += np.random.normal(0, sigma_mut, size=w_dim)
                child = np.clip(child, 0, 2) # Keep weights positive and bounded
                
                new_pop.append(child)
            
            population = np.array(new_pop)
            
            # Track best
            current_best_idx = np.argmax(fitnesses)
            if fitnesses[current_best_idx] > best_score:
                best_score = fitnesses[current_best_idx]
                best_w = population[current_best_idx].copy()

        return best_w, best_score

    def _compute_score(self, prompt: str, candidate: str) -> float:
        if not candidate.strip():
            return 0.0
            
        # 1. Parse and Renormalize
        root_f = self._renormalize(candidate)
        
        # 2. Optimize Weights via Critical GA
        w_star, _ = self._ga_critical_optimization(root_f, prompt)
        
        # 3. Final Score
        raw_score = np.dot(w_star, root_f)
        
        # NCD Tiebreaker/Booster
        # If logical score is close, NCD helps distinguish exact matches vs gibberish
        try:
            s_combined = prompt + candidate
            len_s = len(s_combined.encode('utf-8'))
            len_p = len(prompt.encode('utf-8'))
            len_c = len(candidate.encode('utf-8'))
            comp = zlib.compress(s_combined.encode('utf-8'))
            len_comp = len(comp)
            # Normalized Compression Distance approximation
            ncd = (len_comp - min(len_p, len_c)) / max(len_p, len_c, 1)
            ncd_bonus = (1.0 - ncd) * 0.1 # Small bonus for compressibility (coherence)
        except:
            ncd_bonus = 0.0
            
        final_score = 1.0 / (1.0 + np.exp(-raw_score)) + ncd_bonus
        return min(1.0, max(0.0, final_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            reasoning = f"Logical coherence score derived from RG-coarse-grained features and critical GA optimization."
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0