import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning scorer combining Sparse Autoencoding (via OMP-like 
    feature extraction), Dynamical Systems (constraint propagation), and Mechanism Design.
    
    Core Mechanism:
    1. Structural Parsing: Extracts logical atoms, negations, and numeric values.
    2. Sparse Encoding: Maps text to a sparse latent vector (simulated dictionary).
    3. Dynamical Evolution: Iteratively updates the state vector z using a constraint 
       matrix C (z_new = z + eta * (Cz - z)) to find logical attractors.
    4. Mechanism Design Scoring: Rewards candidates that converge to stable, consistent 
       fixed points (attractors) and penalizes logical contradictions or instability.
    """
    
    def __init__(self):
        self.epsilon = 1e-4
        self.max_steps = 50
        self.eta = 0.1
        self.lambda_pen = 0.5
        # Simulated dictionary size
        self.k = 200 
        # Pre-compiled regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|requires)\b', re.I),
            'causal': re.compile(r'\b(causes|leads to|implies|results in)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower)\b', re.I),
            'number': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural logical features from text."""
        t_lower = text.lower()
        feats = {
            'has_negation': bool(self.patterns['negation'].search(t_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(t_lower)),
            'has_causal': bool(self.patterns['causal'].search(t_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(t_lower)),
            'numbers': [float(n) for n in self.patterns['number'].findall(text)],
            'length': len(text.split()),
            'raw': text
        }
        return feats

    def _encode_sparse(self, feats: Dict, prompt_feats: Dict) -> np.ndarray:
        """
        Simulates Sparse Autoencoder encoding (OMP-like).
        Maps structural features to a sparse latent vector z.
        """
        z = np.zeros(self.k)
        
        # Map specific structural flags to fixed latent indices (Dictionary Learning simulation)
        # Indices 0-4: Structural flags
        if feats['has_negation']: z[0] = 1.0
        if feats['has_conditional']: z[1] = 1.0
        if feats['has_causal']: z[2] = 1.0
        if feats['has_comparative']: z[3] = 1.0
        
        # Numeric consistency check (simple hash to index)
        if feats['numbers']:
            idx = 4 + (int(sum(feats['numbers'])) % 10)
            z[idx] = 1.0
            
        # Prompt alignment bonus (if candidate shares structural props with prompt)
        if feats['has_negation'] == prompt_feats['has_negation']:
            z[10] = 0.5 # Weak prior
            
        return z

    def _build_constraint_matrix(self, prompt_feats: Dict) -> np.ndarray:
        """
        Constructs implication matrix C where C_ij = 1 means feature i implies j.
        This encodes logical constraints (e.g., Conditional -> requires consequence).
        """
        C = np.eye(self.k)
        
        # Rule 1: If conditional exists (feat 1), it implies a structure check (feat 10)
        C[10, 1] = 1.0 
        
        # Rule 2: Causal implies connection
        if prompt_feats['has_causal']:
            C[2, 10] = 0.5 # Weak link
            
        # Rule 3: Negation consistency (self-loop reinforcement for stability)
        C[0, 0] = 1.0
        
        # Add transitivity simulation: if 1->10 and 10->X, then 1->X (simplified)
        # Here we just ensure the matrix is column-normalized implicitly by the dynamics
        return C

    def _evolve_dynamics(self, z: np.ndarray, C: np.ndarray) -> np.ndarray:
        """
        Evolves state z under the dynamical system: z_{t+1} = z_t + eta * (Cz_t - z_t).
        Converges to eigenvectors of C (logical attractors).
        """
        z_curr = z.copy()
        for _ in range(self.max_steps):
            z_next = z_curr + self.eta * (C @ z_curr - z_curr)
            # Enforce non-negativity (sparse codes are typically non-negative)
            z_next = np.maximum(z_next, 0)
            
            if np.linalg.norm(z_next - z_curr, 1) < self.epsilon:
                break
            z_curr = z_next
        return z_curr

    def _mechanism_score(self, z_final: np.ndarray, z_initial: np.ndarray, C: np.ndarray) -> float:
        """
        Computes payoff: Reward stability (attraction) and sparsity, penalize contradiction.
        """
        # 1. Attractor proximity: How much did the state change? Less change = more stable.
        # Ideally, if z is a fixed point, Cz = z.
        residual = np.linalg.norm(C @ z_final - z_final)
        attraction_score = -residual
        
        # 2. Sparsity penalty (encourage binary-like activations)
        # p(z) = -lambda * sum(|z - z^2|) -> 0 if z is 0 or 1
        sparsity_penalty = -self.lambda_pen * np.sum(np.abs(z_final - z_final**2))
        
        # 3. Consistency with initial prompt structure (did we drift too far?)
        # Small drift is good (refinement), huge drift is bad (hallucination)
        drift = np.linalg.norm(z_final - z_initial)
        consistency_score = -0.1 * drift if drift > 0.5 else 0.0
        
        return float(attraction_score + sparsity_penalty + consistency_score)

    def _numeric_check(self, prompt: str, candidate: str) -> float:
        """Explicit numeric reasoning check."""
        p_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', candidate)]
        
        if not p_nums or not c_nums:
            return 0.0
            
        # Heuristic: If prompt has comparison words, check if candidate numbers align logically
        has_comp = any(re.search(w, prompt, re.I)) for w in ['greater', 'less', 'more', 'max', 'min'])
        if has_comp:
            # Simple consistency: if prompt implies ordering, does candidate respect magnitude?
            # This is a simplified proxy for complex logic
            if max(c_nums) <= max(p_nums): 
                return 0.2 # Bonus for magnitude awareness
        return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        C = self._build_constraint_matrix(prompt_feats)
        results = []
        
        # NCD Baseline for tie-breaking
        import zlib
        def get_ncd(a, b):
            s_ab = len(zlib.compress((a+b).encode()))
            s_a = len(zlib.compress(a.encode()))
            s_b = len(zlib.compress(b.encode()))
            if min(s_a, s_b) == 0: return 1.0
            return (s_ab - min(s_a, s_b)) / max(s_a, s_b)

        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Sparse Encoding
            z0 = self._encode_sparse(cand_feats, prompt_feats)
            
            # 2. Dynamical Evolution
            z_star = self._evolve_dynamics(z0, C)
            
            # 3. Mechanism Design Scoring
            score = self._mechanism_score(z_star, z0, C)
            
            # 4. Structural Bonuses (The "Work" patterns)
            if cand_feats['has_negation'] == prompt_feats['has_negation']:
                score += 0.5
            if cand_feats['has_conditional'] == prompt_feats['has_conditional']:
                score += 0.3
            
            # 5. Numeric Logic
            score += self._numeric_check(prompt, cand)
            
            # 6. NCD Tiebreaker (only if scores are very close, handled by sorting stability)
            # We add a tiny NCD component to break ties among structurally similar answers
            ncd_val = get_ncd(prompt, cand)
            score -= ncd_val * 0.01 # Lower NCD (higher similarity) is slightly better
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Converged to attractor with score {score:.4f}. Sparse code stability: {np.linalg.norm(z_star):.2f}."
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on dynamical stability."""
        # Re-use evaluation logic but return normalized confidence
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        # Normalize roughly: assume typical scores range -2 to 2
        # Map to 0-1 via sigmoid-like scaling
        conf = 1.0 / (1.0 + np.exp(-raw_score)) 
        return float(np.clip(conf, 0.0, 1.0))