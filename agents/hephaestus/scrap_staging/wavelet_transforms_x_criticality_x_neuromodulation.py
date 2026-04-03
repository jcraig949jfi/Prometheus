import re
import math
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Multi-Scale Wavelet-Critical Neuromodulatory Scorer (MS-WCNS).
    
    Mechanism:
    1. Parsing: Regex-based extraction of logical features (negation, conditionals, etc.).
    2. Wavelet Decomposition: Haar-like filtering on token salience to find multi-scale contrast.
    3. Criticality: Thresholding based on median + alpha*IQR to isolate divergent structures.
    4. Neuromodulation: Gain control modulating salience based on logical feature density.
    5. Scoring: Aggregated salience normalized, combined with constructive computation and NCD tie-breaking.
    
    Epistemic Honesty: Detects ambiguity/presupposition to cap confidence.
    """

    def __init__(self):
        # Regex patterns for feature extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere|cannot|won\'t|don\'t|doesn\'t|didn\'t|isn\'t|aren\'t|wasn\'t|weren\'t)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|than|>=|<=|==|!=|>|<|=)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided|assuming)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|causes|due to|since)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|next|previous|prior)\b', re.IGNORECASE),
            'numeric': re.compile(r'\b\d+(\.\d+)?\b'),
            'quantifier': re.compile(r'\b(all|every|each|some|any|few|many|most|several)\b', re.IGNORECASE),
            # Meta-confidence triggers
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did|when does)\b', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'\b(every .+ a .+|each .+ a .+)\b', re.IGNORECASE), # Simplified heuristic
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|them)\b.*\b(who|which one)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe|think)\b', re.IGNORECASE)
        }
        self.alpha = 1.0  # Criticality parameter
        self.beta = 0.2   # Neuromodulation gain parameter

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+|[^\s\w]', text.lower())

    def _extract_features(self, text: str) -> Dict[str, bool]:
        flags = {}
        for key, pattern in self.patterns.items():
            if key not in ['scope_ambiguity', 'pronoun_ambiguity', 'false_dichotomy', 'subjectivity', 'presupposition']:
                flags[key] = bool(pattern.search(text))
        return flags

    def _check_meta_confidence(self, text: str) -> Tuple[bool, float]:
        """
        Checks for Tier B traps. Returns (is_ambiguous, confidence_cap).
        """
        caps = []
        if self.patterns['presupposition'].search(text):
            caps.append(0.2)
        if self.patterns['subjectivity'].search(text):
            caps.append(0.3)
        if self.patterns['false_dichotomy'].search(text):
            caps.append(0.3)
        # Heuristics for scope/pronoun are weak in regex, so we rely on low structural match later
        # but if explicit triggers found:
        if self.patterns['scope_ambiguity'].search(text) and "same" in text or "different" in text:
             caps.append(0.3)
        
        if caps:
            return True, min(caps)
        return False, 1.0

    def _wavelet_decompose(self, saliences: List[float]) -> List[float]:
        """Haar-like wavelet decomposition returning coefficients."""
        if len(saliences) == 0:
            return []
        coeffs = []
        current = saliences[:]
        
        while len(current) > 1:
            next_level = []
            # Pad if odd
            if len(current) % 2 != 0:
                current.append(0.0)
            
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i+1]
                # Approximation (average) kept for next level, Detail (difference) stored
                # Standard Haar: (L+R)/sqrt(2), (L-R)/sqrt(2)
                # We store detail coefficient for criticality analysis
                detail = (left - right) / math.sqrt(2)
                coeffs.append(detail)
                next_level.append((left + right) / math.sqrt(2))
            current = next_level
        return coeffs

    def _critical_threshold(self, coeffs: List[float]) -> float:
        if not coeffs:
            return 0.0
        abs_coeffs = [abs(c) for c in coeffs]
        abs_coeffs.sort()
        n = len(abs_coeffs)
        median = abs_coeffs[n // 2]
        q1 = abs_coeffs[n // 4] if n > 1 else median
        q3 = abs_coeffs[(3 * n) // 4] if n > 1 else median
        iqr = q3 - q1
        return median + self.alpha * iqr

    def _compute_salience(self, text: str) -> float:
        tokens = self._tokenize(text)
        if not tokens:
            return 0.0
            
        # 1. Base salience (s0 = 1 for all)
        saliences = [1.0] * len(tokens)
        
        # 2. Wavelet Decomposition
        # We simulate levels by recursively applying filter on the sequence
        # For simplicity in 1D text, we treat the sequence as the signal
        all_coeffs = self._wavelet_decompose(saliences)
        
        if not all_coeffs:
            return 0.0

        # 3. Criticality Thresholding
        threshold = self._critical_threshold(all_coeffs)
        
        # Map coefficients back to a "criticality score"
        # Count how many exceed threshold
        critical_count = sum(1 for c in all_coeffs if abs(c) > threshold)
        base_score = critical_count / (len(all_coeffs) + 1e-6)

        # 4. Neuromodulatory Gain
        features = self._extract_features(text)
        feature_sum = sum(features.values())
        gain = 1.0 + self.beta * feature_sum
        
        # Modulate based on specific logical cues
        if features.get('negation', False):
            # Negation flips sign logic in complex reasoning, here we reduce blind confidence
            gain *= 0.9 
        if features.get('conditional', False) or features.get('causal', False):
            gain *= 1.2 # Boost structured logic
            
        final_score = base_score * gain
        return final_score

    def _constructive_compute(self, text: str) -> float:
        """Attempt to solve math/logic explicitly."""
        # Detect simple comparisons: "9.11 < 9.9" or "is 5 greater than 3?"
        nums = [float(x) for x in re.findall(r'\d+\.\d+|\d+', text)]
        if len(nums) >= 2:
            # Check for comparative keywords
            if re.search(r'\b(greater|larger|more|higher)\b', text, re.IGNORECASE):
                return 1.0 if nums[0] > nums[1] else 0.0
            if re.search(r'\b(less|smaller|lower)\b', text, re.IGNORECASE):
                return 1.0 if nums[0] < nums[1] else 0.0
            
        # Check for explicit boolean questions in candidate
        if "yes" in text.lower() or "true" in text.lower():
            return 0.6 # Weak positive bias if no other info
        return 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = lambda x: len(zlib.compress(x.encode()))
        len1, len2 = z(s1), z(s2)
        if len1 == 0 or len2 == 0: return 1.0
        concat = z((s1 + s2).encode())
        return (concat - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_salience = self._compute_salience(prompt)
        prompt_features = self._extract_features(prompt)
        has_logic = any(prompt_features.values())
        
        scores = []
        
        # Phase 1: Structural & Constructive Scoring
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # A. Constructive Computation (Highest Priority for Math/Logic)
            # If prompt asks a comparison and candidate answers it
            comp_score = self._constructive_compute(prompt + " " + cand)
            if comp_score > 0.5:
                score += 0.6
                reasoning_parts.append("Constructive match")
            
            # B. Wavelet-Critical Salience Matching
            cand_salience = self._compute_salience(cand)
            # Score based on alignment of critical structures
            # If prompt has high logical density, candidate should too
            if has_logic:
                # Similarity in logical "texture"
                similarity = 1.0 - abs(prompt_salience - cand_salience)
                score += similarity * 0.3
                reasoning_parts.append(f"Logical texture match: {similarity:.2f}")
            
            # C. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._ncd(prompt, cand)
            # Lower NCD is better (more similar/compressible together)
            ncd_score = (1.0 - ncd_val) * 0.15
            score += ncd_score
            
            # Normalize rough score to [-1, 1] range roughly
            # Boost if candidate contains explicit confirmation of prompt features
            for key in ['negation', 'conditional', 'causal']:
                if prompt_features.get(key) and self.patterns[key].search(cand):
                    score += 0.1
                    reasoning_parts.append(f"Preserved {key}")

            scores.append({"candidate": cand, "score": score, "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Structural baseline"})

        # Normalize scores to [-1, 1]
        raw_scores = [x['score'] for x in scores]
        max_abs = max(abs(max(raw_scores)), abs(min(raw_scores)), 1e-6)
        for item in scores:
            item['score'] = item['score'] / max_abs
            
        # Sort descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores

    def _meta_confidence(self, prompt: str) -> float:
        is_ambiguous, cap = self._check_meta_confidence(prompt)
        if is_ambiguous:
            return cap
        
        # Check for lack of structural hooks
        features = self._extract_features(prompt)
        if not any(features.values()):
            # If no logical structure detected, be humble
            # Unless it's a simple factoid, but we assume reasoning task
            return 0.4 
        return 1.0

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-confidence check (Tier B traps)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural validation
        # Does the answer contain the logical operators required by the prompt?
        prompt_feats = self._extract_features(prompt)
        ans_feats = self._extract_features(answer)
        
        mismatch_penalty = 0.0
        for key in ['negation', 'conditional', 'causal']:
            if prompt_feats.get(key) and not ans_feats.get(key):
                mismatch_penalty += 0.2
        
        # 3. Constructive verification (if numeric)
        nums_prompt = [float(x) for x in re.findall(r'\d+\.\d+|\d+', prompt)]
        nums_ans = [float(x) for x in re.findall(r'\d+\.\d+|\d+', answer)]
        
        constructive_conf = 0.0
        if len(nums_prompt) >= 2 and len(nums_ans) >= 1:
            # Very rough check: did the answer pick one of the numbers or a result?
            # If prompt is "Is 9.11 > 9.9?" and answer is "No", constructive logic holds.
            # We rely on the evaluate score for this, here we just penalize nonsense
            constructive_conf = 0.2 
            
        base_conf = 0.7
        if mismatch_penalty > 0.3:
            base_conf = 0.3 # Low confidence if logical operators dropped
            
        final_conf = min(meta_cap, base_conf + constructive_conf - mismatch_penalty)
        return max(0.0, min(1.0, final_conf))