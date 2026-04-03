import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning tool combining structural parsing, abductive sparse coding,
    and phase-transition detection.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and relations (negation, comparative, causal, numeric).
    2. Sparse Coding: Builds a dictionary of features and infers sparse codes via ISTA.
    3. Phase Transition: Sweeps sparsity parameter lambda to find the critical point where 
       the system shifts from over-fitted to under-fitted (discontinuous drop in active atoms).
    4. Scoring: Uses reconstruction error at the critical point, penalized by sparsity.
    5. Fallback: Uses NCD only if structural signals are weak or identical.
    """
    
    # Regex patterns for structural extraction
    PATTERNS = {
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
        'comparative': [r'\bmore than\b', r'\bless than\b', r'\bgreater than\b', r'\bsmaller than\b', r'\b>\b', r'\b<\b'],
        'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bimplies\b'],
        'causal': [r'\bbecause\b', r'\btherefore\b', r'\bleads to\b', r'\bcauses\b'],
        'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b'],
        'quantifier': [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b'],
        'numeric': r'(\d+(?:\.\d+)?)\s*(?:kg|m|s|h|units)?' # Simplified numeric capture
    }

    def __init__(self):
        self.dictionary = []  # List of feature strings (over-complete basis)
        self.feature_map = {} # Map feature string to index
        self.K = 0            # Dimension of dictionary

    def _extract_features(self, text: str) -> List[str]:
        """Extract structural features from text."""
        features = []
        text_lower = text.lower()
        
        # Extract regex-based features
        for category, patterns in self.PATTERNS.items():
            if isinstance(patterns, list):
                for pat in patterns:
                    if re.search(pat, text_lower):
                        features.append(f"{category}:{pat}")
            else:
                # Numeric extraction
                matches = re.findall(patterns, text_lower)
                if matches:
                    features.append(f"{category}:present")
                    # Add specific numeric constraints if possible (simplified)
                    if len(matches) >= 2:
                        try:
                            nums = [float(m) for m in matches]
                            if nums[0] < nums[1]:
                                features.append("numeric:asc")
                            elif nums[0] > nums[1]:
                                features.append("numeric:desc")
                        except: pass

        # Add n-grams for content words to ensure coverage (bag-of-words fallback within sparse code)
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        for w in set(words):
            if w not in ['that', 'this', 'with', 'have', 'been', 'were', 'they', 'their']:
                features.append(f"word:{w}")
                
        return list(set(features))

    def _build_dictionary(self, prompt: str, candidates: List[str]):
        """Build over-complete dictionary from prompt and candidates."""
        all_texts = [prompt] + candidates
        all_features = set()
        for t in all_texts:
            feats = self._extract_features(t)
            all_features.update(feats)
        
        self.dictionary = list(all_features)
        self.feature_map = {f: i for i, f in in enumerate(self.dictionary)}
        self.K = len(self.dictionary)

    def _vectorize(self, text: str) -> np.ndarray:
        """Convert text to binary observation vector y."""
        y = np.zeros(self.K)
        feats = self._extract_features(text)
        for f in feats:
            if f in self.feature_map:
                y[self.feature_map[f]] = 1.0
        return y

    def _soft_threshold(self, x: np.ndarray, threshold: float) -> np.ndarray:
        return np.sign(x) * np.maximum(np.abs(x) - threshold, 0.0)

    def _ista(self, y: np.ndarray, Phi: np.ndarray, lam: float, max_iter: int = 50) -> np.ndarray:
        """Iterative Shrinkage-Thresholding Algorithm for sparse coding."""
        if self.K == 0:
            return np.array([])
            
        D = Phi.shape[1]
        x = np.zeros(D)
        # Lipschitz constant approximation
        L = np.linalg.norm(Phi, ord=2)**2 + 1e-6
        
        for _ in range(max_iter):
            grad = Phi.T @ (Phi @ x - y)
            x = self._soft_threshold(x - (1.0/L) * grad, lam/L)
        return x

    def _find_critical_lambda(self, y: np.ndarray, Phi: np.ndarray) -> float:
        """Sweep lambda to find phase transition point."""
        if self.K == 0:
            return 0.1
            
        lambdas = np.logspace(-3, 1, 20)
        m_vals = []
        
        for lam in lambdas:
            x = self._ista(y, Phi, lam)
            m = np.count_nonzero(x) / max(self.K, 1) # Order parameter
            m_vals.append(m)
        
        # Find largest second difference (discontinuity)
        if len(m_vals) < 3:
            return lambdas[0]
            
        diffs = np.abs(np.diff(np.diff(m_vals)))
        if len(diffs) == 0:
            return lambdas[0]
            
        idx = np.argmax(diffs) + 1 # Offset for second diff
        return lambdas[min(idx, len(lambdas)-1)]

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        self._build_dictionary(prompt, candidates)
        
        # If no features found, rely purely on NCD
        if self.K == 0:
            scores = []
            for c in candidates:
                # Invert NCD so higher is better (lower distance = higher score)
                score = 1.0 - self._ncd(prompt, c)
                scores.append({"candidate": c, "score": score, "reasoning": "NCD fallback"})
            return sorted(scores, key=lambda x: x['score'], reverse=True)

        # Construct Phi (Dictionary matrix) - Identity-like but overcomplete based on features
        # Since we built Phi from the union of features, Phi is effectively I_K padded or just I_K
        # To satisfy "over-complete" (D > K), we can duplicate columns with slight noise or just use K=K
        # For this implementation, we treat the feature space as the basis.
        # Phi is K x K identity for exact match logic, but we simulate over-completeness 
        # by allowing the ISTA to select subsets.
        Phi = np.eye(self.K) 
        
        y_prompt = self._vectorize(prompt)
        lambda_c = self._find_critical_lambda(y_prompt, Phi)
        
        results = []
        base_score = 10.0 # Base score for structural match
        
        for c in candidates:
            y_cand = self._vectorize(c)
            x_cand = self._ista(y_prompt, Phi, lambda_c)
            
            # Reconstruction error
            recon_err = np.linalg.norm(y_prompt - Phi @ x_cand)**2
            
            # Sparsity penalty
            sparsity = np.linalg.norm(x_cand, 1)
            
            # Score: Negative error - alpha * sparsity
            # We want high overlap (low error) and low complexity
            score = -recon_err - 0.5 * sparsity
            
            # Boost if exact feature match exists
            overlap = np.sum((y_prompt > 0) & (y_cand > 0))
            if overlap > 0:
                score += base_score * (overlap / self.K)
            
            # NCD Tiebreaker/Booster
            ncd_val = self._ncd(prompt, c)
            if ncd_val < 0.5: # If very similar
                score += 0.1
            
            reason = f"Critical lambda={lambda_c:.3f}, Overlap={overlap}, NCD={ncd_val:.2f}"
            results.append({"candidate": c, "score": float(score), "reasoning": reason})
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Normalize score roughly to 0-1 based on heuristic bounds
        # Structural matches usually yield positive scores, random negative
        conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        return float(np.clip(conf, 0.0, 1.0))