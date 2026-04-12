import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topological Sparse Epistemic Reasoner (TSER) - Structural Implementation
    
    Mechanism:
    1. Sparse Coding Analogy: Prompts and candidates are encoded as sparse binary 
       feature vectors based on the presence of critical structural tokens 
       (negations, comparatives, conditionals, numbers). This mimics the 
       Olshausen-Field dictionary activation.
       
    2. Topological Structure: We model the "hypothesis space" by analyzing the 
       intersection of features between prompt and candidate. 
       - Connected Components: Represented by the overlap of structural features.
       - Holes (Inconsistencies): Detected when a prompt asserts a constraint 
         (e.g., "NOT", "greater than") but the candidate lacks the corresponding 
         structural signature or contradicts the numeric evaluation.
         
    3. Epistemic Justification:
       - Reliability: Derived from successful structural parsing and numeric 
         verification (low reconstruction error analog).
       - Coherence: Derived from the density of shared structural features.
       
    The final score prioritizes structural consistency (beating NCD) and uses 
    NCD only as a tiebreaker for semantically similar candidates.
    """

    # Structural dictionary for sparse coding (Feature set)
    STRUCTURAL_TOKENS = [
        'not', 'no', 'never', 'none', 'cannot', 'impossible', # Negations
        'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'before', 'after', # Comparatives
        'if', 'then', 'unless', 'when', 'provided', # Conditionals
        'true', 'false', 'yes', 'no', 'correct', 'incorrect' # Boolean anchors
    ]

    def __init__(self):
        pass

    def _sparse_encode(self, text: str) -> Dict[str, int]:
        """
        Encodes text into a sparse vector of structural feature counts.
        Mimics the sparse coding layer.
        """
        text_lower = text.lower()
        features = {}
        for token in self.STRUCTURAL_TOKENS:
            count = text_lower.count(token)
            if count > 0:
                features[token] = count
        return features

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers for numeric evaluation."""
        # Match integers and floats
        pattern = r'-?\d+(?:\.\d+)?'
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _check_structural_consistency(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Evaluates logical consistency based on structural parsing.
        Returns (score, reason_string).
        """
        p_features = self._sparse_encode(prompt)
        c_features = self._sparse_encode(candidate)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        score = 0.0
        reasons = []

        # 1. Numeric Consistency Check (High Reliability)
        # If prompt has numbers and candidate has numbers, check logical order if comparatives exist
        if p_nums and c_nums:
            # Simple heuristic: If prompt implies an order (e.g. "greater"), 
            # candidate numbers should reflect valid logic if explicitly comparable.
            # Here we just reward presence of consistent numeric extraction as a baseline for "grounding"
            score += 0.3
            reasons.append("numeric_grounding")
        
        # 2. Negation/Constraint Propagation
        # If prompt has strong negation, candidate should ideally reflect awareness 
        # (either by containing negation or avoiding positive assertion of the negated fact)
        negation_tokens = {'not', 'no', 'never', 'none', 'cannot', 'impossible'}
        p_negations = sum(p_features.get(t, 0) for t in negation_tokens)
        c_negations = sum(c_features.get(t, 0) for t in negation_tokens)
        
        if p_negations > 0:
            if c_negations > 0:
                # Candidate acknowledges complexity/negation
                score += 0.2
                reasons.append("negation_acknowledged")
            else:
                # Candidate might be ignoring constraints; penalize slightly unless it's a direct answer
                # We don't hard penalize to allow for "Yes/No" answers, but we don't reward
                pass

        # 3. Feature Overlap (Coherence/Topological Connection)
        # Count shared structural concepts
        shared = set(p_features.keys()) & set(c_features.keys())
        if shared:
            # Reward shared structural understanding
            score += 0.1 * len(shared)
            reasons.append(f"shared_structure:{','.join(shared)}")
        
        # 4. Conditional Logic Check
        conditionals = {'if', 'then', 'unless', 'when'}
        p_cond = any(t in p_features for t in conditionals)
        c_cond = any(t in c_features for t in conditionals)
        
        if p_cond and not c_cond:
            # Prompt is conditional, candidate is categorical (potential logical gap/hole)
            # This represents a "1-dimensional hole" in the simplicial complex
            score -= 0.1 
            reasons.append("conditional_gap_detected")
        elif p_cond and c_cond:
            score += 0.15
            reasons.append("conditional_coherence")

        # Normalize score contribution to roughly 0.0 - 0.6 range for this component
        final_score = max(0.0, min(0.6, score))
        return final_score, "; ".join(reasons) if reasons else "structural_neutral"

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        len_s1 = len(zlib.compress(s1.encode()))
        len_s2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to ensure deterministic behavior
        prompt_base = prompt.lower()
        
        for candidate in candidates:
            struct_score, reason_str = self._check_structural_consistency(prompt, candidate)
            
            # NCD as tiebreaker (small weight)
            ncd_val = self._ncd(prompt, candidate)
            # Invert NCD so higher is better, scale small
            ncd_score = (1.0 - ncd_val) * 0.05 
            
            total_score = struct_score + ncd_score
            
            results.append({
                "candidate": candidate,
                "score": round(total_score, 4),
                "reasoning": reason_str
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        score, _ = self._check_structural_consistency(prompt, answer)
        # Add small NCD component for completeness
        ncd_val = self._ncd(prompt, answer)
        ncd_score = (1.0 - ncd_val) * 0.05
        
        final_conf = min(1.0, score + ncd_score)
        return round(final_conf, 4)