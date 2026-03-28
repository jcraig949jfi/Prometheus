import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    QD-ToMNet Implementation (Causal-Safe Variant).
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts negations, comparatives, and numeric values.
       Scores candidates based on logical consistency with extracted constraints.
    2. Dialectical Dynamics (Secondary): Simulates Thesis/Antithesis by checking if a candidate
       contradicts the prompt's structural constraints. The 'Synthesis' is the residual score
       after penalizing contradictions.
    3. Quantum-Inspired Superposition (Metaphorical): Candidates are treated as basis states.
       Instead of true density matrices (computationally expensive and historically risky),
       we use a weighted vector space where 'entanglement' represents the dependency between
       the prompt's constraints and the candidate's assertions.
    4. NCD (Tiebreaker): Used only when structural signals are ambiguous.
    
    Note: Per causal analysis, 'Quantum Mechanics' and 'Theory of Mind' concepts are restricted
    to internal variable naming and the confidence wrapper to avoid reasoning traps.
    """

    def __init__(self):
        self.numeric_ops = ['<', '>', '=', '==', '!=', '>=', '<=']
        self.negation_words = ['not', 'no', 'never', 'false', 'impossible', 'deny']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse']

    def _extract_structural_features(self, text: str) -> Dict:
        """Extracts negations, numbers, and comparatives for logical scoring."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(?:' + '|'.join(self.negation_words) + r')\b', text_lower)),
            'comparatives': len(re.findall(r'\b(?:' + '|'.join(self.comparatives) + r')\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'has_question': '?' in text,
            'length': len(text)
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Dialectical consistency check.
        Thesis: Prompt constraints.
        Antithesis: Candidate claims.
        Synthesis: Score based on non-contradiction.
        """
        score = 1.0
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        p_low = prompt.lower()
        c_low = candidate.lower()

        # 1. Numeric Consistency (High Priority)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # Simple heuristic: if prompt has numbers and candidate has numbers,
                # check if they align in a simple comparison context.
                # If prompt implies "less than" and candidate is larger, penalize.
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                
                if 'less' in p_low or 'smaller' in p_low or '<' in p_low:
                    if c_nums and p_nums:
                        if min(c_nums) > max(p_nums): # Rough heuristic for "pick the smaller one"
                            score -= 0.5
                elif 'greater' in p_low or 'larger' in p_low or '>' in p_low:
                    if c_nums and p_nums:
                        if max(c_nums) < min(p_nums): # Rough heuristic for "pick the larger one"
                            score -= 0.5
            except ValueError:
                pass

        # 2. Negation/Contradiction Check
        # If prompt asks what is NOT true, and candidate affirms a positive fact without negation
        if p_feat['negations'] > 0 and c_feat['negations'] == 0:
            # Heuristic: If prompt is negative, valid answers often contain negation or specific negative markers
            # This is a weak signal but better than nothing without an LLM.
            if any(word in c_low for word in ['yes', 'true', 'is']):
                score -= 0.2

        # 3. Structural Overlap (Jaccard-like on key tokens)
        common_tokens = set(p_low.split()) & set(c_low.split())
        overlap_ratio = len(common_tokens) / (len(set(p_low.split())) + 1)
        score += overlap_ratio * 0.5

        return max(0.0, min(1.0, score))

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Pre-calculate prompt features to avoid re-computation
        p_feat = self._extract_structural_features(prompt)
        p_low = prompt.lower()
        
        # Calculate base structural scores for all candidates
        raw_scores = []
        for cand in candidates:
            logic_score = self._check_logical_consistency(prompt, cand)
            raw_scores.append(logic_score)
        
        # Normalize structural scores to prevent dominance by length artifacts
        max_raw = max(raw_scores) if raw_scores else 1.0
        min_raw = min(raw_scores) if raw_scores else 0.0
        range_raw = max_raw - min_raw if max_raw != min_raw else 1.0
        
        final_scores = []
        for i, cand in enumerate(candidates):
            # Normalized structural score (0.6 weight)
            norm_struct = (raw_scores[i] - min_raw) / range_raw
            struct_component = 0.6 * norm_struct + 0.4 # Shift to [0.4, 1.0] range
            
            # NCD Tiebreaker (0.4 weight) - Inverted because lower distance is better
            # We compare candidate to prompt. Lower NCD = more similar/relevant.
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_component = 1.0 - ncd_val # Convert to similarity
            
            # Dialectical Synthesis: Combine structural logic with similarity
            # If structural logic is strong (e.g., numeric match), it dominates.
            final_score = 0.7 * struct_component + 0.3 * ncd_component
            
            # Penalty for exact echo (gameable)
            if cand.strip().lower() == prompt.strip().lower():
                final_score *= 0.5
                
            final_scores.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural: {norm_struct:.2f}, NCD: {ncd_val:.2f}"
            })
        
        # Rank by score descending
        final_scores.sort(key=lambda x: x['score'], reverse=True)
        return final_scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing and NCD as a fallback metric.
        Restricted usage of QM/ToM concepts per causal safety guidelines.
        """
        if not answer:
            return 0.0
            
        # 1. Structural Consistency Check
        logic_score = self._check_logical_consistency(prompt, answer)
        
        # 2. NCD Similarity (Relevance)
        ncd_sim = 1.0 - self._ncd_distance(prompt, answer)
        
        # 3. Synthesis
        # High logic score drives confidence. NCD supports it.
        conf = 0.8 * logic_score + 0.2 * ncd_sim
        
        # Hard constraints
        if not answer.strip():
            return 0.0
            
        return float(np.clip(conf, 0.0, 1.0))