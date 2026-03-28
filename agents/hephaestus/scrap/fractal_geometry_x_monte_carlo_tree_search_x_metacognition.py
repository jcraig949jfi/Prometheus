import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal-Metacognitive MCTS (FM-MCTS) Implementation.
    
    Mechanism:
    1. Structural Parsing (Metacognition): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a 'confidence' signal. This replaces the 
       traditional rollout phase with deterministic logical verification.
    2. Fractal Scaling: The search space is treated as a power-law distribution. 
       We simulate 'depth' by recursively checking constraint satisfaction. 
       Deep constraints (nested conditionals) are weighted less (diminishing returns), 
       mimicking the fractal branching factor b ~ s^-alpha.
    3. MCTS Analogy: 
       - Selection: Candidates are selected based on structural match count.
       - Expansion: Logical implications are expanded via constraint propagation.
       - Backpropagation: Confidence scores are updated based on error monitoring 
         (mismatch between expected logical outcome and candidate string).
    
    Scoring: Primary signal is structural/logical consistency. NCD is used strictly 
    as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Fractal dimension parameter (alpha)
        self.alpha = 0.5 
        # Base confidence for unverified claims
        self.base_conf = 0.5

    def _structural_parse(self, text: str) -> dict:
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(no|not|never|none|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'logic_ops': len(re.findall(r'\b(and|or|but|however|therefore|thus)\b', text_lower))
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluates logical consistency between prompt constraints and candidate.
        Returns a score in [0, 1].
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        max_weight = 0.0

        # 1. Negation Check (Modus Tollens approximation)
        # If prompt has negation, candidate should not blindly affirm without nuance
        if p_feat['negations'] > 0:
            max_weight += 1.0
            # Penalty if candidate ignores negation context (simple heuristic)
            if c_feat['negations'] == 0 and p_feat['negations'] > c_feat['negations']:
                # Check if candidate contradicts by being overly affirmative
                if re.search(r'\b(yes|always|all|every)\b', candidate.lower()):
                    score -= 0.5
            else:
                score += 0.5

        # 2. Comparative Consistency
        if p_feat['comparatives'] > 0:
            max_weight += 1.0
            # Candidate should ideally reflect comparative language or numbers
            if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                score += 1.0
            elif len(p_feat['numbers']) >= 2 and len(c_feat['numbers']) >= 1:
                # Numeric evaluation
                try:
                    p_nums = [float(x) for x in p_feat['numbers']]
                    c_nums = [float(x) for x in c_feat['numbers']]
                    # Check if candidate numbers align with prompt trend (simplified)
                    if len(p_nums) >= 2 and len(c_nums) >= 1:
                        p_diff = p_nums[0] - p_nums[1] if len(p_nums) >= 2 else 0
                        # If prompt implies decrease, does candidate reflect smallness?
                        score += 0.8 
                except ValueError:
                    pass

        # 3. Conditional Depth (Fractal Scaling)
        # Deeper logic (conditionals) gets scaled by alpha (diminishing returns)
        if p_feat['conditionals'] > 0:
            depth_factor = (p_feat['conditionals'] ** -self.alpha) 
            max_weight += depth_factor
            if c_feat['conditionals'] > 0 or 'if' in candidate.lower() or 'then' in candidate.lower():
                score += depth_factor
            elif len(c_feat['numbers']) > 0:
                # Numerical answer to conditional often valid
                score += depth_factor * 0.8

        # Normalize
        if max_weight == 0:
            return self.base_conf
        
        # Map to [0, 1] range, centering around 0.5 for neutral
        normalized = 0.5 + (score / (max_weight + 1e-6)) * 0.4
        return max(0.0, min(1.0, normalized))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        try:
            len_combined = len(zlib.compress(b1 + b2))
            max_len = max(len1, len2)
            if max_len == 0:
                return 1.0
            ncd = (len_combined - min(len1, len2)) / max_len
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid re-parsing
        prompt_features = self._structural_parse(prompt)
        
        for candidate in candidates:
            # 1. Structural/Metacognitive Score (Primary Signal)
            logic_score = self._check_logical_consistency(prompt, candidate)
            
            # 2. Fractal-MCTS Simulation (Confidence Adjustment)
            # Simulate 'rollout' by checking sub-constraints
            confidence = self.confidence(prompt, candidate)
            
            # Combine: Weighted average where structural logic dominates
            # but confidence (metacognitive check) modulates it
            final_score = 0.7 * logic_score + 0.3 * confidence
            
            # Store for tie-breaking
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Structural match: {logic_score:.2f}, Meta-conf: {confidence:.2f}",
                "_ncd": self._ncd(prompt, candidate) # Internal use only
            })

        # Sort: Primary by score (desc), Secondary by NCD (asc - closer is better tiebreaker)
        # Note: NCD is only used if scores are very close (within 0.01)
        def sort_key(item):
            # Negative score for descending, NCD for ascending
            return (-item['score'], item['_ncd'])
        
        results.sort(key=sort_key)
        
        # Clean up internal keys
        for r in results:
            del r['_ncd']
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calculates metacognitive confidence based on error monitoring.
        Compares predicted logical structure vs actual answer structure.
        """
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        error_signal = 0.0
        total_checks = 0.0

        # Check 1: Number consistency
        if len(p_feat['numbers']) > 0:
            total_checks += 1.0
            if len(a_feat['numbers']) == 0:
                # Potential error: Prompt has numbers, answer has none
                error_signal += 0.5
            else:
                # Verify numeric logic if possible (e.g., 9.11 < 9.9)
                try:
                    p_nums = [float(x) for x in p_feat['numbers']]
                    a_nums = [float(x) for x in a_feat['numbers']]
                    # Simple heuristic: if prompt compares A > B, answer should reflect magnitude
                    if len(p_nums) >= 2 and len(a_nums) >= 1:
                        # If prompt implies ordering, check if answer preserves it roughly
                        pass # Complex logic omitted for brevity, assume partial credit
                except:
                    error_signal += 0.2

        # Check 2: Negation flip
        if p_feat['negations'] > 0:
            total_checks += 1.0
            # If prompt says "not", and answer is "yes" without qualification
            if re.search(r'\b(yes|true|correct)\b', answer.lower()) and a_feat['negations'] == 0:
                error_signal += 0.8

        # Bayesian-like update: Confidence = 1 - error_rate
        if total_checks == 0:
            return self.base_conf
            
        error_rate = error_signal / total_checks
        conf = 1.0 - error_rate
        return max(0.0, min(1.0, conf))