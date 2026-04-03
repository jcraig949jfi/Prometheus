import re
import numpy as np
import zlib

class ReasoningTool:
    """
    Implements a Morphogenesis x Adaptive Control x Compositionality reasoning engine.
    
    Mechanism:
    1. Compositionality: Parses text into atomic propositions (nodes) and logical relations (edges).
    2. Morphogenesis: Runs a reaction-diffusion simulation on the graph where truth values 
       propagate via sigmoidal activation functions, stabilizing into a consistent truth pattern.
    3. Adaptive Control: Adjusts edge weights based on the error between current activation 
       and target constraints (derived from question structure), penalizing contradictions.
    4. Epistemic Honesty: Explicitly detects Tier B traps (presuppositions, ambiguity) to 
       cap confidence, ensuring low scores on unanswerable or biased prompts.
    """
    
    def __init__(self):
        self.rng = np.random.default_rng(42)  # Deterministic
        self.t_max = 50
        self.lr = 0.1
        
        # Tier B Trap Patterns
        self.presupposition_re = re.compile(r'\b(have you stopped|have you quit|why did .+ (fail|stop|break))\b', re.I)
        self.scope_ambiguity_re = re.compile(r'\b(every|all) .+ (a|an) .+\b', re.I) # Simplified scope check
        self.pronoun_ambiguity_re = re.compile(r'\b(told|said to) .+ (he|she|him|her)\b', re.I)
        self.false_dichotomy_re = re.compile(r'\b(either .+ or .+)\b', re.I)
        self.subjectivity_re = re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.I)
        self.unanswerable_re = re.compile(r'\b(missing info|cannot be determined|not enough information)\b', re.I)

    def _extract_props(self, text: str) -> list:
        """Extract atomic propositions and logical cues."""
        props = []
        # Normalize
        t = text.lower()
        
        # Extract comparatives
        if re.search(r'(greater|larger|more|higher).*than', t): props.append(("comp_gt", 1.0))
        if re.search(r'(less|smaller|fewer|lower).*than', t): props.append(("comp_lt", 1.0))
        
        # Extract negations
        if re.search(r'\b(not|no|never|none)\b', t): props.append(("neg", -1.0))
        
        # Extract conditionals
        if re.search(r'\b(if|unless|then)\b', t): props.append(("cond", 0.5))
        
        # Extract numbers (simplified)
        nums = re.findall(r'-?\d+\.?\d*', text)
        if len(nums) >= 2:
            try:
                v1, v2 = float(nums[0]), float(nums[1])
                if v1 > v2: props.append(("num_gt", 1.0))
                elif v1 < v2: props.append(("num_lt", -1.0))
                else: props.append(("num_eq", 0.0))
            except: pass
            
        if not props: props.append(("base", 0.0))
        return props

    def _build_graph(self, prompt: str, candidate: str):
        """Construct graph nodes and adjacency matrix."""
        full_text = f"{prompt} {candidate}"
        props = self._extract_props(full_text)
        n = max(len(props), 3)
        
        # Nodes: activations initialized to 0.5 (uncertain)
        a = np.ones(n) * 0.5
        
        # Edges: Weighted adjacency matrix
        # Diagonal is self-bias, off-diagonal are relations
        W = np.eye(n) * 0.1 
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Compositional rule: similar props reinforce, opposites inhibit
                    p_i, p_j = props[i][0] if i < len(props) else "base", props[j][0] if j < len(props) else "base"
                    if p_i == p_j: W[i, j] = 0.8
                    elif ("gt" in p_i and "lt" in p_j) or ("lt" in p_i and "gt" in p_j):
                        W[i, j] = -0.8
                    else:
                        W[i, j] = 0.2 # Weak default connection

        # Biases from morphogen gradients (position in text implies order/causality)
        beta = np.array([p[1] for p in props] + [0.0]*(n-len(props)))
        beta = beta[:n]
        
        return a, W, beta, props

    def _morphogenesis_diffusion(self, a, W, beta, target_vec):
        """Run reaction-diffusion relaxation with adaptive control."""
        T = self.t_max
        for t in range(T):
            # Diffusion step: a(t+1) = sigma(W * a(t) + beta)
            z = W @ a + beta
            a_new = 1.0 / (1.0 + np.exp(-z)) # Sigmoid
            
            # Adaptive Control: Update weights based on error to target
            # Error signal
            e = np.linalg.norm(a_new - target_vec)
            
            # Weight update rule: w_ij += lr * error * a_i * a_j
            # This penalizes paths that lead away from logical consistency
            if e > 0.01:
                adjustment = self.lr * e * np.outer(a_new, a_new)
                W = W + adjustment
                # Clamp weights to prevent explosion
                W = np.clip(W, -1.0, 1.0)
            
            a = a_new
            if np.linalg.norm(a - a_new) < 1e-4: break
            
        return a, e

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (low if trap detected).
        """
        p_lower = prompt.lower()
        
        if self.presupposition_re.search(p_lower): return 0.2
        if self.scope_ambiguity_re.search(p_lower): return 0.4 # Ambiguous scope
        if self.pronoun_ambiguity_re.search(p_lower) and "who" in p_lower: return 0.3
        if self.false_dichotomy_re.search(p_lower): return 0.4
        if self.subjectivity_re.search(p_lower): return 0.3
        if self.unanswerable_re.search(p_lower): return 0.1
        
        # If no structural props found, confidence should be low (honest uncertainty)
        props = self._extract_props(prompt)
        if len(props) == 1 and props[0][0] == "base":
            return 0.3
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a minor tiebreaker."""
        s1_b, s2_b = s1.encode(), s2.encode()
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        if max(c1, c2) == 0: return 0.0
        return c12 / max(c1, c2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Derive target vector from prompt structure (heuristic: prompt implies 'True' goal)
        # In a full system, this would be parsed from the question type.
        # Here we assume the prompt sets a 'True' bias for valid answers.
        base_props = self._extract_props(prompt)
        n_nodes = max(len(base_props), 3)
        target_vec = np.ones(n_nodes) * 0.9 # Target is high activation for consistent logic

        for cand in candidates:
            a, W, beta, props = self._build_graph(prompt, cand)
            
            # Run the core algorithm
            final_a, error = self._morphogenesis_diffusion(a, W, beta, target_vec)
            
            # Score is the mean activation of the final state
            raw_score = float(np.mean(final_a))
            
            # Structural bonus: Did we find matching comparatives/numbers?
            struct_bonus = 0.0
            if any("gt" in p[0] or "lt" in p[0] for p in props): struct_bonus = 0.2
            if any("num" in p[0] for p in props): struct_bonus += 0.2
            
            # NCD tiebreaker (max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.15
            
            # Combine: 50% Algo, 20% Struct, 15% NCD, 15% Base
            combined_score = (raw_score * 0.5) + (struct_bonus * 0.35) + ncd_score + 0.15
            
            # Apply Epistemic Cap
            if meta_cap < 0.5:
                combined_score = min(combined_score, meta_cap)
            
            # Ensure bounds
            combined_score = max(0.0, min(1.0, combined_score))
            
            results.append({
                "candidate": cand,
                "score": combined_score,
                "reasoning": f"Diffusion converged to {final_a.mean():.2f}, Error: {error:.2f}, Meta-Cap: {meta_cap:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by _meta_confidence to ensure epistemic honesty on Tier B traps.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick evaluation to get raw score
        res_list = self.evaluate(prompt, [answer])
        raw_score = res_list[0]["score"] if res_list else 0.0
        
        # If meta analysis detected a trap, cap the confidence severely
        final_conf = min(raw_score, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (simulated by high raw score + no cap)
        if meta_cap == 1.0 and raw_score > 0.85:
            return min(0.95, raw_score)
            
        return max(0.0, min(1.0, final_conf))