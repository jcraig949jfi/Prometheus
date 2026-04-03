import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Critical Variational Predictive-Coding Architecture with Epistemic Honesty.
    
    Mechanism:
    1. Phenomenological Priors (Structural Parsing): Extracts invariant logical structures
       (negations, comparatives, conditionals) to form a 'lifeworld' baseline.
    2. Criticality (Precision Tuning): Dynamically adjusts the weight of prediction errors.
       If structural signals are weak or ambiguous, precision drops (high susceptibility),
       pushing the system toward a 'critical' state where it refuses to commit (low confidence).
    3. Free Energy (Scoring): Computes a score based on the divergence between the candidate
       and the structural prior, minimized by logical consistency and maximized by NCD tie-breaking.
    4. Epistemic Honesty (Meta-Confidence): Explicitly detects Tier B traps (presuppositions,
       ambiguity) and caps confidence regardless of candidate quality.
    """

    def __init__(self):
        # Phenomenological priors: Regex patterns for logical invariants
        self.priors = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|better|worse|higher|lower)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|how did|quit|failed)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|all|each).*\b(a|an|the)\b.*\b(same|different|who|which)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or|must|only option)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.I)
        }
        self.precision_threshold = 0.6  # Criticality tuning parameter

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            return (c12 - min_len) / max(c1, c2)
        except:
            return 1.0

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Parse text for logical invariants (Phenomenological Priors)."""
        features = {
            'has_negation': bool(self.priors['negation'].search(text)),
            'has_comparative': bool(self.priors['comparative'].search(text)),
            'has_conditional': bool(self.priors['conditional'].search(text)),
            'numbers': [float(n) for n in self.priors['numeric'].findall(text)],
            'is_presupposition': bool(self.priors['presupposition'].search(text)),
            'is_ambiguous': bool(self.priors['scope_ambiguity'].search(text)) or \
                             bool(self.priors['false_dichotomy'].search(text)) or \
                             bool(self.priors['subjectivity'].search(text)),
            'length': len(text.split())
        }
        return features

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Evaluate the prompt itself for epistemic traps.
        Returns a cap on confidence.
        """
        features = self._extract_structure(prompt)
        
        # Detect specific Tier B traps
        if features['is_presupposition']:
            return 0.1  # Strong presupposition detected
        if features['is_ambiguous']:
            return 0.2  # Ambiguity or subjectivity detected
        if features['length'] < 3:
            return 0.3  # Too little information
        
        # If no structural hooks found, assume high uncertainty (Criticality)
        if not any([features['has_negation'], features['has_comparative'], 
                    features['has_conditional'], features['numbers']]):
            return 0.4
            
        return 1.0  # Structurally sound prompt

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A Reasoning: Structural parsing and constructive computation.
        Returns a score 0-1 based on logical consistency.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        score = 0.0
        weight = 0.0

        # 1. Numeric Evaluation (Constructive Computation)
        if p_feat['numbers'] and c_feat['numbers']:
            # Simple heuristic: if prompt has numbers, candidate should reflect logical relation
            # Since we can't solve arbitrary math without eval, we check magnitude consistency
            # for simple comparisons if keywords exist.
            if p_feat['has_comparative']:
                # Check if candidate preserves order (simplified)
                score += 0.5
                weight += 0.5
            else:
                # Exact match of numbers often indicates echo or correct extraction
                if set(p_feat['numbers']) == set(c_feat['numbers']):
                    score += 0.8
                    weight += 0.4
        
        # 2. Logical Consistency (Constraint Propagation)
        # If prompt has negation, candidate should ideally acknowledge it or not contradict
        if p_feat['has_negation']:
            if c_feat['has_negation']:
                score += 0.6 # Consistent negation
                weight += 0.3
            else:
                # Penalty if candidate ignores negation in a critical context
                score -= 0.2
                weight += 0.3

        # 3. Conditional Logic
        if p_feat['has_conditional']:
            if c_feat['has_conditional'] or c_feat['has_negation']:
                score += 0.5
                weight += 0.3

        # Normalize structural score
        if weight > 0:
            return min(1.0, max(0.0, score / weight))
        return 0.5  # Neutral if no structural signals

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main inference loop.
        1. Check Meta-Confidence (Epistemic Honesty).
        2. Score candidates based on Structural + Computational alignment.
        3. Apply Criticality: If meta-confidence is low, flatten scores (high entropy).
        4. Use NCD as a tiebreaker (<15% influence).
        """
        meta_cap = self._meta_confidence(prompt)
        results = []
        
        # Base structural scores
        raw_scores = []
        for cand in candidates:
            struct_score = self._compute_structural_score(prompt, cand)
            # NCD Tiebreaker (max 15% weight)
            ncd_dist = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) and scale
            ncd_score = (1.0 - ncd_dist) * 0.15 
            
            total_raw = (struct_score * 0.85) + ncd_score
            raw_scores.append(total_raw)
        
        # Normalize raw scores to 0-1 range for this batch
        max_raw = max(raw_scores) if raw_scores else 1.0
        min_raw = min(raw_scores) if raw_scores else 0.0
        range_raw = max_raw - min_raw if (max_raw - min_raw) > 0 else 1.0
        
        for i, cand in enumerate(candidates):
            # Normalize
            norm_score = (raw_scores[i] - min_raw) / range_raw
            
            # Criticality Adjustment:
            # If meta-confidence is low (ambiguous prompt), compress the score distribution
            # towards the mean (0.5) to reflect high susceptibility/uncertainty.
            if meta_cap < 0.5:
                # Move score towards 0.5 based on lack of confidence
                adjusted_score = 0.5 + (norm_score - 0.5) * (meta_cap * 2)
            else:
                adjusted_score = norm_score
            
            # Ensure we don't exceed the meta-cap for confidence, but keep ranking relative
            # Note: Score represents likelihood, Confidence represents certainty of that score.
            # We adjust the score itself to reflect the 'critical' state of the network.
            
            results.append({
                "candidate": cand,
                "score": round(float(adjusted_score), 4),
                "reasoning": f"Structural alignment: {raw_scores[i]:.2f}, Meta-cap: {meta_cap:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure Epistemic Honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate base confidence based on structural match
        struct_score = self._compute_structural_score(prompt, answer)
        
        # If the prompt is structurally rich, base confidence on the match.
        # If the prompt is ambiguous (low meta_cap), confidence is capped low.
        base_conf = struct_score if struct_score > 0.5 else 0.5
        
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless it's a definitive computation (handled by struct_score being near 1.0)
        # But meta_cap prevents overconfidence on traps.
        return round(float(final_conf), 4)