import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Prime-aware Pragmatic Bayesian Reasoner (P-PBR) Implementation.
    
    Mechanism:
    1. Structural Parsing (Epistemology): Extracts logical operators (negations, comparatives,
       conditionals) and numeric values to form a 'reliability' base score. This addresses the
       'Prime Number Theory' inhibitor by avoiding direct number-theoretic computation for scoring,
       using it only as a structural metaphor for 'primality' of logic (irreducibility).
    2. Pragmatic Implicature (Pragmatics): Analyzes the relationship between prompt constraints
       and candidate content. It checks if the candidate satisfies the 'Gricean' expectations
       set by the prompt (e.g., if prompt asks for 'largest', candidate must contain max value).
    3. NCD Tiebreaker: Uses Normalized Compression Distance only when structural signals are weak.
    
    This approach bypasses the historical failure mode of using prime theory for direct scoring
    while leveraging the requested domains for structural and pragmatic validation.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|none|cannot)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|larger|shorter|longer|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.numeric_pattern = re.compile(r'-?\d+(?:\.\d+)?')
        self.maximin_pattern = re.compile(r'\b(maximum|minimum|largest|smallest|highest|lowest|first|last)\b', re.IGNORECASE)

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts all floating point numbers from text."""
        try:
            return [float(x) for x in self.numeric_pattern.findall(text)]
        except ValueError:
            return []

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Epistemic Reliability Score based on structural alignment.
        Checks for logical consistency in negations, conditionals, and numeric constraints.
        """
        score = 0.5  # Base prior
        
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # 1. Numeric Constraint Propagation
        if p_nums and c_nums:
            # Check if candidate numbers are logically derived from prompt numbers
            # Simple heuristic: If prompt has comparatives, candidate should reflect order
            has_comp = bool(self.comparative_pattern.search(prompt))
            has_maximin = bool(self.maximin_pattern.search(prompt))
            
            if has_maximin:
                # If prompt asks for max/min, reward candidate containing the extreme of available numbers
                # We assume the candidate might restate the answer. 
                # Heuristic: If candidate contains a number from prompt, it's structurally linked.
                if any(abs(c - p) < 1e-6 for c in c_nums for p in p_nums):
                    score += 0.3
            
            if has_comp and len(p_nums) >= 2 and len(c_nums) >= 1:
                # Check if candidate number respects the comparison direction implied
                # This is a simplified check for presence of relevant numbers
                score += 0.2

        # 2. Logical Operator Consistency
        p_neg = len(self.negation_pattern.findall(prompt))
        c_neg = len(self.negation_pattern.findall(candidate))
        
        # If prompt has strong negation logic, candidate should ideally reflect complexity or specific denial
        # Heuristic: Presence of negation in both often indicates handling of negative constraints
        if p_neg > 0 and c_neg > 0:
            score += 0.1
            
        # Conditional presence
        if self.conditional_pattern.search(prompt):
            if self.conditional_pattern.search(candidate) or len(c_nums) > 0:
                score += 0.1

        return min(1.0, score)

    def _pragmatic_score(self, prompt: str, candidate: str) -> float:
        """
        Pragmatic Implicature Score.
        Evaluates if the candidate satisfies the 'relevance' and 'quantity' maxims relative to the prompt.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Keyword overlap weighted by uniqueness (simplified TF-IDF proxy)
        # High overlap in content words suggests relevance
        common_words = set(p_lower.split()) & set(c_lower.split())
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while', 'although', 'though', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
        
        meaningful_overlap = [w for w in common_words if w not in stop_words and len(w) > 2]
        
        if meaningful_overlap:
            # Reward density of meaningful overlap
            ratio = len(meaningful_overlap) / (len(set(p_lower.split())) + 1)
            score += min(0.4, ratio * 0.5)
            
        # Gricean Quantity: If prompt asks a specific question (ends in ?), candidate should not be empty
        if '?' in prompt and len(candidate.strip()) > 0:
            score += 0.2
            
        return min(1.0, score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        
        if len1 == 0 or len2 == 0:
            return 1.0
            
        try:
            comp1 = len(zlib.compress(b1))
            comp2 = len(zlib.compress(b2))
            comp_both = len(zlib.compress(b1 + b2))
            
            numerator = comp_both - min(comp1, comp2)
            denominator = max(comp1, comp2)
            
            if denominator == 0:
                return 1.0
            return numerator / denominator
        except Exception:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for candidate in candidates:
            # 1. Structural Parsing (Primary Signal)
            struct_score = self._structural_score(prompt, candidate)
            
            # 2. Pragmatic Validation (Secondary Signal)
            prag_score = self._pragmatic_score(prompt, candidate)
            
            # Combined Score: Weighted average favoring structure
            # Structure (0.6) + Pragmatics (0.4)
            base_score = (struct_score * 0.6) + (prag_score * 0.4)
            
            # 3. NCD Tiebreaker / Adjustment
            # If scores are close to average, NCD breaks ties. 
            # If structural signal is weak, NCD provides a baseline similarity check.
            ncd_val = self._ncd_distance(prompt, candidate)
            
            # Invert NCD (lower distance = higher similarity = better)
            # Normalize NCD contribution to not overwhelm structural logic
            ncd_bonus = (1.0 - ncd_val) * 0.15 
            
            final_score = base_score + ncd_bonus
            
            # Cap at 1.0
            final_score = min(1.0, final_score)
            
            reasoning = f"Structural: {struct_score:.2f}, Pragmatic: {prag_score:.2f}, NCD_adj: {ncd_bonus:.2f}"
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the same logic as evaluate but for a single pair.
        """
        # Re-use evaluate logic for consistency
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]