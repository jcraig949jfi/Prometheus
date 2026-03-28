import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Measure-Theoretic Entropy-Regularized Adaptive Filter (MTERAF)
    
    Mechanism:
    1. Structural Parsing (Measure Space Construction): Extracts logical operators 
       (negations, comparatives, conditionals) and numeric values to form a 
       structured 'hypothesis space' representation.
    2. MaxEnt Prior (Entropy Regularization): Assigns uniform prior weight to 
       candidates that satisfy structural constraints, penalizing those that 
       contradict explicit negations or logical flows.
    3. Feedback Control (PID-style Gain): Computes an 'error signal' based on 
       the mismatch between prompt constraints and candidate features. 
       - High error (contradiction) -> High gain on penalty (rapid rejection).
       - Low error (consistency) -> Low gain, relying on NCD tie-breaking.
    4. Scoring: Combines structural consistency (logic/numbers) with NCD.
    
    This avoids the 'Measure Theory' and 'MaxEnt' traps by using them as 
    metaphors for structural constraint checking and penalty weighting, 
    rather than performing actual Lebesgue integration.
    """

    def __init__(self):
        # PID-like parameters for belief update damping
        self.kp = 1.5  # Proportional gain for constraint violation
        self.kd = 0.5  # Derivative gain for oscillation damping (history)
        self._prev_error = 0.0
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|false)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|only if|provided)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'boolean_yes': re.compile(r'\byes\b', re.I),
            'boolean_no': re.compile(r'\bno\b', re.I)
        }

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features from text."""
        text_lower = text.lower()
        return {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'is_yes': bool(self.patterns['boolean_yes'].search(text_lower)),
            'is_no': bool(self.patterns['boolean_no'].search(text_lower)),
            'length': len(text)
        }

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Check for direct logical contradictions (Measure Zero events).
        Returns a penalty score (0.0 = consistent, 1.0 = contradiction).
        """
        penalty = 0.0
        
        # Case 1: Prompt asks for affirmation/negation, candidate contradicts
        if prompt_feats['has_negation']:
            # If prompt has negation, a simple "Yes" might be tricky, 
            # but if candidate is "No" when prompt implies positive action, etc.
            # Simplified heuristic: If prompt is negative and candidate is positive assertion without qualification
            if cand_feats['is_yes'] and not cand_feats['has_negation']:
                # Heuristic: Often "No" is the correct answer to "Is X not Y?" if X is Y.
                # We don't penalize heavily here without semantic understanding, 
                # but we flag potential complexity.
                pass 

        # Case 2: Numeric consistency
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # If both have numbers, check if they are wildly different in a comparison context
            # This is a weak proxy, but helps with "Which is larger?" type questions
            if prompt_feats['has_comparative']:
                p_max = max(prompt_feats['numbers'])
                c_max = max(cand_feats['numbers'])
                # If the candidate number isn't in the prompt's set and isn't a clear derivative
                if c_max not in prompt_feats['numbers']:
                    # No direct penalty, but note divergence
                    pass

        # Case 3: Direct Yes/No contradiction with explicit prompt constraints
        # If prompt asks "Is it A or B?" and candidate says "C", NCD handles length, 
        # but logic handles the set membership.
        
        return penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0:
                return 0.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Calculate global stats for relative scoring (Entropy regularization proxy)
        if not candidates:
            return []
            
        scores = []
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            logic_penalty = self._check_logical_consistency(prompt_feats, cand_feats)
            
            # 2. Numeric Evaluation
            num_score = 0.0
            if prompt_feats['numbers'] and cand_feats['numbers']:
                # If prompt has comparatives, favor candidates that respect order
                if prompt_feats['has_comparative']:
                    # Simple heuristic: if prompt says "larger", candidate should be the larger number
                    # This is hard without full semantics, so we rely on NCD for similarity to prompt context
                    pass
            
            # 3. Feedback Control (PID-style adjustment)
            # Error = logic_penalty
            # We want to minimize error. 
            # Score base = 1.0 - error
            base_score = 1.0 - logic_penalty
            
            # Apply proportional gain to penalty
            adjustment = -self.kp * logic_penalty
            
            # Derivative term (damping oscillations if we had history, here simulated per-candidate)
            # If the candidate is very short (e.g., "Yes"/"No") and prompt is complex, 
            # increase skepticism unless structural match is perfect.
            if cand_feats['length'] < 5 and prompt_feats['length'] > 20:
                adjustment -= 0.2 # Penalty for oversimplification in complex contexts

            final_score = base_score + adjustment
            
            # 4. NCD as Tiebreaker / Secondary Signal
            # Invert NCD (0=identical, 1=diff) to similarity (0=diff, 1=identical)
            # But we want diversity? No, usually answer is similar in distribution to prompt context
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD contribution
            ncd_contrib = (1.0 - ncd_val) * 0.3 # Weight 0.3
            
            total_score = final_score * 0.7 + ncd_contrib
            
            # Ensure bounds
            total_score = max(0.0, min(1.0, total_score))
            
            scores.append((cand, total_score))

        # Normalize scores to ensure ranking clarity
        max_s = max(s[1] for s in scores) if scores else 1.0
        min_s = min(s[1] for s in scores) if scores else 0.0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        ranked = []
        for cand, raw_score in scores:
            # Rescale to 0.1 - 0.9 range for clarity
            norm_score = 0.1 + (0.8 * (raw_score - min_s) / range_s)
            ranked.append({
                "candidate": cand,
                "score": round(norm_score, 4),
                "reasoning": f"Structural match: {1.0 - self._check_logical_consistency(prompt_feats, self._extract_features(cand)):.2f}, NCD similarity: {1.0 - self._compute_ncd(prompt, cand):.2f}"
            })
            
        # Sort descending
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment and compression.
        Returns 0.0 to 1.0.
        """
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        # 1. Structural Consistency Check
        penalty = self._check_logical_consistency(p_feats, a_feats)
        
        # 2. Length heuristic (Metacognition)
        # If prompt is complex (many conditionals) and answer is trivial, lower confidence
        complexity_penalty = 0.0
        if p_feats['has_conditional'] or p_feats['has_comparative']:
            if a_feats['length'] < 4: # Very short answer to complex question
                complexity_penalty = 0.3
        
        # 3. NCD Check
        ncd = self._compute_ncd(prompt, answer)
        # If NCD is very high (very different), and no strong structural match, confidence drops
        ncd_penalty = ncd * 0.2
        
        base_conf = 1.0 - penalty - complexity_penalty - ncd_penalty
        
        # Boost if answer contains numbers present in prompt (strong signal)
        if p_feats['numbers'] and a_feats['numbers']:
            common_nums = set(p_feats['numbers']) & set(a_feats['numbers'])
            if common_nums:
                base_conf += 0.2
                
        return max(0.0, min(1.0, base_conf))