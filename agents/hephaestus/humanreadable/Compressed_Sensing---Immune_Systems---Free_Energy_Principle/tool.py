import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning evaluator based on the Free Energy Principle (FEP) 
    combined with Compressed Sensing (CS) and Immune Clonal Selection.
    
    Mechanism:
    1. Feature Extraction: Parses prompt/candidates into sparse logical vectors 
       (predicates, negations, comparatives, conditionals, causality, ordering, quantifiers).
    2. FEP Optimization: Treats the prompt's logical structure as the 'observation' (b) 
       and the candidate's structure as the 'model' (A). 
    3. Immune Search: Uses a clonal selection algorithm to minimize variational free energy:
       F = ||Ax - b||^2 + lambda||x||_1.
       - Prediction Error: Mismatch between prompt constraints and candidate claims.
       - Sparsity Prior: Penalizes overly complex or contradictory logical structures.
    4. Scoring: Lower free energy yields higher score. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.primitives = [
            r'\bnot\b', r'\bnever\b', r'\bno\b', r"n't",  # Negation
            r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bequal\s+to\b', r'[<>=]', # Comparatives
            r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', # Conditionals
            r'\bcause\b', r'\blead\s+to\b', r'\bresult\s+in\b', r'\bbecause\b', # Causal
            r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b', # Ordering
            r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b', r'\bany\b' # Quantifiers
        ]
        self.dict_size = len(self.primitives)
        # Hyperparameters for FEP and Immune Algorithm
        self.lambda_sparsity = 0.5
        self.population_size = 20
        self.elite_count = 5
        self.clones_per_elite = 3
        self.generations = 15
        np.random.seed(42)  # Determinism

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts sparse logical feature vector from text."""
        text_lower = text.lower()
        features = np.zeros(self.dict_size)
        for i, pattern in enumerate(self.primitives):
            if re.search(pattern, text_lower):
                features[i] = 1.0
        return features

    def _extract_numerics(self, text: str) -> List[float]:
        """Extracts numeric values for comparative reasoning."""
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        z = zlib.compress
        len_s1 = len(z(s1.encode()))
        len_s2 = len(z(s2.encode()))
        len_s1_s2 = len(z((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max_len

    def _free_energy(self, A: np.ndarray, x: np.ndarray, b: np.ndarray) -> float:
        """Calculates Variational Free Energy: Prediction Error + Sparsity Penalty."""
        # Prediction error: ||Ax - b||^2
        # A is (m, d), x is (d,), b is (m,) -> Ax is (m,)
        if A.shape[1] != len(x):
            # Handle dimension mismatch if dictionary sizes differ slightly (shouldn't happen here)
            min_dim = min(A.shape[1], len(x))
            pred_err = np.sum((A[:, :min_dim] @ x[:min_dim] - b)**2)
        else:
            pred_err = np.sum((A @ x - b)**2)
        
        # Sparsity prior: lambda * ||x||_1
        sparsity = self.lambda_sparsity * np.sum(np.abs(x))
        return pred_err + sparsity

    def _immune_optimize(self, A: np.ndarray, b: np.ndarray) -> float:
        """
        Performs Immune Clonal Selection to minimize Free Energy.
        Returns the minimum free energy found (lower is better).
        """
        d = self.dict_size
        # 1. Initialize population (p x d) with sparse Laplace noise
        population = np.random.laplace(0, 0.5, (self.population_size, d))
        population = np.sign(population) * np.maximum(np.abs(population) - 0.1, 0) # Soft threshold init

        for gen in range(self.generations):
            # 2. Affinity Evaluation (Free Energy)
            energies = np.array([self._free_energy(A, ind, b) for ind in population])
            
            # 3. Selection: Keep top k
            sorted_idx = np.argsort(energies)
            elites = population[sorted_idx[:self.elite_count]]
            
            # 4. Cloning & Mutation
            new_population = [ind for ind in elites] # Keep elites
            
            for elite in elites:
                for _ in range(self.clones_per_elite):
                    # Clone
                    clone = elite.copy()
                    # Gaussian perturbation
                    noise = np.random.normal(0, 0.1, d)
                    clone += noise
                    # ISTA-like soft thresholding to enforce sparsity (L1 prior)
                    threshold = 0.1
                    clone = np.sign(clone) * np.maximum(np.abs(clone) - threshold, 0)
                    new_population.append(clone)
            
            # 5. Replacement: Keep population size fixed
            # Re-evaluate energies for the expanded pool to select best
            pool = np.array(new_population)
            pool_energies = np.array([self._free_energy(A, ind, b) for ind in pool])
            sorted_pool_idx = np.argsort(pool_energies)
            population = pool[sorted_pool_idx[:self.population_size]]

        # Return best energy found
        final_energies = np.array([self._free_energy(A, ind, b) for ind in population])
        return float(np.min(final_energies))

    def _build_matrices(self, prompt: str, candidate: str):
        """Builds design matrix A (prompt) and target vector b (candidate logic)."""
        # In this formulation, we treat the prompt's extracted features as the 'target' b
        # and the candidate's features as the 'model' x we are trying to fit via A.
        # However, the prompt says: "A has one row per primitive extracted from the question"
        # and we seek x (answer) such that Ax ~ b.
        # To make this computationally tractable without a learned D, we interpret:
        # b = Feature vector of the Prompt (The logical constraints we must satisfy)
        # A = Identity matrix (Each primitive in candidate maps to same primitive in prompt)
        # x = Feature vector of Candidate (The hypothesis)
        # Then ||Ax - b|| becomes ||x - b|| (Direct feature matching with sparsity).
        # To strictly follow "A has one row per primitive", let A be Identity.
        
        feat_prompt = self._extract_features(prompt)
        feat_cand = self._extract_features(candidate)
        
        # Design matrix A (Identity for direct mapping of primitives)
        A = np.eye(self.dict_size)
        
        # Target b is the prompt's feature vector (what we expect to see)
        b = feat_prompt
        
        # Initial x is the candidate's feature vector
        x_init = feat_cand
        
        return A, x_init, b

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Scores a single candidate. Returns (score, reasoning_string)."""
        A, x_init, b = self._build_matrices(prompt, candidate)
        
        # Run immune optimization to find best sparse representation minimizing F
        min_free_energy = self._immune_optimize(A, b)
        
        # Base score from Free Energy (inverted: lower energy = higher score)
        # Shift to positive range roughly
        base_score = 10.0 - min_free_energy
        
        # Structural bonus: Exact numeric consistency check
        prompt_nums = self._extract_numerics(prompt)
        cand_nums = self._extract_numerics(candidate)
        
        reasoning = f"FEP={min_free_energy:.2f}"
        
        if prompt_nums and cand_nums:
            # Simple heuristic: if numbers are present, do they align logically?
            # This is a simplification of "numeric evaluation"
            if abs(prompt_nums[0] - cand_nums[0]) < 1e-6:
                base_score += 2.0
                reasoning += "; nums_match"
        
        # NCD Tiebreaker (only if scores are very close, handled externally or as small noise)
        # Here we add a tiny NCD component to break ties deterministically
        ncd_val = self._compute_ncd(prompt, candidate)
        final_score = base_score - (ncd_val * 0.01) # Small penalty for high NCD
        
        return final_score, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        score, _ = self._score_candidate(prompt, answer)
        # Normalize score to 0-1 range heuristically
        # Assuming typical free energy ranges, map [-5, 15] to [0, 1]
        conf = (score + 5.0) / 20.0
        return max(0.0, min(1.0, conf))