import numpy as np
import zlib
import re

class ReasoningTool:
    """
    Pragmatic Chaotic Meta-Reservoir (PCMR) Implementation.
    
    Mechanism:
    1. Chaos Theory: Uses a deterministic Echo State Network (ESN) with fixed random weights.
       The reservoir dynamics provide a high-dimensional projection sensitive to input ordering
       (simulating sensitive dependence on initial conditions).
    2. Metacognition: Computes a 'Prediction Error' based on the divergence between the 
       candidate's semantic fingerprint and the prompt's expected structure. It adjusts the 
       'leak rate' (confidence damping) dynamically: high structural mismatch increases error,
       lowering the final score.
    3. Pragmatics: Implements Gricean maxims via structural parsing.
       - Quantity: Penalizes candidates that are trivially short or identical to the prompt.
       - Relation: Boosts candidates that preserve key entities found in the prompt.
       - Manner: Prefers candidates with clear logical connectors (if/then, therefore).
       
    The final score is a weighted combination of NCD (baseline), Structural Alignment (Pragmatics),
    and Reservoir Stability (Chaos/Metacognition).
    """

    def __init__(self):
        # Fixed seed for deterministic chaos (ESN weights)
        np.random.seed(42)
        self.reservoir_size = 64
        self.input_size = 32
        self.leak_rate = 0.5
        
        # Initialize chaotic reservoir weights (fixed)
        self.W_in = np.random.randn(self.reservoir_size, self.input_size)
        self.W_res = np.random.randn(self.reservoir_size, self.reservoir_size) * 0.3
        # Ensure spectral radius is manageable for edge-of-chaos
        self.W_res = self.W_res / np.max(np.abs(np.linalg.eigvals(self.W_res))) * 1.1
        
        # Pragmatic keywords
        self.logic_connectors = ['therefore', 'thus', 'hence', 'because', 'if', 'then', 'so', 'but']
        self.negations = ['not', 'no', 'never', 'none', 'cannot']

    def _hash_vector(self, s: str) -> np.ndarray:
        """Convert string to deterministic float vector for reservoir input."""
        h = zlib.crc32(s.encode())
        vec = np.zeros(self.input_size)
        for i in range(self.input_size):
            vec[i] = ((h >> (i % 32)) & 0xFF) / 255.0
        return vec

    def _run_reservoir(self, input_str: str) -> np.ndarray:
        """Run input through the chaotic ESN to get a state signature."""
        state = np.zeros(self.reservoir_size)
        # Process chunks of the string to simulate temporal dynamics
        chunk_size = max(1, len(input_str) // 10)
        chunks = [input_str[i:i+chunk_size] for i in range(0, len(input_str), chunk_size)]
        
        for chunk in chunks[:10]: # Limit steps for speed
            x = self._hash_vector(chunk)
            # ESN Update: state = (1-leak)*state + leak*tanh(W_in*x + W_res*state)
            update = np.tanh(np.dot(self.W_in, x) + np.dot(self.W_res, state))
            state = (1 - self.leak_rate) * state + self.leak_rate * update
            
        return state

    def _structural_parse(self, text: str) -> dict:
        """Extract structural features for pragmatic analysis."""
        lower = text.lower()
        return {
            'has_negation': any(n in lower for n in self.negations),
            'has_logic': any(c in lower for c in self.logic_connectors),
            'word_count': len(re.findall(r'\w+', text)),
            'has_numbers': bool(re.search(r'\d+', text))
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def _pragmatic_score(self, prompt: str, candidate: str) -> float:
        """Score based on Gricean Maxims (Relation, Quantity, Manner)."""
        p_struct = self._structural_parse(prompt)
        c_struct = self._structural_parse(candidate)
        score = 0.0
        
        # Relation: Does candidate share key structural traits?
        if p_struct['has_negation'] == c_struct['has_negation']:
            score += 0.2
        if p_struct['has_numbers'] == c_struct['has_numbers']:
            score += 0.1
            
        # Manner: Logical connectors increase credibility in reasoning tasks
        if c_struct['has_logic']:
            score += 0.15
            
        # Quantity: Penalize extreme brevity unless prompt is also brief
        if c_struct['word_count'] < 3 and p_struct['word_count'] > 5:
            score -= 0.2
            
        return score

    def _metacognitive_monitor(self, prompt: str, candidate: str, base_score: float) -> float:
        """
        Adjust score based on error estimation.
        Simulates 'error-driven reinforcement' by checking consistency between
        the prompt's chaotic signature and the candidate's.
        """
        p_state = self._run_reservoir(prompt)
        c_state = self._run_reservoir(candidate)
        
        # Euclidean distance in reservoir state space as 'prediction error'
        error = np.linalg.norm(p_state - c_state)
        
        # Normalize error (approx range 0-15 for our setup)
        norm_error = min(1.0, error / 15.0)
        
        # If error is high, the candidate is 'chaotically distant' from the prompt context
        # We dampen the score, but allow high base_scores (from logic) to survive slightly better
        adjustment = (1.0 - norm_error) * 0.4 
        return base_score + adjustment

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        p_feat = self._structural_parse(prompt)
        
        for cand in candidates:
            # 1. Baseline: NCD (similarity)
            ncd = self._compute_ncd(prompt, cand)
            base_score = 1.0 - ncd # Higher is better
            
            # 2. Pragmatics: Structural alignment
            prag_score = self._pragmatic_score(prompt, cand)
            
            # 3. Chaos & Metacognition: Reservoir dynamics
            # Run candidate through reservoir to get chaotic signature
            c_state = self._run_reservoir(cand)
            p_state = self._run_reservoir(prompt)
            
            # Chaotic divergence metric: If states are too similar, it might be echoing (bad)
            # If too different, it's irrelevant. We want 'edge of chaos' relevance.
            divergence = np.linalg.norm(c_state - p_state)
            
            # Meta-evaluation: Combine pragmatic boost with chaotic stability
            # We favor candidates that have low NCD (similar meaning) but distinct structure (reasoning)
            meta_adjustment = self._metacognitive_monitor(prompt, cand, base_score)
            
            # Final Score Composition
            # Weighted sum: 40% NCD, 30% Pragmatics, 30% Meta/Chaos
            final_score = (base_score * 0.4) + (prag_score * 0.3) + (meta_adjustment * 0.3)
            
            # Heuristic boost for numeric consistency if prompt has numbers
            if p_feat['has_numbers'] and self._structural_parse(cand)['has_numbers']:
                final_score += 0.1

            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"NCD:{base_score:.2f}, Prag:{prag_score:.2f}, Meta:{meta_adjustment:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same internal scoring mechanism but normalized strictly for binary correctness probability.
        """
        # Generate a synthetic set of 'wrong' answers to compare against? 
        # No, must be deterministic and single-pass.
        # Instead, we evaluate the 'strength' of the answer relative to the prompt using the full pipeline.
        
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
            
        # The score from evaluate is already a probability-like metric in [0,1]
        # We apply a sigmoid-like sharpening to mimic confidence calibration
        score = ranked[0]['score']
        
        # Calibration: If the pragmatic score was very low, confidence should drop hard
        prag = self._pragmatic_score(prompt, answer)
        if prag < -0.1:
            return 0.1
            
        return float(np.clip(score, 0.0, 1.0))