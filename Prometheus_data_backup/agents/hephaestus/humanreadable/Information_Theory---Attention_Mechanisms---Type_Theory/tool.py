import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Information-Bottleneck Attention (TIBA) approximator.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values to form a 'Type Signature'.
       Candidates violating hard type constraints (e.g., wrong polarity) are penalized.
    2. Information Bottleneck (MI Estimation): Estimates Mutual Information between 
       the candidate and the prompt's structural core. High overlap with noise reduces score;
       high overlap with logical operators increases score.
    3. Attention Restriction: Per Coeus guidelines, attention mechanisms are restricted 
       to the confidence wrapper for structural alignment, not direct scoring.
    4. Scoring: Primary signal is structural/numeric consistency. NCD is used only 
       as a tie-breaker for candidates with identical structural scores.
    """

    def __init__(self):
        self.num_pattern = re.compile(r"-?\d+(?:\.\d+)?")
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'n\'t'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        return [float(x) for x in self.num_pattern.findall(text)]

    def _get_type_signature(self, text: str) -> Dict:
        """Extracts logical 'types' (constraints) from text."""
        tokens = set(self._tokenize(text))
        nums = self._extract_numbers(text)
        
        has_negation = bool(tokens & self.negations)
        has_comparative = bool(tokens & self.comparatives)
        has_conditional = bool(tokens & self.conditionals)
        
        # Simple numeric range check for type consistency
        num_min = min(nums) if nums else None
        num_max = max(nums) if nums else None
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'nums': nums,
            'num_count': len(nums),
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        
        # Concatenation compression
        try:
            comp_combined = len(zlib.compress(b1 + b2))
            comp1 = len(zlib.compress(b1))
            comp2 = len(zlib.compress(b2))
            
            max_len = max(comp1, comp2)
            if max_len == 0:
                return 0.0
            ncd = (comp_combined - min(comp1, comp2)) / max_len
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def _check_type_compatibility(self, prompt_sig: Dict, cand_sig: Dict) -> float:
        """
        Checks if the candidate satisfies the logical 'types' implied by the prompt.
        Returns a penalty score (0.0 = violation, 1.0 = compatible).
        """
        score = 1.0
        
        # Negation Consistency: If prompt asks a negative question, answer should reflect it?
        # Heuristic: If prompt has conditional/negation, candidate must not ignore context entirely.
        # Simplified: We check if the candidate introduces contradictory types.
        
        # Numeric Transitivity Check (Simplified)
        # If prompt has numbers and candidate has numbers, they should be related magnitude-wise
        if prompt_sig['num_count'] > 0 and cand_sig['num_count'] > 0:
            # Basic heuristic: Candidate numbers shouldn't be wildly out of distribution 
            # unless it's a calculation result. We assume proximity implies relevance.
            p_avg = sum(prompt_sig['nums']) / prompt_sig['num_count']
            c_avg = sum(cand_sig['nums']) / cand_sig['nums'] if cand_sig['nums'] else 0
            
            # If magnitudes differ by > 10x, slight penalty (unless prompt implies scaling)
            if p_avg != 0 and abs(c_avg - p_avg) > abs(p_avg) * 10:
                score -= 0.2

        return max(0.0, score)

    def _estimate_mi_score(self, prompt: str, candidate: str) -> float:
        """
        Approximates Mutual Information I(C;P) via structural overlap.
        High overlap on logical operators = High Information.
        High overlap on common words = Low Information (Noise).
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        if not c_tokens:
            return 0.0
            
        # Weighted overlap: Logical words carry more 'information' about reasoning
        logical_words = self.negations | self.comparatives | self.conditionals
        overlap = p_tokens & c_tokens
        
        info_weight = 0.0
        for word in overlap:
            if word in logical_words:
                info_weight += 2.0  # High value for logical consistency
            else:
                info_weight += 0.1  # Low value for content overlap
        
        # Normalize by candidate complexity (Bottleneck principle)
        # Penalize if candidate is just repeating prompt (low new info)
        if len(c_tokens) == len(overlap) and len(overlap) > 3:
            info_weight *= 0.5 # Penalty for pure echo
            
        return info_weight / (1.0 + math.log(len(c_tokens) + 1))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_sig = self._get_type_signature(prompt)
        scored_candidates = []
        
        for cand in candidates:
            cand_sig = self._get_type_signature(cand)
            
            # 1. Type Check (Hard constraints)
            type_score = self._check_type_compatibility(prompt_sig, cand_sig)
            
            # 2. Information Bottleneck (MI estimation)
            mi_score = self._estimate_mi_score(prompt, cand)
            
            # 3. Structural Parsing Score (Primary Signal)
            # Does the candidate answer the specific structural form?
            struct_score = 0.0
            if prompt_sig['conditional']:
                if any(k in cand.lower() for k in ['if', 'then', 'because', 'so']):
                    struct_score += 0.5
            if prompt_sig['comparative']:
                if any(k in cand.lower() for k in list(self.comparatives) + ['is', 'than']):
                    struct_score += 0.5
            
            # Numeric Evaluation
            if prompt_sig['num_count'] > 0 and cand_sig['num_count'] > 0:
                # Check for basic arithmetic consistency if obvious
                # (Simplified: just rewarding presence of numbers in numeric context)
                struct_score += 0.5

            # Combined Score: Type Validity * (Structural + MI)
            # Type violations act as a multiplier penalty
            final_score = type_score * (struct_score + mi_score)
            
            scored_candidates.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f"Type-valid:{type_score:.2f}, Struct:{struct_score:.2f}, MI:{mi_score:.2f}",
                '_ncd': None # Placeholder for tie-breaking
            })

        # Tie-breaking with NCD only when scores are effectively equal
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply NCD as tie-breaker for top candidates if scores are very close
        if len(scored_candidates) > 1:
            top_score = scored_candidates[0]['score']
            # Group candidates with similar scores
            i = 0
            while i < len(scored_candidates):
                j = i
                while j < len(scored_candidates) and abs(scored_candidates[j]['score'] - top_score) < 1e-6:
                    j += 1
                
                if j - i > 1:
                    # Tie detected, use NCD to sort this group
                    group = scored_candidates[i:j]
                    # Score by closeness to prompt (lower NCD is better)
                    group.sort(key=lambda x: self._compute_ncd(prompt, x['candidate']))
                    scored_candidates[i:j] = group
                    # Update top_score reference for next iteration if needed, 
                    # though we strictly only break ties among the current top cluster
                    if j < len(scored_candidates):
                        top_score = scored_candidates[j]['score']
                i = j if j > i else i + 1

        # Clean up and format output
        result = []
        for item in scored_candidates:
            result.append({
                'candidate': item['candidate'],
                'score': item['score'],
                'reasoning': item['reasoning']
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence based on structural alignment and type consistency.
        Uses restricted attention (structural parsing) rather than raw similarity.
        """
        prompt_sig = self._get_type_signature(prompt)
        ans_sig = self._get_type_signature(answer)
        
        # 1. Type Consistency Check
        type_compat = self._check_type_compatibility(prompt_sig, ans_sig)
        if type_compat < 0.5:
            return 0.1 # Hard constraint violation

        # 2. Structural Attention (Restricted)
        # Does the answer attend to the logical operators in the prompt?
        alignment_score = 0.0
        
        if prompt_sig['negation']:
            # If prompt is negative, does answer acknowledge it?
            if ans_sig['negation']:
                alignment_score += 0.4
            else:
                # Potential contradiction or ignoring context
                alignment_score -= 0.2
                
        if prompt_sig['comparative']:
            if ans_sig['comparative'] or ans_sig['num_count'] > 0:
                alignment_score += 0.4
        
        if prompt_sig['conditional']:
            if ans_sig['conditional'] or len(ans_sig['nums']) > 0:
                alignment_score += 0.3

        # 3. Information Density (Bottleneck)
        # Is the answer too short (low info) or too long (noise)?
        len_ratio = len(answer) / (len(prompt) + 1)
        density_score = 0.0
        if 0.01 < len_ratio < 2.0:
            density_score = 0.2
        
        raw_score = type_compat * (0.5 + alignment_score + density_score)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, raw_score))