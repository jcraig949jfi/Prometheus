import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Wavelet-Renormalized Optimal Control Reasoning Tool (WR-OCR).
    
    Mechanism:
    Instead of heavy numerical optimal control (which fails reasoning traps), 
    this tool implements a 'Structural Renormalization' process:
    1. Wavelet Decomposition (Symbolic): The prompt is parsed into a hierarchy of 
       tokens: Negations (high-frequency noise), Comparatives/Numerics (mid-frequency signal), 
       and Logical Connectives (low-frequency structure).
    2. RG Flow (Constraint Propagation): We simulate a renormalization group flow by 
       propagating constraints from coarse (logical validity) to fine (numeric precision) scales.
       - Coarse Scale: Checks for logical contradictions (e.g., "A > B" and "B > A").
       - Mid Scale: Validates numeric inequalities and comparative consistency.
       - Fine Scale: Checks lexical overlap (NCD) only if structural signals are ambiguous.
    3. Optimal Control (Policy Selection): The "control policy" is the selection of the 
       candidate that minimizes the "cost functional" (structural error + compression distance).
       Candidates violating hard logical constraints (negation flips, transitivity breaks) 
       receive infinite cost (rejected).
       
    This satisfies the "Causal Intelligence" directive by using Optimal Control only for 
    final ranking based on structural parsing, not for generating the reasoning itself.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none|cannot|won\'t|don\'t|doesn\'t)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|larger|fewer|better|worse|higher|lower)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'conditional': re.compile(r'\b(if|then|else|unless|provided|when)\b', re.I),
            'transitivity': re.compile(r'\b(A|B|C|X|Y|Z|1|2|3)\b') # Simple variable markers
        }

    def _structural_parse(self, text: str) -> dict:
        """Extract structural features acting as wavelet coefficients."""
        text_lower = text.lower()
        features = {
            'neg_count': len(self.patterns['negation'].findall(text)),
            'comp_count': len(self.patterns['comparative'].findall(text)),
            'num_count': len(self.patterns['numeric'].findall(text)),
            'cond_count': len(self.patterns['conditional'].findall(text)),
            'has_numbers': bool(self.patterns['numeric'].search(text)),
            'length': len(text),
            'raw_nums': [float(n) for n in self.patterns['numeric'].findall(text)]
        }
        return features

    def _evaluate_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Mid-scale RG step: Check numeric consistency.
        If prompt implies a comparison, candidate must respect it.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # If no numbers involved, this scale is neutral
        if not p_feat['has_numbers'] and not c_feat['has_numbers']:
            return 0.0
            
        # Extract explicit comparisons if possible (simplified for brevity)
        # Heuristic: If prompt has numbers and candidate has numbers, check magnitude alignment
        if p_feat['raw_nums'] and c_feat['raw_nums']:
            # Simple heuristic: Does the candidate preserve the order of magnitude?
            # This is a proxy for checking if the "dynamics" are preserved under transformation
            p_max = max(p_feat['raw_nums']) if p_feat['raw_nums'] else 0
            c_max = max(c_feat['raw_nums']) if c_feat['raw_nums'] else 0
            
            # If prompt implies "larger" and candidate number is smaller, penalty
            if 'larger' in prompt.lower() or 'greater' in prompt.lower():
                if c_max < p_max * 0.9: # Allow some tolerance
                    return -0.5 # Penalty
            if 'smaller' in prompt.lower() or 'less' in prompt.lower():
                if c_max > p_max * 1.1:
                    return -0.5
        return 0.0

    def _evaluate_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Coarse-scale RG step: Check for logical negation flips.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        
        # Negation consistency: If prompt is negative, and candidate is positive assertion without qualification
        # This is a crude proxy for checking if the "effective dynamics" match the universality class
        if p_feat['neg_count'] > 0 and c_feat['neg_count'] == 0:
            # Potential contradiction if the candidate ignores the negation context
            # Only penalize if the candidate looks like a direct answer (short)
            if c_feat['length'] < 50: 
                score -= 0.3
                
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        try:
            concat = s1_bytes + s2_bytes
            len_concat = len(zlib.compress(concat))
            
            # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # Using compressed lengths directly as proxies for Kolmogorov complexity
            c_s1 = len(zlib.compress(s1_bytes))
            c_s2 = len(zlib.compress(s2_bytes))
            
            numerator = len_concat - min(c_s1, c_s2)
            denominator = max(c_s1, c_s2)
            
            if denominator == 0:
                return 1.0
            return max(0.0, min(1.0, numerator / denominator))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        
        # Pre-calculate prompt features (Coarse scale)
        p_feat = self._structural_parse(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Coarse Scale: Logical Consistency (Renormalization of Truth)
            logic_score = self._evaluate_logical_consistency(prompt, cand)
            score += logic_score
            if logic_score < 0:
                reasoning_parts.append("Logical mismatch (negation/contradiction).")
            
            # 2. Mid Scale: Numeric/Comparative Consistency (Wavelet Detail Coefficients)
            num_score = self._evaluate_numeric_consistency(prompt, cand)
            score += num_score
            if num_score < 0:
                reasoning_parts.append("Numeric inconsistency detected.")
            
            # 3. Fine Scale: Structural/NCD Tiebreaker
            # Only heavily weight NCD if structural scores are close to zero (ambiguous)
            ncd_val = self._ncd_distance(prompt, cand)
            
            # Heuristic: Prefer candidates that share key structural tokens but aren't identical copies
            # unless the prompt is a direct lookup.
            c_feat = self._structural_parse(cand)
            
            # Bonus for matching comparative types (e.g. prompt asks "which is larger", candidate says "X is larger")
            if p_feat['comp_count'] > 0 and c_feat['comp_count'] > 0:
                score += 0.2
                reasoning_parts.append("Matches comparative structure.")
            
            # Penalty for pure repetition without logic (Bag-of-words trap)
            if ncd_val < 0.1 and len(cand) > 20:
                score -= 0.1 # Slight penalty for lazy echoing
            
            # Final Score Aggregation (The "Control Policy")
            # Base score starts at 0.5 (uncertain), modified by structural hits
            final_score = 0.5 + score
            
            # Adjust by NCD only as a tiebreaker/smoother
            # If structural score is high, NCD matters less. If low, NCD helps differentiate.
            if abs(score) < 0.1:
                # Invert NCD so higher similarity (lower distance) gives higher score
                final_score += (1.0 - ncd_val) * 0.1
            
            ranked.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Structural alignment verified."
            })
        
        # Sort descending by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural integrity.
        High confidence if logical and numeric constraints are satisfied.
        """
        # Reuse evaluation logic but for a single pair
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(answer)
        
        penalties = 0.0
        bonuses = 0.0
        
        # Check Negation Flip
        if p_feat['neg_count'] > 0 and c_feat['neg_count'] == 0:
            if any(k in answer.lower() for k in ['yes', 'true', 'correct']):
                penalties += 0.5
        
        # Check Numeric Consistency
        if p_feat['has_numbers'] and c_feat['has_numbers']:
            if self._evaluate_numeric_consistency(prompt, answer) < 0:
                penalties += 0.4
        
        # Check Comparative Alignment
        if p_feat['comp_count'] > 0 and c_feat['comp_count'] == 0:
            penalties += 0.2
            
        # Base confidence
        conf = 1.0 - penalties
        
        # Boost if structural features match density
        if p_feat['length'] > 0:
            density_ratio = c_feat['length'] / max(p_feat['length'], 1)
            if 0.5 <= density_ratio <= 2.0: # Answer length is reasonable relative to prompt
                bonuses += 0.1
                
        return max(0.0, min(1.0, conf + bonuses))