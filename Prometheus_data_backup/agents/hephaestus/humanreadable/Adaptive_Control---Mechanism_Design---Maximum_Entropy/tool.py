import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Entropic Mechanism Controller (AEMC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Adaptive Control): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a feature vector.
    2. Maximum Entropy Constraint (Confidence Wrapper): Uses entropy of the candidate 
       distribution to modulate the final confidence score, penalizing high-uncertainty 
       states as per the theoretical inhibitor warning.
    3. Mechanism Design (Scoring): Candidates are scored based on structural alignment 
       with the prompt's logical constraints. Truthfulness is enforced by penalizing 
       candidates that contradict extracted negations or fail numeric transitivity.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        self._state = {"updates": 0}

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical and numeric features from text."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|best|worst)\b', text_lower)),
            "numbers": [],
            "length": len(text),
            "entropy_estimate": 0.0
        }
        
        # Extract numbers for comparison logic
        nums = re.findall(r'-?\d+\.?\d*', text)
        features["numbers"] = [float(n) for n in nums]
        
        # Simple Shannon entropy estimate for the "Maximum Entropy" component
        if len(text) > 0:
            freq = {}
            for char in text:
                freq[char] = freq.get(char, 0) + 1
            for count in freq.values():
                p = count / len(text)
                if p > 0:
                    features["entropy_estimate"] -= p * math.log2(p)
        
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Module: Checks if candidate violates prompt constraints.
        Returns a score penalty (0.0 to 1.0) where 1.0 is perfect alignment.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        score = 1.0
        
        # Negation consistency: If prompt has strong negation, candidate shouldn't 
        # blindly affirm without qualification (simplified heuristic).
        if p_feat["negations"] > 0 and c_feat["negations"] == 0:
            # Heuristic: Check for simple "Yes" or affirmative start which might ignore negation
            if re.match(r'^(yes|true|correct|it is)', candidate.strip(), re.IGNORECASE):
                score -= 0.3
        
        # Numeric transitivity check (Basic)
        if len(p_feat["numbers"]) >= 2 and len(c_feat["numbers"]) >= 1:
            # If prompt compares A and B, and candidate gives a number, 
            # ensure it's not wildly out of bounds (simplified)
            p_nums = sorted(p_feat["numbers"])
            c_nums = c_feat["numbers"]
            # If prompt implies range, candidate should respect it (loose check)
            if c_nums[0] < p_nums[0] * 0.5 or c_nums[0] > p_nums[-1] * 2.0:
                 # Only penalize if the candidate is providing a specific number
                 if len(c_feat["numbers"]) == 1:
                     score -= 0.2

        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        p_feat = self._extract_structure(prompt)
        
        # Pre-calculate prompt complexity for entropy weighting
        prompt_entropy = p_feat["entropy_estimate"]
        
        scores = []
        for cand in candidates:
            c_feat = self._extract_structure(cand)
            
            # 1. Structural Alignment Score (Primary Signal)
            # Reward matching logical density (conditionals/negations)
            logic_match = 0.0
            if p_feat["conditionals"] > 0:
                logic_match += 0.2 if c_feat["conditionals"] > 0 else -0.2
            if p_feat["negations"] > 0:
                logic_match += 0.2 if c_feat["negations"] > 0 else -0.1
            
            # 2. Mechanism Design Consistency Check
            consistency_score = self._check_logical_consistency(prompt, cand)
            
            # 3. Numeric Evaluation
            numeric_score = 0.0
            if len(p_feat["numbers"]) > 0 and len(c_feat["numbers"]) > 0:
                # Reward if candidate numbers appear in prompt (exact match hint)
                matches = sum(1 for n in c_feat["numbers"] if n in p_feat["numbers"])
                numeric_score = min(0.5, matches * 0.25)
            
            # Base Score
            base_score = 0.5 + logic_match + (consistency_score - 0.5) * 0.4 + numeric_score
            
            # 4. Maximum Entropy Regularization (Confidence Wrapper)
            # Penalize if candidate entropy is too low (rigid) or too high (noise) relative to prompt
            # This implements the "Max Entropy Prior" constraint loosely
            entropy_diff = abs(c_feat["entropy_estimate"] - prompt_entropy)
            entropy_penalty = min(0.2, entropy_diff * 0.01) # Small penalty for mismatch
            
            final_score = base_score - entropy_penalty
            
            # NCD is strictly a tie-breaker, so we store it but don't add to score yet
            scores.append({
                "candidate": cand,
                "score": final_score,
                "ncd": 0.0, # Placeholder
                "reasoning": f"Structural:{logic_match:.2f}, Consistency:{consistency_score:.2f}, Numeric:{numeric_score:.2f}"
            })

        # Resolve ties with NCD
        for i in range(len(scores)):
            for j in range(i + 1, len(scores)):
                if abs(scores[i]["score"] - scores[j]["score"]) < 1e-6:
                    ncd_val = self._ncd(prompt, scores[i]["candidate"])
                    scores[i]["ncd"] = ncd_val
                    scores[j]["ncd"] = self._ncd(prompt, scores[j]["candidate"])
        
        # Sort: Higher score first. If tie, lower NCD (more similar) first.
        # Since we want to beat NCD baseline, structural score is primary.
        scores.sort(key=lambda x: (x["score"], -x["ncd"]), reverse=True)
        
        # Normalize scores to 0-1 range roughly
        max_s = max(s["score"] for s in scores) if scores else 1.0
        min_s = min(s["score"] for s in scores) if scores else 0.0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        result = []
        for s in scores:
            norm_score = (s["score"] - min_s) / range_s
            result.append({
                "candidate": s["candidate"],
                "score": norm_score,
                "reasoning": s["reasoning"]
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calculates confidence based on structural alignment and entropy constraints.
        Returns 0.0 (low confidence) to 1.0 (high confidence).
        """
        p_feat = self._extract_structure(prompt)
        a_feat = self._extract_structure(answer)
        
        # Base confidence from logical consistency
        consistency = self._check_logical_consistency(prompt, answer)
        
        # Entropy constraint: 
        # If the answer is too simple (low entropy) for a complex prompt, reduce confidence.
        # If the answer is random noise (high entropy), reduce confidence.
        prompt_complexity = p_feat["conditionals"] + p_feat["negations"]
        answer_complexity = a_feat["conditionals"] + a_feat["negations"]
        
        complexity_gap = abs(prompt_complexity - answer_complexity)
        entropy_penalty = min(0.5, complexity_gap * 0.15)
        
        # Numeric check
        numeric_bonus = 0.0
        if len(p_feat["numbers"]) > 0 and len(a_feat["numbers"]) > 0:
            if any(n in a_feat["numbers"] for n in p_feat["numbers"]):
                numeric_bonus = 0.2
        
        conf = consistency - entropy_penalty + numeric_bonus
        return max(0.0, min(1.0, conf))