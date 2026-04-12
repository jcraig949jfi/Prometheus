import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A causal-plasticity reasoning tool that models prompts as dynamical systems.
    It constructs a causal graph, applies Hebbian plasticity, tunes to criticality,
    and evaluates causal consistency via do-calculus approximation.
    
    Key Features:
    - Structural Parsing: Extracts causal triples, negations, and comparatives.
    - Dynamics: Uses Lyapunov-like stability analysis on the graph adjacency matrix.
    - Criticality: Adjusts weights to maximize susceptibility (variance/eigen-gap).
    - Epistemic Honesty: Detects ambiguity/presupposition to cap confidence.
    """

    # Causal verbs and relations
    CAUSAL_VERBS = ["cause", "lead", "result", "produce", "increase", "decrease", "change", "affect"]
    COMPARATIVES = ["greater", "less", "more", "fewer", "higher", "lower", "before", "after"]
    NEGATIONS = ["not", "no", "never", "without", "none"]
    
    def __init__(self):
        self.rng = np.random.RandomState(42)  # Deterministic initialization

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract (subject, relation, object) triples based on causal verbs."""
        triples = []
        words = self._tokenize(text)
        if len(words) < 3:
            return triples
            
        # Simple sliding window for subject-verb-object
        for i in range(len(words) - 2):
            w_prev, w_curr, w_next = words[i], words[i+1], words[i+2]
            
            # Check for causal verb in middle
            if any(v in w_curr for v in self.CAUSAL_VERBS):
                triples.append((w_prev, w_curr, w_next))
            # Check for comparative
            elif any(c in w_curr for c in self.COMPARATIVES):
                triples.append((w_prev, w_curr, w_next))
                
        return triples

    def _build_graph(self, text: str) -> Tuple[np.ndarray, Dict[str, int], Dict[int, str]]:
        """Construct weighted adjacency matrix from text."""
        tokens = self._tokenize(text)
        unique_nodes = list(set(tokens))
        node2idx = {n: i for i, n in enumerate(unique_nodes)}
        idx2node = {i: n for n, i in node2idx.items()}
        n = len(unique_nodes)
        
        if n == 0:
            return np.array([]), node2idx, idx2node
            
        W = np.zeros((n, n))
        triples = self._extract_triples(text)
        
        # Base weights from triples
        for s, r, o in triples:
            if s in node2idx and o in node2idx:
                u, v = node2idx[s], node2idx[o]
                sign = 1.0
                if any(neg in r for neg in self.NEGATIONS) or any(neg in s for neg in self.NEGATIONS):
                    sign = -1.0
                W[u, v] += sign
                
        # Hebbian plasticity & Pruning (Sliding window co-occurrence)
        k = 3
        for i in range(len(tokens) - k):
            window = tokens[i:i+k]
            for a in window:
                for b in window:
                    if a != b and a in node2idx and b in node2idx:
                        u, v = node2idx[a], node2idx[b]
                        # Hebbian update: strengthen co-occurrence
                        W[u, v] += 0.1 * (1.0 - W[u, v]) 
                        # Decay
                        W[u, v] -= 0.05 * W[u, v]
                        
        W = np.clip(W, -1.0, 1.0)
        return W, node2idx, idx2node

    def _tune_criticality(self, W: np.ndarray) -> Tuple[np.ndarray, float]:
        """Adjust temperature T to maximize susceptibility chi."""
        if W.size == 0:
            return W, 0.0
            
        # Initial susceptibility
        D = np.diag(np.sum(np.abs(W), axis=1))
        L = D - W
        try:
            eig = np.linalg.eigvalsh(L)
            gap = max(eig[-1] - eig[0], 1e-8)
            chi = np.var(W) / gap
        except:
            chi = 0.0
            gap = 1.0
            
        # Gradient ascent on T (simulated)
        T = 1.0
        target_chi = 0.5 # Empirical target for small graphs
        for _ in range(5):
            dT = 0.1 * (target_chi - chi)
            T += dT
            W_new = W * T
            # Recalculate chi
            D_new = np.diag(np.sum(np.abs(W_new), axis=1))
            L_new = D_new - W_new
            try:
                eig_new = np.linalg.eigvalsh(L_new)
                gap_new = max(eig_new[-1] - eig_new[0], 1e-8)
                chi = np.var(W_new) / gap_new
                W = W_new
            except:
                break
                
        return W, chi

    def _estimate_causal_effect(self, W: np.ndarray, node2idx: Dict, text: str) -> float:
        """Approximate do-calculus back-door adjustment."""
        if W.size == 0 or len(node2idx) < 2:
            return 0.0
            
        # Heuristic: Identify potential intervention (subject of first causal verb)
        triples = self._extract_triples(text)
        if not triples:
            return 0.0
            
        s_sub, _, _ = triples[0]
        if s_sub not in node2idx:
            return 0.0
            
        idx_X = node2idx[s_sub]
        
        # Find parents of X (Z)
        parents = np.where(W[:, idx_X] != 0)[0]
        idx_Y = (idx_X + 1) % W.shape[0] # Heuristic outcome: next node
        
        if len(parents) == 0:
            # Direct effect if no confounders
            return float(np.sum(W[idx_X, :]))
            
        # Back-door adjustment approximation
        try:
            W_ZZ = W[parents][:, parents]
            W_ZY = W[parents, idx_Y]
            W_XZ = W[idx_X, parents]
            
            if W_ZZ.size == 0:
                return 0.0
                
            beta = np.linalg.lstsq(W_ZZ, W_ZY, rcond=None)[0]
            effect = float(np.dot(beta, W_XZ))
            return effect
        except:
            return 0.0

    def _extract_claimed_effect(self, text: str) -> float:
        """Extract numeric magnitude from text."""
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        if nums:
            return float(nums[-1])
        # Detect directionality
        if any(w in text.lower() for w in ["increase", "rise", "gain", "more"]):
            return 1.0
        if any(w in text.lower() for w in ["decrease", "fall", "loss", "less"]):
            return -1.0
        return 0.0

    def _check_dynamics_stability(self, W: np.ndarray) -> float:
        """
        Frame C: Dynamics Tracker.
        Analyze the stability of the state evolution x(t+1) = W * x(t).
        Returns a stability score based on the spectral radius.
        """
        if W.size == 0:
            return 0.0
        try:
            eigenvalues = np.linalg.eigvals(W)
            spectral_radius = np.max(np.abs(eigenvalues))
            # Stable if spectral radius <= 1 (Lyapunov stability for linear systems)
            # Score higher if close to critical point (radius ~ 1.0) but not divergent
            if spectral_radius > 1.5:
                return 0.1 # Divergent
            elif 0.8 <= spectral_radius <= 1.2:
                return 1.0 # Critical/Ideal
            else:
                return 0.5 # Sub-critical
        except:
            return 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if re.search(r"\b(have you|did you|why did|when did)\s+\w+\s+(stop|quit|fail|start)\b", p_lower):
            score = 0.2
        # 2. Scope/Pronoun ambiguity
        if re.search(r"\b(every|all)\s+\w+\s+\w+\s+a\s+\w+\b", p_lower) and "same" in p_lower:
            score = 0.4
        if re.search(r"\b(told|said)\s+\w+\s+he\s+", p_lower) and "who" in p_lower:
            score = 0.3
        # 3. False dichotomy
        if re.search(r"\beither\s+\w+\s+or\s+\w+\b", p_lower) and "option" not in p_lower:
            score = 0.6
        # 4. Subjectivity
        if re.search(r"\b(best|worst|favorite|beautiful)\b", p_lower) and "calculate" not in p_lower:
            score = 0.5
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        return (z12 - min(z1, z2)) / max(z1, z2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_W, p_nodes, _ = self._build_graph(prompt)
        prompt_W, chi_prompt = self._tune_criticality(prompt_W)
        prompt_stability = self._check_dynamics_stability(prompt_W)
        
        # Extract claimed effect from prompt if present (for comparison)
        prompt_effect = self._extract_claimed_effect(prompt)

        for cand in candidates:
            # 1. Structural & Causal Analysis
            full_text = f"{prompt} {cand}"
            W, nodes, _ = self._build_graph(full_text)
            
            if W.size == 0:
                score = -10.0
                reasoning = "Failed to parse structure."
            else:
                # 2. Criticality Tuning
                W_tuned, chi = self._tune_criticality(W)
                
                # 3. Causal Inference
                est_effect = self._estimate_causal_effect(W_tuned, nodes, full_text)
                claim_effect = self._extract_claimed_effect(cand)
                
                # 4. Dynamics Stability (Frame C)
                stability = self._check_dynamics_stability(W_tuned)
                
                # 5. Scoring Logic
                # Error term
                error = abs(est_effect - claim_effect)
                # Consistency with prompt's implied effect if available
                prompt_consistency = 0.0
                if prompt_effect != 0:
                    prompt_consistency = -abs(claim_effect - prompt_effect)
                
                # Composite Score
                # Structural/Computation (60%), Dynamics (25%), NCD (15%)
                base_score = -error + 0.5 * prompt_consistency
                dyn_score = 2.0 * stability 
                ncd_score = (1.0 - self._ncd(prompt, cand)) * 0.5
                
                score = base_score + dyn_score + ncd_score
                reasoning = f"Est:{est_effect:.2f}, Claim:{claim_effect}, Chi:{chi:.2f}, Stable:{stability:.2f}"

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty checks.
        """
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural validity check
        W, nodes, _ = self._build_graph(f"{prompt} {answer}")
        if W.size == 0 or len(nodes) < 2:
            return 0.1  # Low confidence if unparseable
            
        # 3. Dynamics stability check
        W_tuned, _ = self._tune_criticality(W)
        stability = self._check_dynamics_stability(W_tuned)
        
        # Base confidence on stability and graph density
        base_conf = 0.5 + 0.4 * stability
        if len(nodes) < 3:
            base_conf *= 0.8 # Penalize sparse graphs
            
        # Apply epistemic cap
        final_conf = min(base_conf, meta_cap)
        
        # Never exceed 0.9 without explicit calculation proof (heuristic here)
        if "calculate" not in prompt.lower() and "solve" not in prompt.lower():
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))