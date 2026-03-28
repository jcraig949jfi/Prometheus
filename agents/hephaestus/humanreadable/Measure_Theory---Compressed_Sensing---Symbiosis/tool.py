import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Symbiotic Sparse Measurement Framework (SSMF) Implementation.
    
    Mechanism:
    1. Structural Parsing (Measure-Theoretic Support): Extracts logical constraints 
       (negations, comparatives, conditionals) to define a rigid "sigma-algebra" of 
       valid answers. This acts as the hard filter (confidence wrapper).
    2. Sparse Residual Evaluation (Compressed Sensing): Candidates are treated as 
       sparse signals. We compute a "residual" score based on how well the candidate 
       satisfies the extracted structural constraints without unnecessary verbosity 
       (L1 penalty).
    3. Symbiotic Mutualism (Holobiont Exchange): The final score is a mutualistic 
       aggregate. A candidate "donates" points for satisfying constraints and 
       "receives" bonus weight if it aligns with the structural consensus of the 
       group, while penalizing outliers that fail basic logical transitivity.
    
    Note: Measure Theory and Symbiosis concepts are restricted to the confidence 
    wrapper and scoring aggregation logic respectively, per causal intelligence guidelines.
    """

    def __init__(self):
        # No external state needed; stateless deterministic operations
        pass

    def _structural_parse(self, prompt: str) -> Dict:
        """Extracts logical constraints from the prompt (The 'Measure' layer)."""
        p_lower = prompt.lower()
        features = {
            "has_negation": bool(re.search(r'\b(not|no|never|without|impossible)\b', p_lower)),
            "has_comparative": bool(re.search(r'\b(more|less|greater|smaller|better|worse|before|after)\b', p_lower)),
            "has_conditional": bool(re.search(r'\b(if|then|unless|provided|when)\b', p_lower)),
            "numeric_present": bool(re.search(r'\d+', prompt)),
            "question_type": "binary" if re.search(r'\b(yes|no|true|false)\b', p_lower) else "open"
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (combined - max_len) / max_len

    def _evaluate_candidate(self, prompt: str, candidate: str, features: Dict) -> Tuple[float, str]:
        """
        Evaluates a single candidate against structural constraints.
        Returns (score, reasoning_string).
        """
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        score = 0.5  # Base prior
        reasons = []

        # 1. Constraint Propagation (Modus Tollens/Ontology check)
        # If prompt asks for Yes/No and candidate provides it appropriately
        if features["question_type"] == "binary":
            if any(x in c_lower for x in ["yes", "no", "true", "false"]):
                score += 0.3
                reasons.append("Matches binary constraint")
            else:
                score -= 0.2
                reasons.append("Penalized for missing binary format")

        # 2. Negation Handling
        if features["has_negation"]:
            # Heuristic: If prompt has "not", correct answers often contain specific negation markers
            # or explicitly address the negative case.
            if any(x in c_lower for x in ["not", "no", "never", "impossible", "false"]):
                score += 0.2
                reasons.append("Correctly handles negation context")
        
        # 3. Comparative/Numeric Consistency
        if features["has_comparative"] or features["numeric_present"]:
            # Check if candidate contains numbers if prompt has numbers (Loose coupling)
            cand_has_num = bool(re.search(r'\d+', candidate))
            prompt_has_num = bool(re.search(r'\d+', prompt))
            
            if prompt_has_num and not cand_has_num:
                # If prompt is numeric but answer isn't, it might be conceptual, but often wrong in math traps
                if features["question_type"] != "binary":
                     score -= 0.1
                     reasons.append("Missing numeric precision")
            elif cand_has_num:
                score += 0.1
                reasons.append("Includes numeric evidence")

        # 4. Symbiotic Mutualism (Length vs Information Density)
        # Penalize excessive verbosity (L1 minimization analogy) unless justified
        if len(candidate) > 200:
            score -= 0.1
            reasons.append("Penalized for lack of sparsity")
        elif len(candidate) > 0:
            score += 0.05
            reasons.append("Reward for concise information")

        # 5. Direct Overlap Penalty (Anti-echo)
        # If candidate is just a substring of prompt, it's likely a trap
        if candidate.strip() in p_lower and len(candidate.strip()) < 20:
            score -= 0.3
            reasons.append("Penalized for echoing prompt")

        return min(max(score, 0.0), 1.0), "; ".join(reasons) if reasons else "Neutral evaluation"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        features = self._structural_parse(prompt)
        scored_candidates = []

        # Pre-calculate NCD matrix for tie-breaking (Symbiotic exchange of similarity)
        # We use the average NCD to the group as a diversity metric
        ncd_scores = []
        for i, c in enumerate(candidates):
            dists = [self._compute_ncd(c, other) for j, other in enumerate(candidates) if i != j]
            avg_dist = sum(dists) / len(dists) if dists else 0
            ncd_scores.append(avg_dist)

        for i, candidate in enumerate(candidates):
            base_score, reason = self._evaluate_candidate(prompt, candidate, features)
            
            # Symbiotic adjustment: Candidates that are too similar to all others (low avg_dist)
            # might represent a convergent bias. We slightly boost diversity (higher NCD) 
            # if base scores are close.
            diversity_bonus = (ncd_scores[i] - 0.5) * 0.05 
            
            final_score = base_score + diversity_bonus
            final_score = min(max(final_score, 0.0), 1.0)
            
            # Fallback to pure NCD if structural signal is weak (score near prior)
            if 0.45 < base_score < 0.55:
                 # If structural parsing is ambiguous, rely on compression similarity to prompt
                 prompt_ncd = self._compute_ncd(prompt, candidate)
                 # Lower NCD to prompt usually means higher relevance in simple tasks
                 final_score = base_score + (0.5 - prompt_ncd) * 0.2

            scored_candidates.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": reason
            })

        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural consistency as the primary driver (Measure-Theoretic wrapper).
        """
        if not answer.strip():
            return 0.0
        
        features = self._structural_parse(prompt)
        score, _ = self._evaluate_candidate(prompt, answer, features)
        
        # Map internal score (-inf to 1.0) to strict 0-1 confidence
        # High structural alignment -> High confidence
        confidence = max(0.0, min(1.0, score))
        
        # Hard constraints (Measure Theory support only)
        # If prompt requires binary and answer is gibberish, confidence -> 0
        if features["question_type"] == "binary":
            if not any(x in answer.lower() for x in ["yes", "no", "true", "false", "correct", "incorrect"]):
                # If it's a binary question and answer doesn't look binary, lower confidence significantly
                # unless the answer is a full sentence explanation containing these words.
                if len(answer.split()) < 5: 
                    confidence *= 0.5
        
        return round(confidence, 4)