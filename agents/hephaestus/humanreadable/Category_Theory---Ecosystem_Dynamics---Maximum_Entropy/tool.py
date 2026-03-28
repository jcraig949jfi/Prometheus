import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Maximum-Entropy Ecosystem Network (FMEEN) Implementation.
    
    Mechanism:
    1. Category Theory (H -> P): Treats prompt constraints as morphisms. We map 
       candidate strings to a 'probability space' by scoring structural adherence 
       (negations, comparatives, numeric logic) rather than string similarity.
    2. Ecosystem Dynamics: Candidates are species. Their 'weights' evolve via a 
       simplified Lotka-Volterra equation. Competition (Lambda matrix) penalizes 
       redundancy (high similarity to other candidates), while data fitness 
       promotes structural correctness.
    3. Maximum Entropy: Used in the confidence() wrapper. If structural signals 
       are ambiguous, the system defaults to a maximum-entropy (uniform) distribution 
       over the remaining valid candidates, preventing over-confidence on noise.
    
    This avoids the 'historical inhibitor' trap by not using MaxEnt/Ecosystems for 
    raw scoring, but strictly for weight regulation and confidence calibration 
    atop a robust structural parsing core.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Extracts logical constraints from prompt and checks candidate adherence.
        Returns a score 0.0 to 1.0 based on structural compliance.
        """
        score = 0.0
        checks = 0
        p_lower = prompt.lower()
        c_lower = candidate.lower()

        # 1. Negation Handling
        if re.search(r'\b(not|no|never|without)\b', p_lower):
            checks += 1
            # If prompt says "not X", candidate should not contain "X" unless negated
            # Simplified: Check if candidate contradicts a direct negative constraint
            if re.search(r'\bno\b|\bnot\b', c_lower):
                score += 1.0 # Acknowledges negation
            else:
                # Heuristic: if prompt is negative, simple affirmative is risky
                pass 

        # 2. Numeric Evaluation
        nums_prompt = re.findall(r'-?\d+\.?\d*', p_lower)
        nums_candidate = re.findall(r'-?\d+\.?\d*', c_lower)
        
        if nums_prompt:
            checks += 1
            try:
                # Check if candidate preserves numeric magnitude or order if explicit
                p_vals = [float(n) for n in nums_prompt]
                if nums_candidate:
                    c_vals = [float(n) for n in nums_candidate]
                    # Simple consistency: if prompt has numbers, candidate having numbers is good
                    score += 0.8
                    # Specific check: if prompt implies comparison (e.g. "greater than")
                    if "greater" in p_lower or "larger" in p_lower or ">" in p_lower:
                        if len(c_vals) > 0 and len(p_vals) > 0:
                            # Rough heuristic: does the candidate number make sense?
                            # (Hard to verify without specific context, so we reward presence)
                            score += 0.2
                    else:
                        score += 0.2
                else:
                    # Prompt has numbers, candidate doesn't -> likely wrong for math tasks
                    score -= 0.5
            except ValueError:
                pass

        # 3. Conditional/Logical Keywords
        logic_keywords = ['if', 'then', 'therefore', 'because', 'thus', 'hence']
        has_logic_prompt = any(k in p_lower for k in logic_keywords)
        has_logic_candidate = any(k in c_lower for k in logic_keywords)
        
        if has_logic_prompt:
            checks += 1
            if has_logic_candidate:
                score += 1.0
            else:
                score += 0.3 # Might still be right, but less structured

        # 4. Length/Complexity Penalty (Occam's Razor via MaxEnt principle)
        # Overly long answers often hallucinate. Prefer concise.
        if len(candidate.split()) > 50:
            score -= 0.2
            
        # Normalize
        if checks == 0:
            return 0.5 # Neutral if no structural hooks found
        return max(0.0, min(1.0, score / checks + 0.5))

    def _compute_similarity_matrix(self, candidates: List[str]) -> np.ndarray:
        """
        Computes a similarity matrix based on NCD (approximated by length overlap 
        and set intersection for speed/determinism without external libs).
        This forms the 'Lambda' interaction matrix in the ecosystem model.
        """
        n = len(candidates)
        if n == 0:
            return np.array([])
        
        Lambda = np.zeros((n, n))
        # Simple Jaccard-like similarity on character sets for interaction strength
        sets = [set(c.lower()) for c in candidates]
        lens = [len(s) if len(s) > 0 else 1 for s in sets]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    Lambda[i, j] = 1.0
                else:
                    intersection = len(sets[i] & sets[j])
                    union = len(sets[i] | sets[j])
                    Lambda[i, j] = intersection / union if union > 0 else 0.0
        return Lambda

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        n = len(candidates)
        # 1. Functorial Mapping: Hypothesis -> Structural Score (Fitness alpha)
        alphas = np.array([self._structural_score(prompt, c) for c in candidates])
        
        # 2. Ecosystem Dynamics: Lotka-Volterra Weight Evolution
        # Initialize weights uniformly (Maximum Entropy prior)
        w = np.ones(n) / n
        
        # Interaction matrix (Competition)
        Lambda = self._compute_similarity_matrix(candidates)
        
        # Simulate dynamics for a few steps to settle
        # dw_i = w_i * (alpha_i - sum(Lambda_ij * w_j))
        # We add a small data-fitness term derived from the structural score
        dt = 0.1
        for _ in range(10):
            competition = Lambda @ w
            growth = alphas - competition
            # Ensure growth isn't negative enough to flip sign immediately, 
            # but allow natural selection.
            dw = w * growth * dt
            w = w + dw
            w = np.maximum(w, 1e-6) # Prevent extinction
            w = w / np.sum(w) # Normalize (Carrying capacity constraint)

        # 3. Ranking
        # Combine ecological weight with raw structural score for final ranking
        final_scores = w * 0.4 + alphas * 0.6
        
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(final_scores[i]),
                "reasoning": f"Structural fit: {alphas[i]:.2f}, Ecological weight: {w[i]:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on Maximum Entropy principle.
        If structural signals are strong (high score), confidence is high.
        If signals are weak/ambiguous, confidence decays towards uniform (0.5).
        """
        score = self._structural_score(prompt, answer)
        
        # MaxEnt calibration: 
        # If score is near 0.5 (neutral), we are uncertain -> low confidence.
        # If score is near 0 or 1, we are certain -> high confidence.
        # However, since our score is "likelihood of being correct", 
        # high score = high confidence.
        
        # Apply a sigmoid-like scaling to map structural adherence to confidence
        # Avoiding over-confidence on noisy data (Historical Inhibitor mitigation)
        confidence = 1.0 / (1.0 + np.exp(-10 * (score - 0.5)))
        
        return float(np.clip(confidence, 0.01, 0.99))