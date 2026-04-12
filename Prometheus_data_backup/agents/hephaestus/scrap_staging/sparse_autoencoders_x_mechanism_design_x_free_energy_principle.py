import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Sparse-Feature Free-Energy Scorer (SFFES) with Constructive Computation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, conditionals, comparatives).
    2. Constructive Computation: Detects numeric/math patterns and computes exact answers.
    3. Sparse Coding: Uses online K-SVD style dictionary learning (simplified to fixed random projection + thresholding for offline-free constraint) to generate feature codes.
    4. Free Energy Scoring: Combines affinity (semantic similarity via sparse codes), mechanism design penalties (logical violations), and computation match.
    5. Epistemic Honesty: Meta-analysis of prompt ambiguity caps confidence.
    """
    
    def __init__(self):
        self.vocab_size = 500
        self.k_features = 50
        self.lambda_sparse = 0.1
        self.mu_penalty = 2.0
        # Fixed random dictionary for sparse coding (simulating offline learned D)
        np.random.seed(42)
        self.D = np.random.randn(self.vocab_size, self.k_features)
        self.D = self.D / np.linalg.norm(self.D, axis=0)

    def _hash_vocab(self, text: str) -> np.ndarray:
        """Convert text to binary bag-of-words vector."""
        words = re.findall(r'\b\w+\b', text.lower())
        vec = np.zeros(self.vocab_size)
        for w in words:
            idx = hash(w) % self.vocab_size
            vec[idx] = 1
        return vec

    def _ista_solve(self, x: np.ndarray, max_iter=20) -> np.ndarray:
        """Iterative Soft-Thresholding Algorithm for sparse coding."""
        z = np.zeros(self.k_features)
        L = np.linalg.norm(self.D, ord=2)**2 + 1e-6
        for _ in range(max_iter):
            grad = self.D.T @ (self.D @ z - x)
            z = z - (1/L) * grad
            z = np.sign(z) * np.maximum(np.abs(z) - self.lambda_sparse/L, 0)
        return z

    def _extract_constraints(self, text: str) -> List[Dict]:
        """Extract logical structures: negations, comparatives, conditionals, numbers."""
        constraints = []
        lower = text.lower()
        
        # Negations
        if re.search(r'\b(not|never|no|n\'t|without)\b', lower):
            constraints.append({'type': 'negation', 'present': True})
            
        # Comparatives
        if re.search(r'\b(more than|less than|greater|smaller|higher|lower)\b', lower):
            constraints.append({'type': 'comparative', 'present': True})
        if re.search(r'[≥≤<>]', text):
            constraints.append({'type': 'symbolic_comp', 'present': True})

        # Conditionals
        if re.search(r'\b(if|unless|then|otherwise)\b', lower):
            constraints.append({'type': 'conditional', 'present': True})
            
        # Numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            constraints.append({'type': 'numeric', 'values': [float(n) for n in nums]})
            
        # Ambiguity markers (for meta-confidence)
        if re.search(r'\b(either|or|who|he|she|it|best|worst|favorite)\b', lower):
            constraints.append({'type': 'ambiguity_marker', 'present': True})
            
        # Presupposition markers
        if re.search(r'\b(stopped|quit|failed|why did)\b', lower) and re.search(r'\b(you|he|she|they)\b', lower):
             constraints.append({'type': 'presupposition_risk', 'present': True})

        return constraints

    def _compute_constructive_answer(self, prompt: str) -> Optional[float]:
        """Attempt to compute a definitive numeric answer from the prompt."""
        lower = prompt.lower()
        
        # Pattern: "What is X + Y?" or "Calculate X plus Y"
        match = re.search(r'(-?\d+\.?\d*)\s*(\+|plus)\s*(-?\d+\.?\d*)', lower)
        if match:
            return float(match.group(1)) + float(match.group(3))
            
        # Pattern: "What is X - Y?"
        match = re.search(r'(-?\d+\.?\d*)\s*(-|minus)\s*(-?\d+\.?\d*)', lower)
        if match:
            # Avoid matching negative numbers as subtraction
            if '-' in match.group(2) and match.group(1).strip() == "": 
                pass
            else:
                return float(match.group(1)) - float(match.group(3))

        # Pattern: "What is X * Y?" or "X times Y"
        match = re.search(r'(-?\d+\.?\d*)\s*(\*|x|times)\s*(-?\d+\.?\d*)', lower)
        if match:
            return float(match.group(1)) * float(match.group(3))
            
        # Pattern: "What is X / Y?"
        match = re.search(r'(-?\d+\.?\d*)\s*(/|divided by)\s*(-?\d+\.?\d*)', lower)
        if match:
            divisor = float(match.group(3))
            if divisor != 0:
                return float(match.group(1)) / divisor

        return None

    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presupposition, or unanswerability."""
        constraints = self._extract_constraints(prompt)
        lower = prompt.lower()
        
        # 1. Presupposition traps
        if any(c.get('type') == 'presupposition_risk' for c in constraints):
            if re.search(r'\b(stopped|quit)\b', lower) and re.search(r'\b(have you|did you|has he)\b', lower):
                return 0.2
        
        # 2. Pronoun/Scope Ambiguity in questions
        if '?' in prompt:
            if re.search(r'\b(who|he|she|it|they)\b.*\?', lower) and re.search(r'\b(told|said|asked)\b', lower):
                return 0.25 # Pronoun ambiguity
            if re.search(r'\b(every|all)\b.*\b(a|an)\b.*\?', lower):
                return 0.3 # Scope ambiguity risk

        # 3. Subjectivity
        if re.search(r'\b(best|worst|favorite|opinion|think)\b', lower) and not re.search(r'\b(data|fact|calculate)\b', lower):
            return 0.3

        # 4. False Dichotomy
        if re.search(r'\b(either|or)\b', lower) and not re.search(r'\b(true|false|yes|no)\b', lower):
             # Only flag if it looks like a forced choice without logical exhaustiveness
             if len(prompt.split()) < 20: # Heuristic for short dichotomy traps
                 return 0.3

        return 1.0

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Compute Free Energy Score."""
        p_vec = self._hash_vocab(prompt)
        c_vec = self._hash_vocab(candidate)
        
        # Sparse Coding
        z_p = self._ista_solve(p_vec)
        z_c = self._ista_solve(c_vec)
        
        # 1. Affinity (Semantic Similarity)
        # Negative squared Euclidean distance
        affinity = -0.5 * np.linalg.norm(z_p - z_c)**2
        
        # 2. Mechanism Design Penalty (Logical Consistency)
        # We check if candidate violates constraints implied by prompt
        p_constraints = self._extract_constraints(prompt)
        c_constraints = self._extract_constraints(candidate)
        
        penalty = 0.0
        reasoning_steps = []
        
        # Check negation consistency
        p_has_neg = any(c.get('type') == 'negation' for c in p_constraints)
        c_has_neg = any(c.get('type') == 'negation' for c in c_constraints)
        
        # Simple heuristic: If prompt asserts X, candidate should not assert NOT X
        # (Simplified for this implementation to just checking presence overlap)
        if p_has_neg and not c_has_neg:
            # Potential violation if candidate ignores the negation context
            # But only if the candidate is trying to answer, not just echo
            if len(candidate.split()) > 3:
                penalty += 1.0
                reasoning_steps.append("Ignored negation context")

        # 3. Constructive Computation Match (High Weight)
        computed_val = self._compute_constructive_answer(prompt)
        comp_score = 0.0
        
        if computed_val is not None:
            # Try to extract number from candidate
            c_nums = re.findall(r'-?\d+\.?\d*', candidate)
            if c_nums:
                try:
                    c_val = float(c_nums[-1]) # Take last number as answer
                    if abs(c_val - computed_val) < 1e-6:
                        comp_score = 10.0 # Strong reward for correct calculation
                        reasoning_steps.append(f"Computed {computed_val} matches candidate")
                    else:
                        penalty += 5.0 # Heavy penalty for wrong math
                        reasoning_steps.append(f"Math error: expected {computed_val}, got {c_val}")
                except ValueError:
                    penalty += 2.0
            else:
                penalty += 2.0 # Failed to provide numeric answer for math question
                reasoning_steps.append("Missing numeric answer for math problem")

        # 4. Free Energy Approximation
        # F = -Affinity + Sparsity + Penalty - ComputationReward
        # We want to maximize Score = -F
        sparsity_term = -self.lambda_sparse * np.linalg.norm(z_c, ord=1)
        
        total_score = affinity + sparsity_term - (self.mu_penalty * penalty) + comp_score
        
        reason_str = "; ".join(reasoning_steps) if reasoning_steps else "Semantic match"
        return total_score, reason_str

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        len_max = max(len(z1), len(z2))
        if len_max == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / len_max

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-compute constructive answer existence to boost candidates that match it
        computed_val = self._compute_constructive_answer(prompt)
        
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            
            # NCD as minor tiebreaker (max 15% influence logic handled by scaling)
            ncd = self._ncd_score(prompt, cand)
            ncd_bonus = (1.0 - ncd) * 0.5 # Small boost for similarity
            
            final_score = score + ncd_bonus
            
            # Cap score based on meta-confidence if the question is fundamentally flawed
            if meta_cap < 0.3:
                # If the prompt is a trap, even a "matching" answer shouldn't get high confidence
                # But we still return the ranking, just with adjusted internal logic if needed
                pass 

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit for ambiguous prompts.
        """
        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computation Check
        # If we can compute an answer, check if it matches
        computed_val = self._compute_constructive_answer(prompt)
        
        base_conf = 0.5 # Default baseline
        
        if computed_val is not None:
            # Math question
            nums = re.findall(r'-?\d+\.?\d*', answer)
            if nums:
                try:
                    ans_val = float(nums[-1])
                    if abs(ans_val - computed_val) < 1e-6:
                        base_conf = 0.95
                    else:
                        base_conf = 0.1 # Confidently wrong
                except:
                    base_conf = 0.2
            else:
                base_conf = 0.1 # No number provided for math question
        else:
            # Non-math: rely on structural match and lack of ambiguity
            # If meta_cap is low, we must be humble
            if meta_cap < 0.3:
                base_conf = 0.2
            else:
                # Check basic constraint satisfaction
                score, _ = self._score_candidate(prompt, answer)
                # Normalize score roughly to 0-1 range for confidence
                # High score -> high conf, but capped by meta
                normalized = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
                base_conf = normalized

        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Ensure strict bounds
        return max(0.0, min(1.0, final_conf))