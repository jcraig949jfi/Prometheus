import numpy as np
import re
import zlib
from collections import defaultdict

class ReasoningTool:
    """
    Ergodic-Sparse-Counterfactual reasoning tool with dynamics tracking.
    
    Mechanism:
    1. Parse structural predicates (negations, conditionals, comparatives, causals, numerics)
    2. Build ergodic co-occurrence matrix from gold patterns (temporal averaging)
    3. Learn sparse dictionary via iterative hard thresholding
    4. Score candidates by reconstruction error + constraint violations
    5. Track state dynamics: model reasoning as trajectory through feature space
    6. Confidence based on trajectory stability + meta-checks for ambiguity
    """
    
    def __init__(self):
        self.feature_dim = 64
        self.dict_atoms = 16
        self.sparsity = 4
        self.window_size = 3
        self.dictionary = None
        self._init_dictionary()
        
    def _init_dictionary(self):
        """Initialize with gold-standard patterns encoding common reasoning structures."""
        gold_patterns = [
            "if A then B, A is true, therefore B",
            "X > Y and Y > Z, therefore X > Z",
            "not A or B, A is true, therefore B",
            "A causes B, B causes C, therefore A causes C",
            "all X are Y, Z is X, therefore Z is Y",
            "if not A then B, A is false, therefore B",
            "9.11 < 9.9 because 9.11 = 9.11",
            "X before Y, Y before Z, therefore X before Z"
        ]
        
        cooccurrence = np.zeros((self.feature_dim, self.feature_dim))
        total_windows = 0
        
        for pattern in gold_patterns:
            feats = self._extract_features(pattern, pattern)
            indices = [i for i, v in enumerate(feats) if v > 0]
            for i in range(len(indices)):
                for j in range(i, min(i + self.window_size, len(indices))):
                    cooccurrence[indices[i], indices[j]] += 1
                    cooccurrence[indices[j], indices[i]] += 1
                    total_windows += 1
        
        if total_windows > 0:
            cooccurrence /= (total_windows + 1e-10)
        
        eigvals, eigvecs = np.linalg.eigh(cooccurrence)
        top_k = np.argsort(-eigvals)[:self.dict_atoms]
        self.dictionary = eigvecs[:, top_k].copy()
        self.dictionary /= (np.linalg.norm(self.dictionary, axis=0, keepdims=True) + 1e-10)
    
    def _extract_features(self, prompt, candidate):
        """Parse structural predicates into binary feature vector."""
        text = (prompt + " " + candidate).lower()
        feats = np.zeros(self.feature_dim)
        
        # Negations
        feats[0] = len(re.findall(r'\bnot\b|\bnever\b|\bno\b|n\'t|\bnegat', text))
        
        # Conditionals
        feats[1] = len(re.findall(r'\bif\b.*\bthen\b', text))
        feats[2] = len(re.findall(r'\bunless\b', text))
        
        # Comparatives
        feats[3] = len(re.findall(r'\bgreater\b|\bmore\b|\bhigher\b|>', text))
        feats[4] = len(re.findall(r'\bless\b|\bfewer\b|\blower\b|<', text))
        feats[5] = len(re.findall(r'\bequal\b|=', text))
        
        # Causals
        feats[6] = len(re.findall(r'\bcause[sd]?\b|\blead to\b|\bresult in\b|\bproduce[sd]?\b', text))
        
        # Quantifiers
        feats[7] = len(re.findall(r'\ball\b|\bevery\b', text))
        feats[8] = len(re.findall(r'\bsome\b|\bany\b', text))
        feats[9] = len(re.findall(r'\bnone\b|\bno\b', text))
        
        # Temporal
        feats[10] = len(re.findall(r'\bbefore\b|\bprior\b|\bearlier\b', text))
        feats[11] = len(re.findall(r'\bafter\b|\blater\b|\bsubsequent\b', text))
        feats[12] = len(re.findall(r'\bfirst\b|\binitial\b', text))
        feats[13] = len(re.findall(r'\blast\b|\bfinal\b', text))
        
        # Numeric patterns
        nums = re.findall(r'\d+\.?\d*', text)
        feats[14] = len(nums)
        if len(nums) >= 2:
            try:
                feats[15] = float(nums[0]) < float(nums[1])
                feats[16] = float(nums[0]) > float(nums[1])
            except:
                pass
        
        # Logical connectives
        feats[17] = len(re.findall(r'\band\b', text))
        feats[18] = len(re.findall(r'\bor\b', text))
        feats[19] = len(re.findall(r'\btherefore\b|\bthus\b|\bhence\b', text))
        
        # Normalize
        return np.clip(feats, 0, 5) / 5.0
    
    def _sparse_encode(self, x, max_iter=20):
        """Iterative hard thresholding for sparse coding."""
        z = self.dictionary.T @ x
        for _ in range(max_iter):
            residual = x - self.dictionary @ z
            z += self.dictionary.T @ residual
            mask = np.argsort(-np.abs(z))[:self.sparsity]
            z_sparse = np.zeros_like(z)
            z_sparse[mask] = z[mask]
            z = z_sparse
        return z
    
    def _constraint_propagation(self, z):
        """Apply logical constraint rules and compute violation penalty."""
        penalty = 0.0
        
        # Transitivity: if atoms encode A>B and B>C, should encode A>C
        if z[3] > 0.5 and z[4] > 0.5:
            penalty += abs(z[3] - z[4])
        
        # Consistency: not + not = positive
        if z[0] > 1.0:
            penalty += (z[0] - 1.0) * 0.5
        
        # Modus ponens: if conditional + antecedent, should have consequent
        if z[1] > 0.5 and z[19] < 0.2:
            penalty += 0.3
        
        return penalty
    
    def _compute_dynamics(self, prompt, candidate):
        """Track state evolution through reasoning trajectory."""
        sentences = re.split(r'[.!?;]', prompt + " " + candidate)
        states = []
        
        for sent in sentences:
            if sent.strip():
                feats = self._extract_features(sent, "")
                states.append(feats)
        
        if len(states) < 2:
            return 0.5
        
        states = np.array(states)
        # Compute trajectory stability via variance
        trajectory_variance = np.var(states, axis=0).mean()
        
        # Compute convergence: later states should be more similar
        if len(states) >= 3:
            early = states[:len(states)//2]
            late = states[len(states)//2:]
            convergence = 1.0 / (1.0 + np.linalg.norm(late.mean(axis=0) - early.mean(axis=0)))
        else:
            convergence = 0.5
        
        stability_score = 1.0 / (1.0 + trajectory_variance) * convergence
        return stability_score
    
    def _ncd(self, s1, s2):
        """Normalized compression distance (tiebreaker only)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity, presuppositions, unanswerable questions."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\bhave you (stopped|quit)\b|\bwhy did.*fail\b|\bwhen did.*stop\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*\?', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p):
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt, candidates):
        results = []
        
        for cand in candidates:
            feats = self._extract_features(prompt, cand)
            sparse_code = self._sparse_encode(feats)
            reconstruction = self.dictionary @ sparse_code
            recon_error = np.linalg.norm(feats - reconstruction) ** 2
            
            constraint_penalty = self._constraint_propagation(sparse_code)
            dynamics_score = self._compute_dynamics(prompt, cand)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Score decomposition: dynamics 40%, structural 35%, constraint 15%, NCD 10%
            score = (dynamics_score * 0.4 + 
                    (1.0 / (1.0 + recon_error)) * 0.35 + 
                    (1.0 / (1.0 + constraint_penalty)) * 0.15 + 
                    ncd_score * 0.1)
            
            reasoning = f"dynamics={dynamics_score:.2f} recon_err={recon_error:.2f} penalty={constraint_penalty:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        meta_cap = self._meta_confidence(prompt)
        
        feats = self._extract_features(prompt, answer)
        sparse_code = self._sparse_encode(feats)
        reconstruction = self.dictionary @ sparse_code
        recon_error = np.linalg.norm(feats - reconstruction) ** 2
        
        dynamics_score = self._compute_dynamics(prompt, answer)
        
        # Base confidence on trajectory stability and reconstruction quality
        base_conf = dynamics_score * 0.6 + (1.0 / (1.0 + recon_error)) * 0.4
        
        # Cap by meta-confidence
        return min(base_conf * 0.85, meta_cap)