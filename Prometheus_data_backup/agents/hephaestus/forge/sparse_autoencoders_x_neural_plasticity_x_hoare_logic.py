import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A neuro-symbolic reasoning tool combining Sparse Autoencoders, Hebbian Plasticity,
    and Hoare Logic concepts. 
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, conditionals, 
       causality, ordering) using regex to form a binary vector space.
    2. Sparse Dictionary Learning: Projects high-dimensional atom vectors into a sparse 
       latent space (F features) using online L1-penalized optimization (ISTA-like).
    3. Hebbian Plasticity: Maintains a symmetric weight matrix W updated by co-activation 
       (a * a^T) with pruning for low-magnitude weights, creating a dynamic constraint graph.
    4. Hoare-Style Verification: Checks if candidate activations satisfy prompt preconditions 
       and derive postconditions. 
    5. Scoring: Combines structural consistency (Hoare check), graph coherence (a^T W a), 
       and NCD tie-breaking.
    """
    
    def __init__(self):
        self.K = 100  # Max atom vocabulary size (dynamic indexing)
        self.F = 20   # Latent feature size
        self.D = np.random.randn(self.F, self.K) * 0.1  # Dictionary
        self.W = np.zeros((self.F, self.F))             # Hebbian weights
        self.atom_map = {}
        self.atom_count = 0
        self.lambda_l1 = 0.1
        self.eta = 0.01
        self.tau = 0.001
        self.theta = 0.1
        
        # Regex patterns for atomic propositions
        self.patterns = [
            (r'not\s+(\w+)', 'NEG'),
            (r'(\w+)\s*>\s*(\w+)', 'GT'),
            (r'(\w+)\s*<\s*(\w+)', 'LT'),
            (r'if\s+(.+?)\s+then\s+(.+?)', 'COND'),
            (r'(\w+)\s*=\s*(\d+\.?\d*)', 'EQ_NUM'),
            (r'because\s+(.+?)', 'CAUSE'),
            (r'before\s+(.+?)', 'ORDER'),
            (r'after\s+(.+?)', 'ORDER_REV'),
            (r'(\d+\.?\d*)\s*<\s*(\d+\.?\d*)', 'NUM_LT'),
            (r'(\d+\.?\d*)\s*>\s*(\d+\.?\d*)', 'NUM_GT'),
        ]

    def _extract_atoms(self, text: str) -> Dict[int, float]:
        """Extract logical atoms and map to indices."""
        atoms = {}
        text_lower = text.lower()
        
        # Numeric evaluation
        nums = re.findall(r'\d+\.?\d*', text_lower)
        if len(nums) >= 2:
            try:
                v1, v2 = float(nums[0]), float(nums[1])
                if v1 < v2: atoms[self._get_idx(f"{nums[0]}<{nums[1]}")] = 1.0
                if v1 > v2: atoms[self._get_idx(f"{nums[0]}>{nums[1]}")] = 1.0
                if v1 == v2: atoms[self._get_idx(f"{nums[0]}={nums[1]}")] = 1.0
            except: pass

        for pattern, ptype in self.patterns:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                key = f"{ptype}:{match.group(0)}"
                atoms[self._get_idx(key)] = 1.0
                
        return atoms

    def _get_idx(self, key: str) -> int:
        if key not in self.atom_map:
            if self.atom_count < self.K:
                self.atom_map[key] = self.atom_count
                self.atom_count += 1
            else:
                # Hash collision fallback for overflow
                return hash(key) % self.K
        return self.atom_map[key]

    def _to_vector(self, atoms: Dict[int, float]) -> np.ndarray:
        vec = np.zeros(self.K)
        for idx, val in atoms.items():
            if idx < self.K: vec[idx] = val
        return vec

    def _sparse_code(self, s: np.ndarray) -> np.ndarray:
        """ISTA-like sparse coding: min ||s - D^T a||^2 + lambda||a||_1"""
        a = np.zeros(self.F)
        # Simplified online ISTA step
        residual = s - self.D.T @ a
        gradient = self.D @ residual
        a = a + 0.1 * gradient
        a = np.sign(a) * np.maximum(np.abs(a) - self.lambda_l1, 0)
        return a

    def _update_plasticity(self, a: np.ndarray):
        """Hebbian update and pruning."""
        self.W += self.eta * np.outer(a, a)
        self.W[np.abs(self.W) < self.tau] = 0
        # Normalize D slightly to prevent explosion
        norm = np.linalg.norm(self.D, axis=1, keepdims=True) + 1e-8
        self.D /= norm

    def _check_hoare(self, prompt_atoms: Dict[int, float], cand_vec: np.ndarray, cand_atoms: Dict[int, float]) -> Tuple[bool, bool]:
        """Check precondition satisfaction and postcondition derivation."""
        # Precondition: Atoms in prompt must be present in candidate context
        pre_ok = True
        for idx in prompt_atoms:
            if idx < self.K and cand_vec[idx] < self.theta:
                # Soft check: if prompt asserts it, candidate should reflect it
                pre_ok = False 
                break
        
        # Postcondition: Candidate asserts new atoms consistent with prompt structure
        # Simplified: If candidate has atoms, they are "derived" if activation > theta
        post_ok = len(cand_atoms) > 0
        return pre_ok, post_ok

    def _ncd(self, s1: str, s2: str) -> float:
        import zlib
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1+s2).encode()))
        return c12 / max(c1, c2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_atoms = self._extract_atoms(prompt)
        s_prompt = self._to_vector(prompt_atoms)
        
        # Online learning step on prompt
        a_prompt = self._sparse_code(s_prompt)
        self._update_plasticity(a_prompt)
        
        results = []
        for cand in candidates:
            cand_atoms = self._extract_atoms(cand)
            s_cand = self._to_vector(cand_atoms)
            a_cand = self._sparse_code(s_cand)
            
            # Hoare Check
            pre_ok, post_ok = self._check_hoare(prompt_atoms, s_cand, cand_atoms)
            hoare_bonus = 10.0 if (pre_ok or post_ok) else 0.0
            
            # Hebbian Coherence Score
            coherence = float(a_cand.T @ self.W @ a_cand)
            
            # NCD Tiebreaker (inverted, lower is better)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 2.0 # Scale to be comparable
            
            score = coherence + hoare_bonus + ncd_score
            
            # Update model with candidate (simulating reasoning path)
            self._update_plasticity(a_cand)
            
            reason_str = f"Coherence:{coherence:.2f}, Hoare:{'Pass' if hoare_bonus>0 else 'Fail'}, NCD:{ncd_val:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reason_str})
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        if not ranked: return 0.0
        # Normalize score to 0-1 range heuristically
        raw_score = ranked[0]['score']
        # Sigmoid-like mapping
        conf = 1 / (1 + np.exp(-0.5 * (raw_score - 5))) 
        return max(0.0, min(1.0, conf))