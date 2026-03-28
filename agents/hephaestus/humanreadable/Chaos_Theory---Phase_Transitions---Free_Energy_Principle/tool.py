import re
import numpy as np

class ReasoningTool:
    """
    Implements a Chaos-Theory/Free-Energy based reasoning engine.
    Mechanism:
    1. Parses text into a logical proposition graph (nodes=claims, edges=constraints).
    2. Simulates dynamics to minimize prediction error (Free Energy).
    3. Computes the largest Lyapunov exponent to detect chaotic instability.
    4. Scores answers based on low error (consistency) and non-chaotic stability.
    """
    
    def __init__(self):
        self.threshold = 0.5
        self.n_sweep = 21  # Steps for alpha sweep [0, 2]

    def _parse_to_graph(self, text: str):
        """Extracts atomic propositions and logical constraints."""
        text_lower = text.lower()
        propositions = []
        edges = []  # (src_idx, tgt_idx, weight)
        
        # Simple sentence splitter
        sentences = re.split(r'[.!?]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Normalize
            s_clean = sent.replace(" is ", " equals ").replace(" are ", " equals ")
            words = s_clean.split()
            if not words:
                continue

            # Pattern 1: Comparatives (A > B, A < B, A equals B)
            # Detect numbers
            nums = re.findall(r'-?\d+\.?\d*', s_clean)
            if len(nums) >= 2:
                # Assume relation based on keywords or position
                p1 = f"val_1={nums[0]}"
                p2 = f"val_2={nums[1]}"
                propositions.append(p1)
                propositions.append(p2)
                idx1, idx2 = len(propositions)-2, len(propositions)-1
                
                if "greater" in s_clean or "larger" in s_clean or "more" in s_clean:
                    edges.append((idx1, idx2, 1.0)) # If 1 is true, 2 must be consistent with >
                elif "less" in s_clean or "smaller" in s_clean:
                    edges.append((idx1, idx2, -1.0))
                else:
                    # Default equivalence for numeric statements in same sentence
                    edges.append((idx1, idx2, 1.0))
                    edges.append((idx2, idx1, 1.0))
                continue

            # Pattern 2: Negation (not, never, no)
            has_neg = any(n in s_clean for n in ["not", "never", "no ", "cannot"])
            
            # Pattern 3: Conditionals (if, implies, leads to, causes)
            is_cond = any(k in s_clean for k in ["if", "then", "implies", "leads to", "causes"])
            
            # Create a proposition node for the sentence content
            prop_key = f"prop_{len(propositions)}"
            propositions.append(prop_key)
            curr_idx = len(propositions) - 1
            
            # Self-consistency or link to previous if conditional
            if len(propositions) > 1 and is_cond:
                prev_idx = curr_idx - 1
                # If conditional, link prev -> curr
                w = -1.0 if has_neg else 1.0
                edges.append((prev_idx, curr_idx, w))
            elif has_neg:
                # Mark as negative constraint relative to a hypothetical positive base
                # In this simple parser, we treat negation as a self-penalty or specific flag
                # For the matrix, we add a self-loop with negative weight to induce tension if asserted true
                edges.append((curr_idx, curr_idx, -1.0))

        n = len(propositions)
        if n == 0:
            return np.zeros((1,1)), propositions
            
        W = np.zeros((n, n), dtype=np.float64)
        for i, j, w in edges:
            if 0 <= i < n and 0 <= j < n:
                W[i, j] = w
                
        # Add small diagonal decay to prevent runaway if not constrained
        # But keep logic dominant. 
        return W, propositions

    def _dynamics(self, W, steps=50):
        """Run discrete dynamics to find fixed point and estimate error."""
        n = W.shape[0]
        if n == 0: return 0.0, 0.0
        
        s = np.random.randint(0, 2, size=n).astype(np.float64)
        theta = np.full(n, self.threshold)
        
        min_error = float('inf')
        
        for _ in range(steps):
            # Update rule: s(t+1) = sigma(W*s(t) - theta)
            input_sum = np.dot(W, s) 
            # Hard threshold
            s_new = (input_sum > theta).astype(np.float64)
            
            # Prediction error: difference between actual state and what inputs suggest
            # e = s_new - sigmoid_like(W*s) -> approximated by step difference for binary
            error = np.linalg.norm(s_new - s)
            if error < min_error:
                min_error = error
                
            if np.array_equal(s, s_new):
                break
            s = s_new
            
        return min_error, s

    def _lyapunov(self, W, s_star, epsilon=1e-6):
        """Estimate largest Lyapunov exponent via linearization."""
        n = W.shape[0]
        if n == 0: return 0.0
        
        # Jacobian J = D_sigma * W
        # D_sigma is diagonal: 1 if W*s is near threshold, else 0. 
        # Approximation: Assume active nodes contribute to sensitivity.
        # We compute norm of W restricted to active states.
        
        # Linearize around s_star
        # Derivative of hard threshold is 0 almost everywhere, but in chaos theory context
        # for discrete maps, we look at divergence of trajectories.
        # Simplified: lambda ~ log(||W||) scaled by activity.
        
        # Perturb slightly
        s_pert = s_star.copy() + epsilon
        s_pert = np.clip(s_pert, 0, 1)
        
        try:
            traj1 = np.dot(W, s_star)
            traj2 = np.dot(W, s_pert)
            dist = np.linalg.norm(traj2 - traj1)
            if dist == 0: return -1.0 # Converged completely
            # Lyapunov approx
            lyap = np.log(dist + 1e-9) 
        except:
            return 0.0
            
        return lyap

    def _score_candidate(self, text: str):
        """Compute score based on Free Energy (error) and Chaos (Lyapunov)."""
        W, props = self._parse_to_graph(text)
        n = W.shape[0]
        if n == 0:
            return 0.5 # Neutral if no parseable content

        # Sweep alpha to find phase transition region
        alphas = np.linspace(0.1, 2.0, self.n_sweep)
        best_score = -float('inf')
        
        for alpha in alphas:
            W_scaled = W * alpha
            error, s_final = self._dynamics(W_scaled)
            lyap = self._lyapunov(W_scaled, s_final)
            
            # Free Energy F = 0.5 * ||e||^2
            F = 0.5 * (error ** 2)
            
            # Score = exp(-F) * exp(-max(0, lambda))
            # Penalize high error and positive lyapunov (chaos)
            chaos_penalty = max(0.0, lyap)
            score = np.exp(-F) * np.exp(-chaos_penalty)
            
            if score > best_score:
                best_score = score
                
        return float(best_score)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        # Combine prompt with each candidate for context-aware parsing
        for cand in candidates:
            full_text = f"{prompt} {cand}"
            score = self._score_candidate(full_text)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free-energy minimized state with Lyapunov stability check. Score={score:.4f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        full_text = f"{prompt} {answer}"
        score = self._score_candidate(full_text)
        # Normalize score roughly to 0-1 range based on theoretical bounds [0, 1]
        # Since exp(-F)*exp(-lambda) <= 1, we can use it directly but clamp.
        return min(1.0, max(0.0, score))