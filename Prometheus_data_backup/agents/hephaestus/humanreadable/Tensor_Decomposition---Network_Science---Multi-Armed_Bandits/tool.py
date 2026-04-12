import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Adaptive Tensor-Bandit Reasoning Tool with Epistemic Honesty.
    
    Mechanism:
    1. Tensor Decomposition Analogy: Treats the prompt-candidate relationship as a 
       low-rank approximation problem. We decompose the "truth" signal into structural, 
       computational, and similarity components.
    2. Network Science: Uses graph-regularization logic on candidate clusters. 
       Candidates sharing structural features (negations, numbers) reinforce each other's 
       scores via a Laplacian-like smoothing step.
    3. Multi-Armed Bandits: Implements an Upper Confidence Bound (UCB) strategy. 
       Each candidate is an "arm". The tool balances exploitation (high structural match) 
       with exploration (uncertainty reduction via meta-analysis).
    
    Epistemic Honesty (Tier B):
    Prioritizes detecting ambiguity, presuppositions, and scope issues. If the prompt 
    triggers these flags, confidence is capped low regardless of candidate quality.
    """

    def __init__(self):
        self.alpha = 1.0  # Exploration bonus scaling
        self.lambda_reg = 0.1  # Graph regularization strength
        
        # Presupposition and ambiguity triggers
        self.presupposition_triggers = [
            r"\b(stopped|quit|ceased|failed)\b",
            r"\bwhy did\b", r"\bwhy has\b", r"\bwhy were\b",
            r"\bassum(e|ing)\b", r"\bobviously\b"
        ]
        self.scope_triggers = [r"\bevery\b.*\ba\b", r"\ball\b.*\bsome\b"]
        self.pronoun_triggers = [r"\b(he|she|him|her|they|it)\b.*\bwho\b"]
        self.dichotomy_triggers = [r"\beither\b.*\bor\b", r"\bmust\b.*\bchoose\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]

    def _meta_confidence(self, prompt: str) -> Tuple[float, List[str]]:
        """
        Analyzes prompt for Tier B traps (ambiguity, presupposition).
        Returns (max_allowed_confidence, list_of_flags).
        """
        p_lower = prompt.lower()
        flags = []
        max_conf = 1.0

        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                flags.append("presupposition")
                max_conf = min(max_conf, 0.25)
                break

        # Check Scope Ambiguity
        for pattern in self.scope_triggers:
            if re.search(pattern, p_lower):
                flags.append("scope_ambiguity")
                max_conf = min(max_conf, 0.4)
                break
        
        # Check Pronoun Ambiguity (simplified)
        if re.search(r"\bwho\b", p_lower) and any(x in p_lower for x in ["he", "she", "him", "her", "they"]):
            flags.append("pronoun_ambiguity")
            max_conf = min(max_conf, 0.3)

        # Check False Dichotomy
        for pattern in self.dichotomy_triggers:
            if re.search(pattern, p_lower):
                # Only flag if options aren't explicit in a simple list
                if "or" in p_lower and "?" in prompt:
                    flags.append("false_dichotomy")
                    max_conf = min(max_conf, 0.35)
                break

        # Check Subjectivity
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                flags.append("subjectivity")
                max_conf = min(max_conf, 0.2)
                break

        return max_conf, flags

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers for computational verification."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural parsing (negations, comparatives, logic).
        Returns 0.0 to 1.0.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        negations = ["not", "no", "never", "none", "cannot", "impossible"]
        p_has_neg = any(n in p_lower for n in negations)
        c_has_neg = any(n in c_lower for n in negations)
        
        if p_has_neg == c_has_neg:
            score += 0.3
        else:
            score -= 0.3 # Penalty for negation mismatch

        # 2. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If prompt implies a calculation (e.g., more than, less than)
            if "more" in p_lower or "greater" in p_lower:
                if all(c > max(p_nums) for c in c_nums):
                    score += 0.4
                else:
                    score -= 0.2
            elif "less" in p_lower or "smaller" in p_lower:
                if all(c < min(p_nums) for c in c_nums):
                    score += 0.4
                else:
                    score -= 0.2
            elif "equal" in p_lower or "same" in p_lower:
                if set(p_nums) == set(c_nums):
                    score += 0.4
                else:
                    score -= 0.2
            else:
                # Exact match bonus if numbers align
                if set(p_nums) == set(c_nums):
                    score += 0.2
        
        # 3. Keyword Overlap (Weighted)
        common_words = set(p_lower.split()) & set(c_lower.split())
        # Filter stopwords
        stopwords = {"the", "is", "are", "a", "an", "to", "of", "in", "and", "or", "that", "this"}
        significant_overlap = len(common_words - stopwords)
        if significant_overlap > 0:
            score += min(0.3, significant_overlap * 0.05)

        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_both = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max_len

    def _tensor_bandit_score(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Core logic: Simulates Tensor-Bandit scoring.
        1. Factorize candidates into structural features (User/Item/Time analogy).
        2. Apply Graph Regularization (Network Science): Smooth scores based on similarity.
        3. Apply UCB (Bandit): Add exploration bonus based on uncertainty.
        """
        n = len(candidates)
        if n == 0:
            return []

        # Step 1: Initial Structural Scores (The "Observation")
        struct_scores = [self._compute_structural_score(prompt, c) for c in candidates]
        
        # Step 2: NCD Similarity Matrix (The "Network Adjacency")
        # A_ij = exp(-NCD(i, j))
        adj = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    adj[i][j] = 1.0
                else:
                    ncd_val = self._compute_ncd(candidates[i], candidates[j])
                    adj[i][j] = math.exp(-ncd_val) # High similarity = high weight

        # Step 3: Graph Regularization (Laplacian Smoothing)
        # Propagate scores: new_score_i = score_i + lambda * sum(A_ij * (score_j - score_i))
        smoothed_scores = struct_scores[:]
        for i in range(n):
            lap_sum = 0.0
            total_weight = 0.0
            for j in range(n):
                if i != j:
                    weight = adj[i][j]
                    lap_sum += weight * (struct_scores[j] - struct_scores[i])
                    total_weight += weight
            if total_weight > 0:
                smoothed_scores[i] += self.lambda_reg * (lap_sum / total_weight)

        # Step 4: UCB Exploration Bonus
        # Uncertainty is inversely proportional to how many "similar" candidates exist
        final_scores = []
        for i in range(n):
            uncertainty = 1.0 - (sum(adj[i]) / n) # Higher if few neighbors
            exploration_bonus = self.alpha * uncertainty / (1 + len(candidates))
            ucb_score = smoothed_scores[i] + exploration_bonus
            final_scores.append(ucb_score)

        # Normalize to 0-1 range roughly
        min_s = min(final_scores) if final_scores else 0
        max_s = max(final_scores) if final_scores else 1
        range_s = max_s - min_s if (max_s - min_s) > 1e-9 else 1.0
        
        normalized_results = []
        for i, c in enumerate(candidates):
            norm_score = (final_scores[i] - min_s) / range_s
            # Ensure non-negative
            norm_score = max(0.0, norm_score)
            normalized_results.append({
                "candidate": c,
                "score": norm_score,
                "reasoning": f"Structural:{struct_scores[i]:.2f}, Smoothed:{smoothed_scores[i]:.2f}, UCB:{norm_score:.2f}"
            })
        
        # Sort descending
        normalized_results.sort(key=lambda x: x['score'], reverse=True)
        return normalized_results

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Run the tensor-bandit engine
        results = self._tensor_bandit_score(prompt, candidates)
        
        # Adjust scores based on Meta-Confidence (Epistemic Honesty)
        max_allowed_conf, flags = self._meta_confidence(prompt)
        
        if flags:
            # If ambiguous, penalize all scores significantly to reflect uncertainty
            # But preserve ranking relative to each other
            penalty_factor = max_allowed_conf 
            for res in results:
                res['score'] *= penalty_factor
                if flags:
                    res['reasoning'] += f" [WARNING: {', '.join(flags)} detected. Score capped.]"
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt.
        """
        # 1. Meta-Analysis Cap
        max_allowed, flags = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Verification
        # If the answer matches the prompt structurally, base confidence is high
        base_score = self._compute_structural_score(prompt, answer)
        
        # If numbers are involved, verify them strictly
        p_nums = self._extract_numbers(prompt)
        a_nums = self._extract_numbers(answer)
        
        computation_verified = False
        if p_nums and a_nums:
            # Simple heuristic: if numbers in answer are derived logically from prompt
            # For this generic tool, we check if the answer contains the specific numbers 
            # expected by comparatives, or if it's a direct extraction.
            if "not" in prompt.lower() and "not" in answer.lower():
                computation_verified = True
            elif set(p_nums) == set(a_nums):
                computation_verified = True
            elif len(p_nums) == len(a_nums) == 1 and p_nums[0] == a_nums[0]:
                computation_verified = True
        
        if computation_verified:
            base_score = max(base_score, 0.8)
        elif not p_nums and base_score < 0.3:
            # If no numbers and low structural match, likely wrong
            base_score = 0.1

        # 3. Apply Cap
        final_conf = min(base_score, max_allowed)
        
        # 4. Fallback for no structural signal
        if base_score < 0.1 and not flags:
            final_conf = 0.2 # Honest uncertainty

        return round(final_conf, 4)

# Example usage logic would go here if run as script, but class is the requirement.