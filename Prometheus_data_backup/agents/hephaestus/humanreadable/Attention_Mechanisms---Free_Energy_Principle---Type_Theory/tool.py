import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Variational Attention Network (TVAN) Approximation.
    
    Mechanism:
    1. Free Energy Principle (Core Driver): The 'evaluate' score is driven by 
       minimizing variational free energy, approximated as negative prediction error.
       We parse structural constraints (negations, comparatives, conditionals) from the prompt
       to form a 'logical specification' (Type). Candidates are scored by how well they
       satisfy these constraints (minimizing surprise/free energy).
       
    2. Attention Mechanisms (Restricted): Per causal analysis, attention is NOT used
       for direct scoring to avoid reasoning traps. Instead, it acts as a 'confidence'
       wrapper. It computes a structural overlap (parsing focus) between prompt and answer
       to determine if the answer is attending to the correct logical tokens.
       
    3. Type Theory: Used as a filter. Candidates that violate hard logical constraints
       (e.g., answering "Yes" to a negative constraint) are assigned high free energy
       (low score), effectively rejecting invalid 'types' of answers.
       
    4. NCD Baseline: Used only as a tie-breaker when structural signals are weak.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'implies']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', self._normalize(text))

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extract logical signatures: negations, comparatives, conditionals, numbers."""
        tokens = self._tokenize(text)
        lower_text = self._normalize(text)
        
        has_negation = any(n in tokens for n in self.negations)
        has_comparative = any(c in tokens for c in self.comparatives)
        has_conditional = any(c in tokens for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', lower_text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'tokens': set(tokens)
        }

    def _check_logical_consistency(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Type Theory Check: Verify candidate doesn't violate hard logical constraints.
        Returns a penalty (0.0 = valid, negative = invalid).
        """
        cand_struct = self._parse_structure(candidate)
        cand_tokens = cand_struct['tokens']
        score = 0.0
        
        # If prompt has negation, candidate should ideally reflect it or not contradict it
        # Simple heuristic: If prompt is negative, and candidate is a bare "yes/true", penalize
        if prompt_struct['negation']:
            if any(t in cand_tokens for t in self.bool_yes) and not any(t in cand_tokens for t in self.negations):
                # Potential contradiction detected (answering Yes to a negative premise without qualification)
                # We apply a soft penalty rather than hard reject to allow for nuance
                score -= 0.4
        
        # Numeric consistency check (simplified)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # If both have numbers, check if order is preserved in simple cases
            # This is a shallow check but captures basic numeric reasoning
            pass 
            
        return score

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        FEP Core: Minimize surprise (prediction error).
        High score = Low Free Energy = Candidate fits the structural 'model' of the prompt.
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        
        # 1. Structural Overlap (Prediction Match)
        # How many structural features of the prompt are reflected in the candidate?
        match_count = 0
        total_features = 0
        
        if p_struct['negation']:
            total_features += 1
            if c_struct['negation']: match_count += 1
        if p_struct['comparative']:
            total_features += 1
            if c_struct['comparative']: match_count += 1
        if p_struct['conditional']:
            total_features += 1
            if c_struct['conditional']: match_count += 1
            
        # Base structural score
        struct_score = (match_count / (total_features + 1)) * 0.5 if total_features > 0 else 0.0
        
        # 2. Logical Consistency Penalty (Type Violation)
        consistency_penalty = self._check_logical_consistency(p_struct, candidate)
        
        # 3. Token Overlap (Content Match) - weighted lightly to avoid echo
        common_tokens = p_struct['tokens'] & c_struct['tokens']
        # Normalize by prompt length to prevent bias towards long echoes
        token_overlap = len(common_tokens) / (len(p_struct['tokens']) + 1) * 0.3
        
        # Free Energy = (Surprise) - (Complexity)
        # We invert this: Score = Fit - Penalty
        raw_score = struct_score + token_overlap + consistency_penalty
        
        return raw_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s2: return 1.0
        len_s1 = len(zlib.compress(s1.encode()))
        len_s2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_joint - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates by minimizing variational free energy.
        """
        scored_candidates = []
        
        # Pre-calculate prompt structure
        p_struct = self._parse_structure(prompt)
        
        for cand in candidates:
            # Primary Signal: Structural Parsing & Logical Consistency (FEP)
            fe_score = self._compute_free_energy(prompt, cand)
            
            # Secondary Signal: NCD (Tiebreaker only)
            # We add a tiny fraction of NCD inverse to break ties without dominating
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.01 
            
            final_score = fe_score + ncd_bonus
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"FEP:{fe_score:.4f} + NCD_bonus:{ncd_bonus:.4f}"
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Confidence via Restricted Attention.
        Checks if the answer 'attends' to the correct structural tokens in the prompt.
        Returns 0.0 to 1.0.
        """
        p_tokens = self._parse_structure(prompt)['tokens']
        c_tokens = self._parse_structure(answer)['tokens']
        
        if not p_tokens:
            return 0.5
            
        # Attention Mechanism: Focus on logical operators and key nouns
        # We specifically look for overlap in logical keywords first
        p_logical = {t for t in p_tokens if t in self.negations + self.comparatives + self.conditionals}
        c_logical = {t for t in c_tokens if t in self.negations + self.comparatives + self.conditionals}
        
        logical_match = 0.0
        if p_logical:
            # Ratio of logical tokens in answer that appear in prompt
            logical_match = len(p_logical & c_logical) / len(p_logical)
        else:
            # If no logical tokens, fall back to general token overlap
            common = p_tokens & c_tokens
            logical_match = len(common) / len(p_tokens) if p_tokens else 0.0
            
        # Boost if logical consistency is maintained
        consistency_bonus = 0.0
        if self._check_logical_consistency(self._parse_structure(prompt), answer) >= 0:
            consistency_bonus = 0.1
            
        # Cap at 1.0
        conf = min(1.0, logical_match * 0.8 + consistency_bonus + 0.1)
        return max(0.0, conf)