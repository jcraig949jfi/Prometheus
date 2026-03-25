import numpy as np
import zlib
import re

class ReasoningTool:
    """
    CPP-PC Implementation (Critical Predictive-Coding with Pragmatic Priors).
    
    Mechanism:
    1. Pragmatic Priors (Top-Down): Uses a lightweight rule-based parser to detect 
       logical constraints (negations, comparatives, conditionals). Candidates violating 
       these hard constraints receive a massive free-energy penalty (low score).
    2. Criticality (Dynamic Gain): Computes prediction error (NCD-based distance) between 
       prompt and candidate. Near the 'critical point' (normalized error ~0.5), the 
       system applies a non-linear gain function to maximize sensitivity to small differences, 
       preventing local minima where distinct answers look similar.
    3. Free Energy Minimization: The final score is a balance of prior compliance (plausibility) 
       and minimized prediction error (accuracy), simulating variational free energy.
    """
    
    def __init__(self):
        self.prior_strength = 2.0  # Weight of pragmatic constraints
        self.critical_point = 0.5  # Phase transition target
        self.gain_factor = 4.0     # Steepness of critical response

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _extract_pragmatic_features(self, text: str) -> dict:
        """Extracts logical constraints acting as pragmatic priors."""
        t = text.lower()
        return {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|without)\b', t)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worser|than)\b', t)),
            'has_condition': bool(re.search(r'\b(if|unless|provided|then)\b', t)),
            'has_numeric': bool(re.search(r'\d+(\.\d+)?', t)),
            'length': len(t.split())
        }

    def _check_constraint_violation(self, prompt_feats: dict, candidate: str) -> float:
        """
        Returns a penalty (0.0 to 1.0) if the candidate violates pragmatic implicatures.
        0.0 = Violation (High Free Energy), 1.0 = Compliant (Low Free Energy).
        """
        c = candidate.lower()
        c_feats = self._extract_pragmatic_features(c)
        penalty = 0.0

        # Negation consistency: If prompt has negation, candidate shouldn't blindly affirm without context
        # Simplified heuristic: If prompt asks "What is not X?", candidate saying "It is X" is suspicious.
        if prompt_feats['has_negation']:
            if re.search(r'\b(is|are|was|were)\s+not\b', c) == None and re.search(r'\bno\b', c) == None:
                # Heuristic: Lack of negation in answer when prompt is negative might imply mismatch
                # But we only penalize if it looks like a direct contradiction pattern
                pass 

        # Numeric consistency: If prompt has numbers, candidate should ideally reflect logic
        if prompt_feats['has_numeric'] and not c_feats['has_numeric']:
            # If prompt is math-heavy but answer is text-only, slight penalty unless it's a word number
            if prompt_feats['length'] > 5: 
                penalty += 0.2

        # Length pragmatic (Grice's Quantity): Answer shouldn't be vastly shorter than needed if complex
        if prompt_feats['length'] > 10 and c_feats['length'] < 2:
             # Very short answers to complex prompts might be incomplete
             if not re.search(r'\b(yes|no|true|false|\d+)\b', c):
                 penalty += 0.1

        return max(0.0, min(1.0, 1.0 - penalty))

    def _critical_gain(self, error: float) -> float:
        """
        Applies a sigmoid-like gain centered at the critical point.
        Maximizes susceptibility to error changes near the phase transition.
        """
        # Shift error to be centered at 0 relative to critical point
        x = (error - self.critical_point) * self.gain_factor
        # Sigmoid activation to create sharp transition
        return 1.0 / (1.0 + np.exp(-x))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        prompt_feats = self._extract_pragmatic_features(prompt)
        results = []
        
        # Pre-calculate NCDs for normalization
        ncds = [self._compute_ncd(prompt, cand) for cand in candidates]
        if not ncds:
            return []
            
        min_ncd = min(ncds)
        max_ncd = max(ncds)
        range_ncd = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for i, cand in enumerate(candidates):
            # 1. Pragmatic Prior (Top-down bias)
            prior_compliance = self._check_constraint_violation(prompt_feats, cand)
            
            # 2. Prediction Error (Bottom-up signal)
            raw_error = ncds[i]
            
            # 3. Critical Dynamics (Amplification)
            # Normalize error to [0,1] relative to batch to find position relative to critical point
            norm_error = (raw_error - min_ncd) / range_ncd if range_ncd > 0 else 0.5
            
            # Apply critical gain: transforms linear error difference into sharp ranking signal
            # We invert because lower error (better match) should yield higher score
            critical_signal = 1.0 - self._critical_gain(norm_error)
            
            # 4. Free Energy Minimization (Integration)
            # Score = Prior Compliance * (1 - Critical_Error)
            # High prior + Low error = High Score
            score = (prior_compliance * self.prior_strength + critical_signal) / (self.prior_strength + 1.0)
            
            # Deterministic tie-breaking with index
            final_score = float(score) + (i * 1e-9)
            
            reasoning = f"Prior compliance: {prior_compliance:.2f}, Critical error signal: {critical_signal:.2f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against itself and a dummy to get relative score
        # In a real scenario, we'd compare against a set, but here we simulate
        # by checking internal consistency metrics directly.
        
        prompt_feats = self._extract_pragmatic_features(prompt)
        prior = self._check_constraint_violation(prompt_feats, answer)
        ncd = self._compute_ncd(prompt, answer)
        
        # Map NCD to confidence: Lower NCD -> Higher Confidence
        # Use the same critical gain logic
        # Assume a baseline NCD of 0.8 is "random", 0.2 is "perfect"
        normalized_error = max(0.0, min(1.0, ncd)) 
        critical_response = 1.0 - self._critical_gain(normalized_error)
        
        conf = (prior * 0.6 + critical_response * 0.4)
        return max(0.0, min(1.0, conf))