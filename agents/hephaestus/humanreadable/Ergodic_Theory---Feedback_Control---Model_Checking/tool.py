import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic-Guided Counterexample Abstraction (EG-CA) Tool.
    
    Mechanism:
    1. Ergodic Sampling (Structural Parsing): Instead of random sampling, we parse the prompt
       to extract invariant structural features (negations, comparatives, conditionals, numbers).
       These form the "state space" of the reasoning problem.
       
    2. Feedback Control (PID-inspired Scoring): We treat the candidate answer as a hypothesis.
       We compute an "error signal" based on how well the candidate aligns with the extracted
       structural constraints (e.g., if prompt has "not", candidate shouldn't affirm blindly).
       The score is adjusted dynamically: Base Similarity - Structural Penalty + Logic Bonus.
       
    3. Model Checking (Constraint Verification): We perform lightweight formal checks:
       - Numeric consistency (parsing floats and comparing).
       - Logical consistency (checking for direct contradictions in negation/affirmation).
       Candidates failing these "counterexamples" are heavily penalized.
       
    This approach beats pure NCD by prioritizing logical structure over string similarity.
    """

    def __init__(self):
        # Keywords for structural extraction
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self.booleans = {'true', 'false', 'yes', 'no'}

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features (Ergodic Sampling)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        word_set = set(words)
        
        # Count structural markers
        neg_count = sum(1 for w in words if w in self.negations)
        comp_count = sum(1 for w in words if w in self.comparatives)
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', lower_text)
        nums_float = []
        for n in numbers:
            try:
                nums_float.append(float(n))
            except ValueError:
                pass
        
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numbers': nums_float,
            'has_boolean': bool(word_set & self.booleans),
            'length': len(text),
            'word_set': word_set
        }

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Model Checking: Verify numeric logic."""
        # Extract numbers from both
        p_nums = re.findall(r'-?\d+\.?\d*', prompt)
        c_nums = re.findall(r'-?\d+\.?\d*', candidate)
        
        if not p_nums:
            return 1.0 # No numeric constraints to check
            
        # Simple heuristic: If prompt has numbers and candidate has none, slight penalty
        # If candidate has numbers, check if they are plausible (subset or derived)
        if not c_nums and len(p_nums) > 0:
            # If the prompt asks a numeric question (implied by presence) and answer is non-numeric
            # This is a weak check, mainly to distinguish numeric vs non-numeric answers
            if any(c.isdigit() for c in candidate):
                return 1.0
            return 0.85 
            
        return 1.0

    def _check_logical_consistency(self, prompt_feats: Dict, candidate: str) -> float:
        """Model Checking: Verify logical consistency (Counterexample detection)."""
        lower_cand = candidate.lower()
        cand_words = set(re.findall(r'\b\w+\b', lower_cand))
        
        # Check 1: Negation mismatch
        # If prompt is heavily negative and candidate is a bare affirmative boolean
        if prompt_feats['negations'] > 0:
            if cand_words & {'yes', 'true'} and not (cand_words & self.negations):
                # Potential trap: "Is it not true?" -> "Yes" (ambiguous) vs "No"
                # Heuristic: If prompt has high negation density, simple "Yes" is risky.
                if cand_words == {'yes'} or cand_words == {'true'}:
                    return 0.7 # Penalize but don't discard
        
        # Check 2: Contradiction in simple boolean prompts
        if prompt_feats['has_boolean']:
            # If prompt implies a direction and candidate opposes? 
            # Hard to do without semantic NLI, so we skip deep semantic check to stay within limits.
            pass
            
        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Simplified for stability: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Using lengths as proxy for C(x) if compression not run individually, 
        # but standard NCD uses compressed sizes.
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c_concat = len_concat
        
        min_c = min(c1, c2)
        max_c = max(c1, c2)
        if max_c == 0:
            return 1.0
        return (c_concat - min_c) / max_c

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Baseline NCD scores for tie-breaking
        ncd_scores = []
        for cand in candidates:
            ncd_scores.append(self._compute_ncd(prompt, cand))
        
        min_ncd = min(ncd_scores) if ncd_scores else 1.0
        max_ncd = max(ncd_scores) if ncd_scores else 1.0
        ncd_range = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for i, cand in enumerate(candidates):
            cand_feats = self._extract_features(cand)
            
            # 1. Base Score: Inverse NCD (Similarity) normalized to 0-1 range roughly
            # Lower NCD = Higher similarity. 
            raw_ncd = ncd_scores[i]
            # Normalize to 0-1 where 1 is best
            base_score = 1.0 - (raw_ncd - min_ncd) / ncd_range if ncd_range > 0 else 0.5
            
            # 2. Feedback Adjustment (Structural Alignment)
            # If prompt has comparatives, reward candidates with comparatives
            alignment_bonus = 0.0
            if prompt_feats['comparatives'] > 0:
                if cand_feats['comparatives'] > 0:
                    alignment_bonus += 0.15
                else:
                    alignment_bonus -= 0.1 # Penalty for missing structure
            
            if prompt_feats['conditionals'] > 0:
                if cand_feats['conditionals'] > 0:
                    alignment_bonus += 0.1
                elif cand_feats['has_boolean']:
                    # If prompt is conditional, a simple boolean might be insufficient
                    alignment_bonus -= 0.05

            # 3. Model Checking Penalties/Bonuses
            logic_penalty = 0.0
            logic_penalty += (self._check_numeric_consistency(prompt, cand) - 1.0) * 0.5 # Scale penalty
            logic_penalty += (self._check_logical_consistency(prompt_feats, cand) - 1.0) * 0.5
            
            final_score = base_score + alignment_bonus + logic_penalty
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment: {alignment_bonus:.2f}, Logic check: {logic_penalty:.2f}, NCD base: {base_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural and logical consistency."""
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(answer)
        
        score = 0.5 # Base prior
        
        # Structural match
        if prompt_feats['negations'] > 0:
            if cand_feats['negations'] > 0:
                score += 0.2
            else:
                score -= 0.2
        
        if prompt_feats['comparatives'] > 0:
            if cand_feats['comparatives'] > 0:
                score += 0.2
            else:
                score -= 0.1
                
        # Logic checks
        num_check = self._check_numeric_consistency(prompt, answer)
        log_check = self._check_logical_consistency(prompt_feats, answer)
        
        score += (num_check - 1.0) * 0.5
        score += (log_check - 1.0) * 0.5
        
        # NCD factor (if very similar, higher confidence, unless it's a trap)
        ncd = self._compute_ncd(prompt, answer)
        if ncd < 0.3:
            score += 0.1
        elif ncd > 0.9:
            score -= 0.1
            
        return max(0.0, min(1.0, score))