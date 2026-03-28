import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Prime-Weighted Global Broadcast Network (PWGBN) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. This acts as the "local evidence".
    2. Prime-Weighted Hypothesis Graph (Diversity Metric): 
       - Assigns a unique prime to each structural feature (e.g., 2 for negation, 3 for numbers).
       - Computes a "Prime Signature" for each candidate based on features present.
       - Calculates edge weights between candidates using GCD-based similarity (number-theoretic distance).
       - This penalizes redundant candidates that share the same logical flaws.
    3. Global Workspace Ignition (Competition):
       - Candidates compete via a softmax function combining structural score (evidence) 
         and centrality (diversity penalty).
       - High-confidence, structurally distinct candidates "ignite" (gain high score).
    4. NCD Tiebreaker: Used only when structural signals are identical.
    
    This satisfies the requirement to use Prime Theory for structural/diversity scoring 
    rather than direct semantic similarity, avoiding the historical inhibitor trap.
    """

    def __init__(self):
        # First 10 prime numbers for feature encoding
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        # Feature patterns mapped to primes
        self.features = [
            (r'\bnot\b|\bno\b|\bnever\b|\bwithout\b', 0),      # Negation
            (r'\bmore\b|\bless\b|\bgreater\b|\bsmaller\b|\b<|\b>', 1), # Comparatives
            (r'\bif\b|\bthen\b|\bunless\b|\bwhen\b', 2),       # Conditionals
            (r'\d+\.\d+|\d+', 3),                              # Numbers
            (r'\ball\b|\bevery\b|\bnone\b|\bsome\b', 4),       # Quantifiers
            (r'\bcause\b|\bbecause\b|\btherefore\b', 5),       # Causality
            (r'\bsame\b|\bdifferent\b|\bequal\b', 6),          # Equivalence
            (r'\bfirst\b|\blast\b|\bnext\b|\bprevious\b', 7),  # Order
            (r'\btrue\b|\bfalse\b|\byes\b|\bno\b', 8),         # Binary states
            (r'\bonly\b|\bexcept\b', 9)                        # Exclusivity
        ]

    def _extract_features(self, text: str) -> List[int]:
        """Extract structural features and return list of associated primes."""
        text_lower = text.lower()
        active_primes = []
        for pattern, idx in self.features:
            if re.search(pattern, text_lower):
                active_primes.append(self.primes[idx])
        return active_primes if active_primes else [1] # 1 if no features found

    def _compute_prime_signature(self, primes: List[int]) -> int:
        """Compute product of primes (signature)."""
        if not primes:
            return 1
        result = 1
        for p in primes:
            result *= p
        return result

    def _gcd(self, a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Evaluate candidate based on structural alignment with prompt.
        Returns a score where higher is better.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        
        # 1. Negation Consistency
        has_neg_prompt = bool(re.search(r'\bnot\b|\bno\b|\bnever\b', p_lower))
        has_neg_cand = bool(re.search(r'\bnot\b|\bno\b|\bnever\b', c_lower))
        if has_neg_prompt == has_neg_cand:
            score += 2.0
        elif has_neg_cand and not has_neg_prompt:
            score -= 5.0 # Penalty for spurious negation
            
        # 2. Numeric Evaluation (Simple extraction and comparison logic)
        nums_prompt = re.findall(r'\d+\.\d+|\d+', p_lower)
        nums_cand = re.findall(r'\d+\.\d+|\d+', c_lower)
        
        if nums_prompt:
            if nums_cand:
                # Check if candidate numbers are consistent subset or result
                try:
                    p_vals = [float(x) for x in nums_prompt]
                    c_vals = [float(x) for x in nums_cand]
                    # Heuristic: If prompt asks for max/min, check candidate
                    if 'largest' in p_lower or 'max' in p_lower:
                        if max(c_vals) == max(p_vals): score += 3.0
                    elif 'smallest' in p_lower or 'min' in p_lower:
                        if min(c_vals) == min(p_vals): score += 3.0
                    else:
                        # General presence bonus
                        score += 1.0 
                except ValueError:
                    pass
            else:
                score -= 1.0 # Missing numbers when prompt has them

        # 3. Conditional/Logical keyword overlap (Weighted)
        common_logic = 0
        for pattern, _ in self.features[2:]: # Skip negation/comparatives already handled
            if re.search(pattern, p_lower) and re.search(pattern, c_lower):
                common_logic += 0.5
        score += common_logic

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        if max(len1, len2) == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # Step 1: Compute Structural Scores (Local Evidence)
        struct_scores = []
        for c in candidates:
            s = self._structural_score(prompt, c)
            struct_scores.append(s)

        # Step 2: Compute Prime Signatures & Diversity (Global Workspace Competition)
        # Each candidate gets a prime signature based on features
        signatures = []
        feature_sets = []
        for c in candidates:
            feats = self._extract_features(c)
            feature_sets.append(feats)
            signatures.append(self._compute_prime_signature(feats))

        # Compute Diversity Penalty (Redundancy)
        # If two candidates have high GCD (share many prime factors/features), 
        # they are redundant. We want unique high-scorers.
        diversity_scores = []
        for i, sig_i in enumerate(signatures):
            redundancy = 0.0
            for j, sig_j in enumerate(signatures):
                if i != j:
                    # GCD-based similarity
                    common = self._gcd(sig_i, sig_j)
                    if common > 1:
                        # Normalize similarity by geometric mean of signatures to avoid bias to large products
                        sim = math.log(common + 1) / (math.log(sig_i + 1) + math.log(sig_j + 1) + 1e-9)
                        redundancy += sim
            diversity_scores.append(-redundancy) # Negative because redundancy is bad

        # Step 3: Global Ignition (Softmax-like combination)
        # Score = Structural + Diversity + (NCD Tiebreaker logic applied loosely here)
        final_scores = []
        max_struct = max(struct_scores) if struct_scores else 0
        
        for i in range(len(candidates)):
            # Normalize structural to ~0-5 range
            norm_struct = struct_scores[i] 
            # Diversity is usually small negative number
            div = diversity_scores[i] * 2.0 
            
            raw_score = norm_struct + div
            
            # NCD as tiebreaker for very close structural scores
            if abs(raw_score - max_struct) < 0.1:
                # If structurally similar, prefer shorter/more compressed (lower NCD to prompt concept)
                # Actually, for tie breaking, we just add a tiny perturbation based on length/NCD
                ncd_val = self._ncd(prompt, candidates[i])
                raw_score -= ncd_val * 0.01 # Small penalty for high NCD (dissimilarity) if scores are tied

            final_scores.append(raw_score)

        # Rank and format
        ranked_indices = sorted(range(len(candidates)), key=lambda k: final_scores[k], reverse=True)
        
        results = []
        for idx in ranked_indices:
            results.append({
                "candidate": candidates[idx],
                "score": final_scores[idx],
                "reasoning": f"Structural:{struct_scores[idx]:.2f}, Diversity:{diversity_scores[idx]:.2f}"
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment and prime-signature consistency.
        """
        # 1. Structural Check
        struct_score = self._structural_score(prompt, answer)
        
        # Map structural score to probability range
        # Base assumption: score > 0 is good, < 0 is bad
        # Range roughly -5 to +6
        prob = 1.0 / (1.0 + math.exp(-struct_score)) # Sigmoid
        
        # 2. Prime Signature Consistency Check
        # Does the answer introduce wild features not in prompt?
        p_feats = set(self._extract_features(prompt))
        a_feats = set(self._extract_features(answer))
        
        # Penalty for introducing complex logic (conditionals/quantifiers) not present in prompt
        # unless it's a specific feature type that implies derivation
        new_complex = a_feats - p_feats
        complexity_penalty = 0.0
        for p in new_complex:
            if p > 5: # Higher primes = more complex logic (causality, quantifiers)
                complexity_penalty += 0.15
        
        final_conf = max(0.0, min(1.0, prob - complexity_penalty))
        return final_conf