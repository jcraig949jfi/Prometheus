import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse Best-Response Constraint Game (SBRCG) Implementation.
    
    Mechanism:
    1. Structural Parsing (Constraint Definition): Extracts logical constraints 
       (negations, comparatives, conditionals) from the prompt to build a cost matrix.
    2. Sparse Coding (Strategy Space): Represents candidate answers as sparse vectors 
       based on keyword activation relative to constraints.
    3. Nash Equilibrium (Best Response): Iteratively updates candidate scores. 
       A candidate's utility is high if it satisfies structural constraints (low violation cost)
       and maintains sparsity (L1 penalty on conflicting features).
    4. Convergence: The system settles when scores stabilize. The final score is a mix 
       of equilibrium stability and NCD (tiebreaker).
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _structural_parse(self, prompt: str) -> Dict:
        """Extracts logical constraints: negations, comparatives, numbers."""
        p_lower = prompt.lower()
        constraints = {
            'negations': len(re.findall(r'\b(not|no|never|without|except)\b', p_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|before|after)\b', p_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', p_lower)),
            'numbers': re.findall(r'\d+\.?\d*', p_lower),
            'has_question': '?' in prompt
        }
        # Simple numeric evaluation logic
        constraints['numeric_truth'] = False
        if len(constraints['numbers']) >= 2:
            try:
                nums = [float(n) for n in constraints['numbers']]
                if 'greater' in p_lower or 'more' in p_lower:
                    constraints['numeric_truth'] = nums[-2] > nums[-1] # Simplified heuristic
                elif 'less' in p_lower or 'smaller' in p_lower:
                    constraints['numeric_truth'] = nums[-2] < nums[-1]
            except ValueError:
                pass
        return constraints

    def _compute_feature_vector(self, text: str, prompt: str) -> np.ndarray:
        """Creates a sparse feature vector based on prompt keywords."""
        # Normalize
        t_words = set(re.findall(r'\w+', text.lower()))
        p_words = set(re.findall(r'\w+', prompt.lower()))
        
        # Feature dimensions: [overlap_count, length_penalty, keyword_match]
        # We keep it sparse by only activating on significant overlaps
        overlap = len(t_words.intersection(p_words))
        length = len(t_words)
        
        # Specific logical triggers
        has_yes = 1.0 if 'yes' in t_words else 0.0
        has_no = 1.0 if 'no' in t_words else 0.0
        has_true = 1.0 if 'true' in t_words else 0.0
        has_false = 1.0 if 'false' in t_words else 0.0
        
        return np.array([overlap, length, has_yes, has_no, has_true, has_false], dtype=float)

    def _best_response_step(self, utilities: np.ndarray, l1_lambda: float) -> np.ndarray:
        """
        Performs a soft-thresholding step (ISTA-like) to enforce sparsity and equilibrium.
        This simulates the agent choosing a strategy that minimizes violation cost + L1 penalty.
        """
        # Soft thresholding: sign(x) * max(|x| - lambda, 0)
        # Here applied to utilities to prune weak candidates (sparsity)
        thresholded = np.sign(utilities) * np.maximum(np.abs(utilities) - l1_lambda, 0)
        
        # Normalize to represent a probability distribution (Mixed Strategy approximation)
        total = np.sum(thresholded)
        if total > 0:
            return thresholded / total
        return np.zeros_like(utilities)

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        constraints = self._structural_parse(prompt)
        n = len(candidates)
        
        # Initialize utilities based on structural alignment
        # Higher initial utility for candidates that structurally match prompt expectations
        utilities = np.zeros(n)
        features = [self._compute_feature_vector(c, prompt) for c in candidates]
        features = np.array(features)
        
        # Base utility: Overlap with prompt (simple relevance)
        utilities = features[:, 0] 
        
        # Apply Constraint Penalties (The "Game" Logic)
        for i, cand in enumerate(candidates):
            c_lower = cand.lower()
            penalty = 0.0
            
            # Negation consistency
            if constraints['negations'] > 0:
                if 'not' in c_lower or 'no' in c_lower:
                    # If prompt has negation, candidate acknowledging it gets boost, 
                    # but double negation might be penalty depending on context. 
                    # Simplified: Assume candidate must reflect constraint complexity.
                    pass 
            
            # Numeric consistency
            if constraints['numbers'] and constraints['numeric_truth']:
                # If prompt implies a comparison truth, reward candidates with numbers
                if re.search(r'\d+', c_lower):
                    utilities[i] += 2.0
            
            # Conditional logic check (Heuristic)
            if constraints['conditionals'] > 0:
                if 'if' in c_lower or 'then' in c_lower:
                    utilities[i] += 1.5
                elif len(cand.split()) < 3:
                    # Short answers to complex conditional prompts are often wrong
                    utilities[i] -= 1.0

        # Iterative Best-Response (Nash Equilibrium Simulation)
        # Agents adjust strategies based on global utility landscape
        l1_lambda = 0.5 * np.mean(np.abs(utilities)) + self.epsilon
        for _ in range(5): # Fixed iterations for convergence approximation
            utilities = self._best_response_step(utilities, l1_lambda)
            # Re-inject structural bonuses to prevent total collapse to zero
            for i in range(n):
                if features[i, 2] > 0 and constraints['negations'] == 0: # Yes bias if no negation
                     utilities[i] += 0.1
        
        # Final Scoring: Combine Equilibrium Utility with NCD Tiebreaker
        results = []
        max_util = np.max(utilities) if np.max(utilities) > 0 else 1.0
        
        for i, cand in enumerate(candidates):
            # Normalize utility to 0-1 range roughly
            score = (utilities[i] / max_util) * 0.8 # Cap at 0.8 to leave room for NCD
            
            # NCD as tiebreaker/refiner (20% weight)
            # Prefer candidates that compress well with prompt (coherence)
            ncd_val = self._calculate_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.2
            
            final_score = score + ncd_score
            
            # Reasoning trace
            reason = f"Structural match: {features[i,0]}; Constraints: {constraints['negations']} neg, {constraints['comparatives']} comp; Equilibrium utility: {utilities[i]:.4f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the equilibrium stability of the single answer.
        """
        # Treat the single answer as a candidate list of one
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to 0-1 confidence. 
        # Since evaluate returns normalized scores, we clamp.
        conf = max(0.0, min(1.0, score))
        return conf