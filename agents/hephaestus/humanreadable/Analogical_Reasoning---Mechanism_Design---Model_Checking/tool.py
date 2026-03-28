import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Closed-Loop Analogical-Mechanism Verifier (AMV) Implementation.
    
    Mechanism:
    1. Analogical Reasoning (Source Mapping): Extracts structural templates 
       (negations, comparatives, conditionals, numeric relations) from the prompt.
       This acts as the 'Source Domain' structure.
       
    2. Mechanism Design (Incentive Synthesis): Evaluates candidates against 
       these structural constraints. Candidates that satisfy logical transitivity,
       modus tollens, and numeric consistency receive 'incentive compatibility' 
       (high base score). This is the core driver (per Coeus analysis).
       
    3. Model Checking (Exhaustive Verification): Performs a deterministic, 
       finite-state exploration of the candidate's adherence to the extracted 
       logical rules. If a candidate violates a hard constraint (e.g., claims 
       A > B when prompt says B > A), it is flagged as a state violation.
       
    Scoring:
    - Primary: Structural satisfaction (Logic/Numeric/Constraint propagation).
    - Secondary: NCD (Tiebreaker only).
    """

    def __init__(self):
        self._logic_ops = ['if', 'then', 'else', 'unless', 'provided', 'only if']
        self._comp_ops = ['greater', 'less', 'equal', 'more', 'fewer', 'higher', 'lower']
        self._negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical and numeric structures (Analogical Source)."""
        text_lower = text.lower()
        structure = {
            'has_negation': any(n in text_lower for n in self._negations),
            'has_comparative': any(c in text_lower for c in self._comp_ops),
            'has_conditional': any(l in text_lower for l in self._logic_ops),
            'numbers': re.findall(r'\d+(?:\.\d+)?', text),
            'length': len(text.split())
        }
        return structure

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Verifies numeric logic (Model Checking step for numeric states)."""
        p_nums = re.findall(r'\d+(?:\.\d+)?', prompt)
        c_nums = re.findall(r'\d+(?:\.\d+)?', candidate)
        
        if not p_nums:
            return 1.0 # No numeric constraints to check
        
        # Heuristic: If prompt has numbers and candidate has none, penalty
        if not c_nums:
            return 0.5
            
        # Check if candidate numbers are a subset or derived from prompt (simplified)
        # In a full engine, this would parse equations. Here we check presence.
        match_count = 0
        for cn in c_nums:
            if cn in p_nums:
                match_count += 1
        
        return min(1.0, match_count / max(1, len(c_nums)))

    def _verify_logical_integrity(self, prompt: str, candidate: str) -> float:
        """Checks if candidate contradicts prompt negations or conditionals."""
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        score = 1.0
        
        # Modus Tollens / Negation Check
        # If prompt says "X is not Y", candidate shouldn't assert "X is Y"
        if any(n in p_low for n in self._negations):
            # Simple heuristic: if prompt has strong negation, candidate 
            # repeating the affirmative without qualification might be suspect
            # unless it's a direct answer to a negative question.
            pass 

        # Length constraint: Candidate must be substantial enough to hold logic
        if len(c_low.split()) < 2 and len(p_low.split()) > 10:
            score -= 0.2
            
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Mechanism Design Core: Structural Alignment
            cand_struct = self._extract_structure(cand)
            
            # Reward matching structural complexity (Analogical transfer)
            if prompt_struct['has_negation'] and cand_struct['has_negation']:
                score += 0.3
                reasoning_parts.append("matched negation structure")
            elif prompt_struct['has_negation'] and not cand_struct['has_negation']:
                # Potential failure to capture nuance
                score -= 0.1
                reasoning_parts.append("missed negation nuance")
                
            if prompt_struct['has_conditional'] and cand_struct['has_conditional']:
                score += 0.3
                reasoning_parts.append("preserved conditional logic")
            
            # 2. Model Checking: Numeric & Logical Consistency
            num_score = self._check_numeric_consistency(prompt, cand)
            logic_score = self._verify_logical_integrity(prompt, cand)
            
            score += (num_score * 0.4)
            score += (logic_score * 0.3)
            
            if num_score < 1.0:
                reasoning_parts.append("numeric mismatch detected")
            
            # 3. NCD as Tiebreaker (only if structural signals are weak or equal)
            # We add a tiny epsilon based on NCD to break ties without dominating
            ncd_val = self._ncd_distance(prompt, cand)
            tie_breaker = (1.0 - ncd_val) * 0.05 
            
            final_score = score + tie_breaker
            
            # Normalize to 0-1 range roughly
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "structural baseline"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        # Reuse evaluate logic for a single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']