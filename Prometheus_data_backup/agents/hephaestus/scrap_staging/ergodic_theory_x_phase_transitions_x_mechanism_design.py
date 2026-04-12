import re
import numpy as np

class ReasoningTool:
    """
    Ergodic-Mechanism Reasoning Tool.
    
    Core Mechanism:
    1. Structural Parsing: Extracts propositions (negations, comparatives, conditionals)
       from prompt and candidates to build a logical hypergraph representation.
    2. Ergodic Averaging: Simulates belief propagation on the graph. The stationary 
       distribution of the adjacency matrix represents the 'consensus truth' derived 
       from the logical structure.
    3. Phase Transition Detection: Uses the variance of the belief vector as an order 
       parameter. High variance indicates a fragmented/disordered logical state (penalty).
    4. Mechanism Design: Applies a proper scoring rule. Candidates are scored based on 
       alignment with the ergodic consensus (b*) and penalized for logical inconsistency 
       (distance from b*), incentivizing truth-telling.
    """
    
    def __init__(self):
        self.alpha = 0.85  # Damping factor for ergodic iteration
        self.lambda_pen = 0.5  # Penalty weight for mechanism design
        self.max_iter = 50
        self.tol = 1e-6

    def _extract_features(self, text):
        """Extract structural features into a binary vector and edge list."""
        text_lower = text.lower()
        features = []
        edges = []  # (source_idx, target_idx, weight)
        
        # Patterns
        negations = ["not", "no ", "never", "none", "cannot"]
        comparatives = ["greater", "less", "more", "fewer", "bigger", "smaller", "equals", "equal"]
        conditionals = ["if", "then", "unless", "otherwise"]
        causals = ["causes", "leads to", "results in"]
        
        # Feature extraction (simplified to indices for the vector)
        # 0: has_negation, 1: has_comparative, 2: has_conditional, 3: has_causal, 4: has_number
        
        f_vec = [0] * 5
        
        if any(n in text_lower for n in negations):
            f_vec[0] = 1
        if any(c in text_lower for c in comparatives):
            f_vec[1] = 1
        if any(c in text_lower for c in conditionals):
            f_vec[2] = 1
        if any(c in text_lower for c in causals):
            f_vec[3] = 1
        if re.search(r'\d+', text):
            f_vec[4] = 1
            
        # Numeric evaluation logic (Constraint Propagation)
        nums = re.findall(r'-?\d+\.?\d*', text)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                # Encode numeric consistency as a feature interaction
                if "less" in text_lower or "smaller" in text_lower:
                    f_vec[4] = 1.0 if n1 < n2 else 0.0 # Reward correct numeric logic
                elif "greater" in text_lower or "bigger" in text_lower:
                    f_vec[4] = 1.0 if n1 > n2 else 0.0
            except ValueError:
                pass

        return np.array(f_vec, dtype=float)

    def _build_graph(self, prompt, candidate):
        """Build adjacency matrix M from prompt and candidate features."""
        # Combine features
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # Node count
        n = len(p_feat) + len(c_feat)
        M = np.zeros((n, n))
        
        # Self loops for stability (ergodicity)
        np.fill_diagonal(M, 0.1)
        
        # Edges: Prompt influences Candidate (Logical implication)
        # If prompt has a conditional (feat 2) and candidate has matching structure
        if p_feat[2] > 0 and c_feat[2] > 0:
            # Strong connection between conditional structures
            M[len(p_feat):, :len(p_feat)] = 0.5 
            
        # Edges: Feature compatibility (Mechanism alignment)
        # Encourage alignment between prompt constraints and candidate assertions
        for i in range(len(p_feat)):
            if p_feat[i] > 0 and c_feat[i] > 0:
                # Positive reinforcement for matching structural features
                M[len(p_feat) + i, i] = 1.0
                M[i, len(p_feat) + i] = 0.5 # Feedback loop
                
        # Negation handling: If prompt says "not X" and candidate says "X", penalize
        # Simplified: If prompt has negation but candidate lacks it (or vice versa in specific contexts)
        if p_feat[0] > 0 and c_feat[0] == 0:
             # Weakens the link
             M[len(p_feat):, :len(p_feat)] *= 0.5

        # Normalize to column-stochastic (Markov matrix)
        col_sums = M.sum(axis=0)
        col_sums[col_sums == 0] = 1  # Avoid division by zero
        M = M / col_sums
        
        return M

    def _ergodic_average(self, M, f_a):
        """Power iteration to find stationary distribution b*."""
        n = M.shape[0]
        b = np.ones(n) / n  # Initialize uniform belief
        
        # Ensure f_a matches dimension (pad if necessary)
        if len(f_a) < n:
            f_ext = np.zeros(n)
            f_ext[:len(f_a)] = f_a
        else:
            f_ext = f_a[:n]
            
        f_ext = f_ext / (f_ext.sum() + 1e-9) # Normalize external input

        for _ in range(self.max_iter):
            b_new = self.alpha * np.dot(M, b) + (1 - self.alpha) * f_ext
            if np.linalg.norm(b_new - b, 1) < self.tol:
                break
            b = b_new
            
        return b

    def _phase_transition_score(self, b):
        """Calculate order parameter phi and base score."""
        phi = np.var(b)
        # Heuristic critical threshold derived from binary state variance max (0.25)
        # We treat high variance as 'disordered' (fragmented logic)
        tau_c = 0.15 
        if phi < tau_c:
            return 1.0 - phi  # Ordered phase: high score
        else:
            return max(0.0, 1.0 - phi * 2)  # Disordered phase: penalty

    def evaluate(self, prompt, candidates):
        results = []
        if not candidates:
            return []
            
        # Pre-calculate prompt features to anchor the graph
        p_feat = self._extract_features(prompt)
        n_p = len(p_feat)
        
        scores = []
        
        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # 1. Build Graph
            M = self._build_graph(prompt, cand)
            
            # 2. Ergodic Averaging
            # Combine prompt and candidate features for the initial state vector
            f_a = np.concatenate([p_feat, c_feat])
            b_star = self._ergodic_average(M, f_a)
            
            # 3. Phase Transition Detection
            s0 = self._phase_transition_score(b_star)
            
            # 4. Mechanism Design Scoring
            # Penalty for deviation from consensus (b_star)
            # We compare the candidate portion of the belief vector to the candidate features
            c_belief = b_star[n_p:]
            c_feat_norm = c_feat / (c_feat.sum() + 1e-9) if c_feat.sum() > 0 else c_feat
            
            # Ensure dimensions match for distance
            min_len = min(len(c_belief), len(c_feat_norm))
            deviation = np.linalg.norm(c_belief[:min_len] - c_feat_norm[:min_len])
            
            final_score = s0 - self.lambda_pen * deviation
            
            # Add NCD tiebreaker logic (small boost if structurally similar)
            # Only if scores are very close, but here we add a tiny structural bonus
            struct_overlap = np.sum((p_feat > 0) & (c_feat > 0)) * 0.01
            final_score += struct_overlap
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Ergodic consensus: {s0:.2f}, Deviation penalty: {deviation:.2f}"
            })
            scores.append(float(final_score))

        # Rank by score descending
        sorted_indices = np.argsort(scores)[::-1]
        return [results[i] for i in sorted_indices]

    def confidence(self, prompt, answer):
        """Return confidence 0-1 based on the evaluation score."""
        # Evaluate single candidate against itself to get intrinsic confidence
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        # Map score to 0-1 range roughly. Scores can be negative.
        # Assume max plausible score ~1.5, min ~ -1.0
        conf = (score + 1.0) / 2.5
        return max(0.0, min(1.0, conf))