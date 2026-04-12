import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning evaluator combining Chaos Theory, Cognitive Load Theory, and Neuromodulation.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and structural features (negations, comparatives, etc.).
    2. Graph Construction: Builds a directed influence matrix based on logical implications.
    3. Neuromodulation: Applies gain vectors (dopamine/serotonin analogs) based on sentiment cues.
    4. Working Memory: Chunks the graph to Miller's limit (k=7) to simulate cognitive constraints.
    5. Stability Analysis: Computes a Lyapunov-like exponent by iterating a logistic map with 
       small perturbations. Stable candidates (negative exponent, high score) resist noise, 
       indicating robust reasoning.
    """

    def __init__(self):
        self.k_limit = 7  # Miller's Law
        self.steps = 20
        self.epsilon = 1e-3
        
        # Lexicons for neuromodulatory gains
        self.pos_words = {'correct', 'true', 'yes', 'good', 'valid', 'increase', 'gain', 'success'}
        self.neg_words = {'false', 'no', 'bad', 'invalid', 'decrease', 'loss', 'fail', 'error'}
        
        # Structural regex patterns
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nor)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater|smaller|higher|lower)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            'ordering': re.compile(r'[><=]+')
        }

    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions based on sentence splitting and structural cues."""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]', text)
        props = []
        for s in sentences:
            s = s.strip()
            if s:
                props.append(s)
        return props if props else [text]

    def _get_reward_signal(self, text: str) -> float:
        """Calculate dopamine-like reward signal."""
        tokens = set(re.findall(r'\b\w+\b', text.lower()))
        matches = len(tokens.intersection(self.pos_words))
        return 1.0 if matches > 0 else 0.0

    def _get_aversion_signal(self, text: str) -> float:
        """Calculate serotonin-like aversion signal."""
        tokens = set(re.findall(r'\b\w+\b', text.lower()))
        matches = len(tokens.intersection(self.neg_words))
        return 1.0 if matches > 0 else 0.0

    def _build_influence_matrix(self, props: List[str]) -> Tuple[np.ndarray, List[float], List[float]]:
        """Build influence matrix W and gain vectors."""
        n = len(props)
        if n == 0:
            return np.zeros((0,0)), [], []
            
        W = np.zeros((n, n))
        g_da = np.zeros(n)
        g_5ht = np.zeros(n)
        
        for i, p in enumerate(props):
            p_lower = p.lower()
            tokens = set(re.findall(r'\b\w+\b', p_lower))
            
            # Neuromodulatory gains
            reward = 1.0 if tokens.intersection(self.pos_words) else 0.0
            aversion = 1.0 if tokens.intersection(self.neg_words) else 0.0
            g_da[i] = 1 + 0.2 * reward
            g_5ht[i] = 1 - 0.15 * aversion
            
            # Structural linking (Heuristic: sequential implication & keyword density)
            for j in range(n):
                if i == j:
                    W[i, j] = 1.0 # Self-loop for stability
                    continue
                
                q_lower = props[j].lower()
                score = 0.0
                
                # Direct implication heuristic: if prop i contains conditional and j is subsequent
                if self.patterns['conditional'].search(p):
                    if j > i: score += 0.8
                
                # Comparative/Ordering links
                if self.patterns['comparative'].search(p) or self.patterns['ordering'].search(p):
                    if j > i: score += 0.5
                    
                # Causal links
                if self.patterns['causal'].search(p):
                    if j > i: score += 0.7
                
                # Numeric consistency check (simplified)
                nums_i = self.patterns['numeric'].findall(p)
                nums_j = self.patterns['numeric'].findall(q_lower) # Note: using q_lower here was a bug risk, fixed to props[j]
                nums_j = self.patterns['numeric'].findall(props[j])
                
                if nums_i and nums_j:
                    # If numbers match, strong link
                    if set(nums_i) == set(nums_j):
                        score += 0.9
                    # If numbers are ordered logically (simple check)
                    try:
                        if float(nums_i[0]) > float(nums_j[0]) and "less" in p_lower:
                             score -= 0.5 # Penalty for contradiction
                    except: pass

                W[i, j] = min(1.0, score)

        # Apply gains: G = diag(g_da * g_5ht)
        g_combined = g_da * g_5ht
        G = np.diag(g_combined)
        W_tilde = G @ W
        
        return W_tilde, g_da, g_5ht

    def _compute_stability_score(self, text: str) -> float:
        """Compute the Lyapunov-like stability score."""
        props = self._extract_propositions(text)
        if not props:
            return 0.0
            
        W, _, _ = self._build_influence_matrix(props)
        n = W.shape[0]
        if n == 0:
            return 0.0

        # Working memory chunking: Keep top-k nodes by degree + gain
        # Since we already applied gain to W, we sum rows for importance
        importance = np.sum(np.abs(W), axis=1)
        if n > self.k_limit:
            top_indices = np.argsort(importance)[-self.k_limit:]
            # Reconstruct reduced matrix
            W_reduced = W[np.ix_(top_indices, top_indices)]
        else:
            W_reduced = W
            
        # Normalize rows to prevent explosion (Softmax-like or simple sum normalization)
        row_sums = np.sum(np.abs(W_reduced), axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1 # Avoid div by zero
        W_norm = W_reduced / row_sums
        
        # Initial state
        x0 = np.ones(n) * 0.5 if n <= self.k_limit else np.ones(self.k_limit) * 0.5
        b = np.ones_like(x0) * 0.1
        
        # Perturbation
        x_pert = x0.copy()
        idx = np.random.randint(0, len(x0))
        x_pert[idx] += self.epsilon
        
        lyap_sum = 0.0
        count = 0
        
        # Iteration
        x_curr = x0
        x_p_curr = x_pert
        
        for t in range(self.steps):
            # Logistic sigmoid
            def sigmoid(z): return 1 / (1 + np.exp(-z))
            
            x_next = sigmoid(W_norm @ x_curr + b)
            x_p_next = sigmoid(W_norm @ x_p_curr + b)
            
            diff_curr = np.linalg.norm(x_next - x_p_curr) # Distance between perturbed and unperturbed trajectories? 
            # Actually, Lyapunov measures divergence of two nearby trajectories.
            # d_t = || x_t - y_t ||
            
            dist_t = np.linalg.norm(x_curr - x_p_curr)
            dist_next = np.linalg.norm(x_next - x_p_next)
            
            if dist_t > 1e-10:
                lyap_sum += np.log((dist_next + 1e-10) / (dist_t + 1e-10))
                count += 1
            
            x_curr = x_next
            x_p_curr = x_p_next
            
        if count == 0:
            return 0.5
            
        lambda_val = lyap_sum / count
        # Score: -lambda (clipped 0-1). Negative lambda (stable) -> positive score.
        score = -lambda_val
        return float(np.clip(score, 0, 1))

    def _structural_parse_score(self, text: str) -> float:
        """Primary scoring signal: Structural complexity and consistency."""
        score = 0.0
        text_lower = text.lower()
        
        # Count structural features
        if self.patterns['negation'].search(text): score += 0.2
        if self.patterns['comparative'].search(text): score += 0.2
        if self.patterns['conditional'].search(text): score += 0.2
        if self.patterns['causal'].search(text): score += 0.2
        if self.patterns['numeric'].search(text): score += 0.1
        if self.patterns['ordering'].search(text): score += 0.1
        
        # Penalty for excessive length without structure (cognitive load penalty)
        words = text.split()
        if len(words) > 50 and score < 0.5:
            score -= 0.1
            
        return min(1.0, score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Primary Signal: Structural Parsing
            struct_score = self._structural_parse_score(cand)
            
            # Secondary Signal: Chaos/Stability Analysis
            # Only run heavy computation if structural score is non-trivial to save time/complexity
            if struct_score > 0.1:
                stability = self._compute_stability_score(cand)
                # Weighted combination: Structure is primary, Stability refines it
                final_score = 0.6 * struct_score + 0.4 * stability
            else:
                # Fallback for low-structure answers (e.g., "Yes", "No")
                # Use NCD as tiebreaker only if structure fails
                final_score = struct_score 
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural: {struct_score:.2f}, Stability: {self._compute_stability_score(cand):.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Reuse evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0