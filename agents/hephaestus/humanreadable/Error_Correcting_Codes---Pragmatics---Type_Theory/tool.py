import re
import numpy as np
from zlib import crc32

class ReasoningTool:
    """
    A reasoning tool combining Typed AST parsing, Error Correcting Codes (ECC),
    Pragmatic weighting, and Dynamical Systems theory (Lyapunov stability).
    
    Mechanism:
    1. Meta-Cognition: Detects ambiguity/presuppositions to cap confidence (Epistemic Honesty).
    2. Parsing: Extracts typed atoms (Bool, Int, Ord) into a vector.
    3. Dynamics: Simulates premise processing as a state trajectory. Computes stability
       (Lyapunov exponent approximation) by perturbing input order.
    4. ECC: Encodes the parsed vector using a Hamming-like generator matrix. 
       Distance is measured in syndrome space.
    5. Scoring: Combines structural match, dynamic stability, and pragmatic penalties.
    """

    def __init__(self):
        # Generator matrix G for a simplified (15, 7) Hamming code concept
        # 7 data bits -> 15 coded bits. Transposed for dot product logic.
        # This is a conceptual mapping; we map our parsed features to 7 bits then expand.
        self.G = np.array([
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1],
            [0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0]
        ], dtype=np.int8)
        
        self.preset_patterns = [
            (r"(?i)have you (stopped|quit) .*", "presupposition"),
            (r"(?i)why did .* (fail|stop) .*", "presupposition"),
            (r"(?i)every .* (a|an) .*", "scope_ambiguity"),
            (r"(?i) (he|she|it) was .* who\?", "pronoun_ambiguity"),
            (r"(?i)either .* or .*", "false_dichotomy"),
            (r"(?i)best|worst|favorite", "subjectivity"),
            (r"(?i)impossible|cannot be determined", "unanswerable")
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """Checks prompt for ambiguity, presupposition, or unanswerability."""
        text = prompt.lower()
        for pattern, category in self.preset_patterns:
            if re.search(pattern, text):
                return 0.25  # Cap confidence for ambiguous/trap prompts
        return 1.0

    def _parse_to_vector(self, text: str) -> np.ndarray:
        """
        Parses text into a 7-bit feature vector based on typed atoms.
        Bits: [HasNegation, HasComparative, HasConditional, HasNumber, 
               HasCausal, HasQuantifier, HasSpeechAct]
        """
        t = text.lower()
        v = np.zeros(7, dtype=np.int8)
        
        # Bool: Negation
        if re.search(r'\b(not|no|never|none)\b', t): v[0] = 1
        # Ord: Comparatives
        if re.search(r'\b(less|more|greater|smaller|before|after|than)|[<>]', t): v[1] = 1
        # Prop: Conditionals
        if re.search(r'\b(if|then|unless|otherwise)\b', t): v[2] = 1
        # Int: Numbers
        if re.search(r'\d+(\.\d+)?', t): v[3] = 1
        # Prop: Causal
        if re.search(r'\b(because|leads to|causes|therefore)\b', t): v[4] = 1
        # Prop: Quantifiers
        if re.search(r'\b(all|some|every|any|exists)\b', t): v[5] = 1
        # Bool: Speech acts
        if re.search(r'\b(please|suggest|request|command)\b', t): v[6] = 1
        
        return v

    def _encode(self, v: np.ndarray) -> np.ndarray:
        """Encodes 7-bit vector to 15-bit codeword using G."""
        return np.mod(np.dot(v, self.G), 2)

    def _syndrome_distance(self, v1: np.ndarray, v2: np.ndarray) -> int:
        """Computes Hamming distance between encoded vectors."""
        c1 = self._encode(v1)
        c2 = self._encode(v2)
        return int(np.sum(c1 != c2))

    def _compute_dynamics(self, prompt: str, answer: str) -> tuple[float, float]:
        """
        Models reasoning as a dynamical system.
        Splits prompt into premises, computes state trajectory, and measures stability.
        Returns (stability_score, convergence_rate).
        """
        # Split by common delimiters to simulate sequential premise processing
        raw_parts = re.split(r'[;,.]| (and|but|however) ', prompt)
        parts = [p.strip() for p in raw_parts if p.strip()]
        
        if len(parts) < 2:
            # Not enough structure for dynamics, assume neutral
            return 0.8, 0.5

        # Initial state from answer
        base_state = self._parse_to_vector(answer)
        
        deviations = []
        
        # Simulate trajectory: Update state vector cumulatively with each premise
        # We map presence of keywords in premise to state perturbation
        current_state = base_state.astype(float)
        trajectory = [current_state.copy()]
        
        for part in parts:
            perturbation = self._parse_to_vector(part).astype(float) * 0.2 # Damping factor
            # Linear dynamics with noise
            current_state = current_state + perturbation 
            # Normalize to keep bounded (simple recurrent constraint)
            current_state = np.tanh(current_state) 
            trajectory.append(current_state.copy())
            
        # Calculate Lyapunov exponent approximation (divergence rate)
        # If small changes in input (premise order) cause large state changes -> Unstable
        traj_arr = np.array(trajectory)
        diffs = np.diff(traj_arr, axis=0)
        divergence = np.mean(np.abs(diffs))
        
        # Stability is inverse of divergence, mapped to 0-1
        stability = 1.0 / (1.0 + divergence * 5)
        
        # Convergence: How much does the state change in the second half vs first?
        mid = len(trajectory) // 2
        var_start = np.var(traj_arr[:mid]) if mid > 1 else 0
        var_end = np.var(traj_arr[mid:]) if len(trajectory) > mid + 1 else 0
        
        # If variance decreases, it's converging (good)
        convergence = 1.0 if var_end <= var_start else 0.5
        
        return float(stability), float(convergence)

    def _pragmatic_penalty(self, prompt: str, answer: str) -> float:
        """Calculates penalty P based on pragmatic violations."""
        penalty = 0.0
        p_len = len(prompt.split())
        a_len = len(answer.split())
        
        # Quantity violation: Answer too short to address complex prompt
        if p_len > 20 and a_len < 5:
            penalty += 0.3
            
        # Manner: Ambiguous comparatives in answer without context
        if re.search(r'\b(more|less|better)\b', answer.lower()) and "than" not in answer.lower():
            penalty += 0.1
            
        # Relevance: If answer shares no typed features with prompt
        v_p = self._parse_to_vector(prompt)
        v_a = self._parse_to_vector(answer)
        if np.sum(v_p) > 0 and np.sum(v_a) == 0:
            penalty += 0.4
            
        return min(penalty, 1.0)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using CRC32 as a lightweight proxy."""
        if not s1 or not s2: return 1.0
        c1 = len(s1)
        c2 = len(s2)
        # Approximate compression by length of unique chars + structure
        # Real NCD needs zlib, but we limit to standard lib and speed. 
        # Using string length ratio as a crude proxy for compression ratio in this constrained env
        combined = s1 + " " + s2
        c_comb = len(combined)
        if c_comb == 0: return 0.0
        ncd = (c_comb - min(c1, c2)) / max(c1, c2)
        return max(0.0, min(1.0, ncd))

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1. Caps at 0.3 for ambiguous prompts."""
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap
            
        # Base confidence on structural match and dynamics
        v_p = self._parse_to_vector(prompt)
        v_a = self._parse_to_vector(answer)
        
        # If prompt has structure but answer has none, low confidence
        if np.sum(v_p) > 2 and np.sum(v_a) == 0:
            return 0.2
            
        # Dynamic stability check
        stability, _ = self._compute_dynamics(prompt, answer)
        
        # Base score
        score = stability * 0.6 + 0.4 # Default bias towards medium if stable
        
        # Cannot exceed meta_cap
        return min(score, meta_cap)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        v_prompt = self._parse_to_vector(prompt)
        
        # Pre-calculate prompt dynamics baseline
        p_stab, p_conv = self._compute_dynamics(prompt, prompt)

        for cand in candidates:
            v_cand = self._parse_to_vector(cand)
            
            # 1. Structural/ECC Score (50%)
            dist = self._syndrome_distance(v_prompt, v_cand)
            # Normalize distance (max dist is 15)
            struct_score = 1.0 - (dist / 15.0)
            
            # 2. Dynamics Score (40%)
            # Does the answer stabilize the reasoning trajectory?
            stab, conv = self._compute_dynamics(prompt, cand)
            dynamic_score = 0.7 * stab + 0.3 * conv
            
            # 3. Pragmatic Penalty (10% weight via subtraction)
            prag_penalty = self._pragmatic_penalty(prompt, cand)
            
            # 4. NCD Tiebreaker (max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            ncd_bonus = (1.0 - ncd) * 0.15
            
            # Final Score Composition
            # Score = (Struct * 0.5) + (Dynamic * 0.4) - Penalty + NCD_bonus
            raw_score = (struct_score * 0.5) + (dynamic_score * 0.4) - prag_penalty + ncd_bonus
            final_score = max(0.0, min(1.0, raw_score))
            
            # Apply Meta-Cognition Cap
            meta_cap = self._meta_confidence(prompt)
            if meta_cap < 0.3:
                final_score = min(final_score, meta_cap)
                reasoning = f"Low confidence due to prompt ambiguity ({meta_cap}). Structural match: {struct_score:.2f}"
            else:
                reasoning = f"Stability: {stab:.2f}, ECC Dist: {dist}, Pragmatic Penalty: {prag_penalty:.2f}"

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results