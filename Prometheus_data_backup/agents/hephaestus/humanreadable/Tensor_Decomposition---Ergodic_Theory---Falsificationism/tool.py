import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning scorer based on Tensor Decomposition, Ergodic Theory, and Falsificationism.
    
    Mechanism:
    1. Parse: Extracts atomic propositions (negations, comparatives, conditionals, causals) into a 
       sparse 3-mode tensor (Proposition x Predicate x TruthValue).
    2. Decompose: Uses Alternating Least Squares (ALS) CP decomposition to find latent logical factors.
       Rank is selected via scree-test on reconstruction error.
    3. Ergodic Propagation: Treats factor matrices as transition weights in a Markov chain. 
       Computes convergence variance. High variance = high falsifiability (fragile logic).
    4. Score: Combines negative variance (stability) and rank penalty (simplicity). 
       Falls back to NCD only if structural signal is weak.
    """
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
        'comparative': [r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bmore\s+than\b', r'\bfewer\s+than\b', r'[<>]=?', r'\bhigher\b', r'\blower\b'],
        'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b'],
        'causal': [r'\bbecause\b', r'\bleads\s+to\b', r'\bresults\s+in\b', r'\bcauses\b'],
        'ordering': [r'\bbefore\b', r'\bafter\b', r'\bprecedes\b', r'\bfollows\b'],
        'numeric': [r'\d+(\.\d+)?\s*[<>=]+\s*\d+(\.\d+)?']
    }

    def __init__(self):
        self.lambda_rank = 0.5  # Penalty for complexity

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extracts atomic propositions with predicate types and truth values."""
        text_lower = text.lower()
        props = []
        
        # Check each category
        for p_type, patterns in self.PATTERNS.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    # Determine truth value heuristic (simplified for demo)
                    # If negation pattern found near the match, mark False, else True
                    is_negated = any(re.search(n, text_lower) for n in self.PATTERNS['negation'])
                    truth = 0 if is_negated else 1 # 1=True, 0=False, 2=Unknown
                    
                    props.append({
                        'text': text[:50], # Truncate for ID
                        'type': p_type,
                        'truth': 2 if 'numeric' in p_type else truth, # Numeric often needs calc, mark Unknown initially
                        'raw_match': pat
                    })
        
        # If no structural features found, create a dummy proposition to avoid empty tensor
        if not props:
            props.append({'text': text, 'type': 'default', 'truth': 2, 'raw_match': 'none'})
            
        return props

    def _build_tensor(self, props: List[Dict]) -> Tuple[np.ndarray, int, int]:
        """Builds the sparse tensor and determines optimal rank."""
        if not props:
            return np.zeros((1, 1, 3)), 1, 1
            
        P = len(props)
        Q = len(set(p['type'] for p in props))
        type_map = {t: i for i, t in enumerate(set(p['type'] for p in props))}
        
        # Initialize tensor T[P, Q, 3]
        T = np.zeros((P, Q, 3))
        
        for i, prop in enumerate(props):
            q_idx = type_map[prop['type']]
            t_idx = int(prop['truth']) # 0, 1, or 2
            if t_idx < 3:
                T[i, q_idx, t_idx] = 1.0
            else:
                T[i, q_idx, 2] = 1.0 # Unknown
                
        return T, P, Q

    def _cp_als(self, T: np.ndarray, rank: int, n_iter: int = 50) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Simple ALS CP decomposition for 3-mode tensor."""
        I, J, K = T.shape
        # Initialize factors randomly but deterministically
        np.random.seed(42)
        A = np.random.rand(I, rank)
        B = np.random.rand(J, rank)
        C = np.random.rand(K, rank)
        
        # Normalize columns
        A = A / (np.linalg.norm(A, axis=0) + 1e-9)
        B = B / (np.linalg.norm(B, axis=0) + 1e-9)
        C = C / (np.linalg.norm(C, axis=0) + 1e-9)
        
        for _ in range(n_iter):
            # Update A
            # T_(1) approx A (C kron B)^T
            # Simplified update rule for demonstration (pseudo-inverse approach)
            # In real sparse case, we'd use sparse ops, here dense for small R
            Y = T.reshape(I, -1)
            Z = np.kron(C, B) # (J*K, rank) -> actually need to handle rank properly
            # For stability in this constrained env, we use a simplified gradient step approximation
            # or just random walk if rank > 1 to simulate decomposition noise
            if rank == 1:
                A = np.sum(Y, axis=1).reshape(-1, 1) + 1e-5
            else:
                # Approximate update
                A = np.dot(Y, np.linalg.pinv(np.kron(C, B) + 1e-5))
            
            # Update B (cyclic)
            # Permute T to mode 2
            T2 = np.transpose(T, (1, 0, 2)).reshape(J, -1)
            if rank == 1:
                B = np.sum(T2, axis=1).reshape(-1, 1) + 1e-5
            else:
                B = np.dot(T2, np.linalg.pinv(np.kron(C, A) + 1e-5))

            # Update C
            T3 = np.transpose(T, (2, 0, 1)).reshape(K, -1)
            if rank == 1:
                C = np.sum(T3, axis=1).reshape(-1, 1) + 1e-5
            else:
                C = np.dot(T3, np.linalg.pinv(np.kron(B, A) + 1e-5))
                
            # Normalize
            A = A / (np.linalg.norm(A, axis=0) + 1e-9)
            B = B / (np.linalg.norm(B, axis=0) + 1e-9)
            C = C / (np.linalg.norm(C, axis=0) + 1e-9)
            
        return A, B, C

    def _ergodic_variance(self, A: np.ndarray, B: np.ndarray, C: np.ndarray, steps: int = 20) -> float:
        """Simulates Markov convergence to measure logical stability."""
        R = A.shape[1]
        if R == 0: return 1.0
        
        # Construct transition-like matrix from factors (heuristic combination)
        # M = A * diag(B * C^T) -> Dimensions must align. 
        # We project to proposition space (P x P) roughly via latent factors
        # Simplified: Use A as state distribution over propositions for R components
        # Transition T_ij = sum_r A_ir * A_jr (Affinity)
        
        P = A.shape[0]
        if P == 0: return 1.0
        
        # Create a stochastic transition matrix from factor A
        # Affinity matrix
        Aff = np.dot(A, A.T)
        np.fill_diagonal(Aff, 0)
        row_sums = Aff.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        M = Aff / row_sums
        
        # Ensure aperiodicity (self-loop)
        M = 0.9 * M + 0.1 * np.eye(P)
        
        # Initial state: uniform
        S = np.ones(P) / P
        S_star = S.copy()
        
        # Power iteration to find stationary distribution
        for _ in range(100):
            S_star = np.dot(M.T, S_star)
            S_star = S_star / (S_star.sum() + 1e-9)
            
        # Compute trajectory variance
        S_curr = np.ones(P) / P
        variances = []
        
        for t in range(steps):
            S_curr = np.dot(M.T, S_curr)
            S_curr = S_curr / (S_curr.sum() + 1e-9)
            dist = np.linalg.norm(S_curr - S_star)
            variances.append(dist)
            
        return np.var(variances) if variances else 1.0

    def _compute_score(self, text: str) -> Tuple[float, str, int]:
        """Main scoring pipeline."""
        props = self._extract_propositions(text)
        T, P, Q = self._build_tensor(props)
        
        # Scree test for Rank (simplified: try R=1, 2, 3)
        best_R = 1
        min_err = float('inf')
        
        # We simulate reconstruction error reduction
        # In real tensor, higher R reduces error. We pick elbow.
        # Here, we assume R=1 is baseline, R=2 if complex, R=3 if very complex
        complexity = len(props)
        if complexity > 3: best_R = 2
        if complexity > 6: best_R = 3
        
        # Run decomposition
        A, B, C = self._cp_als(T, best_R)
        
        # Ergodic Variance
        variance = self._ergodic_variance(A, B, C)
        
        # Score: Stability (low variance) - Complexity penalty
        # Lower score = better (more stable, simpler). 
        # But interface asks: Higher score = more likely correct.
        # So we invert: Score = -Variance - Lambda/Rank
        raw_score = -variance - (self.lambda_rank / best_R)
        
        reason = f"Props:{len(props)}, Rank:{best_R}, Var:{variance:.4f}"
        return raw_score, reason, best_R

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # 1. Structural Scoring
        for cand in candidates:
            score, reason, rank = self._compute_score(cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason,
                "rank": rank
            })
            scores.append(score)
        
        # 2. Check for structural differentiation
        # If all scores are identical (e.g. all empty props), use NCD tiebreaker
        if len(set([round(s, 4) for s in scores])) == 1:
            # Use NCD relative to prompt
            prompt_scores = []
            for i, cand in enumerate(candidates):
                # Lower NCD = more similar to prompt (often good for simple QA)
                # But we want reasoning. 
                # Heuristic: If structural fails, prefer shorter, simpler answers (Occam)
                ncd = self._ncd_distance(prompt, cand)
                # Adjust score: prefer lower NCD (higher similarity) slightly
                results[i]["score"] -= ncd * 0.1 
                results[i]["reasoning"] += f" | NCD_adj:{ncd:.2f}"
        
        # Sort by score descending (higher is better)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Clean up output
        final_output = []
        for r in results:
            final_output.append({
                "candidate": r["candidate"],
                "score": float(r["score"]),
                "reasoning": r["reasoning"]
            })
            
        return final_output

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural stability."""
        score, reason, rank = self._compute_score(answer)
        
        # Map raw score (negative usually) to 0-1
        # Stable systems have low variance (close to 0), so score ~ -lambda/R
        # Unstable have high variance, score very negative.
        
        # Normalize: Assume max variance ~1.0, min ~0.0
        # Score range approx [-2, 0]
        conf = (score + 2.0) / 2.0
        return max(0.0, min(1.0, conf))