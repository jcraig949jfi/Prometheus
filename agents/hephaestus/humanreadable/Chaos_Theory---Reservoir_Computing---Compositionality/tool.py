import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Compositional Reservoir (CCR) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, conditionals).
    2. Chaotic Reservoir: Uses a fixed, sparse recurrent matrix tuned to the edge of chaos 
       (spectral radius ~1.05) to generate high-dimensional, sensitive trajectories from 
       tokenized input. This provides diverse internal states without external noise.
    3. Compositional Readout: Simulates tensor-product binding by hashing structural roles 
       (e.g., "subject", "object") combined with reservoir states to score candidates.
    4. Metacognition: Estimates local trajectory sensitivity (Lyapunov proxy) to adjust 
       confidence scores. High sensitivity = low confidence.
    5. Scoring: Primary signal is structural/logic match; NCD is a tiebreaker.
    """

    def __init__(self):
        # Reservoir parameters
        self.n_res = 64  # Reservoir size
        self.spectral_radius = 1.05  # Edge of chaos
        self.leak = 0.3  # Leaky integrator
        
        # Initialize fixed chaotic weights (deterministic seed)
        np.random.seed(42)
        # Sparse connectivity for chaos
        sparsity = 0.9
        W = np.random.randn(self.n_res, self.n_res)
        mask = (np.random.rand(self.n_res, self.n_res) < sparsity).astype(float)
        W *= mask
        # Scale to spectral radius
        W *= self.spectral_radius / np.max(np.abs(np.linalg.eigvals(W)))
        self.W = W
        
        # Input weights
        self.W_in = np.random.randn(self.n_res, 1) * 0.5
        
        # State
        self.state = np.zeros(self.n_res)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer preserving structure."""
        return re.findall(r'\w+|[^\s\w]', text.lower())

    def _run_reservoir(self, tokens: List[str]) -> np.ndarray:
        """Run input through chaotic reservoir, return final state."""
        state = np.zeros(self.n_res)
        history = []
        
        for token in tokens:
            # Simple hash-based input vector
            h = hash(token) % 1000
            u = np.sin(np.linspace(0, 2*np.pi, self.n_res)) * (h / 1000.0)
            
            # Leaky integrator update with tanh nonlinearity
            new_state = np.tanh(np.dot(self.W, state) + np.dot(self.W_in, [[u[0]]])[0])
            state = (1 - self.leak) * state + self.leak * new_state
            history.append(state.copy())
            
        return state, history

    def _estimate_lyapunov(self, history: List[np.ndarray]) -> float:
        """Estimate local sensitivity (metacognitive signal)."""
        if len(history) < 2:
            return 0.0
        
        # Approximate divergence between consecutive steps
        divergences = []
        for i in range(1, len(history)):
            diff = np.linalg.norm(history[i] - history[i-1])
            if diff > 1e-6:
                divergences.append(np.log(diff + 1e-6))
        
        if not divergences:
            return 0.0
            
        # High average divergence implies high sensitivity (chaos) -> lower confidence
        return float(np.mean(divergences))

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extract logical structures: negations, comparatives, numbers."""
        lower = text.lower()
        structure = {
            'negations': len(re.findall(r'\b(not|no|never|without)\b', lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', lower)),
            'numbers': re.findall(r'\d+\.?\d*', lower),
            'length': len(text)
        }
        return structure

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core scoring logic combining structure, chaos, and composition."""
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Structural Matching (Primary Signal)
        struct_score = 0.0
        
        # Negation consistency
        if p_struct['negations'] > 0:
            struct_score += 0.3 if c_struct['negations'] > 0 else -0.2
            
        # Comparative logic
        if p_struct['comparatives'] > 0:
            struct_score += 0.3 if c_struct['comparatives'] > 0 else 0.0
            
        # Conditional presence
        if p_struct['conditionals'] > 0:
            struct_score += 0.2 if c_struct['conditionals'] > 0 else 0.0
            
        # Numeric evaluation heuristic
        if p_struct['numbers'] and c_struct['numbers']:
            try:
                p_nums = [float(x) for x in p_struct['numbers']]
                c_nums = [float(x) for x in c_struct['numbers']]
                # Check if candidate numbers are logically derived (simplified)
                if any(abs(p - c) < 0.01 for p in p_nums for c in c_nums):
                    struct_score += 0.4
            except:
                pass

        # 2. Chaotic Reservoir & Compositional Binding
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        # Run reservoir
        p_state, p_hist = self._run_reservoir(p_tokens)
        c_state, _ = self._run_reservoir(c_tokens)
        
        # Compositional similarity (dot product of reservoir states)
        # Simulates binding of temporal patterns
        reservoir_sim = float(np.dot(p_state, c_state)) / (self.n_res * 2.0) # Normalize approx
        
        # 3. Metacognition (Lyapunov adjustment)
        # If the prompt trajectory is highly chaotic (high divergence), reduce confidence
        lyap = self._estimate_lyapunov(p_hist)
        meta_factor = 1.0 / (1.0 + abs(lyap)) # Dampen score if unstable
        
        # Combined Score
        # Weighted sum: Structure (60%) + Reservoir (30%) + Meta (10%)
        final_score = (struct_score * 0.6) + (reservoir_sim * 0.3) + (meta_factor * 0.1)
        
        reason = f"Struct:{struct_score:.2f}, Res:{reservoir_sim:.2f}, Meta:{meta_factor:.2f}"
        return final_score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        scores = []
        
        # First pass: Compute structural and reservoir scores
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
            scores.append(score)
        
        # Tie-breaking with NCD if scores are too close
        if len(scores) > 1:
            max_s = max(scores)
            min_s = min(scores)
            # If range is small, use NCD as tiebreaker
            if max_s - min_s < 0.05:
                for i, res in enumerate(results):
                    ncd = self._compute_ncd(prompt, res['candidate'])
                    # Lower NCD is better (more similar), so subtract
                    res['score'] -= ncd * 0.01
                    res['reasoning'] += f", NCD:{ncd:.2f}"

        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._score_candidate(prompt, answer)
        # Map score to 0-1 range roughly
        # Structural matches can be negative, reservoir sim is centered around 0
        conf = 1.0 / (1.0 + np.exp(-score * 5)) # Sigmoid scaling
        return max(0.0, min(1.0, conf))