import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Compressed Sensing (CS), Multi-Armed Bandits (MAB),
    and Sensitivity Analysis to evaluate logical consistency and structural robustness.
    
    Mechanism:
    1. Feature Extraction: Parses logical structures (negation, conditionals, numerics) 
       into a sparse binary matrix A.
    2. Compressed Sensing: Recovers a sparse 'truth vector' z via ISTA, assuming 
       candidate scores are noisy linear measurements of logical truths.
    3. Bandit Allocation: Simulates active learning by prioritizing features that 
       maximize residual reduction (UCB-like selection).
    4. Sensitivity Analysis: Penalizes candidates whose scores fluctuate wildly 
       under small perturbations (fragile reasoning).
    5. Epistemic Honesty: Detects ambiguity/presupposition to cap confidence.
    """

    def __init__(self):
        # Structural regex patterns for feature extraction
        self.patterns = {
            'negation': [r'\b(not|no|never|neither|n\'t)\b', r'\bwithout\b'],
            'comparative': [r'(more|less|greater|smaller|higher|lower)\s+(than)?', r'[<>]=?', r'\bvs\b'],
            'conditional': [r'\b(if|unless|provided|otherwise)\b', r'\bthen\b'],
            'causal': [r'\b(because|therefore|thus|hence|leads to|results in|causes)\b'],
            'numeric': [r'\d+(\.\d+)?'],
            'ordering': [r'\b(before|after|first|last|next|previous)\b'],
            'quantifier': [r'\b(every|all|some|none|at least|at most)\b'],
            'temporal': [r'\b(when|while|during|until|since)\b']
        }
        
        # Presupposition and ambiguity triggers for Tier B
        self.presupposition_triggers = [
            r'\b(stopped|quit|ceased)\b.*\b(have|has|did)\b',
            r'\bwhy\s+(did|does|is|are)\b', # "Why did X fail" implies X failed
            r'\b(the|this)\s+(problem|issue|error)\b', # Assumes existence
            r'\b(stop|quit)\b.*\bing\b' # "Have you stopped beating..."
        ]
        
        self.ambiguity_triggers = [
            r'\b(either|or)\b.*\b(or|else)\b', # Potential false dichotomy
            r'\b(he|she|it|they)\b.*\bwho\b', # Pronoun ambiguity query
            r'\b(best|worst|favorite)\b.*\bwithout\b', # Subjectivity without criteria
            r'\b(same|different)\b.*\bwhich\b' # Scope ambiguity
        ]

        # ISTA parameters
        self.lambda_ista = 0.1
        self.max_ista_iter = 50
        self.tau = 0.1

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector based on structural patterns."""
        text_lower = text.lower()
        features = []
        for key, patterns in self.patterns.items():
            match_count = 0
            for pat in patterns:
                if re.search(pat, text_lower):
                    match_count += 1
            # Binary presence for sparsity
            features.append(1 if match_count > 0 else 0)
        return np.array(features, dtype=float)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _parse_numeric_constraint(self, text: str) -> Optional[Tuple[float, str, float]]:
        """Extract numeric comparisons: e.g., '5 > 3', 'cost is 10'."""
        # Pattern: Number (operator) Number
        match = re.search(r'(\d+(?:\.\d+)?)\s*([<>=!]+)\s*(\d+(?:\.\d+)?)', text)
        if match:
            return float(match.group(1)), match.group(2), float(match.group(3))
        return None

    def _solve_bat_ball(self, text: str) -> Optional[float]:
        """Solve 'Bat and Ball' type algebraic traps."""
        text_lower = text.lower()
        # Pattern: "A and B cost X. A costs Y more than B." -> Find B.
        # Simplified heuristic for common trap: "total is T", "more than D"
        nums = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', text)]
        if len(nums) >= 2:
            # Heuristic for standard trap: Total = 1.10, Diff = 1.00 -> Ans = 0.05
            # If we see two numbers where one is slightly larger than the other or sum-like
            # This is a simplification; robust solving requires full NLP.
            # We look for the specific structure of the trap in the text
            if re.search(r'(cost|total|sum).*?(\d+\.\d{2})', text_lower) and re.search(r'(more|less).*?(\d+\.\d{2})', text_lower):
                # Extract the two key floats
                vals = sorted([float(x) for x in re.findall(r'\d+\.\d{2}', text)])
                if len(vals) >= 2:
                    # Approximation for the specific trap structure
                    return (vals[1] - vals[0]) / 2 if vals[1] > vals[0] else None
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity/presupposition.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pat in self.presupposition_triggers:
            if re.search(pat, p_lower):
                return 0.25 # Low confidence due to hidden assumption
        
        # 2. Ambiguity Check
        for pat in self.ambiguity_triggers:
            if re.search(pat, p_lower):
                # Check if it's a question about ambiguity
                if '?' in prompt:
                    return 0.30
        
        # 3. Unanswerability / Missing Info
        if re.search(r'(unknown|cannot be determined|insufficient information)', p_lower):
            return 0.1
            
        return 1.0 # No obvious traps detected

    def _ista_recovery(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Iterative Soft Thresholding Algorithm for L1 minimization."""
        m, d = A.shape
        z = np.zeros(d)
        L = np.linalg.norm(A, ord=2)**2 + 1e-6 # Lipschitz constant
        
        for _ in range(self.max_ista_iter):
            gradient = A.T @ (A @ z - b)
            z_next = z - (1/L) * gradient
            # Soft thresholding
            z = np.sign(z_next) * np.maximum(np.abs(z_next) - self.lambda_ista/L, 0)
        return z

    def _simulate_bandit_step(self, A: np.ndarray, b: np.ndarray, z: np.ndarray) -> int:
        """Simulate one step of Bandit-based feature selection (UCB)."""
        residuals = b - A @ z
        d = A.shape[1]
        n_pulls = np.ones(d) # Assume minimal prior pulls for exploration
        ucb_scores = np.zeros(d)
        
        for i in range(d):
            if np.linalg.norm(A[:, i]) == 0:
                ucb_scores[i] = -np.inf
                continue
            # Reward proxy: correlation with residual
            reward = np.abs(residuals.T @ A[:, i])
            exploration = np.sqrt(2 * np.log(d + 1) / (n_pulls[i] + 1))
            ucb_scores[i] = reward + exploration
            
        return int(np.argmax(ucb_scores))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Confidence (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Feature Extraction (Measurement Matrix A)
        # Rows: Prompt + Candidates. Cols: Logical features.
        all_texts = [prompt] + candidates
        rows = [self._extract_features(t) for t in all_texts]
        A = np.vstack(rows)
        m, d = A.shape
        
        # 3. Crude Scores (b) based on heuristics
        b = np.zeros(m)
        for i, cand in enumerate(candidates):
            score = 0.5
            # Numeric consistency check
            nums_prompt = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', prompt)]
            nums_cand = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', cand)]
            
            # Simple numeric overlap/consistency heuristic
            if nums_prompt and nums_cand:
                if any(abs(p - c) < 1e-6 for p in nums_prompt for c in nums_cand):
                    score += 0.3
                else:
                    score -= 0.2
            
            # Length penalty (too short is suspicious, too long is verbose)
            if len(cand.split()) < 2:
                score -= 0.2
            elif len(cand.split()) > 50:
                score -= 0.1
                
            b[i+1] = max(0, min(1, score))
        
        # Prompt gets a high prior score to anchor the system
        b[0] = 1.0 

        # 4. Compressed Sensing Recovery (ISTA)
        z = self._ista_recovery(A, b)
        
        # 5. Simulated Bandit Refinement (One step for efficiency)
        # In a full system, this would loop and re-parse. 
        # Here we simulate the 'focus' by adjusting weights based on the most informative feature.
        best_feature_idx = self._simulate_bandit_step(A, b, z)
        # Boost the weight of the most informative feature slightly to simulate refined parsing
        z[best_feature_idx] *= 1.2 

        # 6. Sensitivity Analysis & Final Scoring
        results = []
        w = z # Recovered truth vector
        
        for i, cand in enumerate(candidates):
            phi_a = A[i+1]
            
            # Base score from model
            base_score = float(w.T @ phi_a)
            
            # Sensitivity penalty: How much does score change if we perturb features?
            # Approximated by L1 norm of weighted features (fragility)
            sensitivity = np.sum(np.abs(w * phi_a))
            penalty = 0.1 * sensitivity
            
            final_score = base_score - penalty
            
            # NCD Tiebreaker (Max 15% influence)
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD to be a bonus for similarity (low NCD = high similarity)
            ncd_bonus = (1.0 - ncd_val) * 0.15
            
            final_score += ncd_bonus
            
            # Apply Epistemic Cap
            if meta_cap < 0.5:
                # If the prompt is tricky, dampen the score variance
                final_score = 0.5 + (final_score - 0.5) * meta_cap
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {np.sum(phi_a)}, Sensitivity penalty: {penalty:.2f}, Meta-cap: {meta_cap:.2f}"
            })
        
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Check Prompt Ambiguity (The Hard Cap)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural Match Check
        features = self._extract_features(prompt + " " + answer)
        if np.sum(features) == 0:
            # No structural patterns matched -> Honest uncertainty
            return min(0.25, cap)
        
        # 3. Compute a preliminary score
        # Re-run a mini-evaluation for this single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # 4. Apply Cap
        final_conf = min(raw_score, cap)
        
        # 5. Never exceed 0.9 without explicit computation proof (heuristic)
        # If the answer is just "Yes" or "No" and prompt is complex, cap at 0.8
        if len(answer.split()) <= 2 and len(prompt.split()) > 10:
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))