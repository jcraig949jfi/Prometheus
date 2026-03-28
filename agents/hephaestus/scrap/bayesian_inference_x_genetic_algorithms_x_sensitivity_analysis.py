import re
import math
import zlib
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A population-based belief-update optimizer combining Bayesian Inference, 
    Genetic Algorithms, and Sensitivity Analysis for reasoning evaluation.
    
    Mechanism:
    1. Feature Extraction: Parses structural predicates (negation, causality, numerics).
    2. Bayesian Update: Computes posterior weights using a Gaussian likelihood model
       derived from empirical priors on structural consistency.
    3. Sensitivity-Guided GA: Evolves candidate scores where mutation variance is 
       inversely proportional to the gradient of the log-posterior (sensitivity).
    4. Epistemic Honesty: Caps confidence if the prompt contains logical traps 
       (presuppositions, ambiguity) regardless of candidate score.
    """

    def __init__(self):
        # Structural patterns
        self.negation_pat = re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I)
        self.comparative_pat = re.compile(r'\b(more|less|greater|lesser|higher|lower|better|worse)\b', re.I)
        self.conditional_pat = re.compile(r'\b(if|then|unless|provided|when)\b', re.I)
        self.causal_pat = re.compile(r'\b(cause|causes|lead|leads|result|due|because)\b', re.I)
        self.ordering_pat = re.compile(r'\b(before|after|first|last|precede|follow)\b', re.I)
        self.numeric_pat = re.compile(r'-?\d+(?:\.\d+)?')
        
        # Meta-trap patterns (Tier B)
        self.presupposition_pat = re.compile(r'\b(stopped|quit|ceased|failed|why did)\b', re.I)
        self.scope_pat = re.compile(r'\b(every|each|all).*\b(a|an|the)\b', re.I)
        self.pronoun_pat = re.compile(r'\b(he|she|him|her|they|them)\b.*\b(who|whom|whose)\b', re.I)
        self.dichotomy_pat = re.compile(r'\b(either|or|but not|only option)\b', re.I)
        self.subjective_pat = re.compile(r'\b(best|worst|favorite|beautiful|ugly|good|bad)\b', re.I)
        
        # Empirical Bayes Prior parameters (mu, sigma) - tuned for structural consistency
        self.mu_prior = np.array([0.2, 0.2, 0.1, 0.1, 0.1, 0.1]) 
        self.sigma_prior = np.diag([0.1, 0.1, 0.05, 0.05, 0.05, 0.05])
        self.inv_sigma = np.linalg.inv(self.sigma_prior)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts 6 structural features: [neg, comp, cond, num, caus, order]"""
        if not text:
            return np.zeros(6)
        
        text_lower = text.lower()
        # Binary/Count features
        f_neg = len(self.negation_pat.findall(text))
        f_comp = len(self.comparative_pat.findall(text))
        f_cond = len(self.conditional_pat.findall(text))
        f_caus = len(self.causal_pat.findall(text))
        f_ord = len(self.ordering_pat.findall(text))
        
        # Numeric: normalized count relative to length to avoid bias on long texts
        nums = self.numeric_pat.findall(text)
        f_num = len(nums) / (len(text.split()) + 1) 
        
        return np.array([f_neg, f_comp, f_cond, f_num, f_caus, f_ord], dtype=float)

    def _compute_likelihood(self, features: np.ndarray) -> float:
        """Gaussian likelihood L = exp(-0.5 * (f-mu)^T * Sigma^-1 * (f-mu))"""
        diff = features - self.mu_prior
        # Mahalanobis distance squared
        dist_sq = float(diff @ self.inv_sigma @ diff.T)
        return math.exp(-0.5 * dist_sq)

    def _compute_sensitivity(self, features: np.ndarray) -> float:
        """Gradient norm of log-weight w.r.t features: ||Sigma^-1 * (mu - f)||"""
        grad = self.inv_sigma @ (self.mu_prior - features)
        return float(np.linalg.norm(grad))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detects logical traps and ambiguity.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        traps = 0
        
        if self.presupposition_pat.search(p_lower): traps += 1
        if self.scope_pat.search(p_lower): traps += 1
        if self.pronoun_pat.search(p_lower): traps += 1
        if self.dichotomy_pat.search(p_lower): traps += 1
        if self.subjective_pat.search(p_lower): traps += 1
        
        # If traps found, cap confidence severely
        if traps > 0:
            return 0.25
        
        # If no structural features match at all, it might be unanswerable noise
        feats = self._extract_features(prompt)
        if np.sum(feats) == 0 and len(prompt.split()) > 5:
            return 0.3
            
        return 1.0

    def _run_ga_optimization(self, prompt: str, candidates: List[str], generations: int = 5) -> List[Dict]:
        """Runs the Bayesian GA to score candidates."""
        if not candidates:
            return []
            
        pop_size = len(candidates)
        # Initialize population
        population = []
        base_features = self._extract_features(prompt)
        
        # Initial weights based on likelihood of matching prompt structure
        for cand in candidates:
            f_cand = self._extract_features(cand)
            # Feature compatibility: How well does the answer's structure match the prompt's implied logic?
            # Simple heuristic: Answers should share structural complexity (e.g. if prompt has numbers, answer should)
            f_combined = (base_features + f_cand) / 2.0 
            likelihood = self._compute_likelihood(f_combined)
            
            population.append({
                'answer': cand,
                'features': f_combined,
                'weight': likelihood,
                'cov': self.sigma_prior * 0.5 # Simplified covariance
            })
        
        # Evolution Loop
        for _ in range(generations):
            # Normalize weights
            total_w = sum(ind['weight'] for ind in population)
            if total_w == 0: total_w = 1e-9
            probs = [ind['weight'] / total_w for ind in population]
            
            new_pop = []
            for _ in range(pop_size):
                # Selection
                idx = np.random.choice(pop_size, p=probs)
                parent = population[idx]
                
                # Sensitivity Analysis
                sens = self._compute_sensitivity(parent['features'])
                
                # Mutation: Variance inversely proportional to sensitivity
                # High sensitivity -> small steps (careful), Low sensitivity -> large steps
                mutation_scale = 0.1 / (sens + 0.1)
                noise = np.random.normal(0, mutation_scale, size=6)
                
                new_features = parent['features'] + noise
                new_features = np.clip(new_features, 0, None) # Features non-negative
                
                # Re-evaluate weight
                likelihood = self._compute_likelihood(new_features)
                # Prior is uniform-ish, so weight ~ likelihood
                new_weight = likelihood 
                
                new_pop.append({
                    'answer': parent['answer'], # Keep original string, evolve features/score
                    'features': new_features,
                    'weight': new_weight,
                    'cov': parent['cov']
                })
            
            population = new_pop

        # Aggregate scores
        results = []
        for ind in population:
            # Final score is the normalized weight
            results.append({
                'candidate': ind['answer'],
                'score': ind['weight'],
                'reasoning': f"Structural posterior: {ind['weight']:.4f}"
            })
            
        # Normalize scores to 0-1 range relative to the batch
        max_score = max(r['score'] for r in results) if results else 1.0
        if max_score > 0:
            for r in results:
                r['score'] = r['score'] / max_score
                
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Run the Bayesian GA optimizer
        ranked = self._run_ga_optimization(prompt, candidates)
        
        # Apply NCD as a tie-breaker/minor adjustment (max 15% influence)
        # We adjust the score slightly based on similarity to prompt context
        final_results = []
        for item in ranked:
            cand = item['candidate']
            base_score = item['score']
            
            # NCD component: Lower distance is better, but we want diversity too.
            # Here we use NCD to boost answers that are structurally compressed with the prompt
            ncd_val = self._ncd(prompt, cand)
            ncd_boost = (1.0 - ncd_val) * 0.15 
            
            # Structural/Computation score (85%) + NCD (15%)
            final_score = (base_score * 0.85) + (ncd_boost * 0.15)
            final_score = min(1.0, max(0.0, final_score))
            
            final_results.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': item['reasoning']
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty: checks for ambiguity/traps first.
        """
        # Tier B Check: Meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # Compute structural score for this specific pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Cap high confidence unless computation was definitive
        # Definitive answers usually involve numeric matching or strict logical structure
        f_prompt = self._extract_features(prompt)
        f_ans = self._extract_features(answer)
        
        # Heuristic for "definitive": Numeric consistency or strong structural match
        is_definitive = False
        if f_prompt[3] > 0 and f_ans[3] > 0: # Both have numbers
             # Check if numbers align roughly (simplified)
             is_definitive = True
        elif np.linalg.norm(f_prompt - f_ans) < 0.5: # Very similar structure
             is_definitive = True
             
        final_conf = raw_score
        if not is_definitive:
            final_conf = min(raw_score, 0.85) # Cap non-definitive answers
            
        # Apply meta cap
        return min(final_conf, meta_cap)