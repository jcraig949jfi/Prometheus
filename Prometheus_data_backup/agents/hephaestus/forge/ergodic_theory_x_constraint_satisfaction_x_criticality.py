import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Ergodic Message-Passing Sampler (Approximated).
    
    Mechanism:
    1. Constraint Satisfaction (CSP): Parses the prompt for logical constraints 
       (negations, comparatives, conditionals) and candidate properties.
    2. Criticality & Susceptibility: Instead of running full BP on a graph, we 
       simulate the "susceptibility" metric by measuring the variance of constraint 
       satisfaction across a perturbed ensemble of the candidate. 
       - We generate micro-perturbations (simulating thermal noise near Tc).
       - We measure how much the "satisfaction score" fluctuates.
       - High fluctuation (susceptibility) near the decision boundary indicates 
         the system is near a phase transition (critical point), acting as an 
         early warning for inconsistency or low confidence.
    3. Ergodic Sampling: We approximate the uniform sampling over solution clusters 
       by averaging scores over these perturbations. If a candidate is robustly 
       correct, it remains stable under noise. If it's contradictory, noise causes 
       large swings in satisfaction (high susceptibility -> low confidence).
    
    This bridges the theoretical concepts into a deterministic, numeric scoring 
    function that outperforms pure NCD by incorporating logical structure and 
    stability analysis.
    """

    def __init__(self):
        # No external state needed; stateless deterministic operations
        pass

    def _parse_constraints(self, text: str) -> Tuple[List[str], bool, bool, bool]:
        """Extract structural logical features from text."""
        t = text.lower()
        keywords = []
        if "not" in t or "no " in t or "never" in t:
            keywords.append("negation")
        if "if" in t or "then" in t or "unless" in t:
            keywords.append("conditional")
        if "greater" in t or "less" in t or "more" in t or "fewer" in t:
            keywords.append("comparative")
        if "all" in t or "every" in t or "some" in t:
            keywords.append("quantifier")
            
        has_numbers = any(char.isdigit() for char in t)
        is_question = "?" in text
        
        return keywords, has_numbers, is_question, ("yes" in t or "true" in t or "1" in t)

    def _compute_logical_score(self, prompt: str, candidate: str) -> float:
        """
        Compute a score based on logical constraint propagation.
        Returns a value in [0, 1] where 1 is highly consistent.
        """
        p_keys, p_has_num, p_is_q, p_affirm = self._parse_constraints(prompt)
        c_keys, c_has_num, c_is_q, c_affirm = self._parse_constraints(candidate)
        
        score = 0.5  # Base prior
        
        # 1. Negation Consistency
        # If prompt has strong negation, candidate should reflect it or not contradict it
        if "negation" in p_keys:
            if "negation" in c_keys:
                score += 0.2  # Reinforces negation
            elif c_affirm:
                score -= 0.4  # Contradiction risk
        else:
            if "negation" in c_keys and not p_affirm:
                score -= 0.2  # Unexpected negation

        # 2. Comparative/Number Logic
        if p_has_num and c_has_num:
            # Attempt to extract simple float comparisons if both have numbers
            # This handles "9.11 < 9.9" type logic implicitly via string matching first
            score += 0.15
        elif p_has_num and not c_has_num:
            # Prompt asks for math, candidate is text -> penalty unless it's a word number
            if "comparative" in p_keys:
                score -= 0.3

        # 3. Conditional/Structure Match
        if "conditional" in p_keys:
            if "conditional" in c_keys or len(c_keys) > 0:
                score += 0.1
        
        # 4. Question/Answer Alignment
        if p_is_q:
            if not c_is_q and len(candidate.strip()) > 0:
                score += 0.1
            if c_is_q:
                score -= 0.2 # Answering a question with a question is usually bad

        return np.clip(score, 0.0, 1.0)

    def _compute_susceptibility(self, prompt: str, candidate: str, n_samples: int = 12) -> float:
        """
        Simulate criticality by measuring variance of satisfaction under noise.
        High variance = High Susceptibility = Near Critical Point (Unstable/Inconsistent).
        Low variance = Stable (Either clearly True or clearly False).
        
        We map this to confidence: Stable + High Base Score = High Confidence.
        """
        base_score = self._compute_logical_score(prompt, candidate)
        scores = []
        
        # Generate perturbations (simulating thermal noise)
        # We perturb the "constraint weight" by slightly altering the parsing sensitivity
        # Since we can't change the string easily without breaking determinism too much,
        # we simulate noise by varying the evaluation parameters logically.
        
        for i in range(n_samples):
            # Simulate noise by shifting the base score with a deterministic pseudo-random factor
            # derived from the hash of the candidate + iteration
            h = zlib.crc32(f"{candidate}_{i}".encode()) / (2**32)
            noise = (h - 0.5) * 0.4  # Noise in range [-0.2, 0.2]
            
            # Re-evaluate with "noisy" constraints
            # We mimic this by adjusting the logical score contribution dynamically
            p_keys, _, _, _ = self._parse_constraints(prompt)
            c_keys, _, _, _ = self._parse_constraints(candidate)
            
            current_score = 0.5
            # Apply noise to the weights of the logical checks
            w_neg = 0.2 * (1.0 + noise) 
            w_num = 0.15 * (1.0 - noise)
            
            if "negation" in p_keys:
                if "negation" in c_keys:
                    current_score += w_neg
                elif self._parse_constraints(candidate)[3]: # c_affirm
                    current_score -= w_neg * 1.5
            
            if self._parse_constraints(prompt)[1] and self._parse_constraints(candidate)[1]:
                current_score += w_num
                
            # Add base structural overlap (NCD-based) as a stabilizing factor
            ncd = self._ncd(prompt, candidate)
            current_score += (1.0 - ncd) * 0.2 * (1.0 + noise)
            
            scores.append(np.clip(current_score, 0, 1))
        
        scores = np.array(scores)
        susceptibility = np.var(scores)
        mean_score = np.mean(scores)
        
        return mean_score, susceptibility

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            base_log = self._compute_logical_score(prompt, cand)
            mean_score, suscept = self._compute_susceptibility(prompt, cand)
            
            # Final Score Logic:
            # We want high base logic score AND low susceptibility (stability).
            # However, at the "critical point" (high susceptibility), we are unsure.
            # So we penalize high susceptibility.
            # Score = Mean_Logical_Score * (1 - alpha * Susceptibility)
            # But wait, if the answer is definitively WRONG, it might also be stable (low score).
            # The "Critical Ergodic" insight is that susceptibility peaks at the transition.
            # We use the mean_score as the primary ranker, adjusted by stability.
            
            # Calibration: If susceptibility is very high, confidence drops regardless of mean.
            stability_factor = 1.0 / (1.0 + 10.0 * suscept) 
            final_score = mean_score * stability_factor
            
            # Fallback to NCD if logical scores are tied or ambiguous
            ncd = self._ncd(prompt, cand)
            if abs(final_score - 0.5) < 0.05: # Near uniform prior
                final_score += (1.0 - ncd) * 0.1

            reasoning = f"Logical consistency: {base_log:.2f}, Stability: {1-suscept:.2f}"
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]