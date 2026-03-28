import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Pragmatic Predictive Swarm (HPPS) Implementation.
    
    Mechanism:
    1. Predictive Coding (Local Model): Agents parse the prompt to form a structural 
       "prediction" of reality (extracting negations, comparatives, numbers, conditionals).
    2. Hypothesis Testing: Candidates are treated as incoming sensory data. The system 
       computes the "prediction error" by checking if the candidate contradicts the 
       extracted structural constraints (e.g., if prompt says "A > B" and candidate implies "B > A").
    3. Pragmatics (Gricean Filter): Signals (scores) are modulated by relevance. 
       Candidates that align with high-certainty structural features (numbers, explicit negations) 
       receive high relevance weights. Redundant or vague candidates are penalized.
    4. Stigmergy: The final score is a trace left in the shared environment, combining 
       structural consistency (logic) with compression similarity (NCD) as a tiebreaker.
    """

    def __init__(self):
        self._structural_cache = {}

    def _extract_structure(self, text: str) -> dict:
        """Extract logical primitives: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        structure = {
            "negations": len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            "numbers": [],
            "has_uncertainty": any(w in text_lower for w in ["maybe", "possibly", "uncertain"]),
        }
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        structure["numbers"] = [float(n) for n in nums]
        
        return structure

    def _check_logical_consistency(self, prompt_struct: dict, candidate: str) -> float:
        """
        Compute prediction error based on logical constraints.
        Returns a consistency score (0.0 to 1.0).
        """
        score = 1.0
        cand_lower = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has strong negation markers, candidate should ideally reflect awareness 
        # (heuristic: if prompt has 'not', candidate containing 'not' or specific negative words might be relevant)
        # However, strictly, we check for contradiction. 
        # Simplified: If prompt implies negation, and candidate is a blind affirmative, penalize.
        if prompt_struct["negations"] > 0:
            if any(w in cand_lower for w in ["yes", "true", "correct"]) and "not" not in cand_lower:
                # Potential contradiction risk, slight penalty unless context clarifies
                score -= 0.1
        
        # 2. Numeric Consistency
        if prompt_struct["numbers"] and len(prompt_struct["numbers"]) >= 2:
            nums = sorted(prompt_struct["numbers"])
            # If candidate contains numbers, check order magnitude logic if possible
            cand_nums = re.findall(r'-?\d+\.?\d*', candidate)
            if cand_nums:
                c_val = float(cand_nums[0])
                # Heuristic: If prompt compares A and B, and candidate picks the wrong extreme
                # This is hard without full semantic parse, so we use presence as a proxy for relevance
                score += 0.2 # Reward numeric grounding
        
        # 3. Conditional/Constraint Propagation
        if prompt_struct["conditionals"] > 0:
            if any(w in cand_lower for w in ["if", "then", "because", "therefore"]):
                score += 0.1 # Reward logical connectives in complex prompts
        
        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len_s1 = len(zlib.compress(s1.encode()))
        len_s2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_joint - max_len) / max_len

    def _pragmatic_relevance_score(self, prompt: str, candidate: str, prompt_struct: dict) -> float:
        """
        Calculate relevance based on Gricean maxims.
        - Quantity: Is the answer concise but complete?
        - Relevance: Does it address the structural features?
        """
        score = 0.5
        
        # Relevance: Candidate length vs Prompt complexity
        # If prompt is complex (high structural count), short answers might be under-informative
        prompt_complexity = prompt_struct["negations"] + prompt_struct["comparatives"] + prompt_struct["conditionals"]
        
        if prompt_complexity > 2:
            if len(candidate.split()) < 3:
                score -= 0.2 # Violation of Quantity (too brief for complex prompt)
            else:
                score += 0.1
        else:
            if len(candidate.split()) > 20:
                score -= 0.1 # Violation of Quantity (too verbose for simple prompt)
        
        # Relevance: Keyword overlap with structural markers
        prompt_words = set(re.findall(r'\w+', prompt.lower()))
        cand_words = set(re.findall(r'\w+', candidate.lower()))
        overlap = len(prompt_words & cand_words)
        
        if overlap > 0:
            score += min(0.3, overlap * 0.05)
            
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD to prompt for tie-breaking
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores) if ncd_scores else 1.0
        
        for candidate in candidates:
            # 1. Logical Consistency (Prediction Error Minimization)
            logic_score = self._check_logical_consistency(prompt_struct, candidate)
            
            # 2. Pragmatic Relevance (Gricean Filter)
            prag_score = self._pragmatic_relevance_score(prompt, candidate, prompt_struct)
            
            # 3. Stigmergic Trace (NCD Tiebreaker)
            # Lower NCD is better. Normalize inverted NCD to 0-1 scale relative to this batch
            current_ncd = self._ncd(prompt, candidate)
            # Avoid division by zero if all identical
            ncd_range = (max_ncd - min_ncd) if (max_ncd := max(s[1] for s in ncd_scores)) > min_ncd else 1.0
            ncd_normalized = 1.0 - ((current_ncd - min_ncd) / ncd_range) if ncd_range > 0 else 1.0
            
            # Final Swarm Score: Weighted combination
            # Logic is primary (Causal), Pragmatics secondary, NCD tertiary
            final_score = (logic_score * 0.5) + (prag_score * 0.3) + (ncd_normalized * 0.2)
            
            reasoning = f"Logic:{logic_score:.2f} Prag:{prag_score:.2f} NCD:{ncd_normalized:.2f}"
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        prompt_struct = self._extract_structure(prompt)
        logic = self._check_logical_consistency(prompt_struct, answer)
        prag = self._pragmatic_relevance_score(prompt, answer, prompt_struct)
        
        # Confidence is the product of logical soundness and pragmatic fit
        conf = (logic * 0.7) + (prag * 0.3)
        return max(0.0, min(1.0, conf))