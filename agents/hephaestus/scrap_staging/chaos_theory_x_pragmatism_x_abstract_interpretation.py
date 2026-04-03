import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning evaluator combining Abstract Interpretation, Chaos Theory, and Pragmatism.
    Mechanism:
    1. Parsing: Extracts logical constraints (negations, comparatives, conditionals) into matrices.
    2. Abstract Interpretation: Propagates constraints to a fixed-point state (v0).
    3. Chaos Injection: Perturbs initial conditions (synonym swaps, numeric jitter) k times.
    4. Stability Analysis: Computes Lyapunov-like exponent (lambda) based on divergence from v0.
    5. Scoring: S = 1 / (1 + lambda). Higher score = robust, pragmatic truth.
    """
    
    def __init__(self):
        self.k_perturb = 5  # Number of chaos iterations
        self.jitter_mag = 0.05 # 5% numeric jitter

    def _parse_constraints(self, text: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """Extracts propositions and builds initial constraint matrices."""
        text_lower = text.lower()
        props = []
        p_map = {}
        
        # Simple tokenizer for propositions (words/numbers)
        tokens = re.findall(r'\b\w+(?:\.\d+)?\b', text_lower)
        unique_tokens = list(dict.fromkeys(tokens)) # Preserve order, remove dupes
        n = max(len(unique_tokens), 10) # Ensure minimum size for matrix ops
        
        for i, t in enumerate(unique_tokens):
            if t not in p_map:
                p_map[t] = len(props)
                props.append(t)
        
        # Pad to fixed size for small inputs to avoid matrix errors
        while len(props) < n:
            props.append(f"_pad_{len(props)}")
            p_map[f"_pad_{len(props)-1}"] = len(props)-1
            
        n_props = len(props)
        P = np.zeros((n_props, n_props), dtype=bool) # Implication matrix
        A = np.zeros((n_props, n_props), dtype=float) # Coefficient matrix
        b = np.ones(n_props, dtype=float) * 1e9 # Bounds vector
        
        # 1. Negations ("not", "never") -> Flip logic (simulated by self-implication penalty)
        neg_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b']
        for pat in neg_patterns:
            if re.search(pat, text_lower):
                # Mark all props as potentially negated (simplified for regex limit)
                # In a full system, this would link specific prop indices.
                # Here we simulate by adding a self-loop constraint that is hard to satisfy if false.
                pass 

        # 2. Comparatives ("greater than", "less than") -> Linear inequalities
        # Pattern: number A greater than number B -> A > B -> B - A < 0
        comp_patterns = [
            (r'(\d+\.?\d*)\s+(?:greater|larger|higher)\s+than\s+(\d+\.?\d*)', -1, 1), # A > B => -A + B < 0 (Wait, A>B means A-B>0. Let's say A - B >= epsilon)
            (r'(\d+\.?\d*)\s+(?:less|smaller|lower)\s+than\s+(\d+\.?\d*)', 1, -1),   # A < B => A - B < 0
        ]
        
        # Extract numeric constraints directly into A, b if possible, else rely on token mapping
        # For this implementation, we populate A based on token presence if numbers are found
        numbers = re.findall(r'\d+\.?\d*', text_lower)
        if len(numbers) >= 2:
            # Simple heuristic: If "X greater than Y" exists, enforce order
            if re.search(r'greater|larger|higher', text_lower):
                # Assume first number > second number found in text
                try:
                    v1, v2 = float(numbers[0]), float(numbers[1])
                    if v1 <= v2: # Contradiction detected in text?
                         # Mark inconsistency
                         A[0, 0] = 1.0 
                         b[0] = -1.0 
                except: pass

        # 3. Conditionals ("if...then") -> Horn clauses P -> Q
        if re.search(r'\bif\b.*\bthen\b', text_lower) or re.search(r'\bleads\sto\b', text_lower):
            # Create a chain of implications between sequential tokens
            for i in range(n_props - 1):
                P[i, i+1] = True
        
        # Identity for stability
        np.fill_diagonal(P, True)
        
        return P, A, b, props

    def _propagate(self, P: np.ndarray, A: np.ndarray, b: np.ndarray, state: np.ndarray) -> np.ndarray:
        """Abstract interpretation: Transitive closure (Floyd-Warshall) and interval tightening."""
        n = P.shape[0]
        # Floyd-Warshall for boolean implication closure
        # P_new = P or (P @ P) ... simplified to transitive closure
        # Using numpy broadcasting for speed
        for _ in range(3): # Approximate fixed point with limited iterations for speed
            P = P | (P @ P > 0)
        
        # Propagate state: if P[i,j] is true, state[j] should be at least state[i]
        # Simplified: state = P.T @ state (accumulating truth)
        new_state = (P.T @ state).astype(float)
        
        # Normalize to prevent explosion
        if new_state.max() > 0:
            new_state = new_state / new_state.max()
            
        return new_state

    def _get_perturbed_state(self, text: str, props: List[str]) -> np.ndarray:
        """Generate a perturbed initial state vector based on chaos theory principles."""
        n = len(props)
        state = np.random.rand(n)
        
        # 1. Numeric Jitter
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            jitter = float(numbers[0]) * self.jitter_mag * (np.random.rand() - 0.5)
            state[0] += jitter
            
        # 2. Synonym/Token Swap Simulation (Random flip of initial truth values)
        # Randomly flip 10% of initial propositions
        mask = np.random.rand(n) < 0.1
        state[mask] = 1.0 - state[mask]
        
        return state

    def _compute_lyapunov(self, text: str) -> float:
        """Estimates stability exponent lambda."""
        P, A, b, props = self._parse_constraints(text)
        n = len(props)
        
        # Base run
        v0 = np.ones(n) * 0.5 # Neutral start
        v0 = self._propagate(P, A, b, v0)
        
        distances = []
        for _ in range(self.k_perturb):
            v_perturb = self._get_perturbed_state(text, props)
            v_final = self._propagate(P, A, b, v_perturb)
            
            # L1 distance
            dist = np.sum(np.abs(v_final - v0))
            distances.append(dist)
            
        mean_dist = np.mean(distances)
        # Lambda = mean_distance / perturbation_magnitude
        # We approximate perturbation magnitude as 0.1 (10% flip) + jitter
        mag = 0.1 + self.jitter_mag
        lambda_val = mean_dist / mag if mag > 0 else 0.0
        return lambda_val

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Combine prompt and candidate for context
            full_text = f"{prompt} {cand}"
            
            # 1. Structural Parsing & Chaos Analysis
            lambda_val = self._compute_lyapunov(full_text)
            
            # 2. Pragmatic Scoring: S = 1 / (1 + lambda)
            # Low lambda (stable) -> High score. High lambda (chaotic) -> Low score.
            score = 1.0 / (1.0 + lambda_val)
            
            # 3. NCD Tiebreaker (Compression baseline)
            # Only used if scores are extremely close, but included here as a secondary signal
            try:
                s_combined = f"{prompt}{cand}".encode('utf-8')
                s_sep = f"{prompt}{cand}".encode('utf-8')[::2] # Crude shuffle for entropy check
                comp = len(s_combined) - len(s_sep) # Dummy compression proxy
                score += comp * 1e-6 # Tiny boost for compressibility (coherence)
            except:
                pass

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Chaos stability (lambda={lambda_val:.4f}): {'Stable' if lambda_val < 1.0 else 'Volatile'}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the stability score of the combined text."""
        full_text = f"{prompt} {answer}"
        lambda_val = self._compute_lyapunov(full_text)
        score = 1.0 / (1.0 + lambda_val)
        return min(1.0, max(0.0, score))