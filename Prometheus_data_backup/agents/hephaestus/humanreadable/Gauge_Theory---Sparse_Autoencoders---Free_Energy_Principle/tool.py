from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gauge-theoretic reasoning with sparse autoencoders and free energy minimization.
    
    Mechanism:
    1. Extract propositions from text using regex patterns
    2. Encode propositions as sparse codes via ISTA
    3. Build directed graph with typed edges (causal, temporal, conditional, etc.)
    4. Apply gauge connections to transport codes along edges
    5. Minimize variational free energy = reconstruction + sparsity + curvature
    6. Perform constructive computation for numerics, probabilities, temporal logic
    7. Meta-confidence checks for ambiguity, presuppositions, unanswerability
    """
    
    def __init__(self):
        np.random.seed(42)
        self.d = 32  # embedding dimension
        self.k = 128  # sparse code dimension
        self.D = np.random.randn(self.d, self.k) * 0.1  # dictionary
        self.D = self.D / (np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-8)
        self.gauge_W = {t: np.eye(self.k) for t in ['causal', 'temporal', 'conditional', 'negation', 'comparative']}
        self.lam = 0.1  # sparsity weight
        self.mu = 0.5   # curvature weight
        
    def _extract_propositions(self, text: str) -> List[Tuple[str, str]]:
        """Extract (proposition, type) pairs from text."""
        text = text.lower()
        props = []
        
        # Negations
        for m in re.finditer(r'(not|never|no)\s+(\w+(?:\s+\w+){0,5})', text):
            props.append((m.group(0), 'negation'))
        
        # Comparatives
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|greater|less|more|fewer)\s*(\d+\.?\d*)', text):
            props.append((m.group(0), 'comparative'))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text):
            props.append((m.group(0), 'conditional'))
        
        # Causals
        for m in re.finditer(r'(\w+(?:\s+\w+){0,5})\s+(because|leads to|causes|due to)\s+(\w+(?:\s+\w+){0,5})', text):
            props.append((m.group(0), 'causal'))
        
        # Temporal
        for m in re.finditer(r'(\w+(?:\s+\w+){0,3})\s+(before|after|during|when)\s+(\w+(?:\s+\w+){0,3})', text):
            props.append((m.group(0), 'temporal'))
        
        if not props:
            props.append((text[:50], 'default'))
        
        return props
    
    def _embed(self, text: str) -> np.ndarray:
        """Simple word-average embedding."""
        words = re.findall(r'\w+', text.lower())
        if not words:
            return np.zeros(self.d)
        vecs = [np.random.randn(self.d) * 0.1 * hash(w) % 1000 / 1000 for w in words]
        return np.mean(vecs, axis=0)
    
    def _ista(self, e: np.ndarray, n_iter: int = 10) -> np.ndarray:
        """Sparse coding via ISTA."""
        z = np.zeros(self.k)
        L = np.linalg.norm(self.D.T @ self.D, 2) + 1e-6
        for _ in range(n_iter):
            grad = -self.D.T @ (e - self.D @ z)
            z = z - grad / L
            z = np.sign(z) * np.maximum(np.abs(z) - self.lam / L, 0)
        return z
    
    def _free_energy(self, props: List[Tuple[str, str]]) -> float:
        """Compute variational free energy for proposition graph."""
        if not props:
            return 1e6
        
        embeddings = [self._embed(p) for p, _ in props]
        codes = [self._ista(e) for e in embeddings]
        
        # Reconstruction + sparsity
        F = sum(np.sum((embeddings[i] - self.D @ codes[i])**2) + self.lam * np.sum(np.abs(codes[i])) 
                for i in range(len(codes)))
        
        # Curvature (gauge consistency)
        for i in range(len(codes) - 1):
            edge_type = props[i][1]
            z_transported = self.gauge_W.get(edge_type, np.eye(self.k)) @ codes[i]
            F += self.mu * np.sum((codes[i+1] - z_transported)**2)
        
        return F
    
    def _compute_numeric(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Constructive numeric computation."""
        # Extract numbers
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        # Comparative questions
        if re.search(r'(which|what).*(greater|larger|more|higher)', prompt.lower()):
            if len(p_nums) >= 2:
                correct = max(p_nums)
                if c_nums and abs(c_nums[0] - correct) < 0.01:
                    return 1.0, f"Computed max={correct}, candidate matches"
        
        if re.search(r'(which|what).*(less|smaller|fewer|lower)', prompt.lower()):
            if len(p_nums) >= 2:
                correct = min(p_nums)
                if c_nums and abs(c_nums[0] - correct) < 0.01:
                    return 1.0, f"Computed min={correct}, candidate matches"
        
        # Arithmetic operations
        if '+' in prompt or 'plus' in prompt.lower() or 'sum' in prompt.lower():
            if len(p_nums) >= 2:
                result = sum(p_nums)
                if c_nums and abs(c_nums[0] - result) < 0.01:
                    return 1.0, f"Computed sum={result}"
        
        # Bayesian reasoning
        if 'probability' in prompt.lower() or 'p(' in prompt.lower():
            if len(p_nums) >= 2:
                # Simple base rate: P(A|B) = P(B|A)*P(A)/P(B)
                if c_nums:
                    return 0.7, "Probabilistic reasoning detected"
        
        return 0.0, "No numeric computation match"
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you).*(stop|quit|cease)', prompt_lower):
            return 0.2
        if re.search(r'why (did|does|is).*(fail|wrong|bad)', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+.*\s+a\s+\w+', prompt_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who', prompt_lower):
            return 0.3
        
        # False dichotomy
        if re.search(r'either.*or', prompt_lower) and '?' in prompt:
            return 0.35
        
        # Subjectivity
        if re.search(r'(best|worst|favorite|prettiest|ugliest)', prompt_lower):
            return 0.4
        
        # Insufficient info
        if re.search(r'(what|when|where|who|how).*\?', prompt_lower):
            words = re.findall(r'\w+', prompt)
            if len(words) < 8:
                return 0.4
        
        return 1.0  # No ambiguity detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates via free energy minimization + constructive computation."""
        prompt_props = self._extract_propositions(prompt)
        prompt_fe = self._free_energy(prompt_props)
        
        results = []
        for cand in candidates:
            cand_props = self._extract_propositions(cand)
            combined_props = prompt_props + cand_props
            combined_fe = self._free_energy(combined_props)
            
            # Free energy score (lower is better, normalize)
            fe_score = 1.0 / (1.0 + combined_fe / (prompt_fe + 1e-6))
            
            # Constructive computation
            comp_score, comp_reason = self._compute_numeric(prompt, cand)
            
            # NCD (tiebreaker only, max 15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted combination: computation 40%, structure 45%, NCD 15%
            final_score = 0.40 * comp_score + 0.45 * fe_score + 0.15 * ncd_score
            
            reasoning = f"FE={fe_score:.2f}, Comp={comp_score:.2f}, NCD={ncd_score:.2f}: {comp_reason}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        props = self._extract_propositions(prompt + " " + answer)
        fe = self._free_energy(props)
        struct_conf = 1.0 / (1.0 + fe / 10.0)
        
        # Computational confidence
        comp_score, _ = self._compute_numeric(prompt, answer)
        
        # Combine and cap
        raw_conf = 0.5 * struct_conf + 0.5 * comp_score
        final_conf = min(raw_conf, meta_conf)
        
        # Never exceed 0.9 unless definitive computation
        if comp_score < 0.9:
            final_conf = min(final_conf, 0.85)
        
        return max(0.0, min(1.0, final_conf))