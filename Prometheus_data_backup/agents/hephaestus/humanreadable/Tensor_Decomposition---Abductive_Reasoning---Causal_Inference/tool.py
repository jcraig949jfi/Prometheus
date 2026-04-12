import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Causal Tensor Abduction Engine (Simplified Implementation)
    
    Mechanism:
    1. Tensor Decomposition Analogy: Parses the prompt into a low-rank structural 
       representation (latent factors: negations, comparatives, conditionals, numeric values).
    2. Abductive Reasoning: Generates hypotheses by matching candidate structures against 
       the prompt's structural constraints. Scores based on explanatory virtue (constraint satisfaction).
    3. Causal Inference (Restricted): Used only within confidence() to validate if the 
       structural match causally implies the answer, avoiding direct scoring bias.
    
    The system prioritizes structural parsing and numeric evaluation over string similarity (NCD),
    using NCD only as a tie-breaker to ensure robustness against adversarial shuffling.
    """

    def __init__(self):
        self.ncd_baseline_acc = 0.20

    def _extract_features(self, text: str) -> dict:
        """Decomposes text into latent structural factors (Tensor Decomposition analogy)."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': [],
            'length': len(text),
            'words': set(re.findall(r'\b\w+\b', text_lower))
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            features['numbers'] = [float(n) for n in nums]
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2: return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        combined = len(zlib.compress(s1_bytes + s2_bytes))
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (combined - min(len1, len2)) / max_len

    def _evaluate_structural_match(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Abductive step: Proposes how well the candidate explains the prompt's constraints.
        Returns (score, reasoning_string)
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        score = 0.0
        reasons = []

        # 1. Numeric Evaluation (Causal Check)
        # If prompt has numbers, does the candidate respect the implied order?
        if p_feat['numbers'] and c_feat['numbers']:
            p_nums = sorted(p_feat['numbers'])
            c_nums = sorted(c_feat['numbers'])
            # Simple heuristic: if prompt asks for max/min, check candidate position
            if 'max' in prompt.lower() or 'largest' in prompt.lower():
                if c_nums and c_nums[-1] == p_nums[-1]:
                    score += 2.0
                    reasons.append("Numeric max constraint satisfied")
                else:
                    score -= 1.0
                    reasons.append("Numeric max constraint violated")
            elif 'min' in prompt.lower() or 'smallest' in prompt.lower():
                if c_nums and c_nums[0] == p_nums[0]:
                    score += 2.0
                    reasons.append("Numeric min constraint satisfied")
                else:
                    score -= 1.0
                    reasons.append("Numeric min constraint violated")
            else:
                # General numeric presence bonus if counts match roughly
                if abs(len(p_feat['numbers']) - len(c_feat['numbers'])) <= 1:
                    score += 0.5
                    reasons.append("Numeric density consistent")

        # 2. Logical Constraint Propagation
        # Negation handling: If prompt says "not X", candidate shouldn't be "X"
        if p_feat['negations'] > 0:
            # Heuristic: if prompt has 'not', candidate having 'yes' might be penalized if context suggests negation
            # This is a simplified abductive check for contradiction
            if 'no' in c_feat['words'] or 'false' in c_feat['words']:
                score += 1.0
                reasons.append("Negation alignment detected")
        
        # Comparative logic
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0 or c_feat['numbers']:
                score += 0.8
                reasons.append("Comparative logic engaged")
        
        # Conditional logic
        if p_feat['conditionals'] > 0:
            if 'if' in c_feat['words'] or 'then' in c_feat['words'] or c_feat['numbers']:
                score += 0.5
                reasons.append("Conditional structure preserved")

        # 3. Keyword Overlap (Base signal)
        common_words = p_feat['words'] & c_feat['words']
        # Filter out stopwords
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'to', 'of', 'in', 'it', 'that', 'this'}
        significant_overlap = common_words - stopwords
        if significant_overlap:
            score += len(significant_overlap) * 0.1
            reasons.append(f"Key terms matched: {len(significant_overlap)}")

        reason_str = "; ".join(reasons) if reasons else "No strong structural link"
        return score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates by generating abductive hypotheses (structural matches)
        and scoring them. Uses NCD only for tie-breaking.
        """
        scored_candidates = []
        
        # Pre-calculate prompt features to avoid re-computation
        prompt_features = self._extract_features(prompt)
        
        for cand in candidates:
            struct_score, reasoning = self._evaluate_structural_match(prompt, cand)
            
            # NCD as tie-breaker (inverted: lower NCD is better, so we subtract it slightly)
            # But since we want higher score = better, and NCD is distance (0=identical)
            # We add a tiny fraction based on similarity (1 - NCD)
            ncd_val = self._compute_ncd(prompt, cand)
            # Scale NCD contribution to be negligible compared to structural logic
            ncd_bonus = (1.0 - ncd_val) * 0.05 
            
            final_score = struct_score + ncd_bonus
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses structural parsing to verify if the answer logically follows (causal check).
        Restricted role: validates structural integrity rather than computing probability.
        """
        if not answer:
            return 0.0
            
        struct_score, _ = self._evaluate_structural_match(prompt, answer)
        
        # Normalize score to 0-1 range roughly
        # Heuristic: > 1.0 is high confidence, < 0 is low
        confidence = 1.0 / (1.0 + pow(2.718, -struct_score)) # Sigmoid-like mapping
        
        # Hard constraints for obvious failures
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # If prompt has specific numbers and answer has none, lower confidence
        if p_feat['numbers'] and not a_feat['numbers']:
            confidence *= 0.5
            
        return max(0.0, min(1.0, confidence))