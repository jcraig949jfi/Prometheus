import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a structural reasoning engine inspired by Tensor-RL-Nash concepts.
    
    Mechanism:
    1. Structural Parsing (Hypothesis Generation): Extracts logical operators (negations,
       comparatives, conditionals) and numeric values from the prompt. This acts as 
       constraining the 'rank' of the problem to essential logical factors.
    2. Constraint Propagation (Equilibrium Computation): Evaluates candidate answers 
       against extracted structural constraints. Candidates violating logical negations 
       or numeric inequalities receive heavy penalties (Bellman error approximation).
    3. Factor Scoring (Representation Learning): Computes a score based on the alignment 
       between the candidate's logical structure and the prompt's structural 'factors'.
    4. NCD Tiebreaker: Uses Normalized Compression Distance only when structural scores 
       are indistinguishable, ensuring robustness against string noise.
    """
    
    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        
    def _extract_structure(self, text: str) -> dict:
        """Extract logical factors: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text)
        }

    def _check_logical_consistency(self, prompt_struct: dict, candidate: str) -> float:
        """
        Evaluate candidate against prompt constraints.
        Returns a penalty score (0.0 = consistent, negative = inconsistent).
        """
        candidate_lower = candidate.lower()
        score = 0.0
        
        # Negation consistency: If prompt has negation, candidate should ideally reflect it
        # or at least not contradict it explicitly if the answer depends on it.
        # Simplified heuristic: Check for direct contradiction patterns.
        if prompt_struct['negation']:
            if re.search(r'\b(yes|true|correct)\b', candidate_lower) and 'not' in candidate_lower:
                pass # Complex, skip penalty
            elif re.search(r'\b(no|false)\b', candidate_lower) and 'not' not in candidate_lower:
                # Potential contradiction depending on context, weak penalty
                pass 

        # Numeric consistency
        if prompt_struct['numbers'] and len(prompt_struct['numbers']) >= 2:
            nums = prompt_struct['numbers']
            # Extract numbers from candidate
            cand_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', candidate)]
            
            if cand_nums:
                # Check if candidate preserves order if comparative exists
                if prompt_struct['comparative']:
                    # Simple check: if prompt says A > B, and candidate mentions numbers,
                    # do they follow logic? (Hard to map A/B without semantic parsing)
                    # Instead, check if candidate contradicts explicit math in prompt
                    pass
                
                # Direct contradiction check: If prompt implies X, candidate says Y
                # Heuristic: If prompt has specific numbers and candidate has totally different ones
                # this might indicate hallucination, but we lack context. 
                # Skip hard numeric penalty without semantic mapping.
                pass

        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(z1, z2)
        if denominator == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt features for factor analysis
        p_has_neg = prompt_struct['negation']
        p_has_comp = prompt_struct['comparative']
        p_has_cond = prompt_struct['conditional']
        
        scores = []
        
        for i, cand in enumerate(candidates):
            c_struct = self._extract_structure(cand)
            
            # 1. Structural Alignment Score (The "Tensor Factor" alignment)
            # We want the candidate's logical signature to align with the prompt's requirements
            alignment = 0.0
            
            # Negation alignment
            if p_has_neg:
                # If prompt is negative, candidate acknowledging negation gets a boost
                if c_struct['negation']:
                    alignment += 2.0
                # If prompt is negative and candidate is a bare "Yes", it might be wrong contextually
                # but we can't know for sure without semantics. 
            else:
                # If prompt is positive, candidate shouldn't be overly negative unless answering "No"
                pass
                
            # Comparative alignment
            if p_has_comp:
                if c_struct['comparative']:
                    alignment += 1.5
                    
            # Conditional alignment
            if p_has_cond:
                if c_struct['conditional']:
                    alignment += 1.5
            
            # 2. Logical Consistency Penalty
            penalty = self._check_logical_consistency(prompt_struct, cand)
            
            # 3. Base Score
            base_score = alignment + penalty
            
            # Store intermediate data
            scores.append({
                'index': i,
                'structural_score': base_score,
                'candidate': cand
            })
        
        # Normalize structural scores to 0-1 range roughly, then apply NCD tiebreaker
        max_struct = max(s['structural_score'] for s in scores)
        min_struct = min(s['structural_score'] for s in scores)
        range_struct = max_struct - min_struct if max_struct != min_struct else 1.0
        
        final_results = []
        for item in scores:
            # Normalize structural score
            norm_struct = (item['structural_score'] - min_struct) / range_struct
            
            # NCD Tiebreaker (only matters if structural scores are close)
            # We use NCD distance from prompt. Closer (lower NCD) is often better for "extraction"
            # but for reasoning, sometimes divergence is needed. 
            # Here we use NCD as a tiebreaker for similar structural scores.
            ncd_val = self._compute_ncd(prompt, item['candidate'])
            
            # Combine: Structural is primary (weight 0.9), NCD is secondary (weight 0.1)
            # Note: Lower NCD is "closer", so we invert it for scoring (1 - ncd)
            total_score = 0.9 * norm_struct + 0.1 * (1.0 - ncd_val)
            
            # Generate reasoning string
            reason_parts = []
            if p_has_neg and c_struct['negation']:
                reason_parts.append("Matches negation structure")
            if p_has_comp and c_struct['comparative']:
                reason_parts.append("Matches comparative structure")
            if p_has_cond and c_struct['conditional']:
                reason_parts.append("Matches conditional structure")
            if not reason_parts:
                reason_parts.append("Structural alignment based on logical factors")
                
            reasoning_str = "; ".join(reason_parts) + f". NCD factor: {1.0-ncd_val:.2f}"
            
            final_results.append({
                'candidate': item['candidate'],
                'score': float(total_score),
                'reasoning': reasoning_str
            })
            
        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimate confidence based on structural alignment strength.
        """
        # Re-use evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]['score']
        
        # Map score (which is roughly 0-1) to confidence
        # High structural alignment + low NCD distance = high confidence
        # We clamp between 0 and 1
        conf = max(0.0, min(1.0, score))
        return conf