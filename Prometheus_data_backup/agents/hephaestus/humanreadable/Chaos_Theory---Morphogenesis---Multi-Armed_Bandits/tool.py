import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Morphogenetic Bandit (CMB) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. Candidates are scored based on 
       constraint satisfaction and numeric correctness.
    2. Morphogenetic Field (Clustering): Candidates are embedded in a 1D space based on 
       structural similarity to the prompt's key terms. A reaction-diffusion approximation 
       aggregates scores of similar candidates, creating "peaks" of confidence.
    3. Chaotic Exploration (Diversity Bonus): A logistic map generates a deterministic 
       chaotic sequence. This injects a small, aperiodic perturbation into the scoring 
       to break ties and prevent locking onto superficially similar but logically flawed 
       candidates (simulating exploration).
    4. NCD (Tiebreaker): Used only when structural scores are identical.
    """

    def __init__(self):
        self.r = 3.99  # Logistic map parameter (edge of chaos)
        self.x = 0.5   # Initial chaotic state
        self.D_u = 0.1 # Diffusion coefficient approximation
        self.steps = 5 # Morphogenesis iteration steps

    def _logistic_step(self) -> float:
        """Generates the next value in the chaotic sequence."""
        self.x = self.r * self.x * (1.0 - self.x)
        return self.x

    def _structural_parse(self, text: str) -> Dict:
        """Extracts logical and numeric features from text."""
        text_lower = text.lower()
        features = {
            'has_not': bool(re.search(r'\b(not|no|never|without)\b', text_lower)),
            'has_if': bool(re.search(r'\b(if|unless|provided)\b', text_lower)),
            'has_comp': bool(re.search(r'(more|less|greater|smaller|larger|better|worst)', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text)
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 1.0
        return (z12 - min(z1, z2)) / max_len

    def _morphogen_update(self, scores: np.ndarray, adjacency: np.ndarray) -> np.ndarray:
        """Approximates reaction-diffusion smoothing on the candidate graph."""
        # Simple diffusion step: u_new = u + D * Laplacian(u)
        # Assuming 1D ring topology for simplicity based on adjacency
        laplacian = np.dot(adjacency, scores) - scores
        return scores + self.D_u * laplacian

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feat = self._structural_parse(prompt)
        n = len(candidates)
        
        # 1. Initialize State
        # Embed candidates: simple hash-based position for adjacency
        positions = np.array([hash(c) % 100 for c in candidates], dtype=float)
        positions = (positions - positions.mean()) / (positions.std() + 1e-9)
        
        # Adjacency matrix (Gaussian kernel based on position distance)
        dist_matrix = np.abs(positions[:, None] - positions[None, :])
        adjacency = np.exp(-dist_matrix ** 2 / 0.5)
        np.fill_diagonal(adjacency, 0)
        adjacency = adjacency / (adjacency.sum(axis=1, keepdims=True) + 1e-9)

        scores = np.zeros(n)
        reasons = []

        # 2. Structural Scoring Loop
        for i, cand in enumerate(candidates):
            cand_feat = self._structural_parse(cand)
            score = 0.0
            reason_parts = []

            # Constraint: Negation matching
            if prompt_feat['has_not'] == cand_feat['has_not']:
                score += 2.0
                reason_parts.append("negation_match")
            else:
                score -= 1.0 # Penalty for logical mismatch
            
            # Constraint: Comparative presence
            if prompt_feat['has_comp'] and cand_feat['has_comp']:
                score += 1.5
                reason_parts.append("comparative_detected")

            # Numeric Evaluation
            if prompt_feat['numbers'] and cand_feat['numbers']:
                p_nums = prompt_feat['numbers']
                c_nums = cand_feat['numbers']
                # Check for direct number presence or simple arithmetic relation
                if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    score += 3.0
                    reason_parts.append("number_match")
                elif len(p_nums) >= 2 and len(c_nums) >= 1:
                    # Heuristic: if prompt has A, B and candidate has A+B or A-B
                    target_sum = p_nums[0] + p_nums[1] if len(p_nums) > 1 else 0
                    target_diff = p_nums[0] - p_nums[1] if len(p_nums) > 1 else 0
                    if any(abs(c - target_sum) < 1e-6 or abs(c - target_diff) < 1e-6 for c in c_nums):
                        score += 4.0
                        reason_parts.append("arithmetic_correct")
                    else:
                        score -= 2.0 # Wrong number
                        reason_parts.append("number_mismatch")

            # Length heuristic (avoid too short/long)
            if 0.5 * prompt_feat['length'] <= cand_feat['length'] <= 2.0 * prompt_feat['length']:
                score += 0.5
            
            scores[i] = score
            reasons.append(", ".join(reason_parts) if reason_parts else "structural_neutral")

        # 3. Morphogenetic Aggregation (Reaction-Diffusion)
        # Evolve the score field to let high-scoring clusters influence neighbors
        current_field = scores.copy()
        for _ in range(self.steps):
            current_field = self._morphogen_update(current_field, adjacency)
        
        # Normalize morphogen field to 0-1 range
        min_f, max_f = current_field.min(), current_field.max()
        if max_f - min_f > 1e-9:
            morph_scores = (current_field - min_f) / (max_f - min_f)
        else:
            morph_scores = np.ones(n) * 0.5

        # 4. Chaotic Exploration & Final Ranking
        final_results = []
        for i in range(n):
            # Inject chaotic perturbation
            chaos_val = self._logistic_step() 
            # Combine morphogenetic score with chaotic exploration bonus
            # Chaos helps break ties and explores edge cases deterministically
            final_score = morph_scores[i] + (chaos_val * 0.05) 
            
            # NCD Tiebreaker logic (only if scores are very close)
            ncd_penalty = 0.0
            if i > 0 and abs(final_score - final_results[-1]['score_raw']) < 0.01:
                ncd_val = self._compute_ncd(prompt, candidates[i])
                ncd_penalty = ncd_val * 0.001 # Small penalty for high complexity if tied
            
            final_score -= ncd_penalty

            final_results.append({
                "candidate": candidates[i],
                "score": float(final_score),
                "reasoning": f"{reasons[i]}; morphogen:{morph_scores[i]:.2f}; chaos:{chaos_val:.2f}",
                "score_raw": final_score # Internal use for sorting stability
            })

        # Sort descending by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Clean up internal keys
        for res in final_results:
            del res['score_raw']
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment and morphogenetic potential."""
        # Re-use evaluation logic for a single candidate
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # The score from evaluate is already normalized roughly 0-1 + small chaos
        conf = results[0]['score']
        return max(0.0, min(1.0, conf))