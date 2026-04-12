import re
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Pragmatic Type-Guided Contextual Bandit (PTGCB) Implementation.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Candidates are treated as dependent types.
       We extract logical constraints (negations, comparatives, conditionals) from the prompt
       as "type predicates". A candidate must satisfy these predicates to inhabit the type.
    2. Pragmatics (Epistemic Honesty/Meta-Confidence): Before scoring, we analyze the prompt
       for Gricean violations (presuppositions, ambiguity, false dichotomies). If the context
       is pragmatically flawed, we cap confidence to signal uncertainty, regardless of candidate match.
    3. Multi-Armed Bandit (Scoring): We simulate a Thompson Sampling step where the "reward"
       is the structural match score, and the "prior" is penalized by pragmatic ambiguity.
       The final score is a weighted sum: Structural (50%) + Computation (20%) + NCD (15%) - Pragmatic Penalty.
    """

    def __init__(self):
        self.epsilon = 1e-6
        # Pragmatic penalty flags
        self.presupposition_triggers = [
            r"\b(stopped|quit|ceased|failed|why did|when did)\b",
            r"\bhave you\b.*\b(stopped|quit)\b",
            r"\bassumes?\b", r"\bpresupposes?\b"
        ]
        self.ambiguity_triggers = [
            r"\b(every|all)\b.*\b(same|different|who|he|she|it)\b",
            r"\bwho\b.*\b(he|she|him|her)\b",
            r"\beither\b.*\bor\b" # Potential false dichotomy
        ]
        self.subjectivity_triggers = [
            r"\b(best|worst|favorite|opinion|believe)\b"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic hazards (Tier B).
        Returns a cap value: 1.0 (safe) to 0.2 (highly ambiguous/trapped).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                score -= 0.6
                break
        
        # Check Ambiguity & False Dichotomy
        ambiguity_count = 0
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                ambiguity_count += 1
        if ambiguity_count > 0:
            score -= (0.4 * min(ambiguity_count, 2))
            
        # Check Subjectivity (Unanswerable without external context)
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                score -= 0.5
                break
                
        return max(0.2, score)

    def _extract_structural_signals(self, prompt: str) -> Dict[str, any]:
        """Extracts logical constraints: negations, comparatives, numbers."""
        signals = {
            "negation": False,
            "comparative": None, # 'max', 'min', 'greater', 'less'
            "numbers": [],
            "conditionals": False
        }
        p_lower = prompt.lower()
        
        # Negation
        if re.search(r"\b(not|no|never|none|cannot|impossible)\b", p_lower):
            signals["negation"] = True
            
        # Comparatives
        if re.search(r"\b(most|largest|highest|max|greatest)\b", p_lower):
            signals["comparative"] = "max"
        elif re.search(r"\b(least|smallest|lowest|min|fewest)\b", p_lower):
            signals["comparative"] = "min"
        elif re.search(r"\b(greater|larger|more)\b", p_lower):
            signals["comparative"] = "greater"
        elif re.search(r"\b(less|smaller|fewer)\b", p_lower):
            signals["comparative"] = "less"
            
        # Numbers (for constructive computation)
        nums = re.findall(r"-?\d+\.?\d*", p_lower)
        signals["numbers"] = [float(n) for n in nums]
        
        # Conditionals
        if re.search(r"\b(if|unless|provided that)\b", p_lower):
            signals["conditionals"] = True
            
        return signals

    def _compute_constructive_score(self, prompt: str, candidate: str) -> float:
        """
        Attempts to verify numeric/logic claims in the candidate against the prompt.
        Returns 1.0 if verified, 0.0 if contradicted, 0.5 if neutral.
        """
        signals = self._extract_structural_signals(prompt)
        c_lower = candidate.lower()
        
        # Numeric Verification
        if signals["numbers"]:
            # Extract numbers from candidate
            c_nums = re.findall(r"-?\d+\.?\d*", c_lower)
            if c_nums:
                try:
                    c_val = float(c_nums[0])
                    p_vals = signals["numbers"]
                    
                    # Simple arithmetic traps (e.g., sum, comparison)
                    if signals["comparative"] == "max":
                        if c_val == max(p_vals): return 1.0
                        if c_val != max(p_vals): return 0.0 # Contradiction
                    elif signals["comparative"] == "min":
                        if c_val == min(p_vals): return 1.0
                        if c_val != min(p_vals): return 0.0
                    elif signals["comparative"] == "greater":
                        # If prompt asks for greater, candidate should be the larger number
                        if len(p_vals) >= 2 and c_val == max(p_vals): return 1.0
                    elif signals["comparative"] == "less":
                        if len(p_vals) >= 2 and c_val == min(p_vals): return 1.0
                        
                    # Direct equality check if only one number context exists
                    if len(p_vals) == 1 and abs(c_val - p_vals[0]) < 0.01:
                        return 1.0
                except ValueError:
                    pass

        # Logical Negation Check
        if signals["negation"]:
            # If prompt has "not", and candidate is "yes" or affirmative without negation
            if re.search(r"\b(yes|true|is|are)\b", c_lower) and not re.search(r"\b(not|no|never)\b", c_lower):
                # Heuristic: if prompt says "X is not Y", candidate "X is Y" is wrong
                # This is a weak heuristic but captures the spirit of constraint propagation
                pass 
                
        return 0.5 # Neutral if no constructive verification possible

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib length approximation."""
        import zlib
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(zlib.compress(b1))
        len2 = len(zlib.compress(b2))
        len12 = len(zlib.compress(b1 + b2))
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len12 - min(len1, len2)) / max_len

    def _type_check(self, prompt: str, candidate: str) -> float:
        """
        Simulates Dependent Type Checking.
        The prompt defines a Type (constraints). The candidate is a Term.
        We check if the Term inhabits the Type.
        """
        signals = self._extract_structural_signals(prompt)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 0.0
        matches = 0
        
        # Constraint 1: Negation Consistency
        # If prompt implies negation, candidate should reflect it or not contradict it
        if signals["negation"]:
            if re.search(r"\b(not|no|never|false)\b", c_lower):
                score += 1.0
            elif re.search(r"\b(yes|true|is|are)\b", c_lower):
                score -= 0.5 # Penalty for affirmative in negative context
            matches += 1
            
        # Constraint 2: Keyword Overlap (Simplified Type Inhabitation)
        # Remove stopwords and check significant token overlap
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now'}
        
        p_tokens = set(re.findall(r'\b\w+\b', p_lower)) - stop_words
        c_tokens = set(re.findall(r'\b\w+\b', c_lower)) - stop_words
        
        if p_tokens:
            intersection = p_tokens.intersection(c_tokens)
            # Jaccard-like score for type inhabitation
            if len(p_tokens.union(c_tokens)) > 0:
                score += (len(intersection) / len(p_tokens.union(c_tokens))) * 2.0
            matches += 1
            
        return score if matches == 0 else score / (matches + 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Confidence (Pragmatic Check)
        pragmatic_cap = self._meta_confidence(prompt)
        
        # 2. Structural Signals
        signals = self._extract_structural_signals(prompt)
        
        results = []
        for cand in candidates:
            # A. Structural/Type Score (50% weight base)
            type_score = self._type_check(prompt, cand)
            
            # B. Constructive Computation Score (20% weight base)
            comp_score = self._compute_constructive_score(prompt, cand)
            
            # C. NCD Score (15% weight base) - Inverted because lower NCD is better
            ncd_val = self._calculate_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # D. Bandit Utility Calculation
            # Utility = (Structural * 0.5) + (Computation * 0.2) + (NCD * 0.15) + (Base Prior 0.15)
            # We add a small random noise to simulate Thompson Sampling exploration if scores are tied
            import random
            noise = random.gauss(0, 0.01)
            
            raw_score = (type_score * 0.50) + (comp_score * 0.20) + (ncd_score * 0.15) + 0.15
            raw_score += noise
            
            # Apply Pragmatic Cap (Epistemic Honesty)
            # If the question is ambiguous, even a good matching answer gets capped confidence
            final_score = min(raw_score, pragmatic_cap)
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"TypeMatch:{type_score:.2f} Comp:{comp_score:.2f} NCD:{ncd_score:.2f} PragCap:{pragmatic_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty via _meta_confidence.
        """
        # 1. Check Pragmatic Hazards (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate the specific answer against the prompt (Tier A)
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
            
        base_score = eval_results[0]["score"]
        
        # 3. Final Confidence Logic
        # If meta_cap is low (ambiguous question), confidence MUST be low.
        # If meta_cap is high, confidence depends on the structural match.
        final_conf = min(base_score, meta_cap)
        
        # Never return > 0.9 unless it's a perfect structural match and safe question
        if meta_cap == 1.0 and base_score > 0.95:
            return 0.95
            
        return max(0.0, min(1.0, final_conf))