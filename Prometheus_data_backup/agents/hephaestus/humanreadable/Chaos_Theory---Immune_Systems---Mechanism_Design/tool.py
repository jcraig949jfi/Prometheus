import zlib
import re
import math

class ReasoningTool:
    """
    CI-MD Reasoning Tool: Chaotic Immune-inspired Mechanism Design.
    
    Core Mechanism:
    1. Chaos Theory (Evaluate Core): Uses logistic map (r=3.9) to generate deterministic
       perturbation vectors. These drive the exploration of candidate features, ensuring
       ergodic coverage of the hypothesis space without stochastic noise.
    2. Mechanism Design (Evaluate Core): Implements a VCG-style incentive layer. Candidates
       are scored based on structural alignment (negations, comparatives, numerics). The
       final score adjusts for "truthful reporting" by penalizing candidates that deviate
       from the structural baseline established by the chaotic probe.
    3. Immune System (Confidence Wrapper): Restricted role per causal analysis. Used only
       in confidence() to measure "affinity" (similarity) between the prompt's structural
       signature and the answer, acting as a safety filter rather than a primary scorer.
    
    This combination leverages the strong forge success of Chaos and Mechanism Design
    while containing the "Immune" inhibitor to a supportive, non-decision-making role.
    """

    def __init__(self):
        self.r = 3.9  # Logistic map parameter for chaos
        self.x = 0.5  # Initial seed for chaotic sequence

    def _chaotic_step(self):
        """Generates next value in logistic map sequence."""
        self.x = self.r * self.x * (1 - self.x)
        return self.x

    def _structural_score(self, text):
        """Extracts structural features: negations, comparatives, numerics."""
        text_lower = text.lower()
        score = 0.0
        
        # Negation detection (Modus Tollens support)
        negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        for word in negations:
            if re.search(r'\b' + word + r'\b', text_lower):
                score += 0.5
        
        # Comparative detection
        comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        for word in comparatives:
            if word in text_lower:
                score += 0.8
                
        # Numeric evaluation capability check
        numbers = re.findall(r"-?\d+\.?\d*", text)
        if numbers:
            score += 1.0 * len(numbers)
            
        return score

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(s1)
        len2 = len(s2)
        if len1 == 0 and len2 == 0:
            return 0.0
        
        try:
            c1 = len(zlib.compress(s1.encode('utf-8')))
            c2 = len(zlib.compress(s2.encode('utf-8')))
            c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
            
            if min(c1, c2) == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """
        Evaluates candidates using Chaotic Exploration and Mechanism Design incentives.
        """
        if not candidates:
            return []

        prompt_struct = self._structural_score(prompt)
        results = []
        
        # Reset chaos state for deterministic run per prompt
        self.x = 0.5 
        
        # Phase 1: Chaotic Exploration & Feature Perturbation
        # Generate chaotic weights for feature importance based on prompt length
        chaos_weights = []
        for _ in range(len(candidates)):
            chaos_weights.append(self._chaotic_step())

        # Phase 2: Mechanism Design (VCG-style incentive)
        # We calculate a "social choice" score based on structural alignment.
        # The "payment" is the improvement in structural fit relative to the chaotic baseline.
        
        base_structural_scores = []
        for i, cand in enumerate(candidates):
            s_score = self._structural_score(cand)
            # Inject chaotic perturbation: small random-like shift based on logistic map
            # This prevents local minima where string length alone dictates score
            perturbation = (chaos_weights[i] - 0.5) * 0.1 
            base_structural_scores.append(s_score + perturbation)

        # Normalize scores to [0, 1] range for comparison
        max_bs = max(base_structural_scores) if base_structural_scores else 1
        min_bs = min(base_structural_scores) if base_structural_scores else 0
        range_bs = max_bs - min_bs if max_bs != min_bs else 1.0

        for i, cand in enumerate(candidates):
            # Structural alignment with prompt
            cand_struct = self._structural_score(cand)
            
            # Mechanism Design: Truthfulness penalty
            # If the candidate has high structural complexity but low alignment with prompt
            # structural hints, it is penalized (simulating VCG truth-telling incentive)
            alignment = 0.0
            if prompt_struct > 0:
                # Check for shared structural markers
                p_has_num = bool(re.search(r"\d", prompt))
                c_has_num = bool(re.search(r"\d", cand))
                if p_has_num == c_has_num:
                    alignment += 0.5
                
                p_has_neg = bool(re.search(r"\b(not|no|never)\b", prompt.lower()))
                c_has_neg = bool(re.search(r"\b(not|no|never)\b", cand.lower()))
                if p_has_neg == c_has_neg:
                    alignment += 0.5
            
            # Chaotic-Mechanism Score
            normalized_base = (base_structural_scores[i] - min_bs) / range_bs
            final_score = (0.6 * normalized_base) + (0.4 * alignment)
            
            # NCD Tiebreaker (only if scores are very close or structural signal weak)
            ncd_val = self._ncd(prompt, cand)
            if abs(final_score - 0.5) < 0.01: 
                final_score -= (ncd_val * 0.01) # Lower NCD (more similar) is better

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Chaotic-Mechanism Score: {final_score:.4f}. Structural alignment: {alignment:.2f}. NCD tiebreaker applied if needed."
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calculates confidence using Immune System analogy (Affinity Maturation).
        Restricted role: Measures affinity between prompt structure and answer structure.
        Returns 0-1.
        """
        # Immune Layer: Affinity Measurement
        # High affinity = high structural match (e.g., if prompt asks for number, answer has number)
        p_struct = self._structural_score(prompt)
        a_struct = self._structural_score(answer)
        
        # Affinity decay based on structural difference
        struct_diff = abs(p_struct - a_struct)
        affinity = 1.0 / (1.0 + struct_diff)
        
        # Secondary check: NCD (Compression similarity)
        ncd_val = self._ncd(prompt, answer)
        
        # Combined confidence: Weighted towards structural affinity (Immune) 
        # but grounded by compression similarity
        conf = (0.7 * affinity) + (0.3 * (1.0 - ncd_val))
        
        return min(1.0, max(0.0, conf))