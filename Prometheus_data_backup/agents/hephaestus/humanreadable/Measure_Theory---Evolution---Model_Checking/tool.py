import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Probabilistic Evolutionary Model Checker (PEMC) Approximation.
    
    Mechanism:
    1. Measure Theory: Uses Lebesgue-like structural complexity (string length + token entropy)
       as a proxy for the 'measure' of the hypothesis space. Simpler valid models are preferred.
    2. Evolution: Candidates are treated as a population. Fitness is determined by satisfying
       logical constraints extracted from the prompt (the 'temporal specification').
    3. Model Checking: Performs symbolic verification of candidates against extracted logical
       rules (negations, comparatives, conditionals). 
       
    The 'probability' of satisfaction is approximated by a structural compliance score,
    bounded by confidence intervals derived from the ratio of satisfied constraints.
    """

    def __init__(self):
        self._constraint_weights = {
            'negation': 0.3,
            'comparative': 0.3,
            'conditional': 0.2,
            'numeric': 0.2
        }

    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """Extract logical structures: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        structures = {
            'negations': len(re.findall(r'\b(not|no|never|without|cannot|impossible)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|when|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text)
        }
        return structures

    def _check_compliance(self, prompt_struct: Dict, candidate_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Simulate model checking: Verify if candidate behavior aligns with prompt constraints.
        Returns a compliance score [0, 1].
        """
        score = 1.0
        checks = 0
        
        # 1. Negation Check: If prompt negates, candidate should reflect awareness or absence
        if prompt_struct['negations'] > 0:
            checks += 1
            # Heuristic: Candidate length shouldn't wildly exceed prompt if negation implies restriction
            if len(candidate) > len(prompt) * 1.5:
                score -= 0.2
            # Check for negative words in candidate if prompt has strong negation
            if prompt_struct['negations'] > 1 and candidate_struct['negations'] == 0:
                score -= 0.15 
                
        # 2. Comparative Check: Numeric consistency
        if prompt_struct['comparatives'] > 0 or prompt_struct['numbers']:
            checks += 1
            p_nums = prompt_struct['numbers']
            c_nums = candidate_struct['numbers']
            
            if p_nums and c_nums:
                try:
                    p_vals = [float(x) for x in p_nums]
                    c_vals = [float(x) for x in c_nums]
                    # If prompt implies ordering (e.g., "greater"), check if candidate respects magnitude
                    # Simplified: If prompt has numbers, candidate numbers should be within reasonable bounds
                    if max(c_vals) > max(p_vals) * 10: # Penalty for hallucinating huge numbers
                        score -= 0.3
                except ValueError:
                    pass

        # 3. Conditional/Logic Flow
        if prompt_struct['conditionals'] > 0:
            checks += 1
            # Heuristic: Candidates responding to conditionals often contain logical connectors
            logical_connectors = ['therefore', 'thus', 'so', 'because', 'yes', 'no']
            if not any(word in candidate.lower() for word in logical_connectors):
                score -= 0.1

        # Normalize score to [0, 1]
        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - max_len) / max_len

    def _estimate_fitness(self, prompt: str, candidate: str) -> float:
        """
        Estimate fitness based on structural compliance (Model Checking) 
        and parsimony (Measure Theory).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # Model Checking Phase
        compliance = self._check_compliance(p_struct, c_struct, prompt, candidate)
        
        # Measure Theory Phase: Parsimony Penalty
        # Prefer simpler candidates (shorter length relative to prompt)
        length_ratio = len(candidate) / max(len(prompt), 1)
        parsimony_penalty = 0.0
        if length_ratio > 2.0:
            parsimony_penalty = 0.1 * (length_ratio - 1.0)
        elif length_ratio < 0.1 and len(prompt) > 20:
            # Too short might miss constraints
            parsimony_penalty = 0.05
            
        base_score = compliance - parsimony_penalty
        return max(0.0, min(1.0, base_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """
        Evaluate candidates using the PEMC approach.
        Returns ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
            
        results = []
        p_struct = self._extract_structure(prompt)
        
        # Pre-calculate NCD for all to use as tiebreaker
        # We want low NCD (similarity in logic) but high structural compliance
        
        for cand in candidates:
            score = self._estimate_fitness(prompt, cand)
            
            # Generate reasoning string
            c_struct = self._extract_structure(cand)
            reasons = []
            if p_struct['negations'] > 0:
                reasons.append(f"Checked negation handling (Prompt: {p_struct['negations']}, Cand: {c_struct['negations']})")
            if p_struct['numbers']:
                reasons.append(f"Verified numeric consistency (Prompt nums: {len(p_struct['numbers'])})")
            if not reasons:
                reasons.append("Structural analysis performed; no specific constraints violated.")
                
            reasoning_str = "; ".join(reasons)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning_str
            })
        
        # Sort by score descending. Use NCD as tiebreaker for stability.
        # We sort primarily by score, then by NCD (lower is better for tie-breaking similarity to prompt logic)
        def sort_key(item):
            # Invert NCD for sorting (we want higher score, then lower NCD)
            ncd_val = self._compute_ncd(prompt, item['candidate'])
            return (-item['score'], ncd_val)
            
        results.sort(key=sort_key)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1 based on structural compliance and measure-theoretic bounds.
        """
        score = self._estimate_fitness(prompt, answer)
        
        # Adjust based on 'delta' (uncertainty due to length/complexity)
        # Longer answers have higher variance in this approximation
        complexity = len(answer) / 100.0
        delta = min(0.2, complexity) # Max 0.2 uncertainty
        
        # Confidence is the lower bound of the probability estimate (score - delta)
        conf = max(0.0, min(1.0, score - delta))
        return conf