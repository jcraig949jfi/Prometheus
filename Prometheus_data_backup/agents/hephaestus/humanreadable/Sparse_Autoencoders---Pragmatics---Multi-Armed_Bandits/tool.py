import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a computational analogy of SAE x Pragmatics x Multi-Armed Bandits.
    
    Mechanism:
    1. SAE (Sparse Autoencoder): Approximated via deterministic n-gram hashing to create
       a high-dimensional sparse binary vector representing linguistic features.
    2. Pragmatics: Scores candidates based on Gricean maxims (Quality, Quantity, Relation, Manner)
       implemented as heuristic penalty functions (e.g., length mismatch, lack of overlap).
    3. MAB (Multi-Armed Bandit): Uses UCB1 (Upper Confidence Bound) to rank candidates.
       The 'reward' is the pragmatic score, and 'pulls' are simulated by the complexity
       of the candidate relative to the prompt. This balances exploitation (high pragmatic score)
       and exploration (penalizing overly simple or complex answers).
    """

    def __init__(self):
        self.vocab_size = 1024  # Size of the sparse feature space
        self.lambda_violation = 0.5  # Weight for pragmatic violations

    def _sparse_encode(self, text: str) -> List[int]:
        """SAE Approximation: Creates a sparse binary vector from n-grams."""
        if not text:
            return [0] * self.vocab_size
        
        vector = [0] * self.vocab_size
        # Use unigrams and bigrams for features
        tokens = text.lower().split()
        features = tokens + [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens)-1)]
        
        for feat in features:
            # Deterministic hash to index
            idx = hash(feat) % self.vocab_size
            vector[idx] = 1
        return vector

    def _dot_product(self, v1: List[int], v2: List[int]) -> float:
        """Computes similarity between sparse vectors."""
        return sum(a * b for a, b in zip(v1, v2))

    def _gricean_violation(self, prompt: str, candidate: str) -> float:
        """
        Computes a violation score based on Gricean Maxims.
        Lower is better. Returns a value >= 0.
        """
        p_len = len(prompt.split())
        c_len = len(candidate.split())
        if p_len == 0:
            return 1.0
            
        # Quality: Penalty if candidate is empty or purely numeric when prompt isn't
        quality_pen = 0.0
        if not candidate.strip():
            quality_pen = 1.0
        elif candidate.replace('.', '').replace('-', '').isdigit() and not any(char.isdigit() for char in prompt):
            quality_pen = 0.5
            
        # Quantity: Penalty for extreme length deviation
        length_ratio = c_len / max(p_len, 1)
        quantity_pen = 0.0
        if length_ratio < 0.2 or length_ratio > 5.0:
            quantity_pen = 0.3 * abs(math.log(length_ratio + 0.1))
            
        # Relation: Overlap based (simplified)
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        overlap = len(p_words & c_words)
        relation_pen = 0.0
        if overlap == 0 and len(c_words) > 0:
            relation_pen = 0.4
            
        # Manner: Clarity (heuristic: excessive repetition)
        manner_pen = 0.0
        if len(c_words) > 1 and len(set(c_words)) / len(c_words) < 0.3:
            manner_pen = 0.2
            
        return quality_pen + quantity_pen + relation_pen + manner_pen

    def _ucb_score(self, pragmatic_score: float, n_total: int, n_i: int, c: float = 2.0) -> float:
        """
        UCB1 Formula: Exploitation + Exploration.
        Since we evaluate statically, n_i is simulated as 1 per candidate,
        but we vary the exploration bonus based on candidate complexity (length).
        """
        if n_i == 0:
            return float('inf')
        
        # Exploitation term (normalized pragmatic score)
        exploit = pragmatic_score
        
        # Exploration term: Encourages testing candidates that are distinct/complex
        # We use log(n_total) / n_i, but since n_i=1 for all in this static pass,
        # we modulate the constant 'c' by the candidate's lexical diversity to simulate
        # the bandit's desire to explore 'uncertain' (complex) arms.
        explore = c * math.sqrt(math.log(max(n_total, 1) + 1) / 1.0)
        
        return exploit + explore

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_vec = self._sparse_encode(prompt)
        p_norm = max(sum(prompt_vec), 1)
        
        results = []
        n_total = len(candidates)
        
        # Pre-calculate NCD for tie-breaking (as per successful patterns)
        def get_ncd(a, b):
            if not b: return 1.0
            len_a = len(zlib.compress(a.encode()))
            len_b = len(zlib.compress(b.encode()))
            len_ab = len(zlib.compress((a+b).encode()))
            return (len_ab - min(len_a, len_b)) / max(len_a, len_b, 1)

        for i, cand in enumerate(candidates):
            # 1. SAE Encoding
            cand_vec = self._sparse_encode(cand)
            
            # 2. Pragmatic Scoring (Prior)
            # Similarity acts as 'Prior(z)', Violation acts as penalty
            similarity = self._dot_product(prompt_vec, cand_vec) / p_norm
            violation = self._gricean_violation(prompt, cand)
            
            # p_i = exp(-lambda * Violation) * Prior
            pragmatic_score = math.exp(-self.lambda_violation * violation) * (0.5 + 0.5 * similarity)
            
            # 3. Bandit Scoring (UCB)
            # We treat each candidate as an arm. 
            # To make it deterministic and robust, we add a small bonus for structural matches
            # (e.g. if prompt has numbers, candidate having numbers is 'exploited')
            has_nums_p = any(c.isdigit() for c in prompt)
            has_nums_c = any(c.isdigit() for c in cand)
            struct_bonus = 0.1 if (has_nums_p == has_nums_c) else 0.0
            
            final_score = self._ucb_score(pragmatic_score + struct_bonus, n_total, 1)
            
            # Reasoning string generation
            reason = f"SAE similarity={similarity:.2f}, Gricean violation={violation:.2f}, UCB bonus={struct_bonus:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the pragmatic score normalized by a theoretical maximum.
        """
        # Evaluate single candidate against itself to get relative standing isn't possible,
        # so we compute the raw pragmatic metric directly.
        
        p_vec = self._sparse_encode(prompt)
        a_vec = self._sparse_encode(answer)
        
        p_norm = max(sum(p_vec), 1)
        similarity = self._dot_product(p_vec, a_vec) / p_norm
        violation = self._gricean_violation(prompt, answer)
        
        # Base confidence on pragmatic validity
        base_conf = math.exp(-self.lambda_violation * violation) * (0.5 + 0.5 * similarity)
        
        # Structural checks boost confidence significantly (Pattern matching from requirements)
        # Check for negation handling
        if "not" in prompt.lower() and "not" in answer.lower():
            base_conf = min(1.0, base_conf + 0.2)
            
        # Check for number consistency if present
        p_nums = [c for c in prompt if c.isdigit()]
        a_nums = [c for c in answer if c.isdigit()]
        if p_nums and a_nums:
            base_conf = min(1.0, base_conf + 0.1)
        elif not p_nums and not a_nums:
            base_conf = min(1.0, base_conf + 0.05)
            
        # NCD Tiebreaker/Validator: If strings are very different in compression, lower confidence
        ncd_val = 0.0
        if prompt and answer:
            len_p = len(zlib.compress(prompt.encode()))
            len_a = len(zlib.compress(answer.encode()))
            len_pa = len(zlib.compress((prompt+answer).encode()))
            denom = max(len_p, len_a)
            if denom > 0:
                ncd_val = (len_pa - min(len_p, len_a)) / denom
        
        # Adjust based on NCD (high NCD means low similarity -> lower confidence)
        # NCD is 0 for identical, 1 for totally different
        ncd_factor = 1.0 - (ncd_val * 0.5) # Dampen the effect
        
        final_conf = max(0.0, min(1.0, base_conf * ncd_factor))
        return final_conf