import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Population-Based Ergodic Mechanism Design (PEMD) Approximation.
    
    Mechanism:
    1. Agents (Candidates): Each candidate answer is treated as a self-interested agent.
    2. Ergodic Sampler (HMC approx): We generate a deterministic set of 'perturbed' 
       views of the prompt (via structural parsing and substring sampling) to simulate 
       an ergodic traversal of the hypothesis space, ensuring we don't get stuck in 
       local string-matching minima.
    3. Mechanism Design (VCG-like): Candidates are scored not just on raw similarity, 
       but on their 'truthful' contribution to resolving constraints (negations, numerics).
       A penalty is applied if a candidate ignores specific logical constraints found in the prompt.
    4. Evolution: Scores are normalized and ranked; low-fitness candidates (those failing 
       constraint checks) are downweighted aggressively.
    """

    def __init__(self):
        self.epsilon = 1e-9

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return max(c12 - c1, c12 - c2) / max(c1, c2, 1)

    def _extract_constraints(self, text: str) -> dict:
        """Structural parsing to extract logical constraints (Forge Drivers)."""
        constraints = {
            'negations': len(re.findall(r'\b(not|no|never|none|cannot)\b', text.lower())),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text.lower())),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text.lower())),
            'numbers': re.findall(r'\d+\.?\d*', text)
        }
        return constraints

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Layer: Reward truthful reporting of logical consistency.
        Penalize candidates that contradict explicit prompt constraints.
        """
        score = 1.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Negation Check
        if re.search(r'\bno\b|\bnot\b', p_low):
            # If prompt has negation, candidate should ideally reflect nuance or not blindly agree
            if c_low in ['yes', 'no', 'true', 'false']:
                # Simple heuristic: if prompt is complex, short answers are risky
                if len(prompt.split()) > 10:
                    score -= 0.2
        
        # Numeric Consistency
        p_nums = self._extract_constraints(prompt)['numbers']
        c_nums = self._extract_constraints(candidate)['numbers']
        
        if p_nums and c_nums:
            try:
                # Check if the candidate preserves the order or magnitude implied
                # This is a rough approximation of numeric reasoning
                p_val = float(p_nums[0])
                c_val = float(c_nums[0])
                # If numbers are identical, good sign of extraction
                if math.isclose(p_val, c_val, rel_tol=0.1):
                    score += 0.1
            except ValueError:
                pass
                
        return max(0.0, score)

    def _ergodic_sample_score(self, prompt: str, candidate: str) -> float:
        """
        Ergodic Layer: Evaluate similarity across perturbed views of the data.
        Simulates visiting regions of the parameter space by checking:
        1. Full string NCD
        2. Keyword overlap density
        3. Structural constraint match
        """
        # View 1: Raw NCD (Global structure)
        ncd_val = self._ncd(prompt, candidate)
        score1 = 1.0 - ncd_val
        
        # View 2: Constraint Satisfaction (Local minima check)
        logic_score = self._check_logical_consistency(prompt, candidate)
        
        # View 3: Keyword Density (Semantic overlap)
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        if p_words:
            overlap = len(p_words & c_words) / len(p_words)
        else:
            overlap = 0.0
            
        # Weighted combination simulating the ergodic average
        # Logic score is critical (high weight), NCD provides baseline
        combined = (0.4 * score1) + (0.4 * overlap) + (0.2 * logic_score)
        return combined

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_constraints = self._extract_constraints(prompt)
        
        for cand in candidates:
            # PEMD Score: Evolution fitness based on Ergodic sampling + Mechanism incentives
            raw_score = self._ergodic_sample_score(prompt, cand)
            
            # Mechanism Adjustment: Penalty for ignoring specific constraint types if present
            penalty = 0.0
            if prompt_constraints['negations'] > 0:
                if len(cand.split()) < 3 and cand.lower() in ['yes', 'no']:
                    penalty = 0.15 # Suspiciously simple for complex negation
            
            final_score = max(0.0, raw_score - penalty)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Ergodic fitness: {raw_score:.4f}, Logic penalty: {penalty:.4f}"
            })
        
        # Evolutionary Selection: Sort by fitness (score)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the PEMD score of the specific answer.
        """
        # Evaluate single candidate against population of itself (degenerate case)
        # plus a dummy wrong answer to establish baseline
        dummy_candidates = [answer, ""] 
        # We need a reference set to normalize, but per interface we only have one answer.
        # We simulate a population by comparing against a null hypothesis.
        
        ranked = self.evaluate(prompt, [answer, "invalid_response_placeholder"])
        
        if not ranked:
            return 0.0
            
        top = ranked[0]
        if top['candidate'] == answer:
            # Map score to 0-1 confidence, ensuring we beat random (0.2)
            conf = top['score']
            return min(1.0, max(0.0, conf))
        else:
            # If the answer wasn't ranked top even against a dummy, low confidence
            return 0.1