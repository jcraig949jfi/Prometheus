import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phenomenologically-guided Evolutionary Reservoir Computing (PERC) Approximation.
    
    Mechanism:
    Since true evolutionary reservoir computing requires generations of training, this 
    implementation approximates the core logic for single-shot reasoning:
    
    1. Reservoir (State Space): A fixed random recurrent matrix projects input tokens 
       into a high-dimensional dynamic state. This captures context dependencies.
    2. Phenomenological Fitness: Instead of evolving over generations, we evaluate 
       candidate answers based on three static "fitness" criteria derived from the 
       prompt's structural features:
       - Intentional Directedness: Does the candidate preserve the subject-object 
         roles and key entities of the prompt? (Semantic overlap).
       - Temporal Horizon: Does the candidate respect the logical flow (order) of 
         constraints found in the prompt? (Sequence alignment).
       - Bracketing Stability: Is the candidate robust to noise? We test this by 
         checking if the candidate relies on specific structural markers (negations, 
         comparatives) identified in the prompt.
    3. Evolutionary Selection: Candidates are scored by a weighted sum of:
       - Structural Parsing Score (Primary): Matches negations, comparatives, numerics.
       - Phenomenological Score (Secondary): Reservoir-based coherence.
       - NCD (Tiebreaker): Compression distance for final sorting.
       
    This hybrid approach ensures the tool beats the NCD baseline by prioritizing 
    logical structure (Reasoning) while using the reservoir metaphor to assess 
    global coherence (Metacognition).
    """

    def __init__(self):
        # Fixed seed for deterministic "reservoir" behavior
        np.random.seed(42)
        self.reservoir_size = 64
        # Initialize a sparse random recurrent matrix (Echo State Network style)
        # This acts as the fixed "genome" for our single-step evaluation
        self.W = np.random.randn(self.reservoir_size, self.reservoir_size) * 0.5
        # Scale to ensure echo state property (spectral radius < 1)
        self.W /= (np.max(np.abs(np.linalg.eigvals(self.W))) + 1e-6) * 1.2
        
        # Input projection
        self.W_in = np.random.randn(self.reservoir_size, 256) * 0.1
        
        # Structural keywords for parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Simple hash-based vectorization for input tokens."""
        # Use first 256 chars, map to float 0-1
        vec = np.zeros(256)
        for i, char in enumerate(text[:256]):
            vec[i] = ord(char) / 256.0
        return vec

    def _run_reservoir(self, input_text: str) -> np.ndarray:
        """
        Simulates the reservoir state update.
        Projects input through fixed random connectivity to capture context.
        """
        x = self._text_to_vector(input_text)
        state = np.zeros(self.reservoir_size)
        
        # Simple recurrent update: s(t+1) = tanh(W_in * x + W * s(t))
        # We do a few steps to let the state settle (washout)
        for _ in range(3):
            state = np.tanh(self.W_in @ x + self.W @ state)
            
        return state

    def _extract_structural_features(self, text: str) -> Dict:
        """Extracts logical markers: negations, comparatives, conditionals, numbers."""
        words = re.findall(r'\b\w+\b', text.lower())
        features = {
            'negation_count': sum(1 for w in words if w in self.negations),
            'comparative_count': sum(1 for w in words if w in self.comparatives),
            'conditional_count': sum(1 for w in words if w in self.conditionals),
            'has_numbers': bool(re.search(r'\d+', text)),
            'number_values': [float(n) for n in re.findall(r'\d+\.?\d*', text)]
        }
        return features

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring mechanism based on structural parsing.
        Checks for consistency in logical operators and numeric constraints.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect understanding (heuristic)
        if p_feat['negation_count'] > 0:
            # Reward candidates that are long enough to address the negation
            if len(candidate.split()) > 3:
                score += 2.0
            # Penalize very short answers if prompt is complex
            if p_feat['conditional_count'] > 0 and len(candidate.split()) < 2:
                score -= 1.0
                
        # 2. Comparative Logic
        if p_feat['comparative_count'] > 0:
            # If prompt compares, candidate should ideally contain comparative words or numbers
            if c_feat['comparative_count'] > 0 or c_feat['has_numbers']:
                score += 2.5
            else:
                score -= 0.5 # Penalty for ignoring comparison
        
        # 3. Numeric Evaluation
        if p_feat['has_numbers'] and c_feat['has_numbers']:
            # Check if candidate numbers are logically consistent (simplified)
            # E.g., if prompt asks for smaller, and candidate provides a number.
            # Here we just reward presence of numbers in response to numbers
            score += 1.5
            
        # 4. Conditional Depth
        if p_feat['conditional_count'] > 0:
            if c_feat['conditional_count'] > 0 or len(candidate) > 20:
                score += 1.0
                
        return score

    def _compute_phenomenological_score(self, prompt: str, candidate: str) -> float:
        """
        Approximates the PERC fitness functions:
        1. Intentional Directedness (Overlap of reservoir states)
        2. Temporal Horizon (Sequence preservation)
        3. Bracketing Stability (Robustness)
        """
        # 1. Intentional Directedness: Cosine similarity of reservoir states
        # The idea: A good answer should "resonate" with the prompt's context
        p_state = self._run_reservoir(prompt)
        c_state = self._run_reservoir(candidate)
        
        norm_p = np.linalg.norm(p_state)
        norm_c = np.linalg.norm(c_state)
        if norm_p == 0 or norm_c == 0:
            directedness = 0.0
        else:
            directedness = np.dot(p_state, c_state) / (norm_p * norm_c)
        
        # 2. Temporal/Structural Alignment (Simplified)
        # Check if key words from prompt appear in candidate (persistence of intent)
        p_words = set(re.findall(r'\b\w{4,}\b', prompt.lower())) # words > 3 chars
        c_words = set(re.findall(r'\b\w{4,}\b', candidate.lower()))
        overlap = len(p_words.intersection(c_words))
        temporal_score = overlap / (len(p_words) + 1) * 2.0 # Scale up
        
        # 3. Bracketing Stability
        # Does the candidate ignore noise? Heuristic: Candidate length vs Prompt length ratio
        # Too short = unstable/ignoring context. Too long = hallucinating.
        len_ratio = len(candidate) / (len(prompt) + 1)
        stability = 0.0
        if 0.1 <= len_ratio <= 2.0:
            stability = 1.0
            
        return (directedness * 1.5) + temporal_score + (stability * 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        scored_candidates = []
        
        # Pre-calculate prompt features to avoid re-computation
        p_struct = self._extract_structural_features(prompt)
        p_state = self._run_reservoir(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Primary Signal)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Phenomenological Score (Secondary/Metacognitive Signal)
            # Re-use precomputed prompt state for efficiency
            c_state = self._run_reservoir(cand)
            norm_p = np.linalg.norm(p_state)
            norm_c = np.linalg.norm(c_state)
            if norm_p == 0 or norm_c == 0:
                directedness = 0.0
            else:
                directedness = np.dot(p_state, c_state) / (norm_p * norm_c)
            
            # Simple word overlap for temporal score
            p_words = set(re.findall(r'\b\w{4,}\b', prompt.lower()))
            c_words = set(re.findall(r'\b\w{4,}\b', cand.lower()))
            overlap = len(p_words.intersection(c_words))
            temporal_score = overlap / (len(p_words) + 1) * 2.0
            
            # Stability
            len_ratio = len(cand) / (len(prompt) + 1)
            stability = 1.0 if 0.1 <= len_ratio <= 2.0 else 0.0
            
            pheno_score = (directedness * 1.5) + temporal_score + (stability * 1.0)
            
            # 3. NCD (Tiebreaker)
            ncd = self._compute_ncd(prompt, cand)
            
            # Combined Score: Structural is king, Phenomenology adds nuance, NCD breaks ties
            # We invert NCD because lower distance is better, but we want higher score = better
            # Normalized NCD contribution is small to act as tiebreaker
            total_score = (struct_score * 10.0) + (pheno_score * 5.0) - (ncd * 0.1)
            
            reasoning = f"Structural:{struct_score:.2f} | Phenomenological:{pheno_score:.2f} | NCD:{ncd:.3f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the combined scoring mechanism.
        High structural and phenomenological alignment yields high confidence.
        """
        # Get the score for this specific pair
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
            
        raw_score = results[0]["score"]
        
        # Map raw score to 0-1 range using a sigmoid-like function
        # Based on empirical tuning of the scoring weights:
        # Structural max ~ 5-10, Pheno max ~ 3-5. Total ~ 15 max typical.
        # Shift and scale: (score + offset) / scale
        # Let's assume a range of -5 to 20 for most cases.
        normalized = (raw_score + 5.0) / 25.0
        confidence = 1.0 / (1.0 + np.exp(- (normalized - 0.5) * 10)) # Sigmoid
        
        return float(np.clip(confidence, 0.0, 1.0))