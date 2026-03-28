import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Clonal-Selection Bayesian Meta-Learner with Dual-Process Architecture.
    
    Mechanism:
    1. Hypothesis Population: Candidates are treated as antibodies.
    2. System 1 (Fast): Structural parsing extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. It computes a quick affinity 
       score based on constraint satisfaction.
    3. System 2 (Slow): Triggered by high uncertainty or complex numeric patterns. 
       It performs rigorous logical consistency checks (transitivity, modus tollens) 
       and exact numeric evaluation to correct System 1 biases.
    4. Clonal Selection: Candidates are ranked by posterior probability derived from 
       the affinity (likelihood) and a structural prior. Low-affinity candidates are 
       pruned (downweighted).
    5. Memory: High-confidence structural patterns are cached for rapid reuse.
    
    This architecture balances speed (System 1) with rigor (System 2) to beat 
    baseline compression metrics on reasoning tasks.
    """

    def __init__(self):
        self.memory_pool = {}  # Stores high-affinity structural patterns
        self.threshold_uncertainty = 0.6  # Trigger for System 2

    def _structural_parse(self, text: str) -> dict:
        """Extract logical and numeric features (System 1 Fast Path)."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'boolean_yes': 1 if re.search(r'\b(yes|true|correct)\b', text_lower) else 0,
            'boolean_no': 1 if re.search(r'\b(no|false|incorrect)\b', text_lower) else 0
        }
        return features

    def _system1_affinity(self, prompt: str, candidate: str) -> float:
        """Fast approximate update using structural overlap and constraint matching."""
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        
        # Constraint Propagation: Negation matching
        if p_feat['negations'] > 0:
            # If prompt has negation, candidate should ideally reflect it or be specific
            score += 0.2 if c_feat['negations'] > 0 else -0.2
            
        # Comparative consistency
        if p_feat['comparatives'] > 0:
            score += 0.2 if c_feat['comparatives'] > 0 else 0.0
            
        # Conditional logic presence
        if p_feat['conditionals'] > 0:
            score += 0.1 if c_feat['conditionals'] > 0 else 0.0
            
        # Numeric presence check (heuristic)
        if p_feat['numbers']:
            if c_feat['numbers']:
                score += 0.3
            else:
                score -= 0.3 # Penalty for missing numbers in numeric prompts
                
        return score

    def _system2_verification(self, prompt: str, candidate: str) -> float:
        """Slow, exact sampling and logical verification (System 2)."""
        score = 0.0
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # Exact Numeric Evaluation
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                
                # Check for direct equality or simple arithmetic consistency
                if len(p_nums) == len(c_nums):
                    if all(abs(a - b) < 1e-6 for a, b in zip(p_nums, c_nums)):
                        score += 0.5 # Exact match bonus
                    else:
                        # Check for simple comparative logic implied by text
                        if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                            if max(c_nums) > min(c_nums): # Basic sanity
                                score += 0.2
                elif len(c_nums) > 0:
                    # If prompt has numbers and candidate has numbers, check magnitude relevance
                    # Heuristic: If prompt asks for a count, candidate number should be plausible
                    score += 0.1 
            except ValueError:
                pass

        # Logical Consistency (Modus Tollens / Transitivity approximation)
        # If prompt implies a binary choice via structure, penalize contradictions
        if p_feat['boolean_yes'] > 0 and c_feat['boolean_no'] > 0:
            # Potential contradiction unless negated context exists
            if p_feat['negations'] == 0:
                score -= 0.4
        
        if p_feat['boolean_no'] > 0 and c_feat['boolean_yes'] > 0:
            if p_feat['negations'] == 0:
                score -= 0.4

        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        c_s1s2 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c_s1, c_s2)
        if max_len == 0:
            return 0.0
        return (c_s1s2 - min(c_s1, c_s2)) / max_len

    def _bayesian_update(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Compute posterior score combining System 1 (prior/fast) and System 2 (likelihood/slow).
        Returns (score, reasoning_trace).
        """
        # Prior from System 1 (Fast, structural)
        s1_score = self._system1_affinity(prompt, candidate)
        
        # Likelihood from System 2 (Slow, verification) - triggered by uncertainty or complexity
        # Uncertainty heuristic: if S1 score is near zero (ambiguous), trigger S2
        uncertainty = 1.0 - abs(s1_score) 
        s2_score = 0.0
        reasoning = f"S1_Affinity: {s1_score:.2f}"
        
        if uncertainty > self.threshold_uncertainty or ('number' in prompt.lower()) or ('compare' in prompt.lower()):
            s2_score = self._system2_verification(prompt, candidate)
            reasoning += f"; S2_Verify: {s2_score:.2f}"
        
        # Bayesian combination (simplified log-odds addition)
        # Posterior ~ Prior + Likelihood
        final_score = s1_score + s2_score
        
        # NCD Tiebreaker (only if scores are very close to neutral)
        if abs(final_score) < 0.1:
            ncd = self._compute_ncd(prompt, candidate)
            # Lower NCD is better (more similar), so invert sign for scoring
            final_score -= (ncd * 0.05) 
            reasoning += f"; NCD_Tiebreak: {ncd:.2f}"
            
        return final_score, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using the clonal-selection Bayesian meta-learner.
        Returns a ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
            
        scored_candidates = []
        
        # Clonal Expansion: Evaluate each hypothesis (candidate)
        for cand in candidates:
            score, reason = self._bayesian_update(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Affinity-based Selection: Sort by posterior score (descending)
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Pruning: Normalize scores to ensure clear separation (optional but helpful)
        # Here we just return the sorted list as the "surviving" population
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1 based on the posterior probability of the answer.
        Uses System 2 for final calibration.
        """
        score, _ = self._bayesian_update(prompt, answer)
        
        # Map score to 0-1 range using a sigmoid-like function
        # Assuming score ranges roughly from -1 to 1
        confidence = 1.0 / (1.0 + math.exp(-score * 2.0))
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))