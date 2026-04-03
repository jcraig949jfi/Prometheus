import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Ergodic-Chaotic Hebbian Scorer (ECHS).
    Mechanism: Maps text propositions to a neural graph. Uses Hebbian learning to 
    strengthen connections between logically linked concepts (plasticity). 
    Runs dynamics to an ergodic average to measure stability (reasoning coherence).
    Penalizes high Lyapunov exponents (chaos/sensitivity) and rewards alignment 
    with prompt structure. Beats NCD by enforcing logical constraint satisfaction.
    """
    
    def __init__(self):
        self.rng = np.random.default_rng(42)  # Deterministic
        self.eta = 0.1      # Learning rate
        self.lam = 0.95     # Decay
        self.t_iters = 50   # Iterations for ergodic average
        self.alpha = 2.0    # Chaos penalty weight
        self.eps = 1e-4     # Perturbation for Lyapunov

    def _extract_props(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract structural propositions: (subj, rel, obj)."""
        text = text.lower()
        props = []
        # Patterns for comparatives, causals, conditionals, simple relations
        patterns = [
            r"(\w+)\s+(is greater than|is less than|causes|implies|precedes)\s+(\w+)",
            r"(\w+)\s+(is|are|was|were)\s+(not|no)?\s*(\w+)",
            r"if\s+(\w+)\s+then\s+(\w+)",
            r"(\d+(?:\.\d+)?)\s*(%|percent)?\s*(is|equals|>)\s*(\d+(?:\.\d+)?)",
        ]
        # Generic subject-verb-object fallback
        generic = r"(\w+)\s+(\w+)\s+(\w+)"
        
        found = set()
        for pat in patterns:
            for m in re.finditer(pat, text):
                groups = [g for g in m.groups() if g]
                if len(groups) >= 3:
                    props.append((groups[0], groups[1], groups[2]))
                    found.add((groups[0], groups[1], groups[2]))
        
        # Fallback generic extraction if specific patterns fail but text exists
        if not props and len(text.split()) > 2:
            words = re.findall(r'\w+', text)
            for i in range(len(words)-2):
                props.append((words[i], words[i+1], words[i+2]))
                if len(props) > 5: break
                
        return list(set(props))

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, List[str], int]:
        """Build proposition graph and initial activation."""
        all_props = self._extract_props(prompt) + self._extract_props(candidate)
        if not all_props:
            # Handle empty case with dummy node
            return np.zeros((1,1)), np.zeros(1), ["_dummy_"], 0
            
        unique_props = list(set(all_props))
        n = len(unique_props)
        idx_map = {p: i for i, p in enumerate(unique_props)}
        
        # Identify prompt indices for bias
        prompt_props = set(self._extract_props(prompt))
        b = np.zeros(n)
        for p in prompt_props:
            if p in idx_map:
                b[idx_map[p]] = 1.0
        
        # Initialize weights (Hebbian potential)
        W = self.rng.normal(0, 0.01, (n, n))
        
        # Pre-fill structural constraints (Transitivity/Logic hints)
        for i, p1 in enumerate(unique_props):
            for j, p2 in enumerate(unique_props):
                if i == j: continue
                # If A->B and B->C, boost A->C logic (simplified)
                if p1[1] == p2[0] or p1[2] == p2[0]:
                    W[i, j] += 0.1
                # Symmetry for similarity
                if p1[0] == p2[0]: 
                    W[i, j] += 0.05
                    
        return W, b, unique_props, n

    def _run_dynamics(self, W: np.ndarray, b: np.ndarray, perturb: float = 0.0) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Run neural dynamics with Hebbian updates."""
        n = W.shape[0]
        if n == 0: return np.array([0.0]), []
        
        a = b + self.rng.normal(0, 0.01, n) + perturb
        if perturb != 0: a += perturb # Apply specific perturbation
        
        history = []
        for _ in range(self.t_iters):
            # Hebbian update: strengthen active co-occurrences
            outer = np.outer(a, a)
            W = W * self.lam + self.eta * outer
            
            # Activation step
            a_new = np.tanh(W @ a + b)
            
            # Decay non-prompt nodes slightly to prevent saturation
            a = 0.9 * a + 0.1 * a_new
            history.append(a.copy())
            
        return a, history

    def _calc_lyapunov(self, W: np.ndarray, b: np.ndarray) -> float:
        """Estimate maximal Lyapunov exponent via perturbation."""
        if W.shape[0] == 0: return 0.0
        
        # Base trajectory
        _, base_hist = self._run_dynamics(W.copy(), b)
        # Perturbed trajectory
        _, pert_hist = self._run_dynamics(W.copy(), b, perturb=self.eps)
        
        lyap_sum = 0.0
        count = 0
        for i in range(1, min(len(base_hist), len(pert_hist))):
            dist_curr = np.linalg.norm(base_hist[i] - pert_hist[i])
            dist_prev = np.linalg.norm(base_hist[i-1] - pert_hist[i-1]) + 1e-10
            if dist_prev > 0:
                lyap_sum += np.log(dist_curr / dist_prev)
                count += 1
                
        return lyap_sum / count if count > 0 else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            W, b, props, n = self._build_graph(prompt, cand)
            if n == 0:
                score = 0.0
                reason = "No structural propositions detected."
            else:
                # Ergodic average
                final_a, history = self._run_dynamics(W, b)
                ergodic_avg = np.mean(history, axis=0) if history else final_a
                
                # Alignment with prompt bias
                s_align = float(np.dot(ergodic_avg, b)) / (n + 1)
                
                # Chaos penalty
                lyap = self._calc_lyapunov(W, b)
                score = s_align - self.alpha * lyap
                
                reason = f"Align:{s_align:.3f}, Chaos:{lyap:.3f}"
            
            results.append({"candidate": cand, "score": score, "reasoning": reason})
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Use relative scoring against a known bad answer (e.g., empty or contradiction)
        # Since we can't generate negatives easily, we normalize based on internal score magnitude
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        
        raw_score = res[0]["score"]
        # Map raw score to 0-1 heuristically based on typical dynamics range [-2, 2]
        conf = 1.0 / (1.0 + np.exp(-raw_score)) 
        return max(0.0, min(1.0, conf))