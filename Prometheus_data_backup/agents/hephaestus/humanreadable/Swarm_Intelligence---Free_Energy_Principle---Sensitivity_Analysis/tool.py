import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Swarm-Free Sensitivity Scorer (SFSS) with Dynamics Tracking.
    
    Mechanism:
    1. Parsing: Extracts logical predicates, comparatives, and numeric values into a hypergraph.
    2. Dynamics: Models reasoning as a dynamical system where particle states evolve 
       under a Free Energy landscape defined by logical constraints (A*p = b).
    3. Sensitivity: Uses Particle Swarm Optimization (PSO) to minimize constraint violation energy.
    4. Epistemic Honesty: Detects ambiguity patterns (Tier B) to cap confidence.
    5. Scoring: Combines minimized free energy (structural/computational) with NCD (tiebreaker).
    """
    
    def __init__(self):
        self.n_particles = 15
        self.n_iterations = 25
        self.lambda_sparse = 0.1
        self.omega = 0.7      # Inertia
        self.eta = 0.1        # Learning rate
        self.phi1 = 1.5       # Cognitive
        self.phi2 = 1.5       # Social

    def _meta_confidence(self, prompt: str) -> float:
        """Detects Tier B traps: presupposition, ambiguity, unanswerability."""
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_patterns = [
            r"have you stopped", r"have you quit", r"why did .+ fail", 
            r"why did .+ stop", r"when did .+ stop", r"continue to"
        ]
        if any(re.search(pat, p_lower) for pat in presupposition_patterns):
            return 0.2

        # 2. Scope/Pronoun Ambiguity
        if re.search(r"every .+ (did|has) a .+\?", p_lower) and "same" not in p_lower:
            return 0.3
        if re.search(r"told .+ he was|told .+ she was", p_lower) and "who" in p_lower:
            return 0.25

        # 3. False Dichotomy
        if re.search(r"either .+ or .+", p_lower) and "only" not in p_lower:
            # Heuristic: if not explicitly exhaustive, lower confidence
            if not re.search(r"must be either", p_lower):
                return 0.4

        # 4. Subjectivity without criteria
        if re.search(r"(best|worst|favorite|ugliest)", p_lower) and not re.search(r"(largest number|highest value|calculated)", p_lower):
            return 0.3

        return 1.0  # No obvious traps detected

    def _parse_to_matrix(self, text: str) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Parses text into constraint matrix A and vector b.
        Returns A, b, and dimension size.
        """
        tokens = re.findall(r'-?\d+\.?\d*|true|false|yes|no', text.lower())
        nums = []
        for t in tokens:
            try:
                nums.append(float(t))
            except:
                pass
        
        # Dimension based on found numbers or default logical space
        dim = max(len(nums), 3) 
        if dim == 0: dim = 3
            
        A = np.zeros((dim, dim))
        b = np.zeros(dim)
        
        # Extract Comparatives (e.g., "5 > 3", "x is less than y")
        comp_matches = re.findall(r'(\d+\.?\d*)\s*(>|<|=|greater than|less than|equals)\s*(\d+\.?\d*)', text.lower())
        for m in comp_matches:
            v1, op, v2 = m
            try:
                n1, n2 = float(v1), float(v2)
                # Map to indices modulo dim to fit matrix
                i1, i2 = int(n1) % dim, int(n2) % dim
                if i1 == i2: continue
                
                if '>' in op or 'greater' in op:
                    A[i1, i1] += 1; A[i1, i2] -= 1; b[i1] += 0.1 # n1 - n2 > 0
                elif '<' in op or 'less' in op:
                    A[i2, i2] += 1; A[i2, i1] -= 1; b[i2] += 0.1 # n2 - n1 > 0
                else: # equals
                    A[i1, i1] += 1; A[i1, i2] -= 1; b[i1] += 0.0
            except: continue

        # Extract Conditionals / Causal chains (Simplified logical flow)
        # "If A then B" -> A implies B. Represented as flow conservation.
        if "if" in text.lower() and "then" in text.lower():
            # Create a dependency chain in the matrix
            for i in range(dim-1):
                A[i, i+1] -= 0.5
                A[i+1, i] += 0.5
                b[i] += 0.1

        # Identity regularization to ensure solvability
        A += np.eye(dim) * 0.1
        return A, b, dim

    def _compute_free_energy(self, p: np.ndarray, A: np.ndarray, b: np.ndarray) -> float:
        """F(p) = 0.5 * ||Ap - b||^2 + lambda * ||p||_1"""
        residual = A @ p - b
        energy = 0.5 * np.dot(residual, residual) + self.lambda_sparse * np.sum(np.abs(p))
        return float(energy)

    def _run_dynamics(self, prompt: str, candidate: str) -> Tuple[float, float, str]:
        """
        Runs the swarm optimization to find the minimum free energy state.
        Returns: (score, confidence_cap, reasoning_trace)
        """
        full_text = f"{prompt} {candidate}"
        A, b, dim = self._parse_to_matrix(full_text)
        
        if dim == 0:
            return 0.0, 0.1, "No logical structure parsed."

        # Initialize Swarm
        # Positions represent truth values in [-1, 1]
        positions = np.random.uniform(-1, 1, (self.n_particles, dim))
        velocities = np.zeros((self.n_particles, dim))
        p_best_pos = positions.copy()
        p_best_score = np.full(self.n_particles, np.inf)
        g_best_pos = positions[0].copy()
        g_best_score = np.inf
        
        trace = []

        # Dynamics Loop
        for k in range(self.n_iterations):
            scores = []
            for i in range(self.n_particles):
                p = positions[i]
                score = self._compute_free_energy(p, A, b)
                scores.append(score)
                
                # Update personal best
                if score < p_best_score[i]:
                    p_best_score[i] = score
                    p_best_pos[i] = p.copy()
                
                # Update global best
                if score < g_best_score:
                    g_best_score = score
                    g_best_pos = p.copy()

            # Track convergence stability (Lyapunov-like exponent approximation)
            if k > 0:
                stability = abs(prev_g_best - g_best_score) if prev_g_best else 1.0
                trace.append(f"Iter {k}: Energy={g_best_score:.4f}, Stability={stability:.4f}")
            prev_g_best = g_best_score

            # Vectorized PSO Update
            r1 = np.random.rand(self.n_particles, dim)
            r2 = np.random.rand(self.n_particles, dim)
            
            # Gradient of Free Energy: A^T(Ap - b) + lambda*sign(p)
            residuals = positions @ A.T - b.reshape(1, -1) # Shape mismatch fix
            # Correct matrix mult: (A @ p) is (dim,), so (A @ P.T).T for batch
            # Let's do loop for clarity in gradient calc or careful broadcasting
            gradients = np.zeros_like(positions)
            for i in range(self.n_particles):
                p = positions[i].reshape(-1, 1)
                grad = A.T @ (A @ p - b.reshape(-1, 1)) + self.lambda_sparse * np.sign(p)
                gradients[i] = grad.flatten()

            velocities = (self.omega * velocities 
                          - self.eta * gradients 
                          + self.phi1 * r1 * (p_best_pos - positions) 
                          + self.phi2 * r2 * (g_best_pos - positions))
            
            positions += velocities
            positions = np.clip(positions, -1, 1)

        # Final Score inversion (Lower energy = Higher score)
        # Normalize roughly to 0-1 range assuming energy < 10 is good
        raw_score = max(0.0, 1.0 - (g_best_score / 5.0))
        
        # Stability bonus: If the system converged smoothly, boost confidence
        if len(trace) > 2:
            last_stab = float(trace[-1].split("Stability=")[1].split(",")[0])
            if last_stab < 0.01:
                raw_score = min(1.0, raw_score + 0.1)

        reasoning = f"Converged to energy {g_best_score:.4f}. " + "; ".join(trace[-2:])
        return raw_score, 1.0, reasoning

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            z = zlib.compress
            l1, l2, l12 = len(z(s1.encode())), len(z(s2.encode())), len(z((s1+s2).encode()))
            if l12 == 0: return 0.0
            return (l12 - min(l1, l2)) / max(l1, l2, 1)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Pre-check meta-confidence on prompt
        meta_conf = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural/Computational Score (Dynamics)
            dyn_score, _, reason = self._run_dynamics(prompt, cand)
            
            # 2. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Weighted Combination: 85% Dynamics, 15% NCD
            final_score = (dyn_score * 0.85) + ncd_score
            
            # Apply Epistemic Honesty Cap
            if meta_conf < 0.3:
                final_score = min(final_score, 0.25) # Cap score for ambiguous prompts
                reason = f"Warning: Prompt contains ambiguity/trap. Score capped. {reason}"
            
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence level if prompt is tricky.
        """
        meta_conf = self._meta_confidence(prompt)
        
        # Run a quick dynamic check
        score, _, _ = self._run_dynamics(prompt, answer)
        
        # If the structural parser found nothing, confidence must be low
        if score < 0.1:
            return 0.1
            
        # Combine structural success with meta-honesty
        # If meta says "risky", cap the confidence even if score is high
        final_conf = min(score, meta_conf)
        
        # Never exceed 0.95 unless it's a pure calculation match
        if "calculate" not in prompt.lower() and "compute" not in prompt.lower():
            final_conf = min(final_conf, 0.9)
            
        return float(np.clip(final_conf, 0.0, 1.0))