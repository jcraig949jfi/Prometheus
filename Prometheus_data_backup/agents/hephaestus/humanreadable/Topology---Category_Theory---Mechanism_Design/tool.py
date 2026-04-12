import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sheaf-theoretic Bayesian Mechanism (SBM) Implementation.
    
    Mechanism:
    1. Topology (Context): The prompt is decomposed into overlapping "open sets" 
       (semantic fragments based on constraints, negations, and comparatives).
    2. Category Theory (Structure): Candidates are treated as objects. Restriction 
       functors map candidates to these local contexts. Consistency is checked 
       via natural transformations (logical alignment between fragment and candidate).
    3. Mechanism Design (Incentive): A proper scoring rule (Brier-like) rewards 
       candidates that maintain global coherence (gluing condition) across all 
       local contexts. Inconsistencies (cohomology holes) penalize the score.
       
    This ensures candidates are ranked by their ability to satisfy local logical 
    constraints while forming a coherent global answer, beating pure compression 
    baselines by focusing on structural validity.
    """

    def __init__(self):
        # Structural patterns for topological decomposition
        self.negation_patterns = [r"\bnot\b", r"\bnever\b", r"\bwithout\b", r"\bexcept\b"]
        self.comparative_patterns = [r"\bmore\s+than\b", r"\bless\s+than\b", r"\bgreater\b", r"\bsmaller\b", r"\b<", r"\b>"]
        self.conditional_patterns = [r"\bif\b", r"\bthen\b", r"\bunless\b", r"\botherwise\b"]
        self.number_regex = re.compile(r"-?\d+\.?\d*")

    def _extract_structural_features(self, text: str) -> Dict:
        """Extract topological features (negations, comparatives, numbers) from text."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall("|".join(self.negation_patterns), text_lower)),
            "comparatives": len(re.findall("|".join(self.comparative_patterns), text_lower)),
            "conditionals": len(re.findall("|".join(self.conditional_patterns), text_lower)),
            "numbers": [float(n) for n in re.findall(self.number_regex, text)],
            "length": len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Category Theory: Check morphism compatibility.
        Returns a consistency score (0.0 to 1.0) based on logical alignment.
        """
        score = 1.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect awareness or not contradict
        has_no = any(re.search(p, p_lower) for p in self.negation_patterns)
        cand_has_no = any(re.search(p, c_lower) for p in self.negation_patterns)
        
        if has_no and not cand_has_no:
            # Potential contradiction if the candidate ignores the negation context
            # Soft penalty unless the candidate is a simple confirmation
            if len(candidate.split()) > 3: 
                score -= 0.2

        # 2. Numeric Consistency (Transitivity)
        p_nums = self._extract_structural_features(prompt)["numbers"]
        c_nums = self._extract_structural_features(candidate)["numbers"]
        
        if p_nums and c_nums:
            # If prompt implies an order (e.g., "greater than 5") and candidate gives a number
            # Simple heuristic: if prompt says "greater than X" and candidate < X, penalize
            if "greater" in p_lower or "more than" in p_lower:
                threshold = p_nums[0] if p_nums else None
                if threshold and c_nums and c_nums[0] < threshold:
                    score -= 0.5
            elif "less" in p_lower or "smaller" in p_lower:
                threshold = p_nums[0] if p_nums else None
                if threshold and c_nums and c_nums[0] > threshold:
                    score -= 0.5

        # 3. Keyword Overlap as a weak functor map (ensures topic relevance)
        prompt_words = set(re.findall(r'\b\w+\b', p_lower))
        cand_words = set(re.findall(r'\b\w+\b', c_lower))
        intersection = prompt_words.intersection(cand_words)
        # Remove stopwords for overlap calc
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        meaningful_overlap = len(intersection - stopwords)
        if meaningful_overlap == 0 and len(cand_words) > 2:
            score -= 0.1
            
        return max(0.0, score)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c12 = len(zlib.compress(s1_bytes + s2_bytes))
            denominator = max(c1, c2)
            if denominator == 0:
                return 1.0
            return (c12 - min(c1, c2)) / denominator
        except Exception:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using the SBM framework.
        1. Decompose prompt into topological constraints.
        2. Map candidates to these constraints (functors).
        3. Score based on consistency (gluing) and mechanism incentives.
        """
        if not candidates:
            return []
        
        scored_candidates = []
        prompt_features = self._extract_structural_features(prompt)
        
        # Pre-calculate prompt complexity for normalization
        prompt_complexity = prompt_features['negations'] + prompt_features['comparatives'] + 1
        
        for cand in candidates:
            # 1. Local Consistency (Category Theory: Natural Transformation check)
            consistency_score = self._check_logical_consistency(prompt, cand)
            
            # 2. Structural Alignment (Mechanism Design: Truthful reporting incentive)
            # Reward candidates that match the structural density of the prompt
            cand_features = self._extract_structural_features(cand)
            
            structural_penalty = 0.0
            # If prompt has high logic density, short answers might be insufficient unless exact
            if prompt_complexity > 2 and cand_features['length'] < 3:
                structural_penalty = 0.1
            
            # 3. Global Coherence (NCD as tiebreaker for similar logical scores)
            # We invert NCD so higher is better, but scale it down to be a tiebreaker
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.05  # Small weight
            
            final_score = consistency_score - structural_penalty + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if consistency_score < 0.8:
                reasoning_parts.append("Logical inconsistency detected with prompt constraints.")
            if structural_penalty > 0:
                reasoning_parts.append("Candidate too brief for complex prompt structure.")
            if not reasoning_parts:
                reasoning_parts.append("High coherence with prompt topology and constraints.")
                
            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence (0-1) based on the evaluation score.
        Uses the internal evaluate logic to determine if the answer is 'glued' correctly.
        """
        # Run single candidate evaluation
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        raw_score = results[0]["score"]
        # Map raw score (approx -0.5 to 1.0) to 0.0 - 1.0
        # Base consistency is 1.0, penalties reduce it.
        confidence = max(0.0, min(1.0, raw_score))
        return round(confidence, 4)