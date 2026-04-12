import math
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Self-Tuning Evolutionary Bayesian Critical Learner (EBCL) Approximation.
    
    Mechanism:
    1. Bayesian Inference: Candidates are treated as hypotheses. Likelihood is estimated
       via structural constraint satisfaction (negation, numeric logic) and NCD-based
       semantic similarity to a synthesized "ideal" response pattern.
    2. Evolution: The population of candidates undergoes a selection phase where 
       'fitness' is a weighted sum of structural validity and semantic coherence.
    3. Criticality: A global 'susceptibility' metric (variance of scores) modulates
       the exploration/exploitation balance. High variance (near criticality) boosts
       diverse but structurally valid candidates; low variance sharpens focus on
       the highest likelihood candidate.
       
    This implementation approximates the theoretical loop using deterministic
    structural parsing and compression-based metrics to ensure robustness without
    external dependencies.
    """

    def __init__(self):
        self._epsilon = 1e-9

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text for numeric reasoning."""
        nums = []
        current = ""
        has_dot = False
        for char in text:
            if char.isdigit() or (char == '.' and not has_dot):
                current += char
                if char == '.':
                    has_dot = True
            else:
                if current:
                    try:
                        nums.append(float(current))
                    except ValueError:
                        pass
                    current = ""
                    has_dot = False
        if current:
            try:
                nums.append(float(current))
            except ValueError:
                pass
        return nums

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Evaluate structural constraints: negations, comparatives, and numeric logic.
        Returns a score between 0.0 and 1.0.
        """
        score = 0.5  # Base prior
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        negations = ['no', 'not', 'never', 'none', 'cannot']
        p_has_neg = any(n in p_lower for n in negations)
        c_has_neg = any(n in c_lower for n in negations)
        
        if p_has_neg == c_has_neg:
            score += 0.2
        else:
            score -= 0.2

        # 2. Numeric Logic (Constraint Propagation)
        p_nums = self._extract_numbers(p_lower)
        c_nums = self._extract_numbers(c_lower)
        
        if p_nums and c_nums:
            # If prompt has numbers, check if candidate respects simple ordering implied
            # or simply matches magnitude if only one exists.
            if len(p_nums) == 1 and len(c_nums) == 1:
                # Heuristic: If prompt asks "which is larger", candidate should be the larger one?
                # Without full NLP, we check if the candidate number appears in prompt or is derived.
                # Simple boost if numbers match exactly (exact answer extraction)
                if abs(p_nums[0] - c_nums[0]) < self._epsilon:
                    score += 0.3
                elif c_nums[0] > p_nums[0] and "larger" in p_lower:
                    score += 0.1
                elif c_nums[0] < p_nums[0] and "smaller" in p_lower:
                    score += 0.1
        
        # 3. Length/Complexity Penalty (Occam's Razor)
        if len(c_lower) < 2:
            score -= 0.1 # Too short to be reasoned
        
        return max(0.0, min(1.0, score))

    def _bayesian_likelihood(self, prompt: str, candidate: str) -> float:
        """
        Estimate likelihood based on semantic similarity (NCD) and structural fit.
        """
        struct_score = self._structural_score(prompt, candidate)
        
        # Semantic coherence via NCD relative to prompt
        # We want low NCD (high similarity) but penalize exact repetition (echo)
        ncd_val = self._ncd(prompt, candidate)
        
        # Transform NCD to likelihood: 1.0 (identical) -> 0.0 (very different)
        # But exact echo is bad for reasoning. 
        if candidate.strip() == prompt.strip():
            semantic_score = 0.1 
        else:
            # Optimal zone is moderate similarity (answering the prompt)
            # NCD of 0.4-0.7 is often good for Q&A pairs
            if 0.3 < ncd_val < 0.8:
                semantic_score = 0.8
            elif ncd_val < 0.3:
                semantic_score = 0.4 # Too similar (echo)
            else:
                semantic_score = 0.3 # Too different
        
        # Combine: Structural score is the strong prior, semantic is the data likelihood
        # P(H|E) ~ P(E|H) * P(H)
        likelihood = (0.6 * semantic_score) + (0.4 * struct_score)
        return min(1.0, likelihood)

    def _compute_susceptibility(self, scores: List[float]) -> float:
        """
        Calculate population susceptibility (variance) to determine criticality.
        High variance = Near critical point (diverging responses).
        """
        if not scores:
            return 0.0
        n = len(scores)
        mean = sum(scores) / n
        variance = sum((x - mean) ** 2 for x in scores) / n
        return variance

    def _evolutionary_fitness(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """
        Run the EBCL loop:
        1. Calculate initial Bayesian scores for all candidates.
        2. Compute susceptibility (variance) of the population.
        3. Modulate scores based on criticality (Exploration vs Exploitation).
        """
        if not candidates:
            return []
        
        # Step 1: Initial Bayesian Scoring
        raw_scores = []
        for cand in candidates:
            score = self._bayesian_likelihood(prompt, cand)
            raw_scores.append(score)
        
        # Step 2: Criticality Check
        susceptibility = self._compute_susceptibility(raw_scores)
        
        # Criticality Modulation Factor
        # If susceptibility is high (near critical), we are in a diverse regime.
        # We boost candidates that are structurally sound but maybe less semantically obvious (Exploration).
        # If susceptibility is low (ordered), we sharpen the highest scorer (Exploitation).
        
        tuned_scores = []
        for i, score in enumerate(raw_scores):
            struct = self._structural_score(prompt, candidates[i])
            
            if susceptibility > 0.05:
                # High susceptibility: Favor structural integrity + diversity
                # Add a small bonus to candidates with high structural score but moderate raw score
                if struct > 0.7 and score < 0.8:
                    score += 0.1 * susceptibility 
            else:
                # Low susceptibility: Sharpen the peak (Exploitation)
                # Apply a non-linear boost to the top scores
                score = score ** 1.2 
            
            tuned_scores.append(max(0.0, min(1.0, score)))

        # Step 3: Selection & Ranking
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": tuned_scores[i],
                "reasoning": f"EBCL Score: {tuned_scores[i]:.4f} (Susceptibility: {susceptibility:.4f})"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
        # Ensure deterministic output for ties by stable sort or secondary key if needed,
        # though Python's sort is stable.
        return self._evolutionary_fitness(prompt, candidates)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the internal Bayesian likelihood as a direct proxy for confidence,
        calibrated by structural checks.
        """
        score = self._bayesian_likelihood(prompt, answer)
        
        # Calibration: If structural check fails significantly, cap confidence
        struct = self._structural_score(prompt, answer)
        if struct < 0.4:
            score *= 0.5
            
        return max(0.0, min(1.0, score))