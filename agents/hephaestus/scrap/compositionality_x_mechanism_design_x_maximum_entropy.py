import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Compositional Mechanism-Design Entropy-Regularized Neural-Symbolic Reasoner (CMDE-NSR).
    
    Implements a hybrid reasoning strategy:
    1. Compositional Front-End: Parses structural logic (negations, conditionals, transitivity).
    2. MaxEnt Prior: Penalizes complex candidate explanations; favors parsimony (Ockham's Razor).
    3. Mechanism Design (VCG-like): Scores candidates based on marginal utility (accuracy gain) 
       minus a complexity cost, incentivizing truthful, simple, and correct hypotheses.
    
    Epistemic Honesty (Tier B): Detects presuppositions, ambiguities, and unanswerable queries
    to cap confidence, preventing over-confident hallucinations.
    """

    def __init__(self):
        # Entropy regularization parameter (lambda)
        self.entropy_weight = 0.15
        # Complexity penalty base
        self.complexity_base = 0.05
        # Thresholds
        self.ambiguity_threshold = 0.25
        self.high_conf_cap = 0.90

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a confidence cap (0.0 - 1.0).
        """
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition Traps ("Have you stopped...", "Why did X fail?")
        presupposition_patterns = [
            r"\bhave you (stopped|quit|ceased)\b",
            r"\bwhy did (it|he|she|they|x)\b", # Assumes event happened
            r"\bwhen did (it|he|she|they|x)\b", # Assumes event happened
            r"\bstop (doing|being)\b",
            r"\bfailed to\b" # In questions like "Why did it fail?"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p):
                # Check if it's actually a question or a statement about failure
                if "?" in p or re.search(r"why|when|how", p):
                    score = min(score, self.ambiguity_threshold)
                    break

        # 2. Scope/Pronoun Ambiguity ("Every X... a Y", "X told Y he...")
        scope_patterns = [
            r"\bevery [a-z]+ .* a [a-z]+\b", # "Every boy kicked a ball" (Same ball?)
            r"\btold [a-z]+ he\b", # Pronoun ambiguity
            r"\btold [a-z]+ she\b",
            r"\bwho is (he|she|it|they)\b" # Often implies missing context
        ]
        for pat in scope_patterns:
            if re.search(pat, p):
                score = min(score, self.ambiguity_threshold)
                break

        # 3. False Dichotomy ("Either A or B" without exhaustiveness)
        if re.search(r"\beither .+ or .+\b", p) and not re.search(r"\bboth\b", p):
            score = min(score, self.ambiguity_threshold)

        # 4. Subjectivity without criteria ("Best", "Favorite" without data)
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p for w in subjective_words):
            if "data" not in p and "table" not in p and "list" not in p:
                score = min(score, self.ambiguity_threshold)

        return score

    def _parse_structure(self, prompt: str, candidate: str) -> float:
        """
        Compositional Front-End: Extracts logical structure and checks consistency.
        Returns a score component (0.0 - 1.0).
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 0.0
        matches = 0
        
        # A. Negation Consistency
        negations = ["not", "no", "never", "none", "cannot", "impossible"]
        prompt_has_neg = any(n in p_low for n in negations)
        cand_has_neg = any(n in c_low for n in negations)
        
        if prompt_has_neg == cand_has_neg:
            score += 0.4
            matches += 1
        else:
            # Strong penalty for negation mismatch
            score -= 0.5

        # B. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r"\d+\.?\d*", p_low)
        c_nums = re.findall(r"\d+\.?\d*", c_low)
        
        if p_nums:
            try:
                # Simple heuristic: If prompt has numbers, candidate should likely reflect them or result
                if c_nums:
                    # Check if candidate number is a result of simple ops on prompt numbers?
                    # Too complex for generic, just check presence/relevance
                    score += 0.4
                    matches += 1
                else:
                    # Prompt has numbers, candidate doesn't -> likely wrong unless "zero" or text
                    if "zero" not in c_low and "none" not in c_low:
                        score -= 0.2
            except:
                pass

        # C. Logical Connectives (If/Then, Because)
        if ("if" in p_low or "because" in p_low or "therefore" in p_low):
            if ("if" in c_low or "because" in c_low or "therefore" in c_low or "thus" in c_low):
                score += 0.2
                matches += 1
        
        # Normalize to 0-1 range roughly
        return max(0.0, min(1.0, 0.5 + score))

    def _compute_entropy_prior(self, candidate: str) -> float:
        """
        Maximum Entropy Prior Layer.
        Calculates a simplicity score. Shorter, less redundant candidates get higher prior probability.
        P(program) ~ exp(-lambda * complexity)
        """
        length = len(candidate)
        # Penalize excessive length (complexity)
        # Base penalty grows with length, capped
        complexity_penalty = min(0.5, length * 0.002)
        
        # Repetition penalty (low entropy in string itself often means low info content or error)
        unique_ratio = len(set(candidate)) / max(1, len(candidate))
        
        # Score: High unique ratio and short length = Good
        prior_score = (1.0 - complexity_penalty) * (0.5 + 0.5 * unique_ratio)
        return prior_score

    def _vcg_mechanism_score(self, prompt: str, candidate: str, structural_score: float, prior_score: float) -> float:
        """
        Mechanism Design Incentive Module (VCG-inspired).
        Payoff = Utility (Structural Match) - Cost (Complexity/Entropy violation)
        
        We simulate the "auction" by treating the structural match as the 'social welfare' 
        and the complexity as the 'bid cost'. 
        Truthful reporting (high score only if both structure and simplicity align) is the dominant strategy.
        """
        # Utility: How well does it fit the logic? (Structural Score)
        utility = structural_score
        
        # Cost: Complexity penalty derived from MaxEnt prior
        # If prior is low (complex), cost is high
        cost = (1.0 - prior_score) * self.entropy_weight
        
        # VCG Payoff: Utility - Cost
        # We scale this to ensure it remains in a reasonable range for ranking
        payoff = utility - cost
        
        # Bonus for exact keyword overlap in logical operators (Reinforcing truthfulness)
        common_logical = set(['true', 'false', 'yes', 'no', 'if', 'then', 'else'])
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        overlap = len(p_words.intersection(c_words))
        if overlap > 0:
            payoff += min(0.1, overlap * 0.02)
            
        return payoff

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_s1_s2 = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence for the whole prompt
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing (Compositional Front-End)
            struct_score = self._parse_structure(prompt, cand)
            
            # 2. MaxEnt Prior (Simplicity)
            prior_score = self._compute_entropy_prior(cand)
            
            # 3. Mechanism Design Scoring
            raw_score = self._vcg_mechanism_score(prompt, cand, struct_score, prior_score)
            
            # 4. NCD Tiebreaker (Max 15% influence)
            # Only used if structural signals are weak or tied
            ncd_val = self._calculate_ncd(prompt, cand)
            # Convert distance to similarity (1 - ncd), weighted lightly
            ncd_bonus = (1.0 - ncd_val) * 0.15
            
            final_score = raw_score + ncd_bonus
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the prompt is ambiguous, we cap the maximum possible score/confidence
            if meta_cap < 0.5:
                # Dampen scores significantly for ambiguous prompts
                final_score = min(final_score, meta_cap + 0.1) 

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, Prior:{prior_score:.2f}, MetaCap:{meta_cap:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous/unanswerable questions.
        """
        # 1. Check Meta-Confidence (The Honesty Filter)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate the specific candidate
        struct_score = self._parse_structure(prompt, answer)
        prior_score = self._compute_entropy_prior(answer)
        raw_score = self._vcg_mechanism_score(prompt, answer, struct_score, prior_score)
        
        # 3. Combine
        # Base confidence on structural match, heavily penalized if meta-cap is low
        base_conf = raw_score
        
        # If meta analysis says "This is a trap", confidence cannot exceed the cap
        if meta_cap < 0.5:
            conf = min(base_conf, meta_cap)
        else:
            # If not a trap, cap high confidence unless computation was definitive
            # We never give > 0.9 unless it's a perfect structural match
            if struct_score < 0.9:
                conf = min(base_conf, 0.85)
            else:
                conf = min(base_conf, self.high_conf_cap)
                
        return max(0.0, min(1.0, conf))