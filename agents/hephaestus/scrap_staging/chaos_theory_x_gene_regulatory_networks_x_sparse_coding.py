import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Sparse Attractor Network (CSAN) Implementation.
    
    Mechanism:
    1. Encoding: Prompts and candidates are mapped to sparse binary vectors (Gene expression).
    2. GRN Topology: A fixed, sparse recurrent weight matrix simulates regulatory constraints.
    3. Chaotic Dynamics: The system iterates the state vector. Candidates that align with the 
       prompt's "attractor basin" (low reconstruction error under chaotic perturbation) 
       receive higher scores.
    4. Scoring: Combines structural constraint satisfaction (logic checks) with the 
       chaotic reconstruction error metric.
    """
    
    def __init__(self):
        self.dim = 64  # Dimensionality of the sparse code (Gene count)
        self.sparsity = 0.15  # Fraction of active genes
        self.chaos_strength = 1.05  # Lyapunov exponent proxy (>1 for chaos)
        self.iterations = 10  # Time steps for dynamic evolution
        
        # Initialize GRN-like weight matrix (Sparse, signed, recurrent)
        # Deterministic seed for reproducibility
        rng = np.random.RandomState(42)
        self.weights = rng.choice([-1, 0, 1], size=(self.dim, self.dim), 
                                  p=[0.4, 0.8, 0.4]) # Highly sparse connectivity
        # Normalize to prevent explosion, keep edge-of-chaos
        self.weights = self.weights.astype(float) 
        self.weights /= (np.sqrt(self.sparsity * self.dim) + 1e-9)

    def _text_to_sparse_vector(self, text: str) -> np.ndarray:
        """Hash text to a deterministic sparse binary vector (Boolean GRN state)."""
        if not text:
            return np.zeros(self.dim)
        
        # Use zlib crc32 for deterministic hashing of n-grams to simulate feature detection
        vec = np.zeros(self.dim)
        clean_text = text.lower()
        
        # Activate genes based on character n-gram hashes
        for i in range(len(clean_text) - 2):
            chunk = clean_text[i:i+3]
            h = zlib.crc32(chunk.encode()) 
            idx = h % self.dim
            # Soft accumulation then threshold for sparsity
            vec[idx] += 1.0
            
        # Normalize and sparsify (Olshausen-Field style L1 constraint approx)
        vec = vec / (vec.max() + 1e-9)
        threshold = np.sort(vec.flatten())[-int(self.dim * self.sparsity)] if vec.max() > 0 else 0
        binary_vec = (vec >= threshold).astype(float)
        
        # Ensure at least one active gene to prevent death
        if binary_vec.sum() == 0:
            binary_vec[h % self.dim] = 1.0
            
        return binary_vec

    def _chaotic_evolution(self, state: np.ndarray, steps: int = 5) -> float:
        """
        Evolve state through GRN dynamics near edge of chaos.
        Returns the average reconstruction error (stability metric).
        Low error = stable attractor (High confidence).
        High error = unstable trajectory (Low confidence).
        """
        current = state.copy()
        total_error = 0.0
        
        for _ in range(steps):
            # Linear dynamics: x(t+1) = W * x(t)
            next_state = np.dot(self.weights, current)
            
            # Non-linear activation (Tanh-like saturation to bound dynamics)
            next_state = np.tanh(next_state * self.chaos_strength)
            
            # Sparse coding constraint: Keep only top-k active (Winner-take-all)
            k = int(self.dim * self.sparsity)
            if k > 0:
                threshold = np.sort(np.abs(next_state)).flatten()[-k]
                mask = np.abs(next_state) >= threshold
                next_state = next_state * mask.astype(float)
            
            # Reconstruction error: How much did the state change/deviate?
            # In a stable attractor, x(t+1) ~ x(t)
            error = np.mean((next_state - current) ** 2)
            total_error += error
            
            current = next_state
            
        return total_error / steps

    def _extract_logical_features(self, text: str) -> Dict[str, float]:
        """Extract structural reasoning features (Constraint Propagation)."""
        t = text.lower()
        features = {
            'negation': float('not' in t or 'no ' in t or 'never' in t),
            'comparative': float('>' in t or '<' in t or 'more' in t or 'less' in t or 'better' in t),
            'conditional': float('if' in t or 'then' in t or 'unless' in t),
            'numeric': float(any(c.isdigit() for c in t)),
            'length': len(t)
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a baseline tie-breaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / (max(c1, c2) + 1e-9)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_vec = self._text_to_sparse_vector(prompt)
        prompt_feats = self._extract_logical_features(prompt)
        results = []
        
        # Pre-calculate prompt chaos stability for context
        prompt_stability = 1.0 / (self._chaotic_evolution(prompt_vec, self.iterations) + 1e-9)
        
        for cand in candidates:
            cand_vec = self._text_to_sparse_vector(cand)
            cand_feats = self._extract_logical_features(cand)
            
            # 1. Chaotic Attractor Score (Dynamic Consistency)
            # Combine prompt and candidate to see if they form a stable joint attractor
            joint_state = (prompt_vec + cand_vec) / 2.0
            instability = self._chaotic_evolution(joint_state, self.iterations)
            chaos_score = 1.0 / (instability + 0.1)  # Inverse error
            
            # 2. Structural Constraint Matching (Reasoning Heuristics)
            struct_score = 0.0
            # Check negation alignment
            if prompt_feats['negation'] == cand_feats['negation']:
                struct_score += 0.5
            # Check numeric consistency (rough heuristic)
            if prompt_feats['numeric'] and cand_feats['numeric']:
                struct_score += 0.3
            elif not prompt_feats['numeric'] and not cand_feats['numeric']:
                struct_score += 0.1
                
            # 3. NCD Tiebreaker (Semantic proximity)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Weighted Fusion
            # Chaos provides the "hypothesis testing", Structure provides "logic gates"
            final_score = (0.6 * chaos_score * 0.1) + (0.3 * struct_score) + (0.1 * ncd_score)
            
            # Reasoning string generation
            reason_parts = []
            if instability < 0.5:
                reason_parts.append("stable attractor")
            else:
                reason_parts.append("chaotic transient")
            if struct_score > 0.4:
                reason_parts.append("structural alignment")
                
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0, 1)),
                "reasoning": f"CSAN dynamics: {', '.join(reason_parts)}. Instability={instability:.3f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on chaotic stability of the joint state.
        """
        prompt_vec = self._text_to_sparse_vector(prompt)
        answer_vec = self._text_to_sparse_vector(answer)
        
        # Joint dynamics
        joint_state = (prompt_vec + answer_vec) / 2.0
        instability = self._chaotic_evolution(joint_state, self.iterations)
        
        # Convert instability to confidence (Low instability = High confidence)
        # Calibrate threshold: <0.2 is very stable, >1.0 is chaotic
        raw_conf = 1.0 / (instability + 0.2)
        conf = float(np.clip(raw_conf * 0.5, 0, 1)) # Scale to 0-1
        
        # Boost if structural features match (e.g. both numeric)
        p_feats = self._extract_logical_features(prompt)
        a_feats = self._extract_logical_features(answer)
        if p_feats['numeric'] == a_feats['numeric'] and p_feats['numeric'] > 0:
            conf = min(1.0, conf + 0.2)
            
        return conf