import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gauge-Equivariant Sparse Compositional Encoder (GESCE) Approximation.
    
    Mechanism:
    1. Base Space (Context): Extracts structural features (negations, comparatives, numbers).
    2. Fiber Bundle (Roles): Maps tokens to semantic roles (Agent, Action, Patient) via simple heuristics.
    3. Gauge Group (Invariance): Checks if candidate answers preserve the 'charge' (logical consistency) 
       of the prompt's structural constraints. Violations increase the 'gauge penalty'.
    4. Sparse Encoder: Uses a high-sparsity keyword match (L1-like) to identify relevant logical operators.
    
    Scoring:
    Score = (Structural Consistency * 0.6) + (Semantic Overlap * 0.3) + (NCD Tiebreaker * 0.1)
    """

    def __init__(self):
        # Structural keywords acting as "gauge fields" for logic
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'before', 'after'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self.quantifiers = {'all', 'some', 'every', 'each', 'any', 'most'}
        
        # Role assignment heuristics (Simplified Fiber Bundle)
        self.role_keywords = {
            'agent': ['who', 'person', 'man', 'woman', 'they', 'he', 'she', 'it'],
            'action': ['run', 'go', 'make', 'do', 'create', 'kill', 'build', 'is', 'are'],
            'patient': ['what', 'object', 'thing', 'him', 'her', 'them']
        }

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict[str, any]:
        tokens = set(self._tokenize(text))
        nums = re.findall(r'-?\d+\.?\d*', text)
        
        has_neg = bool(tokens & self.negations)
        has_comp = bool(tokens & self.comparatives)
        has_cond = bool(tokens & self.conditionals)
        has_quant = bool(tokens & self.quantifiers)
        
        # Numeric evaluation signal
        numeric_val = 0.0
        if nums:
            try:
                numeric_val = float(nums[0])
            except ValueError:
                pass

        return {
            'neg_count': sum(1 for t in tokens if t in self.negations),
            'comp_count': sum(1 for t in tokens if t in self.comparatives),
            'cond_count': sum(1 for t in tokens if t in self.conditionals),
            'has_nums': len(nums) > 0,
            'numeric_val': numeric_val,
            'tokens': tokens
        }

    def _gauge_covariance_penalty(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Calculates a penalty based on gauge symmetry breaking.
        If the prompt has strong logical operators (negation/conditionals), 
        the answer must reflect compatible structural complexity.
        """
        penalty = 0.0
        
        # Symmetry 1: Negation Conservation
        # If prompt is heavily negated, a valid answer often needs to acknowledge it 
        # (or explicitly reverse it). Simple heuristic: mismatched negation counts reduce score.
        if prompt_struct['neg_count'] > 0:
            if cand_struct['neg_count'] == 0:
                # Potential gauge violation: ignoring negation context
                penalty += 0.2
        
        # Symmetry 2: Conditional Consistency
        if prompt_struct['cond_count'] > 0:
            if cand_struct['cond_count'] == 0 and prompt_struct['cond_count'] > 1:
                penalty += 0.1
                
        # Symmetry 3: Numeric Transitivity (Simplified)
        # If prompt has numbers, candidate ignoring them is suspicious
        if prompt_struct['has_nums'] and not cand_struct['has_nums']:
            # Check if candidate is just a generic "Yes/No"
            cand_text = " ".join(cand_struct['tokens'])
            if len(cand_text) < 10 or cand_text in ['yes', 'no', 'true', 'false']:
                penalty += 0.3

        return min(penalty, 1.0)

    def _sparse_compositional_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates sparse autoencoder dictionary matching.
        High weight on logical operators and role-preserving tokens.
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        # Intersection of significant tokens (Sparse basis)
        significant = p_tokens & c_tokens
        
        # Weight logical operators higher (Sparsity constraint)
        logic_weights = 0.0
        for token in significant:
            if token in self.negations or token in self.comparatives or token in self.conditionals:
                logic_weights += 2.0
            elif token in self.quantifiers:
                logic_weights += 1.5
            else:
                logic_weights += 0.5
        
        if not p_tokens:
            return 0.0
            
        # Normalize by prompt complexity (L1 normalization approximation)
        return logic_weights / (len(p_tokens) + 1)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximated here for stability
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        numerator = len_concat - min(comp1, comp2)
        denominator = max(comp1, comp2)
        if denominator == 0:
            return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []
        
        # Pre-calculate prompt stats for gauge reference
        p_len = len(prompt)
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural/Gauge Score (Primary Signal)
            gauge_penalty = self._gauge_covariance_penalty(prompt_struct, cand_struct)
            structural_score = 1.0 - gauge_penalty
            
            # Boost if candidate explicitly resolves a conditional or negation found in prompt
            if prompt_struct['neg_count'] > 0 and cand_struct['neg_count'] > 0:
                structural_score = min(1.0, structural_score + 0.1)
                
            # 2. Sparse Compositional Score (Secondary Signal)
            sparse_score = self._sparse_compositional_score(prompt, cand)
            # Normalize sparse score roughly to 0-1 range based on heuristic max
            sparse_score = min(1.0, sparse_score * 2.0) 
            
            # 3. NCD Tiebreaker (Tertiary)
            # Inverted NCD (higher is better)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Weighted Combination
            # Structural reasoning is prioritized over simple string overlap
            final_score = (structural_score * 0.6) + (sparse_score * 0.3) + (ncd_score * 0.1)
            
            reasoning = f"GaugePenalty:{gauge_penalty:.2f}, Sparse:{sparse_score:.2f}, NCD:{ncd_val:.2f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on gauge consistency and structural alignment.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize the top score to a confidence metric
        # A perfect structural match yields ~0.9+, a random one ~0.3-0.5
        raw_score = results[0]['score']
        
        # Map raw score to confidence curve
        # Assuming random noise is ~0.3, perfect is ~1.0
        conf = max(0.0, min(1.0, (raw_score - 0.3) / 0.7))
        return conf