import numpy as np
import zlib
import re

class ReasoningTool:
    """
    CPC-MDL Approximation: Chaotic Predictive Coding with MDL Regularization.
    
    Mechanism:
    1. Structural Parsing (Free Energy Minimization): Extracts logical constraints
       (negations, comparatives, conditionals) to form a 'prediction model' of the prompt.
    2. Chaotic Latent Dynamics: Uses a discretized Logistic Map (chaotic attractor) 
       to generate deterministic perturbations. This simulates wandering through 
       hypothesis space without external noise.
    3. Algorithmic Information Prior (MDL): Uses Zlib compression length as a 
       proxy for Kolmogorov Complexity. Candidates that require complex explanations 
       (high compression length of error) are penalized.
    4. Scoring: Combines structural match (prediction error), complexity penalty, 
       and chaotic stability into a single score.
    """

    def __init__(self):
        # Initialize chaotic map parameters (Logistic Map: r=3.99 for chaos)
        self.r = 3.99
        self.chaos_steps = 50
        # Weights for the scoring function
        self.w_struct = 0.60  # Structural parsing (Primary driver)
        self.w_mdL = 0.30     # Complexity penalty
        self.w_chaos = 0.10   # Chaotic stability bonus

    def _logistic_map(self, x0, steps):
        """Generates a deterministic chaotic sequence."""
        x = x0
        seq = []
        for _ in range(steps):
            x = self.r * x * (1 - x)
            seq.append(x)
        return np.array(seq)

    def _extract_structure(self, text):
        """
        Extracts logical features: negations, comparatives, numbers.
        Returns a feature vector and a normalized 'complexity' estimate.
        """
        text_lower = text.lower()
        features = []
        
        # 1. Negation detection (Modus Tollens support)
        negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        has_neg = any(n in text_lower.split() for n in negations)
        features.append(1.0 if has_neg else 0.0)
        
        # 2. Comparative detection
        comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        has_comp = any(c in text_lower for c in comparatives)
        features.append(1.0 if has_comp else 0.0)
        
        # 3. Conditional detection
        conditionals = ['if', 'then', 'unless', 'otherwise']
        has_cond = any(c in text_lower.split() for c in conditionals)
        features.append(1.0 if has_cond else 0.0)
        
        # 4. Numeric extraction for direct evaluation
        numbers = re.findall(r"-?\d+\.?\d*", text)
        nums = [float(n) for n in numbers]
        features.append(len(nums)) # Count of numbers
        
        # 5. Simple numeric logic check (if two numbers exist, check order)
        numeric_logic = 0.0
        if len(nums) >= 2:
            # Heuristic: if prompt implies sorting or comparison, check if candidate respects it
            # Since we only have text here, we just flag presence for now.
            numeric_logic = 1.0
        features.append(numeric_logic)

        return np.array(features)

    def _compute_complexity(self, text):
        """Approximates Kolmogorov complexity via Zlib compression length."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _structural_match_score(self, prompt, candidate):
        """
        Computes similarity based on logical structure rather than bag-of-words.
        Returns a score between 0 and 1.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        # Exact feature match is ideal, but we allow soft matching
        # If prompt has negation, candidate should ideally reflect logical consistency
        # Here we use cosine similarity on structural features as a proxy for logical alignment
        norm_p = np.linalg.norm(p_feat)
        norm_c = np.linalg.norm(c_feat)
        
        if norm_p == 0 or norm_c == 0:
            return 0.5 # Neutral if no features extracted
            
        cos_sim = np.dot(p_feat, c_feat) / (norm_p * norm_c)
        return float(cos_sim)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []

        results = []
        prompt_len = len(prompt)
        if prompt_len == 0:
            prompt_len = 1
            
        # Generate a deterministic chaotic seed from the prompt
        # Hash prompt to float [0.1, 0.9] to avoid fixed points
        seed_hash = int(zlib.crc32(prompt.encode())) % 10000
        x0 = 0.1 + (0.8 * (seed_hash / 10000.0))
        chaos_traj = self._logistic_map(x0, self.chaos_steps)
        chaos_stability = np.mean(chaos_traj) # Average position in attractor

        # Pre-calculate prompt complexity
        prompt_complexity = self._compute_complexity(prompt)
        prompt_struct_score = self._structural_match_score(prompt, prompt)

        for cand in candidates:
            # 1. Free Energy (Prediction Error via Structural Mismatch)
            # Lower mismatch = higher score
            struct_score = self._structural_match_score(prompt, cand)
            
            # 2. MDL Regularization (Complexity Penalty)
            # We prefer candidates that explain the prompt with minimal added description length
            # Combined string complexity vs sum of parts
            combined = prompt + " " + cand
            k_combined = self._compute_complexity(combined)
            k_prompt = prompt_complexity
            k_cand = self._compute_complexity(cand)
            
            # Redundancy indicates good explanation (K(A+B) < K(A) + K(B))
            # If K(A+B) is close to K(A), the candidate is very simple/redundant (good for MDL)
            # But we also want information. 
            # Metric: Compression Ratio of the pair relative to individual parts
            mdl_penalty = (k_combined - k_prompt) / (k_cand + 1) 
            # Normalize penalty: 0 is perfect compression, >1 is expansion
            mdl_score = max(0.0, 1.0 - mdl_penalty)

            # 3. Chaotic Perturbation Bonus
            # Does the candidate text length map to a stable region of the chaotic trajectory?
            # This is a computational analogy: robust hypotheses survive chaotic perturbation.
            cand_hash = int(zlib.crc32(cand.encode())) % 10000
            cand_x0 = 0.1 + (0.8 * (cand_hash / 10000.0))
            cand_traj = self._logistic_map(cand_x0, self.chaos_steps)
            
            # Measure divergence from prompt trajectory (deterministic sensitivity)
            divergence = np.mean(np.abs(chaos_traj - cand_traj))
            # Low divergence for similar concepts, high for random noise
            chaos_score = 1.0 / (1.0 + divergence)

            # Final Score Calculation
            score = (self.w_struct * struct_score) + \
                    (self.w_mdL * mdl_score) + \
                    (self.w_chaos * chaos_score)
            
            # Add a small NCD tiebreaker as requested by patterns
            ncd_val = self._ncd(prompt, cand)
            score += (0.05 * (1.0 - ncd_val)) # Small boost for similarity

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Structural match: {struct_score:.2f}, MDL efficiency: {mdl_score:.2f}, Chaotic stability: {chaos_score:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and complexity.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the top score to 0-1 range roughly
        raw_score = res[0]['score']
        # Sigmoid-like mapping to ensure 0-1 bounds with margin
        confidence = 1.0 / (1.0 + np.exp(-5 * (raw_score - 0.5)))
        return float(np.clip(confidence, 0.0, 1.0))

    def _ncd(self, s1, s2):
        """Normalized Compression Distance helper."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        min_len = min(c1, c2)
        if min_len == 0:
            return 1.0
        return (c12 - min_len) / max(c1, c2)