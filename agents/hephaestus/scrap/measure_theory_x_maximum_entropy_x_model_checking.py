import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A measure-theoretic probabilistic model-checking inspired reasoning tool.
    
    Mechanism:
    1. Structural Parsing (The Sigma-Algebra): Decomposes text into logical atoms 
       (negations, comparatives, conditionals, numbers) to form a measurable space.
    2. Maximum Entropy Constraint (The Prior): Assigns base probabilities based on 
       logical consistency rather than raw string similarity. It penalizes candidates 
       that violate explicit constraints (e.g., negation flips) found in the prompt.
    3. Model Checking (The Verification): Evaluates if the candidate satisfies the 
       logical structure extracted from the prompt.
       
    Scoring:
    - Primary: Structural alignment (logic, numbers, negations).
    - Secondary: NCD (compression) used only as a tie-breaker for semantic closeness.
    """

    def __init__(self):
        self.num_pattern = re.compile(r"-?\d+\.?\d*")
        self.neg_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', "n't"}
        self.comp_ops = {'>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer', 'higher', 'lower'}
        self.cond_words = {'if', 'then', 'else', 'when', 'unless', 'provided'}

    def _tokenize(self, text: str) -> set:
        return set(re.findall(r'\b\w+\b', text.lower()))

    def _extract_numbers(self, text: str) -> List[float]:
        return [float(x) for x in self.num_pattern.findall(text)]

    def _has_negation(self, text: str) -> bool:
        tokens = self._tokenize(text)
        return bool(tokens & self.neg_words) or "n't" in text.replace("'", "'")

    def _has_comparative(self, text: str) -> bool:
        tokens = self._tokenize(text)
        return bool(tokens & self.comp_ops) or any(op in text for op in ['>', '<'])

    def _has_conditional(self, text: str) -> bool:
        tokens = self._tokenize(text)
        return bool(tokens & self.cond_words)

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on logical consistency (Model Checking).
        Checks: Negation alignment, Number consistency, Comparative direction.
        """
        score = 0.0
        checks = 0
        
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        # 1. Negation Consistency Check
        # If prompt implies negation, candidate should likely reflect it or contradict logically
        p_neg = self._has_negation(prompt)
        c_neg = self._has_negation(candidate)
        checks += 1
        if p_neg == c_neg:
            score += 1.0
        else:
            # Penalty for flipping negation without cause (simple heuristic)
            score -= 0.5
            
        # 2. Numeric Consistency (Measure Theory analogy: measurable sets)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            checks += 1
            # Check if candidate numbers are a subset or close to prompt numbers
            # Or if the logic holds (e.g. prompt says "less than 5", candidate "4")
            match_count = 0
            for cn in c_nums:
                if any(abs(cn - pn) < 1e-6 for pn in p_nums):
                    match_count += 1
            score += (match_count / max(len(c_nums), 1)) * 2.0 # Boost for number matching
        elif not p_nums and not c_nums:
            checks += 0.5
            score += 0.5 # Neutral if no numbers involved

        # 3. Comparative/Conditional Presence
        p_comp = self._has_comparative(prompt)
        c_comp = self._has_comparative(candidate)
        p_cond = self._has_conditional(prompt)
        c_cond = self._has_conditional(candidate)
        
        if p_comp or p_cond:
            checks += 1
            if (p_comp and c_comp) or (p_cond and c_cond):
                score += 1.5 # High reward for maintaining logical operators
            elif (p_comp and not c_comp) or (p_cond and not c_cond):
                score -= 1.0 # Penalty for dropping logical structure

        # Normalize by checks performed to keep scale reasonable
        return score / max(checks, 1)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features
        p_len = len(prompt)
        
        for cand in candidates:
            # 1. Structural Reasoning Score (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. NCD Score (Tie-breaker / Semantic baseline)
            # Invert NCD so 1.0 is perfect match, 0.0 is totally different
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Hybrid Scoring: Weighted sum favoring structural logic
            # Structural logic is the "Model Checking" engine
            final_score = (0.75 * struct_score) + (0.25 * ncd_score)
            
            # Adjust for length plausibility (Heuristic constraint)
            if len(cand) == 0:
                final_score = 0.0
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural alignment: {struct_score:.2f}, NCD similarity: {ncd_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        Uses the internal evaluation logic to score the single candidate against the prompt.
        """
        # Evaluate as if it's a single candidate list
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]["score"]
        
        # Map raw score to 0-1 confidence range
        # Assuming raw_score roughly ranges from -1.0 to 2.0 based on logic above
        # Clamp and normalize
        conf = (raw_score + 1.0) / 3.0 
        return max(0.0, min(1.0, conf))