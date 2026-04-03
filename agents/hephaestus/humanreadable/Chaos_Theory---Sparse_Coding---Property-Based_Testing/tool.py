from collections import defaultdict

"""
Chaos Theory x Sparse Coding x Property-Based Testing Reasoning Tool

Combines:
- Logical primitive extraction (regex-based parsing)
- Sparse coding via ISTA to learn a logical basis
- Lyapunov-like sensitivity analysis via property-based perturbations
- Dynamical systems tracking of state evolution
"""

import re
import numpy as np
import zlib
from collections import Counter, defaultdict

class ReasoningTool:
    def __init__(self):
        self.dictionary = None  # Sparse coding dictionary D
        self.primitives_vocab = []  # Ordered list of primitive types
        self.alpha = 1.0  # reconstruction error weight
        self.beta = 0.5  # sensitivity weight
        self.gamma = 0.3  # sparsity reward weight
        self.lambda_sparse = 0.1  # L1 regularization
        
    def _extract_primitives(self, text):
        """Extract logical primitives from text"""
        text_lower = text.lower()
        primitives = []
        
        # Negations
        if re.search(r'\bn(?:o|ot|\'t)\b|never|neither|none', text_lower):
            primitives.append('NEG')
        
        # Comparatives
        if re.search(r'>|greater|more than|larger|bigger', text_lower):
            primitives.append('GT')
        if re.search(r'<|less than|smaller|fewer', text_lower):
            primitives.append('LT')
        if re.search(r'>=|at least|no less than', text_lower):
            primitives.append('GTE')
        if re.search(r'<=|at most|no more than', text_lower):
            primitives.append('LTE')
        
        # Conditionals
        if re.search(r'\bif\b.*\bthen\b|\bunless\b|implies', text_lower):
            primitives.append('IFTHEN')
        
        # Causals
        if re.search(r'because|leads? to|results? in|causes?|therefore', text_lower):
            primitives.append('CAUSAL')
        
        # Ordering
        if re.search(r'\bbefore\b|\bafter\b|\bfirst\b|\blast\b|earlier|later', text_lower):
            primitives.append('ORDER')
        
        # Quantifiers
        if re.search(r'\ball\b|\bevery\b|\beach\b', text_lower):
            primitives.append('QUANT_ALL')
        if re.search(r'\bsome\b|\bany\b', text_lower):
            primitives.append('QUANT_SOME')
        
        # Numbers
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        for n in nums:
            primitives.append(f'NUM:{n}')
        
        return primitives
    
    def _primitives_to_vector(self, primitives):
        """Convert primitive list to sparse binary vector"""
        if not self.primitives_vocab:
            return np.zeros(1)
        vec = np.zeros(len(self.primitives_vocab))
        for p in primitives:
            if p in self.primitives_vocab:
                vec[self.primitives_vocab.index(p)] += 1
        return vec
    
    def _build_dictionary(self, vectors, k=10):
        """Build sparse coding dictionary via ISTA"""
        m = vectors.shape[1]
        k = min(k, m)
        D = np.random.randn(m, k)
        D = D / (np.linalg.norm(D, axis=0, keepdims=True) + 1e-8)
        
        for _ in range(20):
            A = np.zeros((k, vectors.shape[0]))
            for i, x in enumerate(vectors):
                A[:, i] = self._ista(x, D, lam=self.lambda_sparse, iters=15)
            D = vectors.T @ A.T
            D = D / (np.linalg.norm(D, axis=0, keepdims=True) + 1e-8)
        
        return D
    
    def _ista(self, x, D, lam=0.1, iters=20):
        """Iterative Shrinkage-Thresholding Algorithm"""
        a = np.zeros(D.shape[1])
        L = np.linalg.norm(D.T @ D, 2)
        step = 1.0 / (L + 1e-8)
        
        for _ in range(iters):
            grad = D.T @ (D @ a - x)
            a_new = a - step * grad
            a = np.sign(a_new) * np.maximum(np.abs(a_new) - step * lam, 0)
        
        return a
    
    def _perturb_primitives(self, primitives):
        """Generate perturbations for sensitivity analysis"""
        if len(primitives) == 0:
            return primitives
        
        perturbed = primitives.copy()
        choice = np.random.randint(0, 4)
        
        if choice == 0 and 'NEG' in perturbed:
            perturbed.remove('NEG')
        elif choice == 0:
            perturbed.append('NEG')
        elif choice == 1:
            for i, p in enumerate(perturbed):
                if p.startswith('NUM:'):
                    num = float(p.split(':')[1])
                    perturbed[i] = f'NUM:{num + np.random.randn()}'
                    break
        elif choice == 2 and 'GT' in perturbed:
            perturbed[perturbed.index('GT')] = 'LT'
        elif choice == 3 and len(perturbed) > 1:
            np.random.shuffle(perturbed)
        
        return perturbed
    
    def _lyapunov_sensitivity(self, primitives, D, N=15):
        """Compute Lyapunov-like sensitivity metric"""
        x = self._primitives_to_vector(primitives)
        a = self._ista(x, D, self.lambda_sparse)
        
        divergences = []
        for _ in range(N):
            x_p_prims = self._perturb_primitives(primitives)
            x_p = self._primitives_to_vector(x_p_prims)
            a_p = self._ista(x_p, D, self.lambda_sparse)
            
            dx = np.linalg.norm(x_p - x) + 1e-8
            da = np.linalg.norm(a_p - a) + 1e-8
            divergences.append(np.log(da / dx))
        
        return np.mean(divergences)
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity, presuppositions, unanswerable questions"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'have you stopped|did you stop|why did.*fail|when did.*stop', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every.*\ba\b|all.*\ban?\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'he|she|it|they', p_lower) and re.search(r'who|which one', p_lower):
            return 0.2
        
        # False dichotomy
        if re.search(r'either.*or\b', p_lower) and not re.search(r'both|neither', p_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\bbest\b|\bworst\b|\bfavorite\b|\bprefer\b', p_lower):
            return 0.25
        
        return 1.0
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def evaluate(self, prompt, candidates):
        """Evaluate and rank candidates"""
        # Build vocabulary from all text
        all_text = [prompt] + candidates
        all_prims = []
        for t in all_text:
            all_prims.extend(self._extract_primitives(t))
        self.primitives_vocab = sorted(set(all_prims))
        
        # Build dictionary from candidates
        if len(self.primitives_vocab) > 0:
            vectors = np.array([self._primitives_to_vector(self._extract_primitives(c)) for c in candidates])
            if vectors.shape[0] > 0:
                self.dictionary = self._build_dictionary(vectors, k=min(10, len(self.primitives_vocab)))
        
        results = []
        for cand in candidates:
            cand_prims = self._extract_primitives(cand)
            
            # Sparse coding score
            if self.dictionary is not None and len(self.primitives_vocab) > 0:
                x = self._primitives_to_vector(cand_prims)
                a = self._ista(x, self.dictionary, self.lambda_sparse)
                recon_error = np.linalg.norm(x - self.dictionary @ a) ** 2
                sparsity = np.sum(a != 0)
                sensitivity = self._lyapunov_sensitivity(cand_prims, self.dictionary)
                
                sparse_score = -self.alpha * recon_error - self.beta * sensitivity + self.gamma * sparsity
            else:
                sparse_score = 0.0
            
            # Structural score
            struct_score = len(cand_prims) * 0.1
            
            # NCD (max 15%)
            ncd_score = (1.0 - self._ncd(prompt, cand)) * 0.15
            
            # Total
            total_score = sparse_score * 0.5 + struct_score * 0.35 + ncd_score
            
            reasoning = f"Sparse:{sparse_score:.2f} Struct:{struct_score:.2f} NCD:{ncd_score:.2f}"
            results.append({"candidate": cand, "score": total_score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1"""
        meta_conf = self._meta_confidence(prompt)
        
        # Extract primitives
        p_prims = self._extract_primitives(prompt)
        a_prims = self._extract_primitives(answer)
        
        if len(p_prims) == 0 and len(a_prims) == 0:
            return 0.3 * meta_conf
        
        # Overlap score
        overlap = len(set(p_prims) & set(a_prims)) / (len(set(p_prims) | set(a_prims)) + 1)
        
        # Complexity penalty (short answers are uncertain)
        complexity = min(1.0, len(answer) / 20.0)
        
        base_conf = min(0.85, overlap * 0.7 + complexity * 0.3)
        
        return base_conf * meta_conf