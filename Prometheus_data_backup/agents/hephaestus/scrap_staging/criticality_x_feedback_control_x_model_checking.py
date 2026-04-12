import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Propositional Graph Parsing, Model Checking (Fixed-Point Iteration),
    Criticality Analysis (Jacobian Spectral Radius), and Feedback Control (PID) to score answers.
    
    Mechanism:
    1. Parses prompt and candidates into atomic propositions and logical edges.
    2. Constructs an adjacency matrix representing logical constraints.
    3. Runs a fixed-point iteration (Model Checking) to find consistent truth values.
    4. Computes the Jacobian spectral radius (Criticality) to measure logical sensitivity.
    5. Applies a PID-like feedback loop to adjust scoring based on error convergence.
    6. Integrates Epistemic Honesty checks for Tier B ambiguity detection.
    """

    def __init__(self):
        self.epsilon = 1e-4
        self.max_steps = 50
        # PID Constants
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.05

    def _tokenize_and_parse(self, text: str) -> Tuple[List[str], List[Tuple], Dict[str, float]]:
        """Extract propositions, logical edges, and numeric facts."""
        text_lower = text.lower()
        propositions = []
        edges = []  # (src_idx, dst_idx, weight)
        facts = {}  # proposition_string -> value (0 or 1)
        
        # Simple regex extractors
        # 1. Negations
        neg_patterns = [r'\bnot\s+(\w+\s+\w+\s+\w+)', r'\bno\s+(\w+\s+\w+\s+\w+)']
        for pat in neg_patterns:
            for match in re.finditer(pat, text_lower):
                prop = match.group(1).strip()
                propositions.append(f"not_{prop}")
                facts[f"not_{prop}"] = 1.0 # Explicitly stated negation is true
        
        # 2. Comparatives (Numeric)
        comp_patterns = [
            (r'(\d+(?:\.\d+)?)\s*(?:is\s*)?(?:greater|more)\s*than\s*(\d+(?:\.\d+)?)', 'gt'),
            (r'(\d+(?:\.\d+)?)\s*(?:is\s*)?(?:less|smaller)\s*than\s*(\d+(?:\.\d+)?)', 'lt'),
            (r'(\d+(?:\.\d+)?)\s*(?:equals?|is)\s*(\d+(?:\.\d+)?)', 'eq')
        ]
        for pat, op in comp_patterns:
            for match in re.finditer(pat, text_lower):
                v1, v2 = float(match.group(1)), float(match.group(2))
                prop_name = f"{v1}_{op}_{v2}"
                propositions.append(prop_name)
                if op == 'gt': facts[prop_name] = 1.0 if v1 > v2 else 0.0
                elif op == 'lt': facts[prop_name] = 1.0 if v1 < v2 else 0.0
                elif op == 'eq': facts[prop_name] = 1.0 if v1 == v2 else 0.0

        # 3. Conditionals (If A then B)
        cond_pattern = r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)'
        for match in re.finditer(cond_pattern, text_lower):
            p_str = match.group(1).strip()
            q_str = match.group(2).strip()
            if p_str and q_str:
                propositions.extend([p_str, q_str])
                edges.append((p_str, q_str, 1.0)) # p -> q weight 1

        # 4. Causal/Leads to
        causal_pattern = r'(.+?)\s+(?:causes|leads to|results in)\s+(.+?)(?:\.|,|$)'
        for match in re.finditer(causal_pattern, text_lower):
            p_str = match.group(1).strip()
            q_str = match.group(2).strip()
            if p_str and q_str:
                propositions.extend([p_str, q_str])
                edges.append((p_str, q_str, 1.0))

        # Deduplicate propositions while preserving order
        unique_props = []
        seen = set()
        for p in propositions:
            if p not in seen:
                unique_props.append(p)
                seen.add(p)
        
        return unique_props, edges, facts

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, int, float]:
        """Build adjacency matrix and initial state vector."""
        full_text = f"{prompt} {candidate}"
        props, edges, facts = self._tokenize_and_parse(full_text)
        n = len(props)
        if n == 0:
            return np.array([]), np.array([]), 0, 0.0

        prop_to_idx = {p: i for i, p in enumerate(props)}
        A = np.zeros((n, n), dtype=float)
        
        # Add structural edges
        for src, dst, w in edges:
            if src in prop_to_idx and dst in prop_to_idx:
                A[prop_to_idx[src], prop_to_idx[dst]] = w
                # Symmetric for AND-like relations if needed, but conditional is directed
        
        # Self-loops for negations (simplified handling)
        for i, p in enumerate(props):
            if p.startswith("not_"):
                A[i, i] = -1.0 # Self inhibition for negation logic

        # Initial state x0
        x = np.full(n, 0.5)
        b = np.zeros(n)
        
        # Encode fixed facts from parsing
        for p, val in facts.items():
            if p in prop_to_idx:
                idx = prop_to_idx[p]
                b[idx] = val if val > 0.5 else -1.0 # Bias towards true/false
                x[idx] = val

        return A, x, n, 1.0 if not props else 0.0

    def _model_check(self, A: np.ndarray, x0: np.ndarray) -> Tuple[np.ndarray, int]:
        """Iterative fixed-point exploration."""
        if A.size == 0:
            return np.array([]), 0
        
        n = A.shape[0]
        x = x0.copy()
        b = np.zeros(n) # Bias handled in initialization or separate
        
        # Re-inject facts as hard constraints in b for the iteration
        # For this simplified version, we rely on the initial x and the dynamics
        
        visited_states = 0
        for k in range(self.max_steps):
            x_new = 1.0 / (1.0 + np.exp(-(A @ x + b))) # Sigmoid activation
            # Clamp known facts if necessary, but let dynamics flow for consistency
            
            diff = np.linalg.norm(x_new - x)
            x = x_new
            visited_states += 1
            if diff < self.epsilon:
                break
        return x, visited_states

    def _compute_criticality(self, A: np.ndarray, x: np.ndarray) -> float:
        """Calculate spectral radius of the Jacobian."""
        if A.size == 0 or x.size == 0:
            return 0.0
        
        # Jacobian J = diag(sigma'(z)) * A
        z = A @ x
        sigma_prime = np.exp(-z) / ((1 + np.exp(-z)) ** 2) # Derivative of sigmoid
        J = np.diag(sigma_prime) @ A
        
        try:
            eigvals = np.linalg.eigvals(J)
            rho = np.max(np.abs(eigvals))
            return float(rho)
        except:
            return 0.0

    def _feedback_score(self, x: np.ndarray, target_val: float, g_init: float) -> Tuple[float, float]:
        """Simulate PID control to find optimal gain and score."""
        n = len(x)
        if n == 0:
            return 0.0, 0.0
            
        # Target vector: ideally all propositions in a correct answer align with prompt logic
        # Here we simplify: target is a vector of 'target_val' (e.g., 1.0 for consistent)
        y = np.full(n, target_val)
        
        e_mean = np.mean(np.abs(y - x))
        g = g_init
        e_prev = e_mean
        integral = 0
        
        for _ in range(5): # 5 PID steps
            integral += e_mean
            derivative = e_mean - e_prev
            g = g + self.Kp * e_mean + self.Ki * integral + self.Kd * derivative
            g = np.clip(g, 0.1, 2.0) # Prevent explosion
            e_prev = e_mean
            # Simulate effect of gain on error (conceptual)
            e_mean = e_mean * (1.0 - 0.1 * g) 

        # Final Score formula
        error_norm = np.linalg.norm(y - x) / np.sqrt(n)
        score = g * (1.0 - error_norm)
        return float(score), float(g)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns low confidence if the prompt exhibits ambiguity, presupposition, or unanswerability.
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        presup_triggers = ["have you stopped", "have you quit", "why did", "when did", "how often did"]
        if any(t in p for t in presup_triggers):
            # Check if it implies a past event that isn't established
            if "stopped" in p or "quit" in p or "fail" in p:
                return 0.2

        # 2. Scope/Pronoun Ambiguity
        if re.search(r'\b(every|each)\s+\w+\s+.*\s+a\s+\w+', p) and "same" not in p:
             # Potential scope ambiguity
            if "same" not in p and "different" not in p:
                 pass # Hard to detect purely by regex, but flag if vague
        if re.search(r'\btold\s+\w+\s+he\s+', p) or re.search(r'\btold\s+\w+\s+she\s+', p):
            if "who" in p:
                return 0.2

        # 3. False Dichotomy
        if re.search(r'\beither\s+.*\s+or\s+.*', p) and "only" not in p:
            # Heuristic: if it forces a choice without context
            if "choose" in p or "which" in p:
                return 0.4 # Moderate uncertainty

        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly", "opinion"]
        if any(w in p for w in subjective_words):
            if "fact" not in p and "data" not in p:
                return 0.3

        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Parse prompt structure once
        prompt_props, _, _ = self._tokenize_and_parse(prompt)
        has_structure = len(prompt_props) > 0

        for cand in candidates:
            # 1. Structural Parsing & Graph Build
            A, x0, n, _ = self._build_graph(prompt, cand)
            
            score = 0.0
            reasoning = ""
            
            if n == 0:
                # Fallback to NCD if no structure found (Max 15% weight logic handled by capping)
                ncd = self._ncd_score(prompt, cand)
                # Invert NCD so higher is better, scale to 0.15 max contribution
                base_score = (1.0 - ncd) * 0.15
                score = base_score
                reasoning = "No logical structure detected; relied on compression similarity."
            else:
                # 2. Model Checking
                x_star, S = self._model_check(A, x0)
                
                # 3. Criticality
                C = self._compute_criticality(A, x_star)
                # Normalize Criticality: Ideally near 1.0 is "critical", but we want stability too.
                # Let's treat C as a multiplier: high C (near 1) = high sensitivity.
                # We penalize extreme instability (C > 1.5) or total rigidity (C < 0.1)
                crit_factor = np.exp(-0.5 * (C - 1.0)**2) if C > 0 else 0.5

                # 4. Feedback Control Scoring
                # Target: propositions should be consistent (converge to 0 or 1, not 0.5)
                # We want the answer to resolve ambiguity, so low entropy in x_star is good?
                # Actually, we want the answer to match the prompt's implied truth.
                # Simplified: Score based on convergence and criticality
                fb_score, g_final = self._feedback_score(x_star, 1.0, 1.0)
                
                # Combine: Structural (Graph) + Criticality + Feedback
                # Weighting: Structural presence is key. 
                raw_score = fb_score * crit_factor * (1.0 if S < 40 else 0.8) # Penalty for non-convergence
                
                # Scale to reasonable range
                score = max(0.0, min(1.0, raw_score))
                reasoning = f"Graph nodes: {n}, States: {S}, Criticality: {C:.2f}, Gain: {g_final:.2f}"

            # Apply Epistemic Cap (Tier B)
            if meta_cap < 0.5:
                score = min(score, meta_cap)
                reasoning += " [Cap applied: Ambiguous/Presupposition detected]"
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence level for ambiguous prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Check for structural match
        props, _, _ = self._tokenize_and_parse(f"{prompt} {answer}")
        if not props:
            # No structure found -> Honest uncertainty
            return 0.2
        
        # Run evaluation internally to get a raw score
        # We simulate a single candidate evaluation
        A, x0, n, _ = self._build_graph(prompt, answer)
        if n == 0:
            return 0.2
            
        x_star, _ = self._model_check(A, x0)
        C = self._compute_criticality(A, x_star)
        
        # Heuristic confidence based on convergence and criticality
        # If the system is too chaotic (C >> 1) or too rigid (C ~ 0), confidence drops
        if C > 2.0 or C < 0.1:
            raw_conf = 0.4
        else:
            # Check if solution is decisive (close to 0 or 1)
            decisiveness = np.mean(np.abs(np.array(x_star) - 0.5)) * 2 # 0 to 1
            raw_conf = decisiveness * 0.8 + 0.1
            
        # Apply cap
        final_conf = min(raw_conf, meta_cap)
        return float(np.clip(final_conf, 0.0, 0.95)) # Never 1.0 to allow for unknown unknowns