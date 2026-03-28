import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning engine based on Ergodic Theory, Network Science, and Sensitivity Analysis.
    
    Mechanism:
    1. Parsing: Extracts propositional units from the prompt and candidates using regex for 
       negations, comparatives, conditionals, causality, and ordering.
    2. Graph Construction: Builds a weighted adjacency matrix where nodes are text fragments.
       Edges represent logical relations (entailment +1, contradiction -1, etc.).
    3. Ergodic Random Walk: Converts weights to a transition matrix and computes the stationary 
       distribution (PageRank-style) to determine the centrality of concepts supporting each candidate.
    4. Sensitivity Analysis: Perturbs the graph weights with Gaussian noise multiple times to 
       compute the variance of the stationary distribution. Candidates with low variance (high stability)
       receive higher robustness scores.
    """
    
    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b|\b[<>]=?\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?')
        }
        self.M = 20  # Number of perturbations for sensitivity analysis
        self.sigma = 0.05  # Noise magnitude

    def _extract_units(self, text: str) -> List[str]:
        """Split text into propositional units (sentences/clauses)."""
        # Simple split by sentence delimiters, keeping delimiters for context if needed
        raw = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s for s in raw if s.strip()]

    def _build_graph(self, prompt: str, candidates: List[str]) -> Tuple[List[str], np.ndarray]:
        """Construct the weighted adjacency matrix W."""
        full_text = f"{prompt} " + " ".join([f"CAND_{i}: {c}" for i, c in enumerate(candidates)])
        units = self._extract_units(full_text)
        n = len(units)
        if n == 0:
            return [], np.array([])
        
        W = np.zeros((n, n))
        
        # Map candidates to unit indices for scoring later
        candidate_indices = []
        for i, c in enumerate(candidates):
            c_lower = f"cand_{i}:"
            for j, u in enumerate(units):
                if c_lower in u.lower() or c.strip() in u.strip():
                    candidate_indices.append(j)
                    break
        
        # If exact match fails, map to the last unit block roughly
        if len(candidate_indices) != len(candidates):
            # Fallback: assume last N units correspond to candidates if structure is simple
            # This is a heuristic fallback for the demo
            start_idx = max(0, n - len(candidates))
            candidate_indices = list(range(start_idx, n))[:len(candidates)]

        for i, u_i in enumerate(units):
            u_i_lower = u_i.lower()
            
            # Self-loop for existence
            W[i, i] = 0.1 
            
            for j, u_j in enumerate(units):
                if i == j: continue
                u_j_lower = u_j.lower()
                weight = 0.0
                
                # Check relations
                if re.search(self.patterns['negation'], u_i_lower) and u_j_lower in u_i_lower:
                    weight -= 1.0 # Contradiction/Negation
                elif re.search(self.patterns['causal'], u_i_lower) and u_j_lower in u_i_lower:
                    weight += 1.0 # Causal
                elif re.search(self.patterns['conditional'], u_i_lower):
                    weight += 0.8 # Conditional support
                elif re.search(self.patterns['comparative'], u_i_lower):
                    weight += 0.5 # Comparative relation
                
                # Co-occurrence / Associative (weak)
                common_words = set(u_i_lower.split()) & set(u_j_lower.split())
                if len(common_words) > 2:
                    weight += 0.2 * min(len(common_words)/5.0, 1.0)
                
                W[i, j] = weight

        return units, W, candidate_indices

    def _compute_stationary(self, W: np.ndarray) -> np.ndarray:
        """Compute stationary distribution via power iteration."""
        n = W.shape[0]
        if n == 0: return np.array([])
        
        # Normalize to row-stochastic (handling negatives by clipping for probability mass)
        P = np.clip(W, 0, None)
        row_sums = P.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        P = P / row_sums
        
        # Power iteration
        pi = np.ones(n) / n
        for _ in range(100):
            pi_next = pi @ P
            if np.linalg.norm(pi_next - pi, 1) < 1e-6:
                break
            pi = pi_next
        return pi

    def _get_robustness_score(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """Main logic: Build graph, perturb, compute variance, return scores."""
        units, W, cand_indices = self._build_graph(prompt, candidates)
        n = len(units)
        
        if n == 0 or W.size == 0:
            return [(c, 0.5) for c in candidates] # Fallback
        
        base_pi = self._compute_stationary(W)
        if len(base_pi) == 0:
            return [(c, 0.5) for c in candidates]

        # Sensitivity Analysis
        variances = np.zeros(n)
        for _ in range(self.M):
            noise = np.random.normal(0, self.sigma, W.shape)
            W_pert = W + noise
            # Ensure non-negative for transition logic in this specific step if needed, 
            # but the definition says keep negatives as penalty terms later. 
            # For P calculation we clip negatives in _compute_stationary.
            pi_pert = self._compute_stationary(W_pert)
            if len(pi_pert) == n:
                variances += (pi_pert - base_pi) ** 2
        
        variances /= self.M
        
        # Score candidates based on stability (low variance = high robustness)
        # And magnitude of base_pi (central concepts)
        results = []
        for i, cand in enumerate(candidates):
            idx = cand_indices[i] if i < len(cand_indices) else 0
            if idx >= n: idx = n - 1
            
            var_c = variances[idx]
            base_c = base_pi[idx]
            
            # Robustness score: High base probability, Low variance
            # S_c = base_c / (1 + var_c) normalized roughly
            score = base_c / (1.0 + var_c * 10.0) 
            results.append((cand, score))
            
        return results

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Try structural reasoning first
        scores = self._get_robustness_score(prompt, candidates)
        
        # Fallback to NCD if structural signal is too weak or uniform (degenerate graph)
        total_score = sum(s[1] for s in scores)
        if total_score < 1e-6:
            # NCD Fallback (Tiebreaker only)
            import zlib
            prompt_bytes = prompt.encode()
            results = []
            for cand in candidates:
                cand_bytes = cand.encode()
                comp_comb = len(zlib.compress(prompt_bytes + cand_bytes))
                comp_prompt = len(zlib.compress(prompt_bytes))
                comp_cand = len(zlib.compress(cand_bytes))
                ncd = (comp_comb - min(comp_prompt, comp_cand)) / max(comp_prompt, comp_cand, 1)
                # Lower NCD is better, invert for score
                results.append({"candidate": cand, "score": 1.0/(1.0+ncd), "reasoning": "NCD fallback"})
            return sorted(results, key=lambda x: x['score'], reverse=True)

        # Normalize scores to 0-1 range roughly
        max_s = max(s[1] for s in scores)
        min_s = min(s[1] for s in scores)
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        final_results = []
        for cand, score in scores:
            norm_score = (score - min_s) / range_s if range_s != 0 else 0.5
            final_results.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": f"Ergodic stability score based on graph centrality and perturbation variance."
            })
            
        return sorted(final_results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate against a single candidate list containing only the answer
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']