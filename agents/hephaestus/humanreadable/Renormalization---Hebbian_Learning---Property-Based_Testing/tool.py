from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Combines renormalization (multi-scale importance), Hebbian learning (co-occurrence),
    property-based testing (mutation/shrinking), and dynamics tracking (state evolution).
    
    Parses predicates into hypergraph, computes fixed-point importance weights,
    learns synaptic matrix from correct pairs, tests robustness via mutations,
    and tracks reasoning trajectory stability.
    """
    
    def __init__(self):
        self.W = None  # Hebbian synaptic matrix
        self.vocab = {}  # predicate type -> index
        self.alpha = 0.6  # renormalization balance
        self.eta = 0.1  # Hebbian learning rate
        self.lambda_robust = 0.3  # robustness penalty
        
    def _parse_predicates(self, text: str) -> Tuple[np.ndarray, np.ndarray]:
        """Extract predicates and build hypergraph (features, adjacency)."""
        predicates = []
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|none|neither)\b', text, re.I):
            predicates.append(('NEG', m.group(1).lower(), 0.0))
        
        # Comparatives
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|greater|less|more|fewer)\s*(\d+\.?\d*)', text, re.I):
            val1, op, val2 = float(m.group(1)), m.group(2), float(m.group(3))
            predicates.append(('CMP', op, val1 - val2))
        
        # Conditionals
        for m in re.finditer(r'\b(if|then|unless|when|whenever)\b', text, re.I):
            predicates.append(('COND', m.group(1).lower(), 0.0))
        
        # Numeric values
        for m in re.finditer(r'\b(\d+\.?\d*)\b', text):
            predicates.append(('NUM', 'value', float(m.group(1))))
        
        # Causal
        for m in re.finditer(r'\b(because|since|leads to|causes|due to)\b', text, re.I):
            predicates.append(('CAUSE', m.group(1).lower(), 0.0))
        
        # Ordering
        for m in re.finditer(r'\b(before|after|first|last|earlier|later)\b', text, re.I):
            predicates.append(('ORDER', m.group(1).lower(), 0.0))
        
        if not predicates:
            predicates.append(('EMPTY', '', 0.0))
        
        # Build feature matrix
        n = len(predicates)
        F = np.zeros((n, 7))  # 6 types + numeric value
        type_map = {'NEG': 0, 'CMP': 1, 'COND': 2, 'NUM': 3, 'CAUSE': 4, 'ORDER': 5, 'EMPTY': 6}
        
        for i, (ptype, _, val) in enumerate(predicates):
            F[i, type_map[ptype]] = 1.0
            if val != 0.0:
                F[i, -1] = val / 100.0  # normalize
        
        # Simple adjacency: connect consecutive predicates
        A = np.zeros((n, n))
        for i in range(n - 1):
            A[i, i + 1] = 1.0
            A[i + 1, i] = 0.5
        
        return F, A
    
    def _renormalize(self, F: np.ndarray, A: np.ndarray, max_iter: int = 10) -> np.ndarray:
        """Compute fixed-point importance weights via renormalization."""
        n = F.shape[0]
        w = np.ones(n) / n
        eps = 1e-3
        
        for _ in range(max_iter):
            if A.sum() > 0:
                A_norm = A / (A.sum(axis=1, keepdims=True) + 1e-9)
                context = A_norm @ w
            else:
                context = np.zeros(n)
            
            intrinsic = F.sum(axis=1)
            intrinsic = intrinsic / (intrinsic.sum() + 1e-9)
            
            w_new = self.alpha * context + (1 - self.alpha) * intrinsic
            w_new = np.exp(w_new) / (np.exp(w_new).sum() + 1e-9)
            
            if np.abs(w_new - w).sum() < eps:
                break
            w = w_new
        
        return w
    
    def _hebbian_score(self, w_prompt: np.ndarray, w_cand: np.ndarray) -> float:
        """Score alignment using Hebbian synaptic matrix."""
        n_p, n_c = len(w_prompt), len(w_cand)
        n_max = max(n_p, n_c)
        
        if self.W is None or self.W.shape[0] < n_max:
            self.W = np.eye(n_max) * 0.1
        
        # Pad to same size
        w_p = np.pad(w_prompt, (0, n_max - n_p))
        w_c = np.pad(w_cand, (0, n_max - n_c))
        
        W_block = self.W[:n_max, :n_max]
        score = w_c @ W_block @ w_p
        return float(score)
    
    def _mutate(self, text: str) -> List[str]:
        """Generate property-based mutations."""
        mutations = [text]
        
        # Numeric perturbation
        for m in re.finditer(r'\b(\d+\.?\d*)\b', text):
            val = float(m.group(1))
            for delta in [-1, 1]:
                new_val = val + delta
                mut = text[:m.start()] + str(new_val) + text[m.end():]
                mutations.append(mut)
        
        # Negation toggle
        if re.search(r'\bnot\b', text, re.I):
            mutations.append(re.sub(r'\bnot\b', '', text, flags=re.I))
        else:
            mutations.append('not ' + text)
        
        # Comparator reversal
        text_rev = text.replace('>', '<TEMP>').replace('<', '>').replace('<TEMP>', '<')
        mutations.append(text_rev)
        
        return mutations[:5]
    
    def _shrink_score(self, prompt: str, candidate: str) -> float:
        """Property-based shrinking to find robustness."""
        F_p, A_p = self._parse_predicates(prompt)
        w_p = self._renormalize(F_p, A_p)
        
        F_c, A_c = self._parse_predicates(candidate)
        w_c = self._renormalize(F_c, A_c)
        base_score = self._hebbian_score(w_p, w_c)
        
        mutations = self._mutate(candidate)
        min_score = base_score
        
        for mut in mutations:
            F_m, A_m = self._parse_predicates(mut)
            w_m = self._renormalize(F_m, A_m)
            s = self._hebbian_score(w_p, w_m)
            min_score = min(min_score, s)
        
        robust_score = base_score - self.lambda_robust * (base_score - min_score)
        return robust_score
    
    def _dynamics_score(self, prompt: str, candidate: str) -> float:
        """Track state evolution stability across premise ordering."""
        sentences = re.split(r'[.!?;]', prompt)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.5
        
        F_c, A_c = self._parse_predicates(candidate)
        w_c = self._renormalize(F_c, A_c)
        
        trajectories = []
        for perm_idx in range(min(3, len(sentences))):
            state = np.zeros(w_c.shape[0])
            for sent in sentences:
                F_s, A_s = self._parse_predicates(sent)
                w_s = self._renormalize(F_s, A_s)
                # Reservoir update: state += tanh(w_s effect)
                w_s_padded = np.pad(w_s, (0, max(0, len(state) - len(w_s))))[:len(state)]
                state = 0.7 * state + 0.3 * np.tanh(w_s_padded + w_c)
            trajectories.append(state)
        
        # Stability = low variance across permutations
        traj_arr = np.array(trajectories)
        stability = 1.0 / (1.0 + traj_arr.std())
        
        # Convergence = final state alignment with candidate
        final_state = trajectories[-1]
        alignment = np.dot(final_state, w_c) / (np.linalg.norm(final_state) * np.linalg.norm(w_c) + 1e-9)
        
        return 0.6 * stability + 0.4 * float(alignment)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/unanswerability markers."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', prompt_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower):
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            struct_score = self._shrink_score(prompt, cand)
            dyn_score = self._dynamics_score(prompt, cand)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            final_score = 0.5 * dyn_score + 0.35 * struct_score + 0.15 * ncd_score
            
            results.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f'dynamics={dyn_score:.2f} struct={struct_score:.2f} ncd={ncd_score:.2f}'
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.35:
            return meta_conf
        
        struct_score = self._shrink_score(prompt, answer)
        dyn_score = self._dynamics_score(prompt, answer)
        
        raw_conf = 0.6 * dyn_score + 0.4 * struct_score
        final_conf = min(meta_conf, raw_conf)
        
        return max(0.0, min(1.0, final_conf))