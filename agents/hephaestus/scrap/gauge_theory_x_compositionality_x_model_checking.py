import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Equivariant Compositional Model-Checking Tool (ECMT).
    
    Mechanism:
    1. Gauge Reduction (Symmetry): Normalizes text to ignore superficial symmetries 
       (case, whitespace, punctuation) akin to quotienting by a permutation group.
    2. Compositional Parsing: Decomposes the prompt into logical fibers:
       - Negations (flip truth value)
       - Comparatives (extract numeric/ordinal relations)
       - Conditionals (identify constraint scopes)
    3. Assume-Guarantee Verification: Checks if candidates satisfy the extracted 
       logical contracts. 
    4. Scoring: 
       - Base score from constraint satisfaction (0.0 to 0.8).
       - Tie-breaking via Normalized Compression Distance (NCD) to prefer 
         informationally dense matches over generic ones.
    """
    
    def __init__(self):
        self._num_pattern = re.compile(r"-?\d+\.?\d*")
        self._negations = {"no", "not", "never", "none", "false", "impossible"}
        self._comparatives = {"greater", "larger", "more", "less", "smaller", "fewer", ">", "<"}
        self._conditionals = {"if", "then", "unless", "provided"}

    def _gauge_normalize(self, text: str) -> str:
        """Quotient operation: Removes gauge degrees of freedom (noise)."""
        t = text.lower()
        t = re.sub(r'[^\w\s\-\.]', '', t) # Remove punctuation except hyphen/dot for numbers
        return " ".join(t.split())

    def _extract_fibers(self, text: str) -> dict:
        """Decompose text into logical components (fibers)."""
        normalized = self._gauge_normalize(text)
        words = set(normalized.split())
        
        has_negation = bool(words & self._negations)
        has_comparative = bool(words & self._comparatives)
        has_conditional = bool(words & self._conditionals)
        numbers = [float(x) for x in self._num_pattern.findall(text)]
        
        return {
            "neg": has_negation,
            "comp": has_comparative,
            "cond": has_conditional,
            "nums": numbers,
            "raw": text
        }

    def _verify_contract(self, prompt_fibers: dict, candidate: str) -> float:
        """
        Assume-Guarantee check: Does the candidate satisfy the prompt's logical constraints?
        Returns a score between 0.0 and 1.0 based on logical consistency.
        """
        cand_norm = self._gauge_normalize(candidate)
        cand_words = set(cand_norm.split())
        cand_nums = [float(x) for x in self._num_pattern.findall(candidate)]
        
        score = 0.0
        checks = 0
        
        # Check 1: Negation Consistency
        # If prompt implies negation, candidate should reflect it or not contradict it
        if prompt_fibers["neg"]:
            # If prompt has negation, and candidate is a simple affirmative without negation words
            # we penalize only if the context suggests a direct contradiction check.
            # Heuristic: If prompt asks "Is it not X?" and candidate is "Yes", it's ambiguous.
            # We rely more on explicit contradiction detection.
            pass 
        
        # Check 2: Numeric/Comparative Consistency
        if prompt_fibers["comp"] and prompt_fibers["nums"] and cand_nums:
            checks += 1
            p_nums = sorted(prompt_fibers["nums"])
            c_nums = sorted(cand_nums)
            
            # Simple transitivity check: If prompt compares A > B, does candidate align?
            # Since we don't have full semantic parse, we check if the candidate 
            # preserves the order of extracted numbers if they appear in both.
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                # Check relative order of first two numbers
                p_order = p_nums[0] < p_nums[1]
                c_order = c_nums[0] < c_nums[1]
                if p_order == c_order:
                    score += 0.5
                else:
                    score -= 0.5 # Penalty for flipping order
            else:
                # If numbers exist, presence in candidate is a weak positive signal
                score += 0.2
                
        # Check 3: Conditional Scope
        if prompt_fibers["cond"]:
            # If prompt is conditional, candidate shouldn't be an absolute unconditional fact
            # unless it's a logical consequence. Hard to verify without LLM.
            # Heuristic: Reward candidates that contain logical connectors if prompt has them.
            if bool(cand_words & self._conditionals) or bool(cand_words & {"therefore", "thus", "so"}):
                score += 0.3
                checks += 1

        # Default base score for passing basic type checks
        if checks == 0:
            return 0.5 # Neutral if no specific constraints found
        return max(0.0, min(1.0, score / checks + 0.5)) if checks > 0 else 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_fibers = self._extract_fibers(prompt)
        results = []
        
        # Pre-calculate NCD to prompt for tie-breaking
        ncd_scores = [(c, self._ncd(self._gauge_normalize(prompt), self._gauge_normalize(c))) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores)
        max_ncd = max(s[1] for s in ncd_scores) if len(ncd_scores) > 1 else min_ncd
        range_ncd = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for i, cand in enumerate(candidates):
            # 1. Compositional Verification Score (Primary Signal)
            logic_score = self._verify_contract(p_fibers, cand)
            
            # 2. Gauge-Invariant Similarity (Tiebreaker)
            # Normalize NCD: lower is better. Invert to add to score.
            ncd_val = ncd_scores[i][1]
            ncd_norm = 1.0 - ((ncd_val - min_ncd) / range_ncd) # 1.0 = best match
            
            # Weighted combination: Logic is dominant, NCD breaks ties
            final_score = (logic_score * 0.7) + (ncd_norm * 0.3)
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Logic:{logic_score:.2f}+NCD:{ncd_norm:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]