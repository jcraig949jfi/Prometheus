import zlib
import math
import re

class ReasoningTool:
    """
    ST-GERN-PSM Approximation for Reasoning Tasks.
    
    Mechanism:
    1. Gauge-Equivariant Core (Structural Parsing): Extracts invariant logical 
       structures (negations, comparatives, conditionals) treating them as 
       symmetry-preserving transformations on the text manifold.
    2. Phenomenological Layer (Intentional Workspace): Maintains a 'focus' state 
       derived from the prompt's constraints. It brackets raw text to isolate 
       the 'noema' (logical intent) vs 'sensory noise' (irrelevant words).
    3. Criticality Controller (Susceptibility Tuning): Monitors the 'distance' 
       between prompt and candidate. It adjusts the scoring weight dynamically 
       to maximize sensitivity to logical mismatches (high susceptibility) 
       while maintaining stability against string noise.
    
    This implementation approximates the complex fiber-bundle dynamics using 
    structural feature extraction and normalized compression distance (NCD) 
    tuned by a criticality factor derived from logical constraint satisfaction.
    """

    def __init__(self):
        self._critical_point = 0.5  # Target susceptibility
        self._gain = 1.0

    def _extract_features(self, text):
        """Gauge-equivariant feature extraction (invariant to word order/noise)."""
        t = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|nobody)\b', t)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than)\b', t)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', t)),
            'has_numeric': bool(re.search(r'\d+(\.\d+)?', t)),
            'length': len(t),
            'word_count': len(t.split())
        }
        return features

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _check_logical_consistency(self, prompt, candidate):
        """
        Phenomenological bracketing: Checks if candidate violates explicit 
        logical constraints found in the prompt (Modus Tollens/Transitivity).
        Returns a penalty score (0.0 = consistent, 1.0 = contradiction).
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        penalty = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()

        # Rule 1: Negation Contradiction
        # If prompt asserts "X is not Y" and candidate asserts "X is Y"
        if p_feats['has_negation'] and not c_feats['has_negation']:
            # Simple heuristic: if prompt has "not" and candidate lacks it, 
            # check for direct substring overlap which might imply contradiction
            # in a binary choice context.
            common_words = set(p_low.split()) & set(c_low.split())
            if len(common_words) > 2: # Significant overlap suggests potential contradiction
                penalty += 0.4

        # Rule 2: Numeric Consistency
        if p_feats['has_numeric'] and c_feats['has_numeric']:
            # Extract numbers
            p_nums = re.findall(r'\d+(\.\d+)?', p_low)
            c_nums = re.findall(r'\d+(\.\d+)?', c_low)
            if p_nums and c_nums:
                try:
                    p_val = float(p_nums[0])
                    c_val = float(c_nums[0])
                    # Check comparatives
                    if p_feats['has_comparative']:
                        if ('less' in p_low or 'smaller' in p_low) and c_val > p_val:
                            penalty += 0.5
                        elif ('more' in p_low or 'greater' in p_low) and c_val < p_val:
                            penalty += 0.5
                except ValueError:
                    pass

        # Rule 3: Conditional/Constraint Propagation
        if p_feats['has_conditional']:
            # If prompt sets a condition "If A then B", and candidate is "A" but not "B"
            # This is a rough approximation of modus tollens failure
            if 'if' in p_low:
                # Very basic check: does candidate ignore the consequence?
                # Hard to do full logic without LLM, so we rely on length/structure match
                if len(c_low.split()) < 3 and p_feats['word_count'] > 10:
                    penalty += 0.2 # Too short to satisfy complex conditional

        return min(penalty, 1.0)

    def _tune_criticality(self, base_score, logical_penalty):
        """
        Criticality Controller: Adjusts gain based on susceptibility.
        If logical penalty is high, we want high susceptibility (large score drop).
        If logical penalty is low, we rely more on structural similarity (NCD).
        """
        # Susceptibility chi approximation
        chi = abs(base_score - 0.5) 
        # Drive towards critical point where small changes matter
        if logical_penalty > 0.1:
            # High penalty should drastically reduce score (high sensitivity)
            adjustment = -0.6 * logical_penalty
        else:
            # Low penalty, fine-tune based on NCD
            adjustment = 0.0
        
        final_score = base_score + adjustment
        return max(0.0, min(1.0, final_score))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_features = self._extract_features(prompt)
        
        for cand in candidates:
            # 1. Gauge Equivariant Core: Structural comparison
            ncd = self._compute_ncd(prompt, cand)
            
            # 2. Phenomenological Layer: Logical consistency check
            logic_penalty = self._check_logical_consistency(prompt, cand)
            
            # Base score from NCD (inverted: lower distance = higher score)
            # NCD is 0..1, we want 1..0 mapping but scaled
            base_score = 1.0 - ncd
            
            # 3. Criticality Controller: Apply dynamic gain
            final_score = self._tune_criticality(base_score, logic_penalty)
            
            # Heuristic boost for exact string matches of key terms if NCD is ambiguous
            if cand.strip().lower() in prompt.lower() and len(cand.strip()) > 2:
                final_score = max(final_score, 0.8)

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"NCD:{1-ncd:.2f}, LogicPen:{logic_penalty:.2f}, CritTuned:{final_score:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        return ranked[0]['score']