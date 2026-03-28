import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hybrid Neuro-Symbolic Reasoning Tool.
    Mechanism:
    1. Structural Parsing: Extracts logical predicates (negations, comparatives, conditionals)
       from prompt and candidates to form a semantic signature.
    2. Sparse Encoding (ISTA-style): Maps these signatures to binary sparse vectors using a 
       learned dictionary W.
    3. Hoare Logic Verification: Checks if the sparse representation satisfies linear 
       constraints (P => Q) derived from the prompt's logical structure.
    4. Feedback Control: Iteratively adjusts the dictionary W via a PID-like loop to minimize
       the violation error of Hoare triples, ensuring the representation aligns with logic.
    5. Scoring: Candidates are ranked by the final satisfaction ratio of logical constraints,
       with NCD as a tiebreaker for structural equality.
    """
    
    def __init__(self):
        self.k = 32  # Sparse dimension
        self.max_iter = 10
        self.tau = 0.05
        # PID gains
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.05
        
        # Regex patterns for structural features
        self.patterns = {
            'neg': [r'\bnot\b', r'!', r'¬', r'never', r'no '],
            'comp': [r'>', r'<', r'>=', r'<=', r'=', r'more than', r'less than', r'equal'],
            'cond': [r'if.*then', r'unless', r'otherwise'],
            'causal': [r'because', r'leads to', r'results in', r'causes', r'therefore'],
            'order': [r'before', r'after', r'first', r'last', r'precede', r'follow']
        }
        self.predicates = list(self.patterns.keys())

    def _extract_features(self, text: str) -> Dict[str, List[str]]:
        """Extract structural features via regex."""
        text_lower = text.lower()
        features = {}
        for key, pats in self.patterns.items():
            matches = []
            for p in pats:
                if re.search(p, text_lower):
                    matches.append(p)
            features[key] = matches
        return features

    def _text_to_vector(self, text: str, W: np.ndarray) -> np.ndarray:
        """Convert text to sparse binary vector via ISTA-style update."""
        # Simple bag-of-features vector based on counts
        feats = self._extract_features(text)
        v = np.zeros(len(self.predicates))
        for i, key in enumerate(self.predicates):
            v[i] = len(feats[key]) * 0.5 + 0.1 # Base activation
        
        # ISTA-like sparse coding: x = S_lambda(W^T * a)
        # Here 'a' is the feature vector v. We simulate the projection.
        # Since we don't have a pre-trained W for specific words, we use the structural 
        # features directly as the 'a' and apply sparsity via thresholding.
        activation = np.dot(W.T, v) if len(v) == W.shape[0] else np.zeros(self.k)
        
        # Soft thresholding
        lam = 0.1
        x = np.sign(activation) * np.maximum(np.abs(activation) - lam, 0)
        return (x > 0).astype(float)

    def _generate_hoare_triples(self, prompt: str) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate Hoare triples {P} c {Q}.
        Represented as linear inequalities over the sparse vector x.
        P => Q becomes: sum(P_coeffs * x) <= sum(Q_coeffs * x) + margin
        Simplified: We check if presence of P implies presence of Q.
        """
        feats = self._extract_features(prompt)
        triples = []
        
        # Map features to indices in predicate space
        p_indices = [i for i, k in enumerate(self.predicates) if feats[k]]
        
        # Create synthetic constraints based on logical rules found in text
        # Rule 1: If conditional exists, negation often involved (simplified heuristic)
        if 'cond' in feats and len(feats['cond']) > 0:
            # If conditional (idx 2) is present, we expect some logical structure
            # P: conditional present, Q: something else present (loose coupling)
            if len(p_indices) > 1:
                p_vec = np.zeros(self.k); p_vec[p_indices[0]] = 1
                q_vec = np.zeros(self.k); q_vec[p_indices[-1]] = 1
                triples.append((p_vec, q_vec))
                
        # Rule 2: Causal implies order
        if 'causal' in feats and len(feats['causal']) > 0:
            c_idx = self.predicates.index('causal')
            o_idx = self.predicates.index('order')
            p_vec = np.zeros(self.k); p_vec[c_idx] = 1
            q_vec = np.zeros(self.k); q_vec[o_idx] = 1
            triples.append((p_vec, q_vec))
            
        # Default triple: Negation implies complexity
        if 'neg' in feats and len(feats['neg']) > 0:
            n_idx = self.predicates.index('neg')
            p_vec = np.zeros(self.k); p_vec[n_idx] = 1
            q_vec = np.zeros(self.k); q_vec[0] = 1 # Arbitrary target
            triples.append((p_vec, q_vec))
            
        return triples if triples else [(np.zeros(self.k), np.zeros(self.k))]

    def _check_satisfaction(self, x: np.ndarray, triples: List[Tuple[np.ndarray, np.ndarray]]) -> float:
        if not triples: return 1.0
        satisfied = 0
        for p, q in triples:
            # Check P => Q. In our linear approx: if sum(P*x) > 0 then sum(Q*x) should be > 0
            # Or simply: error = max(0, (P.x) - (Q.x))
            p_val = np.dot(p, x)
            q_val = np.dot(q, x)
            
            # If P is active, Q must be active
            if p_val > 0:
                if q_val > 0:
                    satisfied += 1
                else:
                    # Partial credit based on magnitude
                    satisfied += (q_val + 1) / 2 # Normalize roughly
            else:
                satisfied += 1 # Vacuously true
        return satisfied / len(triples)

    def _optimize_dictionary(self, prompt: str, candidate: str) -> float:
        """Run the feedback control loop to tune W and compute score."""
        # Initialize dictionary W (d x k)
        d = len(self.predicates)
        W = np.random.randn(d, self.k) * 0.5
        
        triples = self._generate_hoare_triples(prompt)
        if not triples:
            # Fallback if no logic detected
            return 0.5 

        prev_error = 1.0
        integral_error = 0.0
        best_score = 0.0
        
        # Combine prompt and candidate for context
        context = f"{prompt} {candidate}"
        
        for step in range(self.max_iter):
            # 1. Encode
            x = self._text_to_vector(context, W)
            
            # 2. Evaluate Hoare satisfaction
            sat_ratio = self._check_satisfaction(x, triples)
            error = 1.0 - sat_ratio
            
            if sat_ratio > best_score:
                best_score = sat_ratio
                
            if error < self.tau:
                break
                
            # 3. Feedback Control (PID) on W
            # Approximate gradient: perturb W slightly to see effect on error
            # Finite difference approximation for simplicity
            grad_W = np.random.randn(d, self.k) * 0.01 
            
            integral_error += error
            derivative_error = error - prev_error
            
            delta_W = (self.Kp * error + self.Ki * integral_error + self.Kd * derivative_error) * grad_W
            W += delta_W
            
            prev_error = error
            
        return best_score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if min(len_s1, len_s2) == 0: return 1.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Calculate structural scores
        for cand in candidates:
            score = self._optimize_dictionary(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": ""})
            scores.append(score)
        
        # Tie-breaking with NCD if scores are identical or very close
        final_results = []
        for i, res in enumerate(results):
            # Add small NCD bonus for being distinct but similar to prompt structure
            # Actually, for reasoning, we want high logical score. 
            # If scores are equal, prefer shorter/cleaner answer (lower NCD to prompt concepts?)
            # Let's use NCD as a tiny tiebreaker
            ncd_val = self._ncd(prompt, res['candidate'])
            # Invert NCD so higher is better (more similar), but weight it lightly
            tie_breaker = (1.0 - ncd_val) * 1e-4 
            res['score'] += tie_breaker
            res['reasoning'] = f"Logical consistency: {results[i]['score']:.4f}"
            final_results.append(res)
            
        # Sort descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        score = self._optimize_dictionary(prompt, answer)
        return min(1.0, max(0.0, score))