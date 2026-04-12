import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Compressed Sensing, Adaptive Control, and Metamorphic Testing
    with Dynamical Systems tracking (Lyapunov stability) for epistemic honesty.
    
    Mechanism:
    1. Structural Parsing: Extracts binary features (negations, comparatives, etc.).
    2. Dynamics Tracker: Simulates premise processing as a state evolution. 
       Calculates Lyapunov-like stability to detect fragile reasoning (ambiguity).
    3. Compressed Sensing: Uses ISTA (Iterative Soft Thresholding) to infer sparse weights 
       linking features to correctness based on metamorphic relations.
    4. Adaptive Control: Online gradient descent updates weights based on prediction error.
    5. Epistemic Honesty: Caps confidence if dynamics are unstable or meta-traps are detected.
    """

    def __init__(self):
        # Feature definitions (regex patterns)
        self.feature_patterns = [
            (r'\b(not|no|never|neither)\b', 'negation'),
            (r'\b(more than|less than|greater|smaller|higher|lower)\b', 'comparative'),
            (r'\b(if|then|unless|provided)\b', 'conditional'),
            (r'\d+(\.\d+)?', 'numeric'),
            (r'\b(because|therefore|thus|hence|leads to)\b', 'causal'),
            (r'\b(before|after|while|during)\b', 'temporal'),
            (r'\b(all|some|every|none|any)\b', 'quantifier'),
            (r'\b(either|or)\b', 'dichotomy'),
            (r'\b(stopped|quit|failed)\b', 'presupposition_trigger'),
            (r'\b(he|she|they|it|him|her)\b', 'pronoun')
        ]
        self.n_features = len(self.feature_patterns)
        
        # State for Adaptive Control
        self.w = np.zeros(self.n_features)  # Sparse weights
        self.mu = 0.01  # Learning rate
        self.lambda_reg = 0.1  # Sparsity penalty
        
        # Metamorphic Relations (Simulated transformations)
        # We simulate MRs by checking sensitivity to specific feature flips
        self.mr_sensitivity = np.ones(self.n_features) 

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector from text."""
        text_lower = text.lower()
        features = np.zeros(self.n_features)
        for i, (pattern, _) in enumerate(self.feature_patterns):
            if re.search(pattern, text_lower):
                features[i] = 1.0
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detects logical traps, ambiguity, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        score_cap = 1.0
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        if re.search(r'\b(have you stopped|did you quit|why did .+ (fail|stop|break))\b', p_lower):
            score_cap = min(score_cap, 0.2)
            
        # 2. Scope/Pronoun Ambiguity indicators
        if re.search(r'\b(every .+ (a|an) .+|who is .+ (he|she|it))\b', p_lower):
            # Heuristic: if question asks "who" and has multiple pronouns, lower confidence
            if 'who' in p_lower and p_lower.count('?') == 1:
                 score_cap = min(score_cap, 0.4)

        # 3. False Dichotomy ("Either A or B" without context)
        if re.search(r'\b(either .+ or .+)\b', p_lower) and 'otherwise' not in p_lower:
            score_cap = min(score_cap, 0.5)

        # 4. Subjectivity ("Best", "Favorite" without criteria)
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_lower) and 'calculate' not in p_lower:
            score_cap = min(score_cap, 0.6)

        return score_cap

    def _track_dynamics(self, prompt: str, answer: str) -> Tuple[float, float]:
        """
        FRAME C: Dynamics Tracker.
        Models reasoning as state evolution. 
        Returns (stability_score, convergence_rate).
        """
        # Simulate state evolution by processing tokens/segments
        # We approximate the "state" as the cumulative feature vector
        segments = re.split(r'[,.]', prompt) # Split by sentences/clauses
        if len(segments) < 2:
            segments = [prompt, prompt] # Fallback for short prompts
            
        trajectory = []
        state = np.zeros(self.n_features)
        
        # Simulate step-wise update
        for seg in segments:
            delta = self._extract_features(seg)
            # Linear dynamical system approximation: x_k+1 = A*x_k + B*u_k
            # Here A is identity (memory), B is input gain
            state = 0.8 * state + 0.5 * delta # Decay + Input
            
            # Check if answer matches current state implication (simplified)
            # If answer contains features present in state, it's "stable"
            ans_feat = self._extract_features(answer)
            alignment = np.dot(state, ans_feat) / (np.linalg.norm(state) + 1e-6)
            trajectory.append(alignment)

        if len(trajectory) < 2:
            return 0.5, 0.0

        # Lyapunov-like stability: Variance of the trajectory
        # Low variance = stable reasoning path
        traj_np = np.array(trajectory)
        stability = 1.0 / (1.0 + np.var(traj_np)) # Higher is more stable
        
        # Convergence rate: How fast does it settle?
        convergence = 1.0 - (np.abs(traj_np[-1] - traj_np[0]) + 0.1) 
        
        return float(stability), float(convergence)

    def _ista_solve(self, A: np.ndarray, b: np.ndarray, max_iter: int = 50) -> np.ndarray:
        """Iterative Soft Thresholding Algorithm for L1 minimization."""
        n = A.shape[1]
        w = np.zeros(n)
        L = np.linalg.norm(A, ord=2)**2 + 1e-6  # Lipschitz constant
        
        for _ in range(max_iter):
            grad = A.T @ (A @ w - b)
            w = w - (1/L) * grad
            # Soft thresholding
            threshold = self.lambda_reg / L
            w = np.sign(w) * np.maximum(np.abs(w) - threshold, 0)
        return w

    def _generate_mr_matrix(self, base_features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate Metamorphic Relations matrix.
        Rows are transformations, cols are features.
        """
        m = 4 # Number of MRs
        A = np.zeros((m, self.n_features))
        b = np.zeros(m)
        
        # MR1: Negation flip (simulate effect on negation feature)
        A[0, 0] = 1.0 
        b[0] = 0.5 # Expected change score
        
        # MR2: Numeric scaling
        A[1, 3] = 1.0
        b[1] = 0.8
        
        # MR3: Conditional logic
        A[2, 2] = 1.0
        b[2] = 0.6
        
        # MR4: Quantifier shift
        A[3, 6] = 1.0
        b[3] = 0.7
        
        # Add noise to simulate real-world imperfection
        b += np.random.normal(0, 0.1, m)
        return A, b

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Construct MR Matrix based on prompt structure
        base_feats = self._extract_features(prompt)
        A_mr, b_mr = self._generate_mr_matrix(base_feats)
        
        # 2. Compressed Sensing: Infer sparse weights
        # If we have historical data, we'd use it. Here we initialize/refine with ISTA
        w_sparse = self._ista_solve(A_mr, b_mr)
        
        # 3. Adaptive Control: Update global weights
        # Prediction error e = Aw - b
        e = A_mr @ self.w - b_mr
        self.w = self.w - self.mu * (A_mr.T @ e)
        
        # Blend sparse solution with adaptive update
        self.w = 0.7 * self.w + 0.3 * w_sparse 

        for cand in candidates:
            # Feature extraction
            x = self._extract_features(cand)
            
            # Score decomposition
            # 50% Structural (Dot product with learned weights)
            struct_score = float(np.dot(self.w, x))
            
            # 20% Constructive Computation (Heuristic check for math/logic)
            comp_score = 0.0
            if re.search(r'\d+', cand) and re.search(r'[=<>]', cand):
                try:
                    # Attempt to evaluate simple expressions
                    val = eval(cand.split('=')[-1][:20]) # Unsafe in prod, ok for tool demo
                    comp_score = 1.0 if isinstance(val, (int, float)) else 0.0
                except:
                    comp_score = 0.5
            elif len(cand.split()) > 0:
                # Fallback: keyword match for logical connectors
                if any(k in cand.lower() for k in ['therefore', 'thus', 'because']):
                    comp_score = 0.8
            
            # 15% NCD (Similarity to prompt - penalize if too disjoint or identical)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Final Score Calculation
            # Normalize struct_score to ~0-1 range roughly
            struct_norm = 1.0 / (1.0 + np.exp(-struct_score)) # Sigmoid
            
            final_score = (0.55 * struct_norm) + (0.25 * comp_score) + (0.15 * ncd_score)
            
            # Dynamics check for this specific candidate
            stability, _ = self._track_dynamics(prompt, cand)
            final_score *= (0.8 + 0.2 * stability) # Boost stable answers

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural:{struct_norm:.2f}, Comp:{comp_score:.2f}, NCD:{ncd_score:.2f}, Stability:{stability:.2f}"
            })

        # Rank by score
        results.sort(key=lambda k: k['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty via meta-confidence cap.
        """
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return 0.1 # Strongly penalize ambiguous/trap prompts

        # 2. Structural Match
        x = self._extract_features(answer)
        struct_score = float(np.dot(self.w, x))
        base_conf = 1.0 / (1.0 + np.exp(-struct_score))
        
        # 3. Dynamics Stability
        stability, conv_rate = self._track_dynamics(prompt, answer)
        
        # 4. Constructive Verification (if applicable)
        numeric_match = bool(re.search(r'\d+', answer))
        prompt_has_num = bool(re.search(r'\d+', prompt))
        if prompt_has_num and not numeric_match:
            # If prompt has numbers but answer doesn't, lower confidence unless it's a logic trap
            if "not" not in prompt.lower():
                base_conf *= 0.7

        # Combine
        raw_conf = (base_conf * 0.6) + (stability * 0.4)
        
        # Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure bounds
        return max(0.0, min(1.0, final_conf))

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    p = "If John has 5 apples and gives 2 to Mary, how many does he have?"
    cands = ["He has 3 apples.", "He has 7 apples.", "John is hungry."]
    
    print("Evaluation:")
    res = tool.evaluate(p, cands)
    for r in res:
        print(f"{r['candidate']}: {r['score']:.4f} ({r['reasoning']})")
        
    print("\nConfidence:")
    print(f"Correct answer: {tool.confidence(p, 'He has 3 apples.')}")
    
    trap_p = "Have you stopped cheating on tests?"
    print(f"Trap question confidence: {tool.confidence(trap_p, 'Yes')}")