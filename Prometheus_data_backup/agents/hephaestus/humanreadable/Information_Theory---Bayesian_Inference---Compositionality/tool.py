import math
import hashlib
from typing import List, Dict

class ReasoningTool:
    """
    Implements a simplified Compositional Variational Information Bottleneck (CVIB).
    
    Mechanism:
    1. Compositional Prior (PCFG-style): Text is tokenized; structure is approximated
       by treating n-grams as 'constituents'. Valid English-like patterns have higher
       prior probability based on frequency heuristics.
    2. Bayesian Fit: Measures how well the candidate explains the prompt context
       via semantic overlap (Jaccard similarity of token sets).
    3. Information Bottleneck: Penalizes candidates with high complexity (length)
       relative to their explanatory power, simulating the I(x; z) term.
    4. Scoring: Score = Fit - Beta * Complexity + Log(Prior).
    """

    def __init__(self):
        # Simple deterministic hash-based RNG seed for consistency
        self._seed = 42
        # Common English stop words to simulate a simple linguistic prior
        self._stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", 
                           "being", "have", "has", "had", "do", "does", "did", "will", 
                           "would", "could", "should", "may", "might", "must", "shall", 
                           "can", "need", "dare", "ought", "used", "to", "of", "in", 
                           "for", "on", "with", "at", "by", "from", "as", "into", 
                           "through", "during", "before", "after", "above", "below", 
                           "between", "under", "again", "further", "then", "once"}
        self._beta = 0.1  # Compression penalty coefficient

    def _tokenize(self, text: str) -> List[str]:
        """Deterministic tokenizer: lower case, split by non-alphanumeric."""
        clean = "".join([c if c.isalnum() else " " for c in text.lower()])
        return [t for t in clean.split() if t]

    def _hash_val(self, s: str) -> float:
        """Deterministic float in (0, 1) based on string hash."""
        h = int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)
        return h / (16**8)

    def _compute_prior(self, tokens: List[str]) -> float:
        """
        Approximates log p_PCFG(z). 
        Rewards sequences that avoid stop-word heavy noise and have valid length.
        """
        if not tokens:
            return -10.0
        
        # Penalty for being too short or too long (simplified structural prior)
        length = len(tokens)
        length_score = -0.1 * abs(length - 5) # Prefer ~5 tokens as a 'constituent'
        
        # Reward density of non-stopwords (content words imply structure)
        content_words = [t for t in tokens if t not in self._stopwords]
        if len(tokens) == 0:
            return -10.0
        density = len(content_words) / len(tokens)
        
        return length_score + 2.0 * density

    def _compute_fit(self, prompt_tokens: set, candidate_tokens: set) -> float:
        """
        Approximates E[log p(x|z)]. 
        Uses Jaccard similarity to measure overlap between prompt context and answer.
        """
        if not prompt_tokens or not candidate_tokens:
            return 0.0
        intersection = len(prompt_tokens & candidate_tokens)
        union = len(prompt_tokens | candidate_tokens)
        if union == 0:
            return 0.0
        return 5.0 * (intersection / union)

    def _compute_complexity(self, candidate_tokens: List[str]) -> float:
        """
        Approximates Mutual Information I(x; z).
        Longer answers carry more information (higher cost).
        """
        return self._beta * len(candidate_tokens)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_tokens = set(self._tokenize(prompt))
        results = []

        for cand in candidates:
            cand_tokens = self._tokenize(cand)
            cand_set = set(cand_tokens)
            
            # 1. Compositional Prior
            prior = self._compute_prior(cand_tokens)
            
            # 2. Bayesian Fit (Likelihood)
            fit = self._compute_fit(prompt_tokens, cand_set)
            
            # 3. Information Bottleneck (Complexity Penalty)
            complexity_cost = self._compute_complexity(cand_tokens)
            
            # Total Variational Lower Bound (ELBO) approximation
            score = fit + prior - complexity_cost
            
            # Generate reasoning string
            reasoning = (f"Fit:{fit:.2f} Prior:{prior:.2f} Cost:{complexity_cost:.2f}")
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized ELBO score.
        Uses a sigmoid mapping of the internal score.
        """
        # Re-use logic from evaluate but for single item
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]["score"]
        
        # Map score to 0-1 using sigmoid-like function
        # Assuming typical scores range roughly -5 to 10
        mapped = 1.0 / (1.0 + math.exp(-0.5 * (score - 2.0)))
        return max(0.0, min(1.0, mapped))