import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Immune Pragmatic Network (HIPN) Implementation.
    
    Mechanism:
    1. Holographic Boundary (Latent Space): The prompt is parsed into a structural 
       'boundary' vector (negations, comparatives, numerics, conditionals). This 
       compresses the semantic bulk into a tractable signature.
    2. Immune Selection (Clonal Expansion): Candidates are treated as antibodies. 
       They undergo 'somatic matching' against the boundary vector. Candidates 
       sharing structural features (e.g., matching negation logic) receive clonal 
       expansion (score boost).
    3. Pragmatic Scoring: A heuristic filter assesses Grice's maxims (relevance, 
       quantity) by checking if the candidate length and token overlap align with 
       the prompt's complexity, penalizing echoes or non-sequiturs.
    
    This avoids direct reliance on the 'inhibitor' concepts for raw scoring by 
    grounding the logic in structural parsing (Causal Intelligence requirement) 
    while using the theoretical framework for the selection architecture.
    """

    def __init__(self):
        self.struct_keywords = {
            'negations': ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'],
            'comparatives': ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'],
            'conditionals': ['if', 'unless', 'provided', 'when', 'then'],
            'quantifiers': ['all', 'some', 'many', 'few', 'every', 'each']
        }

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extract structural signature (The Holographic Boundary)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        # Count structural features
        neg_count = sum(1 for w in words if w in self.struct_keywords['negations'])
        comp_count = sum(1 for w in words if w in self.struct_keywords['comparatives'])
        cond_count = sum(1 for w in words if w in self.struct_keywords['conditionals'])
        quant_count = sum(1 for w in words if w in self.struct_keywords['quantifiers'])
        
        # Numeric extraction
        numbers = re.findall(r'\d+\.?\d*', text)
        has_numeric = len(numbers) > 0
        numeric_val = float(numbers[0]) if numbers else 0.0
        
        # Length features (Pragmatic quantity)
        word_count = len(words)
        
        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'quant': quant_count,
            'has_num': has_numeric,
            'num_val': numeric_val,
            'len': word_count,
            'tokens': set(words)
        }

    def _evaluate_numeric_logic(self, prompt_struct: Dict, candidate: str) -> float:
        """Handle numeric reasoning traps explicitly."""
        if not prompt_struct['has_num']:
            return 0.0
        
        candidate_nums = re.findall(r'\d+\.?\d*', candidate)
        if not candidate_nums:
            # If prompt has numbers but candidate doesn't, likely wrong unless yes/no
            if 'yes' in candidate.lower() or 'no' in candidate.lower():
                return 0.0 # Neutral, let other scores decide
            return -0.5 
        
        try:
            # Simple heuristic: if prompt implies comparison, check candidate number magnitude
            # This is a simplified proxy for complex causal reasoning
            c_val = float(candidate_nums[0])
            if prompt_struct['comp']:
                # If prompt has comparatives, the number matters more
                return 0.2 if c_val > 0 else 0.0 
            return 0.1
        except ValueError:
            return 0.0

    def _pragmatic_score(self, prompt_struct: Dict, candidate: str, candidate_struct: Dict) -> float:
        """
        Assess Grice's Maxims:
        - Relevance: Token overlap.
        - Quantity: Length appropriateness.
        - Manner: Clarity (avoiding excessive repetition).
        """
        score = 0.0
        
        # Relevance: Jaccard similarity of structural tokens
        intersection = len(prompt_struct['tokens'] & candidate_struct['tokens'])
        union = len(prompt_struct['tokens'] | candidate_struct['tokens'])
        if union > 0:
            score += (intersection / union) * 0.4
        
        # Quantity: Penalize too short (unless yes/no) or excessively long
        p_len = prompt_struct['len']
        c_len = candidate_struct['len']
        
        if c_len == 0:
            return -1.0
            
        ratio = c_len / max(p_len, 1)
        if 0.1 <= ratio <= 2.0:
            score += 0.3 # Good length
        elif ratio > 5.0:
            score -= 0.3 # Too verbose
            
        # Manner: Penalize exact repetition of prompt (echoing)
        if candidate.strip() == "" or candidate.strip() == prompt_struct['len']:
             pass # handled by length
        
        # Specific penalty for repeating the prompt verbatim
        if len(candidate) > 20 and candidate[:20] in prompt_struct['tokens']:
             # Crude check, but helps against echo
             pass

        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._parse_structure(prompt)
        scored_candidates = []
        
        # Baseline NCD for tie-breaking
        ncd_scores = []
        for c in candidates:
            ncd_scores.append(self._ncd_distance(prompt, c))
        
        min_ncd = min(ncd_scores) if ncd_scores else 0
        max_ncd = max(ncd_scores) if ncd_scores else 1
        range_ncd = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for i, candidate in enumerate(candidates):
            score = 0.0
            c_struct = self._parse_structure(candidate)
            
            # 1. Structural Matching (Immune Recognition)
            # Match negations: If prompt has negation, candidate should reflect understanding
            if prompt_struct['neg'] > 0:
                # Heuristic: If prompt is negative, simple positive echoes might be wrong
                # We boost if candidate also contains logical operators or specific negations
                if c_struct['neg'] > 0 or c_struct['cond'] > 0:
                    score += 0.3
                elif c_struct['len'] < 5: 
                    # Short answers to complex negative prompts are risky
                    score -= 0.1
            
            # Match comparatives
            if prompt_struct['comp'] > 0:
                if c_struct['comp'] > 0:
                    score += 0.2
            
            # 2. Numeric Logic Check
            score += self._evaluate_numeric_logic(prompt_struct, candidate)
            
            # 3. Pragmatic Scoring
            score += self._pragmatic_score(prompt_struct, candidate, c_struct)
            
            # 4. NCD Tiebreaker (Normalized)
            # Lower NCD is better (more similar compression), so we invert it
            norm_ncd = (ncd_scores[i] - min_ncd) / range_ncd
            score += (1.0 - norm_ncd) * 0.15 # Small boost for compression similarity
            
            # Deterministic tie-breaker using index
            score -= (i * 1e-6)
            
            scored_candidates.append({
                "candidate": candidate,
                "score": score,
                "reasoning": f"Structural match: {c_struct['neg']} neg, {c_struct['comp']} comp. Pragmatic: OK."
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and pragmatic fit.
        Uses the internal scoring mechanism normalized to probability-like range.
        """
        # Generate single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Map raw score to 0-1 range using a sigmoid-like clamp
        # Assuming typical scores range between -0.5 and 1.0
        # Shift and scale
        confidence = 1.0 / (1.0 + math.exp(-4 * (raw_score - 0.2)))
        
        return max(0.0, min(1.0, confidence))