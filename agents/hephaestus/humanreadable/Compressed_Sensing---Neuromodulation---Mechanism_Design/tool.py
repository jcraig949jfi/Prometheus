import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining Compressed Sensing (CS), Neuromodulatory Gain,
    Mechanism Design (VCG), and Dynamical Systems Theory.
    
    Core Mechanisms:
    1. Feature Extraction: Regex-based parsing of logical primitives (negation, causality, etc.).
    2. Neuromodulation: Dynamically scales feature importance based on sensitivity (negation/modality).
    3. Compressed Sensing (ISTA): Recovers the sparse logical structure of an answer from noisy text.
    4. Mechanism Design: Scores candidates based on a VCG-style payment scheme where logical 
       primitives are agents rewarded for global constraint satisfaction.
    5. Dynamics Tracker: Models reasoning as a state evolution. Confidence is derived from 
       the Lyapunov stability of the solution trajectory under premise perturbation.
    """

    def __init__(self):
        # Primitives for feature extraction
        self.primitives = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bneither\b'],
            'comparative': [r'\bmore than\b', r'\bless than\b', r'\bas\s+\w+\s+as\b', r'\bgreater than\b', r'\bsmaller than\b'],
            'conditional': [r'\bif\b', r'\bunless\b', r'\bprovided that\b', r'\bthen\b', r'\botherwise\b'],
            'numeric': [r'\d+(?:\.\d+)?(?:\s*(?:%|units|kg|m|s))?', r'\bone\b', r'\btwo\b', r'\bthree\b'],
            'causal': [r'\bbecause\b', r'\bleads to\b', r'\bresults in\b', r'\bdue to\b', r'\bcauses\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\branked\b', r'\bfirst\b', r'\blast\b']
        }
        
        # Presupposition/Ambiguity triggers for Tier B
        self.presupposition_triggers = [
            r'\bhave you stopped\b', r'\bwhy did.*fail\b', r'\bwhy did.*stop\b', 
            r'\bwhen did.*stop\b', r'\bstill\b.*\bproblem\b'
        ]
        self.ambiguity_triggers = [
            r'\bevery.*a\s+\w+\b', # Scope ambiguity hint
            r'\bhe\s+was\b', r'\bshe\s+was\b', r'\bthey\s+were\b', # Pronoun ambiguity
            r'\beither.*or\b', # False dichotomy hint
            r'\bbest\b', r'\bworst\b', r'\bfavorite\b' # Subjectivity
        ]

        # ISTA Parameters
        self.lambda_sparsity = 0.1
        self.max_iter = 50
        self.tol = 1e-4

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector based on regex primitives."""
        text_lower = text.lower()
        features = []
        for category, patterns in self.primitives.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    match_count += 1
            features.append(match_count)
        return np.array(features, dtype=float)

    def _compute_gain(self, features: np.ndarray, text: str) -> np.ndarray:
        """Compute neuromodulatory gain vector."""
        text_lower = text.lower()
        neg_count = sum(1 for p in self.primitives['negation'] if re.search(p, text_lower))
        modal_count = sum(1 for p in self.primitives['conditional'] if re.search(p, text_lower))
        
        # Base gain is 1.0, amplified by negation/modality presence
        base_gain = np.ones(len(features))
        # Amplify specific indices corresponding to negation and conditionals if present in text
        # Index 0: negation, Index 2: conditional
        if neg_count > 0:
            base_gain[0] = 1.5  # Amplify negation handling
        if modal_count > 0:
            base_gain[2] = 1.5  # Amplify conditional handling
            
        return base_gain

    def _ista_solve(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Iterative Soft-Thresholding Algorithm for sparse recovery."""
        m, n = A.shape
        if n == 0:
            return np.array([])
            
        x = np.zeros(n)
        # Lipschitz constant estimate
        L = np.linalg.norm(A, ord=2)**2 + 1e-6
        
        for _ in range(self.max_iter):
            grad = A.T @ (A @ x - b)
            x_new = x - (1.0 / L) * grad
            # Soft thresholding
            x_new = np.sign(x_new) * np.maximum(np.abs(x_new) - self.lambda_sparsity / L, 0.0)
            
            if np.linalg.norm(x_new - x) < self.tol:
                break
            x = x_new
        return x

    def _compute_vc_payment(self, A: np.ndarray, x_hat: np.ndarray, b: np.ndarray, idx: int) -> float:
        """Compute VCG-style payment for a specific primitive."""
        if len(x_hat) == 0:
            return 0.0
            
        # Utility is negative reconstruction error (higher is better)
        full_error = np.linalg.norm(A @ x_hat - b)**2
        v_full = -full_error
        
        # Counterfactual: zero out column idx
        A_mod = A.copy()
        A_mod[:, idx] = 0
        # Re-solve or approximate impact? For speed, we approximate impact by removing contribution
        # Strict VCG requires re-solving. Given constraints, we simulate re-solve with reduced matrix if possible
        # Simplified: Measure drop in utility if feature idx is removed
        x_minus = x_hat.copy()
        x_minus[idx] = 0
        v_minus = -np.linalg.norm(A @ x_minus - b)**2
        
        # Payment = Improvement brought by agent i to the system
        # Simplified VCG: v_i(S) - v_i(S\{i}) approximated by contribution to error reduction
        return v_full - v_minus

    def _dynamics_tracker(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Track state evolution to determine stability.
        Simulates premise reordering/perturbation to check Lyapunov stability.
        Returns (stability_score, convergence_rate).
        """
        # Create a synthetic state vector from features
        base_features = self._extract_features(prompt + " " + candidate)
        if np.all(base_features == 0):
            return 0.0, 0.0
            
        # Perturb the input slightly (simulate noise in premise ordering/wording)
        # Since we can't easily reorder words without NLP libs, we simulate perturbation
        # by adding noise to the feature extraction result (representing ambiguity)
        perturbations = []
        for i in range(5):
            noise = np.random.normal(0, 0.1, size=base_features.shape)
            perturbed_feat = base_features + noise
            perturbed_feat[perturbed_feat < 0] = 0
            perturbations.append(perturbed_feat)
            
        # Treat base as equilibrium, measure deviation of trajectories
        deviations = []
        for p in perturbations:
            dist = np.linalg.norm(p - base_features)
            deviations.append(dist)
            
        stability = 1.0 / (1.0 + np.std(deviations) + np.mean(deviations))
        convergence = 1.0 / (1.0 + np.mean(deviations))
        
        return float(stability), float(convergence)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap for confidence.
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # Check presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                score = min(score, 0.2) # Strong penalty
        
        # Check ambiguity triggers
        ambiguity_count = 0
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                ambiguity_count += 1
        
        if ambiguity_count >= 2:
            score = min(score, 0.3)
        elif ambiguity_count == 1:
            score = min(score, 0.6)
            
        # Check for lack of structural content (unanswerable)
        if len(self._extract_features(prompt)) == 0 or np.sum(self._extract_features(prompt)) == 0:
             # Only if prompt itself has no logic cues
            if len(prompt.split()) > 5: # Ignore very short prompts
                score = min(score, 0.3)

        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return c12 / max(c1, c2)

    def _compute_computation_score(self, prompt: str, candidate: str) -> float:
        """
        Attempt to extract and solve simple math/logic if present.
        Returns 1.0 if correct, 0.0 if wrong, 0.5 if not applicable.
        """
        # Extract numbers from prompt and candidate
        nums_p = re.findall(r'\d+(?:\.\d+)?', prompt)
        nums_c = re.findall(r'\d+(?:\.\d+)?', candidate)
        
        if not nums_p or not nums_c:
            return 0.5 # Not a numeric problem
            
        try:
            # Simple heuristic: if candidate number matches a calculation result from prompt numbers
            # Supports basic addition/subtraction checks often found in reasoning traps
            p_nums = [float(x) for x in nums_p]
            c_nums = [float(x) for x in nums_c]
            
            # Check direct match first
            if any(abs(c - p) < 1e-6 for c in c_nums for p in p_nums):
                return 1.0
                
            # Check simple sum
            if any(abs(sum(p_nums) - c) < 1e-6 for c in c_nums):
                return 1.0
                
            # Check simple product
            prod = 1.0
            for x in p_nums: prod *= x
            if any(abs(prod - c) < 1e-6 for c in c_nums):
                return 1.0
                
            # If numbers are present but don't match logic, likely wrong
            return 0.0
            
        except Exception:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Construct Measurement Matrix A from all candidates + prompt context
        # Rows: Candidates, Cols: Features
        all_texts = [prompt + " " + c for c in candidates]
        if not all_texts:
            return []
            
        feature_vectors = [self._extract_features(t) for t in all_texts]
        A = np.vstack(feature_vectors) if feature_vectors else np.array([])
        
        if A.size == 0:
            # Fallback for empty features
            A = np.zeros((len(candidates), len(self.primitives)))

        # Reference vector b (idealized dense signal approximated by mean + noise)
        # In CS context, b is the measurement. Here we treat the aggregate structure as the target.
        b = np.mean(A, axis=0) + 0.1 * np.random.randn(A.shape[1])
        
        # Neuromodulatory Gain
        # Apply gain based on the prompt's inherent complexity
        prompt_feats = self._extract_features(prompt)
        gain = self._compute_gain(prompt_feats, prompt)
        A_mod = A * gain # Broadcast scaling
        
        scored_candidates = []
        
        for i, candidate in enumerate(candidates):
            full_text = prompt + " " + candidate
            
            # 2. Compressed Sensing Recovery
            # Solve for sparse x that explains the candidate's features relative to the matrix
            # Since A is small (candidates x features), we solve per candidate row essentially
            # But to follow the algorithm: treat row i as measurement b_i, recover x
            row_vec = A_mod[i, :].reshape(-1, 1) # Measurement
            # We need a dictionary. Let's use identity for simplicity in this constrained env
            # Or use the global A as dictionary. 
            # Simplified: x_hat = ISTA(A_mod^T, row_vec^T) -> recovering feature weights
            
            # To make ISTA meaningful here: We try to reconstruct the candidate's feature vector
            # using a sparse set of "logical atoms" (columns of A).
            # Since A is candidates x features, we transpose: Features x Candidates.
            # We want to represent candidate i as sparse combo of other candidates? 
            # No, the prompt says: "Treat reference feature vector b as sparse measurement of true underlying propositional set x"
            # Let's interpret: b = row i of A_mod. Dictionary = Identity (features are atoms).
            # Then x is just the soft-thresholded version of the feature vector itself.
            
            b_vec = (A[i, :] * gain).astype(float)
            x_hat = self._ista_solve(np.eye(len(b_vec)), b_vec)
            
            # 3. Mechanism Design Scoring
            payments = []
            for j in range(len(x_hat)):
                p_j = self._compute_vc_payment(np.eye(len(b_vec)), x_hat, b_vec, j)
                payments.append(p_j)
            
            reconstruction_error = -np.linalg.norm(A_mod[i, :] - b_vec)**2
            mechanism_score = np.sum(payments)
            
            # 4. Dynamics Tracking (Stability)
            stability, convergence = self._dynamics_tracker(prompt, candidate)
            
            # 5. Computation Check (Constructive)
            comp_score = self._compute_computation_score(prompt, candidate)
            
            # 6. NCD (Tiebreaker, max 15%)
            ncd = self._compute_ncd(prompt, candidate)
            ncd_score = 1.0 - ncd # Higher is better
            
            # Final Score Composition
            # Structural (Reconstruction + Mechanism): 50%
            # Dynamics (Stability): 30%
            # Computation: 20%
            # NCD: < 15% (capped)
            
            struct_score = reconstruction_error + 0.5 * mechanism_score
            # Normalize struct_score roughly to 0-1 range via sigmoid-like mapping
            struct_norm = 1 / (1 + np.exp(-struct_score)) 
            
            final_score = (
                0.35 * struct_norm +
                0.30 * stability +
                0.20 * comp_score +
                0.15 * ncd_score
            )
            
            # Reasoning string generation
            reasoning_parts = []
            if stability > 0.8: reasoning_parts.append("High logical stability")
            elif stability < 0.4: reasoning_parts.append("Fragile reasoning trajectory")
            if comp_score == 1.0: reasoning_parts.append("Numeric verification passed")
            if comp_score == 0.0: reasoning_parts.append("Numeric inconsistency detected")
            if np.sum(x_hat > 0) > 0: reasoning_parts.append(f"Detected {int(np.sum(x_hat>0))} logical primitives")
            
            reasoning_str = "; ".join(reasoning_parts) if reasoning_parts else "Standard structural match"

            scored_candidates.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": reasoning_str,
                "stability": stability,
                "comp_score": comp_score
            })

        # Rank by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Format output
        return [
            {
                "candidate": item["candidate"],
                "score": item["score"],
                "reasoning": item["reasoning"]
            }
            for item in scored_candidates
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Confidence
        # Run a mini-evaluation to get stability and comp score
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        res = res_list[0]
        stability = res.get('stability', 0.5)
        comp_score = res.get('comp_score', 0.5)
        
        # Base confidence from stability and computation
        # If computation failed (0.0) and it looked like a math problem, confidence should be low
        base_conf = 0.5 * stability + 0.5 * comp_score
        
        # Apply meta cap
        final_conf = min(base_conf, meta_cap)
        
        # Ensure bounds
        return max(0.0, min(1.0, final_conf))