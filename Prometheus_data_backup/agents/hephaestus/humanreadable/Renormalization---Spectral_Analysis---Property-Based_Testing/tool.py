import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Renormalized Spectral Consistency Scorer (RSCS).
    
    Combines spectral graph analysis with renormalization group ideas and
    property-based testing. Parses text into proposition graphs, applies
    spectral clustering to find a fixed point, scores via algebraic connectivity,
    and tests robustness via perturbations.
    """
    
    def __init__(self):
        self.eps = 1e-4
        self.max_iter = 10
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            reasoning = f"Spectral consistency: {score:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._score_candidate(prompt, answer)
        # Cap confidence based on structural certainty
        return min(meta_conf, score * 0.85)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for epistemic traps in the prompt."""
        lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|did you stop|why did .+ fail|when did .+ end)', lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery \w+.*\ba \w+', lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', lower) and re.search(r'\bwho\b', lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', lower) and 'which' not in lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', lower):
            if not re.search(r'\b(according to|measured by|criteria|metric)\b', lower):
                return 0.3
        
        # Check information sufficiency
        unknowns = len(re.findall(r'\?', prompt))
        constraints = len(re.findall(r'\b(if|then|because|since|given|when)\b', lower))
        info_suff = information_sufficiency(unknowns, constraints)
        
        return max(0.5, info_suff)
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Core RSCS algorithm."""
        text = prompt + " " + candidate
        
        # 1. Parse to proposition graph
        props, features = self._parse_propositions(text)
        if len(props) < 2:
            return 0.5  # Neutral for trivial cases
        
        # 2. Build adjacency matrix
        W = self._build_adjacency(props, features)
        n = len(W)
        
        # 3. Renormalization via spectral fixed-point
        W_final = self._renormalize(W)
        
        # 4. Spectral consistency score
        base_score = self._spectral_score(W_final)
        
        # 5. Property-based perturbation sensitivity
        sensitivity = self._perturbation_sensitivity(features, W)
        
        # Combine: high base score + low sensitivity = high confidence
        final_score = base_score * (1.0 - sensitivity * 0.5)
        
        return np.clip(final_score, 0.0, 1.0)
    
    def _parse_propositions(self, text: str) -> Tuple[List[str], np.ndarray]:
        """Extract propositions and feature vectors."""
        sentences = re.split(r'[.!?;]', text)
        props = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        features = []
        for prop in props:
            lower = prop.lower()
            polarity = 1.0 if re.search(r'\b(not|no|never|none)\b', lower) else 0.0
            comparator = 1.0 if re.search(r'(<|>|=|less|more|greater|equal)', lower) else 0.0
            nums = re.findall(r'\d+\.?\d*', prop)
            numeric = float(nums[0]) / 100.0 if nums else 0.0
            causal = 1.0 if re.search(r'\b(because|since|leads to|causes|results in)\b', lower) else 0.0
            quantifier = 1.0 if re.search(r'\b(all|every|some|any|none)\b', lower) else 0.5
            
            features.append([polarity, comparator, numeric, causal, quantifier])
        
        return props, np.array(features) if features else np.zeros((1, 5))
    
    def _build_adjacency(self, props: List[str], features: np.ndarray) -> np.ndarray:
        """Build weighted adjacency matrix from logical relations."""
        n = len(props)
        W = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                prop_i = props[i].lower()
                prop_j = props[j].lower()
                
                # Implication: if...then
                if re.search(r'\bif\b', prop_i) and re.search(r'\bthen\b', prop_j):
                    W[i, j] = 1.0
                
                # Causal relation
                if features[i, 3] > 0.5 and features[j, 3] > 0.5:
                    W[i, j] = 0.5
                
                # Contradiction: negation of similar content
                if features[i, 0] != features[j, 0]:
                    common_words = set(prop_i.split()) & set(prop_j.split())
                    if len(common_words) > 3:
                        W[i, j] = -1.0
                
                # Feature similarity (weak link)
                feat_dist = np.linalg.norm(features[i] - features[j])
                if feat_dist < 1.0:
                    W[i, j] += 0.3
        
        return W
    
    def _renormalize(self, W: np.ndarray) -> np.ndarray:
        """Spectral renormalization via fixed-point iteration."""
        W_curr = W.copy()
        n = len(W)
        k = max(2, int(np.sqrt(n)))
        
        for _ in range(self.max_iter):
            # Compute Laplacian
            D = np.diag(np.abs(W_curr).sum(axis=1))
            L = D - W_curr
            
            # Spectral decomposition
            try:
                eigvals, eigvecs = np.linalg.eigh(L)
                V_k = eigvecs[:, :min(k, n)]
            except:
                return W_curr  # Fallback
            
            # Soft clustering projection
            C = V_k @ V_k.T
            
            # Coarse-grain
            W_new = C.T @ W_curr @ C
            
            # Check convergence
            if np.linalg.norm(W_new - W_curr, 'fro') < self.eps:
                break
            
            W_curr = W_new
        
        return W_curr
    
    def _spectral_score(self, W: np.ndarray) -> float:
        """Score via algebraic connectivity and spectral spread."""
        n = len(W)
        D = np.diag(np.abs(W).sum(axis=1))
        L = D - W
        
        try:
            eigvals = np.linalg.eigvalsh(L)
            eigvals = np.sort(eigvals)
            
            lambda_2 = eigvals[1] if n > 1 else eigvals[0]
            sigma = np.std(eigvals)
            
            # High connectivity + low spread = high score
            base = np.exp(-lambda_2) * (1.0 - sigma / (sigma + 1.0))
            return np.clip(base, 0.0, 1.0)
        except:
            return 0.5
    
    def _perturbation_sensitivity(self, features: np.ndarray, W: np.ndarray) -> float:
        """Property-based testing: perturb and measure sensitivity."""
        n_perturbs = min(20, len(features) * 3)
        scores = []
        
        base_score = self._spectral_score(W)
        
        for _ in range(n_perturbs):
            feat_pert = features.copy()
            idx = np.random.randint(0, len(features))
            dim = np.random.randint(0, features.shape[1])
            
            # Random perturbation
            if dim == 0:  # Flip polarity
                feat_pert[idx, dim] = 1.0 - feat_pert[idx, dim]
            else:  # Jitter
                feat_pert[idx, dim] += np.random.uniform(-0.2, 0.2)
            
            # Rebuild adjacency (simplified)
            W_pert = W + np.random.randn(*W.shape) * 0.1
            score_pert = self._spectral_score(W_pert)
            scores.append(score_pert)
        
        # Sensitivity = how much agreement across perturbations
        if len(scores) > 1:
            agreement = confidence_from_agreement(scores)
            return 1.0 - agreement
        
        return 0.5